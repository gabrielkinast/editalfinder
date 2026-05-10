#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
import warnings
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DEFAULT = ROOT / "config" / "news_research_sources.json"
OUT_DEFAULT = ROOT / "audit_reports_news_research"

HEADERS = {
    "User-Agent": "EditalFinderBot/1.0 (+public scientific/news monitoring)",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_date(v: Any) -> Optional[datetime]:
    if not v:
        return None
    s = str(v).strip()
    if not s:
        return None
    patterns = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M %z",
        "%d %B %Y",
        "%d %b %Y",
    ]
    for p in patterns:
        try:
            dt = datetime.strptime(s[: max(len(p), 10)], p)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    try:
        dt2 = parsedate_to_datetime(s)
        if dt2:
            if dt2.tzinfo is None:
                dt2 = dt2.replace(tzinfo=timezone.utc)
            return dt2.astimezone(timezone.utc)
    except Exception:
        pass
    # IAEA / alguns feeds: ano de 2 dígitos "26-04-30  16:32"
    m_iaea = re.match(r"^\s*(\d{2})-(\d{2})-(\d{2})\s+", s)
    if m_iaea:
        try:
            yy, mo, d = int(m_iaea.group(1)), int(m_iaea.group(2)), int(m_iaea.group(3))
            year = 2000 + yy if yy < 70 else 1900 + yy
            return datetime(year, mo, d, tzinfo=timezone.utc)
        except Exception:
            pass
    m = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", s)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
        except Exception:
            return None
    m2 = re.search(r"\b(20\d{2})/(\d{2})/(\d{2})\b", s)
    if m2:
        try:
            return datetime(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)), tzinfo=timezone.utc)
        except Exception:
            return None
    if "T" in s and re.match(r"20\d{2}-\d{2}-\d{2}T", s[:19]):
        try:
            dt3 = datetime.fromisoformat(s.replace("Z", "+00:00")[:32])
            if dt3.tzinfo is None:
                dt3 = dt3.replace(tzinfo=timezone.utc)
            return dt3.astimezone(timezone.utc)
        except Exception:
            pass
    return None


def _iso_date(dt: Optional[datetime]) -> Optional[str]:
    return dt.date().isoformat() if dt else None


def _strip_html(text: Any, max_len: int = 2400) -> str:
    """Remove tags e colapsa espaços; não inventa conteúdo."""
    if text is None:
        return ""
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", str(text))
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if max_len and len(t) > max_len:
        t = t[: max_len - 1].rsplit(" ", 1)[0] + "…"
    return t


def _local_tag(tag: str) -> str:
    if not tag:
        return ""
    return tag.split("}")[-1].lower()


def _child_text_join(it: ET.Element, *local_names: str) -> str:
    for child in list(it):
        if _local_tag(child.tag) in local_names:
            return "".join(child.itertext() or "").strip()
    return ""


def _parse_date_from_eureka_listing_title(titulo: str) -> Optional[datetime]:
    """Prefixo típico em listings EurekAlert: '4-May-2026 Título...' (inglês)."""
    if not titulo:
        return None
    m = re.match(r"^\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})\b", titulo.strip())
    if not m:
        return None
    mon = m.group(2).lower()[:3]
    mmap = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
    mo = mmap.get(mon)
    if not mo:
        return None
    try:
        return datetime(int(m.group(3)), mo, int(m.group(1)), tzinfo=timezone.utc)
    except Exception:
        return None


