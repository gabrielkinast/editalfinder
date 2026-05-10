"""Crawler: CGN - China General Nuclear Power Group (public procurement)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[CHINA_CGN] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="CGN",
        country="china",
        listing_urls=[
            "https://www.cgnpc.com.cn/",
            "http://ec.cgnpc.com.cn/",
            "https://www.cgnpc.com.cn/n6/n11/index.html",
        ],
        allowed_domains=["cgnpc.com.cn"],
        extra_keywords=[
            "招标", "采购", "公告", "公示", "中标",
            "核电", "核能",
            "nuclear", "tender", "procurement",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.7",
        instituicao="China General Nuclear Power Group",
        orgao_responsavel="CGN",
        tipo_oportunidade_hint="licitacao",
        programa="nuclear_procurement_china",
        max_listing_pages=5,
        max_items=30,
    )
    save_outputs_asia(Path(__file__).parent, "china_cgn", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[CHINA_CGN] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
