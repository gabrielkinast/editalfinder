"""Testes Consulplan crawler (helpers; sem rede)."""

from bs4 import BeautifulSoup

from concursos.main_consulplan_concursos import (
    _pick_edital_pdf,
    collect_listing_cards,
    consulplan_should_discard_non_opportunity,
    consulplan_should_discard_publication_label,
)


def test_collect_listing_only_open_sections():
    html = """
    <div id="ContentPlaceHolder1_PanelRepeaterAbertas_e_Aguardando">
      <div class="thumbnail"><h5>Org A</h5><h6>Cargo A</h6>
        <a href="getConc.aspx?key=abc">Acessar</a></div>
    </div>
    <div id="ContentPlaceHolder1_PanelRepeaterConcluidos">
      <div class="thumbnail"><h5>Org Velho</h5><h6>Cargo Velho</h6>
        <a href="getConc.aspx?key=old">Acessar</a></div>
    </div>
    """
    cards = collect_listing_cards(
        html, "https://institutoconsulplan.org.br/concursosNovo.aspx"
    )
    assert len(cards) == 1
    assert cards[0]["orgao"] == "Org A"
    assert cards[0]["secao_listagem"] == "abertas"


def test_pick_edital_pdf():
    soup = BeautifulSoup(
        """
    <table>
      <tr><td><a href="https://cdn/x/gabarito.pdf">Gabarito</a></td></tr>
      <tr><td><a href="https://cdn/x/edital.pdf">Edital nº 01 - Abertura</a></td></tr>
    </table>
    """,
        "html.parser",
    )
    assert _pick_edital_pdf(soup) == "https://cdn/x/edital.pdf"


def test_discard_gabarito_label():
    drop, _ = consulplan_should_discard_publication_label("Divulgação do gabarito definitivo")
    assert drop is True


def test_discard_non_opportunity():
    drop, _ = consulplan_should_discard_non_opportunity(
        titulo="X", body="homologação final do concurso"
    )
    assert drop is True
