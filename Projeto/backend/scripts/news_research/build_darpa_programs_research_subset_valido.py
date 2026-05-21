#!/usr/bin/env python3
"""
Subset válido DARPA Programs Research para apply staging (sem apply).

Origem: audit_reports_news_research/darpa_strategic_dryrun/standardized/
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SOURCE_ID = "darpa_programs_research"
ORIGIN = (
    ROOT
    / "audit_reports_news_research"
    / "darpa_strategic_dryrun"
    / "standardized"
    / "darpa_programs_research_standardized.json"
)
OUT_BASE = ROOT / "audit_reports_news_research" / "darpa_programs_research_subset_valido"
STD_OUT = OUT_BASE / "standardized" / "darpa_programs_research_standardized.json"
INPUT_DIR_REL = "audit_reports_news_research/darpa_programs_research_subset_valido"


def _matches(it: Dict[str, Any]) -> bool:
    return (
        str(it.get("validacao_status") or "") == "valido"
        and str(it.get("tipo_conteudo") or "") == "pesquisa"
        and str(it.get("tipo_pesquisa") or "") == "programa_pesquisa"
        and str(it.get("fonte_recurso") or "") == SOURCE_ID
    )


def _eixo_distribution(items: List[Dict[str, Any]]) -> Dict[str, int]:
    c: Counter = Counter()
    for it in items:
        for e in it.get("eixo_estrategico") or (it.get("extras") or {}).get("eixo_estrategico") or []:
            if e:
                c[str(e)] += 1
    return dict(c.most_common(20))


def _area_distribution(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    c: Counter = Counter()
    for it in items:
        for a in it.get(key) or []:
            if a:
                c[str(a)] += 1
    return dict(c.most_common(15))


def main() -> int:
    if not ORIGIN.is_file():
        print(f"[ERRO] Origem não encontrada: {ORIGIN}", file=sys.stderr)
        return 1

    all_items: List[Dict[str, Any]] = json.loads(ORIGIN.read_text(encoding="utf-8"))
    if not isinstance(all_items, list):
        print("[ERRO] JSON de origem não é lista", file=sys.stderr)
        return 1

    rejeitados: List[Dict[str, Any]] = []
    subset: List[Dict[str, Any]] = []
    for it in all_items:
        if _matches(it):
            row = dict(it)
            ex = dict(row.get("extras") or {})
            ex["source_id"] = SOURCE_ID
            ex["subset"] = "valido_programa_pesquisa"
            ex["subset_policy"] = "todos_validos_dryrun_estrategico"
            row["extras"] = ex
            subset.append(row)
        else:
            motivos = []
            if str(it.get("validacao_status") or "") != "valido":
                motivos.append("validacao_status!=valido")
            if str(it.get("tipo_conteudo") or "") != "pesquisa":
                motivos.append("tipo_conteudo!=pesquisa")
            if str(it.get("tipo_pesquisa") or "") != "programa_pesquisa":
                motivos.append("tipo_pesquisa!=programa_pesquisa")
            if str(it.get("fonte_recurso") or "") != SOURCE_ID:
                motivos.append("fonte_recurso!=darpa_programs_research")
            rejeitados.append({"link": it.get("link"), "titulo": it.get("titulo"), "motivos": motivos})

    subset.sort(key=lambda x: str(x.get("data_publicacao") or ""), reverse=True)

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
    if proc.stdout:
        print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        return proc.returncode

    load_summary: Dict[str, Any] = {}
    load_path = OUT_BASE / "load_news_research_summary.json"
    if load_path.is_file():
        load_summary = json.loads(load_path.read_text(encoding="utf-8"))

    eixos = _eixo_distribution(subset)
    areas = _area_distribution(subset, "area_tecnologica")
    consolidado: Dict[str, Any] = {
        "fonte": SOURCE_ID,
        "nome_exibicao": "DARPA Research Programs",
        "fonte_recurso": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "origem": str(ORIGIN.relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(STD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "origem_totais": {
            "total_standardized_origem": len(all_items),
            "valido_filtrado": len(subset),
            "rejeitados_filtragem": len(rejeitados),
        },
        "subset": {
            "criterios": [
                "validacao_status=valido",
                "tipo_conteudo=pesquisa",
                "tipo_pesquisa=programa_pesquisa",
                "fonte_recurso=darpa_programs_research",
            ],
            "escolhidos": len(subset),
        },
        "loader_dryrun": {
            "comando": " ".join(load_cmd),
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "would_upsert_pesquisa": load_summary.get("would_upsert_pesquisa"),
            "errors_count": load_summary.get("errors_count"),
            "apply_status": load_summary.get("apply_status"),
            "summary_path": str(load_path.relative_to(ROOT)).replace("\\", "/") if load_path.is_file() else None,
        },
        "distribuicao_eixos_estrategicos": eixos,
        "distribuicao_area_tecnologica": areas,
        "itens": [
            {
                "titulo": it.get("titulo"),
                "data_publicacao": it.get("data_publicacao"),
                "link": it.get("link"),
                "eixo_estrategico": it.get("eixo_estrategico")
                or (it.get("extras") or {}).get("eixo_estrategico"),
            }
            for it in subset
        ],
        "observacao": (
            "Catálogo de programas DARPA (pesquisa estratégica). "
            "Destino: public.pesquisa (programa_pesquisa). Apply não executado nesta tarefa."
        ),
        "apply_staging": {"executado": False},
    }

    (OUT_BASE / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# DARPA Programs Research — subset válido (staging)",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **source_id:** `{SOURCE_ID}`",
        "",
        consolidado["observacao"],
        "",
        "## Origem e filtro",
        "",
        f"| Métrica | Valor |",
        f"|---------|------:|",
        f"| Total na origem | {consolidado['origem_totais']['total_standardized_origem']} |",
        f"| **Subset válido** | **{consolidado['subset']['escolhidos']}** |",
        f"| Rejeitados na filtragem | {consolidado['origem_totais']['rejeitados_filtragem']} |",
        "",
        "## Loader dry-run",
        "",
        f"- **would_upsert_pesquisa:** {consolidado['loader_dryrun']['would_upsert_pesquisa']}",
        f"- **would_upsert_noticia:** {consolidado['loader_dryrun']['would_upsert_noticia']}",
        f"- **errors_count:** {consolidado['loader_dryrun']['errors_count']}",
        f"- **apply_status:** {consolidado['loader_dryrun']['apply_status']}",
        "",
        "## Eixos estratégicos",
        "",
    ]
    for k, v in sorted(eixos.items(), key=lambda x: (-x[1], x[0])):
        md.append(f"- `{k}`: {v}")
    md.extend(["", "## Programas (data desc)", ""])
    for i, row in enumerate(consolidado["itens"], 1):
        md.append(f"{i}. **{row.get('data_publicacao')}** — {row.get('titulo', '')[:90]}")
        md.append(f"   - {row.get('link')}")
    md.append("")
    (OUT_BASE / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "subset": len(subset),
                "would_upsert_pesquisa": consolidado["loader_dryrun"]["would_upsert_pesquisa"],
                "errors_count": consolidado["loader_dryrun"]["errors_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
