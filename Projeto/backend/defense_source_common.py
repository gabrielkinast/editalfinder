from __future__ import annotations

import csv
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from defense_intel import build_defense_extras, detect_keywords
from CORE.http_fetch import fetch_pdf_bytes
from CORE.pdf_enrichment import extract_pdf_text_with_fallback
from crawler_output_safe import CONFIRMED_EMPTY_REASON, save_output_safely

USER_AGENT = "EditalFinderBot/1.0 (+public institutional monitoring; contact: editalfinder)"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection": "keep-alive",
}
DEFAULT_TIMEOUT = 20

_SESSION: Optional[requests.Session] = None
_ROBOTS_RP_CACHE: Dict[str, Optional[RobotFileParser]] = {}


def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is not None:
        return _SESSION
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    _SESSION = session
    return session


NOISY_TITLES = (
    "skip to main content",
    "home",
    "news",
    "events",
    "contact us",
    "privacy policy",
)

# Recovery D — filtros opcionais (supplier portals US/UK) sem scraping agressivo.
_RECOVERY_D_DENY_URL_PARTS = (
    "/faq",
    "/faqs",
    "faq.",
    "-faq",
    "/help",
    "/support",
    "/contact",
    "/careers",
    "careers.",
    "/privacy",
    "/terms",
    "/cookies",
    "/cookie-policy",
    "sign-in",
    "/signin",
    "?signin",
    "zendesk",
    "helpdesk",
)

_RECOVERY_D_PDF_NOISE_HINTS = (
    "supplier-code-of-conduct",
    "code-of-conduct",
    "ethics",
    "scorecard",
    "blue-book",
)

_RECOVERY_D_ALLOW_OVERRIDE = (
    "supplier-registration",
    "vendor-registration",
    "become-a-supplier",
    "supplier-portal",
    "doing-business",
    "procurement",
    "mentor-protege",
    "mentor-protégé",
    "supplier-application",
)


def recovery_d_supplier_portal_collect_skip(url: str, anchor_title: str) -> bool:
    """
    Recusa URLs de FAQ/help/login isolado quando o crawler corre em modo Recovery D.
    Não faz bypass WAF/login; apenas evita ingestão de páginas de ruído conhecidas.
    """
    low_u = (url or "").lower()
    title_l = " ".join((anchor_title or "").split()).strip().lower()
    if any(x in low_u for x in _RECOVERY_D_ALLOW_OVERRIDE):
        return False
    if low_u.endswith(".pdf"):
        if any(h in low_u for h in _RECOVERY_D_PDF_NOISE_HINTS):
            return True
    if any(p in low_u for p in _RECOVERY_D_DENY_URL_PARTS):
        return True
    # Login isolado (portal index sem contexto de registo no título)
    if "/login" in low_u or low_u.rstrip("/").endswith("/login"):
        if not any(
            k in title_l
            for k in (
                "register",
                "registration",
                "supplier",
                "vendor",
                "portal",
                "sign up",
            )
        ):
            return True
    if "hicx.net" in low_u and low_u.rstrip("/").endswith("/app/index.html"):
        return True
    if title_l in ("log in", "sign in", "login", "sign-in") and len(title_l) < 24:
        return True
    return False


def recovery_d1_supplier_qa_url_skip(url: str, source_label: str) -> bool:
    """
    Recovery D.1 — a partir dos hubs corporativos, não seguir páginas de capability/institucional
    nem produto fora da árvore de suppliers (LM: subtree /suppliers only; GDLS: /suppliers ou PDFs wp-content).

    Sem bypass de robots; apenas filtro de âncoras na listagem.
    """
    low = (url or "").split("#", 1)[0].lower().strip()
    sl = (source_label or "").lower()
    if "lockheed" in sl:
        return "lockheedmartin.com" in low and "/suppliers" not in low
    if "general dynamics" in sl:
        if "gdls.com" in low:
            if "/suppliers" in low or "/wp-content/" in low:
                return False
            return True
        if "gd.com" in low:
            return "/suppliers" not in low
        return False
    return False


