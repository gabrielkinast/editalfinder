from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "CNEN",
        "listing_urls": [
            "https://www.gov.br/cnen/pt-br",
            "https://www.gov.br/cnen/pt-br/assuntos/noticias",
        ],
        "keywords": [
            "edital",
            "chamada",
            "fomento",
            "programa",
            "pesquisa",
            "nuclear",
            "radiação",
            "energia",
            "convênio",
        ],
        "avoid_keywords": [
            "concurso público",
            "estágio",
            "pregão",
            "licitação",
        ],
        "program_hint": "CNEN",
        "allowed_domains": ["gov.br"],
        "max_items": 20,
        "max_links_per_page": 100,
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "cnen", items)
    print(f"CNEN: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
