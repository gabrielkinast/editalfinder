#!/usr/bin/env python3
"""
Dry-run before/after para apply controlado BNDES (Backend 10.2D).

Uso:
  python scripts/dry_run_bndes_deadline_apply.py --input outputs/recrawl/bndes/bndes_recrawl.json
  python scripts/dry_run_bndes_deadline_apply.py --input ... --compare-db
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
from bndes_controlled_apply import (  # noqa: E402
    BEFORE_AFTER_FILENAME,
    CANDIDATES_FILENAME,
    NO_DEADLINE_FILENAME,
    OUT_DIR_NAME,
    PDF_CANDIDATES_FILENAME,
    REJECTED_FILENAME,
    SUMMARY_FILENAME,
    run_bndes_deadline_dry_run,
)

OUT_DIR = ROOT / "outputs" / OUT_DIR_NAME


def _load_recrawl_items(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return raw.get("items") or []
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
        "# BNDES deadline apply — dry-run (Backend 10.2D)",
        "",
        f"- **Gerado:** {report.get('generated_at')}",
        f"- **Total recrawled:** {s.get('total_recrawled', 0)}",
        f"- **Detalhe HTML:** {s.get('detail_html_collected', 0)}",
        f"- **PDFs descobertos:** {s.get('pdfs_discovered', 0)}",
        f"- **PDFs extraídos:** {s.get('pdfs_extracted', 0)}",
        f"- **PDFs falhos:** {s.get('pdfs_failed', 0)}",
        f"- **Linhas permanentes:** {s.get('permanent_lines', 0)}",
        f"- **Notícias rejeitadas:** {s.get('news_rejected', 0)}",
        f"- **Chamadas com prazo:** {s.get('calls_with_deadline', 0)}",
        "",
        "## Candidatos",
        "",
        f"- **A atualizar:** {s.get('candidates_to_update', 0)}",
        f"- **Preservados:** {s.get('preserved', 0)}",
        f"- **Sem alteração:** {s.get('unchanged', 0)}",
        f"- **Rejeitados:** {s.get('rejected', 0)}",
        f"- **Sem prazo explicado:** {s.get('no_deadline', 0)}",
        f"- **Candidatos PDF/detail:** {len(report.get('pdf_candidates') or [])}",
        "",
        "Apply **não** executado neste passo.",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run BNDES deadline apply (10.2D)")
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=OUT_DIR)
    ap.add_argument("--compare-db", action="store_true")
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

    report = run_bndes_deadline_dry_run(items, db_by_link=db_by_link)
    out = args.output
    write_json(out / BEFORE_AFTER_FILENAME, report["before_after"])
    write_json(out / CANDIDATES_FILENAME, report["candidates_to_update"])
    write_json(out / REJECTED_FILENAME, report["rejected"])
    write_json(out / NO_DEADLINE_FILENAME, report["no_deadline"])
    write_json(out / PDF_CANDIDATES_FILENAME, report["pdf_candidates"])
    write_json(out / "report.json", report)
    write_md(out / SUMMARY_FILENAME, build_summary_md(report))

    s = report["stats"]
    print(
        f"[dry_run_bndes_deadline_apply] recrawled={s['total_recrawled']} "
        f"update={s['candidates_to_update']} pdf_candidates={len(report['pdf_candidates'])} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
