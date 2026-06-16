"""
Backfill de prazo por fonte (Backend 10.1E / 10.2A) — dry-run + loader wiring.

Não inventa prazo. `sem_prazo` ≠ ruído.
"""
from __future__ import annotations

import copy
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from date_parser import extract_deadline_from_text_enriched, normalize_date_str
from deadline_normalizer import infer_locale_from_source, parse_deadline_date

BACKFILL_SOURCE = "loader_backfill_10.1e"
LOADER_WIRING_VERSION = "loader_wiring_10.2a"

# Default seguro — ativar via EDITALFINDER_ENABLE_DEADLINE_BACKFILL=1
ENABLE_LOADER_DEADLINE_BACKFILL = False

PRIORITY_LOADER_SOURCES = frozenset(
    {"grants_gov", "bndes", "doe_arpae", "eureka", "erc", "amazul"}
)

GRANTS_CLOSE_KEYS = (
    "closeDate",
    "close_date",
    "opportunityCloseDate",
    "applicationDeadline",
    "application_due_date",
    "applicationDueDate",
    "grants_close_date",
    "closingDate",
    "closing_date",
)

GRANTS_META_KEYS = (
    "closeDateExplanation",
    "close_date_explanation",
    "postedDate",
    "posted_date",
    "archiveDate",
    "archive_date",
)

DOE_DEADLINE_KEYS = (
    "full_application_deadline",
    "application_deadline",
    "submission_deadline",
    "proposal_deadline",
    "response_deadline",
    "concept_paper_deadline",
    "deadline",
)

BNDES_DEADLINE_MARKERS = (
    r"inscri[cç][õo]es?\s+at[eé]",
    r"propostas?\s+at[eé]",
    r"prazo\s+final",
    r"data\s+limite",
    r"envio\s+de\s+propostas?\s+at[eé]",
    r"sele[cç][aã]o\s+de\s+fundos?\s+at[eé]",
    r"chamada\s+p[uú]blica\s+at[eé]",
    r"submiss[aã]o\s+at[eé]",
)

BNDES_PERMANENT_PATTERNS = (
    r"linha\s+permanente",
    r"linhas?\s+permanentes?",
    r"programa\s+cont[ií]nuo",
    r"financiamento\s+cont[ií]nuo",
    r"cr[eé]dito\s+dispon[ií]vel\s+de\s+forma\s+cont[ií]nua",
    r"fluxo\s+cont[ií]nuo",
)

SOURCE_ALIASES: Dict[str, Tuple[str, ...]] = {
    "grants_gov": ("grants.gov", "grants gov", "grants_gov"),
    "bndes": ("bndes",),
    "doe_arpae": ("doe_arpae", "arpa-e", "arpa e", "doe arpa"),
    "eureka": ("eureka network", "eureka"),
    "erc": ("erc", "european research council"),
    "amazul": ("amazul", "amazônia azul", "amazonia azul"),
}


def _norm_source(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def normalize_backfill_source(record: Dict[str, Any], source: Optional[str] = None) -> str:
    raw = source or str(
        record.get("fonte_recurso") or record.get("fonte") or record.get("fonte_normalizada") or ""
    )
    low = _norm_source(raw)
    for key, aliases in SOURCE_ALIASES.items():
        if any(a in low for a in aliases):
            return key
    return "unknown"


def _get_nested(record: Dict[str, Any], key: str) -> Any:
    if record.get(key) not in (None, ""):
        return record.get(key)
    extras = record.get("extras")
    if isinstance(extras, dict) and extras.get(key) not in (None, ""):
        return extras.get(key)
    return None


def deadline_backfill_enabled() -> bool:
    """Feature flag: backfill de prazo no loader (10.2A)."""
    return os.getenv("EDITALFINDER_ENABLE_DEADLINE_BACKFILL", "false").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def controlled_apply_enabled() -> bool:
    """Feature flag: escrita controlada no banco (Backend 10.2B)."""
    return os.getenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "false").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _existing_prazo_envio(record: Dict[str, Any]) -> Tuple[Optional[str], bool]:
    """Retorna (iso_ou_raw, é_válido)."""
    for key in ("prazo_envio", "fim_inscricao"):
        val = record.get(key)
        if not val:
            continue
        locale = infer_locale_from_source(
            str(record.get("fonte_recurso") or record.get("fonte") or "")
        )
        parsed = parse_deadline_date(val, locale_hint=locale, source_field=key)
        if parsed:
            return parsed["date"], True
        return str(val).strip()[:40], False
    return None, False


