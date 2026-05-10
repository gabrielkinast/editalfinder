from datetime import datetime
from urllib.parse import urljoin
from typing import List, Optional, Set

from utils_ambev import get_soup, normalize_text, extract_date, extract_deadline_iso
from models_ambev import EditalAmbev

CHALLENGES_INDEX = "https://www.100accelerator.com/challenges"
STARTUPS_HUB = "https://www.ambev.com.br/startups"

SOCIAL = ("facebook.com", "instagram.com", "linkedin.com", "twitter.com", "youtube.com", "whatsapp.com", "google.com")


def _is_challenge_detail(url: str) -> bool:
    u = url.lower().rstrip("/")
    if "100accelerator.com/challenges" not in u:
        return False
    # /challenges ou /challenges/ apenas — não é detalhe
    parts = [p for p in u.split("/") if p]
    if not parts:
        return False
    try:
        idx = parts.index("challenges")
    except ValueError:
        return False
    return len(parts) > idx + 1


def _allowed_ambev_detail(url: str) -> bool:
    u = url.lower()
    if "ambev.com.br" in u:
        return True
    if _is_challenge_detail(url):
        return True
    return False


def _junk_heading(text: str) -> bool:
    t = normalize_text(text).lower()
    if not t or len(t) < 3:
        return True
    if t in ("subchallenges", "subchallenge", "challenges", "learn more"):
        return True
    if "subchallenge" in t:
        return True
    if t.startswith("learn more"):
        return True
    return False


def _title_from_challenge_slug(url: str) -> str:
    slug = url.rstrip("/").split("/")[-1]
    if not slug or slug.lower() == "challenges":
        return ""
    return slug.replace("-", " ").strip().title()


def _reject_url(url: str, titulo: str) -> bool:
    low = url.lower()
    if any(s in low for s in SOCIAL):
        return True
    if low.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".js", ".ico", ".mp4")):
        return True
    if "subchallenge" in low or "sub-challenge" in low:
        return True
    t = titulo.lower()
    if "subchallenge" in t or "challengeschallenges" in t or t.strip() in ("subchallenges", "subchallenge"):
        return True
    return False


class AmbevScraper:
    def extract_editais(self) -> List[EditalAmbev]:
        out: List[EditalAmbev] = []
        seen: Set[str] = set()

        for listing_url, mode in (
            (CHALLENGES_INDEX, "accelerator"),
            (STARTUPS_HUB, "ambev"),
        ):
            print(f"Iniciando extração AMBEV em: {listing_url}")
            soup = get_soup(listing_url)
            if not soup:
                continue
            if mode == "accelerator":
                self._seed_accelerator_challenges(soup, listing_url, out, seen)
            else:
                self._seed_ambev_startups(soup, listing_url, out, seen)

        return out

    def _seed_accelerator_challenges(self, soup, listing_url: str, out: List[EditalAmbev], seen: Set[str]) -> None:
        main = soup.select_one("main") or soup.select_one("article") or soup
        for a in main.select("a[href]"):
            href = a.get("href")
            titulo = normalize_text(a.get_text())
            if not href or href.startswith(("javascript:", "#")):
                continue
            if not href.startswith("http"):
                href = urljoin(listing_url, href)
            full = href.split("?", 1)[0].split("#", 1)[0]
            if full in seen or _reject_url(full, titulo):
                continue
            if not _is_challenge_detail(full):
                continue
            seen.add(full)
            if not titulo or _junk_heading(titulo):
                titulo = _title_from_challenge_slug(full) or "Challenge 100+"
            edital = self.process_detail_page(full, titulo, listing_url=listing_url)
            if edital:
                out.append(edital)

    def _seed_ambev_startups(self, soup, listing_url: str, out: List[EditalAmbev], seen: Set[str]) -> None:
        main = soup.select_one("main") or soup.select_one("#content") or soup.select_one("article") or soup
        hints = ("startup", "programa", "edital", "chamada", "inova", "inscri", "accelerat", "desafio", "oportunidade")
        for a in main.select("a[href]"):
            href = a.get("href")
            titulo = normalize_text(a.get_text())
            if not href or href.startswith(("javascript:", "#")):
                continue
            if not href.startswith("http"):
                href = urljoin(listing_url, href)
            full = href.split("?", 1)[0].split("#", 1)[0]
            if full in seen or _reject_url(full, titulo):
                continue
            low = f"{full} {titulo}".lower()
            if "ambev.com.br" not in full.lower() and "100accelerator.com" not in full.lower():
                continue
            if not any(h in low for h in hints):
                continue
            seen.add(full)
            if full.lower().endswith(".pdf"):
                out.append(
                    EditalAmbev(
                        titulo=titulo or "Documento",
                        link=full,
                        descricao=titulo,
                        extras={
                            "fonte_original": listing_url,
                            "tipo": "PDF",
                            "url_listagem": listing_url,
                            "metodo_extracao": "curated_startups_pdf",
                        },
                    )
                )
                continue
            edital = self.process_detail_page(full, titulo, listing_url=listing_url)
            if edital:
                out.append(edital)

    def process_detail_page(self, url: str, titulo: str, listing_url: str) -> Optional[EditalAmbev]:
        if url.rstrip("/") == listing_url.rstrip("/"):
            return None
        if not _allowed_ambev_detail(url):
            return None

        print(f"Processando página detalhe AMBEV: {url}")
        soup = get_soup(url)
        if not soup:
            return None

        content = soup.select_one("main") or soup.select_one("#content") or soup.select_one("article") or soup
        text = content.get_text()

        h1 = soup.select_one("h1") or soup.select_one("h2")
        if h1:
            h1_text = normalize_text(h1.get_text())
            if len(h1_text) > 5 and not _junk_heading(h1_text):
                titulo = h1_text

        if _junk_heading(titulo):
            slug_title = _title_from_challenge_slug(url)
            if slug_title:
                titulo = slug_title
            elif _is_challenge_detail(url):
                titulo = "Challenge 100+"

        if any(kw in titulo.lower() for kw in ("ops...", "erro", "not found", "404")):
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

        return EditalAmbev(
            titulo=titulo[:250],
            link=url,
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
