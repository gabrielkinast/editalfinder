"""
Saúde de links de editais — checagem HTTP, classificação e recomendações.

Usado por scripts/audit_edital_links.py. Não altera banco automaticamente.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import requests

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36 EditalFinderLinkHealth/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
}

# Status conhecidos (documentação / relatórios)
LINK_STATUS_VALUES = (
    "ok",
    "redirect_ok",
    "broken_404",
    "broken_spa_not_found",
    "forbidden_403",
    "timeout",
    "ssl_error",
    "invalid_url",
    "suspicious",
    "missing",
)

GRANTS_SPA_NOT_FOUND_MESSAGE = (
    "Grants.gov retornou página Page Not Found apesar de HTTP 200"
)

BROKEN_STATUSES = frozenset(
    {"broken_404", "broken_spa_not_found", "timeout", "invalid_url"}
)
DISABLE_BUTTON_STATUSES = BROKEN_STATUSES

GRANTS_SPA_BODY_STRONG = (
    "page not found",
    "we are sorry, we can't find the page",
    "we are sorry, we can\u2019t find the page",
    "can't find the page you are looking for",
    "can\u2019t find the page you are looking for",
)

GRANTS_SPA_BODY_WEAK = ("return to home",)

HTML_NOT_FOUND_HINTS = (
    "404 -",
    "404 error",
    "not found</",
    "no longer available",
    "opportunity not found",
    "could not be found",
    "página não encontrada",
    "pagina nao encontrada",
)

SUSPICIOUS_PATH_HINTS = (
    "/search",
    "/busca",
    "/pesquisa",
    "/home",
    "/index.html",
    "/login",
    "/signin",
    "/register",
    "/advanced-search",
    "/search-results",
)

ESSENTIAL_FIELDS = frozenset({"link", "link_edital", "link_inscricao", "origem", "url_detalhe"})

GRANTS_FETCH_OPP_URL = "https://api.grants.gov/v1/api/fetchOpportunity"
GRANTS_DETAIL_PAYLOAD_MARKER = "search-results-detail"
GRANTS_PNF_PAYLOAD_MARKER = "page-not-found"
SIMPLER_GRANTS_HOST = "simpler.grants.gov"
SIMPLER_OPPORTUNITY_BODY_MARKERS = (
    "posted date",
    "closing date",
    "opportunity number",
    "forecasted",
    "funding opportunity",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_url(raw: Any) -> str:
    s = str(raw or "").strip()
    if not s or s.lower() in ("null", "none", "n/a", "#"):
        return ""
    if s.startswith("//"):
        return f"https:{s}"
    return s


def is_valid_url(url: str) -> bool:
    if not url:
        return False
    try:
        p = urlparse(url)
    except Exception:
        return False
    if p.scheme not in ("http", "https"):
        return False
    if not p.netloc:
        return False
    return True


def _url_has_page_not_found_path(url: str) -> bool:
    return bool(url) and "page-not-found" in url.lower()


def _is_grants_context(*urls: str, body: str = "") -> bool:
    blob = " ".join(u for u in urls if u) + " " + (body or "")[:8000]
    low = blob.lower()
    return "grants.gov" in low or SIMPLER_GRANTS_HOST in low


def _is_simpler_grants_url(url: str) -> bool:
    u = normalize_url(url)
    return bool(u) and SIMPLER_GRANTS_HOST in u.lower()


def _is_legacy_grants_view_url(url: str) -> bool:
    u = normalize_url(url)
    return bool(u) and "grants.gov" in u.lower() and "view-opportunity" in u.lower()


def extract_grants_opp_id(url: str) -> str:
    u = normalize_url(url)
    if not u:
        return ""
    try:
        q = parse_qs(urlparse(u).query)
        for key in ("oppId", "oppid", "opportunityId"):
            vals = q.get(key) or []
            if vals and str(vals[0]).strip().isdigit():
                return str(vals[0]).strip()
    except Exception:
        pass
    m = re.search(r"/search-results-detail/(\d+)", u, re.I)
    if m:
        return m.group(1)
    m = re.search(r"simpler\.grants\.gov/opportunity/(\d+)", u, re.I)
    if m:
        return m.group(1)
    m = re.search(
        r"simpler\.grants\.gov/opportunity/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
        u,
        re.I,
    )
    if m:
        return m.group(1)
    return ""


def simpler_canonical_url_from_item(item: Dict[str, Any]) -> str:
    """URL Simpler preferida em extras (migração legado → canônico)."""
    ex = item.get("extras")
    if not isinstance(ex, dict):
        ex = {}
    for key in ("simpler_canonical_url", "url_detalhe", "origem"):
        u = normalize_url(ex.get(key))
        if u and _is_simpler_grants_url(u):
            return u
    legacy = extract_grants_opp_id(
        normalize_url(item.get("link") or ex.get("legacy_url") or "")
    )
    if legacy.isdigit():
        return f"https://{SIMPLER_GRANTS_HOST}/opportunity/{legacy}"
    return ""


def detect_simpler_grants_opportunity_page(
    url: str,
    final_url: str,
    body: str,
) -> Tuple[bool, str]:
    """Valida página de detalhe Simpler (HTTP 200 + conteúdo de oportunidade)."""
    for u in (normalize_url(url), normalize_url(final_url)):
        if not u or not _is_simpler_grants_url(u):
            continue
        if "/opportunity/" not in u.lower():
            return False, "not_opportunity_path"
        if _url_has_page_not_found_path(u):
            return True, "simpler_page_not_found_url"
    snippet = (body or "")[:80000].lower()
    if not snippet:
        return False, ""
    if any(p in snippet for p in GRANTS_SPA_BODY_STRONG):
        return True, "simpler_html_page_not_found"
    if "/opportunity/" in (final_url or url).lower():
        hits = sum(1 for m in SIMPLER_OPPORTUNITY_BODY_MARKERS if m in snippet)
        if hits >= 2:
            return False, "simpler_content_ok"
        if len(snippet) > 50000 and "opportunity" in snippet:
            return False, "simpler_large_shell_ok"
    return False, ""


def _grants_fetch_opportunity_exists(
    opp_id: str,
    session: Optional[requests.Session] = None,
    timeout: float = 20.0,
) -> bool:
    if not opp_id.isdigit():
        return False
    sess = session or requests.Session()
    try:
        r = sess.post(
            GRANTS_FETCH_OPP_URL,
            json={"opportunityId": int(opp_id)},
            headers={"Content-Type": "application/json", **DEFAULT_HEADERS},
            timeout=timeout,
        )
        data = r.json()
        if int(data.get("errorcode", -1)) != 0:
            return False
        payload = data.get("data")
        return isinstance(payload, dict) and bool(payload.get("id") or payload.get("opportunityTitle"))
    except Exception:
        return False


def _grants_nuxt_payload_snippet(
    path: str,
    session: Optional[requests.Session] = None,
    timeout: float = 20.0,
) -> str:
    base = "https://www.grants.gov"
    clean = path.split("?", 1)[0]
    url = f"{base}{clean}" if clean.startswith("/") else clean
    if not url.endswith("/_payload.json"):
        url = url.rstrip("/") + "/_payload.json"
    sess = session or requests.Session()
    try:
        r = sess.get(url, headers=DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
        if r.status_code >= 400:
            return ""
        return r.text or ""
    except Exception:
        return ""


def detect_grants_gov_legacy_view_opportunity(
    url: str,
    *,
    session: Optional[requests.Session] = None,
    timeout: float = 20.0,
) -> Tuple[bool, str]:
    """
    URL legada view-opportunity.html: SSR devolve 200 mas SPA abre /page-not-found.
    O payload Nuxt da rota legada vem vazio; a rota canônica search-results-detail tem dados.
    """
    u = normalize_url(url)
    if "grants.gov" not in u.lower() or "view-opportunity" not in u.lower():
        return False, ""

    opp_id = extract_grants_opp_id(u)
    if not opp_id:
        return False, ""

    legacy_payload = _grants_nuxt_payload_snippet(
        "/web/grants/view-opportunity.html",
        session=session,
        timeout=timeout,
    )
    legacy_empty = (
        len(legacy_payload) < 180
        and GRANTS_DETAIL_PAYLOAD_MARKER not in legacy_payload
    )

    detail_payload = _grants_nuxt_payload_snippet(
        f"/search-results-detail/{opp_id}",
        session=session,
        timeout=timeout,
    )
    detail_ok = (
        GRANTS_DETAIL_PAYLOAD_MARKER in detail_payload and len(detail_payload) > 400
    )

    pnf_payload = _grants_nuxt_payload_snippet("/page-not-found", session=session, timeout=timeout)
    pnf_marker = GRANTS_PNF_PAYLOAD_MARKER in pnf_payload

    api_ok = _grants_fetch_opportunity_exists(opp_id, session=session, timeout=timeout)

    if legacy_empty and detail_ok:
        return True, "grants_legacy_view_opportunity_spa_page_not_found"
    if legacy_empty and not api_ok:
        return True, "grants_opportunity_missing_api"
    if pnf_marker and "page-not-found" in u.lower():
        return True, "grants_page_not_found_url"
    return False, ""


def detect_broken_spa_not_found(
    url: str,
    final_url: str,
    body: str,
    *,
    redirect_urls: Optional[List[str]] = None,
) -> Tuple[bool, str]:
    """
    Erro semântico: HTTP 200 mas landing Page Not Found (SPA Grants.gov e similares).
    """
    candidates = [normalize_url(url), normalize_url(final_url)]
    if redirect_urls:
        candidates.extend(normalize_url(u) for u in redirect_urls if u)

    for u in candidates:
        if _url_has_page_not_found_path(u):
            return True, "url_page_not_found_path"

    for u in candidates:
        if u and "grants.gov" in u.lower():
            hit, reason = detect_grants_gov_legacy_view_opportunity(u)
            if hit:
                return True, reason

    if not _is_grants_context(*candidates, body=body):
        return False, ""

    snippet = (body or "")[:80000]
    if not snippet:
        return False, ""

    low = snippet.lower()
    has_strong = any(p in low for p in GRANTS_SPA_BODY_STRONG)
    has_weak = any(p in low for p in GRANTS_SPA_BODY_WEAK)

    if has_strong:
        return True, "grants_html_page_not_found"
    if has_weak and ("page not found" in low or _url_has_page_not_found_path(final_url)):
        return True, "grants_html_pnf_with_return_home"

    return False, ""


def collect_link_fields(item: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Retorna lista (campo, url) para auditar."""
    out: List[Tuple[str, str]] = []
    seen: set[str] = set()

    def add(campo: str, val: Any) -> None:
        u = normalize_url(val)
        if not u:
            return
        key = f"{campo}\0{u}"
        if key in seen:
            return
        seen.add(key)
        out.append((campo, u))

    add("link", item.get("link"))
    add("link_edital", item.get("link_edital"))
    add("link_inscricao", item.get("link_inscricao"))
    add("pdf_url", item.get("pdf_url"))
    add("url_documento", item.get("url_documento"))

    ex = item.get("extras")
    if isinstance(ex, dict):
        add("link_edital", ex.get("link_edital"))
        add("pdf_url", ex.get("pdf_url"))
        add("url_documento", ex.get("url_documento"))
        add("url_detalhe", ex.get("url_detalhe"))
        add("origem", ex.get("origem"))
        docs = ex.get("documentos")
        if isinstance(docs, list):
            for i, doc in enumerate(docs):
                if isinstance(doc, str):
                    add(f"documentos[{i}]", doc)
                elif isinstance(doc, dict):
                    add(f"documentos[{i}].url", doc.get("url") or doc.get("link") or doc.get("href"))

    docs_top = item.get("documentos")
    if isinstance(docs_top, list):
        for i, doc in enumerate(docs_top):
            if isinstance(doc, str):
                add(f"documentos[{i}]", doc)
            elif isinstance(doc, dict):
                add(f"documentos[{i}].url", doc.get("url") or doc.get("link") or doc.get("href"))

    return out