def _base_result() -> Dict[str, Any]:
    return {
        "extras_patch": {"deadline_source": BACKFILL_SOURCE},
    }


def _reject_reason(raw: str, field: str) -> Dict[str, Any]:
    return {
        "deadline_backfill_status": "rejected_deadline",
        "rejection_reason": f"{field}:{raw[:80]}",
        "extras_patch": {"deadline_source": BACKFILL_SOURCE, "rejected_field": field},
    }


def _extract_doe_nofo_from_text(text: str) -> Optional[Dict[str, Any]]:
    m = re.search(r"Notice Of Funding Opportunity \(NOFO\)\s+(.+?)(?:\n|$)", text, re.I)
    if not m:
        return None
    line = m.group(1)
    has_tbd = bool(re.search(r"\bTBD\b", line, re.I))
    dates: List[str] = []
    for dm in re.finditer(r"(\d{1,2}/\d{1,2}/\d{4})", line):
        iso = normalize_date_str(dm.group(1), locale="en_US")
        if iso:
            dates.append(iso)
    if len(dates) >= 2:
        return {
            "iso": dates[-1],
            "field": "nofo_full_application",
            "raw": line[:120],
            "reason": "DOE NOFO segunda data (full application)",
        }
    if len(dates) == 1 and not has_tbd:
        return {
            "iso": dates[0],
            "field": "nofo_single_date",
            "raw": line[:120],
            "reason": "DOE NOFO data única",
        }
    if has_tbd:
        return {"tbd": True}
    return None


def _backfill_grants_gov(record: Dict[str, Any]) -> Dict[str, Any]:
    out = _base_result()
    extras = record.get("extras") if isinstance(record.get("extras"), dict) else {}
    locale = "en_US"

    posted = None
    archive = None
    explanation = ""
    for k in GRANTS_META_KEYS:
        v = _get_nested(record, k)
        if not v:
            continue
        if "explanation" in k.lower():
            explanation = str(v)
        elif "posted" in k.lower():
            posted = str(v)[:40]
        elif "archive" in k.lower():
            archive = str(v)[:40]

    if re.search(r"no\s+closing\s+date|forecasted", explanation, re.I):
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "deadline_explicitly_absent",
                "sem_prazo_reason": "Grants.gov closeDateExplanation indica ausência de prazo",
            }
        )
        out["extras_patch"].update(
            {
                "grants_close_date_explanation": explanation[:500],
                "grants_posted_date": posted,
                "grants_archive_date": archive,
            }
        )
        return out

    for key in GRANTS_CLOSE_KEYS:
        val = _get_nested(record, key)
        if not val:
            continue
        parsed = parse_deadline_date(val, locale_hint=locale, source_field=key)
        if not parsed:
            continue
        out.update(
            {
                "prazo_envio": parsed["date"],
                "prazo_fonte": key,
                "prazo_confidence": 0.95,
                "deadline_raw": str(val)[:120],
                "deadline_reason": f"Grants.gov {key}",
                "deadline_backfill_status": "new_deadline_found",
                "sem_prazo_kind": None,
                "sem_prazo_reason": None,
            }
        )
        out["extras_patch"].update(
            {
                "grants_close_date": parsed["date"],
                "grants_close_date_explanation": explanation[:500] or None,
                "grants_posted_date": posted,
                "grants_archive_date": archive,
                "deadline_source_field": key,
            }
        )
        return out

    if posted and not archive:
        out["extras_patch"]["grants_posted_date"] = posted
    if archive:
        out["extras_patch"]["grants_archive_date"] = archive
        out["rejected_fields"] = ["archiveDate_sem_closeDate"]

    titulo = str(record.get("titulo") or "").lower()
    desc = str(record.get("descricao") or "").lower()
    is_funding = any(
        x in f"{titulo} {desc}"
        for x in ("grant", "funding opportunity", "funding program", "nofo", "solicitation")
    )
    status = str(_get_nested(record, "opportunity_status") or extras.get("opportunity_status") or "").lower()
    if status == "forecasted" or "forecast" in desc:
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "deadline_tbd",
                "sem_prazo_reason": "Grants.gov forecast/TBD sem closeDate",
            }
        )
        return out

    if is_funding or "grants" in _norm_source(str(record.get("fonte_recurso") or "")):
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "missing_from_loader",
                "sem_prazo_reason": "Grants.gov sem closeDate persistido — candidato a backfill no loader",
            }
        )
        return out

    out.update(
        {
            "deadline_backfill_status": "no_candidate",
            "sem_prazo_kind": "unknown",
            "sem_prazo_reason": "Grants.gov sem campo de prazo identificável",
        }
    )
    return out


