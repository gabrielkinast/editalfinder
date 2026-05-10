"""Crawler: KAKENHI - Grants-in-Aid for Scientific Research (JSPS).

Coleta apenas anuncios publicos do calendario KAKENHI e categorias de
chamadas. A submissao real ocorre via e-Rad e nao e raspada.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[JAPAN_KAKENHI] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="KAKENHI",
        country="japao",
        listing_urls=[
            "https://www.jsps.go.jp/j-grantsinaid/03_keikaku/index.html",
            "https://www.jsps.go.jp/english/e-grants/grants01.html",
            "https://www.jsps.go.jp/j-grantsinaid/01_seido/index.html",
        ],
        allowed_domains=["jsps.go.jp"],
        extra_keywords=[
            "kakenhi", "科研費", "助成", "公募", "募集", "grant",
            "research", "scientific",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="JSPS / Grants-in-Aid for Scientific Research",
        orgao_responsavel="JSPS",
        tipo_oportunidade_hint="grant",
        programa="kakenhi",
        max_listing_pages=5,
        max_items=30,
    )
    save_outputs_asia(Path(__file__).parent, "japan_kakenhi", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_KAKENHI] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
