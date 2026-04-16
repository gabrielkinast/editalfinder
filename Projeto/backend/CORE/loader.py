import json
import os
import sys
import re
import logging
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any, Tuple

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import supabase
from schema import normalizar
from log_utils import get_logger

try:
    from alerts import process_alerts
except ImportError:
    process_alerts = None

# Configuração de diretórios
CORE_DIR = Path(__file__).parent
TRANSFORMER_DIR = CORE_DIR / "transformer"
logger = get_logger("loader")
TABLES_AVAILABLE = {"edital_anexo": False, "edital_extra_campo": False}
DEFAULT_ORG_ID = None

def get_current_db_editais() -> Dict[str, Any]:
    """Busca todos os editais atuais do banco para comparação de alertas."""
    try:
        response = supabase.table("edital").select("*").execute()
        return {item["link"]: item for item in response.data}
    except Exception as e:
        logger.error(f"Erro ao buscar editais do banco: {e}")
        return {}

def get_default_org_id():
    """Busca a primeira organização disponível no banco para usar como padrão."""
    global DEFAULT_ORG_ID
    if DEFAULT_ORG_ID is not None:
        return DEFAULT_ORG_ID
    
    try:
        response = supabase.table("organizacao").select("id_organizacao").limit(1).execute()
        if response.data:
            DEFAULT_ORG_ID = response.data[0]["id_organizacao"]
            logger.info("Usando organização ID: %s", DEFAULT_ORG_ID)
            return DEFAULT_ORG_ID
    except Exception as exc:
        logger.warning("Não foi possível buscar organização padrão: %s", exc)
    
    return 11 # Fallback para o ID 11 se falhar


def detect_optional_tables():
    """Detect once if auxiliary tables are available in Supabase schema cache."""
    for table_name in TABLES_AVAILABLE:
        try:
            supabase.table(table_name).select("*").limit(1).execute()
            TABLES_AVAILABLE[table_name] = True
            logger.info("Tabela opcional disponível: %s", table_name)
        except Exception as exc:
            TABLES_AVAILABLE[table_name] = False
            logger.warning("Tabela opcional indisponível: %s (%s)", table_name, exc)

def clean_monetary_value(value_str):
    """Converte string monetária (R$ 1.000,00) em float para o banco."""
    if not value_str:
        return None
    
    try:
        # Remove R$, espaços e pontos de milhar
        clean = value_str.replace("R$", "").replace(" ", "").replace(".", "")
        # Substitui vírgula decimal por ponto
        clean = clean.replace(",", ".")
        
        # Trata casos de "milhões", "bilhões"
        multiplier = 1
        if "milhão" in value_str.lower() or "milhões" in value_str.lower():
            multiplier = 1_000_000
            clean = re.sub(r'[^\d.,]', '', clean)
        elif "bilhão" in value_str.lower() or "bilhões" in value_str.lower():
            multiplier = 1_000_000_000
            clean = re.sub(r'[^\d.,]', '', clean)
        elif "mil" in value_str.lower():
            multiplier = 1_000
            clean = re.sub(r'[^\d.,]', '', clean)
            
        return float(clean) * multiplier
    except:
        return None

def map_to_db_schema(item):
    """Mapeia o item padronizado para as colunas reais do banco 'edital'."""
    extras = item.get("extras", {})
    
    # Adiciona novos campos enriquecidos aos extras para não perder informação
    if item.get("programa"):
        extras["programa_identificado"] = item.get("programa")
    if item.get("acao"):
        extras["acao_identificada"] = item.get("acao")
    if item.get("tipo_recurso"):
        extras["tipo_recurso"] = item.get("tipo_recurso")
    
    # Tenta extrair o pdf_url se houver nos extras
    pdf_url = extras.get("pdf_url")
    if not pdf_url and "anexos" in extras:
        # Se for uma string (como no cnpq)
        if isinstance(extras["anexos"], str):
            try:
                anexos = json.loads(extras["anexos"])
                if anexos and isinstance(anexos, list):
                    pdf_url = anexos[0].get("url")
            except:
                pass
        elif isinstance(extras["anexos"], list) and extras["anexos"]:
            pdf_url = extras["anexos"][0].get("url")

    return {
        "titulo": item.get("titulo"),
        "descricao": item.get("descricao"),
        "link": item.get("link"),
        "fonte_recurso": item.get("fonte"),
        "data_publicacao": item.get("data_publicacao"),
        "prazo_envio": item.get("fim_inscricao"),
        "situacao": item.get("situacao"),
        "valor_maximo": clean_monetary_value(item.get("valor")),
        "valor_minimo": item.get("valor_minimo"),
        "contrapartida": item.get("contrapartida"),
        "elegibilidade": item.get("elegibilidade"),
        "contato": item.get("contato"),
        "link_inscricao": item.get("link_inscricao"),
        "ods": item.get("ods"),
        "estado": item.get("estado"),
        "regiao": item.get("regiao"),
        "pdf_url": pdf_url or item.get("link"),
        "status": "Ativo",
        "objetivo": item.get("tipo_recurso") or extras.get("objetivo") or item.get("descricao")[:500] if item.get("descricao") else None,
        "publico_alvo": extras.get("publico_alvo"),
        "temas": extras.get("temas"),
        "score": item.get("score") or 0,
        "score_detalhado": item.get("score_detalhado"), # JSON detalhado
        "justificativa": item.get("justificativa"),
        "recomendacao": item.get("recomendacao"),
        "compatibilidade": item.get("compatibilidade"),
        "id_organizacao": get_default_org_id()
    }, extras


