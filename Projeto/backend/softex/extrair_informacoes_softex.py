import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_softex import get_soup, normalize_text, extract_date, is_deadline_valid
from models_softex import EditalSoftex

BASE_URL = "https://softex.br"
URLS = [
    "https://softex.br/editais/",
    "https://softex.br/noticias/",
    "https://softex.br/categoria/programas/"
]

class SoftexScraper:
    def __init__(self):
        self.base_url = BASE_URL

    def extract_editais(self) -> List[EditalSoftex]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração Softex em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            # Softex /editais/ usa uma estrutura de tabela ou lista de posts
            # Vamos procurar por links dentro de divs de conteúdo ou tabelas
            main_content = soup.select_one(".entry-content") or soup.select_one(".post-content") or soup.select_one("main") or soup
            
            # Se for a página de editais, a estrutura é específica (tabela)
            if "editais" in url:
                rows = soup.select("tr")
                for row in rows:
                    cells = row.select("td")
                    if not cells: continue
                    
                    titulo_cell = cells[0]
                    link_tag = row.select_one("a[href]")
                    
                    if link_tag:
                        titulo = normalize_text(titulo_cell.get_text())
                        # Remove a data que às vezes vem grudada no título
                        titulo = re.sub(r'\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4}$', '', titulo, flags=re.I).strip()
                        
                        href = link_tag['href']
                        full_url = urljoin(self.base_url, href).split("#", 1)[0]
                        
                        if full_url in seen_links: continue
                        seen_links.add(full_url)
                        
                        # Extrai a data do texto da célula se houver
                        data_pub = extract_date(titulo_cell.get_text())
                        
                        edital = EditalSoftex(
                            titulo=titulo,
                            link=full_url,
                            descricao=titulo,
                            data_publicacao=data_pub,
                            situacao="Aberto" if "cancelamento" not in titulo.lower() else "Cancelado"
                        )
                        
                        # Tenta pegar detalhes se não for um PDF direto
                        if not full_url.lower().endswith(".pdf"):
                            edital = self.process_detail_page(full_url, edital)
                        else:
                            edital.extras = {"anexos": [{"nome": "Edital PDF", "url": full_url}]}
                            
                        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                            continue
                            
                        all_editais.append(edital)
                        print(f"Encontrado edital Softex: {titulo[:50]}...")
            
            else:
                # Outras páginas (notícias, programas)
                links = main_content.select("a[href]")
                for a in links:
                    href = a.get("href")
                    titulo = normalize_text(a.get_text())
                    
                    if not href.startswith("http"):
                        href = urljoin(self.base_url, href)
                    
                    full_url = href.split("#", 1)[0]
                    if full_url in seen_links: continue
                    
                    # Filtro de relevância
                    if any(kw in full_url.lower() or kw in titulo.lower() for kw in ["edital", "chamada", "selecao", "fomento", "ia2", "brasil-it", "programa"]):
                        if any(x in full_url.lower() for x in ["facebook", "twitter", "linkedin", "whatsapp", "instagram"]):
                            continue

                        seen_links.add(full_url)
                        print(f"Verificando potencial Softex: {titulo[:50]}...")
                        
                        edital = EditalSoftex(
                            titulo=titulo,
                            link=full_url,
                            descricao=titulo
                        )
                        
                        if not full_url.lower().endswith(".pdf"):
                            edital = self.process_detail_page(full_url, edital)
                        else:
                            edital.extras = {"anexos": [{"nome": "Documento PDF", "url": full_url}]}
                            
                        if edital and edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                            continue
                            
                        if edital:
                            all_editais.append(edital)

        return all_editais

    def process_detail_page(self, url: str, edital: EditalSoftex) -> Optional[EditalSoftex]:
        soup = get_soup(url)
        if not soup:
            return edital

        content = soup.select_one(".entry-content") or soup.select_one("article") or soup
        text = content.get_text()
        
        # Se for notícia, verifica se é anúncio de edital
        if "noticias" in url:
            if not any(kw in (edital.titulo + text).lower() for kw in ["edital", "chamada", "inscrições", "abertas", "fomento"]):
                return None

        # Título da página
        h1 = soup.select_one("h1")
        if h1:
            edital.titulo = normalize_text(h1.get_text())

        # Descrição
        paragraphs = content.select("p")
        descricao = ""
        for p in paragraphs[:5]:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 30:
                descricao += p_text + " "
        edital.descricao = descricao.strip() or edital.titulo
        
        # Datas
        if not edital.data_publicacao:
            edital.data_publicacao = extract_date(text)
        
        # Prazo (deadline)
        prazo = None
        prazo_patterns = [
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega)\s*:?\s*(\d{2}/\d{2}/\d{4})',
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega)\s*:?\s*(\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4})',
            r'(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in prazo_patterns:
            matches = re.findall(pattern, text, re.I)
            for m in matches:
                extracted = extract_date(m)
                if extracted:
                    if not prazo or extracted > prazo:
                        prazo = extracted
        edital.fim_inscricao = prazo

        # Anexos
        anexos = []
        for a in content.select("a[href]"):
            a_href = a.get("href")
            a_text = normalize_text(a.get_text())
            
            if a_href.lower().endswith(".pdf") or "download" in a_href.lower():
                if not a_href.startswith("http"):
                    a_href = urljoin(self.base_url, a_href)
                anexos.append({
                    "nome": a_text or "Documento",
                    "url": a_href
                })
        
        edital.extras = {
            "anexos": anexos,
            "fonte_original": "Softex"
        }

        return edital
