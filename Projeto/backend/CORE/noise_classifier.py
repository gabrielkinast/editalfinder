"""
Classificador de acionabilidade e ruído (Backend 9–10.1).

Ordem de prioridade (10.1):
  1. Oportunidade forte  2. Resultado forte  3. Retificação  4. Portal útil
  5. Portal genérico  6. Evento  7. Notícia  8. Documento auxiliar  9. Fallback

- noise_type só quando is_noise=True (invariante).
- Marcadores fortes de oportunidade vencem resultado/evento fracos.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from source_actionability_profiles import resolve_source_actionability_rule
from source_quality_profiles import (
    classification_bucket,
    get_source_quality_profile,
    match_source_title_rule,
    source_quality_flags,
)

Confidence = str

# --- Oportunidade forte (título prioritário; EN explícito no título) ---
_OPPORTUNITY_STRONG: List[str] = [
    r"\bchamada\s+p[uú]blica\b",
    r"\bchamada\s+publica\b",
    r"\bchamada\s+cnpq\b",
    r"\bchamada\s+cnpq/",
    r"\bchamada\s+mcti\b",
    r"\bchamada\s+fndct\b",
    r"\bchamada\s+de\s+clima\b",
    r"\bchamada\s+regional\b",
    r"\bchamada\s+nacional\b",
    r"\bedital\b",
    r"\bsele[cç][aã]o\s+p[uú]blica\b",
    r"\bselecao\s+publica\b",
    r"\bsele[cç][aã]o\s+de\s+fundos\b",
    r"\bselecao\s+de\s+fundos\b",
    r"\bsubven[cç][aã]o\b",
    r"\bsubvencao\b",
    r"\baux[ií]lio\b",
    r"\bauxilio\b",
    r"\bapoio\s+a\s+projetos\b",
    r"\bprograma\s+de\s+apoio\b",
    r"\bfinanciamento\b",
    r"\bfomento\b",
    r"\bbolsa\b",
    r"\bgrant\b",
    r"\bfunding\s+opportunit",
    r"\bcall\s+for\s+(proposals|applications|projects|market)\b",
    r"\bpremio\b",
    r"\bpr[eê]mio\b",
    r"\blicita[cç][aã]o\b",
    r"\blicitacao\b",
    r"\bdispensa\s+de\s+licita[cç][aã]o\b",
    r"\bdispensa\s+de\s+licitacao\b",
    r"\bpreg[aã]o\b",
    r"\bpregao\b",
    r"\bDE-FOA-\d+\b",
    r"\bconcurso\s+p[uú]blico\b",
    r"\binscri[cç][oõ]es\s+abertas\b",
    r"\brequest\s+for\s+proposals\b",
    r"\bRFP\b",
    r"\bnotice\s+of\s+funding\s+opportunit",
    r"\bnofo\b",
    r"\bbroad\s+agency\s+announcement\b",
    r"\bbaa\b",
    r"\bsolicitation\b",
    r"\btender\b",
    r"\bprocurement\s+notice\b",
    r"\bfunding\s+call\b",
    r"\bresearch\s+opportunit",
    r"\bapplication\s+deadline\b",
]

# EN explícito no corpo — só com título substantivo (evita desconhecido→oportunidade frágil)
_OPPORTUNITY_COMBINED_EXPLICIT: List[str] = [
    r"\bnotice\s+of\s+funding\s+opportunit",
    r"\bcall\s+for\s+proposals\b",
    r"\bcall\s+for\s+applications\b",
    r"\bsolicitation\s+number\b",
    r"\bDE-FOA-\d+\b",
    r"\bNOFO-\d+",
    r"\bfunding\s+opportunity\s+number\b",
]

_GRANT_LIKE_SOURCE_HINTS = (
    "grants.gov",
    "grants gov",
    "nsf",
    "ukri",
    "horizon",
    "doe",
    "arpa",
    "sbir",
    "sttr",
    "nih",
    "eic",
    "erc",
)

# Resultado: apenas marcadores explícitos (Backend 10.1A)
_RESULTADO_STRONG: List[str] = [
    r"\bresultado\s+final\b",
    r"\bresultado\s+preliminar\b",
    r"\bresultados?\s+final\b",
    r"[-–]\s*resultado\s+final\b",
    r"\bhomologa[cç][aã]o\b",
    r"\bhomologacao\b",
    r"\blista\s+(de\s+)?selecionados\b",
    r"\bclassifica[cç][aã]o\s+final\b",
    r"\bclassificacao\s+final\b",
    r"\bjulgamento\s+final\b",
    r"\bdivulga[cç][aã]o\s+do\s+resultado\b",
    r"\bdivulgacao\s+do\s+resultado\b",
    r"\bresultado\s+da\s+sele[cç][aã]o\b",
    r"\bresultado\s+da\s+selecao\b",
    r"^\s*resultado\s*[-–]",
    r"^\s*resultado\b",
    r"\bresultado\s*[-–]\s*sele[cç]",
    r"\bpreliminary\s+result\b",
    r"\bfinal\s+result\b",
    r"\bawardees\b",
    r"\bselected\s+projects\b",
    r"\bselected\s+applicants\b",
    r"\baward\s+notice\b",
    r"\bwinners\s+announced\b",
]

_RETIFICACAO_STRONG: List[str] = [
    r"\bretifica[cç][aã]o\b",
    r"\berrata\b",
    r"\baditivo\b",
]

_PORTAL_UTIL_PHRASES = (
    "funding opportunities",
    "open funding opportunities",
    "find a funding opportunity",
    "licitacoes e contratos",
    "licitações e contratos",
    "editais e programas",
    "pagina de editais",
    "página de editais",
    "atividades financiadas",
    "financiamento de projetos",
    "credito para poder publico",
    "crédito para poder público",
    "eic accelerator",
    "eic pathfinder",
    "capes",
)

_PORTAL_GENERIC_EXACT = frozenset(
    {
        "english",
        "eventos",
        "noticias",
        "notícias",
        "home",
        "portal",
        "privacidade",
        "atuacao",
        "atuação",
    }
)

_PORTAL_GENERIC_PHRASES = (
    "quem somos",
    "sobre o ",
    "sobre a ",
    "sala de imprensa",
    "nossa essencia",
    "nossa essência",
    "protecao de dados",
    "proteção de dados",
    "data resources",
)

_EVENTO_STRONG: List[str] = [
    r"\bwebinar\b",
    r"\bworkshop\b",
    r"\bsemin[aá]rio\b",
    r"\bpalestra\b",
    r"\bconfer[eê]ncia\b",
    r"\binscri[cç][aã]o\s+para\s+evento\b",
]

_NOTICIA_STRONG: List[str] = [
    r"\bnot[ií]cia\b",
    r"/noticias?/",
    r"/news/",
    r"\bpress\s+release\b",
    r"\bsala\s+de\s+imprensa\b",
]


def _norm(s: Any) -> str:
    if s is None:
        return ""
    t = str(s).strip().lower()
    t = unicodedata.normalize("NFKD", t)
    return "".join(c for c in t if not unicodedata.combining(c))


def _titulo_norm(record: Dict[str, Any]) -> str:
    return _norm(record.get("titulo") or "")


def _text_blob(record: Dict[str, Any]) -> str:
    parts = [record.get("titulo"), record.get("descricao"), record.get("resumo")]
    return _norm(" ".join(str(p) for p in parts if p))


def _link_blob(record: Dict[str, Any]) -> str:
    for k in ("link", "url", "link_oficial", "site", "url_edital"):
        v = record.get(k)
        if v:
            return _norm(str(v))
    return ""


def _any_pattern(text: str, patterns: List[str]) -> bool:
    return any(re.search(p, text, re.I) for p in patterns)


def _has_structured_deadline(record: Dict[str, Any]) -> bool:
    from deadline_normalizer import has_useful_deadline

    return has_useful_deadline(record)


def _link_invalid(record: Dict[str, Any]) -> bool:
    link = ""
    for k in ("link", "url", "link_oficial"):
        if record.get(k):
            link = str(record.get(k)).strip()
            break
    if not link or link in ("#", "-", "null", "None"):
        return True
    try:
        p = urlparse(link)
        return not (p.scheme and p.netloc)
    except Exception:
        return True


def _is_grant_like_source(record: Optional[Dict[str, Any]]) -> bool:
    if not record:
        return False
    fonte = _norm(record.get("fonte_recurso") or record.get("fonte") or "")
    return any(hint in fonte for hint in _GRANT_LIKE_SOURCE_HINTS)


def has_opportunity_strong(
    titulo: str,
    combined: str,
    record: Optional[Dict[str, Any]] = None,
) -> bool:
    """Marcadores fortes de oportunidade — preferir título; EN explícito com evidência."""
    profile = get_source_quality_profile(record or {})
    if _title_is_portal_hub_only(titulo, profile):
        return False
    if _any_pattern(titulo, _OPPORTUNITY_STRONG):
        return True
    if re.search(r"^chamada\s+", titulo, re.I) and len(titulo) > 12:
        return True
    if re.search(r"\bchamada\s+.+\bn[oº°]\s*\d", titulo, re.I):
        return True
    # Corpo: só padrões EN inequívocos e título com substância mínima
    if len(titulo) >= 8 and _any_pattern(f"{titulo} {combined[:800]}", _OPPORTUNITY_COMBINED_EXPLICIT):
        return True
    # Fontes de grants: título EN típico (Grants.gov etc.)
    if _is_grant_like_source(record) and len(titulo) >= 6:
        if _any_pattern(titulo, [r"\bfunding\s+opportunit", r"\bgrant\b", r"\bnofo\b", r"\bsolicitation\b"]):
            return True
    return False


def has_resultado_strong(
    titulo: str,
    combined: str,
    record: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Resultado só com marcador explícito no título quando há oportunidade forte no título.
    Texto de apoio (descrição/PDF) com 'resultado' não derruba chamada pública real.
    """
    if _any_pattern(titulo, _RESULTADO_STRONG):
        return True
    if has_opportunity_strong(titulo, combined, record):
        return False
    return _any_pattern(combined, _RESULTADO_STRONG)


