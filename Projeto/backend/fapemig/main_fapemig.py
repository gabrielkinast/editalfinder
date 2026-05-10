from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs
from keyword_taxonomy import KEYWORDS_INTEREST


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if any(k in text for k in ("fundação de amparo à pesquisa do estado de minas gerais", "podcast", "home", "quem somos")):
        return False
    return any(k in text for k in ("chamada", "edital", "submiss", "inscri", "fomento", "resultado", ".pdf"))


def main():
    config = {
        "source_label": "FAPEMIG",
        "listing_urls": [
            "https://fapemig.br/pt/",
            "https://fapemig.br/pt/chamadas_publicas/",
            "https://fapemig.br/pt/editais/",
        ],
        "keywords": KEYWORDS_INTEREST + ["fapemig", "chamada publica", "fomento", "inovacao"],
        "avoid_keywords": ["resultado final", "concurso", "estagio"],
        "program_hint": "Fomento a Ciencia e Tecnologia",
        "allowed_domains": ["fapemig.br"],
        "max_items": 25,
        "max_links_per_page": 150,
        "setor_estrategico": "ciencia_tecnologia_inovacao",
        "orgao_responsavel": "FAPEMIG",
        "instituicao": "Fundação de Amparo à Pesquisa do Estado de Minas Gerais",
        "orgao_contratante": "FAPEMIG",
        "tipo_oportunidade": "chamada_publica",
        "area_cientifica": ["ciencia", "tecnologia", "inovacao"],
        "area_tecnologica": ["pesquisa_aplicada", "transformacao_digital"],
        "subtema_padrao": ["fomento", "pesquisa", "inovacao"],
    }
    try:
        items = scrape_source(config)
        raw_items = list(items)
    except Exception as exc:
        print(f"[FAPEMIG] Falha na coleta: {exc}")
        items = []
        raw_items = []
    items = [x for x in items if _is_relevant_item(x)]
    if not items and raw_items:
        items = raw_items[:8]
    if not items:
        items = [
            {
                "titulo": "FAPEMIG - Página de Editais e Chamadas",
                "descricao": "Índice público de editais e chamadas da FAPEMIG.",
                "link": "https://fapemig.br/pt/chamadas_publicas/",
                "fonte": "FAPEMIG",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "fapemig",
                "acao": "chamada_publica",
                "tipo_recurso": "fomento",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "ciencia_tecnologia_inovacao",
                    "tipo_oportunidade": "chamada_publica",
                    "tipo_recurso": "fomento",
                    "url_listagem": "https://fapemig.br/pt/chamadas_publicas/",
                    "url_detalhe": "https://fapemig.br/pt/chamadas_publicas/",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[FAPEMIG] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "fapemig", items)
    print(f"[FAPEMIG] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
