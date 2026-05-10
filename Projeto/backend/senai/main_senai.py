from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "SENAI",
        "listing_urls": [
            "https://www.portaldaindustria.com.br/senai/canais/chamadas-publicas/",
            "https://www.portaldaindustria.com.br/senai/canais/editais/",
            "https://www.portaldaindustria.com.br/canais/plataforma-inovacao-para-industria/",
        ],
        "keywords": [
            "edital",
            "chamada",
            "inovação",
            "inovacao",
            "tecnologia",
            "fomento",
            "pesquisa",
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
        # Evitar licitação de compras; não bloquear "concurso" (pode haver concursos de inovação).
        "avoid_keywords": ["licitação", "licitacao", "pregão", "pregao"],
        "program_hint": "SENAI",
        "allowed_domains": ["portaldaindustria.com.br"],
        "max_items": 22,
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
        # Remove URL com só 2 segmentos de caminho (ex.: hub /canais/plataforma.../).
        "link_path_min_depth": 3,
        "setor_estrategico": "industria_inovacao",
        "orgao_responsavel": "SENAI",
        "instituicao": "Serviço Nacional de Aprendizagem Industrial",
        "orgao_contratante": "SENAI",
        "tipo_oportunidade": "chamada_publica",
        "area_cientifica": ["engenharia", "materiais", "computacao_aplicada"],
        "area_tecnologica": ["inovacao_industrial", "manufatura_avancada", "transformacao_digital"],
        "subtema_padrao": ["fomento", "inovacao", "pd_i"],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[SENAI] Falha na coleta: {exc}")
        items = []
    if not items:
        print("[SENAI] Nenhum item coletado (sem fallback de página índice).")
    save_outputs(Path(__file__).parent, "senai", items)
    print(f"SENAI: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
