"""Coleta leve de páginas públicas do Banco do Nordeste (linhas de crédito / solicitação)."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from CORE.credito_brasil_onda_a_noise import crawler_link_exclude_extra, crawler_should_drop_item

SOURCE_KEY = "bnb"
LABEL = "BNB"

NOISE_URL = ("/imprensa/", "/noticia", "asset_publisher", "/open-finance")


def _is_relevant(item: dict) -> bool:
    link = str(item.get("link") or "").lower()
    title = str(item.get("titulo") or "").strip().lower()
    desc = str(item.get("descricao") or "")
    if crawler_should_drop_item(title, link, desc):
        return False
    if len(title) < 6:
        return False
    if any(x in link for x in NOISE_URL):
        return False
    if any(x in link for x in crawler_link_exclude_extra()):
        return False
    if "/voce/" in link and "emprestimo" not in link and "financiamento" not in link:
        return False
    hay = f"{title} {link}"
    return any(k in hay for k in ("credito", "crédito", "financ", "micro", "rural", "proposta", "produto", "servico"))


def main():
    config = {
        "source_label": LABEL,
        "listing_urls": [
            "https://www.bnb.gov.br/web/guest/produtos-e-servicos",
            "https://www.bnb.gov.br/web/guest/solicitacao-de-credito",
            "https://www.bnb.gov.br/web/guest/microcredito",
            "https://www.bnb.gov.br/web/guest/atividades-financiadas",
        ],
        "keywords": [
            "credito",
            "crédito",
            "financiamento",
            "micro",
            "rural",
            "emprestimo",
            "linha",
            "proposta",
            "financ",
        ],
        "avoid_keywords": ["ouvidoria", "open finance", "educacao financeira"],
        "link_url_exclude_substrings": list(
            dict.fromkeys(
                ["/imprensa/", "asset_publisher", "noticias/-/"] + crawler_link_exclude_extra()
            )
        ),
        "program_hint": "produtos_bnb",
        "allowed_domains": ["bnb.gov.br"],
        "max_items": 28,
        "max_links_per_page": 200,
        "http_timeout": 14,
        "setor_estrategico": "desenvolvimento_regional",
        "orgao_responsavel": "Banco do Nordeste",
        "instituicao": "Banco do Nordeste S.A.",
        "orgao_contratante": "BNB",
        "tipo_oportunidade": "programa_credito",
        "regiao": "nordeste",
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
        ex.setdefault("origem_portal", "Banco do Nordeste (bnb.gov.br)")
        ex["natureza_recurso"] = "reembolsavel"
        ex["reembolsavel"] = True
        ex["tipo_recurso"] = "credito"
        x["extras"] = ex
        x["tipo_recurso"] = "financiamento_reembolsavel"
        x["acao"] = "credito"
        filtered.append(x)
    items = filtered[:24]
    if not items:
        items = [
            {
                "titulo": "BNB — Produtos e serviços (crédito e financiamento)",
                "descricao": "Portal oficial de produtos, linhas de crédito e solicitação de crédito do Banco do Nordeste.",
                "link": "https://www.bnb.gov.br/web/guest/produtos-e-servicos",
                "fonte": LABEL,
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "produtos_bnb",
                "acao": "credito",
                "tipo_recurso": "financiamento_reembolsavel",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "nordeste",
                    "tipo_oportunidade": "programa_credito",
                    "origem_portal": "Banco do Nordeste (bnb.gov.br)",
                    "natureza_recurso": "reembolsavel",
                    "reembolsavel": True,
                    "metodo_extracao": "fallback_public_index",
                    "url_listagem": "https://www.bnb.gov.br/web/guest/produtos-e-servicos",
                    "url_detalhe": "https://www.bnb.gov.br/web/guest/produtos-e-servicos",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print(f"[{LABEL}] Fallback: índice público único.")
    save_outputs(Path(__file__).parent, SOURCE_KEY, items)
    print(f"[{LABEL}] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