def is_suspicious_url(url: str, final_url: str, status_code: Optional[int]) -> Tuple[bool, str]:
    """Heurística: home/busca genérica em vez de detalhe do edital."""
    for u in (url, final_url):
        if not u:
            continue
        low = u.lower().rstrip("/")
        p = urlparse(low)
        path = (p.path or "/").lower()

        if SIMPLER_GRANTS_HOST in low:
            if path.rstrip("/") in ("/search", "") and "opportunity" not in path:
                return True, "simpler_search_listing_not_detail"
        if "grants.gov" in low and SIMPLER_GRANTS_HOST not in low:
            if "view-opportunity" not in low and path in ("/web/grants", "/web/grants/"):
                return True, "grants_home_sem_oppId"
            if "view-opportunity" in low and "oppid=" not in low:
                return True, "grants_view_sem_oppId"

        if any(h in path for h in SUSPICIOUS_PATH_HINTS):
            return True, "path_busca_ou_home"

        if path in ("", "/") and status_code == 200:
            return True, "raiz_do_dominio"

    return False, ""


def recommend_for_status(
    link_status: str,
    campo: str,
    *,
    all_essential_broken: bool = False,
) -> str:
    if link_status in ("ok", "redirect_ok"):
        return "manter"
    if link_status == "missing":
        return "review_manual"
    if link_status == "forbidden_403":
        return "review_manual"
    if link_status == "suspicious":
        return "corrigir_url"
    if link_status == "broken_spa_not_found":
        return "marcar_link_quebrado"
    if link_status in BROKEN_STATUSES:
        if campo == "pdf_url" or campo.startswith("documentos"):
            return "ocultar_botao_pdf"
        if all_essential_broken and campo in ESSENTIAL_FIELDS:
            return "ocultar_card_do_front"
        return "marcar_link_quebrado"
    return "review_manual"


