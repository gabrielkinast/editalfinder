"""
Simpler.Grants.gov — cliente, URLs canônicas e mapeamento para o pipeline EditalFinder.

- Listagem: API Simpler (com X-API-Key) ou fallback api.grants.gov search2 (sem chave).
- Link canônico: https://simpler.grants.gov/opportunity/{legacy_id|uuid}
- Não usa view-opportunity.html como link principal.
"""
from __future__ import annotations

import os
import re
import time
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

LEGACY_SEARCH2_URL = "https://api.grants.gov/v1/api/search2"
LEGACY_FETCH_OPP_URL = "https://api.grants.gov/v1/api/fetchOpportunity"
SIMPLER_API_BASE = "https://api.simpler.grants.gov"
SIMPLER_SEARCH_PATH = "/v1/opportunities/search"
SIMPLER_PUBLIC_BASE = "https://simpler.grants.gov"
SIMPLER_ROBOTS_URL = f"{SIMPLER_PUBLIC_BASE}/robots.txt"

DEFAULT_USER_AGENT = "EditalFinderBot/1.0 (+public institutional monitoring; contact: editalfinder)"
DEFAULT_SLEEP_SEC = 0.35
DEFAULT_PAGE_SIZE = 25

SOURCE_VARIANT = "simpler_grants_gov"
LEGACY_SOURCE_VARIANT = "grants_legacy_view_opportunity"

STATUS_COLLECT = frozenset({"posted", "forecasted"})
STATUS_HISTORIC = frozenset({"closed", "archived"})

# Rate limit documentado: 60 req/min — usamos ~2 req/s máx no cliente
RATE_LIMIT_SLEEP = float(os.getenv("SIMPLER_GRANTS_SLEEP_SEC", str(DEFAULT_SLEEP_SEC)))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get_api_key() -> str:
    return (
        os.getenv("SIMPLER_GRANTS_API_KEY", "").strip()
        or os.getenv("EDITALFINDER_SIMPLER_GRANTS_API_KEY", "").strip()
    )


