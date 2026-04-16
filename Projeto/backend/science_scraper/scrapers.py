import re
from urllib.parse import urljoin

try:
    from utils import get_soup, normalize_text
    from models import EditalScience
except ImportError:
    from .utils import get_soup, normalize_text
    from .models import EditalScience

class ScienceScrapers:
    def __init__(self):
        self.results = []

    def scrape_ec_europa(self, url, source_name):
        """Scraper para links da Comissão Europeia."""
        print(f"Scraping EC: {url}")
        soup = get_soup(url)
        if not soup: return
        
        # Procura por cards de editais ou links de documentos
        items = soup.select(".views-row") or soup.select(".ecl-card") or soup.select(".ecl-link")
        for item in items:
            link_tag = item if item.name == 'a' else item.find("a")
            if not link_tag or not link_tag.get("href"): continue
            
            href = urljoin(url, link_tag["href"])
            titulo = normalize_text(link_tag.get_text())
            
            if len(titulo) > 15:
                self.results.append(EditalScience(
                    titulo=titulo,
                    link=href,
                    fonte=source_name,
                    descricao=titulo
                ))

    def scrape_osti_gov(self, url, source_name):
        """Scraper para science.osti.gov."""
        print(f"Scraping OSTI: {url}")
        soup = get_soup(url)
        if not soup: return
        
        # OSTI costuma usar tabelas para FOAs
        rows = soup.select("table tr")
        for row in rows[1:]: # Pula header
            cols = row.find_all("td")
            if len(cols) >= 2:
                link_tag = cols[1].find("a")
                if link_tag:
                    titulo = normalize_text(cols[0].get_text() + " - " + link_tag.get_text())
                    href = urljoin(url, link_tag["href"])
                    self.results.append(EditalScience(
                        titulo=titulo,
                        link=href,
                        fonte=source_name
                    ))

    def scrape_grants_gov(self):
        """Scraper para Grants.gov (Oportunidades Abertas)."""
        url = "https://www.grants.gov/web/grants/search-grants.html"
        # Grants.gov usa AJAX e busca dinâmica, mas podemos tentar pegar os links base
        # ou usar a API pública deles (mais estável)
        print(f"Scraping Grants.gov (via API): {url}")
        
        api_url = "https://www.grants.gov/grantsws/rest/opportunities/search"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
        payload = {
            "startRecord": 0,
            "keyword": "science",
            "oppStatuses": "forecasted|posted"
        }
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                opps = data.get("oppts", [])
                for opp in opps:
                    titulo = opp.get("title", "")
                    opp_id = opp.get("id", "")
                    link = f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={opp_id}"
                    
                    self.results.append(EditalScience(
                        titulo=f"Grants.gov: {titulo}",
                        link=link,
                        fonte="GRANTS.GOV",
                        descricao=opp.get("agency", ""),
                        fim_inscricao=opp.get("closeDate")
                    ))
        except Exception as e:
            print(f"Erro ao acessar API do Grants.gov: {e}")

    def scrape_faperj(self):
        """Scraper para FAPERJ."""
        url = "https://www.faperj.br/editais/"
        print(f"Scraping FAPERJ: {url}")
        soup = get_soup(url)
        if not soup: return
        
        # FAPERJ usa cards ou listas de editais
        items = soup.select(".card-body") or soup.select("article") or soup.select("a")
        for item in items:
            link_tag = item if item.name == 'a' else item.find("a")
            if not link_tag: continue
            
            href = link_tag.get("href")
            if not href: continue
            
            titulo = normalize_text(link_tag.get_text())
            if "edital" in titulo.lower() or "chamada" in titulo.lower() or "fomento" in titulo.lower():
                self.results.append(EditalScience(
                    titulo=titulo,
                    link=urljoin(url, href),
                    fonte="FAPERJ"
                ))

    def scrape_aeb(self):
        """Scraper para AEB."""
        url = "https://www.gov.br/aeb/pt-br/assuntos/editais-e-chamadas-publicas-1"
        print(f"Scraping AEB: {url}")
        soup = get_soup(url)
        if not soup: return
        
        items = soup.select(".tileItem") or soup.select("article") or soup.select("a")
        for item in items:
            link_tag = item if item.name == 'a' else item.find("a")
            if not link_tag: continue
            
            href = link_tag.get("href")
            titulo = normalize_text(link_tag.get_text())
            
            if "edital" in titulo.lower() or "chamada" in titulo.lower():
                self.results.append(EditalScience(
                    titulo=titulo,
                    link=urljoin(url, href),
                    fonte="AEB"
                ))

    def scrape_aneel(self):
        """Scraper para ANEEL P&D."""
        url = "https://www.gov.br/aneel/pt-br/assuntos/pesquisa-e-desenvolvimento-e-eficiencia-energetica"
        print(f"Scraping ANEEL: {url}")
        soup = get_soup(url)
        if not soup: return
        
        links = soup.select("a")
        for a in links:
            titulo = normalize_text(a.get_text())
            href = a.get("href")
            if href and ("chamada" in titulo.lower() or "p&d" in titulo.lower() or "edital" in titulo.lower()):
                self.results.append(EditalScience(
                    titulo=titulo,
                    link=urljoin(url, href),
                    fonte="ANEEL"
                ))
