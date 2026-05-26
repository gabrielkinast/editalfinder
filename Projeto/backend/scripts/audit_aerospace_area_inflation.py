#!/usr/bin/env python3
"""
Auditoria de inflação de área aeroespacial (Backend 6) — somente leitura.

Uso:
  python scripts/audit_aerospace_area_inflation.py --from-db --limit 5000
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from opportunity_classifier import (  # noqa: E402
    THEMATIC_AREA_BUCKETS,
    _thematic_explicit_field_blob,
    _thematic_tags_meta_blob,
    _thematic_title_desc_blob,
    explain_thematic_area,
)

OUT_DIR = ROOT / "outputs" / "audit_aerospace_area_inflation"

SPACE_TERMS = (
    "satellite",
    "satelite",
    "orbital",
    "orbita",
    "spacecraft",
    "aeroespacial",
    "aerospace",
    "propulsao",
    "propulsion",
    "foguete",
    "espaco",
    "espacial",
)


def _dominant_field(per_channel: Dict[str, Dict[str, int]], area: str) -> str:
    best = ("none", 0)
    for ch in ("title_desc", "explicit_field", "tags_meta", "fonte_hint", "extras"):
        pts = per_channel.get(ch, {}).get(area, 0)
        if pts > best[1]:
            best = (ch, pts)
    return best[0]


def _field_reason_breakdown(explained: List[Dict[str, Any]]) -> Dict[str, int]:
    c: Counter = Counter()
    for ex in explained:
        ch = ex.get("dominant_field") or "none"
        c[ch] += 1
    return dict(c.most_common())


def _analyze_record(rec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ex = explain_thematic_area(rec)
    primary = ex["area_tematica_normalizada"]
    if primary not in ("aeroespacial", "espaco"):
        return None

    title_blob = _thematic_title_desc_blob(rec)
    has_explicit = any(t in title_blob for t in SPACE_TERMS)
    tag_only = ex.get("primary_tag_only", False)

    per_ch = ex.get("per_channel") or {}
    dominant = _dominant_field(per_ch, primary)
    if dominant == "none" and tag_only:
        dominant = "tags_meta"

    suggested = "ok"
    if tag_only and not has_explicit:
        suggested = "multissetorial_or_sem_classificacao"
    elif primary == "aeroespacial" and "defesa" in _thematic_title_desc_blob(rec):
        suggested = "defesa_seguranca"

    return {
        "id_edital": rec.get("id_edital"),
        "titulo": (rec.get("titulo") or "")[:120],
        "fonte_recurso": rec.get("fonte_recurso") or rec.get("fonte"),
        "area_tematica_normalizada": primary,
        "area_tematica_label": ex.get("area_tematica_label"),
        "confidence": ex.get("area_tematica_confidence"),
        "reasons": ex.get("area_tematica_reasons"),
        "secondary": ex.get("area_tematica_secondary"),
        "dominant_field": dominant,
        "primary_tag_only": tag_only,
        "title_has_space_terms": has_explicit,
        "suggested_reclassification": suggested,
        "scores_all": ex.get("scores_all"),
        "area_field": rec.get("area"),
        "setor": rec.get("setor"),
        "tags_sample": (_thematic_tags_meta_blob(rec) or "")[:120],
    }


def run_audit(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    aerospace_rows: List[Dict[str, Any]] = []
    source_c: Counter = Counter()
    explicit_title = 0
    tag_only_count = 0
    should_reclass = Counter()
    tag_inflation_candidates = 0

    for rec in records:
        ex = explain_thematic_area(rec)
        primary = ex["area_tematica_normalizada"]
        tags_blob = _thematic_tags_meta_blob(rec)
        has_aero_tag = any(
            t in tags_blob
            for t in ("aeroespacial", "veiculos", "satellite", "satelite", "spacecraft", "orbital")
        )
        if has_aero_tag and primary not in ("aeroespacial", "espaco"):
            tag_inflation_candidates += 1

        row = _analyze_record(rec)
        if not row:
            continue
        aerospace_rows.append(row)
        source_c[str(row.get("fonte_recurso") or "desconhecida")] += 1
        if row["title_has_space_terms"]:
            explicit_title += 1
        if row["primary_tag_only"]:
            tag_only_count += 1
        should_reclass[row["suggested_reclassification"]] += 1

    high = [r for r in aerospace_rows if r["confidence"] == "alta"][:50]
    low = [r for r in aerospace_rows if r["confidence"] == "baixa"][:50]

    return {
        "total_records": len(records),
        "aerospace_classified_count": len(aerospace_rows),
        "aerospace_pct": round(100 * len(aerospace_rows) / max(1, len(records)), 2),
        "tag_inflation_candidates_downgraded": tag_inflation_candidates,
        "explicit_title_or_desc_count": explicit_title,
        "tag_only_count": tag_only_count,
        "suggested_reclassification": dict(should_reclass),
        "source_breakdown": dict(source_c.most_common(40)),
        "field_reason_breakdown": _field_reason_breakdown(aerospace_rows),
        "examples_high_confidence": high,
        "examples_low_confidence": low,
    }


def build_summary(r: Dict[str, Any]) -> str:
    t = r["total_records"]
    n = r["aerospace_classified_count"]
    lines = [
        "# Auditoria — inflação de área aeroespacial (Backend 6)",
        "",
        f"**Registros analisados:** {t}",
        f"**Classificados como aeroespacial ou espaco:** {n} ({r['aerospace_pct']}%)",
        "",
        "## Por que domina",
        "",
        "A concentração vem principalmente de **tags genéricas** (`thematic_tags`, `setor_estrategico`)",
        "propagadas pelo blob de classificação internacional, sem confirmação em título/descrição.",
        f"- Registros com tag aero/espacial rebaixados (Backend 6): **{r.get('tag_inflation_candidates_downgraded', 0)}**",
        "",
        "## Sinais no corpus",
        f"- Com termo aero/espacial explícito no título/descrição: **{r['explicit_title_or_desc_count']}**",
        f"- Decisão só por tags/metadados (sem título/campo area): **{r['tag_only_count']}**",
        "",
        "## Reclassificação sugerida (heurística)",
        "",
    ]
    for k, v in r.get("suggested_reclassification", {}).items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Top fontes gerando aeroespacial", ""])
    for k, v in list(r.get("source_breakdown", {}).items())[:12]:
        lines.append(f"- {k}: {v}")
    lines.extend(["", "## Campo dominante da decisão", ""])
    for k, v in r.get("field_reason_breakdown", {}).items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            "Artefatos: `report.json`, `examples_aerospace_high_confidence.json`,",
            "`examples_aerospace_low_confidence.json`, `source_breakdown.json`, `field_reason_breakdown.json`.",
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

    report = run_audit(records)
    write_md(OUT_DIR / "summary.md", build_summary(report))
    write_json(OUT_DIR / "report.json", {k: v for k, v in report.items() if not k.startswith("examples_")})
    write_json(OUT_DIR / "examples_aerospace_high_confidence.json", report["examples_high_confidence"])
    write_json(OUT_DIR / "examples_aerospace_low_confidence.json", report["examples_low_confidence"])
    write_json(OUT_DIR / "source_breakdown.json", report["source_breakdown"])
    write_json(OUT_DIR / "field_reason_breakdown.json", report["field_reason_breakdown"])
    print(f"[audit_aerospace] {report['aerospace_classified_count']}/{report['total_records']} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
