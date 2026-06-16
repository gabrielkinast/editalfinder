"""
Recrawl/enriquecimento BNDES — detail HTML + PDF leve (Backend 10.2D).

Sem OCR pesado; timeouts e limites de tamanho; nenhuma escrita no banco.
"""
from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from bndes_submission_deadline import (
    SUBMISSION_DEADLINE_KIND,
    extract_bndes_submission_deadline,
    merge_bndes_text_blob,
)
from deadline_backfill import BNDES_PERMANENT_PATTERNS

BNDES_RECrawl_VERSION = "bndes_recrawl_10.2d"
DEFAULT_USER_AGENT = "EditalFinderBot/1.0 (+public institutional monitoring; contact: editalfinder)"
MAX_HTML_BYTES = 1_500_000
DEFAULT_PDF_MAX_BYTES = 5_000_000
DEFAULT_PDF_MAX_PAGES = 5
DEFAULT_HTTP_TIMEOUT = 15

_BNDES_HOSTS = ("bndes.gov.br", "www.bndes.gov.br")
_PDF_HREF = re.compile(r"\.pdf(?:\?|$|#)", re.I)
_NEWS_PATTERNS = (
    r"lan[cç]ou,?\s+em",
    r"lan[cç]ado,?\s+em",
    r"publicado\s+em",
    r"publicado\s+no\s+dia",
    r"banco\s+anuncia",
    r"bndes\s+aprova",
    r"divulga[cç][aã]o\s+em",
)
_CALL_PATTERNS = (
    r"chamada\s+p[uú]blica",
    r"sele[cç][aã]o\s+de\s+fundos",
    r"edital\s+bndes",
    r"edital\s+de\s+chamada",
)


def _extras(record: Dict[str, Any]) -> Dict[str, Any]:
    ex = record.get("extras")
    return ex if isinstance(ex, dict) else {}


def extract_bndes_detail_links(record: Dict[str, Any]) -> Dict[str, Any]:
    """Extrai URLs de detalhe e documentos do registro."""
    ex = _extras(record)
    link = str(record.get("link") or ex.get("url_detalhe") or ex.get("url_pagina") or "").strip()
    detail_url = str(ex.get("url_detalhe") or link or "").strip()
    pdf_urls: List[str] = []
    documents: List[Dict[str, str]] = []

    for key in ("pdf_url", "possible_deadline_document_url", "deadline_detail_url"):
        u = ex.get(key)
        if u and str(u).strip().lower().endswith(".pdf"):
            pdf_urls.append(str(u).strip())

    for doc in ex.get("documentos") or ex.get("anexos") or []:
        if not isinstance(doc, dict):
            continue
        u = str(doc.get("url") or doc.get("link") or "").strip()
        if not u:
            continue
        documents.append({"url": u, "nome": str(doc.get("nome") or doc.get("titulo") or "documento")[:120]})
        if _PDF_HREF.search(u):
            pdf_urls.append(u)

    blob = f"{record.get('titulo') or ''} {record.get('descricao') or ''}"
    for m in re.finditer(r"https?://[^\s\"']+\.pdf", blob, re.I):
        pdf_urls.append(m.group(0))

    seen: set[str] = set()
    unique_pdfs: List[str] = []
    for u in pdf_urls:
        if u not in seen:
            seen.add(u)
            unique_pdfs.append(u)

    return {
        "detail_url": detail_url or None,
        "pdf_urls": unique_pdfs,
        "documents": documents,
    }


def extract_bndes_html_text(html: str) -> str:
    """Extrai texto legível de HTML BNDES (sem dependência pesada)."""
    if not html:
        return ""
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html[:MAX_HTML_BYTES], "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        main = (
            soup.select_one(".content")
            or soup.select_one("#conteudo")
            or soup.select_one("main")
            or soup.body
            or soup
        )
        text = main.get_text(separator="\n", strip=True)
    except Exception:
        text = re.sub(r"<[^>]+>", " ", html[:MAX_HTML_BYTES])
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:50_000]


