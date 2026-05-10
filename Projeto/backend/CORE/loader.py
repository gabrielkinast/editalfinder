import argparse
import json
import os
import sys
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import supabase
from schema import normalizar
from log_utils import get_logger
from merge_utils import (
    merge_descricao,
    merge_extras_dict,
    merge_scalar_prefer_non_empty,
    anexos_dedupe_url,
    sanitize_for_postgres,
    _is_empty,
)
from taxonomy_filtros import extras_to_filter_columns
from content_routing import destination_table_for_item, infer_content_type

try:
    from alerts import process_alerts
except ImportError:
    process_alerts = None

# Configuração de diretórios
CORE_DIR = Path(__file__).parent
TRANSFORMER_DIR = CORE_DIR / "transformer"
logger = get_logger("loader")
TABLES_AVAILABLE = {
    "edital_anexo": False,
    "edital_extra_campo": False,
    "noticia": False,
    "pesquisa": False,
}
DEFAULT_ORG_ID = None

# Após migrar o Supabase (seção 7 do schema_sql_completo.sql), defina no .env:
# EDITALFINDER_EXTENDED_SCHEMA=true
EXTENDED_SCHEMA = os.getenv("EDITALFINDER_EXTENDED_SCHEMA", "").strip().lower() in (
    "1",
    "true",
    "yes",
    "on",
)

# Colunas aceitas no upsert (legado)
_LEGACY_EDITAL_COLUMNS = frozenset(
    {
        "titulo",
        "descricao",
        "link",
        "fonte_recurso",
        "data_publicacao",
        "prazo_envio",
        "situacao",
        "valor_maximo",
        "valor_minimo",
        "contrapartida",
        "elegibilidade",
        "contato",
        "link_inscricao",
        "ods",
        "regiao",
        "pdf_url",
        "objetivo",
        "publico_alvo",
        "temas",
        "score",
        "score_detalhado",
        "justificativa",
        "recomendacao",
        "compatibilidade",
        "id_organizacao",
    }
)

_EXTENDED_EXTRA_COLUMNS = frozenset(
    {
        "extras",
        "programa",
        "acao",
        "tipo_recurso",
        "tipo_oportunidade",
        "natureza_recurso",
        "area",
        "publico_alvo_arr",
        "setor_economico",
        "area_cientifica",
        "area_tecnologica",
        "setor_estrategico",
        "pais",
        "estado",
        "municipio",
        "valor_total_texto",
        "moeda",
        "reembolsavel",
        "orgao_responsavel",
        "instituicao",
        "orgao_contratante",
        "numero_edital",
        "numero_chamada",
        "codigo_oportunidade",
        "url_detalhe",
        "classificacao_confianca",
        "ativo",
        "hash_deduplicacao",
        "ultima_coleta",
        # Espelhos de extras (crédito, licitação, internacional, PDF)
        "numero_processo",
        "taxa_juros",
        "carencia",
        "prazo_pagamento",
        "titulo_original",
        "descricao_original",
        "titulo_traduzido",
        "descricao_traduzida",
        "idioma_original",
        "pdf_resumo",
        # i18n adicional / crédito / qualidade / roteamento (espelho extras → coluna)
        "titulo_en",
        "descricao_en",
        "traducao_automatica",
        "garantias",
        "limite_financiavel",
        "percentual_financiavel",
        "prazo_carencia",
        "prazo_amortizacao",
        "prazo_total",
        "publico_beneficiario",
        "finalidade_financiamento",
        "linha_credito",
        "modalidade_financiamento",
        "orgao",
        "unidade_responsavel",
        "subprograma",
        "chamada",
        "edital_numero",
        "data_abertura",
        "data_encerramento",
        "data_resultado",
        "valor_estimado",
        "valor_total",
        "uf",
        "cidade",
        "origem_portal",
        "url_listagem",
        "content_type_detectado",
        "extraction_mode",
        "access_status",
        "access_reason",
        "perfil_ideal",
        "tags",
        "validacao_status",
        "qualidade_dado",
        "warnings",
        "suspeito",
        "motivo_rejeicao",
        "documentos",
        "anexos",
    }
)

_SKIP_EXTRA_CAMPO_KEYS = frozenset(
    {
        "anexos",
        "pdf_texto_extraido",
        "pdf_lido_para_enriquecimento",
    }
)
_MAX_EXTRA_CAMPO_CHARS = 120_000


def _tipo_dado_extra_valor(valor: Any) -> str:
    if isinstance(valor, (dict, list)):
        return "json"
    if isinstance(valor, bool):
        return "boolean"
    if isinstance(valor, (int, float)):
        return "number"
    return "text"


