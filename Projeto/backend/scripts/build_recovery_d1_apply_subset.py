# -*- coding: utf-8 -*-
"""
Recorte final Recovery D.1 — subset de 12 itens para dry-run loader (sem apply).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parents[1]
SRC_STD = ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_qa/standardized"
OUT_STD = ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset/standardized"
LOADER_OUT = ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset_loader_dryrun"

# Títulos exatos como no standardized UTF-8 (aprovados para apply subset)
APPROVED_TITLES: Set[str] = frozenset(
    {
        "New supplier registration (HICX)",
        "Responsible supply chain | BAE Systems UK suppliers",
        "Mentor-Protégé Program",
        "General Dynamics Land Systems — Suppliers (hub)",
        "CYBERSECURITY",
        "iSUPPLIER",
        "QUALITY",
        "TRANSPORTATION AND TRADE COMPLIANCE",
        "Lockheed Martin — Supplier portal (hub)",
        "Doing Business",
        "Business Area Procurement",
        "Small Business Programs",
    }
)

EXCLUDED_BY_POLICY: Tuple[str, ...] = (
    "Small Business Innovation Research",
    "Cybersecurity",
    "Supplier Ethics",
    "Sustainable Supply Chain Management",
    "Supplier Documentation",
    "Webinars & Programs",
    "Supplier News and Events",
    "LM eInvoicing 2026 Training",
    "Maintaining Cybersecurity Maturity Model Certification",
    "Shared Commitment to Equal Employment Opportunity",
    "Power Of A Shared Focus",
    "Document CMMC status in Exostar",
    "Discontinuation of Phone-Based OTP for Supplier Access",
    "Upcoming CMMC Requirements",
)


def _filter_file(path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    kept: List[Dict[str, Any]] = []
    dropped: List[str] = []
    for it in data:
        tit = str(it.get("titulo") or "")
        if tit in APPROVED_TITLES:
            kept.append(it)
        else:
            dropped.append(tit)
    return kept, dropped


def _verify_subset(all_items: List[Dict[str, Any]], loader: Dict[str, Any]) -> Dict[str, Any]:
    def ex(it):
        e = it.get("extras")
        return e if isinstance(e, dict) else {}

    def cnt(pred):
        return sum(1 for it in all_items if pred(it))

    faq = cnt(
        lambda it: any(
            x in (it.get("link") or "").lower()
            for x in ("/faq", "/faqs", "faq.", "/help", "/support")
        )
        and "/supplier" not in (it.get("link") or "").lower()
    )
    login = cnt(
        lambda it: "supplier_login_isolado" in (ex(it).get("validacao_warnings") or [])
        or ex(it).get("recovery_d_login_isolado")
    )
    suspeito = cnt(lambda it: str(it.get("validacao_status") or "").lower() == "suspeito")
    gt3 = cnt(
        lambda it: isinstance(ex(it).get("setor_estrategico"), list) and len(ex(it)["setor_estrategico"]) > 3
    )

    excluded_titles_present = [t for t in EXCLUDED_BY_POLICY if any(str(it.get("titulo")) == t for it in all_items)]

    return {
        "would_upsert_total": loader.get("would_upsert_total"),
        "mapping_errors_total": loader.get("mapping_errors_total"),
        "critical_empty_items_total": loader.get("critical_empty_items_total"),
        "itens_subset_total": len(all_items),
        "faq_help_heuristic": faq,
        "login_isolado": login,
        "validacao_suspeito_top": suspeito,
        "setor_estrategico_gt3": gt3,
        "excluded_policy_titles_in_subset": excluded_titles_present,
        "subset_ok": (
            len(all_items) == 12
            and loader.get("would_upsert_total") == 12
            and loader.get("mapping_errors_total") == 0
            and loader.get("critical_empty_items_total") == 0
            and faq == 0
            and login == 0
            and suspeito == 0
            and not excluded_titles_present
        ),
    }


def main() -> int:
    OUT_STD.mkdir(parents=True, exist_ok=True)

    summary: Dict[str, Any] = {
        "fontes": [],
        "itens_aprovados_total": 0,
        "itens_excluidos_por_fonte": {},
        "titulos_aprovados": sorted(APPROVED_TITLES),
        "titulos_excluidos_politica": list(EXCLUDED_BY_POLICY),
    }

    all_kept: List[Dict[str, Any]] = []
    for src_path in sorted(SRC_STD.glob("*_standardized.json")):
        kept, dropped = _filter_file(src_path)
        out_path = OUT_STD / src_path.name
        out_path.write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")
        key = src_path.stem.replace("_standardized", "")
        summary["fontes"].append({"fonte": key, "mantidos": len(kept), "removidos": len(dropped)})
        summary["itens_excluidos_por_fonte"][key] = dropped
        all_kept.extend(kept)

    summary["itens_aprovados_total"] = len(all_kept)
    if len(all_kept) != 12:
        print(f"[ERRO] Esperado 12 itens, obtido {len(all_kept)}", file=sys.stderr)
        missing = APPROVED_TITLES - {str(it.get("titulo")) for it in all_kept}
        extra = {str(it.get("titulo")) for it in all_kept} - APPROVED_TITLES
        print("Faltam titulos:", missing, file=sys.stderr)
        print("Titulos extra:", extra, file=sys.stderr)
        return 1

    subset_json = ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset.json"
    subset_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Recovery D.1 — Apply subset (12 itens)",
        "",
        "Subconjunto aprovado para **próximo** apply em staging (este artefacto **não** executa apply).",
        "",
        "## Itens incluídos (por título)",
        "",
    ]
    for t in sorted(APPROVED_TITLES):
        md_lines.append(f"- {t}")
    md_lines += ["", "## Por fonte", ""]
    for f in summary["fontes"]:
        md_lines.append(f"- `{f['fonte']}`: **{f['mantidos']}** mantidos, {f['removidos']} fora do subset.")
    md_lines.append("")
    (ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset.md").write_text("\n".join(md_lines), encoding="utf-8")

    LOADER_OUT.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(ROOT / "scripts/load_ready_sources.py"),
        "--dry-run",
        "--sources",
        "general_dynamics_suppliers,lockheed_martin_suppliers,bae_systems_suppliers",
        "--exclude-blocked",
        "--input-dir",
        "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset/standardized",
        "--readiness",
        "audit_reports_retransform/readiness_for_loader.json",
        "--output-dir",
        "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset_loader_dryrun",
    ]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stdout, r.stderr, file=sys.stderr)
        return r.returncode

    loader_path = LOADER_OUT / "load_ready_summary.json"
    if not loader_path.is_file():
        print(f"[ERRO] Falta {loader_path}", file=sys.stderr)
        return 2
    loader = json.loads(loader_path.read_text(encoding="utf-8"))
    verification = _verify_subset(all_kept, loader)

    merged = {"loader_summary": loader, "recovery_d1_subset_verificacao": verification}
    (ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset_loader_dryrun.json").write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    ld_md = [
        "# Recovery D.1 — Loader dry-run (apply subset)",
        "",
        f"- would_upsert_total: **{loader.get('would_upsert_total')}**",
        f"- mapping_errors_total: **{loader.get('mapping_errors_total')}**",
        f"- critical_empty_items_total: **{loader.get('critical_empty_items_total')}**",
        "",
        "## Verificação subset",
        "",
        "```json",
        json.dumps(verification, ensure_ascii=False, indent=2),
        "```",
        "",
        "Ver também `load_ready_summary.md` na mesma pasta.",
        "",
    ]
    (ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset_loader_dryrun.md").write_text(
        "\n".join(ld_md), encoding="utf-8"
    )

    rec = {
        "executar_apply": False,
        "motivo": "Política Recovery D.1 — subset apenas para revisão final antes de janela de apply.",
        "subset_itens": 12,
        "verificacao": verification,
        "proximo_passo": (
            "Quando autorizado, apontar loader staging para este standardized ou fazer merge equivalente; "
            "não usar DELETE; itens excluídos permanecem na fonte completa para futura taxonomia documentação."
        ),
    }
    (ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset_recommendation.json").write_text(
        json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    rec_md = [
        "# Recovery D.1 — Recomendação (apply subset)",
        "",
        "**Apply:** não executado.",
        "",
        f"Subset: **{verification['itens_subset_total']}** itens; `would_upsert_total` = {verification.get('would_upsert_total')}.",
        "",
        f"**subset_ok (checks automáticos):** {verification.get('subset_ok')}",
        "",
        rec["proximo_passo"],
        "",
    ]
    (ROOT / "audit_reports_main_pipeline/recovery_d1_suppliers_apply_subset_recommendation.md").write_text(
        "\n".join(rec_md), encoding="utf-8"
    )

    print(json.dumps(verification, ensure_ascii=False, indent=2))
    return 0 if verification["subset_ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
