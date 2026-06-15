#!/usr/bin/env python3
"""
Apply controlado de resolução de duplicatas Grants.gov (Backend 10.3B).

Marca registros DUPLICADOS como ocultos via extras.curadoria_front.hidden_duplicate.
Não deleta, não altera link/prazo/titulo, não altera o registro canônico.
Exige flags explícitas + --confirm — sem isso o script aborta. Idempotente.

Uso (PowerShell):
  $env:EDITALFINDER_ALLOW_CONTROLLED_APPLY="1"
  $env:EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION="1"
  python scripts/apply_grants_duplicate_resolution.py --input outputs/grants_duplicate_resolution/candidates_to_hide.json --confirm
  Remove-Item Env:EDITALFINDER_ALLOW_CONTROLLED_APPLY
  Remove-Item Env:EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION
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
from grants_duplicate_resolution import (  # noqa: E402
    apply_hide_candidates,
    controlled_apply_enabled,
    duplicate_resolution_enabled,
)

DEFAULT_INPUT = ROOT / "outputs" / "grants_duplicate_resolution" / "candidates_to_hide.json"
OUT_DIR = ROOT / "outputs" / "grants_duplicate_resolution"


def _load_candidates(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return raw.get("candidates") or raw.get("candidates_to_hide") or []
    if isinstance(raw, list):
        return raw
    return []


def _split_log(log: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    updated: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []
    for item in log:
        status = item.get("status")
        if status == "ok":
            updated.append(item)
        elif status in ("skipped", "already_hidden", "error"):
            skipped.append(item)
    return updated, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description="Apply controlado de duplicatas Grants.gov (10.3B)")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--confirm", action="store_true", help="Confirma apply controlado (obrigatório)")
    ap.add_argument("--confirm-large", action="store_true", help="Permite lote > 100")
    args = ap.parse_args()

    if not args.confirm:
        print("[ABORT] Use --confirm para aplicar.")
        return 2
    if not controlled_apply_enabled():
        print("[ABORT] EDITALFINDER_ALLOW_CONTROLLED_APPLY não está ativo.")
        return 2
    if not duplicate_resolution_enabled():
        print("[ABORT] EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION não está ativo.")
        return 2
    if not args.input.exists():
        print(f"[ABORT] Arquivo não encontrado: {args.input}")
        return 1

    candidates = _load_candidates(args.input)
    if not candidates:
        print("[ABORT] candidates_to_hide vazio.")
        return 1

    try:
        result = apply_hide_candidates(candidates, confirm_large=args.confirm_large)
    except RuntimeError as exc:
        print(f"[ABORT] {exc}")
        return 2

    updated, skipped = _split_log(result.get("log") or [])

    apply_summary = {
        "version": "grants_duplicate_resolution_10.3b",
        "applied_at": result.get("applied_at"),
        "ok": result.get("ok", 0),
        "already_hidden": result.get("already_hidden", 0),
        "skipped": result.get("skipped", 0),
        "errors": result.get("errors", 0),
        "total_candidates": result.get("total_candidates", 0),
        "canonical_records_preserved_visible": result.get("ok", 0) + result.get("already_hidden", 0),
    }

    write_json(OUT_DIR / "apply_log.json", result)
    write_json(OUT_DIR / "apply_summary.json", apply_summary)
    write_json(OUT_DIR / "updated_records.json", updated)
    write_json(OUT_DIR / "skipped_records.json", skipped)
    write_md(
        OUT_DIR / "apply_summary.md",
        "\n".join(
            [
                "# Grants.gov controlled duplicate resolution (Backend 10.3B)",
                "",
                f"- **Ocultados (ok):** {apply_summary['ok']}",
                f"- **Já ocultos:** {apply_summary['already_hidden']}",
                f"- **Ignorados:** {apply_summary['skipped']}",
                f"- **Erros:** {apply_summary['errors']}",
                f"- **Total candidatos:** {apply_summary['total_candidates']}",
                "",
                "Arquivos: `apply_summary.json`, `updated_records.json`, `skipped_records.json`.",
            ]
        ),
    )
    print(
        f"[apply_grants_duplicate_resolution] ok={result['ok']} "
        f"already_hidden={result['already_hidden']} skipped={result['skipped']} "
        f"errors={result['errors']} -> {OUT_DIR}"
    )
    return 0 if result.get("errors", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
