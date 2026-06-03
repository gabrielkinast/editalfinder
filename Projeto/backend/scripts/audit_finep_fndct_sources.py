#!/usr/bin/env python3
"""
Auditoria FINEP vs FNDCT — Backend 8 (somente leitura).

Uso:
  python scripts/audit_finep_fndct_sources.py --from-db --limit 5000
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
from opportunity_classifier import (  # noqa: E402
    _detect_finep_signals,
    _detect_fndct_signals,
    classify_source_normalized,
)

OUT_DIR = ROOT / "outputs" / "audit_finep_fndct_sources"


def _blob_has_fndct(rec: Dict[str, Any]) -> bool:
    parts = [
        rec.get("fonte_recurso"),
        rec.get("fonte"),
        rec.get("titulo"),
        rec.get("descricao"),
    ]
    return any("fndct" in str(p).lower() for p in parts if p)


def _analyze_record(rec: Dict[str, Any]) -> Dict[str, Any] | None:
    if not _blob_has_fndct(rec):
        return None

    src = classify_source_normalized(rec)
    finep_hit, finep_reasons = _detect_finep_signals(rec)
    fndct_hit, fndct_reasons = _detect_fndct_signals(rec)

    return {
        "id_edital": rec.get("id_edital"),
        "titulo": (rec.get("titulo") or "")[:120],
        "fonte_recurso": rec.get("fonte_recurso") or rec.get("fonte"),
        "link": (rec.get("link") or "")[:120],
        "fonte_normalizada": src.get("fonte_normalizada"),
        "fundo_origem": src.get("fundo_origem"),
        "probably_finep": finep_hit,
        "finep_signals": finep_reasons,
        "fndct_signals": fndct_reasons,
        "source_notes": src.get("source_notes"),
    }


def run_audit(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    suspicious: List[Dict[str, Any]] = []
    as_fndct_norm = 0
    probably_finep = 0

    for rec in records:
        row = _analyze_record(rec)
        if not row:
            continue
        rows.append(row)
        norm = str(row.get("fonte_normalizada") or "").upper()
        if "FNDCT" in norm and "FINEP" not in norm:
            as_fndct_norm += 1
            if row["probably_finep"] and len(suspicious) < 200:
                suspicious.append(row)
        if row["probably_finep"]:
            probably_finep += 1

    examples = rows[:80]
    return {
        "total_records": len(records),
        "fndct_related_count": len(rows),
        "normalized_as_fndct_only": as_fndct_norm,
        "probably_finep_count": probably_finep,
        "would_normalize_finep": sum(1 for r in rows if r["probably_finep"]),
        "examples": examples,
        "suspicious_source_names": suspicious,
    }


def build_summary(r: Dict[str, Any]) -> str:
    lines = [
        "# Auditoria FINEP / FNDCT — Backend 8",
        "",
        f"**Registros analisados:** {r['total_records']}",
        f"**Com menção FNDCT (fonte/título/descrição):** {r['fndct_related_count']}",
        f"**Normalizados como FNDCT (sem FINEP):** {r['normalized_as_fndct_only']}",
        f"**Provavelmente FINEP (sinais fortes):** {r['probably_finep_count']}",
        f"**Passariam a fonte_normalizada=FINEP:** {r['would_normalize_finep']}",
        "",
        "## Conceito",
        "",
        "- **FINEP** — agência operadora / fonte institucional visível na UI.",
        "- **FNDCT** — fundo de origem do recurso (`fundo_origem`), não substitui FINEP quando ambos aparecem.",
        "",
        "## Sinais FINEP auditados",
        "",
        "- Domínio `finep.gov.br` no link",
        "- FINEP em fonte, título, descrição ou extras (`agencia`, `orgao`)",
        "",
        "Artefatos: `report.json`, `finep_fndct_examples.json`, `suspicious_source_names.json`.",
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

    report = run_audit(records)
    write_md(OUT_DIR / "summary.md", build_summary(report))
    write_json(
        OUT_DIR / "report.json",
        {k: v for k, v in report.items() if k not in ("examples", "suspicious_source_names")},
    )
    write_json(OUT_DIR / "finep_fndct_examples.json", report["examples"])
    write_json(OUT_DIR / "suspicious_source_names.json", report["suspicious_source_names"])
    print(f"[audit_finep_fndct] {report['fndct_related_count']}/{report['total_records']} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
