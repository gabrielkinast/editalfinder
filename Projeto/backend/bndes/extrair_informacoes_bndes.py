import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_bndes import get_soup, normalize_text, extract_date, is_deadline_valid
from models_bndes import EditalBNDES

BASE_URL = "https://www.bndes.gov.br"
# URL fornecida pelo usuário
LIST_URL = "https://www.bndes.gov.br/wps/portal/site/home/mercado-de-capitais/fundos-de-investimentos/chamadas-publicas-para-selecao-de-fundos"

class BNDESScraper:
    def __init__(self):
        self.base_url = BASE_URL
        self.start_url = LIST_URL

    def extract_editais(self) -> List[EditalBNDES]:
        print(f"Iniciando extração BNDES em: {self.start_url}")
        soup = get_soup(self.start_url)
        if not soup:
            return []

        editais = []
        # O BNDES costuma listar chamadas em links dentro de uma área de conteúdo principal.
        # Vamos procurar por links que contenham palavras-chave de editais/chamadas.
        content = soup.select_one(".content") or soup.select_one("#conteudo") or soup.select_one("main")
        if not content:
            # Fallback para o corpo inteiro se não achar container específico
            content = soup

        # Encontra links para editais
        seen_links = set()
        
        # Procuramos por links em listas ou parágrafos
        for a in content.select("a[href]"):
            href = a.get("href")
            # Ignora links irrelevantes
            if any(x in href.lower() for x in ["facebook", "twitter", "linkedin", "youtube"]):
                continue
                
            full_url = urljoin(self.base_url, href).split("#", 1)[0]
            if full_url in seen_links:
                continue
            seen_links.add(full_url)

            # O título costuma ser o texto do link
            titulo = normalize_text(a.get_text())
            if not titulo or len(titulo) < 10:
                continue

            # Verificamos se parece um edital (ex: "Chamada", "Edital", "Seleção")
            if not any(kw in titulo.lower() for kw in ["chamada", "edital", "seleção", "fundo"]):
                continue

            print(f"Verificando edital potencial: {titulo}")
            edital = self.process_detail_page(full_url, titulo)
            if edital:
                # Aplicamos o filtro de deadline (fim_inscricao >= hoje)
                if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                    print(f"[SKIP] Deadline expirada: {edital.fim_inscricao}")
                    continue
                    
                editais.append(edital)

        return editais

    def process_detail_page(self, url: str, titulo: str) -> Optional[EditalBNDES]:
        soup = get_soup(url)
        if not soup:
            return None

        # Container de texto principal
        content = soup.select_one(".content") or soup.select_one("#conteudo") or soup.select_one("main") or soup
        text = content.get_text()
        
        # Descrição - tenta pegar os primeiros parágrafos relevantes
        paragraphs = content.select("p")
        descricao = ""
        for p in paragraphs[:5]:
            p_text = normalize_text(p.get_text())
            if p_text and len(p_text) > 30:
                descricao += p_text + " "
        
        # Datas
        data_pub = extract_date(text)
        
        # Prazo (deadline)
        # BNDES costuma indicar prazos com termos como "até", "prazo", "encerramento", "término"
        prazo = None
        # Padrões comuns para prazos de submissão
        prazo_patterns = [
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições)\s*:?\s*(\d{2}/\d{2}/\d{4})',
            r'(\d{2}/\d{2}/\d{4})'
        ]
        
        # Tenta encontrar no texto
        for pattern in prazo_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                extracted = extract_date(match.group(1))
                if extracted:
                    # Se houver várias datas, a maior costuma ser o deadline de inscrição
                    if not prazo or extracted > prazo:
                        prazo = extracted

        # Anexos (PDFs)
        anexos = []
        for a in content.select("a[href$='.pdf']"):
            anexos.append({
                "nome": normalize_text(a.get_text()) or "Documento PDF",
                "url": urljoin(self.base_url, a['href'])
            })

        return EditalBNDES(
            titulo=titulo,
            link=url,
            descricao=descricao.strip() or titulo,
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": "BNDES / Fundos de Investimento"
            }
        )
