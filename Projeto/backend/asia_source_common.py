"""asia_source_common.py

Utilitarios compartilhados pelos crawlers asiaticos (Japao e China):
- HTTP GET com headers tipo browser, Referer, retries, robots.txt.
- Suporte a proxy: HTTP_PROXY / HTTPS_PROXY (mesmo padrao do CORE/http_fetch.py).
- Timeout: EDITALFINDER_ASIA_TIMEOUT (segundos, default 35).
- User-Agent: por defeito usa um Chrome moderno (melhor com WAFs .cn/.jp).
  Para voltar ao bot identificavel: EDITALFINDER_ASIA_USE_BOT_UA=1
  Ou UA fixo: EDITALFINDER_ASIA_USER_AGENT="Mozilla/5.0 ..."

Limitacao: bloqueio geografico forte (GFW, apenas IP estrangeiro) so contorna
com VPN/proxy na regiao adequada — o codigo nao substitui isso.

NAO gera CSV propositalmente: para conteudo CJK, JSON UTF-8 e mais robusto.
"""

from __future__ import annotations

import json
import os
import re
import time
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from CORE.http_fetch import fetch_pdf_bytes, get_proxies, get_random_ua
from CORE.pdf_enrichment import extract_pdf_text_with_fallback
from CORE.opportunity_gate import (
    annotate_kept_extras,
    evaluate_crawl_candidate,
    rejection_record,
)

from asia_intel import (
    build_asia_extras,
    detect_keywords,
    detect_language,
)

from crawler_output_safe import CONFIRMED_EMPTY_REASON, SaveOutputResult, save_output_safely


USER_AGENT = (
    "EditalFinderBot/1.0 (+public institutional monitoring; "
    "scientific and procurement opportunities; contact: editalfinder)"
)

DEFAULT_TIMEOUT = int(os.getenv("EDITALFINDER_ASIA_TIMEOUT", "35") or "35")
DEFAULT_TIMEOUT = max(10, min(DEFAULT_TIMEOUT, 120))
DEFAULT_DELAY_S = float(os.getenv("EDITALFINDER_ASIA_DELAY", "0.8") or "0.8")
DEFAULT_MAX_LISTING_PAGES = 3

_SESSION: Optional[requests.Session] = None
_ROBOTS_RP_CACHE: Dict[str, Optional[RobotFileParser]] = {}
_EFFECTIVE_UA_CACHE: Optional[str] = None


def _effective_ua() -> str:
    """UA estavel por processo (robots + GET alinhados). Browser-like por defeito."""
    global _EFFECTIVE_UA_CACHE
    if _EFFECTIVE_UA_CACHE is not None:
        return _EFFECTIVE_UA_CACHE
    custom = os.getenv("EDITALFINDER_ASIA_USER_AGENT", "").strip()
    if custom:
        _EFFECTIVE_UA_CACHE = custom[:512]
    elif os.getenv("EDITALFINDER_ASIA_USE_BOT_UA", "").strip().lower() in ("1", "true", "yes", "on"):
        _EFFECTIVE_UA_CACHE = USER_AGENT
    else:
        _EFFECTIVE_UA_CACHE = get_random_ua()
    return _EFFECTIVE_UA_CACHE


def _origin_referer(url: str) -> str:
    p = urlparse(url)
    if p.scheme and p.netloc:
        return f"{p.scheme}://{p.netloc}/"
    return "https://www.google.com/"


def _alternate_accept_language(url: str, current: str) -> str:
    host = urlparse(url).netloc.lower()
    cur_l = current.lower()
    if host.endswith(".cn") or host.endswith(".com.cn") or host.endswith(".gov.cn"):
        if "zh-cn" not in cur_l:
            return "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.5"
        return "en-US,en;q=0.9,zh-CN;q=0.7"
    if host.endswith(".jp") or host.endswith(".go.jp"):
        if "ja" not in cur_l:
            return "ja,en-US;q=0.9,zh-CN;q=0.4"
        return "en-US,en;q=0.9,ja;q=0.6"
    return "en-US,en;q=0.9,ja;q=0.5,zh-CN;q=0.4"


def _proxies_kw() -> Dict[str, Dict[str, str]]:
    raw = get_proxies()
    if not raw:
        return {}
    clean = {k: v for k, v in raw.items() if v}
    return {"proxies": clean} if clean else {}