def _has_retificacao_strong(combined: str) -> bool:
    return _any_pattern(combined, _RETIFICACAO_STRONG)


def _portal_util_match(titulo: str, profile: Dict[str, Any]) -> bool:
    for phrase in _PORTAL_UTIL_PHRASES:
        if phrase in titulo:
            return True
    for util in profile.get("portal_util_titles") or []:
        if _norm(util) in titulo:
            return True
    for pat in profile.get("portal_util_patterns") or []:
        if _norm(pat) in titulo:
            return True
    if re.search(r"\bfunding\s+opportunit", titulo, re.I):
        return True
    if "financiamento" in titulo and ("banco" in titulo or "credito" in titulo):
        return True
    return False


def _title_is_portal_hub_only(titulo: str, profile: Dict[str, Any]) -> bool:
    """
    Página índice de oportunidades (ex.: 'Open funding opportunities'), não chamada específica.
    Vence marcador fraco 'funding opportunity' em oportunidade forte.
    """
    if not _portal_util_match(titulo, profile):
        return False
    if re.search(r"\bchamada\s+.+\bn[oº°]\s*\d", titulo, re.I):
        return False
    if re.search(r"\bedital\s+n[oº°]?\s*\d", titulo, re.I):
        return False
    if re.search(r"\bchamada\s+p[uú]blica\b", titulo, re.I) and len(titulo) > 35:
        return False
    if re.search(r"\bprograma\b.+\b(19|20)\d{2}\b", titulo, re.I):
        return False
    if re.search(r"\bDE-FOA-\d+\b", titulo, re.I):
        return False
    # Oportunidade nomeada (Grants.gov: "Funding Opportunity: …") — não é hub
    if re.search(r"\bfunding\s+opportunit\s*:", titulo, re.I):
        return False
    if re.search(r"\bfunding\s+opportunit", titulo, re.I) and len(titulo) > 40:
        return False
    if re.search(r"\bgrant\b", titulo, re.I) and len(titulo) > 25:
        return False
    if re.search(r"\bnofo\b", titulo, re.I):
        return False
    return True


