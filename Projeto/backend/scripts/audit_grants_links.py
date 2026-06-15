#!/usr/bin/env python3
"""
Auditoria de saúde de links Grants.gov (Backend 10.3A).

Somente leitura — não grava no banco. Validação estrutural (sem HTTP por padrão).

Uso:
  python scripts/audit_grants_links.py --from-db --limit 1000
  python scripts/audit_grants_links.py --input outputs/recrawl/grants_gov/grants_gov_recrawl.json
  python scripts/audit_grants_links.py --from-db --limit 1000 --check-http --http-limit 10
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import (  # noqa: E402
    filter_records_by_source,
    iter_records_from_db,
    load_records_from_json,
    write_json,
    write_md,
)
from grants_link_resolver import audit_grants_links, is_safe_grants_link  # noqa: E402

DEFAULT_OUT = ROOT / "outputs" / "grants_link_audit"
DEFAULT_RECRAWL = ROOT / "outputs" / "recrawl" / "grants_gov" / "grants_gov_recrawl.json"


def _load_records(
    *,
    from_db: bool,
    input_path: Optional[Path],
    limit: Optional[int],
) -> tuple[List[Dict[str, Any]], str]:
    if from_db:
        try:
            rows = list(iter_records_from_db(limit=limit))
            return filter_records_by_source(rows, "grants_gov"), "database"
        except Exception as exc:  # noqa: BLE001
            print(f"[audit_grants_links] DB indisponível ({exc}); usando fallback local.")
    path = input_path or DEFAULT_RECRAWL
    if path.exists():
        rows = load_records_from_json(path, limit=limit)
        return filter_records_by_source(rows, "grants_gov"), f"file:{path.name}"
    return [], "none"


def _maybe_check_http(candidates: List[Dict[str, Any]], http_limit: int) -> List[Dict[str, Any]]:
    """Checagem HTTP opcional, lote pequeno, somente links seguros."""
    out: List[Dict[str, Any]] = []
    try:
        from link_health import check_url
    except Exception as exc:  # noqa: BLE001
        print(f"[audit_grants_links] check-http indisponível: {exc}")
        return out
    checked = 0
    for cand in candidates:
        if checked >= http_limit:
            break
        url = cand.get("new_link") or cand.get("old_link")
        if not url or not is_safe_grants_link(url):
            continue
        res = check_url(url, campo="link")
        out.append(
            {
                "id_edital": cand.get("id_edital"),
                "url": url,
                "link_status": res.get("link_status"),
                "http_status": res.get("http_status"),
                "final_url": res.get("final_url"),
                "error_message": res.get("error_message"),
            }
        )
        checked += 1
    return out


def build_summary_md(audit: Dict[str, Any], origin: str, http_results: List[Dict[str, Any]]) -> str:
    s = audit["stats"]
    lines = [
        "# Grants.gov — auditoria de saúde de links (Backend 10.3A)",
        "",
        f"- **Origem dos dados:** {origin}",
        f"- **Total Grants.gov analisado:** {s['total_grants']}",
        "",
        "## Estado dos links",
        f"- **Já válidos (search-results-detail www):** {s['already_valid']}",
        f"- **page-not-found:** {s['page_not_found']}",
        f"- **Rotas antigas (view-opportunity / /web/grants):** {s['legacy_route']}",
        f"- **Inseguros / domínio externo:** {s['unsafe_or_foreign']}",
        "",
        "## Correção possível",
        f"- **Candidatos canonical_detail (têm ID numérico):** {s['canonical_candidates']}",
        f"- **Fallback por Funding Opportunity Number:** {s['search_fallback_candidates']}",
        f"- **Sem identificador (só search-grants):** {s['missing_identifiers']}",
        f"- **Total candidatos a update:** {s['candidates_to_update']}",
        "",
        "Padrão canônico: `https://www.grants.gov/search-results-detail/<opportunity_id>`",
        "Fallback de busca: `https://www.grants.gov/search-grants?keywords=<FON>`",
        "",
        "Nenhuma escrita no banco neste passo.",
    ]
    if http_results:
        lines += ["", "## Amostra de checagem HTTP (opcional)"]
        for r in http_results:
            lines.append(
                f"- `{r['url']}` → {r['link_status']} (HTTP {r['http_status']})"
            )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria de links Grants.gov (10.3A)")
    ap.add_argument("--from-db", action="store_true", help="Carrega registros do Supabase")
    ap.add_argument("--input", type=Path, default=None, help="JSON local de fallback")
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check-http", action="store_true", help="Checa alguns links via HTTP (opcional)")
    ap.add_argument("--http-limit", type=int, default=10, help="Máximo de links a checar via HTTP")
    args = ap.parse_args()

    records, origin = _load_records(
        from_db=args.from_db, input_path=args.input, limit=args.limit
    )
    audit = audit_grants_links(records)
    buckets = audit["buckets"]

    out = args.output
    write_json(out / "invalid_links.json", buckets["invalid_links"])
    write_json(out / "canonical_candidates.json", buckets["canonical_candidates"])
    write_json(out / "search_fallback_candidates.json", buckets["search_fallback_candidates"])
    write_json(out / "already_valid.json", buckets["already_valid"])
    write_json(out / "missing_identifiers.json", buckets["missing_identifiers"])

    http_results: List[Dict[str, Any]] = []
    if args.check_http:
        http_results = _maybe_check_http(
            buckets["canonical_candidates"] + buckets["search_fallback_candidates"],
            args.http_limit,
        )
        write_json(out / "http_check_sample.json", http_results)

    write_json(out / "audit_stats.json", audit["stats"])
    write_md(out / "summary.md", build_summary_md(audit, origin, http_results))

    s = audit["stats"]
    print(
        f"[audit_grants_links] total={s['total_grants']} "
        f"valid={s['already_valid']} pnf={s['page_not_found']} "
        f"legacy={s['legacy_route']} candidates={s['candidates_to_update']} -> {out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
