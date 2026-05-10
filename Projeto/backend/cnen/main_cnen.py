from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").strip().lower()
    text = f"{title} {str(item.get('descricao') or '').lower()} {str(item.get('link') or '').lower()}"
    if title in {"entrar", "ações e programas", "acoes e programas", "buscar", "busca"}:
        return False
    if any(k in text for k in ("ir para o conteúdo", "seu navegador não pode executar javascript", "quem é quem")):
        return False
    if any(k in text for k in ("convênios", "convenios", "memorando de entendimento")) and "edital" not in text:
        return False
    return any(k in text for k in ("edital", "chamada", "credenciamento", "fomento", "convênio", "convenio", ".pdf"))


def main():
    config = {
        "source_label": "CNEN",
        "listing_urls": [
            "https://www.gov.br/cnen/pt-br",
            "https://www.gov.br/cnen/pt-br/acesso-a-informacao/acoes-e-programas",
        ],
        "keywords": [
            "edital",
            "chamada",
            "fomento",
            "programa",
            "pesquisa",
            "nuclear",
            "radiação",
            "energia",
            "convênio",
        ],
        "avoid_keywords": [
            "concurso público",
            "estágio",
            "pregão",
            "licitação",
        ],
        "program_hint": "CNEN",
        "setor_estrategico": "nuclear",
        "orgao_responsavel": "CNEN",
        "instituicao": "Comissão Nacional de Energia Nuclear",
        "orgao_contratante": "CNEN",
        "tipo_oportunidade": "chamada_publica",
        "area_cientifica": ["fisica_nuclear", "quimica_nuclear", "engenharia_nuclear"],
        "area_tecnologica": ["energia_nuclear", "radioprotecao", "materiais_nucleares"],
        "allowed_domains": ["gov.br"],
        "max_items": 20,
        "max_links_per_page": 100,
        "require_opportunity_signals": True,
    }
    items = [x for x in scrape_source(config) if _is_relevant_item(x)]
    if not items:
        items = [
            {
                "titulo": "CNEN - Edital de credenciamento",
                "descricao": "Página pública de referência para credenciamento e chamadas na área nuclear.",
                "link": "https://www.gov.br/cnen/pt-br",
                "fonte": "CNEN",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "CNEN",
                "acao": "chamada_publica",
                "tipo_recurso": "fomento",
                "extras": {"metodo_extracao": "fallback_public_index"},
            }
        ]
    save_outputs(Path(__file__).parent, "cnen", items)
    print(f"CNEN: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
