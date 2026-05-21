"""Testes FCC crawler (helpers; sem rede)."""

from bs4 import BeautifulSoup

from concursos.main_fcc_concursos import (
    _collect_listing_items,
    _parse_inscricao_box,
    _pick_edital_link,
    _unwrap_pdf_href,
    fcc_should_discard_non_opportunity,
)


LISTING_SNIPPET = """
<div id="refazerLista">
<div class="box5">
  <motion.div class="textoInstituicao2"><a href="/concursos/sface125/index.html">SEFAZ CE</a></motion.div>
  <div class="textoConcurso2"><a href="/concursos/sface125/index.html">Auditor</a></motion.div>
</motion.div>
</motion.div>
"""


def test_collect_listing_items():
    html = """
    <div id="refazerLista">
      <div class="box5">
        <div class="textoInstituicao2"><a href="/concursos/sface125/index.html">SEFAZ CE</a></div>
        <div class="textoConcurso2"><a href="/concursos/sface125/index.html">Auditor</a></div>
      </div>
    </div>
    """
    items = _collect_listing_items(
        html, "https://www.concursosfcc.com.br/concursoInscricaoAberta.html"
    )
    assert len(items) == 1
    assert items[0]["instituicao"] == "SEFAZ CE"
    assert "sface125" in items[0]["url"]


def test_parse_inscricao_box():
    html = """
    <div class="rotuloTopico1">Inscrições (exclusivamente via Internet)</div>
    <div class="box3">
      <span><b>Valor da Inscrição</b></span><br/>
      <span>R$ 230,00 (duzentos e trinta reais)</span><br/><br/>
      <span><b>Período</b></span><br/>
      <span>Período de inscrição para todos os candidatos:
      <br/>Das 10h do dia 27/04/2026 às 23h59min do dia 01/06/2026 (horário de Brasília)</span>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    ini, fim, taxa = _parse_inscricao_box(soup)
    assert ini == "2026-04-27"
    assert fim == "2026-06-01"
    assert taxa == 230.0


def test_unwrap_rybena_pdf():
    href = (
        "https://www.concursosfcc.com.br/rybena/web/index.html?"
        "file=https://www.concursosfcc.com.br/concursos/sface125/edital.pdf"
    )
    assert _unwrap_pdf_href(href).endswith("edital.pdf")


def test_pick_edital_prefers_abertura():
    html = """
    <div class="campoLinkArquivo">
      <a href="/rybena/web/index.html?file=https://x/ret.pdf">Edital retificação</a>
    </div>
    <div class="campoLinkArquivo">
      <a href="/rybena/web/index.html?file=https://x/abertura.pdf">Edital abertura de inscrições</a>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    link = _pick_edital_link(soup, "https://www.concursosfcc.com.br/concursos/x/index.html")
    assert link and "abertura.pdf" in link


def test_discard_resultado():
    drop, _ = fcc_should_discard_non_opportunity(
        titulo="X", body="Divulgação do gabarito definitivo"
    )
    assert drop is True
