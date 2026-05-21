"""Testes do crawler FGV Conhecimento (helpers; sem rede obrigatória)."""

from datetime import date

from concursos.main_fgv_concursos import (
    _collect_concurso_urls,
    _fgv_entity_suffix_from_title,
    _fgv_org_geo_from_title,
    fgv_should_discard_non_opportunity,
)


def test_fgv_entity_suffix_para_o():
    t = "Concurso Público para o Tribunal de Justiça do Estado de Santa Catarina"
    assert _fgv_entity_suffix_from_title(t) == "Tribunal de Justiça do Estado de Santa Catarina"


def test_fgv_entity_suffix_processo_simplificado():
    t = "Processo Seletivo Simplificado para a Secretaria da Educação do Estado de São Paulo"
    assert _fgv_entity_suffix_from_title(t) == "Secretaria da Educação do Estado de São Paulo"


def test_fgv_org_geo_prefeitura():
    t = "Concurso Público para a Prefeitura de Macaé"
    g = _fgv_org_geo_from_title(t)
    assert g["orgao"] == "Prefeitura de Macaé"
    assert g["municipio"] == "Macaé"


def test_collect_concurso_urls_basic():
    html = """
    <html><body>
    <a href="/concursos/foo26">A</a>
    <a href="https://conhecimento.fgv.br/concursos/bar26">B</a>
    <a href="/concursos/nosso-portfolio">C</a>
    </body></html>
    """
    urls = _collect_concurso_urls(
        html,
        "https://conhecimento.fgv.br/concursos",
        robots_parser=None,
    )
    assert "https://conhecimento.fgv.br/concursos/foo26" in urls
    assert "https://conhecimento.fgv.br/concursos/bar26" in urls
    assert not any("nosso-portfolio" in u for u in urls)


def test_fgv_discard_gabarito_sem_edital_nem_fim():
    today = date(2026, 5, 1)
    tit = "X"
    body = "Confira o gabarito definitivo da prova objetiva."
    drop, why = fgv_should_discard_non_opportunity(
        titulo=tit,
        body=body,
        link_edital=None,
        data_fim_inscricao=None,
        today=today,
    )
    assert drop is True
    assert "fgv" in why
