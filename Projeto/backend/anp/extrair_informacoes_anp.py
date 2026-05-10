from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional, Set, Tuple

from utils_anp import get_soup, normalize_text, extract_date, extract_deadline_iso
from models_anp import EditalANP

BASE_URL_GOV = "https://www.gov.br"

# Apenas páginas-índice de PRH, editais e participação social (sem notícias genéricas / FAPESP).
LISTING_URLS: List[str] = [
    "https://www.gov.br/anp/pt-br/assuntos/tecnologia-meio-ambiente/prh-anp-programa-de-formacao-de-recursos-humanos-1",
    "https://www.gov.br/anp/pt-br/assuntos/tecnologia-meio-ambiente/prh-anp-programa-de-formacao-de-recursos-humanos/eixo-academico/edital-de-chamada-publica",
    "https://www.gov.br/anp/pt-br/acesso-a-informacao/participacao-social",
]

PATH_DENY = (
    "noticias",
    "imprensa",
    "galeria",
    "estagio",
    "estágio",
    "forum-de-tecnologia",
    "acoes-e-programas",
    "metas-institucionais",
    "plano-de-comunicacao",
    "plano-de-gestao",
    "plano-diretor",
    "politica-de-diversidade",
    "governanca",
    "reclamacoes",
    "denuncias",
    "dados-abertos",
    "canais_atendimento/imprensa",
    "manual-do",
    "programas-ativos",
    "iniciativas-parcerias",
    "dados-prestacao",
    "encontro-nacional",
    "padroes-perguntas",
    "perguntas-frequentes",
    "arquivos-",
    "rodadas-anp",
    "oferta-permanente",
    "resolucao",
)

# Não usar só "prh" (pega manual, FAQ etc.). Exige sinal de chamada/edital/consulta.
PATH_ALLOW_SUBSTR = (
    "edital",
    "chamada",
    "chamamento",
    "consulta-publica",
    "consulta_publica",
    "consulta-audiencia",
    "audiencia-publica",
    "selecao",
    "seleção",
)


def _is_anp_gov_url(url: str) -> bool:
    u = url.lower()
    return "gov.br/anp" in u


def _listing_candidate(url: str, titulo: str) -> bool:
    if not _is_anp_gov_url(url):
        return False
    low = f"{url} {titulo}".lower()
    if any(d in low for d in PATH_DENY):
        return False
    if not any(a in low for a in PATH_ALLOW_SUBSTR):
        return False
    if url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".zip", ".mp4", ".doc", ".docx", ".xls", ".xlsx")):
        return False
    avoid_t = ("licitação", "licitacao", "pregão", "pregao", "contratação", "contratacao", "mapa do site")
    if any(k in titulo.lower() for k in avoid_t):
        return False
    return True


class ANPScraper:
    def __init__(self):
        self.base_url_gov = BASE_URL_GOV

    def extract_editais(self) -> List[EditalANP]:
        all_editais: List[EditalANP] = []
        seen_links: Set[str] = set()

        for listing_url in LISTING_URLS:
            print(f"Iniciando extração ANP em: {listing_url}")
            soup = get_soup(listing_url)
            if not soup:
                continue
            self._collect_from_listing(soup, listing_url, all_editais, seen_links)

        return all_editais

    def _collect_from_listing(
        self, soup, listing_url: str, editais_list: List[EditalANP], seen_links: Set[str]
    ) -> None:
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
            edital = self.process_detail_page(full_url, titulo, listing_url=listing_url)
            if edital:
                editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str, listing_url: str) -> Optional[EditalANP]:
        if not _is_anp_gov_url(url):
            return None

        if url.lower().endswith(".pdf"):
            return EditalANP(
                titulo=titulo or "Edital ANP (PDF)",
                link=url,
                descricao=titulo,
                situacao="Aberto",
                extras={
                    "anexos": [{"nome": "Edital PDF", "url": url}],
                    "fonte_original": "ANP gov.br",
                    "url_listagem": listing_url,
                    "metodo_extracao": "curated_listing_pdf",
                },
            )

        soup = get_soup(url)
        if not soup:
            return None

        print(f"Processando página detalhe ANP: {url}")

        content = soup.select_one("#content") or soup.select_one("#content-core") or soup.select_one("article") or soup
        text = content.get_text()

        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            h1_text = normalize_text(h1.get_text())
            if h1_text and len(h1_text) > 3:
                titulo = h1_text

        if not titulo or len(titulo) < 4 or any(kw in titulo.lower() for kw in ("ops...", "erro", "not found", "404")):
            return None

        combined = f"{titulo} {text}".lower()
        if any(k in combined for k in ("resultado final", "resultado preliminar", "homologação", "homologacao")):
            if "edital" not in combined and "chamada" not in combined:
                return None

        paragraphs = content.select("p")
        descricao = ""
        count = 0
        for p in paragraphs:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 40:
                descricao += p_text + " "
                count += 1
            if count >= 5:
                break

        data_pub = extract_date(text)
        prazo = extract_deadline_iso(text)

        anexos = []
        for a in content.select("a[href]"):
            a_href = a.get("href")
            a_text = normalize_text(a.get_text())
            if any(ext in (a_href or "").lower() for ext in (".pdf", ".doc", ".docx", ".zip")):
                if not a_href.startswith("http"):
                    a_href = urljoin(self.base_url_gov, a_href)
                anexos.append({"nome": a_text or "Documento", "url": a_href})

        return EditalANP(
            titulo=titulo[:250],
            link=url,
            descricao=(descricao.strip() or titulo)[:4000],
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": "ANP gov.br",
                "data_extracao": datetime.now().strftime("%Y-%m-%d"),
                "url_listagem": listing_url,
                "url_detalhe": url,
                "metodo_extracao": "curated_listing_detail",
            },
        )