def discover_bndes_documents(html: str, base_url: str) -> List[Dict[str, Any]]:
    """Descobre links PDF/documento na página de detalhe."""
    if not html:
        return []
    found: List[Dict[str, Any]] = []
    seen: set[str] = set()
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html[:MAX_HTML_BYTES], "html.parser")
        for a in soup.select("a[href]"):
            href = (a.get("href") or "").strip()
            if not href:
                continue
            full = urljoin(base_url, href)
            if full in seen:
                continue
            low = full.lower()
            label = (a.get_text() or "").strip()[:120]
            if _PDF_HREF.search(low) or "edital" in label.lower() or "chamada" in label.lower():
                seen.add(full)
                kind = "pdf" if _PDF_HREF.search(low) else "document"
                found.append({"url": full, "label": label or full.split("/")[-1], "type": kind})
    except Exception:
        pass
    return found[:20]


def fetch_bndes_detail_page(url: str, *, timeout: int = DEFAULT_HTTP_TIMEOUT) -> Dict[str, Any]:
    """Fetch HTTP de página de detalhe BNDES (timeout + limite de bytes)."""
    if not url:
        return {"ok": False, "html": "", "text": "", "error": "empty_url"}
    host = urlparse(url).netloc.lower()
    if not any(h in host for h in _BNDES_HOSTS):
        return {"ok": False, "html": "", "text": "", "error": "non_bndes_host"}

    try:
        import requests

        r = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": DEFAULT_USER_AGENT, "Accept": "text/html"},
            stream=True,
        )
        r.raise_for_status()
        chunks: List[bytes] = []
        size = 0
        for chunk in r.iter_content(chunk_size=65536):
            if not chunk:
                continue
            chunks.append(chunk)
            size += len(chunk)
            if size > MAX_HTML_BYTES:
                break
        html = b"".join(chunks).decode(r.encoding or "utf-8", errors="replace")
        text = extract_bndes_html_text(html)
        return {"ok": True, "html": html[:MAX_HTML_BYTES], "text": text, "error": None, "source_url": url}
    except Exception as exc:
        return {"ok": False, "html": "", "text": "", "error": str(exc)[:200], "source_url": url}


