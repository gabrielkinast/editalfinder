"""Crawler: RIKEN - The Institute of Physical and Chemical Research."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if any(k in text for k in ("about riken", "overview", "privacy", "linkedin.com", "youtube.com", "facebook.com")):
        return False
    if not any(k in link for k in ("/careers", "/collab", "/news", "/procurement", "/tender", "/grants")):
        if not any(k in text for k in ("call", "open", "application", "fellowship", "grant", "公募", "募集", "入札")):
            return False
    return any(k in text for k in ("call", "open", "application", "fellowship", "grant", "公募", "募集", "入札", "tender"))


def main() -> None:
    print("[JAPAN_RIKEN] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="RIKEN",
        country="japao",
        listing_urls=[
            "https://www.riken.jp/en/news_pubs/news/index.html",
            "https://www.riken.jp/en/careers/",
            "https://www.riken.jp/en/collab/programs/",
            "https://www.riken.jp/pr/news/",
        ],
        allowed_domains=["riken.jp"],
        extra_keywords=[
            "research", "fellowship", "募集", "公募",
            "physics", "chemistry", "quantum",
            "物理", "化学", "量子", "加速器",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="RIKEN",
        orgao_responsavel="RIKEN",
        tipo_oportunidade_hint="pesquisa_colaborativa",
        max_listing_pages=5,
        max_items=30,
    )
    items = [x for x in items if _is_relevant_item(x)]
    save_outputs_asia(Path(__file__).parent, "japan_riken", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_RIKEN] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
