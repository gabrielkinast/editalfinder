#!/usr/bin/env python3
"""
Auditoria global de visibilidade / ruído — aba Editais (todas as fontes).

Não altera o banco. Gera relatórios e SQL comentado (extras.curadoria_front).

Uso:
  python scripts/audit_editais_visibility_noise.py --from-db --source all --limit 2000
  python scripts/audit_editais_visibility_noise.py --from-db --source "Grants.gov" --limit 500
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from editais_visibility import (  # noqa: E402
    HIDDEN_VALUES,
    REVIEW_VALUES,
    RULE_VERSION,
    VISIBLE_VALUES,
    aggregate_source_report,
    build_curadoria_front,
    classify_edital_visibility,
    utc_now_iso,
)

DEFAULT_OUT = ROOT / "audit_reports_main_pipeline" / "editais_visibility_noise_global"


def _load_from_db(
    *,
    source_filter: Optional[str],
    limit: int,
) -> List[Dict[str, Any]]:
    from db import supabase  # type: ignore

    PAGE = 500
    out: List[Dict[str, Any]] = []
    offset = 0
    sf = (source_filter or "").strip()
    while True:
        q = supabase.table("edital").select("*")
        if sf and sf.lower() != "all":
            q = q.ilike("fonte_recurso", f"%{sf}%")
        q = q.order("id_edital", desc=True).range(offset, offset + PAGE - 1)
        res = q.execute()
        rows = res.data or []
        if not rows:
            break
        out.extend(rows)
        if limit > 0 and len(out) >= limit:
            out = out[:limit]
            break
        if len(rows) < PAGE:
            break
        offset += PAGE
    return out


def _load_json(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return [raw]
    if not isinstance(raw, list):
        return []
    return [x for x in raw if isinstance(x, dict)]


def _maybe_link_health(
    item: Dict[str, Any],
    *,
    enabled: bool,
    cache: Dict[str, Dict[str, Any]],
    sleep_s: float,
) -> None:
    if not enabled:
        return
    ex = item.get("extras")
    if isinstance(ex, dict) and isinstance(ex.get("link_health"), dict):
        return
    link = str(item.get("link") or "").strip()
    if not link or link in cache:
        if link in cache:
            if not isinstance(ex, dict):
                ex = {}
                item["extras"] = ex
            ex["link_health"] = cache[link]
        return
    try:
        from link_health import check_url, build_item_link_health, collect_link_fields

        fields = collect_link_fields(item)
        field_results = []
        for campo, url in fields:
            base = check_url(url, campo=campo, timeout=18.0)
            field_results.append({**base, "campo": campo, "link": url})
            if sleep_s > 0:
                time.sleep(sleep_s)
        agg = build_item_link_health(item, field_results)
        if not isinstance(ex, dict):
            ex = {}
            item["extras"] = ex
        ex["link_health"] = agg
        cache[link] = agg
    except Exception as exc:
        if not isinstance(ex, dict):
            ex = {}
            item["extras"] = ex
        ex["link_health"] = {"link_status": "timeout", "error_message": str(exc)[:200]}


def _audit_items(
    items: List[Dict[str, Any]],
    *,
    include_link_health: bool,
    sleep_s: float,
    sample_per_source: int,
) -> List[Dict[str, Any]]:
    seen_links: Set[str] = set()
    seen_hashes: Set[str] = set()
    lh_cache: Dict[str, Dict[str, Any]] = {}
    source_counts: Counter = Counter()
    classified: List[Dict[str, Any]] = []

    for item in items:
        fonte = str(item.get("fonte_recurso") or item.get("fonte") or "—").strip()
        source_counts[fonte] += 1
        do_lh = include_link_health and (
            sample_per_source <= 0
            or source_counts[fonte] <= sample_per_source
            or "grants" in fonte.lower()
        )
        if do_lh:
            _maybe_link_health(item, enabled=True, cache=lh_cache, sleep_s=sleep_s)

        clf = classify_edital_visibility(item, seen_links=seen_links, seen_hashes=seen_hashes)
        row = {
            "id_edital": item.get("id_edital"),
            "titulo": item.get("titulo"),
            "fonte_recurso": fonte,
            "link": item.get("link"),
            "prazo_envio": item.get("prazo_envio"),
            "data_publicacao": item.get("data_publicacao"),
            "tipo_oportunidade": item.get("tipo_oportunidade"),
            "tipo_recurso": item.get("tipo_recurso"),
            "validacao_status": item.get("validacao_status"),
            "qualidade_dado": item.get("qualidade_dado"),
            "ativo": item.get("ativo"),
            "situacao": item.get("situacao"),
            **clf,
            "curadoria_front": build_curadoria_front(clf),
        }
        classified.append(row)
    return classified


def _partition(classified: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    visible: List[Dict[str, Any]] = []
    hidden: List[Dict[str, Any]] = []
    review: List[Dict[str, Any]] = []
    for r in classified:
        v = r.get("visibility") or ""
        if v in VISIBLE_VALUES:
            visible.append(r)
        elif v in HIDDEN_VALUES:
            hidden.append(r)
        elif v in REVIEW_VALUES:
            review.append(r)
        else:
            review.append(r)
    return {
        "visible_current": [r for r in visible if r.get("visibility") == "visible_current"],
        "visible_all": visible,
        "hidden_candidates": hidden,
        "review_candidates": review,
    }


def _build_summary(classified: List[Dict[str, Any]], origin: str) -> Dict[str, Any]:
    vis_c = Counter(r.get("visibility") for r in classified)
    by_fonte = Counter(str(r.get("fonte_recurso") or "—") for r in classified)
    hidden_reason = Counter(
        r.get("visibility") for r in classified if r.get("visibility") in HIDDEN_VALUES
    )
    src_report = aggregate_source_report(classified)
    noisiest = sorted(
        src_report["sources"],
        key=lambda s: (-(s["hidden"] / max(s["total"], 1)), -s["hidden"]),
    )[:15]
    best_visible = sorted(
        src_report["sources"],
        key=lambda s: (-(s["visible_current"] / max(s["total"], 1)), -s["visible_current"]),
    )[:10]
    return {
        "audited_at": utc_now_iso(),
        "rule_version": RULE_VERSION,
        "origin": origin,
        "total_analisado": len(classified),
        "visiveis": sum(vis_c.get(v, 0) for v in VISIBLE_VALUES),
        "review": sum(vis_c.get(v, 0) for v in REVIEW_VALUES),
        "hidden": sum(vis_c.get(v, 0) for v in HIDDEN_VALUES),
        "por_visibility": dict(vis_c),
        "hidden_por_motivo": dict(hidden_reason),
        "por_fonte_recurso": dict(by_fonte),
        "fontes_maior_ruido": [
            {
                "fonte_recurso": s["fonte_recurso"],
                "total": s["total"],
                "hidden": s["hidden"],
                "hidden_pct": round(100 * s["hidden"] / max(s["total"], 1), 1),
                "recommendation": s["recommendation"],
            }
            for s in noisiest
        ],
        "fontes_mais_atuais": [
            {
                "fonte_recurso": s["fonte_recurso"],
                "visible_current": s["visible_current"],
                "total": s["total"],
                "pct": round(100 * s["visible_current"] / max(s["total"], 1), 1),
            }
            for s in best_visible
        ],
        "exemplos_por_fonte": {
            s["fonte_recurso"]: {
                "ruido": s.get("noise_examples", [])[:3],
                "bons": s.get("good_examples", [])[:2],
            }
            for s in noisiest[:8]
        },
        "recomendacoes_por_fonte": {
            s["fonte_recurso"]: s["recommendation"] for s in src_report["sources"]
        },
    }


def _write_summary_md(summary: Dict[str, Any], path: Path) -> None:
    lines = [
        "# Auditoria global — visibilidade Editais",
        "",
        f"- **Total analisado:** {summary.get('total_analisado')}",
        f"- **Visíveis:** {summary.get('visiveis')}",
        f"- **Revisão:** {summary.get('review')}",
        f"- **Ocultos (candidatos):** {summary.get('hidden')}",
        f"- **Regra:** `{summary.get('rule_version')}`",
        f"- **Origem:** `{summary.get('origin')}`",
        "",
        "## Por visibility",
        "",
    ]
    for k, v in sorted((summary.get("por_visibility") or {}).items(), key=lambda kv: -kv[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Hidden por motivo", ""])
    for k, v in sorted((summary.get("hidden_por_motivo") or {}).items(), key=lambda kv: -kv[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Fontes com maior ruído", ""])
    for s in summary.get("fontes_maior_ruido") or []:
        lines.append(
            f"- **{s['fonte_recurso']}**: {s['hidden']}/{s['total']} hidden ({s['hidden_pct']}%) — `{s['recommendation']}`"
        )
    lines.extend(
        [
            "",
            "## Próximos passos",
            "",
            "1. Revisar `hidden_candidates.json` e `review_candidates.json`.",
            "2. Aplicar manualmente `sql_updates_sugeridos.sql` (extras.curadoria_front).",
            "3. Aplicar `docs/sql/UPDATE_VW_EDITAIS_FRONT_VISIBILITY.sql` em staging.",
            "4. Validar `SELECT fonte_recurso, COUNT(*) FROM public.vw_editais_front GROUP BY 1`.",
            "",
            "**Não** apagar linhas de `public.edital`.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _write_source_md(report: Dict[str, Any], path: Path) -> None:
    lines = ["# Relatório por fonte — visibilidade Editais", ""]
    for s in report.get("sources") or []:
        lines.append(f"## {s['fonte_recurso']}")
        lines.append(f"- total: {s['total']}")
        lines.append(f"- visible_current: {s['visible_current']}")
        lines.append(f"- review: {s['review']}")
        lines.append(f"- hidden: {s['hidden']}")
        lines.append(f"- recomendação: **{s['recommendation']}**")
        if s.get("hidden_by_reason"):
            lines.append("- hidden por motivo:")
            for k, v in sorted(s["hidden_by_reason"].items(), key=lambda kv: -kv[1]):
                lines.append(f"  - `{k}`: {v}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _emit_sql_updates(classified: List[Dict[str, Any]], path: Path) -> None:
    lines = [
        "-- sql_updates_sugeridos.sql (audit_editais_visibility_noise.py)",
        "-- REVISAR ANTES DE EXECUTAR. Não deleta linhas.",
        f"-- generated={utc_now_iso()} rule={RULE_VERSION}",
        "",
    ]
    for r in classified:
        vis = r.get("visibility") or ""
        if vis not in HIDDEN_VALUES and vis not in REVIEW_VALUES and vis not in VISIBLE_VALUES:
            continue
        ie = r.get("id_edital")
        if not ie:
            continue
        cf = r.get("curadoria_front") or build_curadoria_front(r)
        payload = json.dumps(cf, ensure_ascii=False).replace("'", "''")
        tit = str(r.get("titulo") or "")[:80].replace("'", "''")
        lines.append(f"-- id_edital={ie} | {vis} | {tit}")
        lines.append(
            f"-- UPDATE public.edital SET extras = jsonb_set("
            f"COALESCE(extras, '{{}}'::jsonb), '{{curadoria_front}}', '{payload}'::jsonb), "
            f"atualizado_em = now() WHERE id_edital = {int(ie)};"
        )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria global visibilidade/ruído — Editais.")
    ap.add_argument("--from-db", action="store_true", help="Ler public.edital via Supabase")
    ap.add_argument("--from-json", type=Path, default=None, help="JSON local (lista)")
    ap.add_argument("--source", default="all", help="fonte_recurso ou 'all'")
    ap.add_argument("--limit", type=int, default=2000)
    ap.add_argument("--sleep", type=float, default=0.2)
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--include-link-health",
        action="store_true",
        help="Checar link_health (amostra; reutiliza extras se existir)",
    )
    ap.add_argument(
        "--sample-per-source",
        type=int,
        default=20,
        help="Máx. itens por fonte com HTTP link_health (0=todos se --include-link-health)",
    )
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.from_json:
        path = args.from_json if args.from_json.is_absolute() else (ROOT / args.from_json)
        items = _load_json(path)
        origin = str(path)
    elif args.from_db:
        sf = None if args.source.strip().lower() == "all" else args.source.strip()
        items = _load_from_db(source_filter=sf, limit=args.limit)
        origin = f"supabase:edital source={args.source}"
    else:
        print("Use --from-db ou --from-json", file=sys.stderr)
        return 1

    if not items:
        print("Nenhum item.", file=sys.stderr)
        return 1

    print(f"Classificando {len(items)} itens …")
    classified = _audit_items(
        items,
        include_link_health=args.include_link_health,
        sleep_s=args.sleep,
        sample_per_source=args.sample_per_source,
    )
    parts = _partition(classified)
    summary = _build_summary(classified, origin)
    src_report = aggregate_source_report(classified)

    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "classificados.json").write_text(
        json.dumps(classified, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "visible_current.json").write_text(
        json.dumps(parts["visible_current"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "hidden_candidates.json").write_text(
        json.dumps(parts["hidden_candidates"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "review_candidates.json").write_text(
        json.dumps(parts["review_candidates"], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "source_quality_report.json").write_text(
        json.dumps(src_report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_summary_md(summary, out_dir / "summary.md")
    _write_source_md(src_report, out_dir / "source_quality_report.md")
    _emit_sql_updates(classified, out_dir / "sql_updates_sugeridos.sql")

    print(out_dir.resolve())
    print(
        f"OK total={summary['total_analisado']} vis={summary['visiveis']} "
        f"review={summary['review']} hidden={summary['hidden']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
