from pathlib import Path
import sys
from urllib.parse import urljoin, urlparse

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
from CORE.http_fetch import fetch_pdf_bytes
from CORE.pdf_enrichment import extract_pdf_text_with_fallback

BASE_PAGES = [
    "https://www.caixa.gov.br/empresa/credito-financiamento/Paginas/default.aspx",
    "https://www.caixa.gov.br/sustentabilidade/fundo-socioambiental-caixa/chamadas-abertas/Paginas/default.aspx",
    "https://www.caixa.gov.br/empresa/Paginas/default.aspx",
]
ALLOWED_HOST = "caixa.gov.br"
TARGET_PATH_HINTS = [
    "/credito",
    "/financiamento",
    "/fundo",
    "/microcredito",
    "/chamadas-abertas",
]
TARGET_TEXT_HINTS = [
    "crédito",
    "credito",
    "financiamento",
    "linha",
    "fundo",
    "chamada",
    "microcrédito",
    "microcredito",
]
NOISE_HINTS = ["ouvidoria", "loterias", "facebook", "youtube", "instagram", "telefones"]


def _is_caixa_url(url: str) -> bool:
    return urlparse(url).netloc.lower().endswith(ALLOWED_HOST)


def _is_candidate_link(text: str, url: str) -> bool:
    low = f"{text} {url}".lower()
    if "?" in text and any(k in low for k in ["cdb", "poupança", "poupanca", "ações online", "acoes online", "fundo de investimento"]):
        return False
    if any(k in low for k in ["/voce/", "/investimentos", "/perguntas-frequentes"]):
        return False
    return any(k in low for k in TARGET_TEXT_HINTS) or any(k in url.lower() for k in TARGET_PATH_HINTS)