def _backfill_doe_arpae(record: Dict[str, Any]) -> Dict[str, Any]:
    out = _base_result()
    locale = "en_US"
    candidates: List[Tuple[int, str, str, str, str]] = []

    priority_map = {
        "full_application_deadline": 1,
        "application_deadline": 2,
        "submission_deadline": 3,
        "proposal_deadline": 4,
        "response_deadline": 5,
        "deadline": 6,
        "concept_paper_deadline": 7,
    }
    for key in DOE_DEADLINE_KEYS:
        val = _get_nested(record, key)
        if not val:
            continue
        parsed = parse_deadline_date(val, locale_hint=locale, source_field=key)
        if parsed:
            prio = priority_map.get(key, 10)
            candidates.append((prio, parsed["date"], key, str(val)[:120], f"DOE_ARPAE {key}"))

    blob = "\n".join(
        str(record.get(k) or "")
        for k in ("titulo", "descricao", "objetivo")
    )
    nofo = _extract_doe_nofo_from_text(blob)
    if nofo and nofo.get("tbd"):
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "deadline_tbd",
                "sem_prazo_reason": "DOE_ARPAE NOFO com TBD sem segunda data",
            }
        )
        return out
    if nofo and nofo.get("iso"):
        candidates.append(
            (3, nofo["iso"], nofo["field"], nofo["raw"], nofo["reason"]),
        )

    if not candidates:
        link = str(record.get("link") or "")
        has_pdf_hint = bool(re.search(r"\.pdf|edital|nofo", blob + link, re.I))
        if has_pdf_hint or "exchange" in link.lower():
            out.update(
                {
                    "deadline_backfill_status": "no_deadline_explained",
                    "sem_prazo_kind": "deadline_in_pdf_or_detail",
                    "sem_prazo_reason": "DOE_ARPAE: prazo provável no detalhe/PDF do portal eXCHANGE",
                    "recrawl_candidate": True,
                }
            )
            return out
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "missing_from_loader",
                "sem_prazo_reason": "DOE_ARPAE sem deadline estruturado no registro",
            }
        )
        return out

    candidates.sort(key=lambda x: x[0])
    _, iso, field, raw, reason = candidates[0]
    out.update(
        {
            "prazo_envio": iso,
            "prazo_fonte": field,
            "prazo_confidence": 0.9 if "concept" not in field else 0.75,
            "deadline_raw": raw,
            "deadline_reason": reason,
            "deadline_backfill_status": "new_deadline_found",
        }
    )
    out["extras_patch"]["deadline_source_field"] = field
    if "concept" in field and len(candidates) == 1:
        out["deadline_reason"] = "DOE_ARPAE concept_paper_deadline (único disponível)"
    return out


def _bndes_document_extras(record: Dict[str, Any], blob: str) -> Dict[str, Any]:
    """Preserva URLs de PDF/edital para recrawl futuro — sem OCR."""
    patch: Dict[str, Any] = {}
    link = str(record.get("link") or "")
    extras = record.get("extras") if isinstance(record.get("extras"), dict) else {}
    for key in ("pdf_url", "url_detalhe", "deadline_detail_url"):
        u = extras.get(key) or record.get(key)
        if u and str(u).strip():
            patch.setdefault("deadline_detail_url", str(u).strip())
            break
    pdf_urls = re.findall(r"https?://[^\s\"']+\.pdf", blob, re.I)
    if pdf_urls:
        patch["possible_deadline_document_url"] = pdf_urls[0]
        patch.setdefault("deadline_detail_url", pdf_urls[0])
    elif link and ".pdf" in link.lower():
        patch["possible_deadline_document_url"] = link
    elif re.search(r"edital|chamada\s+p[uú]blica", blob, re.I) and link:
        patch.setdefault("deadline_detail_url", link)
    return patch


