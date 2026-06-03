#!/usr/bin/env python3
"""
Auditoria de prazos na base edital (Backend 1) — somente leitura.

Uso:
  python scripts/audit_deadlines_backend.py --from-db --limit 5000
  python scripts/audit_deadlines_backend.py --input exports/editais_sample.json
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402

CORE = ROOT / "CORE"
sys.path.insert(0, str(CORE))

from deadline_normalizer import normalize_deadline  # noqa: E402

OUT_DIR = ROOT / "outputs" / "audit_deadlines_backend"


def _pct(n: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{100 * n / total:.1f}%"


def run_audit(records: list) -> dict:
    total = len(records)
    status_c = Counter()
    conf_c = Counter()
    field_c = Counter()
    fonte_problems: Counter = Counter()
    examples_by_fonte: dict = defaultdict(list)
    text_extracted = 0
    structured = 0
    raw_only = 0
    none_count = 0

    for rec in records:
        dl = normalize_deadline(rec)
        st = dl["prazo_status"]
        status_c[st] += 1
        conf_c[dl["prazo_confidence"]] += 1
        if dl["prazo_source_field"]:
            field_c[dl["prazo_source_field"]] += 1
        fonte = str(rec.get("fonte_recurso") or rec.get("fonte") or "—")[:80]
        if st in ("sem_prazo", "prazo_invalido"):
            fonte_problems[fonte] += 1
            if len(examples_by_fonte[fonte]) < 3:
                examples_by_fonte[fonte].append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:100],
                        "prazo_status": st,
                        "prazo_raw": dl.get("prazo_raw"),
                        "prazo_source_field": dl.get("prazo_source_field"),
                        "notes": dl.get("prazo_notes"),
                    }
                )
        if dl["prazo_data"]:
            structured += 1
        elif dl["prazo_raw"]:
            raw_only += 1
        else:
            none_count += 1
        if "extraido_de_texto" in (dl.get("prazo_notes") or []):
            text_extracted += 1

    return {
        "total": total,
        "status": dict(status_c),
        "confidence": dict(conf_c),
        "top_source_fields": field_c.most_common(20),
        "structured_count": structured,
        "raw_only_count": raw_only,
        "none_count": none_count,
        "text_extracted_count": text_extracted,
        "top_fontes_sem_prazo": fonte_problems.most_common(25),
        "examples_by_fonte": dict(examples_by_fonte),
    }


def build_summary_md(report: dict) -> str:
    t = report["total"]
    lines = [
        "# Auditoria de prazos — Backend 1",
        "",
        f"**Total analisado:** {t}",
        "",
        "## Situação de prazo (prazo_status)",
        "",
    ]
    for k, v in sorted(report["status"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v} ({_pct(v, t)})")
    lines.extend(["", "## Confiança", ""])
    for k, v in report["confidence"].items():
        lines.append(f"- `{k}`: {v} ({_pct(v, t)})")
    lines.extend(
        [
            "",
            "## Contagens",
            f"- Com `prazo_data` estruturado: **{report['structured_count']}** ({_pct(report['structured_count'], t)})",
            f"- Só texto bruto / inválido: **{report['raw_only_count']}**",
            f"- Sem prazo: **{report['none_count']}**",
            f"- Extraído de título/descrição: **{report['text_extracted_count']}**",
            "",
            "## Top campos fonte de prazo",
            "",
        ]
    )
    for field, cnt in report["top_source_fields"]:
        lines.append(f"- `{field}`: {cnt}")
    lines.extend(["", "## Top fontes com problema de prazo", ""])
    for fonte, cnt in report["top_fontes_sem_prazo"]:
        lines.append(f"- {fonte}: {cnt}")
    lines.append("")
    lines.append("Ver `report.json` e `examples_by_fonte.json` para amostras.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria de prazos (Backend 1)")
    ap.add_argument("--from-db", action="store_true", help="Ler public.edital via Supabase")
    ap.add_argument("--input", type=Path, help="JSON array de editais exportados")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    records = load_records(from_db=args.from_db, input_path=args.input, limit=args.limit)
    if not records:
        print(
            "Nenhum registro. Use --from-db (com .env.staging) ou --input arquivo.json",
            file=sys.stderr,
        )
        report = {
            "total": 0,
            "error": "no_data",
            "hint": "exporte amostra da tabela edital ou configure Supabase",
        }
        write_json(OUT_DIR / "report.json", report)
        write_md(OUT_DIR / "summary.md", "# Sem dados\n\nConfigure --from-db ou --input.")
        return 1

    report = run_audit(records)
    write_json(OUT_DIR / "report.json", report)
    write_json(OUT_DIR / "examples_by_fonte.json", report["examples_by_fonte"])
    write_md(OUT_DIR / "summary.md", build_summary_md(report))
    print(f"[audit_deadlines_backend] {report['total']} registros -> {OUT_DIR}")
    if __import__("os").environ.get("DEV") or True:
        print("[editais] deadline_filter_result", {"total": report["total"], "status": report["status"]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