def _is_essential_campo(campo: str) -> bool:
    base = campo.split("[", 1)[0]
    return base in ESSENTIAL_FIELDS


def check_url(
    url: str,
    *,
    session: Optional[requests.Session] = None,
    timeout: float = 20.0,
    allow_head: bool = True,
    campo: str = "link",
) -> Dict[str, Any]:
    """
    Testa uma URL e devolve dict com link_status, http_status, final_url, etc.
    """
    checked_at = utc_now_iso()
    essential = _is_essential_campo(campo)

    if not url:
        return {
            "url": "",
            "final_url": "",
            "http_status": None,
            "link_status": "missing",
            "checked_at": checked_at,
            "error_message": "empty",
            "recommendation": "review_manual",
            "essential_broken": False,
        }

    if not is_valid_url(url):
        return {
            "url": url,
            "final_url": "",
            "http_status": None,
            "link_status": "invalid_url",
            "checked_at": checked_at,
            "error_message": "invalid_scheme_or_host",
            "recommendation": "corrigir_url",
            "essential_broken": essential,
        }

    sess = session or requests.Session()
    sess.headers.update(DEFAULT_HEADERS)

    def _request(method: str) -> Tuple[Optional[requests.Response], Optional[str]]:
        try:
            r = sess.request(
                method,
                url,
                timeout=timeout,
                allow_redirects=True,
            )
            return r, None
        except requests.exceptions.SSLError as e:
            return None, f"ssl_error:{e.__class__.__name__}"
        except requests.exceptions.Timeout:
            return None, "timeout"
        except requests.exceptions.ConnectionError as e:
            msg = str(e).lower()
            if "ssl" in msg or "certificate" in msg:
                return None, "ssl_error"
            return None, f"connection_error:{e.__class__.__name__}"
        except requests.exceptions.RequestException as e:
            return None, f"request_error:{e.__class__.__name__}"

    resp, err = _request("GET")
    if resp is not None and resp.status_code in (405, 501) and allow_head:
        resp, err = _request("HEAD")

    if resp is None:
        if err == "timeout":
            st = "timeout"
        elif err and "ssl" in err.lower():
            st = "ssl_error"
        else:
            st = "timeout"
        return {
            "url": url,
            "final_url": "",
            "http_status": None,
            "link_status": st,
            "checked_at": checked_at,
            "error_message": err or "unknown",
            "recommendation": recommend_for_status(st, campo),
            "essential_broken": essential and st in BROKEN_STATUSES,
        }

    status = int(resp.status_code)
    final = normalize_url(resp.url) or url
    hist = list(getattr(resp, "history", []) or [])
    redirect_hops = len(hist)
    redirect_urls = [normalize_url(h.url) for h in hist if getattr(h, "url", None)]
    if normalize_url(resp.url):
        redirect_urls.append(normalize_url(resp.url))

    body_text = ""
    ctype = (resp.headers.get("Content-Type") or "").lower()
    if "html" in ctype or "text/" in ctype or not ctype:
        try:
            body_text = resp.text or ""
        except Exception:
            body_text = ""

    spa_hit, spa_reason = detect_broken_spa_not_found(
        url,
        final,
        body_text,
        redirect_urls=redirect_urls,
    )
    if not spa_hit and _is_simpler_grants_url(url):
        spa_hit, spa_reason = detect_simpler_grants_opportunity_page(url, final, body_text)
    if not spa_hit and "grants.gov" in url.lower() and "view-opportunity" in url.lower():
        spa_hit, spa_reason = detect_grants_gov_legacy_view_opportunity(
            url, session=sess, timeout=timeout
        )
    if spa_hit:
        st = "broken_spa_not_found"
        err_msg = GRANTS_SPA_NOT_FOUND_MESSAGE
        if spa_reason:
            err_msg = f"{GRANTS_SPA_NOT_FOUND_MESSAGE} ({spa_reason})"
        rec = "marcar_link_quebrado"
        if _is_legacy_grants_view_url(url):
            opp_id = extract_grants_opp_id(url)
            if opp_id.isdigit():
                rec = "corrigir_url"
                err_msg = (
                    f"{err_msg}; usar https://{SIMPLER_GRANTS_HOST}/opportunity/{opp_id}"
                )
        return {
            "url": url,
            "final_url": final,
            "http_status": status,
            "link_status": st,
            "checked_at": checked_at,
            "error_message": err_msg,
            "redirect_hops": redirect_hops,
            "recommendation": rec,
            "essential_broken": essential,
            "semantic_error": spa_reason,
        }

    if status in (404, 410):
        link_status = "broken_404"
    elif status == 403:
        link_status = "forbidden_403"
    elif status in (301, 302, 303, 307, 308):
        link_status = "redirect_ok"
    elif 200 <= status <= 299:
        link_status = "redirect_ok" if redirect_hops > 0 else "ok"
    elif 300 <= status <= 399:
        link_status = "redirect_ok"
    else:
        link_status = "broken_404" if status >= 400 else "review_manual"

    err = ""
    if link_status in ("ok", "redirect_ok"):
        sus, reason = is_suspicious_url(url, final, status)
        if sus:
            link_status = "suspicious"
            err = reason or "suspicious_landing"
        elif body_text:
            low = body_text[:12000].lower()
            if any(h in low for h in HTML_NOT_FOUND_HINTS):
                link_status = "broken_404"
                err = "html_body_not_found"

    rec = recommend_for_status(link_status, campo)
    return {
        "url": url,
        "final_url": final,
        "http_status": status,
        "link_status": link_status,
        "checked_at": checked_at,
        "error_message": err or "",
        "redirect_hops": redirect_hops,
        "recommendation": rec,
        "essential_broken": essential and link_status in BROKEN_STATUSES,
    }


