from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "CAPES",
        "listing_urls": [
            "https://www.gov.br/capes/pt-br/acesso-a-informacao/acoes-e-programas",
            "https://www.gov.br/capes/pt-br/assuntos/noticias",
        ],
        "keywords": ["edital", "chamada", "fomento", "bolsa", "programa", "pesquisa"],
        "avoid_keywords": ["licitação", "pregão", "concurso público", "estágio"],
        "program_hint": "CAPES",
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "capes", items)
    print(f"CAPES: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
