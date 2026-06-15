#!/usr/bin/env python3
"""
Dry-run do wiring loader ↔ deadline_backfill (Backend 10.2A).

Compara payload antes/depois do backfill (sem upsert).

Uso:
  python scripts/dry_run_loader_deadline_wiring.py --source grants_gov --limit 200
  python scripts/dry_run_loader_deadline_wiring.py --source bndes --limit 200
  python scripts/dry_run_loader_deadline_wiring.py --from-db --limit 500
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from deadline_backfill import (  # noqa: E402
    LOADER_WIRING_VERSION,
    apply_deadline_backfill_to_payload,
    extract_source_deadline_fields,
    normalize_backfill_source,
)
from loader import map_to_db_schema  # noqa: E402

OUT_DIR = ROOT / "outputs" / "loader_deadline_wiring"
TRANSFORMER_DIR = ROOT / "CORE" / "transformer"

SOURCE_FILES = {
    "grants_gov": TRANSFORMER_DIR / "grants_gov_standardized.json",
    "bndes": TRANSFORMER_DIR / "bndes_standardized.json",
    "doe_arpae": TRANSFORMER_DIR / "doe_arpae_standardized.json",
    "eureka": TRANSFORMER_DIR / "eureka_network_standardized.json",
    "erc": TRANSFORMER_DIR / "erc_standardized.json",
    "amazul": TRANSFORMER_DIR / "amazul_standardized.json",
}


def _load_standardized(source: Optional[str], limit: Optional[int]) -> List[Dict[str, Any]]:
    if source and source in SOURCE_FILES:
        path = SOURCE_FILES[source]
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            rows = data if isinstance(data, list) else [data]
            return rows[:limit] if limit else rows
    return []


def _snapshot_payload(item: Dict[str, Any]) -> Dict[str, Any]:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    return {
        "fim_inscricao": item.get("fim_inscricao"),
        "prazo_envio": item.get("prazo_envio"),
        "extras_closeDate": extras.get("closeDate"),
        "extras_close_date": extras.get("close_date"),
        "extras_grants_close_date": extras.get("grants_close_date"),
        "sem_prazo_kind": extras.get("sem_prazo_kind"),
        "loader_deadline_backfill": extras.get("loader_deadline_backfill"),
    }


def run_wiring_audit(
    records: List[Dict[str, Any]],
    *,
    source_filter: Optional[str] = None,
) -> Dict[str, Any]:
    status_c = Counter()
    by_source: Dict[str, Counter] = defaultdict(Counter)
    examples: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    unchanged = 0
    changed = 0

    for rec in records:
        src = normalize_backfill_source(rec)
        if source_filter and src != source_filter:
            continue

        before = _snapshot_payload(rec)
        after_item = apply_deadline_backfill_to_payload(copy.deepcopy(rec), enabled=True)
        after = _snapshot_payload(after_item)
        result = extract_source_deadline_fields(rec)
        status = result.get("deadline_backfill_status") or "no_candidate"
        status_c[status] += 1
        by_source[src][status] += 1

        mapped_before, _ = map_to_db_schema(rec)
        mapped_after, _ = map_to_db_schema(after_item)
        prazo_before = mapped_before.get("prazo_envio")
        prazo_after = mapped_after.get("prazo_envio")

        if before == after and prazo_before == prazo_after:
            unchanged += 1
        else:
            changed += 1
            if len(examples) < 100:
                examples.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:100],
                        "fonte": rec.get("fonte") or rec.get("fonte_recurso"),
                        "source_key": src,
                        "deadline_backfill_status": status,
                        "before": before,
                        "after": after,
                        "prazo_envio_before": prazo_before,
                        "prazo_envio_after": prazo_after,
                        "deadline_reason": result.get("deadline_reason"),
                        "sem_prazo_kind": result.get("sem_prazo_kind"),
                    }
                )

        if status == "rejected_deadline" and len(rejected) < 60:
            rejected.append(
                {
                    "titulo": (rec.get("titulo") or "")[:80],
                    "fonte": rec.get("fonte"),
                    "rejection_reason": result.get("rejection_reason"),
                }
            )

    return {
        "wiring_version": LOADER_WIRING_VERSION,
        "source_filter": source_filter,
        "total": len(records),
        "changed_payloads": changed,
        "unchanged_payloads": unchanged,
        "status_distribution": dict(status_c),
        "by_source": {k: dict(v) for k, v in by_source.items()},
        "before_after_examples": examples,
        "rejected": rejected,
    }


def build_summary_md(r: Dict[str, Any]) -> str:
    lines = [
        "# Loader deadline wiring — Backend 10.2A",
        "",
        f"**Versão:** {r['wiring_version']} | **Registros:** {r['total']}",
    ]
    if r.get("source_filter"):
        lines.append(f"**Filtro:** `{r['source_filter']}`")
    lines.extend(
        [
            "",
            f"- Payloads alterados: **{r['changed_payloads']}**",
            f"- Payloads inalterados: **{r['unchanged_payloads']}**",
            "",
            "## deadline_backfill_status",
            "",
        ]
    )
    for k, v in sorted(r["status_distribution"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Por fonte", ""])
    for src, dist in sorted(r["by_source"].items()):
        lines.append(f"### {src}")
        for k, v in sorted(dist.items(), key=lambda x: -x[1]):
            lines.append(f"- `{k}`: {v}")
        lines.append("")
    lines.append("Ver `before_after_examples.json`. Flag: `EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1`.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run loader deadline wiring 10.2A")
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--source", type=str, default=None)
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--output", type=Path, default=OUT_DIR)
    args = ap.parse_args()

    records: List[Dict[str, Any]] = []
    if args.from_db:
        records = load_records(from_db=True, limit=args.limit)
    else:
        src_key = (args.source or "grants_gov").lower().replace(" ", "_")
        records = _load_standardized(src_key if src_key in SOURCE_FILES else args.source, args.limit)
        if not records and args.source:
            records = load_records(from_db=True, limit=args.limit or 5000)
            records = [
                r
                for r in records
                if normalize_backfill_source(r) == (args.source or "").lower().replace("-", "_")
            ][: args.limit]

    out = args.output
    if args.source:
        out = out / args.source.lower().replace(" ", "_")

    if not records:
        write_json(out / "report.json", {"total": 0, "error": "no_data"})
        return 1

    report = run_wiring_audit(records, source_filter=(args.source or "").lower().replace("-", "_") or None)
    write_json(out / "report.json", report)
    write_json(out / "by_source.json", report["by_source"])
    write_json(out / "before_after_examples.json", report["before_after_examples"])
    write_json(out / "rejected.json", report["rejected"])
    write_md(out / "summary.md", build_summary_md(report))
    print(f"[dry_run_loader_deadline_wiring] {report['total']} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
