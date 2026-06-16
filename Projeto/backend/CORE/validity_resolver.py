"""
Resolvedor de validade/prazo (Backend 9–10).

Usa actionability_type como camada principal (Backend 10).
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from deadline_backfill import resolve_sem_prazo_context
from deadline_normalizer import normalize_deadline
from noise_classifier import classify_noise

Confidence = str
ValidadeStatus = str

_NAO_APLICAVEL_ACTIONABILITY = frozenset(
    {
        "noticia",
        "evento",
        "portal_generico",
        "pagina_institucional",
        "resultado",
        "retificacao",
        "documento_auxiliar",
        "sem_oportunidade",
    }
)

_OPORTUNIDADE_ACTIONABILITY = frozenset(
    {"oportunidade_principal", "oportunidade_sem_prazo"}
)


def _today() -> date:
    return date.today()


def resolve_validity(
    record: Dict[str, Any],
    *,
    noise: Optional[Dict[str, Any]] = None,
    deadline: Optional[Dict[str, Any]] = None,
    backfill: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    dl = deadline if deadline is not None else normalize_deadline(record)
    nz = noise if noise is not None else classify_noise(record)

    notes: List[str] = []
    prazo_data = dl.get("prazo_data")
    prazo_raw = dl.get("prazo_raw")
    prazo_status = dl.get("prazo_status")
    prazo_conf = dl.get("prazo_confidence") or "nenhuma"
    prazo_source = dl.get("prazo_source_field")

    actionability_type = nz.get("actionability_type") or "desconhecido"
    is_actionable = nz.get("is_actionable_opportunity")

    validade_status: ValidadeStatus = "desconhecido"
    validade_confidence: Confidence = "nenhuma"

    # Portal útil: não é edital com prazo, mas mantém navegação
    if actionability_type == "portal_util":
        validade_status = "nao_aplicavel"
        validade_confidence = "alta"
        notes.append("portal_util:nao_aplicavel_prazo")

    elif actionability_type in _NAO_APLICAVEL_ACTIONABILITY:
        validade_status = "nao_aplicavel"
        validade_confidence = nz.get("confidence") or "alta"
        notes.append(f"actionability:{actionability_type}")
        if actionability_type in ("retificacao", "resultado", "documento_auxiliar"):
            notes.append("documento_auxiliar_de_oportunidade")

    elif record.get("tipo_registro") == "noticia" and actionability_type not in _OPORTUNIDADE_ACTIONABILITY:
        validade_status = "nao_aplicavel"
        validade_confidence = "alta"
        notes.append("tipo_registro:noticia")

    if prazo_status == "prazo_invalido" and validade_status in ("desconhecido", "nao_aplicavel"):
        if actionability_type in _OPORTUNIDADE_ACTIONABILITY:
            validade_status = "prazo_invalido"
            validade_confidence = prazo_conf if prazo_conf != "nenhuma" else "baixa"
            notes.append("prazo_invalido_prioritario")

    if validade_status == "desconhecido" and actionability_type in _OPORTUNIDADE_ACTIONABILITY:
        if prazo_status == "prazo_invalido":
            validade_status = "prazo_invalido"
            validade_confidence = prazo_conf if prazo_conf != "nenhuma" else "baixa"
            notes.append("prazo_invalido")
        elif prazo_data:
            try:
                d = date.fromisoformat(str(prazo_data)[:10])
            except ValueError:
                validade_status = "prazo_invalido"
                validade_confidence = "baixa"
            else:
                delta = (d - _today()).days
                if delta < 0:
                    validade_status = "encerrado"
                elif delta <= 7:
                    validade_status = "vencendo_7"
                elif delta <= 30:
                    validade_status = "vencendo_30"
                else:
                    validade_status = "aberto"
                validade_confidence = prazo_conf if prazo_conf != "nenhuma" else "media"
        else:
            validade_status = "sem_prazo"
            validade_confidence = "media"
            notes.append("oportunidade_sem_prazo_estruturado")

    elif validade_status == "desconhecido":
        if is_actionable:
            validade_status = "sem_prazo"
            validade_confidence = "baixa"
            notes.append("acionavel_incerto")
        else:
            validade_status = "nao_aplicavel"
            validade_confidence = "media"
            notes.append("nao_acionavel_sem_prazo")

    if validade_status == "desconhecido" and not notes:
        notes.append("dados_insuficientes")

    validade_reason = notes[-1] if notes else None
    if dl.get("validade_reason"):
        validade_reason = dl.get("validade_reason")

    if backfill is None:
        extras = record.get("extras")
        if isinstance(extras, dict):
            backfill = extras.get("_deadline_backfill_preview")

    sem_ctx = resolve_sem_prazo_context(
        record,
        actionability_type=actionability_type,
        validade_status=validade_status,
        backfill=backfill,
    )

    return {
        "validade_status": validade_status,
        "validade_data": prazo_data,
        "validade_raw": prazo_raw,
        "validade_confidence": validade_confidence,
        "validade_source": prazo_source,
        "validade_notes": notes,
        "validade_reason": validade_reason,
        "prazo_detectado": dl.get("prazo_detectado"),
        "prazo_fonte": dl.get("prazo_fonte") or (backfill or {}).get("prazo_fonte"),
        "sem_prazo_kind": sem_ctx.get("sem_prazo_kind"),
        "sem_prazo_reason": sem_ctx.get("sem_prazo_reason"),
        "deadline_backfill_status": (backfill or {}).get("deadline_backfill_status")
        or sem_ctx.get("deadline_backfill_status"),
        "actionability_type": actionability_type,
    }