def is_expired_deadline(deadline_iso):
    """Retorna True se o prazo já venceu (<= hoje)."""
    if not deadline_iso:
        return False
    try:
        deadline = date.fromisoformat(deadline_iso)
        return deadline <= date.today()
    except Exception:
        logger.warning("Prazo inválido encontrado: %s", deadline_iso)
        return False


def delete_expired_editals():
    """Apaga apenas editais com prazo_envio vencido (<= hoje)."""
    today_iso = date.today().isoformat()
    try:
        supabase.table("edital").delete().lte("prazo_envio", today_iso).execute()
        logger.info("Editais vencidos removidos (prazo_envio <= %s).", today_iso)
    except Exception as exc:
        logger.warning("Não foi possível remover editais vencidos: %s", exc)


def save_detail_tables(id_edital, extras):
    """Persiste anexos/chaves extras em tabelas auxiliares, quando existirem."""
    if not extras:
        return

    if TABLES_AVAILABLE["edital_anexo"]:
        anexos = extras.get("anexos")
        if isinstance(anexos, str):
            try:
                anexos = json.loads(anexos)
            except Exception:
                anexos = None

        if isinstance(anexos, list):
            for anexo in anexos:
                if not isinstance(anexo, dict):
                    continue
                try:
                    supabase.table("edital_anexo").insert({
                        "id_edital": id_edital,
                        "nome": anexo.get("nome"),
                        "url": anexo.get("url"),
                        "tipo": anexo.get("tipo"),
                    }).execute()
                except Exception as exc:
                    logger.warning("Falha ao inserir anexo do edital %s: %s", id_edital, exc)

    if TABLES_AVAILABLE["edital_extra_campo"]:
        for chave, valor in extras.items():
            if chave in ("anexos",):
                continue
            try:
                supabase.table("edital_extra_campo").insert({
                    "id_edital": id_edital,
                    "chave": str(chave),
                    "valor": json.dumps(valor, ensure_ascii=False) if isinstance(valor, (dict, list)) else str(valor),
                }).execute()
            except Exception as exc:
                logger.warning("Falha ao inserir extra '%s' do edital %s: %s", chave, id_edital, exc)

def inserir_ou_atualizar_edital(edital):
    """Insere ou atualiza um edital no banco de dados."""
    try:
        # Verifica se já existe
        response = supabase.table("edital").select("id_edital").eq("link", edital["link"]).execute()
        
        if response.data:
            # Atualiza
            id_edital = response.data[0]["id_edital"]
            supabase.table("edital").update(edital).eq("id_edital", id_edital).execute()
            return "atualizado", id_edital
        else:
            # Insere
            res = supabase.table("edital").insert(edital).execute()
            novo_id = (res.data or [{}])[0].get("id_edital")
            return "inserido", novo_id
            
    except Exception as e:
        logger.exception("Erro no upsert de edital link=%s", edital.get("link"))
        print(f"[ERRO SUPABASE] {e}")
        return "erro", None

def load_standardized_json(file_path):
    """Lê um arquivo JSON padronizado e o carrega no banco."""
    print(f"\nCarregando: {file_path.name}")
    
    if not file_path.exists():
        logger.error("Arquivo não encontrado: %s", file_path)
        print(f"[ERRO] Arquivo não encontrado: {file_path}")
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            data = [data]

        inseridos = 0
        atualizados = 0
        erros = 0
        ignorados_vencidos = 0

        for item in data:
            try:
                item_normalizado = normalizar(item)
                mapped_item, extras = map_to_db_schema(item_normalizado)

                if not mapped_item.get("link"):
                    logger.warning("Item sem link em %s: titulo=%s", file_path.name, item.get("titulo"))
                    continue
                if is_expired_deadline(mapped_item.get("prazo_envio")):
                    ignorados_vencidos += 1
                    continue

                status, id_edital = inserir_ou_atualizar_edital(mapped_item)
                if id_edital:
                    save_detail_tables(id_edital, extras)
                if status == "inserido":
                    inseridos += 1
                elif status == "atualizado":
                    atualizados += 1
                else:
                    erros += 1

            except Exception as e:
                logger.exception("Erro ao processar item de %s", file_path.name)
                print(f"[ERRO PROCESSAMENTO ITEM] {e}")
                erros += 1

        logger.info(
            "Carga finalizada arquivo=%s inseridos=%s atualizados=%s ignorados_vencidos=%s erros=%s",
            file_path.name, inseridos, atualizados, ignorados_vencidos, erros
        )
        print(
            f"Finalizado {file_path.name}: {inseridos} inseridos, "
            f"{atualizados} atualizados, {ignorados_vencidos} vencidos ignorados, {erros} erros."
        )

    except Exception as e:
        logger.exception("Erro ao ler arquivo %s", file_path)
        print(f"[ERRO AO LER ARQUIVO] {e}")

def main():
    detect_optional_tables()
    delete_expired_editals()
    
    # 1. Busca estado atual do banco para alertas
    old_editais = get_current_db_editais()
    new_editais_buffer = []

    json_files = list(TRANSFORMER_DIR.glob("*_standardized.json"))
    if not json_files:
        print(f"Nenhum arquivo encontrado em {TRANSFORMER_DIR}")
        return

    print(f"Iniciando carregamento de {len(json_files)} arquivos...")
    
    for json_file in json_files:
        # Carrega os dados e popula o buffer de novos editais
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                new_editais_buffer.extend(data)
            load_standardized_json(json_file)
        except: pass

    # 2. Processa Alertas Inteligentes
    if process_alerts:
        print("\n--- PROCESSANDO ALERTAS INTELIGENTES ---")
        process_alerts(new_editais_buffer, old_editais)

if __name__ == "__main__":
    main()
