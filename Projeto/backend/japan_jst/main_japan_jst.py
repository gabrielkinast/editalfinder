"""Crawler: JST - Japan Science and Technology Agency.

Foco: chamadas publicas, programas de P&D, calls for proposals em ciencia
e tecnologia. Coleta apenas conteudo publico institucional.
"""

from __future__ import annotations

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal

SOURCE_NAME = "JST"
COUNTRY = "japao"
MAX_ITEMS = 60
MAX_LISTING_PAGES = 5


def _keep_jst_item(it: dict) -> bool:
    lk = (it.get("link") or "").lower()
    if any(x in lk for x in ("/privacy", "/cookie", "/sitemap", "/sitepolicy", "search?q=", "/contact")):
        return False
    return True


def main() -> int:
    print(f"[{SOURCE_NAME}] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label=SOURCE_NAME,
        country=COUNTRY,
        listing_urls=[
            "https://www.jst.go.jp/EN/research/index.html",
            "https://www.jst.go.jp/EN/news/index.html",
            "https://www.jst.go.jp/EN/announcement/index.html",
            "https://www.jst.go.jp/announce/",
            "https://www.jst.go.jp/pr/info/",
            "https://www.jst.go.jp/sis/co-creation/opportunity/",
        ],
        allowed_domains=["jst.go.jp"],
        extra_keywords=[
            "call", "募集", "公募", "research", "program",
            "grant", "funding", "fellowship", "application", "proposal",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="Japan Science and Technology Agency",
        orgao_responsavel="JST",
        tipo_oportunidade_hint="funding_opportunity",
        max_items=MAX_ITEMS,
        max_listing_pages=MAX_LISTING_PAGES,
    )
    items = [x for x in items if _keep_jst_item(x)]
    result = save_outputs_asia(
        Path(__file__).parent, "japan_jst", items, rejected=rejected, crawl_meta=_crawl_meta
    )
    print(f"[JAPAN_JST] Registros na saída: {len(items)} (gravado={result.wrote_file})")
    return int(result.suggested_exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
