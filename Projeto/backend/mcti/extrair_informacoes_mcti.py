import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_mcti import get_soup, normalize_text, extract_date, is_deadline_valid
from models_mcti import EditalMCTI

BASE_URL_GOV = "https://www.gov.br"
BASE_URL_FINEP = "http://www.finep.gov.br"
BASE_URL_CNPQ = "http://memoria2.cnpq.br"

URLS = [
    "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/editais-e-chamadas-publicas",
    "http://www.finep.gov.br/chamadas-publicas?situacao=aberta",
    "http://memoria2.cnpq.br/web/guest/chamadas-publicas"
]

class MCTIScraper:
    def __init__(self):
        self.base_url_gov = BASE_URL_GOV
        self.base_url_finep = BASE_URL_FINEP
        self.base_url_cnpq = BASE_URL_CNPQ

    def extract_editais(self) -> List[EditalMCTI]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração MCTI em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            if "finep.gov.br" in url:
                self._extract_from_finep(soup, all_editais, seen_links)
            elif "cnpq.br" in url:
                self._extract_from_cnpq(soup, all_editais, seen_links)
            else:
                self._extract_from_gov(soup, all_editais, seen_links)

        return all_editais

    def _extract_from_finep(self, soup, editais_list, seen_links):
        # Procura por editais que mencionem MCTI
        items = soup.select("a[href*='/chamadas-publicas/chamadapublica/']")
        for a in items:
            titulo = normalize_text(a.get_text())
            href = a.get("href")
            full_url = urljoin(self.base_url_finep, href).split("#", 1)[0]
            
            if full_url in seen_links:
                continue
            seen_links.add(full_url)

            # Entra na página para verificar se é MCTI
            edital = self.process_detail_page(full_url, titulo, source="Finep/MCTI")
            if edital:
                editais_list.append(edital)

    def _extract_from_cnpq(self, soup, editais_list, seen_links):
        # No CNPq memoria2, os editais estão em uma lista
        items = soup.select("a[href*='link-permanente']")
        for a in items:
            # O título costuma estar no elemento anterior ou pai
            parent = a.find_parent("div") or a.find_parent("td")
            titulo = normalize_text(parent.get_text()) if parent else "Edital CNPq"
            href = a.get("href")
            full_url = urljoin(self.base_url_cnpq, href).split("#", 1)[0]
            
            if full_url in seen_links:
                continue
            seen_links.add(full_url)

            edital = self.process_detail_page(full_url, titulo, source="CNPq/MCTI")
            if edital:
                editais_list.append(edital)

    def _extract_from_gov(self, soup, editais_list, seen_links):
        main_content = soup.select_one("#content-core") or soup
        links = main_content.select("a[href]")
        for a in links:
            href = a.get("href")
            titulo = normalize_text(a.get_text())
            if not href.startswith("http"):
                href = urljoin(self.base_url_gov, href)
            
            full_url = href.split("#", 1)[0]
            if full_url in seen_links:
                continue
            seen_links.add(full_url)

            if any(kw in full_url.lower() or kw in titulo.lower() for kw in ["edital", "chamada", "selecao"]):
                edital = self.process_detail_page(full_url, titulo, source="MCTI gov.br")
                if edital:
                    editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str, source: str) -> Optional[EditalMCTI]:
        if url.lower().endswith(".pdf"):
            return EditalMCTI(
                titulo=titulo,
                link=url,
                descricao=titulo,
                situacao="Aberto",
                extras={"anexos": [{"nome": "Edital PDF", "url": url}], "fonte_original": source}
            )

        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("#content") or soup.select_one("#content-core") or soup.select_one("article") or soup
        text = content.get_text()
        
        # Filtro: deve conter MCTI ou Ministério da Ciência no texto se vier de Finep/CNPq
        if "finep" in url or "cnpq" in url:
            if not any(kw in (titulo + text).lower() for kw in ["mcti", "ministério da ciência", "ministério de ciência"]):
                return None

        print(f"Encontrado edital relevante para MCTI em {source}: {url}")

        # Título
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
        
        # Prazo
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
                    # Determina a base correta
                    current_base = self.base_url_gov
                    if "finep.gov.br" in url: current_base = self.base_url_finep
                    if "cnpq.br" in url: current_base = self.base_url_cnpq
                    a_href = urljoin(current_base, a_href)
                anexos.append({"nome": a_text or "Documento", "url": a_href})

        return EditalMCTI(
            titulo=titulo,
            link=url,
            descricao=descricao.strip() or titulo,
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": source
            }
        )
