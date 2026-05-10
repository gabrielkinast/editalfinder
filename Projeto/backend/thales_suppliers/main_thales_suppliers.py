from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
THALES_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
if str(THALES_DIR) not in sys.path:
    sys.path.insert(0, str(THALES_DIR))

from defense_source_common import save_outputs, scrape_html_portal

from thales_harvest import merge_thales_items


def main() -> None:
    allowed = ("thalesgroup.com",)
    portal_items = scrape_html_portal(
        source_label="Thales Suppliers",
        country="FR",
        listing_urls=[
            "https://www.thalesgroup.com/en/supplier",
            "https://www.thalesgroup.com/en/supplier-relations",
        ],
        allowed_domains=list(allowed),
        extra_keywords=["supplier", "procurement", "defence", "aerospace", "vendor", "purchasing"],
        max_items=24,
    )
    items = merge_thales_items(portal_items, allowed_domains=allowed)
    items.sort(key=lambda x: str(x.get("link") or ""))
    save_outputs(Path(__file__).parent, "thales_suppliers", items)
    print(f"[THALES_SUPPLIERS] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
