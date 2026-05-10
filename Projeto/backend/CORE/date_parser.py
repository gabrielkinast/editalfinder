"""Normalização de datas e extração de prazos (fonte única para crawlers + transformer)."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

DATE_CANDIDATE_REGEX = r"(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\s+de\s+[a-zA-ZçÇãõáéíóú]+\s+de\s+\d{4})"


def normalize_date_str(raw: Optional[str]) -> Optional[str]:
    """Converte strings de data para YYYY-MM-DD (anos 2000–2035)."""
    if not raw or not isinstance(raw, str):
        return None
    raw = raw.strip().lower()
    if not raw:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            dt = datetime.strptime(raw[:10], fmt).date()
            if 2000 <= dt.year <= 2035:
                return dt.isoformat()
        except Exception:
            continue

    month_map = {
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
    m = re.search(r"(\d{1,2})\s+de\s+([a-zA-ZçÇãõáéíóú]+)\s+de\s+(\d{4})", raw)
    if m:
        day, month_name, year = m.groups()
        month = month_map.get(month_name)
        if month:
            try:
                dt = datetime.strptime(f"{int(day):02d}/{month}/{year}", "%d/%m/%Y").date()
                if 2000 <= dt.year <= 2035:
                    return dt.isoformat()
            except Exception:
                pass
    return None


def extract_deadline_from_text(text: str) -> Optional[str]:
    if not text:
        return None
    keyword_patterns = [
        r"(?:prazo|deadline|inscri[cç][aã]o|encerramento|submiss[aã]o|limite|até|closing|due)\D{0,40}"
        + DATE_CANDIDATE_REGEX,
    ]
    for pattern in keyword_patterns:
        for hit in re.findall(pattern, text, re.IGNORECASE):
            normalized = normalize_date_str(hit)
            if normalized:
                return normalized
    return None
