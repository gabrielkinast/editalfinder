import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional, Tuple
from utils_defesa import get_soup, normalize_text, extract_date, is_deadline_valid
from models_defesa import EditalDefesa, NoticiaDefesa

BASE_URL_GOV = "https://www.gov.br"
URLS_EDITAIS = [
    "https://www.gov.br/defesa/pt-br/assuntos/editais",
    "https://www.gov.br/defesa/pt-br/assuntos/programas-e-projetos",
]

URLS_NOTICIAS = [
    "https://www.gov.br/defesa/pt-br/assuntos/noticias",
]

class DefesaScraper:
    def __init__(self):
        self.base_url_gov = BASE_URL_GOV

    def extract_all(self) -> Tuple[List[EditalDefesa], List[NoticiaDefesa]]:
        editais = self.extract_editais()
        noticias = self.extract_noticias_militares()
        return editais, noticias

    def extract_editais(self) -> List[EditalDefesa]:
        all_editais = []
        seen_links = set()

        for url in URLS_EDITAIS:
            print(f"Iniciando extração editais Defesa em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            main_content = soup.select_one("#content-core") or soup.select_one("article") or soup
            links = main_content.select("a[href]")
            
            for a in links:
                href = a.get("href")
                titulo = normalize_text(a.get_text())
                
                if not href.startswith("http"):
                    href = urljoin(self.base_url_gov, href)
                
                full_url = href.split("#", 1)[0]
                if full_url in seen_links:
                    continue
                
                # Filtro de relevância para Defesa: editais, chamadas, fomento, programas
                relevance_keywords = ["edital", "chamada", "selecao", "fomento", "programa", "projeto", "concurso", "pública", "propostas"]
                avoid_keywords = ["pregão", "licitacao", "contratacao", "ata-de-registro", "dispensa", "facebook", "twitter", "linkedin", "whatsapp"]
                
                if any(kw in full_url.lower() or kw in titulo.lower() for kw in relevance_keywords):
                    if any(kw in full_url.lower() or kw in titulo.lower() for kw in avoid_keywords):
                        continue

                    seen_links.add(full_url)
                    print(f"Verificando potencial edital Defesa: {titulo[:50]}...")
                    edital = self.process_detail_edital(full_url, titulo)
                    if edital:
                        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                            continue
                        all_editais.append(edital)

        return all_editais

    def extract_noticias_militares(self) -> List[NoticiaDefesa]:
        all_noticias = []
        seen_links = set()

        # Palavras-chave para o JSON separado (armas, nuclear, etc)
        news_keywords = ["arma", "militar", "nuclear", "submarino", "caça", "blindado", "míssil", "tecnologia militar", "defesa nacional"]

        for url in URLS_NOTICIAS:
            print(f"Iniciando extração notícias Defesa em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            main_content = soup.select_one("#content-core") or soup.select_one("article") or soup
            links = main_content.select("a[href]")
            
            for a in links:
                href = a.get("href")
                titulo = normalize_text(a.get_text())
                
                if not href.startswith("http"):
                    href = urljoin(self.base_url_gov, href)
                
                full_url = href.split("#", 1)[0]
                if full_url in seen_links:
                    continue
                
                if any(kw in full_url.lower() or kw in titulo.lower() for kw in news_keywords):
                    if any(x in full_url.lower() for x in ["facebook", "twitter", "linkedin", "whatsapp"]):
                        continue

                    seen_links.add(full_url)
                    print(f"Verificando notícia Defesa: {titulo[:50]}...")
                    noticia = self.process_detail_noticia(full_url, titulo)
                    if noticia:
                        all_noticias.append(noticia)

        return all_noticias

    def process_detail_edital(self, url: str, titulo: str) -> Optional[EditalDefesa]:
        if url.lower().endswith(".pdf"):
            return EditalDefesa(
                titulo=titulo if len(titulo) > 10 else f"Documento: {url.split('/')[-1]}",
                link=url,
                descricao=titulo,
                situacao="Aberto",
                extras={"anexos": [{"nome": "Edital PDF", "url": url}], "fonte_original": "Defesa gov.br"}
            )

        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("#content-core") or soup.select_one("article") or soup
        text = content.get_text()
        
        # Filtro de relevância final
        keywords = ["edital", "chamada", "fomento", "seleção", "pública", "propostas", "projeto", "programa"]
        if not any(kw in (titulo + text).lower() for kw in keywords):
            return None

        # Título da página
        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            titulo = normalize_text(h1.get_text())

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
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega)\s*:?\s*(\d{2}/\d{2}/\d{4})',
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
            
            if a_href.lower().endswith(".pdf") or "download" in a_href.lower():
                if not a_href.startswith("http"):
                    a_href = urljoin(self.base_url_gov, a_href)
                anexos.append({
                    "nome": a_text or "Link/Documento",
                    "url": a_href
                })

        return EditalDefesa(
            titulo=titulo,
            link=url,
            descricao=descricao.strip() or titulo,
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": "Defesa gov.br"
            }
        )

    def process_detail_noticia(self, url: str, titulo: str) -> Optional[NoticiaDefesa]:
        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("#content-core") or soup.select_one("article") or soup
        text = content.get_text()
        
        # Título da página
        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            titulo = normalize_text(h1.get_text())

        # Descrição
        paragraphs = content.select("p")
        descricao = ""
        for p in paragraphs[:3]:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 30:
                descricao += p_text + " "
        
        # Data
        data_pub = extract_date(text)

        return NoticiaDefesa(
            titulo=titulo,
            link=url,
            descricao=descricao.strip(),
            data_publicacao=data_pub
        )
