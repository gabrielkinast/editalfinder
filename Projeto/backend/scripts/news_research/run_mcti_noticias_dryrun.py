#!/usr/bin/env python3
"""
Dry-run MCTI Notícias — pipeline Notícias/Pesquisas com filtro forte de relevância CT&I.

Gera audit_reports_news_research/mcti_noticias_dryrun/ (padrão max_items=30, janela 12m).
Sem apply em Supabase. Não altera MCTI Fomento (Radar).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.crawl_news_research_sources import (  # noqa: E402
    CONFIG_DEFAULT,
    _MCTI_NOTICIAS_BASE,
    _http_get,
    _load_json,
    _mcti_date_from_url,
    _normalize_mcti_noticia_link,
    _parse_date,
    crawl_source,
)

SOURCE_ID = "mcti_noticias"
DEFAULT_OUT = ROOT / "audit_reports_news_research" / "mcti_noticias_dryrun"

FEEDS_404 = [
    f"{_MCTI_NOTICIAS_BASE}/rss.xml",
    f"{_MCTI_NOTICIAS_BASE}/atom.xml",
    f"{_MCTI_NOTICIAS_BASE}/feed/RSS",
    f"{_MCTI_NOTICIAS_BASE}/feed/Atom",
]


def _probe_feeds() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for url in FEEDS_404:
        resp = _http_get(url, timeout=25)
        out.append(
            {
                "url": url,
                "status": resp.status_code if resp else None,
                "ok": bool(resp and resp.status_code == 200),
            }
        )
    return out


def _listing_inventory() -> Dict[str, Any]:
    hub = _MCTI_NOTICIAS_BASE
    resp = _http_get(hub, timeout=60)
    if not resp:
        return {"hub_fetch_ok": False, "errors": [{"error": "fetch_failed", "url": hub}]}
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(resp.text or "", "html.parser")
    links: List[str] = []
    for a in soup.find_all("a", href=True):
        lk = _normalize_mcti_noticia_link(a["href"], hub)
        if lk and lk not in links:
            links.append(lk)
    return {
        "hub_fetch_ok": True,
        "hub_url": hub,
        "article_links_on_hub": len(links),
        "sample_links": links[:8],
    }


def _within_window_count(items: List[Dict[str, Any]], months: int) -> int:
    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * months)
    n = 0
    for r in items:
        dt = (
            _parse_date(r.get("data_publicacao_raw"))
            or _parse_date(r.get("data_publicacao"))
            or _mcti_date_from_url(str(r.get("link") or ""))
        )
        if dt and dt >= min_dt:
            n += 1
    return n


def _distribution(std_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    eixo: Counter = Counter()
    rel: Counter = Counter()
    for it in std_items:
        ex = it.get("extras") or {}
        for e in it.get("eixo_estrategico") or ex.get("eixo_estrategico") or []:
            if e:
                eixo[str(e)] += 1
        rv = ex.get("relevancia_mcti")
        if rv:
            rel[str(rv)] += 1
    return {
        "eixo_estrategico": dict(eixo.most_common(15)),
        "relevancia_mcti": dict(rel.most_common(5)),
    }


def _examples(items: List[Dict[str, Any]], n: int = 5) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in items[:n]:
        out.append(
            {
                "titulo": (it.get("titulo") or "")[:200],
                "link": (it.get("link") or "")[:800],
                "relevancia_mcti": it.get("relevancia_mcti") or (it.get("extras") or {}).get("relevancia_mcti"),
                "motivos_relevancia": (it.get("motivos_relevancia") or (it.get("extras") or {}).get("motivos_relevancia") or [])[:6],
                "motivos_descarte": (it.get("motivos_descarte") or (it.get("extras") or {}).get("motivos_descarte") or [])[:6],
            }
        )
    return out


def _run_summary_stats(std_items: List[Dict[str, Any]], meta: Dict[str, Any]) -> Dict[str, Any]:
    val_counts: Dict[str, int] = {}
    for it in std_items:
        v = str(it.get("validacao_status") or "unknown")
        val_counts[v] = val_counts.get(v, 0) + 1
    return {
        "validacao_status_counts": val_counts,
        "total_valido": int(val_counts.get("valido") or 0),
        "total_incompleto": int(val_counts.get("incompleto") or 0)
        + int(val_counts.get("acesso_limitado") or 0),
        "errors_count": len(meta.get("errors") or []),
    }


def run_dryrun(
    out_dir: Path,
    max_items: int,
    time_window_months: int = 12,
    page_enrich_max: Optional[int] = None,
) -> Dict[str, Any]:
    cfg = _load_json(Path(CONFIG_DEFAULT), {})
    sources = cfg.get("sources") if isinstance(cfg, dict) else []
    src = next((s for s in sources if str(s.get("id")) == SOURCE_ID), None)
    if not src:
        raise SystemExit(f"[ERRO] Fonte {SOURCE_ID} não encontrada em {CONFIG_DEFAULT}")

    src_run = dict(src)
    src_run["max_items"] = max_items
    src_run["time_window_months"] = time_window_months
    if page_enrich_max is not None:
        src_run["page_enrich_max"] = page_enrich_max

    feed_probe = _probe_feeds()
    listing_inv = _listing_inventory()

    raw_items, std_items, meta = crawl_source(src_run)
    pre_rel = meta.get("mcti_pre_relevance_raw") or []
    review = meta.get("review_candidates") or []
    discard = meta.get("descartados_ruido") or []

    std_dir = out_dir / "standardized"
    raw_dir = out_dir / "raw"
    std_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_payload = pre_rel if pre_rel else raw_items
    (raw_dir / f"{SOURCE_ID}_raw.json").write_text(
        json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (std_dir / f"{SOURCE_ID}_standardized.json").write_text(
        json.dumps(std_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / f"{SOURCE_ID}_crawl_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "review_candidates.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "descartados_ruido.json").write_text(
        json.dumps(discard, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    stats = _run_summary_stats(std_items, meta)
    distrib = _distribution(std_items)
    fs = meta.get("theme_filter_stats") or {}
    within_pre = _within_window_count(pre_rel, time_window_months)
    within_std = sum(1 for r in raw_items if r.get("within_window"))

    summary = {
        "fonte": SOURCE_ID,
        "nome_exibicao": src.get("name"),
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run",
        "apply": False,
        "output_dir": out_dir.name,
        "diagnostico": {
            "url_base": _MCTI_NOTICIAS_BASE,
            "cms": "gov.br / Plone",
            "rss_atom": "404 — usar listagem HTML",
            "feeds_testados": feed_probe,
            "listagem": listing_inv,
            "detalhe": "og:description, #content-core, .documentPublished, og:image",
            "robots_txt": "gov.br/robots.txt — acesso pode retornar 403 em alguns clientes; crawler HTTP padrão",
            "separacao_fomento": "MCTI Fomento permanece Radar/Editais (não alterado)",
        },
        "config": {
            "max_items": max_items,
            "time_window_months": time_window_months,
            "page_enrich_max": src_run.get("page_enrich_max"),
            "seed_urls": src_run.get("seed_urls"),
        },
        "totais": {
            "total_raw": len(pre_rel) if pre_rel else meta.get("mcti_pre_relevance_total") or len(raw_payload),
            "dentro_12_meses": within_pre,
            "standardized": len(std_items),
            "review": len(review),
            "descartados_ruido": len(discard),
            "raw_apos_relevancia": meta.get("raw_total"),
            "within_window_standardized": within_std,
            "sem_data": meta.get("without_date_total"),
            "page_enrich_fetches": meta.get("page_enrich_fetch_total"),
            "total_valido": stats["total_valido"],
            "total_incompleto": stats["total_incompleto"],
            "errors_count": stats["errors_count"],
        },
        "filtros": {
            "mcti_sent_discard": fs.get("mcti_sent_discard"),
            "mcti_sent_review": fs.get("mcti_sent_review"),
            "rejected_mcti_non_path": fs.get("rejected_mcti_non_path"),
            "discarded_post_enrich": meta.get("discarded_post_enrich_total"),
        },
        "validacao_status_counts": stats["validacao_status_counts"],
        "distribuicao": distrib,
        "exemplos": {
            "mantidos": _examples(std_items, 5),
            "descartados": _examples(discard, 5),
            "review": _examples(review, 5),
        },
        "warnings": [],
        "errors": meta.get("errors") or [],
        "paths": {
            "standardized": str((std_dir / f"{SOURCE_ID}_standardized.json").resolve()),
            "raw": str((raw_dir / f"{SOURCE_ID}_raw.json").resolve()),
            "review_candidates": str((out_dir / "review_candidates.json").resolve()),
            "descartados_ruido": str((out_dir / "descartados_ruido.json").resolve()),
        },
    }
    if meta.get("errors"):
        summary["warnings"].append({"tipo": "fetch_errors", "detalhe": meta["errors"]})
    if not std_items and not review:
        summary["warnings"].append({"tipo": "nenhum_item_standardized_ou_review"})

    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        f"# MCTI Notícias — dry-run (max_items={max_items}, janela {time_window_months}m)",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Diretório:** `{out_dir.name}`",
        f"- **page_enrich_max:** {summary['config'].get('page_enrich_max')}",
        "",
        "## Diagnóstico",
        "",
        f"- **CMS:** gov.br/Plone",
        f"- **RSS/Atom:** indisponível (404 nos feeds testados)",
        f"- **Links no hub:** {listing_inv.get('article_links_on_hub', '—')}",
        "",
        "## Totais",
        "",
        f"| Métrica | Valor |",
        f"|---------|------:|",
        f"| Total raw (pré-relevância) | {summary['totais']['total_raw']} |",
        f"| Dentro 12 meses (raw) | {summary['totais']['dentro_12_meses']} |",
        f"| Standardized (mantidos) | {summary['totais']['standardized']} |",
        f"| Review | {summary['totais']['review']} |",
        f"| Descartados (ruído) | {summary['totais']['descartados_ruido']} |",
        f"| Válidos | {summary['totais']['total_valido']} |",
        f"| Incompletos | {summary['totais']['total_incompleto']} |",
        "",
        "## Eixos (mantidos)",
        "",
    ]
    for k, v in sorted((distrib.get("eixo_estrategico") or {}).items(), key=lambda x: (-x[1], x[0])):
        md.append(f"- `{k}`: {v}")
    md.extend(["", "## Exemplos mantidos", ""])
    for ex in summary["exemplos"]["mantidos"]:
        md.append(f"- [{ex.get('titulo', '')[:80]}]({ex.get('link', '')})")
    md.extend(["", "## Exemplos descartados", ""])
    for ex in summary["exemplos"]["descartados"]:
        md.append(f"- {ex.get('titulo', '')[:80]} — {ex.get('motivos_descarte', [])[:3]}")
    md.extend(["", "## Exemplos review", ""])
    for ex in summary["exemplos"]["review"]:
        md.append(f"- {ex.get('titulo', '')[:80]} — rel={ex.get('relevancia_mcti')}")
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="mcti_noticias_dryrun")
    ap.add_argument("--max-items", type=int, default=30)
    ap.add_argument("--time-window-months", type=int, default=12)
    args = ap.parse_args()

    out_arg = Path(args.output_dir)
    if out_arg.is_absolute():
        out_dir = out_arg
    elif "audit_reports_news_research" in out_arg.parts:
        out_dir = ROOT / out_arg
    else:
        out_dir = ROOT / "audit_reports_news_research" / out_arg.name

    summary = run_dryrun(out_dir, max_items=args.max_items, time_window_months=args.time_window_months)
    print(json.dumps({"totais": summary["totais"], "distribuicao": summary.get("distribuicao")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
