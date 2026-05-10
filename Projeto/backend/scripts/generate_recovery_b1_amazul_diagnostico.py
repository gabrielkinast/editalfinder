#!/usr/bin/env python3
"""Gera recovery_b1_amazul_diagnostico.{json,md} a partir de post_daily_warning_examples.json.

Relatórios consolidados de recovery/onda (secções 1–10 + JSON interpretativo) devem seguir
`scripts/recovery_report_template.py` — ver `recovery_*_consolidado.{md,json}`.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
POST = ROOT / "audit_reports_main_pipeline" / "post_daily_warning_examples.json"
OUT_JSON = ROOT / "audit_reports_main_pipeline" / "recovery_b1_amazul_diagnostico.json"
OUT_MD = ROOT / "audit_reports_main_pipeline" / "recovery_b1_amazul_diagnostico.md"

WARN_KEYS = (
    "edital.suspeito_ativo_true",
    "edital.prazo_vencido_ativo_true",
    "edital.credito_tipo_recurso_incoerente",
)


def _classify(row: Dict[str, Any]) -> str:
    lk = str(row.get("link") or "").lower()
    tit = str(row.get("titulo") or "").lower()
    to = str(row.get("tipo_oportunidade") or "").lower()
    mot = str(row.get("motivo") or "").lower()
    if "amazul.mar.mil.br" not in lk:
        return "precisa_revisao_manual"
    if "/acesso-a-informacao/licitacoes-e-contratos/" in lk and any(
        x in lk for x in ("dispensa-de-licitacao", "dispensa-de-licitação", "pregao", "pregão", "contrato", "edital")
    ):
        if "prazo" in mot or "vencido" in mot:
            return "oportunidade_vencida"
        if "credito" in mot or "financiamento" in mot or "reembolsavel" in mot:
            return "chamada_editais_reais"
        if to == "licitacao" or "dispensa" in tit or "licita" in tit:
            return "chamada_editais_reais"
    if "chamada" in tit or "edital" in tit:
        return "oportunidade_real"
    if "hub" in tit or lk.rstrip("/").endswith("amazul.mar.mil.br"):
        return "pagina_institucional"
    return "precisa_revisao_manual"


def _acao(cat: str, problem: str) -> str:
    if problem == "suspeito_ativo_true":
        if cat == "chamada_editais_reais":
            return "Calibração local + validacao incompleto (Recovery B.1); não desativar sem curadoria."
        return "Rever gate/qualidade; curadoria se persistir suspeito."
    if problem == "prazo_vencido_ativo_true":
        return "Documentar prazo vencido; política de arquivo ou ativo=false em passo futuro (sem inventar datas)."
    if problem == "credito_tipo_recurso_incoerente":
        return "Marcar reembolsavel=false para compra pública AMAZUL no transformer; texto com 'crédito' no objeto ≠ linha de crédito bancário."
    return "Revisão manual."


def main() -> int:
    data = json.loads(POST.read_text(encoding="utf-8"))
    ebw = data.get("examples_by_warning") or {}
    sbw = data.get("summary_by_warning") or {}

    by_problem: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for wk in WARN_KEYS:
        block = ebw.get(wk) or {}
        for ex in block.get("examples") or []:
            if not isinstance(ex, dict):
                continue
            if str(ex.get("fonte_recurso") or "").strip().upper() != "AMAZUL":
                continue
            pid = ex.get("id")
            cat = _classify(ex)
            rec = {
                "warning": wk.split(".")[-1],
                "id": pid,
                "titulo": ex.get("titulo"),
                "link": ex.get("link"),
                "validacao_status": ex.get("validacao_status"),
                "tipo_oportunidade": ex.get("tipo_oportunidade"),
                "tipo_recurso": ex.get("tipo_recurso"),
                "prazo_envio": ex.get("prazo_envio"),
                "motivo_staging": ex.get("motivo"),
                "classificacao": cat,
                "acao_recomendada": _acao(cat, wk.split(".")[-1]),
            }
            by_problem[wk].append(rec)

    out = {
        "fonte": "AMAZUL",
        "timestamp_post_daily": data.get("timestamp"),
        "contagens_summary_by_warning": {
            wk: (sbw.get(wk) or {}).get("by_source", {}).get("AMAZUL")
            for wk in WARN_KEYS
            if (sbw.get(wk) or {}).get("by_source")
        },
        "itens_por_warning": {k.split(".")[-1]: v for k, v in by_problem.items()},
        "nota": "Exemplos limitados pelo validador (máx. ~30 por warning). Contagens completas em summary_by_warning.by_source.AMAZUL.",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Recovery B.1 — diagnóstico AMAZUL",
        "",
        f"- **Post-daily:** `{POST.relative_to(ROOT)}` ({data.get('timestamp')})",
        "",
        "## Contagens AMAZUL (`summary_by_warning`)",
        "",
        "| Warning | AMAZUL (count) |",
        "|---------|---------------:|",
    ]
    for wk in WARN_KEYS:
        short = wk.split(".")[-1]
        n = (sbw.get(wk) or {}).get("by_source", {}).get("AMAZUL", "—")
        lines.append(f"| `{short}` | {n} |")
    lines.extend(["", "## Itens (exemplos filtrados)", ""])
    for wk in WARN_KEYS:
        short = wk.split(".")[-1]
        lines.append(f"### `{short}`")
        lines.append("")
        for r in by_problem.get(wk, [])[:15]:
            lines.append(f"- **id {r.get('id')}** — {r.get('classificacao')}: {str(r.get('titulo'))[:100]}")
            lk = str(r.get("link") or "")
            lines.append(f"  - Link: `{lk[:200]}{'…' if len(lk) > 200 else ''}`")
            lines.append(f"  - Ação: {r.get('acao_recomendada')}")
        lines.append("")

    lines.append("Detalhe JSON: `recovery_b1_amazul_diagnostico.json`.")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("OK", OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
