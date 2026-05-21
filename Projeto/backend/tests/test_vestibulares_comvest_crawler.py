"""Testes do crawler Comvest (helpers; sem rede obrigatória)."""

from concursos.main_vestibulares_comvest import (
    _mes_ano_to_iso,
    _parse_inscricao_dates,
    _parse_prova_dates,
)


def test_mes_ano_to_iso():
    assert _mes_ano_to_iso(18, "outubro", 2026) == "2026-10-18"


def test_parse_inscricao_de_a_mes():
    di, df = _parse_inscricao_dates(
        "Período de inscrições: de 01 a 15 de setembro de 2027"
    )
    assert di == "2027-09-01"
    assert df == "2027-09-15"


def test_parse_inscricao_slash():
    di, df = _parse_inscricao_dates("Inscrições de 10/08/2027 até 20/09/2027")
    assert di == "2027-08-10"
    assert df == "2027-09-20"


def test_parse_prova_primeira_fase():
    p = _parse_prova_dates(
        "A primeira fase será realizada no dia 18 de outubro de 2026"
    )
    assert p == "2026-10-18"
