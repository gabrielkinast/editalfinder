"""Testes do crawler EmbarcaTech residências (helpers; sem rede)."""

from bs4 import BeautifulSoup

from concursos.main_residencias_embarcatech import (
    _collect_process_urls,
    _infer_valor_tipo,
    _is_institutional_process_url,
    _parse_inscricao_dates,
    _parse_table_dates,
    embarcatech_should_discard,
)


def test_is_institutional_process_url():
    assert _is_institutional_process_url("https://ead.ifrn.edu.br/portal/edital-24-2024-dg-zl-re-ifrn/")
    assert not _is_institutional_process_url("https://embarcatech.softex.br/inscricoes/")


def test_parse_table_dates():
    html = """
    <table>
    <tr><td>Inscrições dos alunos</td><td>10/10/2024 até 01/11/2024 às 14h</td></tr>
    </table>
    """
    soup = BeautifulSoup(html, "html.parser")
    a, b = _parse_table_dates(soup)
    assert a == "2024-10-10"
    assert b == "2024-11-01"


def test_parse_inscricao_de_ate():
    a, b = _parse_inscricao_dates("Período de inscrições de 01/10/2024 a 15/10/2024")
    assert a == "2024-10-01"
    assert b == "2024-10-15"


def test_collect_process_urls():
    html = """
    <a href="https://ead.ifrn.edu.br/portal/edital-24-2024-dg-zl-re-ifrn/">Edital IFRN</a>
    <a href="https://embarcatech.softex.br/inscricoes/">Hub</a>
    """
    urls = _collect_process_urls(
        html,
        "https://embarcatech.softex.br/inscricoes/",
        robots_parser=None,
    )
    assert any("ifrn.edu.br" in u for u in urls)


def test_discard_resultado():
    drop, _ = embarcatech_should_discard("X", "Divulgação do resultado final")
    assert drop is True


def test_infer_valor_tipo():
    assert _infer_valor_tipo("Bolsa mensal", "R$ 3100", True) == "bolsa"
    assert _infer_valor_tipo("Auxílio", "valor auxilio estudantil", True) == "auxilio"
    assert _infer_valor_tipo("X", "Y", False) is None
