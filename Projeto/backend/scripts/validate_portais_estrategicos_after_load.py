#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação pós-carga: links standardized vs public.portal_estrategico e view de front.

- Secção `fornecedores`: regras + `vw_fornecedores_front`.
- Secção `investimentos`: regras próprias; tenta `vw_investimentos_front` se existir, senão
  não falha só por causa da view (marca como skipped nos relatórios).

Somente SELECT / leitura. Não altera dados.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
for _p in (ROOT / ".env.staging", ROOT / ".env.local", ROOT / ".env", CORE / ".env"):
    if _p.is_file():
        load_dotenv(dotenv_path=_p, override=False)

DEFAULT_INPUT = ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_final/standardized"


def _mask_host(url: str) -> str:
    if not url:
        return ""
    try:
        h = (urlparse(url).hostname or "").strip()
    except Exception:
        return "***"
    if len(h) <= 6:
        return (h[0] + "***" + h[-1]) if h else ""
    return h[:3] + "***" + h[-3:]


def _read_guard_staging() -> Tuple[bool, Dict[str, Any]]:
    url = os.getenv("SUPABASE_URL", "").strip()
    env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
    has_url = bool(url)
    has_service_key = bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    )
    env_ok = env in ("staging", "local")
    env_prod = env in ("production", "prod")
    block_reason = ""
    if env_prod:
        block_reason = "environment_marked_production"
    elif not env_ok:
        block_reason = "invalid_editalfinder_env"
    elif not has_url:
        block_reason = "missing_supabase_url"
    elif not has_service_key:
        block_reason = "missing_service_key"
    guard = {
        "editalfinder_env": env,
        "has_supabase_url": has_url,
        "has_service_key": has_service_key,
        "url_host_masked": _mask_host(url),
        "block_reason": block_reason,
    }
    return block_reason == "", guard


def _get_supabase_client():
    from supabase import create_client

    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL ou chave de serviço ausente")
    return create_client(url, key)


def _peek_frontend_section(input_dir: Path, sources: Set[str]) -> str:
    """Inferir 'fornecedores' | 'investimentos' a partir do primeiro item dos JSONs."""
    seen: Set[str] = set()
    for key in sorted(sources):
        path = input_dir / f"{key}_standardized.json"
        if not path.is_file():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list) or not raw or not isinstance(raw[0], dict):
            continue
        it = raw[0]
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        fs = str(it.get("frontend_section") or ex.get("frontend_section") or "").strip().lower()
        if fs in ("fornecedores", "investimentos"):
            seen.add(fs)
    if len(seen) > 1:
        return "mixed"
    if "investimentos" in seen:
        return "investimentos"
    return "fornecedores"


def _collect_links(input_dir: Path, sources: Set[str]) -> List[str]:
    links: List[str] = []
    for key in sorted(sources):
        path = input_dir / f"{key}_standardized.json"
        if not path.is_file():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            continue
        for it in raw:
            if isinstance(it, dict):
                lk = str(it.get("link") or "").strip()
                if lk.startswith("http://") or lk.startswith("https://"):
                    links.append(lk)
    return links


def _check_row_fornecedores(r: Dict[str, Any]) -> List[str]:
    err: List[str] = []
    if (r.get("frontend_section") or "").strip().lower() != "fornecedores":
        err.append("frontend_section")
    if r.get("mostrar_no_radar") is not False:
        err.append("mostrar_no_radar")
    if r.get("mostrar_em_fornecedores") is not True:
        err.append("mostrar_em_fornecedores")
    vs = (r.get("validacao_status") or "").strip().lower()
    if vs == "suspeito":
        err.append("validacao_suspeito")
    pt = (r.get("portal_tipo") or "").strip()
    if not pt:
        err.append("portal_tipo_vazio")
    ses = r.get("setor_estrategico") or []
    if isinstance(ses, list) and len(ses) > 3:
        err.append("setor_estrategico_gt3")
    return err


