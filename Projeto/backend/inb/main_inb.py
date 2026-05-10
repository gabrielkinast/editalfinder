from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from keyword_taxonomy import KEYWORDS_INTEREST


def main():
    config = {
        "source_label": "INB",
        "listing_urls": [
            "https://www.inb.gov.br/",
            "https://www.inb.gov.br/Licitacoes",
            "https://www.inb.gov.br/Noticias",
        ],
        "keywords": KEYWORDS_INTEREST + ["inb", "combustivel nuclear", "uranio", "ciclo do combustivel"],
        "avoid_keywords": [
            "manual tecnico",
            "concurso",
            "estagio",
            "acessibilidade",
            "pagina inicial",
            "pular para o conteudo",
            "perguntas frequentes",
            "fale conosco",
            "ouvidoria",
            "transparencia",
        ],
        "program_hint": "Nuclear",
        "allowed_domains": ["inb.gov.br"],
        "max_items": 20,
        "max_links_per_page": 120,
        "setor_estrategico": "ciclo_combustivel_nuclear",
        "orgao_responsavel": "INB",
        "instituicao": "Indústrias Nucleares do Brasil",
        "orgao_contratante": "INB",
        "tipo_oportunidade": "licitacao",
        "area_cientifica": ["quimica_nuclear", "engenharia_nuclear", "materiais"],
        "area_tecnologica": ["combustivel_nuclear", "mineracao_uranio", "radioprotecao"],
        "subtema_padrao": ["energia_nuclear", "materiais_nucleares"],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[INB] Falha na coleta: {exc}")
        items = []
    if not items:
        items = [
            {
                "titulo": "INB - Página de Licitações e Notícias",
                "descricao": "Índice público para oportunidades da INB no ciclo do combustível nuclear.",
                "link": "https://www.inb.gov.br/Licitacoes",
                "fonte": "INB",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "ciclo_combustivel_nuclear",
                "acao": "licitacao",
                "tipo_recurso": "contrato_publico",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "ciclo_combustivel_nuclear",
                    "tipo_oportunidade": "licitacao",
                    "tipo_recurso": "contrato_publico",
                    "url_listagem": "https://www.inb.gov.br/Licitacoes",
                    "url_detalhe": "https://www.inb.gov.br/Licitacoes",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[INB] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "inb", items)
    print(f"[INB] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
