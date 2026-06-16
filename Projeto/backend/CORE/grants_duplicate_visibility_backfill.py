"""
Backfill de visibilidade em duplicatas Grants.gov ocultas (Backend 10.3C).

Garante que registros já marcados pelo 10.3B tenham ambos:
  - extras.curadoria_front.hidden_duplicate = true
  - extras.curadoria_front.visibility = "hidden_duplicate"

Não deleta, não altera schema, não oculta canônicos, não sobrescreve extras.
"""
from __future__ import annotations

import copy
import os
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from grants_duplicate_resolution import (
    DEFAULT_MAX_BATCH,
    _as_int_id,
    _get_extras,
    controlled_apply_enabled,
    is_grants_gov_record,
    merge_curadoria_front,
)

VISIBILITY_TARGET = "hidden_duplicate"
RESOLVED_BY_BACKFILL = "backend_10.3c"


def visibility_backfill_enabled() -> bool:
    return os.getenv("EDITALFINDER_ALLOW_DUPLICATE_VISIBILITY_BACKFILL", "").strip() in (
        "1",
        "true",
        "True",
    )


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_curadoria_front(record: Dict[str, Any]) -> Dict[str, Any]:
    cf = _get_extras(record).get("curadoria_front")
    return cf if isinstance(cf, dict) else {}


def is_marked_hidden_duplicate(cf: Dict[str, Any]) -> bool:
    if not isinstance(cf, dict):
        return False
    if cf.get("hidden_duplicate") is True:
        return True
    return str(cf.get("visibility") or "").lower() == VISIBILITY_TARGET


def visibility_backfill_complete(cf: Dict[str, Any]) -> bool:
    if not isinstance(cf, dict):
        return False
    return (
        cf.get("hidden_duplicate") is True
        and str(cf.get("visibility") or "").lower() == VISIBILITY_TARGET
    )


def build_visibility_backfill_patch(cf: Dict[str, Any]) -> Dict[str, Any]:
    """Somente campos faltantes — não sobrescreve valores já corretos."""
    patch: Dict[str, Any] = {}
    if cf.get("hidden_duplicate") is not True:
        patch["hidden_duplicate"] = True
    if str(cf.get("visibility") or "").lower() != VISIBILITY_TARGET:
        patch["visibility"] = VISIBILITY_TARGET
    if patch and "visibility_backfill_by" not in cf:
        patch["visibility_backfill_by"] = RESOLVED_BY_BACKFILL
    return patch


def _is_referenced_as_canonical(record_id: int, records: List[Dict[str, Any]]) -> bool:
    for rec in records:
        if _as_int_id(rec.get("id_edital")) == record_id:
            continue
        cf = get_curadoria_front(rec)
        if _as_int_id(cf.get("duplicate_of_id_edital")) == record_id:
            return True
    return False


