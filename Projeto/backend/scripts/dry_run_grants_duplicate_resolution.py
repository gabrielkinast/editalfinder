#!/usr/bin/env python3
"""
Dry-run de resolução de duplicatas Grants.gov (Backend 10.3B).

Somente leitura — não escreve no banco. Lê duplicate_targets.json (saída do 10.3A)
e separa candidatos a ocultar, já ocultos e inválidos. Com --from-db, valida cada
duplicata contra o registro real (canônico Grants.gov, mesma oportunidade etc.).

Uso:
  python scripts/dry_run_grants_duplicate_resolution.py --input outputs/grants_link_fix/duplicate_targets.json
  python scripts/dry_run_grants_duplicate_resolution.py --input outputs/grants_link_fix/duplicate_targets.json --from-db --limit 2000
"""
from __future__ import annotations

import argparse
import json
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
    write_json,
    write_md,
)
from grants_duplicate_resolution import (  # noqa: E402
    build_duplicate_groups,
    build_hide_candidates,
)

DEFAULT_INPUT = ROOT / "outputs" / "grants_link_fix" / "duplicate_targets.json"
DEFAULT_OUT = ROOT / "outputs" / "grants_duplicate_resolution"


def _load_duplicate_targets(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return raw.get("duplicate_targets") or raw.get("items") or []
    if isinstance(raw, list):
        return raw
    return []


def _records_by_id_from_db(limit: Optional[int]) -> Optional[Dict[int, Dict[str, Any]]]:
    try:
        rows = filter_records_by_source(list(iter_records_from_db(limit=limit)), "grants_gov")
    except Exception as exc:  # noqa: BLE001
        print(f"[dry_run_grants_duplicate_resolution] DB indisponível ({exc}); sem validação rica.")
        return None
    by_id: Dict[int, Dict[str, Any]] = {}
    for r in rows:
        try:
            by_id[int(r.get("id_edital"))] = r
        except (TypeError, ValueError):
            continue
    return by_id


def build_summary_md(result: Dict[str, Any], origin: str, *, group_count: int = 0) -> str:
    s = result["stats"]
    invalid_by_reason: Dict[str, int] = {}
    for item in result["invalid_duplicates"]:
        invalid_by_reason[item.get("reason", "?")] = invalid_by_reason.get(item.get("reason", "?"), 0) + 1

    lines = [
        "# Grants.gov — dry-run de resolução de duplicatas (Backend 10.3B)",
        "",
        f"- **Origem:** {origin}",
        f"- **Validado contra o banco:** {s['validated_against_db']}",
        f"- **Total duplicate_targets:** {s['total_duplicate_targets']}",
        f"- **Candidatos a ocultar:** {s['candidates_to_hide']}",
        f"- **Já ocultos:** {s['already_hidden']}",
        f"- **Inválidos:** {s['invalid_duplicates']}",
        f"- **Grupos duplicados (opportunity_id):** {group_count}",
        f"- **Registros canônicos distintos:** {s['distinct_canonical_records']}",
        "",
        "## Inválidos por motivo",
    ]
    if invalid_by_reason:
        for reason, n in sorted(invalid_by_reason.items(), key=lambda kv: -kv[1]):
            lines.append(f"- {reason}: {n}")
    else:
        lines.append("- (nenhum)")

    lines += ["", "## Exemplos de candidatos a ocultar"]
    for c in result["candidates_to_hide"][:5]:
        lines.append(
            f"- id_edital={c['id_edital']} -> canônico {c['duplicate_of_id_edital']} "
            f"(opp {c['opportunity_id']})"
        )
    if not result["candidates_to_hide"]:
        lines.append("- (nenhum)")

    lines += [
        "",
        "Nenhuma escrita no banco neste passo (dry-run).",
        "",
        "Para aplicar (após revisão):",
        "```powershell",
        '$env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"',
        '$env:EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION="1"',
        "python scripts/apply_grants_duplicate_resolution.py --input outputs/grants_duplicate_resolution/candidates_to_hide.json --confirm",
        "Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY",
        "Remove-Item Env:EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION",
        "```",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run resolução de duplicatas Grants.gov (10.3B)")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--from-db", action="store_true", help="Valida cada duplicata contra o banco")
    ap.add_argument("--limit", type=int, default=2000)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    duplicate_targets = _load_duplicate_targets(args.input)
    origin = f"file:{args.input.name}"
    if not duplicate_targets:
        print(f"[dry_run_grants_duplicate_resolution] Nenhum duplicate_target em {args.input}")

    records_by_id = _records_by_id_from_db(args.limit) if args.from_db else None
    if args.from_db and records_by_id is not None:
        origin += "+db"

    result = build_hide_candidates(duplicate_targets, records_by_id=records_by_id)
    groups = build_duplicate_groups(duplicate_targets, records_by_id=records_by_id)

    out = args.output
    summary_payload = {
        "version": "grants_duplicate_resolution_10.3b",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "origin": origin,
        "stats": {
            **result["stats"],
            "duplicate_groups": len(groups),
            "records_to_hide": result["stats"]["candidates_to_hide"],
            "canonical_records_visible": result["stats"]["distinct_canonical_records"],
        },
    }
    write_json(out / "dry_run_summary.json", summary_payload)
    write_json(
        out / "candidates_to_hide.json",
        {
            "version": "grants_duplicate_resolution_10.3b",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "origin": origin,
            "stats": result["stats"],
            "candidates": result["candidates_to_hide"],
        },
    )
    write_json(out / "already_hidden.json", result["already_hidden"])
    write_json(out / "invalid_duplicates.json", result["invalid_duplicates"])
    write_json(out / "canonical_records.json", result["canonical_records"])
    write_json(
        out / "groups.json",
        {
            "version": "grants_duplicate_resolution_10.3b",
            "generated_at": summary_payload["generated_at"],
            "total_groups": len(groups),
            "groups": groups,
        },
    )
    write_md(out / "summary.md", build_summary_md(result, origin, group_count=len(groups)))

    s = result["stats"]
    print(
        f"[dry_run_grants_duplicate_resolution] total={s['total_duplicate_targets']} "
        f"to_hide={s['candidates_to_hide']} already_hidden={s['already_hidden']} "
        f"invalid={s['invalid_duplicates']} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
