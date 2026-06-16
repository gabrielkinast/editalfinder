"""
Canonicalizador de links Grants.gov (Backend 10.3A).

Problema: registros Grants.gov com `link` apontando para rotas que abrem
"PAGE NOT FOUND" (ex.: simpler.grants.gov/opportunity/<id> legado,
www.grants.gov/web/grants/view-opportunity.html, /page-not-found, vazio).

Padrão público canônico atual:
    https://www.grants.gov/search-results-detail/<opportunity_id>

Quando não há ID numérico, cair para busca por Funding Opportunity Number:
    https://www.grants.gov/search-grants?keywords=<encoded>

Última opção segura:
    https://www.grants.gov/search-grants

Este módulo é puro (sem rede) e nunca retorna page-not-found, javascript:,
data:, URL não-HTTPS ou domínio fora de grants.gov para fonte Grants.gov.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, quote_plus, urlparse

WWW_DETAIL_BASE = "https://www.grants.gov/search-results-detail"
SEARCH_GRANTS_BASE = "https://www.grants.gov/search-grants"

GRANTS_HOSTS = ("grants.gov",)  # cobre www.grants.gov, api.grants.gov, simpler.grants.gov

# Campos que podem conter um ID numérico interno confiável da oportunidade
NUMERIC_ID_FIELDS = (
    "opportunity_id",
    "opportunityId",
    "opportunityIdNumber",
    "opportunity_number_id",
    "grants_opportunity_id",
    "grants_gov_opp_id",
    "legacy_opp_id",
    "legacy_opportunity_id",
)

# Campos que podem conter o Funding Opportunity Number (não numérico interno)
OPP_NUMBER_FIELDS = (
    "opportunity_number",
    "opportunityNumber",
    "funding_opportunity_number",
    "fundingOpportunityNumber",
    "codigo_oportunidade",
    "numero_chamada",
)

UNSAFE_SCHEMES = ("javascript:", "data:", "vbscript:", "file:")

PAGE_NOT_FOUND_MARKERS = ("page-not-found", "pagenotfound", "404")
LEGACY_ROUTE_MARKERS = ("view-opportunity", "/web/grants")

_NUMERIC_RE = re.compile(r"^\d{1,12}$")


def _norm_str(val: Any) -> str:
    if val is None:
        return ""
    s = str(val).strip()
    if s.lower() in ("", "null", "none", "n/a", "#"):
        return ""
    return s


def _get_extras(record: Dict[str, Any]) -> Dict[str, Any]:
    ex = record.get("extras") if isinstance(record, dict) else None
    return ex if isinstance(ex, dict) else {}


def is_grants_gov_record(record: Dict[str, Any]) -> bool:
    if not isinstance(record, dict):
        return False
    fonte = str(record.get("fonte") or record.get("fonte_recurso") or "").strip().lower()
    if "grants" in fonte:
        return True
    link = str(record.get("link") or "").lower()
    if "grants.gov" in link:
        return True
    ex = _get_extras(record)
    sv = str(ex.get("source_variant") or "").lower()
    return "grants" in sv


def _is_numeric_id(val: Any) -> bool:
    s = _norm_str(val)
    return bool(s) and bool(_NUMERIC_RE.match(s))


def _url_domain_ok(url: str) -> bool:
    """True se URL é https e domínio termina em grants.gov."""
    try:
        p = urlparse(url)
    except Exception:
        return False
    if p.scheme != "https":
        return False
    host = (p.netloc or "").lower()
    return any(host == h or host.endswith("." + h) for h in GRANTS_HOSTS)


def _is_unsafe_link(url: str) -> bool:
    low = url.lower().strip()
    if not low:
        return True
    if any(low.startswith(s) for s in UNSAFE_SCHEMES):
        return True
    return False


def _link_is_page_not_found_or_legacy(url: str) -> bool:
    low = url.lower()
    if any(m in low for m in PAGE_NOT_FOUND_MARKERS):
        return True
    if any(m in low for m in LEGACY_ROUTE_MARKERS):
        return True
    return False


def extract_numeric_id_from_link(url: str) -> str:
    """Extrai ID numérico de rotas conhecidas Grants.gov / Simpler (só domínio grants.gov)."""
    u = _norm_str(url)
    if not u:
        return ""
    try:
        host = (urlparse(u).netloc or "").lower()
    except Exception:
        return ""
    if not any(host == h or host.endswith("." + h) for h in GRANTS_HOSTS):
        return ""
    low = u.lower()
    # ID numérico deve ser o segmento completo (terminado por / ? # ou fim)
    m = re.search(r"/search-results-detail/(\d+)(?:[/?#]|$)", low)
    if m:
        return m.group(1)
    m = re.search(r"/opportunity/(\d+)(?:[/?#]|$)", low)
    if m:
        return m.group(1)
    try:
        q = parse_qs(urlparse(u).query)
        for key in ("oppId", "oppid", "opportunityId", "opportunityid"):
            vals = q.get(key) or []
            if vals and _is_numeric_id(vals[0]):
                return _norm_str(vals[0])
    except Exception:
        pass
    return ""


def _find_numeric_id(record: Dict[str, Any], extras: Dict[str, Any]) -> Tuple[str, str]:
    """Retorna (id, source_field) priorizando campos dedicados, depois o link."""
    for field in NUMERIC_ID_FIELDS:
        for container, prefix in ((record, ""), (extras, "extras.")):
            if _is_numeric_id(container.get(field)):
                return _norm_str(container.get(field)), f"{prefix}{field}"

    # `id` só conta se for fonte Grants.gov e numérico interno confiável
    if _is_numeric_id(record.get("id")):
        return _norm_str(record.get("id")), "id"

    link = _norm_str(record.get("link")) or _norm_str(extras.get("url_detalhe")) or _norm_str(extras.get("legacy_url"))
    from_link = extract_numeric_id_from_link(link)
    if from_link:
        return from_link, "link"
    return "", ""


def _find_opportunity_number(record: Dict[str, Any], extras: Dict[str, Any]) -> Tuple[str, str]:
    for field in OPP_NUMBER_FIELDS:
        for container, prefix in ((record, ""), (extras, "extras.")):
            val = _norm_str(container.get(field))
            if val:
                return val, f"{prefix}{field}"
    return "", ""


def build_detail_url(opportunity_id: str) -> str:
    return f"{WWW_DETAIL_BASE}/{_norm_str(opportunity_id)}"


def build_search_fallback_url(opportunity_number: str) -> str:
    return f"{SEARCH_GRANTS_BASE}?keywords={quote_plus(_norm_str(opportunity_number))}"


def is_safe_grants_link(url: str) -> bool:
    """Link aceitável: https, domínio grants.gov, sem page-not-found."""
    u = _norm_str(url)
    if not u or _is_unsafe_link(u):
        return False
    if not _url_domain_ok(u):
        return False
    if any(m in u.lower() for m in PAGE_NOT_FOUND_MARKERS):
        return False
    return True


def normalize_grants_gov_link(record: Dict[str, Any], *, now: Any = None) -> Dict[str, Any]:
    """
    Resolve o link canônico de um registro Grants.gov.

    Retorna dict com:
      canonical_link, link_status, reason, opportunity_id, opportunity_number,
      source_field, old_link, old_link_invalid.
    """
    base = {
        "canonical_link": None,
        "link_status": "invalid",
        "reason": "",
        "opportunity_id": "",
        "opportunity_number": "",
        "source_field": "",
        "old_link": _norm_str(record.get("link")) if isinstance(record, dict) else "",
        "old_link_invalid": False,
    }
    if not is_grants_gov_record(record):
        base["reason"] = "not_grants_gov_record"
        return base

    extras = _get_extras(record)
    old_link = _norm_str(record.get("link"))
    old_unsafe = bool(old_link) and (_is_unsafe_link(old_link) or not _url_domain_ok(old_link))
    old_pnf = bool(old_link) and _link_is_page_not_found_or_legacy(old_link)
    base["old_link_invalid"] = old_unsafe or old_pnf or not old_link

    numeric_id, id_field = _find_numeric_id(record, extras)
    opp_number, num_field = _find_opportunity_number(record, extras)
    base["opportunity_id"] = numeric_id
    base["opportunity_number"] = opp_number

    if numeric_id:
        base["canonical_link"] = build_detail_url(numeric_id)
        base["link_status"] = "canonical_detail"
        base["source_field"] = id_field
        if id_field == "link" and not base["old_link_invalid"]:
            base["reason"] = "normalized_to_www_search_results_detail"
        else:
            base["reason"] = f"canonical_detail_from_{id_field or 'id'}"
        return base

    if opp_number:
        base["canonical_link"] = build_search_fallback_url(opp_number)
        base["link_status"] = "search_fallback"
        base["source_field"] = num_field
        base["reason"] = f"search_fallback_from_{num_field or 'opportunity_number'}"
        return base

    base["canonical_link"] = SEARCH_GRANTS_BASE
    base["link_status"] = "missing"
    base["reason"] = "no_identifier_search_grants_fallback"
    return base


def apply_link_resolution_to_item(item: Dict[str, Any], *, rewrite_link: str = "if_broken") -> Dict[str, Any]:
    """
    Carimba extras com a resolução e (opcionalmente) reescreve item["link"].

    rewrite_link:
      - "if_broken": só reescreve se o link atual for inseguro/page-not-found/legado
                     ou se houver canonical_detail diferente do link atual.
      - "always": sempre usa canonical_link quando disponível e seguro.
      - "never": apenas carimba extras, não toca no link.
    """
    if not is_grants_gov_record(item):
        return item
    ex = item.get("extras")
    if not isinstance(ex, dict):
        ex = {}
        item["extras"] = ex

    res = normalize_grants_gov_link(item)
    ex["grants_link_status"] = res["link_status"]
    ex["grants_link_reason"] = res["reason"]
    if res["opportunity_id"]:
        ex["grants_opportunity_id"] = res["opportunity_id"]
    if res["opportunity_number"]:
        ex["grants_opportunity_number"] = res["opportunity_number"]
    if res["canonical_link"]:
        ex["grants_canonical_link"] = res["canonical_link"]

    canonical = res["canonical_link"]
    if not canonical or not is_safe_grants_link(canonical):
        return item

    if rewrite_link == "never":
        return item

    old_link = _norm_str(item.get("link"))
    should_rewrite = False
    if rewrite_link == "always":
        should_rewrite = True
    elif rewrite_link == "if_broken":
        if res["old_link_invalid"]:
            should_rewrite = True
        elif res["link_status"] == "canonical_detail" and old_link != canonical:
            # link simpler legado/working → canônico www
            if "simpler.grants.gov" in old_link.lower() or "search-results-detail" in old_link.lower():
                should_rewrite = True

    if should_rewrite and old_link != canonical:
        ex["grants_old_link"] = old_link
        item["link"] = canonical
    return item


# ---------------------------------------------------------------------------
# Auditoria e dry-run (puros, sem rede, sem banco) — Backend 10.3A
# ---------------------------------------------------------------------------

def _record_title(record: Dict[str, Any]) -> str:
    return _norm_str(record.get("titulo") or record.get("title") or record.get("opportunity_title"))


def _record_id_edital(record: Dict[str, Any]) -> Any:
    for key in ("id_edital", "id"):
        val = record.get(key)
        if val not in (None, ""):
            return val
    return None


def classify_link_audit(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classifica o estado do link de um registro Grants.gov (sem reescrever nada).

    audit_status:
      - already_valid: link atual já é seguro e canônico (search-results-detail www)
      - canonical_candidate: dá para gerar search-results-detail/<id>
      - search_fallback_candidate: sem id, mas tem opportunity number
      - missing_identifier: sem id e sem número → só search-grants
      - page_not_found / legacy / unsafe: link atual quebrado
    """
    old_link = _norm_str(record.get("link"))
    res = normalize_grants_gov_link(record)
    low = old_link.lower()

    old_is_pnf = bool(old_link) and any(m in low for m in PAGE_NOT_FOUND_MARKERS)
    old_is_legacy = bool(old_link) and any(m in low for m in LEGACY_ROUTE_MARKERS)
    old_is_unsafe = bool(old_link) and (_is_unsafe_link(old_link) or (not _url_domain_ok(old_link)))
    old_is_canonical_www = bool(
        re.match(r"^https://www\.grants\.gov/search-results-detail/\d+/?$", low)
    )

    audit_status = res["link_status"]
    if old_is_pnf:
        audit_status = "page_not_found"
    elif old_is_legacy:
        audit_status = "legacy_route"
    elif old_is_unsafe:
        audit_status = "unsafe_or_foreign"
    elif old_is_canonical_www and res["link_status"] == "canonical_detail":
        audit_status = "already_valid"
    elif res["link_status"] == "canonical_detail":
        audit_status = "canonical_candidate"
    elif res["link_status"] == "search_fallback":
        audit_status = "search_fallback_candidate"
    elif res["link_status"] == "missing":
        audit_status = "missing_identifier"

    needs_update = bool(
        res["canonical_link"]
        and is_safe_grants_link(res["canonical_link"])
        and _norm_str(res["canonical_link"]) != old_link
    )
    return {
        "id_edital": _record_id_edital(record),
        "titulo": _record_title(record),
        "old_link": old_link,
        "new_link": res["canonical_link"],
        "link_status": res["link_status"],
        "audit_status": audit_status,
        "reason": res["reason"],
        "opportunity_id": res["opportunity_id"],
        "opportunity_number": res["opportunity_number"],
        "source_field": res["source_field"],
        "old_link_invalid": res["old_link_invalid"],
        "needs_update": needs_update,
    }


