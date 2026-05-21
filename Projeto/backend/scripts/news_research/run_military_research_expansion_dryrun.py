#!/usr/bin/env python3
"""
Dry-run unificado — expansão militar/técnico-científica (sem apply).

Saída: audit_reports_news_research/military_research_expansion_dryrun/
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
    _load_json,
    crawl_source,
)
from scripts.news_research.military_af_research import MILITARY_SOURCE_PRIORITY  # noqa: E402

OUT_DIR = ROOT / "audit_reports_news_research" / "military_research_expansion_dryrun"

NEWS_SOURCES = ("arl_news", "space_force_news", "afnwc_news", "afmc_news")
PESQUISA_SOURCES = (
    "afrl_technology_areas",
    "arl_resources",
    "afnwc_innovation",
    "afnwc_weapon_systems",
)
ALL_SOURCES = tuple(MILITARY_SOURCE_PRIORITY)

DESTINO = {
    "afmc_news": "noticia",
    "afnwc_news": "noticia",
    "space_force_news": "noticia",
    "arl_news": "noticia",
    "afrl_technology_areas": "pesquisa",
    "afnwc_innovation": "pesquisa",
    "afnwc_weapon_systems": "pesquisa",
    "arl_resources": "pesquisa",
}


def _probe_live(url: str) -> Dict[str, Any]:
    import requests

    H = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        r = requests.get(url, headers=H, timeout=45)
        return {"url": url, "status": r.status_code, "bytes": len(r.text or ""), "ok": r.status_code == 200}
    except Exception as e:
        return {"url": url, "status": None, "error": str(e)[:200], "ok": False}


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
    return dict(c.most_common(12))


def _examples(items: List[Dict[str, Any]], n: int = 3) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in items[:n]:
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        out.append(
            {
                "titulo": (it.get("titulo") or "")[:140],
                "link": (it.get("link") or "")[:500],
                "validacao_status": it.get("validacao_status"),
                "data_publicacao": it.get("data_publicacao"),
                "eixo_estrategico": it.get("eixo_estrategico") or ex.get("eixo_estrategico"),
            }
        )
    return out


def _recommendation(sid: str, st: Dict[str, Any], raw_n: int, review_n: int) -> str:
    v = int(st.get("total_valido") or 0)
    if sid in PESQUISA_SOURCES:
        if v >= 5 or (sid == "afnwc_weapon_systems" and v >= 1):
            return "apply_controlado"
        if v >= 3:
            return "apply_controlado"
        if v >= 1 or raw_n >= 1:
            return "latente" if review_n > v else "precisa_melhoria"
        return "nao_recomendado"
    if v >= 8:
        return "apply_controlado"
    if v >= 3:
        return "apply_controlado"
    if v >= 1 or raw_n >= 5:
        return "latente"
    if raw_n > 0:
        return "precisa_melhoria"
    return "nao_recomendado"


def _crawl(cfg: Dict[str, Any], sources: List[Dict[str, Any]], sid: str) -> Tuple[List, List, Dict]:
    src = next((s for s in sources if str(s.get("id")) == sid), None)
    if not src:
        raise SystemExit(f"[ERRO] Fonte {sid} não encontrada em config")
    return crawl_source({**src, **cfg.get(sid, {})})


def run_dryrun(overrides: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    os.environ["DOD_AFMIL_WAYBACK_FALLBACK"] = "1"
    os.environ["AFRL_WAYBACK_FALLBACK"] = "1"

    sources = _load_json(Path(CONFIG_DEFAULT), {}).get("sources") or []
    diag_urls = [
        "https://www.afmc.af.mil/News/",
        "https://www.afnwc.af.mil/News/",
        "https://www.spaceforce.mil/News/",
        "https://afresearchlab.com/technology/",
        "https://arl.devcom.army.mil/media-center/",
        "https://arl.devcom.army.mil/resources/",
    ]
    diagnostico = {u: _probe_live(u) for u in diag_urls}
    diagnostico["wayback"] = "DOD_AFMIL_WAYBACK_FALLBACK=1 para hubs .af.mil bloqueados"

    raw_by: Dict[str, List] = {}
    std_by: Dict[str, List] = {}
    meta_by: Dict[str, Dict] = {}
    review_all: List[Dict[str, Any]] = []
    discard_all: List[Dict[str, Any]] = []

    for sid in ALL_SOURCES:
        raw, std, meta = _crawl(overrides, sources, sid)
        raw_by[sid] = raw
        std_by[sid] = std
        meta_by[sid] = meta
        for rc in meta.get("review_candidates") or []:
            if isinstance(rc, dict):
                rc = {**rc, "source_id": sid, "destino_sugerido": rc.get("destino_sugerido") or "Radar/Editais"}
                review_all.append(rc)
        for d in meta.get("descartados_ruido") or []:
            if isinstance(d, dict):
                discard_all.append({**d, "source_id": sid})

    por_fonte: Dict[str, Any] = {}
    recs: Dict[str, str] = {}
    for sid in ALL_SOURCES:
        meta = meta_by.get(sid) or {}
        pre = int(meta.get("military_pre_relevance_total") or meta.get("raw_total") or len(raw_by.get(sid) or []))
        st = _stats(std_by.get(sid) or [])
        rev_n = len([r for r in review_all if r.get("source_id") == sid])
        disc_n = len([d for d in discard_all if d.get("source_id") == sid])
        rec = _recommendation(sid, st, pre, rev_n)
        recs[sid] = rec
        por_fonte[sid] = {
            "destino": DESTINO.get(sid),
            "raw_analisado": pre,
            "raw_pos_filtro": len(raw_by.get(sid) or []),
            "standardized": st["total"],
            "validos": st["total_valido"],
            "incompletos": st["total_incompleto"],
            "review": rev_n,
            "descartados": disc_n,
            "eixos": _eixos(std_by.get(sid) or []),
            "exemplos_mantidos": _examples(
                [x for x in (std_by.get(sid) or []) if x.get("validacao_status") == "valido"]
            ),
            "exemplos_descartados": [
                {
                    "titulo": (d.get("titulo") or "")[:120],
                    "link": (d.get("link") or "")[:400],
                    "motivo": d.get("motivo") or d.get("routing"),
                }
                for d in discard_all
                if d.get("source_id") == sid
            ][:4],
            "destino_sugerido": (
                "Radar/Editais"
                if rev_n and sid in ("arl_resources",)
                else DESTINO.get(sid)
            ),
            "recomendacao": rec,
            "listing_method": meta.get("listing_method"),
            "errors": meta.get("errors"),
        }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(exist_ok=True)
    (OUT_DIR / "standardized").mkdir(exist_ok=True)

    for sid in ALL_SOURCES:
        pre_raw = (meta_by.get(sid) or {}).get("military_pre_relevance_raw") or raw_by.get(sid) or []
        (OUT_DIR / "raw" / f"{sid}_raw.json").write_text(
            json.dumps(pre_raw, ensure_ascii=False, indent=2), encoding="utf-8"
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
        "fonte": "military_research_expansion",
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run",
        "apply": False,
        "diagnostico": diagnostico,
        "config_overrides": overrides,
        "por_fonte": por_fonte,
        "recomendacoes": recs,
        "totais": {
            "fontes": len(ALL_SOURCES),
            "review_total": len(review_all),
            "descartados_total": len(discard_all),
            "standardized_total": sum(len(std_by.get(s) or []) for s in ALL_SOURCES),
            "validos_total": sum(por_fonte[s]["validos"] for s in ALL_SOURCES),
        },
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Military / Research Expansion — dry-run",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Apply:** não",
        "",
        "## Por fonte",
        "",
        "| Fonte | Destino | Raw | Std | Válidos | Review | Desc. | Recomendação |",
        "|-------|---------|-----|-----|---------|--------|-------|--------------|",
    ]
    for sid in ALL_SOURCES:
        p = por_fonte[sid]
        lines.append(
            f"| {sid} | {p['destino']} | {p['raw_analisado']} | {p['standardized']} | "
            f"{p['validos']} | {p['review']} | {p['descartados']} | `{p['recomendacao']}` |"
        )
    lines.extend(["", "## Diagnóstico HTTP (live, browser UA)", ""])
    for u, d in diagnostico.items():
        if isinstance(d, dict):
            lines.append(f"- {u}: status={d.get('status')} bytes={d.get('bytes', '')}")
    (OUT_DIR / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--news-max", type=int, default=30)
    ap.add_argument("--pesquisa-max", type=int, default=20)
    args = ap.parse_args()
    overrides: Dict[str, Dict[str, Any]] = {}
    for sid in NEWS_SOURCES:
        overrides[sid] = {
            "max_items": args.news_max,
            "time_window_months": 12,
            "page_enrich_max": 15 if sid != "arl_news" else 12,
        }
    for sid in PESQUISA_SOURCES:
        overrides[sid] = {
            "max_items": args.pesquisa_max,
            "time_window_months": 24,
            "page_enrich_max": (
                12
                if sid == "afrl_technology_areas"
                else (8 if sid == "arl_resources" else 0)
            ),
        }
    summary = run_dryrun(overrides)
    print(json.dumps(summary["totais"], indent=2))
    print("por_fonte:", json.dumps({k: v["recomendacao"] for k, v in summary["por_fonte"].items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
