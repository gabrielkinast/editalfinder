from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs, scrape_html_portal

GRANTS_API_URL = "https://api.grants.gov/v1/api/search2"

# Hub institucional: só listagem — nunca gravar como item final.
IARPA_HUB_URLS: Set[str] = {
    "https://www.iarpa.gov/research-programs",
    "https://www.iarpa.gov/research-programs/",
}

# Páginas explicativas / hub de engajamento — não são oportunidades concretas.
IARPA_SKIP_URLS: Set[str] = {
    "https://www.iarpa.gov/engage-with-us/proposers-days",
    "https://www.iarpa.gov/engage-with-us/proposers-days/",
}

DENY_PATH_MARKERS = (
    "/news",
    "/about",
    "/contact",
    "/careers",
    "/privacy",
    "/login",
)


def _session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["POST"]),
    )
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s


def _parse_us_date(raw: Optional[str]) -> Optional[str]:
    if not raw or not isinstance(raw, str):
        return None
    raw = raw.strip()
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", raw)
    if not m:
        return raw[:10] if len(raw) >= 10 else None
    mo, d, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        return datetime(y, mo, d).date().isoformat()
    except ValueError:
        return None


def _is_iarpa_hub_url(url: str) -> bool:
    u = (url or "").strip().split("#", 1)[0].rstrip("/").lower()
    return u in {x.rstrip("/").lower() for x in IARPA_HUB_URLS}


def _is_iarpa_skip_url(url: str) -> bool:
    u = (url or "").strip().split("#", 1)[0].rstrip("/").lower()
    if u in {x.rstrip("/").lower() for x in IARPA_SKIP_URLS}:
        return True
    return False


def _is_detail_iarpa_path(url: str) -> bool:
    """Aceita subpáginas de programa/oportunidade em iarpa.gov (não hub raiz)."""
    if "iarpa.gov" not in (url or "").lower():
        return False
    if _is_iarpa_hub_url(url):
        return False
    low = url.lower()
    if any(x in low for x in DENY_PATH_MARKERS):
        return False
    try:
        parts = [p for p in urlparse(url).path.strip("/").split("/") if p]
    except Exception:
        return False
    if len(parts) < 2:
        return False
    if parts[0] in ("research-programs", "programs", "solicitations", "baa", "opportunities", "funding", "challenges"):
        return True
    blob = "/".join(parts).lower()
    return any(
        x in blob
        for x in (
            "broad-agency-announcement",
            "proposers-day",
            "proposers_day",
            "solicitation",
            "funding",
            "opportunity",
            "challenge",
        )
    )


def _keep_grants_row(row: Dict[str, Any]) -> bool:
    """Filtra hits Grants.gov ligados a IARPA / IC / programas típicos (exclui DARPA órfão)."""
    title = str(row.get("title") or row.get("opportunityTitle") or "").strip()
    agency = str(row.get("agency") or row.get("agencyName") or "").strip()
    blob = f"{title} {agency}".lower()
    if "darpa" in agency.lower() and "iarpa" not in blob:
        return False
    if "iarpa" in blob:
        return True
    if "director of national intelligence" in agency.lower() or "odni" in agency.lower():
        return True
    tokens = (
        "tei-rex",
        "tei rex",
        "trojai",
        " elq",
        "supercables",
        "super cables",
        "entangled logical",
        "coherent superconducting",
        "intelligence community centers",
        "iccae",
    )
    tl = title.lower()
    if any(t in tl for t in tokens):
        return True
    return False


