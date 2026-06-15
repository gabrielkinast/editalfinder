"""Normalização de datas e extração de prazos (fonte única para crawlers + transformer)."""
from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional, Tuple

DATE_CANDIDATE_REGEX = (
    r"(\d{4}-\d{2}-\d{2}"
    r"|\d{1,2}/\d{1,2}/\d{2,4}"
    r"|\d{1,2}\.\d{1,2}\.\d{4}"
    r"|\d{1,2}\s+de\s+[a-zA-ZçÇãõáéíóú]+\s+de\s+\d{4}"
    r"|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}"
    r"|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})"
)

EN_MONTH = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

PT_MONTH = {
    "janeiro": "01",
    "fevereiro": "02",
    "março": "03",
    "marco": "03",
    "abril": "04",
    "maio": "05",
    "junho": "06",
    "julho": "07",
    "agosto": "08",
    "setembro": "09",
    "outubro": "10",
    "novembro": "11",
    "dezembro": "12",
}

# Contextos que indicam data de publicação/resultado/evento — não prazo de submissão
REJECT_CONTEXT_PATTERNS: List[str] = [
    r"publicado\s+em",
    r"divulgado\s+em",
    r"lan[cç]ado,?\s+em",
    r"lan[cç]ou,?\s+em",
    r"^em\s+\d",
    r"resultado\s+em",
    r"resultado\s+final",
    r"evento\s+em",
    r"not[ií]cia\s+de",
    r"atualizado\s+em",
    r"updated\s+on",
    r"posted\s+on",
    r"posted\s+date",
    r"post\s+date",
    r"release\s+date",
    r"data\s+de\s+publica",
    r"open\s+date",
    r"forecast",
    r"palestra\s+de\s+esclarecimento",
    r"webinar",
]

# Palavras que indicam prazo de submissão/inscrição
DEADLINE_KEYWORD_PATTERNS: List[str] = [
    r"prazo\s+final",
    r"data\s+limite",
    r"inscri[cç][õo]es?\s+at[eé]",
    r"submiss[aã]o\s+at[eé]",
    r"propostas?\s+at[eé]",
    r"envio\s+de\s+propostas?\s+at[eé]",
    r"encerramento",
    r"per[ií]odo\s+de\s+(?:inscri[cç][õo]es?|submiss[aã]o)",
    r"vig[eê]ncia\s+do\s+edital\s+at[eé]",
    r"\bat[eé]\s+(?:o\s+dia\s+)?\d",
    r"deadline",
    r"application\s+deadline",
    r"proposal\s+deadline",
    r"submission\s+deadline",
    r"full\s+application\s+deadline",
    r"concept\s+paper\s+deadline",
    r"letter\s+of\s+intent\s+deadline",
    r"closing\s+date",
    r"close\s+date",
    r"due\s+date",
    r"responses?\s+due",
    r"applications?\s+due",
    r"proposals?\s+due",
    r"nofo\s+closes",
    r"opportunity\s+closes",
    r"call\s+deadline",
    r"call\s+closes",
    r"submission\s+deadline",
    r"project\s+submission\s+deadline",
]

PT_TEXT_DEADLINE_PATTERNS: List[Tuple[str, str]] = [
    (r"inscri[cç][õo]es?\s+at[eé]\s+(\d{1,2}/\d{1,2}/\d{4})", "inscricoes_ate"),
    (r"submiss[aã]o\s+at[eé]\s+(\d{1,2}/\d{1,2}/\d{4})", "submissao_ate"),
    (r"propostas?\s+at[eé]\s+(\d{1,2}/\d{1,2}/\d{4})", "propostas_ate"),
    (r"prazo\s+final\s*[:\s]+(\d{1,2}/\d{1,2}/\d{4})", "prazo_final"),
    (r"data\s+limite\s*[:\s]+(\d{1,2}/\d{1,2}/\d{4})", "data_limite"),
    (r"encerramento\s*[:\s]+(\d{1,2}/\d{1,2}/\d{4})", "encerramento"),
    (r"at[eé]\s+o\s+dia\s+(\d{1,2}/\d{1,2}/\d{4})", "ate_dia"),
    (r"at[eé]\s+(\d{1,2}/\d{1,2}/\d{4})", "ate"),
    (r"at[eé]\s+(\d{1,2}\s+de\s+[a-zçãõéêôíóú]+\s+de\s+\d{4})", "ate_extenso"),
    (
        r"per[ií]odo\s+de\s+(?:inscri[cç][õo]es?|submiss[aã]o)\s*[:\s]*\d{1,2}/\d{1,2}/\d{4}\s*a\s*(\d{1,2}/\d{1,2}/\d{4})",
        "periodo_fim",
    ),
    (
        r"inscri[cç][õo]es?\s+de\s+\d{1,2}/\d{1,2}/\d{4}\s+at[eé]\s+(\d{1,2}/\d{1,2}/\d{4})",
        "inscricoes_periodo_fim",
    ),
]

