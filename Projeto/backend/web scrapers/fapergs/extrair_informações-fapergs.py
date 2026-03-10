from __future__ import annotations

import html
import io
import re
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from models_fapergs import EditalFapergs, FapergsAnexo
from utils_fapergs import (
    choose_best_pdf,
    clean_text,
    extract_all_dates,
    extract_numero_edital,
    first_nonempty,
    is_noise_text,
    is_probable_nav_title,
    normalize_text,
    parse_date_br,
)

BASE_URL = "https://fapergs.rs.gov.br"
ABERTOS_URL = "https://fapergs.rs.gov.br/abertos"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0 Safari/537.36"
}

ENTRY_KEYWORDS = [
    "edital", "chamada", "bolsa", "bolsas", "programa", "centelha",
    "trajetorias", "mestrado", "doutorado", "subvencao", "talentos globais",
    "pesquisa", "inovacao", "inovacao", "auxilio", "arc", "ard",
]

IGNORE_PAGE_KEYWORDS = [
    "fale conosco", "conselho superior", "quem somos", "transparencia", "cookies",
]

ARTICLE_SELECTORS = [
    # items returned by server-side pagedlist (common)
    "article.conteudo-lista__item",
    "div.matriz-ui-pagedlist-body article",
    "article.clearfix",
]

TITLE_SELECTORS = [
    "h1", "h2", "h3", "h4",
    ".conteudo-lista__titulo",
    ".conteudo-lista__item-titulo",
    ".titulo",
    "a",
]


