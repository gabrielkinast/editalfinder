from __future__ import annotations

import re
from typing import Dict, List, Set

KEYWORDS_INTEREST: List[str] = [
    "defesa nacional",
    "base industrial de defesa",
    "seguranca publica",
    "soberania",
    "tecnologias estrategicas",
    "materiais avancados",
    "blindagem",
    "veiculos militares",
    "aeronautica",
    "naval",
    "submarino",
    "nuclear",
    "energia nuclear",
    "fisica nuclear",
    "quimica nuclear",
    "engenharia nuclear",
    "radioprotecao",
    "radiofarmacos",
    "uranio",
    "combustivel nuclear",
    "reatores",
    "fusao nuclear",
    "fissao nuclear",
    "sensores",
    "radares",
    "propulsao",
    "sistemas embarcados",
    "dual-use",
    "p&d",
    "pd&i",
    "inovacao",
    "chamada publica",
    "edital",
    "licitacao",
    "pregao",
    "financiamento",
    "subvencao",
]

THEMATIC_PATTERNS: Dict[str, List[str]] = {
    "defesa": ["defesa", "base industrial de defesa", "forcas armadas", "militar", "exercito", "marinha", "aeronautica"],
    "seguranca_publica": ["seguranca publica", "policia", "policiamento", "forca nacional", "pericia"],
    "nuclear": ["nuclear", "uranio", "reator", "radiofarmaco", "radioprotecao", "fissao", "fusao"],
    "materiais": ["ciencia dos materiais", "materiais avancados", "blindagem", "liga metalica", "composito"],
    "energia": ["energia", "geracao", "eficiencia energetica", "eletronuclear", "combustivel"],
    "aeroespacial": ["aeroespacial", "espacial", "satelite", "lancador", "dcta", "ita", "iae"],
    "veiculos": ["veiculo militar", "blindado", "viatura", "submarino", "navio patrulha"],
    "industria": ["industria pesada", "manufatura", "cadeia produtiva", "industrial"],
    # Evita sobreclassificação com termos genéricos isolados.
    "ciencia_tecnologia": [
        "pesquisa cientifica",
        "desenvolvimento tecnologico",
        "ciencia tecnologia inovacao",
        "ct&i",
        "pd&i",
        "p&d",
        "laboratorio de pesquisa",
    ],
    "dual_use": ["dual-use", "duplo uso", "tecnologia dual", "uso dual"],
}

def _normalize(text: str) -> str:
    cleaned = (text or "").lower()
    cleaned = (
        cleaned.replace("á", "a")
        .replace("à", "a")
        .replace("â", "a")
        .replace("ã", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )
    return re.sub(r"\s+", " ", cleaned).strip()


def has_interest_keyword(text: str) -> bool:
    norm = _normalize(text)
    return any(keyword in norm for keyword in KEYWORDS_INTEREST)


def classify_thematic_tags(text: str) -> List[str]:
    norm = _normalize(text)
    found: Set[str] = set()
    for theme, patterns in THEMATIC_PATTERNS.items():
        if any(pattern in norm for pattern in patterns):
            found.add(theme)
    return sorted(found)
