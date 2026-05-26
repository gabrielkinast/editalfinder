#!/usr/bin/env python3
"""
Compara prazos no banco vs parsers Backend 3 por fonte (sem UPDATE).

Uso:
  python scripts/dry_run_source_deadline_improvements.py --from-db
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from deadline_normalizer import normalize_deadline  # noqa: E402
from source_deadline_parsers import (  # noqa: E402
    enrich_araucaria_crawler_item,
    enrich_china_crawler_item,
    enrich_grants_crawler_item,
)

OUT_DIR = ROOT / "outputs" / "source_deadline_improvements"

FOCUS_SOURCES = (
    ("china", ("china international", "mofcom")),
    ("araucaria", ("fundação araucária", "fundacao araucaria")),
    ("grants", ("grants.gov",)),
)


def _match_source(fonte: str, patterns: tuple) -> bool:
    f = fonte.lower()
    return any(p in f for p in patterns)


def _has_db_prazo(rec: Dict[str, Any]) -> bool:
    for k in ("prazo_envio", "fim_inscricao"):
        v = rec.get(k)
        if v and str(v).strip()[:4].isdigit():
            s = str(v).strip()[:10]
            if "-" in s[:10]:
                return True
    return False


def _simulate_reprocess(rec: Dict[str, Any], bucket: str) -> Dict[str, Any]:
    item = {
        "titulo": rec.get("titulo"),
        "descricao": rec.get("descricao"),
        "link": rec.get("link"),
        "fonte": rec.get("fonte_recurso") or rec.get("fonte"),
        "data_publicacao": rec.get("data_publicacao"),
        "fim_inscricao": rec.get("prazo_envio") or rec.get("fim_inscricao"),
        "extras": rec.get("extras") if isinstance(rec.get("extras"), dict) else {},
    }
    if bucket == "china":
        return enrich_china_crawler_item(
            item,
            detail_html=str(item.get("descricao") or ""),
            listing_text=str(item.get("titulo") or ""),
        )
    if bucket == "araucaria":
        return enrich_araucaria_crawler_item(item)
    return enrich_grants_crawler_item(item)


def run_comparison(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    per_source: Dict[str, Any] = {}
    for bucket, patterns in FOCUS_SOURCES:
        subset = [
            r
            for r in records
            if _match_source(str(r.get("fonte_recurso") or r.get("fonte") or ""), patterns)
        ]
        before_dl = sum(1 for r in subset if _has_db_prazo(r))
        after_dl = 0
        gained = 0
        conf_c: Dict[str, int] = {}
        samples = []

        for rec in subset:
            sim = _simulate_reprocess(rec, bucket)
            dl = normalize_deadline(sim)
            if dl.get("prazo_data"):
                after_dl += 1
                conf = dl.get("prazo_confidence") or "nenhuma"
                conf_c[conf] = conf_c.get(conf, 0) + 1
                if not _has_db_prazo(rec):
                    gained += 1
                    if len(samples) < 15:
                        samples.append(
                            {
                                "id_edital": rec.get("id_edital"),
                                "titulo": (rec.get("titulo") or "")[:80],
                                "antes": {"prazo_envio": rec.get("prazo_envio")},
                                "depois": {
                                    "prazo_data": dl.get("prazo_data"),
                                    "prazo_confidence": dl.get("prazo_confidence"),
                                    "prazo_source_field": dl.get("prazo_source_field"),
                                },
                            }
                        )

        per_source[bucket] = {
            "total": len(subset),
            "before_with_deadline": before_dl,
            "after_with_deadline_estimated": after_dl,
            "gained_deadline_count": gained,
            "confidence_distribution": conf_c,
            "sample_before_after": samples,
        }

    return per_source


def build_summary(report: Dict[str, Any]) -> str:
    lines = [
        "# Dry-run melhorias de prazo por fonte — Backend 3",
        "",
        "Simula re-parse com `source_deadline_parsers` sobre registros atuais (sem gravar).",
        "",
    ]
    for bucket, data in report.items():
        t = data["total"]
        lines.extend(
            [
                f"## {bucket}",
                f"- Total: **{t}**",
                f"- Com prazo na BD (antes): **{data['before_with_deadline']}**",
                f"- Com prazo após parser (estimado): **{data['after_with_deadline_estimated']}**",
                f"- Ganho estimado (BD vazia → prazo): **{data['gained_deadline_count']}**",
                f"- Confiança: `{data['confidence_distribution']}`",
                "",
            ]
        )
    lines.append("Ver `report.json` e `*/sample_before_after.json`.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    records = load_records(from_db=args.from_db, input_path=args.input, limit=args.limit)
    if not records:
        write_md(OUT_DIR / "summary.md", "# Sem dados")
        return 1

    report = run_comparison(records)
    write_md(OUT_DIR / "summary.md", build_summary(report))
    write_json(OUT_DIR / "report.json", report)
    for bucket, data in report.items():
        write_json(OUT_DIR / f"{bucket}_sample_before_after.json", data.get("sample_before_after", []))
    print(f"[dry_run_source_deadline_improvements] -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
