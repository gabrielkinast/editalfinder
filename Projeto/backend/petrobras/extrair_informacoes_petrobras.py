from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional, Set

from utils_petrobras import (
    get_soup,
    normalize_text,
    extract_date,
    extract_deadline_iso,
    normalize_petrobras_url,
)
from models_petrobras import EditalPetrobras

# Somente páginas de seleções públicas e inovação (sem agência de notícias genérica).
LISTING_URLS = [
    "https://petrobras.com.br/sustentabilidade/selecoes-publicas",
    "https://petrobras.com.br/cultural/selecoes-publicas-culturais",
    "https://tecnologia.petrobras.com.br/modulo-startups.html",
]

DENY_PATH = (
    "socioambiental",
    "noticias",
    "news",
    "concursos",
    "carreiras",
    "privacidade",
    "cookies",
    "gestaodepatrocinios",
)
DENY_TITLE = ("resultado", "retificação", "retificacao", "cookie", "copyright", "ops", "link do botão", "link do botao")


def _allowed_domain(url: str) -> bool:
    u = url.lower()
    if "petrobras.com.br" in u:
        return True
    if "bussolasocial.com.br/petrobras/editais" in u:
        return True
    return False


def _listing_candidate(url: str, titulo: str) -> bool:
    if not _allowed_domain(url):
        return False
    low = f"{url} {titulo}".lower()
    if any(d in low for d in DENY_PATH):
        return False
    if any(d in titulo.lower() for d in DENY_TITLE):
        return False
    pos = ("edital", "chamada", "seleção", "selecao", "seleções", "selecoes", "inscriç", "inscri", "regulamento", "oportunidade", "startup", "cultural")
    if not any(p in low for p in pos):
        return False
    if url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".js", ".mp4")):
        return False
    avoid = ("licitação", "licitacao", "pregão", "pregao", "venda de ativos")
    if any(a in low for a in avoid):
        return False
    return True


class PetrobrasScraper:
    def extract_editais(self) -> List[EditalPetrobras]:
        all_editais: List[EditalPetrobras] = []
        seen_links: Set[str] = set()

        for listing_url in LISTING_URLS:
            print(f"Iniciando extração Petrobras em: {listing_url}")
            soup = get_soup(listing_url)
            if not soup:
                continue
            self._extract_from_page(soup, listing_url, all_editais, seen_links)

        return all_editais

    def _extract_from_page(self, soup, listing_url: str, editais_list: List[EditalPetrobras], seen_links: Set[str]) -> None:
        main_content = soup.select_one("main") or soup.select_one("#content") or soup.select_one("article") or soup
        for a in main_content.select("a[href]"):
            href = a.get("href")
            titulo = normalize_text(a.get_text())
            if not href:
                continue
            if not href.startswith("http"):
                href = urljoin(listing_url, href)
            full_url = normalize_petrobras_url(href.split("#", 1)[0].split("?", 1)[0])
            if not full_url or full_url in seen_links:
                continue
            if not _listing_candidate(full_url, titulo):
                continue

            if full_url.lower().endswith(".pdf"):
                seen_links.add(full_url)
                editais_list.append(
                    EditalPetrobras(
                        titulo=titulo or "Edital Petrobras (PDF)",
                        link=normalize_petrobras_url(full_url),
                        descricao=titulo,
                        extras={
                            "fonte_original": listing_url,
                            "tipo": "PDF",
                            "url_listagem": listing_url,
                            "metodo_extracao": "curated_listing_pdf",
                        },
                    )
                )
                continue

            seen_links.add(full_url)
            edital = self.process_detail_page(full_url, titulo, listing_url=listing_url)
            if edital:
                editais_list.append(edital)

    def process_detail_page(self, url: str, titulo: str, listing_url: str) -> Optional[EditalPetrobras]:
        url = normalize_petrobras_url(url)
        if url.rstrip("/") == listing_url.rstrip("/"):
            return None
        if not _allowed_domain(url):
            return None

        print(f"Processando página detalhe Petrobras: {url}")
        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("main") or soup.select_one("#content") or soup.select_one("article") or soup
        text = content.get_text()

        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            h1_text = normalize_text(h1.get_text())
            if len(h1_text) > 5:
                titulo = h1_text

        if any(kw in titulo.lower() for kw in ("ops...", "erro", "not found", "404")):
            return None

        combined = f"{titulo} {text}".lower()
        if "resultado" in combined and "inscriç" not in combined and "edital" not in combined:
            return None

        paragraphs = content.select("p")
        descricao = ""
        count = 0
        for p in paragraphs:
            p_text = normalize_text(p.get_text())
            if len(p_text) > 50:
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
            if a_href and any(ext in a_href.lower() for ext in (".pdf", ".doc", ".zip", ".rar")):
                if not a_href.startswith("http"):
                    a_href = urljoin(url, a_href)
                anexos.append({"nome": a_text or "Documento", "url": a_href})

        return EditalPetrobras(
            titulo=titulo[:250],
            link=normalize_petrobras_url(url),
            descricao=(descricao.strip() or titulo)[:4000],
            data_publicacao=data_pub,
            fim_inscricao=prazo,
            situacao="Aberto",
            extras={
                "anexos": anexos,
                "fonte_original": listing_url,
                "data_extracao": datetime.now().strftime("%Y-%m-%d"),
                "url_listagem": listing_url,
                "url_detalhe": url,
                "metodo_extracao": "curated_listing_detail",
            },
        )
