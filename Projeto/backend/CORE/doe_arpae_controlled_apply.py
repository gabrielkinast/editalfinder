"""
Apply controlado de deadlines DOE_ARPAE (Backend 10.2C).

Dry-run por padrão; escrita no banco somente com EDITALFINDER_ALLOW_CONTROLLED_APPLY=1.
"""
from __future__ import annotations

import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from deadline_backfill import (
    DOE_DEADLINE_KEYS,
    apply_deadline_backfill_to_payload,
    controlled_apply_enabled,
    deadline_backfill_enabled,
    extract_source_deadline_fields,
    normalize_backfill_source,
)
from deadline_normalizer import infer_locale_from_source, parse_deadline_date
from doe_arpae_recrawl import stats_for_doe_recrawl_items

DOE_SOURCE_KEY = "doe_arpae"
DOE_FONTES = frozenset({"doe_arpae", "doe arpa-e", "arpa-e", "arpa e", "doe arpa"})
CONTROLLED_APPLY_VERSION = "doe_arpae_controlled_apply_10.2c"
DEFAULT_MAX_APPLY_BATCH = 100
DRY_RUN_REPORT_MAX_AGE_HOURS = 72

OUT_DIR_NAME = "doe_arpae_deadline_apply"
SUMMARY_FILENAME = "summary.md"
BEFORE_AFTER_FILENAME = "before_after.json"
CANDIDATES_FILENAME = "candidates_to_update.json"
REJECTED_FILENAME = "rejected.json"
NO_DEADLINE_FILENAME = "no_deadline.json"


def is_doe_arpae_record(record: Dict[str, Any]) -> bool:
    fonte = str(record.get("fonte") or record.get("fonte_recurso") or "").strip().lower()
    if any(f in fonte for f in DOE_FONTES):
        return True
    return normalize_backfill_source(record) == DOE_SOURCE_KEY


def _get_extras(record: Dict[str, Any]) -> Dict[str, Any]:
    extras = record.get("extras")
    return extras if isinstance(extras, dict) else {}


def _has_doe_deadline_in_payload(item: Dict[str, Any]) -> bool:
    ex = _get_extras(item)
    for key in DOE_DEADLINE_KEYS:
        if ex.get(key) or item.get(key):
            return True
    if re.search(r"Notice Of Funding Opportunity \(NOFO\)", _blob(item), re.I):
        return True
    return bool(item.get("fim_inscricao"))


def _blob(item: Dict[str, Any]) -> str:
    ex = _get_extras(item)
    return f"{item.get('titulo') or ''} {item.get('descricao') or ''} {ex.get('nofo_text') or ''}"


def _has_nofo_tbd(item: Dict[str, Any]) -> bool:
    ex = _get_extras(item)
    if ex.get("nofo_tbd"):
        return True
    return bool(re.search(r"NOFO.*\bTBD\b", _blob(item), re.I))


def _has_nofo_two_dates(item: Dict[str, Any]) -> bool:
    ex = _get_extras(item)
    return bool(ex.get("nofo_two_dates"))


def snapshot_deadline_state(record: Dict[str, Any]) -> Dict[str, Any]:
    extras = _get_extras(record)
    return {
        "link": record.get("link"),
        "titulo": (record.get("titulo") or "")[:120],
        "fonte": record.get("fonte") or record.get("fonte_recurso"),
        "fim_inscricao": record.get("fim_inscricao"),
        "prazo_envio": record.get("prazo_envio"),
        "extras_full_application_deadline": extras.get("full_application_deadline"),
        "extras_concept_paper_deadline": extras.get("concept_paper_deadline"),
        "extras_deadline_source_field": extras.get("deadline_source_field"),
        "sem_prazo_kind": extras.get("sem_prazo_kind"),
        "id_edital": record.get("id_edital"),
    }


def _valid_prazo_iso(val: Any, record: Dict[str, Any]) -> Optional[str]:
    if not val:
        return None
    locale = infer_locale_from_source(
        str(record.get("fonte_recurso") or record.get("fonte") or "DOE_ARPAE")
    )
    parsed = parse_deadline_date(val, locale_hint=locale, source_field="prazo_envio")
    return parsed["date"] if parsed else None