EN_TEXT_DEADLINE_PATTERNS: List[Tuple[str, str]] = [
    (r"full\s+application\s+deadline\s*[:\s]+([^\n<]{6,40})", "full_application_deadline"),
    (r"application\s+deadline\s*[:\s]+([^\n<]{6,40})", "application_deadline"),
    (r"proposal\s+deadline\s*[:\s]+([^\n<]{6,40})", "proposal_deadline"),
    (r"submission\s+deadline\s*[:\s]+([^\n<]{6,40})", "submission_deadline"),
    (r"concept\s+paper\s+deadline\s*[:\s]+([^\n<]{6,40})", "concept_paper_deadline"),
    (r"letter\s+of\s+intent\s+deadline\s*[:\s]+([^\n<]{6,40})", "loi_deadline"),
    (r"closing\s+date\s*[:\s]+([^\n<]{6,40})", "closing_date"),
    (r"close\s+date\s*[:\s]+([^\n<]{6,40})", "close_date"),
    (r"due\s+date\s*[:\s]+([^\n<]{6,40})", "due_date"),
    (r"responses?\s+due\s*[:\s]+([^\n<]{6,40})", "responses_due"),
    (r"applications?\s+due\s*[:\s]+([^\n<]{6,40})", "applications_due"),
    (r"deadline\s*[:\s]+([^\n<]{6,40})", "deadline"),
    (r"nofo\s+closes?\s+on\s+([^\n<]{6,40})", "nofo_closes"),
    (r"opportunity\s+closes?\s+on\s+([^\n<]{6,40})", "opportunity_closes"),
    (r"call\s+closes?\s+on\s+([^\n<]{6,40})", "call_closes"),
    (r"call\s+deadline\s*[:\s]+([^\n<]{6,40})", "call_deadline"),
]


def _in_year_range(year: int) -> bool:
    return 2000 <= year <= 2035


def _parse_english_month_phrase(text: str) -> Optional[str]:
    t = text.lower().strip()
    m = re.search(
        r"(january|february|march|april|may|june|july|august|september|october|november|december|"
        r"jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2}),?\s+(\d{4})",
        t,
    )
    if m:
        month_name, day, year = m.groups()
        month = EN_MONTH.get(month_name)
        if month:
            try:
                dt = datetime(int(year), month, int(day)).date()
                if _in_year_range(dt.year):
                    return dt.isoformat()
            except ValueError:
                pass
    m2 = re.search(r"(\d{1,2})\s+([a-z]{3,9})\s+(\d{4})", t)
    if m2:
        day, month_name, year = m2.groups()
        month = EN_MONTH.get(month_name)
        if month:
            try:
                dt = datetime(int(year), month, int(day)).date()
                if _in_year_range(dt.year):
                    return dt.isoformat()
            except ValueError:
                pass
    return None