def _fetch_grants_iarpa_opportunities() -> List[Dict[str, Any]]:
    """Grants.gov search2 — campos reais: title, id, agency, number, openDate, closeDate, docType, oppStatus."""
    items: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    s = _session()
    payloads = [
        {"startRecordNum": 0, "rows": 45, "oppStatuses": "forecasted|posted|archived", "keyword": "IARPA"},
        {"startRecordNum": 0, "rows": 25, "oppStatuses": "forecasted|posted|archived", "keyword": "Intelligence Advanced Research Projects"},
    ]
    for payload in payloads:
        try:
            r = s.post(
                GRANTS_API_URL,
                headers={"Content-Type": "application/json", "User-Agent": "EditalFinderBot/1.0"},
                json=payload,
                timeout=35,
            )
            r.raise_for_status()
            data = r.json()
            rows = data.get("data", {}).get("oppHits", []) or data.get("oppHits", []) or []
        except Exception as exc:
            print(f"[IARPA] Grants.gov ({payload.get('keyword')}): {exc}")
            continue
        for row in rows:
            if not isinstance(row, dict) or not _keep_grants_row(row):
                continue
            title = str(row.get("title") or row.get("opportunityTitle") or "").strip()
            opp_id = row.get("id") or row.get("opportunityId")
            if not opp_id or not title:
                continue
            key = str(opp_id)
            if key in seen:
                continue
            seen.add(key)
            agency = str(row.get("agency") or row.get("agencyName") or "").strip()
            number = str(row.get("number") or row.get("fundingOpportunityNumber") or "").strip()
            doc_type = str(row.get("docType") or "").strip()
            opp_status = str(row.get("oppStatus") or "").strip()
            open_d = _parse_us_date(str(row.get("openDate") or ""))
            close_d = _parse_us_date(str(row.get("closeDate") or ""))
            link = f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={opp_id}"
            desc_parts = [
                title,
                f"Agency: {agency}" if agency else "",
                f"Opportunity number: {number}" if number else "",
                f"Document type: {doc_type}" if doc_type else "",
                f"Status on Grants.gov: {opp_status}" if opp_status else "",
                f"Posted: {open_d}" if open_d else "",
                f"Close: {close_d}" if close_d else "",
            ]
            descricao = " | ".join(p for p in desc_parts if p).strip()[:8000]
            items.append(
                {
                    "titulo": title[:280],
                    "descricao": descricao,
                    "link": link,
                    "fonte": "IARPA",
                    "data_publicacao": open_d,
                    "fim_inscricao": close_d,
                    "situacao": "Aberto" if opp_status == "posted" else "Em andamento",
                    "valor": None,
                    "programa": "IARPA",
                    "acao": "fomento_pesquisa",
                    "tipo_recurso": "fomento_pdi",
                    "extras": {
                        "pais": "Estados Unidos",
                        "idioma_original": "en",
                        "origem_portal": "IARPA (Grants.gov)",
                        "orgao_contratante": agency or "IARPA / US Government",
                        "nivel_sensibilidade": "publico_institucional",
                        "origem": link,
                        "metodo_extracao": "grants_gov_api",
                        "codigo_oportunidade": str(opp_id),
                        "numero_chamada": number or "",
                        "agency": agency or "",
                        "grants_gov_opp_id": str(opp_id),
                        "grants_gov_status": opp_status or "",
                        "natureza_recurso": "nao_reembolsavel",
                        "reembolsavel": False,
                        "grants_doc_type": doc_type,
                        "grants_opp_status": opp_status,
                    },
                }
            )
    return items


def _is_relevant_item(item: Dict[str, Any]) -> bool:
    lk_raw = str(item.get("link") or "")
    if _is_iarpa_hub_url(lk_raw) or _is_iarpa_skip_url(lk_raw):
        return False
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    title_link = f"{title} {link}"
    if any(k in title_link for k in ("about", "contact", "career", "privacy", "sam.gov/content/home")):
        return False
    if "grants.gov" in link and "oppid=" in link:
        return True
    if _is_detail_iarpa_path(str(item.get("link") or "")):
        return True
    return any(
        k in text
        for k in (
            "research program",
            "broad agency announcement",
            "baa",
            "solicitation",
            "proposal",
            "funding",
            "challenge",
            "proposers",
            "iarpa",
        )
    )


def main() -> None:
    print("[IARPA] Iniciando coleta (Grants.gov + listagem iarpa.gov como fonte de links)…")
    items: List[Dict[str, Any]] = []

    items.extend(_fetch_grants_iarpa_opportunities())
    print(f"[IARPA] Grants.gov: {len(items)} oportunidades após filtro.")

    scraped: List[Dict[str, Any]] = []
    try:
        scraped = scrape_html_portal(
            source_label="IARPA",
            country="US",
            listing_urls=["https://www.iarpa.gov/research-programs"],
            allowed_domains=["iarpa.gov"],
            extra_keywords=[
                "baa",
                "broad agency announcement",
                "research program",
                "solicitation",
                "proposal",
                "funding",
                "challenge",
                "proposers",
            ],
            max_items=28,
            max_listing_pages=3,
        )
    except Exception as exc:
        print(f"[IARPA] Scrape listagem: {exc}")

    seen_links = {str(x.get("link") or "").split("#", 1)[0].rstrip("/").lower() for x in items}
    for it in scraped:
        lk = str(it.get("link") or "").split("#", 1)[0].rstrip("/").lower()
        if not lk or lk in seen_links:
            continue
        if _is_iarpa_hub_url(str(it.get("link") or "")) or _is_iarpa_skip_url(str(it.get("link") or "")):
            continue
        if not _is_detail_iarpa_path(str(it.get("link") or "")):
            continue
        extras = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        extras.setdefault("origem_portal", "IARPA (iarpa.gov)")
        it["extras"] = extras
        it.setdefault("programa", "IARPA")
        it.setdefault("tipo_recurso", "fomento_pdi")
        items.append(it)
        seen_links.add(lk)

    items = [x for x in items if _is_relevant_item(x)]

    if not items:
        print("[IARPA] Nenhum item após filtros — não gravando hub / fallback genérico.")
    save_outputs(Path(__file__).parent, "iarpa", items)
    print(f"[IARPA] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
