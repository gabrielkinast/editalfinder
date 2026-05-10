"""Coleta segura BID Lab: chamadas, desafios e programas acionaveis."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs

SOURCE_KEY = "bid_lab"
LABEL = "BID Lab"


def _is_actionable(item: dict) -> bool:
    link = str(item.get("link") or "").lower()
    title = str(item.get("titulo") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if any(
        k in link
        for k in (
            "/news",
            "/noticias",
            "/blog",
            "/events",
            "/evento",
            "/about",
            "/contact",
            "/careers",
        )
    ):
        return False
    if any(k in text for k in ("press release", "media", "annual report")):
        return False
    path_ok = any(
        frag in link
        for frag in (
            "/call",
            "/calls",
            "/challenge",
            "/program",
            "/venture",
            "/apply",
            "/funding",
            "/innovation",
        )
    )
    call_markers = (
        "call",
        "open call",
        "apply",
        "application",
        "challenge",
        "proposal",
        "deadline",
        "submission",
        "funding",
        "grant",
        "venture",
        "startup",
        "innovation programme",
        "programa",
    )
    return path_ok or any(m in text for m in call_markers)


def main() -> None:
    config = {
        "source_label": LABEL,
        "listing_urls": [
            "https://bidlab.org/en/call-for-proposals",
            "https://bidlab.org/en/calls",
            "https://bidlab.org/en/innovation",
            "https://bidlab.org/en/venture",
        ],
        "keywords": [
            "call",
            "open",
            "apply",
            "application",
            "challenge",
            "proposal",
            "funding",
            "grant",
            "venture",
            "startup",
            "innovation",
            "programme",
        ],
        "avoid_keywords": ["news", "blog", "event", "privacy", "career", "contact"],
        "link_url_exclude_substrings": [
            "/news",
            "/noticias",
            "/blog",
            "/events",
            "/about",
            "/contact",
            "/careers",
            "/press",
        ],
        "allowed_domains": ["bidlab.org", "iadb.org", "idbinvest.org"],
        "program_hint": "BID Lab Innovation and Ventures",
        "max_items": 22,
        "max_links_per_page": 160,
        "http_timeout": 14,
        "setor_estrategico": "inovacao",
        "orgao_responsavel": "BID Lab",
        "instituicao": "Inter-American Development Bank Group",
        "orgao_contratante": "BID Lab",
        "tipo_oportunidade": "innovation_programme",
        "pais": "Internacional",
        "regiao": "multilateral",
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
        ex.setdefault("origem_portal", "BID Lab (bidlab.org)")
        ex.setdefault("url_detalhe", it.get("link"))
        ex.setdefault("url_listagem", "https://bidlab.org/en/calls")
        ex.setdefault("natureza_recurso", "nao_reembolsavel")
        it["tipo_recurso"] = it.get("tipo_recurso") or "grant"
        it["acao"] = it.get("acao") or "open_call"
        it["extras"] = ex
        filtered.append(it)

    save_outputs(Path(__file__).parent, SOURCE_KEY, filtered)
    print(f"[{LABEL}] Registros salvos: {len(filtered)}")


if __name__ == "__main__":
    main()
