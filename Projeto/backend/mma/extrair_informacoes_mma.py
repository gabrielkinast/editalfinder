from urllib.parse import urljoin
from typing import List, Optional, Set

from utils_mma import get_soup, normalize_text, extract_date, extract_deadline_iso, is_deadline_valid
from models_mma import EditalMMA

BASE_URL_GOV = "https://www.gov.br"

# Somente índices de editais/chamamentos (sem /noticias).
LISTING_URLS = [
    "https://www.gov.br/mma/pt-br/acesso-a-informacao/editais-e-chamamentos-publicos",
    "https://www.gov.br/mma/pt-br/acesso-a-informacao/participacao-social/3-5-editais-de-chamamento-publico",
    "https://www.gov.br/mma/pt-br/assuntos/editais",
    "https://www.gov.br/mma/pt-br/assuntos/fundo-nacional-do-meio-ambiente",
]

PATH_DENY = (
    "/noticias",
    "sala-de-imprensa",
    "perguntas-frequentes",
    "manual",
    "normativos",
    "governanca",
    "governança",
    "carta-de-servicos",
    "mapa-do-site",
    "ouvidoria",
    "facebook",
    "twitter",
    "linkedin",
    "whatsapp",
)

KEYWORDS_AVOID = ("pregão", "pregao", "licitacao", "licitação", "dispensa", "ata-de-registro")


def _is_mma_url(url: str) -> bool:
    return "gov.br/mma" in url.lower()


def _has_opportunity_signal(url: str, titulo: str) -> bool:
    low = f"{url} {titulo}".lower()
    if "edital" in low or "chamada" in low or "chamamento" in low or "fnma" in low or "fnme" in low:
        return True
    if "consulta" in low and "public" in low:
        return True
    if "selecao" in low or "seleção" in low:
        return True
    if "fomento" in low or "propostas" in low:
        return True
    return False


def _listing_candidate(url: str, titulo: str) -> bool:
    if not _is_mma_url(url):
        return False
    low = f"{url} {titulo}".lower()
    if any(d in low for d in PATH_DENY):
        return False
    if any(k in low for k in KEYWORDS_AVOID):
        return False
    if not _has_opportunity_signal(url, titulo):
        return False
    if url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".js")):
        return False
    return True


class MMAScraper:
    def __init__(self):
        self.base_url_gov = BASE_URL_GOV

    def extract_editais(self) -> List[EditalMMA]:
        all_editais: List[EditalMMA] = []
        seen_links: Set[str] = set()

        for listing_url in LISTING_URLS:
            print(f"Iniciando extração MMA em: {listing_url}")
            soup = get_soup(listing_url)
            if not soup:
                continue
            main_content = soup.select_one("#content-core") or soup.select_one("article") or soup
            for a in main_content.select("a[href]"):
                href = a.get("href")
                titulo = normalize_text(a.get_text())
                if not href:
                    continue
                if not href.startswith("http"):
                    href = urljoin(self.base_url_gov, href)
                full_url = href.split("#", 1)[0].split("?", 1)[0]
                if full_url in seen_links:
                    continue
                if not _listing_candidate(full_url, titulo):
                    continue
                seen_links.add(full_url)
                print(f"Verificando potencial edital MMA: {titulo[:50]}...")
                edital = self.process_detail_page(full_url, titulo, listing_url=listing_url)
                if edital:
                    if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
                        continue
                    all_editais.append(edital)

        return all_editais

    def process_detail_page(self, url: str, titulo: str, listing_url: str) -> Optional[EditalMMA]:
        if not _is_mma_url(url):
            return None

        if url.lower().endswith(".pdf"):
            return EditalMMA(
                titulo=titulo if len(titulo) > 10 else f"Documento: {url.split('/')[-1]}",
                link=url,
                descricao=titulo,
                situacao="Aberto",
                extras={
                    "anexos": [{"nome": "Edital PDF", "url": url}],
                    "fonte_original": "MMA gov.br",
                    "url_listagem": listing_url,
                    "metodo_extracao": "curated_listing_pdf",
                },
            )

        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("#content-core") or soup.select_one("article") or soup
        text = content.get_text()

        keywords = ("edital", "chamada", "chamamento", "fomento", "seleção", "selecao", "pública", "publica", "propostas", "consulta")
        if not any(kw in (titulo + text).lower() for kw in keywords):
            return None

        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            titulo = normalize_text(h1.get_text()) or titulo

        paragraphs = content.select("p")
        descricao = ""
        for p in paragraphs[:6]:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 30:
                descricao += p_text + " "

        data_pub = extract_date(text)
        prazo = extract_deadline_iso(text)

        anexos = []
        for a in content.select("a[href]"):
            a_href = a.get("href")
            a_text = normalize_text(a.get_text())
            if not a_href:
                continue
            if a_href.lower().endswith(".pdf") or "download" in a_href.lower():
                if not a_href.startswith("http"):
                    a_href = urljoin(self.base_url_gov, a_href)
                anexos.append({"nome": a_text or "Link/Documento", "url": a_href})

        return EditalMMA(
            titulo=titulo[:250],
            link=url,
            descricao=(descricao.strip() or titulo)[:4000],
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": "MMA gov.br",
                "url_listagem": listing_url,
                "url_detalhe": url,
                "metodo_extracao": "curated_listing_detail",
            },
        )
