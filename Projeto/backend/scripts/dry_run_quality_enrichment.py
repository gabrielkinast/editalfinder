#!/usr/bin/env python3
"""
Dry-run Backend 9: ruído + validade + quality_score sem gravar no banco.

Uso:
  python scripts/dry_run_quality_enrichment.py --from-db --limit 5000
  python scripts/dry_run_quality_enrichment.py --from-db --limit 5000 --with-deadline-backfill
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from opportunity_enricher import ENRICHMENT_VERSION, enrich_opportunity_record  # noqa: E402

OUT_DIR = ROOT / "outputs" / "backend_9_quality_dry_run"


def _pct(n: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{100 * n / total:.1f}%"


def run_dry_run(
    records: List[Dict[str, Any]],
    *,
    with_deadline_backfill: bool = False,
) -> Dict[str, Any]:
    total = len(records)
    actionable = 0
    noise = 0
    nao_aplicavel = 0
    sem_prazo_acionavel = 0
    portal_util = 0
    sem_prazo_kind_c = Counter()
    backfill_status_c = Counter()
    validade_c = Counter()
    actionability_c = Counter()
    classification_bucket_c = Counter()
    quality_level_c = Counter()
    fonte_scores: Dict[str, List[int]] = defaultdict(list)
    fonte_noise: Counter = Counter()
    fonte_total: Counter = Counter()

    high_q: List[Dict[str, Any]] = []
    low_q: List[Dict[str, Any]] = []
    noise_review: List[Dict[str, Any]] = []
    actionable_no_dl: List[Dict[str, Any]] = []
    not_actionable: List[Dict[str, Any]] = []

    for rec in records:
        enr = enrich_opportunity_record(rec, with_deadline_backfill=with_deadline_backfill)
        fonte = str(enr.get("fonte_normalizada") or rec.get("fonte_recurso") or "—")[:80]
        fonte_total[fonte] += 1
        qs = enr.get("quality_score") or 0
        fonte_scores[fonte].append(qs)

        vs = enr.get("validade_status") or "desconhecido"
        validade_c[vs] += 1
        actionability_c[enr.get("actionability_type") or "desconhecido"] += 1
        classification_bucket_c[enr.get("classification_bucket") or "desconhecido"] += 1
        quality_level_c[enr.get("quality_level") or "revisao"] += 1
        if enr.get("actionability_type") == "portal_util":
            portal_util += 1
        if enr.get("sem_prazo_kind"):
            sem_prazo_kind_c[enr.get("sem_prazo_kind")] += 1
        if enr.get("deadline_backfill_status"):
            backfill_status_c[enr.get("deadline_backfill_status")] += 1

        if enr.get("is_actionable_opportunity"):
            actionable += 1
            if vs == "sem_prazo" and len(actionable_no_dl) < 80:
                actionable_no_dl.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:100],
                        "fonte": fonte,
                        "quality_score": qs,
                    }
                )
        else:
            if len(not_actionable) < 60:
                not_actionable.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:80],
                        "noise_type": enr.get("noise_type"),
                        "validade_status": vs,
                    }
                )

        if enr.get("is_noise"):
            noise += 1
            fonte_noise[fonte] += 1
            if len(noise_review) < 80:
                noise_review.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:100],
                        "noise_type": enr.get("noise_type"),
                        "noise_score": enr.get("noise_score"),
                    }
                )
        if vs == "nao_aplicavel":
            nao_aplicavel += 1
        if enr.get("is_actionable_opportunity") and vs == "sem_prazo":
            sem_prazo_acionavel += 1

        if qs >= 75 and len(high_q) < 40:
            high_q.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:100],
                    "quality_score": qs,
                    "validade_status": vs,
                }
            )
        if (qs < 35 or enr.get("quality_level") == "revisao") and len(low_q) < 80:
            low_q.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:100],
                    "quality_score": qs,
                    "quality_level": enr.get("quality_level"),
                    "flags": enr.get("quality_flags"),
                }
            )

    ranking = []
    for fonte, scores in fonte_scores.items():
        if len(scores) < 3:
            continue
        avg = sum(scores) / len(scores)
        ranking.append(
            {
                "fonte": fonte,
                "count": len(scores),
                "avg_quality_score": round(avg, 1),
                "noise_count": fonte_noise[fonte],
                "noise_pct": round(100 * fonte_noise[fonte] / len(scores), 1),
            }
        )
    ranking.sort(key=lambda x: x["avg_quality_score"], reverse=True)
    worst_noise = sorted(ranking, key=lambda x: -x["noise_pct"])[:25]

    return {
        "enrichment_version": ENRICHMENT_VERSION,
        "with_deadline_backfill": with_deadline_backfill,
        "backend_calibration": "10.1e",
        "total": total,
        "actionable_count": actionable,
        "ruido_provavel_count": noise,
        "nao_aplicavel_count": nao_aplicavel,
        "portal_util_count": portal_util,
        "actionability_type_distribution": dict(actionability_c),
        "classification_bucket_distribution": dict(classification_bucket_c),
        "sem_prazo_among_actionable": sem_prazo_acionavel,
        "validity_distribution": dict(validade_c),
        "quality_level_distribution": dict(quality_level_c),
        "source_quality_ranking_best": ranking[:25],
        "source_quality_ranking_worst_noise": worst_noise,
        "high_quality_opportunities": high_q,
        "low_quality_review": low_q,
        "noise_review": noise_review,
        "actionable_without_deadline": actionable_no_dl,
        "not_actionable_records": not_actionable,
        "sem_prazo_kind_distribution": dict(sem_prazo_kind_c),
        "deadline_backfill_status_distribution": dict(backfill_status_c),
    }


def build_summary_md(r: Dict[str, Any]) -> str:
    t = r["total"]
    lines = [
        "# Dry-run qualidade Backend 9",
        "",
        f"**Versão:** {r['enrichment_version']} | **Total:** {t}",
        f"**Backfill:** {'sim' if r.get('with_deadline_backfill') else 'não'}",
        "",
        f"- Acionáveis: **{r['actionable_count']}** ({_pct(r['actionable_count'], t)})",
        f"- Ruído provável (is_noise): **{r['ruido_provavel_count']}** ({_pct(r['ruido_provavel_count'], t)})",
        f"- Portal útil: **{r.get('portal_util_count', 0)}**",
        f"- Não aplicável: **{r['nao_aplicavel_count']}** ({_pct(r['nao_aplicavel_count'], t)})",
        f"- Acionáveis com `sem_prazo`: **{r['sem_prazo_among_actionable']}**",
        "",
        "## validade_status",
        "",
    ]
    for k, v in sorted(r["validity_distribution"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## quality_level", ""])
    for k, v in r["quality_level_distribution"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("Ver JSONs de ranking, ruído e revisão.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run Backend 9 quality")
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--source", type=str, default=None, help="Filtrar por fonte (ex.: grants_gov)")
    ap.add_argument("--output", type=Path, default=OUT_DIR)
    ap.add_argument(
        "--with-deadline-backfill",
        action="store_true",
        help="Aplica deadline_backfill em memória antes do enricher",
    )
    args = ap.parse_args()

    records = load_records(
        from_db=args.from_db,
        input_path=args.input,
        limit=args.limit,
        source=args.source,
    )
    out = args.output
    if args.with_deadline_backfill:
        out = ROOT / "outputs" / "backend_9_quality_dry_run_with_backfill"
    if not records:
        write_json(out / "report.json", {"total": 0, "error": "no_data"})
        return 1

    report = run_dry_run(records, with_deadline_backfill=args.with_deadline_backfill)
    write_json(out / "report.json", report)
    write_json(out / "high_quality_opportunities.json", report["high_quality_opportunities"])
    write_json(out / "low_quality_review.json", report["low_quality_review"])
    write_json(out / "noise_review.json", report["noise_review"])
    write_json(out / "actionable_without_deadline.json", report["actionable_without_deadline"])
    write_json(out / "not_actionable_records.json", report["not_actionable_records"])
    write_json(out / "source_quality_ranking.json", {
        "best": report["source_quality_ranking_best"],
        "worst_noise": report["source_quality_ranking_worst_noise"],
    })
    write_md(out / "summary.md", build_summary_md(report))
    print(f"[dry_run_quality_enrichment] {report['total']} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
