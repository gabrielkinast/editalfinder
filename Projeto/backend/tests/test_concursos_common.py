"""Testes mínimos para concursos.common."""
from datetime import date

from concursos.common import (
    infer_nivel_escolaridade,
    infer_orgao_local_from_title,
    infer_tipo_selecao,
    infer_tipo_selecao_meta,
    normalize_text,
    parse_money_br,
    parse_remuneracao_taxa_br,
    parse_salario_min_max_br,
    parse_vagas,
    parse_vagas_certame,
    parse_vagas_cadastro_reserva,
    pci_infer_qualidade_dado,
    recency_should_discard,
    validate_concurso_item,
)


def test_normalize_text():
    assert normalize_text("  Olá\nMundo  ") == "Olá Mundo"


def test_parse_vagas():
    assert parse_vagas("Abertas 120 vagas para analista") == 120
    assert parse_vagas("Abertas 1.100 vagas para analista") == 1100
    assert parse_vagas("Há 4 vagas no edital") == 4
    assert parse_vagas("Concurso 2026 com 50 vagas") == 50
    assert parse_vagas("sem numero aqui") is None


def test_parse_vagas_cadastro_reserva_sem_numero():
    assert parse_vagas_cadastro_reserva("Cadastro reserva para o cargo") is True
    assert parse_vagas("Cadastro reserva para o cargo") is None


def test_parse_money_milhares_e_mil():
    assert parse_money_br("Remuneração de R$ 15,6 mil") == 15600.0
    assert parse_money_br("Salários de até R$ 22 mil") == 22000.0
    assert parse_money_br("R$ 10.868,68 iniciais") == 10868.68
    assert parse_money_br("R$ 1.719,26") == 1719.26


def test_parse_salario_ate_max():
    smin, smax = parse_salario_min_max_br("Ganhos até R$ 10.868,68 para o cargo")
    assert smin is None
    assert smax == 10868.68


def test_parse_remuneracao_taxa_vs_salario():
    smin, smax, taxa, meta = parse_remuneracao_taxa_br(
        "Taxa de inscrição de R$ 110,00. Salário inicial de R$ 5.000,00 para o cargo."
    )
    assert taxa == 110.0
    assert smin == 5000.0 and smax == 5000.0
    assert meta.get("possible_fee_detected") is True
    assert meta.get("possible_salary_detected") is True


def test_parse_remuneracao_so_taxa_pequena():
    smin, smax, taxa, _ = parse_remuneracao_taxa_br("O candidato paga R$ 95 referentes ao processo.")
    assert smin is None and smax is None
    assert taxa == 95.0


def test_pci_infer_qualidade_niveis():
    assert (
        pci_infer_qualidade_dado(
            titulo="T",
            link="https://x",
            orgao="Prefeitura",
            instituicao=None,
            estado="SP",
            municipio="Campinas",
            data_fim_inscricao="2026-06-01",
            data_prova="2026-07-01",
            data_publicacao=None,
            numero_vagas=10,
            salario_min=None,
            salario_max=None,
            taxa_inscricao=None,
        )
        == "alta"
    )
    assert (
        pci_infer_qualidade_dado(
            titulo="T",
            link="https://x",
            orgao="X",
            instituicao=None,
            estado=None,
            municipio=None,
            data_fim_inscricao=None,
            data_prova=None,
            data_publicacao=None,
            numero_vagas=5,
            salario_min=None,
            salario_max=None,
            taxa_inscricao=None,
        )
        == "media"
    )
    assert (
        pci_infer_qualidade_dado(
            titulo="T",
            link="https://x",
            orgao=None,
            instituicao=None,
            estado=None,
            municipio=None,
            data_fim_inscricao=None,
            data_prova=None,
            data_publicacao=None,
            numero_vagas=None,
            salario_min=None,
            salario_max=None,
            taxa_inscricao=None,
        )
        == "baixa"
    )
    r = infer_orgao_local_from_title("Prefeitura de Arujá - SP abre concurso")
    assert r["orgao"] == "Prefeitura de Arujá"
    assert r["municipio"] == "Arujá"
    assert r["estado"] == "SP"
    r2 = infer_orgao_local_from_title("Câmara de Campinas - SP")
    assert r2["orgao"] == "Câmara de Campinas"
    assert r2["municipio"] == "Campinas"
    assert r2["estado"] == "SP"


def test_infer_orgao_marinha_titulo_curto():
    r = infer_orgao_local_from_title("Marinha divulga concurso para a Escola Naval")
    assert r["orgao"] == "Marinha do Brasil"


def test_infer_nivel_escolaridade():
    assert infer_nivel_escolaridade("Concurso nível médio", "") == "medio"
    assert infer_nivel_escolaridade("", "Exige nível superior completo") == "superior"


def test_parse_remuneracao_ate_nove_mil_sem_salario_min():
    smin, smax, taxa, meta = parse_remuneracao_taxa_br(
        "Prefeitura abre seleção com salários de até R$ 9,5 mil e nível médio."
    )
    assert smin is None
    assert smax == 9500.0
    assert taxa is None
    assert meta.get("possible_salary_detected") is True


def test_parse_remuneracao_quatorze_mil():
    smin, smax, _, _ = parse_remuneracao_taxa_br("Remuneração de até R$ 14,4 mil para os cargos.")
    assert smin is None
    assert smax == 14400.0


def test_infer_orgao_prefeitura_car_longo_titulo():
    r = infer_orgao_local_from_title(
        "Prefeitura de Carlos Barbosa abre concursos públicos e processo seletivo com salários de até R$ 14,4 mil"
    )
    assert r["orgao"] == "Prefeitura de Carlos Barbosa"
    assert r["municipio"] == "Carlos Barbosa"


