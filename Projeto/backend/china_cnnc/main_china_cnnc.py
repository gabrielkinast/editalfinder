"""Crawler: CNNC - China National Nuclear Corporation (public procurement)."""

from __future__ import annotations

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> int:
    print("[CHINA_CNNC] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="CNNC",
        country="china",
        listing_urls=[
            "https://www.cnnc.com.cn/",
            "https://ec.cnnc.com.cn/",
            "https://www.cnnc.com.cn/cnnc/300557/300558/index.html",
        ],
        allowed_domains=["cnnc.com.cn"],
        extra_keywords=[
            "招标", "采购", "公告", "公示", "中标",
            "核电", "核燃料", "核能",
            "nuclear", "tender", "procurement",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.7",
        instituicao="China National Nuclear Corporation",
        orgao_responsavel="CNNC",
        tipo_oportunidade_hint="licitacao",
        programa="nuclear_procurement_china",
        max_listing_pages=5,
        max_items=30,
    )
    if not items:
        print("[CHINA_CNNC] Nenhum item (sem fallback de índice institucional).")
    result = save_outputs_asia(
        Path(__file__).parent, "china_cnnc", items, rejected=rejected, crawl_meta=_crawl_meta
    )
    print(
        f"[CHINA_CNNC] Registros na saída: {len(items)} (gravado={result.wrote_file}, exit_sugerido={result.suggested_exit_code})"
    )
    return int(result.suggested_exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