def _allowed_upsert_keys() -> frozenset:
    if EXTENDED_SCHEMA:
        return _LEGACY_EDITAL_COLUMNS | _EXTENDED_EXTRA_COLUMNS
    return _LEGACY_EDITAL_COLUMNS


def _strip_payload(row: Dict[str, Any]) -> Dict[str, Any]:
    allowed = _allowed_upsert_keys()
    return {k: v for k, v in row.items() if k in allowed}


def get_current_db_editais() -> Dict[str, Any]:
    """Busca todos os editais atuais do banco para comparação de alertas."""
    try:
        response = supabase.table("edital").select("*").execute()
        if response and hasattr(response, "data") and response.data:
            editais_dict: Dict[str, Any] = {}
            for item in response.data:
                if isinstance(item, dict) and "link" in item:
                    editais_dict[str(item["link"])] = item
            return editais_dict
        return {}
    except Exception as e:
        logger.error("Erro ao buscar editais do banco: %s", e)
        return {}


def get_default_org_id():
    """Busca a primeira organização disponível no banco para usar como padrão."""
    global DEFAULT_ORG_ID
    if DEFAULT_ORG_ID is not None:
        return DEFAULT_ORG_ID

    try:
        response = supabase.table("organizacao").select("id_organizacao").limit(1).execute()
        if response and hasattr(response, "data") and response.data and len(response.data) > 0:
            org_data = response.data[0]
            if isinstance(org_data, dict):
                DEFAULT_ORG_ID = org_data.get("id_organizacao")
                logger.info("Usando organização ID: %s", DEFAULT_ORG_ID)
                return DEFAULT_ORG_ID
    except Exception as exc:
        logger.warning("Não foi possível buscar organização padrão: %s", exc)

    return 11  # Fallback para o ID 11 se falhar


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
    if not value_str or not isinstance(value_str, str):
        return None

    value_str = value_str.strip().upper()
    if value_str in ("NULL", "N/A", "NÃO ESPECIFICADO"):
        return None

    try:
        multiplier = 1
        if "BILHÃO" in value_str or "BILHÕES" in value_str or "BI " in value_str:
            multiplier = 1_000_000_000
        elif "MILHÃO" in value_str or "MILHÕES" in value_str or "MI " in value_str:
            multiplier = 1_000_000
        elif "MIL" in value_str:
            if not ("MILHÃO" in value_str or "MILHÕES" in value_str):
                multiplier = 1_000

        clean = re.sub(r"[^\d,.]", "", value_str)

        if not clean:
            return None

        if "," in clean and "." in clean:
            if clean.rfind(",") > clean.rfind("."):
                clean = clean.replace(".", "").replace(",", ".")
            else:
                clean = clean.replace(",", "")
        elif "," in clean:
            clean = clean.replace(",", ".")
        elif "." in clean:
            if clean.count(".") > 1 or len(clean.split(".")[-1]) != 2:
                clean = clean.replace(".", "")

        return float(clean) * multiplier
    except Exception as e:
        logger.debug("Falha ao converter valor monetário '%s': %s", value_str, e)
        return None


def _serialize_publico_alvo(val: Any) -> Any:
    if isinstance(val, list):
        return json.dumps(val, ensure_ascii=False)
    return val


