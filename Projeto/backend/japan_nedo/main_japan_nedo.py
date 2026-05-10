"""Crawler: NEDO - New Energy and Industrial Technology Development Org."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[NEDO] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="NEDO",
        country="japao",
        listing_urls=[
            "https://www.nedo.go.jp/english/index.html",
            "https://www.nedo.go.jp/koubo/index.html",
            "https://www.nedo.go.jp/news/press/index.html",
        ],
        allowed_domains=["nedo.go.jp"],
        extra_keywords=[
            "公募", "募集", "助成", "委託",
            "energy", "semiconductor", "battery", "ai",
            "半導体", "電池", "エネルギー", "量子",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="New Energy and Industrial Technology Development Organization",
        orgao_responsavel="NEDO",
        tipo_oportunidade_hint="funding_opportunity",
        max_listing_pages=5,
        max_items=40,
    )
    save_outputs_asia(Path(__file__).parent, "japan_nedo", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_NEDO] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
