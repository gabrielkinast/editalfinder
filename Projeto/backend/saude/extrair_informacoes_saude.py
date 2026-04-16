import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_saude import get_soup, normalize_text, extract_date, is_deadline_valid
from models_saude import EditalSaude

BASE_URL_GOV = "https://www.gov.br"
BASE_URL_CNPQ = "http://memoria2.cnpq.br"

URLS = [
    "https://www.gov.br/saude/pt-br/assuntos/noticias/2026",
    "https://www.gov.br/saude/pt-br/assuntos/noticias/2025",
    "https://www.gov.br/saude/pt-br/composicao/sectics/decit",
    "http://memoria2.cnpq.br/web/guest/chamadas-publicas"
]

class SaudeScraper:
    def __init__(self):
        self.base_url_gov = BASE_URL_GOV
        self.base_url_cnpq = BASE_URL_CNPQ

    def extract_editais(self) -> List[EditalSaude]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração Ministério da Saúde em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            if "cnpq.br" in url:
                self._extract_from_cnpq(soup, all_editais, seen_links)
            else:
                self._extract_from_gov(soup, all_editais, seen_links)

        return all_editais

    def _extract_from_cnpq(self, soup, editais_list, seen_links):
        # Procura por editais que mencionem MS, Decit ou SCTIE
        items = soup.select("a[href*='link-permanente']")
        for a in items:
            parent = a.find_parent("div") or a.find_parent("td")
            text_context = normalize_text(parent.get_text()) if parent else ""
            
            # Filtro: deve ser do Ministério da Saúde
            if not any(kw in text_context.lower() for kw in ["ms", "decit", "sctie", "ministério da saúde"]):
                continue

            titulo = text_context
            href = a.get("href")
            full_url = urljoin(self.base_url_cnpq, href).split("#", 1)[0]
            
            if full_url in seen_links:
                continue
            seen_links.add(full_url)

            edital = self.process_detail_page(full_url, titulo, source="CNPq/MS-Decit")
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
            
            # Filtro: links que pareçam editais, chamadas ou notícias de fomento
            if any(kw in full_url.lower() or kw in titulo.lower() for kw in ["edital", "chamada", "selecao", "fomento", "programa", "concurso"]):
                # Evita links de redes sociais
                if any(x in full_url.lower() for x in ["facebook", "twitter", "linkedin", "whatsapp"]):
                    continue

                seen_links.add(full_url)
                print(f"Verificando potencial Ministério da Saúde: {titulo[:50]}...")
                edital = self.process_detail_page(full_url, titulo, source="MS gov.br")
                if edital:
                    if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                        continue
                    editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str, source: str) -> Optional[EditalSaude]:
        if url.lower().endswith(".pdf"):
            return EditalSaude(
                titulo=titulo if len(titulo) > 10 else f"Documento: {url.split('/')[-1]}",
                link=url,
                descricao=titulo,
                situacao="Aberto",
                extras={"anexos": [{"nome": "Edital PDF", "url": url}], "fonte_original": source}
            )

        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("#content-core") or soup.select_one("article") or soup
        text = content.get_text()
        
        # Filtro de relevância para Saúde/Decit/SCTIE
        is_relevant = any(kw in (titulo + text).lower() for kw in ["edital", "chamada", "fomento", "seleção", "pública", "propostas", "pesquisa"])
        is_ms = any(kw in (titulo + text).lower() for kw in ["ministério da saúde", "decit", "sctie", "sectics", "sus"])
        
        if not (is_relevant and is_ms):
            return None

        print(f"Encontrado edital/notícia relevante MS: {url}")

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

        # Anexos e links externos (CNPq)
        anexos = []
        for a in content.select("a[href]"):
            a_href = a.get("href")
            a_text = normalize_text(a.get_text())
            
            if a_href.lower().endswith(".pdf") or "cnpq.br" in a_href.lower() or "download" in a_href.lower():
                if not a_href.startswith("http"):
                    a_href = urljoin(self.base_url_gov, a_href)
                anexos.append({
                    "nome": a_text or "Link/Documento",
                    "url": a_href
                })

        return EditalSaude(
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
