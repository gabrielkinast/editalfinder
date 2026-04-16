from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "IPEN",
        "listing_urls": [
            "https://www.gov.br/ipen/pt-br",
            "https://www.gov.br/ipen/pt-br/assuntos/noticias",
        ],
        "keywords": [
            "edital",
            "chamada",
            "fomento",
            "programa",
            "pesquisa",
            "nuclear",
            "radioisótopo",
            "convênio",
            "p&d",
            "pd&i",
        ],
        "avoid_keywords": [
            "concurso público",
            "estágio",
            "pregão",
            "licitação",
        ],
        "program_hint": "IPEN-CNEN",
        "allowed_domains": ["gov.br"],
        "max_items": 20,
        "max_links_per_page": 100,
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "ipen", items)
    print(f"IPEN: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