def _check_row_investimentos(r: Dict[str, Any]) -> List[str]:
    err: List[str] = []
    if (r.get("frontend_section") or "").strip().lower() != "investimentos":
        err.append("frontend_section_investimentos")
    if r.get("mostrar_no_radar") is not False:
        err.append("mostrar_no_radar")
    if r.get("mostrar_em_investimentos") is not True:
        err.append("mostrar_em_investimentos")
    if r.get("mostrar_em_fornecedores") is not False:
        err.append("mostrar_em_fornecedores_deve_false")
    vs = (r.get("validacao_status") or "").strip().lower()
    if vs == "suspeito":
        err.append("validacao_suspeito")
    pt = (r.get("portal_tipo") or "").strip()
    if not pt:
        err.append("portal_tipo_vazio")
    ex = r.get("extras")
    if isinstance(ex, str):
        try:
            ex = json.loads(ex)
        except Exception:
            ex = {}
    if not isinstance(ex, dict):
        ex = {}
    w1 = str(ex.get("portal_tipo_wave1") or "").strip().lower()
    if not w1:
        err.append("extras.portal_tipo_wave1_ausente")
    ses = r.get("setor_estrategico") or []
    if isinstance(ses, list) and len(ses) > 3:
        err.append("setor_estrategico_gt3")
    return err


