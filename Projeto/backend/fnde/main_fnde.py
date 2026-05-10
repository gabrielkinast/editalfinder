from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    text = f"{title} {str(item.get('descricao') or '').lower()} {link}"
    if "/pt-br/orgaos/" in link:
        return False
    if "acoes-e-programas" in link and "chamada" not in text and "edital" not in text:
        return False
    if any(k in text for k in ("carta de serviços", "serviços disponíveis", "solicitar a")):
        return False
    if "fndo-nacional-de-desenvolvimento-da-educacao" in link:
        return False
    if any(k in text for k in ("ouvidoria", "mapa do site", "fale conosco")):
        return False
    return any(k in text for k in ("edital", "chamada", "inscri", "submiss", "sele", ".pdf"))

def main():
    config = {
        "source_label": "FNDE",
        "listing_urls": [
            "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas",
            "https://www.gov.br/fnde/pt-br/acesso-a-informacao/chamadas-publicas",
        ],
        "keywords": ["edital", "chamada", "programa", "fomento", "financiamento", "educacao", "municipio"],
        "avoid_keywords": ["concurso", "estagio", "pregao", "licitacao"],
        "program_hint": "FNDE",
        "allowed_domains": ["gov.br"],
        "max_items": 30,
        "max_links_per_page": 180,
        "setor_estrategico": "educacao_publica",
        "orgao_responsavel": "FNDE",
        "instituicao": "Fundo Nacional de Desenvolvimento da Educação",
        "orgao_contratante": "FNDE",
        "tipo_oportunidade": "chamada_publica",
        "area_cientifica": ["educacao", "politicas_publicas"],
        "area_tecnologica": ["gestao_educacional", "infraestrutura_escolar"],
        "subtema_padrao": ["fomento", "educacao", "investimento_publico"],
        "require_opportunity_signals": True,
    }
    raw_items = []
    try:
        items = scrape_source(config)
        raw_items = list(items)
    except Exception as exc:
        print(f"[FNDE] Falha na coleta: {exc}")
        items = []
    items = [x for x in items if _is_relevant_item(x)]
    if not items:
        items = [
            {
                "titulo": "FNDE - Página de Programas e Chamadas",
                "descricao": "Índice público de programas, editais e chamadas do FNDE.",
                "link": "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas",
                "fonte": "FNDE",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "fnde",
                "acao": "chamada_publica",
                "tipo_recurso": "fomento",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "educacao_publica",
                    "tipo_oportunidade": "chamada_publica",
                    "tipo_recurso": "fomento",
                    "url_listagem": "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas",
                    "url_detalhe": "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[FNDE] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "fnde", items)
    print(f"[FNDE] Registros salvos: {len(items)}")

if __name__ == "__main__":
    main()
