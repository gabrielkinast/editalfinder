from __future__ import annotations

import re
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import importlib.util
import sys
from pathlib import Path


def _carregar_modulo(nome: str, arquivo: str):
    caminho = Path(__file__).with_name(arquivo)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar {arquivo}")
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


_models = _carregar_modulo("models_cnpq", "models-cnpq.py")
_utils = _carregar_modulo("utils_cnpq", "utils-cnpq.py")

EditalCNPq = _models.EditalCNPq
AnexoCNPq = _models.AnexoCNPq


normalizar_espacos = _utils.normalizar_espacos
extrair_datas_publicacao = _utils.extrair_datas_publicacao
extrair_periodo_inscricoes = _utils.extrair_periodo_inscricoes
escolher_descricao = _utils.escolher_descricao
eh_link_de_chamada = _utils.eh_link_de_chamada
eh_anexo_pdf_relevante = _utils.eh_anexo_pdf_relevante


BASE_URL = "https://www.gov.br"
LIST_URL = "https://www.gov.br/cnpq/pt-br/chamadas/abertas-para-submissao"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0 Safari/537.36"
    )
}


class CNPQScraper:
    def __init__(self) -> None:
        self.session = requests.Session()
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=1.0,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(HEADERS)

    def get_soup(self, url: str) -> BeautifulSoup:
        resp = self.session.get(url, timeout=40)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup

    def extrair_editais(self, url_inicial: str = LIST_URL, limite_paginas: int = 20) -> List[EditalCNPq]:
        url = url_inicial
        visitadas: set[str] = set()
        editais: list[EditalCNPq] = []

        for _ in range(limite_paginas):
            if not url or url in visitadas:
                break
            visitadas.add(url)

            soup = self.get_soup(url)
            novos = self._extrair_da_pagina(soup, url)
            editais.extend(novos)
            url = self._proxima_pagina(soup, url)

        return self._deduplicar(editais)

    def _extrair_da_pagina(self, soup: BeautifulSoup, page_url: str) -> List[EditalCNPq]:
        resultados: list[EditalCNPq] = []

        titulos = soup.find_all(re.compile(r"^h[1-6]$"))
        for titulo_tag in titulos:
            if titulo_tag.name not in {"h2", "h3"}:
                continue

            titulo = normalizar_espacos(titulo_tag.get_text(" ", strip=True))
            if not titulo:
                continue
            if "chamada" not in titulo.lower() and "cnpq" not in titulo.lower():
                continue
            if "abertas para submissão" in titulo.lower() or "abertas para submissao" in titulo.lower():
                continue

            edital = self._extrair_bloco_do_titulo(titulo_tag, page_url)
            if edital:
                resultados.append(edital)

        return resultados

    def _extrair_bloco_do_titulo(self, titulo_tag: Tag, page_url: str) -> Optional[EditalCNPq]:
        titulo = normalizar_espacos(titulo_tag.get_text(" ", strip=True))
        bloco_tags: list[Tag] = []
        cursor = titulo_tag.find_next_sibling()

        while cursor is not None:
            if isinstance(cursor, Tag) and cursor.name in {"h2", "h3"}:
                break
            if isinstance(cursor, Tag):
                bloco_tags.append(cursor)
            cursor = cursor.find_next_sibling()

        textos: list[str] = []
        publicado_em = None
        atualizado_em = None
        inscr_inicio = None
        inscr_fim = None
        anexos: list[AnexoCNPq] = []
        url_chamada = None

        for tag in bloco_tags:
            texto = normalizar_espacos(tag.get_text(" ", strip=True))
            if texto:
                textos.append(texto)

            pub, at = extrair_datas_publicacao(texto)
            if pub and not publicado_em:
                publicado_em = pub
            if at and not atualizado_em:
                atualizado_em = at

            # Inscrições podem vir no mesmo li ou em p + li subsequente.
            if "inscrições" in texto.lower() or "inscricoes" in texto.lower() or re.search(r"\d{2}/\d{2}/\d{4}\s*a\s*\d{2}/\d{2}/\d{4}", texto):
                ini, fim = extrair_periodo_inscricoes(texto)
                if ini or fim:
                    inscr_inicio = inscr_inicio or ini
                    inscr_fim = inscr_fim or fim

            for a in tag.select("a[href]"):
                nome = normalizar_espacos(a.get_text(" ", strip=True)) or "PDF"
                href = urljoin(page_url, a.get("href", ""))
                if not href:
                    continue
                if eh_anexo_pdf_relevante(nome, href):
                    anexos.append(AnexoCNPq(nome=nome, url=href, tipo="pdf"))
                    if url_chamada is None and eh_link_de_chamada(nome, href):
                        url_chamada = href

        descricao = escolher_descricao(textos)

        if inscr_inicio is None or inscr_fim is None:
            # fallback olhando o texto todo do bloco
            texto_bloco = " ".join(textos)
            ini, fim = extrair_periodo_inscricoes(texto_bloco)
            inscr_inicio = inscr_inicio or ini
            inscr_fim = inscr_fim or fim

        if url_chamada is None:
            for anexo in anexos:
                nome_anexo = anexo.nome.lower()
                if "chamada" in nome_anexo or "edital" in nome_anexo:
                    url_chamada = anexo.url
                    break

        if url_chamada is None and anexos:
            url_chamada = anexos[0].url

        return EditalCNPq(
            titulo=titulo,
            url_pagina=page_url,
            url_chamada=url_chamada,
            publicado_em=publicado_em,
            atualizado_em=atualizado_em,
            inscricoes_inicio=inscr_inicio,
            inscricoes_fim=inscr_fim,
            descricao=descricao,
            anexos=self._deduplicar_anexos(anexos),
        )

    def _proxima_pagina(self, soup: BeautifulSoup, page_url: str) -> Optional[str]:
        candidatos = []
        for a in soup.select("a[href]"):
            texto = normalizar_espacos(a.get_text(" ", strip=True)).lower()
            href = a.get("href", "")
            if not href:
                continue
            if "próximo" in texto or "proximo" in texto or "next" in texto:
                candidatos.append(urljoin(page_url, href))

        for cand in candidatos:
            if "gov.br/cnpq/pt-br/chamadas" in cand:
                return cand
        return candidatos[0] if candidatos else None

    @staticmethod
    def _deduplicar(editais: List[EditalCNPq]) -> List[EditalCNPq]:
        vistos: set[str] = set()
        final: list[EditalCNPq] = []
        for edital in editais:
            chave = edital.titulo.strip().lower()
            if chave in vistos:
                continue
            vistos.add(chave)
            final.append(edital)
        return final

    @staticmethod
    def _deduplicar_anexos(anexos: List[AnexoCNPq]) -> List[AnexoCNPq]:
        vistos: set[tuple[str, str]] = set()
        saida: list[AnexoCNPq] = []
        for anexo in anexos:
            chave = (anexo.nome.strip().lower(), anexo.url)
            if chave in vistos:
                continue
            vistos.add(chave)
            saida.append(anexo)
        return saida
