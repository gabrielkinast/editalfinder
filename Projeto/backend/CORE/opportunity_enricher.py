"""
Enriquecimento central de oportunidades (Backend 2+).

Combina deadline_normalizer + opportunity_classifier + ruído/validade/quality (Backend 9).

Feature flag (não ativar em produção sem dry-run aprovado):
  EDITALFINDER_ENABLE_BACKEND_ENRICHMENT=false|true
"""
from __future__ import annotations

import copy
import os
from typing import Any, Dict, List, Optional

from deadline_backfill import apply_deadline_backfill_in_memory
from deadline_normalizer import normalize_deadline
from noise_classifier import classify_noise
from opportunity_classifier import classify_record_full
from quality_score import compute_quality_score
from source_quality_profiles import classification_bucket
from validity_resolver import resolve_validity

ENRICHMENT_VERSION = "backend_10.1e"

# Campos novos expostos no dict enriquecido (não substituem prazo/fim_inscricao legados).
ENRICHMENT_TOP_LEVEL_KEYS = (
    "prazo_data",
    "prazo_raw",
    "prazo_status",
    "prazo_confidence",
    "prazo_source_field",
    "prazo_notes",
    "tipo_registro",
    "kind_confidence",
    "kind_reasons",
    "modalidade_normalizada",
    "modalidade_label",
    "modalidade_confidence",
    "modalidade_reasons",
    "escopo_geografico",
    "escopo_confidence",
    "escopo_reasons",
    "fonte_normalizada",
    "fonte_original",
    "fundo_origem",
    "programa_fundo",
    "source_notes",
    "pais_origem",
    "source_scope",
    "qualidade_flags",
    "area_tematica_normalizada",
    "area_tematica_label",
    "area_tematica_confidence",
    "area_tematica_reasons",
    "area_tematica_secondary",
    # Backend 9–10
    "actionability_type",
    "classification_bucket",
    "noise_score",
    "is_noise",
    "noise_type",
    "is_actionable_opportunity",
    "actionability_score",
    "validade_status",
    "validade_data",
    "validade_raw",
    "validade_confidence",
    "validade_source",
    "validade_reason",
    "sem_prazo_kind",
    "sem_prazo_reason",
    "deadline_backfill_status",
    "prazo_detectado",
    "prazo_fonte",
    "quality_score",
    "quality_level",
    "quality_flags",
    "review_reasons",
)


def backend_enrichment_enabled() -> bool:
    """
    Feature flag para integração gradual; não ativar em produção sem dry-run aprovado.
    """
    return os.getenv("EDITALFINDER_ENABLE_BACKEND_ENRICHMENT", "false").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


_NON_PROMOTABLE_ACTIONABILITY = frozenset(
    {
        "portal_util",
        "portal_generico",
        "resultado",
        "noticia",
        "evento",
        "retificacao",
        "documento_auxiliar",
        "sem_oportunidade",
        "pagina_institucional",
    }
)

_USEFUL_VALIDADE_STATUSES = frozenset(
    {"aberto", "encerrado", "vencendo_7", "vencendo_30", "prazo_invalido"}
)


def _reconcile_actionability_with_validity(
    noise: Dict[str, Any],
    validity: Dict[str, Any],
    deadline: Dict[str, Any],
) -> Dict[str, Any]:
    """Promove/demove actionability conforme prazo útil — sem alterar portal/resultado/notícia."""
    out = dict(noise)
    at = out.get("actionability_type") or "desconhecido"
    if at in _NON_PROMOTABLE_ACTIONABILITY:
        return out

    has_dl = bool(deadline.get("prazo_data")) and deadline.get("prazo_status") not in (
        "prazo_invalido",
        "sem_prazo",
    )
    vs = validity.get("validade_status")

    if at == "oportunidade_sem_prazo" and has_dl and vs in _USEFUL_VALIDADE_STATUSES - {"prazo_invalido"}:
        out["actionability_type"] = "oportunidade_principal"
        out["is_actionable_opportunity"] = True
        out["actionability_score"] = round(min(1.0, float(out.get("actionability_score") or 0.65) + 0.35), 3)
        flags = list(out.get("quality_flags") or [])
        if "oportunidade_sem_prazo" in flags:
            flags.remove("oportunidade_sem_prazo")
        out["quality_flags"] = flags
    # 10.1E: ausência de prazo não rebaixa oportunidade real — sem_prazo ≠ ruído.

    if out.get("actionability_type") != at:
        out["classification_bucket"] = classification_bucket(
            out.get("actionability_type") or at,
            bool(out.get("is_noise")),
        )

    return out


