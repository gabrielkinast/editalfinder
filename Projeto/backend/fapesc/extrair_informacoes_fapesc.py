import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_fapesc import get_soup, normalize_text, extract_date, is_deadline_valid
from models_fapesc import EditalFapesc

BASE_URL = "https://fapesc.sc.gov.br"

URLS = [
    "https://fapesc.sc.gov.br/category/chamadas-abertas/",
    "https://fapesc.sc.gov.br/category/chamadas-em-andamento/",
    "https://fapesc.sc.gov.br/category/chamadas-publicas/"
]

class FapescScraper:
    def __init__(self):
        self.base_url = BASE_URL

    def extract_editais(self) -> List[EditalFapesc]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração FAPESC em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            self._extract_from_list(soup, url, all_editais, seen_links)

        return all_editais

    def _extract_from_list(self, soup, current_url, editais_list, seen_links):
        # Na FAPESC os editais estão em posts de blog dentro dessas categorias
        articles = soup.select("article")
        if not articles:
            # Tenta encontrar por classes comuns de tema de wordpress
            articles = soup.select(".post") or soup.select(".entry")

        for article in articles:
            a = article.select_one("a[href]")
            if not a: continue
            
            href = a.get("href")
            titulo = normalize_text(a.get_text())
            
            if not href or href.startswith("#"):
                continue

            if not href.startswith("http"):
                href = urljoin(current_url, href)
            
            full_url = href.split("?", 1)[0].split("#", 1)[0]
            if full_url in seen_links:
                continue

            # Critérios de relevância
            keywords = ["edital", "chamada", "seleção", "fomento", "programa", "projeto", "bolsa", "subvenção", "inovação"]
            is_relevant = any(kw in full_url.lower() or kw in titulo.lower() for kw in keywords)
            
            # Filtros de exclusão
            avoid = ["licitação", "pregão", "concurso público", "contratação de bens", "venda de ativos"]
            is_avoid = any(kw in full_url.lower() or kw in titulo.lower() for kw in avoid)

            if is_relevant and not is_avoid:
                seen_links.add(full_url)
                edital = self.process_detail_page(full_url, titulo, source=current_url)
                if edital:
                    editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str, source: str) -> Optional[EditalFapesc]:
        print(f"Processando página detalhe FAPESC: {url}")
        soup = get_soup(url)
        if not soup:
            return None

        # O conteúdo principal do wordpress geralmente está em .entry-content ou article
        content = soup.select_one(".entry-content") or soup.select_one("article") or soup.select_one(".post-content") or soup
        text = content.get_text()
        
        # Título
        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            h1_text = normalize_text(h1.get_text())
            if len(h1_text) > 5:
                titulo = h1_text

        if any(kw in titulo.lower() for kw in ["ops...", "erro", "not found", "404"]):
            return None

        # Descrição
        paragraphs = content.select("p")
        descricao = ""
        count = 0
        for p in paragraphs:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 40:
                descricao += p_text + " "
                count += 1
            if count >= 6: break
        
        # Datas
        data_pub = extract_date(text)
        
        # Prazo (deadline) - FAPESC costuma colocar "Prazo para submissão: DD/MM/YYYY a DD/MM/YYYY"
        prazo = None
        prazo_patterns = [
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega|final|limite)\s*:?\s*(\d{2}/\d{2}/\d{4})\s*a\s*(\d{2}/\d{2}/\d{4})',
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega|final|limite)\s*:?\s*(\d{2}/\d{2}/\d{4})',
            r'(?:inscrições|vão)\s+até\s+(\d{1,2}\s+de\s+[a-zA-Zç]+\s+de\s+\d{4})',
            r'(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in prazo_patterns:
            matches = re.findall(pattern, text, re.I)
            for m in matches:
                # Se for o formato "DE ... A ...", pegamos a segunda data
                if isinstance(m, tuple) and len(m) == 2:
                    extracted = extract_date(m[1])
                else:
                    extracted = extract_date(m)
                
                if extracted:
                    if not prazo or extracted > prazo:
                        prazo = extracted

        # Anexos
        anexos = []
        for a in content.select("a[href]"):
            a_href = a.get("href")
            a_text = normalize_text(a.get_text())
            if any(ext in a_href.lower() for ext in [".pdf", ".doc", ".zip", ".rar"]):
                if not a_href.startswith("http"):
                    a_href = urljoin(url, a_href)
                anexos.append({"nome": a_text or "Documento", "url": a_href})

        return EditalFapesc(
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
