import re
import requests
from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional
from utils_abdi import get_soup, normalize_text, extract_date, is_deadline_valid
from models_abdi import EditalABDI

BASE_URL = "https://www.abdi.com.br"
URLS = [
    "https://www.abdi.com.br/agro-40/editais-e-documentos/",
    "https://www.abdi.com.br/transparencia/aquisicao-de-bens-e-servicos/",
    "https://www.abdi.com.br/transparencia/consultas-publicas/",
    "https://www.abdi.com.br/concursos/"
]

class ABDIScraper:
    def __init__(self):
        self.base_url = BASE_URL

    def extract_editais(self) -> List[EditalABDI]:
        all_editais = []
        for url in URLS:
            print(f"Iniciando extração ABDI em: {url}")
            soup = get_soup(url)
            if not soup:
                continue

            # ABDI usa tabelas ou listas para transparência
            # Procura por linhas de tabela (tr) ou links que pareçam editais
            content = soup.select_one(".content") or soup.select_one("article") or soup.select_one("main") or soup
            
            # Tenta encontrar links que contenham palavras-chave no texto ou na URL
            links = content.select("a[href]")
            for a in links:
                href = a.get("href")
                titulo = normalize_text(a.get_text())
                
                # Filtro: links internos que pareçam editais/documentos
                if any(kw in href.lower() or kw in titulo.lower() for kw in ["edital", "chamada", "fomento", "selecao", "concurso", "termo-de-referencia", "processo-seletivo"]):
                    if not href.startswith("http"):
                        href = urljoin(self.base_url, href)
                    
                    # Evita duplicatas
                    full_url = href.split("#", 1)[0]
                    if any(e.link == full_url for e in all_editais):
                        continue
                        
                    # Se for PDF direto, cria o edital sem entrar na página
                    if full_url.lower().endswith(".pdf"):
                        edital = EditalABDI(
                            titulo=titulo if len(titulo) > 10 else f"Documento: {full_url.split('/')[-1]}",
                            link=full_url,
                            descricao=titulo,
                            situacao="Aberto",
                            extras={"anexos": [{"nome": "Edital PDF", "url": full_url}], "fonte_original": "ABDI"}
                        )
                        all_editais.append(edital)
                        print(f"Encontrado PDF direto: {edital.titulo[:50]}...")
                    else:
                        print(f"Verificando página de edital: {titulo[:50]}...")
                        edital = self.process_detail_page(full_url, titulo)
                        if edital:
                            if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                                continue
                            all_editais.append(edital)

        return all_editais

    def _process_link(self, a, source_url, editais_list):
        href = a.get("href")
        full_url = urljoin(self.base_url, href).split("#", 1)[0]
        if any(e.link == full_url for e in editais_list):
            return
        
        titulo = normalize_text(a.get_text())
        if len(titulo) < 10:
            return
            
        edital = self.process_detail_page(full_url, titulo)
        if edital:
            if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                return
            editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str) -> Optional[EditalABDI]:
        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one(".content") or soup.select_one("article") or soup.select_one("main") or soup
        text = content.get_text()
        
        # Filtro de relevância: Verificamos se o texto contém palavras-chave de fomento/editais
        if not any(kw in (titulo + text).lower() for kw in ["edital", "chamada", "fomento", "seleção", "concurso", "pública"]):
            return None

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
            r'(?:prazo|vencimento|término|até|submissão|propostas|inscrições|encerramento)\s*:?\s*(\d{2}/\d{2}/\d{4})',
            r'(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in prazo_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                extracted = extract_date(match.group(1))
                if extracted:
                    if not prazo or extracted > prazo:
                        prazo = extracted

        # Anexos
        anexos = []
        for a in content.select("a[href$='.pdf'], a[href*='/download/']"):
            anexos.append({
                "nome": normalize_text(a.get_text()) or "Documento",
                "url": urljoin(self.base_url, a['href'])
            })

        return EditalABDI(
            titulo=titulo,
            link=url,
            descricao=descricao.strip() or titulo,
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": "ABDI"
            }
        )
