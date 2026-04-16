from __future__ import annotations

import re
from dataclasses import replace
from datetime import date
from typing import Iterable, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from models import EditalFinep
from utils import (
    choose_best_pdf,
    clean_multiline_text,
    is_noise_text,
    normalize_ascii,
    normalize_text,
    parse_br_date,
)

BASE_URL = "https://www.finep.gov.br"
LIST_URL = f"{BASE_URL}/chamadas-publicas/chamadaspublicas?situacao=aberta"
DEFAULT_TIMEOUT = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Referer": BASE_URL,
}


class FinepScraper:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=4,
            backoff_factor=1,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "HEAD"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update(HEADERS)
        return session

    def get_html(self, url: str) -> str:
        response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
        response.raise_for_status()
        if response.encoding is None:
            response.encoding = response.apparent_encoding or "utf-8"
        return response.text

    def get_soup(self, url: str) -> BeautifulSoup:
        return self.html_to_soup(self.get_html(url))

    @staticmethod
    def html_to_soup(html: str) -> BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup

    def extrair_links_chamadas_abertas(self) -> list[str]:
        html = self.get_html(LIST_URL)
        soup = self.html_to_soup(html)

        links: list[str] = []
        seen: set[str] = set()

        for a in soup.select("a[href]"):
            href = normalize_text(a.get("href"))
            if not href:
                continue
            if "/chamadas-publicas/chamadapublica/" not in href:
                continue
            full_url = urljoin(BASE_URL, href)
            full_url = full_url.split("#", 1)[0]
            if full_url not in seen:
                seen.add(full_url)
                links.append(full_url)

        if links:
            return links

        # fallback bruto por regex no HTML
        for match in re.finditer(r'(/chamadas-publicas/chamadapublica/\d+)', html, flags=re.I):
            full_url = urljoin(BASE_URL, match.group(1))
            if full_url not in seen:
                seen.add(full_url)
                links.append(full_url)

        return links

    def extrair_detalhes_chamada(self, url: str) -> EditalFinep:
        html = self.get_html(url)
        soup = self.html_to_soup(html)
        text = clean_multiline_text(soup.get_text("\n", strip=True))

        titulo = self._extract_title(soup, text)
        campos = self._extract_fields(text)
        descricao = self._extract_description(soup, text)
        pdf_url = self._extract_pdf_url(soup, url, html)
        fonte = self._detect_source(text, titulo)

        edital = EditalFinep(
            titulo=titulo,
            url=url,
            fonte=fonte,
            situacao=campos.get("situacao"),
            data_publicacao=parse_br_date(campos.get("data_publicacao")),
            prazo_envio=parse_br_date(campos.get("prazo_envio")),
            fonte_recurso=campos.get("fonte_recurso"),
            publico_alvo=campos.get("publico_alvo"),
            temas=campos.get("temas"),
            objetivo=campos.get("objetivo"),
            descricao=descricao,
            pdf_url=pdf_url,
        )

        return self._normalize_edital(edital)

    def _detect_source(self, text: str, title: str) -> str:
        full_text = f"{title} {text}".lower()
        
        if "fndct" in full_text:
            return "FNDCT"
        if "funttel" in full_text:
            return "FUNTTEL"
        if "bndes" in full_text or "funtec" in full_text:
            return "BNDES Funtec"
            
        return "Finep"

    def _extract_title(self, soup: BeautifulSoup, text: str) -> str:
        for selector in ("h1", "h2", ".page-header h2", ".item-page h2", ".contentheading"):
            tag = soup.select_one(selector)
            if tag:
                title = normalize_text(tag.get_text(" ", strip=True))
                if title and normalize_ascii(title) != "chamadas publicas":
                    return title

        for line in text.split("\n"):
            if not line:
                continue
            nline = normalize_ascii(line)
            if nline == "chamadas publicas":
                continue
            if len(line) > 8:
                return line
        return "Sem título"

    def _extract_fields(self, text: str) -> dict[str, str]:
        patterns = {
            "data_publicacao": [
                r"Data de Publica[cç][aã]o\s*:\s*(\d{2}/\d{2}/\d{4})",
                r"Data de publica[cç][aã]o\s*:\s*(\d{2}/\d{2}/\d{4})",
            ],
            "prazo_envio": [
                r"Prazo para envio(?: eletr[oô]nico)? de propostas(?: at[eé])?\s*:\s*(\d{2}/\d{2}/\d{4})",
                r"Prazo para envio de propostas at[eé]\s*:\s*(\d{2}/\d{2}/\d{4})",
                r"Prazo para envio eletr[oô]nico da proposta\s*:\s*(\d{2}/\d{2}/\d{4})",
            ],
            "fonte_recurso": [
                r"Fonte de Recurso\s*:\s*(.+?)(?=\n[A-ZÁÉÍÓÚÂÊÔÃÕÇa-záéíóúâêôãõç][^\n]{0,40}:|\Z)",
            ],
            "publico_alvo": [
                r"P[uú]blico-alvo\s*:\s*(.+?)(?=\n[A-ZÁÉÍÓÚÂÊÔÃÕÇa-záéíóúâêôãõç][^\n]{0,40}:|\Z)",
                r"Publico-alvo\s*:\s*(.+?)(?=\n[A-ZÁÉÍÓÚÂÊÔÃÕÇa-záéíóúâêôãõç][^\n]{0,40}:|\Z)",
            ],
            "temas": [
                r"Tema(?:\(s\))?\s*:\s*(.+?)(?=\n[A-ZÁÉÍÓÚÂÊÔÃÕÇa-záéíóúâêôãõç][^\n]{0,40}:|\Z)",
                r"Temas\s*:\s*(.+?)(?=\n[A-ZÁÉÍÓÚÂÊÔÃÕÇa-záéíóúâêôãõç][^\n]{0,40}:|\Z)",
            ],
            "situacao": [
                r"Situa[cç][aã]o\s*:\s*(.+?)(?=\n[A-ZÁÉÍÓÚÂÊÔÃÕÇa-záéíóúâêôãõç][^\n]{0,40}:|\Z)",
            ],
            "objetivo": [
                r"Objetivo(?: Geral)?\s*:\s*(.+?)(?=\n[A-ZÁÉÍÓÚÂÊÔÃÕÇa-záéíóúâêôãõç][^\n]{0,40}:|\Z)",
            ],
        }

        values: dict[str, str] = {}
        for field, regex_list in patterns.items():
            for pattern in regex_list:
                match = re.search(pattern, text, flags=re.I | re.S)
                if match:
                    values[field] = normalize_text(match.group(1))
                    break
        return values

    def _extract_description(self, soup: BeautifulSoup, text: str) -> str | None:
        blocks: list[str] = []

        for selector in (".item-page", "article", ".com-content-article__body", ".page-body", ".entry-content"):
            node = soup.select_one(selector)
            if node:
                candidate = clean_multiline_text(node.get_text("\n", strip=True))
                if candidate and not is_noise_text(candidate):
                    blocks.append(candidate)

        if not blocks:
            paragraphs = []
            for p in soup.select("p, li"):
                candidate = normalize_text(p.get_text(" ", strip=True))
                if not candidate or len(candidate) < 40 or is_noise_text(candidate):
                    continue
                paragraphs.append(candidate)
            if paragraphs:
                blocks.append("\n".join(paragraphs[:12]))

        if not blocks and text and not is_noise_text(text):
            blocks.append(text)

        if not blocks:
            return None

        best = max(blocks, key=len)
        lines = []
        for line in best.split("\n"):
            nline = normalize_ascii(line)
            if nline in {"chamadas publicas", "documentos"}:
                continue
            if is_noise_text(line):
                continue
            lines.append(line)

        cleaned = "\n".join(lines).strip()
        return cleaned or None

    def _extract_pdf_url(self, soup: BeautifulSoup, page_url: str, html: str) -> str | None:
        candidates: list[str] = []

        for a in soup.select("a[href]"):
            href = normalize_text(a.get("href"))
            label = normalize_text(a.get_text(" ", strip=True))
            if not href:
                continue
            lowered = normalize_ascii(f"{href} {label}")
            if ".pdf" in lowered or any(keyword in lowered for keyword in ("edital", "anexo", "faq", "regulamento", "formulario", "resultado")):
                candidates.append(urljoin(page_url, href))

        if not candidates:
            for match in re.finditer(r'https?://[^\s"\']+\.pdf', html, flags=re.I):
                candidates.append(match.group(0))

        if not candidates:
            return None
        return choose_best_pdf(candidates)

    def _normalize_edital(self, edital: EditalFinep) -> EditalFinep:
        titulo = edital.titulo
        if normalize_ascii(titulo) == "chamadas publicas" and edital.descricao:
            for line in edital.descricao.split("\n"):
                if len(line) > 10 and normalize_ascii(line) != "chamadas publicas":
                    titulo = line[:220]
                    break

        situacao = normalize_text(edital.situacao)
        if situacao:
            if normalize_ascii(situacao).startswith("aberta"):
                situacao = "Aberta"
            elif normalize_ascii(situacao).startswith("encerrada"):
                situacao = "Encerrada"

        # fallback forte a partir da listagem/texto se a página detalhada vier ruim
        descricao = edital.descricao or ""
        if edital.data_publicacao is None and descricao:
            edital = replace(edital, data_publicacao=parse_br_date(descricao))

        return replace(edital, titulo=titulo, situacao=situacao or None)


def extrair_links_chamadas_abertas() -> list[str]:
    return FinepScraper().extrair_links_chamadas_abertas()


def extrair_detalhes_chamada(url: str) -> EditalFinep:
    return FinepScraper().extrair_detalhes_chamada(url)