def _build_item(listing_url: str, detail_url: str, title: str) -> dict | None:
    if detail_url.lower().endswith(".pdf"):
        name_low = normalize_text(title).lower()
        if not any(k in f"{name_low} {detail_url.lower()}" for k in ["regulamento", "edital", "chamada", "convite", "termo de referencia", "termo_de_referencia"]):
            return None
        tipo_recurso = "subvencao" if any(k in detail_url.lower() for k in ["fundo", "chamada"]) else "financiamento_reembolsavel"
        pdf_text = ""
        pdf_resumo = ""
        data_publicacao = None
        fim_inscricao = None
        valor = None
        try:
            pdf_bytes = fetch_pdf_bytes(detail_url, page_referer=listing_url)
            if pdf_bytes:
                extracted = extract_pdf_text_with_fallback(pdf_bytes, max_pages=5) or ""
                if extracted:
                    pdf_text = normalize_text(extracted)[:2000]
                    pdf_resumo = pdf_text[:500]
                    data_publicacao = parse_date(pdf_text)
                    fim_inscricao = extract_deadline(pdf_text)
                    valor = extract_value(pdf_text)
        except Exception:
            pass
        return {
            "titulo": normalize_text(title)[:250] or "Documento CAIXA",
            "descricao": pdf_resumo or normalize_text(title) or "Documento público da CAIXA associado a chamada/linha financeira.",
            "link": detail_url,
            "fonte": "CAIXA",
            "data_publicacao": data_publicacao,
            "fim_inscricao": fim_inscricao,
            "situacao": "Em andamento",
            "valor": valor,
            "programa": "produtos_caixa",
            "acao": "credito",
            "tipo_recurso": tipo_recurso,
            "extras": {
                "pais": "Brasil",
                "regiao": "brasil",
                "orgao_responsavel": "CAIXA",
                "instituicao": "Caixa Econômica Federal",
                "orgao_contratante": "CAIXA",
                "tipo_oportunidade": "linha_credito",
                "tipo_recurso": tipo_recurso,
                "natureza_recurso": "nao_reembolsavel" if tipo_recurso == "subvencao" else "reembolsavel",
                "reembolsavel": tipo_recurso != "subvencao",
                "publico_alvo": "empresas e entes públicos",
                "setor_estrategico": "credito_publico",
                "subtema": ["credito", "financiamento", "fundos"],
                "area_cientifica": [],
                "area_tecnologica": ["infraestrutura", "habitacao", "saneamento", "energia"],
                "documentos": [{"nome": normalize_text(title) or "Documento PDF", "url": detail_url}],
                "pdf_url": detail_url,
                "pdf_texto_extraido": pdf_text,
                "pdf_resumo": pdf_resumo,
                "valor_total": valor or "",
                "url_listagem": listing_url,
                "url_detalhe": detail_url,
                "metodo_extracao": "pdf_link_curated",
                "nivel_sensibilidade": "publico_institucional",
            },
        }
    detail = fetch_soup(detail_url)
    if not detail:
        return None
    h1 = detail.select_one("h1")
    final_title = normalize_text(h1.get_text()) if h1 else normalize_text(title)
    body = normalize_text(detail.get_text(" "))[:3500]
    if not final_title:
        return None
    low = f"{final_title} {body} {detail_url}".lower()
    if any(k in low for k in NOISE_HINTS):
        return None
    docs = []
    for a in detail.select("a[href]"):
        href = a.get("href")
        if not href:
            continue
        full = urljoin(detail_url, href)
        if full.lower().endswith((".pdf", ".doc", ".docx", ".xls", ".xlsx")):
            docs.append({"nome": normalize_text(a.get_text()) or "Documento", "url": full})
    tipo_recurso = "subvencao" if any(k in low for k in ["fundo", "não reembols", "nao reembols", "chamada"]) else "financiamento_reembolsavel"
    extras = {
        "pais": "Brasil",
        "regiao": "brasil",
        "orgao_responsavel": "CAIXA",
        "instituicao": "Caixa Econômica Federal",
        "orgao_contratante": "CAIXA",
        "tipo_oportunidade": "linha_credito",
        "tipo_recurso": tipo_recurso,
        "natureza_recurso": "nao_reembolsavel" if tipo_recurso == "subvencao" else "reembolsavel",
        "reembolsavel": tipo_recurso != "subvencao",
        "publico_alvo": "empresas e entes públicos",
        "setor_estrategico": "credito_publico",
        "subtema": ["credito", "financiamento", "fundos"],
        "area_cientifica": [],
        "area_tecnologica": ["infraestrutura", "habitacao", "saneamento", "energia"],
        "documentos": docs,
        "pdf_url": next((d["url"] for d in docs if d["url"].lower().endswith(".pdf")), ""),
        "valor_total": extract_value(body) or "",
        "url_listagem": listing_url,
        "url_detalhe": detail_url,
        "metodo_extracao": "html_listing_detail_curated",
        "nivel_sensibilidade": "publico_institucional",
    }
    return {
        "titulo": final_title[:250],
        "descricao": body,
        "link": detail_url,
        "fonte": "CAIXA",
        "data_publicacao": parse_date(body),
        "fim_inscricao": extract_deadline(body),
        "situacao": "Em andamento",
        "valor": extract_value(body),
        "programa": "produtos_caixa",
        "acao": "credito",
        "tipo_recurso": tipo_recurso,
        "extras": extras,
    }


def _collect_curated() -> list[dict]:
    items = []
    seen = set()
    for listing in BASE_PAGES:
        soup = fetch_soup(listing)
        if not soup:
            continue
        for a in soup.select("a[href]"):
            text = normalize_text(a.get_text())
            href = a.get("href")
            if not href:
                continue
            full = urljoin(listing, href).split("#", 1)[0]
            if not full.startswith("http") or not _is_caixa_url(full):
                continue
            if full in seen:
                continue
            if not _is_candidate_link(text, full):
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
        items = _collect_curated()
    except Exception as exc:
        print(f"[CAIXA] Falha na coleta: {exc}")
        items = []
    if not items:
        items = [
            {
                "titulo": "CAIXA - Crédito, Fundos e Financiamentos",
                "descricao": "Índice público de produtos financeiros e chamadas da CAIXA.",
                "link": "https://www.caixa.gov.br/empresa/credito-financiamento/Paginas/default.aspx",
                "fonte": "CAIXA",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "produtos_caixa",
                "acao": "credito",
                "tipo_recurso": "financiamento_reembolsavel",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "tipo_oportunidade": "linha_credito",
                    "tipo_recurso": "financiamento_reembolsavel",
                    "natureza_recurso": "reembolsavel",
                    "reembolsavel": True,
                    "url_listagem": "https://www.caixa.gov.br/empresa/credito-financiamento/Paginas/default.aspx",
                    "url_detalhe": "https://www.caixa.gov.br/empresa/credito-financiamento/Paginas/default.aspx",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[CAIXA] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "caixa", items)
    print(f"[CAIXA] Registros salvos: {len(items)}")

if __name__ == "__main__":
    main()
