"""Crawler: NORINCO Group - paginas publicas institucionais e de
procurement (escopo institucional publico apenas).

ESCOPO RESTRITO: comunicados publicos, paginas corporativas, listagens de
procurement publicas. Nao coleta especificacoes tecnicas, manuais de
equipamento militar, ou conteudo classificado.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


def main() -> int:
    print("[CHINA_NORINCO] Iniciando coleta...")
    items, rejected, _crawl_meta = scrape_asia_html_portal(
        source_label="NORINCO Group (Public)",
        country="china",
        listing_urls=[
            "http://www.norincogroup.com.cn/",
            "http://en.norincogroup.com.cn/",
            "http://www.norincogroup.com.cn/col/col5081/index.html",
        ],
        allowed_domains=["norincogroup.com.cn"],
        extra_keywords=[
            "公告", "新闻", "招标", "采购", "供应商",
            "press", "release", "announcement", "procurement",
            "supplier",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.7",
        instituicao="NORINCO Group",
        orgao_responsavel="NORINCO",
        tipo_oportunidade_hint="noticia_institucional",
        programa="defesa_industrial_china",
        acao="comunicado_publico",
        tipo_recurso="Comunicado / Procurement Publico",
        max_listing_pages=5,
        max_items=15,
    )
    for item in items:
        ex = item.get("extras") or {}
        ex["empresa_prime"] = "NORINCO Group"
        item["extras"] = ex

    result = save_outputs_asia(
        Path(__file__).parent, "china_norinco", items, rejected=rejected, crawl_meta=_crawl_meta
    )
    print(
        f"[CHINA_NORINCO] Registros na saída: {len(items)} (gravado={result.wrote_file}, exit_sugerido={result.suggested_exit_code})"
    )
    return int(result.suggested_exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
