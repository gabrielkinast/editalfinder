from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs, scrape_html_portal


def main() -> None:
    items = scrape_html_portal(
        source_label="Lockheed Martin Suppliers",
        country="US",
        # Recovery D: apenas hub de fornecedores — evita arrastar páginas de capabilities/produtos.
        listing_urls=[
            "https://www.lockheedmartin.com/en-us/suppliers.html",
        ],
        allowed_domains=["lockheedmartin.com"],
        extra_keywords=["supplier", "defense", "procurement", "vendor"],
        max_items=20,
        supplier_recovery_d_filter=True,
        supplier_recovery_d1_qa=True,
    )
    save_outputs(Path(__file__).parent, "lockheed_martin_suppliers", items)
    print(f"[LOCKHEED_SUPPLIERS] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
