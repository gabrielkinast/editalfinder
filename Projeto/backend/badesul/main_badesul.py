from pathlib import Path
import sys
from datetime import datetime
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import requests

from CORE.http_fetch import fetch_pdf_bytes
from CORE.pdf_enrichment import extract_pdf_text_with_fallback
from scraper_generic import extract_deadline, extract_value, normalize_text, parse_date, save_outputs

BASE_URL = "https://www.badesul.com.br"
PUBLIC_PAGE = "https://www.badesul.com.br/publicacoes/10072"
MENU_API = "https://www.badesul.com.br/fas-service/rest/menu/listAll"
PUBLIC_API_TMPL = "https://www.badesul.com.br/fas/transparencia/findAllPublicacaoByTipoPublicacao/{tipo}/-1/-1"
DOWNLOAD_TMPL = "https://www.badesul.com.br/fas/transparencia/download?idPublicacao={pub_id}"
SOURCE_NAME = "BADESUL"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Authorization": "Basic ZmFzOmZhcw==",
}


def _date_to_iso(raw: str) -> str | None:
    txt = (raw or "").strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(txt, fmt).date().isoformat()
        except Exception:
            continue
    return parse_date(txt)


def _detect_tipo_recurso(text: str) -> str:
    low = text.lower()
    if any(k in low for k in ["subven", "chamada", "seleção pública", "selecao publica"]):
        return "subvencao"
    if any(k in low for k in ["crédito", "credito", "financiamento", "juros", "carência", "carencia"]):
        return "financiamento_reembolsavel"
    return "financiamento_reembolsavel"


def _looks_like_noise_attachment(title: str, subtitle: str, desc: str) -> bool:
    blob = f"{title} {subtitle} {desc}".lower()
    if blob.startswith("anexo ") or "modelo de " in blob:
        return True
    if "lista de entidades" in blob or "entidades inscritas" in blob:
        return True
    noise_terms = ("anexo i", "anexo ii", "anexo iii", "anexo iv", "anexo v", "anexo vi", "declaração", "declaracao")
    return any(t in blob for t in noise_terms)


def _detect_tipo_oportunidade(text: str) -> str:
    low = text.lower()
    if any(k in low for k in ("linha de crédito", "linha de credito", "crédito", "credito", "financiamento")):
        return "linha_de_credito"
    if any(k in low for k in ("subven", "edital", "chamada", "seleção pública", "selecao publica")):
        return "programa"
    return "programa"


