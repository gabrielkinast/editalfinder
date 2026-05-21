"""Testes IME militar/aeroespacial crawler (helpers; sem rede)."""

from bs4 import BeautifulSoup

import re

from concursos.main_militar_aeroespacial_ime import (
    _score_pdf,
    _year_from_url,
    ime_should_discard_non_opportunity,
    pick_edital_pdf,
)


def test_year_from_url():
    assert _year_from_url("/admissao/cfg/2026-2027/CFG%20ATIVA%202026.pdf") == 2026


def test_score_cfg_ativa_reserva():
    href_a = "https://www.ime.eb.mil.br/images/arquivos/admissao/cfg/2026-2027/CFG%20ATIVA%202026.pdf"
    href_r = "https://www.ime.eb.mil.br/images/arquivos/admissao/cfg/2026-2027/CFG%20RESERVA%202026.pdf"
    assert _score_pdf(href_a, "EDITAL CFG/ATIVA", process_key="cfg_ativa", cfg_track="ativa") > _score_pdf(
        href_r, "EDITAL CFG/ATIVA", process_key="cfg_ativa", cfg_track="ativa"
    )
    assert _score_pdf(href_r, "EDITAL CFG/RESERVA", process_key="cfg_reserva", cfg_track="reserva") > _score_pdf(
        href_a, "EDITAL CFG/RESERVA", process_key="cfg_reserva", cfg_track="reserva"
    )


def test_pick_edital_cfg_ativa():
    html = """
    <div class="com-content-article__body">
    <a href="/images/arquivos/admissao/cfg/2026-2027/CFG%20RESERVA%202026.pdf">RESERVA</a>
    <a href="/images/arquivos/admissao/cfg/2026-2027/CFG%20ATIVA%202026.pdf">EDITAL CFG/ATIVA 2026-2027</a>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    link = pick_edital_pdf(
        soup,
        "https://www.ime.eb.mil.br/vestibular-e-concursos/cfg-ensino-medio/inscricoes",
        process_key="cfg_ativa",
        cfg_track="ativa",
    )
    assert link and "ATIVA" in link


def test_discard_resultado_final():
    drop, _ = ime_should_discard_non_opportunity(
        titulo="X",
        pdf_url="https://www.ime.eb.mil.br/images/arquivos/admissao/cg/Resultado_FINAL_EQA25.pdf",
    )
    assert drop is True


def test_cp_vagas_regex():
    blob = "Número de vagas para o CP/IME 2026: 90 (Portaria)"
    m = re.search(r"n[uú]mero\s+de\s+vagas[^:]{0,120}:\s*(\d{1,4})\b", blob, re.I)
    assert m and int(m.group(1)) == 90


def test_no_discard_aprovados_in_body_text():
    drop, _ = ime_should_discard_non_opportunity(
        titulo="IME — CP/IME 2026",
        pdf_url="https://www.ime.eb.mil.br/images/arquivos/admissao/cp/Calendario_CP_IME_2026.pdf",
    )
    assert drop is False


def test_pick_edital_cg_mic():
    html = """
    <a href="/images/arquivos/admissao/cg/Resultado_FINAL_EQA25.pdf">Resultado</a>
    <a href="/images/arquivos/admissao/cg/MIC_EQA_2025PUBLICADO.pdf">Manual MIC</a>
    <a href="/images/arquivos/admissao/cg/Calendario_EQA20252026.pdf">Calendário</a>
    """
    soup = BeautifulSoup(html, "html.parser")
    link = pick_edital_pdf(
        soup,
        "https://www.ime.eb.mil.br/vestibular-e-concursos/cg/legislacao-cg",
        process_key="cg",
    )
    assert link and "MIC_EQA" in link
