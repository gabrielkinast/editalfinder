"""Crawler: NIMS - National Institute for Materials Science."""

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
    if any(k in text for k in ("introduction", "about nims", "privacy", "sns", "twitter.com", "linkedin.com", "youtube.com")):
        return False
    if not any(k in link for k in ("/news", "/recruit", "/employment", "/event", "/publicity", "/tender", "/procurement")):
        if not any(k in text for k in ("call", "open", "application", "recruit", "公募", "募集", "入札")):
            return False
    return any(k in text for k in ("call", "open", "application", "recruit", "fellowship", "公募", "募集", "入札", "tender"))


def main() -> None:
    print("[JAPAN_NIMS] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="NIMS",
        country="japao",
        listing_urls=[
            "https://www.nims.go.jp/eng/news/index.html",
            "https://www.nims.go.jp/news/",
            "https://www.nims.go.jp/research/index.html",
            "https://www.nims.go.jp/eng/employment/index.html",
        ],
        allowed_domains=["nims.go.jp"],
        extra_keywords=[
            "材料", "先端材料", "半導体", "ナノ",
            "materials", "advanced materials", "nano",
            "公募", "募集", "research",
        ],
        accept_language="ja,en;q=0.9",
        instituicao="National Institute for Materials Science",
        orgao_responsavel="NIMS",
        tipo_oportunidade_hint="funding_opportunity",
        max_listing_pages=5,
        max_items=30,
    )
    items = [x for x in items if _is_relevant_item(x)]
    save_outputs_asia(Path(__file__).parent, "japan_nims", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[JAPAN_NIMS] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
