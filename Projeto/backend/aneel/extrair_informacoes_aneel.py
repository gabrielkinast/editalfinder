import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from pathlib import Path
import sys
from utils_aneel import get_soup, normalize_text, extract_date, is_deadline_valid
from models_aneel import EditalAneel

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from CORE.http_fetch import fetch_pdf_bytes
from CORE.pdf_enrichment import extract_pdf_text_with_fallback

BASE_URL = "https://www.gov.br"

URLS = [
    "https://www.gov.br/aneel/pt-br/assuntos/programa-de-pesquisa-desenvolvimento-e-inovacao/chamadas-de-projetos-de-pdi-estrategicos",
    "https://www.gov.br/aneel/pt-br/assuntos/programa-de-pesquisa-desenvolvimento-e-inovacao",
    "https://www.gov.br/aneel/pt-br/canais_atendimento/imprensa/noticias",
    "https://www.gov.br/aneel/pt-br/assuntos/programa-de-pesquisa-desenvolvimento-e-inovacao/projetos-prioritarios-de-p-d",
    "https://dadosabertos.aneel.gov.br/dataset/projetos-de-p-d-em-energia-eletrica"
]

class AneelScraper:
    def __init__(self):
        self.base_url = BASE_URL

    def extract_editais(self) -> List[EditalAneel]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração ANEEL em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            self._extract_from_page(soup, url, all_editais, seen_links)

        return all_editais

    def _extract_from_page(self, soup, current_url, editais_list, seen_links):
        # No gov.br/aneel, procurar links que pareçam editais ou chamadas
        main_content = soup.select_one("#content-core") or soup.select_one("article") or soup
        links = main_content.select("a[href]")
        
        for a in links:
            href = a.get("href")
            titulo = normalize_text(a.get_text())
            
            if not href or href.startswith("javascript:") or href.startswith("#"):
                continue

            if not href.startswith("http"):
                href = urljoin(current_url, href)
            
            full_url = href.split("?", 1)[0].split("#", 1)[0]
            if full_url in seen_links:
                continue

            # Critérios de relevância para ANEEL
            keywords = [
                "edital", "chamada", "seleção", "fomento", "programa", "projeto", 
                "pdi", "p&d", "inovação", "pesquisa", "desenvolvimento", "leilão"
            ]
            
            url_lower = full_url.lower()
            titulo_lower = titulo.lower()
            
            is_relevant = any(kw in url_lower or kw in titulo_lower for kw in keywords)
            
            # Filtros de exclusão (licitações administrativas conforme pedido anterior)
            avoid = ["licitação", "pregão", "concurso público", "contratação de bens", "venda de ativos", "processo seletivo simplificado"]
            is_avoid = any(kw in url_lower or kw in titulo_lower for kw in avoid)
            
            # Exclui imagens/arquivos irrelevantes
            irrelevant_ext = [".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".mp3", ".css", ".js", ".ico"]
            is_irrelevant_ext = any(url_lower.endswith(ext) for ext in irrelevant_ext)

            if is_relevant and not is_avoid and not is_irrelevant_ext:
                seen_links.add(full_url)
                
                # Se for PDF direto
                if url_lower.endswith(".pdf"):
                    pdf_text = ""
                    try:
                        pdf_bytes = fetch_pdf_bytes(full_url, page_referer=current_url)
                        if pdf_bytes:
                            extracted = extract_pdf_text_with_fallback(pdf_bytes, max_pages=5) or ""
                            pdf_text = normalize_text(extracted)[:2200]
                    except Exception:
                        pdf_text = ""
                    title_from_pdf = self._guess_pdf_title(full_url, titulo, pdf_text)
                    editais_list.append(EditalAneel(
                        titulo=title_from_pdf,
                        link=full_url,
                        descricao=(pdf_text[:900] if pdf_text else titulo or "Documento de edital/chamada da ANEEL"),
                        data_publicacao=extract_date(pdf_text) if pdf_text else None,
                        fim_inscricao=self._extract_deadline_iso(pdf_text) if pdf_text else None,
                        extras={
                            "fonte_original": current_url,
                            "tipo": "PDF",
                            "pdf_url": full_url,
                            "pdf_texto_extraido": pdf_text,
                            "pdf_resumo": pdf_text[:500] if pdf_text else "",
                            "metodo_extracao": "pdf_enriched",
                        }
                    ))
                    continue

                # Processa página de detalhe
                edital = self.process_detail_page(full_url, titulo, source=current_url)
                if edital:
                    editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str, source: str) -> Optional[EditalAneel]:
        if url == source: return None
        
        print(f"Processando página detalhe ANEEL: {url}")
        soup = get_soup(url)
        if not soup:
            return None

        # Conteúdo principal do gov.br
        content = soup.select_one("#content-core") or soup.select_one("article") or soup
        text = content.get_text()
        
        # Título mais preciso
        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            h1_text = normalize_text(h1.get_text())
            if len(h1_text) > 5:
                titulo = h1_text

        if any(kw in titulo.lower() for kw in ["ops...", "erro", "not found", "404"]):
            return None

        # Descrição (primeiros parágrafos relevantes)
        paragraphs = content.select("p")
        descricao = ""
        count = 0
        for p in paragraphs:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 40:
                descricao += p_text + " "
                count += 1
            if count >= 5: break
        
        # Datas
        data_pub = extract_date(text)
        
        # Prazo (deadline)
        prazo = None
        prazo_patterns = [
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega|final|limite)\s*:?\s*(\d{2}/\d{2}/\d{4})',
            r'(?:inscrições|vão)\s+até\s+(\d{1,2}\s+de\s+[a-zA-Zç]+\s+de\s+\d{4})',
            r'(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in prazo_patterns:
            matches = re.findall(pattern, text, re.I)
            for m in matches:
                extracted = extract_date(m)
                if extracted:
                    if not prazo or extracted > prazo:
                        prazo = extracted

        # Anexos
        anexos = []
        for a in content.select("a[href]"):
            a_href = a.get("href")
            a_text = normalize_text(a.get_text())
            if any(ext in a_href.lower() for ext in [".pdf", ".doc", ".zip", ".rar", ".xls", ".xlsx"]):
                if not a_href.startswith("http"):
                    a_href = urljoin(url, a_href)
                anexos.append({"nome": a_text or "Documento", "url": a_href})

        return EditalAneel(
            titulo=titulo,
            link=url,
            descricao=descricao.strip() or titulo,
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": source,
                "data_extracao": datetime.now().strftime("%Y-%m-%d")
            }
        )

    def _guess_pdf_title(self, url: str, anchor_title: str, pdf_text: str) -> str:
        for ln in (pdf_text or "").split("."):
            txt = normalize_text(ln)
            low = txt.lower()
            if len(txt) < 12:
                continue
            if any(k in low for k in ["edital", "chamada", "concurso", "projeto p&d", "pdi", "termo de referência"]):
                return txt[:240]
        if anchor_title and len(anchor_title.strip()) > 8 and anchor_title.strip().lower() not in {"baixar", "edital", "english version"}:
            return anchor_title.strip()[:240]
        filename = url.split("/")[-1].replace(".pdf", "").replace("_", " ").replace("-", " ")
        return f"ANEEL - {normalize_text(filename)[:180]}"

    def _extract_deadline_iso(self, text: str) -> Optional[str]:
        m = re.search(r"(\d{2}/\d{2}/\d{4})", text or "")
        return extract_date(m.group(1)) if m else None
