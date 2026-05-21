#!/usr/bin/env python3
"""
Subset válido — DARPA Programs Research (valido + pesquisa + 24m) + loader dry-run.

Origem: audit_reports_news_research/darpa_strategic_dryrun/standardized/darpa_programs_research_standardized.json
Saída: audit_reports_news_research/darpa_programs_subset_valido/

Destino: public.pesquisa (tipo_pesquisa=programa_pesquisa). Sem apply.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ORIGIN = (
    ROOT
    / "audit_reports_news_research"
    / "darpa_strategic_dryrun"
    / "standardized"
    / "darpa_programs_research_standardized.json"
)
OUT_BASE = ROOT / "audit_reports_news_research" / "darpa_programs_subset_valido"
STD_OUT = OUT_BASE / "standardized" / "darpa_programs_research_standardized.json"
INPUT_DIR_REL = "audit_reports_news_research/darpa_programs_subset_valido"
SOURCE_ID = "darpa_programs_research"
WINDOW_MONTHS = 24
TIPO_PESQUISA_DEFAULT = "programa_pesquisa"


def _parse_pub_date(item: Dict[str, Any]) -> Optional[datetime]:
    raw = str(item.get("data_publicacao") or "").strip()[:10]
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _within_window(item: Dict[str, Any], min_dt: datetime) -> bool:
    dt = _parse_pub_date(item)
    return bool(dt and dt >= min_dt)


def _prepare_pesquisa_row(item: Dict[str, Any]) -> Dict[str, Any]:
    row = dict(item)
    row["fonte_recurso"] = SOURCE_ID
    row["tipo_conteudo"] = "pesquisa"
    tp = str(row.get("tipo_pesquisa") or "").strip()
    if not tp:
        row["tipo_pesquisa"] = TIPO_PESQUISA_DEFAULT
    if not (row.get("descricao") or "").strip() and (row.get("resumo") or "").strip():
        row["descricao"] = row["resumo"]
    return row


def _row_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    return {
        "titulo": item.get("titulo"),
        "data_publicacao": item.get("data_publicacao"),
        "link": item.get("link"),
        "fonte_recurso": item.get("fonte_recurso") or SOURCE_ID,
        "tipo_pesquisa": item.get("tipo_pesquisa"),
        "eixo_estrategico": item.get("eixo_estrategico") or ex.get("eixo_estrategico"),
        "validacao_status": item.get("validacao_status"),
        "tipo_conteudo": item.get("tipo_conteudo"),
    }


def _eixo_distribution(items: List[Dict[str, Any]]) -> Dict[str, int]:
    c: Counter = Counter()
    for it in items:
        for e in it.get("eixo_estrategico") or (it.get("extras") or {}).get("eixo_estrategico") or []:
            if e:
                c[str(e)] += 1
    return dict(c.most_common(20))


def main() -> int:
    if not ORIGIN.is_file():
        print(f"[ERRO] Origem não encontrada: {ORIGIN}", file=sys.stderr)
        return 1

    all_items: List[Dict[str, Any]] = json.loads(ORIGIN.read_text(encoding="utf-8"))
    if not isinstance(all_items, list):
        print("[ERRO] JSON de origem não é lista", file=sys.stderr)
        return 1

    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * WINDOW_MONTHS)
    subset: List[Dict[str, Any]] = []
    excluidos: List[Dict[str, Any]] = []
    portal_latente: List[Dict[str, Any]] = []

    for it in all_items:
        if str(it.get("validacao_status") or "") != "valido":
            motivo = f"validacao_status={it.get('validacao_status')}"
            if str(it.get("validacao_status") or "") == "incompleto":
                portal_latente.append({**_row_summary(it), "motivo": "incompleto_candidato_portal_institucional"})
            excluidos.append({**_row_summary(it), "motivo": motivo})
            continue
        if str(it.get("tipo_conteudo") or "").lower() != "pesquisa":
            excluidos.append({**_row_summary(it), "motivo": "tipo_conteudo!=pesquisa"})
            continue
        if not _within_window(it, min_dt):
            excluidos.append({**_row_summary(it), "motivo": f"fora_janela_{WINDOW_MONTHS}m"})
            continue
        subset.append(_prepare_pesquisa_row(it))

    subset.sort(key=lambda x: _parse_pub_date(x) or datetime.min.replace(tzinfo=timezone.utc), reverse=True)

    STD_OUT.parent.mkdir(parents=True, exist_ok=True)
    STD_OUT.write_text(json.dumps(subset, ensure_ascii=False, indent=2), encoding="utf-8")

    (OUT_BASE / "darpa_programs_payload_noticia.json").write_text("[]", encoding="utf-8")
    (OUT_BASE / "darpa_programs_review_candidates.json").write_text("[]", encoding="utf-8")

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
    load_summary: Dict[str, Any] = {}
    load_summary_path = OUT_BASE / "load_news_research_summary.json"
    if load_summary_path.is_file():
        load_summary = json.loads(load_summary_path.read_text(encoding="utf-8"))
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode

    apply_cmd = (
        "# NÃO EXECUTADO — apply staging pesquisa\n"
        "$env:EDITALFINDER_ENV='staging'\n"
        "$env:EDITALFINDER_ALLOW_STAGING_APPLY='true'\n"
        "python scripts/load_news_research_sources.py `\n"
        "  --apply --staging --test-db-before-apply `\n"
        f"  --source {SOURCE_ID} `\n"
        f"  --input-dir {INPUT_DIR_REL}"
    )

    consolidado: Dict[str, Any] = {
        "fonte": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "apply_executado": False,
        "destino": "public.pesquisa",
        "tipo_pesquisa": TIPO_PESQUISA_DEFAULT,
        "origem_standardized": str(ORIGIN.relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(STD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "janela_publica_meses": WINDOW_MONTHS,
        "corte_data_minima": min_dt.date().isoformat(),
        "totais": {
            "original": len(all_items),
            "subset_escolhido": len(subset),
            "excluido": len(excluidos),
            "valido_original": sum(
                1 for it in all_items if str(it.get("validacao_status") or "") == "valido"
            ),
            "incompletos_nao_incluidos": len(portal_latente),
        },
        "incompletos_portal_institucional_latente": portal_latente,
        "itens_incluidos": [_row_summary(it) for it in subset],
        "itens_excluidos": excluidos[:30],
        "eixos_estrategicos": _eixo_distribution(subset),
        "loader_dryrun": {
            "comando": " ".join(load_cmd),
            "input_dir": INPUT_DIR_REL,
            "would_upsert_pesquisa": load_summary.get("would_upsert_pesquisa"),
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "errors_count": load_summary.get("errors_count"),
            "skipped": load_summary.get("skipped"),
            "apply_status": load_summary.get("apply_status"),
            "total_pesquisa_input": load_summary.get("total_pesquisa"),
            "summary_path": str(load_summary_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "apply_staging": {
            "executado": False,
            "powershell": apply_cmd,
        },
        "observacao": (
            "Programas DARPA são pesquisa estratégica (programa_pesquisa), não notícia. "
            "15 incompletos do dry-run estratégico ficam fora do subset; candidatos a portal_institucional "
            "se forem enriquecidos no futuro."
        ),
    }

    (OUT_BASE / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# DARPA Programs Research — subset válido (staging)",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **Destino:** `public.pesquisa` · `tipo_pesquisa={TIPO_PESQUISA_DEFAULT}`",
        f"- **Janela:** {WINDOW_MONTHS} meses (corte ≥ `{consolidado['corte_data_minima']}`)",
        "",
        "## Totais",
        "",
        f"| Original | {consolidado['totais']['original']} |",
        f"| Válidos no original | {consolidado['totais']['valido_original']} |",
        f"| **Subset** | **{consolidado['totais']['subset_escolhido']}** |",
        f"| Incompletos (latentes) | {consolidado['totais']['incompletos_nao_incluidos']} |",
        "",
        "## Loader dry-run",
        "",
        f"- **would_upsert_pesquisa:** {load_summary.get('would_upsert_pesquisa')}",
        f"- **errors_count:** {load_summary.get('errors_count')}",
        f"- **apply:** não",
        "",
        "## Eixos",
        "",
    ]
    for k, v in sorted((consolidado.get("eixos_estrategicos") or {}).items(), key=lambda x: (-x[1], x[0])):
        md.append(f"- `{k}`: {v}")
    md.extend(["", "## Programas (título · data)", ""])
    for row in consolidado["itens_incluidos"]:
        md.append(f"- **{row.get('data_publicacao')}** — {row.get('titulo', '')[:90]}")
    md.extend(["", "## Apply staging (não executado)", "", "```powershell", apply_cmd, "```", ""])
    (OUT_BASE / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "subset": len(subset),
                "would_upsert_pesquisa": load_summary.get("would_upsert_pesquisa"),
                "errors_count": load_summary.get("errors_count"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