def classify_apply_action(
    recrawl_item: Dict[str, Any],
    *,
    db_record: Optional[Dict[str, Any]] = None,
) -> Tuple[str, Dict[str, Any]]:
    if not is_doe_arpae_record(recrawl_item):
        return "reject", {"reason": "fonte_nao_doe_arpae"}

    after_item = apply_deadline_backfill_to_payload(copy.deepcopy(recrawl_item), enabled=True)
    backfill = extract_source_deadline_fields(recrawl_item)
    status = backfill.get("deadline_backfill_status") or "no_candidate"

    before_db = db_record or {}
    before_prazo = _valid_prazo_iso(
        before_db.get("prazo_envio") or before_db.get("fim_inscricao"),
        before_db or recrawl_item,
    )
    after_prazo = _valid_prazo_iso(
        after_item.get("prazo_envio") or after_item.get("fim_inscricao"),
        after_item,
    )

    meta = {
        "deadline_backfill_status": status,
        "sem_prazo_kind": backfill.get("sem_prazo_kind"),
        "deadline_reason": backfill.get("deadline_reason"),
        "prazo_fonte": backfill.get("prazo_fonte"),
        "before_prazo_envio": before_prazo or before_db.get("prazo_envio"),
        "after_prazo_envio": after_prazo,
    }

    if status == "rejected_deadline":
        return "reject", {**meta, "reason": backfill.get("rejection_reason")}

    has_db = bool(db_record)
    has_source_deadline = _has_doe_deadline_in_payload(recrawl_item)

    if after_prazo and before_prazo and before_prazo == after_prazo:
        return "unchanged", meta

    if after_prazo and before_prazo and before_prazo != after_prazo:
        return "preserve", {**meta, "reason": "nao_sobrescrever_prazo_valido_diferente"}

    if after_prazo and (not before_prazo or not has_db):
        if has_source_deadline or status in ("new_deadline_found", "replacement_candidate"):
            return "update", {**meta, "reason": "novo_prazo_doe_arpae"}

    if status == "preserved_existing" and after_prazo and not before_prazo:
        return "update", {**meta, "reason": "db_sem_prazo_recrawl_com_deadline"}

    if status == "preserved_existing" and before_prazo:
        return "preserve", {**meta, "reason": "prazo_valido_existente"}

    if status in ("new_deadline_found", "replacement_candidate") and after_prazo:
        return "update", meta

    if status in ("no_deadline_explained", "no_candidate") and not after_prazo:
        return "no_deadline", meta

    if not after_prazo:
        return "no_deadline", meta

    return "unchanged", meta


def build_candidate_entry(
    recrawl_item: Dict[str, Any],
    *,
    db_record: Optional[Dict[str, Any]] = None,
    action: str,
    meta: Dict[str, Any],
) -> Dict[str, Any]:
    after_item = apply_deadline_backfill_to_payload(copy.deepcopy(recrawl_item), enabled=True)
    ex = _get_extras(recrawl_item)
    return {
        "action": action,
        "fonte": "DOE_ARPAE",
        "source_key": DOE_SOURCE_KEY,
        "link": recrawl_item.get("link"),
        "titulo": (recrawl_item.get("titulo") or "")[:200],
        "codigo_oportunidade": ex.get("codigo_oportunidade") or ex.get("numero_chamada"),
        "before": snapshot_deadline_state(db_record or {}),
        "after": snapshot_deadline_state(after_item),
        "payload_after": after_item,
        "meta": meta,
        "controlled_apply_version": CONTROLLED_APPLY_VERSION,
    }