def map_to_db_schema(item):
    """Mapeia o item padronizado para as colunas reais do banco 'edital'."""
    extras = item.get("extras", {})
    if not isinstance(extras, dict):
        extras = {}

    if item.get("programa"):
        extras.setdefault("programa_identificado", item.get("programa"))
    if item.get("acao"):
        extras.setdefault("acao_identificada", item.get("acao"))
    if item.get("tipo_recurso"):
        extras.setdefault("tipo_recurso", item.get("tipo_recurso"))

    pdf_url = extras.get("pdf_url")
    if isinstance(pdf_url, str):
        pdf_url = pdf_url.strip()
    if not pdf_url and "anexos" in extras:
        if isinstance(extras["anexos"], str):
            try:
                anexos = json.loads(extras["anexos"])
                if anexos and isinstance(anexos, list):
                    pdf_url = anexos[0].get("url")
            except Exception:
                pass
        elif isinstance(extras["anexos"], list) and extras["anexos"]:
            pdf_url = extras["anexos"][0].get("url")
    if not pdf_url and isinstance(extras.get("documentos"), list):
        for d in extras.get("documentos") or []:
            if not isinstance(d, dict):
                continue
            u = str(d.get("url") or d.get("link") or "").strip()
            if u.lower().endswith(".pdf"):
                pdf_url = u
                break
    if isinstance(pdf_url, str) and pdf_url and not pdf_url.lower().startswith(("http://", "https://")):
        pdf_url = None
    link_item = str(item.get("link") or "").strip()
    link_is_pdf = link_item.lower().split("?", 1)[0].endswith(".pdf")

    pub = extras.get("publico_alvo")
    if pub is not None and not isinstance(pub, str):
        pub = _serialize_publico_alvo(pub)

    return {
        "titulo": item.get("titulo"),
        "descricao": item.get("descricao"),
        "link": item.get("link"),
        "fonte_recurso": item.get("fonte"),
        "data_publicacao": item.get("data_publicacao"),
        "prazo_envio": item.get("fim_inscricao"),
        "situacao": item.get("situacao"),
        "valor_maximo": clean_monetary_value(item.get("valor")),
        "valor_minimo": item.get("valor_minimo") or extras.get("valor_minimo"),
        "contrapartida": item.get("contrapartida") or extras.get("contrapartida"),
        "elegibilidade": item.get("elegibilidade"),
        "contato": item.get("contato"),
        "link_inscricao": item.get("link_inscricao"),
        "ods": item.get("ods"),
        "regiao": item.get("regiao"),
        "pdf_url": pdf_url or (link_item if link_is_pdf else None),
        "objetivo": item.get("tipo_recurso")
        or extras.get("objetivo")
        or (item.get("descricao")[:500] if item.get("descricao") else None),
        "publico_alvo": pub if pub is not None else extras.get("publico_alvo"),
        "temas": extras.get("temas"),
        "score": item.get("score") or 0,
        "score_detalhado": item.get("score_detalhado"),
        "justificativa": item.get("justificativa"),
        "recomendacao": item.get("recomendacao"),
        "compatibilidade": item.get("compatibilidade"),
        "id_organizacao": get_default_org_id(),
    }, extras


def get_destination_table(item: Dict[str, Any]) -> str:
    """Tabela operacional para o item normalizado."""
    try:
        return destination_table_for_item(item)
    except Exception:
        return "edital"


def map_to_content_schema(item: Dict[str, Any], table_name: str) -> Dict[str, Any]:
    """Mapeia item padronizado para public.noticia/public.pesquisa."""
    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
    def _normalize_array_field(value: Any) -> Optional[List[str]]:
        """
        Normaliza campos que no banco podem ser arrays (text[]):
        - str -> [str]
        - list/tuple/set -> lista de strings não vazias
        - vazio -> None
        """
        if value is None:
            return None
        if isinstance(value, str):
            s = value.strip()
            return [s] if s else None
        if isinstance(value, (list, tuple, set)):
            out: List[str] = []
            for v in value:
                if v is None:
                    continue
                s = str(v).strip()
                if s:
                    out.append(s)
            return out or None
        s = str(value).strip()
        return [s] if s else None
    content_type = infer_content_type(item)
    docs = extras.get("documentos") if isinstance(extras.get("documentos"), list) else []
    primary_doc = ""
    for d in docs:
        if isinstance(d, dict):
            primary_doc = str(d.get("url") or d.get("link") or "").strip()
            if primary_doc:
                break
    return sanitize_for_postgres(
        {
            "titulo": item.get("titulo"),
            "resumo": item.get("descricao"),
            "link": item.get("link"),
            "fonte": item.get("fonte"),
            "data_publicacao": item.get("data_publicacao"),
            "pais": extras.get("pais"),
            "orgao": extras.get("orgao_responsavel")
            or extras.get("orgao_contratante")
            or extras.get("instituicao")
            or item.get("fonte"),
            "setor_estrategico": _normalize_array_field(extras.get("setor_estrategico")),
            "area_cientifica": _normalize_array_field(extras.get("area_cientifica")),
            "area_tecnologica": _normalize_array_field(extras.get("area_tecnologica")),
            "idioma": extras.get("idioma_original"),
            "tags": _normalize_array_field(
                extras.get("thematic_tags") or extras.get("subtema") or extras.get("palavras_chave_detectadas")
            ),
            "url_documento": item.get("pdf_url") or extras.get("pdf_url") or primary_doc,
            "content_type": content_type,
            "extras": {**extras, "source_table_intended": table_name, "content_type": content_type},
            "hash_deduplicacao": extras.get("content_hash") or item.get("hash_deduplicacao"),
            "ultima_coleta": datetime.now(timezone.utc).isoformat(),
        }
    )


def is_expired_deadline(deadline_iso):
    """Retorna True se o prazo já venceu (< hoje)."""
    if not deadline_iso:
        return False
    try:
        deadline = date.fromisoformat(str(deadline_iso)[:10])
        return deadline < date.today()
    except Exception:
        logger.warning("Prazo inválido encontrado: %s", deadline_iso)
        return False


