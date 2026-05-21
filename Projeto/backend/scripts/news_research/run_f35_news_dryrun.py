#!/usr/bin/env python3
"""
Dry-run piloto F-35 News & Features — Notícias Estratégicas internacional.

Gera artefatos em audit_reports_news_research/f35_news_dryrun/ (padrão max_items=10)
ou diretório alternativo (ex.: f35_news_dryrun_30 com --max-items 30).

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
    _F35_FEED_PATH,
    _F35_HUB_FRAG,
    _F35_NEWS_BASE,
    _f35_public_link,
    _f35_should_keep_raw,
    _http_get,
    _load_json,
    _parse_date,
    crawl_source,
)

SOURCE_ID = "f35_news"
DEFAULT_OUT = ROOT / "audit_reports_news_research" / "f35_news_dryrun"
BASELINE_OUT = ROOT / "audit_reports_news_research" / "f35_news_dryrun"


def _f35_feed_inventory(time_window_months: int = 12) -> Dict[str, Any]:
    """Contagens no feed JSON sem cap de max_items (só leitura)."""
    url = f"{_F35_NEWS_BASE}{_F35_FEED_PATH}"
    resp = _http_get(url, timeout=60)
    if not resp:
        return {"feed_fetch_ok": False, "errors": [{"error": "fetch_failed", "url": url}]}
    try:
        data = json.loads(resp.text or "[]")
    except Exception as e:
        return {"feed_fetch_ok": False, "errors": [{"error": "json_parse", "detail": str(e)}]}

    items = data if isinstance(data, list) else []
    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * time_window_months)
    total_feed = len(items)
    within_window = 0
    news_features_path = 0
    eligible_pipeline = 0
    content_type_counts: Counter = Counter()
    for it in items:
        if not isinstance(it, dict):
            continue
        pub = str(it.get("Date") or "").strip()
        dt = _parse_date(pub)
        if dt and dt >= min_dt:
            within_window += 1
        href = str(it.get("URL") or "").strip()
        link = _f35_public_link(href).lower()
        if _F35_HUB_FRAG in link and not link.rstrip("/").endswith("news-and-features.html"):
            news_features_path += 1
        ctt = it.get("Content Type Tags") or {}
        if isinstance(ctt, dict):
            for v in ctt.values():
                if isinstance(v, str) and v.strip():
                    content_type_counts[v.strip()] += 1
        if dt and dt >= min_dt and _F35_HUB_FRAG in link:
            row = {
                "titulo": str(it.get("Title") or "")[:320],
                "descricao": str(it.get("Description") or ""),
                "link": _f35_public_link(href),
                "data_publicacao_raw": pub,
                "feed_categories": [],
            }
            ok, _ = _f35_should_keep_raw(row)
            if ok:
                eligible_pipeline += 1

    return {
        "feed_fetch_ok": True,
        "feed_json_url": url,
        "total_no_feed": total_feed,
        "total_dentro_janela_meses": within_window,
        "total_com_path_news_features": news_features_path,
        "total_elegivel_pos_filtros_pipeline": eligible_pipeline,
        "time_window_months": time_window_months,
        "content_type_tags_no_feed": dict(content_type_counts.most_common(20)),
    }


def _distribution(std_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    cat: Counter = Counter()
    eixo: Counter = Counter()
    content_type: Counter = Counter()
    general_tags: Counter = Counter()
    for it in std_items:
        c = it.get("categoria") or (it.get("extras") or {}).get("categoria")
        if c:
            cat[str(c)] += 1
        for e in it.get("eixo_estrategico") or (it.get("extras") or {}).get("eixo_estrategico") or []:
            if e:
                eixo[str(e)] += 1
        fcs = [str(t).strip() for t in ((it.get("extras") or {}).get("feed_categories") or []) if t]
        for ct in ("News", "Feature", "3rd Party Article"):
            if ct in fcs:
                content_type[ct] += 1
                break
        for t in fcs:
            if t not in ("News", "Feature", "3rd Party Article") and len(t) > 2:
                general_tags[t] += 1
    return {
        "categoria_principal": dict(cat.most_common(15)),
        "content_type_tag": dict(content_type.most_common(10)),
        "general_tags_top": dict(general_tags.most_common(20)),
        "eixo_estrategico": dict(eixo.most_common(15)),
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

    feed_inv = _f35_feed_inventory(time_window_months)
    raw_items, std_items, meta = crawl_source(src_run)

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

    stats = _run_summary_stats(std_items, meta)
    distrib = _distribution(std_items)

    warnings = []
    if meta.get("errors"):
        warnings.append({"tipo": "fetch_errors", "detalhe": meta["errors"]})
    if meta.get("without_date_total"):
        warnings.append({"tipo": "sem_data", "count": meta["without_date_total"]})
    if not std_items:
        warnings.append({"tipo": "nenhum_item_standardized", "detalhe": "verificar feed JSON ou filtros"})
    if feed_inv.get("total_elegivel_pos_filtros_pipeline", 0) > max_items:
        warnings.append(
            {
                "tipo": "cap_max_items",
                "elegivel_no_feed": feed_inv.get("total_elegivel_pos_filtros_pipeline"),
                "max_items": max_items,
            }
        )

    summary = {
        "fonte": SOURCE_ID,
        "nome_exibicao": src.get("name"),
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run",
        "apply": False,
        "output_dir": str(out_dir.name),
        "diagnostico": {
            "url_base": _F35_NEWS_BASE,
            "hub_html": f"{_F35_NEWS_BASE}/f35/news-and-features.html",
            "feed_json": f"{_F35_NEWS_BASE}{_F35_FEED_PATH}",
            "rss": "não disponível (listagem via JSON AEM + Algolia no browser)",
            "robots_txt": "https://www.f35.com/robots.txt — Allow paths regionais; sem Disallow em /f35/",
            "cms": "Adobe AEM (Lockheed Martin F-35)",
            "listagem": "JSON estático f35feed.json (data-path no hub); hub renderizado com Algolia InstantSearch",
            "data_publicacao": "campo Date (RFC822, ex. Wed, 13 May 2026 … MDT)",
            "imagem": "Thumbnail Image no feed (absolutizada para f35.com)",
            "autor": "F-35 / Lockheed Martin (metadado feed)",
            "copyright": "Apenas Description do feed; enrich opcional og:description; sem corpo integral",
        },
        "config": {
            "max_items": max_items,
            "time_window_months": time_window_months,
            "page_enrich_max": src_run.get("page_enrich_max"),
        },
        "feed_inventory": feed_inv,
        "totais": {
            "raw_apos_filtros": meta.get("raw_total"),
            "standardized": len(std_items),
            "within_window_12m": meta.get("within_window_total"),
            "sem_data": meta.get("without_date_total"),
            "page_enrich_fetches": meta.get("page_enrich_fetch_total"),
            "discarded_post_enrich": meta.get("discarded_post_enrich_total", 0),
            "total_valido": stats["total_valido"],
            "total_incompleto": stats["total_incompleto"],
            "errors_count": stats["errors_count"],
        },
        "validacao_status_counts": stats["validacao_status_counts"],
        "distribuicao": distrib,
        "warnings": warnings,
        "errors": meta.get("errors") or [],
        "paths": {
            "standardized": str((std_dir / f"{SOURCE_ID}_standardized.json").resolve()),
            "exemplos": str((std_dir / "exemplos.json").resolve()),
            "raw": str((raw_dir / f"{SOURCE_ID}_raw.json").resolve()),
            "crawl_meta": str((out_dir / f"{SOURCE_ID}_crawl_meta.json").resolve()),
        },
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        f"# F-35 News & Features — dry-run (max_items={max_items})",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Modo:** dry-run (sem apply)",
        f"- **Diretório:** `{out_dir.name}`",
        f"- **Fonte:** `{SOURCE_ID}` — {summary['nome_exibicao']}",
        "",
        "## Inventário do feed",
        "",
        f"- **Total no feed JSON:** {feed_inv.get('total_no_feed', '—')}",
        f"- **Dentro de {time_window_months} meses:** {feed_inv.get('total_dentro_janela_meses', '—')}",
        f"- **Elegível (filtros pipeline, sem cap):** {feed_inv.get('total_elegivel_pos_filtros_pipeline', '—')}",
        "",
        "## Resultados processados",
        "",
        f"- **Processados (cap max_items):** {summary['totais']['standardized']}",
        f"- **Na janela {time_window_months}m:** {summary['totais']['within_window_12m']}",
        f"- **Válidos:** {summary['totais']['total_valido']}",
        f"- **Incompletos / acesso_limitado:** {summary['totais']['total_incompleto']}",
        f"- **errors_count:** {summary['totais']['errors_count']}",
        "",
        "### Validação",
        "",
    ]
    for k, v in stats["validacao_status_counts"].items():
        md.append(f"- `{k}`: **{v}**")
    if distrib.get("eixo_estrategico"):
        md.extend(["", "### Eixos estratégicos", ""])
        for k, v in sorted(distrib["eixo_estrategico"].items(), key=lambda x: (-x[1], x[0])):
            md.append(f"- `{k}`: {v}")
    if distrib.get("content_type_tag"):
        md.extend(["", "### Content type (feed)", ""])
        for k, v in sorted(distrib["content_type_tag"].items(), key=lambda x: (-x[1], x[0])):
            md.append(f"- `{k}`: {v}")
    if distrib.get("general_tags_top"):
        md.extend(["", "### Tags gerais (top)", ""])
        for k, v in list(sorted(distrib["general_tags_top"].items(), key=lambda x: (-x[1], x[0])))[:12]:
            md.append(f"- `{k}`: {v}")
    if warnings:
        md.extend(["", "## Warnings", ""])
        for w in warnings:
            md.append(f"- {w}")
    md.extend(
        [
            "",
            "## Artefatos",
            "",
            f"- `{summary['paths']['standardized']}`",
            "",
        ]
    )
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    return summary


def _compare_runs(
    baseline_dir: Path, expanded_dir: Path, feed_inv: Dict[str, Any]
) -> Dict[str, Any]:
    def _load_summary(d: Path) -> Dict[str, Any]:
        p = d / "summary.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}

    b = _load_summary(baseline_dir)
    e = _load_summary(expanded_dir)

    def _metrics(s: Dict[str, Any]) -> Dict[str, Any]:
        t = s.get("totais") or {}
        return {
            "max_items_config": (s.get("config") or {}).get("max_items"),
            "total_processado": t.get("standardized"),
            "within_window": t.get("within_window_12m"),
            "total_valido": t.get("total_valido") or (s.get("validacao_status_counts") or {}).get("valido"),
            "total_incompleto": t.get("total_incompleto"),
            "errors_count": t.get("errors_count", len(s.get("errors") or [])),
            "validacao_status_counts": s.get("validacao_status_counts") or {},
            "distribuicao": s.get("distribuicao") or {},
        }

    bm, em = _metrics(b), _metrics(e)
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "feed": {
            "total_no_feed": feed_inv.get("total_no_feed"),
            "total_dentro_12_meses": feed_inv.get("total_dentro_janela_meses"),
            "total_elegivel_pipeline_sem_cap": feed_inv.get("total_elegivel_pos_filtros_pipeline"),
            "content_type_tags_no_feed": feed_inv.get("content_type_tags_no_feed"),
        },
        "dryrun_original": {
            "diretorio": baseline_dir.name,
            **bm,
        },
        "dryrun_ampliado": {
            "diretorio": expanded_dir.name,
            **em,
        },
        "delta": {
            "processado": (em.get("total_processado") or 0) - (bm.get("total_processado") or 0),
            "valido": (em.get("total_valido") or 0) - (bm.get("total_valido") or 0),
            "incompleto": (em.get("total_incompleto") or 0) - (bm.get("total_incompleto") or 0),
        },
        "nota": (
            "O feed tem mais itens elegíveis que max_items; dry-run original cap=10, "
            "ampliado cap=30. Apply não executado."
        ),
    }


def _write_comparison_md(comp: Dict[str, Any], out_dir: Path) -> None:
    f = comp["feed"]
    o = comp["dryrun_original"]
    a = comp["dryrun_ampliado"]
    lines = [
        "# F-35 — comparação dry-run 10 vs 30",
        "",
        "## Feed (inventário)",
        "",
        f"| Métrica | Valor |",
        f"|---------|------:|",
        f"| Total no feed JSON | {f.get('total_no_feed')} |",
        f"| Dentro de 12 meses | {f.get('total_dentro_12_meses')} |",
        f"| Elegível (pipeline, sem cap) | {f.get('total_elegivel_pipeline_sem_cap')} |",
        "",
        "## Execuções",
        "",
        "| Métrica | `f35_news_dryrun` (10) | `f35_news_dryrun_30` (30) | Δ |",
        "|---------|------------------------:|--------------------------:|--:|",
        f"| Processado | {o.get('total_processado')} | {a.get('total_processado')} | {comp['delta']['processado']:+d} |",
        f"| Válido | {o.get('total_valido')} | {a.get('total_valido')} | {comp['delta']['valido']:+d} |",
        f"| Incompleto | {o.get('total_incompleto')} | {a.get('total_incompleto')} | {comp['delta']['incompleto']:+d} |",
        f"| errors_count | {o.get('errors_count')} | {a.get('errors_count')} | — |",
        "",
        "### Validação (ampliado)",
        "",
    ]
    for k, v in (a.get("validacao_status_counts") or {}).items():
        lines.append(f"- `{k}`: **{v}**")
    dist_a = a.get("distribuicao") or {}
    if dist_a.get("content_type_tag"):
        lines.extend(["", "### Content type — ampliado (30 itens)", ""])
        for k, v in sorted(dist_a["content_type_tag"].items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"- `{k}`: {v}")
    lines.extend(["", "### Eixos (ampliado)", ""])
    for k, v in sorted(dist_a.get("eixo_estrategico", {}).items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    (out_dir / "comparacao_dryrun_10_vs_30.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run F-35 News (sem apply).")
    ap.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUT.relative_to(ROOT)),
        help="Subpasta em audit_reports_news_research/ (ex.: f35_news_dryrun_30)",
    )
    ap.add_argument("--max-items", type=int, default=10)
    ap.add_argument("--time-window-months", type=int, default=12)
    ap.add_argument(
        "--compare-baseline",
        default=str(BASELINE_OUT.relative_to(ROOT)),
        help="Diretório do dry-run original para comparacao (se existir summary.json)",
    )
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

    print(
        json.dumps(
            {
                "summary": summary["totais"],
                "feed": summary.get("feed_inventory"),
                "validacao": summary["validacao_status_counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(summary["paths"]["standardized"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
