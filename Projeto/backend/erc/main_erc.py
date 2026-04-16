from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "ERC",
        "listing_urls": [
            "https://erc.europa.eu/funding",
            "https://erc.europa.eu/funding/advanced-grants",
        ],
        "keywords": ["grant", "funding", "call", "proposal", "research", "erc"],
        "avoid_keywords": ["job", "press", "event"],
        "program_hint": "European Research Council",
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "erc", items)
    print(f"ERC: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
