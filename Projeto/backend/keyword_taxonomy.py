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

# Frases multi-palavra: substring no texto normalizado (espaços colapsados).
# Palavra única curta (<12 chars): exige fronteira [^a-z0-9] para evitar "ita" em "digital",
# "dcta" em palavras compostas acidentais, etc.
# Palavra única longa (>=12): substring (ex.: "aeroespacial").
# Excepções documentadas:
#   - Padrões com & ou hífen: re.escape no ramo de fronteira (token curto).
#   - Siglas curtas (ex.: dcta, inpe, nasa): só disparam como token isolado por fronteira;
#     não usar siglas de 2–3 letras salvo contexto frasal (espaço no padrão).
THEMATIC_PATTERNS: Dict[str, List[str]] = {
    "defesa": [
        "defesa",
        "base industrial de defesa",
        "defesa nacional",
        "ministerio da defesa",
        "tecnologias de defesa",
        "forcas armadas",
        "militar",
        "exercito",
        "marinha",
        "aeronautica",
    ],
    "seguranca_publica": [
        "seguranca publica",
        "policiamento",
        "forca nacional",
        "pericia criminal",
    ],
    "nuclear": [
        "energia nuclear",
        "fisica nuclear",
        "engenharia nuclear",
        "radiofarmaco",
        "radioprotecao",
        "combustivel nuclear",
        "uranio",
        "reator nuclear",
        "fissao",
        "fusao",
        "nuclear",
    ],
    "materiais": [
        "ciencia dos materiais",
        "materiais avancados",
        "liga metalica",
        "composito",
        "blindagem",
    ],
    "energia": [
        "eficiencia energetica",
        "eletronuclear",
        "geracao distribuida",
        "matriz energetica",
        "energia",
        "combustivel",
    ],
    "aeroespacial": [
        "aeroespacial",
        "aerospace",
        "space industry",
        "space mission",
        "veiculo lancador",
        "veículo lançador",
        "lancador espacial",
        "instituto tecnologico de aeronautica",
        "instituto tecnologico de aeronáutica",
        "tecnologias aeroespaciais",
        "engenharia aeroespacial",
        "satelite",
        "satélite",
        "orbita",
        "orbital",
        "foguete",
        "agencia espacial",
        "missao espacial",
        "dcta",
        "ita aeroespacial",
        "iae aeronautica",
        "instituto de aeronautica e espaco",
        "inpe",
        "jaxa",
        "nasa",
        "espacial",
    ],
    "veiculos": [
        "veiculo militar",
        "blindado",
        "viatura",
        "navio patrulha",
        "submarino",
    ],
    "industria": [
        "industria pesada",
        "cadeia produtiva",
        "manufatura",
        "industrial",
    ],
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


def _pattern_matches(norm: str, pattern: str) -> bool:
    """
    Evita substring curta dentro de palavras comuns (ex.: 'ita' em 'digital').

    - Frase com espaço: substring directa em `norm`.
    - Token longo (>= 12 chars): substring (ex.: 'aeroespacial').
    - Token mais curto: fronteira não alfanumérica (texto já está normalizado sem acentos).
    """
    p = (pattern or "").strip().lower()
    if not p or not norm:
        return False
    if " " in p:
        return p in norm
    if len(p) >= 12:
        return p in norm
    return bool(
        re.search(
            rf"(^|[^a-z0-9]){re.escape(p)}([^a-z0-9]|$)",
            norm,
        )
    )


def has_interest_keyword(text: str) -> bool:
    norm = _normalize(text)
    return any(_pattern_matches(norm, keyword) for keyword in KEYWORDS_INTEREST)


def classify_thematic_tags(text: str) -> List[str]:
    norm = _normalize(text)
    found: Set[str] = set()
    for theme, patterns in THEMATIC_PATTERNS.items():
        if any(_pattern_matches(norm, pat) for pat in patterns):
            found.add(theme)
    return sorted(found)
