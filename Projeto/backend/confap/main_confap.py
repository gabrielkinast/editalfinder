from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs

POSITIVE_HINTS = [
    "edital",
    "chamada",
    "fomento",
    "call",
    "submission",
    "proposal",
    "deadline",
]
NOISE_HINTS = [
    "quem somos",
    "diretoria",
    "histórico",
    "historia",
    "notícias",
    "noticias",
    "contato",
]
STRONG_HINTS = [
    "chamada pública",
    "chamada publica",
    "call for",
    "resultado final",
    "prazo para submissão",
    "prazo para submissao",
]


def _is_relevant_item(item: dict) -> bool:
    text = f"{item.get('titulo','')} {item.get('descricao','')} {item.get('link','')}".lower()
    has_positive = any(k in text for k in POSITIVE_HINTS)
    has_noise = any(k in text for k in NOISE_HINTS)
    has_strong = any(k in text for k in STRONG_HINTS)
    return has_positive and (not has_noise or has_strong)


def _dedupe(items: list[dict]) -> list[dict]:
    out = []
    seen = set()
    for it in items:
        key = f"{it.get('link','')}|{it.get('titulo','')}".strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def _normalize_titles(items: list[dict]) -> list[dict]:
    for it in items:
        title = str(it.get("titulo") or "").strip().lower()
        link = str(it.get("link") or "")
        if title == "editais" and "/editais/" in link:
            slug = link.rstrip("/").split("/")[-1].replace("-", " ").strip()
            if slug:
                it["titulo"] = slug[:250]
    return items


def main():
    config = {
        "source_label": "CONFAP",
        "listing_urls": [
            "https://confap.org.br/pt/editais",
            "https://confap.org.br/pt/chamadas-publicas/",
        ],
        "keywords": ["edital", "chamada", "fomento", "oportunidade", "pesquisa", "inovacao"],
        "avoid_keywords": ["concurso", "estagio", "pregao", "licitacao"],
        "program_hint": "CONFAP",
        "allowed_domains": ["confap.org.br"],
        "max_items": 30,
        "max_links_per_page": 180,
        "setor_estrategico": "ciencia_tecnologia_inovacao",
        "orgao_responsavel": "CONFAP",
        "instituicao": "Conselho Nacional das FAPs",
        "orgao_contratante": "CONFAP",
        "tipo_oportunidade": "chamada_publica",
        "area_cientifica": ["ciencia", "tecnologia", "inovacao"],
        "area_tecnologica": ["pesquisa_aplicada", "cooperacao_internacional"],
        "subtema_padrao": ["fomento", "pesquisa", "inovacao"],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[CONFAP] Falha na coleta: {exc}")
        items = []
    items = _normalize_titles(_dedupe([x for x in items if _is_relevant_item(x)]))
    if not items:
        items = [
            {
                "titulo": "CONFAP - Página de Editais e Chamadas",
                "descricao": "Índice público de editais e chamadas do CONFAP.",
                "link": "https://confap.org.br/pt/editais",
                "fonte": "CONFAP",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "confap",
                "acao": "chamada_publica",
                "tipo_recurso": "fomento",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "ciencia_tecnologia_inovacao",
                    "tipo_oportunidade": "chamada_publica",
                    "tipo_recurso": "fomento",
                    "url_listagem": "https://confap.org.br/pt/editais",
                    "url_detalhe": "https://confap.org.br/pt/editais",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[CONFAP] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "confap", items)
    print(f"[CONFAP] Registros salvos: {len(items)}")

if __name__ == "__main__":
    main()
