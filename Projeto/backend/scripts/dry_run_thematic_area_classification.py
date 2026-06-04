#!/usr/bin/env python3
"""
Dry-run de classificação de área temática (Backend 5/6) — sem UPDATE no banco.

Uso:
  python scripts/dry_run_thematic_area_classification.py --from-db --limit 5000
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from opportunity_classifier import (  # noqa: E402
    classify_thematic_area,
    extract_current_area_labels,
    is_technology_innovation_label,
)
from opportunity_enricher import enrich_opportunity_record  # noqa: E402

OUT_DIR = ROOT / "outputs" / "thematic_area_dry_run"
BACKEND_5_SNAPSHOT = OUT_DIR / "area_distribution_before_after.json"


def _before_primary(labels: List[str]) -> str:
    if not labels:
        return "sem_classificacao"
    for lb in labels:
        if is_technology_innovation_label(lb):
            return "tecnologia_inovacao"
    return labels[0][:40]


def _load_backend5_after() -> Dict[str, int]:
    if not BACKEND_5_SNAPSHOT.exists():
        return {}
    data = json.loads(BACKEND_5_SNAPSHOT.read_text(encoding="utf-8"))
    return data.get("after") or {}


def run_dry_run(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    before_c = Counter()
    after_c = Counter()
    low_conf: List[Dict[str, Any]] = []
    reclassified: List[Dict[str, Any]] = []
    aerospace_reclassified: List[Dict[str, Any]] = []
    examples_by_new: Dict[str, List[Dict[str, Any]]] = {}

    tech_before = 0
    tech_after = 0

    for rec in records:
        labels = extract_current_area_labels(rec)
        before_key = _before_primary(labels)
        before_c[before_key] += 1
        if before_key == "tecnologia_inovacao" or any(is_technology_innovation_label(x) for x in labels):
            tech_before += 1

        enriched = enrich_opportunity_record(rec)
        after_key = enriched.get("area_tematica_normalizada") or "sem_classificacao"
        after_label = enriched.get("area_tematica_label") or after_key
        after_c[after_key] += 1
        if after_key == "tecnologia_inovacao":
            tech_after += 1

        if enriched.get("area_tematica_confidence") == "baixa" and len(low_conf) < 300:
            low_conf.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:90],
                    "area_antes": labels,
                    "area_nova": after_label,
                    "confidence": enriched.get("area_tematica_confidence"),
                }
            )

        was_tech = before_key == "tecnologia_inovacao" or any(is_technology_innovation_label(x) for x in labels)
        if was_tech and after_key != "tecnologia_inovacao":
            if len(reclassified) < 300:
                reclassified.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:100],
                        "area_antes": labels,
                        "area_nova": after_label,
                        "secundarias": enriched.get("area_tematica_secondary"),
                        "reasons": enriched.get("area_tematica_reasons"),
                    }
                )

        raw_cls = classify_thematic_area(rec)
        reasons = raw_cls.get("area_tematica_reasons") or []
        if any("tag_only_downgrade:aeroespacial" in str(x) for x in reasons) and len(aerospace_reclassified) < 400:
            aerospace_reclassified.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:100],
                    "area_nova": after_label,
                    "confidence": enriched.get("area_tematica_confidence"),
                    "secondary": enriched.get("area_tematica_secondary"),
                    "reasons": reasons,
                }
            )

        if len(examples_by_new.get(after_key, [])) < 4:
            examples_by_new.setdefault(after_key, []).append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:80],
                    "label": after_label,
                    "confidence": enriched.get("area_tematica_confidence"),
                }
            )

    backend5_after = _load_backend5_after()
    compare_keys = (
        "aeroespacial",
        "espaco",
        "defesa_seguranca",
        "tecnologias_estrategicas",
        "multissetorial",
        "sem_classificacao",
    )
    backend6_compare = {
        k: {
            "backend_5_after": backend5_after.get(k, 0),
            "backend_6_after": after_c.get(k, 0),
            "delta": after_c.get(k, 0) - backend5_after.get(k, 0),
        }
        for k in compare_keys
    }

    return {
        "total": len(records),
        "technology_innovation_before": tech_before,
        "technology_innovation_after": tech_after,
        "before_distribution": dict(before_c.most_common(30)),
        "after_distribution": dict(after_c.most_common(30)),
        "backend_6_compare": backend6_compare,
        "reclassified_from_tech_count": len(reclassified),
        "aerospace_tag_downgraded_count": len(aerospace_reclassified),
        "low_confidence_count": len(low_conf),
        "examples_by_new_area": examples_by_new,
        "low_confidence_review": low_conf,
        "technology_innovation_reclassified": reclassified,
        "aerospace_reclassified": aerospace_reclassified,
    }


def build_summary(r: Dict[str, Any]) -> str:
    t = r["total"]
    tb = r["technology_innovation_before"]
    ta = r["technology_innovation_after"]
    lines = [
        "# Dry-run área temática — Backend 5",
        "",
        f"**Registros:** {t}",
        "",
        "## Tecnologia e Inovação",
        f"- Antes (rótulo atual ou equivalente): **{tb}** ({100 * tb / t:.1f}%)",
        f"- Depois (classificador backend): **{ta}** ({100 * ta / t:.1f}%)",
        f"- Reclassificados a partir de Tech/Inovação: **{r['reclassified_from_tech_count']}**",
        "",
        "## Top áreas — depois",
        "",
    ]
    for k, v in sorted(r["after_distribution"].items(), key=lambda x: -x[1])[:15]:
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            f"## Baixa confiança: **{r['low_confidence_count']}**",
            "",
            "Artefatos: `area_distribution_before_after.json`, `technology_innovation_reclassified.json`.",
        ]
    )
    return "\n".join(lines)


def build_backend6_summary(r: Dict[str, Any]) -> str:
    t = r["total"]
    cmp = r.get("backend_6_compare") or {}
    lines = [
        "# Dry-run área temática — Backend 6",
        "",
        f"**Registros:** {t}",
        "",
        "## Comparação Backend 5 → Backend 6",
        "",
        "| Área | Backend 5 (after) | Backend 6 | Δ |",
        "|------|-------------------|-----------|---|",
    ]
    for k in (
        "aeroespacial",
        "espaco",
        "defesa_seguranca",
        "tecnologias_estrategicas",
        "multissetorial",
        "sem_classificacao",
    ):
        row = cmp.get(k, {})
        lines.append(
            f"| `{k}` | {row.get('backend_5_after', '—')} | {row.get('backend_6_after', 0)} | {row.get('delta', 0):+d} |"
        )
    lines.extend(
        [
            "",
            f"**Rebaixados por tag aeroespacial sem confirmação:** {r.get('aerospace_tag_downgraded_count', 0)}",
            "",
            "## Top áreas — Backend 6",
            "",
        ]
    )
    for k, v in sorted(r["after_distribution"].items(), key=lambda x: -x[1])[:12]:
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            "Artefatos: `area_distribution_backend_6.json`, `aerospace_reclassified.json`.",
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
    write_md(OUT_DIR / "backend_6_summary.md", build_backend6_summary(report))
    write_json(
        OUT_DIR / "report.json",
        {k: v for k, v in report.items() if k not in ("examples_by_new_area", "low_confidence_review", "technology_innovation_reclassified", "aerospace_reclassified")},
    )
    write_json(
        OUT_DIR / "area_distribution_before_after.json",
        {"before": report["before_distribution"], "after": report["after_distribution"]},
    )
    write_json(OUT_DIR / "area_distribution_backend_6.json", report["after_distribution"])
    write_json(OUT_DIR / "examples_by_new_area.json", report["examples_by_new_area"])
    write_json(OUT_DIR / "low_confidence_review.json", report["low_confidence_review"])
    write_json(OUT_DIR / "technology_innovation_reclassified.json", report["technology_innovation_reclassified"])
    write_json(OUT_DIR / "aerospace_reclassified.json", report["aerospace_reclassified"])
    print(f"[dry_run_thematic_area] {report['total']} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

