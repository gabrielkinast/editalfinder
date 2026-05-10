from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_intel import build_defense_extras, detect_keywords
from defense_source_common import save_outputs, scrape_html_portal

API_URL = "https://api.www.sbir.gov/public/api/solicitations"
PAGE_ROWS = 60
MAX_OFFSETS = [0, 60, 120, 180]

# Páginas de apoio / API / FAQ — nunca devem ser tratadas como oportunidade (Recovery A).
_SBIR_GOV_DENY_PATH_PREFIXES: tuple[str, ...] = (
    "/api",
    "/data-resources",
    "/participating-agencies",
    "/impact",
    "/faq",
    "/about",
    "/company-registration",
    "/awards",
    "/portfolio",
    "/resources",
    "/lab2market",
    "/community",
    "/success-stories",
    "/events-listing",
    "/events",
    "/news",
    "/program-highlights",
)


def _is_sbir_opportunity_detail_url(url: str) -> bool:
    """No fallback HTML: só páginas de topic/solicitation com identificador (não hubs institucionais)."""
    try:
        path = (urlparse((url or "").lower()).path or "").rstrip("/")
    except Exception:
        return False
    if re.match(r"^/topics/\d+", path):
        return True
    if path.startswith("/solicitation/") and len(path) > len("/solicitation/"):
        return True
    parts = [p for p in path.split("/") if p]
    if len(parts) >= 2 and parts[0] == "solicitations" and parts[1]:
        return True
    return False


def _is_sbir_support_or_hub_url(url: str) -> bool:
    low = (url or "").lower()
    if "sbir.gov" not in low:
        return False
    try:
        path = urlparse(low).path or ""
    except Exception:
        path = low.split("sbir.gov", 1)[-1] if "sbir.gov" in low else low
    p = path.rstrip("/").lower() or "/"
    if p == "/topics":
        return True
    return any(p.startswith(pref) for pref in _SBIR_GOV_DENY_PATH_PREFIXES)


def _is_relevant_html_item(item: Dict[str, object]) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if any(k in text for k in ("login", "register", "sign in", "overview", "app-landing", "company-registration")):
        return False
    noise_titles = (
        "success stories",
        "news and events",
        "news & events",
        "events",
        "our impact",
        "data resources",
    )
    if title.strip() in noise_titles or any(nt in title for nt in ("success stor", "event listing")):
        return False
    return any(k in text for k in ("sbir", "sttr", "solicitation", "topic", "open", "funding", "phase i", "phase ii"))


def _session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_sbir() -> List[Dict[str, object]]:
    headers = {"User-Agent": "EditalFinderBot/1.0"}
    items: List[Dict[str, object]] = []
    seen = set()
    session = _session()
    try:
        all_rows = []
        for offset in MAX_OFFSETS:
            response = session.get(
                API_URL,
                headers=headers,
                params={"agency": "DoD", "rows": PAGE_ROWS, "start": offset},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            rows = data if isinstance(data, list) else data.get("data", [])
            if not rows:
                break
            all_rows.extend(rows)
        for row in all_rows:
            title = str(row.get("solicitation_title") or row.get("title") or row.get("program_title") or "").strip()
            desc = str(row.get("description") or title)
            merged = f"{title} {desc}"
            if not detect_keywords(merged):
                continue
            link = str(row.get("solicitation_agency_url") or row.get("url") or row.get("link") or "https://www.sbir.gov/")
            topic_code = row.get("topic_code") or row.get("solicitation_number")
            dedupe_key = topic_code or link or title
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            extras = build_defense_extras(
                text=merged,
                source_name="DoD SBIR/STTR",
                origem=link,
                pais="US",
                orgao_contratante=str(row.get("agency") or row.get("branch") or "DoD"),
            )
            extras["topic_code"] = row.get("topic_code")
            extras["codigo_oportunidade"] = str(row.get("solicitation_number") or row.get("topic_code") or "")
            extras["numero_chamada"] = str(row.get("solicitation_number") or "")
            extras["modalidade"] = str(row.get("program") or "SBIR/STTR")
            extras["publico_alvo"] = "Small Business / Pesquisa aplicada"
            extras["objetivo"] = title[:600]
            extras["url_listagem"] = API_URL
            extras["url_detalhe"] = link
            extras["metodo_extracao"] = "api_rest"
            if _is_sbir_support_or_hub_url(link):
                continue
            items.append(
                {
                    "titulo": title[:250] or "DoD SBIR/STTR Opportunity",
                    "descricao": desc[:3500],
                    "link": link,
                    "fonte": "DoD SBIR/STTR",
                    "data_publicacao": str(row.get("open_date") or row.get("release_date") or "")[:10] or None,
                    "fim_inscricao": str(row.get("close_date") or row.get("application_due_date") or "")[:10] or None,
                    "situacao": "Aberto",
                    "valor": row.get("award_amount"),
                    "programa": "base_industrial_defesa",
                    "acao": "programa_pdi",
                    "tipo_recurso": "funding_opportunity",
                    "extras": extras,
                }
            )
    except Exception as exc:
        print(f"[DOD_SBIR_STTR] Falha ao consultar API: {exc}")
        html_items = scrape_html_portal(
            source_label="DoD SBIR/STTR",
            country="US",
            listing_urls=[
                "https://www.sbir.gov/topics",
                "https://www.sbir.gov/solicitations",
            ],
            allowed_domains=["sbir.gov"],
            extra_keywords=["sbir", "sttr", "topic", "solicitation", "funding", "phase i", "phase ii"],
            max_items=28,
            max_listing_pages=2,
        )
        if html_items:
            for it in html_items:
                lk = str(it.get("link") or "")
                if _is_sbir_support_or_hub_url(lk):
                    continue
                if not _is_sbir_opportunity_detail_url(lk):
                    continue
                if not _is_relevant_html_item(it):
                    continue
                it["programa"] = "base_industrial_defesa"
                it["acao"] = "programa_pdi"
                it["tipo_recurso"] = "fomento_investimento"
                extras = it.get("extras") if isinstance(it.get("extras"), dict) else {}
                extras["tipo_recurso"] = "fomento_investimento"
                extras["natureza_recurso"] = "nao_reembolsavel"
                extras["reembolsavel"] = False
                extras["observacoes"] = "Coleta via fallback HTML por limitação 429 na API."
                it["extras"] = extras
                items.append(it)
        # Sem índice /topics como edital: hub não é oportunidade acionável (Recovery A).
    return items


def main() -> None:
    print("[DOD_SBIR_STTR] Iniciando coleta por API...")
    items = fetch_sbir()
    save_outputs(Path(__file__).parent, "dod_sbir_sttr", items)
    print(f"[DOD_SBIR_STTR] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
