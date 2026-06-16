"""
Resolução controlada de oportunidades Grants.gov duplicadas (Backend 10.3B).

Contexto: o 10.3A canonicalizou links Grants.gov para
`https://www.grants.gov/search-results-detail/<id>`. 97 registros colidiram no
`link UNIQUE` porque a mesma oportunidade existe em mais de uma linha.

Este módulo NÃO deleta, NÃO mescla fisicamente, NÃO altera schema, NÃO altera o
registro canônico e NÃO altera `link`/`prazo`/`titulo`. Apenas marca o registro
DUPLICADO com metadados em `extras.curadoria_front.hidden_duplicate` para que o
frontend o oculte por padrão.
"""
from __future__ import annotations

import copy
import os
import re
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

from grants_link_resolver import (
    WWW_DETAIL_BASE,
    is_grants_gov_record,
    normalize_grants_gov_link,
)

DUPLICATE_REASON = "same_grants_opportunity_id"
DUPLICATE_SOURCE = "grants_link_fix_10.3a"
RESOLVED_BY = "backend_10.3b"
DEFAULT_MAX_BATCH = 100

_CANONICAL_DETAIL_RE = re.compile(
    r"^https://www\.grants\.gov/search-results-detail/(\d+)/?$", re.I
)


def controlled_apply_enabled() -> bool:
    return os.getenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "").strip() in ("1", "true", "True")


def duplicate_resolution_enabled() -> bool:
    return os.getenv("EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION", "").strip() in ("1", "true", "True")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_canonical_detail_link(link: Any) -> bool:
    return bool(_CANONICAL_DETAIL_RE.match(str(link or "").strip()))


def _canonical_id_from_link(link: Any) -> str:
    m = _CANONICAL_DETAIL_RE.match(str(link or "").strip())
    return m.group(1) if m else ""


def _as_int_id(val: Any) -> Optional[int]:
    if val is None or val == "":
        return None
    try:
        return int(str(val).strip())
    except (TypeError, ValueError):
        return None


def _get_extras(record: Dict[str, Any]) -> Dict[str, Any]:
    ex = record.get("extras_raw") if isinstance(record, dict) else None
    if not isinstance(ex, dict):
        ex = record.get("extras") if isinstance(record, dict) else None
    return ex if isinstance(ex, dict) else {}


def already_hidden_duplicate(extras: Dict[str, Any]) -> bool:
    cf = extras.get("curadoria_front") if isinstance(extras, dict) else None
    return bool(isinstance(cf, dict) and cf.get("hidden_duplicate") is True)


def build_curadoria_patch(
    *,
    duplicate_of_id_edital: int,
    canonical_link: str,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "hidden_duplicate": True,
        "visibility": "hidden_duplicate",
        "duplicate_of_id_edital": duplicate_of_id_edital,
        "duplicate_reason": DUPLICATE_REASON,
        "duplicate_source": DUPLICATE_SOURCE,
        "resolved_by": RESOLVED_BY,
        "resolved_at": now or _utc_now_iso(),
        "canonical_link": canonical_link,
    }


