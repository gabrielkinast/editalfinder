from __future__ import annotations

from pathlib import Path

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs, scrape_html_portal

SOURCE_NAME = "DARPA Opportunities"

def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    text = f"{title} {str(item.get('descricao') or '').lower()} {link}"
    if link.rstrip("/") in {"https://www.darpa.mil/work-with-us", "http://www.darpa.mil/work-with-us"}:
        return False
    if "work-with-us" in link and not any(k in text for k in ("opportunit", "solicitation", "proposal", "baa", "open", "broad agency")):
        return False
    if any(k in title for k in ("home", "news", "contact")):
        return False
    return any(k in text for k in ("opportunit", "solicitation", "proposal", "baa", "broad agency", "challenge", "open", "research announcement"))


def main() -> None:
    print(f"[{SOURCE_NAME}] Iniciando coleta...")
    items = scrape_html_portal(
        source_label=SOURCE_NAME,
        country="US",
        listing_urls=[
            "https://www.darpa.mil/work-with-us/opportunities",
            "https://www.darpa.mil/news-events",
        ],
        allowed_domains=["darpa.mil"],
        extra_keywords=["darpa", "broad agency announcement", "baa", "solicitation", "proposal"],
        max_items=60,
        max_listing_pages=5,
    )
    items = [x for x in items if _is_relevant_item(x)]
    save_outputs(Path(__file__).parent, "darpa_opportunities", items)
    print(f"[DARPA] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
