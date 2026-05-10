"""Coleta leve — AgeRio (linhas de crédito RJ); exclui notícias genéricas na filtragem."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from CORE.credito_brasil_onda_a_noise import crawler_link_exclude_extra, crawler_should_drop_item

SOURCE_KEY = "agerio"
LABEL = "AGERIO"

def _is_actionable_credit(item: dict) -> bool:
    link = str(item.get("link") or "").lower()
    title = str(item.get("titulo") or "").strip().lower()
    desc = str(item.get("descricao") or "")
    if crawler_should_drop_item(title, link, desc):
        return False
    if any(x in link for x in crawler_link_exclude_extra()):
        return False
    if "/noticias/" in link or "/sem-categoria/" in link:
        return False
    if "/agerio-orienta/" in link:
        return False
    hay = f"{title} {link}"
    if len(title) < 5 and "/#" in link:
        return False
    return any(
        k in hay
        for k in (
            "credito",
            "crédito",
            "linha",
            "financ",
            "micro",
            "empresa",
            "inov",
            "programa",
            "empreed",
        )
    )


def main():
    config = {
        "source_label": LABEL,
        "listing_urls": [
            "https://www.agerio.com.br/linhas-de-credito/",
            "https://www.agerio.com.br/areas-de-atuacao/tipo/empresas/",
            "https://www.agerio.com.br/",
        ],
        "keywords": [
            "credito",
            "crédito",
            "linha",
            "financ",
            "micro",
            "empresa",
            "inov",
            "programa",
            "empreendedor",
            "rio",
        ],
        "avoid_keywords": [],
        "link_url_exclude_substrings": list(
            dict.fromkeys(["/noticias/", "/sem-categoria/"] + crawler_link_exclude_extra())
        ),
        "program_hint": "linhas_agerio",
        "allowed_domains": ["agerio.com.br"],
        "max_items": 26,
        "max_links_per_page": 200,
        "http_timeout": 15,
        "setor_estrategico": "desenvolvimento_regional",
        "orgao_responsavel": "AgeRio",
        "instituicao": "AgeRio — Agência de Fomento do Estado do Rio de Janeiro",
        "orgao_contratante": "AgeRio",
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
        if not _is_actionable_credit(x):
            continue
        key = str(x.get("link") or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        ex = x.get("extras") if isinstance(x.get("extras"), dict) else {}
        ex.setdefault("origem_portal", "AgeRio (agerio.com.br)")
        ex.setdefault("estado", "RJ")
        ex["natureza_recurso"] = "reembolsavel"
        ex["reembolsavel"] = True
        ex["tipo_recurso"] = "credito"
        x["extras"] = ex
        x["tipo_recurso"] = "financiamento_reembolsavel"
        x["acao"] = "credito"
        filtered.append(x)
    items = filtered[:22]
    if not items:
        items = [
            {
                "titulo": "AgeRio — Linhas de crédito",
                "descricao": "Página oficial de linhas de crédito da AgeRio para empresas e segmentos no Estado do Rio.",
                "link": "https://www.agerio.com.br/linhas-de-credito/",
                "fonte": LABEL,
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "linhas_agerio",
                "acao": "credito",
                "tipo_recurso": "financiamento_reembolsavel",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "sudeste",
                    "estado": "RJ",
                    "tipo_oportunidade": "programa_credito",
                    "origem_portal": "AgeRio (agerio.com.br)",
                    "natureza_recurso": "reembolsavel",
                    "reembolsavel": True,
                    "metodo_extracao": "fallback_public_index",
                    "url_listagem": "https://www.agerio.com.br/linhas-de-credito/",
                    "url_detalhe": "https://www.agerio.com.br/linhas-de-credito/",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print(f"[{LABEL}] Fallback: índice público único.")
    save_outputs(Path(__file__).parent, SOURCE_KEY, items)
    print(f"[{LABEL}] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
