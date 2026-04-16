import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_mma import get_soup, normalize_text, extract_date, is_deadline_valid
from models_mma import EditalMMA

BASE_URL_GOV = "https://www.gov.br"
URLS = [
    "https://www.gov.br/mma/pt-br/assuntos/fundo-nacional-do-meio-ambiente",
    "https://www.gov.br/mma/pt-br/acesso-a-informacao/editais-e-chamamentos-publicos",
    "https://www.gov.br/mma/pt-br/assuntos/editais",
    "https://www.gov.br/mma/pt-br/assuntos/noticias"
]

class MMAScraper:
    def __init__(self):
        self.base_url_gov = BASE_URL_GOV

    def extract_editais(self) -> List[EditalMMA]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração MMA em: {url}")
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
                
                # Filtro de relevância para MMA/FNMA
                relevance_keywords = ["edital", "chamada", "chamamento", "selecao", "fomento", "programa", "projeto", "concurso", "pública", "propostas", "fnma"]
                avoid_keywords = ["pregão", "licitacao", "contratacao", "ata-de-registro", "dispensa", "facebook", "twitter", "linkedin", "whatsapp"]
                
                if any(kw in full_url.lower() or kw in titulo.lower() for kw in relevance_keywords):
                    if any(kw in full_url.lower() or kw in titulo.lower() for kw in avoid_keywords):
                        continue

                    seen_links.add(full_url)
                    print(f"Verificando potencial edital MMA: {titulo[:50]}...")
                    edital = self.process_detail_page(full_url, titulo)
                    if edital:
                        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                            continue
                        all_editais.append(edital)

        return all_editais

    def process_detail_page(self, url: str, titulo: str) -> Optional[EditalMMA]:
        if url.lower().endswith(".pdf"):
            return EditalMMA(
                titulo=titulo if len(titulo) > 10 else f"Documento: {url.split('/')[-1]}",
                link=url,
                descricao=titulo,
                situacao="Aberto",
                extras={"anexos": [{"nome": "Edital PDF", "url": url}], "fonte_original": "MMA gov.br"}
            )

        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("#content-core") or soup.select_one("article") or soup
        text = content.get_text()
        
        # Filtro de relevância final
        keywords = ["edital", "chamada", "chamamento", "fomento", "seleção", "pública", "propostas", "projeto", "programa", "meio ambiente"]
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

        return EditalMMA(
            titulo=titulo,
            link=url,
            descricao=descricao.strip() or titulo,
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": "MMA gov.br"
            }
        )
