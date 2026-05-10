"""Crawler: JAXA - Japan Aerospace Exploration Agency."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> int:
    print("[JAPAN_JAXA] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="JAXA",
        country="japao",
        listing_urls=[
            "https://global.jaxa.jp/press/",
            "https://www.jaxa.jp/press/index_j.html",
            "https://www.jaxa.jp/about/iso/chotatsu/",
            "https://www.jaxa.jp/about/recruit/index_j.html",
        ],
        allowed_domains=["jaxa.jp"],
        extra_keywords=[
            "宇宙", "衛星", "ロケット", "航空",
            "space", "satellite", "launch", "aerospace",
            "公募", "募集", "調達",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="Japan Aerospace Exploration Agency",
        orgao_responsavel="JAXA",
        tipo_oportunidade_hint="funding_opportunity",
        max_listing_pages=5,
        max_items=30,
    )
    if not items:
        print("[JAPAN_JAXA] Nenhum item (sem fallback de índice institucional).")
    result = save_outputs_asia(
        Path(__file__).parent, "japan_jaxa", items, rejected=rejected, crawl_meta=_crawl_meta
    )
    print(f"[JAPAN_JAXA] Registros na saída: {len(items)} (gravado={result.wrote_file})")
    return int(result.suggested_exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
