"""Testes ITA vestibular crawler (helpers; sem rede)."""

from bs4 import BeautifulSoup

from concursos.main_militar_aeroespacial_ita import (
    _parse_prova_dates,
    _parse_vestibular_year,
    _pick_edital_pdf,
    ita_should_discard_non_opportunity,
)


def test_parse_vestibular_year():
    assert _parse_vestibular_year("Vestibular 2027 cronograma") == 2027


def test_parse_prova_dates():
    blob = "Prova 1ª Fase: 27 set 2026 (13h-18h) Provas 2ª Fase: 20 a 23 out 2026"
    p1, p2 = _parse_prova_dates(blob)
    assert p1 == "2026-09-27"
    assert p2 == "2026-10-23"


def test_pick_edital_pdf():
    html = """
    <a href="programa_2026.pdf">Programa de Matérias</a>
    <a href="instrucoes/edital_2026_retificado.pdf">Edital do Concurso 2026</a>
    """
    soup = BeautifulSoup(html, "html.parser")
    link = _pick_edital_pdf(soup, "https://www.vestibular.ita.br/topo.htm")
    assert link and "edital_2026" in link


def test_discard_gabarito():
    drop, _ = ita_should_discard_non_opportunity(titulo="X", body="gabarito definitivo")
    assert drop is True
