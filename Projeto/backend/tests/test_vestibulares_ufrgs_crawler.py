"""Testes do crawler UFRGS CV (helpers; sem rede obrigatória)."""

from concursos.main_vestibulares_ufrgs import (
    _infer_tipo,
    _is_process_url,
    _parse_inscricao_dates,
    ufrgs_should_discard,
)


def test_parse_inscricao_de_a_mes():
    a, b = _parse_inscricao_dates(
        "Período de inscrições: de 08 a 29 de setembro de 2025"
    )
    assert a == "2025-09-08"
    assert b == "2025-09-29"


def test_is_process_url():
    assert _is_process_url("https://www.ufrgs.br/coperse/concurso-vestibular/")
    assert _is_process_url("https://www.ufrgs.br/coperse/processo-seletivo-simplificado-cln-2026-1/")
    assert not _is_process_url("https://www.ufrgs.br/coperse/cv-2015/")
    assert not _is_process_url("https://www.ufrgs.br/coperse/concurso-vestibular-anteriores/")


def test_infer_tipo():
    t, _ = _infer_tipo("Vestibular UFRGS 2027", "prova de redação")
    assert t == "vestibular"
    t2, _ = _infer_tipo("PSU 2024", "processo seletivo unificado extravestibular")
    assert t2 == "programa_ingresso"


def test_discard_aquisicao_provas():
    drop, _ = ufrgs_should_discard("VESTIBULAR 2026", "aquisição de provas anteriores")
    assert drop is True