def normalize_date_str(raw: Optional[str], *, locale: str = "pt_BR") -> Optional[str]:
    """Converte strings de data para YYYY-MM-DD (anos 2000–2035)."""
    if not raw or not isinstance(raw, str):
        return None
    raw = raw.strip()
    if not raw:
        return None
    low = raw.lower()
    if low in ("tbd", "forecasted", "no closing date", "none", "null", "n/a"):
        return None

    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(raw[:10], fmt).date()
            if _in_year_range(dt.year):
                return dt.isoformat()
        except Exception:
            continue

    if locale.startswith("en"):
        for fmt in ("%m/%d/%Y", "%m/%d/%y"):
            try:
                dt = datetime.strptime(raw[:10], fmt).date()
                if _in_year_range(dt.year):
                    return dt.isoformat()
            except Exception:
                continue

    for fmt in ("%d/%m/%Y", "%d.%m.%Y"):
        try:
            dt = datetime.strptime(raw[:10], fmt).date()
            if _in_year_range(dt.year):
                return dt.isoformat()
        except Exception:
            continue

    m = re.search(r"(\d{1,2})\s+de\s+([a-zA-ZçÇãõáéíóú]+)\s+de\s+(\d{4})", low)
    if m:
        day, month_name, year = m.groups()
        month = PT_MONTH.get(month_name)
        if month:
            try:
                dt = datetime.strptime(f"{int(day):02d}/{month}/{year}", "%d/%m/%Y").date()
                if _in_year_range(dt.year):
                    return dt.isoformat()
            except Exception:
                pass

    en = _parse_english_month_phrase(raw)
    if en:
        return en

    m_us = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", raw)
    if m_us:
        a, b, year = (int(x) for x in m_us.groups())
        if locale.startswith("en"):
            try:
                dt = datetime(year, a, b).date()
                if _in_year_range(dt.year):
                    return dt.isoformat()
            except ValueError:
                pass
        try:
            dt = datetime(year, b, a).date()
            if _in_year_range(dt.year):
                return dt.isoformat()
        except ValueError:
            pass

    return None


def _context_rejected(ctx: str) -> bool:
    low = ctx.lower()
    return any(re.search(p, low, re.I) for p in REJECT_CONTEXT_PATTERNS)


def _has_deadline_keyword(ctx: str) -> bool:
    low = ctx.lower()
    return any(re.search(p, low, re.I) for p in DEADLINE_KEYWORD_PATTERNS)


def extract_deadline_from_text(text: str, *, locale: str = "pt_BR") -> Optional[str]:
    """Extrai primeira data com contexto de prazo; rejeita publicação/resultado."""
    if not text:
        return None

    patterns = PT_TEXT_DEADLINE_PATTERNS if not locale.startswith("en") else EN_TEXT_DEADLINE_PATTERNS + PT_TEXT_DEADLINE_PATTERNS
    for pattern, _field in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            ctx_start = max(0, m.start() - 60)
            ctx = text[ctx_start : m.end() + 20]
            if _context_rejected(ctx):
                continue
            raw = m.group(1).strip()
            iso = normalize_date_str(raw, locale=locale)
            if iso:
                return iso

    keyword_patterns = [
        r"(?:prazo|deadline|inscri[cç][aã]o|encerramento|submiss[aã]o|limite|at[eé]|closing|due)\D{0,50}"
        + DATE_CANDIDATE_REGEX,
    ]
    for pattern in keyword_patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            ctx_start = max(0, m.start() - 60)
            ctx = text[ctx_start : m.end() + 20]
            if _context_rejected(ctx):
                continue
            if not _has_deadline_keyword(ctx):
                continue
            groups = m.groups()
            raw = groups[-1] if groups else m.group(0)
            iso = normalize_date_str(raw, locale=locale)
            if iso:
                return iso

    return None


def extract_deadline_from_text_enriched(
    text: str,
    *,
    locale: str = "pt_BR",
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Retorna (iso, source_field, raw_fragment)."""
    if not text:
        return None, None, None

    patterns = (
        EN_TEXT_DEADLINE_PATTERNS + PT_TEXT_DEADLINE_PATTERNS
        if locale.startswith("en")
        else PT_TEXT_DEADLINE_PATTERNS + EN_TEXT_DEADLINE_PATTERNS
    )
    for pattern, field in patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            ctx_start = max(0, m.start() - 60)
            ctx = text[ctx_start : m.end() + 20]
            if _context_rejected(ctx):
                continue
            raw = m.group(1).strip()
            iso = normalize_date_str(raw, locale=locale)
            if not iso:
                iso = _parse_english_month_phrase(raw)
            if iso:
                return iso, field, raw[:120]

    iso = extract_deadline_from_text(text, locale=locale)
    if iso:
        return iso, "texto_keyword", None
    return None, None, None
