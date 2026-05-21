"""Testes unitários — extração de datas FGV (HTML/PDF texto)."""

from concursos.fgv_edital_dates import (
    fgv_merge_schedule_with_pdf_text,
    fgv_schedule_from_text,
)


def test_periodo_inscricoes_por_extenso_macae_style():
    t = (
        "4. DAS INSCRIÇÕES 4.1 As inscrições estarão abertas no período de "
        "30 de março de 2026 a 30 de abril de 2026."
    )
    s = fgv_schedule_from_text(t)
    assert s["data_inicio_inscricao"] == "2026-03-30"
    assert s["data_fim_inscricao"] == "2026-04-30"


def test_periodo_inscricoes_de_a_slash():
    t = "Período de inscrições de 10/03/2026 a 15/04/2026 para o concurso."
    s = fgv_schedule_from_text(t)
    assert s["data_inicio_inscricao"] == "2026-03-10"
    assert s["data_fim_inscricao"] == "2026-04-15"


def test_periodo_mojibake_marco_no_pdf():
    t = "estarão abertas no período de 30 de maro de 2026 a 30 de abril de 2026."
    s = fgv_schedule_from_text(t)
    assert s["data_inicio_inscricao"] == "2026-03-30"
    assert s["data_fim_inscricao"] == "2026-04-30"


def test_encerramento_inscricoes():
    t = "O encerramento das inscrições ocorrerá em 20/05/2026."
    s = fgv_schedule_from_text(t)
    assert s["data_fim_inscricao"] == "2026-05-20"


def test_prova_objetiva():
    t = "A prova objetiva será em 14/06/2026 no período da manhã."
    s = fgv_schedule_from_text(t)
    assert s["data_prova"] == "2026-06-14"


def test_merge_pdf_overrides_fim():
    prior = fgv_schedule_from_text("Sem datas aqui.")
    assert prior["data_fim_inscricao"] is None
    pdf_blob = "Período de inscrições de 01/02/2026 a 28/02/2026."
    m = fgv_merge_schedule_with_pdf_text(
        titulo="X",
        body="Sem datas.",
        pdf_text=pdf_blob,
        prior_inicio=prior["data_inicio_inscricao"],
        prior_fim=prior["data_fim_inscricao"],
        prior_prova=prior["data_prova"],
    )
    assert m["data_fim_inscricao"] == "2026-02-28"
    assert m["data_inicio_inscricao"] == "2026-02-01"
