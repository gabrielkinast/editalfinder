#!/usr/bin/env python3
"""
Apply controlado de correção de links Grants.gov (Backend 10.3A).

Exige flags explícitas — sem elas o script aborta.

Uso (PowerShell):
  $env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"
  $env:EDITALFINDER_ALLOW_LINK_FIX="1"
  python scripts/apply_grants_link_fix.py --input outputs/grants_link_fix/candidates_to_update.json
  Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY
  Remove-Item Env:EDITALFINDER_ALLOW_LINK_FIX
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
from grants_link_apply import (  # noqa: E402
    apply_grants_link_candidates,
    controlled_apply_enabled,
    link_fix_enabled,
)

DEFAULT_INPUT = ROOT / "outputs" / "grants_link_fix" / "candidates_to_update.json"
OUT_DIR = ROOT / "outputs" / "grants_link_fix"


def _load_candidates(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return raw.get("candidates") or raw.get("candidates_to_update") or []
    if isinstance(raw, list):
        return raw
    return []


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply controlado de links Grants.gov (10.3A)")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--confirm-large", action="store_true", help="Permite lote > 100")
    args = ap.parse_args()

    if not controlled_apply_enabled():
        print(
            "[ABORT] EDITALFINDER_ALLOW_CONTROLLED_APPLY não está ativo. "
            "Defina EDITALFINDER_ALLOW_CONTROLLED_APPLY=1 para apply."
        )
        return 2
    if not link_fix_enabled():
        print(
            "[ABORT] EDITALFINDER_ALLOW_LINK_FIX não está ativo. "
            "Defina EDITALFINDER_ALLOW_LINK_FIX=1 para correção de links."
        )
        return 2

    if not args.input.exists():
        print(f"[ABORT] Arquivo não encontrado: {args.input}")
        return 1

    candidates = _load_candidates(args.input)
    if not candidates:
        print("[ABORT] candidates_to_update vazio.")
        return 1

    try:
        result = apply_grants_link_candidates(candidates, confirm_large=args.confirm_large)
    except RuntimeError as exc:
        print(f"[ABORT] {exc}")
        return 2

    write_json(OUT_DIR / "apply_log.json", result)
    write_md(
        OUT_DIR / "apply_summary.md",
        "\n".join(
            [
                "# Grants.gov controlled link fix (Backend 10.3A)",
                "",
                f"- **Aplicados (ok):** {result.get('ok', 0)}",
                f"- **Erros:** {result.get('errors', 0)}",
                f"- **Ignorados:** {result.get('skipped', 0)}",
                f"- **Total candidatos:** {result.get('total_candidates', 0)}",
            ]
        ),
    )
    print(
        f"[apply_grants_link_fix] ok={result['ok']} errors={result['errors']} "
        f"skipped={result['skipped']} -> {OUT_DIR / 'apply_log.json'}"
    )
    return 0 if result.get("errors", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
