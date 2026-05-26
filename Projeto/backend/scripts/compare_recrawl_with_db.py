#!/usr/bin/env python3
"""
Compara amostra recoletada (enriched) com registros atuais no banco — somente leitura.

Uso standalone:
  python scripts/compare_recrawl_with_db.py --source grants --enriched outputs/backend_4_recrawl_comparison/grants/enriched_sample.json
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records  # noqa: E402
from _recrawl_common import (  # noqa: E402
    DEFAULT_OUT,
    db_structured_deadline,
    fonte_matches,
    item_has_deadline,
    match_key,
    normalize_link,
    normalize_title,
    write_json,
    write_md,
)


def compare_source(
    enriched_new: List[Dict[str, Any]],
    db_records: List[Dict[str, Any]],
    source: str,
) -> Dict[str, Any]:
    db_subset = [r for r in db_records if fonte_matches(str(r.get("fonte_recurso") or r.get("fonte") or ""), source)]
    by_key_db: Dict[str, Dict[str, Any]] = {}
    for r in db_subset:
        by_key_db[match_key(r)] = r

    by_key_new: Dict[str, Dict[str, Any]] = {}
    for it in enriched_new:
        by_key_new[match_key(it)] = it

    keys_db = set(by_key_db)
    keys_new = set(by_key_new)
    matched = keys_db & keys_new
    new_only = keys_new - keys_db
    db_only = keys_db - keys_new

    deadlines_gained = 0
    deadlines_changed = 0
    title_changed = 0
    link_changed = 0
    matched_diffs: List[Dict[str, Any]] = []

    for k in matched:
        db_r = by_key_db[k]
        new_r = by_key_new[k]
        had_db, iso_db, _ = (db_structured_deadline(db_r), None, None)
        if had_db:
            for fld in ("prazo_envio", "fim_inscricao"):
                v = db_r.get(fld)
                if v and "-" in str(v)[:10]:
                    iso_db = str(v)[:10]
                    break
        has_new, iso_new, conf_new = item_has_deadline(new_r)
        if has_new and not had_db:
            deadlines_gained += 1
        if has_new and had_db and iso_new and iso_db and iso_new != iso_db:
            deadlines_changed += 1
        if normalize_title(db_r.get("titulo")) != normalize_title(new_r.get("titulo")):
            title_changed += 1
        if normalize_link(db_r.get("link")) != normalize_link(new_r.get("link")):
            link_changed += 1
        if deadlines_gained or deadlines_changed or (has_new and not had_db):
            matched_diffs.append(
                {
                    "match_key": k,
                    "id_edital": db_r.get("id_edital"),
                    "titulo": (new_r.get("titulo") or "")[:80],
                    "prazo_db": iso_db,
                    "prazo_new": iso_new,
                    "prazo_confidence": conf_new,
                    "link_db": db_r.get("link"),
                    "link_new": new_r.get("link"),
                }
            )

    unmatched_new = [
        {
            "match_key": k,
            "titulo": (by_key_new[k].get("titulo") or "")[:100],
            "link": by_key_new[k].get("link"),
            "prazo_new": item_has_deadline(by_key_new[k])[1],
        }
        for k in sorted(new_only)[:100]
    ]
    unmatched_db = [
        {
            "match_key": k,
            "id_edital": by_key_db[k].get("id_edital"),
            "titulo": (by_key_db[k].get("titulo") or "")[:100],
            "link": by_key_db[k].get("link"),
            "prazo_db": by_key_db[k].get("prazo_envio"),
        }
        for k in sorted(db_only)[:100]
    ]

    new_with_deadline = sum(1 for k in new_only if item_has_deadline(by_key_new[k])[0])

    return {
        "source": source,
        "db_count": len(db_subset),
        "new_count": len(enriched_new),
        "matched_count": len(matched),
        "new_only_count": len(new_only),
        "db_only_count": len(db_only),
        "deadlines_gained_on_matched": deadlines_gained,
        "deadlines_changed": deadlines_changed,
        "title_changed": title_changed,
        "link_changed": link_changed,
        "new_only_with_deadline": new_with_deadline,
        "deadline_gain_estimate": deadlines_gained + new_with_deadline,
        "matched_diff": matched_diffs[:200],
        "unmatched_new": unmatched_new,
        "unmatched_db": unmatched_db,
    }


def build_comparison_md(results: Dict[str, Any]) -> str:
    lines = ["# Comparação recoleta vs banco — Backend 4", ""]
    for src, data in results.items():
        lines.extend(
            [
                f"## {src}",
                f"- BD: **{data['db_count']}** | Recoleta: **{data['new_count']}**",
                f"- Matched: **{data['matched_count']}** | Só novo: **{data['new_only_count']}** | Só BD: **{data['db_only_count']}**",
                f"- Prazo ganho (matched): **{data['deadlines_gained_on_matched']}**",
                f"- Prazo alterado: **{data['deadlines_changed']}**",
                f"- Novos com prazo: **{data['new_only_with_deadline']}**",
                f"- **Ganho estimado:** {data['deadline_gain_estimate']}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["china", "araucaria", "grants", "all"], default="all")
    ap.add_argument("--enriched", type=Path, help="Arquivo enriched único (senão lê por fonte do output dir)")
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--limit", type=int, default=5000)
    args = ap.parse_args()

    if not args.from_db:
        print("Use --from-db para carregar registros Supabase", file=sys.stderr)
        return 1

    db_records = load_records(from_db=True, limit=args.limit)
    sources = ["china", "araucaria", "grants"] if args.source == "all" else [args.source]
    results: Dict[str, Any] = {}

    for src in sources:
        path = args.enriched or (args.output / src / "enriched_sample.json")
        if not path.is_file():
            print(f"[compare] ausente {path}", file=sys.stderr)
            continue
        import json

        enriched = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(enriched, list):
            enriched = [enriched]
        results[src] = compare_source(enriched, db_records, src)
        write_json(args.output / src / "matched_diff.json", results[src].get("matched_diff", []))
        write_json(args.output / src / "unmatched_new.json", results[src].get("unmatched_new", []))
        write_json(args.output / src / "unmatched_db.json", results[src].get("unmatched_db", []))

    write_md(args.output / "summary" / "comparison_summary.md", build_comparison_md(results))
    write_json(args.output / "summary" / "comparison_report.json", results)
    print(f"[compare_recrawl_with_db] -> {args.output / 'summary'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
