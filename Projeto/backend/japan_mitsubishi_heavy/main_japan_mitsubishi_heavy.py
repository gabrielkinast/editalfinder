"""Crawler: Mitsubishi Heavy Industries - paginas publicas de fornecedores
e procurement.

ESCOPO: apenas conteudo publico institucional (corporate procurement,
supplier portal). Nao coleta documentos tecnicos sensiveis ou material
classificado de defesa.
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
        source_label="Mitsubishi Heavy Industries (Suppliers)",
        country="japao",
        listing_urls=[
            "https://www.mhi.com/finance/procurement/",
            "https://www.mhi.com/finance/procurement/policy.html",
            "https://www.mhi.com/news/",
        ],
        allowed_domains=["mhi.com"],
        extra_keywords=[
            "procurement", "supplier", "supply chain",
            "調達", "サプライヤー", "公告",
            "aerospace", "energy", "nuclear", "infrastructure",
        ],
        accept_language="en,ja;q=0.8",
        instituicao="Mitsubishi Heavy Industries",
        orgao_responsavel="MHI",
        tipo_oportunidade_hint="supplier_portal",
        programa="defesa_industrial_japao",
        acao="fornecedores_estrategicos",
        tipo_recurso="Portal de Fornecedores",
        max_items=20,
    )
    # Marca empresa_prime nos extras de cada item.
    for item in items:
        ex = item.get("extras") or {}
        ex["empresa_prime"] = "Mitsubishi Heavy Industries"
        item["extras"] = ex

    save_outputs_asia(Path(__file__).parent, "japan_mitsubishi_heavy", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_MITSUBISHI_HEAVY] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
