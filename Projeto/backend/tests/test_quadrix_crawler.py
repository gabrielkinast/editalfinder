"""Testes do crawler Quadrix (helpers; rede opcional em smoke)."""

from bs4 import BeautifulSoup

from concursos.main_quadrix_concursos import (
    _collect_informacao_urls,
    _parse_inscricao_dates,
    quadrix_should_discard_non_opportunity,
    quadrix_should_discard_situacao,
)


def test_collect_informacao_urls():
    html = """
    <html><body>
    <a href="/informacoes/3032/">A</a>
    <a href="https://www.quadrix.org.br/informacoes/3063/">B</a>
    <a href="/painel/x">P</a>
    </body></html>
    """
    urls = _collect_informacao_urls(
        html,
        "https://www.quadrix.org.br/index/abertos/",
        robots_parser=None,
    )
    assert "https://www.quadrix.org.br/informacoes/3032" in urls
    assert "https://www.quadrix.org.br/informacoes/3063" in urls


def test_parse_inscricao_dates_from_p_insc():
    html = """<html><body><div id="pgInformacoes">
    <p class="insc"><b>Inscrições:</b> 11/05/2026 10:00 a 22/06/2026 23:00</p>
    </div></body></html>"""
    soup = BeautifulSoup(html, "html.parser")
    a, b = _parse_inscricao_dates(soup)
    assert a == "2026-05-11"
    assert b == "2026-06-22"


def test_situacao_encerrada():
    assert quadrix_should_discard_situacao("situação: encerrado")[0] is True


def test_non_opportunity_not_title_only():
    drop, _ = quadrix_should_discard_non_opportunity(
        titulo="Concurso público",
        body="Período de inscrições abertas conforme edital.",
    )
    assert drop is False
