import re
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_fappr import get_soup, normalize_text, extract_date, is_deadline_valid
from models_fappr import EditalFappr

BASE_URL = "https://www.fappr.pr.gov.br"

URLS = [
    "https://www.fappr.pr.gov.br/Programas-Abertos",
    "https://www.fappr.pr.gov.br/Pagina/Programas-2025",
    "https://www.fappr.pr.gov.br/Pagina/Programas-2026"
]

class FapprScraper:
    def __init__(self):
        self.base_url = BASE_URL

    def extract_editais(self) -> List[EditalFappr]:
        all_editais = []
        seen_links = set()

        for url in URLS:
            print(f"Iniciando extração Fundação Araucária em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            self._extract_from_page(soup, url, all_editais, seen_links)

        return all_editais

    def _extract_from_page(self, soup, current_url, editais_list, seen_links):
        # A Fundação Araucária costuma usar divs com títulos em negrito ou h3/h4 para cada edital
        # Vamos procurar por padrões comuns de contêineres de editais
        
        # Procura por blocos de conteúdo que contenham "CP" ou "PI" (Chamada Pública ou Inexigibilidade)
        content_divs = soup.select(".field-item") or [soup.select_one("#content")] or [soup]
        
        for container in content_divs:
            # Encontrar todos os parágrafos ou h3 que pareçam títulos de chamadas
            items = container.find_all(['p', 'h2', 'h3', 'h4', 'strong'])
            
            for item in items:
                text = normalize_text(item.get_text())
                # Exemplo: "CP 04/26: Interconexões Brasillinois"
                if re.search(r'(CP|PI|PA|PMI)\s+\d+/\d+', text, re.I):
                    titulo = text
                    
                    # O próximo elemento ou o próprio elemento costuma ter links
                    # Vamos procurar links nos arredores do título
                    parent = item.parent
                    links_found = parent.select("a[href]")
                    
                    edital_link = None
                    anexos = []
                    
                    for a in links_found:
                        a_href = a.get("href")
                        a_text = normalize_text(a.get_text())
                        
                        if not a_href.startswith("http"):
                            a_href = urljoin(self.base_url, a_href)
                            
                        if "edital" in a_text.lower() or "edital" in a_href.lower():
                            edital_link = a_href
                        elif any(ext in a_href.lower() for ext in [".pdf", ".doc", ".zip", ".rar"]):
                            anexos.append({"nome": a_text or "Documento", "url": a_href})

                    # Se não achou um link específico de edital, usa o primeiro PDF ou o próprio link do título se houver
                    if not edital_link and anexos:
                        edital_link = anexos[0]["url"]
                    elif not edital_link and item.name == 'a':
                        edital_link = urljoin(self.base_url, item.get("href"))

                    if edital_link and edital_link not in seen_links:
                        seen_links.add(edital_link)
                        
                        # Tenta pegar a descrição (parágrafo seguinte ao título)
                        descricao = ""
                        next_sibling = item.find_next_sibling()
                        if next_sibling and next_sibling.name == 'p':
                            descricao = normalize_text(next_sibling.get_text())
                        
                        # Datas e prazos costumam estar na descrição ou no título
                        data_pub = extract_date(titulo) or extract_date(descricao)
                        
                        # FAPPR costuma não ter data de fim explícita no HTML, mas vamos tentar
                        fim_insc = None
                        prazo_match = re.search(r'até\s+(\d{2}/\d{2}/\d{4})', descricao.lower() + " " + titulo.lower())
                        if prazo_match:
                            fim_insc = extract_date(prazo_match.group(1))

                        editais_list.append(EditalFappr(
                            titulo=titulo,
                            link=edital_link,
                            descricao=descricao or titulo,
                            data_publicacao=data_pub,
                            fim_inscricao=fim_insc,
                            situacao="Aberto",
                            extras={
                                "anexos": anexos,
                                "fonte_original": current_url,
                                "tipo_chamada": titulo.split(":")[0] if ":" in titulo else "Chamada"
                            }
                        ))

    def process_detail_page(self, url: str, titulo: str, source: str) -> Optional[EditalFappr]:
        # Para FAPPR, a maioria das informações já está na página de listagem
        # Mas se for uma página interna, processamos
        if url.lower().endswith(".pdf"):
            return None # Já tratado na listagem

        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one(".field-item") or soup.select_one("#content") or soup
        text = content.get_text()
        
        # Tenta extrair mais detalhes se necessário
        data_pub = extract_date(text)
        
        return EditalFappr(
            titulo=titulo,
            link=url,
            descricao=normalize_text(text[:500]),
            data_publicacao=data_pub,
            situacao="Aberto",
            extras={"fonte_original": source}
        )