def _backfill_bndes(record: Dict[str, Any], *, existing_iso: Optional[str] = None) -> Dict[str, Any]:
    out = _base_result()
    from bndes_submission_deadline import (
        SUBMISSION_DEADLINE_KIND,
        extract_bndes_submission_deadline,
        merge_bndes_text_blob,
    )

    blob = merge_bndes_text_blob(record)
    low = blob.lower()
    doc_patch = _bndes_document_extras(record, blob)
    if doc_patch:
        out["extras_patch"].update(doc_patch)

    ex = record.get("extras") if isinstance(record.get("extras"), dict) else {}
    existing_kind = ex.get("deadline_kind")
    if existing_iso is None:
        existing_iso, existing_valid = _existing_prazo_envio(record)
        if not existing_valid:
            existing_iso = None

    if any(re.search(p, low, re.I) for p in BNDES_PERMANENT_PATTERNS):
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "permanent_funding_line",
                "sem_prazo_reason": "Linha/programa permanente BNDES sem deadline explícito",
            }
        )
        return out

    submission = extract_bndes_submission_deadline(blob)
    ignored: List[Dict[str, Any]] = list(submission.get("ignored_dates") or [])

    def _append_ignored(iso: str, reason: str, context: str) -> None:
        if not iso:
            return
        if any(d.get("iso") == iso and d.get("reason") == reason for d in ignored):
            return
        ignored.append({"iso": iso, "raw": iso, "reason": reason, "context": context[:160]})

    if (
        submission.get("deadline_kind") == SUBMISSION_DEADLINE_KIND
        and submission.get("iso")
    ):
        sub_iso = submission["iso"]
        if existing_iso and existing_iso != sub_iso:
            _append_ignored(
                existing_iso,
                "replaced_non_submission_prazo",
                "prazo_envio existente substituído por submissão (Como participar)",
            )
        if ignored:
            out["extras_patch"]["bndes_ignored_dates"] = ignored

        if existing_iso == sub_iso and existing_kind == SUBMISSION_DEADLINE_KIND:
            status = "preserved_existing"
            reason = "BNDES prazo de submissão existente preservado"
        elif existing_iso and existing_iso != sub_iso:
            status = "corrected_deadline_found"
            reason = "corrected_bndes_submission_deadline"
            out["extras_patch"]["replaced_prazo_envio"] = existing_iso
        elif existing_iso and existing_kind != SUBMISSION_DEADLINE_KIND:
            status = "corrected_deadline_found"
            reason = "corrected_bndes_submission_deadline"
            out["extras_patch"]["replaced_prazo_envio"] = existing_iso
        else:
            status = "new_deadline_found"
            reason = f"BNDES submissão: {submission.get('field') or 'submission_deadline'}"

        out.update(
            {
                "prazo_envio": sub_iso,
                "prazo_fonte": submission.get("field") or "bndes_submission",
                "prazo_confidence": submission.get("confidence", 0.9),
                "deadline_raw": submission.get("raw") or blob[:120],
                "deadline_reason": reason,
                "deadline_backfill_status": status,
            }
        )
        out["extras_patch"]["deadline_kind"] = SUBMISSION_DEADLINE_KIND
        out["extras_patch"]["deadline_source_field"] = submission.get("field")
        out["extras_patch"]["bndes_submission_confidence"] = submission.get("confidence")
        if submission.get("source_block"):
            out["extras_patch"]["bndes_submission_source_block"] = submission["source_block"]
        return out

    if existing_iso:
        _append_ignored(
            existing_iso,
            "preserved_non_submission_prazo",
            "prazo_envio existente sem deadline_kind=submission_deadline",
        )
        if ignored:
            out["extras_patch"]["bndes_ignored_dates"] = ignored
        out.update(
            {
                "deadline_backfill_status": "rejected_deadline",
                "rejection_reason": "prazo_nao_e_submissao",
                "prazo_envio_invalid_existing": existing_iso,
            }
        )
        return out

    if submission.get("ignored_dates"):
        out["extras_patch"]["bndes_ignored_dates"] = submission["ignored_dates"]

    if re.search(r"lan[cç]ou,?\s+em|publicado\s+em|^em\s+\d", low, re.I):
        if re.search(r"\.pdf|edital\s+de\s+chamada|chamada\s+p[uú]blica", low, re.I) or doc_patch:
            out.update(
                {
                    "deadline_backfill_status": "no_deadline_explained",
                    "sem_prazo_kind": "deadline_in_pdf_or_detail",
                    "sem_prazo_reason": "BNDES: notícia de lançamento — prazo provável no PDF/edital",
                    "recrawl_candidate": True,
                }
            )
            out["extras_patch"].setdefault("sem_prazo_kind", "deadline_in_pdf_or_detail")
            return out

    has_marker = any(re.search(p, blob, re.I) for p in BNDES_DEADLINE_MARKERS)
    if not has_marker:
        if "chamada pública" in low or "chamada publica" in low or "seleção de fundos" in low:
            out.update(
                {
                    "deadline_backfill_status": "no_deadline_explained",
                    "sem_prazo_kind": "missing_from_loader",
                    "sem_prazo_reason": "BNDES chamada sem prazo no texto persistido",
                    "recrawl_candidate": True,
                }
            )
            return out
        out.update(
            {
                "deadline_backfill_status": "no_candidate",
                "sem_prazo_kind": "unknown",
                "sem_prazo_reason": "BNDES sem marcador confiável de prazo",
            }
        )
        return out

    out.update(
        {
            "deadline_backfill_status": "no_deadline_explained",
            "sem_prazo_kind": "missing_from_loader",
            "sem_prazo_reason": "BNDES com marcador mas sem prazo de submissão identificado",
            "recrawl_candidate": True,
        }
    )
    return out


