#!/usr/bin/env python3
"""
Dry-run estratégico DARPA — Notícias / Programas / Opportunities (sem apply).

Gera audit_reports_news_research/darpa_strategic_dryrun/ com três rotas separadas:
- darpa_news → public.noticia (standardized)
- darpa_programs_research → public.pesquisa (standardized)
- darpa_opportunities_research → review_for_edital apenas (review_candidates.json)

Sem apply. Não insere opportunities em public.edital.
"""
from __future__ import annotations

import argparse
import importlib.util
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
    _http_get,
    _infer_darpa_opportunity_type,
    _load_json,
    crawl_source,
)

OUT_DIR = ROOT / "audit_reports_news_research" / "darpa_strategic_dryrun"
SOURCE_NEWS = "darpa_news"
SOURCE_PROGRAMS = "darpa_programs_research"
SOURCE_OPP = "darpa_opportunities_research"

FEEDS = {
    "news_rss": "https://www.darpa.mil/rss/news.xml",
    "opportunities_rss": "https://www.darpa.mil/rss/opportunities.xml",
}
HUBS = {
    "news": "https://www.darpa.mil/news",
    "programs": "https://www.darpa.mil/research/programs",
    "opportunities": "https://www.darpa.mil/work-with-us/opportunities",
}


def _load_route_module() -> Any:
    path = ROOT / "scripts" / "dry_run_news_research_loader.py"
    spec = importlib.util.spec_from_file_location("dry_run_news_research_loader", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _probe_urls() -> Dict[str, Any]:
    out: Dict[str, Any] = {"feeds": [], "hubs": [], "robots_txt": {}}
    for k, u in FEEDS.items():
        r = _http_get(u, timeout=45)
        out["feeds"].append(
            {
                "id": k,
                "url": u,
                "status": r.status_code if r else None,
                "ok": bool(r and r.status_code == 200),
                "bytes": len(r.text or "") if r else 0,
            }
        )
    for k, u in HUBS.items():
        r = _http_get(u, timeout=45)
        out["hubs"].append(
            {
                "id": k,
                "url": u,
                "status": r.status_code if r else None,
                "ok": bool(r and r.status_code == 200),
            }
        )
    rb = _http_get("https://www.darpa.mil/robots.txt", timeout=30)
    if rb:
        lines = (rb.text or "").splitlines()
        out["robots_txt"] = {
            "status": rb.status_code,
            "lines": len(lines),
            "allow_news": any("Allow" in ln and "/news" in ln for ln in lines),
            "sample": lines[:12],
        }
    return out


def _stats(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    val: Counter = Counter()
    for it in items:
        val[str(it.get("validacao_status") or "unknown")] += 1
    return {
        "total": len(items),
        "validacao_status_counts": dict(val),
        "total_valido": int(val.get("valido") or 0),
        "total_incompleto": int(val.get("incompleto") or 0) + int(val.get("acesso_limitado") or 0),
    }


def _eixos(items: List[Dict[str, Any]]) -> Dict[str, int]:
    c: Counter = Counter()
    for it in items:
        for e in it.get("eixo_estrategico") or (it.get("extras") or {}).get("eixo_estrategico") or []:
            if e:
                c[str(e)] += 1
    return dict(c.most_common(15))


def _examples(items: List[Dict[str, Any]], n: int = 5) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in items[:n]:
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        out.append(
            {
                "titulo": (it.get("titulo") or "")[:180],
                "link": (it.get("link") or "")[:800],
                "validacao_status": it.get("validacao_status"),
                "data_publicacao": it.get("data_publicacao"),
                "eixo_estrategico": it.get("eixo_estrategico") or ex.get("eixo_estrategico"),
            }
        )
    return out


def _to_review_entry(item: Dict[str, Any], source_id: str, motivo: str) -> Dict[str, Any]:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    tit = str(item.get("titulo") or "")
    return {
        "titulo": item.get("titulo"),
        "resumo": item.get("resumo") or item.get("descricao"),
        "link": item.get("link"),
        "fonte": "DARPA",
        "fonte_recurso": source_id,
        "data_publicacao": item.get("data_publicacao"),
        "data_publicacao_raw": item.get("data_publicacao"),
        "tipo_oportunidade": ex.get("tipo_oportunidade") or _infer_darpa_opportunity_type(tit),
        "prazo": ex.get("prazo") or ex.get("deadline"),
        "review_for_edital": True,
        "routing": "review_for_edital",
        "review_reason": motivo,
        "validacao_status": item.get("validacao_status"),
        "eixo_estrategico": item.get("eixo_estrategico") or ex.get("eixo_estrategico"),
        "extras": {**ex, "nao_auto_edital": True},
    }


def _split_news(
    std_news: List[Dict[str, Any]], route_mod: Any
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    kept: List[Dict[str, Any]] = []
    review: List[Dict[str, Any]] = []
    discard: List[Dict[str, Any]] = []
    for it in std_news:
        decision, motivo = route_mod.route_item(SOURCE_NEWS, it)
        if decision == "review_for_edital":
            review.append(_to_review_entry(it, SOURCE_NEWS, motivo))
        elif decision == "rejected_noise":
            discard.append(
                {
                    "titulo": it.get("titulo"),
                    "link": it.get("link"),
                    "motivo": motivo,
                    "routing": "descartado_ruido",
                }
            )
        elif decision == "pesquisa":
            review.append(_to_review_entry(it, SOURCE_NEWS, f"news_rota_pesquisa:{motivo}"))
        else:
            kept.append(it)
    return kept, review, discard


def _crawl_source(cfg: Dict[str, Any], sources: List[Dict[str, Any]], sid: str) -> Tuple[List, List, Dict]:
    src = next((s for s in sources if str(s.get("id")) == sid), None)
    if not src:
        raise SystemExit(f"[ERRO] Fonte {sid} não encontrada")
    src_run = {**src, **cfg.get(sid, {})}
    return crawl_source(src_run)


def run_dryrun(cfg_overrides: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    route_mod = _load_route_module()
    diag = _probe_urls()
    sources = _load_json(Path(CONFIG_DEFAULT), {}).get("sources") or []

    raw_news, std_news_all, meta_news = _crawl_source(cfg_overrides, sources, SOURCE_NEWS)
    news_kept, news_review_from_route, news_discard = _split_news(std_news_all, route_mod)

    raw_prog, std_prog, meta_prog = _crawl_source(cfg_overrides, sources, SOURCE_PROGRAMS)

    raw_opp, std_opp_all, meta_opp = _crawl_source(cfg_overrides, sources, SOURCE_OPP)
    opp_review: List[Dict[str, Any]] = []
    opp_discard: List[Dict[str, Any]] = []
    for it in std_opp_all:
        decision, motivo = route_mod.route_item(SOURCE_OPP, it)
        if decision == "review_for_edital":
            opp_review.append(_to_review_entry(it, SOURCE_OPP, motivo))
        elif decision == "rejected_noise":
            opp_discard.append({"titulo": it.get("titulo"), "link": it.get("link"), "motivo": motivo})
        else:
            opp_review.append(_to_review_entry(it, SOURCE_OPP, f"forcado_review:{decision}:{motivo}"))

    review_all = news_review_from_route + opp_review
    discard_all = news_discard + opp_discard

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(exist_ok=True)
    (OUT_DIR / "standardized").mkdir(exist_ok=True)

    (OUT_DIR / "raw" / f"{SOURCE_NEWS}_raw.json").write_text(
        json.dumps(raw_news, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "raw" / f"{SOURCE_PROGRAMS}_raw.json").write_text(
        json.dumps(raw_prog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "raw" / f"{SOURCE_OPP}_raw.json").write_text(
        json.dumps(raw_opp, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "standardized" / f"{SOURCE_NEWS}_standardized.json").write_text(
        json.dumps(news_kept, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "standardized" / f"{SOURCE_PROGRAMS}_standardized.json").write_text(
        json.dumps(std_prog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "review_candidates.json").write_text(
        json.dumps(review_all, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "descartados_ruido.json").write_text(
        json.dumps(discard_all, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    st_news = _stats(news_kept)
    st_prog = _stats(std_prog)
    errors_count = len((meta_news.get("errors") or [])) + len((meta_prog.get("errors") or [])) + len(
        (meta_opp.get("errors") or [])
    )

    subset_rec: Dict[str, Any] = {
        "recomendado": st_news["total_valido"] >= 5 and errors_count == 0,
        "noticias_validas": st_news["total_valido"],
        "pesquisas_validas": st_prog["total_valido"],
        "apply": False,
        "nota": (
            "Subset sugerido: notícias válidas do dry-run (≤12m) após roteamento; "
            "opportunities permanecem em review_for_edital/Radar; não apply automático."
        ),
    }

    summary = {
        "fonte": "darpa_strategic",
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run",
        "apply": False,
        "diagnostico": {
            **diag,
            "cms": "Drupal (darpa.mil)",
            "news": "RSS news.xml + hub /news",
            "programs": "sitemap.xml /research/programs/{slug} (hub SPA)",
            "opportunities": "RSS opportunities.xml (links canônicos por âncora)",
            "solicitations": "via opportunities RSS (RFI/BAA/título)",
        },
        "config": cfg_overrides,
        "totais_por_rota": {
            "darpa_news": {
                "raw": len(raw_news),
                "raw_meta": meta_news.get("raw_total"),
                "standardized_noticias": len(news_kept),
                **st_news,
            },
            "darpa_programs_research": {
                "raw": len(raw_prog),
                "raw_meta": meta_prog.get("raw_total"),
                "standardized_pesquisas": len(std_prog),
                **st_prog,
            },
            "darpa_opportunities_research": {
                "raw": len(raw_opp),
                "raw_meta": meta_opp.get("raw_total"),
                "review_opportunities": len(opp_review),
                "nao_standardized_edital": True,
            },
        },
        "agregado": {
            "review_total": len(review_all),
            "descartados_total": len(discard_all),
            "errors_count": errors_count,
        },
        "eixos": {
            "noticias": _eixos(news_kept),
            "programas": _eixos(std_prog),
        },
        "exemplos": {
            "noticias_mantidas": _examples(news_kept),
            "programas_mantidos": _examples(std_prog),
            "review": _examples(review_all),
            "descartados": discard_all[:5],
        },
        "recomendacao_apply": subset_rec,
        "paths": {
            "dir": str(OUT_DIR.relative_to(ROOT)).replace("\\", "/"),
            "news_std": f"standardized/{SOURCE_NEWS}_standardized.json",
            "programs_std": f"standardized/{SOURCE_PROGRAMS}_standardized.json",
            "review": "review_candidates.json",
        },
    }

    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# DARPA — dry-run estratégico (Notícias / Programas / Opportunities)",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Apply:** não",
        "",
        "## Diagnóstico",
        "",
        f"- **News RSS:** {diag['feeds'][0].get('ok')} ({FEEDS['news_rss']})",
        f"- **Opportunities RSS:** {diag['feeds'][1].get('ok')} ({FEEDS['opportunities_rss']})",
        f"- **Programas:** sitemap (~730 slugs); hub HTML SPA",
        "",
        "## Totais",
        "",
        "| Rota | Raw | Standardized | Válidos | Incompletos | Review |",
        "|------|----:|-------------:|--------:|------------:|-------:|",
        f"| Notícias | {summary['totais_por_rota']['darpa_news']['raw']} | "
        f"{summary['totais_por_rota']['darpa_news']['standardized_noticias']} | "
        f"{summary['totais_por_rota']['darpa_news']['total_valido']} | "
        f"{summary['totais_por_rota']['darpa_news']['total_incompleto']} | "
        f"{len(news_review_from_route)} |",
        f"| Programas | {summary['totais_por_rota']['darpa_programs_research']['raw']} | "
        f"{summary['totais_por_rota']['darpa_programs_research']['standardized_pesquisas']} | "
        f"{summary['totais_por_rota']['darpa_programs_research']['total_valido']} | "
        f"{summary['totais_por_rota']['darpa_programs_research']['total_incompleto']} | — |",
        f"| Opportunities | {summary['totais_por_rota']['darpa_opportunities_research']['raw']} | — | — | — | "
        f"{summary['totais_por_rota']['darpa_opportunities_research']['review_opportunities']} |",
        "",
        f"- **Descartados (ruído):** {summary['agregado']['descartados_total']}",
        f"- **errors_count:** {summary['agregado']['errors_count']}",
        "",
        "## Recomendação",
        "",
        f"- Subset notícias apply-ready: **{subset_rec['recomendado']}** "
        f"({subset_rec['noticias_validas']} válidas)",
        f"- Opportunities: **somente review_for_edital** (não `public.edital` automático)",
        "",
    ]
    (OUT_DIR / "summary.md").write_text("\n".join(md), encoding="utf-8")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--news-max", type=int, default=45)
    ap.add_argument("--programs-max", type=int, default=40)
    ap.add_argument("--opp-max", type=int, default=40)
    args = ap.parse_args()

    overrides = {
        SOURCE_NEWS: {"max_items": args.news_max, "time_window_months": 12, "page_enrich_max": 20},
        SOURCE_PROGRAMS: {"max_items": args.programs_max, "time_window_months": 24, "page_enrich_max": 25},
        SOURCE_OPP: {"max_items": args.opp_max, "time_window_months": 12, "page_enrich_max": 10},
    }
    summary = run_dryrun(overrides)
    print(json.dumps({"agregado": summary["agregado"], "totais": summary["totais_por_rota"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
