#!/usr/bin/env python3
"""
Auditoria: registros Grants.gov legados → URL Simpler.Grants.gov.

Não aplica SQL. Saída em audit_reports_main_pipeline/grants_simpler_migration/:
  summary.json, summary.md
  matched_updates.json
  unmatched_legacy_broken.json
  sql_updates_sugeridos.sql

Uso:
  python scripts/audit_grants_legacy_to_simpler.py --from-json CORE/transformer/grants_gov_standardized.json
  python scripts/audit_grants_legacy_to_simpler.py --from-db --limit 200
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from link_health import (  # noqa: E402
    build_item_link_health,
    check_url,
    collect_link_fields,
    detect_grants_gov_legacy_view_opportunity,
)
from grants_gov.simpler_grants_common import (
    build_canonical_opportunity_url,
    extract_legacy_opp_id_from_item,
    extract_opportunity_number_from_item,
    get_api_key,
    probe_simpler_opportunity_exists,
    fetch_simpler_search_page,
    map_simpler_api_hit,
    _session,
)

OUT_DIR = ROOT / "audit_reports_main_pipeline" / "grants_simpler_migration"
DEFAULT_JSON = CORE / "transformer" / "grants_gov_standardized.json"


def _is_grants_item(item: Dict[str, Any]) -> bool:
    fonte = str(item.get("fonte") or item.get("fonte_recurso") or "").lower()
    link = str(item.get("link") or "").lower()
    return "grant" in fonte or "grants.gov" in link


def _load_json(path: Path, limit: int) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else [raw]
    items = [x for x in items if isinstance(x, dict) and _is_grants_item(x)]
    return items[:limit] if limit > 0 else items


def _load_db(limit: int) -> List[Dict[str, Any]]:
    try:
        from db import supabase  # type: ignore
    except Exception as exc:
        raise SystemExit(f"Supabase indisponível: {exc}") from exc

    q = (
        supabase.table("edital")
        .select("id_edital,titulo,link,fonte_recurso,extras,prazo_envio,data_publicacao")
        .ilike("fonte_recurso", "%grant%")
        .limit(limit)
    )
    res = q.execute()
    rows = res.data or []
    out = []
    for row in rows:
        ex = row.get("extras") if isinstance(row.get("extras"), dict) else {}
        out.append(
            {
                "id_edital": row.get("id_edital"),
                "titulo": row.get("titulo"),
                "link": row.get("link"),
                "fonte": row.get("fonte_recurso"),
                "fonte_recurso": row.get("fonte_recurso"),
                "fim_inscricao": row.get("prazo_envio"),
                "data_publicacao": row.get("data_publicacao"),
                "extras": ex,
            }
        )
    return out


def _search_simpler_by_number(
    session: requests.Session,
    opp_num: str,
    api_key: str,
) -> Optional[Dict[str, Any]]:
    if not api_key or not opp_num:
        return None
    try:
        rows, _ = fetch_simpler_search_page(
            session,
            page_offset=1,
            page_size=5,
            statuses=["posted", "forecasted", "closed", "archived"],
            api_key=api_key,
            query=opp_num[:80],
        )
    except Exception:
        return None
    num_up = opp_num.strip().upper()
    for row in rows:
        if str(row.get("opportunity_number") or "").upper() == num_up:
            return map_simpler_api_hit(row)
    return None


def _sql_update(row: Dict[str, Any]) -> str:
    eid = row.get("id_edital")
    new_link = row.get("suggested_link", "").replace("'", "''")
    titulo = str(row.get("titulo") or "")[:60].replace("'", "''")
    return (
        f"-- id_edital={eid} | {titulo}\n"
        f"-- UPDATE public.edital SET link = '{new_link}', "
        f"extras = jsonb_set(COALESCE(extras,'{{}}'::jsonb), '{{source_variant}}', '\"simpler_grants_gov\"') "
        f"WHERE id_edital = {eid};\n"
    )


def run_audit(
    items: List[Dict[str, Any]],
    *,
    sleep_sec: float = 0.5,
    probe_simpler: bool = True,
) -> Dict[str, Any]:
    session = _session()
    api_key = get_api_key()
    matched: List[Dict[str, Any]] = []
    unmatched: List[Dict[str, Any]] = []

    for item in items:
        link = str(item.get("link") or "")
        legacy = extract_legacy_opp_id_from_item(item)
        opp_num = extract_opportunity_number_from_item(item)
        is_legacy_url = "view-opportunity" in link.lower()

        legacy_broken = False
        if is_legacy_url and legacy:
            legacy_broken, _ = detect_grants_gov_legacy_view_opportunity(
                link, session=session, timeout=20.0
            )

        suggested = None
        match_method = None

        if api_key and opp_num:
            hit = _search_simpler_by_number(session, opp_num, api_key)
            if hit:
                suggested = hit.get("link")
                match_method = "api_opportunity_number"
                time.sleep(sleep_sec)

        if not suggested and legacy and probe_simpler:
            ok, detail = probe_simpler_opportunity_exists(legacy, session=session)
            if ok:
                suggested = build_canonical_opportunity_url(legacy_opp_id=legacy)
                match_method = "probe_simpler_legacy_id"

        if not suggested and legacy:
            suggested = build_canonical_opportunity_url(legacy_opp_id=legacy)
            match_method = match_method or "inferred_legacy_id"

        row = {
            "id_edital": item.get("id_edital"),
            "titulo": item.get("titulo"),
            "link_atual": link,
            "opportunity_number": opp_num,
            "legacy_opp_id": legacy,
            "legacy_broken_spa": legacy_broken,
            "suggested_link": suggested,
            "match_method": match_method,
        }

        if suggested and (is_legacy_url or legacy_broken or "simpler.grants.gov" not in link.lower()):
            matched.append(row)
        elif legacy_broken or is_legacy_url:
            ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
            field_results = []
            for campo, url in collect_link_fields(item):
                field_results.append(
                    {**check_url(url, session=session, campo=campo), "campo": campo, "link": url}
                )
            lh = build_item_link_health(item, field_results)
            unmatched.append(
                {
                    **row,
                    "link_health": lh,
                    "visibility_suggestion": "hidden_invalid_link",
                }
            )
        time.sleep(sleep_sec * 0.5)

    return {
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "matched_updates": matched,
        "unmatched_legacy_broken": unmatched,
        "api_key_used": bool(api_key),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-json", type=Path, default=None)
    parser.add_argument("--from-db", action="store_true")
    parser.add_argument("--limit", type=int, default=150)
    parser.add_argument("--sleep", type=float, default=0.5)
    args = parser.parse_args()

    if args.from_db:
        items = _load_db(args.limit)
        source_label = "supabase"
    else:
        path = args.from_json or DEFAULT_JSON
        path = path if path.is_absolute() else (ROOT / path).resolve()
        if not path.is_file():
            raise SystemExit(f"JSON não encontrado: {path}")
        items = _load_json(path, args.limit)
        source_label = str(path)

    print(f"[audit] {len(items)} itens Grants de {source_label}")
    result = run_audit(items, sleep_sec=args.sleep)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "matched_updates.json").write_text(
        json.dumps(result["matched_updates"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUT_DIR / "unmatched_legacy_broken.json").write_text(
        json.dumps(result["unmatched_legacy_broken"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    summary = {
        "source": source_label,
        "items_audited": len(items),
        "matched_count": result["matched_count"],
        "unmatched_count": result["unmatched_count"],
        "api_key_used": result["api_key_used"],
        "note": "SQL sugerido não aplicado automaticamente",
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    sql_lines = [
        "-- Sugestões de UPDATE (revisar antes de executar)",
        "-- Grants.gov legado → Simpler.Grants.gov",
        "",
    ]
    for row in result["matched_updates"][:500]:
        if row.get("suggested_link"):
            sql_lines.append(_sql_update(row))
    (OUT_DIR / "sql_updates_sugeridos.sql").write_text("\n".join(sql_lines), encoding="utf-8")

    md = [
        "# Migração Grants.gov → Simpler.Grants.gov",
        "",
        f"- Itens auditados: **{len(items)}**",
        f"- Match com URL Simpler sugerida: **{result['matched_count']}**",
        f"- Legado quebrado sem match: **{result['unmatched_count']}**",
        f"- API key Simpler: **{result['api_key_used']}**",
        "",
        "Registros antigos **não são apagados**. Aplicar `sql_updates_sugeridos.sql` apenas após revisão.",
    ]
    (OUT_DIR / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"[audit] matched={result['matched_count']} unmatched={result['unmatched_count']} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
