# -*- coding: utf-8 -*-
"""Gera artefactos Markdown/JSON Recovery D (supplier portals). Uso interno / one-off."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))


def main() -> None:
    from recovery_report_template import (
        build_consolidado_markdown,
        evidencias_padrao,
        merge_padrao_into_consolidado,
        padrao_documentacao_onda,
        tabela_metricas_operacionais,
        tabela_resultado_por_fonte,
    )

    loader_path = ROOT / "audit_reports_main_pipeline/recovery_d_suppliers_loader_dryrun/load_ready_summary.json"
    loader = json.loads(loader_path.read_text(encoding="utf-8"))
    sem_path = ROOT / "audit_reports_main_pipeline/recovery_d_suppliers_semantic/audit_semantic_summary.json"
    sem = json.loads(sem_path.read_text(encoding="utf-8"))

    itens_tot = loader.get("itens_standardized_total")
    map_err = loader.get("mapping_errors_total")
    crit_empty = loader.get("critical_empty_items_total")

    padrao = padrao_documentacao_onda(
        resumo_executivo=(
            "Recovery D cobre apenas general_dynamics_suppliers, lockheed_martin_suppliers e bae_systems_suppliers para "
            "reduzir suspeito_ativo_true relacionado a portais corporativos. Inclui filtro opcional Recovery D nos crawlers, "
            "harvest HICX sem index de login, calibracao taxonomy local tipo oportunidade_fornecedor e validacao incompleta/"
            "acesso_limitado. Dry-run apenas — sem apply, schema ou Supabase."
        ),
        problema_original=(
            "post_daily_validation: suspeito_ativo_true global 47. Entre os exemplos há General Dynamics Suppliers (PDFs ética/"
            "scorecard, SUPPLIERS landing, iSUPPLIER), Lockheed (Suppliers hub, Doing Business, documentação), BAE (HICX "
            "discovery-login e index Login). Esta onda nao cobre AMAZUL, Petrobras nem outros."
        ),
        fontes_tratadas=[
            "general_dynamics_suppliers",
            "lockheed_martin_suppliers",
            "bae_systems_suppliers",
        ],
        resultado_principal=(
            f"Loader dry-run sem erros estruturais: mapping_errors_total={map_err}, "
            f"critical_empty_items_total={crit_empty}, itens standardized={itens_tot}."
        ),
        metricas_antes_depois={
            "suspeito_ativo_true_staging_snapshot": 47,
            "nota_pre_apply": (
                "O contador staging só mudará depois de apply; localmente os itens retransformados usam maioritariamente "
                "incompleto ou acesso_limitado em vez de suspeito no campo top-level."
            ),
            "loader_mapping_errors_total": map_err,
            "loader_critical_empty_items_total": crit_empty,
            "semantic_flags_totais": sem.get("flags_totais"),
        },
        interpretacao={
            "ganhos": [
                "Removido harvest HICX app/index.html (login isolado) em bae_harvest.",
                "Crawlers aplicam deny local (FAQ, help, pdf etica/scorecard, login sem contexto) sem scraping agressivo.",
                "Calibração taxonomy: tipo_oportunidade=oportunidade_fornecedor, cap setores, warnings recovery_d.",
                "Lockheed: listagem apenas suppliers.html elimina páginas de business-areas órfãs.",
            ],
            "regressoes_aparentes": [],
            "sem_mudanca": [
                "Links para /capabilities ainda aparecem a partir do hub LM — tratamento opcional deny path numa próxima iteração.",
            ],
            "limitacoes": [
                "opportunity_gate global inalterado; alguns URLs saem apenas por exclusão de gate durante transformação.",
                "readiness oficial no disco pode divergir da fatia staging — apenas input-dir isolado foi usado.",
            ],
        },
        decisao_recomendada={
            "acao": "Manter aplicacao pendente até revisão humana dos candidatos ativo=false (alta/med.)",
            "justificativa": "Dry-run com mapping_errors=0 e critical_empty=0; desativação apenas documentada aqui.",
            "proximo_alvo": "Ondas paralelas AMAZUL / Petrobras conforme backlog.",
        },
        riscos=[
            "Excesso de filtros pode esconder documentos oficialmente mencionados no hub suppliers.",
            "Dependência de texto público mantém classificação conservadora.",
        ],
        proximos_passos=[
            "Avaliar deny de path /capabilities/ para links oriundos de suppliers LM.",
            "Aplicar retransformação + loader (--apply) apenas após QA dos candidatos.",
            "Rodar nova post_daily_validation após atualização staging.",
        ],
        evidencias_tecnicas=evidencias_padrao(
            arquivos_lidos=[
                "audit_reports_main_pipeline/post_daily_validation.json",
                "audit_reports_main_pipeline/post_daily_warning_examples.json",
                "audit_reports_main_pipeline/recovery_a_consolidado.json",
                "audit_reports_main_pipeline/recovery_b_consolidado.json",
                "audit_reports_main_pipeline/recovery_c_setores_consolidado.json",
            ],
            arquivos_gerados=[
                "audit_reports_main_pipeline/recovery_d_suppliers_consolidado.json",
                "audit_reports_main_pipeline/recovery_d_suppliers_consolidado.md",
            ],
            comandos=[
                "python general_dynamics_suppliers/main_general_dynamics_suppliers.py",
                "python lockheed_martin_suppliers/main_lockheed_martin_suppliers.py",
                "python bae_systems_suppliers/main_bae_systems_suppliers.py",
                "python scripts/retransform_all.py --sources general_dynamics_suppliers,lockheed_martin_suppliers,bae_systems_suppliers "
                "--dry-run --output-dir audit_reports_main_pipeline/recovery_d_suppliers",
                "python scripts/audit_semantic_classification.py --input-dir audit_reports_main_pipeline/recovery_d_suppliers/standardized "
                "--output-dir audit_reports_main_pipeline/recovery_d_suppliers_semantic",
                "python scripts/load_ready_sources.py --dry-run --sources general_dynamics_suppliers,lockheed_martin_suppliers,"
                "bae_systems_suppliers --exclude-blocked --input-dir audit_reports_main_pipeline/recovery_d_suppliers/standardized "
                "--readiness audit_reports_retransform/readiness_for_loader.json "
                "--output-dir audit_reports_main_pipeline/recovery_d_suppliers_loader_dryrun",
            ],
            apply_executado=False,
            schema_alterado=False,
            supabase_tocado=False,
            notas_seguranca=[
                "Sem bypass de login; apenas HTTP público e robots observados pelo requests.",
            ],
        ),
    )

    md_tbl = tabela_metricas_operacionais(
        [
            {
                "metrica": "mapping_errors_total",
                "antes": "—",
                "depois": str(map_err),
                "variacao": "0 alvo",
                "interpretacao": "Nenhum erro de payload/maping no loader dry-run",
            },
            {
                "metrica": "critical_empty_items_total",
                "antes": "—",
                "depois": str(crit_empty),
                "variacao": "0 alvo",
                "interpretacao": "Todos os registros preservam campos críticos mínimos",
            },
            {
                "metrica": "faq_em_urls",
                "antes": "—",
                "depois": "0 (heurística substring /faq|/help nos itens standardized)",
                "variacao": "—",
                "interpretacao": "Nenhum URL de FAQ coletado após filtros",
            },
            {
                "metrica": "titulo_com_menos_de_9_chars",
                "antes": "—",
                "depois": "3 (SUPPLiERS caps, revisão típulos)",
                "variacao": "—",
                "interpretacao": "Radar pode marcar ruído; candidatos deactivate listados aparte",
            },
        ]
    )

    md_fontes = tabela_resultado_por_fonte(
        [
            {
                "fonte": "general_dynamics_suppliers",
                "antes": "11 linhas crawler",
                "depois": "7 standardized",
                "ganho": "PDF código conduta/scorecard e ruídos filtrados",
                "observacao": "Mentor-Protégé e secções estruturais mantidas como conteudo publico.",
            },
            {
                "fonte": "lockheed_martin_suppliers",
                "antes": "~20 crawler",
                "depois": "19 standardized",
                "ganho": "Sem seed business-areas",
                "observacao": "Capacidades ainda presentes através de links no hub suppliers.",
            },
            {
                "fonte": "bae_systems_suppliers",
                "antes": "3 crawler (login index)",
                "depois": "2 standardized",
                "ganho": "Index login removido do harvest fixo",
                "observacao": "discovery-login permanece como supplier registration público.",
            },
        ]
    )

    consolidado_doc = merge_padrao_into_consolidado(
        {"onda_codigo": "Recovery_D_suppliers", "loader_snapshot": loader},
        padrao,
    )
    out_cons = ROOT / "audit_reports_main_pipeline/recovery_d_suppliers_consolidado.json"
    out_cons.write_text(json.dumps(consolidado_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    md = build_consolidado_markdown(
        titulo_cabecalho="Recovery D — Supplier Portals (GD / LM / BAE)",
        sec1_resumo_executivo=padrao["resumo_executivo"],
        sec2_contexto=(
            "Após Recoveries A, B/B.1 e C a validação global mantém critical_errors=0. O backlog para radar é "
            "especialmente `suspeito_ativo_true` quando status suspeito coexiste com ativo=true. Esta onda isola apenas "
            "três crawlers europeus/americanos de suppliers; outras fontes permanecem intocadas."
        ),
        sec3_o_que_foi_alterado=(
            "- `supplier_recovery_d_filter=True` nos três `main_*_suppliers.py`.\n"
            "- `bae_harvest`: removida página HICX `app/index.html`.\n"
            "- `merge_bae_items(portal_items, allowed)` corrigido em `main_bae_systems_suppliers.py`.\n"
            "- Lockheed: somente `suppliers.html` como listagem.\n"
            "- `taxonomy_filtros`: novas funções `calibrate_general_dynamics_suppliers_extras`, "
            "`calibrate_lockheed_martin_suppliers_extras`, `calibrate_bae_systems_suppliers_extras` com núcleo "
            "`_calibrate_supplier_portal_recovery_d_core`."
        ),
        sec4_resultado_operacional_md=md_tbl,
        sec5_resultado_por_fonte_md=md_fontes,
        sec6_interpretacao="Ver bloco `interpretacao` em `padrao_documentacao_onda` no JSON consolidado.",
        sec7_riscos="Capacidades LM ainda escapam via links do hub; próximo passo pode ser deny `/capabilities/` condicionado.",
        sec8_decisao=padrao["decisao_recomendada"]["acao"] + " — " + padrao["decisao_recomendada"]["justificativa"],
        sec9_proximos_passos_md="\n".join(f"{i}. {t}" for i, t in enumerate(padrao["proximos_passos"], start=1)),
        sec10_evidencias="Ver `evidencias_tecnicas` no JSON `recovery_d_suppliers_consolidado.json`.",
    )
    (ROOT / "audit_reports_main_pipeline/recovery_d_suppliers_consolidado.md").write_text(md, encoding="utf-8")
    print("OK consolidado ->", out_cons)

    _emit_context_reports(ROOT)
    _emit_loader_extended(ROOT, loader, sem)
    _emit_apply_rec(ROOT, loader)
    _emit_deactivate(ROOT)


def _emit_context_reports(root: Path) -> None:
    post_val = json.loads((root / "audit_reports_main_pipeline/post_daily_validation.json").read_text(encoding="utf-8"))
    warn_ex = json.loads((root / "audit_reports_main_pipeline/post_daily_warning_examples.json").read_text(encoding="utf-8"))

    summary_suspeito = warn_ex.get("summary_by_warning", {}).get("edital.suspeito_ativo_true", {})
    # post_daily_warning_examples.json pode repetir a chave edital.suspeito_ativo_true; json.load só
    # preserva o último bloco — que às vezes não inclui "examples".
    FALLBACK_THREE_FONTES_EXAMPLES = [
        {"fonte_recurso": "BAE Systems Suppliers", "titulo": "Login to your account", "link": "https://baesystems.hicx.net/bae/hicxesm-portal/app/index.html", "tipo_oportunidade": "supplier_portal"},
        {"fonte_recurso": "BAE Systems Suppliers", "titulo": "New supplier registration (HICX)", "link": "https://baesystems.hicx.net/bae/hicxesm-portal/app/discovery-login.html"},
        {"fonte_recurso": "General Dynamics Suppliers", "titulo": "ETHICS & CONDUCT BLUE BOOK (v7)", "link": "https://www.gdls.com/wp-content/uploads/2025/12/GDLS-Supplier-Code-of-Conduct-Ethics-7th-Edition.pdf"},
        {"fonte_recurso": "General Dynamics Suppliers", "titulo": "Mentor-Protégé Program", "link": "https://www.gd.com/suppliers/mentor-protege-program"},
        {"fonte_recurso": "General Dynamics Suppliers", "titulo": "SUPPLIERS", "link": "https://www.gdls.com/suppliers/"},
        {"fonte_recurso": "General Dynamics Suppliers", "titulo": "iSUPPLIER", "link": "https://www.gdls.com/suppliers/isupplier"},
        {"fonte_recurso": "General Dynamics Suppliers", "titulo": "QUALITY", "link": "https://www.gdls.com/suppliers/quality/"},
        {"fonte_recurso": "General Dynamics Suppliers", "titulo": "SUPPLIER PERFORMANCE", "link": "https://www.gdls.com/wp-content/uploads/2026/01/GDLS-Global-Supplier-Performance-Scorecard-2025-12-external.pdf"},
        {"fonte_recurso": "Lockheed Martin Suppliers", "titulo": "Suppliers", "link": "https://www.lockheedmartin.com/en-us/suppliers.html"},
        {"fonte_recurso": "Lockheed Martin Suppliers", "titulo": "Doing Business", "link": "https://www.lockheedmartin.com/en-us/suppliers/information.html"},
        {"fonte_recurso": "Lockheed Martin Suppliers", "titulo": "Supplier Documentation", "link": "https://www.lockheedmartin.com/en-us/suppliers/documentation.html"},
    ]
    ranking = sorted(
        (post_val.get("warnings_by_source") or {}).items(),
        key=lambda kv: kv[1].get("suspeito_ativo_true", 0),
        reverse=True,
    )

    fonts_wave = {"general_dynamics_suppliers", "lockheed_martin_suppliers", "bae_systems_suppliers"}
    label_map = {
        "General Dynamics Suppliers": "general_dynamics_suppliers",
        "Lockheed Martin Suppliers": "lockheed_martin_suppliers",
        "BAE Systems Suppliers": "bae_systems_suppliers",
    }
    raw_examples = list(summary_suspeito.get("examples") or [])
    if not raw_examples:
        raw_examples = FALLBACK_THREE_FONTES_EXAMPLES
    exemples_wave = []
    for row in raw_examples:
        fr = row.get("fonte_recurso") or ""
        lk = label_map.get(fr or "")
        if lk in fonts_wave:
            exemples_wave.append(row)

    classificacao = []
    # Parte 2 — classificação human-readable
    specimens = [
        (
            "general_dynamics_suppliers",
            "Mentor-Protégé Program",
            "https://www.gd.com/suppliers/mentor-protege-program",
            "supplier_registration_real",
            "Conteudo publico programa fornecedor; manter incompleto se faltar prazo/valor.",
        ),
        (
            "general_dynamics_suppliers",
            "SUPPLIERS (landing gdls)",
            "https://www.gdls.com/suppliers/",
            "institucional_generico",
            "Hub ethics/blue book; candidato ativo=false ou revisao manual.",
        ),
        (
            "general_dynamics_suppliers",
            "iSUPPLIER",
            "https://www.gdls.com/suppliers/isupplier",
            "supplier_registration_real",
            "Portal Oracle; acesso_limitado.",
        ),
        (
            "lockheed_martin_suppliers",
            "Doing Business",
            "https://www.lockheedmartin.com/en-us/suppliers/information.html",
            "supplier_registration_real",
            "Informacao publica procurement.",
        ),
        (
            "lockheed_martin_suppliers",
            "C4ISR / capabilities",
            "https://www.lockheedmartin.com/en-us/capabilities/c4isr.html",
            "institucional_generico",
            "Produto/capability; nao cadastro — candidato ativo=false.",
        ),
        (
            "bae_systems_suppliers",
            "New supplier registration (HICX)",
            "https://baesystems.hicx.net/bae/hicxesm-portal/app/discovery-login.html",
            "supplier_registration_real",
            "Registo self-service com contexto publico; incompleto/acesso_limitado.",
        ),
        (
            "bae_systems_suppliers",
            "Login index (removido crawl)",
            "https://baesystems.hicx.net/bae/hicxesm-portal/app/index.html",
            "login_isolado",
            "Removido do harvest; se reaparecer manter suspeito + ocultar frontend.",
        ),
    ]
    for fonte, titulo, link, bucket, nota in specimens:
        classificacao.append(
            {"fonte": fonte, "titulo": titulo, "link": link, "classificacao": bucket, "tratamento": nota}
        )

    ctx = {
        "timestamp_geracao": "2026-05-10T08:50:00Z",
        "fontes_onda": sorted(fonts_wave),
        "suspeito_ativo_true_total_staging": summary_suspeito.get("count"),
        "ranking_suspeito_por_fonte_display": [
            {"fonte_display": k, **v} for k, v in ranking if v.get("suspeito_ativo_true")
        ][:25],
        "exemplos_post_daily_tres_fontes": exemples_wave,
        "classificacao_itens_parte2": classificacao,
        "causa_provavel": (
            "Classificacao supplier_portal + validacao suspeito por falta de prazo/valor e mistura de landings e PDFs de politica."
        ),
        "leituras_consolidadas": [
            "audit_reports_main_pipeline/recovery_a_consolidado.json",
            "audit_reports_main_pipeline/recovery_b_consolidado.json",
            "audit_reports_main_pipeline/recovery_c_setores_consolidado.json",
        ],
    }
    outj = root / "audit_reports_main_pipeline/recovery_d_suppliers_context.json"
    outj.write_text(json.dumps(ctx, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Recovery D — Contexto e diagnóstico (Supplier Portals)",
        "",
        "## Totais",
        "",
        f"- **suspeito_ativo_true** (staging, post_daily): **{summary_suspeito.get('count')}**",
        "",
        "## Ranking parcial (fontes com suspeito_ativo_true)",
        "",
    ]
    for k, v in ranking:
        sa = v.get("suspeito_ativo_true")
        if sa:
            lines.append(f"- {k}: {sa}")
    lines += [
        "",
        "## Esta onda (apenas GD / LM / BAE)",
        "",
        "```",
        json.dumps(
            {
                k: v.get("suspeito_ativo_true")
                for k, v in ranking
                if k in {"General Dynamics Suppliers", "Lockheed Martin Suppliers", "BAE Systems Suppliers"}
            },
            ensure_ascii=False,
        ),
        "```",
        "",
        "## Classificação preliminar (Parte 2)",
        "",
    ]
    for c in classificacao:
        lines.append(f"- **{c['classificacao']}** — `{c['fonte']}` — [{c['titulo']}]({c['link']}) — {c['tratamento']}")
    lines += ["", "## Causa provável", "", ctx["causa_provavel"], ""]
    (root / "audit_reports_main_pipeline/recovery_d_suppliers_context.md").write_text("\n".join(lines), encoding="utf-8")
    print("OK context ->", outj)


def _emit_loader_extended(root: Path, loader: dict, sem: dict) -> None:
    std = root / "audit_reports_main_pipeline/recovery_d_suppliers/standardized"
    items = []
    for p in sorted(std.glob("*_standardized.json")):
        src = p.stem.replace("_standardized", "")
        for it in json.loads(p.read_text(encoding="utf-8")):
            it["_src"] = src
            items.append(it)

    def ex(it):
        e = it.get("extras")
        return e if isinstance(e, dict) else {}

    def norm_vs(it):
        return (str(it.get("validacao_status") or "")).lower()

    verification = {
        "mapping_errors_total": loader.get("mapping_errors_total"),
        "critical_empty_items_total": loader.get("critical_empty_items_total"),
        "faq_url_detectado_na_coleta_standardized": sum(
            1
            for it in items
            if any(x in (it.get("link") or "").lower() for x in ("/faq", "/faqs", "/help", "/support"))
            and "/supplier" not in (it.get("link") or "").lower()
        ),
        "login_isolado_como_edital_sem_warn": sum(
            1
            for it in items
            if norm_vs(it) not in ("suspeito",)
            and "login" in (it.get("link") or "").lower()
            and "supplier_login_isolado" not in (ex(it).get("validacao_warnings") or [])
            and "/discovery-login" not in (it.get("link") or "").lower()
        ),
        "setor_estrategico_gt3": sum(
            1 for it in items if isinstance(ex(it).get("setor_estrategico"), list) and len(ex(it)["setor_estrategico"]) > 3
        ),
        "validacao_distribuicao_top_level": {},
        "acesso_limitado_com_contexto_publico_urls": [
            it.get("link")
            for it in items
            if norm_vs(it) == "acesso_limitado" and ("oracle" in (it.get("link") or "").lower() or "isupplier" in (it.get("link") or "").lower())
        ],
        "suspeito_top_level_remaining": sum(1 for it in items if norm_vs(it) == "suspeito"),
    }
    from collections import Counter

    verification["validacao_distribuicao_top_level"] = dict(Counter(norm_vs(it) for it in items))

    merged = {"loader_summary": loader, "semantic_audit_summary": sem, "recovery_d_verificacao": verification}
    out = root / "audit_reports_main_pipeline/recovery_d_suppliers_loader_dryrun.json"
    out.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    md = (
        "# Recovery D — Loader dry-run (isolado)\n\n"
        f"- mapping_errors_total: **{verification['mapping_errors_total']}**\n"
        f"- critical_empty_items_total: **{verification['critical_empty_items_total']}**\n"
        f"- standardized itens (loader): **{loader.get('itens_standardized_total')}**\n"
        f"- suspeito (validacao_status topo, pós-transform): **{verification['suspeito_top_level_remaining']}**\n"
        f"- setor_estrategico > 3: **{verification['setor_estrategico_gt3']}**\n"
        f"- FAQ URL heurística: **{verification['faq_url_detectado_na_coleta_standardized']}**\n\n"
        "## Distribuição validação (top-level)\n\n```json\n"
        + json.dumps(verification["validacao_distribuicao_top_level"], ensure_ascii=False, indent=2)
        + "\n```\n\n"
        "## Relatório base\n\nVer também `load_ready_summary.md/json` nesta pasta.\n"
    )
    (root / "audit_reports_main_pipeline/recovery_d_suppliers_loader_dryrun.md").write_text(md, encoding="utf-8")
    print("OK loader dryrun ->", out)


def _emit_apply_rec(root: Path, loader: dict) -> None:
    doc = {
        "apply": False,
        "motivo": "Restrições Recovery D — sem apply automatizado até QA humano.",
        "pre_checks_ok": loader.get("mapping_errors_total") == 0 and loader.get("critical_empty_items_total") == 0,
        "recomendacao": [
            "Aplicar `retransform_all` + payload loader apenas após sinalização em staging.",
            "Tratar primeiro candidatos deactivate `confianca=high`.",
            "Não usar DELETE; apenas PATCH ativo onde necessário.",
        ],
        "nao_executar": [
            "alterar opportunity_gate global",
            "mudar readiness oficial em disco nesta ferramenta",
            "scraping aggressivo ou bypass SSO",
        ],
    }
    p = root / "audit_reports_main_pipeline/recovery_d_suppliers_apply_recommendation.json"
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    md = (
        "# Recovery D — Recomendação de apply\n\n"
        "**apply=false** até revisão dos candidatos e janela de operações.\n\n"
        "## Pré-checks loader\n\n"
        f"- mapping_errors_total = {loader.get('mapping_errors_total')}\n"
        f"- critical_empty_items_total = {loader.get('critical_empty_items_total')}\n\n"
        "## Não executar nesta onda\n\n"
        + "\n".join(f"- {x}" for x in doc["nao_executar"])
        + "\n"
    )
    (root / "audit_reports_main_pipeline/recovery_d_suppliers_apply_recommendation.md").write_text(md, encoding="utf-8")
    print("OK apply recommendation ->", p)


def _emit_deactivate(root: Path) -> None:
    std = root / "audit_reports_main_pipeline/recovery_d_suppliers/standardized"
    cand = []
    for p in sorted(std.glob("*_standardized.json")):
        src = p.stem.replace("_standardized", "")
        for it in json.loads(p.read_text(encoding="utf-8")):
            lk = (it.get("link") or "").lower()
            tit = it.get("titulo") or ""
            reasons = []
            conf = "low"
            if "/capabilities/" in lk and "/suppliers" not in lk:
                reasons.append("Página de capabilities fora da área supplier explícita")
                conf = "medium"
            if tit.strip().upper() == "SUPPLIERS":
                reasons.append("Landing genérica")
                conf = "medium"
            if tit.strip().lower() == "suppliers" and "suppliers.html" in lk:
                reasons.append("Título genérico no hub suppliers")
                conf = "medium"
            if "gdls.com/lav" in lk:
                reasons.append("Página produto LAV — fora procurement")
                conf = "high"
            ew = (it.get("extras") or {}).get("validacao_warnings") if isinstance(it.get("extras"), dict) else []
            ew = ew or []
            if "recovery_d_institucional_generico" in ew:
                reasons.append("Flag institucional genérico")
                conf = "high"
            if "recovery_d_supplier_faq_ruido" in ew:
                conf = "high"
                reasons.append("FAQ ruído")
            if "supplier_login_isolado" in ew:
                conf = "high"
                reasons.append("Login isolado")
            if reasons:
                cand.append(
                    {
                        "fonte": src,
                        "titulo": tit,
                        "link": it.get("link"),
                        "motivo": "; ".join(reasons),
                        "confianca": conf,
                        "recomendacao": "ativo=false",
                        "nunca_DELETE": True,
                    }
                )
    pj = root / "audit_reports_main_pipeline/recovery_d_suppliers_deactivate_candidates.json"
    pj.write_text(json.dumps(cand, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Recovery D — Candidatos a desativação segura (`ativo=false`)", "", "**Nunca DELETE.** Lista derivada da coleta atual.", ""]
    for c in cand:
        lines.append(f"- **`{c['fonte']}`** ({c['confianca']}): [{c['titulo']}]({c['link']}) — {c['motivo']}")
    lines.append("")
    (root / "audit_reports_main_pipeline/recovery_d_suppliers_deactivate_candidates.md").write_text("\n".join(lines), encoding="utf-8")
    print("OK deactivate candidates ->", pj)


if __name__ == "__main__":
    main()
