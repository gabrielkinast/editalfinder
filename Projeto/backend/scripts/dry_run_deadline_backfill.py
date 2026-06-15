#!/usr/bin/env python3
"""
Dry-run de backfill de prazo por fonte (Backend 10.1E) — somente leitura.

Uso:
  python scripts/dry_run_deadline_backfill.py --from-db --limit 5000
  python scripts/dry_run_deadline_backfill.py --source grants_gov --from-db --limit 500
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from deadline_backfill import (  # noqa: E402
    BACKFILL_SOURCE,
    apply_deadline_backfill_in_memory,
    extract_source_deadline_fields,
    normalize_backfill_source,
)

OUT_DIR = ROOT / "outputs" / "deadline_backfill"

SOURCE_FILTER_ALIASES = {
    "grants_gov": ("grants.gov", "grants gov"),
    "bndes": ("bndes",),
    "doe_arpae": ("doe_arpae", "arpa-e", "arpa e"),
    "eureka": ("eureka",),
    "erc": ("erc",),
    "amazul": ("amazul",),
}


def _pct(n: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{100 * n / total:.1f}%"


def _matches_source_filter(record: Dict[str, Any], source_filter: Optional[str]) -> bool:
    if not source_filter:
        return True
    aliases = SOURCE_FILTER_ALIASES.get(source_filter.lower(), (source_filter,))
    fonte = str(record.get("fonte_recurso") or record.get("fonte") or "").lower()
    return any(a in fonte for a in aliases)


def run_backfill_audit(
    records: List[Dict[str, Any]],
    *,
    source_filter: Optional[str] = None,
) -> Dict[str, Any]:
    total = 0
    status_c = Counter()
    sem_kind_c = Counter()
    by_source: Dict[str, Counter] = defaultdict(Counter)

    candidates: List[Dict[str, Any]] = []
    preserved: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    explained: List[Dict[str, Any]] = []
    unknown: List[Dict[str, Any]] = []
    recrawl: List[Dict[str, Any]] = []

    for rec in records:
        if not _matches_source_filter(rec, source_filter):
            continue
        total += 1
        result = extract_source_deadline_fields(rec)
        _, applied = apply_deadline_backfill_in_memory(rec)

        status = result.get("deadline_backfill_status") or "no_candidate"
        status_c[status] += 1
        src = result.get("backfill_source_key") or normalize_backfill_source(rec)
        by_source[src][status] += 1

        kind = result.get("sem_prazo_kind")
        if kind:
            sem_kind_c[kind] += 1

        row = {
            "id_edital": rec.get("id_edital"),
            "titulo": (rec.get("titulo") or "")[:100],
            "fonte": rec.get("fonte_recurso") or rec.get("fonte"),
            "backfill_source": src,
            "deadline_backfill_status": status,
            "prazo_envio": result.get("prazo_envio"),
            "prazo_fonte": result.get("prazo_fonte"),
            "deadline_reason": result.get("deadline_reason"),
            "sem_prazo_kind": kind,
            "sem_prazo_reason": result.get("sem_prazo_reason"),
            "rejection_reason": result.get("rejection_reason"),
        }

        if status == "new_deadline_found":
            if len(candidates) < 120:
                candidates.append(row)
        elif status == "preserved_existing":
            if len(preserved) < 80:
                preserved.append(row)
        elif status == "replacement_candidate":
            if len(candidates) < 120:
                candidates.append({**row, "note": "replacement_candidate"})
        elif status == "rejected_deadline":
            if len(rejected) < 80:
                rejected.append(row)
        elif status == "no_deadline_explained":
            if len(explained) < 120:
                explained.append(row)
            if result.get("recrawl_candidate") and len(recrawl) < 80:
                recrawl.append(row)
        elif status == "no_candidate":
            if len(unknown) < 80:
                unknown.append(row)

    by_source_json = {k: dict(v) for k, v in by_source.items()}

    return {
        "backfill_version": BACKFILL_SOURCE,
        "source_filter": source_filter,
        "total_analyzed": total,
        "status_distribution": dict(status_c),
        "sem_prazo_kind_distribution": dict(sem_kind_c),
        "by_source": by_source_json,
        "counts": {
            "new_deadline_candidates": status_c.get("new_deadline_found", 0)
            + status_c.get("replacement_candidate", 0),
            "preserved_existing": status_c.get("preserved_existing", 0),
            "rejected_deadlines": status_c.get("rejected_deadline", 0),
            "no_deadline_explained": status_c.get("no_deadline_explained", 0),
            "no_candidate_unknown": status_c.get("no_candidate", 0),
            "recrawl_pdf_candidates": len(recrawl),
        },
        "backfill_candidates": candidates,
        "preserved_deadlines": preserved,
        "rejected_deadlines": rejected,
        "no_deadline_explained": explained,
        "no_candidate_unknown": unknown,
        "recrawl_pdf_candidates": recrawl,
    }


def build_summary_md(r: Dict[str, Any]) -> str:
    t = r["total_analyzed"]
    c = r["counts"]
    lines = [
        "# Dry-run deadline backfill — Backend 10.1E",
        "",
        f"**Versão:** {r['backfill_version']} | **Total analisado:** {t}",
    ]
    if r.get("source_filter"):
        lines.append(f"**Filtro fonte:** `{r['source_filter']}`")
    lines.extend(
        [
            "",
            "## Resumo",
            "",
            f"- Novos prazos candidatos: **{c['new_deadline_candidates']}**",
            f"- Prazos preservados: **{c['preserved_existing']}**",
            f"- Prazos rejeitados: **{c['rejected_deadlines']}**",
            f"- Sem prazo explicado: **{c['no_deadline_explained']}**",
            f"- Sem prazo desconhecido: **{c['no_candidate_unknown']}**",
            f"- Candidatos recrawl/PDF: **{c['recrawl_pdf_candidates']}**",
            "",
            "## deadline_backfill_status",
            "",
        ]
    )
    for k, v in sorted(r["status_distribution"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v} ({_pct(v, t)})")
    lines.extend(["", "## sem_prazo_kind", ""])
    for k, v in sorted(r["sem_prazo_kind_distribution"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Por fonte", ""])
    for src, dist in sorted(r["by_source"].items()):
        lines.append(f"### {src}")
        for k, v in sorted(dist.items(), key=lambda x: -x[1]):
            lines.append(f"- `{k}`: {v}")
        lines.append("")
    lines.append("Ver JSONs: `backfill_candidates.json`, `no_deadline_explained.json`, `rejected_deadlines.json`.")
    lines.append("")
    lines.append("**Regra:** `sem_prazo` é condição de validade, não de ruído.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run deadline backfill 10.1E")
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--source", type=str, default=None, help="grants_gov|bndes|doe_arpae|...")
    ap.add_argument("--output", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    records = load_records(from_db=args.from_db, input_path=args.input, limit=args.limit)
    out = args.output
    if args.source:
        out = out / args.source.lower()
    if not records:
        write_json(out / "report.json", {"total_analyzed": 0, "error": "no_data"})
        return 1

    report = run_backfill_audit(records, source_filter=args.source)
    write_json(out / "report.json", report)
    write_json(out / "by_source.json", report["by_source"])
    write_json(out / "backfill_candidates.json", report["backfill_candidates"])
    write_json(out / "no_deadline_explained.json", report["no_deadline_explained"])
    write_json(out / "rejected_deadlines.json", report["rejected_deadlines"])
    write_json(out / "preserved_deadlines.json", report.get("preserved_deadlines", []))
    write_json(out / "recrawl_pdf_candidates.json", report["recrawl_pdf_candidates"])
    write_md(out / "summary.md", build_summary_md(report))
    print(f"[dry_run_deadline_backfill] {report['total_analyzed']} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