def _parse_date_from_url(url: str) -> Optional[datetime]:
    if not url:
        return None
    for pat in (
        r"(20\d{2})-(\d{2})-(\d{2})",
        r"(20\d{2})/(\d{2})/(\d{2})",
        r"/(20\d{2})/(\d{1,2})/(\d{1,2})/",
        r"/(20\d{2})/(\d{1,2})/(\d{1,2})[^/0-9]",
    ):
        m = re.search(pat, url)
        if not m:
            continue
        try:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if 1 <= mo <= 12 and 1 <= d <= 31:
                return datetime(y, mo, d, tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def _meta_and_jsonld_dates(html: str) -> List[str]:
    """Extrai strings de data candidatas de meta tags e JSON-LD (sem inventar)."""
    out: List[str] = []
    if not html or len(html) > 900_000:
        return out
    soup = BeautifulSoup(html, "html.parser")
    for attrs in (
        {"property": "article:published_time"},
        {"name": "article:published_time"},
        {"property": "og:updated_time"},
        {"name": "pubdate"},
        {"name": "date"},
    ):
        n = soup.find("meta", attrs=attrs)
        if n and n.get("content"):
            out.append(str(n.get("content")).strip())
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text() or ""
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        stack = [data] if isinstance(data, dict) else list(data) if isinstance(data, list) else []
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                for k in ("datePublished", "dateModified", "uploadDate"):
                    v = cur.get(k)
                    if isinstance(v, str) and v.strip():
                        out.append(v.strip())
                for v in cur.values():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(cur, list):
                stack.extend(cur)
    return out


def _snippet_from_article_html(html: str, max_len: int = 1200) -> str:
    """Meta description / og:description / primeiro parágrafo principal."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for attrs in ({"property": "og:description"}, {"name": "description"}):
        n = soup.find("meta", attrs=attrs)
        if n and n.get("content"):
            s = _strip_html(n.get("content"), max_len=max_len)
            if len(s) >= 20:
                return s
    main = soup.find("article") or soup.find("main") or soup.body
    if main:
        for p in main.find_all("p", limit=6):
            t = _strip_html(p.get_text(), max_len=max_len)
            if len(t) >= 40:
                return t
    return ""


def _filter_search_blob(r: Dict[str, Any]) -> str:
    """Texto agregado para require/exclude: título, descrição, link, categorias do feed."""
    parts = [
        str(r.get("titulo") or ""),
        str(r.get("descricao") or ""),
        str(r.get("link") or ""),
    ]
    cats = r.get("feed_categories")
    if isinstance(cats, list):
        parts.extend(str(c) for c in cats if c)
    return " ".join(parts).lower()


def _apply_source_filters(
    src: Dict[str, Any], r: Dict[str, Any]
) -> Tuple[bool, List[str], Optional[str]]:
    """
    exclude_keywords / require_any_keyword sobre blob expandido (incl. categorias RSS).
    Devolve (passou, keywords que deram match require_any, motivo de exclusão ou None).

    Nota: contexto biológico de \"defense\" (plant immunity, etc.) não é rejeitado aqui;
    a taxonomia (militar vs biológico) é aplicada em build_eurekalert_wave1_payloads.py.
    """
    blob = _filter_search_blob(r)
    matched: List[str] = []
    for kw in src.get("exclude_keywords") or []:
        if not isinstance(kw, str) or not kw.strip():
            continue
        ks = kw.strip().lower()
        if ks in blob:
            return False, [], f"exclude_keyword:{kw.strip()}"
    req = src.get("require_any_keyword") or []
    if isinstance(req, list) and req:
        for kw in req:
            if not isinstance(kw, str) or not kw.strip():
                continue
            ks = kw.strip().lower()
            if ks in blob:
                matched.append(kw.strip())
        if not matched:
            return False, [], "require_any_keyword_no_match"
    return True, matched, None


def _passes_source_filters(src: Dict[str, Any], r: Dict[str, Any]) -> bool:
    ok, _, _ = _apply_source_filters(src, r)
    return ok


def _exclude_reason_is_medical_generic(reason: Optional[str]) -> bool:
    """Heurística para diagnóstico: exclusão alinhada a temas de saúde/medicina genéricos."""
    if not reason or not str(reason).startswith("exclude_keyword:"):
        return False
    frag = str(reason).split(":", 1)[-1].lower()
    needles = (
        "cancer",
        "clinical",
        "patient",
        "hospital",
        "disease",
        "medicine",
        "health",
        "psychology",
        "oncology",
        "covid",
        "diabetes",
        "alzheimer",
        "pediatric",
        "trial",
        "therapy",
        "biology",
    )
    return any(n in frag for n in needles)


def _loose_item_categories(inner: str) -> List[str]:
    out: List[str] = []
    for m in re.finditer(r"<category\b([^>]*)>([\s\S]*?)</category>", inner, re.I):
        attrs, inner_txt = m.group(1), m.group(2)
        term_m = re.search(r'term\s*=\s*["\']([^"\']+)["\']', attrs)
        if term_m:
            t = term_m.group(1).strip()
            if t:
                out.append(t)
                continue
        t = re.sub(r"\s+", " ", _strip_html(inner_txt, max_len=400)).strip()
        if t:
            out.append(t)
    for m in re.finditer(r"<category\b([^/>]+)/>", inner, re.I):
        attrs = m.group(1)
        term_m = re.search(r'term\s*=\s*["\']([^"\']+)["\']', attrs)
        if term_m:
            t = term_m.group(1).strip()
            if t:
                out.append(t)
    return out


def _first_pdf_from_iaea_page(html: str, base_url: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """Primeiro PDF IAEA visível na página (anchor), sem rastrear site inteiro."""
    if not html:
        return None, []
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.select('a[href*=".pdf"]'):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        full = urljoin(base_url, href).split("#", 1)[0]
        low = full.lower()
        if not low.endswith(".pdf"):
            continue
        host = (urlparse(full).hostname or "").lower()
        if "iaea.org" not in host:
            continue
        doc = {"url": full[:800], "tipo": "pdf"}
        return full[:800], [doc]
    return None, []


def _maybe_enrich_from_page(r: Dict[str, Any], budget: Dict[str, int], src_id: str = "") -> None:
    """
    Até `max` GETs por fonte: meta/JSON-LD/resumo quando RSS/listing veio vazio.
    Não inventa texto: só extrai do HTML público.
    """
    max_f = int(budget.get("max", 25))
    if int(budget.get("n", 0)) >= max_f:
        return
    lk = str(r.get("link") or "").strip()
    if not lk.startswith("http"):
        return
    body = _strip_html(r.get("descricao") or "", max_len=600)
    min_body = 40 if src_id == "iaea_news_publications" else 35
    need_text = len(body) < min_body
    raw_pub = str(r.get("data_publicacao_raw") or "").strip()
    need_date = not raw_pub or not _parse_date(raw_pub)
    if not need_text and not need_date:
        return
    resp = _http_get(lk, timeout=22)
    if not resp or not (resp.text or "").strip():
        return
    budget["n"] = int(budget.get("n", 0)) + 1
    r["_page_enriched"] = True
    html = resp.text
    if need_text:
        sn = _snippet_from_article_html(html)
        if sn:
            r["descricao"] = sn[:3000]
    if need_date:
        found = False
        for cand in _meta_and_jsonld_dates(html):
            if _parse_date(cand):
                r["data_publicacao_raw"] = cand[:120]
                found = True
                break
        if not found:
            for m in re.finditer(r"\b(20\d{2}-\d{2}-\d{2})\b", html[:14000]):
                if _parse_date(m.group(1)):
                    r["data_publicacao_raw"] = m.group(1)
                    found = True
                    break
        if not found:
            udt = _parse_date_from_url(lk)
            if udt:
                r["data_publicacao_raw"] = udt.strftime("%Y-%m-%d")
    if src_id == "iaea_news_publications" and not (r.get("pdf_url") or "").strip():
        pdf_u, docs = _first_pdf_from_iaea_page(html, lk)
        if pdf_u:
            r["pdf_url"] = pdf_u
            if docs:
                cur = r.get("documentos")
                if isinstance(cur, list):
                    r["documentos"] = cur + docs
                else:
                    r["documentos"] = docs


def _http_get(url: str, timeout: int = 30) -> Optional[requests.Response]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code >= 400:
            return None
        return r
    except Exception:
        return None


def _looks_like_feed_xml(text: str) -> bool:
    low = (text or "").lower()
    return "<rss" in low or "<feed" in low or "<rdf:rdf" in low


def _xml_text_local(el: ET.Element, *local_names: str) -> str:
    want = {n.lower() for n in local_names}
    for ch in list(el):
        tag = _local_tag(ch.tag)
        if tag in want:
            return "".join(ch.itertext() or "").strip()
    return ""


def _extract_feed_items_loose(feed_url: str, body: str) -> List[Dict[str, Any]]:
    """
    Fallback quando o XML do feed é inválido (ex.: `<br>` em `<title>` na IAEA publications).
    Extrai blocos `<item>...</item>` e saneia tags vazias comuns antes do ElementTree.
    """
    out: List[Dict[str, Any]] = []
    for m in re.finditer(r"<item\b[^>]*>([\s\S]*?)</item>", body, re.I):
        inner = m.group(1)
        inner = re.sub(r"(?is)<\s*br\s*/?>", " ", inner)
        inner = re.sub(r"(?is)<\s*img[^>]*/?>", " ", inner)
        frag = f"<?xml version='1.0' encoding='utf-8'?><item>{inner}</item>"
        try:
            it = ET.fromstring(frag.encode("utf-8", errors="ignore"))
        except Exception:
            continue
        title = _xml_text_local(it, "title")[:320]
        link = _xml_text_local(it, "link")
        desc = (
            _xml_text_local(it, "description")
            or _xml_text_local(it, "summary")
            or _child_text_join(it, "encoded")
        )
        desc = _strip_html(desc, max_len=3000)
        pub = _xml_text_local(it, "pubDate", "published", "updated")
        if link:
            link = urljoin(feed_url, link)
        if not title and not link:
            continue
        cats_loose = _loose_item_categories(inner)
        out.append(
            {
                "titulo": title[:320],
                "descricao": re.sub(r"\s+", " ", desc).strip()[:3000],
                "link": link[:800],
                "data_publicacao_raw": pub,
                "source_method": "rss_loose",
                "feed_categories": cats_loose,
            }
        )
    return out


def _extract_feed_items(feed_url: str, body: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(body.encode("utf-8", errors="ignore"))
    except Exception:
        return _extract_feed_items_loose(feed_url, body)

    # RSS 2.0 / Atom fallback
    items = root.findall(".//item")
    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    if not items and "<item" in (body or "").lower():
        return _extract_feed_items_loose(feed_url, body)

    for it in items:
        def _text(path: str) -> str:
            n = it.find(path)
            return (n.text or "").strip() if n is not None and n.text else ""

        title = _text("title") or _text("{http://www.w3.org/2005/Atom}title")
        link = _text("link")
        if not link:
            atom_link = it.find("{http://www.w3.org/2005/Atom}link")
            if atom_link is not None:
                link = atom_link.attrib.get("href", "").strip()
        desc = (
            _text("description")
            or _child_text_join(it, "encoded")
            or _text("summary")
            or _text("{http://www.w3.org/2005/Atom}summary")
            or _child_text_join(it, "content")
        )
        desc = _strip_html(desc, max_len=3000)
        pub = (
            _text("pubDate")
            or _child_text_join(it, "date")
            or _text("published")
            or _text("updated")
            or _text("{http://www.w3.org/2005/Atom}updated")
            or _text("{http://www.w3.org/2005/Atom}published")
        )
        if link:
            link = urljoin(feed_url, link)
        if not title and not link:
            continue
        cats: List[str] = []
        for cat in it.findall("category"):
            t = (cat.text or "").strip()
            if not t:
                t = (cat.get("term") or cat.get("text") or "").strip()
            if t:
                cats.append(t)
        for cat in it.findall("{http://www.w3.org/2005/Atom}category"):
            t = (cat.get("term") or cat.text or "").strip()
            if t:
                cats.append(t)
        inst_src = ""
        for ch in list(it):
            lt = _local_tag(ch.tag)
            if lt in ("creator", "author", "source", "publisher", "contributor"):
                tx = "".join(ch.itertext() or "").strip()
                if tx and not inst_src:
                    inst_src = tx[:500]
        out.append(
            {
                "titulo": title[:320],
                "descricao": re.sub(r"\s+", " ", desc).strip()[:3000],
                "link": link[:800],
                "data_publicacao_raw": pub,
                "source_method": "rss",
                "feed_categories": cats,
                "fonte_instituicao_raw": inst_src or None,
            }
        )
    return out


def _extract_listing_items(seed_url: str, body: str, max_items: int) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(body, "html.parser")
    out: List[Dict[str, Any]] = []
    seen = set()
    seed_host = (urlparse(seed_url).hostname or "").lower()
    banned_hosts = ("x.com", "facebook.com", "linkedin.com", "youtube.com", "instagram.com")
    generic_titles = {
        "home",
        "news",
        "events",
        "search",
        "about",
        "contact",
        "publications",
        "work with us",
        "skip to main content",
    }
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        link = urljoin(seed_url, href).split("#", 1)[0]
        host = (urlparse(link).hostname or "").lower()
        if host and seed_host and host != seed_host:
            if not host.endswith("." + seed_host):
                continue
        if any(bh in host for bh in banned_hosts):
            continue
        if link in seen:
            continue
        if "eurekalert.org" in seed_host:
            if not re.search(r"/news-releases/\d{4,}\b", link, re.I):
                continue
        seen.add(link)
        title = " ".join((a.get_text() or "").split()).strip()
        ctx = f"{title} {link}".lower()
        # filtros conservadores de ruído
        if any(x in link.lower() for x in ("/login", "/signin", "/contact", "/about", "/privacy", "/terms", "/cookie", "/careers", "/jobs")):
            continue
        if title.lower() in generic_titles:
            continue
        if len(title) < 10 and not any(k in ctx for k in ("news", "research", "publication", "report", "study", "nasa", "darpa", "iaea", "eurekalert")):
            continue
        path = urlparse(link).path or "/"
        segs = [s for s in path.split("/") if s]
        if len(segs) < 2 and not any(k in ctx for k in ("rss", "xml", "news", "article", "publication")):
            continue
        out.append(
            {
                "titulo": title[:320] or link.rsplit("/", 1)[-1][:120],
                "descricao": "",
                "link": link[:800],
                "data_publicacao_raw": "",
                "source_method": "html_listing",
                "feed_categories": [],
            }
        )
        if len(out) >= max_items:
            break
    return out


def _discover_rss_links(seed_url: str, body: str) -> List[str]:
    soup = BeautifulSoup(body, "html.parser")
    out = []
    for n in soup.select("link[type='application/rss+xml'][href], link[type='application/atom+xml'][href]"):
        h = (n.get("href") or "").strip()
        if h:
            out.append(urljoin(seed_url, h))
    for a in soup.select("a[href]"):
        h = (a.get("href") or "").strip()
        txt = " ".join((a.get_text() or "").split()).lower()
        if not h:
            continue
        hl = h.lower()
        if hl.endswith(".rss") or hl.endswith(".xml") or "rss" in hl or "atom" in hl or "rss" in txt:
            out.append(urljoin(seed_url, h))
    ded = []
    seen = set()
    for u in out:
        if u in seen:
            continue
        seen.add(u)
        ded.append(u)
    return ded[:8]


def _seed_plan(src: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Lista (seed_url, seed_kind) com kind news|publications|mixed para roteamento IAEA."""
    sid = str(src.get("id") or "")
    if sid == "iaea_news_publications":
        news = [str(u).strip() for u in (src.get("seed_urls_news") or []) if str(u).strip()]
        pubs = [str(u).strip() for u in (src.get("seed_urls_publications") or []) if str(u).strip()]
        if news or pubs:
            # Publicações primeiro para garantir itens `pesquisa` antes do teto max_items.
            return [(u, "publications") for u in pubs] + [(u, "news") for u in news]
    out: List[Tuple[str, str]] = []
    for u in src.get("seed_urls") or []:
        u = str(u).strip()
        if u:
            out.append((u, "mixed"))
    return out


def _detect_content_type(item: Dict[str, Any], src_id: str) -> str:
    lk = str(item.get("link") or "").lower()
    tit = str(item.get("titulo") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    blob = f"{tit} {desc} {lk}"

    if src_id == "iaea_news_publications":
        sk = str(item.get("seed_kind") or "mixed")
        if sk == "publications":
            return "pesquisa"
        if sk == "news":
            return "noticia"
        if "/publications/" in lk or "/resources/" in lk or "/sites/default/files/" in lk:
            return "pesquisa"
        if any(
            x in lk
            for x in (
                "/newscenter/",
                "/pressreleases/",
                "/press/",
                "/multimedia/",
                "/newscenter/news/",
            )
        ):
            return "noticia"
        if any(
            x in blob
            for x in (
                "technical report",
                "safety standard",
                "iaea series",
                "nuclear security series",
                "guidance document",
                "publication ",
                "tecdoc",
            )
        ):
            return "pesquisa"

    if src_id == "eurekalert_science_filtered":
        if any(
            x in blob
            for x in (
                "published in",
                "peer-reviewed",
                "peer reviewed",
                "in the journal",
                "proceedings",
                "technical report",
                "preprint",
                "doi:",
                "arxiv:",
                "10.1038/",
                "10.1126/",
                "systematic review",
            )
        ):
            return "pesquisa"
        if len(desc) > 1200 and any(x in blob for x in ("study", "researchers", "findings", "experiments", "method")):
            return "pesquisa"
        return "noticia"

    t = blob
    if any(x in t for x in ("report", "study", "publication", "paper", "research", "white paper", "technical")):
        return "pesquisa"
    if "darpa_opportunities_research" in src_id:
        return "pesquisa"
    return "noticia"


def _iaea_infer_tags(blob: str, base_tags: List[str]) -> List[str]:
    """Refina tags nucleares quando o texto/URL traz evidência (sem inventar domínios fora do nuclear)."""
    b = blob.lower()
    extra: List[str] = []
    if any(k in b for k in ("safeguard", "safeguards", "verification", "inspector")):
        extra.append("seguranca_nuclear")
    if any(k in b for k in ("reactor", "nuclear energy", "nuclear power", "npp", "electricity")):
        extra.append("energia")
    if any(k in b for k in ("radiotherapy", "cancer", "health", "nutrition", "sterile")):
        extra.append("aplicacoes_nucleares")
    seen = set()
    out: List[str] = []
    for t in list(base_tags) + extra:
        if not isinstance(t, str) or not t.strip():
            continue
        k = t.strip()
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def _std_item(src: Dict[str, Any], raw: Dict[str, Any]) -> Dict[str, Any]:
    sid = str(src.get("id") or "")
    dt = _parse_date(raw.get("data_publicacao_raw")) or _parse_date_from_url(str(raw.get("link") or ""))
    if not dt and sid == "eurekalert_science_filtered":
        dt = _parse_date_from_eureka_listing_title(str(raw.get("titulo") or ""))
    content_type = _detect_content_type(raw, sid)
    tags = []
    for a in src.get("areas") or []:
        if isinstance(a, str) and a.strip():
            tags.append(a.strip())
    if sid == "iaea_news_publications":
        tags = _iaea_infer_tags(
            f"{raw.get('titulo','')} {raw.get('descricao','')} {raw.get('link','')}",
            tags,
        )
    if sid == "eurekalert_science_filtered":
        fc = raw.get("feed_categories")
        if isinstance(fc, list):
            for c in fc:
                if isinstance(c, str) and c.strip():
                    c2 = c.strip()[:120]
                    if c2 not in tags:
                        tags.append(c2)
    body = _strip_html(raw.get("descricao") or "", max_len=2500)
    desc_fallback_titulo = False
    if sid == "iaea_news_publications" and content_type == "pesquisa" and len(body) < 40:
        tt = re.sub(r"\s+", " ", str(raw.get("titulo") or "").strip())
        if len(tt) >= 40:
            body = tt[:2500]
            desc_fallback_titulo = True
    missing_summary = len(body) < 40
    has_date = bool(_iso_date(dt))
    if content_type == "pesquisa" and not has_date:
        val = "incompleto"
    elif missing_summary and not has_date:
        val = "acesso_limitado"
    elif missing_summary:
        val = "incompleto"
    else:
        val = "valido" if has_date else "incompleto"
    q = 40
    if body:
        q = min(95, 55 + min(40, len(body) // 25))
    if has_date:
        q = min(100, q + 5)
    fonte_nome = src.get("name")
    if sid == "iaea_news_publications":
        fonte_rec = "iaea_news_publications"
    elif sid == "eurekalert_science_filtered":
        fonte_rec = "eurekalert_science_filtered"
    else:
        fonte_rec = fonte_nome
    docs: List[Any] = []
    if isinstance(raw.get("documentos"), list):
        docs = [d for d in raw.get("documentos") if isinstance(d, dict)]
    pdf_u = raw.get("pdf_url") if isinstance(raw.get("pdf_url"), str) else None
    io_lang = raw.get("idioma_original") or raw.get("lang")
    idioma = str(io_lang).strip()[:12] if io_lang else "en"
    extras: Dict[str, Any] = {
        "source_id": src.get("id"),
        "source_method": raw.get("source_method"),
        "seed_url": raw.get("seed_url"),
        "seed_kind": raw.get("seed_kind"),
        "kind_declared": src.get("kind"),
        "time_window_months": src.get("time_window_months"),
        "content_type": content_type,
        "titulo_original": raw.get("titulo"),
        "descricao_original": raw.get("descricao"),
        "origem_portal": src.get("name"),
        "url_detalhe": raw.get("link"),
        "idioma_original": idioma if idioma else "en",
        "missing_summary": missing_summary,
        "pesquisa_sem_data": bool(content_type == "pesquisa" and not has_date),
        "page_enriched": bool(raw.get("_page_enriched")),
        "iaea_descricao_fallback_titulo": desc_fallback_titulo,
    }
    if sid == "eurekalert_science_filtered":
        extras["eurekalert_filtered"] = True
        extras["matched_keywords"] = list(raw.get("_matched_keywords") or [])
        extras["feed_categories"] = [
            x for x in (raw.get("feed_categories") or []) if isinstance(x, str) and x.strip()
        ][:40]
        if raw.get("fonte_instituicao_raw"):
            extras["instituicao_fonte_original"] = str(raw.get("fonte_instituicao_raw"))[:500]
    return {
        "titulo": raw.get("titulo"),
        "resumo": body or None,
        "descricao": body or None,
        "link": raw.get("link"),
        "fonte": fonte_nome,
        "fonte_recurso": fonte_rec,
        "data_publicacao": _iso_date(dt),
        "pais": src.get("country"),
        "regiao": src.get("region"),
        "idioma_original": idioma if idioma else "en",
        "tipo_conteudo": content_type,
        "tipo_pesquisa": "relatorio_tecnico" if content_type == "pesquisa" else None,
        "area_cientifica": [a for a in tags if a in ("ciencia_tecnologia", "fisica", "nuclear", "medicina")],
        "area_tecnologica": [a for a in tags if a not in ("fisica",)],
        "setor_estrategico": [a for a in tags if a in ("defesa", "nuclear", "aeroespacial")],
        "tags": tags,
        "imagem_url": None,
        "documentos": docs,
        "pdf_url": pdf_u,
        "qualidade_dado": q,
        "validacao_status": val,
        "extras": extras,
    }


def crawl_source(src: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    max_items = int(src.get("max_items") or 30)
    tw = int(src.get("time_window_months") or 12)
    min_dt = _now_utc() - timedelta(days=30 * tw)
    raw_items: List[Dict[str, Any]] = []
    standardized: List[Dict[str, Any]] = []
    seen = set()
    errors = []

    filter_stats: Dict[str, Any] = {
        "extracted_total": 0,
        "skipped_duplicate_link": 0,
        "rejected_exclude_keyword": 0,
        "rejected_exclude_medical_generic": 0,
        "rejected_require_any_keyword": 0,
        "rejected_feed_kind_cap": 0,
        "passed_theme_filters": 0,
        "matched_keyword_counts": {},
        "reject_samples": [],
    }

    plan = _seed_plan(src)
    if not plan:
        plan = [(str(s).strip(), "mixed") for s in (src.get("seed_urls") or []) if str(s).strip()]

    sid0 = str(src.get("id") or "")
    kind_counts: Dict[str, int] = {}
    feed_caps: Dict[str, Any] = src.get("feed_kind_caps") if isinstance(src.get("feed_kind_caps"), dict) else {}

    for seed, seed_kind in plan:
        if len(raw_items) >= max_items:
            break
        resp = _http_get(str(seed))
        if not resp:
            errors.append({"seed": seed, "error": "fetch_failed"})
            continue
        body = resp.text or ""
        extracted: List[Dict[str, Any]]
        if _looks_like_feed_xml(body):
            extracted = _extract_feed_items(str(seed), body)
        else:
            extracted = _extract_listing_items(str(seed), body, max_items=max_items)
            # Em fontes listing-heavy, tenta descobrir feed oficial e usar itens datados.
            if len(extracted) < max(5, max_items // 6):
                for rss in _discover_rss_links(str(seed), body):
                    rr = _http_get(rss)
                    if not rr:
                        continue
                    if not _looks_like_feed_xml(rr.text or ""):
                        continue
                    extracted.extend(_extract_feed_items(rss, rr.text or ""))
                    if len(extracted) >= max_items:
                        break
        for r in extracted:
            filter_stats["extracted_total"] += 1
            lk = str(r.get("link") or "").strip()
            if not lk:
                continue
            if lk in seen:
                filter_stats["skipped_duplicate_link"] += 1
                continue
            ok, matched_kws, excl = _apply_source_filters(src, r)
            if not ok:
                if excl == "require_any_keyword_no_match":
                    filter_stats["rejected_require_any_keyword"] += 1
                elif excl and str(excl).startswith("exclude_keyword"):
                    filter_stats["rejected_exclude_keyword"] += 1
                    if _exclude_reason_is_medical_generic(excl):
                        filter_stats["rejected_exclude_medical_generic"] += 1
                if len(filter_stats["reject_samples"]) < 24:
                    filter_stats["reject_samples"].append(
                        {
                            "link": lk[:800],
                            "titulo": (str(r.get("titulo") or ""))[:220],
                            "excluded_reason": excl,
                        }
                    )
                continue
            if sid0 == "iaea_news_publications" and feed_caps.get(seed_kind) is not None:
                lim = int(feed_caps[seed_kind])
                if kind_counts.get(seed_kind, 0) >= lim:
                    filter_stats["rejected_feed_kind_cap"] += 1
                    continue
            seen.add(lk)
            r["seed_url"] = seed
            r["seed_kind"] = seed_kind
            r["_matched_keywords"] = matched_kws
            for mk in matched_kws:
                kc = filter_stats["matched_keyword_counts"]
                kc[mk] = kc.get(mk, 0) + 1
            filter_stats["passed_theme_filters"] += 1
            kind_counts[seed_kind] = kind_counts.get(seed_kind, 0) + 1
            raw_items.append(r)
            if len(raw_items) >= max_items:
                break
        time.sleep(0.2)

    enrich_max = int(src.get("page_enrich_max") or 25)
    enrich_budget = {"n": 0, "max": enrich_max}
    for r in raw_items:
        _maybe_enrich_from_page(r, enrich_budget, src_id=sid0)

    for r in raw_items:
        dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(str(r.get("link") or ""))
        if not dt and sid0 == "eurekalert_science_filtered":
            dt = _parse_date_from_eureka_listing_title(str(r.get("titulo") or ""))
        r["data_publicacao"] = _iso_date(dt)
        r["within_window"] = bool(dt and dt >= min_dt)

    # Para first cycle: manter itens sem data, mas sinalizar.
    for r in raw_items:
        std = _std_item(src, r)
        standardized.append(std)

    by_kind: Dict[str, int] = {}
    for r in raw_items:
        k = str(r.get("seed_kind") or "mixed")
        by_kind[k] = by_kind.get(k, 0) + 1
    meta = {
        "source_id": src.get("id"),
        "source_name": src.get("name"),
        "method": src.get("method"),
        "seed_urls_used": [s for s, _ in plan],
        "max_items": max_items,
        "time_window_months": tw,
        "raw_total": len(raw_items),
        "within_window_total": sum(1 for r in raw_items if r.get("within_window")),
        "without_date_total": sum(1 for r in raw_items if not r.get("data_publicacao")),
        "raw_by_seed_kind": by_kind,
        "feed_kind_caps_applied": feed_caps if sid0 == "iaea_news_publications" else {},
        "page_enrich_fetch_total": int(enrich_budget.get("n", 0)),
        "errors": errors,
        "theme_filter_stats": filter_stats,
    }
    return raw_items, standardized, meta


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawl seguro de fontes notícia/pesquisa (sem apply).")
    ap.add_argument("--config", default=str(CONFIG_DEFAULT))
    ap.add_argument("--output-dir", default=str(OUT_DEFAULT))
    ap.add_argument("--sources", default="", help="CSV de source ids")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    out_dir = Path(args.output_dir)
    raw_dir = out_dir / "raw"
    std_dir = out_dir / "standardized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    std_dir.mkdir(parents=True, exist_ok=True)

    cfg = _load_json(cfg_path, {})
    sources = cfg.get("sources") if isinstance(cfg, dict) else []
    if not isinstance(sources, list):
        sources = []
    filt = {s.strip() for s in args.sources.split(",") if s.strip()}
    if filt:
        sources = [s for s in sources if str(s.get("id") or "") in filt]

    all_meta = []
    by_source = []
    examples = []
    total_raw = total_std = 0
    for s in sources:
        raw_items, std_items, meta = crawl_source(s)
        sid = str(s.get("id") or "source")
        (raw_dir / f"{sid}_raw.json").write_text(json.dumps(raw_items, ensure_ascii=False, indent=2), encoding="utf-8")
        (std_dir / f"{sid}_standardized.json").write_text(json.dumps(std_items, ensure_ascii=False, indent=2), encoding="utf-8")
        (out_dir / f"{sid}_crawl_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        total_raw += len(raw_items)
        total_std += len(std_items)
        by_source.append(
            {
                "source_id": sid,
                "raw_total": len(raw_items),
                "standardized_total": len(std_items),
                "within_window_total": meta["within_window_total"],
                "without_date_total": meta["without_date_total"],
                "error_total": len(meta["errors"]),
            }
        )
        examples.extend(
            {
                "source_id": sid,
                "titulo": i.get("titulo"),
                "link": i.get("link"),
                "data_publicacao": i.get("data_publicacao"),
                "tipo_conteudo": i.get("tipo_conteudo"),
            }
            for i in std_items[:8]
        )
        all_meta.append(meta)

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config_path": str(cfg_path.resolve()),
        "sources_total": len(sources),
        "raw_total": total_raw,
        "standardized_total": total_std,
        "by_source_path": str((out_dir / "by_source.json")),
        "examples_path": str((out_dir / "examples.json")),
        "notes": [
            "Sem apply em banco; apenas geração local de artefatos.",
            "Janela alvo: últimos 12 meses quando data disponível.",
            "Itens sem data são mantidos neste ciclo e sinalizados em auditoria."
        ],
    }

    (out_dir / "by_source.json").write_text(json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "examples.json").write_text(json.dumps(examples[:80], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "news_research_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# News/Research crawl summary",
        "",
        f"- Fontes avaliadas: **{summary['sources_total']}**",
        f"- Itens brutos: **{summary['raw_total']}**",
        f"- Itens standardized: **{summary['standardized_total']}**",
        "- Sem apply em Supabase (first cycle).",
        "",
        "## Por fonte",
        "",
    ]
    for r in by_source:
        md.append(
            f"- `{r['source_id']}`: raw={r['raw_total']} std={r['standardized_total']} "
            f"janela12m={r['within_window_total']} sem_data={r['without_date_total']} erros={r['error_total']}"
        )
    (out_dir / "news_research_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

