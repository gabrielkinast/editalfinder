#!/usr/bin/env python3
"""
Recrawl controlado Grants.gov / Simpler API (Backend 10.2B).

Preserva closeDate, postedDate, archiveDate, closeDateExplanation em extras.
Sem escrita no banco.

Uso:
  python scripts/recrawl_grants_gov.py --limit 500 --output outputs/recrawl/grants_gov/grants_gov_recrawl.json
  python scripts/recrawl_grants_gov.py --limit 50 --no-network
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _backend_audit_io import write_json, write_md  # noqa: E402

DEFAULT_OUT = ROOT / "outputs" / "recrawl" / "grants_gov" / "grants_gov_recrawl.json"


def _stats_for_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        "total": len(items),
        "with_closeDate": 0,
        "without_closeDate": 0,
        "no_closing_date_explanation": 0,
        "postedDate_only": 0,
        "with_archiveDate": 0,
    }
    import re

    for it in items:
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        close = ex.get("closeDate") or ex.get("close_date") or it.get("fim_inscricao")
        posted = ex.get("postedDate") or ex.get("posted_date") or it.get("data_publicacao")
        archive = ex.get("archiveDate") or ex.get("archive_date")
        expl = str(ex.get("closeDateExplanation") or ex.get("close_date_explanation") or "")

        if close:
            stats["with_closeDate"] += 1
        else:
            stats["without_closeDate"] += 1
        if re.search(r"no\s+closing\s+date", expl, re.I):
            stats["no_closing_date_explanation"] += 1
        if posted and not close:
            stats["postedDate_only"] += 1
        if archive:
            stats["with_archiveDate"] += 1
    return stats


def recrawl_grants_gov(
    limit: int,
    *,
    no_network: bool = False,
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if no_network:
        fixture = ROOT / "grants_gov" / "outputs" / "grants_gov_editais.json"
        if not fixture.exists():
            fixture = ROOT / "tests" / "fixtures" / "grants_gov_recrawl_sample.json"
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        items = raw if isinstance(raw, list) else raw.get("items", [])
        items = items[:limit]
        meta = {"mode": "offline_fixture", "fixture": str(fixture), "limit": limit}
        return items, meta

    from grants_gov.simpler_grants_common import collect_opportunities

    max_pages = max(1, (limit + 24) // 25)
    items, api_meta = collect_opportunities(
        max_pages=max_pages,
        max_items=limit,
        include_historic=True,
    )
    meta = {"mode": "live_api", "limit": limit, "api_meta": api_meta}
    return items[:limit], meta


def build_summary_md(stats: Dict[str, Any], meta: Dict[str, Any]) -> str:
    lines = [
        "# Grants.gov recrawl (Backend 10.2B)",
        "",
        f"- **Modo:** {meta.get('mode')}",
        f"- **Total:** {stats.get('total', 0)}",
        f"- **Com closeDate:** {stats.get('with_closeDate', 0)}",
        f"- **Sem closeDate:** {stats.get('without_closeDate', 0)}",
        f"- **No closing date (explanation):** {stats.get('no_closing_date_explanation', 0)}",
        f"- **postedDate only:** {stats.get('postedDate_only', 0)}",
        f"- **Com archiveDate:** {stats.get('with_archiveDate', 0)}",
        "",
        "Nenhuma escrita no banco neste passo.",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Recrawl Grants.gov (10.2B)")
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--no-network", action="store_true", help="Usa fixture local (testes/offline)")
    args = ap.parse_args()

    items, meta = recrawl_grants_gov(args.limit, no_network=args.no_network)
    stats = _stats_for_items(items)

    payload = {
        "version": "grants_recrawl_10.2b",
        "stats": stats,
        "meta": meta,
        "items": items,
    }
    write_json(args.output, payload)
    summary_path = args.output.parent / "summary.md"
    write_md(summary_path, build_summary_md(stats, meta))
    print(
        f"[recrawl_grants_gov] total={stats['total']} "
        f"closeDate={stats['with_closeDate']} -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
