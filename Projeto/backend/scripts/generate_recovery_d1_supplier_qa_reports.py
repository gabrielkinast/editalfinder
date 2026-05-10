# -*- coding: utf-8 -*-
"""
Gera relatórios Recovery D.1 (QA supplier portals) a partir do standardized + loader dry-run.
Não aplica alterações na base; só escreve ficheiros em audit_reports_main_pipeline/.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
STD_DIR = ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_qa/standardized"
LOADER_DIR = ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_qa_loader_dryrun"
OUT_BASE = ROOT / "audit_reports_main_pipeline"


def _extras(item: Dict[str, Any]) -> Dict[str, Any]:
    ex = item.get("extras")
    return ex if isinstance(ex, dict) else {}


def _rows_from_standardized() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if not STD_DIR.is_dir():
        raise FileNotFoundError(f"Missing standardized dir: {STD_DIR}")
    for path in sorted(STD_DIR.glob("*_standardized.json")):
        fonte_key = path.stem.replace("_standardized", "")
        data = json.loads(path.read_text(encoding="utf-8"))
        for i, item in enumerate(data):
            ex = _extras(item)
            rows.append(
                {
                    "idx": len(rows) + 1,
                    "fonte": fonte_key,
                    "titulo": item.get("titulo"),
                    "link": item.get("link"),
                    "tipo_oportunidade": ex.get("tipo_oportunidade") or item.get("tipo_oportunidade"),
                    "tipo_recurso": item.get("tipo_recurso") or ex.get("tipo_recurso"),
                    "validacao_status": item.get("validacao_status") or ex.get("validacao_status"),
                    "decisao_qa": ex.get("recovery_d1_decisao_qa", ""),
                    "motivo_qa": ex.get("recovery_d1_motivo_qa", ""),
                    "acao_recomendada": ex.get("recovery_d1_acao_recomendada", ""),
                }
            )
    return rows


def _verification(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    def cnt(pred):
        return sum(1 for it in items if pred(it))

    def row(item):
        ex = _extras(item)
        lk = (item.get("link") or "").lower()
        tit = str(item.get("titulo") or "").lower()
        vs = str(item.get("validacao_status") or ex.get("validacao_status") or "").lower()
        return lk, tit, vs, ex

    faq_like = cnt(
        lambda it: any(
            x in (it.get("link") or "").lower()
            for x in ("/faq", "/faqs", "faq.", "/help", "/support")
        )
        and "/supplier" not in (it.get("link") or "").lower()
    )
    login_strong = cnt(
        lambda it: ("supplier_login_isolado" in (_extras(it).get("validacao_warnings") or []))
        or _extras(it).get("recovery_d_login_isolado")
    )
    suspeito = cnt(lambda it: str(it.get("validacao_status") or "").lower() == "suspeito")
    gt3 = cnt(
        lambda it: isinstance(_extras(it).get("setor_estrategico"), list)
        and len(_extras(it)["setor_estrategico"]) > 3
    )
    generic_short = cnt(
        lambda it: str(it.get("titulo") or "").strip().lower()
        in ("suppliers", "supplier")
        and "hub" not in str(it.get("titulo") or "").lower()
    )
    caps_left = cnt(lambda it: "/capabilities/" in (it.get("link") or "").lower())
    lav_left = cnt(lambda it: "/lav" in (it.get("link") or "").lower() and "gdls.com" in (it.get("link") or "").lower())

    return {
        "itens_total": len(items),
        "faq_help_support_url_heuristic": faq_like,
        "login_isolado_warnings": login_strong,
        "validacao_suspeito_top_level": suspeito,
        "setor_estrategico_gt3": gt3,
        "titulo_generico_suppliers_sem_normalizacao": generic_short,
        "capabilities_na_colecao": caps_left,
        "gdls_lav_na_colecao": lav_left,
        "criterios_apply": {
            "sem_faq_help": faq_like == 0,
            "sem_login_isolado_forte": login_strong == 0,
            "sem_capabilities_fantasma": caps_left == 0,
            "sem_lav_produto": lav_left == 0,
            "suspeito_zero_ou_explicado": suspeito == 0,
            "mapping_loader_zero": True,
        },
    }


def main() -> int:
    all_items: List[Dict[str, Any]] = []
    for path in sorted(STD_DIR.glob("*_standardized.json")):
        all_items.extend(json.loads(path.read_text(encoding="utf-8")))

    qa_table = _rows_from_standardized()
    verification_flat = _verification(all_items)

    qa_doc = {
        "titulo": "Recovery D.1 — QA Supplier Portals",
        "nota_crawl": (
            "Recovery D.1: URLs Lockheed Martin fora do path /suppliers foram recusadas; "
            "em gdls.com mantêm-se apenas /suppliers/* e PDFs em /wp-content/; gd.com apenas /suppliers/*."
        ),
        "artefatos_lidos_recovery_d_prev": [
            "audit_reports_main_pipeline/recovery_d_suppliers_context.json",
            "audit_reports_main_pipeline/recovery_d_suppliers_loader_dryrun.json",
            "audit_reports_main_pipeline/recovery_d_suppliers_apply_recommendation.json",
            "audit_reports_main_pipeline/recovery_d_suppliers_deactivate_candidates.json",
            "audit_reports_main_pipeline/recovery_d_suppliers/standardized/*.json (baseline conceptual 28 itens antes de D.1)",
        ],
        "comparativo_recovery_d_linha_anterior": {
            "standardized_recovery_d_prev": 28,
            "standardized_recovery_d1_pos_pipeline": len(qa_table),
            "nota_delta": (
                "Menos linhas porque o crawl D.1 corta páginas de capability/who-we-are e produto GDLS fora de /suppliers; "
                "o PDF SCM continua filtrado pelo opportunity_gate no transformer (comportamento já visto)."
            ),
        },
        "itens_total": len(qa_table),
        "tabela_qa": qa_table,
        "verificacao_pos_pipeline": verification_flat,
    }
    (OUT_BASE / "recovery_d1_suppliers_qa.json").write_text(
        json.dumps(qa_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md_lines = [
        "# Recovery D.1 — QA Supplier Portals",
        "",
        "Leituras de contexto prévias (Recovery D): "
        "`recovery_d_suppliers_context.json`, `recovery_d_suppliers_loader_dryrun.json`, "
        "`recovery_d_suppliers_apply_recommendation.json`, `recovery_d_suppliers_deactivate_candidates.json`, "
        "e standardized Recovery D (~28 itens antes do recorte D.1).",
        "",
        qa_doc["nota_crawl"],
        "",
        f"**Baseline Recovery D (~28 standardized)** vs **Recovery D.1 atual: {len(qa_table)}** — ver `comparativo_recovery_d_linha_anterior` no JSON.",
        "",
        f"**Itens nesta tabela:** {len(qa_table)}",
        "",
        "## Verificação automática",
        "",
        "```json",
        json.dumps(verification_flat, ensure_ascii=False, indent=2),
        "```",
        "",
        "| # | Fonte | Título | tipo_op | validação | Decisão QA | Motivo | Ação recomendada |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for r in qa_table:
        tit = str(r["titulo"] or "").replace("|", "\\|")[:80]
        md_lines.append(
            "| {idx} | `{fonte}` | {tit} | `{to}` | `{vs}` | `{dq}` | {mot} | {acao} |".format(
                idx=r["idx"],
                fonte=r["fonte"],
                tit=tit,
                to=r.get("tipo_oportunidade") or "",
                vs=r.get("validacao_status") or "",
                dq=r.get("decisao_qa") or "",
                mot=str(r.get("motivo_qa") or "").replace("|", "\\|")[:120],
                acao=str(r.get("acao_recomendada") or "").replace("|", "\\|")[:120],
            )
        )
    md_lines.append("")
    (OUT_BASE / "recovery_d1_suppliers_qa.md").write_text("\n".join(md_lines), encoding="utf-8")

    loader_summary_path = LOADER_DIR / "load_ready_summary.json"
    if not loader_summary_path.is_file():
        print(f"[AVISO] Sem {loader_summary_path}", file=sys.stderr)
        loader = {}
    else:
        loader = json.loads(loader_summary_path.read_text(encoding="utf-8"))

    merged_loader = {
        "loader_summary": loader,
        "recovery_d1_verificacao": verification_flat,
        "mapping_errors_total": loader.get("mapping_errors_total"),
        "critical_empty_items_total": loader.get("critical_empty_items_total"),
    }
    (OUT_BASE / "recovery_d1_suppliers_qa_loader_dryrun.json").write_text(
        json.dumps(merged_loader, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lm = OUT_BASE / "recovery_d1_suppliers_qa_loader_dryrun.md"
    lm.write_text(
        "\n".join(
            [
                "# Recovery D.1 — Loader dry-run (QA)",
                "",
                f"- mapping_errors_total: **{loader.get('mapping_errors_total', '—')}**",
                f"- critical_empty_items_total: **{loader.get('critical_empty_items_total', '—')}**",
                f"- itens standardized: **{loader.get('itens_standardized_total', len(all_items))}**",
                "",
                "## Verificação Recovery D.1",
                "",
                "```json",
                json.dumps(verification_flat, ensure_ascii=False, indent=2),
                "```",
                "",
                "Ver também `load_ready_summary.md` na pasta do loader.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    pre_ok = (
        loader.get("mapping_errors_total") == 0
        and loader.get("critical_empty_items_total") == 0
        and verification_flat["faq_help_support_url_heuristic"] == 0
        and verification_flat["login_isolado_warnings"] == 0
        and verification_flat["validacao_suspeito_top_level"] == 0
        and verification_flat["capabilities_na_colecao"] == 0
        and verification_flat["gdls_lav_na_colecao"] == 0
        and verification_flat["titulo_generico_suppliers_sem_normalizacao"] == 0
    )

    apply_doc = {
        "apply_autorizado": False,
        "pronto_para_review_apply_human": pre_ok,
        "motivo_se_nao_pronto": None if pre_ok else "Critérios D.1 automáticos falham ou pendências na coleção.",
        "pre_check_recuperacao_d1": {
            "mapping_errors_total_zero": loader.get("mapping_errors_total") == 0,
            "critical_empty_zero": loader.get("critical_empty_items_total") == 0,
            "sem_faq_help": verification_flat["faq_help_support_url_heuristic"] == 0,
            "sem_login_isolado": verification_flat["login_isolado_warnings"] == 0,
            "suspeito_explicado": verification_flat["validacao_suspeito_top_level"] == 0,
            "sem_capabilities_residuais": verification_flat["capabilities_na_colecao"] == 0,
            "sem_lav_residuo": verification_flat["gdls_lav_na_colecao"] == 0,
            "titulos_genericos_normalizados": verification_flat["titulo_generico_suppliers_sem_normalizacao"] == 0,
        },
        "recomendacao": (
            "Critérios automáticos D.1 satisfeitos — falta apenas confirmação humana e decisão de janela para apply "
            "(esta ferramenta não executa apply)."
            if pre_ok
            else "Corrigir coleção ou heurísticas até os pre-checks ficarem verdes; só então agendar apply manual."
        ),
        "candidatos_ativo_false_nao_aplicados": [
            r
            for r in qa_table
            if r.get("decisao_qa") == "candidato_ativo_false"
        ],
    }
    (OUT_BASE / "recovery_d1_suppliers_qa_apply_recommendation.json").write_text(
        json.dumps(apply_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    apply_md = [
        "# Recovery D.1 — Recomendação de apply",
        "",
        "**apply:** não executado nesta onda (política Recovery D.1).",
        "",
        f"**Pronto para review humano pré-apply:** {'sim' if apply_doc.get('pronto_para_review_apply_human') else 'não'}",
        "",
        f"Detalhe: {apply_doc.get('motivo_se_nao_pronto') or 'Pre-checks automáticos OK.'}",
        "",
        "## Pre-checks",
        "",
        "```json",
        json.dumps(apply_doc["pre_check_recuperacao_d1"], ensure_ascii=False, indent=2),
        "```",
        "",
        apply_doc["recomendacao"],
        "",
    ]
    (OUT_BASE / "recovery_d1_suppliers_qa_apply_recommendation.md").write_text(
        "\n".join(apply_md), encoding="utf-8"
    )

    print("Escrito:", OUT_BASE / "recovery_d1_suppliers_qa.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
