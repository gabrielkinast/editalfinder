from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "DOE_ARPAE",
        "listing_urls": [
            "https://arpa-e.energy.gov/funding-opportunities",
            "https://www.energy.gov/eere/funding-opportunities",
        ],
        "keywords": ["funding", "foa", "opportunity", "program", "grant", "innovation"],
        "avoid_keywords": ["procurement", "career", "job"],
        "program_hint": "DOE / ARPA-E",
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "doe_arpae", items)
    print(f"DOE/ARPA-E: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
