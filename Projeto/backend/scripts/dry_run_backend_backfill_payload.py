#!/usr/bin/env python3
"""
Dry-run de payload de backfill Backend 6 — gera JSON de UPDATE sem executar SQL.

Uso:
  python scripts/dry_run_backend_backfill_payload.py --from-db --limit 5000
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from opportunity_enricher import ENRICHMENT_TOP_LEVEL_KEYS, enrich_opportunity_record  # noqa: E402

OUT_DIR = ROOT / "outputs" / "backend_backfill_payload_dry_run"

BACKFILL_COLUMNS = ENRICHMENT_TOP_LEVEL_KEYS + ("backend_enrichment", "area_tematica_secondary_keys")


def _payload_for_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    enriched = enrich_opportunity_record(rec)
    payload: Dict[str, Any] = {"id_edital": rec.get("id_edital")}
    for col in BACKFILL_COLUMNS:
        if col in enriched:
            payload[col] = enriched[col]
    payload["backend_enrichment"] = enriched.get("extras", {}).get("backend_enrichment") or {}
    return payload


def _would_change(rec: Dict[str, Any], payload: Dict[str, Any], col: str) -> bool:
    old = rec.get(col)
    new = payload.get(col)
    if old is None and new in (None, "", [], {}):
        return False
    return old != new


def run_dry_run(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    gains: Counter = Counter()
    low_conf: Counter = Counter()
    tipo_changes = 0
    area_changes = 0
    prazo_low = 0
    samples: List[Dict[str, Any]] = []
    risky: List[Dict[str, Any]] = []

    for rec in records:
        payload = _payload_for_record(rec)
        changed_cols: Dict[str, Any] = {}
        for col in BACKFILL_COLUMNS:
            if col == "backend_enrichment":
                continue
            if _would_change(rec, payload, col):
                changed_cols[col] = {"old": rec.get(col), "new": payload.get(col)}
            if payload.get(col) not in (None, "", [], {}):
                gains[col] += 1

        if payload.get("prazo_confidence") == "baixa":
            prazo_low += 1
            low_conf["prazo_confidence_baixa"] += 1
        if payload.get("area_tematica_confidence") == "baixa":
            low_conf["area_tematica_confidence_baixa"] += 1

        if changed_cols.get("tipo_registro"):
            tipo_changes += 1
        if changed_cols.get("area_tematica_normalizada") or changed_cols.get("area_tematica_label"):
            area_changes += 1

        if len(samples) < 5:
            samples.append({"id_edital": rec.get("id_edital"), "update_payload": payload})

        if (
            payload.get("area_tematica_confidence") == "baixa"
            or payload.get("prazo_confidence") == "baixa"
            or payload.get("kind_confidence") == "baixa"
        ) and len(risky) < 200:
            risky.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:90],
                    "changed_columns": list(changed_cols.keys()),
                    "area_tematica": payload.get("area_tematica_label"),
                    "area_confidence": payload.get("area_tematica_confidence"),
                    "prazo_confidence": payload.get("prazo_confidence"),
                }
            )

    return {
        "total": len(records),
        "records_with_any_new_field": sum(1 for _ in records),
        "gains_by_column": dict(gains.most_common()),
        "low_confidence_counts": dict(low_conf),
        "tipo_registro_would_change": tipo_changes,
        "area_tematica_would_change": area_changes,
        "prazo_baixa_confidence": prazo_low,
        "sample_update_payload": samples,
        "risky_updates_review": risky,
    }


def build_summary(r: Dict[str, Any]) -> str:
    lines = [
        "# Dry-run payload de backfill — Backend 6",
        "",
        f"**Registros:** {r['total']}",
        "",
        "## Campos que ganhariam valor",
        "",
    ]
    for col, n in r.get("gains_by_column", {}).items():
        lines.append(f"- `{col}`: {n}")
    lines.extend(
        [
            "",
            f"**Mudariam tipo_registro:** {r.get('tipo_registro_would_change', 0)}",
            f"**Mudariam área temática:** {r.get('area_tematica_would_change', 0)}",
            f"**Prazo com baixa confiança:** {r.get('prazo_baixa_confidence', 0)}",
            "",
            "## Baixa confiança",
            "",
        ]
    )
    for k, v in r.get("low_confidence_counts", {}).items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            "Nenhum UPDATE foi executado. Ver `sample_update_payload.json` e `risky_updates_review.json`.",
        ]
    )
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
    write_json(OUT_DIR / "sample_update_payload.json", report["sample_update_payload"])
    write_json(OUT_DIR / "changes_by_column.json", report["gains_by_column"])
    write_json(
        OUT_DIR / "report.json",
        {k: v for k, v in report.items() if k not in ("sample_update_payload", "risky_updates_review")},
    )
    write_json(OUT_DIR / "risky_updates_review.json", report["risky_updates_review"])
    print(f"[dry_run_backend_backfill] {report['total']} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
