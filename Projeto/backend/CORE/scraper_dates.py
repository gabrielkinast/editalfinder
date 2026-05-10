"""Extração leve de datas/prazos para crawlers (evita importar transformer.py inteiro)."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

DATE_CANDIDATE = r"(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4}|\d{1,2}\s+de\s+[a-zA-ZçÇãõáéíóú]+\s+de\s+\d{4})"

_MONTH_PT = {
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


def normalize_date_str(raw: str) -> Optional[str]:
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
    m = re.search(r"(\d{1,2})\s+de\s+([a-zA-ZçÇãõáéíóú]+)\s+de\s+(\d{4})", raw)
    if m:
        day, month_name, year = m.groups()
        month = _MONTH_PT.get(month_name)
        if month:
            try:
                dt = datetime.strptime(f"{int(day):02d}/{month}/{year}", "%d/%m/%Y").date()
                if 2000 <= dt.year <= 2035:
                    return dt.isoformat()
            except Exception:
                pass
    return None


def extract_deadline_from_text(text: str) -> Optional[str]:
    """Primeira data encontrada após palavras-chave de prazo (PT/EN)."""
    if not text:
        return None
    keyword_patterns = [
        r"(?:prazo|deadline|inscri[cç][aã]o|encerramento|submiss[aã]o|limite|até|closing|due)\D{0,40}"
        + DATE_CANDIDATE,
    ]
    for pattern in keyword_patterns:
        for hit in re.findall(pattern, text, re.IGNORECASE):
            normalized = normalize_date_str(hit)
            if normalized:
                return normalized
    return None


def extract_latest_deadline_from_text(text: str) -> Optional[str]:
    """Entre várias datas plausíveis no texto, retorna a mais tardia (útil quando há cronograma)."""
    if not text:
        return None
    found: list[str] = []
    for m in re.finditer(DATE_CANDIDATE, text, re.IGNORECASE):
        n = normalize_date_str(m.group(1))
        if n:
            found.append(n)
    if not found:
        d = extract_deadline_from_text(text)
        return d
    return max(found)
