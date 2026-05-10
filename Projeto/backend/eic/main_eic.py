"""Coleta segura EIC: calls do European Innovation Council."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs

SOURCE_KEY = "eic"
LABEL = "EIC"


def _is_actionable(item: dict) -> bool:
    link = str(item.get("link") or "").lower()
    text = f"{item.get('titulo') or ''} {item.get('descricao') or ''} {link}".lower()
    if any(x in link for x in ("/news", "/events", "/about", "/contact", "/faq", "/team")):
        return False
    if "eic.ec.europa.eu" not in link and "ec.europa.eu" not in link:
        return False
    return any(
        m in text
        for m in (
            "call",
            "open call",
            "deadline",
            "apply",
            "application",
            "submission",
            "pathfinder",
            "accelerator",
            "transition",
            "funding",
            "grant",
        )
    )


def main() -> None:
    config = {
        "source_label": LABEL,
        "listing_urls": [
            "https://eic.ec.europa.eu/eic-funding-opportunities_en",
            "https://eic.ec.europa.eu/eic-funding-opportunities/eic-accelerator_en",
            "https://eic.ec.europa.eu/eic-funding-opportunities/eic-pathfinder_en",
            "https://eic.ec.europa.eu/eic-funding-opportunities/eic-transition_en",
        ],
        "keywords": [
            "call",
            "open call",
            "deadline",
            "apply",
            "application",
            "submission",
            "accelerator",
            "pathfinder",
            "transition",
            "funding",
            "grant",
            "innovation",
        ],
        "avoid_keywords": ["news", "event", "about", "contact", "faq"],
        "link_url_exclude_substrings": [
            "/news",
            "/events",
            "/about",
            "/contact",
            "/faq",
            "/team",
        ],
        "allowed_domains": ["eic.ec.europa.eu", "ec.europa.eu"],
        "program_hint": "European Innovation Council",
        "max_items": 14,
        "max_links_per_page": 100,
        "http_timeout": 12,
        "setor_estrategico": "inovacao",
        "orgao_responsavel": "European Innovation Council",
        "instituicao": "European Commission",
        "orgao_contratante": "EIC",
        "tipo_oportunidade": "funding_opportunity",
        "pais": "Uniao Europeia",
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
        ex.setdefault("origem_portal", "EIC (eic.ec.europa.eu)")
        ex.setdefault("url_detalhe", it.get("link"))
        ex.setdefault("url_listagem", "https://eic.ec.europa.eu/eic-funding-opportunities_en")
        ex.setdefault("tipo_oportunidade", "funding_opportunity")
        ex.setdefault("natureza_recurso", "nao_reembolsavel")
        it["tipo_recurso"] = "grant"
        it["acao"] = "apply"
        it["extras"] = ex
        filtered.append(it)

    save_outputs(Path(__file__).parent, SOURCE_KEY, filtered)
    print(f"[{LABEL}] Registros salvos: {len(filtered)}")


if __name__ == "__main__":
    main()
