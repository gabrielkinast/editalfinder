"""
Perfis de qualidade por fonte (Backend 9–10.1C) — allowlist/blocklist e flags.

Não altera crawlers nesta fase.
"""
from __future__ import annotations

import unicodedata
from typing import Any, Dict, List, Optional

from source_actionability_profiles import (
    get_source_actionability_profile,
    normalize_source_name,
)

SOURCE_QUALITY_PROFILES: Dict[str, Dict[str, Any]] = {
    "Fundação Araucária": {
        "deadline_often_in_pdf": True,
        "requires_pdf_text": True,
        "known_noise_patterns": ["resultado", "homologação", "retificação", "errata"],
    },
    "Fundacao Araucaria": {
        "deadline_often_in_pdf": True,
        "requires_pdf_text": True,
        "known_noise_patterns": ["resultado", "homologação", "retificação"],
    },
    "China International Tendering": {
        "requires_detail_page": True,
        "detail_blocked_risk": True,
        "known_noise_patterns": ["news", "announcement"],
    },
    "Grants.gov": {
        "deadline_field": "close_date",
        "forecast_without_deadline": True,
        "known_noise_patterns": ["forecast", "archive"],
        "grant_opportunity_hints": True,
    },
    "FAPESC": {
        "known_noise_patterns": ["resultado", "homologação", "retificação", "comunicado"],
    },
    "FINEP": {
        "known_noise_patterns": ["resultado", "homologação", "retificação", "ata"],
    },
    "CNPq": {
        "known_noise_patterns": ["resultado", "homologação", "retificação"],
    },
    "BNDES": {
        "known_noise_patterns": ["notícia", "comunicado", "resultado"],
    },
    "BDMG": {
        "blocklist_titles": [
            "Sobre o BDMG",
            "Notícias",
            "Eventos",
            "Sala de Imprensa",
            "Atuação",
            "Nossa Essência",
            "Privacidade",
            "English",
        ],
    },
    "Banco de Desenvolvimento de Minas Gerais": {
        "blocklist_titles": [
            "Sobre o BDMG",
            "Notícias",
            "Eventos",
            "Sala de Imprensa",
        ],
    },
    "BNB": {
        "portal_util_patterns": ["atividades financiadas", "linha de credito", "linha de crédito"],
        "not_event_generic": ["atividades financiadas", "fruticultura"],
    },
    "Banco do Nordeste": {
        "portal_util_patterns": ["atividades financiadas"],
        "not_event_generic": ["atividades financiadas"],
    },
    "EIC": {
        "portal_util_titles": [
            "EIC Accelerator",
            "EIC Pathfinder",
            "EIC Transition",
            "Funding opportunities",
        ],
    },
    "European Innovation Council": {
        "portal_util_titles": ["EIC Accelerator", "EIC Pathfinder", "EIC Transition"],
    },
    "DOE ARPA-E": {
        "opportunity_id_patterns": [r"DE-FOA-\d+"],
        "force_opportunity_principal": True,
    },
    "ARPA-E": {
        "opportunity_id_patterns": [r"DE-FOA-\d+"],
        "force_opportunity_principal": True,
    },
    "DoD SBIR": {
        "portal_util_titles": ["Funding Opportunities", "DoD SBIR/STTR Funding Opportunities"],
        "blocklist_titles": ["Data Resources"],
    },
    "SBIR": {
        "portal_util_titles": ["Funding Opportunities"],
        "blocklist_titles": ["Data Resources"],
    },
    "CAPES": {
        "portal_util_titles": ["CAPES Editais e Programas", "Editais e Programas", "Pagina de Editais"],
    },
    "Banco do Nordeste": {
        "portal_util_patterns": ["atividades financiadas", "financiamento de projetos", "credito para poder"],
    },
}


def _norm_title(s: Any) -> str:
    if s is None:
        return ""
    t = str(s).strip().lower()
    t = unicodedata.normalize("NFKD", t)
    return "".join(c for c in t if not unicodedata.combining(c))


def _norm_fonte_key(fonte: Optional[str]) -> str:
    if not fonte:
        return ""
    return str(fonte).strip()


