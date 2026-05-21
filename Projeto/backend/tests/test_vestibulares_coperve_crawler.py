"""Testes do crawler Coperve vestibulares (helpers; sem rede obrigatória)."""

from concursos.main_vestibulares_coperve import (
    _infer_tipo_vestibular,
    _is_process_candidate,
    _parse_inscricao_from_blob,
    coperve_should_discard_closed,
)


def test_parse_inscricao_de_ate():
    a, b = _parse_inscricao_from_blob("De 14/04/2026 10:00 a 14/05/2026 23:59")
    assert a == "2026-04-14"
    assert b == "2026-05-14"


def test_infer_tipo_vestibular():
    t, _ = _infer_tipo_vestibular("Vestibular Unificado 2026", "prova objetiva")
    assert t == "vestibular"
    t2, _ = _infer_tipo_vestibular("Processo Seletivo Refugiados", "vagas para refugiados")
    assert t2 == "programa_ingresso"


def test_is_process_candidate():
    assert _is_process_candidate("https://refugiados2026.ufsc.br/")
    assert not _is_process_candidate("https://001ddp2026.concursos.ufsc.br/")


def test_discard_encerrado():
    drop, _ = coperve_should_discard_closed(
        "Vestibular 2025",
        "Inscrições encerradas no dia 15 de outubro de 2025",
    )
    assert drop is True
