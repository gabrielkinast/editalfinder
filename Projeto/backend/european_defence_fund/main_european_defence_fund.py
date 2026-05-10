from __future__ import annotations

from pathlib import Path

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs, scrape_html_portal


def main() -> None:
    print("[EUROPEAN_DEFENCE_FUND] Iniciando coleta...")
    items = scrape_html_portal(
        source_label="European Defence Fund",
        country="EU",
        listing_urls=[
            "https://defence-industry-space.ec.europa.eu/eu-defence-industry/european-defence-fund-edf_en",
            "https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search",
            "https://defence-industry-space.ec.europa.eu/funding-opportunities_en",
        ],
        allowed_domains=["europa.eu", "ec.europa.eu"],
        extra_keywords=["european defence fund", "edf call", "defence"],
        max_items=50,
        max_listing_pages=5,
    )
    save_outputs(Path(__file__).parent, "european_defence_fund", items)
    print(f"[EUROPEAN_DEFENCE_FUND] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
