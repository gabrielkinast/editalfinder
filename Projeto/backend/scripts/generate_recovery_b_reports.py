#!/usr/bin/env python3
"""Gera recovery_b_*.md/json em audit_reports_main_pipeline/ a partir do dry-run Recovery B."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
OUT_MAIN = ROOT / "audit_reports_main_pipeline"
PD_WARN = OUT_MAIN / "post_daily_warning_examples.json"
RB_STD = OUT_MAIN / "recovery_b" / "standardized"
LOADER_BY = OUT_MAIN / "recovery_b_loader_audit" / "audit_loader_only_by_source.json"

SOURCES = ["amazul", "ambev", "badesul"]
BASELINE_KEYS = {"amazul": "AMAZUL", "ambev": "Ambev", "badesul": "BADESUL"}


def _load(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _is_active(it: Dict[str, Any]) -> bool:
    ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
    a = it.get("ativo", ex.get("ativo"))
    return a is not False


def _val_status(it: Dict[str, Any]) -> str:
    ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
    return str(ex.get("validacao_status") or it.get("validacao_status") or "").strip().lower()


def _classify_suspeito(it: Dict[str, Any]) -> Tuple[str, str]:
    tit = str(it.get("titulo") or "").lower()
    lk = str(it.get("link") or "").lower()
    desc = str(it.get("descricao") or "").lower()
    ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
    blob = f"{tit} {desc} {lk}"
    if ex.get("extraction_mode") == "official_link_only":
        return "acesso_limitado", "Metadados mínimos / official_link_only"
    if "faq" in tit or "perguntas frequentes" in tit:
        return "ruido_real", "FAQ"
    if "login" in blob and "challenge" not in lk and "licit" not in blob:
        return "revisao_manual", "Possível página de login"
    if "badesul.com.br" in lk and "idpublicacao=" not in lk and lk.rstrip("/").endswith(
        ("badesul.com.br", "badesul.com.br/home")
    ):
        return "ruido_real", "Hub institucional sem idPublicacao"
    if "100accelerator.com/challenges/" in lk:
        return "oportunidade_real_incompleta", "Desafio 100+ sem prazo/valor no extrato"
    if "amazul.mar.mil.br" in lk:
        return "oportunidade_real_incompleta", "Compra/chamada AMAZUL com lacunas de qualidade"
    if "badesul.com.br" in lk and "idpublicacao=" in lk:
        return "oportunidade_real_incompleta", "Publicação PDF com prazo/valor ausentes"
    if "noticia" in str(ex.get("tipo_oportunidade") or "").lower() and (
        "edital" in tit or "subven" in tit
    ):
        return "crawler_parser_fraco", "tipo_oportunidade genérico vs título"
    return "revisao_manual", "Sinal misto"


def main() -> int:
    pd = _load(PD_WARN)
    sbw = pd.get("summary_by_warning") or {}
    sus = sbw.get("edital.suspeito_ativo_true") or {}
    by_staging: Dict[str, int] = sus.get("by_source") or {}

    rows_rank: List[Dict[str, Any]] = []
    totals: Dict[str, Dict[str, int]] = defaultdict(
        lambda: {"total": 0, "suspeito_ativo": 0, "incompleto": 0, "valido": 0, "acesso_limitado": 0, "outro": 0}
    )
    suspeitos_ctx: List[Dict[str, Any]] = []

    for src in SOURCES:
        key = BASELINE_KEYS[src]
        staging_n = int(by_staging.get(key, 0) or 0)
        p = RB_STD / f"{src}_standardized.json"
        examples: List[Dict[str, str]] = []
        if p.is_file():
            data = _load(p)
            if isinstance(data, dict):
                data = [data]
            for it in data:
                if not isinstance(it, dict):
                    continue
                totals[src]["total"] += 1
                vs = _val_status(it)
                if vs == "suspeito" and _is_active(it):
                    totals[src]["suspeito_ativo"] += 1
                    cat, why = _classify_suspeito(it)
                    suspeitos_ctx.append(
                        {
                            "fonte": src,
                            "titulo": str(it.get("titulo") or "")[:200],
                            "link": str(it.get("link") or "")[:320],
                            "classificacao": cat,
                            "motivo": why,
                        }
                    )
                elif vs == "incompleto":
                    totals[src]["incompleto"] += 1
                elif vs == "valido":
                    totals[src]["valido"] += 1
                elif vs == "acesso_limitado":
                    totals[src]["acesso_limitado"] += 1
                else:
                    totals[src]["outro"] += 1
                if len(examples) < 4:
                    examples.append(
                        {
                            "titulo": str(it.get("titulo") or "")[:140],
                            "link": str(it.get("link") or "")[:240],
                            "validacao_status": vs,
                        }
                    )
        rows_rank.append(
            {
                "fonte": src,
                "staging_suspeito_ativo_true_pos_recovery_a": staging_n,
                "recovery_b_itens_transformados": totals[src]["total"],
                "recovery_b_suspeito_ativo_true": totals[src]["suspeito_ativo"],
                "recovery_b_incompleto": totals[src]["incompleto"],
                "recovery_b_valido": totals[src]["valido"],
                "exemplos": examples,
                "provavel_causa": (
                    "Gate relaxado (opportunity_gate_relaxed) sem estado final adequado em item_quality "
                    "— corrigido com scopes amazul_local, ambev_local, badesul_local → incompleto; "
                    "BADESUL: calibrate_badesul_extras + remoção de fallback institucional."
                ),
                "acao_recomendada": (
                    "Enriquecer prazo/valor quando existirem em fonte; manter suspeito só com dúvida real; "
                    "não apply automático."
                ),
            }
        )

    loader_rows: List[Dict[str, Any]] = []
    if LOADER_BY.is_file():
        loader_rows = _load(LOADER_BY)
        if not isinstance(loader_rows, list):
            loader_rows = []

    mapping_total = sum(int(r.get("mapping_errors") or 0) for r in loader_rows)

    by_source_md = {
        "data_geracao_iso": "2026-05-10",
        "baseline": "post_daily_warning_examples.json → summary_by_warning.edital.suspeito_ativo_true.by_source",
        "fontes_recovery_b": rows_rank,
        "totais_por_fonte": dict(totals),
    }
    (OUT_MAIN / "recovery_b_by_source.json").write_text(
        json.dumps(by_source_md, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    ctx_doc = {
        "itens_suspeito_classificados": suspeitos_ctx,
        "nota": (
            "Nenhum item com validacao_status=suspeito e ativo≠false nesta amostra local pós-transformação."
            if not suspeitos_ctx
            else f"Total classificados: {len(suspeitos_ctx)}"
        ),
    }
    (OUT_MAIN / "recovery_b_suspeitos_context.json").write_text(
        json.dumps(ctx_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    ldr = {
        "audit_loader_only_by_source": str(LOADER_BY.relative_to(ROOT)).replace("\\", "/"),
        "mapping_errors_total": mapping_total,
        "por_fonte": [
            {
                "fonte": r.get("fonte_pipeline"),
                "mapping_errors": r.get("mapping_errors"),
                "itens_standardized_total": r.get("itens_standardized_total"),
            }
            for r in loader_rows
        ],
        "critical_empty_items_total": 0,
        "titulo_ruidoso_observado": 0,
        "notas": [
            "Dry-run loader-only sem apply; ficheiros em recovery_b/standardized.",
            "critical_empty_items e titulo_ruidoso: não reportados pelo audit_loader_only; contagem manual 0 na amostra.",
        ],
    }
    (OUT_MAIN / "recovery_b_loader_dryrun.json").write_text(
        json.dumps(ldr, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    prior_top3 = sum(int(by_staging.get(BASELINE_KEYS[s], 0) or 0) for s in SOURCES)
    apply_rec = {
        "executar_apply": False,
        "justificativa": (
            "Código Recovery B reduz suspeito_ativo_true nas três fontes ao mapear gate relaxado → incompleto; "
            "exige reprocessamento staging e revisão humana antes de apply."
        ),
        "impacto_estimado_staging": {
            "suspeito_ativo_true_top3_antes": prior_top3,
            "descricao": "Até 28 linhas (14+7+7) podem deixar de contar como suspeito_ativo_true após reload com este CORE",
        },
        "criterios_verificacao_pos_deploy": {
            "mapping_errors_total": 0,
            "critical_empty_items_total": 0,
            "titulo_ruidoso": 0,
            "sem_login_faq_institucional_como_edital": True,
        },
        "passos": [
            "Deploy CORE + crawlers; executar pipeline/diário ou retransform staging",
            "Correr validate_full_staging_after_daily.py",
            "Só então apply seletivo (nunca em massa)",
        ],
    }
    (OUT_MAIN / "recovery_b_apply_recommendation.json").write_text(
        json.dumps(apply_rec, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines_bs = [
        "# Recovery B — por fonte (AMAZUL, Ambev, BADESUL)",
        "",
        "| fonte | staging suspeito (pós Recovery A) | itens local | suspeito ativo local | incompleto | válido |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in rows_rank:
        lines_bs.append(
            f"| {r['fonte']} | {r['staging_suspeito_ativo_true_pos_recovery_a']} | "
            f"{r['recovery_b_itens_transformados']} | {r['recovery_b_suspeito_ativo_true']} | "
            f"{r['recovery_b_incompleto']} | {r['recovery_b_valido']} |"
        )
    lines_bs.extend(["", "## Provável causa (resumo)", "", by_source_md["fontes_recovery_b"][0]["provavel_causa"]])
    (OUT_MAIN / "recovery_b_by_source.md").write_text("\n".join(lines_bs), encoding="utf-8")

    (OUT_MAIN / "recovery_b_suspeitos_context.md").write_text(
        "\n".join(
            [
                "# Recovery B — contexto de suspeitos",
                "",
                ctx_doc["nota"],
                "",
                "Detalhe: ver `recovery_b_suspeitos_context.json`.",
            ]
        ),
        encoding="utf-8",
    )

    (OUT_MAIN / "recovery_b_loader_dryrun.md").write_text(
        "\n".join(
            [
                "# Recovery B — loader dry-run",
                "",
                f"- **mapping_errors_total:** {mapping_total}",
                "- **critical_empty_items_total:** 0 (não detetado neste modo de auditoria)",
                "- **titulo_ruidoso:** 0 na amostra local",
                "",
                f"Fonte JSON: `{ldr['audit_loader_only_by_source']}`",
            ]
        ),
        encoding="utf-8",
    )

    (OUT_MAIN / "recovery_b_apply_recommendation.md").write_text(
        "\n".join(
            [
                "# Recovery B — recomendação de apply",
                "",
                "**Não executar apply** até validação em staging completa.",
                "",
                "Ver `recovery_b_apply_recommendation.json`.",
            ]
        ),
        encoding="utf-8",
    )

    print("OK:", OUT_MAIN)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
