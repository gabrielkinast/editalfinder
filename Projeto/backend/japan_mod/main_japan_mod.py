"""Crawler: Japan Ministry of Defense - public communications only.

ESCOPO: apenas comunicados publicos institucionais e avisos de procurement
publico. Nao coleta documentos operacionais, manuais tecnicos ou conteudo
sensivel.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> None:
    print("[JAPAN_MOD] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="Japan MOD",
        country="japao",
        listing_urls=[
            "https://www.mod.go.jp/en/index.html",
            "https://www.mod.go.jp/j/press/news/index.html",
            "https://www.mod.go.jp/j/procurement/chotatsu/",
        ],
        allowed_domains=["mod.go.jp"],
        extra_keywords=[
            "公告", "調達", "入札", "press release",
            "procurement", "tender", "announcement",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="Ministry of Defense (Japan)",
        orgao_responsavel="Japan MoD",
        tipo_oportunidade_hint="noticia_institucional",
        programa="defesa_industrial_japao",
        max_listing_pages=5,
        max_items=20,
    )
    save_outputs_asia(Path(__file__).parent, "japan_mod", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_MOD] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
