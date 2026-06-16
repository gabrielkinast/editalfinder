#!/usr/bin/env python3
"""
Auditoria de ruído e acionabilidade (Backend 9–10) — somente leitura.

Uso:
  python scripts/audit_noise_backend.py --from-db --limit 5000
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from noise_classifier import classify_noise  # noqa: E402

OUT_DIR = ROOT / "outputs" / "audit_noise_backend"


def _pct(n: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{100 * n / total:.1f}%"


def _titulo_key(t: str) -> str:
    t = unicodedata.normalize("NFKD", (t or "").lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", t).strip()[:80]


def _find_near_duplicates(records: List[Dict[str, Any]], max_pairs: int = 50) -> List[Dict[str, Any]]:
    buckets: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for rec in records:
        key = (_titulo_key(rec.get("titulo") or ""), str(rec.get("fonte_recurso") or rec.get("fonte") or "")[:60])
        if not key[0] or len(key[0]) < 12:
            continue
        buckets[key].append(rec)
    pairs: List[Dict[str, Any]] = []
    for key, group in buckets.items():
        if len(group) < 2:
            continue
        for i in range(min(len(group) - 1, 2)):
            a, b = group[i], group[i + 1]
            pairs.append(
                {
                    "titulo_key": key[0],
                    "fonte": key[1],
                    "ids": [a.get("id_edital"), b.get("id_edital")],
                }
            )
            if len(pairs) >= max_pairs:
                return pairs
    return pairs


def run_audit(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    classification_bucket_c = Counter()
    actionability_type_c = Counter()
    noise_by_type_c = Counter()  # só is_noise=True
    non_actionable_by_type_c = Counter()

    fonte_noise: Counter = Counter()
    fonte_total: Counter = Counter()
    fonte_actionability: Dict[str, Counter] = defaultdict(Counter)

    actionable = 0
    noise_count = 0
    ambiguous: List[Dict[str, Any]] = []
    noise_examples: List[Dict[str, Any]] = []
    actionable_examples: List[Dict[str, Any]] = []
    portal_util_examples: List[Dict[str, Any]] = []
    portal_generico_examples: List[Dict[str, Any]] = []
    false_positive_noise: List[Dict[str, Any]] = []
    false_negative_noise: List[Dict[str, Any]] = []

    for rec in records:
        nz = classify_noise(rec)
        fonte = str(rec.get("fonte_recurso") or rec.get("fonte") or "—")[:80]
        fonte_total[fonte] += 1

        at = nz.get("actionability_type") or "desconhecido"
        bucket = nz.get("classification_bucket") or "desconhecido"
        actionability_type_c[at] += 1
        classification_bucket_c[bucket] += 1
        fonte_actionability[fonte][at] += 1

        if at not in ("oportunidade_principal", "oportunidade_sem_prazo"):
            non_actionable_by_type_c[at] += 1

        if nz.get("is_noise"):
            noise_count += 1
            fonte_noise[fonte] += 1
            nt = nz.get("noise_type")
            if nt:
                noise_by_type_c[nt] += 1
            if len(noise_examples) < 60:
                noise_examples.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:100],
                        "fonte": fonte,
                        "noise_type": nt,
                        "actionability_type": at,
                    }
                )

        if nz.get("is_actionable_opportunity"):
            actionable += 1
            if len(actionable_examples) < 40:
                actionable_examples.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:100],
                        "fonte": fonte,
                        "actionability_type": at,
                    }
                )

        if at == "portal_util" and len(portal_util_examples) < 40:
            portal_util_examples.append(
                {"id_edital": rec.get("id_edital"), "titulo": (rec.get("titulo") or "")[:100], "fonte": fonte}
            )
        if at == "portal_generico" and len(portal_generico_examples) < 40:
            portal_generico_examples.append(
                {"id_edital": rec.get("id_edital"), "titulo": (rec.get("titulo") or "")[:100], "fonte": fonte}
            )

        if "possivel_falso_positivo_resultado" in (nz.get("review_reasons") or []) and len(false_positive_noise) < 50:
            false_positive_noise.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:100],
                    "actionability_type": at,
                }
            )
        if "possivel_falso_negativo_resultado" in (nz.get("review_reasons") or []) and len(false_negative_noise) < 50:
            false_negative_noise.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:100],
                    "actionability_type": at,
                }
            )

        if nz.get("confidence") == "baixa" and len(ambiguous) < 80:
            ambiguous.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:100],
                    "actionability_type": at,
                    "classification_bucket": bucket,
                    "review_reasons": nz.get("review_reasons"),
                }
            )

    dupes = _find_near_duplicates(records)
    noise_by_source = {
        f: {
            "total": fonte_total[f],
            "ruido_provavel": fonte_noise[f],
            "pct_ruido": round(100 * fonte_noise[f] / fonte_total[f], 1),
        }
        for f in fonte_total
        if fonte_total[f] >= 5
    }
    source_breakdown = {
        f: dict(cnt) for f, cnt in list(fonte_actionability.items())[:50]
    }

    return {
        "backend_version": "10.2a",
        "total": total,
        "actionable_count": actionable,
        "ruido_provavel_count": noise_count,
        "ruido_provavel_pct": round(100 * noise_count / total, 2) if total else 0,
        "classification_by_actionability_type": dict(classification_bucket_c),
        "actionability_type_distribution": dict(actionability_type_c),
        "noise_by_type": dict(noise_by_type_c),
        "non_actionable_by_type": dict(non_actionable_by_type_c),
        "noise_by_source": dict(sorted(noise_by_source.items(), key=lambda x: -x[1]["ruido_provavel"])[:40]),
        "source_actionability_breakdown": source_breakdown,
        "near_duplicate_pairs": len(dupes),
        "noise_examples": noise_examples,
        "actionable_examples": actionable_examples,
        "portal_util_examples": portal_util_examples,
        "portal_generico_examples": portal_generico_examples,
        "likely_false_positive_noise": false_positive_noise,
        "likely_false_negative_noise": false_negative_noise,
        "ambiguous_review": ambiguous,
        "near_duplicates_sample": dupes,
        "metrics_legend": {
            "ruido_provavel_count": "Registros com is_noise=true (subconjunto de ruído real)",
            "noise_by_type": "Contagem apenas onde is_noise=true",
            "non_actionable_by_type": "Todos os registros não oportunidade_principal/sem_prazo",
            "classification_by_actionability_type": "Buckets agregados para dashboard",
        },
    }


def build_summary_md(report: Dict[str, Any]) -> str:
    t = report["total"]
    lines = [
        "# Auditoria de ruído e acionabilidade — Backend 10.2A",
        "",
        f"**Total analisado:** {t}",
        "",
        "## Métricas principais (não confundir)",
        "",
        f"- **Oportunidades acionáveis** (`is_actionable_opportunity`): **{report['actionable_count']}** ({_pct(report['actionable_count'], t)})",
        f"- **Ruído provável** (`is_noise=true`): **{report['ruido_provavel_count']}** ({_pct(report['ruido_provavel_count'], t)})",
        "",
        "> `non_actionable_by_type` inclui portal, notícia, sem oportunidade etc. — **não** é o mesmo que ruído provável.",
        "",
        "## classification_by_actionability_type (buckets)",
        "",
    ]
    for k, v in sorted(report["classification_by_actionability_type"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v} ({_pct(v, t)})")
    lines.extend(["", "## actionability_type_distribution (detalhe)", ""])
    for k, v in sorted(report["actionability_type_distribution"].items(), key=lambda x: -x[1])[:20]:
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            "## noise_by_type (somente is_noise=true)",
            "",
        ]
    )
    for k, v in sorted(report["noise_by_type"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## non_actionable_by_type (não principal)", ""])
    for k, v in sorted(report["non_actionable_by_type"].items(), key=lambda x: -x[1])[:15]:
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Top fontes — ruído provável (mín. 5 registros)", ""])
    for fonte, info in list(report["noise_by_source"].items())[:15]:
        lines.append(f"- {fonte}: {info['ruido_provavel']}/{info['total']} ({info['pct_ruido']}%)")
    lines.append("")
    lines.append("Ver `portal_util_examples.json`, `likely_false_positive_noise.json`, `source_actionability_breakdown.json`.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria ruído/acionabilidade Backend 10")
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--source", type=str, default=None, help="Filtrar por fonte (ex.: grants_gov)")
    args = ap.parse_args()

    records = load_records(
        from_db=args.from_db,
        input_path=args.input,
        limit=args.limit,
        source=args.source,
    )
    if not records:
        write_json(OUT_DIR / "report.json", {"total": 0, "error": "no_data"})
        write_md(OUT_DIR / "summary.md", "# Sem dados")
        return 1

    report = run_audit(records)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "noise_examples.json", report["noise_examples"])
    write_json(OUT_DIR / "actionable_examples.json", report["actionable_examples"])
    write_json(OUT_DIR / "ambiguous_review.json", report["ambiguous_review"])
    write_json(OUT_DIR / "noise_by_source.json", report["noise_by_source"])
    write_json(OUT_DIR / "noise_by_kind.json", report["noise_by_type"])
    write_json(OUT_DIR / "classification_by_actionability_type.json", report["classification_by_actionability_type"])
    write_json(OUT_DIR / "actionability_type_distribution.json", report["actionability_type_distribution"])
    write_json(OUT_DIR / "non_actionable_by_type.json", report["non_actionable_by_type"])
    write_json(OUT_DIR / "portal_util_examples.json", report["portal_util_examples"])
    write_json(OUT_DIR / "portal_generico_examples.json", report["portal_generico_examples"])
    write_json(OUT_DIR / "likely_false_positive_noise.json", report["likely_false_positive_noise"])
    write_json(OUT_DIR / "likely_false_negative_noise.json", report["likely_false_negative_noise"])
    write_json(OUT_DIR / "source_actionability_breakdown.json", report["source_actionability_breakdown"])
    write_md(OUT_DIR / "summary.md", build_summary_md(report))
    print(f"[audit_noise_backend] {report['total']} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