def get_source_quality_profile(record: Dict[str, Any]) -> Dict[str, Any]:
    fonte = (
        record.get("fonte_normalizada")
        or record.get("fonte_recurso")
        or record.get("fonte")
        or ""
    )
    key = _norm_fonte_key(fonte)
    merged: Dict[str, Any] = {}
    if key in SOURCE_QUALITY_PROFILES:
        merged = dict(SOURCE_QUALITY_PROFILES[key])
    else:
        for name, profile in SOURCE_QUALITY_PROFILES.items():
            nl, nn = name.lower(), key.lower()
            if nl in nn or nn in nl:
                merged = dict(profile)
                break

    action = get_source_actionability_profile(fonte)
    if action:
        merged = {**merged, **action}
        block = list(merged.get("blocklist_titles") or [])
        for t in action.get("portal_generic_titles") or []:
            if t not in block:
                block.append(t)
        if block:
            merged["blocklist_titles"] = block
        util_pats = list(merged.get("portal_util_patterns") or [])
        for m in action.get("portal_util_markers") or []:
            if m not in util_pats:
                util_pats.append(m)
        if util_pats:
            merged["portal_util_patterns"] = util_pats
        util_titles = list(merged.get("portal_util_titles") or [])
        for t in action.get("portal_util_titles") or []:
            if t not in util_titles:
                util_titles.append(t)
        if util_titles:
            merged["portal_util_titles"] = util_titles

    merged["source_canonical"] = normalize_source_name(fonte)
    return merged


def match_source_title_rule(record: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Retorna actionability_type sugerido por regra de fonte, ou None.
    """
    prof = profile if profile is not None else get_source_quality_profile(record)
    titulo = _norm_title(record.get("titulo"))
    if not titulo:
        return None

    for blocked in prof.get("blocklist_titles") or []:
        bt = _norm_title(blocked)
        if titulo == bt or titulo.startswith(bt) or bt in titulo:
            return "portal_generico"

    for util in prof.get("portal_util_titles") or []:
        if _norm_title(util) in titulo or titulo == _norm_title(util):
            return "portal_util"

    for pat in prof.get("portal_util_patterns") or []:
        if _norm_title(pat) in titulo:
            return "portal_util"

    if prof.get("force_opportunity_principal"):
        import re

        for pat in prof.get("opportunity_id_patterns") or []:
            if re.search(pat, record.get("titulo") or "", re.I):
                return "oportunidade_principal"
        if re.search(r"DE-FOA-\d+", record.get("titulo") or "", re.I):
            return "oportunidade_principal"

    return None


def source_quality_flags(record: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> List[str]:
    prof = profile if profile is not None else get_source_quality_profile(record)
    flags: List[str] = []
    if prof.get("deadline_often_in_pdf"):
        flags.append("fonte_prazo_em_pdf")
    if prof.get("requires_detail_page"):
        flags.append("fonte_requer_pagina_detalhe")
    if prof.get("detail_blocked_risk"):
        flags.append("fonte_risco_detalhe_bloqueado")
    if prof.get("forecast_without_deadline"):
        flags.append("fonte_forecast_sem_close_date")
    if match_source_title_rule(record, prof):
        flags.append("fonte_regra_titulo")
    return flags


def classification_bucket(actionability_type: str, is_noise: bool) -> str:
    """
    Bucket agregado para relatórios (Backend 10.1).

    ruido_provavel no relatório = is_noise=True (não inclui resultado/portal_util/doc auxiliar).
    """
    at = actionability_type or "desconhecido"
    if at in ("oportunidade_principal", "oportunidade_sem_prazo"):
        return "oportunidade_acionavel"
    if at == "portal_util":
        return "portal_util"
    if at in ("documento_auxiliar", "retificacao", "resultado"):
        return "documento_auxiliar"
    if at in ("portal_generico", "noticia", "evento", "pagina_institucional", "sem_oportunidade"):
        return "nao_aplicavel"
    if is_noise:
        return "ruido_provavel"
    return "desconhecido"
