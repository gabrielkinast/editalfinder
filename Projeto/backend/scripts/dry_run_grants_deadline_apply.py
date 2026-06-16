#!/usr/bin/env python3
"""
Dry-run before/after para apply controlado Grants.gov (Backend 10.2B).

Uso:
  python scripts/dry_run_grants_deadline_apply.py --input outputs/recrawl/grants_gov/grants_gov_recrawl.json
  python scripts/dry_run_grants_deadline_apply.py --input ... --compare-db
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import write_json, write_md  # noqa: E402
from grants_controlled_apply import (  # noqa: E402
    BEFORE_AFTER_FILENAME,
    CANDIDATES_FILENAME,
    NO_DEADLINE_FILENAME,
    OUT_DIR_NAME,
    REJECTED_FILENAME,
    SUMMARY_FILENAME,
    run_grants_deadline_dry_run,
)

OUT_DIR = ROOT / "outputs" / OUT_DIR_NAME


def _load_recrawl_items(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return raw.get("items") or raw.get("enriched") or []
    return []


def _load_db_by_link(links: List[str]) -> Dict[str, Dict[str, Any]]:
    try:
        import loader  # noqa: WPS433
    except Exception:
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for link in links:
        if not link:
            continue
        row = loader.fetch_edital_by_link(link)
        if row:
            out[link] = row
    return out


def build_summary_md(report: Dict[str, Any]) -> str:
    s = report.get("stats") or {}
    lines = [
        "# Grants.gov deadline apply — dry-run (Backend 10.2B)",
        "",
        f"- **Gerado:** {report.get('generated_at')}",
        f"- **Total recrawled:** {s.get('total_recrawled', 0)}",
        f"- **Com closeDate:** {s.get('with_closeDate', 0)}",
        f"- **Sem closeDate:** {s.get('without_closeDate', 0)}",
        f"- **No closing date:** {s.get('no_closing_date_explanation', 0)}",
        f"- **postedDate only:** {s.get('postedDate_only', 0)}",
        "",
        "## Candidatos",
        "",
        f"- **A atualizar:** {s.get('candidates_to_update', 0)}",
        f"- **Preservados:** {s.get('preserved', 0)}",
        f"- **Sem alteração:** {s.get('unchanged', 0)}",
        f"- **Rejeitados:** {s.get('rejected', 0)}",
        f"- **Sem prazo:** {s.get('no_deadline', 0)}",
        "",
        "Apply **não** executado neste passo.",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run Grants.gov deadline apply (10.2B)")
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=OUT_DIR)
    ap.add_argument(
        "--compare-db",
        action="store_true",
        help="Compara com registros existentes no Supabase (somente leitura)",
    )
    args = ap.parse_args()

    if not args.input.exists():
        print(f"[ERRO] Input não encontrado: {args.input}")
        return 1

    items = _load_recrawl_items(args.input)
    if not items:
        write_json(args.output / "report.json", {"error": "empty_input"})
        return 1

    db_by_link: Optional[Dict[str, Dict[str, Any]]] = None
    if args.compare_db:
        links = [str(it.get("link") or "") for it in items]
        db_by_link = _load_db_by_link(links)

    report = run_grants_deadline_dry_run(items, db_by_link=db_by_link)
    out = args.output
    write_json(out / BEFORE_AFTER_FILENAME, report["before_after"])
    write_json(out / CANDIDATES_FILENAME, report["candidates_to_update"])
    write_json(out / REJECTED_FILENAME, report["rejected"])
    write_json(out / NO_DEADLINE_FILENAME, report["no_deadline"])
    write_json(out / "report.json", report)
    write_md(out / SUMMARY_FILENAME, build_summary_md(report))

    s = report["stats"]
    print(
        f"[dry_run_grants_deadline_apply] recrawled={s['total_recrawled']} "
        f"update={s['candidates_to_update']} preserved={s['preserved']} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
