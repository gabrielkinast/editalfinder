"""
Coleta Thales Group — fornecedores / procurement.

A listagem pública costuma estar atrás de Incapsula para `requests` simples; por isso
mantemos um manifesto de URLs oficiais (secção Supplier / Key documents) como fallback,
além de uma colheita relaxada de âncoras quando o HTML real está disponível.
"""

from __future__ import annotations

import re
import time
from typing import Dict, Iterable, List, Set, Tuple
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from defense_intel import build_defense_extras, detect_keywords
from defense_source_common import (
    _extract_best_title,
    _extract_document_links,
    _extract_ids,
    _extract_main_text,
    _infer_tipo_recurso,
    _parse_date,
    _safe_get,
)
from CORE.http_fetch import fetch_pdf_bytes
from CORE.pdf_enrichment import extract_pdf_text_with_fallback

SOURCE_LABEL = "Thales Suppliers"
COUNTRY = "FR"

# Seeds oficiais (supplier relations / procurement hub).
SEED_LISTING_URLS: Tuple[str, ...] = (
    "https://www.thalesgroup.com/en/supplier",
    "https://www.thalesgroup.com/en/supplier-relations",
)

# PDFs e textos alinhados à página pública "Key documents" (supplier relations).
CURATED_RESOURCES: Tuple[Tuple[str, str, str], ...] = (
    (
        "Thales Security Requirements - Purchasing",
        "https://www.thalesgroup.com/sites/default/files/2025-06/SECURITY%20REQUIREMENTS%20PURCHASING%20T%26Cs%20%281%29_0.pdf",
        "Official Thales purchasing security requirements for suppliers (PDF, Key documents).",
    ),
    (
        "Generic Requirements Applicable to External Providers (GRAEP)",
        "https://www.thalesgroup.com/sites/default/files/2025-06/87212869-ACQ-GRP-EN-006%20-%20Matrice%20EGAPE%20-%20GRAEP%20Matrix%20%283%29.pdf",
        "GRAEP matrix — requirements applicable to external providers supplying Thales (PDF).",
    ),
    (
        "General terms and conditions of purchase",
        "https://www.thalesgroup.com/sites/default/files/2025-09/THALES%20GENERAL%20TERMS%20AND%20CONDITIONS%20OF%20PURCHASE%20-%2005.05.2025%20%282%29.pdf",
        "Thales Group general terms and conditions of purchase (PDF).",
    ),
)

HUB_SUPPLIER_PAGE = "https://www.thalesgroup.com/en/supplier"

EXTRA_KEYWORDS = (
    "supplier",
    "procurement",
    "vendor",
    "purchasing",
    "requirement",
    "graep",
    "external provider",
    "tender",
    "sourcing",
    "onboarding",
)

URL_POSITIVE = (
    "/supplier",
    "supplier-relations",
    "procurement",
    "/sites/default/files/",
    "requirement",
    "graep",
    "conditions-of-purchase",
    "terms-of-purchase",
    "purchasing",
    "vendor",
    "onboarding",
    "e-acquisition",
    "eacquisition",
)

BLOCK_SUBSTR = (
    "datenschutz",
    "privacy-policy",
    "cookie-policy",
    "/careers",
    "/investors",
    "/investor-relations",
    "/news-centre",
    "/news/",
    "/press",
    "/contact",
    "/about",
    "/products",
    "sustainability",
    "/legal",
    "mediator",
    "news-centre/insights",
)


def _allowed_host(url: str, allowed: Iterable[str]) -> bool:
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    allow = [d.lower() for d in allowed]
    return any(host == d or host.endswith("." + d) for d in allow)


def _is_bot_challenge_html(html: str) -> bool:
    if not html or len(html) < 2800:
        return True
    low = html.lower()
    return any(
        x in low
        for x in (
            "incapsula",
            "pardon our interruption",
            "cf-browser-verification",
            "challenge-platform",
        )
    )


def _block_url(url: str) -> bool:
    low = url.lower()
    return any(b in low for b in BLOCK_SUBSTR)


def _url_self_signals(url: str) -> bool:
    low = url.lower()
    if _block_url(low):
        return False
    return any(s in low for s in URL_POSITIVE) or low.endswith(".pdf") or ".pdf?" in low


def _context_keywords(context: str) -> bool:
    low = context.lower()
    return bool(detect_keywords(low)) or any(k in low for k in EXTRA_KEYWORDS)


