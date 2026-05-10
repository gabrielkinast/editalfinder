"""Coleta segura Eureka Network: calls de P&D colaborativo."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs

SOURCE_KEY = "eureka_network"
LABEL = "Eureka Network"


def _is_actionable(item: dict) -> bool:
    link = str(item.get("link") or "").lower()
    text = f"{item.get('titulo') or ''} {item.get('descricao') or ''} {link}".lower()
    if any(x in link for x in ("/news", "/about", "/events", "/contact", "/faq", "/success-story")):
        return False
    call_markers = (
        "call",
        "open call",
        "deadline",
        "apply",
        "application",
        "proposal",
        "submission",
        "eurostars",
        "globalstars",
        "network projects",
        "cluster call",
    )
    return any(m in text for m in call_markers)


def main() -> None:
    config = {
        "source_label": LABEL,
        "listing_urls": [
            "https://www.eurekanetwork.org/open-calls/",
            "https://www.eurekanetwork.org/programmes/eurostars/",
            "https://www.eurekanetwork.org/programmes/globalstars/",
        ],
        "keywords": [
            "open call",
            "call",
            "apply",
            "application",
            "deadline",
            "proposal",
            "submission",
            "eurostars",
            "globalstars",
            "network projects",
            "cluster",
            "funding",
        ],
        "avoid_keywords": ["news", "about", "event", "contact", "faq", "story"],
        "link_url_exclude_substrings": [
            "/news",
            "/about",
            "/events",
            "/contact",
            "/faq",
            "/success-story",
        ],
        "allowed_domains": ["eurekanetwork.org"],
        "program_hint": "Eureka Collaborative R&D Calls",
        "max_items": 24,
        "max_links_per_page": 180,
        "http_timeout": 12,
        "setor_estrategico": "ciencia_tecnologia",
        "orgao_responsavel": "Eureka Network",
        "instituicao": "Eureka Network",
        "orgao_contratante": "Eureka Network",
        "tipo_oportunidade": "call_for_proposals",
        "pais": "Internacional",
        "regiao": "europa",
        "idioma_original": "en",
        "enrich_meta_tags": True,
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[{LABEL}] Falha na coleta: {exc}")
        items = []

    filtered = []
    seen = set()
    for it in items:
        if not _is_actionable(it):
            continue
        lk = str(it.get("link") or "").strip().lower()
        if not lk or lk in seen:
            continue
        seen.add(lk)
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        ex.setdefault("origem_portal", "Eureka Network (eurekanetwork.org)")
        ex.setdefault("url_detalhe", it.get("link"))
        ex.setdefault("url_listagem", "https://www.eurekanetwork.org/open-calls/")
        ex.setdefault("tipo_oportunidade", "call_for_proposals")
        ex.setdefault("natureza_recurso", "nao_reembolsavel")
        it["tipo_recurso"] = "grant"
        it["acao"] = "submit_proposal"
        it["extras"] = ex
        filtered.append(it)

    save_outputs(Path(__file__).parent, SOURCE_KEY, filtered)
    print(f"[{LABEL}] Registros salvos: {len(filtered)}")


if __name__ == "__main__":
    main()
