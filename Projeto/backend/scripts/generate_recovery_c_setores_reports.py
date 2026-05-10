#!/usr/bin/env python3
"""Gera relatórios Recovery C (setores) — contexto e diagnóstico.

Uso:
  python scripts/generate_recovery_c_setores_reports.py \\
    [--standardized-dir DIR]   # default: audit_reports_retransform/standardized

Requer artefatos em audit_reports_main_pipeline/ já presentes no repositório.
"""
from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "audit_reports_main_pipeline"
RT = ROOT / "audit_reports_retransform" / "standardized"


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _se_list(it: Dict[str, Any]) -> List[str]:
    ex = it.get("extras") or {}
    se = ex.get("setor_estrategico")
    if isinstance(se, list):
        return [str(x) for x in se if x]
    return []


def build_context() -> Dict[str, Any]:
    post_val = _load(MAIN / "post_daily_validation.json")
    wbs = post_val.get("warnings_by_source") or {}
    se_tot = 72
    for w in post_val.get("warnings") or []:
        if w.get("problem") == "setor_estrategico_muito_amplo":
            se_tot = w.get("count", se_tot)
            break
    ranking = []
    for src, row in wbs.items():
        if not isinstance(row, dict):
            continue
        c = row.get("setor_estrategico_muito_amplo")
        if isinstance(c, int) and c > 0:
            ranking.append({"fonte": src, "setor_estrategico_muito_amplo": c, "warnings_total": row.get("total")})
    ranking.sort(key=lambda x: -x["setor_estrategico_muito_amplo"])

    ex_path = MAIN / "post_daily_warning_examples.json"
    examples_emb = []
    examples_nuc = []
    if ex_path.is_file():
        pdata = _load(ex_path)
        tables = pdata.get("tables") or {}
        ed = tables.get("edital") or {}
        probs = ed.get("problems") or {}
        block = probs.get("setor_estrategico_muito_amplo") or {}
        for ex in (block.get("examples") or [])[:25]:
            fr = ex.get("fonte_recurso") or ex.get("fonte") or ""
            if fr == "EMBRAPII":
                examples_emb.append(ex)
            elif fr == "NUCLEP":
                examples_nuc.append(ex)

    return {
        "gerado_em": _iso_now(),
        "validacao_global": {
            "fonte": "audit_reports_main_pipeline/post_daily_validation.json",
            "timestamp": post_val.get("timestamp"),
            "ok": post_val.get("ok"),
            "critical_errors_count": len(post_val.get("critical_errors") or []),
            "setor_estrategico_muito_amplo_total": se_tot,
        },
        "ranking_fontes_setor_amplo": ranking[:25],
        "exemplos_embrapii": examples_emb[:8],
        "exemplos_nuclep": examples_nuc[:8],
        "motivo_provavel_excesso": (
            "O enrich_opportunity_classification agrega tags temáticas em setor_estrategico e mantém até 4 entradas; "
            "várias fontes recebem pacotes defesa_industrial+aeroespacial+ciencia_tecnologia+industria sem poda por evidência. "
            "URLs de listagem e textos longos aumentam acertos genéricos."
        ),
        "estrategia_correcao": (
            "Recovery C: função recovery_c_cap_setor_estrategico_br em calibrate_embrapii_extras e calibrate_nuclep_extras — "
            "máximo 3 setores com pontuação por evidência em título/descrição/URL/tipos; excedentes em tags_secundarias; "
            "lista completa também em setores_detectados. NUCLEP: páginas institucionais (quem somos, composição, etc.) "
            "recebem tipo_oportunidade noticia_institucional + aviso recovery_c_nuclep_pagina_institucional."
        ),
        "fontes_recovery_c_fase1": ["embrapii", "nuclep"],
        "referencias_consolidados": [
            "audit_reports_main_pipeline/recovery_a_consolidado.json",
            "audit_reports_main_pipeline/recovery_b_consolidado.json",
            "audit_reports_main_pipeline/recovery_b1_amazul_consolidado.json",
        ],
    }


def simulate_cap(item: Dict[str, Any], source: str) -> Dict[str, Any]:
    from CORE.taxonomy_filtros import calibrate_embrapii_extras, calibrate_nuclep_extras

    cpy = deepcopy(item)
    if source == "embrapii":
        calibrate_embrapii_extras(cpy)
    else:
        calibrate_nuclep_extras(cpy)
    return cpy


def build_diagnostico(standardized_dir: Path) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "gerado_em": _iso_now(),
        "standardized_dir": str(standardized_dir),
        "embrapii": {"items_total": 0, "gt3_antes": 0, "itens": []},
        "nuclep": {"items_total": 0, "gt3_antes": 0, "itens": []},
    }
    for src in ("embrapii", "nuclep"):
        path = standardized_dir / f"{src}_standardized.json"
        if not path.is_file():
            continue
        data = _load(path)
        out[src]["items_total"] = len(data)
        for it in data:
            se = _se_list(it)
            if len(se) <= 3:
                continue
            out[src]["gt3_antes"] += 1
            after = simulate_cap(it, src)
            se_after = _se_list(after)
            ex = after.get("extras") or {}
            dropped = [s for s in se if s not in se_after]
            out[src]["itens"].append(
                {
                    "titulo": it.get("titulo"),
                    "link": it.get("link"),
                    "setor_estrategico_antes": se,
                    "setor_estrategico_depois": se_after,
                    "excedentes_movidos_tags_secundarias": dropped,
                    "setores_detectados_extras": ex.get("setores_detectados"),
                    "calibracao_setor_estrategico": ex.get("calibracao_setor_estrategico"),
                    "tipo_oportunidade_depois": ex.get("tipo_oportunidade"),
                    "aviso_institucional": "recovery_c_nuclep_pagina_institucional"
                    in (ex.get("validacao_warnings") or []),
                }
            )
    return out


