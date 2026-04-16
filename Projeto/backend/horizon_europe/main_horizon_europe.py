from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "HORIZON_EUROPE",
        "listing_urls": [
            "https://research-and-innovation.ec.europa.eu/funding/funding-opportunities/funding-programmes-and-open-calls/horizon-europe_en",
            "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search",
        ],
        "keywords": ["call", "horizon", "funding", "grant", "innovation", "research"],
        "avoid_keywords": ["procurement", "tender award", "job"],
        "program_hint": "Horizon Europe",
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "horizon_europe", items)
    print(f"Horizon Europe: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
