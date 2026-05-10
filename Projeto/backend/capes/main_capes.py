from pathlib import Path
import sys
from urllib.parse import urljoin

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import (
    extract_deadline,
    extract_value,
    fetch_soup,
    normalize_text,
    parse_date,
    save_outputs,
)

LISTINGS = [
    "https://www.gov.br/capes/pt-br/assuntos/editais-e-resultados",
]
POSITIVE_HINTS = ["edital", "chamada", "bolsa", "inscri", "submiss", "fomento", "seleção", "aberto"]
NOISE_HINTS = ["sei.capes", "ouvidoria", "acesso-a-informacao", "mapa-do-site", "telefones", "licitacoes", "resultado", "governança", "carta-de-servicos", "outras-acoes"]


def _is_candidate(text: str, link: str) -> bool:
    low = f"{text} {link}".lower()
    if "gov.br/capes" not in link.lower():
        return False
    if any(k in low for k in NOISE_HINTS):
        return False
    return any(k in low for k in POSITIVE_HINTS)


def _build_item(listing_url: str, detail_url: str, title: str) -> dict | None:
    detail = fetch_soup(detail_url)
    if not detail:
        return None
    h1 = detail.select_one("h1")
    final_title = normalize_text(h1.get_text()) if h1 else normalize_text(title)
    main = detail.select_one("main") or detail.select_one("#content-core") or detail.select_one(".documentByLine")
    body = normalize_text((main.get_text(" ") if main else detail.get_text(" ")))[:3500]
    body_low = body.lower()
    if any(k in body_low for k in ["resultado final", "resultado preliminar", "resultados 2026", "carta de serviços", "governança"]):
        return None
    if not _is_candidate(final_title, detail_url):
        return None
    docs = []
    seen_docs = set()
    for a in detail.select("a[href]"):
        href = a.get("href")
        if not href:
            continue
        full = urljoin(detail_url, href)
        if full.lower().endswith((".pdf", ".doc", ".docx")) and full not in seen_docs:
            seen_docs.add(full)
            docs.append({"nome": normalize_text(a.get_text()) or "Documento", "url": full})
    return {
        "titulo": final_title[:250] or "Edital CAPES",
        "descricao": body or final_title,
        "link": detail_url,
        "fonte": "CAPES",
        "data_publicacao": parse_date(body),
        "fim_inscricao": extract_deadline(body),
        "situacao": "Em andamento",
        "valor": extract_value(body),
        "programa": "capes",
        "acao": "chamada_publica",
        "tipo_recurso": "fomento",
        "extras": {
            "pais": "Brasil",
            "regiao": "brasil",
            "orgao_responsavel": "CAPES",
            "instituicao": "Coordenação de Aperfeiçoamento de Pessoal de Nível Superior",
            "orgao_contratante": "CAPES",
            "setor_estrategico": "educacao_ciencia",
            "tipo_oportunidade": "chamada_publica",
            "tipo_recurso": "fomento",
            "natureza_recurso": "nao_reembolsavel",
            "reembolsavel": False,
            "area_cientifica": ["educacao", "ciencia", "pesquisa"],
            "area_tecnologica": ["formacao", "internacionalizacao", "pesquisa_aplicada"],
            "subtema": ["bolsa", "fomento", "pesquisa"],
            "documentos": docs,
            "pdf_url": next((d["url"] for d in docs if d["url"].lower().endswith(".pdf")), ""),
            "url_listagem": listing_url,
            "url_detalhe": detail_url,
            "metodo_extracao": "html_listing_detail_curated",
            "nivel_sensibilidade": "publico_institucional",
        },
    }


def _collect_curated() -> list[dict]:
    items = []
    seen = set()
    for listing in LISTINGS:
        soup = fetch_soup(listing)
        if not soup:
            continue
        for a in soup.select("a[href]"):
            text = normalize_text(a.get_text())
            href = a.get("href")
            if not href:
                continue
            full = urljoin(listing, href).split("#", 1)[0]
            if full in seen:
                continue
            if not _is_candidate(text, full):
                continue
            seen.add(full)
            item = _build_item(listing, full, text)
            if item:
                items.append(item)
            if len(items) >= 30:
                return items
    return items


def main():
    try:
        items = [x for x in _collect_curated() if not str(x.get("titulo","")).lower().startswith("resultados")]
    except Exception as exc:
        print(f"[CAPES] Falha na coleta: {exc}")
        items = []
    if not items:
        items = [
            {
                "titulo": "CAPES - Página de Editais e Programas",
                "descricao": "Índice público de editais, bolsas e programas da CAPES.",
                "link": "https://www.gov.br/capes/pt-br/assuntos/editais-e-resultados",
                "fonte": "CAPES",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "capes",
                "acao": "chamada_publica",
                "tipo_recurso": "fomento",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "educacao_ciencia",
                    "tipo_oportunidade": "chamada_publica",
                    "tipo_recurso": "fomento",
                    "url_listagem": "https://www.gov.br/capes/pt-br/assuntos/editais-e-resultados",
                    "url_detalhe": "https://www.gov.br/capes/pt-br/assuntos/editais-e-resultados",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[CAPES] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "capes", items)
    print(f"[CAPES] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
