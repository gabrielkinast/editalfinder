"""Crawler: e-Rad Japan (paginas publicas).

A submissao real exige login institucional. Aqui coletamos apenas a area
publica de noticias e listagem de chamadas.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal

SOURCE_NAME = "e-Rad"


def _keep_erad_item(it: dict) -> bool:
    lk = (it.get("link") or "").lower()
    tit = str(it.get("titulo") or "")
    if "/organ/procedure" in lk or "procedure.html" in lk:
        return False
    if "新規登録" in tit and ("ログイン" in tit or "パスワード" in str(it.get("descricao") or "")):
        return False
    return True


def main() -> int:
    print(f"[{SOURCE_NAME}] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label=SOURCE_NAME,
        country="japao",
        listing_urls=[
            "https://www.e-rad.go.jp/news/index.html",
            "https://www.e-rad.go.jp/topics/index.html",
        ],
        allowed_domains=["e-rad.go.jp"],
        extra_keywords=[
            "公募", "募集", "お知らせ", "新規", "research",
            "提案", "助成",
        ],
        accept_language="ja,en;q=0.8",
        instituicao="e-Rad / Japan Cross-ministerial R&D Management System",
        orgao_responsavel="Cabinet Office of Japan",
        tipo_oportunidade_hint="funding_opportunity",
        max_items=40,
        max_listing_pages=5,
    )
    items = [x for x in items if _keep_erad_item(x)]
    result = save_outputs_asia(
        Path(__file__).parent, "japan_e_rad", items, rejected=rejected, crawl_meta=_crawl_meta
    )
    print(f"[JAPAN_E_RAD] Registros na saída: {len(items)} (gravado={result.wrote_file})")
    return int(result.suggested_exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
