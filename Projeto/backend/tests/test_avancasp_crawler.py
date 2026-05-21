"""Testes Avança SP crawler (helpers; sem rede)."""

from bs4 import BeautifulSoup

from concursos.main_avancasp_concursos import (
    _collect_informacao_urls,
    _parse_inscricao_dates,
    _pick_edital_pdf,
    avancasp_should_discard_non_opportunity,
)


def test_collect_informacao_urls_dedupe():
    html = """
    <a href="/informacoes/255/">A</a>
    <a href="/informacoes/255/">B</a>
    <a href="/informacoes/256/">C</a>
    <a href="/painel/login">X</a>
    """
    urls = _collect_informacao_urls(
        html,
        "https://www.avancasp.org.br/index/abertos/",
        robots_parser=None,
    )
    assert urls == [
        "https://www.avancasp.org.br/informacoes/255",
        "https://www.avancasp.org.br/informacoes/256",
    ]


def test_parse_inscricao_dates():
    html = '<p class="insc">Inscrições: 14/05/2026 00:00 a 15/06/2026 23:59</p>'
    soup = BeautifulSoup(html, "html.parser")
    a, b = _parse_inscricao_dates(soup)
    assert a == "2026-05-14"
    assert b == "2026-06-15"


def test_pick_edital_pdf():
    html = """
    <div id="blocoPublicacoes">
      <li class="pdf"><a href="https://cdn.example.com/cronograma.pdf">Cronograma</a></li>
      <li class="pdf"><a href="https://cdn.example.com/edital.pdf">EDITAL COMPLETO</a></li>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    link = _pick_edital_pdf(soup, "https://www.avancasp.org.br/informacoes/1/")
    assert link == "https://cdn.example.com/edital.pdf"


def test_discard_gabarito():
    drop, _ = avancasp_should_discard_non_opportunity(
        titulo="X", body="Divulgação do gabarito definitivo"
    )
    assert drop is True
