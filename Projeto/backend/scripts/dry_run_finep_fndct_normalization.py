#!/usr/bin/env python3
"""
Dry-run normalização FINEP/FNDCT — Backend 8 (sem UPDATE).

Uso:
  python scripts/dry_run_finep_fndct_normalization.py --from-db --limit 5000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from opportunity_classifier import classify_source_normalized  # noqa: E402
from opportunity_enricher import enrich_opportunity_record  # noqa: E402

OUT_DIR = ROOT / "outputs" / "finep_fndct_normalization_dry_run"


def _is_fndct_related(rec: Dict[str, Any]) -> bool:
    blob = " ".join(
        str(rec.get(k) or "")
        for k in ("fonte_recurso", "fonte", "titulo", "descricao", "link")
    ).lower()
    return "fndct" in blob or "finep" in blob


def run_dry_run(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    before_after: List[Dict[str, Any]] = []
    changed: List[Dict[str, Any]] = []
    to_finep = 0
    keep_fndct = 0
    with_fundo_fndct = 0

    for rec in records:
        if not _is_fndct_related(rec):
            continue

        before_src = str(rec.get("fonte_recurso") or rec.get("fonte") or "")
        old_norm = classify_source_normalized(
            {**rec, "fonte_recurso": before_src, "fonte": before_src}
        )
        # Simular "antes": alias simples sem regra FINEP
        before_normalized = before_src
        if "finep" in before_src.lower():
            before_normalized = "FINEP"
        elif "fndct" in before_src.lower():
            before_normalized = "FNDCT"

        enriched = enrich_opportunity_record(rec)
        after_norm = enriched.get("fonte_normalizada")
        fundo = enriched.get("fundo_origem")

        row = {
            "id_edital": rec.get("id_edital"),
            "titulo": (rec.get("titulo") or "")[:100],
            "fonte_recurso": before_src,
            "before_fonte_normalizada": before_normalized,
            "after_fonte_normalizada": after_norm,
            "fundo_origem": fundo,
            "programa_fundo": enriched.get("programa_fundo"),
            "source_notes": enriched.get("source_notes"),
        }
        before_after.append(row)

        if str(after_norm).upper() == "FINEP":
            to_finep += 1
        elif str(after_norm).upper() == "FNDCT":
            keep_fndct += 1
        if fundo == "FNDCT":
            with_fundo_fndct += 1

        if before_normalized != after_norm and len(changed) < 300:
            changed.append(row)

    return {
        "total_records": len(records),
        "finep_fndct_related": len(before_after),
        "would_be_finep": to_finep,
        "would_keep_fndct_source": keep_fndct,
        "with_fundo_origem_fndct": with_fundo_fndct,
        "changed_count": len([r for r in before_after if r["before_fonte_normalizada"] != r["after_fonte_normalizada"]]),
        "before_after_sources": before_after,
        "changed_records_review": changed,
    }


def build_summary(r: Dict[str, Any]) -> str:
    lines = [
        "# Dry-run FINEP/FNDCT — Backend 8",
        "",
        f"**Registros no corpus:** {r['total_records']}",
        f"**Relacionados FINEP/FNDCT:** {r['finep_fndct_related']}",
        "",
        "## Resultado da normalização",
        f"- **fonte_normalizada = FINEP:** {r['would_be_finep']}",
        f"- **fonte_normalizada = FNDCT (sem forçar FINEP):** {r['would_keep_fndct_source']}",
        f"- **fundo_origem = FNDCT:** {r['with_fundo_origem_fndct']}",
        f"- **Mudanças vs rótulo legado simplificado:** {r['changed_count']}",
        "",
        "Artefatos: `before_after_sources.json`, `changed_records_review.json`.",
        "",
        "Nenhum UPDATE executado.",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--limit", type=int, default=5000)
    args = ap.parse_args()

    records = load_records(from_db=args.from_db, input_path=args.input, limit=args.limit)
    if not records:
        write_md(OUT_DIR / "summary.md", "# Sem dados")
        return 1

    report = run_dry_run(records)
    write_md(OUT_DIR / "summary.md", build_summary(report))
    write_json(
        OUT_DIR / "report.json",
        {k: v for k, v in report.items() if k not in ("before_after_sources", "changed_records_review")},
    )
    write_json(OUT_DIR / "before_after_sources.json", report["before_after_sources"])
    write_json(OUT_DIR / "changed_records_review.json", report["changed_records_review"])
    print(f"[dry_run_finep_fndct] {report['finep_fndct_related']} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