def _existing_structured_deadline(record: Dict[str, Any]) -> Optional[str]:
    for k in ("prazo_envio", "fim_inscricao", "prazo_data"):
        v = record.get(k)
        if v and str(v).strip():
            s = str(v).strip()[:10]
            if len(s) >= 8 and s[4:5] == "-":
                return s
    return None


def build_qualidade_flags(
    record: Dict[str, Any],
    *,
    deadline: Dict[str, Any],
    kind: Dict[str, Any],
    modality: Dict[str, Any],
    geo: Dict[str, Any],
    noise: Optional[Dict[str, Any]] = None,
    validity: Optional[Dict[str, Any]] = None,
    quality: Optional[Dict[str, Any]] = None,
) -> List[str]:
    flags: List[str] = []
    st = deadline.get("prazo_status")
    conf = deadline.get("prazo_confidence")

    if st == "sem_prazo":
        flags.append("sem_prazo")
    if st == "prazo_invalido":
        flags.append("prazo_invalido")
    if conf == "baixa":
        flags.append("prazo_baixa_confianca")
    if "extraido_de_texto" in (deadline.get("prazo_notes") or []):
        flags.append("prazo_texto_derivado")

    if kind.get("kind") == "desconhecido":
        flags.append("kind_desconhecido")
    if kind.get("confidence") == "baixa":
        flags.append("kind_baixa_confianca")
    if modality.get("modalidade_normalizada") == "sem_classificacao":
        flags.append("modalidade_sem_classificacao")
    if modality.get("confidence") == "baixa":
        flags.append("modalidade_baixa_confianca")
    if geo.get("scope") == "desconhecido":
        flags.append("escopo_desconhecido")

    titulo = (record.get("titulo") or "").lower()
    if kind.get("kind") == "edital" and modality.get("modalidade_normalizada") == "noticia_institucional":
        flags.append("possivel_noticia_em_edital")
    if kind.get("kind") == "edital" and any(x in titulo for x in ("notícia", "comunicado", "press release")):
        flags.append("titulo_parece_noticia")
    if kind.get("kind") == "noticia" and any(
        x in titulo for x in ("chamada pública", "chamada publica", "edital n", "call for proposals")
    ):
        flags.append("titulo_parece_edital")

    if noise:
        flags.extend(noise.get("quality_flags") or [])
        if noise.get("is_noise"):
            flags.append("backend9_ruido")
        if noise.get("is_actionable_opportunity"):
            flags.append("backend9_acionavel")

    if validity:
        vs = validity.get("validade_status")
        if vs == "nao_aplicavel":
            flags.append("validade_nao_aplicavel")
        elif vs == "sem_prazo":
            flags.append("validade_sem_prazo")

    if quality:
        flags.extend(quality.get("quality_flags") or [])

    if (
        "prazo_baixa_confianca" in flags
        or "kind_desconhecido" in flags
        or "possivel_noticia_em_edital" in flags
        or "titulo_parece_noticia" in flags
        or "titulo_parece_edital" in flags
        or "backend9_ruido" in flags
        or "provavel_ruido" in flags
    ):
        flags.append("revisao_humana")

    return sorted(set(flags))


