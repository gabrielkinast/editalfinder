from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from keyword_taxonomy import KEYWORDS_INTEREST


def main():
    config = {
        "source_label": "NUCLEP",
        "listing_urls": [
            "https://www.nuclep.gov.br/",
            "https://www.nuclep.gov.br/licitacoes/",
            "https://www.nuclep.gov.br/noticias/",
        ],
        "keywords": KEYWORDS_INTEREST + ["nuclep", "industria pesada", "nuclear", "defesa"],
        "avoid_keywords": [
            "manual tecnico",
            "concurso",
            "estagio",
            "pagina inicial",
            "pular para o conteudo",
            "acessibilidade",
            "facebook",
            "instagram",
            "flickr",
            "ouvidoria",
            "codigo de etica",
        ],
        "program_hint": "Industria Nuclear e Defesa",
        "allowed_domains": ["nuclep.gov.br"],
        "max_items": 20,
        "max_links_per_page": 120,
        "setor_estrategico": "nuclear_industrial",
        "orgao_responsavel": "NUCLEP",
        "instituicao": "NUCLEP",
        "orgao_contratante": "NUCLEP",
        "tipo_oportunidade": "licitacao",
        "area_cientifica": ["engenharia_nuclear", "materiais", "fisica_aplicada"],
        "area_tecnologica": ["fabricacao_pesada", "materiais_avancados", "defesa"],
        "subtema_padrao": ["nuclear", "materiais_avancados"],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[NUCLEP] Falha na coleta: {exc}")
        items = []
    if not items:
        items = [
            {
                "titulo": "NUCLEP - Página de Licitações",
                "descricao": "Índice público para oportunidades de contratação da NUCLEP.",
                "link": "https://www.nuclep.gov.br/licitacoes/",
                "fonte": "NUCLEP",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "industria_nuclear_e_defesa",
                "acao": "licitacao",
                "tipo_recurso": "contrato_publico",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "nuclear_industrial",
                    "tipo_oportunidade": "licitacao",
                    "tipo_recurso": "contrato_publico",
                    "url_listagem": "https://www.nuclep.gov.br/licitacoes/",
                    "url_detalhe": "https://www.nuclep.gov.br/licitacoes/",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[NUCLEP] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "nuclep", items)
    print(f"[NUCLEP] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
