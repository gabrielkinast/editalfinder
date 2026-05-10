"""Crawler: JSPS - Japan Society for the Promotion of Science."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal

SOURCE_NAME = "JSPS"
MAX_ITEMS = 50
MAX_LISTING_PAGES = 5


def main() -> None:
    print(f"[{SOURCE_NAME}] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label=SOURCE_NAME,
        country="japao",
        listing_urls=[
            "https://www.jsps.go.jp/english/index.html",
            "https://www.jsps.go.jp/english/e-grants/index.html",
            "https://www.jsps.go.jp/j-grantsinaid/index.html",
            "https://www.jsps.go.jp/english/e-fellow/index.html",
            "https://www.jsps.go.jp/j-grantsinaid/01_seido/01_shumoku/index.html",
        ],
        allowed_domains=["jsps.go.jp"],
        extra_keywords=[
            "grant", "fellowship", "募集", "公募", "research",
            "kakenhi", "科研費", "助成",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="Japan Society for the Promotion of Science",
        orgao_responsavel="JSPS",
        tipo_oportunidade_hint="grant",
        max_items=MAX_ITEMS,
        max_listing_pages=MAX_LISTING_PAGES,
    )
    save_outputs_asia(Path(__file__).parent, "japan_jsps", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_JSPS] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