def classify_record_for_backfill(
    record: Dict[str, Any],
    *,
    all_records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Classifica um registro Grants.gov para backfill de visibilidade.
    Retorna status: already_ok | candidate | anomaly | skipped
    """
    rid = _as_int_id(record.get("id_edital"))
    base = {"id_edital": rid, "titulo": record.get("titulo")}

    if not is_grants_gov_record(record):
        return {**base, "status": "skipped", "reason": "nao_grants_gov"}

    cf = get_curadoria_front(record)
    if not is_marked_hidden_duplicate(cf):
        return {**base, "status": "skipped", "reason": "nao_marcado_oculto"}

    dup_of = _as_int_id(cf.get("duplicate_of_id_edital"))
    has_bool = cf.get("hidden_duplicate") is True
    has_vis = str(cf.get("visibility") or "").lower() == VISIBILITY_TARGET

    if rid is not None and dup_of is not None and rid == dup_of:
        return {**base, "status": "anomaly", "reason": "duplicate_of_aponta_para_si"}

    if (has_bool or has_vis) and dup_of is None:
        return {**base, "status": "anomaly", "reason": "oculto_sem_duplicate_of_id_edital", "curadoria_front": cf}

    if rid is not None and all_records and _is_referenced_as_canonical(rid, all_records):
        if has_bool or has_vis:
            return {
                **base,
                "status": "anomaly",
                "reason": "canonico_referenciado_esta_oculto",
                "duplicate_of_id_edital": dup_of,
            }

    if visibility_backfill_complete(cf):
        return {**base, "status": "already_ok", "curadoria_front": cf}

    patch = build_visibility_backfill_patch(cf)
    missing = []
    if not has_bool:
        missing.append("hidden_duplicate")
    if not has_vis:
        missing.append("visibility")

    return {
        **base,
        "status": "candidate",
        "reason": "backfill_" + "_e_".join(missing),
        "duplicate_of_id_edital": dup_of,
        "curadoria_patch": patch,
        "curadoria_front_before": cf,
    }


def analyze_visibility_backfill(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Dry-run: classifica todos os registros Grants.gov. Não escreve no banco."""
    grants = [r for r in records if is_grants_gov_record(r)]
    already_ok: List[Dict[str, Any]] = []
    candidates: List[Dict[str, Any]] = []
    anomalies: List[Dict[str, Any]] = []
    skipped = 0
    needs_visibility = 0
    needs_hidden_boolean = 0

    for rec in grants:
        result = classify_record_for_backfill(rec, all_records=grants)
        status = result.get("status")
        cf = get_curadoria_front(rec)

        if status == "already_ok":
            already_ok.append(result)
        elif status == "candidate":
            candidates.append(result)
            if cf.get("hidden_duplicate") is True and str(cf.get("visibility") or "").lower() != VISIBILITY_TARGET:
                needs_visibility += 1
            if str(cf.get("visibility") or "").lower() == VISIBILITY_TARGET and cf.get("hidden_duplicate") is not True:
                needs_hidden_boolean += 1
        elif status == "anomaly":
            anomalies.append(result)
        else:
            skipped += 1

    stats = {
        "total_analyzed": len(grants),
        "already_ok": len(already_ok),
        "candidates_to_update": len(candidates),
        "needs_visibility": needs_visibility,
        "needs_hidden_duplicate_boolean": needs_hidden_boolean,
        "anomalies": len(anomalies),
        "skipped_not_hidden": skipped,
    }
    return {
        "stats": stats,
        "already_ok": already_ok,
        "candidates_to_update": candidates,
        "anomalies": anomalies,
    }


def apply_visibility_backfill(
    candidates: List[Dict[str, Any]],
    *,
    confirm_large: bool = False,
    supabase_client: Any = None,
    row_fetcher: Optional[Callable[[int], Optional[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """Apply controlado — atualiza somente extras. Idempotente."""
    if not controlled_apply_enabled():
        raise RuntimeError("Apply abortado: EDITALFINDER_ALLOW_CONTROLLED_APPLY não está ativo.")
    if not visibility_backfill_enabled():
        raise RuntimeError(
            "Apply abortado: EDITALFINDER_ALLOW_DUPLICATE_VISIBILITY_BACKFILL não está ativo."
        )
    if len(candidates) > DEFAULT_MAX_BATCH and not confirm_large:
        raise RuntimeError(
            f"Lote grande ({len(candidates)} > {DEFAULT_MAX_BATCH}). Use --confirm-large."
        )

    from grants_duplicate_resolution import _default_extras_fetcher  # noqa: WPS433

    client = supabase_client
    if client is None and row_fetcher is None:
        import loader  # noqa: WPS433

        client = loader.supabase
    if row_fetcher is None:
        if client is None:
            raise RuntimeError("Supabase não configurado — apply abortado.")
        row_fetcher = _default_extras_fetcher(client)

    log: List[Dict[str, Any]] = []
    ok = 0
    skipped = 0
    already = 0
    err = 0
    anomalies: List[Dict[str, Any]] = []

    for cand in candidates:
        rid = _as_int_id(cand.get("id_edital"))
        if rid is None:
            skipped += 1
            log.append({"status": "skipped", "reason": "sem_id_edital"})
            continue
        try:
            row = row_fetcher(rid)
            if row is None:
                skipped += 1
                log.append({"id_edital": rid, "status": "skipped", "reason": "registro_nao_encontrado"})
                continue
            if not is_grants_gov_record(row):
                skipped += 1
                log.append({"id_edital": rid, "status": "skipped", "reason": "fonte_nao_grants"})
                continue

            cf = get_curadoria_front(row)
            if not is_marked_hidden_duplicate(cf):
                skipped += 1
                log.append({"id_edital": rid, "status": "skipped", "reason": "nao_marcado_oculto"})
                continue
            if _as_int_id(cf.get("duplicate_of_id_edital")) is None:
                anomalies.append({"id_edital": rid, "reason": "oculto_sem_duplicate_of_id_edital"})
                skipped += 1
                log.append({"id_edital": rid, "status": "skipped", "reason": "anomalia_sem_duplicate_of"})
                continue
            if visibility_backfill_complete(cf):
                already += 1
                log.append({"id_edital": rid, "status": "already_ok"})
                continue

            patch = cand.get("curadoria_patch") or build_visibility_backfill_patch(cf)
            if not patch:
                already += 1
                log.append({"id_edital": rid, "status": "already_ok"})
                continue

            new_extras = merge_curadoria_front(_get_extras(row), patch)
            client.table("edital").update({"extras": new_extras}).eq("id_edital", rid).execute()
            ok += 1
            log.append(
                {
                    "id_edital": rid,
                    "status": "ok",
                    "patch_keys": list(patch.keys()),
                    "duplicate_of_id_edital": cf.get("duplicate_of_id_edital"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            err += 1
            log.append({"id_edital": rid, "status": "error", "error": str(exc)[:200]})

    return {
        "version": "grants_duplicate_visibility_backfill_10.3c",
        "applied_at": _utc_now_iso(),
        "ok": ok,
        "already_ok": already,
        "skipped": skipped,
        "errors": err,
        "total_candidates": len(candidates),
        "anomalies": anomalies,
        "log": log,
    }


def audit_visibility_compliance(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Auditoria 10.3C — conformidade de hidden_duplicate + visibility."""
    grants = [r for r in records if is_grants_gov_record(r)]
    hidden: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []
    compliant = 0

    for rec in grants:
        cf = get_curadoria_front(rec)
        rid = rec.get("id_edital")
        if not is_marked_hidden_duplicate(cf):
            continue
        hidden.append(rec)
        problems = []
        if cf.get("hidden_duplicate") is not True:
            problems.append("missing_hidden_duplicate_boolean")
        if str(cf.get("visibility") or "").lower() != VISIBILITY_TARGET:
            problems.append("missing_visibility_hidden_duplicate")
        if not cf.get("duplicate_of_id_edital"):
            problems.append("missing_duplicate_of_id_edital")
        if not cf.get("duplicate_reason"):
            problems.append("missing_duplicate_reason")
        if not cf.get("canonical_link"):
            problems.append("missing_canonical_link")
        if problems:
            issues.append({"id_edital": rid, "problems": problems, "curadoria_front": cf})
        else:
            compliant += 1

        if _is_referenced_as_canonical(_as_int_id(rid) or -1, grants) and is_marked_hidden_duplicate(cf):
            issues.append({"id_edital": rid, "problems": ["canonico_referenciado_esta_oculto"]})

    visible_canon_hidden = [
        r.get("id_edital")
        for r in grants
        if not is_marked_hidden_duplicate(get_curadoria_front(r))
        and _is_referenced_as_canonical(_as_int_id(r.get("id_edital")) or -1, grants)
        and get_curadoria_front(r).get("hidden_duplicate") is True
    ]

    return {
        "total_grants": len(grants),
        "hidden_duplicates": len(hidden),
        "visibility_compliant": compliant,
        "visibility_issues": len(issues),
        "issues": issues,
        "canon_hidden_errors": visible_canon_hidden,
        "all_compliant": len(issues) == 0 and len(visible_canon_hidden) == 0,
    }
