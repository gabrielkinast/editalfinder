"""Coleta leve — Banco da Amazônia (linhas de fomento / crédito empresarial e rural)."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from CORE.credito_brasil_onda_a_noise import crawler_link_exclude_extra, crawler_should_drop_item

SOURCE_KEY = "banco_da_amazonia"
LABEL = "BASA"


def _is_relevant(item: dict) -> bool:
    link = str(item.get("link") or "").lower()
    title = str(item.get("titulo") or "").strip().lower()
    desc = str(item.get("descricao") or "")
    # Recovery A: foco empresas/agro — não PF genérico nem microsite soluções PF.
    if "/solucoes-pf/" in link or "/pessoa-fisica" in link:
        return False
    if crawler_should_drop_item(title, link, desc):
        return False
    if len(title) < 5:
        return False
    if any(x in link for x in crawler_link_exclude_extra()):
        return False
    if any(
        x in link
        for x in (
            "/o-banco/",
            "educacao-financeira",
            "seguros",
            "cartao-de-credito",
            "renegociacao",
            "conta-pj",
            "/concurso",
            "internet-banking",
            "fale-conosco",
            "ouvidoria",
        )
    ):
        if "linhas-de-fomento" not in link and "credito-e-financiamento" not in link and "financiamento-agro" not in link:
            return False
    hay = f"{title} {link}"
    return any(
        k in hay
        for k in (
            "credito",
            "crédito",
            "financ",
            "fomento",
            "fn",
            "pronaf",
            "agro",
            "finame",
            "empresa",
            "linha",
        )
    )


def main():
    config = {
        "source_label": LABEL,
        "listing_urls": [
            "https://www.bancoamazonia.com.br/empresas/credito-e-financiamentos",
            "https://www.bancoamazonia.com.br/rural/credito-e-financiamento-agro",
            "https://www.bancoamazonia.com.br/linhas-de-fomento/fno",
        ],
        "keywords": [
            "credito",
            "crédito",
            "financiamento",
            "fomento",
            "fn",
            "pronaf",
            "finame",
            "agro",
            "linha",
            "empresa",
        ],
        "avoid_keywords": ["cartao de credito", "seguros", "investimento", "internet banking", "abra sua conta"],
        "link_url_exclude_substrings": list(dict.fromkeys(crawler_link_exclude_extra())),
        "program_hint": "linhas_basa",
        "allowed_domains": ["bancoamazonia.com.br"],
        "max_items": 30,
        "max_links_per_page": 220,
        "http_timeout": 16,
        "setor_estrategico": "desenvolvimento_regional",
        "orgao_responsavel": "Banco da Amazônia",
        "instituicao": "Banco da Amazônia S.A.",
        "orgao_contratante": "BASA",
        "tipo_oportunidade": "programa_credito",
        "regiao": "norte",
        "area_cientifica": [],
        "area_tecnologica": ["inovacao", "agro"],
        "subtema_padrao": ["credito", "financiamento", "desenvolvimento_regional", "agro"],
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
        ex.setdefault("origem_portal", "Banco da Amazônia (bancoamazonia.com.br)")
        ex["natureza_recurso"] = "reembolsavel"
        ex["reembolsavel"] = True
        ex["tipo_recurso"] = "credito"
        x["extras"] = ex
        x["tipo_recurso"] = "financiamento_reembolsavel"
        x["acao"] = "credito"
        filtered.append(x)
    items = filtered[:26]
    if not items:
        items = [
            {
                "titulo": "BASA — Crédito e financiamentos para empresas",
                "descricao": "Linhas de crédito, FNO e produtos de fomento divulgados pelo Banco da Amazônia.",
                "link": "https://www.bancoamazonia.com.br/empresas/credito-e-financiamentos",
                "fonte": LABEL,
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "linhas_basa",
                "acao": "credito",
                "tipo_recurso": "financiamento_reembolsavel",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "norte",
                    "tipo_oportunidade": "programa_credito",
                    "origem_portal": "Banco da Amazônia (bancoamazonia.com.br)",
                    "natureza_recurso": "reembolsavel",
                    "reembolsavel": True,
                    "metodo_extracao": "fallback_public_index",
                    "url_listagem": "https://www.bancoamazonia.com.br/empresas/credito-e-financiamentos",
                    "url_detalhe": "https://www.bancoamazonia.com.br/empresas/credito-e-financiamentos",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print(f"[{LABEL}] Fallback: índice público único.")
    save_outputs(Path(__file__).parent, SOURCE_KEY, items)
    print(f"[{LABEL}] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