def update_expired_editals_status() -> None:
    """
    Marca oportunidades com prazo_envio passado como encerradas / inativas.
    Não remove linhas (substitui delete_expired_editals).
    """
    today_iso = date.today().isoformat()
    try:
        supabase.table("edital").update({"situacao": "Encerrado", "ativo": False}).lt(
            "prazo_envio", today_iso
        ).execute()
        logger.info(
            "update_expired_editals_status: marcados Encerrado/ativo=false onde prazo_envio < %s",
            today_iso,
        )
    except Exception as exc:
        err = str(exc).lower()
        if "ativo" in err or "column" in err or "42703" in str(exc):
            try:
                supabase.table("edital").update({"situacao": "Encerrado"}).lt(
                    "prazo_envio", today_iso
                ).execute()
                logger.info(
                    "update_expired_editals_status: apenas situacao=Encerrado (coluna ativo indisponível)."
                )
            except Exception as exc2:
                logger.warning("update_expired_editals_status falhou: %s", exc2)
        else:
            logger.warning("update_expired_editals_status falhou: %s", exc)


def delete_expired_editals():
    """Obsoleto: não apaga mais registros. Use update_expired_editals_status()."""
    logger.warning(
        "delete_expired_editals() está obsoleto e não remove dados. "
        "Chamando update_expired_editals_status()."
    )
    update_expired_editals_status()


def fetch_edital_by_link(link: str) -> Optional[Dict[str, Any]]:
    if not link:
        return None
    try:
        r = supabase.table("edital").select("*").eq("link", str(link)).limit(1).execute()
        if r.data and isinstance(r.data, list) and len(r.data) > 0:
            return sanitize_for_postgres(r.data[0])
    except Exception as exc:
        logger.warning("fetch_edital_by_link falhou link=%s: %s", link, exc)
    return None


def fetch_extras_fragments(id_edital: int) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if not TABLES_AVAILABLE["edital_extra_campo"] or not id_edital:
        return out
    try:
        r = (
            supabase.table("edital_extra_campo")
            .select("chave", "valor")
            .eq("id_edital", id_edital)
            .execute()
        )
        for row in r.data or []:
            if not isinstance(row, dict):
                continue
            chave = row.get("chave")
            raw = row.get("valor")
            if chave is None:
                continue
            if isinstance(raw, str):
                try:
                    out[str(chave)] = json.loads(raw)
                except Exception:
                    out[str(chave)] = raw
            else:
                out[str(chave)] = raw
    except Exception as exc:
        logger.warning("fetch_extras_fragments id=%s: %s", id_edital, exc)
    return sanitize_for_postgres(out)


def _merge_db_row(
    existing: Optional[Dict[str, Any]],
    mapped: Dict[str, Any],
    merged_extras: Dict[str, Any],
    item_n: Dict[str, Any],
) -> Dict[str, Any]:
    """Mescla registro existente com novo payload sem degradar dados."""

    def _apply_filter_columns(row: Dict[str, Any]) -> None:
        if not EXTENDED_SCHEMA:
            return
        pseudo = {
            "titulo": row.get("titulo"),
            "tipo_recurso": item_n.get("tipo_recurso") or merged_extras.get("tipo_recurso"),
            "programa": item_n.get("programa"),
            "acao": item_n.get("acao"),
            "extras": merged_extras,
        }
        row.update(extras_to_filter_columns(pseudo, merged_extras))
        row["ultima_coleta"] = datetime.now(timezone.utc).isoformat()

    if not existing:
        row = dict(mapped)
        if EXTENDED_SCHEMA:
            row["extras"] = merged_extras
            _apply_filter_columns(row)
            if row.get("ativo") is None:
                row["ativo"] = True
        return sanitize_for_postgres(_strip_payload(row))

    row = dict(mapped)
    for key, new_val in mapped.items():
        old_val = existing.get(key)
        if key == "descricao":
            row[key] = merge_descricao(old_val, new_val)
        elif key in ("titulo", "fonte_recurso", "link"):
            row[key] = merge_scalar_prefer_non_empty(old_val, new_val) or new_val
        elif key == "valor_maximo":
            row[key] = new_val if new_val is not None else old_val
        elif key == "pdf_url":
            row[key] = merge_scalar_prefer_non_empty(old_val, new_val) or new_val
        elif key == "situacao":
            row[key] = new_val if not _is_empty(new_val) else old_val
        elif key == "publico_alvo":
            row[key] = merge_scalar_prefer_non_empty(old_val, new_val) or new_val
        else:
            row[key] = new_val if not _is_empty(new_val) else old_val

    if EXTENDED_SCHEMA and existing:
        # Preserva colunas espelho já gravadas se o novo payload não as trouxer (evita apagar titulo_original, pdf_resumo, etc.)
        for k in _EXTENDED_EXTRA_COLUMNS:
            if k == "extras":
                continue
            if not _is_empty(row.get(k)):
                continue
            old_v = existing.get(k)
            if not _is_empty(old_v):
                row[k] = old_v

    if EXTENDED_SCHEMA:
        row["extras"] = merged_extras
        _apply_filter_columns(row)
        if row.get("ativo") is None:
            row["ativo"] = (
                existing.get("ativo") if existing.get("ativo") is not None else True
            )

    return sanitize_for_postgres(_strip_payload(row))


