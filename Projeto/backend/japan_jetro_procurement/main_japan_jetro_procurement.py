"""Crawler: JETRO - Japanese Government Procurement (English portal).

Foco em editais publicos do governo japones expostos via JETRO.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[JETRO Government Procurement] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="JETRO Government Procurement",
        country="japao",
        listing_urls=[
            "https://www.jetro.go.jp/en/database/procurement/",
            "https://www.jetro.go.jp/en/database/procurement/national/",
            "https://www.jetro.go.jp/en/database/procurement/quasi/",
        ],
        allowed_domains=["jetro.go.jp"],
        extra_keywords=[
            "tender", "procurement", "bid", "rfp", "rfq", "contract",
            "specification", "supply", "公告", "調達", "入札",
        ],
        accept_language="en,ja;q=0.8",
        instituicao="Japan External Trade Organization",
        orgao_responsavel="JETRO",
        tipo_oportunidade_hint="procurement",
        programa="japan_procurement",
        acao="procurement_publico",
        tipo_recurso="Contratacao Publica",
        max_listing_pages=5,
        max_items=50,
    )
    save_outputs_asia(Path(__file__).parent, "japan_jetro_procurement", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_JETRO_PROCUREMENT] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