def _pack_enrichment_fields(
    record: Dict[str, Any],
    full: Dict[str, Any],
    notes: List[str],
    *,
    backfill_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    dl = full["deadline"]
    kind = full["kind"]
    mod = full["modality"]
    geo = full["geo"]
    src = full["source"]
    thematic = full.get("thematic_area") or {}
    flags_deadline = full.get("flags") or {}

    noise = classify_noise(record)
    validity = resolve_validity(record, noise=noise, deadline=dl, backfill=backfill_result)
    noise = _reconcile_actionability_with_validity(noise, validity, dl)

    partial = {
        "prazo_data": dl.get("prazo_data"),
        "prazo_raw": dl.get("prazo_raw"),
        "prazo_status": dl.get("prazo_status"),
        "prazo_confidence": dl.get("prazo_confidence"),
        "tipo_registro": kind.get("kind"),
        "modalidade_normalizada": mod.get("modalidade_normalizada"),
        "fonte_normalizada": src.get("fonte_normalizada"),
        "actionability_type": noise.get("actionability_type"),
        "classification_bucket": noise.get("classification_bucket"),
        "noise_score": noise.get("noise_score"),
        "is_noise": noise.get("is_noise"),
        "noise_type": noise.get("noise_type"),
        "is_actionable_opportunity": noise.get("is_actionable_opportunity"),
        "actionability_score": noise.get("actionability_score"),
        "validade_status": validity.get("validade_status"),
        "validade_data": validity.get("validade_data"),
        "validade_confidence": validity.get("validade_confidence"),
        "validade_reason": validity.get("validade_reason"),
        "sem_prazo_kind": validity.get("sem_prazo_kind"),
        "sem_prazo_reason": validity.get("sem_prazo_reason"),
        "deadline_backfill_status": validity.get("deadline_backfill_status"),
        "prazo_detectado": dl.get("prazo_detectado"),
        "prazo_fonte": dl.get("prazo_fonte"),
        "review_reasons": list(noise.get("review_reasons") or []),
    }
    quality = compute_quality_score(record, partial)

    qualidade = build_qualidade_flags(
        record,
        deadline=dl,
        kind=kind,
        modality=mod,
        geo=geo,
        noise=noise,
        validity=validity,
        quality=quality,
    )

    review_reasons = sorted(
        set(list(noise.get("review_reasons") or []) + list(validity.get("validade_notes") or []))
    )

    return {
        "prazo_data": dl.get("prazo_data"),
        "prazo_raw": dl.get("prazo_raw"),
        "prazo_status": dl.get("prazo_status"),
        "prazo_confidence": dl.get("prazo_confidence"),
        "prazo_source_field": dl.get("prazo_source_field"),
        "prazo_notes": list(dl.get("prazo_notes") or []),
        "tipo_registro": kind.get("kind"),
        "kind_confidence": kind.get("confidence"),
        "kind_reasons": list(kind.get("reasons") or []),
        "modalidade_normalizada": mod.get("modalidade_normalizada"),
        "modalidade_label": mod.get("modalidade_label"),
        "modalidade_confidence": mod.get("confidence"),
        "modalidade_reasons": list(mod.get("reasons") or []),
        "escopo_geografico": geo.get("scope"),
        "escopo_confidence": geo.get("confidence"),
        "escopo_reasons": list(geo.get("reasons") or []),
        "fonte_normalizada": src.get("fonte_normalizada"),
        "fonte_original": src.get("fonte_original"),
        "fundo_origem": src.get("fundo_origem"),
        "programa_fundo": src.get("programa_fundo"),
        "source_notes": list(src.get("source_notes") or []),
        "pais_origem": src.get("pais_origem") or geo.get("pais_origem"),
        "source_scope": src.get("source_scope") or geo.get("scope"),
        "qualidade_flags": qualidade,
        "area_tematica_normalizada": thematic.get("area_tematica_normalizada"),
        "area_tematica_label": thematic.get("area_tematica_label"),
        "area_tematica_confidence": thematic.get("area_tematica_confidence"),
        "area_tematica_reasons": list(thematic.get("area_tematica_reasons") or []),
        "area_tematica_secondary": list(thematic.get("area_tematica_secondary") or []),
        "is_aberto": flags_deadline.get("is_aberto"),
        "is_vencendo_7": flags_deadline.get("is_vencendo_7"),
        "is_vencendo_30": flags_deadline.get("is_vencendo_30"),
        "actionability_type": noise.get("actionability_type"),
        "classification_bucket": noise.get("classification_bucket"),
        "noise_score": noise.get("noise_score"),
        "is_noise": noise.get("is_noise"),
        "noise_type": noise.get("noise_type"),
        "is_actionable_opportunity": noise.get("is_actionable_opportunity"),
        "actionability_score": noise.get("actionability_score"),
        "validade_status": validity.get("validade_status"),
        "validade_data": validity.get("validade_data"),
        "validade_raw": validity.get("validade_raw"),
        "validade_confidence": validity.get("validade_confidence"),
        "validade_source": validity.get("validade_source"),
        "validade_reason": validity.get("validade_reason"),
        "sem_prazo_kind": validity.get("sem_prazo_kind"),
        "sem_prazo_reason": validity.get("sem_prazo_reason"),
        "deadline_backfill_status": validity.get("deadline_backfill_status"),
        "prazo_detectado": dl.get("prazo_detectado"),
        "prazo_fonte": dl.get("prazo_fonte"),
        "quality_score": quality.get("quality_score"),
        "quality_level": quality.get("quality_level"),
        "quality_flags": quality.get("quality_flags"),
        "review_reasons": review_reasons,
        "_enrichment_notes": notes,
        "_enrichment_version": ENRICHMENT_VERSION,
    }


def enrichment_preview_dict(fields: Dict[str, Any]) -> Dict[str, Any]:
    """Subconjunto seguro para extras.backend_enrichment (sem chaves internas _)."""
    return {k: v for k, v in fields.items() if not k.startswith("_")}


def enrich_opportunity_record(
    record: Dict[str, Any],
    *,
    with_deadline_backfill: bool = False,
) -> Dict[str, Any]:
    """
    Retorna cópia enriquecida; não altera o dict original.

    Não sobrescreve prazo_envio, fim_inscricao, prazo nem extras existentes.
    Campos novos são adicionados no topo; snapshot completo também em extras.backend_enrichment.

    with_deadline_backfill: aplica deadline_backfill em memória antes do enricher (dry-run).
    """
    notes: List[str] = []
    work_record = record
    backfill_result: Optional[Dict[str, Any]] = None
    if with_deadline_backfill:
        work_record, backfill_result = apply_deadline_backfill_in_memory(record)
        if backfill_result.get("deadline_backfill_status") == "new_deadline_found":
            notes.append("deadline_backfill:new_deadline_found")
        elif backfill_result.get("sem_prazo_kind"):
            notes.append(f"sem_prazo_kind:{backfill_result.get('sem_prazo_kind')}")

    full = classify_record_full(work_record)
    packed = _pack_enrichment_fields(work_record, full, notes, backfill_result=backfill_result)

    out = copy.deepcopy(record)
    extras = out.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        out["extras"] = extras

    for key in ENRICHMENT_TOP_LEVEL_KEYS:
        if key not in packed:
            continue
        new_val = packed[key]
        if key in out and out[key] not in (None, "", [], {}):
            if out[key] != new_val:
                notes.append(f"preserved_existing_top:{key}")
                packed.setdefault("_enrichment_notes", []).append(f"preserved_existing_top:{key}")
            continue
        out[key] = new_val

    be = extras.get("backend_enrichment")
    if isinstance(be, dict) and be:
        notes.append("merged_into_extras.backend_enrichment")
    extras["backend_enrichment"] = enrichment_preview_dict(packed)
    extras["backend_enrichment"]["enrichment_version"] = ENRICHMENT_VERSION
    if notes:
        extras["backend_enrichment"]["merge_notes"] = notes

    return out


def apply_backend_enrichment_if_enabled(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Integração no pipeline: só anexa extras.backend_enrichment (in-place).
    Não envia colunas novas ao upsert — loader continua com schema legado.
    """
    if not backend_enrichment_enabled():
        return item
    enriched = enrich_opportunity_record(item)
    be = enriched.get("extras", {}).get("backend_enrichment")
    preview = dict(be) if isinstance(be, dict) else enrichment_preview_dict(
        {k: enriched.get(k) for k in ENRICHMENT_TOP_LEVEL_KEYS if k in enriched}
    )
    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        item["extras"] = extras
    extras["backend_enrichment"] = {
        **preview,
        "enrichment_version": ENRICHMENT_VERSION,
    }
    return item
