"""Coleta segura FONPLATA: financiamento, procurement e cooperacao tecnica acionavel."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs

SOURCE_KEY = "fonplata"
LABEL = "FONPLATA"


def _is_actionable(item: dict) -> bool:
    link = str(item.get("link") or "").lower()
    text = f"{item.get('titulo') or ''} {item.get('descricao') or ''} {link}".lower()
    if any(
        x in link
        for x in ("/noticias", "/news", "/blog", "/quienes-somos", "/about", "/contacto", "/eventos")
    ):
        return False
    if link.rstrip("/").endswith("/financiamiento") or "politicas-y-guias" in link:
        return False
    path_ok = any(
        frag in link
        for frag in (
            "/oportunidades",
            "/convocatorias",
            "/adquisiciones",
            "licit",
            "convocatoria",
            "procurement",
            "reclutamiento",
            "consultoria",
        )
    )
    if not path_ok:
        return False
    return any(
        k in text
        for k in (
            "convocatoria",
            "call",
            "apply",
            "application",
            "deadline",
            "project financing",
            "financiamiento",
            "cooperacion tecnica",
            "cooperación técnica",
            "procurement",
            "licitacion",
            "licitación",
            "tender",
            "submission",
            "proposal",
        )
    )


def main() -> None:
    config = {
        "source_label": LABEL,
        "listing_urls": [
            "https://www.fonplata.org/es/oportunidades",
            "https://www.fonplata.org/es/oportunidades/reclutamiento-de-personal",
            "https://www.fonplata.org/es/adquisiciones",
        ],
        "keywords": [
            "convocatoria",
            "oportunidad",
            "reclutamiento",
            "consultoria",
            "call",
            "apply",
            "application",
            "deadline",
            "financiamiento",
            "project financing",
            "procurement",
            "licitacion",
            "cooperacion",
            "proposal",
            "submission",
        ],
        "avoid_keywords": ["noticias", "news", "blog", "eventos", "about", "contacto"],
        "link_url_exclude_substrings": [
            "/noticias",
            "/news",
            "/blog",
            "/quienes-somos",
            "/about",
            "/contacto",
            "/eventos",
        ],
        "allowed_domains": ["fonplata.org"],
        "program_hint": "FONPLATA opportunities",
        "max_items": 18,
        "max_links_per_page": 200,
        "http_timeout": 14,
        "setor_estrategico": "desenvolvimento_regional",
        "orgao_responsavel": "FONPLATA",
        "instituicao": "FONPLATA Banco de Desarrollo",
        "orgao_contratante": "FONPLATA",
        "tipo_oportunidade": "project_financing",
        "pais": "Internacional",
        "regiao": "multilateral",
        "idioma_original": "es",
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
        ex.setdefault("origem_portal", "FONPLATA (fonplata.org)")
        ex.setdefault("url_detalhe", it.get("link"))
        ex.setdefault("url_listagem", "https://www.fonplata.org/es/convocatorias")
        if any(k in lk for k in ("adquisiciones", "licit", "procurement", "tender")):
            ex.setdefault("tipo_oportunidade", "procurement")
            it["tipo_recurso"] = "oportunidade_fornecedor"
            it["acao"] = "procurement"
        else:
            ex.setdefault("tipo_oportunidade", "project_financing")
            it["tipo_recurso"] = it.get("tipo_recurso") or "financiamento"
            it["acao"] = it.get("acao") or "open_call"
        it["extras"] = ex
        filtered.append(it)

    save_outputs(Path(__file__).parent, SOURCE_KEY, filtered)
    print(f"[{LABEL}] Registros salvos: {len(filtered)}")


if __name__ == "__main__":
    main()
