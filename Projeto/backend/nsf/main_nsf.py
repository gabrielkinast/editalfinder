from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "NSF",
        "listing_urls": [
            "https://new.nsf.gov/funding/opportunities",
            "https://www.grants.gov/search-results-detail/NSF",
        ],
        "keywords": ["funding", "program", "solicitation", "proposal", "grant", "opportunity"],
        "avoid_keywords": ["job", "procurement", "press release"],
        "program_hint": "National Science Foundation",
    }
    items = scrape_source(config)
    save_outputs(Path(__file__).parent, "nsf", items)
    print(f"NSF: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
