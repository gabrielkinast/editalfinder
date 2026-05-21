"""Testes do crawler AOCP (helpers; sem rede obrigatória)."""

from concursos.main_aocp_concursos import (
    _pick_link_edital,
    _parse_aocp_datetime_to_iso_date,
    aocp_should_discard_non_opportunity,
)


def test_parse_iso_date():
    assert _parse_aocp_datetime_to_iso_date("2018-02-05 23:59:59") == "2018-02-05"


def test_parse_br_date():
    assert _parse_aocp_datetime_to_iso_date("05/02/2018 23:59:59") == "2018-02-05"


def test_pick_edital_prefers_abertura():
    pubs = [
        {"nome": "16/04/2026 - Homologação", "url": "https://x/homolog.pdf"},
        {"nome": "01/01/2017 - Edital de Abertura Nº 001/2017", "url": "https://x/edital.pdf"},
    ]
    assert _pick_link_edital(pubs) == "https://x/edital.pdf"


def test_non_opportunity_resultado_final():
    drop, _ = aocp_should_discard_non_opportunity(
        titulo="SUSIPE",
        chamada="Concurso Público C-204 - Divulgado o Edital de Resultado Final.",
    )
    assert drop is True


def test_non_opportunity_abertura_ok():
    drop, _ = aocp_should_discard_non_opportunity(
        titulo="Prefeitura X",
        chamada="Edital de Abertura nº 01/2026. Período de inscrições.",
    )
    assert drop is False
