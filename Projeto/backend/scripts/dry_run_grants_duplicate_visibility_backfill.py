#!/usr/bin/env python3
"""
Dry-run — backfill de visibility em duplicatas Grants.gov ocultas (Backend 10.3C).

Somente leitura. Não escreve no banco.

Uso:
  python scripts/dry_run_grants_duplicate_visibility_backfill.py --from-db --limit 3000
  python scripts/dry_run_grants_duplicate_visibility_backfill.py --input outputs/grants_duplicate_resolution/updated_records.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

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
from grants_duplicate_visibility_backfill import analyze_visibility_backfill  # noqa: E402

DEFAULT_OUT = ROOT / "outputs" / "grants_duplicate_visibility_backfill"


def _load_target_ids(path: Path) -> List[int]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("candidates") or raw.get("log") or []
    ids = []
    for item in items:
        if isinstance(item, dict) and item.get("id_edital") is not None:
            ids.append(int(item["id_edital"]))
    return ids


def _records_for_run(args: argparse.Namespace) -> List[Dict[str, Any]]:
    if args.from_db:
        rows = list(iter_records_from_db(limit=args.limit))
        return filter_records_by_source(rows, "grants_gov")
    if args.input:
        if args.input.suffix == ".json":
            raw = json.loads(args.input.read_text(encoding="utf-8"))
            if isinstance(raw, list) and raw and "extras" in (raw[0] or {}):
                return [r for r in raw if isinstance(r, dict)]
            target_ids = set(_load_target_ids(args.input))
            rows = list(iter_records_from_db(limit=args.limit))
            grants = filter_records_by_source(rows, "grants_gov")
            return [r for r in grants if int(r.get("id_edital", -1)) in target_ids]
        return load_records_from_json(args.input, limit=args.limit)
    raise RuntimeError("Use --from-db ou --input")


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run backfill visibility duplicatas Grants (10.3C)")
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path, default=None)
    ap.add_argument("--limit", type=int, default=3000)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    if not args.from_db and not args.input:
        ap.error("Informe --from-db ou --input")

    records = _records_for_run(args)
    result = analyze_visibility_backfill(records)
    s = result["stats"]
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    write_json(
        out / "dry_run_summary.json",
        {
            "version": "grants_duplicate_visibility_backfill_10.3c",
            "generated_at": ts,
            "stats": s,
            "sample_candidates": result["candidates_to_update"][:5],
            "sample_anomalies": result["anomalies"][:5],
        },
    )
    write_json(out / "candidates_to_update.json", result["candidates_to_update"])
    write_json(out / "already_ok.json", result["already_ok"])
    write_json(out / "anomalies.json", result["anomalies"])
    write_md(
        out / "summary.md",
        "\n".join(
            [
                "# Dry-run — Grants duplicate visibility backfill (10.3C)",
                "",
                f"- **Analisados:** {s['total_analyzed']}",
                f"- **Já OK:** {s['already_ok']}",
                f"- **Candidatos a atualizar:** {s['candidates_to_update']}",
                f"- **Precisam visibility:** {s['needs_visibility']}",
                f"- **Precisam hidden_duplicate:** {s['needs_hidden_duplicate_boolean']}",
                f"- **Anomalias:** {s['anomalies']}",
                "",
                "Nenhuma escrita no banco.",
            ]
        ),
    )
    print(
        f"[dry_run_grants_duplicate_visibility_backfill] analyzed={s['total_analyzed']} "
        f"ok={s['already_ok']} to_update={s['candidates_to_update']} "
        f"anomalies={s['anomalies']} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
