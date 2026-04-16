from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "CBPF",
        # Conteúdo institucional e oportunidades estão principalmente no gov.br
        "listing_urls": [
            "https://www.gov.br/cbpf/pt-br",
            "https://www.gov.br/cbpf/pt-br/acesso-a-informacao/acoes-e-programas",
            "https://www.gov.br/cbpf/pt-br/acesso-a-informacao/acoes-e-programas/programas",
            "https://www.cbpf.br/",
        ],
        "keywords": [
            "edital",
            "chamada",
            "bolsa",
            "programa",
            "pesquisa",
            "física",
            "fomento",
            "evento",
            "oportunidade",
            "mestrado",
            "doutorado",
            "pos",
            "workshop",
        ],
        "avoid_keywords": [
            "concurso público",
            "estágio",
        ],
        "program_hint": "CBPF",
        "allowed_domains": ["gov.br", "cbpf.br"],
        "max_items": 20,
        "max_links_per_page": 100,
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "cbpf", items)
    print(f"CBPF: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
