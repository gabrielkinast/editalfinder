"""Testes do crawler IBFC (helpers; rede opcional em smoke)."""

from bs4 import BeautifulSoup

from concursos.main_ibfc_concursos import (
    _collect_informacao_urls,
    _parse_inscricao_dates,
    ibfc_should_discard_non_opportunity,
    ibfc_should_discard_situacao,
)


def test_collect_informacao_urls():
    html = """
    <html><body>
    <a href="/informacoes/490/">A</a>
    <a href="https://concursos.ibfc.org.br/informacoes/500/">B</a>
    <a href="/painel/x">P</a>
    </body></html>
    """
    urls = _collect_informacao_urls(
        html,
        "https://concursos.ibfc.org.br/index/abertos/",
        robots_parser=None,
    )
    assert "https://concursos.ibfc.org.br/informacoes/490" in urls
    assert "https://concursos.ibfc.org.br/informacoes/500" in urls


def test_parse_inscricao_dates_from_p_insc():
    html = """<html><body><div id="pgInformacoes">
    <p class="insc"><b>Inscrições:</b> 11/05/2026 10:00 a 22/06/2026 23:00</p>
    </div></body></html>"""
    soup = BeautifulSoup(html, "html.parser")
    a, b = _parse_inscricao_dates(soup)
    assert a == "2026-05-11"
    assert b == "2026-06-22"


def test_situacao_encerrada():
    assert ibfc_should_discard_situacao("situação: encerrado")[0] is True


def test_non_opportunity_not_title_only():
    drop, _ = ibfc_should_discard_non_opportunity(
        titulo="Concurso público",
        body="Período de inscrições abertas conforme edital.",
    )
    assert drop is False
