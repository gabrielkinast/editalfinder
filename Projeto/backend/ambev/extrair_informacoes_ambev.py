import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_ambev import get_soup, normalize_text, extract_date, is_deadline_valid
from models_ambev import EditalAmbev

BASE_URL = "https://www.ambev.com.br"

URLS = [
    "https://www.ambev.com.br/startups",
    "https://www.100accelerator.com/",
    "https://www.ambev.com.br/sustentabilidade",
    "https://www.ambev.com.br/sala-de-imprensa"
]

class AmbevScraper:
    def __init__(self):
        self.base_url = BASE_URL

    def extract_editais(self) -> List[EditalAmbev]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração AMBEV em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            self._extract_from_page(soup, url, all_editais, seen_links)

        return all_editais

    def _extract_from_page(self, soup, current_url, editais_list, seen_links):
        # Captura links de todo o documento, não apenas main
        links = soup.select("a[href]")
        
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

            # Palavras-chave expandidas
            keywords = [
                "edital", "chamada", "seleção", "fomento", "programa", "projeto", 
                "startup", "aceleradora", "inovação", "sustentabilidade", 
                "inscrição", "impacto", "esg", "challenge", "oportunidade"
            ]
            
            url_lower = full_url.lower()
            titulo_lower = titulo.lower()
            
            is_relevant = any(kw in url_lower or kw in titulo_lower for kw in keywords)
            
            # Filtros de exclusão
            irrelevant_ext = [".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".mp3", ".css", ".js", ".ico"]
            is_irrelevant_ext = any(url_lower.endswith(ext) for ext in irrelevant_ext)
            
            avoid_links = ["facebook.com", "instagram.com", "linkedin.com", "twitter.com", "youtube.com", "whatsapp.com", "google.com"]
            is_avoid_link = any(avoid in url_lower for avoid in avoid_links)

            if is_relevant and not is_irrelevant_ext and not is_avoid_link:
                # Se for PDF
                if url_lower.endswith(".pdf"):
                    seen_links.add(full_url)
                    editais_list.append(EditalAmbev(
                        titulo=titulo or "Documento AMBEV",
                        link=full_url,
                        descricao=titulo or "Edital/Documento relevante encontrado",
                        extras={"fonte_original": current_url, "tipo": "PDF"}
                    ))
                    continue

                # Processa página de detalhe
                seen_links.add(full_url)
                edital = self.process_detail_page(full_url, titulo, source=current_url)
                if edital:
                    editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str, source: str) -> Optional[EditalAmbev]:
        if url == source: return None
        
        # Não processa páginas externas muito grandes para evitar loop infinito ou lentidão
        if "ambev.com.br" not in url and "100accelerator.com" not in url:
            return EditalAmbev(
                titulo=titulo,
                link=url,
                descricao=f"Link externo relevante encontrado em {source}",
                situacao="Aberto",
                extras={"fonte_original": source, "externo": True}
            )

        print(f"Processando página detalhe AMBEV: {url}")
        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("main") or soup.select_one("#content") or soup.select_one("article") or soup
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
            if len(p_text) > 50:
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
            if any(ext in a_href.lower() for ext in [".pdf", ".doc", ".zip", ".rar"]):
                if not a_href.startswith("http"):
                    a_href = urljoin(url, a_href)
                anexos.append({"nome": a_text or "Documento", "url": a_href})

        return EditalAmbev(
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