def audit_grants_links(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Auditoria estrutural de links Grants.gov (sem HTTP)."""
    buckets: Dict[str, List[Dict[str, Any]]] = {
        "already_valid": [],
        "canonical_candidates": [],
        "search_fallback_candidates": [],
        "missing_identifiers": [],
        "invalid_links": [],
    }
    stats = {
        "total_grants": 0,
        "already_valid": 0,
        "canonical_candidates": 0,
        "search_fallback_candidates": 0,
        "missing_identifiers": 0,
        "page_not_found": 0,
        "legacy_route": 0,
        "unsafe_or_foreign": 0,
        "candidates_to_update": 0,
    }
    for rec in records:
        if not is_grants_gov_record(rec):
            continue
        stats["total_grants"] += 1
        a = classify_link_audit(rec)
        st = a["audit_status"]

        if a["needs_update"]:
            stats["candidates_to_update"] += 1

        if st == "already_valid":
            stats["already_valid"] += 1
            buckets["already_valid"].append(a)
            continue
        if st in ("page_not_found", "legacy_route", "unsafe_or_foreign"):
            stats[st] += 1
            buckets["invalid_links"].append(a)
            # também classificamos para onde corrigir
            if a["link_status"] == "canonical_detail":
                buckets["canonical_candidates"].append(a)
            elif a["link_status"] == "search_fallback":
                buckets["search_fallback_candidates"].append(a)
            else:
                buckets["missing_identifiers"].append(a)
            continue
        if st == "canonical_candidate":
            stats["canonical_candidates"] += 1
            buckets["canonical_candidates"].append(a)
        elif st == "search_fallback_candidate":
            stats["search_fallback_candidates"] += 1
            buckets["search_fallback_candidates"].append(a)
        elif st == "missing_identifier":
            stats["missing_identifiers"] += 1
            buckets["missing_identifiers"].append(a)
    return {"stats": stats, "buckets": buckets}


def build_link_fix_candidates(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Dry-run de correção: separa candidatos a update, sem mudança, não corrigíveis
    e alvos duplicados (mesma oportunidade canônica em mais de um registro).

    Como o link tem UNIQUE no banco, dois registros que resolvem para o mesmo
    `search-results-detail/<id>` não podem receber o mesmo link sem colidir.
    Esses casos vão para `duplicate_targets` (revisão manual / dedup), nunca
    para apply automático, e nunca implicam deleção.

    Não escreve no banco.
    """
    candidates_to_update: List[Dict[str, Any]] = []
    no_change: List[Dict[str, Any]] = []
    invalid_unfixable: List[Dict[str, Any]] = []
    duplicate_targets: List[Dict[str, Any]] = []

    grants = [r for r in records if is_grants_gov_record(r)]

    # Quem já "possui" cada link atual (para detectar colisão com outro registro).
    owner_of_link: Dict[str, Any] = {}
    for rec in grants:
        link = _norm_str(rec.get("link"))
        if link:
            owner_of_link.setdefault(link, _record_id_edital(rec))

    assigned: Dict[str, Any] = {}  # new_link -> id_edital que o levará

    for rec in grants:
        a = classify_link_audit(rec)
        new_link = a["new_link"]
        if not new_link or not is_safe_grants_link(new_link):
            invalid_unfixable.append(a)
            continue
        if not a["needs_update"]:
            no_change.append(a)
            assigned.setdefault(new_link, a["id_edital"])
            continue

        owner = owner_of_link.get(new_link)
        clash_existing = owner is not None and owner != a["id_edital"]
        clash_batch = new_link in assigned and assigned[new_link] != a["id_edital"]
        if clash_existing or clash_batch:
            a["duplicate_of_id_edital"] = assigned.get(new_link, owner)
            duplicate_targets.append(a)
            continue

        assigned[new_link] = a["id_edital"]
        candidates_to_update.append(a)

    stats = {
        "total_grants": len(grants),
        "candidates_to_update": len(candidates_to_update),
        "no_change": len(no_change),
        "invalid_unfixable": len(invalid_unfixable),
        "duplicate_targets": len(duplicate_targets),
        "canonical_detail_updates": sum(
            1 for c in candidates_to_update if c["link_status"] == "canonical_detail"
        ),
        "search_fallback_updates": sum(
            1 for c in candidates_to_update if c["link_status"] == "search_fallback"
        ),
    }
    return {
        "stats": stats,
        "candidates_to_update": candidates_to_update,
        "no_change": no_change,
        "invalid_unfixable": invalid_unfixable,
        "duplicate_targets": duplicate_targets,
    }
