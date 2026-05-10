"""Crawler: MEXT - Ministry of Education, Culture, Sports, Science and Technology."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[JAPAN_MEXT] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="MEXT",
        country="japao",
        listing_urls=[
            "https://www.mext.go.jp/en/news/index.htm",
            "https://www.mext.go.jp/b_menu/koubo/index.htm",
            "https://www.mext.go.jp/a_menu/shinkou/sentan/index.htm",
        ],
        allowed_domains=["mext.go.jp"],
        extra_keywords=[
            "公募", "募集", "research", "science", "technology",
            "材料", "量子", "原子力", "宇宙", "半導体",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="Ministry of Education, Culture, Sports, Science and Technology",
        orgao_responsavel="MEXT",
        tipo_oportunidade_hint="chamada_publica",
        max_listing_pages=5,
        max_items=35,
    )
    save_outputs_asia(Path(__file__).parent, "japan_mext", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_MEXT] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
