#!/usr/bin/env python3
"""
Dry-run MCTI Notícias — variante enriquecida (page_enrich_max=30) + comparação com baseline.

Gera audit_reports_news_research/mcti_noticias_dryrun_enriched/ e, se ≥12 válidos e errors=0,
subset em mcti_noticias_subset_valido/ + loader dry-run.

Sem apply.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.news_research.run_mcti_noticias_dryrun import (  # noqa: E402
    SOURCE_ID,
    _distribution,
    _examples,
    _run_summary_stats,
    run_dryrun,
)

BASELINE_DIR = ROOT / "audit_reports_news_research" / "mcti_noticias_dryrun"
ENRICHED_DIR = ROOT / "audit_reports_news_research" / "mcti_noticias_dryrun_enriched"
SUBSET_DIR = ROOT / "audit_reports_news_research" / "mcti_noticias_subset_valido"
STD_ENRICHED = ENRICHED_DIR / "standardized" / f"{SOURCE_ID}_standardized.json"
STD_SUBSET = SUBSET_DIR / "standardized" / f"{SOURCE_ID}_standardized.json"
INPUT_DIR_REL = "audit_reports_news_research/mcti_noticias_subset_valido"
WINDOW_MONTHS = 12
PAGE_ENRICH_MAX = 30
MIN_VALIDOS_SUBSET = 12


def _load_summary(d: Path) -> Dict[str, Any]:
    p = d / "summary.json"
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _load_std(d: Path) -> List[Dict[str, Any]]:
    p = d / "standardized" / f"{SOURCE_ID}_standardized.json"
    if not p.is_file():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _metrics(summary: Dict[str, Any]) -> Dict[str, Any]:
    t = summary.get("totais") or {}
    return {
        "total_raw": t.get("total_raw"),
        "mantidos": t.get("standardized"),
        "review": t.get("review"),
        "descartados": t.get("descartados_ruido"),
        "validos": t.get("total_valido"),
        "incompletos": t.get("total_incompleto"),
        "errors_count": t.get("errors_count"),
        "page_enrich_max": (summary.get("config") or {}).get("page_enrich_max"),
        "page_enrich_fetches": t.get("page_enrich_fetches"),
        "validacao_status_counts": summary.get("validacao_status_counts") or {},
        "distribuicao": summary.get("distribuicao") or {},
    }


def _incompleto_to_valido(
    base_std: List[Dict[str, Any]], enriched_std: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    by_link_b: Dict[str, Dict[str, Any]] = {}
    for it in base_std:
        lk = str(it.get("link") or "").strip()
        if lk:
            by_link_b[lk] = it
    out: List[Dict[str, Any]] = []
    for it in enriched_std:
        lk = str(it.get("link") or "").strip()
        if not lk:
            continue
        prev = by_link_b.get(lk)
        if not prev:
            continue
        if str(prev.get("validacao_status") or "") == "valido":
            continue
        if str(it.get("validacao_status") or "") != "valido":
            continue
        out.append(
            {
                "titulo": (it.get("titulo") or "")[:200],
                "link": lk[:800],
                "validacao_antes": prev.get("validacao_status"),
                "validacao_depois": it.get("validacao_status"),
                "resumo_chars_antes": len(str(prev.get("resumo") or prev.get("descricao") or "")),
                "resumo_chars_depois": len(str(it.get("resumo") or it.get("descricao") or "")),
            }
        )
    return out


def _compare(base_dir: Path, enriched_dir: Path) -> Dict[str, Any]:
    sb, se = _load_summary(base_dir), _load_summary(enriched_dir)
    mb, me = _metrics(sb), _metrics(se)
    delta = {k: (me.get(k) or 0) - (mb.get(k) or 0) for k in mb if isinstance(mb.get(k), (int, float))}
    eixos_b = (mb.get("distribuicao") or {}).get("eixo_estrategico") or {}
    eixos_e = (me.get("distribuicao") or {}).get("eixo_estrategico") or {}
    eixos_delta: Dict[str, int] = {}
    for k in set(eixos_b) | set(eixos_e):
        eixos_delta[k] = int(eixos_e.get(k, 0)) - int(eixos_b.get(k, 0))
    promovidos = _incompleto_to_valido(_load_std(base_dir), _load_std(enriched_dir))
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "baseline": {"diretorio": base_dir.name, **mb},
        "enriched": {"diretorio": enriched_dir.name, **me},
        "delta": delta,
        "eixos_estrategicos_delta": eixos_delta,
        "incompleto_para_valido": promovidos,
        "incompleto_para_valido_total": len(promovidos),
    }


def _write_comparison_md(comp: Dict[str, Any], out_dir: Path) -> None:
    b, e = comp["baseline"], comp["enriched"]
    d = comp["delta"]
    lines = [
        "# MCTI Notícias — comparação baseline vs enriched",
        "",
        f"- **Gerado:** {comp['generated_at']}",
        f"- **Baseline:** `{b.get('diretorio')}` — page_enrich_max={b.get('page_enrich_max')}",
        f"- **Enriched:** `{e.get('diretorio')}` — page_enrich_max={e.get('page_enrich_max')}",
        "",
        "| Métrica | Baseline | Enriched | Δ |",
        "|---------|----------:|----------:|--:|",
        f"| Total raw | {b.get('total_raw')} | {e.get('total_raw')} | {d.get('total_raw', 0):+d} |",
        f"| Mantidos | {b.get('mantidos')} | {e.get('mantidos')} | {d.get('mantidos', 0):+d} |",
        f"| Review | {b.get('review')} | {e.get('review')} | {d.get('review', 0):+d} |",
        f"| Descartados | {b.get('descartados')} | {e.get('descartados')} | {d.get('descartados', 0):+d} |",
        f"| **Válidos** | **{b.get('validos')}** | **{e.get('validos')}** | **{d.get('validos', 0):+d}** |",
        f"| Incompletos | {b.get('incompletos')} | {e.get('incompletos')} | {d.get('incompletos', 0):+d} |",
        f"| errors_count | {b.get('errors_count')} | {e.get('errors_count')} | — |",
        f"| page_enrich_fetches | {b.get('page_enrich_fetches')} | {e.get('page_enrich_fetches')} | — |",
        "",
        f"## Promovidos incompleto → válido ({comp['incompleto_para_valido_total']})",
        "",
    ]
    for row in comp.get("incompleto_para_valido") or []:
        lines.append(
            f"- **{row.get('titulo', '')[:70]}** — resumo {row.get('resumo_chars_antes')}→"
            f"{row.get('resumo_chars_depois')} chars"
        )
    if comp.get("eixos_estrategicos_delta"):
        lines.extend(["", "## Δ eixos estratégicos (mantidos)", ""])
        for k, v in sorted(comp["eixos_estrategicos_delta"].items(), key=lambda x: (-abs(x[1]), x[0])):
            if v:
                lines.append(f"- `{k}`: {v:+d}")
    lines.append("")
    (out_dir / "comparacao_mcti_noticias_base_vs_enriched.md").write_text("\n".join(lines), encoding="utf-8")


def _parse_pub(item: Dict[str, Any]) -> Optional[datetime]:
    raw = str(item.get("data_publicacao") or "").strip()[:10]
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _build_subset_valido(enriched_std: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * WINDOW_MONTHS)
    validos: List[Dict[str, Any]] = []
    excluidos: List[Dict[str, Any]] = []
    for it in enriched_std:
        if str(it.get("validacao_status") or "") != "valido":
            excluidos.append(
                {
                    "titulo": (it.get("titulo") or "")[:120],
                    "link": it.get("link"),
                    "motivo": f"validacao_status={it.get('validacao_status')}",
                }
            )
            continue
        dt = _parse_pub(it)
        if not dt or dt < min_dt:
            excluidos.append(
                {
                    "titulo": (it.get("titulo") or "")[:120],
                    "link": it.get("link"),
                    "motivo": f"fora_janela_{WINDOW_MONTHS}m",
                }
            )
            continue
        validos.append(it)
    validos.sort(key=lambda x: _parse_pub(x) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return validos, excluidos


def _build_payload_noticia(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        row = dict(item)
        if str(row.get("tipo_conteudo") or "").lower() == "noticia":
            row.pop("tipo_pesquisa", None)
        if not row.get("descricao") and row.get("resumo"):
            row["descricao"] = row["resumo"]
        out.append(row)
    return out


def _run_loader_dryrun() -> Dict[str, Any]:
    load_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "load_news_research_sources.py"),
        "--dry-run",
        "--source",
        SOURCE_ID,
        "--input-dir",
        INPUT_DIR_REL,
    ]
    proc = subprocess.run(load_cmd, cwd=str(ROOT), capture_output=True, text=True)
    summary_path = SUBSET_DIR / "load_news_research_summary.json"
    loader: Dict[str, Any] = {"returncode": proc.returncode}
    if summary_path.is_file():
        loader.update(json.loads(summary_path.read_text(encoding="utf-8")))
    if proc.returncode != 0:
        loader["stderr"] = (proc.stderr or "")[-2000:]
        loader["stdout"] = (proc.stdout or "")[-2000:]
    return loader


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-dir", default=str(BASELINE_DIR.relative_to(ROOT)))
    ap.add_argument("--output-dir", default="mcti_noticias_dryrun_enriched")
    ap.add_argument("--max-items", type=int, default=30)
    ap.add_argument("--page-enrich-max", type=int, default=PAGE_ENRICH_MAX)
    ap.add_argument("--min-validos-subset", type=int, default=MIN_VALIDOS_SUBSET)
    ap.add_argument("--skip-subset", action="store_true")
    args = ap.parse_args()

    base_dir = Path(args.baseline_dir)
    if not base_dir.is_absolute():
        base_dir = ROOT / base_dir

    out_arg = Path(args.output_dir)
    enriched_dir = out_arg if out_arg.is_absolute() else ROOT / "audit_reports_news_research" / out_arg.name

    summary = run_dryrun(
        enriched_dir,
        max_items=args.max_items,
        time_window_months=WINDOW_MONTHS,
        page_enrich_max=args.page_enrich_max,
    )
    summary["variante"] = "enriched"
    summary["comparacao_com"] = base_dir.name
    (enriched_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    comp = _compare(base_dir, enriched_dir)
    (enriched_dir / "comparacao_mcti_noticias_base_vs_enriched.json").write_text(
        json.dumps(comp, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_comparison_md(comp, enriched_dir)

    validos = int((summary.get("totais") or {}).get("total_valido") or 0)
    errors = int((summary.get("totais") or {}).get("errors_count") or 0)
    subset_built = False
    consolidado: Optional[Dict[str, Any]] = None

    if not args.skip_subset and validos >= args.min_validos_subset and errors == 0:
        enriched_std = _load_std(enriched_dir)
        subset_items, excluidos = _build_subset_valido(enriched_std)
        if subset_items:
            STD_SUBSET.parent.mkdir(parents=True, exist_ok=True)
            STD_SUBSET.write_text(json.dumps(subset_items, ensure_ascii=False, indent=2), encoding="utf-8")
            payload = _build_payload_noticia(subset_items)
            (SUBSET_DIR / "mcti_noticias_payload_noticia.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            (SUBSET_DIR / "mcti_noticias_payload_pesquisa.json").write_text("[]", encoding="utf-8")
            (SUBSET_DIR / "mcti_noticias_review_candidates.json").write_text("[]", encoding="utf-8")
            subset_built = True
            loader = _run_loader_dryrun()
            consolidado = {
                "fonte": SOURCE_ID,
                "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "origem_enriched": str(STD_ENRICHED.relative_to(ROOT)).replace("\\", "/"),
                "subset_standardized": str(STD_SUBSET.relative_to(ROOT)).replace("\\", "/"),
                "criterio_subset": {
                    "validacao_status": "valido",
                    "janela_meses": WINDOW_MONTHS,
                    "min_validos_enriched": args.min_validos_subset,
                },
                "enriched_dryrun": {
                    "diretorio": enriched_dir.name,
                    "validos": validos,
                    "mantidos": (summary.get("totais") or {}).get("standardized"),
                    "errors_count": errors,
                },
                "subset": {
                    "escolhidos": len(subset_items),
                    "excluidos": len(excluidos),
                },
                "loader_dryrun": {
                    "would_upsert_noticia": loader.get("would_upsert_noticia"),
                    "errors_count": loader.get("errors_count"),
                    "returncode": loader.get("returncode"),
                    "apply_status": loader.get("apply_status"),
                    "summary_path": str(
                        (SUBSET_DIR / "load_news_research_dryrun_summary.json").relative_to(ROOT)
                    ).replace("\\", "/"),
                },
                "comparacao": {
                    "delta_validos": comp["delta"].get("validos"),
                    "promovidos_incompleto_valido": comp["incompleto_para_valido_total"],
                },
                "apply": False,
                "observacao": "Subset válido recente a partir do dry-run enriched; apply não executado.",
            }
            (SUBSET_DIR / "consolidado_subset.json").write_text(
                json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            md = [
                "# MCTI Notícias — subset válido recente (consolidado)",
                "",
                f"- **Execução:** {consolidado['data_execucao']}",
                f"- **Origem enriched:** `{consolidado['origem_enriched']}`",
                f"- **Subset:** `{consolidado['subset_standardized']}`",
                "",
                "## Totais",
                "",
                f"| Enriched válidos | {validos} |",
                f"| **Subset escolhido** | **{len(subset_items)}** |",
                f"| Excluídos do subset | {len(excluidos)} |",
                "",
                "## Loader dry-run",
                "",
                f"- **would_upsert_noticia:** {loader.get('would_upsert_noticia')}",
                f"- **errors_count:** {loader.get('errors_count')}",
                f"- **apply:** não",
                "",
                f"Promovidos incompleto→válido (enriched vs baseline): **{comp['incompleto_para_valido_total']}**",
                "",
            ]
            (SUBSET_DIR / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "enriched": summary.get("totais"),
                "delta_validos": comp["delta"].get("validos"),
                "promovidos": comp["incompleto_para_valido_total"],
                "subset_built": subset_built,
                "subset_n": consolidado["subset"]["escolhidos"] if consolidado else 0,
                "loader": (consolidado or {}).get("loader_dryrun"),
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
