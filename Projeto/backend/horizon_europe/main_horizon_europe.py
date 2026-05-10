from pathlib import Path
import re
import sys
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs

NOISE_HINTS = [
    "skip to main content",
    "cookie policy",
    "privacy statement",
    "/news/",
    "/events/",
    "/contact",
    "/help/",
    "search results",
    "sign in",
    "log in",
]

# Página estática pública do Funding & Tenders Portal (HTML com links para topic-details).
TOPIC_LIST_PUBLIC = (
    "https://ec.europa.eu/info/funding-tenders/opportunities/data/topic-list.html"
)

INSTITUTIONAL_PATH_MARKERS = [
    "/funding-programmes-and-open-calls/horizon-europe",
    "funding-programmes-and-open-calls/horizon-europe_",
    "/topic-search",
    "/topic-search?",
]


def _topic_slug(url: str) -> Optional[str]:
    if not url:
        return None
    m = re.search(r"/topic-details/([^/?#]+)", url, re.IGNORECASE)
    return m.group(1).strip().lower() if m else None


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if any(k in text for k in NOISE_HINTS):
        return False
    for m in INSTITUTIONAL_PATH_MARKERS:
        if m in link:
            return False
    if "topic-search" in link and "topic-details" not in link:
        return False
    if "topic-details/" not in link:
        return False
    if "/topic-details/horizon-" not in link:
        return False
    return any(
        k in text
        for k in [
            "horizon",
            "topic",
            "deadline",
            "submission",
            "grant",
            "work programme",
            "call for proposal",
            "funding",
            "budget",
        ]
    )


def _dedupe_by_topic_slug(items: list) -> list:
    seen: set[str] = set()
    out: list = []
    for it in items:
        slug = _topic_slug(str(it.get("link") or ""))
        key = slug or str(it.get("link") or "").lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def main():
    config = {
        "source_label": "HORIZON_EUROPE",
        "listing_urls": [TOPIC_LIST_PUBLIC],
        "keywords": [
            "call",
            "horizon",
            "funding",
            "grant",
            "innovation",
            "research",
            "topic",
            "tender",
            "europe",
            "deadline",
            "submission",
            "consortium",
            "work programme",
        ],
        "avoid_keywords": [
            "procurement contract",
            "tender award",
            "job opening",
            "career",
            "press release",
        ],
        "link_url_exclude_substrings": [
            "/news/",
            "/events/",
            "/cookies",
            "/privacy",
            "/contact",
            "/search?",
            "login",
            "sign-in",
            "/topic-search",
            "/funding-programmes-and-open-calls/horizon-europe",
        ],
        "link_url_must_contain_any": [
            "topic-details/",
        ],
        "link_url_must_contain_all": [
            "horizon-",
        ],
        "link_path_min_depth": 2,
        "program_hint": "Horizon Europe",
        "allowed_domains": ["europa.eu"],
        "max_items": 25,
        "max_links_per_page": 12000,
        "http_timeout": 90,
        "enrich_meta_tags": True,
        "setor_estrategico": "",
        "tipo_oportunidade": "",
        "area_cientifica": [],
        "area_tecnologica": [],
        "subtema_padrao": [],
        "pais": "União Europeia",
        "regiao": "Europa",
        "idioma_original": "en",
    }
    try:
        raw = scrape_source(config)
    except Exception as exc:
        print(f"[HORIZON_EUROPE] Falha na coleta: {exc}")
        raw = []
    items = [x for x in raw if _is_relevant_item(x)]
    items = _dedupe_by_topic_slug(items)
    if not items:
        print(
            "[HORIZON_EUROPE] Nenhum item com evidência de topic Horizon "
            f"(índice público: {TOPIC_LIST_PUBLIC})."
        )
    save_outputs(Path(__file__).parent, "horizon_europe", items)
    print(f"Horizon Europe: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