def _request_headers(accept_language: str, page_url: str) -> Dict[str, str]:
    return {
        "User-Agent": _effective_ua(),
        "Accept-Language": accept_language,
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "application/json;q=0.8,image/avif,image/webp,*/*;q=0.5"
        ),
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Referer": _origin_referer(page_url),
    }


def _get_session() -> requests.Session:
    global _SESSION
    if _SESSION is not None:
        return _SESSION
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        status=4,
        backoff_factor=0.9,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET", "HEAD"]),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.trust_env = True
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    _SESSION = session
    return session


def _can_fetch(url: str) -> bool:
    """Le robots.txt do dominio. Conservadoramente fail-open em caso de erro
    (igual ao defense_source_common para nao derrubar fontes), mas mantemos
    delays e UA identificavel.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            return True
        robots = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        ua = _effective_ua()
        if robots in _ROBOTS_RP_CACHE:
            rp_cached = _ROBOTS_RP_CACHE[robots]
            return True if rp_cached is None else rp_cached.can_fetch(ua, url)

        resp = _get_session().get(
            robots,
            headers=_request_headers("en-US,en;q=0.9", robots),
            timeout=min(15, DEFAULT_TIMEOUT),
            **_proxies_kw(),
        )
        if resp.status_code != 200 or not (resp.text or "").strip():
            _ROBOTS_RP_CACHE[robots] = None
            return True

        rp = RobotFileParser()
        rp.set_url(robots)
        rp.parse(resp.text.splitlines())
        _ROBOTS_RP_CACHE[robots] = rp
        return rp.can_fetch(ua, url)
    except Exception:
        return True


def _apply_response_encoding(response: requests.Response) -> None:
    if not response.encoding or response.encoding.lower() in ("iso-8859-1",):
        response.encoding = response.apparent_encoding or "utf-8"


def safe_get(
    url: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    accept_language: str = "ja,en;q=0.8",
) -> Optional[requests.Response]:
    """GET resiliente: robots, proxy, headers de browser, 2ª tentativa em 403/418/429."""
    try:
        if not _can_fetch(url):
            return None
        sess = _get_session()
        px = _proxies_kw()
        langs = (accept_language, _alternate_accept_language(url, accept_language))
        last: Optional[requests.Response] = None
        for attempt, lang in enumerate(langs):
            if attempt > 0 and (
                last is None
                or (
                    last.status_code not in (403, 418, 429)
                    and last.status_code != 0
                )
            ):
                break
            if attempt > 0:
                time.sleep(0.6)
            response = sess.get(
                url,
                headers=_request_headers(lang, url),
                timeout=timeout,
                allow_redirects=True,
                **px,
            )
            last = response
            if response.status_code == 200:
                _apply_response_encoding(response)
                return response
        return None
    except Exception:
        return None


def parse_loose_date(text: str) -> Optional[str]:
    """Tenta converter strings de data heterogeneas em YYYY-MM-DD."""
    if not text:
        return None
    raw = text.strip()
    formats = (
        "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
        "%d/%m/%Y", "%d-%m-%Y",
        "%Y%m%d",
    )
    for fmt in formats:
        try:
            return datetime.strptime(raw[:10], fmt).date().isoformat()
        except Exception:
            continue
    m_std = re.search(r"\b(20\d{2})[-./](\d{1,2})[-./](\d{1,2})\b", raw)
    if m_std:
        try:
            y, mo, d = (int(x) for x in m_std.groups())
            return datetime(y, mo, d).date().isoformat()
        except Exception:
            pass

    # Formato japones/chines: 2025年10月15日
    m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", raw)
    if m:
        try:
            y, mo, d = (int(x) for x in m.groups())
            return datetime(y, mo, d).date().isoformat()
        except Exception:
            pass
    # Formato em ingles textual: April 17, 2026
    m_en = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s*(20\d{2})\b",
        raw,
        re.IGNORECASE,
    )
    if m_en:
        try:
            return datetime.strptime(f"{m_en.group(1)} {m_en.group(2)} {m_en.group(3)}", "%B %d %Y").date().isoformat()
        except Exception:
            pass
    return None


def _extract_document_links(base_url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    docs: List[Dict[str, str]] = []
    for a in soup.select("a[href]"):
        href = a.get("href") or ""
        if not href:
            continue
        url = urljoin(base_url, href).split("#", 1)[0]
        txt = " ".join((a.get_text() or "").split())[:180] or "Documento"
        lower = f"{txt} {url}".lower()
        if any(k in lower for k in (".pdf", "guideline", "application", "募集要項", "招标", "公告", "document", "call")):
            docs.append({"nome": txt, "url": url})
    seen = set()
    out = []
    for d in docs:
        if d["url"] in seen:
            continue
        seen.add(d["url"])
        out.append(d)
    return out[:12]


def _extract_main_text(soup: BeautifulSoup, max_chars: int) -> str:
    container = (
        soup.select_one("main")
        or soup.select_one("article")
        or soup.select_one("#content")
        or soup.select_one(".content")
        or soup.select_one(".entry-content")
        or soup
    )
    chunks: List[str] = []
    for node in container.select("p, li"):
        chunk = " ".join((node.get_text() or "").split()).strip()
        if len(chunk) < 25:
            continue
        low = chunk.lower()
        if any(k in low for k in ("skip to", "privacy", "cookie", "contact", "about us")):
            continue
        chunks.append(chunk)
        if len(chunks) >= 14:
            break
    text = " ".join(chunks) if chunks else " ".join(container.get_text(" ").split())
    return text[:max_chars]


def _extract_notice_numbers(text: str) -> Dict[str, str]:
    if not text:
        return {"numero_edital": "", "numero_chamada": "", "numero_processo": "", "codigo_oportunidade": ""}
    patterns = {
        "numero_edital": r"(?:edital|公告编号|notice no\.?|招标编号)\s*[:：#]?\s*([A-Z0-9\-_/\.]{3,})",
        "numero_chamada": r"(?:call id|call no\.?|chamada)\s*[:：#]?\s*([A-Z0-9\-_/\.]{3,})",
        "numero_processo": r"(?:processo|process no\.?|项目编号)\s*[:：#]?\s*([A-Z0-9\-_/\.]{3,})",
        "codigo_oportunidade": r"(?:oppid|opportunity id|topic code|课题编号)\s*[:：#]?\s*([A-Z0-9\-_/\.]{3,})",
    }
    out: Dict[str, str] = {}
    for k, p in patterns.items():
        m = re.search(p, text, re.IGNORECASE)
        out[k] = m.group(1).strip() if m else ""
    return out


def _build_page_url(url: str, page_number: int) -> str:
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    query["page"] = [str(page_number)]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def _next_listing_candidates(listing_url: str, soup: BeautifulSoup) -> List[str]:
    candidates: List[str] = []
    for anchor in soup.select("a[href]"):
        txt = " ".join((anchor.get_text() or "").split()).lower()
        href = anchor.get("href") or ""
        if not href:
            continue
        if any(k in txt for k in ("next", "次", "下一页", "次へ", "more", "older")) or "page=" in href:
            candidates.append(urljoin(listing_url, href).split("#", 1)[0])
    return candidates[:5]


def is_relevant(text: str, *, extra_keywords: Iterable[str] = ()) -> bool:
    """Retorna True se o texto contem alguma palavra-chave relevante."""
    if not text:
        return False
    if detect_keywords(text):
        return True
    norm = text.lower()
    return any(k.lower() in norm for k in extra_keywords if k)


def scrape_asia_html_portal(
    *,
    source_label: str,
    country: str,
    listing_urls: Iterable[str],
    allowed_domains: Iterable[str],
    extra_keywords: Optional[List[str]] = None,
    max_items: int = 30,
    delay_s: float = DEFAULT_DELAY_S,
    accept_language: str = "ja,en;q=0.8",
    instituicao: str = "",
    orgao_responsavel: str = "",
    orgao_contratante: str = "",
    tipo_oportunidade_hint: str = "",
    programa: str = "asia_science_tech",
    acao: str = "monitoramento_oportunidades_publicas",
    tipo_recurso: str = "Oportunidade Publica",
    fetch_detail: bool = True,
    detail_max_chars: int = 3500,
    max_listing_pages: int = DEFAULT_MAX_LISTING_PAGES,
) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], Dict[str, Any]]:
    """Coletor HTML generico para portais asiaticos.

    - Le cada URL de listagem.
    - Para cada link <a> dentro do dominio permitido, aplica filtro multilingue.
    - Opcionalmente busca o detalhe e extrai um trecho do body para enriquecer
      a descricao e a classificacao tematica.
    - Retorna (itens validos, rejeitados, crawl_meta) — rejeitados para *_rejected.json (nao vao ao transformer).
    """
    items: List[Dict[str, object]] = []
    rejected: List[Dict[str, object]] = []
    seen = set()
    allowed = [d.lower() for d in allowed_domains]
    extra_keywords = [k for k in (extra_keywords or [])]
    listing_events: List[Dict[str, Any]] = []

    for listing_url in listing_urls:
        queue = [listing_url]
        seen_listing_pages = set()
        while queue and len(seen_listing_pages) < max_listing_pages and len(items) < max_items:
            current_listing = queue.pop(0)
            if current_listing in seen_listing_pages:
                continue
            seen_listing_pages.add(current_listing)
            response = safe_get(current_listing, accept_language=accept_language)
            listing_events.append(
                {
                    "url": current_listing,
                    "ok": response is not None,
                    "status_code": getattr(response, "status_code", None) if response else None,
                }
            )
            if not response:
                print(f"[{source_label}] Falha ao acessar listagem: {current_listing}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for next_candidate in _next_listing_candidates(current_listing, soup):
                if next_candidate not in seen_listing_pages and next_candidate not in queue:
                    queue.append(next_candidate)
            if len(seen_listing_pages) < max_listing_pages:
                page_num = len(seen_listing_pages) + 1
                paged = _build_page_url(listing_url, page_num)
                if paged not in seen_listing_pages and paged not in queue and paged != listing_url:
                    queue.append(paged)

            for anchor in soup.select("a[href]"):
                if len(items) >= max_items:
                    break
                href = anchor.get("href")
                if not href:
                    continue
                url = urljoin(current_listing, href).split("#", 1)[0]
                if not url.startswith("http"):
                    continue

                host = urlparse(url).netloc.lower()
                if host.startswith("www."):
                    host = host[4:]
                if allowed and not any(host == d or host.endswith("." + d) for d in allowed):
                    continue
                if url in seen:
                    continue

                title_raw = (anchor.get_text() or "").strip()
                title = " ".join(title_raw.split())
                if not title or len(title) < 4:
                    continue

                context = f"{title} {url}"
                if not is_relevant(context, extra_keywords=extra_keywords):
                    continue

                seen.add(url)
                time.sleep(delay_s)

                body = ""
                docs: List[Dict[str, str]] = []
                detail = None
                detail_missing = False
                if fetch_detail:
                    detail = safe_get(url, accept_language=accept_language)
                    if detail:
                        body_soup = BeautifulSoup(detail.text, "html.parser")
                        for tag in body_soup(["script", "style", "noscript"]):
                            tag.decompose()
                        docs = _extract_document_links(url, body_soup)
                        body = _extract_main_text(body_soup, detail_max_chars)
                    else:
                        detail_missing = True

                text_full = f"{title} {body}".strip()
                extras = build_asia_extras(
                    titulo_original=title,
                    descricao_original=body or title,
                    text_for_classification=text_full,
                    source_name=source_label,
                    origem=url,
                    pais=country,
                    instituicao=instituicao,
                    orgao_responsavel=orgao_responsavel,
                    orgao_contratante=orgao_contratante or source_label,
                    tipo_oportunidade_hint=tipo_oportunidade_hint,
                )
                ids = _extract_notice_numbers(f"{title} {body}")
                extras.update(ids)
                extras["url_listagem"] = current_listing
                extras["url_detalhe"] = url
                extras["metodo_extracao"] = "html_listing_detail"
                extras["documentos"] = docs
                if docs and not extras.get("pdf_url"):
                    for d in docs:
                        if d["url"].lower().endswith(".pdf") or ".pdf?" in d["url"].lower():
                            extras["pdf_url"] = d["url"]
                            break
                if extras.get("pdf_url"):
                    try:
                        pdf_bytes = fetch_pdf_bytes(str(extras.get("pdf_url")), page_referer=url)
                        if pdf_bytes:
                            extracted = extract_pdf_text_with_fallback(pdf_bytes, max_pages=5) or ""
                            pdf_text = " ".join(extracted.split())[:2200]
                            if pdf_text:
                                extras["pdf_texto_extraido"] = pdf_text
                                extras["pdf_resumo"] = pdf_text[:500]
                                if len(body) < 250:
                                    body = f"{body} {pdf_text[:900]}".strip()
                    except Exception:
                        pass
                extras["data_publicacao_original"] = extras.get("data_publicacao_original") or ""
                extras["fim_inscricao_original"] = extras.get("fim_inscricao_original") or ""
                extras["prazo_submissao_original"] = extras.get("prazo_submissao_original") or ""

                detail_status = int(detail.status_code) if detail is not None else None
                raw_html = (detail.text or "")[:12000] if detail is not None else ""
                if detail is not None:
                    extras["http_status_detail"] = detail_status
                if detail_missing:
                    extras["detail_fetch_failed"] = True

                gate = evaluate_crawl_candidate(
                    titulo=title,
                    descricao=body or "",
                    link=url,
                    status_code=detail_status,
                    raw_html=raw_html,
                    fonte=source_label,
                    extras=extras,
                    detail_missing=detail_missing,
                )
                if not gate.keep:
                    rejected.append(
                        rejection_record(
                            titulo=title,
                            link=url,
                            fonte=source_label,
                            gate=gate,
                            status_code=detail_status,
                        )
                    )
                    continue

                annotate_kept_extras(extras, gate)

                items.append({
                    "titulo": title[:250],
                    "descricao": (body or title)[:1500],
                    "link": url,
                    "fonte": source_label,
                    "data_publicacao": parse_loose_date(body),
                    "fim_inscricao": None,
                    "situacao": "Aberto",
                    "valor": None,
                    "programa": programa,
                    "acao": acao,
                    "tipo_recurso": tipo_recurso,
                    "extras": extras,
                })

        if len(items) >= max_items:
            break

    if rejected:
        why = Counter(r.get("access_status") or "?" for r in rejected)
        print(
            f"[{source_label}] opportunity_gate: validos={len(items)} rejeitados={len(rejected)} "
            f"por_status={dict(why)}"
        )

    any_listing_ok = any(bool(e.get("ok")) for e in listing_events)
    listing_attempts = len(listing_events)
    collection_failed = listing_attempts > 0 and not any_listing_ok
    if items:
        tipo_resultado = "coleta_com_itens"
    elif collection_failed:
        tipo_resultado = "falha_de_coleta"
    elif listing_attempts > 0 and any_listing_ok:
        tipo_resultado = "coleta_vazia_pos_filtros"
    else:
        tipo_resultado = "coleta_sem_listagens"

    crawl_meta: Dict[str, Any] = {
        "source_label": source_label,
        "listing_events": listing_events,
        "listing_attempts": listing_attempts,
        "any_listing_ok": any_listing_ok,
        "collection_failed": collection_failed,
        "tipo_resultado": tipo_resultado,
        "itens_count": len(items),
        "rejected_count": len(rejected),
    }
    if collection_failed:
        print(f"[{source_label}] falha_de_coleta: nenhuma listagem obteve resposta HTTP OK.")
    elif not items and any_listing_ok:
        print(f"[{source_label}] coleta_vazia_pos_filtros: listagens OK mas 0 itens após filtros/gate.")

    return items, rejected, crawl_meta


def save_outputs_asia(
    base_dir: Path,
    output_prefix: str,
    items: List[Dict[str, object]],
    *,
    rejected: Optional[List[Dict[str, object]]] = None,
    crawl_meta: Optional[Dict[str, Any]] = None,
    allow_empty_confirmed: bool = False,
    empty_confirmed_reason: Optional[str] = None,
) -> SaveOutputResult:
    """Grava outputs/<prefix>_editais.json com backup e proteção contra [] por falha."""
    output_dir = base_dir / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{output_prefix}_editais.json"

    meta = dict(crawl_meta or {})
    cf = bool(meta.get("collection_failed"))
    fr: Optional[str] = None
    if cf:
        fr = str(meta.get("failure_reason") or "todas_as_listagens_falharam_ou_rede")

    items_typed: List[Dict[str, Any]] = [dict(x) for x in items] if items else []

    result = save_output_safely(
        items_typed,
        json_path,
        output_prefix,
        allow_empty=allow_empty_confirmed,
        empty_confirmed_reason=empty_confirmed_reason,
        failure_reason=fr,
        collection_failed=cf,
        listing_events=list(meta.get("listing_events") or []),
        extra_context={
            "tipo_resultado": meta.get("tipo_resultado"),
            "rejected_count": len(rejected or []),
        },
    )

    rej_path = output_dir / f"{output_prefix}_rejected.json"
    if rejected is not None and result.wrote_file:
        with rej_path.open("w", encoding="utf-8") as f:
            json.dump(rejected, f, ensure_ascii=False, indent=2)

    return result


__all__ = [
    "USER_AGENT", "safe_get", "parse_loose_date", "is_relevant",
    "scrape_asia_html_portal", "save_outputs_asia",
    "CONFIRMED_EMPTY_REASON",
]
