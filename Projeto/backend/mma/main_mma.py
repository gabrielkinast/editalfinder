import json
import csv
import os
import re
from pathlib import Path
from datetime import datetime
from extrair_informacoes_mma import MMAScraper
from utils_mma import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "mma_editais.json"
CSV_PATH = OUTPUT_DIR / "mma_editais.csv"

# Índices genéricos do gov.br (título curto / seção), sem slug de edital ou consulta específica no link.
_HUB_TITLE_EXACT = frozenset(
    {
        "consultas públicas",
        "consultas publicas",
        "consultas públicas (secex)",
        "consultas publicas (secex)",
        "gov.br",
        "início",
        "inicio",
        "home",
    }
)
_HUB_TITLE_PREFIX = (
    "3.2 audiências e consultas",
    "3.2 audiencias e consultas",
    "3.5. editais de chamamento",
    "3.5 editais de chamamento",
)


def _title_norm(item: dict) -> str:
    t = str(item.get("titulo") or "").lower().strip()
    return re.sub(r"\s+", " ", t)


def _link_suggests_opportunity(link: str) -> bool:
    low = link.lower()
    return any(
        s in low
        for s in (
            "/edital",
            "edital-",
            "editais/",
            "chamamento-publico",
            "chamamento_publico",
            "consulta-publica",
            "consulta_publica",
            "consulta-audiencia",
            "selecao-publica",
            "seleção-pública",
            "/fnma",
            "/fnme",
            ".pdf",
        )
    )


def _is_mma_hub_noise(item: dict) -> bool:
    """Descarta páginas-índice (ex.: só 'Consultas Públicas') sem URL de oportunidade concreta."""
    title = _title_norm(item)
    link = str(item.get("link") or "").lower()
    if "gov.br/mma" not in link:
        return True
    if title in _HUB_TITLE_EXACT:
        return not _link_suggests_opportunity(link)
    if any(title.startswith(p) for p in _HUB_TITLE_PREFIX):
        return not _link_suggests_opportunity(link)
    if title in ("editais de chamamento público", "editais de chamamento publico", "audiências e consultas públicas", "audiencias e consultas publicas"):
        return not _link_suggests_opportunity(link)
    return False


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if any(k in text for k in ["perguntas frequentes", "manual", "normativos", "governança", "governanca", "destinação de florestas", "programa de gestão e desempenho", "servidores"]):
        return False
    if _is_mma_hub_noise(item):
        return False
    return any(k in text for k in ["edital", "chamada", "chamamento", "consulta pública", "inscri", "submiss"])


def _enrich_item(item: dict) -> dict:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras.update(
        {
            "pais": extras.get("pais") or "Brasil",
            "regiao": extras.get("regiao") or "brasil",
            "orgao_responsavel": extras.get("orgao_responsavel") or "MMA/FNMA",
            "instituicao": extras.get("instituicao") or "Ministério do Meio Ambiente",
            "orgao_contratante": extras.get("orgao_contratante") or "MMA/FNMA",
            "setor_estrategico": extras.get("setor_estrategico") or "meio_ambiente",
            "tipo_oportunidade": extras.get("tipo_oportunidade") or "chamada_publica",
            "tipo_recurso": extras.get("tipo_recurso") or "fomento",
            "natureza_recurso": extras.get("natureza_recurso") or "nao_reembolsavel",
            "reembolsavel": extras.get("reembolsavel") if extras.get("reembolsavel") is not None else False,
            "area_cientifica": extras.get("area_cientifica") or ["ecologia", "sustentabilidade", "clima"],
            "area_tecnologica": extras.get("area_tecnologica") or ["descarbonizacao", "bioeconomia", "conservacao"],
            "url_listagem": extras.get("url_listagem") or "https://www.gov.br/mma/pt-br",
            "url_detalhe": extras.get("url_detalhe") or item.get("link") or "",
            "metodo_extracao": extras.get("metodo_extracao") or "html_listing_detail",
            "nivel_sensibilidade": extras.get("nivel_sensibilidade") or "publico_institucional",
        }
    )
    item["extras"] = extras
    item.setdefault("valor", None)
    item.setdefault("programa", "mma_fnma")
    item.setdefault("acao", "chamada_publica")
    item.setdefault("tipo_recurso", "fomento")
    return item


def _fallback_items() -> list:
    return [
        _enrich_item(
            {
                "titulo": "MMA/FNMA - Página de Editais e Programas",
                "descricao": "Índice público de editais e programas do MMA/FNMA.",
                "link": "https://www.gov.br/mma/pt-br",
                "fonte": "MMA/FNMA",
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
    
    scraper = MMAScraper()
    print("Coletando editais e programas do MMA / FNMA...")
    
    # Extrai a lista e processa detalhes
    editais = scraper.extract_editais()
    
    final_data = []
    for edital in editais:
        # Filtro de deadline final
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            print(f"Pulando edital vencido: {edital.titulo[:50]} ({edital.fim_inscricao})")
            continue
            
        print(f"Processando detalhes: {edital.titulo[:100]}")
        item = _enrich_item(edital.to_dict())
        if _is_relevant_item(item):
            final_data.append(item)

    if not final_data:
        final_data = _fallback_items()
        print("[MMA] Fallback ativado por ausência de itens.")
    save_json(final_data)
    save_csv(final_data)
    print(f"Sucesso! {len(final_data)} editais e programas do MMA / FNMA salvos em {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
