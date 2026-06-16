#!/usr/bin/env python3
"""
Apply controlado — backfill visibility duplicatas Grants.gov (Backend 10.3C).

Uso (PowerShell):
  $env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"
  $env:EDITALFINDER_ALLOW_DUPLICATE_VISIBILITY_BACKFILL="1"
  python scripts/apply_grants_duplicate_visibility_backfill.py --confirm
  Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY
  Remove-Item Env:EDITALFINDER_ALLOW_DUPLICATE_VISIBILITY_BACKFILL
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
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import write_json, write_md  # noqa: E402
from grants_duplicate_visibility_backfill import (  # noqa: E402
    apply_visibility_backfill,
    controlled_apply_enabled,
    visibility_backfill_enabled,
)

DEFAULT_INPUT = ROOT / "outputs" / "grants_duplicate_visibility_backfill" / "candidates_to_update.json"
OUT_DIR = ROOT / "outputs" / "grants_duplicate_visibility_backfill"


def _load_candidates(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return raw.get("candidates_to_update") or raw.get("candidates") or []
    if isinstance(raw, list):
        return raw
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply backfill visibility duplicatas Grants (10.3C)")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--confirm", action="store_true", help="Confirma apply (obrigatório)")
    ap.add_argument("--confirm-large", action="store_true")
    args = ap.parse_args()

    if not args.confirm:
        print("[ABORT] Use --confirm para aplicar.")
        return 2
    if not controlled_apply_enabled():
        print("[ABORT] EDITALFINDER_ALLOW_CONTROLLED_APPLY não está ativo.")
        return 2
    if not visibility_backfill_enabled():
        print("[ABORT] EDITALFINDER_ALLOW_DUPLICATE_VISIBILITY_BACKFILL não está ativo.")
        return 2
    if not args.input.exists():
        print(f"[ABORT] Arquivo não encontrado: {args.input}")
        return 1

    candidates = _load_candidates(args.input)
    if not candidates:
        print("[ABORT] candidates_to_update vazio.")
        return 1

    try:
        result = apply_visibility_backfill(candidates, confirm_large=args.confirm_large)
    except RuntimeError as exc:
        print(f"[ABORT] {exc}")
        return 2

    updated = [x for x in result.get("log", []) if x.get("status") == "ok"]
    skipped = [x for x in result.get("log", []) if x.get("status") not in ("ok", "already_ok")]
    already = [x for x in result.get("log", []) if x.get("status") == "already_ok"]

    summary = {
        "version": "grants_duplicate_visibility_backfill_10.3c",
        "applied_at": result.get("applied_at"),
        "ok": result.get("ok", 0),
        "already_ok": result.get("already_ok", 0),
        "skipped": result.get("skipped", 0),
        "errors": result.get("errors", 0),
        "total_candidates": result.get("total_candidates", 0),
        "anomalies_count": len(result.get("anomalies") or []),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "apply_log.json", result)
    write_json(OUT_DIR / "apply_summary.json", summary)
    write_json(OUT_DIR / "updated_records.json", updated)
    write_json(OUT_DIR / "skipped_records.json", skipped + already)
    write_json(OUT_DIR / "anomalies.json", result.get("anomalies") or [])
    write_md(
        OUT_DIR / "apply_summary.md",
        "\n".join(
            [
                "# Apply — Grants duplicate visibility backfill (10.3C)",
                "",
                f"- **Atualizados:** {summary['ok']}",
                f"- **Já OK:** {summary['already_ok']}",
                f"- **Ignorados:** {summary['skipped']}",
                f"- **Erros:** {summary['errors']}",
                f"- **Anomalias:** {summary['anomalies_count']}",
            ]
        ),
    )
    print(
        f"[apply_grants_duplicate_visibility_backfill] ok={summary['ok']} "
        f"already_ok={summary['already_ok']} errors={summary['errors']} -> {OUT_DIR}"
    )
    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
