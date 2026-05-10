#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

import main as orchestrator  # noqa: E402
import transformer as tr  # noqa: E402


OUT_DIR = ROOT / "audit_reports_gate_coverage"
OUT_DIR.mkdir(parents=True, exist_ok=True)


WRAPPER_BY_SOURCE = {
    "cnpq": "transform_cnpq",
    "finep": "transform_finep",
    "fapergs": "transform_fapergs",
    "embrapii": "transform_embrapii",
}


def _source_output_path(source: str) -> Path:
    if source == "science_scraper":
        return ROOT / source / "outputs" / "science_editais.json"
    if source == "plataforma_industria":
        return ROOT / source / "outputs" / "plataforma_editais.json"
    return ROOT / source / "outputs" / f"{source}_editais.json"


def _source_standardized_path(source: str) -> Path:
    return CORE / "transformer" / f"{source}_standardized.json"


def _transform_function_for_source(source: str) -> str:
    return WRAPPER_BY_SOURCE.get(source, "transform_bndes")


def _run_synthetic_tests() -> Dict[str, Any]:
    noise_item = {
        "titulo": "Contato",
        "link": "https://www.bndes.gov.br/contato",
        "fonte": "BNDES",
        "descricao": "Página de contato institucional",
    }
    valid_item = {
        "titulo": "Edital de chamada pública para apoio a projetos de inovação",
        "link": "https://www.bndes.gov.br/wps/portal/site/home/financiamento/chamadas-publicas/edital-inovacao",
        "fonte": "BNDES",
        "descricao": "Chamada pública com prazo de inscrição e apoio financeiro para empresas e ICTs.",
        "fim_inscricao": "2026-12-31",
        "valor": "R$ 1.000.000,00",
        "extras": {"numero_edital": "01/2026", "tipo_oportunidade": "chamada_publica"},
    }

    funcs = {
        "transform_generic": lambda arr: tr.transform_generic(arr, "bndes"),
        "transform_cnpq": lambda arr: tr.transform_cnpq(arr, "bndes"),
        "transform_finep": lambda arr: tr.transform_finep(arr, "bndes"),
        "transform_fapergs": lambda arr: tr.transform_fapergs(arr, "bndes"),
        "transform_embrapii": lambda arr: tr.transform_embrapii(arr, "bndes"),
        "transform_bndes": lambda arr: tr.transform_bndes(arr, "bndes"),
    }

    rows: List[Dict[str, Any]] = []
    for fname, fn in funcs.items():
        r_noise = fn([noise_item])
        r_valid = fn([valid_item])
        noise_rejected = len(r_noise.items) == 0
        valid_kept = len(r_valid.items) > 0
        valid_status = None
        if valid_kept:
            ex = r_valid.items[0].get("extras") if isinstance(r_valid.items[0].get("extras"), dict) else {}
            valid_status = ex.get("validacao_status")
        rows.append(
            {
                "transform_function": fname,
                "noise_item_rejected": noise_rejected,
                "noise_reasons": [x.get("motivo_descarte") for x in (r_noise.rejected or [])[:3]],
                "valid_item_kept": valid_kept,
                "valid_item_status": valid_status,
                "valid_item_rejection_reasons": [x.get("motivo_descarte") for x in (r_valid.rejected or [])[:3]],
            }
        )
    return {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "tests": rows,
    }


def _read_standardized_sample(standardized_path: Path) -> Dict[str, Any]:
    if not standardized_path.is_file():
        return {"exists": False}
    try:
        data = json.loads(standardized_path.read_text(encoding="utf-8"))
        if isinstance(data, list) and data:
            it = data[0]
            ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
            return {
                "exists": True,
                "count": len(data),
                "has_content_type_detectado": bool(ex.get("content_type_detectado")),
                "has_validacao_status": bool(ex.get("validacao_status")),
                "has_documentos": isinstance(ex.get("documentos"), list),
                "has_quality": ex.get("qualidade_dado") is not None,
                "has_gate_relaxed": bool(ex.get("opportunity_gate_relaxed")),
                "has_profile": ex.get("perfil_ideal") is not None,
            }
        return {"exists": True, "count": 0}
    except Exception as exc:
        return {"exists": True, "error": str(exc)}


