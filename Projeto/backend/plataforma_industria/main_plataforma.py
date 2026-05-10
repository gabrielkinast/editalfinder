from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").strip().lower()
    link = str(item.get("link") or "").strip().lower()
    text = f"{title} {str(item.get('descricao') or '').lower()} {link}"
    if title in {"home", "resultados", "categorias", "edições", "edicoes", "interlocutores regionais"}:
        return False
    if any(k in text for k in ("tutorial do sistema", "resultado final", "ver resultados anteriores")):
        return False
    # Índice genérico da plataforma (sem /categoria/)
    if link.rstrip("/").endswith("/canais/plataforma-inovacao-para-industria") and "/categoria/" not in link:
        return False
    if "/plataforma-inovacao-para-industria/resultados" in link or "/plataforma-inovacao-para-industria/edicoes" in link:
        return False
    return any(k in text for k in ("chamada", "edital", "inscri", "submiss", "aberta", ".pdf", "programa", "fomento"))


def main():
    config = {
        "source_label": "PLATAFORMA_INDUSTRIA",
        "listing_urls": [
            "https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/",
            "https://www.portaldaindustria.com.br/senai/canais/chamadas-publicas/",
        ],
        "keywords": [
            "edital",
            "chamada",
            "inovacao",
            "inovação",
            "fomento",
            "subvencao",
            "subvenção",
            "empresa",
            "startup",
            "industria",
            "indústria",
            "credito",
            "crédito",
            "financiamento",
            "programa",
            "projeto",
            "senai",
            "plataforma",
            "smart",
            "rota",
            "finep",
            "bndes",
            "inscri",
            "seleção",
            "selecao",
        ],
        "avoid_keywords": ["estagio", "estágio", "ouvidoria", "acessibilidade"],
        "program_hint": "Plataforma Inovação para Indústria",
        "allowed_domains": ["portaldaindustria.com.br"],
        "max_items": 24,
        "max_links_per_page": 200,
        "http_timeout": 22,
        "link_url_must_contain_any": [
            "/senai/canais/",
            "/canais/plataforma-inovacao-para-industria/",
        ],
        "link_url_exclude_substrings": [
            "/tag/",
            "?s=",
            "facebook.com",
            "linkedin.com",
            "instagram.com",
            "twitter.com",
            "whatsapp.com",
            "plataforma-inovacao-para-industria/resultados",
            "plataforma-inovacao-para-industria/edicoes",
        ],
        "link_path_min_depth": 3,
        "setor_estrategico": "industria_inovacao",
        "orgao_responsavel": "CNI/SENAI/SEBRAE",
        "instituicao": "Plataforma Inovação para Indústria",
        "orgao_contratante": "Sistema Indústria",
        "tipo_oportunidade": "chamada_publica",
        "area_cientifica": ["engenharia", "materiais", "computacao_aplicada"],
        "area_tecnologica": ["transformacao_digital", "industria_4_0", "inovacao_aberta"],
        "subtema_padrao": ["inovacao_industrial", "startups", "pd_i"],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[PLATAFORMA_INDUSTRIA] Falha na coleta: {exc}")
        items = []
    items = [x for x in items if _is_relevant_item(x)]
    if not items:
        print("[PLATAFORMA_INDUSTRIA] Nenhum item coletado (sem fallback de índice genérico).")
    save_outputs(Path(__file__).parent, "plataforma", items)
    print(f"[PLATAFORMA_INDUSTRIA] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
