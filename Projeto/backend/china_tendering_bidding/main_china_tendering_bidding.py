"""Crawler: China Tendering and Bidding Public Service Platform.

Coleta apenas a area publica (sem login, sem captcha). Em caso de bloqueio
anti-bot, o crawler simplesmente retorna 0 itens sem falhar o pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal

SOURCE_NAME = "China Tendering & Bidding"


def main() -> None:
    print(f"[{SOURCE_NAME}] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label=SOURCE_NAME,
        country="china",
        listing_urls=[
            "https://www.cebpubservice.com/",
            "https://www.ggzy.gov.cn/",
            "https://www.ggzy.gov.cn/information/html/a/",
            "https://www.cebpubservice.com/ctpsp_iiss/searchbid/queryResult.htm",
        ],
        allowed_domains=["cebpubservice.com", "ggzy.gov.cn"],
        extra_keywords=[
            "招标", "投标", "中标", "采购", "公告",
            "tender", "bid", "procurement",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.7",
        instituicao="China Tendering and Bidding Public Service Platform",
        orgao_responsavel="National Development and Reform Commission",
        tipo_oportunidade_hint="licitacao",
        programa="china_procurement",
        acao="procurement_publico",
        tipo_recurso="Contratacao Publica",
        max_items=70,
        max_listing_pages=5,
    )
    save_outputs_asia(Path(__file__).parent, "china_tendering_bidding", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[CHINA_TENDERING_BIDDING] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
