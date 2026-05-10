from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from keyword_taxonomy import KEYWORDS_INTEREST


def main():
    config = {
        "source_label": "AMAZUL",
        # Listagens antigas (/licitacoes, /chamadas-publicas) retornam 404; conteúdo em Acesso à Informação.
        "listing_urls": [
            "https://www.amazul.mar.mil.br/acesso-a-informacao/licitacoes-e-contratos",
        ],
        "keywords": KEYWORDS_INTEREST
        + [
            "amazul",
            "submarino",
            "nuclear",
            "defesa",
            "licit",
            "pregão",
            "pregao",
            "edital",
            "chamada pública",
            "chamada publica",
            "contrata",
            "aquisição",
            "aquisicao",
        ],
        "avoid_keywords": [
            "manual tecnico",
            "concurso",
            "concursos",
            "estagio",
            "estágio",
            "noticia",
            "notícia",
            "multimidia",
            "galeria",
            "comandante",
        ],
        "link_url_exclude_substrings": [
            "/noticias/",
            "/noticia/",
            "/multimidia/",
            "/concursos/",
            "/concurso/",
            "/estagio",
            "/estágio",
            "/contato",
            "/fale-conosco",
            "/cookies",
            "/privacidade",
            "facebook.com",
            "instagram.com",
            "twitter.com",
            "youtube.com",
        ],
        "link_url_must_contain_any": [
            "/licit",
            "/chamada",
            "/edital",
            "/preg",
            "/compras",
            "/contrat",
            ".pdf",
            "modalidade",
            "uasg",
        ],
        "link_path_min_depth": 2,
        "program_hint": "AMAZUL",
        "allowed_domains": ["amazul.mar.mil.br"],
        "max_items": 20,
        "max_links_per_page": 120,
        "http_timeout": 15,
        "setor_estrategico": "",
        "orgao_responsavel": "AMAZUL",
        "instituicao": "AMAZUL",
        "orgao_contratante": "AMAZUL",
        "tipo_oportunidade": "",
        "area_cientifica": [],
        "area_tecnologica": [],
        "subtema_padrao": [],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[AMAZUL] Falha na coleta: {exc}")
        items = []
    if not items:
        print("[AMAZUL] Nenhum item com evidência de licitação/chamada (sem fallback de índice).")
    save_outputs(Path(__file__).parent, "amazul", items)
    print(f"[AMAZUL] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
