"""Testes CORE/noise_classifier.py (Backend 10–10.1)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from noise_classifier import classify_noise  # noqa: E402


def _cl(titulo: str, **kwargs):
    rec = {"titulo": titulo, "link": "https://example.org/page", **kwargs}
    return classify_noise(rec)


def _assert_actionable(out: dict) -> None:
    assert out["is_noise"] is False
    assert out["noise_type"] is None
    assert out["is_actionable_opportunity"] is True
    assert out["classification_bucket"] == "oportunidade_acionavel"
    assert out["actionability_type"] in ("oportunidade_principal", "oportunidade_sem_prazo")


# --- 1. Chamadas CNPq não viram resultado ---


def test_chamada_cnpq_mpa_jovem_cientista() -> None:
    out = _cl(
        "CHAMADA PÚBLICA CNPq/MPA Nº 03/2026 PROGRAMA JOVEM CIENTISTA DA PESCA ARTESANAL - INICIAÇÃO CIENTÍFICA"
    )
    _assert_actionable(out)


def test_chamada_cnpq_ms_pesquisas_estrategicas() -> None:
    out = _cl("Chamada CNPq/MS-SCTIE-Decit Nº 30/2025 - Pesquisas Estratégicas em Terapias Avançadas")
    _assert_actionable(out)


def test_chamada_cnpq_auxilio_promocao_eventos() -> None:
    """'Eventos' no nome do programa não deve virar tipo evento."""
    out = _cl("Chamada CNPq Nº 26/2025 Auxílio à Promoção de Eventos Científicos, Tecnológicos e/ou de Inovação")
    _assert_actionable(out)
    assert out["actionability_type"] != "evento"


def test_chamada_selecao_fundos_clima() -> None:
    out = _cl("Chamada Pública para Seleção de Fundos com Foco em Mitigação Climática - Chamada de Clima")
    _assert_actionable(out)


def test_chamada_cnpq_mcti_fndct() -> None:
    out = _cl("Chamada Pública CNPq/MCTI/FNDCT Nº 25/2025")
    _assert_actionable(out)


def test_chamada_embrapii_unidades() -> None:
    out = _cl("Chamada Pública Unidades Embrapii nº 03/2025")
    _assert_actionable(out)


def test_premio_confap() -> None:
    out = _cl("premio confap de ciencia tecnologia inovacao professora niede guidon 5 edicao 2025")
    assert out["is_noise"] is False
    assert out["actionability_type"] in ("oportunidade_principal", "oportunidade_sem_prazo", "desconhecido")


# --- 2. Resultados finais ---


def test_chamada_resultado_final_2022() -> None:
    out = _cl("Chamada Pública 03/2022 – RESULTADO FINAL")
    assert out["actionability_type"] == "resultado"
    assert out["is_actionable_opportunity"] is False
    assert out["is_noise"] is False
    assert out["noise_type"] is None


def test_resultado_selecao_subvencao() -> None:
    out = _cl("Resultado - Seleção Pública de Subvenção Econômica")
    assert out["actionability_type"] == "resultado"


def test_chamada_resultado_final_2020() -> None:
    out = _cl("CHAMADA PÚBLICA 04/2020 – Resultado Final")
    assert out["actionability_type"] == "resultado"


def test_lista_selecionados_chamada_publica() -> None:
    out = _cl("Lista de selecionados - Chamada Pública")
    assert out["actionability_type"] == "resultado"
    assert out["is_noise"] is False
    assert out["noise_type"] is None
    assert out["is_actionable_opportunity"] is False


def test_chamada_real_nao_vira_resultado_por_resultado_no_corpo() -> None:
    """Marcador 'resultado' só no corpo não derruba chamada no título."""
    out = _cl(
        "Chamada Pública CNPq/MCTI/FNDCT Nº 25/2025",
        descricao="O resultado desta seleção será divulgado em breve.",
    )
    _assert_actionable(out)
    assert out["actionability_type"] != "resultado"


# --- 3. Portal útil ---


def test_licitacoes_contratos_portal_util() -> None:
    out = _cl("Licitações e Contratos")
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False
    assert out["noise_type"] is None
    assert out["classification_bucket"] == "portal_util"


def test_open_funding_opportunities() -> None:
    out = _cl("Open funding opportunities")
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False


def test_bnb_atividades_financiadas() -> None:
    out = _cl(
        "Educação – atividades financiadas – Banco do Nordeste",
        fonte_recurso="Banco do Nordeste",
    )
    assert out["actionability_type"] == "portal_util"
    assert out["actionability_type"] != "evento"
    assert out["is_noise"] is False
    assert out["noise_type"] is None


def test_eureka_network_portal_util() -> None:
    out = _cl("Eureka Network funding opportunities", fonte_recurso="Eureka Network")
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False


# --- 3b. Grants.gov EN ---


def test_grants_gov_funding_opportunity_title() -> None:
    out = _cl(
        "SBIR/STTR Funding Opportunity: Advanced Propulsion",
        fonte_recurso="Grants.gov",
    )
    assert out["is_noise"] is False
    assert out["noise_type"] is None
    assert out["actionability_type"] in ("oportunidade_principal", "oportunidade_sem_prazo")


def test_grants_gov_notice_of_funding_in_body() -> None:
    out = _cl(
        "Advanced Manufacturing Research Grant",
        fonte_recurso="Grants.gov",
        descricao="This is a Notice of Funding Opportunity (NOFO) for small businesses.",
    )
    assert out["actionability_type"] in ("oportunidade_principal", "oportunidade_sem_prazo", "desconhecido")
    assert out["is_noise"] is False


# --- 4. Portal genérico ---


def test_sobre_bdmg() -> None:
    out = _cl("Sobre o BDMG", fonte_recurso="BDMG")
    assert out["actionability_type"] in ("portal_generico", "sem_oportunidade")
    assert out["is_noise"] is True


def test_english_portal_generico() -> None:
    out = _cl("English")
    assert out["actionability_type"] == "portal_generico"
    assert out["is_noise"] is True


# --- 5. Eventos ---


def test_titulo_eventos_portal() -> None:
    out = _cl("Eventos")
    assert out["actionability_type"] in ("portal_generico", "evento")
    assert out["is_actionable_opportunity"] is False


def test_webinar_evento_not_actionable() -> None:
    out = _cl("Webinar – Applying to Eurostars")
    assert out["actionability_type"] == "evento"
    assert out["is_actionable_opportunity"] is False


# --- 6. Invariantes ---


def test_invariant_noise_type_null_when_not_noise() -> None:
    out = _cl("Chamada pública de fomento 2026", fim_inscricao="2030-01-01")
    assert out["is_noise"] is False
    assert out["noise_type"] is None


def test_invariant_desconhecido_nao_e_ruido() -> None:
    """desconhecido permanece is_noise=false mesmo com link válido."""
    out = _cl("Página institucional genérica sem marcadores", fonte_recurso="CAS")
    assert out["actionability_type"] == "desconhecido"
    assert out["is_noise"] is False
    assert out["noise_type"] is None


def test_invariant_non_noise_types_have_null_noise_type() -> None:
    cases = [
        ("Chamada pública 2026", {"fim_inscricao": "2030-01-01"}),
        ("Chamada Pública 03/2022 – RESULTADO FINAL", {}),
        ("Licitações e Contratos", {}),
        ("Webinar – Applying to Eurostars", {}),
        ("Retificação do edital 01/2025", {}),
    ]
    for titulo, extra in cases:
        out = _cl(titulo, **extra)
        if out["actionability_type"] in (
            "oportunidade_principal",
            "oportunidade_sem_prazo",
            "resultado",
            "retificacao",
            "portal_util",
            "documento_auxiliar",
            "evento",
            "desconhecido",
        ):
            assert out["is_noise"] is False, titulo
            assert out["noise_type"] is None, titulo


def test_dispensa_licitacao_not_resultado() -> None:
    out = _cl("Dispensa de Licitação 01/2026")
    assert out["actionability_type"] in ("oportunidade_principal", "oportunidade_sem_prazo")
    assert out["is_noise"] is False


def test_de_foa_principal() -> None:
    out = _cl("DE-FOA-0003555", fonte_recurso="DOE ARPA-E")
    assert out["actionability_type"] in ("oportunidade_principal", "oportunidade_sem_prazo")


# --- 7. Perfis por fonte (10.1C) — BDMG ---


def test_bdmg_sobre_portal_generico() -> None:
    out = _cl("Sobre o BDMG", fonte_recurso="BDMG")
    assert out["actionability_type"] == "portal_generico"
    assert out["is_noise"] is True


def test_bdmg_eventos_portal_generico() -> None:
    out = _cl("Eventos", fonte_recurso="BDMG")
    assert out["actionability_type"] == "portal_generico"
    assert out["is_noise"] is True


def test_bdmg_linhas_financiamento_portal_util() -> None:
    out = _cl("Linhas Permanentes de Financiamento Municipal", fonte_recurso="BDMG")
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False
    assert out["noise_type"] is None


def test_bdmg_trabalhe_sem_oportunidade() -> None:
    out = _cl("Trabalhe no BDMG", fonte_recurso="BDMG")
    assert out["actionability_type"] == "sem_oportunidade"
    assert out["is_noise"] is True


def test_bdmg_protecao_dados_portal_generico() -> None:
    out = _cl("Proteção de dados e Privacidade", fonte_recurso="BDMG")
    assert out["actionability_type"] == "portal_generico"
    assert out["is_noise"] is True


# --- BNB ---


def test_bnb_graos_atividades_financiadas() -> None:
    out = _cl("Grãos – atividades financiadas – Banco do Nordeste", fonte_recurso="BNB")
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False


def test_bnb_credito_poder_publico() -> None:
    out = _cl(
        "Crédito para Poder Público – financiamento de projetos – Banco do Nordeste",
        fonte_recurso="Banco do Nordeste",
    )
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False


# --- Eureka ---


def test_eureka_open_funding_hub() -> None:
    out = _cl("Open funding opportunities", fonte_recurso="Eureka Network")
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False


def test_eureka_eurostars_call_opportunity() -> None:
    out = _cl("Eurostars call for projects", fonte_recurso="Eureka Network")
    assert out["actionability_type"] in ("oportunidade_principal", "oportunidade_sem_prazo")
    assert out["is_noise"] is False


def test_eureka_innowwide_call() -> None:
    out = _cl("Innowwide call for market feasibility projects", fonte_recurso="Eureka Network")
    assert out["actionability_type"] in ("oportunidade_principal", "oportunidade_sem_prazo")
    assert out["is_noise"] is False


# --- QST ---


def test_qst_japanese_not_opportunity() -> None:
    out = _cl(
        "量子科学技術研究開発機構の研究成果発表",
        fonte_recurso="QST",
        descricao="research news from national institute",
    )
    assert out["actionability_type"] == "noticia"
    assert out["is_actionable_opportunity"] is False
    assert out["is_noise"] is True


# --- China ---


def test_mofcom_desconhecido_sem_ruido() -> None:
    out = _cl("某公司招标公告", fonte_recurso="China International Tendering (MOFCOM)")
    assert out["actionability_type"] == "desconhecido"
    assert out["is_noise"] is False


def test_nsfc_desconhecido_sem_forcar_ruido() -> None:
    out = _cl("国家自然科学基金项目指南", fonte_recurso="NSFC")
    assert out["actionability_type"] == "desconhecido"
    assert out["is_noise"] is False


# --- Suppliers ---


def test_lockheed_supplier_portal() -> None:
    out = _cl("Supplier Portal", fonte_recurso="Lockheed Martin Suppliers")
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False


def test_bae_become_supplier() -> None:
    out = _cl("Become a Supplier", fonte_recurso="BAE Systems Suppliers")
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False


def test_general_dynamics_procurement() -> None:
    out = _cl("Procurement — Doing Business With Us", fonte_recurso="General Dynamics Suppliers")
    assert out["actionability_type"] == "portal_util"
    assert out["is_noise"] is False


# --- DoD SBIR ---


def test_dod_sbir_data_resources_portal_generico() -> None:
    out = _cl("Data Resources", fonte_recurso="DoD SBIR/STTR")
    assert out["actionability_type"] == "portal_generico"
    assert out["is_noise"] is True


# --- Regressão 10.1A ---


def test_cnpq_nao_regride_10_1a() -> None:
    out = _cl("Chamada Pública CNPq/MCTI/FNDCT Nº 25/2025", fonte_recurso="CNPq")
    _assert_actionable(out)


def test_grants_gov_nao_regride_10_1a() -> None:
    out = _cl(
        "SBIR/STTR Funding Opportunity: Advanced Propulsion",
        fonte_recurso="Grants.gov",
    )
    assert out["actionability_type"] in ("oportunidade_principal", "oportunidade_sem_prazo")
    assert out["is_noise"] is False
