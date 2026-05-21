#!/usr/bin/env python3
"""
Auditoria de saúde dos links de editais (HTTP + heurísticas).

Não altera o banco. Gera relatórios JSON/MD e SQL comentado opcional.

Uso:
  python scripts/audit_edital_links.py --source grants --limit 100
  python scripts/audit_edital_links.py --source grants --from-json CORE/transformer/grants_gov_standardized.json
  python scripts/audit_edital_links.py --source grants --from-db --limit 50
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from link_health import (  # noqa: E402
    BROKEN_STATUSES,
    build_item_link_health,
    check_url,
    collect_link_fields,
    normalize_url,
    utc_now_iso,
)

SOURCE_REGISTRY: Dict[str, Dict[str, Any]] = {
    "grants": {
        "label": "Grants.gov",
        "json_default": CORE / "transformer" / "grants_gov_standardized.json",
        "json_globs": ["grants_gov_standardized.json"],
        "fonte_match": ("grants", "grants.gov", "grants_gov", "grants.gov"),
        "db_ilike": "%grant%",
    },
}


def _load_json_items(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return [raw]
    if not isinstance(raw, list):
        return []
    return [x for x in raw if isinstance(x, dict)]


def _resolve_items(
    source: str,
    *,
    from_json: Optional[Path],
    from_db: bool,
    limit: int,
) -> Tuple[List[Dict[str, Any]], str]:
    cfg = SOURCE_REGISTRY.get(source)
    if not cfg:
        raise SystemExit(f"Fonte desconhecida: {source}. Disponíveis: {', '.join(sorted(SOURCE_REGISTRY))}")

    if from_json:
        path = from_json if from_json.is_absolute() else (ROOT / from_json).resolve()
        if not path.is_file():
            raise SystemExit(f"JSON não encontrado: {path}")
        items = _load_json_items(path)
        return items[:limit] if limit > 0 else items, str(path)

    if from_db:
        items = _load_from_supabase(source, cfg, limit)
        return items, "supabase:edital"

    path = cfg["json_default"]
    if not path.is_file():
        raise SystemExit(f"Artefato padrão ausente: {path}. Use --from-json ou --from-db.")
    items = _load_json_items(path)
    return items[:limit] if limit > 0 else items, str(path)


def _load_from_supabase(source: str, cfg: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
    try:
        from db import supabase  # type: ignore
    except Exception as e:
        raise SystemExit(f"--from-db indisponível: {e}") from e

    patterns = list(cfg.get("fonte_match") or ())
    q = (
        supabase.table("edital")
        .select("id_edital,titulo,link,link_inscricao,pdf_url,fonte_recurso,extras")
        .or_("fonte_recurso.ilike.%grant%,link.ilike.%grants.gov%")
        .order("id_edital", desc=True)
    )
    res = q.limit(max(limit * 2, limit, 100)).execute()
    rows = res.data or []
    out: List[Dict[str, Any]] = []
    for r in rows:
        fr = str(r.get("fonte_recurso") or "").strip().lower()
        lk = str(r.get("link") or "").lower()
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        orig = str(ex.get("origem_portal") or ex.get("origem") or "").lower()
        if patterns and not (
            any(p in fr for p in patterns)
            or "grants.gov" in lk
            or any(p in orig for p in patterns)
        ):
            continue
        out.append(r)
        if limit > 0 and len(out) >= limit:
            break
    return out


def _item_identity(item: Dict[str, Any], idx: int) -> Dict[str, str]:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    return {
        "id_edital": str(item.get("id_edital") or item.get("id") or ""),
        "titulo": str(item.get("titulo") or "")[:300],
        "fonte_recurso": str(
            item.get("fonte_recurso") or item.get("fonte") or ex.get("fonte_recurso") or ""
        ),
        "row_index": str(idx),
    }


def _audit_items(
    items: List[Dict[str, Any]],
    *,
    sleep_s: float,
    timeout: float,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    session = requests.Session()
    checked: List[Dict[str, Any]] = []
    url_cache: Dict[str, Dict[str, Any]] = {}

    for idx, item in enumerate(items):
        ident = _item_identity(item, idx)
        fields = collect_link_fields(item)
        field_results: List[Dict[str, Any]] = []

        for campo, url in fields:
            cache_key = f"{url}\0{campo}"
            if cache_key in url_cache:
                base = dict(url_cache[cache_key])
            else:
                base = check_url(url, session=session, timeout=timeout, campo=campo)
                url_cache[cache_key] = base
                if sleep_s > 0:
                    time.sleep(sleep_s)

            row = {
                **ident,
                "campo": campo,
                "link": url,
                "final_url": base.get("final_url") or "",
                "http_status": base.get("http_status"),
                "link_status": base.get("link_status"),
                "checked_at": base.get("checked_at"),
                "error_message": base.get("error_message") or "",
                "recommendation": base.get("recommendation") or "",
                "essential_broken": base.get("essential_broken"),
                "semantic_error": base.get("semantic_error"),
            }
            field_results.append(row)
            checked.append(row)

        agg = build_item_link_health(item, field_results)
        ident["_link_health_preview"] = agg

    return checked, list(url_cache.values())


def _partition_reports(checked: List[Dict[str, Any]]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    broken: List[Dict[str, Any]] = []
    review: List[Dict[str, Any]] = []
    for row in checked:
        st = str(row.get("link_status") or "")
        rec = str(row.get("recommendation") or "")
        if st in BROKEN_STATUSES or st == "ssl_error" or rec == "marcar_link_quebrado":
            broken.append(row)
        elif st in ("suspicious", "forbidden_403", "missing") or rec in (
            "review_manual",
            "corrigir_url",
            "ocultar_card_do_front",
        ):
            review.append(row)
    return checked, broken, review


def _build_summary(
    source: str,
    origin: str,
    checked: List[Dict[str, Any]],
    items_count: int,
) -> Dict[str, Any]:
    status_c = Counter(r.get("link_status") for r in checked)
    rec_c = Counter(r.get("recommendation") for r in checked)
    campo_c = Counter(r.get("campo") for r in checked)
    items_with_broken = len(
        {
            (r.get("id_edital"), r.get("row_index"), r.get("titulo"))
            for r in checked
            if r.get("link_status") in BROKEN_STATUSES or r.get("link_status") == "ssl_error"
        }
    )
    return {
        "source": source,
        "origin": origin,
        "audited_at": utc_now_iso(),
        "items_count": items_count,
        "urls_checked": len(checked),
        "items_with_any_broken_essential": items_with_broken,
        "link_status_counts": dict(status_c),
        "recommendation_counts": dict(rec_c),
        "by_campo": dict(campo_c),
    }


def _write_summary_md(summary: Dict[str, Any], path: Path) -> None:
    lines = [
        f"# Link health — {summary.get('source')}",
        "",
        f"- **Origem:** `{summary.get('origin')}`",
        f"- **Auditado em:** {summary.get('audited_at')}",
        f"- **Itens:** {summary.get('items_count')}",
        f"- **URLs testadas:** {summary.get('urls_checked')}",
        f"- **Itens com link essencial quebrado:** {summary.get('items_with_any_broken_essential')}",
        "",
        "## Status HTTP",
        "",
    ]
    for k, v in sorted((summary.get("link_status_counts") or {}).items(), key=lambda kv: -kv[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Recomendações", ""])
    for k, v in sorted((summary.get("recommendation_counts") or {}).items(), key=lambda kv: -kv[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            "## Próximos passos",
            "",
            "1. Revisar `broken_links.json` e `review_candidates.json`.",
            "2. Aplicar manualmente trechos de `docs/sql/FIX_GRANTS_BROKEN_LINKS.sql` (extras.link_health).",
            "3. Re-rodar crawler grants se oppId estiver desatualizado.",
            "",
            "**Não** apagar linhas de edital automaticamente.",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def _emit_sql_template(
    source: str,
    checked: List[Dict[str, Any]],
    items: List[Dict[str, Any]],
    out_sql: Path,
) -> None:
    """Gera SQL comentado — não executar sem revisão."""
    lines = [
        "-- =============================================================================",
        "-- FIX_GRANTS_BROKEN_LINKS.sql",
        "-- =============================================================================",
        "-- REVISAR ANTES DE EXECUTAR. Não deleta linhas.",
        f"-- source={source} generated={utc_now_iso()}",
        "-- Aplica extras.link_health para itens broken_spa_not_found / outros BROKEN.",
        "",
    ]
    by_item: Dict[str, List[Dict[str, Any]]] = {}
    for r in checked:
        key = r.get("id_edital") or f"idx:{r.get('row_index')}"
        by_item.setdefault(str(key), []).append(r)

    emitted = 0
    for idx, item in enumerate(items):
        key = str(item.get("id_edital") or item.get("id") or f"idx:{idx}")
        rows = by_item.get(key) or by_item.get(f"idx:{idx}") or []
        if not rows:
            continue
        agg = build_item_link_health(item, rows)
        if str(agg.get("link_status") or "") not in BROKEN_STATUSES and not agg.get(
            "all_essential_broken"
        ):
            continue

        id_edital = item.get("id_edital") or item.get("id")
        titulo = str(item.get("titulo") or "")[:120].replace("'", "''")
        payload = json.dumps(agg, ensure_ascii=False).replace("'", "''")

        lines.append(f"-- id_edital={id_edital} | {titulo}")
        lines.append(f"-- link_status={agg.get('link_status')} http_status={agg.get('http_status')}")
        lines.append(f"-- final_url={agg.get('final_url')}")
        lines.append(f"-- error: {agg.get('error_message')}")

        if id_edital:
            ie = int(id_edital)
            lines.append(
                f"-- UPDATE public.edital SET extras = jsonb_set("
                f"COALESCE(extras, '{{}}'::jsonb), '{{link_health}}', '{payload}'::jsonb), "
                f"atualizado_em = now() WHERE id_edital = {ie};"
            )
            if agg.get("all_essential_broken"):
                lines.append(
                    f"-- Opcional (consenso manual): UPDATE public.edital SET ativo = false WHERE id_edital = {ie};"
                )
        else:
            link = normalize_url(item.get("link")).replace("'", "''")
            lines.append(
                f"-- UPDATE public.edital SET extras = jsonb_set("
                f"COALESCE(extras, '{{}}'::jsonb), '{{link_health}}', '{payload}'::jsonb), "
                f"atualizado_em = now() WHERE link = '{link}';"
            )
        lines.append("")
        emitted += 1

    if emitted == 0:
        lines.append("-- Nenhum item broken nesta execução.")

    out_sql.parent.mkdir(parents=True, exist_ok=True)
    out_sql.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria de links de editais.")
    ap.add_argument("--source", required=True, help="Chave da fonte (ex.: grants)")
    ap.add_argument("--limit", type=int, default=100, help="Máximo de editais (0 = todos)")
    ap.add_argument("--sleep", type=float, default=0.5, help="Pausa entre URLs novas")
    ap.add_argument("--timeout", type=float, default=20.0, help="Timeout HTTP por URL")
    ap.add_argument(
        "--output-dir",
        default="audit_reports_main_pipeline/link_health_grants",
        help="Pasta de saída",
    )
    ap.add_argument("--from-json", type=Path, default=None, help="JSON local (lista de editais)")
    ap.add_argument("--from-db", action="store_true", help="Ler edital do Supabase")
    args = ap.parse_args()

    source = args.source.strip().lower()
    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    items, origin = _resolve_items(
        source,
        from_json=args.from_json,
        from_db=args.from_db,
        limit=args.limit,
    )
    if not items:
        print("Nenhum item para auditar.", file=sys.stderr)
        return 1

    print(f"Auditando {len(items)} itens de {origin} …")
    checked, _cache = _audit_items(items, sleep_s=args.sleep, timeout=args.timeout)
    checked, broken, review = _partition_reports(checked)
    summary = _build_summary(source, origin, checked, len(items))

    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "checked_links.json").write_text(
        json.dumps(checked, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "broken_links.json").write_text(
        json.dumps(broken, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "review_candidates.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_summary_md(summary, out_dir / "summary.md")

    sql_path = ROOT / "docs" / "sql" / "FIX_GRANTS_BROKEN_LINKS.sql"
    if source == "grants":
        _emit_sql_template(source, checked, items, sql_path)

    print(out_dir.resolve())
    print(
        f"OK: {summary['urls_checked']} URLs | broken={len(broken)} | review={len(review)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
