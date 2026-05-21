#!/usr/bin/env python3
"""
Dry-run estratégico AFRL — News + Diretorias RA/RJ/RR + Mission Highlights (sem apply).

Rotas:
- afrl_news → public.noticia
- afrl_air_warfare_research / afrl_space_warfare_research / afrl_technology_transition → public.pesquisa (1 institucional cada)
- afrl_mission_highlights → public.noticia (highlights com data)
- review_candidates.json → relevância + review_for_edital (oportunidades)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.crawl_news_research_sources import (  # noqa: E402
    CONFIG_DEFAULT,
    _AFRL_BASE,
    _AFRL_NEWS_HUB,
    _http_get,
    _load_json,
    _parse_date,
    crawl_source,
)

OUT_DIR = ROOT / "audit_reports_news_research" / "afrl_strategic_dryrun"

SOURCE_NEWS = "afrl_news"
SOURCE_HIGHLIGHTS = "afrl_mission_highlights"
DIRECTORATE_SOURCES = (
    "afrl_air_warfare_research",
    "afrl_space_warfare_research",
    "afrl_technology_transition",
)
ALL_SOURCES = (SOURCE_NEWS,) + DIRECTORATE_SOURCES + (SOURCE_HIGHLIGHTS,)


def _probe(url: str) -> Dict[str, Any]:
    r = _http_get(url, timeout=45)
    return {
        "url": url,
        "status": r.status_code if r else None,
        "ok": bool(r and r.status_code == 200),
        "bytes": len(r.text or "") if r else 0,
    }


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


def _examples(items: List[Dict[str, Any]], n: int = 4) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in items[:n]:
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        out.append(
            {
                "titulo": (it.get("titulo") or "")[:160],
                "link": (it.get("link") or "")[:800],
                "validacao_status": it.get("validacao_status"),
                "data_publicacao": it.get("data_publicacao"),
                "fonte_recurso": it.get("fonte_recurso"),
                "eixo_estrategico": it.get("eixo_estrategico") or ex.get("eixo_estrategico"),
                "diretoria_origem": ex.get("diretoria_origem"),
                "highlights_total": ex.get("highlights_total"),
                "possivel_edital": ex.get("possivel_edital"),
            }
        )
    return out


def _crawl_source(cfg: Dict[str, Any], sources: List[Dict[str, Any]], sid: str) -> Tuple[List, List, Dict]:
    src = next((s for s in sources if str(s.get("id")) == sid), None)
    if not src:
        raise SystemExit(f"[ERRO] Fonte {sid} não encontrada")
    src_run = {**src, **cfg.get(sid, {})}
    return crawl_source(src_run)


def _highlights_stats(std_pesquisa: List[Dict[str, Any]]) -> Dict[str, int]:
    total = 0
    with_date = 0
    for it in std_pesquisa:
        ex = it.get("extras") or {}
        hl = ex.get("highlights") if isinstance(ex.get("highlights"), list) else []
        total += len(hl)
        with_date += sum(1 for h in hl if isinstance(h, dict) and h.get("data_publicacao_raw"))
    return {"highlights_em_extras_total": total, "highlights_com_data_em_extras": with_date}


def run_dryrun(cfg_overrides: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    os.environ["AFRL_WAYBACK_FALLBACK"] = "1"

    sources = _load_json(Path(CONFIG_DEFAULT), {}).get("sources") or []
    diag = {
        "news_hub": _probe(_AFRL_NEWS_HUB),
        "ra": _probe(f"{_AFRL_BASE}/RA/"),
        "rj": _probe(f"{_AFRL_BASE}/RJ/"),
        "rr": _probe(f"{_AFRL_BASE}/RR/"),
        "note": "Diretorias 403 → fixtures/news_research/afrl_{RA,RJ,RR}_directorate.html; News → Wayback se necessário.",
    }

    raw_by: Dict[str, List] = {}
    std_by: Dict[str, List] = {}
    meta_by: Dict[str, Dict] = {}
    review_all: List[Dict[str, Any]] = []
    discard_all: List[Dict[str, Any]] = []

    for sid in ALL_SOURCES:
        raw, std, meta = _crawl_source(cfg_overrides, sources, sid)
        raw_by[sid] = raw
        std_by[sid] = std
        meta_by[sid] = meta
        review_all.extend(meta.get("review_candidates") or [])
        discard_all.extend(meta.get("descartados_ruido") or [])

    std_news = std_by.get(SOURCE_NEWS) or []
    std_hl = std_by.get(SOURCE_HIGHLIGHTS) or []
    std_pesquisa = []
    for sid in DIRECTORATE_SOURCES:
        std_pesquisa.extend(std_by.get(sid) or [])

    st_news = _stats(std_news)
    st_hl = _stats(std_hl)
    st_pes = _stats(std_pesquisa)
    hl_meta = meta_by.get(DIRECTORATE_SOURCES[0], {})
    hl_stats = _highlights_stats(std_pesquisa)

    pre_news = meta_by.get(SOURCE_NEWS, {}).get("afrl_pre_relevance_total")
    highlights_analisados = int(hl_meta.get("highlights_captured") or 0)
    for sid in DIRECTORATE_SOURCES:
        highlights_analisados = max(
            highlights_analisados, int(meta_by.get(sid, {}).get("highlights_captured") or 0)
        )

    errors_count = sum(len((meta_by.get(s) or {}).get("errors") or []) for s in ALL_SOURCES)

    if st_news["total_valido"] >= 8 and len(std_pesquisa) >= 3:
        recomendacao = "apply_controlado"
    elif st_news["total_valido"] >= 4 or st_hl["total_valido"] >= 3:
        recomendacao = "apply_controlado"
    elif st_news["total"] + st_hl["total"] + len(std_pesquisa) >= 5:
        recomendacao = "latente"
    else:
        recomendacao = "precisa_melhoria"

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(exist_ok=True)
    (OUT_DIR / "standardized").mkdir(exist_ok=True)

    for sid in ALL_SOURCES:
        raw_payload = meta_by.get(sid, {}).get("afrl_pre_relevance_raw") or raw_by.get(sid) or []
        if sid == SOURCE_NEWS and meta_by.get(sid, {}).get("afrl_pre_relevance_raw"):
            raw_payload = meta_by[sid]["afrl_pre_relevance_raw"]
        (OUT_DIR / "raw" / f"{sid}_raw.json").write_text(
            json.dumps(raw_payload if sid == SOURCE_NEWS else raw_by.get(sid) or [], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        (OUT_DIR / "standardized" / f"{sid}_standardized.json").write_text(
            json.dumps(std_by.get(sid) or [], ensure_ascii=False, indent=2), encoding="utf-8"
        )

    (OUT_DIR / "review_candidates.json").write_text(
        json.dumps(review_all, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "descartados_ruido.json").write_text(
        json.dumps(discard_all, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    summary = {
        "fonte": "afrl_strategic",
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run",
        "apply": False,
        "diagnostico": diag,
        "config": cfg_overrides,
        "totais": {
            "noticias_analisadas": pre_news or len(raw_by.get(SOURCE_NEWS) or []),
            "highlights_analisados": highlights_analisados,
            "highlights_com_data": int(hl_meta.get("highlights_with_date") or 0),
            "highlights_sem_data": max(0, highlights_analisados - int(hl_meta.get("highlights_with_date") or 0)),
            "registros_institucionais": len(std_pesquisa),
            "standardized_noticia_news": len(std_news),
            "standardized_noticia_highlights": len(std_hl),
            "standardized_pesquisa": len(std_pesquisa),
            "review_total": len(review_all),
            "descartados_total": len(discard_all),
            "errors_count": errors_count,
        },
        "por_fonte": {
            SOURCE_NEWS: {"raw": len(raw_by.get(SOURCE_NEWS) or []), **st_news},
            SOURCE_HIGHLIGHTS: {"raw": len(raw_by.get(SOURCE_HIGHLIGHTS) or []), **st_hl},
            **{
                sid: {
                    "raw": len(raw_by.get(sid) or []),
                    **(_stats(std_by.get(sid) or [])),
                    "highlights_captured": meta_by.get(sid, {}).get("highlights_captured"),
                }
                for sid in DIRECTORATE_SOURCES
            },
        },
        "eixos": {
            "noticias_news": _eixos(std_news),
            "noticias_highlights": _eixos(std_hl),
            "pesquisa_diretorias": _eixos(std_pesquisa),
        },
        "extras_highlights": hl_stats,
        "exemplos": {
            "noticias_news": _examples(std_news),
            "noticias_highlights": _examples(std_hl),
            "pesquisa_diretorias": _examples(std_pesquisa),
            "review": review_all[:5],
            "descartados": discard_all[:5],
        },
        "recomendacao": recomendacao,
    }

    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# AFRL — dry-run estratégico (News + RA/RJ/RR + Highlights)",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Recomendação:** `{recomendacao}`",
        "",
        "## Totais",
        "",
        f"| Métrica | Valor |",
        f"|---------|------:|",
        f"| Notícias analisadas (hub News) | {summary['totais']['noticias_analisadas']} |",
        f"| Highlights analisados (RA/RJ/RR) | {summary['totais']['highlights_analisados']} |",
        f"| Highlights com data | {summary['totais']['highlights_com_data']} |",
        f"| Highlights sem data (só extras) | {summary['totais']['highlights_sem_data']} |",
        f"| Registros institucionais (pesquisa) | {summary['totais']['registros_institucionais']} |",
        f"| Std notícia — news | {summary['totais']['standardized_noticia_news']} ({st_news['total_valido']} válidos) |",
        f"| Std notícia — highlights | {summary['totais']['standardized_noticia_highlights']} ({st_hl['total_valido']} válidos) |",
        f"| Review | {summary['totais']['review_total']} |",
        f"| Descartados | {summary['totais']['descartados_total']} |",
        "",
    ]
    (OUT_DIR / "summary.md").write_text("\n".join(md), encoding="utf-8")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--news-max", type=int, default=30)
    ap.add_argument("--highlights-max", type=int, default=25)
    args = ap.parse_args()
    overrides = {
        SOURCE_NEWS: {"max_items": args.news_max, "time_window_months": 12, "page_enrich_max": 25},
        SOURCE_HIGHLIGHTS: {
            "max_items": args.highlights_max,
            # Fixture/dates em cards podem ser >12m; produção: manter 12 em config.
            "time_window_months": 24,
            "page_enrich_max": 15,
        },
        **{sid: {"max_items": 1, "time_window_months": 24, "page_enrich_max": 0} for sid in DIRECTORATE_SOURCES},
    }
    summary = run_dryrun(overrides)
    print(json.dumps(summary["totais"], indent=2))
    print("recomendacao:", summary["recomendacao"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
