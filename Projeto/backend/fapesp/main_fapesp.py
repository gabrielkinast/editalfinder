from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "FAPESP",
        "listing_urls": [
            "https://fapesp.br/chamadas/",
            "https://fapesp.br/oportunidades/",
        ],
        "keywords": ["chamada", "oportunidade", "auxílio", "bolsa", "edital", "fomento"],
        "avoid_keywords": ["licitação", "pregão", "concurso"],
        "program_hint": "FAPESP",
        "max_items": 15,
        "max_links_per_page": 100,
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "fapesp", items)
    print(f"FAPESP: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
