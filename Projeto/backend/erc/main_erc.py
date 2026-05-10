from pathlib import Path
import sys
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs

ERC_APPLY_HUB = "https://erc.europa.eu/apply-grant"

NOISE_HINTS = [
    "privacy notice",
    "/news/",
    "/events/",
    "job opportunities",
    "vacancy",
    "sign in",
    "log in",
]

# Páginas de apoio / governança, não oportunidade de grant para investigador principal.
EXCLUDE_PATH_FRAGMENTS = [
    "/panel-members",
    "/independent-observers",
    "/science-journalism",
]

# Esquemas ERC e vias públicas de oportunidade (sem login).
ALLOWED_GRANT_SLUGS = frozenset(
    {
        "starting-grant",
        "consolidator-grant",
        "advanced-grant",
        "synergy-grant",
        "proof-concept",
        "erc-plus-grant",
        "additional-opportunities",
        "non-european-researchers",
        "erc-ukraine",
    }
)


def _erc_grant_scheme_url(url: str) -> bool:
    """True se for página de esquema /apply-grant/<slug> permitido (não hub, não apoio)."""
    low = (url or "").strip().lower()
    if "erc.europa.eu" not in low:
        return False
    if any(x in low for x in EXCLUDE_PATH_FRAGMENTS):
        return False
    try:
        path = urlparse(low).path.rstrip("/")
    except Exception:
        return False
    parts = [p for p in path.split("/") if p]
    if len(parts) < 2:
        return False
    if parts[0] != "apply-grant":
        return False
    return parts[1] in ALLOWED_GRANT_SLUGS


def _is_relevant_item(item: dict) -> bool:
    link = str(item.get("link") or "")
    if not _erc_grant_scheme_url(link):
        return False
    title = str(item.get("titulo") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    low_link = link.lower()
    text = f"{title} {desc} {low_link}"
    if any(k in text for k in NOISE_HINTS):
        return False
    if "funding opportunity" in text and "closed" in text:
        return False
    return True


def main():
    config = {
        "source_label": "ERC",
        "listing_urls": [
            ERC_APPLY_HUB,
        ],
        "keywords": [
            "grant",
            "funding",
            "call",
            "proposal",
            "research",
            "erc",
            "deadline",
            "starting",
            "consolidator",
            "advanced",
            "synergy",
            "proof of concept",
            "applicant",
            "researcher",
        ],
        "avoid_keywords": ["job", "press office", "media advisory", "panel member"],
        "link_url_exclude_substrings": [
            "/news/",
            "/events/",
            "/jobs/",
            "login",
            "sign-in",
            *EXCLUDE_PATH_FRAGMENTS,
        ],
        "link_url_must_contain_any": [
            "/apply-grant/",
        ],
        "link_path_min_depth": 2,
        "program_hint": "European Research Council",
        "allowed_domains": ["europa.eu"],
        "max_items": 12,
        "max_links_per_page": 120,
        "http_timeout": 35,
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
        print(f"[ERC] Falha na coleta: {exc}")
        raw = []
    items = [x for x in raw if _is_relevant_item(x)]
    if not items:
        print(
            "[ERC] Nenhum item com evidência de esquema apply-grant (URL antiga apply-grants corrigida)."
        )
    save_outputs(Path(__file__).parent, "erc", items)
    print(f"ERC: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
