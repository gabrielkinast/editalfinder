from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "IPEN",
        "listing_urls": [
            "https://www.gov.br/ipen/pt-br",
            "https://www.gov.br/ipen/pt-br/assuntos/noticias",
        ],
        "keywords": [
            "edital",
            "chamada",
            "fomento",
            "programa",
            "pesquisa",
            "nuclear",
            "radioisótopo",
            "convênio",
            "p&d",
            "pd&i",
        ],
        "avoid_keywords": [
            "concurso público",
            "estágio",
            "pregão",
            "licitação",
            "acessibilidade",
            "fale conosco",
            "página inicial",
        ],
        "program_hint": "IPEN-CNEN",
        "allowed_domains": ["gov.br"],
        "max_items": 20,
        "max_links_per_page": 100,
        "setor_estrategico": "nuclear_civil",
        "orgao_responsavel": "IPEN",
        "instituicao": "IPEN-CNEN",
        "orgao_contratante": "IPEN",
        "tipo_oportunidade": "chamada_publica",
        "area_cientifica": ["fisica_nuclear", "quimica_nuclear", "radioquimica"],
        "area_tecnologica": ["radiofarmacos", "materiais_avancados", "radioprotecao"],
        "subtema_padrao": ["energia_nuclear", "saude_nuclear"],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[IPEN] Falha na coleta: {exc}")
        items = []
    if not items:
        items = [
            {
                "titulo": "IPEN - Página de Oportunidades",
                "descricao": "Índice público de chamadas, projetos e programas do IPEN.",
                "link": "https://www.gov.br/ipen/pt-br",
                "fonte": "IPEN",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "ipen_cnen",
                "acao": "chamada_publica",
                "tipo_recurso": "fomento",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "nuclear_civil",
                    "tipo_oportunidade": "chamada_publica",
                    "tipo_recurso": "fomento",
                    "url_listagem": "https://www.gov.br/ipen/pt-br",
                    "url_detalhe": "https://www.gov.br/ipen/pt-br",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[IPEN] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "ipen", items)
    print(f"IPEN: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
