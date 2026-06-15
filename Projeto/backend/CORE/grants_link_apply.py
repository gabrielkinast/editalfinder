"""
Apply controlado de correção de links Grants.gov (Backend 10.3A).

Regras de segurança:
- Exige EDITALFINDER_ALLOW_CONTROLLED_APPLY=1 e EDITALFINDER_ALLOW_LINK_FIX=1.
- Só aceita registros Grants.gov.
- Só aceita new_link https em grants.gov, nunca page-not-found.
- Update preferencial por id_edital (evita duplicação por link UNIQUE).
- Sem id_edital → não aplica (upsert por link duplicaria registros).
- Lote > 100 exige confirm_large.
- Nunca deleta registros. Gera apply_log com old_link/new_link.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from grants_link_resolver import is_grants_gov_record, is_safe_grants_link

DEFAULT_MAX_LINK_FIX_BATCH = 100


def controlled_apply_enabled() -> bool:
    return os.getenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "").strip() in ("1", "true", "True")


def link_fix_enabled() -> bool:
    return os.getenv("EDITALFINDER_ALLOW_LINK_FIX", "").strip() in ("1", "true", "True")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _candidate_is_grants(cand: Dict[str, Any]) -> bool:
    probe = {
        "fonte": cand.get("fonte") or cand.get("fonte_recurso") or "Grants.gov",
        "link": cand.get("old_link") or cand.get("link"),
        "extras": {
            "grants_opportunity_id": cand.get("opportunity_id"),
            "grants_opportunity_number": cand.get("opportunity_number"),
        },
    }
    # Candidatos vêm do dry-run, que já filtra Grants.gov; reforço defensivo:
    if "grants" in str(probe["fonte"]).lower():
        return True
    return is_grants_gov_record(probe)


def validate_link_fix_candidate(cand: Dict[str, Any]) -> Optional[str]:
    """Retorna motivo de rejeição (str) ou None se válido."""
    if not isinstance(cand, dict):
        return "candidato_invalido"
    if not _candidate_is_grants(cand):
        return "fonte_nao_grants"
    new_link = str(cand.get("new_link") or "").strip()
    if not new_link:
        return "sem_new_link"
    if not is_safe_grants_link(new_link):
        return "new_link_inseguro_ou_page_not_found"
    if cand.get("id_edital") in (None, ""):
        return "sem_id_edital_upsert_por_link_inseguro"
    if str(cand.get("old_link") or "").strip() == new_link:
        return "sem_mudanca"
    return None


def apply_grants_link_candidates(
    candidates: List[Dict[str, Any]],
    *,
    confirm_large: bool = False,
    supabase_client: Any = None,
) -> Dict[str, Any]:
    """
    Aplica correção de links por id_edital. Exige flags explícitas.
    """
    if not controlled_apply_enabled():
        raise RuntimeError(
            "Apply abortado: EDITALFINDER_ALLOW_CONTROLLED_APPLY não está ativo."
        )
    if not link_fix_enabled():
        raise RuntimeError(
            "Apply abortado: EDITALFINDER_ALLOW_LINK_FIX não está ativo."
        )

    if len(candidates) > DEFAULT_MAX_LINK_FIX_BATCH and not confirm_large:
        raise RuntimeError(
            f"Lote grande ({len(candidates)} > {DEFAULT_MAX_LINK_FIX_BATCH}). "
            f"Use --confirm-large para prosseguir."
        )

    # Pré-validação: aborta o lote se houver candidato de fonte não-Grants.
    for i, cand in enumerate(candidates):
        if not _candidate_is_grants(cand):
            raise RuntimeError(f"Candidato {i} não é Grants.gov — apply abortado.")

    client = supabase_client
    if client is None:
        import loader  # noqa: WPS433

        client = loader.supabase
    if client is None:
        raise RuntimeError("Supabase não configurado — apply abortado.")

    log: List[Dict[str, Any]] = []
    ok = 0
    err = 0
    skipped = 0
    duplicate = 0
    seen_targets: Dict[str, Any] = {}

    for cand in candidates:
        reason = validate_link_fix_candidate(cand)
        if reason:
            skipped += 1
            log.append(
                {
                    "id_edital": cand.get("id_edital"),
                    "old_link": cand.get("old_link"),
                    "new_link": cand.get("new_link"),
                    "status": "skipped",
                    "reason": reason,
                }
            )
            continue
        id_edital = cand["id_edital"]
        new_link = str(cand["new_link"]).strip()

        # Link tem UNIQUE: não tentar aplicar o mesmo alvo duas vezes no lote.
        if new_link in seen_targets and seen_targets[new_link] != id_edital:
            duplicate += 1
            log.append(
                {
                    "id_edital": id_edital,
                    "old_link": cand.get("old_link"),
                    "new_link": new_link,
                    "status": "skipped",
                    "reason": "duplicate_target_in_batch",
                    "duplicate_of_id_edital": seen_targets[new_link],
                }
            )
            continue

        try:
            resp = (
                client.table("edital")
                .update({"link": new_link})
                .eq("id_edital", id_edital)
                .execute()
            )
            data = getattr(resp, "data", None)
            # PostgREST com return=representation devolve as linhas atualizadas.
            # Lista vazia => nenhuma linha afetada (id inexistente / RLS).
            if isinstance(data, list) and len(data) == 0:
                skipped += 1
                log.append(
                    {
                        "id_edital": id_edital,
                        "old_link": cand.get("old_link"),
                        "new_link": new_link,
                        "status": "skipped",
                        "reason": "no_rows_affected",
                    }
                )
                continue
            seen_targets[new_link] = id_edital
            ok += 1
            log.append(
                {
                    "id_edital": id_edital,
                    "old_link": cand.get("old_link"),
                    "new_link": new_link,
                    "link_status": cand.get("link_status"),
                    "status": "ok",
                }
            )
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            # Colisão de UNIQUE (link já existe em outro registro) => duplicado,
            # não é erro de apply. Nunca deletamos; vai para revisão manual.
            if "23505" in msg or "duplicate key" in msg.lower() or "edital_link_key" in msg:
                duplicate += 1
                log.append(
                    {
                        "id_edital": id_edital,
                        "old_link": cand.get("old_link"),
                        "new_link": new_link,
                        "status": "skipped",
                        "reason": "duplicate_link_exists",
                        "error": msg[:200],
                    }
                )
                continue
            err += 1
            log.append(
                {
                    "id_edital": id_edital,
                    "old_link": cand.get("old_link"),
                    "new_link": new_link,
                    "status": "error",
                    "error": msg[:200],
                }
            )

    return {
        "version": "grants_link_apply_10.3a",
        "applied_at": _utc_now_iso(),
        "ok": ok,
        "errors": err,
        "skipped": skipped,
        "duplicate": duplicate,
        "total_candidates": len(candidates),
        "log": log,
    }