def _build_item(tipo_id: str, pub: dict) -> dict:
    title = normalize_text(pub.get("tituloPublicacao") or "Publicação BADESUL")
    subtitle = normalize_text(pub.get("subtituloPublicacao") or "")
    desc = normalize_text(pub.get("descricaoPublicacao") or "")
    published = pub.get("dataPublicacao") or pub.get("dataPublicacaoMesAno") or ""
    link = DOWNLOAD_TMPL.format(pub_id=pub.get("id"))
    merged_text = " ".join(x for x in [title, subtitle, desc] if x).strip()

    pdf_bytes = fetch_pdf_bytes(link, page_referer=PUBLIC_PAGE)
    pdf_text = extract_pdf_text_with_fallback(pdf_bytes, max_pages=8) if pdf_bytes else None
    if pdf_text:
        merged_text = f"{merged_text} {normalize_text(pdf_text[:2500])}".strip()

    tipo_recurso = _detect_tipo_recurso(merged_text)
    tipo_oportunidade = _detect_tipo_oportunidade(merged_text)
    valor = extract_value(merged_text)
    fim = extract_deadline(merged_text)

    return {
        "titulo": title[:250],
        "descricao": (desc or subtitle or title)[:3500],
        "link": link,
        "fonte": SOURCE_NAME,
        "data_publicacao": _date_to_iso(published),
        "fim_inscricao": fim,
        "situacao": "Em andamento",
        "valor": valor,
        "programa": "linhas_badesul",
        "acao": "credito",
        "tipo_recurso": tipo_recurso,
        "extras": {
            "pais": "Brasil",
            "regiao": "brasil",
            "orgao_responsavel": "BADESUL",
            "instituicao": "Badesul Desenvolvimento",
            "orgao_contratante": "BADESUL",
            "numero_edital": "",
            "codigo_oportunidade": str(pub.get("id") or ""),
            "tipo_oportunidade": tipo_oportunidade,
            "tipo_recurso": tipo_recurso,
            "natureza_recurso": "nao_reembolsavel" if tipo_recurso == "subvencao" else "reembolsavel",
            "reembolsavel": tipo_recurso != "subvencao",
            "publico_alvo": "empresas e municípios",
            "perfil_ideal": ["empresa", "pequena_empresa", "media_empresa", "cooperativa", "governo_municipal"],
            "setor_estrategico": "desenvolvimento_regional",
            "subtema": ["credito", "financiamento", "desenvolvimento_regional"],
            "area_cientifica": [],
            "area_tecnologica": ["inovacao", "energia", "infraestrutura"],
            "documentos": [{"nome": title or "Documento PDF", "url": link}],
            "pdf_url": link,
            "pdf_resumo": (pdf_text[:700] + "...") if pdf_text and len(pdf_text) > 700 else (pdf_text or ""),
            "pdf_texto_extraido": (pdf_text[:3000] if pdf_text else ""),
            "data_publicacao_original": str(published),
            "valor_total": valor or "",
            "url_listagem": f"{BASE_URL}/publicacoes/{tipo_id}",
            "url_detalhe": link,
            "metodo_extracao": "api_publicacoes_pdf_enriched",
            "nivel_sensibilidade": "publico_institucional",
            "observacoes": subtitle,
            "tamanho_arquivo": pub.get("tamanhoArquivo") or "",
            "extensao_arquivo": pub.get("extensaoArquivo") or "",
        },
    }


def _discover_publicacao_ids() -> list[str]:
    ids = {"10072"}  # confirmado manualmente
    try:
        resp = requests.get(MENU_API, headers=HEADERS, timeout=30)
        if resp.ok:
            data = resp.json()
            if isinstance(data, list):
                for item in data:
                    comp = str(item.get("complemento") or "").strip()
                    title = normalize_text(item.get("titulo") or "").lower()
                    if comp.isdigit() and ("edital" in title or "subven" in title or "publica" in title):
                        ids.add(comp)
    except Exception as exc:
        print(f"[BADESUL] Aviso: falha ao descobrir IDs de publicação no menu: {exc}")
    return sorted(ids)


def _collect_curated() -> list[dict]:
    items: list[dict] = []
    seen = set()
    for tipo_id in _discover_publicacao_ids():
        try:
            url = f"{PUBLIC_API_TMPL.format(tipo=tipo_id)}?_={int(datetime.now().timestamp())}"
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            payload = resp.json()
            if not isinstance(payload, list):
                continue
            for pub in payload:
                if not isinstance(pub, dict):
                    continue
                pub_id = str(pub.get("id") or "")
                if not pub_id or pub_id in seen:
                    continue
                title = normalize_text(pub.get("tituloPublicacao") or "")
                subtitle = normalize_text(pub.get("subtituloPublicacao") or "")
                desc = normalize_text(pub.get("descricaoPublicacao") or "")
                if _looks_like_noise_attachment(title, subtitle, desc):
                    continue
                seen.add(pub_id)
                item = _build_item(tipo_id, pub)
                items.append(item)
                if len(items) >= 40:
                    return items
        except Exception as exc:
            print(f"[BADESUL] Falha ao coletar publicações do tipo {tipo_id}: {exc}")
            continue
    return items


def main():
    try:
        items = _collect_curated()
    except Exception as exc:
        print(f"[BADESUL] Falha na coleta: {exc}")
        items = []
    if not items:
        print("[BADESUL] Nenhum item coletado; não usar página institucional como edital (lista vazia confirmada).")
    save_outputs(Path(__file__).parent, "badesul", items, allow_empty=not bool(items))
    print(f"[BADESUL] Registros salvos: {len(items)}")

if __name__ == "__main__":
    main()
