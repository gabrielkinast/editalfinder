from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "ELETRONUCLEAR",
        "listing_urls": [
            "https://www.eletronuclear.gov.br/",
            "https://www.eletronuclear.gov.br/pt-br",
        ],
        "keywords": [
            "edital",
            "chamada",
            "fomento",
            "programa",
            "pesquisa",
            "inovação",
            "p&d",
            "parceria",
            "nuclear",
        ],
        "avoid_keywords": [
            "concurso público",
            "estágio",
        ],
        "program_hint": "Eletronuclear",
        "allowed_domains": ["eletronuclear.gov.br"],
        "max_items": 20,
        "max_links_per_page": 100,
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "eletronuclear", items)
    print(f"Eletronuclear: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
