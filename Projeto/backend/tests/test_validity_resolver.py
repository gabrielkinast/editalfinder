"""Testes CORE/validity_resolver.py + deadline_normalizer (Backend 9 / 10.1D)."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from deadline_normalizer import (  # noqa: E402
    has_useful_deadline,
    infer_locale_from_source,
    normalize_deadline,
    parse_deadline_date,
)
from opportunity_enricher import enrich_opportunity_record  # noqa: E402
from validity_resolver import resolve_validity  # noqa: E402


def test_edital_futuro_aberto() -> None:
    future = (date.today() + timedelta(days=60)).isoformat()
    rec = {
        "titulo": "Chamada pública de fomento",
        "fim_inscricao": future,
        "link": "https://example.org/edital",
    }
    out = resolve_validity(rec)
    assert out["validade_status"] in ("aberto", "vencendo_30")
    assert out["validade_data"] == future


def test_edital_passado_encerrado() -> None:
    past = (date.today() - timedelta(days=30)).isoformat()
    rec = {"titulo": "Edital encerrado", "prazo_envio": past, "link": "https://x.com/e"}
    out = resolve_validity(rec)
    assert out["validade_status"] == "encerrado"


def test_noticia_nao_aplicavel() -> None:
    rec = {
        "titulo": "Notícia: ministro anuncia programa",
        "link": "https://gov.br/noticias/1",
        "tipo_registro": "noticia",
    }
    out = resolve_validity(rec)
    assert out["validade_status"] == "nao_aplicavel"


def test_edital_sem_prazo() -> None:
    rec = {
        "titulo": "Chamada pública para projetos de PD&I",
        "descricao": "Inscrições abertas. Consulte o edital para prazos.",
        "link": "https://example.org/chamada",
    }
    out = resolve_validity(rec)
    assert out["validade_status"] in ("sem_prazo", "desconhecido")


def test_grants_forecast_sem_close() -> None:
    rec = {
        "titulo": "Forecast opportunity — research grant",
        "fonte_recurso": "Grants.gov",
        "descricao": "Forecast notice without close date.",
        "extras": {"closeDateExplanation": "No closing date — forecasted"},
        "link": "https://grants.gov/forecast/1",
    }
    out = resolve_validity(rec)
    assert out["validade_status"] in ("sem_prazo", "desconhecido", "nao_aplicavel")
    assert out["validade_data"] in (None, "")


def test_prazo_invalido() -> None:
    rec = {"titulo": "Edital", "prazo": "data inválida xyz", "link": "https://x.com"}
    out = resolve_validity(rec)
    assert out["validade_status"] in ("prazo_invalido", "sem_prazo")


# --- Backend 10.1D ---


def test_pt_br_numeric_deadline_in_text() -> None:
    target = date.today() + timedelta(days=90)
    future = target.strftime("%d/%m/%Y")
    rec = {
        "titulo": "Chamada Pública BNDES",
        "fonte_recurso": "BNDES",
        "descricao": f"Inscrições até {future} para seleção de fundos.",
        "link": "https://bndes.gov.br/chamada",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] == target.isoformat()
    out = resolve_validity(rec, deadline=dl)
    assert out["validade_status"] in ("aberto", "vencendo_30", "vencendo_7")


def test_pt_br_textual_month() -> None:
    year = date.today().year + 1
    rec = {
        "titulo": "Seleção de Fundos",
        "fonte_recurso": "BNDES",
        "descricao": f"Prazo final: 15 de dezembro de {year}",
        "link": "https://bndes.gov.br/edital",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] == f"{year}-12-15"


def test_pt_br_publication_date_rejected() -> None:
    rec = {
        "titulo": "Linha permanente de financiamento BNDES",
        "fonte_recurso": "BNDES",
        "descricao": "Publicado em 10/05/2026 sem prazo de inscrição.",
        "link": "https://bndes.gov.br/linha",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] is None
    assert dl["prazo_status"] == "sem_prazo"


def test_pt_br_result_date_rejected() -> None:
    rec = {
        "titulo": "Resultado da chamada",
        "fonte_recurso": "BNDES",
        "descricao": "Resultado em 10/05/2026 divulgado no portal.",
        "link": "https://bndes.gov.br/resultado",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] is None


def test_en_deadline_textual() -> None:
    year = date.today().year + 1
    rec = {
        "titulo": "ARPA-E funding opportunity",
        "fonte_recurso": "DOE_ARPAE",
        "descricao": f"Full Application Deadline: March 31, {year}",
        "link": "https://arpa-e.energy.gov/foa",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] == f"{year}-03-31"


def test_grants_close_date_field() -> None:
    future = (date.today() + timedelta(days=120)).isoformat()
    rec = {
        "titulo": "Research Grant",
        "fonte_recurso": "Grants.gov",
        "extras": {"closeDate": future},
        "link": "https://grants.gov/opp/1",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] == future
    assert dl["prazo_confidence"] == "alta"


def test_grants_posted_date_rejected() -> None:
    rec = {
        "titulo": "Grant without close",
        "fonte_recurso": "Grants.gov",
        "data_publicacao": "2026-01-01",
        "extras": {"postedDate": "2026-01-01"},
        "link": "https://grants.gov/opp/2",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] is None


def test_grants_archive_date_rejected_without_close() -> None:
    rec = {
        "titulo": "Archived grant",
        "fonte_recurso": "Grants.gov",
        "extras": {"archiveDate": "2026-12-31"},
        "link": "https://grants.gov/opp/3",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] is None


def test_doe_full_application_beats_concept_paper() -> None:
    year = date.today().year + 1
    rec = {
        "titulo": "DE-FOA-TEST",
        "fonte_recurso": "DOE_ARPAE",
        "full_application_deadline": f"{year}-04-30",
        "concept_paper_deadline": f"{year}-03-15",
        "link": "https://arpa-e.energy.gov/foa",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] == f"{year}-04-30"


def test_bndes_linha_permanente_sem_data() -> None:
    rec = {
        "titulo": "Linha permanente de financiamento BNDES",
        "fonte_recurso": "BNDES",
        "descricao": "Crédito disponível de forma contínua.",
        "link": "https://bndes.gov.br/financiamento",
    }
    dl = normalize_deadline(rec)
    out = resolve_validity(rec, deadline=dl)
    assert dl["prazo_data"] is None
    assert out["validade_status"] in ("sem_prazo", "desconhecido")


def test_ambiguous_numeric_date_uses_locale_by_source() -> None:
    parsed_en = parse_deadline_date("03/04/2026", locale_hint="en_US", source="Grants.gov")
    parsed_br = parse_deadline_date("03/04/2026", locale_hint="pt_BR", source="BNDES")
    assert parsed_en and parsed_en["date"] == "2026-03-04"
    assert parsed_br and parsed_br["date"] == "2026-04-03"


def test_doe_nofo_two_dates_prefers_second() -> None:
    rec = {
        "titulo": "DE-FOA-0003556",
        "fonte_recurso": "DOE_ARPAE",
        "descricao": (
            "DE-FOA-0003556 SUPERHOT Notice Of Funding Opportunity (NOFO) "
            "2/19/2025 09:30 AM ET 3/5/2026 09:30 AM ET"
        ),
        "link": "https://arpa-e.energy.gov/",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] == "2026-03-05"


def test_doe_nofo_tbd_rejected_single_date() -> None:
    rec = {
        "titulo": "DE-FOA-0003555",
        "fonte_recurso": "DOE_ARPAE",
        "descricao": "Notice Of Funding Opportunity (NOFO) 2/14/2025 09:30 AM ET TBD",
        "link": "https://arpa-e.energy.gov/",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] is None


def test_multiple_candidates_choose_best_deadline() -> None:
    year = date.today().year + 1
    rec = {
        "titulo": "Grant",
        "fonte_recurso": "Grants.gov",
        "concept_paper_deadline": f"{year}-02-01",
        "full_application_deadline": f"{year}-05-01",
        "close_date": f"{year}-06-01",
        "link": "https://grants.gov/1",
    }
    dl = normalize_deadline(rec)
    assert dl["prazo_data"] == f"{year}-05-01"


def test_has_useful_deadline_with_prazo_envio() -> None:
    future = (date.today() + timedelta(days=30)).isoformat()
    rec = {"titulo": "Chamada", "prazo_envio": future, "link": "https://x.com"}
    assert has_useful_deadline(rec) is True


def test_enricher_promotes_sem_prazo_with_close_date() -> None:
    future = (date.today() + timedelta(days=45)).isoformat()
    rec = {
        "titulo": "Call for proposals — innovation fund",
        "fonte_recurso": "Grants.gov",
        "descricao": "Funding opportunity for research teams.",
        "extras": {"closeDate": future},
        "link": "https://grants.gov/opp/99",
    }
    enr = enrich_opportunity_record(rec)
    assert enr.get("prazo_data") == future
    assert enr.get("actionability_type") == "oportunidade_principal"


def test_enricher_portal_util_stays_portal_with_date() -> None:
    rec = {
        "titulo": "EIC Accelerator",
        "fonte_recurso": "EIC",
        "descricao": "Application deadline: March 31, 2027 for hub information.",
        "link": "https://eic.ec.europa.eu/accelerator",
    }
    enr = enrich_opportunity_record(rec)
    assert enr.get("actionability_type") in ("portal_util", "oportunidade_principal", "desconhecido")


def test_infer_locale_en_for_grants() -> None:
    assert infer_locale_from_source("Grants.gov") == "en_US"


def test_infer_locale_br_for_bndes() -> None:
    assert infer_locale_from_source("BNDES") == "pt_BR"
