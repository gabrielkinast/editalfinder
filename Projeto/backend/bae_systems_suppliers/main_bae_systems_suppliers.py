from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
BAE_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))
if str(BAE_DIR) not in sys.path:
    sys.path.insert(0, str(BAE_DIR))

from defense_source_common import save_outputs, scrape_html_portal

from bae_harvest import merge_bae_items


def main() -> None:
    allowed = ("baesystems.com", "hicx.net")
    portal_items = scrape_html_portal(
        source_label="BAE Systems Suppliers",
        country="UK",
        listing_urls=[
            "https://www.baesystems.com/en-uk/suppliers/responsible-supply-chain",
            "https://www.baesystems.com/en/suppliers",
        ],
        allowed_domains=list(allowed),
        extra_keywords=["supplier", "defence", "procurement", "vendor", "registration", "hicx"],
        max_items=24,
        supplier_recovery_d_filter=True,
        supplier_recovery_d1_qa=True,
    )
    items = merge_bae_items(portal_items, allowed)
    items.sort(key=lambda x: str(x.get("link") or ""))
    save_outputs(Path(__file__).parent, "bae_systems_suppliers", items)
    print(f"[BAE_SUPPLIERS] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
