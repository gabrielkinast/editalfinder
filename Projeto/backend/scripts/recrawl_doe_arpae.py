#!/usr/bin/env python3
"""
Recrawl controlado DOE_ARPAE (Backend 10.2C).

Listagem eXCHANGE + enriquecimento de deadlines estruturados do texto disponível.
Sem scraping agressivo; sem escrita no banco.

Uso:
  python scripts/recrawl_doe_arpae.py --limit 200 --output outputs/recrawl/doe_arpae/doe_arpae_recrawl.json
  python scripts/recrawl_doe_arpae.py --limit 50 --no-network
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "CORE"))
sys.path.insert(0, str(ROOT / "scripts"))

from _backend_audit_io import write_json, write_md  # noqa: E402
from doe_arpae_recrawl import (  # noqa: E402
    DOE_RECrawl_VERSION,
    enrich_doe_arpae_recrawl_item,
    stats_for_doe_recrawl_items,
)

DEFAULT_OUT = ROOT / "outputs" / "recrawl" / "doe_arpae" / "doe_arpae_recrawl.json"


def recrawl_doe_arpae(
    limit: int,
    *,
    no_network: bool = False,
    http_timeout: int = 28,
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if no_network:
        fixture = ROOT / "tests" / "fixtures" / "doe_arpae_recrawl_sample.json"
        if not fixture.exists():
            fixture = ROOT / "doe_arpae" / "outputs" / "doe_arpae_editais.json"
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        items = raw if isinstance(raw, list) else raw.get("items", [])
        items = [enrich_doe_arpae_recrawl_item(it) for it in items[:limit]]
        return items, {"mode": "offline_fixture", "fixture": str(fixture), "limit": limit}

    from doe_arpae.main_doe_arpae import collect_arpa_e_exchange_foas

    raw_items = collect_arpa_e_exchange_foas(max_items=limit, http_timeout=http_timeout)
    items = [enrich_doe_arpae_recrawl_item(it) for it in raw_items]
    return items, {
        "mode": "live_exchange_listing",
        "limit": limit,
        "http_timeout": http_timeout,
        "source": "arpa-e-foa.energy.gov",
    }


def build_summary_md(stats: Dict[str, Any], meta: Dict[str, Any]) -> str:
    lines = [
        "# DOE_ARPAE recrawl (Backend 10.2C)",
        "",
        f"- **Modo:** {meta.get('mode')}",
        f"- **Total:** {stats.get('total', 0)}",
        f"- **Com full_application_deadline:** {stats.get('with_full_application_deadline', 0)}",
        f"- **Com concept_paper_deadline:** {stats.get('with_concept_paper_deadline', 0)}",
        f"- **Com submission/application/response:** {stats.get('with_submission_application_response', 0)}",
        f"- **NOFO duas datas:** {stats.get('nofo_two_dates', 0)}",
        f"- **NOFO TBD:** {stats.get('nofo_tbd', 0)}",
        f"- **Sem deadline estruturado:** {stats.get('without_structured_deadline', 0)}",
        f"- **postedDate only:** {stats.get('posted_only', 0)}",
        "",
        "Nenhuma escrita no banco neste passo.",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Recrawl DOE_ARPAE (10.2C)")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--http-timeout", type=int, default=28)
    args = ap.parse_args()

    items, meta = recrawl_doe_arpae(
        args.limit,
        no_network=args.no_network,
        http_timeout=args.http_timeout,
    )
    stats = stats_for_doe_recrawl_items(items)

    payload = {
        "version": DOE_RECrawl_VERSION,
        "stats": stats,
        "meta": meta,
        "items": items,
    }
    write_json(args.output, payload)
    summary_path = args.output.parent / "summary.md"
    write_md(summary_path, build_summary_md(stats, meta))
    print(
        f"[recrawl_doe_arpae] total={stats['total']} "
        f"full_app={stats['with_full_application_deadline']} "
        f"concept={stats['with_concept_paper_deadline']} -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
