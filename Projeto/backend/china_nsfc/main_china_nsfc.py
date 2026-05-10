"""Crawler: NSFC - National Natural Science Foundation of China."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal

SOURCE_NAME = "NSFC"


def main() -> int:
    print(f"[{SOURCE_NAME}] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label=SOURCE_NAME,
        country="china",
        listing_urls=[
            "https://www.nsfc.gov.cn/",
            "https://www.nsfc.gov.cn/publish/portal0/tab442/",
            "https://www.nsfc.gov.cn/publish/portal0/tab434/",
            "https://www.nsfc.gov.cn/english/site_1/index.html",
            "https://www.nsfc.gov.cn/english/site_1/funding/index.html",
        ],
        allowed_domains=["nsfc.gov.cn"],
        extra_keywords=[
            "项目申报", "通知公告", "基金", "课题", "公告", "公示",
            "research", "fund", "grant",
            "物理", "数学", "化学", "材料", "量子", "核",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.7",
        instituicao="National Natural Science Foundation of China",
        orgao_responsavel="NSFC",
        tipo_oportunidade_hint="grant",
        max_items=60,
        max_listing_pages=5,
    )
    result = save_outputs_asia(
        Path(__file__).parent, "china_nsfc", items, rejected=rejected, crawl_meta=_crawl_meta
    )
    print(f"[CHINA_NSFC] Registros na saída: {len(items)} (gravado={result.wrote_file}, exit_sugerido={result.suggested_exit_code})")
    return int(result.suggested_exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
