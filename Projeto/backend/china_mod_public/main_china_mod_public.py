"""Crawler: Ministry of National Defense of the PRC - PUBLIC announcements only.

ESCOPO: apenas comunicados publicos institucionais (press releases, white
papers em formato resumo). Nao coleta documentos operacionais, manuais de
equipamento, especificacoes tecnicas militares ou conteudo sensivel.
A area de procurement do PLA fica explicitamente NO ROADMAP, nao e
implementada por este crawler.
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
        source_label="China MOD (public)",
        country="china",
        listing_urls=[
            "http://www.mod.gov.cn/",
            "http://eng.mod.gov.cn/",
            "http://www.mod.gov.cn/gfbw/index.htm",
        ],
        allowed_domains=["mod.gov.cn"],
        extra_keywords=[
            "公告", "新闻", "白皮书",
            "press", "announcement", "release", "white paper",
        ],
        accept_language="zh-CN,zh;q=0.9,en;q=0.7",
        instituicao="Ministry of National Defense (PRC)",
        orgao_responsavel="China MoND",
        tipo_oportunidade_hint="noticia_institucional",
        programa="defesa_industrial_china",
        acao="comunicado_publico",
        tipo_recurso="Comunicado Institucional",
        max_items=20,
    )
    save_outputs_asia(Path(__file__).parent, "china_mod_public", items, rejected=rejected, crawl_meta=_crawl_meta)
    print(f"[CHINA_MOD_PUBLIC] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
