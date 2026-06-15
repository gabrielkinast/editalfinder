#!/usr/bin/env python3
"""
Recoleta controlada Backend 4 — sem insert/update no banco.

Uso:
  python scripts/recrawl_sources_dry_run.py --source china --limit 50
  python scripts/recrawl_sources_dry_run.py --source araucaria --limit 50
  python scripts/recrawl_sources_dry_run.py --source grants --limit 50
  python scripts/recrawl_sources_dry_run.py --source all --limit 50 --from-db
  python scripts/recrawl_sources_dry_run.py --source china --no-network --offline-fixtures
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _recrawl_common import (  # noqa: E402
    DEFAULT_OUT,
    item_has_deadline,
    load_json_list,
    write_json,
    write_md,
)

# Garantia explícita: não importar loader para upsert neste script
_LOADER_FORBIDDEN = ("upsert_routed_item", "inserir_ou_atualizar_edital", "load_standardized_json")


def _assert_no_db_write() -> None:
    for name in _LOADER_FORBIDDEN:
        if name in sys.modules:
            raise RuntimeError(f"Backend 4 dry-run: módulo proibido carregado ({name})")


def _enrich_all(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    from opportunity_enricher import enrich_opportunity_record

    return [enrich_opportunity_record(it) for it in items]


def recrawl_china(
    limit: int,
    *,
    no_network: bool,
    offline_fixtures: bool,
) -> Tuple[Dict[str, Any], List[Dict], List[Dict], List[Dict]]:
    from source_deadline_parsers import enrich_china_crawler_item

    stats: Dict[str, Any] = {
        "listed": 0,
        "details_attempted": 0,
        "details_obtained": 0,
        "deadlines_extracted": 0,
        "block_403": 0,
        "block_timeout": 0,
        "block_empty": 0,
        "block_other": 0,
        "detail_fail_reasons": {},
    }
    raw: List[Dict[str, Any]] = []
    parsed: List[Dict[str, Any]] = []
    detail_log: List[Dict[str, Any]] = []

    cached = ROOT / "china_mofcom_tendering" / "outputs" / "china_mofcom_tendering_editais.json"
    fixture_html = (
        "<section><p>Bid closing date: 2026-09-30</p>"
        "<p>Tender closing date: 2026-10-01</p></section>"
    )

    if no_network or offline_fixtures:
        raw = load_json_list(cached, limit)
        stats["mode"] = "offline_json"
        stats["listed"] = len(raw)
    else:
        from asia_source_common import scrape_asia_html_portal

        items, _rej, crawl_meta = scrape_asia_html_portal(
            source_label="China International Tendering (MOFCOM)",
            country="china",
            listing_urls=[
                "https://www.chinabidding.com/en/",
                "http://www.chinabidding.com/",
            ],
            allowed_domains=["chinabidding.com", "chinabidding.mofcom.gov.cn"],
            extra_keywords=["tender", "bid", "招标", "采购"],
            max_items=limit,
            max_listing_pages=2,
            fetch_detail=True,
        )
        raw = [dict(x) for x in items[:limit]]
        stats["mode"] = "live_scrape"
        stats["listed"] = len(raw)
        stats["crawl_meta"] = crawl_meta

    safe_get_fn = None
    if not no_network:
        from asia_source_common import safe_get

        safe_get_fn = safe_get

    enriched: List[Dict[str, Any]] = []
    for item in raw[:limit]:
        link = item.get("link") or ""
        detail_html = ""
        detail_status = None
        fail_reason = None
        ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}

        if offline_fixtures:
            detail_html = fixture_html
            detail_status = 200
            stats["details_obtained"] += 1
        elif safe_get_fn and link:
            stats["details_attempted"] += 1
            try:
                resp = safe_get_fn(str(link), accept_language="en-US,en;q=0.9,zh-CN;q=0.7")
            except Exception as exc:
                resp = None
                fail_reason = f"exception:{exc.__class__.__name__}"
            if resp is not None and resp.status_code == 200 and (resp.text or "").strip():
                detail_html = (resp.text or "")[:12000]
                detail_status = 200
                stats["details_obtained"] += 1
            elif resp is not None:
                detail_status = int(resp.status_code)
                if detail_status == 403:
                    fail_reason = "403"
                    stats["block_403"] += 1
                elif detail_status >= 500:
                    fail_reason = f"http_{detail_status}"
                    stats["block_other"] += 1
                else:
                    fail_reason = f"http_{detail_status}"
                    stats["block_empty"] += 1
            else:
                fail_reason = fail_reason or "no_response"
                stats["block_timeout"] += 1
        elif ex.get("detail_fetch_failed") and not offline_fixtures:
            fail_reason = "cached_detail_fetch_failed"
            if ex.get("http_status_detail") == 403:
                stats["block_403"] += 1
            stats["block_empty"] += 1

        if fail_reason:
            stats["detail_fail_reasons"][fail_reason] = stats["detail_fail_reasons"].get(fail_reason, 0) + 1

        parsed_item = enrich_china_crawler_item(
            dict(item),
            detail_html=detail_html,
            listing_text=str(item.get("descricao") or ""),
        )
        has_dl, iso, _conf = item_has_deadline(parsed_item)
        if has_dl:
            stats["deadlines_extracted"] += 1

        parsed.append(
            {
                "link": link,
                "titulo": (item.get("titulo") or "")[:80],
                "detail_status": detail_status,
                "detail_html_len": len(detail_html),
                "fail_reason": fail_reason,
                "fim_inscricao": parsed_item.get("fim_inscricao"),
                "prazo_confidence": (parsed_item.get("extras") or {}).get("deadline_normalizer", {}).get("prazo_confidence"),
                "deadline_missing_in_source": (parsed_item.get("extras") or {}).get("deadline_missing_in_source"),
            }
        )
        detail_log.append(
            {"link": link, "detail_status": detail_status, "fail_reason": fail_reason, "deadline": iso}
        )
        enriched.append(_enrich_all([parsed_item])[0])

    stats["deadline_gain_estimate"] = sum(1 for e in enriched if item_has_deadline(e)[0])
    if stats["details_attempted"]:
        stats["block_rate"] = round(
            100
            * (stats["details_attempted"] - stats["details_obtained"])
            / stats["details_attempted"],
            1,
        )
    else:
        stats["block_rate"] = 0.0
    return stats, raw, parsed, enriched


def recrawl_araucaria(
    limit: int,
    *,
    no_network: bool,
) -> Tuple[Dict[str, Any], List[Dict], List[Dict], List[Dict]]:
    from source_deadline_parsers import enrich_araucaria_crawler_item

    stats: Dict[str, Any] = {
        "listed": 0,
        "with_pdf": 0,
        "pdf_accessible": 0,
        "pdf_text_extracted": 0,
        "deadlines_from_text": 0,
        "deadline_requires_pdf": 0,
    }
    raw: List[Dict[str, Any]] = []
    parsed: List[Dict[str, Any]] = []

    if no_network:
        raw = load_json_list(ROOT / "fappr" / "outputs" / "fappr_editais.json", limit)
        stats["mode"] = "offline_json"
    else:
        sys.path.insert(0, str(ROOT / "fappr"))
        from extrair_informacoes_fappr import FapprScraper

        scraper = FapprScraper()
        editais = scraper.extract_editais()[:limit]
        for ed in editais:
            raw.append(ed.to_dict() if hasattr(ed, "to_dict") else dict(ed))
        stats["mode"] = "live_scrape"

    stats["listed"] = len(raw)

    fetch_pdf = None
    extract_pdf = None
    if not no_network:
        try:
            from CORE.http_fetch import fetch_pdf_bytes
            from CORE.pdf_enrichment import extract_pdf_text_with_fallback

            fetch_pdf = fetch_pdf_bytes
            extract_pdf = extract_pdf_text_with_fallback
        except ImportError:
            pass

    pipeline_items: List[Dict[str, Any]] = []
    for item in raw[:limit]:
        ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
        link = str(item.get("link") or "")
        pdf_url = link if link.lower().endswith(".pdf") else None
        if not pdf_url and ex.get("anexos"):
            for a in ex["anexos"]:
                if isinstance(a, dict) and str(a.get("url", "")).lower().endswith(".pdf"):
                    pdf_url = a["url"]
                    break
        if pdf_url:
            stats["with_pdf"] += 1
        pdf_text = ex.get("pdf_texto_extraido") or ""
        pdf_ok = False
        if pdf_url and fetch_pdf and extract_pdf and not pdf_text:
            try:
                pdf_bytes = fetch_pdf(pdf_url)
                if pdf_bytes:
                    stats["pdf_accessible"] += 1
                    pdf_text = extract_pdf(pdf_bytes, max_pages=8) or ""
                    if pdf_text:
                        stats["pdf_text_extracted"] += 1
                        ex["pdf_texto_extraido"] = pdf_text[:8000]
                        pdf_ok = True
            except Exception:
                pass
        elif pdf_text:
            stats["pdf_text_extracted"] += 1
            pdf_ok = True

        item["extras"] = ex
        enriched_item = enrich_araucaria_crawler_item(item)
        has_dl, iso, conf = item_has_deadline(enriched_item)
        if has_dl:
            stats["deadlines_from_text"] += 1
        if (enriched_item.get("extras") or {}).get("deadline_requires_pdf"):
            stats["deadline_requires_pdf"] += 1

        parsed.append(
            {
                "titulo": (item.get("titulo") or "")[:80],
                "link": link[:120],
                "has_pdf": bool(pdf_url),
                "pdf_text_len": len(pdf_text or ""),
                "pdf_accessible": pdf_ok,
                "fim_inscricao": enriched_item.get("fim_inscricao"),
                "prazo_confidence": enriched_item.get("prazo_confidence"),
                "deadline_requires_pdf": (enriched_item.get("extras") or {}).get("deadline_requires_pdf"),
            }
        )
        pipeline_items.append(enriched_item)

    enriched = _enrich_all(pipeline_items)
    stats["deadline_gain_estimate"] = sum(1 for e in enriched if item_has_deadline(e)[0])
    return stats, raw, parsed, enriched


def recrawl_grants(
    limit: int,
    *,
    no_network: bool,
) -> Tuple[Dict[str, Any], List[Dict], List[Dict], List[Dict]]:
    from grants_gov.simpler_grants_common import collect_opportunities

    stats: Dict[str, Any] = {
        "total": 0,
        "with_close_date": 0,
        "without_close_date": 0,
        "forecasted": 0,
        "archived": 0,
        "posted_only_no_close": 0,
        "legacy_view_url": 0,
    }
    raw_hits: List[Dict[str, Any]] = []
    parsed: List[Dict[str, Any]] = []

    if no_network:
        raw_items = load_json_list(ROOT / "grants_gov" / "outputs" / "grants_gov_editais.json", limit)
        stats["mode"] = "offline_json"
        pipeline = raw_items
        for it in pipeline:
            ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
            raw_hits.append(
                {
                    "close_date": ex.get("close_date") or it.get("fim_inscricao"),
                    "posted_date": ex.get("posted_date") or it.get("data_publicacao"),
                    "opportunity_status": ex.get("opportunity_status"),
                    "link": it.get("link"),
                }
            )
    else:
        pipeline, meta = collect_opportunities(max_pages=3, max_items=limit, include_historic=True)
        stats["mode"] = "live_api"
        stats["api_meta"] = meta
        raw_hits = meta.get("raw_hits_sample") or []

    pipeline_list = pipeline
    stats["total"] = len(pipeline_list)

    final_items: List[Dict[str, Any]] = []
    for it in pipeline_list[:limit]:
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        st = str(ex.get("opportunity_status") or it.get("status_prazo") or "").lower()
        close = ex.get("close_date") or ex.get("grants_close_date") or it.get("fim_inscricao")
        posted = ex.get("posted_date") or it.get("data_publicacao")
        link = str(it.get("link") or "")

        if "view-opportunity" in link.lower():
            stats["legacy_view_url"] += 1
        if st == "forecasted":
            stats["forecasted"] += 1
        if st in ("closed", "archived"):
            stats["archived"] += 1
        if close:
            stats["with_close_date"] += 1
        else:
            stats["without_close_date"] += 1
            if posted and not close:
                stats["posted_only_no_close"] += 1

        parsed.append(
            {
                "titulo": (it.get("titulo") or "")[:70],
                "link": link[:100],
                "status": st,
                "close_date": close,
                "posted_date": posted,
                "legacy_url": "view-opportunity" in link.lower(),
            }
        )
        final_items.append(dict(it))

    enriched = _enrich_all(final_items)
    stats["deadlines_extracted"] = sum(1 for e in enriched if item_has_deadline(e)[0])
    stats["deadline_gain_estimate"] = stats["deadlines_extracted"]
    return stats, raw_hits, parsed, enriched


def build_china_summary(stats: Dict[str, Any], parsed: List[Dict]) -> str:
    lines = [
        "# China / MOFCOM — recoleta dry-run",
        "",
        f"- Modo: `{stats.get('mode')}`",
        f"- Listados: **{stats.get('listed', 0)}**",
        f"- Detalhes tentados: **{stats.get('details_attempted', 0)}**",
        f"- Detalhes obtidos: **{stats.get('details_obtained', 0)}**",
        f"- Deadlines extraídos: **{stats.get('deadlines_extracted', 0)}**",
        f"- Taxa bloqueio: **{stats.get('block_rate', 0)}%**",
        f"- 403: {stats.get('block_403', 0)} | timeout/sem resposta: {stats.get('block_timeout', 0)} | vazio/outro: {stats.get('block_empty', 0) + stats.get('block_other', 0)}",
        f"- Ganho estimado (com prazo): **{stats.get('deadline_gain_estimate', 0)}**",
        "",
        "## Motivos de falha no detail",
        "",
    ]
    for k, v in sorted((stats.get("detail_fail_reasons") or {}).items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Exemplos com deadline", ""])
    for p in parsed:
        if p.get("fim_inscricao"):
            lines.append(f"- {p.get('titulo')} → {p.get('fim_inscricao')} ({p.get('prazo_confidence')})")
            if len([x for x in parsed if x.get("fim_inscricao")]) >= 5:
                break
    lines.extend(["", "## Exemplos sem deadline", ""])
    n = 0
    for p in parsed:
        if not p.get("fim_inscricao"):
            lines.append(f"- {p.get('titulo')} | fail={p.get('fail_reason')} status={p.get('detail_status')}")
            n += 1
            if n >= 5:
                break
    if stats.get("block_rate", 0) > 50:
        lines.append("\n**Recomendação:** proxy/região ou fonte alternativa (API/RSS) — detail continua bloqueado.")
    return "\n".join(lines)


def build_araucaria_summary(stats: Dict[str, Any], parsed: List[Dict]) -> str:
    return "\n".join(
        [
            "# Fundação Araucária — recoleta dry-run",
            "",
            f"- Modo: `{stats.get('mode')}`",
            f"- Listados: **{stats.get('listed', 0)}**",
            f"- Com PDF: **{stats.get('with_pdf', 0)}**",
            f"- PDF acessível: **{stats.get('pdf_accessible', 0)}**",
            f"- PDF com texto: **{stats.get('pdf_text_extracted', 0)}**",
            f"- Prazos no texto: **{stats.get('deadlines_from_text', 0)}**",
            f"- Exigem PDF (flag): **{stats.get('deadline_requires_pdf', 0)}**",
            f"- Ganho estimado: **{stats.get('deadline_gain_estimate', 0)}**",
            "",
            "Sem OCR nesta fase; prazo depende de PDF textual ou HTML com datas explícitas.",
        ]
    )


def build_grants_summary(stats: Dict[str, Any], parsed: List[Dict]) -> str:
    return "\n".join(
        [
            "# Grants.gov / Simpler — recoleta dry-run",
            "",
            f"- Modo: `{stats.get('mode')}`",
            f"- Total: **{stats.get('total', 0)}**",
            f"- Com close_date: **{stats.get('with_close_date', 0)}**",
            f"- Sem close_date: **{stats.get('without_close_date', 0)}**",
            f"- Forecasted: **{stats.get('forecasted', 0)}**",
            f"- Archived/closed: **{stats.get('archived', 0)}**",
            f"- Posted sem close: **{stats.get('posted_only_no_close', 0)}**",
            f"- URL legado view-opportunity: **{stats.get('legacy_view_url', 0)}**",
            f"- Ganho estimado: **{stats.get('deadline_gain_estimate', 0)}**",
            "",
            "postedDate não é usado como deadline.",
        ]
    )


def run_source(
    source: str,
    limit: int,
    out_dir: Path,
    *,
    no_network: bool,
    offline_fixtures: bool,
) -> Dict[str, Any]:
    if source == "china":
        stats, raw, parsed, enriched = recrawl_china(
            limit, no_network=no_network, offline_fixtures=offline_fixtures
        )
        summary_fn = build_china_summary
    elif source == "araucaria":
        stats, raw, parsed, enriched = recrawl_araucaria(limit, no_network=no_network)
        summary_fn = build_araucaria_summary
    else:
        stats, raw, parsed, enriched = recrawl_grants(limit, no_network=no_network)
        summary_fn = build_grants_summary

    src_dir = out_dir / source
    write_json(src_dir / "raw_sample.json", raw)
    write_json(src_dir / "parsed_sample.json", parsed)
    write_json(src_dir / "enriched_sample.json", enriched)
    write_json(src_dir / "stats.json", stats)
    write_md(src_dir / "summary.md", summary_fn(stats, parsed))
    return stats


def main() -> int:
    _assert_no_db_write()
    ap = argparse.ArgumentParser(description="Recoleta Backend 4 (sem banco)")
    ap.add_argument("--source", choices=["china", "araucaria", "grants", "all"], default="all")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--from-db", action="store_true", help="Comparar com banco após recoleta")
    ap.add_argument("--no-network", action="store_true")
    ap.add_argument("--offline-fixtures", action="store_true", help="China: HTML fixture nos details")
    args = ap.parse_args()

    out = args.output
    (out / "summary").mkdir(parents=True, exist_ok=True)
    sources = ["china", "araucaria", "grants"] if args.source == "all" else [args.source]

    all_stats: Dict[str, Any] = {}
    for src in sources:
        print(f"[recrawl] {src} limit={args.limit} no_network={args.no_network}")
        all_stats[src] = run_source(
            src,
            args.limit,
            out,
            no_network=args.no_network,
            offline_fixtures=args.offline_fixtures,
        )

    write_json(out / "summary" / "recrawl_stats.json", all_stats)
    write_md(
        out / "summary" / "recrawl_overview.md",
        "# Backend 4 recoleta\n\n"
        + "\n".join(f"- **{k}**: ganho estimado {v.get('deadline_gain_estimate', 0)}" for k, v in all_stats.items()),
    )

    if args.from_db:
        from compare_recrawl_with_db import compare_source, build_comparison_md
        from _backend_audit_io import load_records

        db_records = load_records(from_db=True, limit=5000)
        import json

        comp: Dict[str, Any] = {}
        for src in sources:
            path = out / src / "enriched_sample.json"
            if path.is_file():
                enriched = json.loads(path.read_text(encoding="utf-8"))
                comp[src] = compare_source(enriched, db_records, src)
                write_json(out / src / "matched_diff.json", comp[src].get("matched_diff", []))
                write_json(out / src / "unmatched_new.json", comp[src].get("unmatched_new", []))
                write_json(out / src / "unmatched_db.json", comp[src].get("unmatched_db", []))
        write_md(out / "summary" / "comparison_summary.md", build_comparison_md(comp))
        write_json(out / "summary" / "comparison_report.json", comp)

    print(f"[recrawl_sources_dry_run] concluído -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
