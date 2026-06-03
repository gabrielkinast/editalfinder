#!/usr/bin/env python3
"""
Compara enriquecimento shadow vs tabela principal — somente leitura.

Uso:
  python scripts/compare_backend_enrichment_shadow.py --from-db --limit 5000
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from _backend_shadow_common import (  # noqa: E402
    SHADOW_PAYLOAD_KEYS,
    build_shadow_payload,
    field_coverage,
    load_shadow_rows_from_db,
)

OUT_DIR = ROOT / "outputs" / "backend_7_shadow_comparison"


def _dist(values: List[Any]) -> Dict[str, int]:
    c: Counter = Counter(str(v) if v is not None else "null" for v in values)
    return dict(c.most_common(40))


def compare(records: List[Dict[str, Any]], shadow_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    shadow_by_id = {r["id_edital"]: r for r in shadow_rows if r.get("id_edital") is not None}
    matched: List[Dict[str, Any]] = []
    missing_shadow: List[Any] = []

    for rec in records:
        rid = rec.get("id_edital")
        if rid in shadow_by_id:
            matched.append(shadow_by_id[rid])
        else:
            missing_shadow.append(rid)
            matched.append(build_shadow_payload(rec))

    used_fallback = len(shadow_rows) == 0 or len(missing_shadow) > 0

    low_conf = sum(
        1
        for s in matched
        if s.get("prazo_confidence") == "baixa"
        or s.get("kind_confidence") == "baixa"
        or s.get("area_tematica_confidence") == "baixa"
        or s.get("modalidade_confidence") == "baixa"
    )
    kind_non_edital = sum(
        1 for s in matched if s.get("tipo_registro") in ("noticia", "pesquisa", "concurso")
    )
    sem_area = sum(1 for s in matched if s.get("area_tematica_normalizada") == "sem_classificacao")

    risky: List[Dict[str, Any]] = []
    for rec, shadow in zip(records, matched):
        if len(risky) >= 200:
            break
        flags = shadow.get("qualidade_flags") or []
        if "revisao_humana" in flags or shadow.get("area_tematica_confidence") == "baixa":
            risky.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:90],
                    "tipo_registro": shadow.get("tipo_registro"),
                    "area_tematica_label": shadow.get("area_tematica_label"),
                    "qualidade_flags": flags,
                }
            )

    cov = field_coverage(matched)
    prazo_with_date = sum(1 for s in matched if s.get("prazo_data"))

    return {
        "total_main": len(records),
        "shadow_rows_in_db": len(shadow_rows),
        "matched_shadow": len(records) - len(missing_shadow),
        "missing_shadow_ids_count": len(missing_shadow),
        "used_computed_fallback": used_fallback,
        "field_coverage": cov,
        "deadline_distribution": _dist([s.get("prazo_status") for s in matched]),
        "deadline_with_structured_date": prazo_with_date,
        "kind_distribution": _dist([s.get("tipo_registro") for s in matched]),
        "modality_distribution": _dist([s.get("modalidade_normalizada") for s in matched]),
        "area_distribution": _dist([s.get("area_tematica_normalizada") for s in matched]),
        "low_confidence_any_field": low_conf,
        "kind_non_edital_count": kind_non_edital,
        "sem_classificacao_count": sem_area,
        "risky_review": risky,
    }


def build_summary(r: Dict[str, Any]) -> str:
    t = r["total_main"]
    lines = [
        "# Comparação shadow vs principal — Backend 7",
        "",
        f"**Registros na tabela principal:** {t}",
        f"**Linhas na tabela sombra (DB):** {r['shadow_rows_in_db']}",
        f"**Match por id_edital:** {r['matched_shadow']}",
        f"**Sem linha shadow:** {r['missing_shadow_ids_count']}",
        "",
    ]
    if r.get("used_computed_fallback"):
        lines.append(
            "_Nota: tabela sombra vazia ou indisponível — métricas calculadas a partir do enricher (fallback)._"
        )
        lines.append("")
    lines.extend(
        [
            "## Cobertura",
            f"- Prazo estruturado (`prazo_data`): **{r.get('deadline_with_structured_date', 0)}**",
            f"- Baixa confiança (qualquer campo): **{r.get('low_confidence_any_field', 0)}**",
            f"- tipo_registro ≠ edital (notícia/pesquisa/concurso): **{r.get('kind_non_edital_count', 0)}**",
            f"- area sem_classificacao: **{r.get('sem_classificacao_count', 0)}**",
            "",
            "## Distribuição — prazo_status (top)",
            "",
        ]
    )
    for k, v in list(r.get("deadline_distribution", {}).items())[:8]:
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Distribuição — tipo_registro", ""])
    for k, v in list(r.get("kind_distribution", {}).items())[:8]:
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Distribuição — area_tematica_normalizada (top)", ""])
    for k, v in list(r.get("area_distribution", {}).items())[:10]:
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            "Artefatos: `field_coverage.json`, `deadline_distribution.json`, `kind_distribution.json`,",
            "`modality_distribution.json`, `area_distribution.json`, `risky_review.json`.",
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

    shadow_rows: List[Dict[str, Any]] = []
    if args.from_db:
        try:
            ids = [r.get("id_edital") for r in records if r.get("id_edital") is not None]
            shadow_rows = load_shadow_rows_from_db(id_editais=ids)
        except Exception as exc:
            print(f"[compare] shadow table unavailable: {exc}")

    report = compare(records, shadow_rows)
    write_md(OUT_DIR / "summary.md", build_summary(report))
    write_json(OUT_DIR / "field_coverage.json", report["field_coverage"])
    write_json(OUT_DIR / "deadline_distribution.json", report["deadline_distribution"])
    write_json(OUT_DIR / "kind_distribution.json", report["kind_distribution"])
    write_json(OUT_DIR / "modality_distribution.json", report["modality_distribution"])
    write_json(OUT_DIR / "area_distribution.json", report["area_distribution"])
    write_json(OUT_DIR / "risky_review.json", report["risky_review"])
    write_json(
        OUT_DIR / "report.json",
        {k: v for k, v in report.items() if k not in ("risky_review",)},
    )
    print(f"[compare_shadow] {report['total_main']} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