def _document_links_thales(base_url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    docs = _extract_document_links(base_url, soup)
    for a in soup.select("a[href]"):
        href = a.get("href") or ""
        if not href:
            continue
        url = urljoin(base_url, href).split("#", 1)[0]
        txt = " ".join((a.get_text() or "").split())[:220] or ""
        low = f"{txt} {url}".lower()
        if not url.lower().endswith(".pdf") and ".pdf?" not in url.lower():
            continue
        if not any(k in low for k in ("supplier", "purchas", "procurement", "graep", "requirement", "provider", "thales", "acq", "security")):
            continue
        if _block_url(url):
            continue
        nome = txt or "PDF"
        docs.append({"nome": nome, "url": url})
    seen: Set[str] = set()
    out: List[Dict[str, str]] = []
    for d in docs:
        u = d["url"]
        if u in seen:
            continue
        seen.add(u)
        out.append(d)
    return out[:24]


def _build_item(
    listing_url: str,
    detail_url: str,
    anchor_title: str,
    body: str,
    detail_soup: BeautifulSoup | None,
    docs: List[Dict[str, str]],
) -> Dict[str, object]:
    best_title = _extract_best_title(anchor_title, detail_soup)
    merged = f"{anchor_title} {body}".strip()
    tipo_recurso = _infer_tipo_recurso(merged)
    extras = build_defense_extras(
        text=merged,
        source_name=SOURCE_LABEL,
        origem=detail_url,
        pais=COUNTRY,
        orgao_contratante=SOURCE_LABEL,
    )
    extras.update(_extract_ids(merged))
    extras["url_listagem"] = listing_url
    extras["url_detalhe"] = detail_url
    extras["metodo_extracao"] = "html_listing_detail_relaxed"
    extras["documentos"] = docs
    extras["tipo_recurso"] = tipo_recurso
    extras["natureza_recurso"] = "nao_reembolsavel" if "fomento" in tipo_recurso else "contratual"
    extras["reembolsavel"] = False if "fomento" in tipo_recurso else None
    extras["origem_portal"] = "Thales"
    if docs and not extras.get("pdf_url"):
        for d in docs:
            du = d["url"].lower()
            if du.endswith(".pdf") or ".pdf?" in du:
                extras["pdf_url"] = d["url"]
                break
    pdf_text = ""
    if extras.get("pdf_url"):
        try:
            pdf_bytes = fetch_pdf_bytes(str(extras.get("pdf_url")), page_referer=detail_url)
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

    return {
        "titulo": best_title,
        "descricao": (body or anchor_title).strip()[:5000],
        "link": detail_url,
        "fonte": SOURCE_LABEL,
        "data_publicacao": _parse_date(body),
        "fim_inscricao": None,
        "situacao": "Em andamento",
        "valor": None,
        "programa": "tecnologias_estrategicas",
        "acao": "monitoramento_oportunidades_publicas",
        "tipo_recurso": tipo_recurso,
        "extras": extras,
    }


def _title_from_url(url: str) -> str:
    path = urlparse(url).path
    base = path.rsplit("/", 1)[-1].replace("-", " ").replace("_", " ")
    base = re.sub(r"\.pdf.*$", "", base, flags=re.I)
    return (base[:200] or "Document").strip()


def harvest_relaxed_from_seeds(
    allowed_domains: Tuple[str, ...],
    max_items: int = 24,
    delay_s: float = 0.55,
) -> List[Dict[str, object]]:
    items: List[Dict[str, object]] = []
    seen: Set[str] = set()

    for listing_url in SEED_LISTING_URLS:
        if len(items) >= max_items:
            break
        response = _safe_get(listing_url, timeout=28)
        if not response:
            continue
        raw = response.text or ""
        if _is_bot_challenge_html(raw):
            continue
        soup = BeautifulSoup(raw, "html.parser")
        for a in soup.select("a[href]"):
            if len(items) >= max_items:
                break
            href = a.get("href") or ""
            if not href:
                continue
            url = urljoin(listing_url, href).split("#", 1)[0]
            if not _allowed_host(url, allowed_domains):
                continue
            if _block_url(url):
                continue
            if url in seen:
                continue
            title = " ".join((a.get_text() or "").split()).strip()
            aria = " ".join((a.get("aria-label") or "").split()).strip()
            if len(title) < 4 and aria:
                title = aria
            if len(title) < 3:
                if not _url_self_signals(url):
                    continue
                title = _title_from_url(url)
            low_title = title.lower()
            if low_title in ("skip to main content", "home", "news", "events"):
                continue
            ctx = f"{title} {url}".lower()
            if not _context_keywords(ctx) and not _url_self_signals(url):
                continue
            seen.add(url)
            time.sleep(delay_s)
            detail = _safe_get(url, timeout=28)
            body = ""
            docs: List[Dict[str, str]] = []
            detail_soup = None
            if detail and not _is_bot_challenge_html(detail.text or ""):
                detail_soup = BeautifulSoup(detail.text, "html.parser")
                docs = _document_links_thales(url, detail_soup)
                body = _extract_main_text(detail_soup)[:3500]
            elif detail and _is_bot_challenge_html(detail.text or ""):
                body = title
            items.append(
                _build_item(
                    listing_url=listing_url,
                    detail_url=url,
                    anchor_title=title,
                    body=body or title,
                    detail_soup=detail_soup,
                    docs=docs,
                )
            )
    return items


def curated_manifest_items() -> List[Dict[str, object]]:
    """Itens mínimos a partir de URLs oficiais publicadas na área Supplier (Key documents)."""
    out: List[Dict[str, object]] = []
    for titulo, link, desc in CURATED_RESOURCES:
        merged = f"{titulo} {desc}"
        tipo_recurso = _infer_tipo_recurso(merged)
        extras = build_defense_extras(
            text=merged,
            source_name=SOURCE_LABEL,
            origem=link,
            pais=COUNTRY,
            orgao_contratante=SOURCE_LABEL,
        )
        extras.update(_extract_ids(merged))
        extras["url_listagem"] = HUB_SUPPLIER_PAGE
        extras["url_detalhe"] = link
        extras["metodo_extracao"] = "curated_official_manifest"
        extras["documentos"] = [{"nome": titulo, "url": link}]
        extras["tipo_recurso"] = tipo_recurso
        extras["natureza_recurso"] = "contratual"
        extras["pdf_url"] = link
        extras["origem_portal"] = "Thales"
        pdf_text = ""
        try:
            pdf_bytes = fetch_pdf_bytes(link, page_referer=HUB_SUPPLIER_PAGE)
            if pdf_bytes:
                extracted = extract_pdf_text_with_fallback(pdf_bytes, max_pages=5) or ""
                pdf_text = " ".join(extracted.split())[:2200]
        except Exception:
            pdf_text = ""
        if pdf_text:
            extras["pdf_texto_extraido"] = pdf_text
            extras["pdf_resumo"] = pdf_text[:500]
        out.append(
            {
                "titulo": titulo,
                "descricao": desc if not pdf_text else f"{desc} {pdf_text[:1200]}".strip()[:5000],
                "link": link,
                "fonte": SOURCE_LABEL,
                "data_publicacao": _parse_date(pdf_text) or None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "tecnologias_estrategicas",
                "acao": "monitoramento_oportunidades_publicas",
                "tipo_recurso": tipo_recurso,
                "extras": extras,
            }
        )
    return out


def hub_supplier_page_item() -> Dict[str, object] | None:
    """Uma entrada para a página hub de supplier relations (ação concreta: docs + ferramentas)."""
    listing = HUB_SUPPLIER_PAGE
    response = _safe_get(listing, timeout=28)
    body = ""
    detail_soup = None
    if response and not _is_bot_challenge_html(response.text or ""):
        detail_soup = BeautifulSoup(response.text, "html.parser")
        body = _extract_main_text(detail_soup)[:4500]
    if len((body or "").strip()) < 120:
        body = (
            "Thales supplier relations hub: procurement stakes, key supplier documents "
            "(security requirements, GRAEP, general terms), and references to collaborative "
            "tools (e.g. e-ACQuisition, Air Supply — restricted access for registered suppliers)."
        )
    merged = f"Supplier Relations {body}"[:5000]
    tipo_recurso = _infer_tipo_recurso(merged)
    extras = build_defense_extras(
        text=merged,
        source_name=SOURCE_LABEL,
        origem=listing,
        pais=COUNTRY,
        orgao_contratante=SOURCE_LABEL,
    )
    extras.update(_extract_ids(merged))
    extras["url_listagem"] = listing
    extras["url_detalhe"] = listing
    extras["metodo_extracao"] = "curated_hub_summary" if not response or _is_bot_challenge_html(response.text or "") else "html_hub_relaxed"
    extras["documentos"] = []
    extras["tipo_recurso"] = tipo_recurso
    extras["origem_portal"] = "Thales"
    docs = _document_links_thales(listing, detail_soup) if detail_soup else []
    extras["documentos"] = docs
    if docs and not extras.get("pdf_url"):
        for d in docs:
            du = d["url"].lower()
            if du.endswith(".pdf") or ".pdf?" in du:
                extras["pdf_url"] = d["url"]
                break
    return {
        "titulo": "Supplier Relations | Thales Group",
        "descricao": body.strip()[:5000],
        "link": listing,
        "fonte": SOURCE_LABEL,
        "data_publicacao": None,
        "fim_inscricao": None,
        "situacao": "Em andamento",
        "valor": None,
        "programa": "tecnologias_estrategicas",
        "acao": "monitoramento_oportunidades_publicas",
        "tipo_recurso": tipo_recurso,
        "extras": extras,
    }


def merge_thales_items(portal_items: List[Dict[str, object]], allowed_domains: Tuple[str, ...]) -> List[Dict[str, object]]:
    by_link: Dict[str, Dict[str, object]] = {}
    for it in portal_items:
        lk = str(it.get("link") or "").strip()
        if lk:
            by_link[lk] = it
    relaxed = harvest_relaxed_from_seeds(allowed_domains=allowed_domains)
    for it in relaxed:
        lk = str(it.get("link") or "").strip()
        if lk and lk not in by_link:
            by_link[lk] = it
    # PDFs oficiais (Key documents) + hub — dedupe; preenchem lacunas quando Incapsula bloqueia listagens.
    for it in curated_manifest_items():
        lk = str(it.get("link") or "").strip()
        if lk and lk not in by_link:
            by_link[lk] = it
    hub = hub_supplier_page_item()
    if hub:
        hlk = str(hub.get("link") or "").strip()
        if hlk and hlk not in by_link:
            by_link[hlk] = hub
    return list(by_link.values())
