"""Crawler: CAS - Chinese Academy of Sciences."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[CHINA_CAS] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="CAS",
        country="china",
        listing_urls=[
            "https://www.cas.cn/",
            "https://www.cas.cn/tz/",
            "https://english.cas.cn/",
            "https://english.cas.cn/news/",
        ],
        allowed_domains=["cas.cn"],
        extra_keywords=[
            "公告", "通知", "招标", "采购", "项目", "课题",
            "research", "science", "academy",
            "物理", "化学", "材料", "量子", "核", "航天",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.8",
        instituicao="Chinese Academy of Sciences",
        orgao_responsavel="CAS",
        tipo_oportunidade_hint="pesquisa_colaborativa",
        max_listing_pages=5,
        max_items=35,
    )
    save_outputs_asia(Path(__file__).parent, "china_cas", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[CHINA_CAS] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
