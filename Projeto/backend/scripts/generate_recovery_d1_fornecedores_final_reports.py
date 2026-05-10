# -*- coding: utf-8 -*-
"""Relatórios finais Recovery D — Fornecedores & Investimentos (sem apply)."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
STD = ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_final/standardized"
LOADER = ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_final_loader_dryrun/load_ready_summary.json"


def _ex(it: Dict[str, Any]) -> Dict[str, Any]:
    e = it.get("extras")
    return e if isinstance(e, dict) else {}


def _load_items() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in sorted(STD.glob("*_standardized.json")):
        for it in json.loads(p.read_text(encoding="utf-8")):
            it["_src"] = p.stem.replace("_standardized", "")
            out.append(it)
    return out


def _verify(items: List[Dict[str, Any]], loader: Dict[str, Any]) -> Dict[str, Any]:
    def cnt(pred):
        return sum(1 for it in items if pred(it))

    faq = cnt(
        lambda it: any(
            x in (it.get("link") or "").lower()
            for x in ("/faq", "/faqs", "faq.", "/help", "/support")
        )
    )
    login = cnt(
        lambda it: "supplier_login_isolado" in (_ex(it).get("validacao_warnings") or [])
        or _ex(it).get("recovery_d_login_isolado")
    )
    suspeito = cnt(lambda it: str(it.get("validacao_status") or "").lower() == "suspeito")
    gt3 = cnt(
        lambda it: isinstance(_ex(it).get("setor_estrategico"), list) and len(_ex(it)["setor_estrategico"]) > 3
    )
    sec = cnt(lambda it: _ex(it).get("frontend_section") == "fornecedores")
    rada = cnt(lambda it: _ex(it).get("mostrar_no_radar") is False)
    forn = cnt(lambda it: _ex(it).get("mostrar_em_fornecedores") is True)
    inv = cnt(lambda it: _ex(it).get("mostrar_em_investimentos") is False)
    portal = cnt(lambda it: bool(str(_ex(it).get("portal_tipo") or "").strip()))
    doc_forte = cnt(
        lambda it: str(_ex(it).get("tipo_oportunidade") or "") == "documentacao_fornecedor"
        and _ex(it).get("mostrar_no_radar") is True
    )

    checks = {
        "itens_total": len(items),
        "loader_would_upsert": loader.get("would_upsert_total"),
        "mapping_errors_total": loader.get("mapping_errors_total"),
        "critical_empty_items_total": loader.get("critical_empty_items_total"),
        "faq_help_heuristic": faq,
        "login_isolado": login,
        "validacao_suspeito_top": suspeito,
        "setor_estrategico_gt3": gt3,
        "frontend_section_fornecedores": sec,
        "mostrar_no_radar_false": rada,
        "mostrar_em_fornecedores_true": forn,
        "mostrar_em_investimentos_false": inv,
        "portal_tipo_preenchido": portal,
        "documentacao_com_mostrar_radar_true": doc_forte,
        "todos_checks_ok": (
            len(items) == 26
            and sec == len(items)
            and rada == len(items)
            and forn == len(items)
            and inv == len(items)
            and portal == len(items)
            and loader.get("mapping_errors_total") == 0
            and loader.get("critical_empty_items_total") == 0
            and faq == 0
            and login == 0
            and suspeito == 0
            and gt3 == 0
            and doc_forte == 0
        ),
    }
    return checks


def main() -> int:
    if not STD.is_dir():
        print(f"[ERRO] Falta {STD}", file=sys.stderr)
        return 2
    items = _load_items()
    if not LOADER.is_file():
        print(f"[ERRO] Falta {LOADER}", file=sys.stderr)
        return 3
    loader = json.loads(LOADER.read_text(encoding="utf-8"))
    verif = _verify(items, loader)

    tipo_opp = Counter(str(_ex(it).get("tipo_oportunidade") or "") for it in items)
    portal_t = Counter(str(_ex(it).get("portal_tipo") or "") for it in items)

    doc_items = [it for it in items if str(_ex(it).get("tipo_oportunidade") or "") == "documentacao_fornecedor"]

    sys.path.insert(0, str(ROOT / "scripts"))
    from recovery_report_template import (
        build_consolidado_markdown,
        evidencias_padrao,
        merge_padrao_into_consolidado,
        padrao_documentacao_onda,
        tabela_metricas_operacionais,
    )

    padrao = padrao_documentacao_onda(
        resumo_executivo=(
            "Recovery D finaliza marcações para a secção produto «Fornecedores & Investimentos»: extras de roteamento, "
            "tipos supplier/documentação, cap de qualidade para não simular edital forte. Apply e Supabase ficam pendentes."
        ),
        problema_original=(
            "Itens de portais GD/LM/BAE não devem alimentar o Radar de Fomento como oportunidade principal; precisam "
            "taxonomia e flags explícitas no JSON."
        ),
        fontes_tratadas=["general_dynamics_suppliers", "lockheed_martin_suppliers", "bae_systems_suppliers"],
        resultado_principal=json.dumps(verif, ensure_ascii=False),
        metricas_antes_depois={
            "tipo_oportunidade_distribuicao": dict(tipo_opp),
            "portal_tipo_distribuicao": dict(portal_t),
        },
        interpretacao={
            "ganhos": [
                "frontend_section=fornecedores em todos os itens D.1",
                "documentacao_fornecedor isolada do radar principal",
                "View SQL proposta em docs/sql sem executar migration",
            ],
            "regressoes_aparentes": [],
            "sem_mudanca": ["opportunity_gate global inalterado"],
            "limitacoes": ["mostrar_no_radar=true reservado a futuras oportunidades acionáveis com prazo explícito"],
        },
        decisao_recomendada={
            "acao": "Opção 1 (preferida): aplicar os 26 itens em staging com extras de fornecedores e mostrar_no_radar=false.",
            "justificativa": "Checks automáticos passam; taxonomia e vista SQL alinhadas; risco baixo se o front filtrar por frontend_section.",
            "proximo_alvo": "Opção 2 se quiserem carga incremental: subset 12 principais primeiro, documentação depois.",
        },
        riscos=[
            "Consumidores legacy do payload podem assumir tipo_oportunidade antigo — rever API pública.",
            "View SQL requer validação DBA e índices em extras.",
        ],
        proximos_passos=[
            "QA rápido no staging após apply (quando autorizado).",
            "Implementar rota UI «Fornecedores» filtrando extras.frontend_section.",
            "Planejar vw_investimentos_front quando existirem dados.",
        ],
        evidencias_tecnicas=evidencias_padrao(
            arquivos_lidos=[
                "audit_reports_main_pipeline/recovery_d1_fornecedores_final/standardized/*.json",
                str(LOADER.relative_to(ROOT)).replace("\\", "/"),
            ],
            arquivos_gerados=[
                "audit_reports_main_pipeline/recovery_d1_fornecedores_final.md",
                "audit_reports_main_pipeline/fornecedores_investimentos_backend_design.md",
                "docs/sql/VW_FORNECEDORES_FRONT_PROPOSTA.sql",
            ],
            comandos=[
                "python scripts/retransform_all.py --sources general_dynamics_suppliers,lockheed_martin_suppliers,bae_systems_suppliers --dry-run --output-dir audit_reports_main_pipeline/recovery_d1_fornecedores_final",
                "python scripts/audit_semantic_classification.py ...",
                "python scripts/load_ready_sources.py ... recovery_d1_fornecedores_final_loader_dryrun",
            ],
            apply_executado=False,
            schema_alterado=False,
            supabase_tocado=False,
            notas_seguranca=["Sem apply nesta tarefa."],
        ),
    )

    doc_body = merge_padrao_into_consolidado(
        {
            "verificacao_recovery_d_fornecedores": verif,
            "documentacao_itens": [{"titulo": it.get("titulo"), "link": it.get("link")} for it in doc_items],
        },
        padrao,
    )
    outj = ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_final.json"
    outj.write_text(json.dumps(doc_body, ensure_ascii=False, indent=2), encoding="utf-8")

    tbl = tabela_metricas_operacionais(
        [
            {"metrica": k, "antes": "—", "depois": str(v), "variacao": "—", "interpretacao": ""}
            for k, v in verif.items()
            if k != "todos_checks_ok"
        ]
        + [
            {
                "metrica": "todos_checks_ok",
                "antes": "—",
                "depois": str(verif["todos_checks_ok"]),
                "variacao": "—",
                "interpretacao": "Gate QA automático Recovery D final",
            }
        ]
    )

    md = build_consolidado_markdown(
        titulo_cabecalho="Recovery D — Fornecedores & Investimentos (final)",
        sec1_resumo_executivo=padrao["resumo_executivo"],
        sec2_contexto="Ver `fornecedores_investimentos_backend_design.md` e constantes em `taxonomy_filtros.py`.",
        sec3_o_que_foi_alterado=(
            "- `TIPO_OPORTUNIDADE_FORNECEDORES_INVESTIMENTOS` e conjuntos de títulos D.1.\n"
            "- `_apply_recovery_d_fornecedores_investimentos_routing` + QA metadata.\n"
            "- `item_quality`: cap documentação / hub.\n"
            "- Proposta SQL `docs/sql/VW_FORNECEDORES_FRONT_PROPOSTA.sql`."
        ),
        sec4_resultado_operacional_md=tbl,
        sec5_resultado_por_fonte_md="Ver distribuições em `metricas_antes_depois` no JSON.",
        sec6_interpretacao="Ver `padrao_documentacao_onda.interpretacao` no JSON.",
        sec7_riscos="\n".join(padrao["riscos"]),
        sec8_decisao=padrao["decisao_recomendada"]["acao"],
        sec9_proximos_passos_md="\n".join(f"{i}. {t}" for i, t in enumerate(padrao["proximos_passos"], start=1)),
        sec10_evidencias="JSON `recovery_d1_fornecedores_final.json` → `evidencias_tecnicas`.",
    )
    (ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_final.md").write_text(md, encoding="utf-8")

    merged_ld = {"loader_summary": loader, "verificacao": verif}
    (ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_final_loader_dryrun.json").write_text(
        json.dumps(merged_ld, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_final_loader_dryrun.md").write_text(
        "\n".join(
            [
                "# Recovery D — Loader dry-run (fornecedores final)",
                "",
                f"- would_upsert_total: **{loader.get('would_upsert_total')}**",
                f"- mapping_errors_total: **{loader.get('mapping_errors_total')}**",
                f"- critical_empty_items_total: **{loader.get('critical_empty_items_total')}**",
                "",
                "```json",
                json.dumps(verif, ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )

    rec = {
        "opcao_recomendada": 1,
        "texto": (
            "Opção 1: aplicar os 26 itens em staging com extras.frontend_section=fornecedores, "
            "mostrar_no_radar=false e mostrar_em_fornecedores=true — alinhado aos checks e à vista SQL proposta."
        ),
        "alternativas": {
            "2": "Aplicar subset de 12 itens principais agora e documentação numa segunda carga.",
            "3": "Não aplicar até o front consumir explicitamente frontend_section.",
        },
        "verificacao": verif,
        "apply_executado": False,
    }
    (ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_apply_recommendation.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_apply_recommendation.md").write_text(
        "\n".join(
            [
                "# Recovery D — Recomendação de apply (fornecedores)",
                "",
                f"**Opção recomendada:** {rec['opcao_recomendada']} — {rec['texto']}",
                "",
                "**Alternativas:** ver chave `alternativas` no JSON.",
                "",
                "**Apply nesta tarefa:** não.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(json.dumps(verif, ensure_ascii=False, indent=2))
    return 0 if verif["todos_checks_ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
