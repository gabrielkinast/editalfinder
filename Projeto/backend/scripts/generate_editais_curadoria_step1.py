#!/usr/bin/env python3
"""Gera APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql e plano (não executa SQL)."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parent.parent
VIS_DIR = ROOT / "audit_reports_main_pipeline" / "editais_visibility_noise_global"
GRANTS_BROKEN = ROOT / "audit_reports_main_pipeline" / "link_health_grants_db_v2" / "broken_links.json"

SAFE_VISIBILITY = frozenset(
    {
        "hidden_institutional",
        "hidden_resultado",
        "hidden_invalid_link",
        "hidden_duplicate",
    }
)

DEFER_VISIBILITY = frozenset(
    {
        "hidden_historical",
        "hidden_expired",
        "hidden_not_opportunity",
        "review_missing_deadline",
        "review_possible_continuous_flow",
        "review_possible_opportunity",
        "review_link_suspicious",
    }
)

BROKEN_LINK = frozenset({"broken_404", "broken_spa_not_found", "timeout", "invalid_url"})
ESSENTIAL_CAMPOS = frozenset({"link", "link_edital", "link_inscricao", "origem", "url_detalhe"})


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_link_health_from_broken(rows: List[Dict[str, Any]]) -> Dict[int, Dict[str, Any]]:
    by_id: Dict[int, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        try:
            ie = int(r.get("id_edital") or 0)
        except (TypeError, ValueError):
            continue
        if ie:
            by_id[ie].append(r)

    out: Dict[int, Dict[str, Any]] = {}
    for ie, flds in by_id.items():
        essential = [f for f in flds if str(f.get("campo") or "").split("[")[0] in ESSENTIAL_CAMPOS]
        broken_ess = [f for f in essential if f.get("link_status") in BROKEN_LINK]
        if not broken_ess:
            continue
        primary = next((f for f in broken_ess if f.get("campo") == "link"), broken_ess[0])
        agg_st = str(primary.get("link_status") or "broken_404")
        out[ie] = {
            "link_status": agg_st,
            "checked_at": primary.get("checked_at"),
            "final_url": primary.get("final_url") or "",
            "http_status": primary.get("http_status"),
            "error_message": primary.get("error_message") or "",
            "recommendation": "marcar_link_quebrado",
            "fields": [
                {
                    "campo": f.get("campo"),
                    "link": f.get("link"),
                    "final_url": f.get("final_url"),
                    "http_status": f.get("http_status"),
                    "link_status": f.get("link_status"),
                    "essential_broken": f.get("essential_broken"),
                    "error_message": f.get("error_message"),
                }
                for f in flds
            ],
            "all_essential_broken": all(
                f.get("link_status") in BROKEN_LINK for f in essential
            ),
            "has_accessible_link": False,
        }
    return out


def main() -> None:
    hidden = _load(VIS_DIR / "hidden_candidates.json")
    classificados = _load(VIS_DIR / "classificados.json")
    grants_rows = _load(GRANTS_BROKEN) if GRANTS_BROKEN.is_file() else []

    link_health_by_id = _build_link_health_from_broken(grants_rows)

    # Safe rows from visibility audit
    plan: Dict[int, Dict[str, Any]] = {}
    for row in hidden:
        vis = str(row.get("visibility") or "")
        if vis not in SAFE_VISIBILITY:
            continue
        try:
            ie = int(row.get("id_edital"))
        except (TypeError, ValueError):
            continue
        cf = row.get("curadoria_front") or {
            "visibility": vis,
            "reason": row.get("reason"),
            "confidence": row.get("confidence"),
            "checked_at": row.get("checked_at"),
            "rule_version": row.get("rule_version") or "editais_visibility_v1",
            "signals": row.get("signals") or [],
            "source_recommendation": row.get("source_recommendation") or "",
        }
        plan[ie] = {
            "id_edital": ie,
            "titulo": row.get("titulo"),
            "fonte_recurso": row.get("fonte_recurso"),
            "visibility": vis,
            "curadoria_front": cf,
            "link_health": None,
            "source": "visibility_audit",
        }

    # Grants: hidden_invalid_link + link_health (não sobrescrever duplicate/institutional/resultado)
    for ie, lh in link_health_by_id.items():
        if ie in plan:
            plan[ie]["link_health"] = lh
            if plan[ie]["visibility"] == "hidden_invalid_link":
                plan[ie]["source"] = "visibility_audit+grants_link_health"
            else:
                plan[ie]["source"] = f"{plan[ie]['visibility']}+grants_link_health"
            continue
        plan[ie] = {
            "id_edital": ie,
            "titulo": (grants_rows[0] if False else None),
            "fonte_recurso": "Grants.gov",
            "visibility": "hidden_invalid_link",
            "curadoria_front": {
                "visibility": "hidden_invalid_link",
                "reason": lh.get("error_message")
                or "Link essencial quebrado (auditoria Grants.gov).",
                "confidence": "alta",
                "checked_at": lh.get("checked_at"),
                "rule_version": "editais_visibility_v1",
                "signals": ["grants_link_health", "essential_link_broken"],
                "source_recommendation": "precisa_melhoria_crawler",
            },
            "link_health": lh,
            "source": "grants_link_health",
        }
        for r in grants_rows:
            if int(r.get("id_edital") or 0) == ie:
                plan[ie]["titulo"] = r.get("titulo")
                plan[ie]["fonte_recurso"] = r.get("fonte_recurso") or "Grants.gov"
                break

    # Enrich titulo/fonte from classificados
    by_id_cls = {int(c["id_edital"]): c for c in classificados if c.get("id_edital")}
    for ie, p in plan.items():
        if ie in by_id_cls:
            if not p.get("titulo"):
                p["titulo"] = by_id_cls[ie].get("titulo")
            if not p.get("fonte_recurso") or p["fonte_recurso"] == "Grants.gov":
                p["fonte_recurso"] = by_id_cls[ie].get("fonte_recurso") or p.get("fonte_recurso")

    # Deferred counts (etapa 2)
    defer_counts = Counter()
    defer_examples: Dict[str, List[Dict]] = defaultdict(list)
    for row in classificados:
        vis = str(row.get("visibility") or "")
        ie = row.get("id_edital")
        if vis in SAFE_VISIBILITY and int(ie) in plan:
            continue
        if vis in DEFER_VISIBILITY or vis.startswith("hidden_") or vis.startswith("review_"):
            defer_counts[vis] += 1
            if len(defer_examples[vis]) < 3:
                defer_examples[vis].append(
                    {
                        "id_edital": ie,
                        "titulo": str(row.get("titulo") or "")[:100],
                        "fonte_recurso": row.get("fonte_recurso"),
                    }
                )
        elif vis.startswith("visible"):
            pass

    items = sorted(plan.values(), key=lambda x: x["id_edital"])
    vis_c = Counter(p["visibility"] for p in items)
    fonte_c = Counter(p.get("fonte_recurso") or "—" for p in items)
    with_lh = sum(1 for p in items if p.get("link_health"))

    plan_doc = {
        "generated_at": classificados[0].get("checked_at") if classificados else None,
        "rule_version": "editais_visibility_v1",
        "step": 1,
        "safe_visibilities": sorted(SAFE_VISIBILITY),
        "deferred_to_step2": sorted(DEFER_VISIBILITY) + ["hidden_historical", "hidden_expired", "hidden_not_opportunity"],
        "total_to_update": len(items),
        "with_link_health": with_lh,
        "por_visibility": dict(vis_c),
        "por_fonte_recurso": dict(fonte_c.most_common(40)),
        "exemplos_por_visibility": {},
        "deferred_counts": dict(defer_counts),
        "deferred_examples": dict(defer_examples),
        "sql_file": "docs/sql/APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql",
        "not_executed": True,
    }
    for vis in SAFE_VISIBILITY:
        ex = [p for p in items if p["visibility"] == vis][:5]
        plan_doc["exemplos_por_visibility"][vis] = [
            {
                "id_edital": p["id_edital"],
                "titulo": str(p.get("titulo") or "")[:100],
                "fonte_recurso": p.get("fonte_recurso"),
                "source": p.get("source"),
            }
            for p in ex
        ]

    # SQL
    sql_lines = [
        "-- =============================================================================",
        "-- APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql",
        "-- =============================================================================",
        "-- ETAPA 1 — curadoria segura (alta confiança). REVISAR ANTES DE EXECUTAR.",
        "-- Não DELETE. Apenas extras.curadoria_front (+ extras.link_health para Grants).",
        f"-- Total UPDATEs: {len(items)}",
        f"-- Por visibility: {dict(vis_c)}",
        "--",
        "-- FORA desta etapa: hidden_historical, review_*, hidden_expired, hidden_not_opportunity",
        "--",
        "BEGIN;",
        "",
    ]

    for p in items:
        ie = p["id_edital"]
        cf = json.dumps(p["curadoria_front"], ensure_ascii=False).replace("'", "''")
        tit = str(p.get("titulo") or "")[:90].replace("'", "''")
        vis = p["visibility"]
        sql_lines.append(f"-- id_edital={ie} | {vis} | {p.get('fonte_recurso')} | {tit}")
        if p.get("link_health"):
            lh = json.dumps(p["link_health"], ensure_ascii=False).replace("'", "''")
            sql_lines.append(
                f"UPDATE public.edital SET extras = jsonb_set("
                f"jsonb_set(COALESCE(extras, '{{}}'::jsonb), '{{curadoria_front}}', '{cf}'::jsonb), "
                f"'{{link_health}}', '{lh}'::jsonb), atualizado_em = now() "
                f"WHERE id_edital = {ie};"
            )
        else:
            sql_lines.append(
                f"UPDATE public.edital SET extras = jsonb_set("
                f"COALESCE(extras, '{{}}'::jsonb), '{{curadoria_front}}', '{cf}'::jsonb), "
                f"atualizado_em = now() WHERE id_edital = {ie};"
            )
        sql_lines.append("")

    sql_lines.extend(["COMMIT;", "", "-- Fim etapa 1"])

    sql_path = ROOT / "docs" / "sql" / "APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql"
    sql_path.write_text("\n".join(sql_lines), encoding="utf-8")

    (VIS_DIR / "step1_apply_plan.json").write_text(
        json.dumps(plan_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Etapa 1 — plano de apply (curadoria segura)",
        "",
        f"- **Total UPDATEs:** {len(items)}",
        f"- **Com link_health:** {with_lh}",
        f"- **SQL:** `docs/sql/APPLY_EDITAIS_CURADORIA_FRONT_SAFE_STEP1.sql`",
        "",
        "## Por visibility",
        "",
    ]
    for k, v in vis_c.most_common():
        md.append(f"- `{k}`: {v}")
    md.extend(["", "## Por fonte (top 15)", ""])
    for k, v in fonte_c.most_common(15):
        md.append(f"- **{k}**: {v}")
    md.extend(["", "## Deixado para etapa 2", ""])
    for k, v in defer_counts.most_common():
        md.append(f"- `{k}`: {v}")
    md.extend(["", "## Exemplos etapa 1", ""])
    for vis, exs in plan_doc["exemplos_por_visibility"].items():
        md.append(f"### {vis}")
        for ex in exs:
            md.append(f"- {ex['id_edital']}: {ex['titulo'][:80]}… ({ex['fonte_recurso']})")
        md.append("")
    (VIS_DIR / "step1_apply_plan.md").write_text("\n".join(md), encoding="utf-8")

    print(f"SQL: {sql_path}")
    print(f"Plan: {len(items)} updates, link_health={with_lh}")
    print(dict(vis_c))


if __name__ == "__main__":
    main()