def _session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "POST"]),
    )
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.headers.update(
        {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )
    return s


def build_canonical_opportunity_url(
    *,
    opportunity_id: Optional[str] = None,
    legacy_opp_id: Optional[str | int] = None,
) -> str:
    """URL pública Simpler; aceita UUID ou id numérico legado (redirect server-side)."""
    if opportunity_id and str(opportunity_id).strip():
        oid = str(opportunity_id).strip()
        return f"{SIMPLER_PUBLIC_BASE}/opportunity/{oid}"
    if legacy_opp_id is not None and str(legacy_opp_id).strip():
        return f"{SIMPLER_PUBLIC_BASE}/opportunity/{str(legacy_opp_id).strip()}"
    return f"{SIMPLER_PUBLIC_BASE}/search?page=1"


def build_legacy_view_url(legacy_opp_id: str | int) -> str:
    return (
        f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={legacy_opp_id}"
    )


def _parse_us_date(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    if re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return s[:10]
    for fmt in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(s[:10], fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _status_prazo_from_row(
    opp_status: str,
    close_iso: Optional[str],
) -> str:
    st = (opp_status or "").strip().lower()
    if st == "forecasted":
        return "previsto"
    if st in STATUS_HISTORIC:
        return "encerrado"
    if close_iso:
        try:
            close_d = date.fromisoformat(close_iso[:10])
            if close_d < date.today():
                return "encerrado"
        except ValueError:
            pass
        return "aberto"
    if st == "posted":
        return "aberto"
    return "aberto"


def curadoria_front_for_row(opp_status: str, close_iso: Optional[str]) -> Dict[str, Any]:
    st = (opp_status or "").strip().lower()
    if st in STATUS_HISTORIC:
        return {
            "visibility": "hidden_historical",
            "reason": f"grants_simpler_status_{st}",
            "confidence": "alta",
        }
    if close_iso:
        try:
            if date.fromisoformat(close_iso[:10]) < date.today():
                return {
                    "visibility": "hidden_expired",
                    "reason": "grants_simpler_close_date_passed",
                    "confidence": "alta",
                }
        except ValueError:
            pass
    if st in STATUS_COLLECT:
        if st == "forecasted" or not close_iso:
            if not close_iso:
                return {
                    "visibility": "review_missing_deadline",
                    "reason": "grants_simpler_forecasted_or_no_close",
                    "confidence": "media",
                }
        return {
            "visibility": "visible_current",
            "reason": f"grants_simpler_status_{st}",
            "confidence": "alta",
        }
    return {
        "visibility": "review_missing_deadline",
        "reason": "grants_simpler_unknown_status",
        "confidence": "baixa",
    }


def map_simpler_api_hit(row: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza item da API Simpler search → dict interno."""
    legacy_id = row.get("legacy_opportunity_id") or row.get("legacy_id")
    opp_uuid = row.get("opportunity_id")
    opp_num = row.get("opportunity_number") or ""
    posted = _parse_us_date(row.get("post_date"))
    close = _parse_us_date(row.get("close_date"))
    status = str(row.get("opportunity_status") or "").lower()
    agency = row.get("agency_name") or row.get("top_level_agency_name") or ""
    title = str(row.get("opportunity_title") or row.get("title") or "").strip()
    link = build_canonical_opportunity_url(
        opportunity_id=opp_uuid,
        legacy_opp_id=legacy_id,
    )
    return {
        "titulo": title,
        "opportunity_number": opp_num,
        "agency": agency,
        "agency_code": row.get("agency_code"),
        "posted_date": posted,
        "close_date": close,
        "opportunity_status": status,
        "funding_instrument": row.get("funding_instrument"),
        "category": row.get("funding_category"),
        "eligibility": row.get("applicant_types"),
        "award_ceiling": row.get("award_ceiling"),
        "award_floor": row.get("award_floor"),
        "summary": row.get("summary") or row.get("description"),
        "legacy_opp_id": str(legacy_id) if legacy_id is not None else None,
        "opportunity_id": str(opp_uuid) if opp_uuid else None,
        "link": link,
        "source_url": link,
        "opp_status_raw": status,
    }


def map_legacy_search2_hit(row: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza oppHit do api.grants.gov search2."""
    legacy_id = row.get("id") or row.get("opportunityId")
    opp_num = row.get("number") or row.get("fundingOpportunityNumber") or ""
    title = str(row.get("title") or row.get("opportunityTitle") or "").strip()
    agency = row.get("agency") or row.get("agencyName") or ""
    status = str(row.get("oppStatus") or "").lower()
    posted = _parse_us_date(row.get("openDate") or row.get("postDate"))
    close = _parse_us_date(row.get("closeDate") or row.get("closeDateFormatted"))
    link = build_canonical_opportunity_url(legacy_opp_id=legacy_id)
    return {
        "titulo": title,
        "opportunity_number": opp_num,
        "agency": agency,
        "agency_code": row.get("agencyCode"),
        "posted_date": posted,
        "close_date": close or None,
        "opportunity_status": status,
        "funding_instrument": row.get("docType"),
        "category": None,
        "eligibility": row.get("applicantTypes"),
        "award_ceiling": row.get("awardCeiling"),
        "award_floor": row.get("awardFloor"),
        "summary": None,
        "legacy_opp_id": str(legacy_id) if legacy_id is not None else None,
        "opportunity_id": None,
        "link": link,
        "source_url": link,
        "opp_status_raw": status,
    }


def build_pipeline_item(
    mapped: Dict[str, Any],
    *,
    collected_at: Optional[str] = None,
    metodo_extracao: str = "simpler_api",
) -> Dict[str, Any]:
    """Converte dict normalizado → item do crawler (antes do transformer)."""
    from defense_intel import build_defense_extras, detect_keywords

    title = mapped.get("titulo") or ""
    agency = mapped.get("agency") or ""
    desc = f"{title} {agency}".strip()
    if not detect_keywords(desc):
        return {}

    legacy_id = mapped.get("legacy_opp_id")
    opp_num = mapped.get("opportunity_number") or ""
    link = mapped.get("link") or ""
    posted = mapped.get("posted_date")
    close = mapped.get("close_date")
    status = mapped.get("opportunity_status") or ""

    extras = build_defense_extras(
        text=desc,
        source_name="Grants.gov",
        origem=link,
        pais="US",
        orgao_contratante=str(agency or "US Federal Agencies"),
    )
    extras.update(
        {
            "source_variant": SOURCE_VARIANT,
            "legacy_source_variant": LEGACY_SOURCE_VARIANT,
            "opportunity_number": opp_num,
            "agency": agency,
            "agency_code": mapped.get("agency_code"),
            "opportunity_status": status,
            "posted_date": posted,
            "close_date": close,
            "award_ceiling": mapped.get("award_ceiling"),
            "award_floor": mapped.get("award_floor"),
            "funding_instrument": mapped.get("funding_instrument"),
            "funding_category": mapped.get("category"),
            "eligibility": mapped.get("eligibility"),
            "legacy_opp_id": legacy_id,
            "legacy_url": build_legacy_view_url(legacy_id) if legacy_id else None,
            "simpler_opportunity_uuid": mapped.get("opportunity_id"),
            "simpler_canonical_url": link,
            "collected_at": collected_at or utc_now_iso(),
            "codigo_oportunidade": opp_num or str(legacy_id or ""),
            "numero_chamada": opp_num,
            "opportunity_id": mapped.get("opportunity_id") or legacy_id,
            "modalidade": "grant",
            "tipo_oportunidade": "funding_opportunity",
            "objetivo": (mapped.get("summary") or title)[:600],
            "url_listagem": f"{SIMPLER_PUBLIC_BASE}/search",
            "url_detalhe": link,
            "metodo_extracao": metodo_extracao,
            "source_url": mapped.get("source_url") or link,
        }
    )
    if mapped.get("summary"):
        extras["descricao_resumo"] = str(mapped["summary"])[:3500]

    cur = curadoria_front_for_row(status, close)
    extras["curadoria_front"] = {
        **cur,
        "rule_version": "grants_simpler_v1",
        "checked_at": collected_at or utc_now_iso(),
    }

    situacao = "Aberto" if _status_prazo_from_row(status, close) != "encerrado" else "Encerrado"
    pub = posted or datetime.now(timezone.utc).date().isoformat()

    return {
        "titulo": title[:250] or "Funding Opportunity",
        "descricao": (mapped.get("summary") or desc)[:3500],
        "link": link,
        "fonte": "Grants.gov",
        "data_publicacao": pub,
        "fim_inscricao": close,
        "situacao": situacao,
        "valor": mapped.get("award_ceiling") or mapped.get("award_floor"),
        "programa": "tecnologias_estrategicas",
        "acao": "funding_opportunity",
        "tipo_recurso": "grant",
        "status_prazo": _status_prazo_from_row(status, close),
        "extras": extras,
    }


def fetch_simpler_search_page(
    session: requests.Session,
    *,
    page_offset: int,
    page_size: int,
    statuses: List[str],
    api_key: str,
    query: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    payload: Dict[str, Any] = {
        "filters": {"opportunity_status": {"one_of": statuses}},
        "pagination": {
            "page_offset": page_offset,
            "page_size": page_size,
            "sort_order": [
                {"order_by": "post_date", "sort_direction": "descending"},
            ],
        },
    }
    if query:
        payload["query"] = query[:100]
        payload["query_operator"] = "AND"

    headers = {"X-API-Key": api_key}
    time.sleep(RATE_LIMIT_SLEEP)
    r = session.post(
        f"{SIMPLER_API_BASE}{SIMPLER_SEARCH_PATH}",
        json=payload,
        headers=headers,
        timeout=45,
    )
    r.raise_for_status()
    body = r.json()
    data = body.get("data") or []
    meta = body.get("pagination_info") or {}
    return data if isinstance(data, list) else [], meta


def fetch_legacy_search2_page(
    session: requests.Session,
    *,
    page_index: int,
    page_size: int,
    keyword: str,
) -> List[Dict[str, Any]]:
    payload = {
        "startRecordNum": page_index * page_size,
        "rows": page_size,
        "oppStatuses": "forecasted|posted",
        "keyword": keyword,
    }
    time.sleep(RATE_LIMIT_SLEEP)
    r = session.post(LEGACY_SEARCH2_URL, json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    rows = (
        data.get("data", {}).get("oppHits", [])
        or data.get("oppHits", [])
        or []
    )
    return rows if isinstance(rows, list) else []


def collect_opportunities(
    *,
    max_pages: int = 3,
    page_size: int = DEFAULT_PAGE_SIZE,
    max_items: int = 50,
    statuses: Optional[List[str]] = None,
    keyword: str = "defense military nuclear aerospace dual-use",
    include_historic: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Coleta oportunidades (Posted + Forecasted por padrão).
    Retorna (itens pipeline, meta diagnóstico).
    """
    statuses = statuses or sorted(STATUS_COLLECT)
    if include_historic:
        statuses = sorted(set(statuses) | STATUS_HISTORIC)

    session = _session()
    api_key = get_api_key()
    collected_at = utc_now_iso()
    meta: Dict[str, Any] = {
        "collected_at": collected_at,
        "api_mode": "simpler_api" if api_key else "legacy_search2_fallback",
        "statuses": statuses,
        "max_pages": max_pages,
        "page_size": page_size,
        "max_items": max_items,
        "robots_url": SIMPLER_ROBOTS_URL,
        "rate_limit_sleep_sec": RATE_LIMIT_SLEEP,
    }

    raw_hits: List[Dict[str, Any]] = []
    seen: set[str] = set()

    if api_key:
        for page in range(1, max_pages + 1):
            try:
                rows, pinfo = fetch_simpler_search_page(
                    session,
                    page_offset=page,
                    page_size=page_size,
                    statuses=statuses,
                    api_key=api_key,
                )
            except Exception as exc:
                meta.setdefault("errors", []).append(f"simpler_page_{page}:{exc}")
                break
            meta.setdefault("pagination", []).append(pinfo)
            if not rows:
                break
            for row in rows:
                st = str(row.get("opportunity_status") or "").lower()
                if not include_historic and st in STATUS_HISTORIC:
                    continue
                key = row.get("opportunity_number") or row.get("opportunity_id") or row.get("legacy_opportunity_id")
                if not key or key in seen:
                    continue
                seen.add(str(key))
                raw_hits.append(map_simpler_api_hit(row))
                if len(raw_hits) >= max_items:
                    break
            if len(raw_hits) >= max_items:
                break
    else:
        meta["api_key_missing"] = True
        meta["note"] = (
            "Defina SIMPLER_GRANTS_API_KEY para API Simpler; "
            "usando api.grants.gov search2 + links simpler.grants.gov/opportunity/{id}"
        )
        for page in range(max_pages):
            try:
                rows = fetch_legacy_search2_page(
                    session,
                    page_index=page,
                    page_size=page_size,
                    keyword=keyword,
                )
            except Exception as exc:
                meta.setdefault("errors", []).append(f"legacy_page_{page}:{exc}")
                break
            if not rows:
                break
            for row in rows:
                st = str(row.get("oppStatus") or "").lower()
                if not include_historic and st in STATUS_HISTORIC:
                    continue
                key = row.get("number") or row.get("id")
                if not key or str(key) in seen:
                    continue
                seen.add(str(key))
                raw_hits.append(map_legacy_search2_hit(row))
                if len(raw_hits) >= max_items:
                    break
            if len(raw_hits) >= max_items:
                break

    items: List[Dict[str, Any]] = []
    discarded_historic: List[Dict[str, Any]] = []
    for mapped in raw_hits:
        st = mapped.get("opportunity_status") or ""
        if st in STATUS_HISTORIC and not include_historic:
            discarded_historic.append(mapped)
            continue
        item = build_pipeline_item(
            mapped,
            collected_at=collected_at,
            metodo_extracao=meta["api_mode"],
        )
        if item:
            items.append(item)

    meta["raw_hit_count"] = len(raw_hits)
    meta["pipeline_item_count"] = len(items)
    meta["discarded_historic_count"] = len(discarded_historic)
    return items, meta


def dedupe_key_for_item(item: Dict[str, Any]) -> str:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    num = (ex.get("opportunity_number") or ex.get("numero_chamada") or "").strip().upper()
    if num:
        return f"num:{num}"
    link = (item.get("link") or "").strip().lower()
    if link:
        return f"link:{link}"
    tit = (item.get("titulo") or "").strip().lower()[:120]
    ag = (ex.get("agency") or "").strip().lower()[:80]
    return f"ta:{tit}|{ag}"


def merge_with_existing_grants(
    new_items: List[Dict[str, Any]],
    existing: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Dedup loader: preferir atualizar link legado quebrado quando opportunity_number coincide.
    Não remove registros antigos da lista existing — só marca ações sugeridas em meta.
    """
    by_key: Dict[str, Dict[str, Any]] = {}
    for it in existing:
        by_key[dedupe_key_for_item(it)] = it

    stats = {"new": 0, "update_link": 0, "skip_duplicate": 0}
    out = list(existing)

    for it in new_items:
        key = dedupe_key_for_item(it)
        prev = by_key.get(key)
        if not prev:
            out.append(it)
            by_key[key] = it
            stats["new"] += 1
            continue
        prev_link = (prev.get("link") or "").lower()
        new_link = (it.get("link") or "").lower()
        if "view-opportunity" in prev_link and "simpler.grants.gov" in new_link:
            prev["link"] = it["link"]
            ex = prev.get("extras") if isinstance(prev.get("extras"), dict) else {}
            ex.update(it.get("extras") or {})
            ex["source_variant"] = SOURCE_VARIANT
            ex["simpler_canonical_url"] = new_link
            prev["extras"] = ex
            stats["update_link"] += 1
        else:
            stats["skip_duplicate"] += 1

    return out, stats


def extract_opportunity_number_from_item(item: Dict[str, Any]) -> str:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    return str(
        ex.get("opportunity_number")
        or ex.get("numero_chamada")
        or ex.get("codigo_oportunidade")
        or ""
    ).strip()


def extract_legacy_opp_id_from_item(item: Dict[str, Any]) -> str:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    raw = ex.get("legacy_opp_id") or ex.get("opportunity_id") or ""
    link = item.get("link") or ex.get("legacy_url") or ex.get("origem") or ""
    if not raw and "view-opportunity" in str(link).lower():
        m = re.search(r"oppId=(\d+)", link, re.I)
        if m:
            return m.group(1)
    return str(raw).strip() if raw else ""


def probe_simpler_opportunity_exists(
    legacy_opp_id: str,
    session: Optional[requests.Session] = None,
    timeout: float = 15.0,
) -> Tuple[bool, str]:
    """HEAD/GET leve: URL /opportunity/{legacy_id} deve redirecionar sem Page Not Found."""
    if not legacy_opp_id or not str(legacy_opp_id).isdigit():
        return False, "invalid_legacy_id"
    sess = session or _session()
    url = build_canonical_opportunity_url(legacy_opp_id=legacy_opp_id)
    try:
        time.sleep(RATE_LIMIT_SLEEP)
        r = sess.get(url, timeout=timeout, allow_redirects=True)
        final = r.url or url
        if r.status_code >= 400:
            return False, f"http_{r.status_code}"
        if "page-not-found" in final.lower():
            return False, "redirect_page_not_found"
        body = (r.text or "")[:30000].lower()
        if "page not found" in body and "return to home" in body:
            return False, "body_page_not_found"
        if "/opportunity/" in final:
            return True, final
        return False, "unexpected_final_url"
    except Exception as exc:
        return False, str(exc)[:80]