def main() -> int:
    ap = argparse.ArgumentParser(description="Validar portal_estrategico após carga (somente leitura)")
    ap.add_argument("--staging", action="store_true", required=True, help="Marcador explícito (staging/local)")
    ap.add_argument("--sources", default="general_dynamics_suppliers,lockheed_martin_suppliers,bae_systems_suppliers")
    ap.add_argument("--input-dir", default=str(DEFAULT_INPUT))
    ap.add_argument("--output-dir", required=True)
    ap.add_argument(
        "--frontend-section",
        choices=("auto", "fornecedores", "investimentos"),
        default="auto",
        help="Regras de linha e view: auto infere a partir do primeiro item dos JSONs.",
    )
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    input_dir = Path(args.input_dir)
    sources = {x.strip().lower() for x in str(args.sources).split(",") if x.strip()}

    if args.frontend_section == "auto":
        section = _peek_frontend_section(input_dir, sources)
    else:
        section = args.frontend_section
    if section == "mixed":
        summary_err = {
            "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "error",
            "erro": "frontend_section_mista_nos_jsons",
            "sources_selected": sorted(sources),
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "validate_portais_estrategicos_after_load.json").write_text(
            json.dumps(summary_err, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_dir / "validate_portais_estrategicos_after_load.md").write_text(
            "# Validação\n\nErro: `frontend_section` inconsistente entre ficheiros standardized.\n",
            encoding="utf-8",
        )
        print(out_dir.resolve(), file=sys.stderr)
        return 1

    ok, guard = _read_guard_staging()
    expected_links = _collect_links(input_dir, sources)
    unique_expected: Set[str] = set(expected_links)
    ordered_links = sorted(unique_expected)

    row_issues: List[Dict[str, Any]] = []
    view_links: Set[str] = set()
    table_links: Set[str] = set()
    view_error = ""
    view_name_used = ""
    investimentos_view_skipped = False
    investimentos_view_skip_reason = ""

    if not ok:
        status = "blocked"
    elif not unique_expected:
        status = "no_expected_links"
    else:
        status = "running"
        try:
            sb = _get_supabase_client()
            chunk = 40
            for i in range(0, len(ordered_links), chunk):
                batch = ordered_links[i : i + chunk]
                r = sb.table("portal_estrategico").select("*").in_("link", batch).execute()
                for row in getattr(r, "data", None) or []:
                    if not isinstance(row, dict):
                        continue
                    lk = str(row.get("link") or "")
                    table_links.add(lk)
                    if section == "investimentos":
                        miss = _check_row_investimentos(row)
                    else:
                        miss = _check_row_fornecedores(row)
                    if miss:
                        row_issues.append({"link": lk, "problemas": miss})
            for i in range(0, len(ordered_links), chunk):
                batch = ordered_links[i : i + chunk]
                try:
                    if section == "investimentos":
                        view_name_used = "vw_investimentos_front"
                        try:
                            rv = sb.table("vw_investimentos_front").select("link").in_("link", batch).execute()
                            for row in getattr(rv, "data", None) or []:
                                if isinstance(row, dict) and row.get("link"):
                                    view_links.add(str(row["link"]))
                        except Exception as exc_inv:
                            investimentos_view_skipped = True
                            investimentos_view_skip_reason = str(exc_inv)
                            view_name_used = ""
                            break
                    else:
                        view_name_used = "vw_fornecedores_front"
                        rv = sb.table("vw_fornecedores_front").select("link").in_("link", batch).execute()
                        for row in getattr(rv, "data", None) or []:
                            if isinstance(row, dict) and row.get("link"):
                                view_links.add(str(row["link"]))
                except Exception as exc:
                    view_error = str(exc)
                    break
            status = "ok" if not view_error else "view_partial"
        except Exception as exc:
            status = "error"
            view_error = str(exc)

    missing_in_table = sorted(unique_expected - table_links)
    missing_in_view: Any = sorted(unique_expected - view_links) if not view_error else None
    if investimentos_view_skipped:
        missing_in_view = []

    summary: Dict[str, Any] = {
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "staging_flag": True,
        "frontend_section": section,
        "view_name": view_name_used or ("" if investimentos_view_skipped else "vw_fornecedores_front"),
        "investimentos_view_skipped": investimentos_view_skipped,
        "investimentos_view_skip_reason": investimentos_view_skip_reason or None,
        "input_dir": str(input_dir.resolve()),
        "output_dir": str(out_dir.resolve()),
        "sources_selected": sorted(sources),
        "expected_links_count": len(unique_expected),
        "found_in_portal_estrategico_count": len(table_links & unique_expected),
        "found_in_front_view_count": len(view_links & unique_expected) if not view_error else 0,
        "found_in_vw_fornecedores_front_count": len(view_links & unique_expected)
        if (not view_error and section == "fornecedores")
        else 0,
        "missing_in_portal_estrategico": missing_in_table,
        "missing_in_front_view": missing_in_view if not view_error and not investimentos_view_skipped else [],
        "missing_in_vw_fornecedores_front": missing_in_view if not view_error else None,
        "row_rule_violations": row_issues,
        "row_rule_violations_count": len(row_issues),
        "view_query_error": view_error or None,
        "environment_guard": guard,
        "status": status,
    }

    (out_dir / "validate_portais_estrategicos_after_load.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md = [
        "# Validação portais estratégicos (pós-carga)",
        "",
        f"- Secção: **{summary['frontend_section']}**",
        f"- Status: **{summary['status']}**",
        f"- Links esperados: **{summary['expected_links_count']}**",
        f"- Encontrados em `portal_estrategico`: **{summary['found_in_portal_estrategico_count']}**",
        f"- Encontrados na view de front: **{summary['found_in_front_view_count']}** (`{summary.get('view_name') or 'n/d'}`)",
        f"- Violações de regras por linha: **{summary['row_rule_violations_count']}**",
        "",
        "## environment_guard",
        "",
        "```json",
        json.dumps(guard, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    if view_error:
        md.append(f"- Erro na view: `{view_error}`")
    if investimentos_view_skipped:
        md.append(f"- View investimentos omitida: `{investimentos_view_skip_reason}`")
    (out_dir / "validate_portais_estrategicos_after_load.md").write_text("\n".join(md), encoding="utf-8")

    print(out_dir.resolve())
    if not ok or status in ("blocked", "no_expected_links", "error"):
        return 1
    if missing_in_table or row_issues:
        return 1
    if view_error:
        return 1
    if investimentos_view_skipped:
        return 0 if not missing_in_table and not row_issues else 1
    if missing_in_view:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
