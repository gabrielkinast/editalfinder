"""Crawler: China International Tendering / MOFCOM."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal

SOURCE_NAME = "China International Tendering (MOFCOM)"


def main() -> None:
    print(f"[{SOURCE_NAME}] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label=SOURCE_NAME,
        country="china",
        listing_urls=[
            "https://www.chinabidding.mofcom.gov.cn/",
            "http://www.chinabidding.com/",
            "https://english.mofcom.gov.cn/",
            "https://www.chinabidding.com/en/",
        ],
        allowed_domains=[
            "chinabidding.mofcom.gov.cn",
            "chinabidding.com",
            "mofcom.gov.cn",
        ],
        extra_keywords=[
            "招标", "投标", "中标", "采购", "公告", "公示",
            "tender", "bid", "procurement", "contract",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.7",
        instituicao="Ministry of Commerce of the PRC",
        orgao_responsavel="MOFCOM",
        tipo_oportunidade_hint="licitacao",
        programa="china_procurement",
        acao="procurement_publico",
        tipo_recurso="Contratacao Publica",
        max_items=80,
        max_listing_pages=6,
    )
    save_outputs_asia(Path(__file__).parent, "china_mofcom_tendering", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[CHINA_MOFCOM_TENDERING] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
