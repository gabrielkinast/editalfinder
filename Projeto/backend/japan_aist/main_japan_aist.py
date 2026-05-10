"""Crawler: AIST - National Institute of Advanced Industrial Science and Technology."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[JAPAN_AIST] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="AIST",
        country="japao",
        listing_urls=[
            "https://www.aist.go.jp/index_en.html",
            "https://www.aist.go.jp/aist_j/news/index.html",
            "https://www.aist.go.jp/aist_j/procure/",
            "https://www.aist.go.jp/aist_j/recruit/",
        ],
        allowed_domains=["aist.go.jp"],
        extra_keywords=[
            "公募", "募集", "調達", "入札",
            "research", "industrial", "materials", "ai",
            "材料", "半導体", "量子", "エネルギー",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="National Institute of Advanced Industrial Science and Technology",
        orgao_responsavel="AIST",
        tipo_oportunidade_hint="funding_opportunity",
        max_listing_pages=5,
        max_items=30,
    )
    save_outputs_asia(Path(__file__).parent, "japan_aist", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_AIST] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
