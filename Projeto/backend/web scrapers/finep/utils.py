from __future__ import annotations

import re
import unicodedata
from datetime import datetime, date
from typing import Iterable, Optional


NOISE_PATTERNS = (
    "seu navegador nao suporta java script",
    "seu navegador não suporta java script",
    "alguns recursos estarão limitados",
    "alguns recursos estarao limitados",
    "javascript",
)


PDF_POSITIVE_HINTS = (
    "edital",
    "chamada",
    "regulamento",
    "anexo",
    "faq",
    "resultado",
    "formulario",
    "manual operacional",
)

PDF_NEGATIVE_HINTS = (
    "manual_cliente",
    "manual cliente",
    "cadastro",
    "cliente_cadastro",
    "termo de uso",
)


def normalize_text(text: str | None) -> str:
    if not text:
        return ""
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()



def normalize_ascii(text: str | None) -> str:
    text = normalize_text(text)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()



def parse_br_date(text: str | None) -> Optional[date]:
    if not text:
        return None
    text = normalize_text(text)
    match = re.search(r"(\d{2}[/-]\d{2}[/-]\d{4})", text)
    if not match:
        return None
    raw = match.group(1).replace("-", "/")
    try:
        return datetime.strptime(raw, "%d/%m/%Y").date()
    except ValueError:
        return None



def clean_multiline_text(text: str | None) -> str:
    if not text:
        return ""
    text = text.replace("\r", "\n")
    lines = [normalize_text(line) for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)



def is_noise_text(text: str | None) -> bool:
    normalized = normalize_ascii(text)
    return any(pattern in normalized for pattern in NOISE_PATTERNS)



def choose_best_pdf(candidates: Iterable[str]) -> str | None:
    best_url = None
    best_score = -10**9

    for url in candidates:
        nurl = normalize_ascii(url)
        score = 0
        if ".pdf" in nurl:
            score += 20
        for hint in PDF_POSITIVE_HINTS:
            if hint in nurl:
                score += 8
        for hint in PDF_NEGATIVE_HINTS:
            if hint in nurl:
                score -= 30
        if "download.finep.gov.br" in nurl:
            score += 3
        if best_url is None or score > best_score:
            best_url = url
            best_score = score

    return best_url
