from __future__ import annotations

import re
import unicodedata
from datetime import datetime, date
from typing import Iterable, Optional

NOISE_PATTERNS = [
    "aceitar todos",
    "aceitar necessários",
    "utilizamos cookies",
    "voltar imprimir",
    "redes sociais",
    "início do menu",
    "início do conteúdo",
    "desenvolvido pela procergs",
]

NAV_TITLES = {
    "inicial", "abertos", "em julgamento", "encerrados", "mais avisos", "mais notícias",
    "fale conosco", "mapa do site", "transparência ativa", "quem somos", "equipe",
    "legislação", "institucional", "notícias", "avisos", "conteúdo", "menu", "busca",
}

PDF_NEGATIVE_HINTS = [
    "lista final",
    "lista preliminar",
    "errata",
    "resultado",
    "homolog",
    "retificação",
    "retificacao",
    "ata",
    "aditivo",
    "manual",
    "cartilha",
    "orienta",
]

PDF_POSITIVE_HINTS = [
    "edital",
    "chamada",
    "programa",
    "bolsa",
    "bolsas",
    "seleção",
    "selecao",
    "trajetorias",
    "talentos globais",
]

DATE_PATTERNS = [
    re.compile(r"\b(\d{2}/\d{2}/\d{4})\b"),
    re.compile(r"\b(\d{2}-\d{2}-\d{4})\b"),
]


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text).strip().lower()


def clean_text(text: str) -> str:
    text = (text or "").replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -\n\t")


def is_noise_text(text: str) -> bool:
    text_norm = normalize_text(text)
    if not text_norm:
        return True

    # Só considera ruído se o texto for curto e praticamente só boilerplate.
    if len(text_norm) < 180:
        return any(pattern in text_norm for pattern in NOISE_PATTERNS)

    hits = sum(1 for pattern in NOISE_PATTERNS if pattern in text_norm)

    # Se o texto tem sinais reais de edital, não descarta.
    sinais_validos = [
        "edital",
        "chamada",
        "programa",
        "bolsa",
        "bolsas",
        "inscricao",
        "inscricoes",
        "submissao",
        "prazo",
        "pesquisa",
        "inovacao",
    ]
    if any(s in text_norm for s in sinais_validos):
        return False

    # Só trata como ruído quando quase tudo parece boilerplate.
    return hits >= 3

def is_probable_nav_title(text: str) -> bool:
    text_norm = normalize_text(text)
    return (not text_norm) or (text_norm in NAV_TITLES)


def parse_date_br(text: str) -> Optional[date]:
    text = clean_text(text)
    if not text:
        return None
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            return parse_date_br(match.group(1))
    return None


def extract_all_dates(text: str) -> list[date]:
    found: list[date] = []
    for pattern in DATE_PATTERNS:
        for match in pattern.findall(text or ""):
            dt = parse_date_br(match)
            if dt and dt not in found:
                found.append(dt)
    return found


def first_nonempty(values: Iterable[Optional[str]]) -> Optional[str]:
    for value in values:
        value = clean_text(value or "")
        if value:
            return value
    return None


def extract_numero_edital(text: str) -> Optional[str]:
    m = re.search(r"\b(?:edital|chamada)\s*(?:n[ºo.]?\s*)?(\d{1,3}/\d{4})\b", text or "", flags=re.I)
    if m:
        return m.group(1)
    return None


def score_pdf(name: str, url: str) -> int:
    hay = normalize_text(f"{name} {url}")
    score = 0
    for hint in PDF_POSITIVE_HINTS:
        if hint in hay:
            score += 4
    for hint in PDF_NEGATIVE_HINTS:
        if hint in hay:
            score -= 7
    if hay.endswith(".pdf") or ".pdf" in hay:
        score += 1
    if "upload/arquivos" in hay:
        score += 1
    return score


def choose_best_pdf(candidates: list[tuple[str, str]]) -> Optional[tuple[str, str]]:
    if not candidates:
        return None
    unique: list[tuple[str, str]] = []
    seen = set()
    for name, url in candidates:
        key = url.strip().lower()
        if key not in seen:
            seen.add(key)
            unique.append((clean_text(name), url))
    ranked = sorted(unique, key=lambda item: (score_pdf(item[0], item[1]), len(item[0])), reverse=True)
    best = ranked[0]
    return best if score_pdf(best[0], best[1]) >= 0 else None