class FapergsScraper:
    def __init__(self) -> None:
        self.session = requests.Session()
        retry = Retry(
            total=4,
            backoff_factor=0.8,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "HEAD"),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(HEADERS)

    def get_html(self, url: str) -> str:
        resp = self.session.get(url, timeout=40)
        resp.raise_for_status()
        return resp.text

    def get_soup(self, url: str) -> BeautifulSoup:
        return BeautifulSoup(self.get_html(url), "html.parser")

    def _is_candidate_link(self, title: str, full_url: str) -> bool:
        title_n = normalize_text(title)
        url_n = normalize_text(full_url)
        if not full_url.startswith(BASE_URL):
            return False
        if any(x in url_n for x in ["facebook", "twitter", "youtube", "instagram", "google.com", "sig.fapergs", "whatsapp", "imprimir"]):
            return False
        if is_probable_nav_title(title):
            return False
        return any(k in title_n or k in url_n for k in ENTRY_KEYWORDS)

    def _article_candidates(self, soup: BeautifulSoup) -> list[BeautifulSoup]:
        found: list[BeautifulSoup] = []
        seen = set()
        for selector in ARTICLE_SELECTORS:
            for art in soup.select(selector):
                ident = id(art)
                if ident not in seen:
                    seen.add(ident)
                    found.append(art)
        return found

    def _best_title_from_article(self, article: BeautifulSoup) -> str:
        for selector in TITLE_SELECTORS:
            el = article.select_one(selector)
            if el:
                text = clean_text(el.get_text(" ", strip=True))
                if text and not is_probable_nav_title(text):
                    return text
        return clean_text(article.get_text(" ", strip=True))

    def _best_url_from_article(self, article: BeautifulSoup, base_url: str) -> Optional[str]:
        links = []
        for a in article.select("a[href]"):
            href = (a.get("href") or "").strip()
            if not href:
                continue
            full = urljoin(base_url, href)
            text = clean_text(a.get_text(" ", strip=True))
            if full.startswith(BASE_URL) and not any(bad in normalize_text(full) for bad in ["facebook", "twitter", "whatsapp", "imprimir"]):
                score = 0
                hay = normalize_text(f"{text} {full}")
                if "/upload/arquivos/" in hay or ".pdf" in hay:
                    score -= 10
                if any(k in hay for k in ENTRY_KEYWORDS):
                    score += 4
                if text:
                    score += 1
                links.append((score, full))
        if not links:
            return None
        links.sort(reverse=True)
        return links[0][1]

    def extract_open_entries(self) -> list[tuple[str, str]]:
        html = self.get_html(ABERTOS_URL)
        with open("debug_fapergs_abertos.html", "w", encoding="utf-8") as f:
            f.write(html)
            print(html[:2000])
        soup = BeautifulSoup(html, "html.parser")
        entries: list[tuple[str, str]] = []
        seen_urls = set()

        # if the page uses a matriz pagedlist component, try fetching entries from its service first
        section = soup.select_one("section[data-matriz-source-uri]")
        if section:
            service_uri = section["data-matriz-source-uri"]
            full_service = urljoin(ABERTOS_URL, service_uri)
            page = 1
            pagecount = 1
            while page <= pagecount:
                params = {"currentPage": page, "pageSize": 50}
                try:
                    headers = {
                        "Referer": ABERTOS_URL,
                        "X-Requested-With": "XMLHttpRequest",
                    }

                    resp = self.session.get(
                        full_service,
                        params=params,
                        headers=headers,
                        timeout=40
                    )
                    resp.raise_for_status()

                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type.lower():
                        data = resp.json()
                        body_html = data.get("body", "")
                        pagecount = int(data.get("pagecount", 0) or 0)
                    else:
                        body_html = resp.text
                        pagecount = 1
                except Exception:
                    break
                page += 1

                body_soup = BeautifulSoup(body_html, "html.parser")
                for article in self._article_candidates(body_soup):
                    article_text = clean_text(article.get_text(" ", strip=True))
                    article_norm = normalize_text(article_text)
                    if not article_text:
                        continue
                    if not any(k in article_norm for k in ENTRY_KEYWORDS) and "aberto" not in article_norm:
                        continue

                    title = self._best_title_from_article(article)
                    url = self._best_url_from_article(article, ABERTOS_URL)
                    if url and self._is_candidate_link(title or article_text, url) and url not in seen_urls:
                        seen_urls.add(url)
                        entries.append((title or article_text[:180], url))

        # Caminho principal: cada item da lista é um <article class="conteudo-lista__item clearfix">.
        for article in self._article_candidates(soup):
            article_text = clean_text(article.get_text(" ", strip=True))
            article_norm = normalize_text(article_text)
            if not article_text:
                continue
            if not any(k in article_norm for k in ENTRY_KEYWORDS) and "aberto" not in article_norm:
                continue

            title = self._best_title_from_article(article)
            url = self._best_url_from_article(article, ABERTOS_URL)
            if url and self._is_candidate_link(title or article_text, url) and url not in seen_urls:
                seen_urls.add(url)
                entries.append((title or article_text[:180], url))

        # Fallback: anchors dentro do container principal.
        if not entries:
            container = soup.select_one("div.matriz-ui-pagedlist-body.conteudo-lista__body")
            scope = container if container else soup
            for a in scope.select("a[href]"):
                href = (a.get("href") or "").strip()
                title = clean_text(a.get_text(" ", strip=True))
                full = urljoin(ABERTOS_URL, href)
                if href and self._is_candidate_link(title, full) and full not in seen_urls:
                    seen_urls.add(full)
                    entries.append((title or full.rsplit("/", 1)[-1], full))

        # Fallback: regex por blocos article no HTML bruto.
        if not entries:
            for block in re.findall(r"<article[^>]*conteudo-lista__item[^>]*>(.*?)</article>", html, flags=re.I | re.S):
                block_soup = BeautifulSoup(block, "html.parser")
                title = self._best_title_from_article(block_soup)
                url = self._best_url_from_article(block_soup, ABERTOS_URL)
                text = clean_text(block_soup.get_text(" ", strip=True))
                if url and self._is_candidate_link(title or text, url) and url not in seen_urls:
                    seen_urls.add(url)
                    entries.append((title or text[:180], url))

        return entries

    def parse_entry_page(self, title_hint: str, page_url: str) -> Optional[EditalFapergs]:
        # some pages return the homepage HTML concatenated with the real document,
        # so we fetch raw text and, if multiple <!DOCTYPE> markers are present, keep
        # only the last one before parsing. This avoids noise detection tripping on
        # the site header.
        raw = self.get_html(page_url)
        parts = re.split(r"(?i)<!DOCTYPE", raw)
        if len(parts) > 2:
            # rebuild using the last document
            raw = "<!DOCTYPE" + parts[-1]
        soup = BeautifulSoup(raw, "html.parser")
        for selector in [
                "header",
                "footer",
                "nav",
                "aside",
                ".wrapper__cabecalho__funcionalidades",
                ".cabecalho",
                ".navbar",
                ".redes-sociais",
                ".lgpd",
                ".cookies",
                ".cookie",
                ".barra-governo",
            ]:
                for el in soup.select(selector):
                    el.decompose()

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        page_title = first_nonempty([
            clean_text((soup.find("h1") or {}).get_text(" ", strip=True) if soup.find("h1") else ""),
            clean_text((soup.find("title") or {}).get_text(" ", strip=True) if soup.find("title") else ""),
            title_hint,
        ]) or "Sem título"

        if any(x in normalize_text(page_title) for x in IGNORE_PAGE_KEYWORDS):
            return None

        page_text = soup.get_text("\n", strip=True)
        page_text_clean = clean_text(page_text)

        # Só descarta se realmente não houver sinal de conteúdo útil.
        if is_noise_text(page_text):
            sinais_validos = ["edital", "chamada", "bolsa", "programa", "prazo", "inscri", "pesquisa"]
            if not any(s in normalize_text(page_text_clean) for s in sinais_validos):
                return None

        
        data_publicacao = None

        patterns_pub = [
            r"Publica[cç][aã]o:\s*(\d{2}/\d{2}/\d{4})",
            r"Data\s+de\s+publica[cç][aã]o:\s*(\d{2}/\d{2}/\d{4})",
            r"Publicado\s+em\s*(\d{2}/\d{2}/\d{4})",
        ]

        for pattern in patterns_pub:
            pub_match = re.search(pattern, page_text_clean, flags=re.I)
            if pub_match:
                data_publicacao = parse_date_br(pub_match.group(1))
                if data_publicacao:
                    break

        if not data_publicacao:
            all_dates = extract_all_dates(page_text_clean)
            if all_dates:
                data_publicacao = all_dates[0]

        related_pages: list[tuple[str, str]] = []
        pdf_candidates: list[tuple[str, str]] = []
        anexos: list[FapergsAnexo] = []

        for a in soup.select("a[href]"):
            href = (a.get("href") or "").strip()
            if not href:
                continue
            name = clean_text(a.get_text(" ", strip=True)) or href.rsplit("/", 1)[-1]
            full = urljoin(page_url, href)
            low = normalize_text(f"{name} {full}")
            if any(x in low for x in ["facebook", "twitter", "instagram", "youtube", "google.com", "mailto:", "sig.fapergs", "whatsapp", "imprimir"]):
                continue
            if ".pdf" in low or "upload/arquivos" in low:
                pdf_candidates.append((name, full))
                anexos.append(FapergsAnexo(nome=name, url=full))
            elif full.startswith(BASE_URL) and full != page_url and self._is_candidate_link(name, full):
                related_pages.append((name, full))

        for rel_name, rel_url in related_pages[:3]:
            if pdf_candidates:
                break
            try:
                rel_soup = self.get_soup(rel_url)
                rel_text = clean_text(rel_soup.get_text("\n", strip=True))
                if not data_publicacao:
                    rel_pub = re.search(r"Publica[cç][aã]o:\s*(\d{2}/\d{2}/\d{4})", rel_text, flags=re.I)
                    if rel_pub:
                        data_publicacao = parse_date_br(rel_pub.group(1))
                for a in rel_soup.select("a[href]"):
                    href = (a.get("href") or "").strip()
                    name = clean_text(a.get_text(" ", strip=True)) or href.rsplit("/", 1)[-1]
                    full = urljoin(rel_url, href)
                    low = normalize_text(f"{name} {full}")
                    if ".pdf" in low or "upload/arquivos" in low:
                        pdf_candidates.append((name or rel_name, full))
                        anexos.append(FapergsAnexo(nome=name or rel_name, url=full))
            except Exception:
                pass

        best_pdf = choose_best_pdf(pdf_candidates)
        pdf_url = best_pdf[1] if best_pdf else None

        prazo_envio = None
        objetivo = None
        descricao = self.extract_description(page_text)
        numero_edital = extract_numero_edital(page_title) or extract_numero_edital(page_text_clean)

        if pdf_url:
            try:
                pdf_text = self.extract_pdf_text(pdf_url)
                prazo_envio = self.infer_deadline_from_pdf(pdf_text)
                objetivo = self.extract_objetivo_from_pdf(pdf_text)
                numero_edital = numero_edital or extract_numero_edital(pdf_text)
                if not descricao:
                    descricao = self.extract_description(pdf_text)
            except Exception:
                pass

        has_signal = (
            numero_edital
            or pdf_url
            or any(k in normalize_text(page_title) for k in ["edital", "bolsa", "programa", "chamada"])
        )
        if not has_signal:
            return None

        return EditalFapergs(
            titulo=page_title,
            url_pagina=page_url,
            pdf_url=pdf_url,
            situacao="Aberto",
            data_publicacao=data_publicacao,
            prazo_envio=prazo_envio,
            objetivo=objetivo,
            descricao=descricao,
            numero_edital=numero_edital,
            anexos=self._dedupe_anexos(anexos),
        )

    def _dedupe_anexos(self, anexos: list[FapergsAnexo]) -> list[FapergsAnexo]:
        out: list[FapergsAnexo] = []
        seen = set()
        for anexo in anexos:
            key = anexo.url.strip().lower()
            if key not in seen:
                seen.add(key)
                out.append(anexo)
        return out

    def extract_pdf_text(self, pdf_url: str) -> str:
        resp = self.session.get(pdf_url, timeout=60)
        resp.raise_for_status()
        reader = PdfReader(io.BytesIO(resp.content))
        parts: list[str] = []
        for page in reader.pages[:10]:
            try:
                parts.append(page.extract_text() or "")
            except Exception:
                continue
        return clean_text("\n".join(parts))

    def infer_deadline_from_pdf(self, pdf_text: str):
        text = pdf_text or ""
        patterns = [
            r"per[ií]odo de submiss[aã]o[^.]{0,120}?de\s*\d{1,2}\s+de\s+[a-zç]+\s+a\s*(\d{2}/\d{2}/\d{4})",
            r"encerram-se em\s*(\d{2}/\d{2}/\d{4})",
            r"encerram em\s*(\d{2}/\d{2}/\d{4})",
            r"at[eé]\s*(\d{2}/\d{2}/\d{4})",
            r"submiss[aã]o[^\n]{0,80}?(\d{2}/\d{2}/\d{4})",
            r"inscri[cç][oõ]es[^\n]{0,120}?(\d{2}/\d{2}/\d{4})",
            r"cronograma[^\n]{0,120}?(\d{2}/\d{2}/\d{4})",
        ]
        for pattern in patterns:
            m = re.search(pattern, text, flags=re.I)
            if m:
                dt = parse_date_br(m.group(1))
                if dt:
                    return dt
        dates = extract_all_dates(text)
        if dates:
            futureish = [d for d in dates if d.year >= 2025]
            if futureish:
                return max(futureish)
        return None

    def extract_objetivo_from_pdf(self, pdf_text: str) -> Optional[str]:
        text = pdf_text or ""
        patterns = [
            r"\b(?:1\.?\s*)?OBJETIVO\b[:\s-]*(.{80,900}?)(?:\b2\.?\s*[A-ZÁÉÍÓÚÇ]|P[ÚU]BLICO-ALVO|CRONOGRAMA|RECURSOS)",
            r"objetivo geral[:\s-]*(.{80,900}?)(?:p[úu]blico-alvo|cronograma|recursos)",
        ]
        for pattern in patterns:
            m = re.search(pattern, text, flags=re.I | re.S)
            if m:
                return clean_text(m.group(1))[:900]
        return None

    def extract_description(self, text: str) -> Optional[str]:
        lines = [clean_text(x) for x in (text or "").split("\n") if clean_text(x)]
        filtered = [
            x for x in lines
            if len(x) > 40
            and not is_noise_text(x)
            and "arquivos anexos" not in normalize_text(x)
            and "conteudos relacionados" not in normalize_text(x)
            and "publicacao:" not in normalize_text(x)
        ]
        return filtered[0][:900] if filtered else None

    def collect(self) -> List[EditalFapergs]:
        items: list[EditalFapergs] = []
        seen_pages = set()
        entries = self.extract_open_entries()
        for title, url in entries:
            if url in seen_pages:
                continue
            seen_pages.add(url)
            try:
                item = self.parse_entry_page(title, url)
                if item:
                    items.append(item)
            except Exception:
                continue
        return items
