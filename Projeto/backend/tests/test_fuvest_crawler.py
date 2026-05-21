"""Testes do crawler Fuvest (helpers; sem rede obrigatória)."""

from concursos.main_fuvest_concursos import (
    _is_news_slug,
    _is_pagination_url,
    _parse_inscricao_dates,
    fuvest_should_discard,
)


def test_parse_inscricao_fuvest_horario():
    di, df = _parse_inscricao_dates(
        "Inscrição: das 12h de 17/08/2026 até as 12h de 09/10/2026"
    )
    assert di == "2026-08-17"
    assert df == "2026-10-09"


def test_parse_inscricao_periodo():
    di, df = _parse_inscricao_dates(
        "Período: das 12h de 11/02/2026 até as 12h de 06/03/2026"
    )
    assert di == "2026-02-11"
    assert df == "2026-03-06"


def test_is_pagination():
    assert _is_pagination_url("https://www.fuvest.br/residencia/2")
    assert not _is_pagination_url("https://www.fuvest.br/residencia-medica")


def test_is_news_slug():
    assert _is_news_slug("residencia-medica-2026-divulga-resultado-pre-recurso")
    assert not _is_news_slug("auxiliar-laboratorio-2026")


def test_discard_resultado_sem_edital():
    drop, _ = fuvest_should_discard("Concurso X", "resultado final divulgado", link_edital=None, data_fim=None)
    assert drop is True


def test_keep_com_edital():
    drop, _ = fuvest_should_discard("Concurso X", "inscrições abertas", link_edital="http://x/ed.pdf", data_fim=None)
    assert drop is False