def write_md_context(ctx: Dict[str, Any], path: Path) -> None:
    lines = [
        "# Recovery C — Setores estratégicos (contexto)",
        "",
        f"Gerado em **{ctx['gerado_em']}**.",
        "",
        "## Situação na validação global",
        "",
        f"- **ok:** `{ctx['validacao_global'].get('ok')}`",
        f"- **Erros críticos:** {ctx['validacao_global'].get('critical_errors_count')}",
        f"- **setor_estrategico_muito_amplo (total edição):** **{ctx['validacao_global'].get('setor_estrategico_muito_amplo_total')}**",
        "",
        "## Ranking de fontes (warning setor amplo)",
        "",
        "| Fonte | setor_estrategico_muito_amplo | total warnings (fonte) |",
        "|---|---:|---:|",
    ]
    for r in ctx.get("ranking_fontes_setor_amplo", [])[:15]:
        lines.append(
            f"| {r['fonte']} | {r['setor_estrategico_muito_amplo']} | {r.get('warnings_total', '—')} |"
        )
    lines += [
        "",
        "## Por que o excesso?",
        "",
        ctx.get("motivo_provavel_excesso", ""),
        "",
        "## Estratégia de correção (fase 1)",
        "",
        ctx.get("estrategia_correcao", ""),
        "",
        "## Exemplos EMBRAPII (validator)",
        "",
    ]
    for ex in ctx.get("exemplos_embrapii", [])[:5]:
        lines.append(f"- **{ex.get('titulo', '')[:80]}** — `{ex.get('link', '')}`")
    lines += ["", "## Exemplos NUCLEP (validator)", ""]
    for ex in ctx.get("exemplos_nuclep", [])[:5]:
        lines.append(f"- **{ex.get('titulo', '')[:80]}** — `{ex.get('link', '')}`")
    lines += [
        "",
        "## Referências",
        "",
    ]
    for ref in ctx.get("referencias_consolidados", []):
        lines.append(f"- `{ref}`")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_md_diagnostic(d: Dict[str, Any], path: Path) -> None:
    lines = [
        "# Recovery C — Diagnóstico por fonte (EMBRAPII / NUCLEP)",
        "",
        f"Pasta standardized: `{d.get('standardized_dir', '')}`",
        "",
        "## EMBRAPII",
        "",
        f"- Itens: **{d['embrapii']['items_total']}**",
        f"- Com `setor_estrategico` > 3 antes do cap: **{d['embrapii']['gt3_antes']}**",
        "",
    ]
    for row in d["embrapii"]["itens"]:
        lines.append(f"### {row.get('titulo', '')[:100]}")
        lines.append(f"- Link: {row.get('link')}")
        lines.append(f"- Antes: `{row.get('setor_estrategico_antes')}`")
        lines.append(f"- Depois (simulação calibração): `{row.get('setor_estrategico_depois')}`")
        lines.append(f"- Excedentes → tags: `{row.get('excedentes_movidos_tags_secundarias')}`")
        lines.append("")
    lines += ["## NUCLEP", "", f"- Itens: **{d['nuclep']['items_total']}**", f"- >3 setores antes: **{d['nuclep']['gt3_antes']}**", ""]
    for row in d["nuclep"]["itens"]:
        lines.append(f"### {row.get('titulo', '')[:100]}")
        lines.append(f"- Link: {row.get('link')}")
        lines.append(f"- Institucional (flag): {row.get('aviso_institucional')}")
        lines.append(f"- Antes: `{row.get('setor_estrategico_antes')}`")
        lines.append(f"- Depois: `{row.get('setor_estrategico_depois')}`")
        lines.append(f"- Excedentes: `{row.get('excedentes_movidos_tags_secundarias')}`")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--standardized-dir",
        type=Path,
        default=RT,
        help="Pasta com *_standardized.json (pré ou pós retransform)",
    )
    args = ap.parse_args()

    ctx = build_context()
    (MAIN / "recovery_c_setores_context.json").write_text(
        json.dumps(ctx, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_md_context(ctx, MAIN / "recovery_c_setores_context.md")

    diag = build_diagnostico(args.standardized_dir.resolve())
    (MAIN / "recovery_c_setores_diagnostico.json").write_text(
        json.dumps(diag, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_md_diagnostic(diag, MAIN / "recovery_c_setores_diagnostico.md")
    print("OK", MAIN / "recovery_c_setores_context.{md,json}")
    print("OK", MAIN / "recovery_c_setores_diagnostico.{md,json}")


if __name__ == "__main__":
    main()