def _extract_main_text(soup: BeautifulSoup) -> str:
    container = (
        soup.select_one("main")
        or soup.select_one("article")
        or soup.select_one("#content")
        or soup.select_one(".content")
        or soup.select_one(".entry-content")
        or soup
    )
    paragraphs = []
    for node in container.select("p, li"):
        chunk = " ".join((node.get_text() or "").split()).strip()
        if len(chunk) < 40:
            continue
        low = chunk.lower()
        if any(k in low for k in ("privacy policy", "cookie", "skip to", "contact us", "about us")):
            continue
        paragraphs.append(chunk)
        if len(paragraphs) >= 14:
            break
    text = " ".join(paragraphs) if paragraphs else " ".join(container.get_text(" ").split())
    for marker in ("Skip to main content", "Ir para o Conteúdo", "Atenção! Seu navegador não pode executar javascript"):
        text = text.replace(marker, " ")
    return " ".join(text.split())


def _extract_best_title(anchor_title: str, soup: Optional[BeautifulSoup]) -> str:
    if soup:
        h1 = soup.select_one("h1")
        if h1:
            h1_text = " ".join((h1.get_text() or "").split()).strip()
            if h1_text and len(h1_text) >= 4 and not h1_text.lower().startswith("skip to"):
                return h1_text[:250]
    clean_anchor = " ".join((anchor_title or "").split()).strip()
    return clean_anchor[:250]


