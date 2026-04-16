from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "WELLCOME",
        "listing_urls": [
            "https://wellcome.org/grant-funding",
            "https://wellcome.org/grant-funding/schemes",
        ],
        "keywords": ["grant", "funding", "research", "call", "programme", "scheme"],
        "avoid_keywords": ["job", "procurement", "event"],
        "program_hint": "Wellcome Trust",
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "wellcome", items)
    print(f"WELLCOME: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