def merge_curadoria_front(
    existing_extras: Optional[Dict[str, Any]],
    curadoria_patch: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Merge seguro: preserva todo o extras e os campos existentes de curadoria_front,
    aplicando apenas o patch de hidden_duplicate por cima.
    """
    merged = copy.deepcopy(existing_extras) if isinstance(existing_extras, dict) else {}
    cf = merged.get("curadoria_front")
    if not isinstance(cf, dict):
        cf = {}
    cf = copy.deepcopy(cf)
    cf.update(curadoria_patch)
    merged["curadoria_front"] = cf
    return merged


def _dup_entry_fields(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai campos do item de duplicate_targets.json (ou registro equivalente)."""
    dup_id = _as_int_id(entry.get("id_edital"))
    dup_of = _as_int_id(
        entry.get("duplicate_of_id_edital")
        or entry.get("duplicate_of")
        or entry.get("canonical_id_edital")
    )
    canonical_link = str(entry.get("new_link") or entry.get("canonical_link") or "").strip()
    opportunity_id = str(
        entry.get("opportunity_id") or _canonical_id_from_link(canonical_link) or ""
    ).strip()
    return {
        "id_edital": dup_id,
        "duplicate_of_id_edital": dup_of,
        "canonical_link": canonical_link,
        "opportunity_id": opportunity_id,
        "titulo": entry.get("titulo"),
    }


def _validate_with_records(
    fields: Dict[str, Any],
    records_by_id: Dict[int, Dict[str, Any]],
) -> Optional[str]:
    """Validação rica quando temos os registros (DB). Retorna motivo de invalidez ou None."""
    dup = records_by_id.get(fields["id_edital"])
    canonical = records_by_id.get(fields["duplicate_of_id_edital"])
    if dup is None:
        return "duplicado_nao_encontrado"
    if canonical is None:
        return "canonico_nao_encontrado"
    if not is_grants_gov_record(dup):
        return "duplicado_nao_e_grants"
    if not is_grants_gov_record(canonical):
        return "canonico_nao_e_grants"

    canonical_link = fields["canonical_link"]
    # O canônico precisa ter (ou resolver para) o link canônico válido.
    canon_current = str(canonical.get("link") or "").strip()
    canon_resolved = normalize_grants_gov_link(canonical).get("canonical_link") or ""
    if not is_canonical_detail_link(canon_current) and not is_canonical_detail_link(canon_resolved):
        return "canonico_sem_link_canonico_valido"

    # Devem compartilhar a mesma oportunidade (opportunity_id / canonical_link).
    dup_opp = _canonical_id_from_link(canonical_link) or fields["opportunity_id"]
    canon_opp = _canonical_id_from_link(canon_current) or _canonical_id_from_link(canon_resolved)
    if dup_opp and canon_opp and dup_opp != canon_opp:
        return "opportunity_id_divergente"
    return None


def build_hide_candidates(
    duplicate_targets: List[Dict[str, Any]],
    *,
    records_by_id: Optional[Dict[int, Dict[str, Any]]] = None,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Dry-run: separa candidatos a ocultar, já ocultos e inválidos. Não escreve no banco.
    """
    candidates_to_hide: List[Dict[str, Any]] = []
    already_hidden: List[Dict[str, Any]] = []
    invalid_duplicates: List[Dict[str, Any]] = []
    canonical_records: List[Dict[str, Any]] = []
    seen_canonical: set = set()

    for entry in duplicate_targets:
        if not isinstance(entry, dict):
            invalid_duplicates.append({"entry": entry, "reason": "entrada_invalida"})
            continue
        f = _dup_entry_fields(entry)

        reason: Optional[str] = None
        if f["id_edital"] is None:
            reason = "sem_id_edital"
        elif f["duplicate_of_id_edital"] is None:
            reason = "sem_duplicate_of_id_edital"
        elif not is_canonical_detail_link(f["canonical_link"]):
            reason = "canonical_link_invalido"
        elif f["id_edital"] == f["duplicate_of_id_edital"]:
            reason = "duplicado_e_o_proprio_canonico"

        if reason is None and records_by_id is not None:
            reason = _validate_with_records(f, records_by_id)

        if reason is not None:
            invalid_duplicates.append({**f, "reason": reason})
            continue

        # idempotência: já oculto?
        if records_by_id is not None:
            dup_rec = records_by_id.get(f["id_edital"]) or {}
            if already_hidden_duplicate(_get_extras(dup_rec)):
                already_hidden.append(f)
                continue

        patch = build_curadoria_patch(
            duplicate_of_id_edital=f["duplicate_of_id_edital"],
            canonical_link=f["canonical_link"],
            now=now,
        )
        candidates_to_hide.append({**f, "curadoria_patch": patch})

        if f["duplicate_of_id_edital"] not in seen_canonical:
            seen_canonical.add(f["duplicate_of_id_edital"])
            canonical_records.append(
                {
                    "id_edital": f["duplicate_of_id_edital"],
                    "canonical_link": f["canonical_link"],
                    "opportunity_id": f["opportunity_id"],
                }
            )

    stats = {
        "total_duplicate_targets": len(duplicate_targets),
        "candidates_to_hide": len(candidates_to_hide),
        "already_hidden": len(already_hidden),
        "invalid_duplicates": len(invalid_duplicates),
        "distinct_canonical_records": len(canonical_records),
        "validated_against_db": records_by_id is not None,
    }
    return {
        "stats": stats,
        "candidates_to_hide": candidates_to_hide,
        "already_hidden": already_hidden,
        "invalid_duplicates": invalid_duplicates,
        "canonical_records": canonical_records,
    }


def _parse_deadline(record: Dict[str, Any]) -> Optional[str]:
    for key in ("prazo_envio", "fim_inscricao", "deadline", "close_date"):
        val = record.get(key)
        if val:
            return str(val)
    ex = _get_extras(record)
    for key in ("prazo_envio", "fim_inscricao"):
        if ex.get(key):
            return str(ex[key])
    return None


def _completeness_score(record: Dict[str, Any]) -> int:
    score = 0
    for key in ("titulo", "descricao", "objetivo", "link"):
        if _norm_str(record.get(key)):
            score += 1
    return score


def _norm_str(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    return s if s.lower() not in ("", "null", "none") else ""


def extract_opportunity_id(record: Dict[str, Any]) -> str:
    """ID numérico da oportunidade Grants.gov (link canônico, extras ou resolver)."""
    link = _norm_str(record.get("link"))
    opp = _canonical_id_from_link(link)
    if opp:
        return opp
    resolved = normalize_grants_gov_link(record).get("opportunity_id") or ""
    if _norm_str(resolved):
        return str(resolved).strip()
    ex = _get_extras(record)
    for key in ("opportunity_id", "grants_opportunity_id", "legacy_opp_id"):
        val = _norm_str(ex.get(key))
        if val and val.isdigit():
            return val
    return ""


def canonical_record_score(record: Dict[str, Any]) -> Tuple[int, str, int, int, str, int]:
    """
    Pontuação para escolha do canônico (maior = preferido).
    Desempate estável: menor id_edital por último na tupla (invertido no sort).
    """
    link = _norm_str(record.get("link"))
    canonical_link = 1000 if is_canonical_detail_link(link) else 0
    deadline = _parse_deadline(record) or ""
    completeness = _completeness_score(record)
    quality = int(record.get("score") or record.get("relevancia") or 0)
    updated = _norm_str(record.get("atualizado_em") or record.get("criado_em"))
    rid = _as_int_id(record.get("id_edital")) or 10**12
    return (canonical_link, deadline, quality, completeness, updated, -rid)


def pick_canonical_record(group: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Escolhe 1 canônico entre registros do mesmo opportunity_id."""
    if not group:
        raise ValueError("grupo vazio")
    if len(group) == 1:
        return group[0]
    return max(group, key=canonical_record_score)


def group_grants_by_opportunity_id(
    records: List[Dict[str, Any]],
) -> Dict[str, List[Dict[str, Any]]]:
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for rec in records:
        if not is_grants_gov_record(rec):
            continue
        opp = extract_opportunity_id(rec)
        if not opp:
            continue
        groups.setdefault(opp, []).append(rec)
    return {k: v for k, v in groups.items() if len(v) > 1}


def build_duplicate_groups(
    duplicate_targets: List[Dict[str, Any]],
    *,
    records_by_id: Optional[Dict[int, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Agrupa duplicate_targets por opportunity_id para auditoria / groups.json."""
    by_opp: Dict[str, Dict[str, Any]] = {}
    for entry in duplicate_targets:
        f = _dup_entry_fields(entry)
        opp = f.get("opportunity_id") or ""
        if not opp:
            continue
        grp = by_opp.setdefault(
            opp,
            {
                "opportunity_id": opp,
                "canonical_link": f.get("canonical_link"),
                "canonical_id_edital": f.get("duplicate_of_id_edital"),
                "duplicate_ids": [],
                "size": 0,
            },
        )
        if f.get("id_edital") is not None:
            grp["duplicate_ids"].append(f["id_edital"])
        grp["size"] = 1 + len(grp["duplicate_ids"])
        if records_by_id and f.get("duplicate_of_id_edital") in records_by_id:
            canon = records_by_id[f["duplicate_of_id_edital"]]
            grp["canonical_titulo"] = canon.get("titulo")
    return list(by_opp.values())


def build_duplicate_targets_from_groups(
    groups: Dict[str, List[Dict[str, Any]]],
    *,
    now: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Gera duplicate_targets a partir de grupos DB (mesma opportunity_id).
    Usa pick_canonical_record para escolher o canônico.
    """
    targets: List[Dict[str, Any]] = []
    for opp, members in groups.items():
        canonical = pick_canonical_record(members)
        canon_id = _as_int_id(canonical.get("id_edital"))
        canon_link = _norm_str(canonical.get("link"))
        if not is_canonical_detail_link(canon_link):
            resolved = normalize_grants_gov_link(canonical).get("canonical_link") or ""
            canon_link = resolved if is_canonical_detail_link(resolved) else f"{WWW_DETAIL_BASE}/{opp}"
        for rec in members:
            rid = _as_int_id(rec.get("id_edital"))
            if rid is None or rid == canon_id:
                continue
            targets.append(
                {
                    "id_edital": rid,
                    "duplicate_of_id_edital": canon_id,
                    "new_link": canon_link,
                    "canonical_link": canon_link,
                    "opportunity_id": opp,
                    "titulo": rec.get("titulo"),
                }
            )
    return targets


def _default_extras_fetcher(supabase_client: Any) -> Callable[[int], Optional[Dict[str, Any]]]:
    def _fetch(id_edital: int) -> Optional[Dict[str, Any]]:
        resp = (
            supabase_client.table("edital")
            .select("id_edital,fonte_recurso,extras")
            .eq("id_edital", id_edital)
            .limit(1)
            .execute()
        )
        data = getattr(resp, "data", None)
        if isinstance(data, list) and data:
            return data[0]
        return None

    return _fetch


def apply_hide_candidates(
    candidates: List[Dict[str, Any]],
    *,
    confirm_large: bool = False,
    supabase_client: Any = None,
    row_fetcher: Optional[Callable[[int], Optional[Dict[str, Any]]]] = None,
    now: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Apply controlado: marca duplicatas como ocultas em extras.curadoria_front.
    Só altera `extras` do registro DUPLICADO. Exige flags explícitas. Idempotente.
    """
    if not controlled_apply_enabled():
        raise RuntimeError(
            "Apply abortado: EDITALFINDER_ALLOW_CONTROLLED_APPLY não está ativo."
        )
    if not duplicate_resolution_enabled():
        raise RuntimeError(
            "Apply abortado: EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION não está ativo."
        )
    if len(candidates) > DEFAULT_MAX_BATCH and not confirm_large:
        raise RuntimeError(
            f"Lote grande ({len(candidates)} > {DEFAULT_MAX_BATCH}). Use --confirm-large."
        )

    # Pré-validação: precisa de id_edital e duplicate_of_id_edital em todos.
    for i, cand in enumerate(candidates):
        f = _dup_entry_fields(cand)
        if f["id_edital"] is None:
            raise RuntimeError(f"Candidato {i} sem id_edital — apply abortado.")
        if f["duplicate_of_id_edital"] is None:
            raise RuntimeError(f"Candidato {i} sem duplicate_of_id_edital — apply abortado.")
        if not is_canonical_detail_link(f["canonical_link"]):
            raise RuntimeError(f"Candidato {i} canonical_link inválido — apply abortado.")

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
    err = 0
    skipped = 0
    already = 0

    for cand in candidates:
        f = _dup_entry_fields(cand)
        dup_id = f["id_edital"]
        dup_of = f["duplicate_of_id_edital"]
        canonical_link = f["canonical_link"]
        try:
            row = row_fetcher(dup_id)
            if row is None:
                skipped += 1
                log.append({"id_edital": dup_id, "status": "skipped", "reason": "registro_nao_encontrado"})
                continue
            if not is_grants_gov_record(row):
                skipped += 1
                log.append({"id_edital": dup_id, "status": "skipped", "reason": "fonte_nao_grants"})
                continue
            existing_extras = _get_extras(row)
            if already_hidden_duplicate(existing_extras):
                already += 1
                log.append({"id_edital": dup_id, "status": "already_hidden", "reason": "ja_oculto"})
                continue

            patch = cand.get("curadoria_patch") or build_curadoria_patch(
                duplicate_of_id_edital=dup_of,
                canonical_link=canonical_link,
                now=now,
            )
            new_extras = merge_curadoria_front(existing_extras, patch)

            # Atualiza SOMENTE a coluna extras do registro duplicado.
            client.table("edital").update({"extras": new_extras}).eq("id_edital", dup_id).execute()
            ok += 1
            log.append(
                {
                    "id_edital": dup_id,
                    "duplicate_of_id_edital": dup_of,
                    "canonical_link": canonical_link,
                    "status": "ok",
                }
            )
        except Exception as exc:  # noqa: BLE001
            err += 1
            log.append({"id_edital": dup_id, "status": "error", "error": str(exc)[:200]})

    return {
        "version": "grants_duplicate_resolution_10.3b",
        "applied_at": _utc_now_iso(),
        "ok": ok,
        "already_hidden": already,
        "skipped": skipped,
        "errors": err,
        "total_candidates": len(candidates),
        "log": log,
    }
