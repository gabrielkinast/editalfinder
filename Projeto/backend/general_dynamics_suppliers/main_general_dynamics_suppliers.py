from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs, scrape_html_portal


def main() -> None:
    items = scrape_html_portal(
        source_label="General Dynamics Suppliers",
        country="US",
        listing_urls=[
            "https://www.gd.com/suppliers",
            "https://www.gdls.com/suppliers/",
        ],
        allowed_domains=["gd.com", "gdls.com"],
        extra_keywords=["supplier", "land systems", "defense"],
        max_items=20,
        supplier_recovery_d_filter=True,
        supplier_recovery_d1_qa=True,
    )
    save_outputs(Path(__file__).parent, "general_dynamics_suppliers", items)
    print(f"[GENERAL_DYNAMICS_SUPPLIERS] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
