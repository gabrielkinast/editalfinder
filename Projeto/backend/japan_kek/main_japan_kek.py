"""Crawler: KEK - High Energy Accelerator Research Organization."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[JAPAN_KEK] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="KEK",
        country="japao",
        listing_urls=[
            "https://www.kek.jp/en/news/",
            "https://www.kek.jp/ja/news/",
            "https://www.kek.jp/ja/inst/krs/",
            "https://www.kek.jp/en/jobs/",
        ],
        allowed_domains=["kek.jp"],
        extra_keywords=[
            "加速器", "高エネルギー", "素粒子",
            "accelerator", "high energy", "particle physics",
            "公募", "調達", "募集",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="High Energy Accelerator Research Organization",
        orgao_responsavel="KEK",
        tipo_oportunidade_hint="pesquisa_colaborativa",
        max_listing_pages=5,
        max_items=30,
    )
    save_outputs_asia(Path(__file__).parent, "japan_kek", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_KEK] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
