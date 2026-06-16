#!/usr/bin/env python3
"""
Apply controlado de deadlines DOE_ARPAE (Backend 10.2C).

Exige flags explícitas — sem elas o script aborta.

Uso (bash):
  EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1 \\
  EDITALFINDER_ALLOW_CONTROLLED_APPLY=1 \\
  python scripts/apply_doe_arpae_deadline_backfill.py \\
    --input outputs/doe_arpae_deadline_apply/candidates_to_update.json

Uso (PowerShell):
  $env:EDITALFINDER_ENABLE_DEADLINE_BACKFILL="1"
  $env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"
  python scripts/apply_doe_arpae_deadline_backfill.py --input outputs/doe_arpae_deadline_apply/candidates_to_update.json
  Remove-Item Env:EDITALFINDER_ENABLE_DEADLINE_BACKFILL
  Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import write_json, write_md  # noqa: E402
from deadline_backfill import controlled_apply_enabled, deadline_backfill_enabled  # noqa: E402
from doe_arpae_controlled_apply import apply_doe_arpae_candidates, load_candidates_file  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply controlado DOE_ARPAE deadlines (10.2C)")
    ap.add_argument(
        "--input",
        type=Path,
        default=ROOT / "outputs" / "doe_arpae_deadline_apply" / "candidates_to_update.json",
    )
    ap.add_argument("--confirm-large", action="store_true")
    ap.add_argument("--skip-dry-run-check", action="store_true", help="Somente testes")
    args = ap.parse_args()

    if not controlled_apply_enabled():
        print(
            "[ABORT] EDITALFINDER_ALLOW_CONTROLLED_APPLY não está ativo. "
            "Defina EDITALFINDER_ALLOW_CONTROLLED_APPLY=1 para apply."
        )
        return 2
    if not deadline_backfill_enabled():
        print(
            "[ABORT] EDITALFINDER_ENABLE_DEADLINE_BACKFILL não está ativo. "
            "Defina EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1."
        )
        return 2

    if not args.input.exists():
        print(f"[ABORT] Arquivo não encontrado: {args.input}")
        return 1

    candidates = load_candidates_file(args.input)
    if not candidates:
        print("[ABORT] candidates_to_update vazio.")
        return 1

    try:
        result = apply_doe_arpae_candidates(
            candidates,
            root=ROOT,
            confirm_large=args.confirm_large,
            skip_dry_run_check=args.skip_dry_run_check,
        )
    except RuntimeError as exc:
        print(f"[ABORT] {exc}")
        return 2

    out_dir = ROOT / "outputs" / "doe_arpae_deadline_apply"
    write_json(out_dir / "apply_log.json", result)
    write_md(
        out_dir / "apply_summary.md",
        "\n".join(
            [
                "# DOE_ARPAE controlled apply",
                "",
                f"- **Aplicados (ok):** {result.get('ok', 0)}",
                f"- **Erros:** {result.get('errors', 0)}",
                f"- **Ignorados:** {result.get('skipped', 0)}",
                f"- **Total candidatos:** {result.get('total_candidates', 0)}",
            ]
        ),
    )
    print(
        f"[apply_doe_arpae_deadline_backfill] ok={result['ok']} "
        f"errors={result['errors']} -> {out_dir / 'apply_log.json'}"
    )
    return 0 if result.get("errors", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
