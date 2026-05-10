"""Crawler: ATLA - Acquisition, Technology & Logistics Agency (Japan MoD).

ESCOPO: apenas oportunidades publicas e institucionais (chamadas de
pesquisa academica e dual-use de carater publico, como o programa
Innovative Science & Technology Initiative for Security). Nao coleta
documentos tecnicos sensiveis ou manuais.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[JAPAN_ATLA] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="ATLA",
        country="japao",
        listing_urls=[
            "https://www.mod.go.jp/atla/en/",
            "https://www.mod.go.jp/atla/funding.html",
            "https://www.mod.go.jp/atla/koubo.html",
        ],
        allowed_domains=["mod.go.jp"],
        extra_keywords=[
            "公募", "募集", "安全保障技術",
            "innovative science", "security technology", "research",
            "funding", "grant", "fellowship",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="Acquisition, Technology & Logistics Agency",
        orgao_responsavel="ATLA / Japan MoD",
        tipo_oportunidade_hint="funding_opportunity",
        programa="security_technology_research",
        max_listing_pages=5,
        max_items=20,
    )
    save_outputs_asia(Path(__file__).parent, "japan_atla", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_ATLA] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
