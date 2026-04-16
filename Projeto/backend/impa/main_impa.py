from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "IMPA",
        "listing_urls": [
            "https://impa.br/pt-br/",
            "https://impa.br/pt-br/eventos/",
        ],
        "keywords": [
            "edital",
            "chamada",
            "bolsa",
            "programa",
            "curso",
            "evento",
            "matemática",
            "pesquisa",
            "fomento",
            "oportunidade",
        ],
        "avoid_keywords": [
            "concurso público",
        ],
        "program_hint": "IMPA",
        "allowed_domains": ["impa.br"],
        "max_items": 20,
        "max_links_per_page": 100,
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "impa", items)
    print(f"IMPA: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
