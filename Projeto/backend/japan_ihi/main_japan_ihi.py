"""Crawler: IHI Corporation - paginas publicas de fornecedores e procurement
(escopo institucional publico apenas).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="IHI Corporation (Suppliers)",
        country="japao",
        listing_urls=[
            "https://www.ihi.co.jp/en/all_news/",
            "https://www.ihi.co.jp/en/company/procurement/",
            "https://www.ihi.co.jp/procurement/",
        ],
        allowed_domains=["ihi.co.jp"],
        extra_keywords=[
            "procurement", "supplier",
            "調達", "サプライヤー", "公告",
            "aerospace", "energy", "industrial systems",
        ],
        accept_language="en,ja;q=0.8",
        instituicao="IHI Corporation",
        orgao_responsavel="IHI",
        tipo_oportunidade_hint="supplier_portal",
        programa="defesa_industrial_japao",
        acao="fornecedores_estrategicos",
        tipo_recurso="Portal de Fornecedores",
        max_items=20,
    )
    for item in items:
        ex = item.get("extras") or {}
        ex["empresa_prime"] = "IHI Corporation"
        item["extras"] = ex

    save_outputs_asia(Path(__file__).parent, "japan_ihi", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_IHI] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
