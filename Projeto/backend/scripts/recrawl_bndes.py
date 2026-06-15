#!/usr/bin/env python3
"""
Recrawl controlado BNDES — detail HTML + PDF discovery (Backend 10.2D).

Sem apply; sem scraping agressivo.

Uso:
  python scripts/recrawl_bndes.py --limit 200 --output outputs/recrawl/bndes/bndes_recrawl.json
  python scripts/recrawl_bndes.py --limit 50 --no-network
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "CORE"))
sys.path.insert(0, str(ROOT / "scripts"))

from _backend_audit_io import write_json, write_md  # noqa: E402
from bndes_detail_recrawl import (  # noqa: E402
    BNDES_RECrawl_VERSION,
    enrich_bndes_recrawl_item,
    stats_for_bndes_recrawl_items,
)

DEFAULT_OUT = ROOT / "outputs" / "recrawl" / "bndes" / "bndes_recrawl.json"


def recrawl_bndes(
    limit: int,
    *,
    no_network: bool = False,
    http_timeout: int = 15,
    max_detail_fetches: int = 30,
    max_pdf_fetches: int = 10,
) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if no_network:
        fixture = ROOT / "tests" / "fixtures" / "bndes_recrawl_sample.json"
        if not fixture.exists():
            fixture = ROOT / "bndes" / "outputs" / "bndes_editais.json"
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        items = raw if isinstance(raw, list) else raw.get("items", [])
        enriched = [
            enrich_bndes_recrawl_item(it, fetch_detail=False, fetch_pdf=False)
            for it in items[:limit]
        ]
        return enriched, {"mode": "offline_fixture", "fixture": str(fixture), "limit": limit}

    source = ROOT / "bndes" / "outputs" / "bndes_editais.json"
    if not source.exists():
        source = ROOT / "CORE" / "transformer" / "bndes_standardized.json"
    raw = json.loads(source.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("items", [])

    enriched: List[Dict[str, Any]] = []
    detail_fetches = 0
    pdf_fetches = 0
    for it in items[:limit]:
        do_detail = detail_fetches < max_detail_fetches
        do_pdf = pdf_fetches < max_pdf_fetches
        out = enrich_bndes_recrawl_item(
            it,
            fetch_detail=do_detail,
            fetch_pdf=do_pdf,
            http_timeout=http_timeout,
        )
        ex = out.get("extras") if isinstance(out.get("extras"), dict) else {}
        if ex.get("bndes_detail_fetch"):
            detail_fetches += 1
        if ex.get("bndes_pdf_extract"):
            pdf_fetches += 1
        enriched.append(out)

    return enriched, {
        "mode": "live_enriched",
        "source": str(source),
        "limit": limit,
        "detail_fetches": detail_fetches,
        "pdf_fetches": pdf_fetches,
    }


def build_summary_md(stats: Dict[str, Any], meta: Dict[str, Any]) -> str:
    lines = [
        "# BNDES recrawl (Backend 10.2D)",
        "",
        f"- **Modo:** {meta.get('mode')}",
        f"- **Total:** {stats.get('total', 0)}",
        f"- **Detalhe HTML coletado:** {stats.get('detail_html_collected', 0)}",
        f"- **PDFs descobertos:** {stats.get('pdfs_discovered', 0)}",
        f"- **PDFs extraídos:** {stats.get('pdfs_extracted', 0)}",
        f"- **PDFs falhos:** {stats.get('pdfs_failed', 0)}",
        f"- **Linhas permanentes:** {stats.get('permanent_lines', 0)}",
        f"- **Notícias (data rejeitada):** {stats.get('news_rejected', 0)}",
        f"- **Chamadas com prazo:** {stats.get('calls_with_deadline', 0)}",
        f"- **Sem deadline estruturado:** {stats.get('without_structured_deadline', 0)}",
        f"- **Candidatos PDF/detail:** {stats.get('pdf_detail_candidates', 0)}",
        "",
        "Nenhuma escrita no banco neste passo.",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Recrawl BNDES (10.2D)")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--http-timeout", type=int, default=15)
    ap.add_argument("--max-detail-fetches", type=int, default=30)
    ap.add_argument("--max-pdf-fetches", type=int, default=10)
    args = ap.parse_args()

    items, meta = recrawl_bndes(
        args.limit,
        no_network=args.no_network,
        http_timeout=args.http_timeout,
        max_detail_fetches=args.max_detail_fetches,
        max_pdf_fetches=args.max_pdf_fetches,
    )
    stats = stats_for_bndes_recrawl_items(items)

    payload = {"version": BNDES_RECrawl_VERSION, "stats": stats, "meta": meta, "items": items}
    write_json(args.output, payload)
    summary_path = args.output.parent / "summary.md"
    write_md(summary_path, build_summary_md(stats, meta))
    print(
        f"[recrawl_bndes] total={stats['total']} "
        f"calls_deadline={stats['calls_with_deadline']} "
        f"pdf_candidates={stats['pdf_detail_candidates']} -> {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
