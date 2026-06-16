"""
Perfis de acionabilidade por fonte — Backend 10.1C.

Complementa SOURCE_QUALITY_PROFILES com regras de classificação por fonte.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple

# Marcadores globais reutilizados
SUPPLIER_PORTAL_MARKERS: Tuple[str, ...] = (
    "supplier portal",
    "become a supplier",
    "procurement",
    "doing business with us",
    "supplier registration",
    "vendor portal",
    "fornecedores",
    "cadastro de fornecedor",
)

CAREERS_MARKERS: Tuple[str, ...] = (
    "trabalhe conosco",
    "trabalhe no",
    "trabalhe na",
    "vagas",
    "carreiras",
    "now hiring",
    "join our team",
    "work with us",
)

SOURCE_ACTIONABILITY_PROFILES: Dict[str, Dict[str, Any]] = {
    "BDMG": {
        "kind": "mixed_bank_portal",
        "portal_generic_titles": [
            "sobre o bdmg",
            "nossa essencia",
            "atuacao",
            "sala de imprensa",
            "eventos",
            "english",
            "protecao de dados",
            "privacidade",
            "noticias",
            "documentacao bdmg",
        ],
        "portal_util_markers": [
            "linhas permanentes",
            "linhas de financiamento",
            "linha de financiamento",
            "credito para municipios",
            "credito para municípios",
            "financiamento municipal",
            "financiamento para inovacao",
            "financiamento para inovação",
            "credito para",
            "credito ",
        ],
        "news_markers": ["noticia", "imprensa", "documentacao"],
        "careers_markers": ["trabalhe no bdmg", "trabalhe na bdmg"],
    },
    "BNB": {
        "kind": "bank_funding_portal",
        "portal_util_markers": [
            "atividades financiadas",
            "credito para poder",
            "crédito para poder",
            "financiamento de projetos",
            "linha de credito",
            "linha de crédito",
        ],
        "opportunity_markers": ["edital", "chamada", "selecao publica", "seleção pública", "subvencao", "subvenção"],
    },
    "Eureka Network": {
        "kind": "funding_hub",
        "portal_util_titles": [
            "open funding opportunities",
            "funding opportunities",
        ],
        "opportunity_markers": [
            "call for projects",
            "call for proposals",
            "eurostars",
            "globalstars",
            "innowwide",
        ],
    },
    "QST": {
        "kind": "news_research_source",
        "block_as_edital": True,
        "default_if_weak": "noticia",
        "news_markers": ["news", "press", "release", "研究", "ニュース"],
    },
    "China MOFCOM": {
        "kind": "china_tender",
        "tender_markers": ["招标", "tender", "procurement", "bidding", "bid announcement"],
        "news_markers": ["news", "announcement", "通知", "公告"],
        "keep_desconhecido_without_strong_evidence": True,
    },
    "China NSFC": {
        "kind": "china_research",
        "tender_markers": ["grant", "funding", "program", "project"],
        "news_markers": ["news", "announcement", "通知"],
        "keep_desconhecido_without_strong_evidence": True,
    },
    "DoD SBIR/STTR": {
        "kind": "grant_like_with_portal",
        "portal_util_titles": [
            "funding opportunities",
            "dod sbir/sttr funding opportunities",
        ],
        "portal_util_markers": ["how to apply", "program overview", "overview"],
        "portal_generic_titles": ["data resources"],
        "opportunity_markers": [
            "sbir",
            "sttr",
            "solicitation",
            "baa",
            "funding opportunity",
        ],
    },
    "EMBRAPII": {
        "kind": "mixed_calls_results",
        "known_result_markers": ["resultado final", "homologacao", "homologação", "selecionados"],
    },
}

SUPPLIER_SOURCE_CANONICAL_KEYS = frozenset(
    {
        "Lockheed Martin Suppliers",
        "General Dynamics Suppliers",
        "BAE Systems Suppliers",
        "Rheinmetall Suppliers",
        "Thales Suppliers",
        "Mitsubishi Heavy Industries",
    }
)

_SUPPLIER_DEFAULT_PROFILE: Dict[str, Any] = {
    "kind": "supplier_portal",
    "recommended_module": "portal_estrategico",
    "portal_util_markers": list(SUPPLIER_PORTAL_MARKERS),
}

# Alias normalizado (ascii lower) → chave canónica do perfil
_SOURCE_KEY_ALIASES: Dict[str, str] = {
    "bdmg": "BDMG",
    "banco de desenvolvimento de minas gerais": "BDMG",
    "bnb": "BNB",
    "banco do nordeste": "BNB",
    "eureka network": "Eureka Network",
    "eureka": "Eureka Network",
    "japan_qst": "QST",
    "qst": "QST",
    "china international tendering (mofcom)": "China MOFCOM",
    "china international tendering": "China MOFCOM",
    "china mofcom tendering": "China MOFCOM",
    "china mofcom": "China MOFCOM",
    "mofcom": "China MOFCOM",
    "china nsfc": "China NSFC",
    "nsfc": "China NSFC",
    "dod sbir/sttr": "DoD SBIR/STTR",
    "dod sbir": "DoD SBIR/STTR",
    "sbir/sttr": "DoD SBIR/STTR",
    "embrapii": "EMBRAPII",
    "lockheed martin suppliers": "Lockheed Martin Suppliers",
    "general dynamics suppliers": "General Dynamics Suppliers",
    "bae systems suppliers": "BAE Systems Suppliers",
    "rheinmetall suppliers": "Rheinmetall Suppliers",
    "thales suppliers": "Thales Suppliers",
    "mitsubishi heavy industries": "Mitsubishi Heavy Industries",
    "japan mitsubishi heavy": "Mitsubishi Heavy Industries",
}


def _norm_text(s: Any) -> str:
    if s is None:
        return ""
    t = str(s).strip().lower()
    t = unicodedata.normalize("NFKD", t)
    return "".join(c for c in t if not unicodedata.combining(c))


def normalize_source_name(source: Optional[str]) -> str:
    """Normaliza fonte_recurso/slug para chave canónica de perfil."""
    if not source:
        return ""
    raw = str(source).strip()
    key = _norm_text(raw)
    if key in _SOURCE_KEY_ALIASES:
        return _SOURCE_KEY_ALIASES[key]
    for alias, canonical in _SOURCE_KEY_ALIASES.items():
        if alias in key or key in alias:
            return canonical
    if "supplier" in key and ("lockheed" in key or "bae" in key or "general dynamics" in key):
        for part in ("lockheed martin suppliers", "general dynamics suppliers", "bae systems suppliers",
                     "rheinmetall suppliers", "thales suppliers"):
            if part.split()[0] in key:
                return _SOURCE_KEY_ALIASES.get(part, raw)
    return raw


def _is_supplier_source(canonical: str) -> bool:
    return canonical in SUPPLIER_SOURCE_CANONICAL_KEYS or "supplier" in _norm_text(canonical)


def get_source_actionability_profile(source: Optional[str]) -> Dict[str, Any]:
    canonical = normalize_source_name(source)
    if not canonical:
        return {}
    if _is_supplier_source(canonical):
        base = dict(_SUPPLIER_DEFAULT_PROFILE)
        extra = SOURCE_ACTIONABILITY_PROFILES.get(canonical, {})
        base.update(extra)
        return base
    return dict(SOURCE_ACTIONABILITY_PROFILES.get(canonical, {}))


def source_profile_has_marker(
    profile: Dict[str, Any],
    titulo: str,
    text: str,
    marker_type: str,
) -> bool:
    """Verifica marcadores do perfil: portal_generic_titles, portal_util_markers, news_markers, etc."""
    titulo_n = _norm_text(titulo)
    blob = f"{titulo_n} {_norm_text(text)}"

    if marker_type == "portal_generic_titles":
        for item in profile.get("portal_generic_titles") or []:
            n = _norm_text(item)
            if titulo_n == n or titulo_n.startswith(n + " ") or (len(titulo_n) < 60 and n in titulo_n):
                return True
        return False

    if marker_type == "portal_util_titles":
        for item in profile.get("portal_util_titles") or []:
            n = _norm_text(item)
            if titulo_n == n or n in titulo_n:
                return True
        return False

    key = {
        "portal_util": "portal_util_markers",
        "portal_util_markers": "portal_util_markers",
        "news": "news_markers",
        "news_markers": "news_markers",
        "careers": "careers_markers",
        "careers_markers": "careers_markers",
        "opportunity": "opportunity_markers",
        "opportunity_markers": "opportunity_markers",
        "tender": "tender_markers",
        "tender_markers": "tender_markers",
        "supplier": "portal_util_markers",
    }.get(marker_type, marker_type)

    markers = profile.get(key) or []
    if marker_type == "supplier" and not markers:
        markers = list(SUPPLIER_PORTAL_MARKERS)

    for m in markers:
        n = _norm_text(m)
        if not n:
            continue
        if len(n) <= 4:
            if re.search(rf"\b{re.escape(n)}\b", blob):
                return True
        elif n in blob:
            return True
    return False


def resolve_source_actionability_rule(
    record: Dict[str, Any],
    titulo: str,
    combined: str,
    *,
    opportunity_strong: bool,
    resultado_strong: bool,
) -> Optional[str]:
    """
    Regras por fonte após oportunidade/resultado global.
    Retorna actionability_type ou None para fallback global.
    """
    fonte = record.get("fonte_normalizada") or record.get("fonte_recurso") or record.get("fonte") or ""
    profile = get_source_actionability_profile(fonte)
    if not profile:
        return None

    # Oportunidade forte explícita vence perfil (exceto resultado forte no título)
    if opportunity_strong and not resultado_strong:
        return None

    # Fonte bloqueada como edital (QST etc.)
    if profile.get("block_as_edital") and not opportunity_strong:
        if source_profile_has_marker(profile, titulo, combined, "portal_generic_titles"):
            return "portal_generico"
        if source_profile_has_marker(profile, titulo, combined, "news_markers"):
            return "noticia"
        default = profile.get("default_if_weak", "desconhecido")
        if default in ("noticia", "sem_oportunidade", "portal_generico"):
            return default
        return "noticia"

    # Portal genérico institucional
    if source_profile_has_marker(profile, titulo, combined, "portal_generic_titles"):
        return "portal_generico"

    # Carreiras / RH
    careers = list(profile.get("careers_markers") or []) + list(CAREERS_MARKERS)
    prof_careers = {**profile, "careers_markers": careers}
    if source_profile_has_marker(prof_careers, titulo, combined, "careers_markers"):
        return "sem_oportunidade"

    # Supplier portal
    if profile.get("kind") == "supplier_portal":
        if source_profile_has_marker(profile, titulo, combined, "supplier"):
            return "portal_util"
        if any(m in _norm_text(titulo) for m in ("supplier", "procurement", "fornecedor")):
            return "portal_util"

    # Portal útil (hubs, linhas de crédito)
    if source_profile_has_marker(profile, titulo, combined, "portal_util_titles"):
        return "portal_util"
    if source_profile_has_marker(profile, titulo, combined, "portal_util_markers"):
        return "portal_util"

    # Eureka / BNB: oportunidade nomeada com marcadores de perfil
    if profile.get("kind") in ("funding_hub", "bank_funding_portal", "grant_like_with_portal"):
        if source_profile_has_marker(profile, titulo, combined, "opportunity_markers"):
            return "oportunidade_sem_prazo"

    # Notícia explícita por fonte
    if source_profile_has_marker(profile, titulo, combined, "news_markers"):
        return "noticia"

    # China: sem evidência forte → manter desconhecido (não forçar ruído)
    if profile.get("keep_desconhecido_without_strong_evidence"):
        if source_profile_has_marker(profile, titulo, combined, "tender_markers"):
            return None
        return None

    return None
