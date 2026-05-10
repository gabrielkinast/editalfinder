from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs, scrape_html_portal


def main() -> None:
    items = scrape_html_portal(
        source_label="Rheinmetall Suppliers",
        country="DE",
        listing_urls=[
            # Caminhos antigos (/en/company/suppliers) devolvem 404; onboarding oficial.
            # Microsite "terms of use" puxa também página só de privacidade (GDPR) — fora do escopo "ação fornecedor".
            "https://www.rheinmetall.com/en/suppliers/become-a-supplier",
        ],
        allowed_domains=["rheinmetall.com", "procurementportal.rheinmetall.com", "ivalua.app"],
        extra_keywords=["supplier", "defence", "procurement", "land systems"],
        max_items=20,
    )
    save_outputs(Path(__file__).parent, "rheinmetall_suppliers", items)
    print(f"[RHEINMETALL_SUPPLIERS] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
