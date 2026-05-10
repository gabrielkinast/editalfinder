import re
import requests
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from pathlib import Path
import sys
from utils_abdi import get_soup, normalize_text, extract_date, is_deadline_valid
from models_abdi import EditalABDI

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from CORE.http_fetch import fetch_pdf_bytes
from CORE.pdf_enrichment import extract_pdf_text_with_fallback

BASE_URL = "https://www.abdi.com.br"
URLS = [
    "https://www.abdi.com.br/agro-40/editais-e-documentos/",
    "https://www.abdi.com.br/transparencia/aquisicao-de-bens-e-servicos/",
    "https://www.abdi.com.br/transparencia/consultas-publicas/",
    "https://www.abdi.com.br/concursos/"
]


def _extract_money(text: str) -> Optional[str]:
    m = re.search(r"(R\$\s?\d[\d\.\,]*(?:\s?(?:mil|milh[aã]o|milh[oõ]es))?)", text, re.IGNORECASE)
    return normalize_text(m.group(1)) if m else None


def _extract_deadline_iso(text: str) -> Optional[str]:
    m = re.search(r"(\d{2}/\d{2}/\d{4})", text)
    if not m:
        return None
    return extract_date(m.group(1))


def _guess_title_from_pdf(url: str, extracted_text: str) -> str:
    lines = [normalize_text(x) for x in (extracted_text or "").splitlines()]
    for ln in lines[:30]:
        low = ln.lower()
        if len(ln) < 12:
            continue
        if any(k in low for k in ["edital", "chamada", "concurso", "termo de referência", "seleção", "agro", "inovação", "inovacao"]):
            return ln[:240]
    filename = url.split("/")[-1].replace(".pdf", "")
    clean = filename.replace("_", " ").replace("-", " ").strip()
    return f"ABDI - {clean[:180]}"


def _build_pdf_edital(full_url: str, anchor_title: str) -> EditalABDI:
    pdf_text = ""
    try:
        pdf_bytes = fetch_pdf_bytes(full_url, page_referer=BASE_URL)
        if pdf_bytes:
            pdf_text = extract_pdf_text_with_fallback(pdf_bytes, max_pages=5) or ""
    except Exception:
        pdf_text = ""
    pdf_text_norm = normalize_text(pdf_text)[:2200] if pdf_text else ""
    title = _guess_title_from_pdf(full_url, pdf_text)
    desc = pdf_text_norm[:900] if pdf_text_norm else (anchor_title or title)
    return EditalABDI(
        titulo=title,
        link=full_url,
        descricao=desc,
        data_publicacao=extract_date(pdf_text_norm) if pdf_text_norm else None,
        fim_inscricao=_extract_deadline_iso(pdf_text_norm) if pdf_text_norm else None,
        situacao="Aberto",
        extras={
            "anexos": [{"nome": "Edital PDF", "url": full_url}],
            "fonte_original": "ABDI",
            "pdf_url": full_url,
            "pdf_texto_extraido": pdf_text_norm,
            "pdf_resumo": pdf_text_norm[:500] if pdf_text_norm else "",
            "valor_total": _extract_money(pdf_text_norm) or "",
            "objetivo": pdf_text_norm[:500] if pdf_text_norm else "",
            "metodo_extracao": "pdf_enriched",
        },
    )


class ABDIScraper:
    def __init__(self):
        self.base_url = BASE_URL

    def extract_editais(self) -> List[EditalABDI]:
        all_editais = []
        for url in URLS:
            print(f"Iniciando extração ABDI em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            # ABDI usa tabelas ou listas para transparência
            # Procura por linhas de tabela (tr) ou links que pareçam editais
            content = soup.select_one(".content") or soup.select_one("article") or soup.select_one("main") or soup
            
            # Tenta encontrar links que contenham palavras-chave no texto ou na URL
            links = content.select("a[href]")
            for a in links:
                href = a.get("href")
                titulo = normalize_text(a.get_text())
                
                # Filtro: links internos que pareçam editais/documentos
                if any(kw in href.lower() or kw in titulo.lower() for kw in ["edital", "chamada", "fomento", "selecao", "concurso", "termo-de-referencia", "processo-seletivo"]):
                    if not href.startswith("http"):
                        href = urljoin(self.base_url, href)
                    
                    # Evita duplicatas
                    full_url = href.split("#", 1)[0]
                    if any(e.link == full_url for e in all_editais):
                        continue
                        
                    # Se for PDF direto, cria o edital sem entrar na página
                    if full_url.lower().endswith(".pdf"):
                        edital = _build_pdf_edital(full_url, titulo)
                        all_editais.append(edital)
                        print(f"Encontrado PDF direto: {edital.titulo[:50]}...")
                    else:
                        print(f"Verificando página de edital: {titulo[:50]}...")
                        edital = self.process_detail_page(full_url, titulo)
                        if edital:
                            if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                                continue
                            all_editais.append(edital)

        return all_editais

    def _process_link(self, a, source_url, editais_list):
        href = a.get("href")
        full_url = urljoin(self.base_url, href).split("#", 1)[0]
        if any(e.link == full_url for e in editais_list):
            return
        
        titulo = normalize_text(a.get_text())
        if len(titulo) < 10:
            return
            
        edital = self.process_detail_page(full_url, titulo)
        if edital:
            if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                return
            editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str) -> Optional[EditalABDI]:
        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one(".content") or soup.select_one("article") or soup.select_one("main") or soup
        text = content.get_text()
        
        # Filtro de relevância: Verificamos se o texto contém palavras-chave de fomento/editais
        if not any(kw in (titulo + text).lower() for kw in ["edital", "chamada", "fomento", "seleção", "concurso", "pública"]):
            return None

        # Descrição
        paragraphs = content.select("p")
        descricao = ""
        for p in paragraphs[:5]:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 30:
                descricao += p_text + " "
        
        # Datas
        data_pub = extract_date(text)
        
        # Prazo (deadline)
        prazo = None
        prazo_patterns = [
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento)\s*:?\s*(\d{2}/\d{2}/\d{4})',
            r'(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in prazo_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                extracted = extract_date(match.group(1))
                if extracted:
                    if not prazo or extracted > prazo:
                        prazo = extracted

        # Anexos
        anexos = []
        for a in content.select("a[href$='.pdf'], a[href*='/download/']"):
            anexos.append({
                "nome": normalize_text(a.get_text()) or "Documento",
                "url": urljoin(self.base_url, a['href'])
            })

        return EditalABDI(
            titulo=titulo,
            link=url,
            descricao=descricao.strip() or titulo,
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": "ABDI"
            }
        )
