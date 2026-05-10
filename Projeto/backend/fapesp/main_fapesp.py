from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").strip().lower()
    text = f"{title} {str(item.get('descricao') or '').lower()} {str(item.get('link') or '').lower()}"
    if title in {"ops... ocorreu um erro home", "home", "buscar", "busca", "entrar"}:
        return False
    if any(k in text for k in ("ocorreu um erro", "ir para o conteúdo", "javascript")):
        return False
    if "carta de serviços" in text:
        return False
    return any(k in text for k in ("chamada", "edital", "bolsa", "auxílio", "auxilio", "fomento", ".pdf"))


def main():
    config = {
        "source_label": "FAPESP",
        "listing_urls": [
            "https://fapesp.br/chamadas/",
            "https://fapesp.br/oportunidades/",
        ],
        "keywords": ["chamada", "oportunidade", "auxílio", "bolsa", "edital", "fomento"],
        "avoid_keywords": ["licitação", "pregão", "concurso"],
        "program_hint": "FAPESP",
        "allowed_domains": ["fapesp.br"],
        "max_items": 30,
        "max_links_per_page": 180,
        "setor_estrategico": "ciencia_tecnologia_inovacao",
        "orgao_responsavel": "FAPESP",
        "instituicao": "Fundação de Amparo à Pesquisa do Estado de São Paulo",
        "orgao_contratante": "FAPESP",
        "tipo_oportunidade": "chamada_publica",
        "area_cientifica": ["ciencia", "tecnologia", "inovacao"],
        "area_tecnologica": ["pdi", "inovacao"],
        "subtema_padrao": ["bolsa", "fomento", "pesquisa", "auxilio"],
        "require_opportunity_signals": True,
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[FAPESP] Falha na coleta: {exc}")
        items = []
    items = [x for x in items if _is_relevant_item(x)]
    for item in items:
        t = str(item.get("titulo") or "")
        if "Home Financiamento à pesquisa" in t:
            item["titulo"] = "FAPESP - Chamadas de Propostas"
    if not items:
        items = [
            {
                "titulo": "FAPESP - Chamadas e Oportunidades",
                "descricao": "Índice público de chamadas, auxílios e bolsas da FAPESP.",
                "link": "https://fapesp.br/chamadas/",
                "fonte": "FAPESP",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "fapesp",
                "acao": "chamada_publica",
                "tipo_recurso": "fomento",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "ciencia_tecnologia_inovacao",
                    "tipo_oportunidade": "chamada_publica",
                    "tipo_recurso": "fomento",
                    "url_listagem": "https://fapesp.br/chamadas/",
                    "url_detalhe": "https://fapesp.br/chamadas/",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[FAPESP] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "fapesp", items)
    print(f"[FAPESP] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
