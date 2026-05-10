import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_aneel import AneelScraper
from utils_aneel import is_deadline_valid
import re

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "aneel_editais.json"
CSV_PATH = OUTPUT_DIR / "aneel_editais.csv"


def _enrich_item(item: dict) -> dict:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras.update(
        {
            "pais": extras.get("pais") or "Brasil",
            "regiao": extras.get("regiao") or "brasil",
            "orgao_responsavel": extras.get("orgao_responsavel") or "ANEEL",
            "instituicao": extras.get("instituicao") or "Agência Nacional de Energia Elétrica",
            "orgao_contratante": extras.get("orgao_contratante") or "ANEEL",
            "setor_estrategico": extras.get("setor_estrategico") or "energia_eletrica",
            "tipo_oportunidade": extras.get("tipo_oportunidade") or "chamada_publica",
            "tipo_recurso": extras.get("tipo_recurso") or "fomento",
            "natureza_recurso": extras.get("natureza_recurso") or "nao_reembolsavel",
            "reembolsavel": extras.get("reembolsavel") if extras.get("reembolsavel") is not None else False,
            "area_cientifica": extras.get("area_cientifica") or ["energia", "engenharia", "sustentabilidade"],
            "area_tecnologica": extras.get("area_tecnologica") or ["redes_eletricas", "eficiencia_energetica", "geracao"],
            "url_listagem": extras.get("url_listagem") or "https://www.gov.br/aneel/pt-br",
            "url_detalhe": extras.get("url_detalhe") or item.get("link") or "",
            "metodo_extracao": extras.get("metodo_extracao") or "html_listing_detail",
            "nivel_sensibilidade": extras.get("nivel_sensibilidade") or "publico_institucional",
        }
    )
    item["extras"] = extras
    item.setdefault("valor", None)
    item.setdefault("programa", "aneel")
    item.setdefault("acao", "chamada_publica")
    item.setdefault("tipo_recurso", "fomento")
    return item


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").strip().lower()
    desc = str(item.get("descricao") or "").strip().lower()
    link = str(item.get("link") or "").strip().lower()
    text = f"{title} {desc} {link}"
    if not title or len(title) < 8:
        return False
    if title in {"baixar", "edital", "english version"}:
        return False
    if any(k in text for k in ["sorry, you have been blocked", "conteúdo restrito", "conteudo restrito"]):
        return False
    if any(k in text for k in ["programa de estágio", "governança em privacidade", "acoes-e-programas/esg"]):
        return False
    if link.endswith(".csv"):
        return False
    return any(k in text for k in ["chamada", "edital", "pdi", "pesquisa", "desenvolvimento", ".pdf"])


def _clean_description(text: str) -> str:
    out = re.sub(r"https?://\S+", " ", str(text or ""), flags=re.IGNORECASE)
    out = out.replace("Atenção! Seu navegador não pode executar javascript.", " ")
    out = re.sub(r"\s+", " ", out).strip()
    return out


def _fallback_items() -> list:
    return [
        _enrich_item(
            {
                "titulo": "ANEEL - Página de Editais e Programas",
                "descricao": "Índice público de editais, chamadas e programas da ANEEL.",
                "link": "https://www.gov.br/aneel/pt-br",
                "fonte": "ANEEL",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "extras": {"metodo_extracao": "fallback_public_index"},
            }
        )
    ]

def save_json(data: list):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_csv(data: list):
    if not data:
        return
    keys = data[0].keys()
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    scraper = AneelScraper()
    print("Coletando editais, programas e fomento da ANEEL (Setor de Energia)...")
    
    # Extrai a lista e processa detalhes
    editais = scraper.extract_editais()
    
    final_data = []
    for edital in editais:
        # Filtro de deadline final
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            print(f"Pulando edital vencido: {edital.titulo[:50]} ({edital.fim_inscricao})")
            continue
            
        print(f"Processando: {edital.titulo[:100]}")
        item = _enrich_item(edital.to_dict())
        item["descricao"] = _clean_description(item.get("descricao"))
        if _is_relevant_item(item):
            final_data.append(item)

    if not final_data:
        final_data = _fallback_items()
        print("[ANEEL] Fallback ativado por ausência de itens.")
    save_json(final_data)
    save_csv(final_data)
    print(f"Sucesso! {len(final_data)} editais e programas da ANEEL salvos em {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
