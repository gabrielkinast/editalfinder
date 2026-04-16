from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "SENAI",
        "listing_urls": [
            "https://www.portaldaindustria.com.br/senai/canais/chamadas-publicas/",
            "https://www.portaldaindustria.com.br/senai/canais/editais/",
        ],
        "keywords": ["edital", "chamada", "inovação", "tecnologia", "fomento", "pesquisa"],
        "avoid_keywords": ["licitação", "pregão", "concurso"],
        "program_hint": "SENAI",
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "senai", items)
    print(f"SENAI: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
