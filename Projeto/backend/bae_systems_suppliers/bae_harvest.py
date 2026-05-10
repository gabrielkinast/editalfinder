"""
Coleta BAE Systems — fornecedores / portal HICX.

O site corporativo `baesystems.com` costuma responder 403/Incapsula a `requests` simples.
O portal oficial de fornecedores na **baesystems.hicx.net** costuma devolver HTML completo
e texto útil (registo / login) — prioridade na colheita.

Manifesto / stub corporativo: só URL verificável + estado de fetch factual (sem inventar corpo).
"""

from __future__ import annotations

import time
from typing import Dict, List, Set, Tuple
from bs4 import BeautifulSoup

from defense_intel import build_defense_extras
from defense_source_common import (
    _extract_best_title,
    _extract_document_links,
    _extract_ids,
    _extract_main_text,
    _infer_tipo_recurso,
    _parse_date,
    _safe_get,
)

SOURCE_LABEL = "BAE Systems Suppliers"
COUNTRY = "UK"
LISTING_REFERENCE = "https://www.baesystems.com/en-uk/suppliers/responsible-supply-chain"

HICX_PAGES: Tuple[Tuple[str, str], ...] = (
    (
        "https://baesystems.hicx.net/bae/hicxesm-portal/app/discovery-login.html",
        "New supplier registration (HICX)",
    ),
)

CORP_STUB_URL = "https://www.baesystems.com/en-uk/suppliers/responsible-supply-chain"


def _is_challenge_html(html: str) -> bool:
    if not html or len(html) < 2500:
        return True
    low = html.lower()
    return any(
        x in low
        for x in (
            "incapsula",
            "pardon our interruption",
            "cf-browser-verification",
            "attention required",
        )
    )


def _plain_text(soup: BeautifulSoup, limit: int = 4000) -> str:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    text = " ".join(soup.get_text(separator=" ").split())
    return text[:limit]


def _build_item(
    listing_url: str,
    detail_url: str,
    anchor_title: str,
    body: str,
    detail_soup: BeautifulSoup | None,
    metodo: str,
    http_note: str | None = None,
) -> Dict[str, object]:
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
    extras["metodo_extracao"] = metodo
    extras["origem_portal"] = "BAE Systems"
    docs: List[Dict[str, str]] = []
    if detail_soup:
        docs = _extract_document_links(detail_url, detail_soup)[:16]
    extras["documentos"] = docs
    extras["tipo_recurso"] = tipo_recurso
    extras["natureza_recurso"] = "contratual"
    extras["reembolsavel"] = None
    if http_note:
        extras["detail_fetch_note"] = http_note
    if metodo in ("bae_hicx_fetch_failed", "bae_hicx_challenge_html"):
        extras["detail_fetch_failed"] = True
    if metodo == "bae_baesystems_waf_stub":
        extras["http_status_code"] = 403
        extras["access_limitation_candidate"] = True
    best_title = _extract_best_title(anchor_title, detail_soup)
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


def harvest_hicx_portal_pages() -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for url, fallback_title in HICX_PAGES:
        time.sleep(0.55)
        resp = _safe_get(url, timeout=32)
        if not resp:
            out.append(
                _build_item(
                    LISTING_REFERENCE,
                    url,
                    fallback_title,
                    fallback_title,
                    None,
                    "bae_hicx_fetch_failed",
                    http_note="GET failed (timeout or network).",
                )
            )
            continue
        raw = resp.text or ""
        if _is_challenge_html(raw):
            out.append(
                _build_item(
                    LISTING_REFERENCE,
                    url,
                    fallback_title,
                    fallback_title,
                    None,
                    "bae_hicx_challenge_html",
                    http_note="Short or challenge HTML from HICX URL.",
                )
            )
            continue
        soup = BeautifulSoup(raw, "html.parser")
        body = _extract_main_text(soup)[:4500] or _plain_text(soup, 4000)
        if len(body.strip()) < 80:
            body = _plain_text(soup, 4000)
        out.append(
            _build_item(
                LISTING_REFERENCE,
                url,
                fallback_title,
                body,
                soup,
                "bae_hicx_portal_html",
            )
        )
    return out


def _maybe_corporate_stub() -> Dict[str, object] | None:
    """HTML corporativo útil ou stub factual quando o bot não obtém conteúdo."""
    time.sleep(0.45)
    resp = _safe_get(CORP_STUB_URL, timeout=28)
    if resp and not _is_challenge_html(resp.text or ""):
        soup = BeautifulSoup(resp.text, "html.parser")
        body = _extract_main_text(soup)[:4500]
        if len(body.strip()) < 120:
            body = _plain_text(soup, 4000)
        if len(body.strip()) < 120:
            return None
        return _build_item(
            CORP_STUB_URL,
            CORP_STUB_URL,
            "Responsible supply chain | BAE Systems UK suppliers",
            body,
            soup,
            "bae_corporate_supplier_html",
        )
    status = str(getattr(resp, "status_code", "") or "") if resp else ""
    note = (
        f"Automated GET returned HTTP {status} or anti-bot/challenge HTML (short response). "
        "Official BAE Systems UK page on responsible supply chain — open in a browser for full content."
    )
    if not resp:
        note = "Automated GET failed (timeout or network). Official BAE Systems UK suppliers URL."
    return _build_item(
        LISTING_REFERENCE,
        CORP_STUB_URL,
        "Responsible supply chain | BAE Systems UK suppliers",
        note,
        None,
        "bae_baesystems_waf_stub",
        http_note=note[:500],
    )


def merge_bae_items(
    portal_items: List[Dict[str, object]],
    _allowed_domains: Tuple[str, ...],
) -> List[Dict[str, object]]:
    by_link: Dict[str, Dict[str, object]] = {}
    for it in portal_items:
        lk = str(it.get("link") or "").strip()
        if lk:
            by_link[lk] = it
    for it in harvest_hicx_portal_pages():
        lk = str(it.get("link") or "").strip()
        if lk and lk not in by_link:
            by_link[lk] = it
    stub = _maybe_corporate_stub()
    if stub:
        lk = str(stub.get("link") or "").strip()
        if lk and lk not in by_link:
            by_link[lk] = stub
    return list(by_link.values())