def _portal_generic_match(titulo: str, combined: str, profile: Dict[str, Any]) -> bool:
    for blocked in profile.get("blocklist_titles") or []:
        bt = _norm(blocked)
        if titulo == bt or titulo.startswith(bt + " ") or titulo.endswith(" " + bt):
            return True
        if len(titulo) < 60 and bt in titulo:
            return True
    if titulo in _PORTAL_GENERIC_EXACT:
        return True
    for phrase in _PORTAL_GENERIC_PHRASES:
        if phrase in titulo:
            return True
    if re.search(r"\bsobre\b", titulo, re.I) and len(titulo.split()) <= 8:
        return True
    return False


def _evento_institutional(
    titulo: str,
    combined: str,
    record: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Evento real (webinar/seminário), não 'promoção de eventos' dentro de chamada.
    """
    if has_opportunity_strong(titulo, combined, record):
        if re.search(r"\bchamada\b", titulo, re.I) and re.search(
            r"\b(aux[ií]lio|promocao|programa)\b", titulo, re.I
        ):
            return False
        if _any_pattern(titulo, [r"^\s*webinar\b", r"^\s*semin[aá]rio\b", r"^\s*workshop\b"]):
            return True
        return False
    if titulo in ("evento", "eventos", "webinar", "seminario", "seminário"):
        return titulo != "eventos"
    return _any_pattern(titulo, _EVENTO_STRONG) or _any_pattern(combined, _EVENTO_STRONG)


def _decide_actionability_type(
    record: Dict[str, Any],
    *,
    titulo: str,
    combined: str,
    profile: Dict[str, Any],
) -> str:
    """Pipeline 10.1 — oportunidade forte antes de resultado/evento."""
    if re.search(r"\bDE-FOA-\d+\b", record.get("titulo") or "", re.I):
        return "oportunidade_principal" if _has_structured_deadline(record) else "oportunidade_sem_prazo"

    opp = has_opportunity_strong(titulo, combined, record)
    res = has_resultado_strong(titulo, combined, record)

    source_rule = match_source_title_rule(record, profile)
    if source_rule == "portal_generico" and opp:
        source_rule = None
    if source_rule == "portal_util" and opp and res:
        source_rule = None
    if source_rule and not opp:
        return source_rule

    # 4 antecipado: hub de portal (antes de 'funding opportunity' virar oportunidade)
    if _title_is_portal_hub_only(titulo, profile):
        return "portal_util"

    # 1–2: Oportunidade vs resultado (contextual)
    if opp and res:
        return "resultado"
    if res:
        return "resultado"
    if opp:
        return "oportunidade_principal" if _has_structured_deadline(record) else "oportunidade_sem_prazo"

    # 3: Retificação
    if _has_retificacao_strong(combined):
        return "retificacao"

    # 3b: Perfil por fonte (10.1C)
    profile_rule = resolve_source_actionability_rule(
        record,
        titulo,
        combined,
        opportunity_strong=opp,
        resultado_strong=res,
    )
    if profile_rule:
        return profile_rule

    # 4: Portal útil (não competir com chamada já resolvida)
    if _portal_util_match(titulo, profile):
        return "portal_util"

    # 5: Portal genérico
    if _portal_generic_match(titulo, combined, profile):
        return "portal_generico"

    # 6: Evento institucional
    if _evento_institutional(titulo, combined, record):
        return "evento"

    # 7: Notícia
    if _any_pattern(combined, _NOTICIA_STRONG) and not opp:
        return "noticia"

    # 8: Documento auxiliar leve
    if re.search(r"\b(comunicado|anexo|ata)\b", combined, re.I):
        return "documento_auxiliar"

    if _link_invalid(record):
        return "sem_oportunidade"

    if len(titulo) < 4:
        return "sem_oportunidade"

    return "desconhecido"


def _derive_is_noise(actionability_type: str, *, link_bad: bool) -> bool:
    """
    Ruído provável (10.1): apenas conteúdo sem valor de oportunidade/portal útil/doc derivado.
    """
    if actionability_type in (
        "oportunidade_principal",
        "oportunidade_sem_prazo",
        "portal_util",
        "resultado",
        "retificacao",
        "documento_auxiliar",
        "evento",
    ):
        return False
    if actionability_type in ("portal_generico", "noticia", "sem_oportunidade", "pagina_institucional"):
        return True
    if actionability_type == "desconhecido":
        return False
    return False


def _noise_type_when_is_noise(actionability_type: str) -> Optional[str]:
    mapping = {
        "portal_generico": "portal",
        "pagina_institucional": "portal",
        "noticia": "noticia",
        "sem_oportunidade": "sem_oportunidade",
        "desconhecido": "outro",
    }
    return mapping.get(actionability_type, "outro")


def classify_noise(record: Dict[str, Any]) -> Dict[str, Any]:
    titulo = _titulo_norm(record)
    combined = f"{_text_blob(record)} {_link_blob(record)}"
    profile = get_source_quality_profile(record)

    actionability_type = _decide_actionability_type(
        record, titulo=titulo, combined=combined, profile=profile
    )

    link_bad = _link_invalid(record)
    is_noise = _derive_is_noise(actionability_type, link_bad=link_bad)
    noise_type = _noise_type_when_is_noise(actionability_type) if is_noise else None

    is_actionable = actionability_type in ("oportunidade_principal", "oportunidade_sem_prazo")
    opp_strong = has_opportunity_strong(titulo, combined, record)
    res_strong = has_resultado_strong(titulo, combined, record)
    actionability_norm = round(min(1.0, 0.65 + (0.35 if _has_structured_deadline(record) else 0.0)), 3) if is_actionable else 0.0

    bucket = classification_bucket(actionability_type, is_noise)

    quality_flags: List[str] = list(source_quality_flags(record, profile))
    review_reasons: List[str] = []

    if link_bad:
        quality_flags.append("link_invalido")
    if actionability_type == "oportunidade_sem_prazo":
        quality_flags.append("oportunidade_sem_prazo")
    if actionability_type == "portal_util":
        quality_flags.append("portal_util")

    if opp_strong and actionability_type == "resultado":
        review_reasons.append("possivel_falso_positivo_resultado")
    if res_strong and actionability_type in ("oportunidade_principal", "oportunidade_sem_prazo"):
        review_reasons.append("possivel_falso_negativo_resultado")

    confidence: Confidence = "media"
    if is_actionable and opp_strong:
        confidence = "alta"
    elif actionability_type in ("resultado", "portal_generico", "portal_util") and not review_reasons:
        confidence = "alta"
    elif review_reasons or actionability_type == "desconhecido":
        confidence = "baixa"

    noise_score = 0.0
    if is_noise:
        noise_score = round(min(1.0, 0.5 + (0.1 if actionability_type == "sem_oportunidade" else 0)), 3)

    return {
        "actionability_type": actionability_type,
        "classification_bucket": bucket,
        "noise_score": noise_score,
        "is_noise": is_noise,
        "noise_type": noise_type,
        "is_actionable_opportunity": is_actionable,
        "actionability_score": actionability_norm,
        "quality_flags": sorted(set(quality_flags)),
        "review_reasons": sorted(set(review_reasons)),
        "confidence": confidence,
        "_scores_debug": {
            "opportunity_strong": opp_strong,
            "resultado_strong": res_strong,
        },
    }
