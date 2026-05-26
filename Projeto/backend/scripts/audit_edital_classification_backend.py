#!/usr/bin/env python3
"""
Auditoria de classificação (modalidade, escopo, tipo de registro) — Backend 1.

Também gera candidatos para revisão kind em outputs/audit_kind_classification_review/

Uso:
  python scripts/audit_edital_classification_backend.py --from-db --limit 3000
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from opportunity_classifier import (  # noqa: E402
    classify_geo_scope,
    classify_opportunity_modality,
    classify_record_kind,
    classify_source_normalized,
)

OUT_CLASS = ROOT / "outputs" / "audit_edital_classification_backend"
OUT_KIND = ROOT / "outputs" / "audit_kind_classification_review"


def run_audit(records: list) -> dict:
    kind_c = Counter()
    mod_c = Counter()
    scope_c = Counter()
    fonte_c = Counter()
    tipo_op_c = Counter()
    area_dup = Counter()
    review_candidates = []

    for rec in records:
        kind = classify_record_kind(rec)
        mod = classify_opportunity_modality(rec)
        geo = classify_geo_scope(rec)
        src = classify_source_normalized(rec)

        kind_c[kind["kind"]] += 1
        mod_c[mod["modalidade_normalizada"]] += 1
        scope_c[geo["scope"]] += 1
        fonte_c[src["fonte_normalizada"][:60]] += 1
        tipo_op = str(rec.get("tipo_oportunidade") or "")[:40]
        if tipo_op:
            tipo_op_c[tipo_op] += 1
        area = str(rec.get("area") or "")[:50]
        if area and "tecnologia" in area.lower()[:30]:
            area_dup[area] += 1

        # Candidatos a revisão: kind vs expectativa heurística
        titulo = (rec.get("titulo") or "").lower()
        suspicious = False
        reason = []
        if kind["kind"] == "edital" and any(
            x in titulo for x in ("notícia", "news:", "comunicado", "publicado em")
        ):
            suspicious = True
            reason.append("titulo_parece_noticia")
        if kind["kind"] == "noticia" and any(
            x in titulo for x in ("chamada pública", "edital n", "call for proposals")
        ):
            suspicious = True
            reason.append("titulo_parece_edital")
        if kind["kind"] == "edital" and mod["modalidade_normalizada"] == "noticia_institucional":
            suspicious = True
            reason.append("modalidade_noticia_em_edital")
        if kind["kind"] == "edital" and mod["modalidade_normalizada"] == "pesquisa_publicacao":
            suspicious = True
            reason.append("modalidade_pesquisa_em_edital")

        if suspicious and len(review_candidates) < 500:
            review_candidates.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:120],
                    "fonte_recurso": rec.get("fonte_recurso"),
                    "kind": kind["kind"],
                    "modalidade": mod["modalidade_normalizada"],
                    "scope": geo["scope"],
                    "reasons": reason,
                    "tipo_oportunidade": rec.get("tipo_oportunidade"),
                    "area": (rec.get("area") or "")[:80],
                }
            )

    return {
        "total": len(records),
        "kind": dict(kind_c),
        "modalidade_normalizada": dict(mod_c),
        "escopo_geografico": dict(scope_c),
        "top_fontes_normalizadas": fonte_c.most_common(30),
        "top_tipo_oportunidade_raw": tipo_op_c.most_common(20),
        "area_tecnologia_samples": area_dup.most_common(15),
        "review_candidates_count": len(review_candidates),
        "review_candidates": review_candidates,
    }


def build_summary_md(report: dict) -> str:
    t = report["total"]
    lines = [
        "# Auditoria de classificação — Backend 1",
        "",
        f"**Total:** {t}",
        "",
        "## Tipo de registro (kind)",
        "",
    ]
    for k, v in sorted(report["kind"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Modalidade normalizada", ""])
    for k, v in sorted(report["modalidade_normalizada"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Escopo geográfico", ""])
    for k, v in report["escopo_geografico"].items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Top fontes normalizadas", ""])
    for fonte, cnt in report["top_fontes_normalizadas"][:15]:
        lines.append(f"- {fonte}: {cnt}")
    lines.extend(
        [
            "",
            f"**Candidatos à revisão (kind):** {report['review_candidates_count']}",
            "",
            "Ver `review_candidates.json` em `outputs/audit_kind_classification_review/`.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    records = load_records(from_db=args.from_db, input_path=args.input, limit=args.limit)
    if not records:
        write_md(OUT_CLASS / "summary.md", "# Sem dados\n")
        return 1

    report = run_audit(records)
    write_json(OUT_CLASS / "report.json", report)
    write_md(OUT_CLASS / "summary.md", build_summary_md(report))
    write_json(OUT_KIND / "review_candidates.json", report["review_candidates"])
    write_md(
        OUT_KIND / "summary.md",
        f"# Revisão kind\n\n{report['review_candidates_count']} candidatos.\n",
    )
    print(f"[audit_edital_classification_backend] -> {OUT_CLASS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