def build_item_link_health(
    item: Dict[str, Any],
    field_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Agrega resultados por edital para extras.link_health."""
    by_field = {r["campo"]: r for r in field_results if r.get("campo")}
    statuses = [r.get("link_status") for r in field_results if (r.get("link") or r.get("url"))]
    primary = (
        by_field.get("link")
        or by_field.get("url_detalhe")
        or by_field.get("origem")
        or by_field.get("link_edital")
        or by_field.get("link_inscricao")
    )
    agg_status = (primary or {}).get("link_status") or (statuses[0] if statuses else "missing")

    essential_checks = [
        r
        for r in field_results
        if _is_essential_campo(str(r.get("campo") or ""))
        and (r.get("link") or r.get("url"))
    ]
    all_essential_broken = bool(essential_checks) and all(
        r.get("link_status") in BROKEN_STATUSES or r.get("essential_broken") is True
        for r in essential_checks
    )

    for r in field_results:
        r["recommendation"] = recommend_for_status(
            str(r.get("link_status") or ""),
            str(r.get("campo") or ""),
            all_essential_broken=all_essential_broken,
        )
        if r.get("link_status") == "broken_spa_not_found":
            r["essential_broken"] = _is_essential_campo(str(r.get("campo") or ""))
            r["error_message"] = r.get("error_message") or GRANTS_SPA_NOT_FOUND_MESSAGE
            r["recommendation"] = "marcar_link_quebrado"

    prim = primary or {}
    return {
        "link_status": agg_status,
        "checked_at": utc_now_iso(),
        "final_url": prim.get("final_url") or "",
        "http_status": prim.get("http_status"),
        "error_message": prim.get("error_message") or "",
        "recommendation": prim.get("recommendation") or recommend_for_status(str(agg_status), "link"),
        "fields": field_results,
        "all_essential_broken": all_essential_broken,
        "has_accessible_link": any(
            r.get("link_status") in ("ok", "redirect_ok")
            for r in field_results
            if _is_essential_campo(str(r.get("campo") or ""))
        ),
    }


def grants_url_structure_ok(url: str) -> Tuple[bool, str]:
    """Validação estrutural Grants.gov / Simpler (sem HTTP) para ingestão."""
    u = normalize_url(url)
    if not u:
        return False, "missing"
    if _is_simpler_grants_url(u):
        if "/opportunity/" in u.lower():
            return True, "simpler_canonical"
        return False, "simpler_not_opportunity_path"
    if "grants.gov" not in u.lower():
        return True, ""
    if "view-opportunity" in u.lower():
        if "oppid=" not in u.lower():
            return False, "missing_oppId"
        return False, "legacy_view_opportunity_deprecated"
    return False, "not_view_opportunity"


def stamp_structural_link_health(item: Dict[str, Any], *, source_key: str = "") -> None:
    """
    Marca extras.link_health estrutural (sem rede). Usar em crawlers/transformer.
    """
    ex = item.get("extras")
    if not isinstance(ex, dict):
        ex = {}
        item["extras"] = ex

    link = normalize_url(item.get("link") or ex.get("url_detalhe") or ex.get("origem"))
    ok, reason = True, ""
    sk = (source_key or "").lower()
    if "grant" in sk or "grants.gov" in link.lower():
        ok, reason = grants_url_structure_ok(link)

    lh = ex.get("link_health")
    if not isinstance(lh, dict):
        lh = {}
    lh["structural_checked_at"] = utc_now_iso()
    lh["structural_ok"] = ok
    if reason:
        lh["structural_reason"] = reason
        lh["link_status"] = "suspicious" if ok is False else lh.get("link_status")
    ex["link_health"] = lh