def _backfill_eureka(record: Dict[str, Any]) -> Dict[str, Any]:
    out = _base_result()
    titulo = str(record.get("titulo") or "").lower()
    desc = str(record.get("descricao") or "").lower()
    blob = f"{titulo} {desc}"

    hub_markers = (
        "open funding opportunities",
        "funding opportunities",
        "innovation programmes",
        "programmes",
    )
    if any(m in titulo or m in desc for m in hub_markers) and "deadline" not in blob:
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "portal_or_hub",
                "sem_prazo_reason": "Eureka hub/programa sem deadline de call",
            }
        )
        return out

    iso, field, raw = extract_deadline_from_text_enriched(blob, locale="en_US")
    if iso:
        out.update(
            {
                "prazo_envio": iso,
                "prazo_fonte": field or "texto_eureka",
                "prazo_confidence": 0.8,
                "deadline_raw": raw,
                "deadline_reason": f"Eureka {field or 'call deadline'}",
                "deadline_backfill_status": "new_deadline_found",
            }
        )
        out["extras_patch"]["deadline_source_field"] = field
        return out

    if any(x in blob for x in ("call for", "open call", "submission")):
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "source_has_no_deadline",
                "sem_prazo_reason": "Eureka call sem data no registro",
            }
        )
        return out

    out.update(
        {
            "deadline_backfill_status": "no_candidate",
            "sem_prazo_kind": "unknown",
            "sem_prazo_reason": "Eureka sem prazo identificável",
        }
    )
    return out


def _backfill_erc(record: Dict[str, Any]) -> Dict[str, Any]:
    out = _base_result()
    blob = f"{record.get('titulo') or ''} {record.get('descricao') or ''}"
    iso, field, raw = extract_deadline_from_text_enriched(blob, locale="en_US")
    if iso:
        out.update(
            {
                "prazo_envio": iso,
                "prazo_fonte": field or "texto_erc",
                "prazo_confidence": 0.8,
                "deadline_raw": raw,
                "deadline_reason": f"ERC {field or 'deadline'}",
                "deadline_backfill_status": "new_deadline_found",
            }
        )
        out["extras_patch"]["deadline_source_field"] = field
        return out

    if re.search(r"\b(starting grant|advanced grant|synergy grant|call)\b", blob, re.I):
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "continuous_program",
                "sem_prazo_reason": "ERC programa/call sem deadline no texto persistido",
            }
        )
        return out

    out.update(
        {
            "deadline_backfill_status": "no_candidate",
            "sem_prazo_kind": "unknown",
            "sem_prazo_reason": "ERC sem prazo identificável",
        }
    )
    return out


