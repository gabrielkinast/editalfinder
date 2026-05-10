"""Crawler: Kawasaki Heavy Industries - paginas publicas de fornecedores
e procurement (escopo institucional publico apenas).
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
        source_label="Kawasaki Heavy Industries (Suppliers)",
        country="japao",
        listing_urls=[
            "https://global.kawasaki.com/en/corp/profile/procurement/",
            "https://www.khi.co.jp/procurement/",
            # Removido /en/news/: notícias corporativas fora do escopo supplier_portal.
        ],
        allowed_domains=["kawasaki.com", "khi.co.jp"],
        extra_keywords=[
            "procurement", "supplier", "purchasing",
            "調達", "サプライヤー", "公告",
            "aerospace", "rolling stock", "energy",
        ],
        accept_language="en,ja;q=0.8",
        instituicao="Kawasaki Heavy Industries",
        orgao_responsavel="KHI",
        tipo_oportunidade_hint="supplier_portal",
        programa="defesa_industrial_japao",
        acao="fornecedores_estrategicos",
        tipo_recurso="Portal de Fornecedores",
        max_items=20,
    )
    for item in items:
        ex = item.get("extras") or {}
        ex["empresa_prime"] = "Kawasaki Heavy Industries"
        item["extras"] = ex

    save_outputs_asia(Path(__file__).parent, "japan_kawasaki_heavy", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_KAWASAKI_HEAVY] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