def test_infer_tipo_selecao_estagio_so_no_titulo_nao_usa_corpo():
    t, _ = infer_tipo_selecao_meta(
        "Câmara Municipal de X abre Concurso Público com salários de até R$ 9,5 mil",
        "Outra notícia fala de seleção de estágio na Assembleia.",
    )
    assert t == "concurso_publico"


def test_infer_tipo_selecao_estagio_prioriza_concurso_no_corpo():
    t, ev = infer_tipo_selecao_meta(
        "Assembleia Legislativa do RS abre seleção de estágio",
        "Também divulgamos concursos públicos em outras editorias.",
    )
    assert t == "estagio"
    assert "estagio" in ev


def test_infer_tipo_selecao_misto_concursos_e_ps():
    t, ev = infer_tipo_selecao_meta(
        "Prefeitura de X abre concursos públicos e processo seletivo",
        "Detalhes no edital.",
    )
    assert t == "processo_seletivo"
    assert "concursos_publicos_e_processo" in ev or "misto" in ev


def test_parse_vagas_certame_com_contexto():
    n, notes = parse_vagas_certame(
        "O edital municipal descreve 16 vagas para o concurso público de nível médio."
    )
    assert n == 16
    assert notes == []


def test_parse_vagas_certame_rejeita_sem_contexto():
    n, notes = parse_vagas_certame("Somewhere 34 vagas in unrelated boilerplate footer text.")
    assert n is None
    assert any("vagas_sem_contexto" in x for x in notes)


def test_parse_vagas_certame_ambiguous_multiplos():
    n, notes = parse_vagas_certame(
        "O concurso A traz 10 vagas para analista. Já o processo B prevê 20 vagas para assistente."
    )
    assert n is None
    assert any("vagas_ambiguas" in x for x in notes)


def test_parse_vagas_certame_paragraph_scope_same_number_two_blocks():
    body = (
        "O concurso publico municipal.\n\n"
        "No concurso publico municipal ha 34 vagas para nivel medio.\n\n"
        "O concurso publico estadual.\n\n"
        "No concurso publico estadual ha tambem 34 vagas para assistente.\n\n"
    )
    n, notes = parse_vagas_certame(body, paragraph_scope=True, title_for_crosscheck="")
    assert n is None
    assert any("vagas_ambiguas_nao_preenchidas" in x for x in notes)


def test_parse_vagas_certame_title_vagas_mismatch_body():
    body = "O concurso publico federal preve 16 vagas na Saude.\n\n"
    tit = "Concurso com 34 vagas para gari - Fundatec"
    n, notes = parse_vagas_certame(body, paragraph_scope=True, title_for_crosscheck=tit)
    assert n is None
    assert any("vagas_ambiguas_nao_preenchidas" in x for x in notes)


def test_parse_remuneracao_taxa_120_nao_vai_salario_min():
    smin, smax, taxa, _ = parse_remuneracao_taxa_br(
        "A taxa de inscrição de R$ 120,00. O salário inicial do cargo é de R$ 4.500,00."
    )
    assert taxa == 120.0
    assert smin == 4500.0
    assert smax == 4500.0


def test_parse_remuneracao_taxa_80_com_inscricao():
    smin, smax, taxa, _ = parse_remuneracao_taxa_br(
        "Taxa de R$ 80,00 para inscrição no concurso. Remuneração de até R$ 9,5 mil."
    )
    assert taxa == 80.0
    assert smin is None
    assert smax == 9500.0


def test_parse_remuneracao_r_120_sem_contexto_ambiguo():
    smin, smax, taxa, meta = parse_remuneracao_taxa_br(
        "Valor fixo de R$ 120,00 mencionado sem detalhar origem."
    )
    assert smin is None and smax is None
    assert taxa is None
    assert any("valor_ambiguo" in n for n in meta["value_extraction_notes"])


def test_pci_adjust_confidence_ambiguidade():
    from concursos.common import pci_adjust_confidence_for_ambiguity

    assert (
        pci_adjust_confidence_for_ambiguity(
            "alta", value_extraction_notes=["valor_ambiguo_excluido_de_salario:120.0"]
        )
        == "media"
    )
    assert (
        pci_adjust_confidence_for_ambiguity(
            "media", value_extraction_notes=["vagas_ambiguas_nao_preenchidas"]
        )
        == "baixa"
    )


def test_infer_tipo_vestibular():
    assert infer_tipo_selecao("Vestibular 2026 da X", "") == "vestibular"


def test_infer_tipo_concurso_publico_explicito():
    assert infer_tipo_selecao("Abre concurso público para analista", "") == "concurso_publico"


def test_infer_tipo_professor():
    assert infer_tipo_selecao("Professor de Matemática — processo", "") == "professor"


def test_recency_keep_future_prova():
    today = date(2026, 5, 1)
    drop, _ = recency_should_discard(
        data_fim_inscricao="2025-12-01",
        data_prova="2026-06-01",
        today=today,
        text_for_recent_heuristic="x",
    )
    assert drop is False


def test_recency_drop_past_fim_no_future_prova():
    today = date(2026, 5, 1)
    drop, why = recency_should_discard(
        data_fim_inscricao="2025-12-01",
        data_prova="2026-01-10",
        today=today,
        text_for_recent_heuristic="x",
    )
    assert drop is True
    assert "passada" in why


def test_validate_concurso_item_min():
    row = {
        "titulo": "T",
        "link": "https://example.com/x",
        "fonte": "f",
        "tipo_selecao": "concurso_publico",
        "status": "ativo",
        "validacao_status": "incompleto",
        "qualidade_dado": "media",
        "tags": [],
        "extras": {},
        "ativo": True,
    }
    assert validate_concurso_item(row) == []
