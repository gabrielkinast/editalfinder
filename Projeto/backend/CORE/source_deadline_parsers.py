"""
Parsers de prazo por fonte (Backend 3) — extração na origem antes do loader.

Usa deadline_normalizer.normalize_deadline no fechamento; não inventa prazo sem evidência.
"""
from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from date_parser import normalize_date_str
from deadline_normalizer import normalize_deadline

# --- China / MOFCOM / tendering (EN + ZH labels) ---
CHINA_DEADLINE_PATTERNS: List[Tuple[str, str]] = [
    (r"(?:bid\s+)?closing\s+date\s*[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})", "bid_closing_date"),
    (r"(?:tender\s+)?closing\s+date\s*[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})", "tender_closing_date"),
    (r"submission\s+deadline\s*[:\s]+([^\n<]{6,40})", "submission_deadline"),
    (r"(?:deadline|due\s+date)\s*[:\s]+([^\n<]{6,40})", "deadline"),
    (r"closes?\s+on\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})", "closes_on"),
    (r"expiry\s+date\s*[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})", "expiry_date"),
    (r"end\s+date\s*[:\s]+(\d{4}[-/]\d{1,2}[-/]\d{1,2})", "end_date"),
    (r"截止\s*(?:时间|日期)?\s*[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)", "zh_deadline"),
    (r"投标截止\s*[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)", "zh_bid_close"),
    (r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s*(?:截止|结束)", "zh_date_before_marker"),
]

# Publication-like labels — never use as submission deadline
CHINA_PUBLICATION_MARKERS = (
    "publish",
    "posted",
    "release date",
    "opening date",
    "公告日期",
    "发布时间",
    "开标时间",
)

# --- Fundação Araucária / FAPPR (PT) ---
ARAUCARIA_DEADLINE_PATTERNS: List[Tuple[str, str]] = [
    (r"inscri[cç][õo]es?\s+at[eé]\s+(\d{1,2}/\d{1,2}/\d{4})", "inscricoes_ate"),
    (r"submiss[aã]o\s+at[eé]\s+(\d{1,2}/\d{1,2}/\d{4})", "submissao_ate"),
    (r"prazo\s+de\s+submiss[aã]o\s*[:\s]+(\d{1,2}/\d{1,2}/\d{4})", "prazo_submissao"),
    (r"prazo\s+para\s+(?:envio|inscri[cç][aã]o)\s*[:\s]+(\d{1,2}/\d{1,2}/\d{4})", "prazo_envio"),
    (r"per[ií]odo\s+de\s+inscri[cç][õo]es?\s*[:\s]*\d{1,2}/\d{1,2}/\d{4}\s*a\s*(\d{1,2}/\d{1,2}/\d{4})", "periodo_inscricoes_fim"),
    (r"data\s+limite\s*[:\s]+(\d{1,2}/\d{1,2}/\d{4})", "data_limite"),
    (r"encerramento\s*(?:das?\s+inscri[cç][õo]es?)?\s*[:\s]+(\d{1,2}/\d{1,2}/\d{4})", "encerramento"),
    (r"at[eé]\s+(\d{1,2}\s+de\s+[a-zçãõéêôíóú]+\s+de\s+\d{4})", "ate_extenso"),
    (r"at[eé]\s+(\d{1,2}/\d{1,2}/\d{4})", "ate"),
]

GRANTS_CLOSE_KEYS = (
    "close_date",
    "closeDate",
    "closeDateFormatted",
    "closingDate",
    "closing_date",
    "applicationDueDate",
    "application_due_date",
    "responseDate",
)
GRANTS_NON_DEADLINE_KEYS = (
    "posted_date",
    "postedDate",
    "post_date",
    "openDate",
    "archiveDate",
    "archive_date",
)


def _zh_date_to_iso(m: re.Match) -> Optional[str]:
    g = m.group(1)
    zm = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", g)
    if zm:
        y, mo, d = (int(x) for x in zm.groups())
        return f"{y:04d}-{mo:02d}-{d:02d}"
    return normalize_date_str(g)


def _first_iso_from_patterns(
    text: str,
    patterns: List[Tuple[str, str]],
    *,
    skip_publication_context: bool = False,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Returns (iso_date, raw_fragment, source_field)."""
    if not text or not str(text).strip():
        return None, None, None
    blob = str(text)
    low = blob.lower()
    for pattern, field in patterns:
        for m in re.finditer(pattern, blob, re.IGNORECASE):
            ctx_start = max(0, m.start() - 40)
            ctx = low[ctx_start : m.start() + 20]
            if skip_publication_context and any(p in ctx for p in CHINA_PUBLICATION_MARKERS):
                continue
            raw = m.group(1).strip()
            iso = _zh_date_to_iso(m) if "年" in raw else normalize_date_str(raw)
            if not iso:
                iso = normalize_date_str(m.group(0))
            if iso:
                return iso, raw[:120], field
    return None, None, None


def parse_china_tender_deadlines(
    text: str,
    *,
    html: Optional[str] = None,
) -> Dict[str, Any]:
    """Extrai prazo de licitação China/MOFCOM; não usa data de publicação."""
    combined = "\n".join(p for p in (text, html or "") if p)
    iso, raw, field = _first_iso_from_patterns(
        combined,
        CHINA_DEADLINE_PATTERNS,
        skip_publication_context=True,
    )
    out: Dict[str, Any] = {
        "deadline_source_field": field,
        "deadline_confidence": None,
        "deadline_missing_in_source": not bool(iso),
    }
    if iso:
        out["prazo_data"] = iso
        out["fim_inscricao"] = iso
        out["prazo_envio_raw"] = raw
        out["deadline_confidence"] = "alta" if field and "zh_" not in field else "media"
        out["deadline"] = iso
        out["deadline_source"] = field
    else:
        pub_only = bool(
            re.search(
                r"(?:publish|posted|release|opening|公告|发布|开标)",
                combined,
                re.I,
            )
        )
        if pub_only and not re.search(r"clos|deadline|截止|投标", combined, re.I):
            out["deadline_missing_in_source"] = True
    return out


def parse_araucaria_deadlines(
    text: str,
    *,
    has_pdf: bool = False,
    pdf_text: Optional[str] = None,
) -> Dict[str, Any]:
    """Fundação Araucária / FAPPR — HTML e texto de PDF já disponível."""
    parts = [text or ""]
    if pdf_text:
        parts.append(pdf_text)
    combined = "\n".join(parts)
    iso, raw, field = _first_iso_from_patterns(combined, ARAUCARIA_DEADLINE_PATTERNS)
    out: Dict[str, Any] = {
        "deadline_source_field": field,
        "deadline_requires_pdf": bool(has_pdf and not iso and not pdf_text),
    }
    if iso:
        out["prazo_data"] = iso
        out["fim_inscricao"] = iso
        out["fim_inscricao_raw"] = raw
        out["prazo_envio_raw"] = raw
        out["deadline"] = iso
        out["deadline_source"] = field
        out["deadline_confidence"] = "alta" if field in ("inscricoes_ate", "prazo_submissao", "data_limite") else "media"
    elif has_pdf and not pdf_text:
        out["deadline_requires_pdf"] = True
    return out


def parse_grants_api_deadlines(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Escolhe close/due da API Grants/Simpler; ignora posted/archive como prazo de inscrição.
    """
    raw_close: Optional[str] = None
    source_field: Optional[str] = None
    for k in GRANTS_CLOSE_KEYS:
        v = row.get(k)
        if v is not None and str(v).strip():
            raw_close = str(v).strip()
            source_field = k
            break
    iso = None
    if raw_close:
        if re.match(r"^\d{4}-\d{2}-\d{2}", raw_close):
            iso = raw_close[:10]
        else:
            for fmt in ("%m/%d/%Y", "%m/%d/%y"):
                try:
                    from datetime import datetime

                    iso = datetime.strptime(raw_close[:10], fmt).date().isoformat()
                    break
                except ValueError:
                    continue
            if not iso:
                iso = normalize_date_str(raw_close)
    posted = None
    for k in GRANTS_NON_DEADLINE_KEYS:
        v = row.get(k)
        if v:
            posted = str(v)[:10]
            break
    out: Dict[str, Any] = {
        "grants_close_date": iso,
        "deadline_source_field": source_field,
        "posted_date_reference": posted,
    }
    if iso:
        out["fim_inscricao"] = iso
        out["prazo_envio_raw"] = raw_close
        out["deadline"] = iso
        out["deadline_source"] = source_field or "close_date"
        out["deadline_confidence"] = "alta"
        out["grants_close_date"] = iso
    elif posted and not raw_close:
        out["deadline_missing_in_source"] = True
        out["deadline_confidence"] = "nenhuma"
    return out


def merge_deadline_into_item(
    item: Dict[str, Any],
    parsed: Dict[str, Any],
    *,
    source_key: str,
) -> Dict[str, Any]:
    """Mescla campos parseados no item do crawler e roda normalize_deadline."""
    out = deepcopy(item)
    extras = out.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        out["extras"] = extras

    for k in (
        "fim_inscricao",
        "prazo_envio_raw",
        "fim_inscricao_raw",
        "deadline",
        "prazo_data",
    ):
        if parsed.get(k) and not out.get(k):
            out[k] = parsed[k]

    for ek in (
        "deadline",
        "deadline_source",
        "deadline_source_field",
        "deadline_confidence",
        "grants_close_date",
        "deadline_missing_in_source",
        "deadline_requires_pdf",
    ):
        if ek in parsed and parsed[ek] is not None:
            extras[ek] = parsed[ek]

    extras["deadline_parser_source"] = source_key

    dl = normalize_deadline(out)
    extras["deadline_normalizer"] = {
        "prazo_data": dl.get("prazo_data"),
        "prazo_status": dl.get("prazo_status"),
        "prazo_confidence": dl.get("prazo_confidence"),
        "prazo_source_field": dl.get("prazo_source_field"),
        "prazo_notes": dl.get("prazo_notes"),
    }
    if dl.get("prazo_data") and not out.get("fim_inscricao"):
        out["fim_inscricao"] = dl["prazo_data"]
    if dl.get("prazo_raw") and not out.get("prazo_envio_raw"):
        out["prazo_envio_raw"] = dl["prazo_raw"]

    return out


def enrich_china_crawler_item(item: Dict[str, Any], *, detail_html: str = "", listing_text: str = "") -> Dict[str, Any]:
    text = " ".join(
        [
            str(item.get("titulo") or ""),
            str(item.get("descricao") or ""),
            listing_text,
        ]
    )
    parsed = parse_china_tender_deadlines(text, html=detail_html)
    return merge_deadline_into_item(item, parsed, source_key="china_mofcom")


def enrich_araucaria_crawler_item(item: Dict[str, Any], *, extra_text: str = "") -> Dict[str, Any]:
    pdf_text = None
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if extras.get("pdf_texto_extraido"):
        pdf_text = str(extras["pdf_texto_extraido"])
    has_pdf = bool(
        str(item.get("link") or "").lower().endswith(".pdf")
        or extras.get("pdf_url")
        or any(
            isinstance(a, dict) and str(a.get("url", "")).lower().endswith(".pdf")
            for a in (extras.get("anexos") or [])
        )
    )
    parsed = parse_araucaria_deadlines(
        " ".join([str(item.get("descricao") or ""), str(item.get("titulo") or ""), extra_text]),
        has_pdf=has_pdf,
        pdf_text=pdf_text,
    )
    return merge_deadline_into_item(item, parsed, source_key="fundacao_araucaria")


def enrich_grants_crawler_item(item: Dict[str, Any], *, api_row: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    row = dict(api_row or {})
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    row.setdefault("close_date", extras.get("close_date") or item.get("fim_inscricao"))
    row.setdefault("posted_date", extras.get("posted_date") or item.get("data_publicacao"))
    row.setdefault("closeDate", row.get("close_date"))
    row.setdefault("postedDate", row.get("posted_date"))
    parsed = parse_grants_api_deadlines(row)
    return merge_deadline_into_item(item, parsed, source_key="grants_gov")
