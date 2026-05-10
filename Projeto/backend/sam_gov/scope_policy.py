"""Escopo e classificação local SAM.gov (política em config/sam_gov_scope_policy.json)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_POLICY_PATH = Path(__file__).resolve().parent.parent / "config" / "sam_gov_scope_policy.json"


def load_policy() -> Dict[str, Any]:
    if not _POLICY_PATH.is_file():
        return {}
    data = json.loads(_POLICY_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _norm_blob(*parts: Any) -> str:
    return " ".join(str(p or "") for p in parts).lower()


def _hits(terms: List[str], blob: str) -> int:
    n = 0
    bl = blob.lower()
    for t in terms:
        if not t or not str(t).strip():
            continue
        if str(t).lower().strip() in bl:
            n += 1
    return n


def classify_sam_gov_relevance(opp: Dict[str, Any], policy: Dict[str, Any]) -> str:
    """Devolve high_relevance | medium_relevance | low_relevance | reject_noise."""
    pos_terms = list(policy.get("positive_terms_strong") or [])
    neg_terms = list(policy.get("negative_terms_strong") or [])
    neg_title = list(policy.get("negative_terms_title_only_extra") or [])
    agencies = list(policy.get("priority_agencies_substrings") or [])
    pref_types = list(policy.get("preferred_notice_types_substrings") or [])

    title = str(opp.get("title") or "")
    dept = str(opp.get("department") or "")
    sub = str(opp.get("subTier") or opp.get("subtier") or "")
    office = str(opp.get("office") or "")
    ntype = str(opp.get("type") or "") + " " + str(opp.get("baseType") or "")
    naics = str(opp.get("naicsCode") or "")
    sol = str(opp.get("solicitationNumber") or "")

    blob = _norm_blob(title, dept, sub, office, ntype, naics, sol)
    title_l = title.lower()
    pos = _hits(pos_terms, blob)
    neg = _hits(neg_terms, blob) + _hits(neg_title, title_l)
    agency_pri = any(a.lower() in blob for a in agencies if str(a).strip())
    type_pref = any(p.lower() in ntype.lower() for p in pref_types if str(p).strip())

    rej = (policy.get("relevance_scoring") or {}).get("reject_noise") or {}
    neg_thr = int(rej.get("negative_hits_gte") or 2)
    pos_eq = int(rej.get("positive_hits_eq") or 0)
    if neg >= neg_thr and pos <= pos_eq:
        return "reject_noise"

    if agency_pri:
        if pos >= 1:
            return "high_relevance"
        return "medium_relevance"
    if pos >= 2:
        return "high_relevance"
    if pos >= 1 and type_pref:
        return "medium_relevance"
    if pos >= 1:
        return "medium_relevance"
    return "reject_noise"


def passes_acceptance(opp: Dict[str, Any], link: str, policy: Dict[str, Any]) -> Tuple[bool, str]:
    acc = policy.get("acceptance_rules") or {}
    title = str(opp.get("title") or "").strip()
    dept = str(opp.get("department") or "").strip()
    sub = str(opp.get("subTier") or opp.get("subtier") or "").strip()
    nid = str(opp.get("noticeId") or "").strip()

    if acc.get("require_non_empty_title") and not title:
        return False, "sem_titulo"
    if acc.get("require_notice_detail_link") and "sam.gov/opp/" not in link.lower():
        return False, "link_nao_notice"
    if not nid:
        return False, "sem_notice_id"

    lk = link.lower()
    for subu in acc.get("reject_url_substrings") or []:
        if subu.lower() in lk:
            return False, "url_listagem_ou_hub"

    if acc.get("require_agency_or_department") and not (dept or sub):
        return False, "sem_agencia"

    blob = _norm_blob(title, dept, sub, opp.get("type"), opp.get("naicsCode"))
    pos_terms = list(policy.get("positive_terms_strong") or [])
    pos = _hits(pos_terms, blob)
    if pos < int(acc.get("require_min_positive_hits") or 1):
        return False, "sem_termo_positivo"

    neg_terms = list(policy.get("negative_terms_strong") or [])
    neg_title = list(policy.get("negative_terms_title_only_extra") or [])
    neg = _hits(neg_terms, blob) + _hits(neg_title, title.lower())
    if acc.get("reject_if_strong_negative_dominant"):
        thr = int(acc.get("strong_negative_dominant_min_neg") or 2)
        if neg >= thr and pos == 0:
            return False, "negativo_dominante"

    rel = classify_sam_gov_relevance(opp, policy)
    min_rel = str(acc.get("min_relevance_to_save") or "medium_relevance")
    rank = {"reject_noise": 0, "low_relevance": 1, "medium_relevance": 2, "high_relevance": 3}
    if rank.get(rel, 0) < rank.get(min_rel, 2):
        return False, f"abaixo_{min_rel}"

    return True, ""


def opportunity_dict_to_item(opp: Dict[str, Any], policy: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    notice_id = str(opp.get("noticeId") or "").strip()
    if not notice_id:
        return None

    ui = str(opp.get("uiLink") or "").strip()
    link = ui if ui.startswith("http") else f"https://sam.gov/opp/{notice_id}/view"

    ok, _reason = passes_acceptance(opp, link, policy)
    if not ok:
        return None

    title = str(opp.get("title") or "").strip()[:400]
    dept = str(opp.get("department") or "").strip()
    sub = str(opp.get("subTier") or opp.get("subtier") or "").strip()
    office = str(opp.get("office") or "").strip()
    sol = str(opp.get("solicitationNumber") or "").strip()
    posted = str(opp.get("postedDate") or "").strip()
    deadline = str(opp.get("responseDeadLine") or opp.get("reponseDeadLine") or "").strip()
    ntype = str(opp.get("type") or "").strip()
    base_type = str(opp.get("baseType") or "").strip()
    naics = str(opp.get("naicsCode") or "").strip()
    psc = str(opp.get("classificationCode") or "").strip()
    set_aside = str(opp.get("setAside") or opp.get("typeOfSetAsideDescription") or "").strip()
    set_code = str(opp.get("setAsideCode") or opp.get("typeOfSetAside") or "").strip()
    desc_url = str(opp.get("description") or "").strip()
    pop = opp.get("placeOfPerformance")
    pop_str = ""
    if isinstance(pop, dict):
        pop_str = json.dumps(pop, ensure_ascii=False)[:1200]

    desc_parts = [
        title,
        f"Department: {dept}" if dept else "",
        f"Sub-tier: {sub}" if sub else "",
        f"Office: {office}" if office else "",
        f"Notice type: {ntype}" if ntype else "",
        f"Base type: {base_type}" if base_type else "",
        f"Solicitation number: {sol}" if sol else "",
        f"NAICS: {naics}" if naics else "",
        f"PSC: {psc}" if psc else "",
        f"Set-aside: {set_aside}" if set_aside else "",
        f"Posted: {posted}" if posted else "",
        f"Response deadline: {deadline}" if deadline else "",
        f"Description URL: {desc_url}" if desc_url else "",
        f"Place of performance: {pop_str}" if pop_str else "",
    ]
    descricao = " | ".join(p for p in desc_parts if p).strip()[:8000]

    docs: List[Dict[str, str]] = []
    for u in opp.get("resourceLinks") or []:
        if isinstance(u, str) and u.strip().startswith("http"):
            docs.append({"nome": "attachment", "url": u.strip()[:2000]})

    rel = classify_sam_gov_relevance(opp, policy)

    return {
        "titulo": title,
        "descricao": descricao,
        "link": link,
        "fonte": "SAM.gov",
        "data_publicacao": posted[:10] if posted else None,
        "fim_inscricao": deadline[:10] if deadline and len(deadline) >= 10 else None,
        "situacao": "Em andamento",
        "valor": None,
        "programa": "SAM.gov",
        "acao": "monitoramento_oportunidades_publicas",
        "tipo_recurso": "Contratacao Publica",
        "extras": {
            "pais": "Estados Unidos",
            "idioma_original": "en",
            "origem_portal": "SAM.gov",
            "orgao_contratante": " | ".join(x for x in (dept, sub, office) if x).strip() or "US Federal",
            "origem": link,
            "metodo_extracao": "sam_gov_opportunities_api_v2",
            "sam_gov_notice_id": notice_id,
            "sam_gov_solicitation_number": sol,
            "sam_gov_department": dept,
            "sam_gov_subtier": sub,
            "sam_gov_office": office,
            "sam_gov_notice_type": ntype,
            "sam_gov_base_type": base_type,
            "sam_gov_posted_date": posted,
            "sam_gov_response_deadline": deadline,
            "sam_gov_naics": naics,
            "sam_gov_psc": psc,
            "sam_gov_set_aside": set_aside,
            "sam_gov_set_aside_code": set_code,
            "sam_gov_place_of_performance": pop if isinstance(pop, dict) else {},
            "sam_gov_description_url": desc_url,
            "sam_gov_source_url": link,
            "sam_gov_relevance": rel,
            "documentos": docs,
            "codigo_oportunidade": notice_id,
            "numero_chamada": sol,
            "nivel_sensibilidade": "publico_institucional",
        },
    }