def run_doe_arpae_deadline_dry_run(
    recrawl_items: List[Dict[str, Any]],
    *,
    db_by_link: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    recrawl_stats = stats_for_doe_recrawl_items(recrawl_items)
    stats = {
        "total_recrawled": len(recrawl_items),
        **recrawl_stats,
        "candidates_to_update": 0,
        "preserved": 0,
        "unchanged": 0,
        "rejected": 0,
        "no_deadline": 0,
    }
    before_after: List[Dict[str, Any]] = []
    candidates: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    no_deadline: List[Dict[str, Any]] = []

    for item in recrawl_items:
        link = str(item.get("link") or "")
        db_rec = (db_by_link or {}).get(link) if link else None
        action, meta = classify_apply_action(item, db_record=db_rec)
        entry = build_candidate_entry(item, db_record=db_rec, action=action, meta=meta)
        before_after.append(
            {"link": link, "action": action, "before": entry["before"], "after": entry["after"], "meta": meta}
        )

        if action == "update":
            stats["candidates_to_update"] += 1
            candidates.append(entry)
        elif action == "preserve":
            stats["preserved"] += 1
        elif action == "unchanged":
            stats["unchanged"] += 1
        elif action == "reject":
            stats["rejected"] += 1
            rejected.append(entry)
        elif action == "no_deadline":
            stats["no_deadline"] += 1
            no_deadline.append(entry)

    return {
        "version": CONTROLLED_APPLY_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stats": stats,
        "before_after": before_after,
        "candidates_to_update": candidates,
        "rejected": rejected,
        "no_deadline": no_deadline,
    }


def _dry_run_report_path(root: Path) -> Path:
    return root / "outputs" / OUT_DIR_NAME / SUMMARY_FILENAME


def validate_dry_run_report_recent(root: Path, max_age_hours: int = DRY_RUN_REPORT_MAX_AGE_HOURS) -> None:
    path = _dry_run_report_path(root)
    if not path.exists():
        raise RuntimeError(
            f"Relatório dry-run ausente: {path}. Execute dry_run_doe_arpae_deadline_apply.py antes do apply."
        )
    age_h = (datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 3600
    if age_h > max_age_hours:
        raise RuntimeError(
            f"Relatório dry-run expirado ({age_h:.1f}h > {max_age_hours}h). Reexecute o dry-run."
        )


def validate_candidates_batch(
    candidates: List[Dict[str, Any]],
    *,
    max_batch: int = DEFAULT_MAX_APPLY_BATCH,
    confirm_large: bool = False,
) -> None:
    if not candidates:
        raise RuntimeError("candidates_to_update vazio — nada a aplicar.")
    if len(candidates) > max_batch and not confirm_large:
        raise RuntimeError(
            f"Lote grande ({len(candidates)} > {max_batch}). Use --confirm-large para prosseguir."
        )
    for i, cand in enumerate(candidates):
        if not is_doe_arpae_record(cand.get("payload_after") or cand):
            raise RuntimeError(f"Candidato {i} não é DOE_ARPAE — apply abortado.")


def merge_extras_for_apply(
    existing_extras: Optional[Dict[str, Any]],
    new_extras: Dict[str, Any],
) -> Dict[str, Any]:
    merged = copy.deepcopy(existing_extras) if isinstance(existing_extras, dict) else {}
    for k, v in new_extras.items():
        if v is None or k.startswith("_"):
            continue
        merged[k] = v
    return merged


def resolve_prazo_for_apply(
    existing_row: Optional[Dict[str, Any]],
    mapped_new: Dict[str, Any],
    candidate_meta: Dict[str, Any],
) -> Optional[str]:
    existing_iso = _valid_prazo_iso((existing_row or {}).get("prazo_envio"), existing_row or mapped_new)
    new_iso = _valid_prazo_iso(mapped_new.get("prazo_envio"), mapped_new)
    if existing_iso and new_iso and existing_iso != new_iso:
        return existing_iso
    if existing_iso and not new_iso:
        return existing_iso
    return new_iso or mapped_new.get("prazo_envio")


def apply_doe_arpae_candidates(
    candidates: List[Dict[str, Any]],
    *,
    root: Optional[Path] = None,
    confirm_large: bool = False,
    skip_dry_run_check: bool = False,
) -> Dict[str, Any]:
    if not controlled_apply_enabled():
        raise RuntimeError("Apply abortado: EDITALFINDER_ALLOW_CONTROLLED_APPLY não está ativo.")
    if not deadline_backfill_enabled():
        raise RuntimeError("Apply abortado: EDITALFINDER_ENABLE_DEADLINE_BACKFILL não está ativo.")

    root = root or Path(__file__).resolve().parent.parent
    if not skip_dry_run_check:
        validate_dry_run_report_recent(root)

    validate_candidates_batch(candidates, confirm_large=confirm_large)

    import loader  # noqa: WPS433

    log: List[Dict[str, Any]] = []
    ok = 0
    err = 0
    skipped = 0

    for cand in candidates:
        payload = cand.get("payload_after")
        if not isinstance(payload, dict):
            skipped += 1
            log.append({"link": cand.get("link"), "status": "skipped", "reason": "sem_payload_after"})
            continue

        if not is_doe_arpae_record(payload):
            raise RuntimeError(f"Fonte inválida no apply: {payload.get('fonte')}")

        payload = apply_deadline_backfill_to_payload(copy.deepcopy(payload), enabled=True)
        mapped, extras_new = loader.map_to_db_schema(payload)
        link = str(mapped.get("link") or "")
        if not link:
            skipped += 1
            log.append({"link": None, "status": "skipped", "reason": "sem_link"})
            continue

        existing = loader.fetch_edital_by_link(link)
        if existing and not is_doe_arpae_record(existing):
            raise RuntimeError(
                f"Registro existente com fonte diferente ({existing.get('fonte_recurso')}) — abortado."
            )

        prazo = resolve_prazo_for_apply(existing, mapped, cand.get("meta") or {})
        if prazo:
            mapped["prazo_envio"] = prazo

        merged_extras = merge_extras_for_apply(existing.get("extras") if existing else None, extras_new)
        row = loader._merge_db_row(existing, mapped, merged_extras, payload)  # noqa: SLF001
        status, id_edital = loader.inserir_ou_atualizar_edital(row)
        entry = {
            "link": link,
            "status": status,
            "id_edital": id_edital,
            "prazo_envio": row.get("prazo_envio"),
            "action": cand.get("action"),
            "had_existing": bool(existing),
        }
        log.append(entry)
        if status == "ok":
            ok += 1
            if id_edital:
                loader.save_detail_tables(id_edital, merged_extras)
        else:
            err += 1

    return {
        "version": CONTROLLED_APPLY_VERSION,
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "total_candidates": len(candidates),
        "ok": ok,
        "errors": err,
        "skipped": skipped,
        "log": log,
    }


def load_candidates_file(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        return raw.get("candidates_to_update") or raw.get("items") or []
    return []
