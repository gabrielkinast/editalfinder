"""Crawler: JAEA - Japan Atomic Energy Agency.

Coleta apenas oportunidades publicas e institucionais (調達情報, 公募研究).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def _keep_jaea_item(it: dict) -> bool:
    lk = (it.get("link") or "").lower()
    tit = (it.get("titulo") or "").strip().lower()
    if "/study_results" in lk or "study_results" in lk:
        return False
    if tit in ("r&d results", "rd results", "study results"):
        return False
    if lk.rstrip("/").endswith("/english") or lk.endswith("/english/"):
        return False
    return True


def main() -> int:
    print("[JAPAN_JAEA] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="JAEA",
        country="japao",
        listing_urls=[
            "https://www.jaea.go.jp/english/",
            "https://www.jaea.go.jp/news/",
            "https://www.jaea.go.jp/02/chotatsu/",
            "https://www.jaea.go.jp/02/koubo/",
        ],
        allowed_domains=["jaea.go.jp"],
        extra_keywords=[
            "原子力", "核燃料", "放射線", "加速器", "材料",
            "公募", "調達", "入札",
            "nuclear", "atomic", "research", "fellowship",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="Japan Atomic Energy Agency",
        orgao_responsavel="JAEA",
        tipo_oportunidade_hint="procurement",
        max_listing_pages=5,
        max_items=30,
    )
    items = [x for x in items if _keep_jaea_item(x)]
    result = save_outputs_asia(
        Path(__file__).parent, "japan_jaea", items, rejected=rejected, crawl_meta=_crawl_meta
    )
    print(f"[JAPAN_JAEA] Registros na saída: {len(items)} (gravado={result.wrote_file})")
    return int(result.suggested_exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
