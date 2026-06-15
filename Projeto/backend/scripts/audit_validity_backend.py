#!/usr/bin/env python3
"""
Auditoria de validade/prazo (Backend 9) — somente leitura.

Uso:
  python scripts/audit_validity_backend.py --from-db --limit 5000
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from deadline_normalizer import normalize_deadline  # noqa: E402
from noise_classifier import classify_noise  # noqa: E402
from validity_resolver import resolve_validity  # noqa: E402

OUT_DIR = ROOT / "outputs" / "audit_validity_backend"


def _pct(n: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{100 * n / total:.1f}%"


def run_audit(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    validade_c = Counter()
    fonte_sem_validade: Counter = Counter()
    fonte_total: Counter = Counter()
    actionable = 0
    without_validity_useful = 0  # sem_prazo + desconhecido entre acionáveis
    no_deadline_actionable: List[Dict[str, Any]] = []
    not_applicable: List[Dict[str, Any]] = []
    invalid_examples: List[Dict[str, Any]] = []
    more_than_400_bucket: List[Dict[str, Any]] = []

    for rec in records:
        nz = classify_noise(rec)
        dl = normalize_deadline(rec)
        val = resolve_validity(rec, noise=nz, deadline=dl)
        vs = val.get("validade_status") or "desconhecido"
        validade_c[vs] += 1
        fonte = str(rec.get("fonte_recurso") or rec.get("fonte") or "—")[:80]
        fonte_total[fonte] += 1

        if nz.get("is_actionable_opportunity"):
            actionable += 1
            if vs in ("sem_prazo", "desconhecido", "prazo_invalido"):
                without_validity_useful += 1
                fonte_sem_validade[fonte] += 1
                if len(no_deadline_actionable) < 100:
                    no_deadline_actionable.append(
                        {
                            "id_edital": rec.get("id_edital"),
                            "titulo": (rec.get("titulo") or "")[:100],
                            "fonte": fonte,
                            "validade_status": vs,
                            "prazo_status": dl.get("prazo_status"),
                        }
                    )

        if vs == "nao_aplicavel" and len(not_applicable) < 60:
            not_applicable.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:100],
                    "noise_type": nz.get("noise_type"),
                }
            )
        if vs == "prazo_invalido" and len(invalid_examples) < 40:
            invalid_examples.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:100],
                    "validade_raw": val.get("validade_raw"),
                }
            )

    # Registros sem validade útil no sentido frontend (sem data e não nao_aplicavel)
    for rec in records:
        nz = classify_noise(rec)
        val = resolve_validity(rec, noise=nz)
        vs = val.get("validade_status")
        if vs in ("sem_prazo", "desconhecido") and not val.get("validade_data"):
            if len(more_than_400_bucket) < 500:
                more_than_400_bucket.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:80],
                        "validade_status": vs,
                        "is_actionable": nz.get("is_actionable_opportunity"),
                        "noise_type": nz.get("noise_type"),
                    }
                )

    by_source = {
        f: {
            "total": fonte_total[f],
            "sem_validade_util": fonte_sem_validade[f],
        }
        for f in fonte_total
        if fonte_sem_validade[f] > 0
    }
    by_source = dict(sorted(by_source.items(), key=lambda x: -x[1]["sem_validade_util"])[:35])

    return {
        "total": total,
        "validity_distribution": dict(validade_c),
        "actionable_count": actionable,
        "actionable_without_useful_validity": without_validity_useful,
        "count_sem_prazo_or_unknown": validade_c.get("sem_prazo", 0) + validade_c.get("desconhecido", 0),
        "count_nao_aplicavel": validade_c.get("nao_aplicavel", 0),
        "count_vencendo_7": validade_c.get("vencendo_7", 0),
        "count_vencendo_30": validade_c.get("vencendo_30", 0),
        "count_encerrado": validade_c.get("encerrado", 0),
        "count_aberto": validade_c.get("aberto", 0),
        "records_without_useful_validity_sample_count": len(more_than_400_bucket),
        "more_than_400_without_validity": more_than_400_bucket[:450],
        "no_deadline_but_actionable": no_deadline_actionable,
        "not_applicable_examples": not_applicable,
        "invalid_deadline_examples": invalid_examples,
        "by_source": by_source,
        "audit_date": date.today().isoformat(),
    }


def build_summary_md(report: Dict[str, Any]) -> str:
    t = report["total"]
    lines = [
        "# Auditoria de validade — Backend 9",
        "",
        f"**Total:** {t} | **Data:** {report.get('audit_date')}",
        "",
        "## Distribuição validade_status",
        "",
    ]
    for k, v in sorted(report["validity_distribution"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v} ({_pct(v, t)})")
    lines.extend(
        [
            "",
            "## Respostas-chave",
            "",
            f"- Oportunidades acionáveis: **{report['actionable_count']}**",
            f"- Acionáveis sem validade útil (sem_prazo/desconhecido/inválido): **{report['actionable_without_useful_validity']}**",
            f"- `nao_aplicavel` (notícia/portal/auxiliar): **{report['count_nao_aplicavel']}** — explica parte dos \"sem prazo\"",
            f"- `sem_prazo` real: **{report['validity_distribution'].get('sem_prazo', 0)}**",
            f"- Vencendo 7d / 30d: **{report['count_vencendo_7']}** / **{report['count_vencendo_30']}**",
            f"- Amostra registros sem validade útil: **{report['records_without_useful_validity_sample_count']}** (ver JSON)",
            "",
            "## Top fontes — acionáveis sem validade útil",
            "",
        ]
    )
    for fonte, info in list(report["by_source"].items())[:15]:
        lines.append(f"- {fonte}: {info['sem_validade_util']}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria de validade (Backend 9)")
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
    write_json(OUT_DIR / "validity_distribution.json", report["validity_distribution"])
    write_json(OUT_DIR / "more_than_400_without_validity.json", report["more_than_400_without_validity"])
    write_json(OUT_DIR / "no_deadline_but_actionable.json", report["no_deadline_but_actionable"])
    write_json(OUT_DIR / "not_applicable_examples.json", report["not_applicable_examples"])
    write_json(OUT_DIR / "invalid_deadline_examples.json", report["invalid_deadline_examples"])
    write_json(OUT_DIR / "by_source.json", report["by_source"])
    write_md(OUT_DIR / "summary.md", build_summary_md(report))
    print(f"[audit_validity_backend] {report['total']} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
