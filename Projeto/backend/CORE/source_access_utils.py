"""
Utilitários de descoberta de acesso a fontes públicas (sem contornar WAF/captcha/login).

Usados por scripts/audit_source_access_methods.py — pedidos HTTP modestos,
timeouts curtos e cache local opcional.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36 EditalFinderAccessAudit/1.0"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
}

CLOUDFLARE_HINTS = (
    "cf-ray",
    "cloudflare",
    "checking your browser",
    "cf-browser-verification",
    "attention required! | cloudflare",
)
LOGIN_HINTS = (
    "sign in",
    "log in",
    "login required",
    "authentication required",
    "acesso restrito",
    "faça login",
    "fazer login",
)
CAPTCHA_HINTS = (
    "recaptcha",
    "g-recaptcha",
    "hcaptcha",
    "cf-turnstile",
    "captcha",
)
SPA_HINTS = (
    "enable javascript",
    "please enable javascript",
    "you need to enable javascript",
    "noscript",
)


def _origin(url: str) -> str:
    p = urlparse(url)
    if p.scheme and p.netloc:
        return f"{p.scheme}://{p.netloc}"
    return ""


def polite_get(
    url: str,
    *,
    timeout: float = 18.0,
    max_retries: int = 2,
    sleep_between: float = 1.2,
    session: Optional[requests.Session] = None,
    headers: Optional[Dict[str, str]] = None,
) -> Tuple[Optional[requests.Response], Optional[str]]:
    """
    GET simples com pequeno backoff em 5xx/429.
    Devolve (response, erro_curto) ou (None, mensagem).
    """
    sess = session or requests.Session()
    hdrs = {**DEFAULT_HEADERS, **(headers or {})}
    last_err: Optional[str] = None
    for attempt in range(max_retries + 1):
        try:
            r = sess.get(url, headers=hdrs, timeout=timeout, allow_redirects=True)
            if r.status_code == 429 and attempt < max_retries:
                ra = r.headers.get("Retry-After")
                wait = float(ra) if ra and ra.isdigit() else sleep_between * (attempt + 2)
                time.sleep(min(wait, 30.0))
                last_err = "429_retry"
                continue
            if 500 <= r.status_code < 600 and attempt < max_retries:
                time.sleep(sleep_between * (attempt + 2))
                last_err = f"5xx_{r.status_code}"
                continue
            time.sleep(sleep_between)
            return r, None
        except requests.RequestException as e:
            last_err = str(e)[:200]
            if attempt < max_retries:
                time.sleep(sleep_between * (attempt + 2))
            else:
                return None, last_err
    return None, last_err or "unknown"


def cache_http_response(
    url: str,
    payload: Dict[str, Any],
    *,
    cache_dir: Path,
) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha256(url.encode("utf-8")).hexdigest()[:40]
    path = cache_dir / f"{h}.json"
    rec = {"url": url, "saved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **payload}
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def fetch_robots_txt(
    base_url: str,
    *,
    timeout: float = 15.0,
    sleep_between: float = 1.0,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    origin = _origin(base_url)
    if not origin:
        return {"ok": False, "error": "url_invalida", "lines": []}
    robots_url = f"{origin}/robots.txt"
    r, err = polite_get(robots_url, timeout=timeout, max_retries=1, sleep_between=sleep_between, session=session)
    if err or r is None:
        return {"ok": False, "error": err or "sem_resposta", "url": robots_url, "lines": [], "raw_lines": []}
    text = r.text or ""
    parse_lines = [ln.rstrip("\r") for ln in text.splitlines()]
    lines_nocomment = [ln.strip() for ln in parse_lines if ln.strip() and not ln.strip().startswith("#")]
    return {
        "ok": r.status_code == 200,
        "status_code": r.status_code,
        "url": robots_url,
        "raw_lines": parse_lines[:500],
        "lines": lines_nocomment[:400],
        "sitemap_hints": _extract_sitemap_directives(text),
    }


def _extract_sitemap_directives(robots_body: str) -> List[str]:
    out: List[str] = []
    for ln in robots_body.splitlines():
        m = re.match(r"\s*Sitemap:\s*(\S+)", ln, re.I)
        if m:
            out.append(m.group(1).strip())
    return out


def robots_can_fetch(robots_lines: List[str], url: str, user_agent: str = "*") -> Optional[bool]:
    """None se não houver robots parseável."""
    if not robots_lines:
        return None
    rp = RobotFileParser()
    try:
        rp.parse(robots_lines)
        return rp.can_fetch(user_agent, url)
    except Exception:
        return None


def fetch_sitemap_urls(
    base_url: str,
    robots_sitemaps: List[str],
    *,
    timeout: float = 18.0,
    sleep_between: float = 1.0,
    session: Optional[requests.Session] = None,
) -> Dict[str, Any]:
    origin = _origin(base_url)
    candidates = list(robots_sitemaps)
    if origin:
        candidates.extend(
            [
                f"{origin}/sitemap.xml",
                f"{origin}/sitemap_index.xml",
                f"{origin}/wp-sitemap.xml",
            ]
        )
    seen: set[str] = set()
    results: List[Dict[str, Any]] = []
    for sm in candidates:
        if sm in seen:
            continue
        seen.add(sm)
        r, err = polite_get(sm, timeout=timeout, max_retries=1, sleep_between=sleep_between, session=session)
        if err or r is None:
            results.append({"url": sm, "ok": False, "error": err})
            continue
        body = (r.text or "")[:800_000]
        locs: List[str] = []
        if r.status_code == 200 and body:
            for m in re.finditer(r"<loc>\s*([^<]+)\s*</loc>", body, re.I):
                locs.append(m.group(1).strip())
        results.append(
            {
                "url": sm,
                "ok": r.status_code == 200,
                "status_code": r.status_code,
                "loc_count_sample": len(locs),
                "loc_samples": locs[:15],
            }
        )
        if locs:
            break
    return {"checked": results}


def discover_feeds(html: str, base_url: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    feeds: List[Dict[str, str]] = []
    for link in soup.find_all("link"):
        rel = (link.get("rel") or [])
        if isinstance(rel, str):
            rel = [rel]
        rel_l = " ".join(rel).lower()
        typ = (link.get("type") or "").lower()
        href = link.get("href")
        if not href:
            continue
        if "alternate" in rel_l and ("rss" in typ or "atom" in typ or "xml" in typ):
            feeds.append({"href": urljoin(base_url, href), "type": typ or "xml"})
    for a in soup.find_all("a", href=True):
        h = a["href"].lower()
        if any(x in h for x in ("/feed", "/rss", ".rss", "format=rss", "format=atom")):
            feeds.append({"href": urljoin(base_url, a["href"]), "type": "guess"})
    dedup: Dict[str, Dict[str, str]] = {}
    for f in feeds:
        dedup[f["href"]] = f
    return list(dedup.values())[:20]


def extract_json_ld(html: str) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[Dict[str, Any]] = []
    for tag in soup.find_all("script", type=lambda t: t and "ld+json" in t.lower()):
        raw = tag.string or tag.get_text() or ""
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        out.append({"@type": item.get("@type"), "keys": sorted(item.keys())[:40]})
            elif isinstance(data, dict):
                out.append({"@type": data.get("@type"), "keys": sorted(data.keys())[:40]})
        except json.JSONDecodeError:
            out.append({"@type": None, "keys": [], "parse_error": True})
    return out[:25]


def extract_meta_tags(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    meta: Dict[str, str] = {}
    for tag in soup.find_all("meta"):
        name = (tag.get("name") or tag.get("property") or "").strip().lower()
        content = tag.get("content")
        if name and content:
            meta[name] = str(content)[:500]
    return dict(sorted(meta.items())[:60])


def extract_open_graph(html: str) -> Dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    og: Dict[str, str] = {}
    for tag in soup.find_all("meta", property=True):
        prop = str(tag.get("property") or "").strip()
        if prop.lower().startswith("og:"):
            c = tag.get("content")
            if c:
                og[prop] = str(c)[:800]
    return og


def discover_official_documents(html: str, base_url: str, *, same_host_only: bool = True) -> List[str]:
    try:
        host = urlparse(base_url).netloc.lower()
    except Exception:
        host = ""
    soup = BeautifulSoup(html, "html.parser")
    docs: List[str] = []
    for a in soup.find_all("a", href=True):
        full = urljoin(base_url, a["href"])
        low = full.lower().split("?", 1)[0]
        if not any(low.endswith(ext) for ext in (".pdf", ".docx", ".doc")):
            continue
        if same_host_only:
            if urlparse(full).netloc.lower() != host:
                continue
        docs.append(full)
    dedup: List[str] = []
    seen: set[str] = set()
    for u in docs:
        if u not in seen:
            seen.add(u)
            dedup.append(u)
        if len(dedup) >= 40:
            break
    return dedup


def detect_cloudflare_response(r: requests.Response) -> bool:
    h = {k.lower(): v for k, v in r.headers.items()}
    if "cf-ray" in h:
        return True
    srv = (h.get("server") or "").lower()
    if "cloudflare" in srv:
        return True
    body = (r.text or "")[:12000].lower()
    return any(x in body for x in CLOUDFLARE_HINTS)


def classify_html_response(
    url: str,
    r: Optional[requests.Response],
    fetch_error: Optional[str],
    *,
    robots_disallows: Optional[bool] = None,
) -> str:
    if robots_disallows is True:
        return "robots_disallow"
    if fetch_error and r is None:
        return "endpoint_quebrado"
    if r is None:
        return "endpoint_quebrado"
    sc = r.status_code
    if sc == 429:
        return "rate_limit_429"
    if sc in (401, 403):
        if detect_cloudflare_response(r):
            return "cloudflare_403"
        body = (r.text or "")[:8000].lower()
        if any(x in body for x in LOGIN_HINTS):
            return "login_required"
        if "cloudflare" in body:
            return "cloudflare_403"
        # 403/401 público sem assinatura CF: limite de acesso (WAF, geo, política), não “site caído”.
        return "access_http_403"
    if sc >= 500:
        return "endpoint_quebrado"
    if sc != 200:
        return "endpoint_quebrado"
    body = r.text or ""
    low = body.lower()
    if any(x in low for x in CAPTCHA_HINTS):
        return "captcha"
    if any(x in low for x in LOGIN_HINTS) and len(body) < 25_000:
        return "login_required"
    if len(body) < 900 and any(x in low for x in SPA_HINTS):
        return "spa_pouco_html"
    if len(body) < 400:
        return "spa_pouco_html"
    return "ok_html_publico"


def recommend_safe_method(
    classification: str,
    signals: Dict[str, Any],
) -> str:
    """Uma etiqueta principal de método seguro sugerido."""
    if classification == "api_publica_disponivel":
        return "usar_api_publica"
    if classification == "fonte_sem_dados":
        return "revisar_manualmente"
    if signals.get("rss_found"):
        return "usar_rss"
    if signals.get("sitemap_ok"):
        return "usar_sitemap"
    if signals.get("json_ld_types"):
        return "usar_json_ld"
    if signals.get("open_graph_keys") or signals.get("meta_keys"):
        return "usar_meta_tags"
    if classification in ("cloudflare_403", "access_http_403", "rate_limit_429", "robots_disallow"):
        return "blocked_access_limited"
    if classification in ("login_required", "captcha"):
        return "revisar_manualmente"
    if classification == "spa_pouco_html":
        return "usar_pagina_alternativa_oficial"
    if classification == "endpoint_quebrado":
        return "revisar_manualmente"
    return "usar_curadoria_oficial_minima"