def _backfill_amazul(record: Dict[str, Any]) -> Dict[str, Any]:
    out = _base_result()
    existing, valid = _existing_prazo_envio(record)
    if valid and existing:
        out.update(
            {
                "deadline_backfill_status": "preserved_existing",
                "prazo_envio": existing,
                "deadline_reason": "AMAZUL prazo_envio existente preservado",
            }
        )
        return out

    blob = f"{record.get('titulo') or ''} {record.get('descricao') or ''}"
    iso, field, raw = extract_deadline_from_text_enriched(blob, locale="pt_BR")
    if iso and re.search(r"prazo|inscri|encerramento|at[eé]|deadline", blob, re.I):
        out.update(
            {
                "prazo_envio": iso,
                "prazo_fonte": field,
                "prazo_confidence": 0.75,
                "deadline_raw": raw,
                "deadline_reason": "AMAZUL prazo explícito no texto",
                "deadline_backfill_status": "new_deadline_found",
            }
        )
        return out

    if re.search(r"licita[cç][aã]o|dispensa", blob, re.I):
        out.update(
            {
                "deadline_backfill_status": "no_deadline_explained",
                "sem_prazo_kind": "missing_from_loader",
                "sem_prazo_reason": "AMAZUL licitação sem deadline explícito no registro",
            }
        )
        return out

    out.update(
        {
            "deadline_backfill_status": "no_candidate",
            "sem_prazo_kind": "unknown",
            "sem_prazo_reason": "AMAZUL sem prazo identificável",
        }
    )
    return out


_BACKFILL_HANDLERS = {
    "grants_gov": _backfill_grants_gov,
    "bndes": _backfill_bndes,
    "doe_arpae": _backfill_doe_arpae,
    "eureka": _backfill_eureka,
    "erc": _backfill_erc,
    "amazul": _backfill_amazul,
}