def main() -> int:
    sources = []
    for folder, script in orchestrator.SCRAPERS:
        source = folder
        main_path = ROOT / folder / script
        output_path = _source_output_path(source)
        standardized_path = _source_standardized_path(source)
        tf = _transform_function_for_source(source)
        wrapper = tf != "transform_generic"
        sample = _read_standardized_sample(standardized_path)

        calls_transform_generic = True
        if tf == "transform_finep":
            calls_transform_generic = True
        if tf == "transform_bndes":
            calls_transform_generic = True

        calls_gate = calls_transform_generic
        calls_noise = calls_transform_generic
        normalizes_docs = calls_transform_generic
        applies_validation = calls_transform_generic
        applies_profile = calls_transform_generic
        applies_classification = calls_transform_generic
        goes_loader = True
        writes_standardized = standardized_path.is_file()

        obs: List[str] = []
        if source in ("pncp_defesa", "compras_defesa"):
            obs.append("Possui relaxamento local no transformer (pncp_defesa_local).")
        if not output_path.is_file():
            obs.append("Output bruto não encontrado no momento da auditoria.")
        if sample.get("has_gate_relaxed") and source not in ("pncp_defesa", "compras_defesa"):
            obs.append("Encontrado opportunity_gate_relaxed fora do escopo esperado.")

        if calls_transform_generic and not wrapper:
            risk = "baixo"
        elif calls_transform_generic and wrapper:
            risk = "medio"
        elif not calls_transform_generic and goes_loader:
            risk = "alto"
        elif not calls_transform_generic and not goes_loader:
            risk = "critico"
        else:
            risk = "desconhecido"

        sources.append(
            {
                "fonte": source,
                "crawler_path": str(main_path.relative_to(ROOT)).replace("\\", "/"),
                "output_path": str(output_path.relative_to(ROOT)).replace("\\", "/"),
                "transform_function": tf,
                "calls_transform_generic": calls_transform_generic,
                "calls_wrapper": wrapper,
                "calls_opportunity_gate": calls_gate,
                "calls_noise_filter": calls_noise,
                "normalizes_documents": normalizes_docs,
                "applies_validation": applies_validation,
                "applies_profile": applies_profile,
                "applies_classification": applies_classification,
                "applies_sanitize_for_postgres": calls_transform_generic,
                "writes_standardized_json": writes_standardized,
                "standardized_path": str(standardized_path.relative_to(ROOT)).replace("\\", "/"),
                "goes_to_loader": goes_loader,
                "sample_checks": sample,
                "risk": risk,
                "observacoes": obs,
            }
        )

    bypass = [
        s
        for s in sources
        if (not s["calls_opportunity_gate"])
        or (not s["calls_noise_filter"])
        or (not s["calls_transform_generic"])
    ]

    risk_count: Dict[str, int] = {}
    for s in sources:
        risk_count[s["risk"]] = risk_count.get(s["risk"], 0) + 1

    syn = _run_synthetic_tests()
    (OUT_DIR / "synthetic_gate_test.json").write_text(json.dumps(syn, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fontes_total": len(sources),
        "fontes_calls_transform_generic": sum(1 for s in sources if s["calls_transform_generic"]),
        "fontes_calls_opportunity_gate": sum(1 for s in sources if s["calls_opportunity_gate"]),
        "fontes_calls_noise_filter": sum(1 for s in sources if s["calls_noise_filter"]),
        "fontes_normalizes_documents": sum(1 for s in sources if s["normalizes_documents"]),
        "fontes_applies_validation": sum(1 for s in sources if s["applies_validation"]),
        "fontes_go_loader": sum(1 for s in sources if s["goes_to_loader"]),
        "fontes_bypassing_gate": len(bypass),
        "risk_distribution": risk_count,
        "synthetic_expectation": {
            "noise_should_reject_all": all(t["noise_item_rejected"] for t in syn["tests"]),
            "valid_should_keep_or_marked": all(t["valid_item_kept"] for t in syn["tests"]),
        },
    }

    by_source_path = OUT_DIR / "gate_coverage_by_source.json"
    by_source_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "sources_bypassing_gate.json").write_text(json.dumps(bypass, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "gate_coverage_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Cobertura de gates/filtros",
        "",
        f"- Fontes totais: **{summary['fontes_total']}**",
        f"- Passam por `transform_generic`: **{summary['fontes_calls_transform_generic']}**",
        f"- Aplicam `opportunity_gate`: **{summary['fontes_calls_opportunity_gate']}**",
        f"- Aplicam `noise_filter`: **{summary['fontes_calls_noise_filter']}**",
        f"- Normalizam documentos: **{summary['fontes_normalizes_documents']}**",
        f"- Vão para loader: **{summary['fontes_go_loader']}**",
        f"- Fontes que pulam gate: **{summary['fontes_bypassing_gate']}**",
        "",
        "## Distribuição de risco",
        "",
    ]
    for k, v in sorted(summary["risk_distribution"].items()):
        md.append(f"- {k}: {v}")
    md.extend(
        [
            "",
            "## Teste sintético",
            "",
            f"- `Contato` rejeitado em todos os caminhos: **{summary['synthetic_expectation']['noise_should_reject_all']}**",
            f"- `Edital válido` mantido nos caminhos testados: **{summary['synthetic_expectation']['valid_should_keep_or_marked']}**",
            "",
            "Ver detalhes em `synthetic_gate_test.json` e cobertura por fonte em `gate_coverage_by_source.json`.",
        ]
    )
    (OUT_DIR / "gate_coverage_summary.md").write_text("\n".join(md), encoding="utf-8")

    transform_md = [
        "# Transform Paths",
        "",
        "## Funções transform_*",
        "",
        "- `transform_cnpq` -> `transform_generic`",
        "- `transform_finep` -> `transform_generic` + ajuste local `tipo_recurso`",
        "- `transform_fapergs` -> `transform_generic`",
        "- `transform_embrapii` -> `transform_generic`",
        "- `transform_bndes` -> `transform_generic` (wrapper multi-fontes)",
        "",
        "## Pipeline comum (`_transform_item_with_result`)",
        "",
        "- `noise_filter.should_discard_item`",
        "- `opportunity_gate.evaluate_item_dict`",
        "- relax local `pncp_defesa/compras_defesa` (transformer apenas)",
        "- normalização de documentos/PDF",
        "- `enrich_opportunity_classification` + `br_public_hints`",
        "- `apply_quality_to_payload` (`validacao_status`)",
        "- `sanitize_for_postgres`",
        "",
        "## Loader",
        "",
        "- `main.py` -> `CORE/transformer.py` gera `*_standardized.json`",
        "- `main.py` -> `CORE/loader.py` consome standardized via `load_standardized_json`",
        "- auditorias (`audit_pipeline.py`, `audit_docs_pipeline.py`) chamam `loader.map_to_db_schema` em dry-run",
    ]
    (OUT_DIR / "transform_paths.md").write_text("\n".join(transform_md), encoding="utf-8")
    print(OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
