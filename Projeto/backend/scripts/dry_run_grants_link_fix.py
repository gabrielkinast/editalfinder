#!/usr/bin/env python3
"""
Dry-run de correção de links Grants.gov (Backend 10.3A).

Somente leitura — não escreve no banco. Gera a lista de candidatos a update
que o apply controlado consumirá.

Uso:
  python scripts/dry_run_grants_link_fix.py --from-db --limit 1000
  python scripts/dry_run_grants_link_fix.py --input outputs/recrawl/grants_gov/grants_gov_recrawl.json
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import (  # noqa: E402
    filter_records_by_source,
    iter_records_from_db,
    load_records_from_json,
    write_json,
    write_md,
)
from grants_link_resolver import build_link_fix_candidates  # noqa: E402

DEFAULT_OUT = ROOT / "outputs" / "grants_link_fix"
DEFAULT_RECRAWL = ROOT / "outputs" / "recrawl" / "grants_gov" / "grants_gov_recrawl.json"


def _load_records(
    *,
    from_db: bool,
    input_path: Optional[Path],
    limit: Optional[int],
) -> tuple[List[Dict[str, Any]], str]:
    if from_db:
        try:
            rows = list(iter_records_from_db(limit=limit))
            return filter_records_by_source(rows, "grants_gov"), "database"
        except Exception as exc:  # noqa: BLE001
            print(f"[dry_run_grants_link_fix] DB indisponível ({exc}); usando fallback local.")
    path = input_path or DEFAULT_RECRAWL
    if path.exists():
        rows = load_records_from_json(path, limit=limit)
        return filter_records_by_source(rows, "grants_gov"), f"file:{path.name}"
    return [], "none"


def build_summary_md(result: Dict[str, Any], origin: str) -> str:
    s = result["stats"]
    lines = [
        "# Grants.gov — dry-run de correção de links (Backend 10.3A)",
        "",
        f"- **Origem dos dados:** {origin}",
        f"- **Total Grants.gov:** {s['total_grants']}",
        f"- **Candidatos a update:** {s['candidates_to_update']}",
        f"  - canonical_detail: {s['canonical_detail_updates']}",
        f"  - search_fallback: {s['search_fallback_updates']}",
        f"- **Sem mudança:** {s['no_change']}",
        f"- **Não corrigíveis:** {s['invalid_unfixable']}",
        f"- **Alvos duplicados (mesma oportunidade, link UNIQUE):** {s.get('duplicate_targets', 0)}",
        "",
        "Nenhuma escrita no banco neste passo (dry-run).",
        "",
        "Para aplicar (apenas após revisão):",
        "```powershell",
        '$env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"',
        '$env:EDITALFINDER_ALLOW_LINK_FIX="1"',
        "python scripts/apply_grants_link_fix.py --input outputs/grants_link_fix/candidates_to_update.json",
        "Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY",
        "Remove-Item Env:EDITALFINDER_ALLOW_LINK_FIX",
        "```",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run correção de links Grants.gov (10.3A)")
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path, default=None)
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    records, origin = _load_records(
        from_db=args.from_db, input_path=args.input, limit=args.limit
    )
    result = build_link_fix_candidates(records)

    out = args.output
    write_json(
        out / "candidates_to_update.json",
        {
            "version": "grants_link_fix_10.3a",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "origin": origin,
            "stats": result["stats"],
            "candidates": result["candidates_to_update"],
        },
    )
    write_json(out / "no_change.json", result["no_change"])
    write_json(out / "invalid_unfixable.json", result["invalid_unfixable"])
    write_json(out / "duplicate_targets.json", result.get("duplicate_targets", []))
    write_md(out / "summary.md", build_summary_md(result, origin))

    s = result["stats"]
    print(
        f"[dry_run_grants_link_fix] candidates={s['candidates_to_update']} "
        f"no_change={s['no_change']} unfixable={s['invalid_unfixable']} "
        f"duplicates={s.get('duplicate_targets', 0)} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
