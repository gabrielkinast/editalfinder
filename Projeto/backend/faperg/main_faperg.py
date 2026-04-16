from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "FAPERG",
        "listing_urls": [
            "https://fapergs.rs.gov.br/editais-abertos",
            "https://fapergs.rs.gov.br/editais-encerrados",
        ],
        "keywords": ["edital", "chamada", "fomento", "programa", "pesquisa"],
        "avoid_keywords": ["licitação", "pregão", "concurso"],
        "program_hint": "FAPERG",
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "faperg", items)
    print(f"FAPERG: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
