import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_petrobras import get_soup, normalize_text, extract_date, is_deadline_valid
from models_petrobras import EditalPetrobras

BASE_URL = "https://petrobras.com.br"

URLS = [
    "https://petrobras.com.br/sustentabilidade/selecoes-publicas",
    "https://tecnologia.petrobras.com.br/modulo-startups.html",
    "https://petrobras.com.br/cultural/selecoes-publicas-culturais",
    "https://agencia.petrobras.com.br/w/noticias",
    "https://petrobras.com.br/inovacao-e-tecnologia/centro-de-pesquisa"
]

class PetrobrasScraper:
    def __init__(self):
        self.base_url = BASE_URL

    def extract_editais(self) -> List[EditalPetrobras]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração Petrobras em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            self._extract_from_page(soup, url, all_editais, seen_links)

        return all_editais

    def _extract_from_page(self, soup, current_url, editais_list, seen_links):
        # Procura links que pareçam editais ou chamadas
        # Na Petrobras, muitas vezes estão em seções específicas ou notícias
        
        main_content = soup.select_one("main") or soup.select_one("#content") or soup.select_one("article") or soup
        links = main_content.select("a[href]")
        
        for a in links:
            href = a.get("href")
            titulo = normalize_text(a.get_text())
            
            if not href.startswith("http"):
                href = urljoin(current_url, href)
            
            full_url = href.split("#", 1)[0]
            if full_url in seen_links:
                continue

            # Palavras-chave para identificar editais/fomento
            keywords = ["edital", "chamada", "seleção", "fomento", "programa", "projeto", "oportunidade", "concurso", "startup"]
            is_relevant = any(kw in full_url.lower() or kw in titulo.lower() for kw in keywords)
            
            # Filtros para evitar lixo
            irrelevant_ext = [".png", ".jpg", ".jpeg", ".gif", ".svg", ".mp4", ".mp3", ".css", ".js"]
            is_irrelevant_ext = any(full_url.lower().endswith(ext) for ext in irrelevant_ext)
            
            # Exclui licitações comerciais se necessário, mas usuário pediu "editais" de forma geral
            avoid = ["licitação", "pregão", "contratação de bens", "venda de ativos"]
            is_avoid = any(kw in full_url.lower() or kw in titulo.lower() for kw in avoid)

            if is_relevant and not is_avoid and not is_irrelevant_ext:
                # Se for um PDF direto
                if full_url.lower().endswith(".pdf"):
                    seen_links.add(full_url)
                    editais_list.append(EditalPetrobras(
                        titulo=titulo or "Edital Petrobras (PDF)",
                        link=full_url,
                        descricao=titulo,
                        extras={"fonte_original": current_url, "tipo": "PDF"}
                    ))
                    continue

                # Se for uma página de detalhe
                seen_links.add(full_url)
                edital = self.process_detail_page(full_url, titulo, source=current_url)
                if edital:
                    editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str, source: str) -> Optional[EditalPetrobras]:
        # Evita re-processar se for a mesma página de origem
        if url == source: return None
        
        print(f"Processando página detalhe Petrobras: {url}")
        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("main") or soup.select_one("#content") or soup.select_one("article") or soup
        text = content.get_text()
        
        # Título mais preciso
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
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento|entrega|final)\s*:?\s*(\d{2}/\d{2}/\d{4})',
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

        return EditalPetrobras(
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
