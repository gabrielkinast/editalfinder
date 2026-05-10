from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from keyword_taxonomy import KEYWORDS_INTEREST


def main():
    # Rotas gov.br/dcta|ita|iae/pt-br/* passaram a responder 404 (HTML/JSON) em verificações de 2026-05;
    # manter URLs históricas até mapear o novo hub (FAB, outro domínio ou PNCP) sem inventar dados.
    config = {
        "source_label": "DCTA ITA IAE",
        "listing_urls": [
            "https://www.gov.br/dcta/pt-br/chamamentos-e-licitacoes",
            "https://www.gov.br/dcta/pt-br/editais",
            "https://www.gov.br/ita/pt-br/chamamentos-e-licitacoes",
            "https://www.gov.br/ita/pt-br/editais",
            "https://www.gov.br/iae/pt-br/chamamentos-e-licitacoes",
            "https://www.gov.br/iae/pt-br/editais",
        ],
        "keywords": KEYWORDS_INTEREST
        + [
            "dcta",
            "ita",
            "iae",
            "fab",
            "aeronautica",
            "aeronáutica",
            "edital",
            "chamada",
            "licit",
            "pregão",
            "pregao",
            "compra",
            "contrata",
            "fomento",
            "pesquisa",
            "mestrado",
            "doutorado",
            "bolsa",
            "seleção",
            "selecao",
            "processo seletivo",
        ],
        "avoid_keywords": [
            "manual tecnico",
            "noticia",
            "notícia",
            "galeria",
            "agenda institucional",
            "mapa do site",
            "cookies",
            "politica de privacidade",
            "política de privacidade",
            "fale conosco",
            "ouvidoria",
            "acesso à informação",
            "acesso a informacao",
        ],
        "link_url_exclude_substrings": [
            "/noticias/",
            "/notícias/",
            "/concursos/",
            "/concurso-publico/",
            "/acesso-a-informacao",
            "/acesso-a-informação",
            "/contato",
            "/servicos/",
            "/serviços/",
            "facebook.com",
            "instagram.com",
            "twitter.com",
            "youtube.com",
            "linkedin.com",
        ],
        "link_url_must_contain_any": [
            "/dcta/",
            "/ita/",
            "/iae/",
            "edital",
            "chamada",
            "licit",
            "preg",
            "contrat",
            "compras",
            "selecao",
            "seleção",
            "processo-seletivo",
            ".pdf",
        ],
        "link_path_min_depth": 3,
        "program_hint": "DCTA / ITA / IAE",
        "allowed_domains": ["gov.br"],
        "max_items": 25,
        "max_links_per_page": 150,
        "http_timeout": 18,
        "setor_estrategico": "",
        "orgao_responsavel": "DCTA/ITA/IAE",
        "instituicao": "Comando da Aeronáutica",
        "orgao_contratante": "DCTA/ITA/IAE",
        "tipo_oportunidade": "",
        "area_cientifica": [],
        "area_tecnologica": [],
        "subtema_padrao": [],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[DCTA_ITA_IAE] Falha na coleta: {exc}")
        items = []
    if not items:
        print("[DCTA_ITA_IAE] Nenhum item com evidência (sem fallback de índice institucional).")
    save_outputs(
        Path(__file__).parent,
        "dcta_ita_iae",
        items,
        failure_reason=(
            "Nenhum item com evidencia; URLs historicas gov.br/dcta|ita|iae retornam 404 "
            "ou nao possuem hub atual mapeado. Sem fallback institucional."
        )
        if not items
        else None,
        collection_failed=not items,
    )
    print(f"[DCTA_ITA_IAE] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
