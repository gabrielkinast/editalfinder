"""Crawler: QST - National Institutes for Quantum Science and Technology."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[JAPAN_QST] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="QST",
        country="japao",
        listing_urls=[
            "https://www.qst.go.jp/site/qst-english/",
            "https://www.qst.go.jp/site/news/",
            "https://www.qst.go.jp/site/chotatsu/",
            "https://www.qst.go.jp/site/saiyou/",
        ],
        allowed_domains=["qst.go.jp"],
        extra_keywords=[
            "量子", "放射線", "核融合", "加速器", "材料",
            "quantum", "radiation", "fusion", "accelerator",
            "公募", "募集", "調達",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="National Institutes for Quantum Science and Technology",
        orgao_responsavel="QST",
        tipo_oportunidade_hint="funding_opportunity",
        max_listing_pages=5,
        max_items=30,
    )
    save_outputs_asia(Path(__file__).parent, "japan_qst", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_QST] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