def _can_fetch(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return True
        robots = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        if robots in _ROBOTS_RP_CACHE:
            rp_cached = _ROBOTS_RP_CACHE[robots]
            return True if rp_cached is None else rp_cached.can_fetch(USER_AGENT, url)

        resp = _get_session().get(robots, headers=HEADERS, timeout=12)
        if resp.status_code != 200 or not (resp.text or "").strip():
            _ROBOTS_RP_CACHE[robots] = None
            return True

        rp = RobotFileParser()
        rp.set_url(robots)
        rp.parse(resp.text.splitlines())
        _ROBOTS_RP_CACHE[robots] = rp
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        # Fail-open conservador para não derrubar fonte; coleta mantém baixa taxa.
        return True


def _safe_get(url: str, timeout: int = DEFAULT_TIMEOUT) -> Optional[requests.Response]:
    try:
        if not _can_fetch(url):
            return None
        response = _get_session().get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response
    except Exception:
        return None


def _infer_tipo_recurso(text: str) -> str:
    low = (text or "").lower()
    if any(k in low for k in ("grant", "funding", "fund", "investment", "invest", "subsid", "non-dilutive", "award")):
        return "fomento_investimento"
    if any(k in low for k in ("sbir", "sttr", "baa", "call for proposals", "challenge")):
        return "fomento_pdi"
    return "contratacao_publica"


def _parse_date(text: str) -> Optional[str]:
    if not text:
        return None
    raw = text.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(raw[:19], fmt).date().isoformat()
        except Exception:
            continue
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        return raw[:10]
    m = re.search(r"\b(20\d{2})[-./](\d{1,2})[-./](\d{1,2})\b", raw)
    if m:
        try:
            y, mo, d = (int(x) for x in m.groups())
            return datetime(y, mo, d).date().isoformat()
        except Exception:
            return None
    return None


def _next_listing_candidates(listing_url: str, soup: BeautifulSoup) -> List[str]:
    out: List[str] = []
    for a in soup.select("a[href]"):
        text = " ".join((a.get_text() or "").split()).lower()
        href = a.get("href") or ""
        if not href:
            continue
        if any(k in text for k in ("next", "more", "older", "próxima", "proxima")) or "page=" in href:
            out.append(urljoin(listing_url, href).split("#", 1)[0])
    return out[:5]


def _build_page_url(url: str, page: int) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query["page"] = [str(page)]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def _extract_document_links(base_url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    docs: List[Dict[str, str]] = []
    for a in soup.select("a[href]"):
        href = a.get("href") or ""
        if not href:
            continue
        url = urljoin(base_url, href).split("#", 1)[0]
        txt = " ".join((a.get_text() or "").split())[:180] or "Documento"
        if txt.lower().startswith("skip to "):
            continue
        low = f"{txt} {url}".lower()
        if any(k in low for k in (".pdf", "solicitation", "guideline", "announcement", "tender", "baa", "call")):
            docs.append({"nome": txt, "url": url})
    seen = set()
    out: List[Dict[str, str]] = []
    for d in docs:
        if d["url"] in seen:
            continue
        seen.add(d["url"])
        out.append(d)
    return out[:12]


def _extract_ids(text: str) -> Dict[str, str]:
    if not text:
        return {"numero_edital": "", "numero_chamada": "", "numero_processo": "", "codigo_oportunidade": ""}
    pats = {
        "numero_edital": r"(?:edital|solicitation no\.?|notice id)\s*[:#]?\s*([A-Z0-9\-_/\.]{3,})",
        "numero_chamada": r"(?:call id|call no\.?|baa)\s*[:#]?\s*([A-Z0-9\-_/\.]{3,})",
        "numero_processo": r"(?:processo|proc(?:ess)? no\.?)\s*[:#]?\s*([A-Z0-9\-_/\.]{3,})",
        "codigo_oportunidade": r"(?:oppid|opportunity id|topic code)\s*[:#]?\s*([A-Z0-9\-_/\.]{3,})",
    }
    out = {}
    for k, p in pats.items():
        m = re.search(p, text, re.IGNORECASE)
        out[k] = m.group(1).strip() if m else ""
    return out


def scrape_html_portal(
    source_label: str,
    country: str,
    listing_urls: Iterable[str],
    allowed_domains: Iterable[str],
    extra_keywords: Optional[List[str]] = None,
    max_items: int = 30,
    delay_s: float = 0.6,
    max_listing_pages: int = 3,
    supplier_recovery_d_filter: bool = False,
    supplier_recovery_d1_qa: bool = False,
) -> List[Dict[str, object]]:
    items: List[Dict[str, object]] = []
    seen = set()
    allowed = [d.lower() for d in allowed_domains]
    extra_keywords = [k.lower() for k in (extra_keywords or [])]

    for listing_url in listing_urls:
        queue = [listing_url]
        seen_listing_pages = set()
        while queue and len(seen_listing_pages) < max_listing_pages and len(items) < max_items:
            current_listing = queue.pop(0)
            if current_listing in seen_listing_pages:
                continue
            seen_listing_pages.add(current_listing)
            response = _safe_get(current_listing)
            if not response:
                print(f"[{source_label}] Falha ao acessar listagem: {current_listing}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for nxt in _next_listing_candidates(current_listing, soup):
                if nxt not in seen_listing_pages and nxt not in queue:
                    queue.append(nxt)
            if len(seen_listing_pages) < max_listing_pages:
                guess = _build_page_url(listing_url, len(seen_listing_pages) + 1)
                # Páginas estáticas de fornecedor/procurement não são listagens paginadas; ?page=2 gera duplicados e ruído.
                static_supplier = any(
                    x in listing_url.lower()
                    for x in ("supplier", "procurement", "become-a-supplier", "lieferantenportal", "microsites")
                )
                if (
                    not static_supplier
                    and guess not in seen_listing_pages
                    and guess not in queue
                    and guess != listing_url
                ):
                    queue.append(guess)

            for a in soup.select("a[href]"):
                if len(items) >= max_items:
                    break
                href = a.get("href")
                if not href:
                    continue
                url = urljoin(current_listing, href).split("#", 1)[0]
                low_u = url.lower()
                if any(
                    x in low_u
                    for x in (
                        "datenschutz",
                        "privacy-policy",
                        "cookie-policy",
                        "/careers",
                        "/investors",
                        "/investor-relations",
                    )
                ):
                    continue
                host = urlparse(url).netloc.lower()
                if host.startswith("www."):
                    host = host[4:]
                if allowed and not any(host == d or host.endswith("." + d) for d in allowed):
                    continue
                if url in seen:
                    continue
                title = " ".join((a.get_text() or "").split()).strip()
                if not title:
                    continue
                if supplier_recovery_d_filter and recovery_d_supplier_portal_collect_skip(url, title):
                    continue
                if supplier_recovery_d1_qa and recovery_d1_supplier_qa_url_skip(url, source_label):
                    continue
                low_title = title.lower()
                if low_title in NOISY_TITLES or low_title.startswith("skip to "):
                    continue
                if len(low_title) < 6:
                    continue
                context = f"{title} {url}".lower()
                keywords = detect_keywords(context)
                if not keywords and not any(k in context for k in extra_keywords):
                    continue
                seen.add(url)
                time.sleep(delay_s)

                detail = _safe_get(url, timeout=25)
                body = ""
                docs: List[Dict[str, str]] = []
                detail_soup: Optional[BeautifulSoup] = None
                if detail:
                    detail_soup = BeautifulSoup(detail.text, "html.parser")
                    docs = _extract_document_links(url, detail_soup)
                    body = _extract_main_text(detail_soup)[:3500]
                best_title = _extract_best_title(title, detail_soup)
                merged = f"{title} {body}"
                tipo_recurso = _infer_tipo_recurso(merged)
                extras = build_defense_extras(
                    text=merged,
                    source_name=source_label,
                    origem=url,
                    pais=country,
                    orgao_contratante=source_label,
                )
                extras.update(_extract_ids(merged))
                extras["url_listagem"] = current_listing
                extras["url_detalhe"] = url
                extras["metodo_extracao"] = "html_listing_detail"
                extras["documentos"] = docs
                extras["tipo_recurso"] = tipo_recurso
                extras["natureza_recurso"] = "nao_reembolsavel" if "fomento" in tipo_recurso else "contratual"
                extras["reembolsavel"] = False if "fomento" in tipo_recurso else None
                if docs and not extras.get("pdf_url"):
                    for d in docs:
                        if d["url"].lower().endswith(".pdf") or ".pdf?" in d["url"].lower():
                            extras["pdf_url"] = d["url"]
                            break
                pdf_text = ""
                if extras.get("pdf_url"):
                    try:
                        pdf_bytes = fetch_pdf_bytes(str(extras.get("pdf_url")), page_referer=url)
                        if pdf_bytes:
                            extracted = extract_pdf_text_with_fallback(pdf_bytes, max_pages=5) or ""
                            pdf_text = " ".join(extracted.split())[:2200]
                    except Exception:
                        pdf_text = ""
                if pdf_text:
                    extras["pdf_texto_extraido"] = pdf_text
                    extras["pdf_resumo"] = pdf_text[:500]
                    if not _parse_date(body):
                        extras["data_publicacao_original"] = extras.get("data_publicacao_original") or _parse_date(pdf_text) or ""

                items.append(
                    {
                        "titulo": best_title,
                        "descricao": body or title,
                        "link": url,
                        "fonte": source_label,
                        "data_publicacao": _parse_date(body),
                        "fim_inscricao": None,
                        "situacao": "Em andamento",
                        "valor": None,
                        "programa": "tecnologias_estrategicas",
                        "acao": "monitoramento_oportunidades_publicas",
                        "tipo_recurso": tipo_recurso,
                        "extras": extras,
                    }
                )
        if len(items) >= max_items:
            break
    return items


def save_outputs(
    base_dir: Path,
    output_prefix: str,
    items: List[Dict[str, object]],
    *,
    failure_reason: Optional[str] = None,
    collection_failed: bool = False,
    allow_empty: bool = False,
) -> None:
    output_dir = base_dir / "outputs"
    output_dir.mkdir(exist_ok=True)
    json_path = output_dir / f"{output_prefix}_editais.json"
    csv_path = output_dir / f"{output_prefix}_editais.csv"
    result = save_output_safely(
        [dict(x) for x in items] if items else [],
        json_path,
        output_prefix,
        allow_empty=allow_empty,
        empty_confirmed_reason=CONFIRMED_EMPTY_REASON if allow_empty else None,
        failure_reason=failure_reason,
        collection_failed=collection_failed,
    )
    if not result.wrote_file:
        return
    if items:
        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(items[0].keys()))
            writer.writeheader()
            writer.writerows(items)
    else:
        csv_path.write_text("", encoding="utf-8")
