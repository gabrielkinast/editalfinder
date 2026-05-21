"""Testes do crawler Objetiva (helpers; sem rede obrigatória)."""

from bs4 import BeautifulSoup

from concursos.main_objetiva_concursos import (
    _collect_informacao_urls,
    _parse_inscricao_dates,
    _pick_edital_pdf,
    objetiva_should_discard_non_opportunity,
)


def test_collect_informacao_urls():
    html = """
    <html><body>
    <a href="/informacoes/2589/">A</a>
    <a href="https://concursos.objetivas.com.br/informacoes/2590">B</a>
    </body></html>
    """
    urls = _collect_informacao_urls(
        html,
        "https://concursos.objetivas.com.br/index/abertos/",
        robots_parser=None,
    )
    assert "https://concursos.objetivas.com.br/informacoes/2589" in urls


def test_parse_inscricao_dates():
    html = """
    <html><body>
    <p class="insc">Inscrições de 01/05/2026 00:00 a 15/05/2026 23:59</p>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    a, b = _parse_inscricao_dates(soup)
    assert a == "2026-05-01"
    assert b == "2026-05-15"


def test_pick_edital_pdf():
    html = """
    <div id="blocoPublicacoes">
    <li class="pdf"><a href="https://cdn.example/edital.pdf">Edital de Abertura</a></li>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    assert _pick_edital_pdf(soup) == "https://cdn.example/edital.pdf"


def test_non_opportunity_resultado():
    drop, _ = objetiva_should_discard_non_opportunity(
        titulo="Concurso X",
        body="Divulgação do Gabarito Definitivo.",
    )
    assert drop is True