def _rebuild_merged_extras(
    existing: Optional[Dict[str, Any]],
    extras_new: Dict[str, Any],
    *,
    taxonomy_replace_keys: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """
    Reconstrói extras fundindo BD + payload.

    Se `taxonomy_replace_keys` (ex.: {'setor_estrategico'}) for passado, após o merge
    normal substitui essas chaves pelo valor do payload novo quando não vazio — evita
    união de listas que infla setores após correções taxonómicas curadas.
    """
    existing_json = {}
    if existing and isinstance(existing.get("extras"), dict):
        existing_json = existing["extras"]
    old_fragments = {}
    if existing and existing.get("id_edital"):
        old_fragments = fetch_extras_fragments(int(existing["id_edital"]))
    base = merge_extras_dict(old_fragments, existing_json)
    merged = merge_extras_dict(base, extras_new)
    if taxonomy_replace_keys:
        for k in taxonomy_replace_keys:
            nv = extras_new.get(k)
            if _is_empty(nv):
                continue
            if isinstance(nv, (dict, list)):
                merged[k] = deepcopy(nv)
            else:
                merged[k] = nv
    return sanitize_for_postgres(merged)


def detect_field_changes(old_record: Optional[Dict[str, Any]], new_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Detecta mudanças simples campo a campo entre registro antigo e novo payload.
    Apenas comparação em memória; sem efeitos colaterais.
    """
    old = old_record if isinstance(old_record, dict) else {}
    new = new_payload if isinstance(new_payload, dict) else {}
    keys = sorted(set(old.keys()) | set(new.keys()))
    changes: List[Dict[str, Any]] = []
    for k in keys:
        ov = old.get(k)
        nv = new.get(k)
        if ov == nv:
            continue
        changes.append({"campo": k, "valor_antigo": ov, "valor_novo": nv})
    return changes


def build_history_events(old_record: Optional[Dict[str, Any]], new_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Constrói eventos de histórico para futura persistência em edital_historico.
    Não grava nada; apenas retorna estrutura de eventos.
    """
    changes = detect_field_changes(old_record, new_payload)
    events: List[Dict[str, Any]] = []
    if not old_record:
        events.append(
            {
                "tipo_evento": "criado",
                "campo": None,
                "valor_antigo": None,
                "valor_novo": None,
                "valor_antigo_json": None,
                "valor_novo_json": None,
                "metadata": {"changes": len(changes)},
            }
        )
        return events

    for ch in changes:
        campo = ch["campo"]
        ov = ch["valor_antigo"]
        nv = ch["valor_novo"]
        tipo = "atualizado"
        if campo == "prazo_envio":
            tipo = "prazo_alterado"
        elif campo in ("valor_maximo", "valor_minimo", "valor_total_texto"):
            tipo = "valor_alterado"
        elif campo == "situacao":
            tipo = "situacao_alterada"
        elif campo == "pdf_url" and _is_empty(ov) and not _is_empty(nv):
            tipo = "pdf_adicionado"
        elif campo == "extras" and isinstance(nv, dict) and isinstance(ov, dict):
            docs_old = ov.get("documentos") if isinstance(ov.get("documentos"), list) else []
            docs_new = nv.get("documentos") if isinstance(nv.get("documentos"), list) else []
            if len(docs_new) > len(docs_old):
                tipo = "documento_adicionado"
            else:
                tipo = "merge_extras"
        elif campo in ("tipo_recurso", "tipo_oportunidade", "area", "perfil_ideal", "setor_economico", "area_cientifica", "area_tecnologica", "setor_estrategico"):
            tipo = "classificacao_alterada"

        evt = {
            "tipo_evento": tipo,
            "campo": campo,
            "valor_antigo": None if isinstance(ov, (dict, list)) else ov,
            "valor_novo": None if isinstance(nv, (dict, list)) else nv,
            "valor_antigo_json": ov if isinstance(ov, (dict, list)) else None,
            "valor_novo_json": nv if isinstance(nv, (dict, list)) else None,
            "metadata": {},
        }
        events.append(evt)
    return events


def save_history_events(id_edital: int, events: List[Dict[str, Any]], id_execucao: Optional[str] = None) -> None:
    """
    Persiste eventos em public.edital_historico quando a tabela existir.
    Falhas não quebram o loader.
    """
    if not id_edital or not isinstance(events, list) or not events:
        return
    for ev in events:
        try:
            row = {
                "id_edital": id_edital,
                "tipo_evento": ev.get("tipo_evento") or "atualizado",
                "campo": ev.get("campo"),
                "valor_antigo": ev.get("valor_antigo"),
                "valor_novo": ev.get("valor_novo"),
                "valor_antigo_json": ev.get("valor_antigo_json"),
                "valor_novo_json": ev.get("valor_novo_json"),
                "fonte": ev.get("fonte"),
                "id_execucao": id_execucao,
                "metadata": ev.get("metadata") if isinstance(ev.get("metadata"), dict) else {},
            }
            supabase.table("edital_historico").insert(sanitize_for_postgres(row)).execute()
        except Exception as exc:
            logger.debug("save_history_events falhou id_edital=%s: %s", id_edital, exc)


def save_detail_tables(id_edital: int, extras: Dict[str, Any]) -> None:
    """Persiste anexos e extras fragmentados com deduplicação (limpa antes de reinserir)."""
    if not extras or not id_edital:
        return

    if TABLES_AVAILABLE["edital_anexo"]:
        anexos = extras.get("anexos")
        if isinstance(anexos, str):
            try:
                anexos = json.loads(anexos)
            except Exception:
                anexos = None
        if isinstance(anexos, list) and anexos:
            try:
                supabase.table("edital_anexo").delete().eq("id_edital", id_edital).execute()
            except Exception as exc:
                logger.warning("Falha ao limpar anexos id_edital=%s: %s", id_edital, exc)
            for anexo in anexos_dedupe_url(anexos):
                if not isinstance(anexo, dict):
                    continue
                try:
                    supabase.table("edital_anexo").insert(
                        sanitize_for_postgres(
                            {
                                "id_edital": id_edital,
                                "nome": anexo.get("nome"),
                                "url": anexo.get("url"),
                                "tipo": anexo.get("tipo"),
                            }
                        )
                    ).execute()
                except Exception as exc:
                    logger.warning("Falha ao inserir anexo do edital %s: %s", id_edital, exc)

    if TABLES_AVAILABLE["edital_extra_campo"]:
        try:
            supabase.table("edital_extra_campo").delete().eq("id_edital", id_edital).execute()
        except Exception as exc:
            logger.warning("Falha ao limpar edital_extra_campo id=%s: %s", id_edital, exc)
        for ordem, (chave, valor) in enumerate(sorted(extras.items(), key=lambda kv: str(kv[0]))):
            if chave in _SKIP_EXTRA_CAMPO_KEYS:
                continue
            try:
                valor_limpo = sanitize_for_postgres(valor)
                val_str = (
                    json.dumps(valor_limpo, ensure_ascii=False)
                    if isinstance(valor_limpo, (dict, list))
                    else str(valor_limpo)
                )
                val_str = val_str.replace("\x00", "")
                if len(val_str) > _MAX_EXTRA_CAMPO_CHARS:
                    logger.debug(
                        "Omitindo extra '%s' por tamanho (%s) id_edital=%s",
                        chave,
                        len(val_str),
                        id_edital,
                    )
                    continue
                row_full: Dict[str, Any] = {
                    "id_edital": id_edital,
                    "chave": str(chave).replace("\x00", ""),
                    "valor": val_str,
                    "tipo_dado": _tipo_dado_extra_valor(valor),
                    "tamanho_valor": len(val_str),
                    "ordem": ordem,
                }
                try:
                    supabase.table("edital_extra_campo").insert(row_full).execute()
                except Exception as exc_full:
                    err = str(exc_full).lower()
                    if any(
                        s in err
                        for s in (
                            "tipo_dado",
                            "tamanho_valor",
                            "ordem",
                            "column",
                            "42703",
                            "schema",
                            "pgrst",
                        )
                    ):
                        supabase.table("edital_extra_campo").insert(
                            {
                                "id_edital": id_edital,
                                "chave": str(chave).replace("\x00", ""),
                                "valor": val_str,
                            }
                        ).execute()
                    else:
                        raise
            except Exception as exc:
                logger.warning("Falha ao inserir extra '%s' do edital %s: %s", chave, id_edital, exc)


def inserir_ou_atualizar_edital(edital: Dict[str, Any]) -> Tuple[str, Optional[int]]:
    """Insere ou atualiza um edital (upsert por link)."""
    try:
        edital = sanitize_for_postgres(sanitize_for_postgres(edital))
        res = supabase.table("edital").upsert(edital, on_conflict="link").execute()

        if res and hasattr(res, "data") and res.data and len(res.data) > 0:
            item_data = res.data[0]
            if isinstance(item_data, dict):
                id_edital = item_data.get("id_edital")
                return "ok", id_edital
        return "erro", None

    except Exception as e:
        logger.exception("Erro no upsert de edital link=%s", edital.get("link"))
        print(f"[ERRO SUPABASE] {e}")
        return "erro", None


def inserir_ou_atualizar_conteudo(table_name: str, row: Dict[str, Any]) -> Tuple[str, Optional[int]]:
    """Upsert em public.noticia/public.pesquisa por link."""
    if table_name not in ("noticia", "pesquisa"):
        return "destino_invalido", None
    if not TABLES_AVAILABLE.get(table_name):
        logger.warning("Tabela %s indisponivel; item nao sera gravado em edital.", table_name)
        return "tabela_indisponivel", None
    try:
        row = sanitize_for_postgres(row)
        res = supabase.table(table_name).upsert(row, on_conflict="link").execute()
        if res and hasattr(res, "data") and res.data and len(res.data) > 0:
            first = res.data[0]
            if isinstance(first, dict):
                return "ok", first.get(f"id_{table_name}") or first.get("id")
        return "ok", None
    except Exception as exc:
        logger.exception("Erro no upsert de %s link=%s", table_name, row.get("link"))
        print(f"[ERRO SUPABASE {table_name}] {exc}")
        return "erro", None


def upsert_routed_item(
    item_normalizado: Dict[str, Any],
    *,
    taxonomy_replace_keys: Optional[Set[str]] = None,
) -> Tuple[str, str, Optional[int]]:
    """Roteia item normalizado para edital, noticia ou pesquisa."""
    destination = get_destination_table(item_normalizado)
    if destination in ("noticia", "pesquisa"):
        row = map_to_content_schema(item_normalizado, destination)
        if not row.get("link"):
            return destination, "sem_link", None
        status, row_id = inserir_ou_atualizar_conteudo(destination, row)
        return destination, status, row_id
    mapped, extras_new = map_to_db_schema(item_normalizado)
    if not mapped.get("link"):
        return "edital", "sem_link", None
    if is_expired_deadline(mapped.get("prazo_envio")):
        mapped["situacao"] = mapped.get("situacao") or "Encerrado"
        if EXTENDED_SCHEMA:
            mapped["ativo"] = False
    existing = fetch_edital_by_link(str(mapped["link"]))
    merged_extras = _rebuild_merged_extras(existing, extras_new, taxonomy_replace_keys=taxonomy_replace_keys)
    payload = _merge_db_row(existing, mapped, merged_extras, item_normalizado)
    status, id_edital = inserir_ou_atualizar_edital(payload)
    if id_edital:
        save_detail_tables(id_edital, merged_extras)
    return "edital", status, id_edital


def load_standardized_json(file_path):
    """Lê um arquivo JSON padronizado e o carrega no banco."""
    print(f"\nCarregando: {file_path.name}")

    if not file_path.exists():
        logger.error("Arquivo não encontrado: %s", file_path)
        return

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            data = [data]

        sucessos = 0
        erros = 0
        marcados_encerrados = 0
        inseridos = 0
        atualizados = 0
        roteados_noticia = 0
        roteados_pesquisa = 0

        for item in data:
            try:
                item_normalizado = normalizar(item)
                destination = get_destination_table(item_normalizado)
                if destination in ("noticia", "pesquisa"):
                    status, row_id = inserir_ou_atualizar_conteudo(
                        destination,
                        map_to_content_schema(item_normalizado, destination),
                    )
                    if status == "ok":
                        sucessos += 1
                        if destination == "noticia":
                            roteados_noticia += 1
                        else:
                            roteados_pesquisa += 1
                    else:
                        erros += 1
                    _ = row_id
                    continue
                try:
                    try:
                        from opportunity_gate import evaluate_item_dict as _eval_item_gate
                    except ImportError:
                        from CORE.opportunity_gate import evaluate_item_dict as _eval_item_gate

                    _lg = _eval_item_gate(item_normalizado)
                    if not _lg.keep:
                        logger.info(
                            "Loader: skip opportunity_gate (%s) link=%s",
                            (_lg.rejection_reason or _lg.access_status or ""),
                            item_normalizado.get("link"),
                        )
                        continue
                except Exception:
                    logger.exception(
                        "Loader: falha ao avaliar opportunity_gate; item marcado suspeito link=%s",
                        item_normalizado.get("link"),
                    )
                    ex = item_normalizado.get("extras")
                    if not isinstance(ex, dict):
                        ex = {}
                        item_normalizado["extras"] = ex
                    ex.setdefault("validacao_status", "suspeito")
                    w = ex.setdefault("validacao_warnings", [])
                    if isinstance(w, list) and "opportunity_gate_eval_exception" not in w:
                        w.append("opportunity_gate_eval_exception")

                mapped, extras_new = map_to_db_schema(item_normalizado)

                if not mapped.get("link"):
                    continue

                if is_expired_deadline(mapped.get("prazo_envio")):
                    mapped["situacao"] = mapped.get("situacao") or "Encerrado"
                    marcados_encerrados += 1
                    if EXTENDED_SCHEMA:
                        mapped["ativo"] = False

                existing = fetch_edital_by_link(str(mapped["link"]))
                merged_extras = _rebuild_merged_extras(existing, extras_new)

                payload = _merge_db_row(existing, mapped, merged_extras, item_normalizado)

                status_code, id_edital = inserir_ou_atualizar_edital(payload)
                if id_edital:
                    if existing:
                        atualizados += 1
                    else:
                        inseridos += 1
                    save_detail_tables(id_edital, merged_extras)
                    sucessos += 1
                else:
                    erros += 1

                _ = status_code

            except Exception:
                logger.exception("Erro ao processar item de %s", file_path.name)
                erros += 1

        logger.info(
            "Carga arquivo=%s sucessos=%s inseridos=%s atualizados=%s "
            "roteados_noticia=%s roteados_pesquisa=%s "
            "itens_com_prazo_passado_marcados=%s erros=%s extended_schema=%s",
            file_path.name,
            sucessos,
            inseridos,
            atualizados,
            roteados_noticia,
            roteados_pesquisa,
            marcados_encerrados,
            erros,
            EXTENDED_SCHEMA,
        )
        print(
            f"Finalizado {file_path.name}: {sucessos} upserts OK "
            f"(novos ~{inseridos}, atualizados ~{atualizados}), "
            f"{roteados_noticia} noticias e {roteados_pesquisa} pesquisas roteadas, "
            f"{marcados_encerrados} com prazo vencido rotulados Encerrado/inativo, "
            f"{erros} erros. EDITALFINDER_EXTENDED_SCHEMA={EXTENDED_SCHEMA}"
        )

    except Exception as e:
        logger.exception("Erro ao ler arquivo %s", file_path)
        print(f"[ERRO AO LER ARQUIVO] {e}")


def _parse_loader_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Carrega ficheiros *_standardized.json no Supabase (upsert por link)."
    )
    p.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("EDITALFINDER_LOADER_WORKERS", "1") or "1"),
        help="Ficheiros JSON em paralelo (default: 1). Recomendado 2-4; cuidado com rate limits do Supabase.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_loader_cli()
    loader_workers = max(1, min(int(args.workers or 1), 12))

    detect_optional_tables()
    update_expired_editals_status()

    old_editais = get_current_db_editais()
    new_editais_buffer: List[Any] = []

    json_files = sorted(TRANSFORMER_DIR.glob("*_standardized.json"))
    if not json_files:
        print(f"Nenhum arquivo encontrado em {TRANSFORMER_DIR}")
        return

    print(f"Iniciando carregamento de {len(json_files)} arquivos...")
    print(
        "Schema estendido (extras JSONB + colunas de filtro): "
        f"{'ATIVO' if EXTENDED_SCHEMA else 'DESLIGADO'} — defina EDITALFINDER_EXTENDED_SCHEMA=true após migrar o banco."
    )

    for json_file in json_files:
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    new_editais_buffer.extend(data)
        except Exception:
            logger.exception("Falha ao ler arquivo para buffer de alertas %s", json_file)

    if loader_workers <= 1:
        for json_file in json_files:
            load_standardized_json(json_file)
    else:
        w = min(loader_workers, len(json_files))
        print(f"[loader] Paralelo: {w} workers, {len(json_files)} ficheiros.")
        with ThreadPoolExecutor(max_workers=w) as ex:
            futures = {ex.submit(load_standardized_json, jf): jf for jf in json_files}
            for fut in as_completed(futures):
                jf = futures[fut]
                try:
                    fut.result()
                except Exception:
                    logger.exception("Falha ao processar arquivo %s", jf)

    if process_alerts:
        print("\n--- PROCESSANDO ALERTAS INTELIGENTES ---")
        process_alerts(new_editais_buffer, old_editais)


if __name__ == "__main__":
    main()
