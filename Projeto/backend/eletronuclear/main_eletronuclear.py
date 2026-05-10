from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").strip().lower()
    text = f"{title} {str(item.get('descricao') or '').lower()} {str(item.get('link') or '').lower()}"
    if title in {"ir para o conteúdo 1", "ir para o conteudo 1", "ativar o modo mais acessível", "buscar", "pesquisar"}:
        return False
    if any(k in text for k in ("comando para ignorar faixa de opções", "seu navegador não pode executar javascript")):
        return False
    return any(k in text for k in ("chamada", "edital", "parceria", "p&d", "novos empreendimentos", "licit", ".pdf"))


def main():
    config = {
        "source_label": "ELETRONUCLEAR",
        "listing_urls": [
            "https://www.eletronuclear.gov.br/Paginas/canais-de-negocios.aspx",
            "https://www.eletronuclear.gov.br/Paginas/novos-empreendimentos.aspx",
            "https://www.eletronuclear.gov.br/Paginas/licitacoes-e-contratos.aspx",
        ],
        "keywords": [
            "edital",
            "chamada",
            "fomento",
            "programa",
            "pesquisa",
            "inovação",
            "p&d",
            "parceria",
            "nuclear",
        ],
        "avoid_keywords": [
            "concurso público",
            "estágio",
            "acessibilidade",
            "fale conosco",
            "ouvidoria",
        ],
        "program_hint": "Eletronuclear",
        "allowed_domains": ["eletronuclear.gov.br"],
        "max_items": 20,
        "max_links_per_page": 100,
        "setor_estrategico": "energia_nuclear",
        "orgao_responsavel": "Eletronuclear",
        "instituicao": "Eletronuclear",
        "orgao_contratante": "Eletronuclear",
        "tipo_oportunidade": "licitacao",
        "area_cientifica": ["engenharia_nuclear", "fisica_aplicada", "materiais"],
        "area_tecnologica": ["operacao_reatores", "seguranca_nuclear", "radioprotecao"],
        "subtema_padrao": ["energia_nuclear", "infraestrutura_critica"],
        "require_opportunity_signals": True,
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[ELETRONUCLEAR] Falha na coleta: {exc}")
        items = []
    items = [x for x in items if _is_relevant_item(x)]
    if not items:
        items = [
            {
                "titulo": "Eletronuclear - Página de Licitações e Oportunidades",
                "descricao": "Índice público para oportunidades da Eletronuclear.",
                "link": "https://www.eletronuclear.gov.br/pt-br",
                "fonte": "ELETRONUCLEAR",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "eletronuclear",
                "acao": "licitacao",
                "tipo_recurso": "contrato_publico",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "energia_nuclear",
                    "tipo_oportunidade": "licitacao",
                    "tipo_recurso": "contrato_publico",
                    "url_listagem": "https://www.eletronuclear.gov.br/pt-br",
                    "url_detalhe": "https://www.eletronuclear.gov.br/pt-br",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[ELETRONUCLEAR] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "eletronuclear", items)
    print(f"Eletronuclear: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
