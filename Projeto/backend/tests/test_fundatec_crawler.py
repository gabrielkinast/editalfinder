"""Testes do crawler Fundatec (extrações específicas)."""

from datetime import date

from bs4 import BeautifulSoup

from concursos.common import parse_remuneracao_taxa_br, parse_vagas_certame
from concursos.main_fundatec_concursos import (
    extract_data_fim_inscricao_fundatec,
    extract_fundatec_article_text,
    fundatec_should_discard_non_opportunity,
    fundatec_strip_vagas_salario_if_low_trust,
    _pick_portal_concurso_link_from_node,
)


def test_fundatec_fim_nao_usa_somente_data_editorial():
    s = "Matéria publicada em 07/05/2026. A cidade divulga novo concurso."
    assert extract_data_fim_inscricao_fundatec(s) is None


def test_fundatec_fim_inscricoes_explicito_ddmmyyyy():
    s = "As inscrições seguem até 08/05/2026 para os cargos."
    assert extract_data_fim_inscricao_fundatec(s) == "2026-05-08"


def test_fundatec_fim_inscricoes_por_extenso_com_contexto():
    s = "As inscrições vão até o dia 29 de maio de 2026 conforme edital."
    assert extract_data_fim_inscricao_fundatec(s) == "2026-05-29"


def test_sidebar_121_vagas_nao_contamina_artigo():
    """Vagas na sidebar/fora do .entry-content não entram no texto principal."""
    html = """
    <html><head><title>Post X - Fundatec</title></head><body>
    <div id="secondary" class="sidebar">Outro certame com 121 vagas no estado.</div>
    <article>
      <div class="entry-content">
        <p>O município divulga processo com 4 vagas para técnico.</p>
      </div>
    </article>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    tit, body, frag, notes = extract_fundatec_article_text(soup)
    assert "121" not in body
    vagas, _ = parse_vagas_certame(
        body,
        scan_limit=5000,
        paragraph_scope=True,
        title_for_crosscheck=tit or "Post",
    )
    assert vagas == 4


def test_descarta_participacao_candidatos():
    tit = "Cidade recebe candidatos no domingo"
    body = "Mais de 2,5 mil candidatos participam das provas neste domingo."
    drop, reason = fundatec_should_discard_non_opportunity(
        titulo=tit,
        body=body,
        link_edital=None,
        data_fim_inscricao=None,
        today=date(2026, 5, 12),
    )
    assert drop is True
    assert reason == "noticia_nao_oportunidade_ativa"


def test_descarta_prova_foi_realizada():
    tit = "Provas do concurso"
    body = "A prova foi realizada no domingo, 3 de maio de 2026, com fiscalização."
    drop, _ = fundatec_should_discard_non_opportunity(
        titulo=tit,
        body=body,
        link_edital=None,
        data_fim_inscricao=None,
        today=date(2026, 5, 12),
    )
    assert drop is True


def test_mantem_se_data_fim_futura_mesmo_com_participam():
    tit = "Inscrições abertas"
    body = "Mil candidatos participarão após o encerramento das inscrições."
    drop, _ = fundatec_should_discard_non_opportunity(
        titulo=tit,
        body=body,
        link_edital="https://www.fundatec.org.br/portal/concursos/x",
        data_fim_inscricao="2026-12-31",
        today=date(2026, 5, 12),
    )
    assert drop is False


def test_salario_somente_corpo_principal():
    html = """
    <body>
    <aside class="widget">Salários de até R$ 10.000,00 em outro edital.</aside>
    <article><div class="entry-content">
      <p>Taxa de inscrição R$ 120,00. Sem menção a salário neste parágrafo.</p>
    </div></article>
    </body>
    """
    soup = BeautifulSoup(html, "html.parser")
    _, body, _, _ = extract_fundatec_article_text(soup)
    smin, smax, taxa, meta = parse_remuneracao_taxa_br(body)
    assert smin is None and smax is None
    assert taxa == 120.0
    assert meta.get("possible_salary_detected") is not True


def test_link_edital_so_no_artigo_principal():
    page = "https://www2.fundatec.org.br/2026/05/01/post-teste/"
    html = f"""
    <body>
    <aside><a href="https://www.fundatec.org.br/portal/concursos/index_concursos.php?concurso=99">sidebar</a></aside>
    <article><div class="entry-content"><p>Texto.</p><a href="https://example.com/outro">x</a></div></article>
    </body>
    """
    soup = BeautifulSoup(html, "html.parser")
    _, _, frag, _ = extract_fundatec_article_text(soup)
    assert _pick_portal_concurso_link_from_node(frag, page) is None

    html2 = """
    <article><div class="entry-content">
      <p>Inscrições no <a href="https://www.fundatec.org.br/portal/concursos/index_concursos.php?concurso=12">portal</a>.</p>
    </div></article>
    """
    soup2 = BeautifulSoup(html2, "html.parser")
    _, _, frag2, _ = extract_fundatec_article_text(soup2)
    assert _pick_portal_concurso_link_from_node(frag2, page) is not None
    assert "index_concursos.php?concurso=12" in _pick_portal_concurso_link_from_node(frag2, page)


def test_suprime_vagas_salario_sem_link_nem_data_fim():
    n, smin, smax, taxa, notes = fundatec_strip_vagas_salario_if_low_trust(
        link_edital=None,
        data_fim_inscricao=None,
        numero_vagas=121,
        salario_min=9700.0,
        salario_max=10000.0,
        taxa_inscricao=50.0,
    )
    assert n is None and smin is None and smax is None and taxa is None
    assert "valores_suprimidos_sem_link_oficial_nem_data_fim" in notes
