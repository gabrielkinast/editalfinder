#!/usr/bin/env python3
"""
Auditoria pós-apply — resolução de duplicatas Grants.gov (Backend 10.3B).

Somente leitura. Confirma:
- duplicatas marcadas hidden_duplicate;
- canônicos não ocultos;
- nenhuma deleção (contagem estável vs baseline opcional).

Uso:
  python scripts/audit_grants_duplicate_resolution.py --from-db --limit 3000
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import filter_records_by_source, iter_records_from_db, write_json, write_md  # noqa: E402
from grants_duplicate_resolution import (  # noqa: E402
    already_hidden_duplicate,
    extract_opportunity_id,
    group_grants_by_opportunity_id,
    is_canonical_detail_link,
    pick_canonical_record,
)
from grants_duplicate_visibility_backfill import audit_visibility_compliance  # noqa: E402

OUT_DIR = ROOT / "outputs" / "grants_duplicate_resolution"


def _audit_records(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    grants = filter_records_by_source(records, "grants_gov")
    hidden: List[Dict[str, Any]] = []
    visible: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []

    for rec in grants:
        ex = rec.get("extras") if isinstance(rec.get("extras"), dict) else {}
        if already_hidden_duplicate(ex):
            hidden.append(rec)
        else:
            visible.append(rec)

    groups = group_grants_by_opportunity_id(grants)
    groups_ok = 0
    groups_with_multiple_visible = 0

    for opp, members in groups.items():
        visible_members = [m for m in members if not already_hidden_duplicate(m.get("extras") or {})]
        hidden_members = [m for m in members if already_hidden_duplicate(m.get("extras") or {})]
        if len(visible_members) == 1:
            groups_ok += 1
        elif len(visible_members) > 1:
            groups_with_multiple_visible += 1
            issues.append(
                {
                    "opportunity_id": opp,
                    "reason": "multiplos_visiveis",
                    "visible_ids": [m.get("id_edital") for m in visible_members],
                    "expected_canonical": pick_canonical_record(members).get("id_edital"),
                }
            )
        elif len(visible_members) == 0 and len(hidden_members) > 0:
            issues.append({"opportunity_id": opp, "reason": "nenhum_visivel_no_grupo", "hidden_count": len(hidden_members)})

    for rec in hidden:
        cf = (rec.get("extras") or {}).get("curadoria_front") or {}
        if not cf.get("duplicate_of_id_edital"):
            issues.append({"id_edital": rec.get("id_edital"), "reason": "hidden_sem_duplicate_of"})
        if cf.get("hidden_duplicate") is not True:
            issues.append({"id_edital": rec.get("id_edital"), "reason": "missing_hidden_duplicate_boolean"})
        if str(cf.get("visibility") or "").lower() != "hidden_duplicate":
            issues.append({"id_edital": rec.get("id_edital"), "reason": "missing_visibility_hidden_duplicate"})
        if not cf.get("duplicate_reason"):
            issues.append({"id_edital": rec.get("id_edital"), "reason": "missing_duplicate_reason"})
        canon_link = cf.get("canonical_link")
        if not canon_link:
            issues.append({"id_edital": rec.get("id_edital"), "reason": "missing_canonical_link"})
        elif not is_canonical_detail_link(canon_link):
            issues.append({"id_edital": rec.get("id_edital"), "reason": "canonical_link_invalido", "link": canon_link})

    visibility_audit = audit_visibility_compliance(records)

    return {
        "total_grants": len(grants),
        "hidden_duplicates": len(hidden),
        "visible_grants": len(visible),
        "duplicate_groups": len(groups),
        "groups_with_one_visible": groups_ok,
        "groups_with_multiple_visible": groups_with_multiple_visible,
        "issues": issues,
        "visibility_compliant": visibility_audit["visibility_compliant"],
        "visibility_issues": visibility_audit["visibility_issues"],
        "visibility_all_compliant": visibility_audit["all_compliant"],
        "sample_hidden": [
            {
                "id_edital": r.get("id_edital"),
                "duplicate_of": (r.get("extras") or {}).get("curadoria_front", {}).get("duplicate_of_id_edital"),
                "opportunity_id": extract_opportunity_id(r),
            }
            for r in hidden[:10]
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria pós-apply duplicatas Grants.gov (10.3B)")
    ap.add_argument("--from-db", action="store_true", required=True)
    ap.add_argument("--limit", type=int, default=3000)
    ap.add_argument("--baseline-total", type=int, default=None, help="Total esperado de editais Grants (sem deleção)")
    args = ap.parse_args()

    rows = list(iter_records_from_db(limit=args.limit))
    report = _audit_records(rows)
    report["audited_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.baseline_total is not None:
        report["baseline_total"] = args.baseline_total
        report["deletions_detected"] = args.baseline_total > report["total_grants"]
    else:
        report["deletions_detected"] = None

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_DIR / "post_audit.json", report)
    write_md(
        OUT_DIR / "post_audit.md",
        "\n".join(
            [
                "# Post-audit — Grants duplicate resolution (10.3B)",
                "",
                f"- **Total Grants.gov:** {report['total_grants']}",
                f"- **Ocultos (hidden_duplicate):** {report['hidden_duplicates']}",
                f"- **Visíveis:** {report['visible_grants']}",
                f"- **Grupos duplicados:** {report['duplicate_groups']}",
                f"- **Grupos com 1 visível:** {report['groups_with_one_visible']}",
                f"- **Grupos com >1 visível:** {report['groups_with_multiple_visible']}",
                f"- **Issues:** {len(report['issues'])}",
                f"- **Visibility compliant (10.3C):** {report.get('visibility_compliant', 0)}",
                f"- **Visibility issues:** {report.get('visibility_issues', 0)}",
            ]
        ),
    )
    print(
        f"[audit_grants_duplicate_resolution] hidden={report['hidden_duplicates']} "
        f"visible={report['visible_grants']} issues={len(report['issues'])} "
        f"visibility_compliant={report.get('visibility_compliant', 0)}"
    )
    all_ok = not report["issues"] and report.get("visibility_all_compliant", True)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
