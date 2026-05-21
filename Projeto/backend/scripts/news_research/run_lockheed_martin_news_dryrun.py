#!/usr/bin/env python3
"""
Dry-run Lockheed Martin Newsroom — Notícias Estratégicas internacional (filtro técnico forte).

Gera audit_reports_news_research/lockheed_martin_news_dryrun/ (padrão max_items=10)
ou diretório alternativo (ex.: lockheed_martin_news_dryrun_30).

Sem apply em Supabase.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.crawl_news_research_sources import (  # noqa: E402
    CONFIG_DEFAULT,
    _LM_FEED_PATH,
    _LM_NEWS_BASE,
    _LM_NEWS_HUB,
    _http_get,
    _load_json,
    _lockheed_martin_should_keep_raw,
    _parse_date,
    crawl_source,
)

SOURCE_ID = "lockheed_martin_news"
DEFAULT_OUT = ROOT / "audit_reports_news_research" / "lockheed_martin_news_dryrun"
BASELINE_OUT = ROOT / "audit_reports_news_research" / "lockheed_martin_news_dryrun"


def _lm_feed_inventory(time_window_months: int = 12) -> Dict[str, Any]:
    url = f"{_LM_NEWS_BASE}{_LM_FEED_PATH}"
    resp = _http_get(url, timeout=120)
    if not resp:
        return {"feed_fetch_ok": False, "errors": [{"error": "fetch_failed", "url": url}]}
    try:
        items = json.loads(resp.text or "[]")
    except Exception as e:
        return {"feed_fetch_ok": False, "errors": [{"error": "json_parse", "detail": str(e)}]}
    if not isinstance(items, list):
        items = []
    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * time_window_months)
    within = 0
    elegivel = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        dt = _parse_date(str(it.get("Date") or ""))
        if dt and dt >= min_dt:
            within += 1
        row = {
            "titulo": it.get("Title"),
            "descricao": it.get("Description"),
            "link": it.get("URL"),
            "data_publicacao_raw": it.get("Date"),
            "feed_categories": [],
        }
        if dt and dt >= min_dt:
            ok, _ = _lockheed_martin_should_keep_raw(row)
            if ok:
                elegivel += 1
    return {
        "feed_fetch_ok": True,
        "feed_json_url": url,
        "total_no_feed": len(items),
        "total_dentro_janela_meses": within,
        "total_elegivel_pos_filtros_basicos": elegivel,
        "total_elegivel_pos_filtros_pipeline": elegivel,
        "time_window_months": time_window_months,
    }


def _distribution(std_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    eixo: Counter = Counter()
    story: Counter = Counter()
    for it in std_items:
        for e in it.get("eixo_estrategico") or (it.get("extras") or {}).get("eixo_estrategico") or []:
            if e:
                eixo[str(e)] += 1
        st = (it.get("extras") or {}).get("lm_story_type") or it.get("categoria")
        if st:
            story[str(st)[:80]] += 1
    return {
        "eixo_estrategico": dict(eixo.most_common(15)),
        "story_type": dict(story.most_common(10)),
    }


def _run_summary_stats(std_items: List[Dict[str, Any]], meta: Dict[str, Any]) -> Dict[str, Any]:
    val_counts: Dict[str, int] = {}
    for it in std_items:
        v = str(it.get("validacao_status") or "unknown")
        val_counts[v] = val_counts.get(v, 0) + 1
    errors = meta.get("errors") or []
    return {
        "validacao_status_counts": val_counts,
        "total_valido": int(val_counts.get("valido") or 0),
        "total_incompleto": int(val_counts.get("incompleto") or 0)
        + int(val_counts.get("acesso_limitado") or 0),
        "errors_count": len(errors),
    }


def run_dryrun(out_dir: Path, max_items: int, time_window_months: int = 12) -> Dict[str, Any]:
    cfg = _load_json(Path(CONFIG_DEFAULT), {})
    sources = cfg.get("sources") if isinstance(cfg, dict) else []
    src = next((s for s in sources if str(s.get("id")) == SOURCE_ID), None)
    if not src:
        raise SystemExit(f"[ERRO] Fonte {SOURCE_ID} não encontrada em {CONFIG_DEFAULT}")

    src_run = dict(src)
    src_run["max_items"] = max_items
    src_run["time_window_months"] = time_window_months

    feed_inv = _lm_feed_inventory(time_window_months)
    raw_items, std_items, meta = crawl_source(src_run)
    review = meta.get("review_candidates") or []

    std_dir = out_dir / "standardized"
    raw_dir = out_dir / "raw"
    std_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    (raw_dir / f"{SOURCE_ID}_raw.json").write_text(
        json.dumps(raw_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (std_dir / f"{SOURCE_ID}_standardized.json").write_text(
        json.dumps(std_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (std_dir / "exemplos.json").write_text(
        json.dumps(std_items[:5], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / f"{SOURCE_ID}_crawl_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "review_candidates.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    stats = _run_summary_stats(std_items, meta)
    distrib = _distribution(std_items)
    fs = meta.get("theme_filter_stats") or {}

    warnings = []
    if meta.get("errors"):
        warnings.append({"tipo": "fetch_errors", "detalhe": meta["errors"]})
    if not std_items:
        warnings.append({"tipo": "nenhum_item_standardized"})
    if feed_inv.get("total_elegivel_pos_filtros_pipeline", 0) > max_items:
        warnings.append(
            {
                "tipo": "cap_max_items",
                "elegivel_pipeline": feed_inv.get("total_elegivel_pos_filtros_pipeline"),
                "max_items": max_items,
            }
        )

    summary = {
        "fonte": SOURCE_ID,
        "nome_exibicao": src.get("name"),
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run",
        "apply": False,
        "output_dir": out_dir.name,
        "diagnostico": {
            "url_base": _LM_NEWS_BASE,
            "hub_html": f"{_LM_NEWS_BASE}{_LM_NEWS_HUB}",
            "feed_json": f"{_LM_NEWS_BASE}{_LM_FEED_PATH}",
            "rss": "não encontrado; feed JSON AEM",
            "robots_txt": "Allow /en-us; Disallow parcial news-releases/in-the-news",
            "cms": "Adobe AEM + news.lockheedmartin.com",
            "listagem": "JSON newsfeed.json; hub SPA Algolia",
            "rotas_institucionais": "/capabilities/, /suppliers/ → rejeitado",
            "copyright": "Description do feed; sem corpo integral",
        },
        "config": {
            "max_items": max_items,
            "time_window_months": time_window_months,
            "page_enrich_max": src_run.get("page_enrich_max"),
        },
        "feed_inventory": feed_inv,
        "filtros": {
            "rejected_require_any": fs.get("rejected_require_any_keyword"),
            "rejected_exclude": fs.get("rejected_exclude_keyword"),
            "rejected_lm_routing": fs.get("rejected_lm_routing"),
            "lm_sent_review": fs.get("lm_sent_review"),
        },
        "totais": {
            "raw_apos_filtros": meta.get("raw_total"),
            "standardized": len(std_items),
            "within_window_12m": meta.get("within_window_total"),
            "review_candidates": len(review),
            "sem_data": meta.get("without_date_total"),
            "page_enrich_fetches": meta.get("page_enrich_fetch_total"),
            "total_valido": stats["total_valido"],
            "total_incompleto": stats["total_incompleto"],
            "errors_count": stats["errors_count"],
        },
        "validacao_status_counts": stats["validacao_status_counts"],
        "distribuicao": distrib,
        "warnings": warnings,
        "errors": meta.get("errors") or [],
        "observacao": (
            "Fonte corporativa ampla; aplicar lote controlado (subset ≤20). "
            "Filtro forte de relevância técnica ativo."
        ),
        "paths": {
            "standardized": str((std_dir / f"{SOURCE_ID}_standardized.json").resolve()),
            "raw": str((raw_dir / f"{SOURCE_ID}_raw.json").resolve()),
            "review_candidates": str((out_dir / "review_candidates.json").resolve()),
        },
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        f"# Lockheed Martin Newsroom — dry-run (max_items={max_items})",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Diretório:** `{out_dir.name}`",
        "",
        "## Inventário feed",
        "",
        f"- **Total feed:** {feed_inv.get('total_no_feed')}",
        f"- **Dentro 12m:** {feed_inv.get('total_dentro_janela_meses')}",
        f"- **Elegíveis (pipeline básico):** {feed_inv.get('total_elegivel_pos_filtros_pipeline')}",
        "",
        "## Resultados",
        "",
        f"- **Processados:** {summary['totais']['standardized']}",
        f"- **Válidos:** {summary['totais']['total_valido']}",
        f"- **Review:** {summary['totais']['review_candidates']}",
        f"- **errors_count:** {summary['totais']['errors_count']}",
        "",
    ]
    for k, v in stats["validacao_status_counts"].items():
        md.append(f"- `{k}`: **{v}**")
    if distrib.get("eixo_estrategico"):
        md.extend(["", "### Eixos", ""])
        for k, v in sorted(distrib["eixo_estrategico"].items(), key=lambda x: (-x[1], x[0])):
            md.append(f"- `{k}`: {v}")
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    return summary


def _compare_runs(
    baseline_dir: Path, expanded_dir: Path, feed_inv: Dict[str, Any]
) -> Dict[str, Any]:
    def _load_summary(d: Path) -> Dict[str, Any]:
        p = d / "summary.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}

    b, e = _load_summary(baseline_dir), _load_summary(expanded_dir)

    def _metrics(s: Dict[str, Any]) -> Dict[str, Any]:
        t = s.get("totais") or {}
        return {
            "max_items_config": (s.get("config") or {}).get("max_items"),
            "total_processado": t.get("standardized"),
            "total_valido": t.get("total_valido"),
            "total_incompleto": t.get("total_incompleto"),
            "review_candidates": t.get("review_candidates"),
            "errors_count": t.get("errors_count"),
            "validacao_status_counts": s.get("validacao_status_counts") or {},
            "distribuicao": s.get("distribuicao") or {},
        }

    bm, em = _metrics(b), _metrics(e)
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "feed": {
            "total_no_feed": feed_inv.get("total_no_feed"),
            "total_dentro_12_meses": feed_inv.get("total_dentro_janela_meses"),
            "total_elegivel_pipeline": feed_inv.get("total_elegivel_pos_filtros_pipeline"),
        },
        "dryrun_original": {"diretorio": baseline_dir.name, **bm},
        "dryrun_ampliado": {"diretorio": expanded_dir.name, **em},
        "delta": {
            "processado": (em.get("total_processado") or 0) - (bm.get("total_processado") or 0),
            "valido": (em.get("total_valido") or 0) - (bm.get("total_valido") or 0),
        },
        "nota": "Fonte corporativa; cap max_items; apply não executado.",
    }


def _write_comparison_md(comp: Dict[str, Any], out_dir: Path) -> None:
    f = comp["feed"]
    o, a = comp["dryrun_original"], comp["dryrun_ampliado"]
    lines = [
        "# Lockheed Martin Newsroom — comparação dry-run 10 vs 30",
        "",
        f"| Total feed | {f.get('total_no_feed')} |",
        f"| Dentro 12m (bruto) | {f.get('total_dentro_12_meses')} |",
        f"| Elegíveis pipeline | {f.get('total_elegivel_pipeline')} |",
        "",
        "| Métrica | dry-run 10 | dry-run 30 | Δ |",
        "|---------|----------:|----------:|--:|",
        f"| Processado | {o.get('total_processado')} | {a.get('total_processado')} | {comp['delta']['processado']:+d} |",
        f"| Válido | {o.get('total_valido')} | {a.get('total_valido')} | {comp['delta']['valido']:+d} |",
        f"| Review | {o.get('review_candidates')} | {a.get('review_candidates')} | — |",
        f"| errors_count | {o.get('errors_count')} | {a.get('errors_count')} | — |",
        "",
    ]
    dist = a.get("distribuicao") or {}
    if dist.get("eixo_estrategico"):
        lines.extend(["### Eixos (ampliado)", ""])
        for k, v in sorted(dist["eixo_estrategico"].items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"- `{k}`: {v}")
    lines.append("")
    (out_dir / "comparacao_dryrun_10_vs_30.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default="lockheed_martin_news_dryrun")
    ap.add_argument("--max-items", type=int, default=10)
    ap.add_argument("--time-window-months", type=int, default=12)
    ap.add_argument("--compare-baseline", default="lockheed_martin_news_dryrun")
    ap.add_argument("--no-compare", action="store_true")
    args = ap.parse_args()

    out_arg = Path(args.output_dir)
    if out_arg.is_absolute():
        out_dir = out_arg
    elif "audit_reports_news_research" in out_arg.parts:
        out_dir = ROOT / out_arg
    else:
        out_dir = ROOT / "audit_reports_news_research" / out_arg.name

    summary = run_dryrun(out_dir, max_items=args.max_items, time_window_months=args.time_window_months)

    if not args.no_compare:
        baseline = ROOT / "audit_reports_news_research" / Path(args.compare_baseline).name
        comp = _compare_runs(baseline, out_dir, summary.get("feed_inventory") or {})
        (out_dir / "comparacao_dryrun_10_vs_30.json").write_text(
            json.dumps(comp, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        _write_comparison_md(comp, out_dir)

    print(json.dumps({"totais": summary["totais"], "feed": summary.get("feed_inventory")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
