"""Extração de valores monetários a partir de texto livre."""
from __future__ import annotations

import re
from typing import Optional


def extract_value(text: Optional[str]) -> Optional[str]:
    """Extrai valores monetários (R$, milhão, USD, EUR) do texto."""
    if not text:
        return None

    text = re.sub(r"\s+", " ", text)
    text = re.sub(
        r"(\d+),(\d+)\s?(milh[aã]o|milh[oõ]es|bilh[aã]o|bilh[oõ]es)",
        r"\1.\2 \3",
        text,
        flags=re.IGNORECASE,
    )

    range_pattern = (
        r"(?:R\$\s?)?(\d+(?:[.,]\d+)*(?:\s?milh[oõ]es|bilh[oõ]es|mil|milh[aã]o|bilh[aã]o)?)\s+"
        r"(?:a|até|e)\s+(?:R\$\s?)?(\d+(?:[.,]\d+)*(?:\s?milh[oõ]es|bilh[oõ]es|mil|milh[aã]o|bilh[aã]o)?)"
    )
    range_match = re.search(range_pattern, text, re.IGNORECASE)
    if range_match:
        return f"R$ {range_match.group(1)} - {range_match.group(2)}"

    pattern = r"R\$\s?(\d+(?:[.,]\d+)*(?:,\d{2})?)(?:\s?(milh[oõ]es|bilh[oõ]es|mil|milh[aã]o|bilh[aã]o))?"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        valor_num = match.group(1)
        multiplicador = match.group(2)
        if multiplicador:
            return f"R$ {valor_num} {multiplicador}"
        return f"R$ {valor_num}"

    pattern_millions = r"(\d+(?:[.,]\d+)?)\s?(milh[oõ]es|bilh[oõ]es|mil|milh[aã]o|bilh[aã]o)"
    match_mil = re.search(pattern_millions, text, re.IGNORECASE)
    if match_mil:
        return f"R$ {match_mil.group(1)} {match_mil.group(2)}"

    usd = re.search(
        r"(\$|USD)\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d{3})*(?:,\d{2})?)\s?"
        r"(milh[oõ]es|bilh[oõ]es|mil|milh[aã]o|bilh[aã]o)?",
        text,
        re.IGNORECASE,
    )
    if usd:
        val = usd.group(2)
        mult = usd.group(3) or ""
        return f"USD {val} {mult}".strip()

    eur = re.search(
        r"(€|EUR)\s?(\d{1,3}(?:\.\d{3})*(?:,\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?)\s?"
        r"(milh[oõ]es|bilh[oõ]es|mil|milh[aã]o|bilh[aã]o)?",
        text,
        re.IGNORECASE,
    )
    if eur:
        val = eur.group(2)
        mult = eur.group(3) or ""
        return f"EUR {val} {mult}".strip()

    return None


def extract_value_min(text: Optional[str]) -> Optional[float]:
    """Menor valor numérico associado a expressões tipo 'mínimo', 'a partir de'."""
    if not text:
        return None

    text_clean = text.replace("\n", " ")
    text_lower = text_clean.lower()

    min_patterns = [
        r"(?:valor\s+m[ií]nimo|m[ií]nimo\s+(?:de\s+)?(?:R\$\s?)?)([\d\.,]+)",
        r"(?:a\s+partir\s+de\s+(?:R\$\s?)?)([\d\.,]+)",
        r"(?:m[ií]nima\s+(?:de\s+)?(?:R\$\s?)?)([\d\.,]+)",
        r"(?:apoio\s+(?:de|no)\s+(?:valor\s+de\s+)?(?:R\$\s?)?)([\d\.,]+)",
        r"(?:recursos?\s+(?:de|no)\s+(?:valor\s+de\s+)?(?:R\$\s?)?)([\d\.,]+)",
        r"(?:at[eé]\s+(?:R\$\s?)?)([\d\.,]+)\s+(?:a|até)",
        r"(?:entre\s+(?:R\$\s?)?)([\d\.,]+)\s+e\s+(?:R\$\s?)?([\d\.,]+)",
    ]

    min_values: list[float] = []
    for pattern in min_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            val = match[0] if isinstance(match, tuple) else match
            try:
                val_clean = val.replace(".", "").replace(",", ".")
                num_val = float(val_clean)
                if num_val > 0:
                    min_values.append(num_val)
            except Exception:
                pass

    return min(min_values) if min_values else None
