"""Testes do crawler Legalle (helpers; sem rede obrigatória)."""

from bs4 import BeautifulSoup

from concursos.main_legalle_concursos import (
    _collect_ver_urls,
    _parse_inscricao_dates,
    _pick_edital_pdf,
    legalle_should_discard_non_opportunity,
)


def test_collect_ver_urls():
    html = """
    <html><body>
    <a href="/edital/ver/2410/">A</a>
    <a href="https://portal.editais.legalleconcursos.com.br/edital/ver/2411">B</a>
    </body></html>
    """
    urls = _collect_ver_urls(
        html,
        "https://portal.editais.legalleconcursos.com.br/edital/index/abertos/",
        robots_parser=None,
    )
    assert "https://portal.editais.legalleconcursos.com.br/edital/ver/2410" in urls


def test_parse_inscricao_dates():
    html = """
    <html><body>
    <div class="col-sm-10">
    <p><b>Inscrições de</b> 04/05/2026 - 00:00 <b>até</b> 14/05/2026 - 18:00</p>
    </div>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    a, b = _parse_inscricao_dates(soup)
    assert a == "2026-05-04"
    assert b == "2026-05-14"


def test_pick_edital_abertura():
    html = """
    <div id="arquivos">
    <motion class="list-group-item">
    <p class="text-secondary">Edital nº 001/2025 - Abertura e Inscrições</p>
    <a href="https://cdn.example/edital.pdf">DOWNLOAD</a>
    </div>
    </div>
    """
    html = html.replace("<motion", "<div")
    soup = BeautifulSoup(html, "html.parser")
    assert _pick_edital_pdf(soup) == "https://cdn.example/edital.pdf"


def test_non_opportunity_resultado():
    drop, _ = legalle_should_discard_non_opportunity(
        titulo="Concurso X",
        body="Divulgado o Edital de Resultado Final.",
    )
    assert drop is True
