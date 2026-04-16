import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_anp import get_soup, normalize_text, extract_date, is_deadline_valid
from models_anp import EditalANP

BASE_URL_GOV = "https://www.gov.br"
BASE_URL_FAPESP = "https://fapesp.br"

URLS = [
    "https://www.gov.br/anp/pt-br/assuntos/tecnologia-meio-ambiente/prh-anp-programa-de-formacao-de-recursos-humanos-1",
    "https://www.gov.br/anp/pt-br/assuntos/tecnologia-meio-ambiente/pdi",
    "https://www.gov.br/anp/pt-br/canais_atendimento/imprensa/noticias-comunicados",
    "https://fapesp.br/anp"
]

class ANPScraper:
    def __init__(self):
        self.base_url_gov = BASE_URL_GOV
        self.base_url_fapesp = BASE_URL_FAPESP

    def extract_editais(self) -> List[EditalANP]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração ANP em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            if "fapesp.br" in url:
                self._extract_from_fapesp(soup, all_editais, seen_links)
            else:
                self._extract_from_gov(soup, all_editais, seen_links)

        return all_editais

    def _extract_from_fapesp(self, soup, editais_list, seen_links):
        # Na FAPESP, procurar por links de chamadas ou editais que mencionem ANP
        links = soup.select("a[href]")
        for a in links:
            href = a.get("href")
            titulo = normalize_text(a.get_text())
            
            if not href.startswith("http"):
                href = urljoin(self.base_url_fapesp, href)
            
            full_url = href.split("#", 1)[0]
            if full_url in seen_links:
                continue

            # Critérios de relevância para fapesp.br/anp
            is_relevant = any(kw in full_url.lower() or kw in titulo.lower() for kw in ["edital", "chamada", "anp", "prh"])
            
            if is_relevant:
                seen_links.add(full_url)
                edital = self.process_detail_page(full_url, titulo, source="FAPESP/ANP")
                if edital:
                    editais_list.append(edital)

    def _extract_from_gov(self, soup, editais_list, seen_links):
        # No gov.br/anp, procurar em todo o conteúdo principal
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

            # Filtra por palavras-chave de fomento/editais
            keywords = ["edital", "chamada", "fomento", "programa", "projeto", "seleção", "prh", "pdi"]
            is_relevant = any(kw in full_url.lower() or kw in titulo.lower() for kw in keywords)
            
            # Exclui extensões irrelevantes (imagens, etc.)
            irrelevant_ext = [".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".mp3"]
            is_irrelevant_ext = any(full_url.lower().endswith(ext) for ext in irrelevant_ext)

            # Exclui licitações (conforme pedido anterior do usuário para outras agências)
            avoid = ["licitação", "pregão", "concurso", "contratação de serviços", "aquisição de bens"]
            is_avoid = any(kw in full_url.lower() or kw in titulo.lower() for kw in avoid)

            if is_relevant and not is_avoid and not is_irrelevant_ext:
                seen_links.add(full_url)
                edital = self.process_detail_page(full_url, titulo, source="ANP gov.br")
                if edital:
                    editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str, source: str) -> Optional[EditalANP]:
        if url.lower().endswith(".pdf"):
            return EditalANP(
                titulo=titulo or "Edital ANP (PDF)",
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
        
        print(f"Processando página detalhe ANP: {url}")

        # Título mais preciso se disponível
        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            h1_text = normalize_text(h1.get_text())
            if h1_text and len(h1_text) > 3:
                titulo = h1_text

        # Filtro final: se o título for muito curto ou genérico (como "Ops..."), pular
        if not titulo or len(titulo) < 4 or any(kw in titulo.lower() for kw in ["ops...", "erro", "not found", "404"]):
            return None

        # Descrição (primeiros parágrafos)
        paragraphs = content.select("p")
        descricao = ""
        count = 0
        for p in paragraphs:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 40:
                descricao += p_text + " "
                count += 1
            if count >= 4: break
        
        # Datas
        data_pub = extract_date(text)
        
        # Prazo (deadline)
        prazo = None
        prazo_patterns = [
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega)\s*:?\s*(\d{2}/\d{2}/\d{4})',
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega)\s+até\s+(\d{1,2}\s+de\s+[a-zA-Zç]+\s+de\s+\d{4})',
            r'(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in prazo_patterns:
            matches = re.findall(pattern, text, re.I)
            for m in matches:
                extracted = extract_date(m)
                if extracted:
                    # Se encontrarmos múltiplas datas, tentamos pegar a maior (geralmente o prazo final)
                    if not prazo or extracted > prazo:
                        prazo = extracted

        # Anexos
        anexos = []
        for a in content.select("a[href]"):
            a_href = a.get("href")
            a_text = normalize_text(a.get_text())
            if any(ext in a_href.lower() for ext in [".pdf", ".doc", ".zip", ".rar"]):
                if not a_href.startswith("http"):
                    base = self.base_url_fapesp if "fapesp.br" in url else self.base_url_gov
                    a_href = urljoin(base, a_href)
                anexos.append({"nome": a_text or "Documento", "url": a_href})

        return EditalANP(
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
