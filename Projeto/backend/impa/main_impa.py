from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").strip().lower()
    text = f"{title} {str(item.get('descricao') or '').lower()} {str(item.get('link') or '').lower()}"
    link = str(item.get("link") or "").lower()
    if not title or title in {"buscar", "busca", "entrar", "quem é quem", "temas de pesquisa"}:
        return False
    if "/noticias/" in link:
        return False
    if title.isdigit() and len(title) == 4:
        return False
    if any(k in text for k in ("menu sanduiche", "veja todos os resultados", "faleconosco@impa.br")):
        return False
    if any(k in text for k in ("analista administrativo", "vaga", "rh", "clt", "salário")):
        return False
    return any(k in text for k in ("edital", "chamada", "bolsa", "oportunidade", "fomento", "inscri", ".pdf"))


def main():
    config = {
        "source_label": "IMPA",
        "listing_urls": [
            "https://impa.br/pt-br/",
            "https://impa.br/pt-br/oportunidades/",
        ],
        "keywords": [
            "edital",
            "chamada",
            "bolsa",
            "programa",
            "curso",
            "evento",
            "matemática",
            "pesquisa",
            "fomento",
            "oportunidade",
        ],
        "avoid_keywords": [
            "concurso público",
        ],
        "program_hint": "IMPA",
        "allowed_domains": ["impa.br"],
        "max_items": 20,
        "max_links_per_page": 100,
        "require_opportunity_signals": True,
    }
    items = [x for x in scrape_source(config) if _is_relevant_item(x)]
    if not items:
        items = [
            {
                "titulo": "IMPA - Oportunidades",
                "descricao": "Página pública de oportunidades acadêmicas e chamadas do IMPA.",
                "link": "https://impa.br/pt-br/oportunidades/",
                "fonte": "IMPA",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "IMPA",
                "acao": "chamada_publica",
                "tipo_recurso": "fomento",
                "extras": {"metodo_extracao": "fallback_public_index"},
            }
        ]
    save_outputs(Path(__file__).parent, "impa", items)
    print(f"IMPA: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
