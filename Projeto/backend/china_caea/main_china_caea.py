"""Crawler: CAEA - China Atomic Energy Authority (public communications only)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[CHINA_CAEA] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="CAEA",
        country="china",
        listing_urls=[
            "https://www.caea.gov.cn/",
            "https://www.caea.gov.cn/n6759362/index.html",
            "https://www.caea.gov.cn/english/",
        ],
        allowed_domains=["caea.gov.cn"],
        extra_keywords=[
            "通知公告", "公告", "招标", "公示",
            "核能", "核工业", "辐射防护",
            "nuclear", "atomic energy",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.7",
        instituicao="China Atomic Energy Authority",
        orgao_responsavel="CAEA",
        tipo_oportunidade_hint="noticia_institucional",
        programa="nuclear_research_china",
        max_listing_pages=5,
        max_items=20,
    )
    save_outputs_asia(Path(__file__).parent, "china_caea", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[CHINA_CAEA] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
