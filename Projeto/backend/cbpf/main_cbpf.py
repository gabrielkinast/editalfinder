from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def main():
    config = {
        "source_label": "CBPF",
        # Conteúdo institucional e oportunidades estão principalmente no gov.br
        "listing_urls": [
            "https://www.gov.br/cbpf/pt-br/acesso-a-informacao/acoes-e-programas",
            "https://www.gov.br/cbpf/pt-br/acesso-a-informacao/acoes-e-programas/programas",
            "https://www.cbpf.br/",
        ],
        "keywords": [
            "edital",
            "chamada",
            "bolsa",
            "programa",
            "pesquisa",
            "física",
            "fomento",
            "evento",
            "oportunidade",
            "mestrado",
            "doutorado",
            "pos",
            "workshop",
        ],
        "avoid_keywords": [
            "concurso público",
            "estágio",
            "acessibilidade",
            "página inicial",
            "fale conosco",
        ],
        "program_hint": "CBPF",
        "allowed_domains": ["gov.br", "cbpf.br"],
        "max_items": 20,
        "max_links_per_page": 100,
        "setor_estrategico": "ciencia_fisica",
        "orgao_responsavel": "CBPF",
        "instituicao": "Centro Brasileiro de Pesquisas Físicas",
        "orgao_contratante": "CBPF",
        "tipo_oportunidade": "chamada_publica",
        "area_cientifica": ["fisica", "fisica_nuclear", "materiais"],
        "area_tecnologica": ["instrumentacao_cientifica", "aceleradores", "tecnologias_quanticas"],
        "subtema_padrao": ["fisica", "pesquisa_aplicada"],
        "require_opportunity_signals": True,
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[CBPF] Falha na coleta: {exc}")
        items = []
    if not items:
        items = [
            {
                "titulo": "CBPF - Página de Oportunidades",
                "descricao": "Índice público de programas e oportunidades do CBPF.",
                "link": "https://www.gov.br/cbpf/pt-br",
                "fonte": "CBPF",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "cbpf",
                "acao": "chamada_publica",
                "tipo_recurso": "fomento",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "ciencia_fisica",
                    "tipo_oportunidade": "chamada_publica",
                    "tipo_recurso": "fomento",
                    "url_listagem": "https://www.gov.br/cbpf/pt-br",
                    "url_detalhe": "https://www.gov.br/cbpf/pt-br",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[CBPF] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "cbpf", items)
    print(f"CBPF: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
