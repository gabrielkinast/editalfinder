"""Crawler: MOST - Ministry of Science and Technology of China."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[CHINA_MOST] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="MOST China",
        country="china",
        listing_urls=[
            "https://www.most.gov.cn/",
            "https://www.most.gov.cn/tztg/",
            "https://www.most.gov.cn/kjbgz/",
            "https://en.most.gov.cn/",
        ],
        allowed_domains=["most.gov.cn"],
        extra_keywords=[
            "通知公告", "项目", "课题", "重点", "研发",
            "科技", "创新", "招标",
            "research", "science", "technology",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.7",
        instituicao="Ministry of Science and Technology of the PRC",
        orgao_responsavel="MOST",
        tipo_oportunidade_hint="funding_opportunity",
        max_listing_pages=5,
        max_items=35,
    )
    save_outputs_asia(Path(__file__).parent, "china_most", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[CHINA_MOST] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
