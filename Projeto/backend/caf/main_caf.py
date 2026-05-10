"""Coleta segura CAF: programas, chamadas e oportunidades acionaveis."""
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs

SOURCE_KEY = "caf"
LABEL = "CAF"


def _is_actionable(item: dict) -> bool:
    link = str(item.get("link") or "").lower()
    text = f"{item.get('titulo') or ''} {item.get('descricao') or ''} {link}".lower()
    if any(
        x in link
        for x in ("/sala-de-prensa", "/noticias", "/blog", "/acerca-de", "/contacto", "/eventos", "/about")
    ):
        return False
    if any(x in text for x in ("press release", "comunicado", "evento", "webinar")):
        return False
    path_ok = any(
        frag in link
        for frag in (
            "convocatoria",
            "convocatorias",
            "oportunidades-laborales-y-procurement",
            "procurement",
            "licit",
            "concurso",
            "call-for",
            "funding",
        )
    )
    return path_ok or any(
        k in text
        for k in (
            "convocatoria",
            "call",
            "apply",
            "application",
            "deadline",
            "challenge",
            "proposal",
            "financing",
            "project financing",
            "procurement",
            "concurso",
            "programa",
            "cooperacion tecnica",
            "cooperación técnica",
        )
    )


def main() -> None:
    config = {
        "source_label": LABEL,
        "listing_urls": [
            "https://www.caf.com/es/trabaja-con-nosotros/convocatorias/",
            "https://www.caf.com/es/actualidad/convocatorias/",
            "https://www.caf.com/es/oportunidades-laborales-y-procurement/",
        ],
        "keywords": [
            "convocatoria",
            "convocatorias",
            "call",
            "application",
            "deadline",
            "challenge",
            "funding",
            "financing",
            "procurement",
            "tender",
            "project",
            "cooperacion",
            "innovation",
            "licit",
        ],
        "avoid_keywords": ["news", "noticias", "blog", "evento", "press", "acerca de"],
        # Nao excluir /trabaja-con-nosotros em geral: convocatorias oficiais ficam nesse path.
        "link_url_exclude_substrings": [
            "/noticias",
            "/blog",
            "/sala-de-prensa",
            "/acerca-de",
            "/contacto",
            "/eventos",
            "/vacantes",
            "/empleos",
        ],
        "allowed_domains": ["caf.com"],
        "program_hint": "CAF calls and financing",
        "max_items": 22,
        "max_links_per_page": 200,
        "http_timeout": 14,
        "setor_estrategico": "desenvolvimento_regional",
        "orgao_responsavel": "CAF",
        "instituicao": "Banco de Desarrollo de America Latina y el Caribe",
        "orgao_contratante": "CAF",
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
        ex.setdefault("origem_portal", "CAF (caf.com)")
        ex.setdefault("url_detalhe", it.get("link"))
        ex.setdefault("url_listagem", "https://www.caf.com/es/actualidad/convocatorias/")
        if "procurement" in lk or "licit" in lk or "tender" in lk:
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
