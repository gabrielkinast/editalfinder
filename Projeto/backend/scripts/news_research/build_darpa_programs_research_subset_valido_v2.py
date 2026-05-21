#!/usr/bin/env python3
"""
Subset válido v2 — DARPA Programs Research (tipos + roteamento corrigidos).

Origem: audit_reports_news_research/darpa_strategic_dryrun/standardized/
Saída: audit_reports_news_research/darpa_programs_research_subset_valido_v2/
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
DISPLAY_FONTE = "DARPA"
ORIGIN = (
    ROOT
    / "audit_reports_news_research"
    / "darpa_strategic_dryrun"
    / "standardized"
    / "darpa_programs_research_standardized.json"
)
OUT_BASE = ROOT / "audit_reports_news_research" / "darpa_programs_research_subset_valido_v2"
STD_OUT = OUT_BASE / "standardized" / "darpa_programs_research_standardized.json"
INPUT_DIR_REL = "audit_reports_news_research/darpa_programs_research_subset_valido_v2"


def _matches(it: Dict[str, Any]) -> bool:
    return (
        str(it.get("validacao_status") or "") == "valido"
        and str(it.get("tipo_conteudo") or "") == "pesquisa"
        and str(it.get("tipo_pesquisa") or "") == "programa_pesquisa"
        and str(it.get("fonte_recurso") or "") == SOURCE_ID
    )


def _enrich_row(row: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(row)
    out["fonte"] = DISPLAY_FONTE
    out["fonte_recurso"] = SOURCE_ID
    out["tipo_conteudo"] = "pesquisa"
    out["tipo_pesquisa"] = "programa_pesquisa"
    out["tipo_recurso"] = "programa_estrategico"
    out["tipo_oportunidade"] = "pesquisa_estrategica"
    ex = dict(out.get("extras") or {})
    ex.update(
        {
            "source_id": SOURCE_ID,
            "subset": "valido_programa_pesquisa_v2",
            "subset_policy": "tipos_pesquisa_recurso_oportunidade_explicitos",
            "tipo_pesquisa": "programa_pesquisa",
            "tipo_recurso": "programa_estrategico",
            "tipo_oportunidade": "pesquisa_estrategica",
        }
    )
    out["extras"] = ex
    if not (out.get("descricao") or "").strip() and (out.get("resumo") or "").strip():
        out["descricao"] = out["resumo"]
    return out


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
    subset = [_enrich_row(it) for it in all_items if _matches(it)]
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
    consolidado: Dict[str, Any] = {
        "fonte": SOURCE_ID,
        "nome_exibicao": "DARPA Research Programs",
        "fonte_recurso": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "versao": "v2_tipos_explicitos",
        "origem": str(ORIGIN.relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(STD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "origem_totais": {
            "total_standardized_origem": len(all_items),
            "valido_filtrado": len(subset),
        },
        "subset": {
            "criterios": [
                "validacao_status=valido",
                "tipo_conteudo=pesquisa",
                "tipo_pesquisa=programa_pesquisa",
                "fonte_recurso=darpa_programs_research",
                "tipo_recurso=programa_estrategico",
                "tipo_oportunidade=pesquisa_estrategica",
                "fonte=DARPA",
            ],
            "escolhidos": len(subset),
        },
        "loader_dryrun": {
            "comando": " ".join(load_cmd),
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "would_upsert_pesquisa": load_summary.get("would_upsert_pesquisa"),
            "errors_count": load_summary.get("errors_count"),
            "pesquisa_tipo_pesquisa_filled": load_summary.get("pesquisa_tipo_pesquisa_filled"),
            "pesquisa_tipo_recurso_filled": load_summary.get("pesquisa_tipo_recurso_filled"),
            "pesquisa_tipo_oportunidade_filled": load_summary.get("pesquisa_tipo_oportunidade_filled"),
            "apply_status": load_summary.get("apply_status"),
        },
        "distribuicao_eixos_estrategicos": eixos,
        "observacao": (
            "Programas DARPA → public.pesquisa apenas (programa_pesquisa). "
            "DARPA News nunca deve ir para public.pesquisa. Apply não executado."
        ),
        "apply_staging": {"executado": False},
    }

    (OUT_BASE / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    ld = consolidado["loader_dryrun"]
    md = [
        "# DARPA Programs Research — subset válido v2",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **source_id:** `{SOURCE_ID}`",
        "",
        consolidado["observacao"],
        "",
        "## Loader dry-run",
        "",
        f"| Métrica | Valor |",
        f"|---------|------:|",
        f"| Subset | {len(subset)} |",
        f"| would_upsert_pesquisa | {ld.get('would_upsert_pesquisa')} |",
        f"| tipo_pesquisa preenchido | {ld.get('pesquisa_tipo_pesquisa_filled')} / {len(subset)} |",
        f"| tipo_recurso preenchido | {ld.get('pesquisa_tipo_recurso_filled')} / {len(subset)} |",
        f"| errors_count | {ld.get('errors_count')} |",
        "",
        "## Eixos",
        "",
    ]
    for k, v in sorted(eixos.items(), key=lambda x: (-x[1], x[0])):
        md.append(f"- `{k}`: {v}")
    md.append("")
    (OUT_BASE / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "subset": len(subset),
                "would_upsert_pesquisa": ld.get("would_upsert_pesquisa"),
                "tipo_pesquisa_filled": ld.get("pesquisa_tipo_pesquisa_filled"),
                "tipo_recurso_filled": ld.get("pesquisa_tipo_recurso_filled"),
                "errors_count": ld.get("errors_count"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    ok = (
        ld.get("would_upsert_pesquisa") == len(subset)
        and ld.get("pesquisa_tipo_pesquisa_filled") == len(subset)
        and ld.get("pesquisa_tipo_recurso_filled") == len(subset)
        and ld.get("errors_count") == 0
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
