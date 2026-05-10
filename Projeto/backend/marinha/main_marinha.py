from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from keyword_taxonomy import KEYWORDS_INTEREST


def main():
    config = {
        "source_label": "Marinha do Brasil",
        "listing_urls": [
            "https://www.marinha.mil.br/editais",
            "https://www.marinha.mil.br/licitacoes",
        ],
        "keywords": KEYWORDS_INTEREST
        + [
            "marinha",
            "forca naval",
            "arsenal de marinha",
            "licit",
            "pregão",
            "pregao",
            "edital",
            "contrata",
            "aquisição",
            "aquisicao",
            "compra pública",
            "compra publica",
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
            "multimídia",
            "galeria de fotos",
            "comandante",
            "hino",
            "cerimonial",
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
            "/acesso-a-informacao",
            "/acesso-a-informação",
            "/cookies",
            "/privacidade",
            "facebook.com",
            "instagram.com",
            "twitter.com",
            "youtube.com",
        ],
        "link_url_must_contain_any": [
            "/licit",
            "/editais/",
            "/edital",
            "/preg",
            "/compras",
            "/contrat",
            ".pdf",
            "modalidade",
            "uasg",
        ],
        "link_path_min_depth": 2,
        "program_hint": "Marinha do Brasil",
        "allowed_domains": ["marinha.mil.br"],
        "max_items": 25,
        "max_links_per_page": 120,
        "http_timeout": 15,
        "setor_estrategico": "",
        "orgao_responsavel": "Marinha do Brasil",
        "instituicao": "Marinha do Brasil",
        "orgao_contratante": "Marinha do Brasil",
        "tipo_oportunidade": "",
        "area_cientifica": [],
        "area_tecnologica": [],
        "subtema_padrao": [],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[MARINHA] Falha na coleta: {exc}")
        items = []
    if not items:
        print("[MARINHA] Nenhum item com evidência de licitação/edital (sem fallback de índice).")
    save_outputs(
        Path(__file__).parent,
        "marinha",
        items,
        failure_reason=(
            "Nenhum item com evidencia de licitacao/edital; fonte historicamente bloqueada "
            "por Cloudflare/403 ou listagem sem HTML util. Sem fallback de indice."
        )
        if not items
        else None,
        collection_failed=not items,
    )
    print(f"[MARINHA] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
