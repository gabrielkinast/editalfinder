from pathlib import Path
import sys
from urllib.parse import urljoin

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import extract_deadline, extract_value, fetch_soup, normalize_text, parse_date, save_outputs

LISTING_URL = "https://embrapii.org.br/transparencia/#chamadas"
SOURCE_NAME = "EMBRAPII"
BASE_URL = "https://embrapii.org.br"
POSITIVE_HINTS = ["chamada pública", "chamada publica", "edital", "submissão", "submissao", "projeto"]
NOISE_HINTS = ["ouvidoria", "trabalhe conosco", "politica de privacidade", "cookie"]


def _is_relevant(title: str, url: str) -> bool:
    text = f"{title} {url}".lower()
    if any(k in text for k in NOISE_HINTS):
        return False
    if "embrapii.org.br" not in url.lower():
        return False
    return any(k in text for k in POSITIVE_HINTS)


def _build_item(listing_url: str, detail_url: str, title: str) -> dict | None:
    detail = fetch_soup(detail_url)
    if not detail:
        return None
    h1 = detail.select_one("h1")
    final_title = normalize_text(h1.get_text()) if h1 else normalize_text(title)
    main = detail.select_one("main") or detail.select_one("#content") or detail
    body = normalize_text(main.get_text(" "))[:3500]
    if not final_title:
        return None
    docs = []
    seen_docs = set()
    for a in detail.select("a[href]"):
        href = a.get("href")
        if not href:
            continue
        full = urljoin(detail_url, href)
        if full.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")) and full not in seen_docs:
            seen_docs.add(full)
            docs.append({"nome": normalize_text(a.get_text()) or "Documento", "url": full})
    pub = parse_date(body)
    return {
        "titulo": final_title[:250],
        "descricao": body or final_title,
        "link": detail_url,
        "fonte": SOURCE_NAME,
        "data_publicacao": pub,
        "fim_inscricao": extract_deadline(body),
        "situacao": "Aberto",
        "valor": extract_value(body),
        "programa": "embrapii_inovacao",
        "acao": "chamada_publica",
        "tipo_recurso": "Subvenção (Não Reembolsável)",
        "extras": {
            "regiao": "brasil",
            "pais": "Brasil",
            "idioma_original": "pt",
            "titulo_original": final_title[:250],
            "descricao_original": body or final_title,
            "titulo_traduzido": "",
            "descricao_traduzida": "",
            "setor_estrategico": "inovacao_industrial",
            "subtema": ["pdi", "inovacao", "chamada_publica"],
            "area_cientifica": [],
            "area_tecnologica": ["inovacao", "pdi"],
            "tipo_oportunidade": "chamada_publica",
            "orgao_responsavel": SOURCE_NAME,
            "instituicao": SOURCE_NAME,
            "empresa_prime": "",
            "orgao_contratante": SOURCE_NAME,
            "numero_edital": "",
            "numero_chamada": "",
            "numero_processo": "",
            "codigo_oportunidade": "",
            "modalidade": "",
            "publico_alvo": "",
            "elegibilidade": "",
            "objetivo": "",
            "escopo": "",
            "itens_financiaveis": [],
            "itens_nao_financiaveis": [],
            "valor_total": "",
            "valor_por_projeto": "",
            "contrapartida": "",
            "prazo_execucao": "",
            "cronograma": [],
            "documentos": docs,
            "pdf_url": next((d["url"] for d in docs if d["url"].lower().endswith(".pdf")), ""),
            "pdf_texto_extraido": "",
            "pdf_resumo": "",
            "data_publicacao_original": "",
            "fim_inscricao_original": "",
            "prazo_submissao_original": "",
            "metodo_extracao": "html_listing_detail_curated",
            "url_listagem": listing_url,
            "url_detalhe": detail_url,
            "palavras_chave_detectadas": ["inovacao", "pdi", "chamada publica"],
            "nivel_sensibilidade": "publico_institucional",
            "necessita_traducao": False,
            "observacoes": "",
            "ano": pub[:4] if pub else "",
        },
    }


def _collect_curated() -> list[dict]:
    soup = fetch_soup(LISTING_URL)
    if not soup:
        return []
    items = []
    seen = set()
    for a in soup.select("a[href]"):
        text = normalize_text(a.get_text())
        href = a.get("href")
        if not href:
            continue
        full = urljoin(BASE_URL, href).split("#", 1)[0]
        if full in seen:
            continue
        if not _is_relevant(text, full):
            continue
        seen.add(full)
        item = _build_item(LISTING_URL, full, text)
        if item:
            items.append(item)
        if len(items) >= 30:
            break
    return items


def main():
    try:
        items = _collect_curated()
    except Exception as exc:
        print(f"[EMBRAPII] Falha na coleta: {exc}")
        items = []
    if not items:
        items = [
            {
                "titulo": "EMBRAPII - Chamadas Públicas",
                "descricao": "Índice público de chamadas e programas de inovação da EMBRAPII.",
                "link": LISTING_URL,
                "fonte": SOURCE_NAME,
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "embrapii_inovacao",
                "acao": "chamada_publica",
                "tipo_recurso": "Subvenção (Não Reembolsável)",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "setor_estrategico": "inovacao_industrial",
                    "tipo_oportunidade": "chamada_publica",
                    "tipo_recurso": "Subvenção (Não Reembolsável)",
                    "url_listagem": LISTING_URL,
                    "url_detalhe": LISTING_URL,
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[EMBRAPII] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "embrapii", items)
    print(f"[EMBRAPII] Registros salvos: {len(items)}")

if __name__ == "__main__":
    main()
