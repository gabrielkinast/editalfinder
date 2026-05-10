"""Crawler: Procurement and funding pages from top Chinese universities.

Cobre Tsinghua, Peking University e University of Science and Technology
of China num unico crawler para reduzir ruido na orquestracao.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from asia_source_common import save_outputs_asia, scrape_asia_html_portal


UNIVERSITY_TARGETS = [
    {
        "label": "Tsinghua University",
        "domains": ["tsinghua.edu.cn"],
        "urls": [
            "https://cwc.tsinghua.edu.cn/",
            "https://www.tsinghua.edu.cn/tzgg.htm",
        ],
    },
    {
        "label": "Peking University",
        "domains": ["pku.edu.cn"],
        "urls": [
            "https://cwc.pku.edu.cn/",
            "https://www.pku.edu.cn/tzgg.htm",
        ],
    },
    {
        "label": "University of Science and Technology of China",
        "domains": ["ustc.edu.cn"],
        "urls": [
            "https://www.ustc.edu.cn/tzgg.htm",
            "https://www.ustc.edu.cn/cwc/",
        ],
    },
]


def main() -> int:
    all_items: List[Dict[str, object]] = []
    all_rejected: List[Dict[str, object]] = []
    merged_meta: Dict[str, Any] = {
        "listing_events": [],
        "source_label": "china_university_procurement",
    }
    for target in UNIVERSITY_TARGETS:
        try:
            items, rejected, meta = scrape_asia_html_portal(
                source_label=target["label"],
                country="china",
                listing_urls=target["urls"],
                allowed_domains=target["domains"],
                extra_keywords=[
                    "招标", "采购", "公告", "公示",
                    "项目申报", "课题",
                    "research", "tender", "procurement",
                ],
                accept_language="zh-CN,zh;q=0.9,en;q=0.7",
                instituicao=target["label"],
                orgao_responsavel=target["label"],
                tipo_oportunidade_hint="procurement",
                programa="china_university_procurement",
                max_items=15,
            )
            all_items.extend(items)
            all_rejected.extend(rejected)
            merged_meta["listing_events"].extend(meta.get("listing_events") or [])
        except Exception as exc:
            print(f"[CHINA_UNIVERSITY] Falha em {target['label']}: {exc}")

    ev = list(merged_meta["listing_events"])
    any_ok = any(bool(e.get("ok")) for e in ev)
    attempts = len(ev)
    cf = attempts > 0 and not any_ok
    merged_meta["listing_attempts"] = attempts
    merged_meta["any_listing_ok"] = any_ok
    merged_meta["collection_failed"] = cf
    if all_items:
        merged_meta["tipo_resultado"] = "coleta_com_itens"
    elif cf:
        merged_meta["tipo_resultado"] = "falha_de_coleta"
    elif attempts > 0 and any_ok:
        merged_meta["tipo_resultado"] = "coleta_vazia_pos_filtros"
    else:
        merged_meta["tipo_resultado"] = "coleta_sem_listagens"

    result = save_outputs_asia(
        Path(__file__).parent,
        "china_university_procurement",
        all_items,
        rejected=all_rejected or None,
        crawl_meta=merged_meta,
    )
    print(
        f"[CHINA_UNIVERSITY_PROCUREMENT] validos={len(all_items)} "
        f"rejeitados={len(all_rejected)} (gravado={result.wrote_file}, exit_sugerido={result.suggested_exit_code})"
    )
    return int(result.suggested_exit_code)


if __name__ == "__main__":
    raise SystemExit(main())
