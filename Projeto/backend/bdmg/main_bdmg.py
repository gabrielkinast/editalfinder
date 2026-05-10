"""Coleta leve — BDMG (linhas de crédito MG)."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from CORE.credito_brasil_onda_a_noise import crawler_link_exclude_extra, crawler_should_drop_item

SOURCE_KEY = "bdmg"
LABEL = "BDMG"


def _is_relevant(item: dict) -> bool:
    link = str(item.get("link") or "").lower()
    title = str(item.get("titulo") or "").strip().lower()
    desc = str(item.get("descricao") or "")
    if crawler_should_drop_item(title, link, desc):
        return False
    if len(title) < 4 and "#" not in link:
        return False
    if "relacao-investidores" in link or "transparencia" in link:
        return False
    if any(x in link for x in crawler_link_exclude_extra()):
        return False
    hay = f"{title} {link}"
    return any(
        k in hay
        for k in (
            "credito",
            "crédito",
            "bdmg",
            "pronampe",
            "empresa",
            "micro",
            "pequena",
            "media",
            "giro",
            "fungetur",
            "verde",
            "linha",
            "programa",
        )
    )


def main():
    config = {
        "source_label": LABEL,
        "listing_urls": [
            "https://www.bdmg.mg.gov.br/linhaspermanentes",
            "https://www.bdmg.mg.gov.br/micro-empresa",
            "https://www.bdmg.mg.gov.br/pequenas-empresas",
        ],
        "keywords": [
            "credito",
            "crédito",
            "bdmg",
            "pronampe",
            "empresa",
            "micro",
            "giro",
            "fungetur",
            "verde",
            "financ",
            "linha",
            "programa",
        ],
        "avoid_keywords": ["relacao-investidores", "relatório", "regulamento cvm"],
        "link_url_exclude_substrings": list(
            dict.fromkeys(["/relacao-investidores"] + crawler_link_exclude_extra())
        ),
        "program_hint": "linhas_bdmg",
        "allowed_domains": ["bdmg.mg.gov.br"],
        "max_items": 32,
        "max_links_per_page": 260,
        "http_timeout": 15,
        "setor_estrategico": "desenvolvimento_regional",
        "orgao_responsavel": "BDMG",
        "instituicao": "Banco de Desenvolvimento de Minas Gerais",
        "orgao_contratante": "BDMG",
        "tipo_oportunidade": "programa_credito",
        "regiao": "sudeste",
        "area_cientifica": [],
        "area_tecnologica": ["inovacao"],
        "subtema_padrao": ["credito", "financiamento", "desenvolvimento_regional"],
        "enrich_meta_tags": True,
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[{LABEL}] Falha na coleta: {exc}")
        items = []
    seen = set()
    filtered = []
    for x in items:
        if not _is_relevant(x):
            continue
        key = str(x.get("link") or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        ex = x.get("extras") if isinstance(x.get("extras"), dict) else {}
        ex.setdefault("origem_portal", "BDMG (bdmg.mg.gov.br)")
        ex.setdefault("estado", "MG")
        ex["natureza_recurso"] = "reembolsavel"
        ex["reembolsavel"] = True
        ex["tipo_recurso"] = "credito"
        x["extras"] = ex
        x["tipo_recurso"] = "financiamento_reembolsavel"
        x["acao"] = "credito"
        filtered.append(x)
    items = filtered[:28]
    if not items:
        items = [
            {
                "titulo": "BDMG — Linhas de crédito",
                "descricao": "Portal oficial do BDMG com linhas permanentes e programas para empresas em Minas Gerais.",
                "link": "https://www.bdmg.mg.gov.br/linhaspermanentes",
                "fonte": LABEL,
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "linhas_bdmg",
                "acao": "credito",
                "tipo_recurso": "financiamento_reembolsavel",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "sudeste",
                    "estado": "MG",
                    "tipo_oportunidade": "programa_credito",
                    "origem_portal": "BDMG (bdmg.mg.gov.br)",
                    "natureza_recurso": "reembolsavel",
                    "reembolsavel": True,
                    "metodo_extracao": "fallback_public_index",
                    "url_listagem": "https://www.bdmg.mg.gov.br/linhaspermanentes",
                    "url_detalhe": "https://www.bdmg.mg.gov.br/linhaspermanentes",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print(f"[{LABEL}] Fallback: índice público único.")
    save_outputs(Path(__file__).parent, SOURCE_KEY, items)
    print(f"[{LABEL}] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