def extract_bndes_pdf_text(
    pdf_url: str,
    *,
    max_pages: int = DEFAULT_PDF_MAX_PAGES,
    max_bytes: int = DEFAULT_PDF_MAX_BYTES,
    timeout: int = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    """Extrai texto de PDF BNDES com limites (pypdf/pdfplumber se disponível)."""
    base = {
        "ok": False,
        "text": "",
        "pages_read": 0,
        "source_url": pdf_url,
        "error": None,
    }
    if not pdf_url:
        base["error"] = "empty_url"
        return base

    try:
        from pdf_enrichment import extract_pdf_text_with_fallback
    except ImportError:
        base["error"] = "no_library"
        return base

    try:
        import requests

        r = requests.get(
            pdf_url,
            timeout=timeout,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            stream=True,
        )
        r.raise_for_status()
        cl = r.headers.get("Content-Length")
        if cl and int(cl) > max_bytes:
            base["error"] = "pdf_too_large"
            return base
        data = bytearray()
        for chunk in r.iter_content(chunk_size=65536):
            if not chunk:
                continue
            data.extend(chunk)
            if len(data) > max_bytes:
                base["error"] = "pdf_too_large"
                return base
        text = extract_pdf_text_with_fallback(bytes(data), max_pages=max_pages) or ""
        if not text.strip():
            base["error"] = "empty_pdf_text"
            return base
        base["ok"] = True
        base["text"] = text[:30_000]
        base["pages_read"] = min(max_pages, max(1, text.count("\f") + 1))
        return base
    except Exception as exc:
        err = str(exc).lower()
        if "timeout" in err or "timed out" in err:
            base["error"] = "timeout"
        else:
            base["error"] = str(exc)[:120]
        return base


def extract_bndes_deadline_from_text(text: str) -> Dict[str, Any]:
    """Extrai prazo de submissão BNDES; rejeita dúvidas/resultado/diligência."""
    sub = extract_bndes_submission_deadline(text)
    return {
        "iso": sub.get("iso"),
        "field": sub.get("field"),
        "raw": sub.get("raw"),
        "deadline_kind": sub.get("deadline_kind"),
        "confidence": sub.get("confidence", 0.0),
        "ignored_dates": sub.get("ignored_dates") or [],
        "rejected_publication": sub.get("iso") is None and any(
            i.get("reason") in ("publicado_em", "lancamento") for i in (sub.get("ignored_dates") or [])
        ),
    }


def classify_bndes_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Classificação semântica BNDES (notícia, linha permanente, chamada)."""
    titulo = str(record.get("titulo") or "")
    desc = str(record.get("descricao") or "")
    ex = _extras(record)
    blob = f"{titulo} {desc} {ex.get('bndes_detail_text') or ''}".lower()

    if any(re.search(p, blob, re.I) for p in BNDES_PERMANENT_PATTERNS):
        return {
            "category": "permanent_funding_line",
            "sem_prazo_kind": "permanent_funding_line",
            "is_news": False,
            "is_call": False,
        }

    is_news = any(re.search(p, blob, re.I) for p in _NEWS_PATTERNS)
    is_call = any(re.search(p, blob, re.I) for p in _CALL_PATTERNS)

    if is_news and not is_call:
        return {
            "category": "launch_news",
            "sem_prazo_kind": "deadline_in_pdf_or_detail",
            "is_news": True,
            "is_call": False,
        }

    if is_call:
        return {"category": "call", "sem_prazo_kind": None, "is_news": is_news, "is_call": True}

    return {"category": "other", "sem_prazo_kind": "unknown", "is_news": is_news, "is_call": False}


def _merge_text_for_backfill(item: Dict[str, Any]) -> str:
    return merge_bndes_text_blob(item)


def enrich_bndes_recrawl_item(
    item: Dict[str, Any],
    *,
    fetch_detail: bool = False,
    fetch_pdf: bool = False,
    http_timeout: int = DEFAULT_HTTP_TIMEOUT,
) -> Dict[str, Any]:
    """Enriquece registro BNDES com texto de detalhe/PDF quando disponível."""
    out = copy.deepcopy(item)
    ex = out.get("extras")
    if not isinstance(ex, dict):
        ex = {}
        out["extras"] = ex

    links = extract_bndes_detail_links(out)
    ex["bndes_detail_links"] = links
    classification = classify_bndes_record(out)
    ex["bndes_classification"] = classification

    detail_url = links.get("detail_url")
    if fetch_detail and detail_url and not ex.get("bndes_detail_text"):
        fetched = fetch_bndes_detail_page(detail_url, timeout=http_timeout)
        ex["bndes_detail_fetch"] = {
            "ok": fetched.get("ok"),
            "error": fetched.get("error"),
            "source_url": fetched.get("source_url"),
        }
        if fetched.get("ok") and fetched.get("text"):
            ex["bndes_detail_text"] = fetched["text"][:25_000]
            docs = discover_bndes_documents(fetched.get("html") or "", detail_url)
            if docs:
                ex["bndes_documents_discovered"] = docs
                for d in docs:
                    if d.get("type") == "pdf" and d.get("url"):
                        links.setdefault("pdf_urls", [])
                        if d["url"] not in links["pdf_urls"]:
                            links["pdf_urls"].append(d["url"])

    pdf_urls = links.get("pdf_urls") or []
    if pdf_urls and not ex.get("pdf_url"):
        ex["pdf_url"] = pdf_urls[0]
        ex.setdefault("possible_deadline_document_url", pdf_urls[0])

    if fetch_pdf and pdf_urls and not ex.get("pdf_texto_extraido"):
        pdf_result = extract_bndes_pdf_text(pdf_urls[0], timeout=http_timeout)
        ex["bndes_pdf_extract"] = {
            "ok": pdf_result.get("ok"),
            "error": pdf_result.get("error"),
            "pages_read": pdf_result.get("pages_read"),
            "source_url": pdf_result.get("source_url"),
        }
        if pdf_result.get("ok") and pdf_result.get("text"):
            ex["pdf_texto_extraido"] = pdf_result["text"][:25_000]

    merged = _merge_text_for_backfill(out)
    deadline = extract_bndes_deadline_from_text(merged)
    ex["bndes_deadline_extract"] = deadline
    if deadline.get("ignored_dates"):
        ex["bndes_ignored_dates"] = deadline["ignored_dates"]
    if deadline.get("deadline_kind") == SUBMISSION_DEADLINE_KIND and deadline.get("iso"):
        ex["deadline_source_field"] = deadline.get("field")
        ex["deadline_kind"] = SUBMISSION_DEADLINE_KIND
        ex["bndes_deadline_iso"] = deadline["iso"]
        ex["bndes_submission_confidence"] = deadline.get("confidence")
        out["fim_inscricao"] = deadline["iso"]
        out["prazo_envio"] = deadline["iso"]

    if classification.get("category") == "permanent_funding_line":
        ex.setdefault("sem_prazo_kind", "permanent_funding_line")
    elif deadline.get("rejected_publication"):
        ex["bndes_publication_date_rejected"] = True
    elif not deadline.get("iso") and pdf_urls and not ex.get("pdf_texto_extraido"):
        ex.setdefault("sem_prazo_kind", "deadline_in_pdf_or_detail")
    elif not deadline.get("iso") and classification.get("is_call"):
        ex.setdefault("sem_prazo_kind", "missing_from_loader")

    ex["bndes_recrawl_version"] = BNDES_RECrawl_VERSION
    return out


def stats_for_bndes_recrawl_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        "total": len(items),
        "detail_html_collected": 0,
        "pdfs_discovered": 0,
        "pdfs_extracted": 0,
        "pdfs_failed": 0,
        "permanent_lines": 0,
        "news_rejected": 0,
        "calls_with_deadline": 0,
        "without_structured_deadline": 0,
        "pdf_detail_candidates": 0,
    }
    for it in items:
        ex = _extras(it)
        if ex.get("bndes_detail_text"):
            stats["detail_html_collected"] += 1
        pdfs = (ex.get("bndes_detail_links") or {}).get("pdf_urls") or []
        if pdfs:
            stats["pdfs_discovered"] += 1
        pdf_ex = ex.get("bndes_pdf_extract") or {}
        if pdf_ex.get("ok"):
            stats["pdfs_extracted"] += 1
        elif pdf_ex and pdf_ex.get("error"):
            stats["pdfs_failed"] += 1
        cls = ex.get("bndes_classification") or {}
        if cls.get("category") == "permanent_funding_line":
            stats["permanent_lines"] += 1
        if ex.get("bndes_publication_date_rejected"):
            stats["news_rejected"] += 1
        if ex.get("bndes_deadline_iso") or (
            ex.get("deadline_kind") == SUBMISSION_DEADLINE_KIND and it.get("fim_inscricao")
        ):
            if cls.get("is_call") or cls.get("category") == "call":
                stats["calls_with_deadline"] += 1
            elif cls.get("category") != "permanent_funding_line":
                stats["calls_with_deadline"] += 1
        else:
            stats["without_structured_deadline"] += 1
        if ex.get("sem_prazo_kind") == "deadline_in_pdf_or_detail":
            stats["pdf_detail_candidates"] += 1
    return stats
