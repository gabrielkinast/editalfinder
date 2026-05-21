#!/usr/bin/env python3
"""
Dry-run War.gov / U.S. DoD News — Notícias Estratégicas internacionais (filtro técnico forte).

Gera audit_reports_news_research/war_gov_news_dryrun/.
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
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.crawl_news_research_sources import (  # noqa: E402
    CONFIG_DEFAULT,
    _WAR_GOV_RSS_NEWS_STORIES,
    _http_get,
    _load_json,
    _parse_date,
    _war_gov_url_allowed,
    crawl_source,
)

SOURCE_ID = "war_gov_news"
DEFAULT_OUT = ROOT / "audit_reports_news_research" / "war_gov_news_dryrun"


def _rss_probe() -> Dict[str, Any]:
    url = _WAR_GOV_RSS_NEWS_STORIES
    resp = _http_get(url, timeout=90)
    if not resp:
        return {"ok": False, "url": url, "error": "fetch_failed"}
    body = resp.text or ""
    sections: Counter = Counter()
    if body.strip().startswith("<?xml"):
        import re
        from xml.etree import ElementTree as ET

        root = ET.fromstring(resp.content)
        for it in root.findall(".//item"):
            link_el = it.find("link")
            lk = (link_el.text or "").strip() if link_el is not None else ""
            ok, sec = _war_gov_url_allowed(lk)
            if ok:
                sections[sec] += 1
            else:
                sections["rejected"] += 1
    return {
        "ok": True,
        "url": url,
        "final_url": resp.url,
        "status": resp.status_code,
        "bytes": len(body),
        "sections_in_feed": dict(sections),
    }


def _hub_probe() -> Dict[str, Any]:
    url = "https://www.war.gov/news/"
    resp = _http_get(url, timeout=45)
    return {
        "url": url,
        "status": resp.status_code if resp else None,
        "ok": bool(resp and resp.status_code == 200),
        "note": "Hub HTML opcional; listagem principal via RSS.",
    }


def _within_window_count(items: List[Dict[str, Any]], months: int) -> int:
    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * months)
    n = 0
    for r in items:
        dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date(r.get("data_publicacao"))
        if dt and dt >= min_dt:
            n += 1
    return n


def _distribution(std_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    eixo: Counter = Counter()
    rel: Counter = Counter()
    sec: Counter = Counter()
    for it in std_items:
        ex = it.get("extras") or {}
        for e in it.get("eixo_estrategico") or ex.get("eixo_estrategico") or []:
            if e:
                eixo[str(e)] += 1
        rv = ex.get("relevancia_war_gov")
        if rv:
            rel[str(rv)] += 1
        s = ex.get("war_gov_section")
        if s:
            sec[str(s)] += 1
    return {
        "eixo_estrategico": dict(eixo.most_common(15)),
        "relevancia_war_gov": dict(rel.most_common(5)),
        "war_gov_section": dict(sec.most_common(5)),
    }


def _examples(items: List[Dict[str, Any]], n: int = 5) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in items[:n]:
        ex = it.get("extras") or {}
        out.append(
            {
                "titulo": (it.get("titulo") or "")[:200],
                "link": (it.get("link") or "")[:800],
                "relevancia_war_gov": ex.get("relevancia_war_gov"),
                "war_gov_section": ex.get("war_gov_section"),
                "motivos_relevancia": (ex.get("motivos_relevancia") or [])[:6],
                "motivos_descarte": (ex.get("motivos_descarte") or [])[:6],
            }
        )
    return out


def _apply_readiness(std_n: int, review_n: int, valid_n: int, meta: Dict[str, Any]) -> str:
    if valid_n >= 8:
        return "excelente_para_subset_top_10_20_e_apply_controlado"
    if valid_n >= 4:
        return "boa_com_subset_top_10_recomendado"
    if std_n + review_n >= 5:
        return "moderada_revisar_filtros_antes_apply"
    return "fraca_aumentar_janela_ou_ajustar_filtros"


def run_dryrun(out_dir: Path, max_items: int, time_window_months: int = 12) -> Dict[str, Any]:
    cfg = _load_json(Path(CONFIG_DEFAULT), {})
    sources = cfg.get("sources") if isinstance(cfg, dict) else []
    src = next((s for s in sources if str(s.get("id")) == SOURCE_ID), None)
    if not src:
        raise SystemExit(f"[ERRO] Fonte {SOURCE_ID} não encontrada em {CONFIG_DEFAULT}")

    src_run = dict(src)
    src_run["max_items"] = max_items
    src_run["time_window_months"] = time_window_months

    rss_probe = _rss_probe()
    hub_probe = _hub_probe()

    raw_items, std_items, meta = crawl_source(src_run)
    pre_rel = meta.get("war_gov_pre_relevance_raw") or []
    review = meta.get("review_candidates") or []
    discard = meta.get("descartados_ruido") or []

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "raw").mkdir(exist_ok=True)
    (out_dir / "standardized").mkdir(exist_ok=True)

    raw_payload = pre_rel if pre_rel else raw_items
    (out_dir / "raw" / f"{SOURCE_ID}_raw.json").write_text(
        json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "standardized" / f"{SOURCE_ID}_standardized.json").write_text(
        json.dumps(std_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "review_candidates.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "descartados_ruido.json").write_text(
        json.dumps(discard, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / f"{SOURCE_ID}_crawl_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    val_counts: Dict[str, int] = {}
    for it in std_items:
        v = str(it.get("validacao_status") or "unknown")
        val_counts[v] = val_counts.get(v, 0) + 1
    valid_n = int(val_counts.get("valido") or 0)
    distrib = _distribution(std_items)
    fs = meta.get("theme_filter_stats") or {}

    summary = {
        "fonte": SOURCE_ID,
        "nome_exibicao": "U.S. Department of Defense / War.gov",
        "fonte_recurso": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run",
        "apply": False,
        "output_dir": out_dir.name,
        "diagnostico": {
            "hub": hub_probe,
            "rss_news_stories": rss_probe,
            "robots_txt": "https://www.war.gov/robots.txt",
            "detalhe_html": "Artigo pode retornar 403; resumo via RSS description",
            "fonte_oficial": "U.S. Department of Defense / War.gov (não jornalismo independente)",
        },
        "config": {
            "max_items": max_items,
            "time_window_months": time_window_months,
            "seed_urls": src_run.get("seed_urls"),
        },
        "totais": {
            "total_raw": len(pre_rel) if pre_rel else len(raw_payload),
            "dentro_12_meses": _within_window_count(pre_rel or raw_payload, time_window_months),
            "standardized": len(std_items),
            "review": len(review),
            "descartados_ruido": len(discard),
            "raw_apos_relevancia": meta.get("raw_total"),
            "within_window_standardized": sum(1 for r in raw_items if r.get("within_window")),
            "total_valido": valid_n,
            "total_incompleto": int(val_counts.get("incompleto") or 0)
            + int(val_counts.get("acesso_limitado") or 0),
            "errors_count": len(meta.get("errors") or []),
        },
        "filtros": {
            "war_gov_sent_discard": fs.get("war_gov_sent_discard"),
            "war_gov_sent_review": fs.get("war_gov_sent_review"),
            "rejected_war_gov_path": fs.get("rejected_war_gov_path"),
        },
        "validacao_status_counts": val_counts,
        "distribuicao": distrib,
        "avaliacao_fonte": _apply_readiness(len(std_items), len(review), valid_n, meta),
        "exemplos": {
            "mantidos": _examples(std_items, 5),
            "descartados": _examples(discard, 5),
            "review": _examples(review, 5),
        },
        "errors": meta.get("errors") or [],
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        f"# War.gov News — dry-run (max_items={max_items}, janela {time_window_months}m)",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Fonte:** U.S. Department of Defense / War.gov (`war_gov_news`)",
        f"- **Avaliação:** {summary['avaliacao_fonte']}",
        "",
        "## Diagnóstico",
        "",
        f"- **RSS News Stories:** {rss_probe.get('ok')} — `{rss_probe.get('url', '')}`",
        f"- **Hub HTML:** HTTP {hub_probe.get('status')} (listagem via RSS)",
        f"- **Seções no feed:** {rss_probe.get('sections_in_feed', {})}",
        "",
        "## Totais",
        "",
        "| Métrica | Valor |",
        "|---------|------:|",
        f"| Total raw (pré-relevância) | {summary['totais']['total_raw']} |",
        f"| Dentro {time_window_months}m | {summary['totais']['dentro_12_meses']} |",
        f"| Standardized | {summary['totais']['standardized']} |",
        f"| Review | {summary['totais']['review']} |",
        f"| Descartados | {summary['totais']['descartados_ruido']} |",
        f"| Válidos | {summary['totais']['total_valido']} |",
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
        md.append(f"- {ex.get('titulo', '')[:80]} — rel={ex.get('relevancia_war_gov')}")
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-items", type=int, default=30)
    ap.add_argument("--time-window-months", type=int, default=12)
    ap.add_argument("--output-dir", type=str, default=str(DEFAULT_OUT))
    args = ap.parse_args()
    summary = run_dryrun(Path(args.output_dir), args.max_items, args.time_window_months)
    print(json.dumps(summary["totais"], ensure_ascii=False, indent=2))
    print("avaliacao:", summary["avaliacao_fonte"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
