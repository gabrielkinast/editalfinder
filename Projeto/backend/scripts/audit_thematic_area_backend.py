#!/usr/bin/env python3
"""
Auditoria de área temática no backend (Backend 5) — somente leitura.

Uso:
  python scripts/audit_thematic_area_backend.py --from-db --limit 5000
"""
from __future__ import annotations

import argparse
import random
import sys
from collections import Counter, defaultdict
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

OUT_DIR = ROOT / "outputs" / "audit_thematic_area_backend"

DOMAIN_HINTS = {
    "energia": ("energia", "solar", "eolica", "hidrogenio", "bateria"),
    "saude": ("saude", "medicina", "hospital", "sus", "vacina"),
    "agronegocio": ("agro", "agricultura", "pecuaria", "embrapa"),
    "defesa_seguranca": ("defesa", "militar", "nato", "darpa", "marinha"),
    "aeroespacial": ("satelite", "espaco", "aeroespacial", "nasa"),
    "nuclear": ("nuclear", "reator", "radiacao", "cnen"),
}


def _primary_current_label(labels: List[str]) -> str:
    if not labels:
        return "(vazio)"
    return labels[0]


def _titulo_sugere_outra_area(titulo: str) -> str | None:
    t = (titulo or "").lower()
    for domain, hints in DOMAIN_HINTS.items():
        if any(h in t for h in hints):
            if domain != "tecnologia_inovacao":
                return domain
    return None


def run_audit(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    area_dist: Counter = Counter()
    fonte_tech: Counter = Counter()
    examples_by_area: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    suspicious: List[Dict[str, Any]] = []
    tech_samples: List[Dict[str, Any]] = []

    for rec in records:
        labels = extract_current_area_labels(rec)
        primary = _primary_current_label(labels)
        area_dist[primary] += 1

        fonte = str(rec.get("fonte_recurso") or rec.get("fonte") or "—")[:80]
        if is_technology_innovation_label(primary) or any(is_technology_innovation_label(x) for x in labels):
            fonte_tech[fonte] += 1

        if len(examples_by_area[primary]) < 3:
            examples_by_area[primary].append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:100],
                    "area": labels,
                    "fonte": fonte,
                }
            )

        if is_technology_innovation_label(primary) and len(tech_samples) < 40:
            tech_samples.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:120],
                    "fonte": fonte,
                    "area": labels,
                    "setor": rec.get("setor"),
                    "categoria": rec.get("categoria"),
                    "extras_keys": list((rec.get("extras") or {}).keys())[:15]
                    if isinstance(rec.get("extras"), dict)
                    else [],
                }
            )

        hinted = _titulo_sugere_outra_area(rec.get("titulo") or "")
        if is_technology_innovation_label(primary) and hinted:
            new_cls = classify_thematic_area(rec)
            if new_cls.get("area_tematica_normalizada") != "tecnologia_inovacao":
                suspicious.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:100],
                        "area_atual": labels,
                        "titulo_sugere": hinted,
                        "classificador_novo": new_cls.get("area_tematica_label"),
                        "confidence": new_cls.get("area_tematica_confidence"),
                        "fonte": fonte,
                    }
                )

    return {
        "total": len(records),
        "area_distribution": dict(area_dist.most_common(40)),
        "technology_innovation_count": sum(
            1
            for k in area_dist
            if is_technology_innovation_label(k)
            for _ in range(area_dist[k])
        ),
        "top_fontes_technology_innovation": fonte_tech.most_common(25),
        "examples_by_area": dict(examples_by_area),
        "technology_innovation_samples": tech_samples[:25],
        "suspicious_count": len(suspicious),
        "suspicious_area_assignments": suspicious[:200],
    }


def build_summary(report: Dict[str, Any]) -> str:
    t = report["total"]
    lines = [
        "# Auditoria de área temática — Backend 5",
        "",
        f"**Registros:** {t}",
        "",
        "## Distribuição de área atual (campo `area` / extras)",
        "",
    ]
    for area, cnt in sorted(report["area_distribution"].items(), key=lambda x: -x[1])[:20]:
        lines.append(f"- **{area}**: {cnt} ({100 * cnt / t:.1f}%)")
    lines.extend(
        [
            "",
            f"## Concentração em Tecnologia e Inovação: **{report['technology_innovation_count']}** ({100 * report['technology_innovation_count'] / t:.1f}%)",
            "",
            "### Top fontes que geram Tecnologia e Inovação",
            "",
        ]
    )
    for fonte, cnt in report["top_fontes_technology_innovation"][:15]:
        lines.append(f"- {fonte}: {cnt}")
    lines.extend(
        [
            "",
            f"### Atribuições suspeitas (título indica outra área): **{report['suspicious_count']}**",
            "",
            "Ver `suspicious_area_assignments.json` e `technology_innovation_samples.json`.",
            "",
            "**Nota:** o frontend também aplica fallback `Tecnologia e Inovação` em `classificationService.js` quando nenhuma keyword casa — isso infla o filtro mesmo com backend vazio.",
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
    write_json(OUT_DIR / "report.json", {k: v for k, v in report.items() if k not in ("examples_by_area", "suspicious_area_assignments", "technology_innovation_samples")})
    write_json(OUT_DIR / "examples_by_area.json", report["examples_by_area"])
    write_json(OUT_DIR / "suspicious_area_assignments.json", report["suspicious_area_assignments"])
    write_json(OUT_DIR / "technology_innovation_samples.json", report["technology_innovation_samples"])
    write_md(OUT_DIR / "summary.md", build_summary(report))
    print(f"[audit_thematic_area_backend] {report['total']} registros -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