def extract_source_deadline_fields(
    record: Dict[str, Any],
    source: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extrai candidato a prazo_envio ou explica ausência de prazo por fonte.
    Não altera o registro original.
    """
    src = normalize_backfill_source(record, source)
    existing, valid = _existing_prazo_envio(record)

    if src == "bndes":
        result = _backfill_bndes(record, existing_iso=existing if valid else None)
        result["backfill_source_key"] = src
        if result.get("deadline_backfill_status") in ("new_deadline_found", "corrected_deadline_found"):
            result.setdefault("prazo_confidence", result.get("prazo_confidence", 0.9))
        return result

    if valid and existing:
        result = _base_result()
        result.update(
            {
                "deadline_backfill_status": "preserved_existing",
                "prazo_envio": existing,
                "prazo_fonte": "prazo_envio",
                "prazo_confidence": 1.0,
                "deadline_reason": "prazo_envio/fim_inscricao existente válido",
                "sem_prazo_kind": None,
                "sem_prazo_reason": None,
            }
        )
        result["extras_patch"]["deadline_source_field"] = "prazo_envio"
        return result

    handler = _BACKFILL_HANDLERS.get(src)
    if handler:
        result = handler(record)
    else:
        result = _base_result()
        result.update(
            {
                "deadline_backfill_status": "no_candidate",
                "sem_prazo_kind": "unknown",
                "sem_prazo_reason": f"Fonte {src} sem handler de backfill",
            }
        )

    if existing and not valid and result.get("prazo_envio"):
        result["deadline_backfill_status"] = "replacement_candidate"
        result["prazo_envio_invalid_existing"] = existing
        result["deadline_reason"] = (
            f"Substituição candidata: prazo inválido '{existing}' → {result['prazo_envio']}"
        )

    if result.get("deadline_backfill_status") == "new_deadline_found":
        result.setdefault("prazo_confidence", 0.9)

    result["backfill_source_key"] = src
    return result


def _normalize_payload_deadline_shape(payload: Dict[str, Any]) -> None:
    """Promove campos API conhecidos para forma legível pelo backfill/loader."""
    extras = payload.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        payload["extras"] = extras

    if payload.get("prazo_envio") and not payload.get("fim_inscricao"):
        payload["fim_inscricao"] = payload["prazo_envio"]
    if payload.get("fim_inscricao") and not payload.get("prazo_envio"):
        payload["prazo_envio"] = payload["fim_inscricao"]

    for key in GRANTS_CLOSE_KEYS:
        val = extras.get(key) or payload.get(key)
        if not val:
            continue
        if not extras.get("closeDate"):
            extras["closeDate"] = val
        if not extras.get("close_date"):
            extras["close_date"] = val
        break

    for meta_key in GRANTS_META_KEYS:
        val = extras.get(meta_key) or payload.get(meta_key)
        if val is not None and meta_key not in extras:
            extras[meta_key] = val

    for key in DOE_DEADLINE_KEYS:
        val = extras.get(key) or payload.get(key)
        if val and not payload.get(key):
            payload[key] = val


def apply_deadline_backfill_to_payload(
    payload: Dict[str, Any],
    source: Optional[str] = None,
    enabled: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Integração loader (10.2A): aplica backfill ao payload pré-upsert.

    enabled=False → payload inalterado.
    enabled=True → mescla prazo_envio/fim_inscricao e extras_patch quando confiável.
    """
    if enabled is None:
        enabled = deadline_backfill_enabled()
    if not enabled:
        return payload

    rec, result = apply_deadline_backfill_in_memory(payload)
    extras = rec.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        rec["extras"] = extras

    extras["loader_deadline_backfill"] = {
        "version": LOADER_WIRING_VERSION,
        "status": result.get("deadline_backfill_status"),
        "prazo_fonte": result.get("prazo_fonte"),
        "deadline_reason": result.get("deadline_reason"),
        "sem_prazo_kind": result.get("sem_prazo_kind"),
        "sem_prazo_reason": result.get("sem_prazo_reason"),
        "backfill_source_key": result.get("backfill_source_key"),
    }
    if result.get("sem_prazo_kind") and not result.get("prazo_envio"):
        extras.setdefault("sem_prazo_kind", result.get("sem_prazo_kind"))
        if result.get("sem_prazo_reason"):
            extras.setdefault("sem_prazo_reason", result.get("sem_prazo_reason"))

    return rec


def apply_deadline_backfill_in_memory(record: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Aplica backfill em cópia do registro (dry-run).
    Só grava prazo_envio quando status é new_deadline_found.
    """
    rec = copy.deepcopy(record)
    _normalize_payload_deadline_shape(rec)
    result = extract_source_deadline_fields(rec, source=normalize_backfill_source(rec))

    extras = rec.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        rec["extras"] = extras

    patch = result.get("extras_patch") or {}
    for k, v in patch.items():
        if v is not None:
            extras[k] = v

    status = result.get("deadline_backfill_status")
    if status in ("new_deadline_found", "corrected_deadline_found") and result.get("prazo_envio"):
        rec["prazo_envio"] = result["prazo_envio"]
        rec["fim_inscricao"] = result["prazo_envio"]

    extras["_deadline_backfill_preview"] = {
        k: v
        for k, v in result.items()
        if k != "extras_patch"
    }
    return rec, result


def resolve_sem_prazo_context(
    record: Dict[str, Any],
    *,
    actionability_type: str,
    validade_status: str,
    backfill: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Semântica explicativa — sem_prazo não é ruído."""
    if validade_status == "nao_aplicavel":
        return {
            "sem_prazo_kind": "not_applicable",
            "sem_prazo_reason": f"Prazo não aplicável para {actionability_type}",
        }
    if validade_status not in ("sem_prazo", "desconhecido"):
        return {"sem_prazo_kind": None, "sem_prazo_reason": None}

    if backfill and backfill.get("sem_prazo_kind"):
        return {
            "sem_prazo_kind": backfill.get("sem_prazo_kind"),
            "sem_prazo_reason": backfill.get("sem_prazo_reason"),
            "deadline_backfill_status": backfill.get("deadline_backfill_status"),
        }

    if actionability_type == "portal_util":
        return {
            "sem_prazo_kind": "portal_or_hub",
            "sem_prazo_reason": "Portal/hub útil — deadline não exigido",
        }

    titulo = str(record.get("titulo") or "").lower()
    if any(x in titulo for x in ("linha permanente", "linhas permanentes", "permanent")):
        return {
            "sem_prazo_kind": "permanent_funding_line",
            "sem_prazo_reason": "Linha/programa permanente sem deadline explícito",
        }

    if actionability_type == "oportunidade_sem_prazo":
        return {
            "sem_prazo_kind": "missing_from_loader",
            "sem_prazo_reason": "Oportunidade real sem deadline estruturado no registro",
        }

    return {
        "sem_prazo_kind": "unknown",
        "sem_prazo_reason": "Nenhum campo ou marcador confiável de prazo encontrado",
    }
