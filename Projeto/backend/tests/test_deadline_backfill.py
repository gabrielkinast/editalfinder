"""Testes CORE/deadline_backfill.py (Backend 10.1E)."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from deadline_backfill import (  # noqa: E402
    BACKFILL_SOURCE,
    apply_deadline_backfill_in_memory,
    extract_source_deadline_fields,
)
from opportunity_enricher import enrich_opportunity_record  # noqa: E402


def _future_iso(days: int = 90) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


# --- Grants.gov ---


def test_grants_close_date_iso() -> None:
    iso = _future_iso()
    rec = {
        "fonte_recurso": "Grants.gov",
        "titulo": "Research grant",
        "extras": {"closeDate": iso},
        "link": "https://grants.gov/1",
    }
    out = extract_source_deadline_fields(rec)
    assert out["prazo_envio"] == iso
    assert out["deadline_backfill_status"] == "new_deadline_found"
    assert out["extras_patch"]["deadline_source_field"] == "closeDate"


def test_grants_close_date_us_format() -> None:
    future = date.today() + timedelta(days=120)
    us = future.strftime("%m/%d/%Y")
    rec = {
        "fonte_recurso": "Grants.gov",
        "extras": {"close_date": us},
        "link": "https://grants.gov/2",
    }
    out = extract_source_deadline_fields(rec)
    assert out["prazo_envio"] == future.isoformat()


def test_grants_close_explanation_blocks() -> None:
    rec = {
        "fonte_recurso": "Grants.gov",
        "titulo": "Forecast grant",
        "extras": {"closeDateExplanation": "No closing date — forecasted"},
        "link": "https://grants.gov/3",
    }
    out = extract_source_deadline_fields(rec)
    assert out.get("prazo_envio") is None
    assert out["sem_prazo_kind"] == "deadline_explicitly_absent"


def test_grants_posted_date_not_deadline() -> None:
    rec = {
        "fonte_recurso": "Grants.gov",
        "titulo": "Funding opportunity",
        "data_publicacao": "2026-01-01",
        "extras": {"postedDate": "2026-01-01"},
        "link": "https://grants.gov/4",
    }
    out = extract_source_deadline_fields(rec)
    assert out.get("prazo_envio") is None
    assert out["sem_prazo_kind"] in ("missing_from_loader", "deadline_tbd", "unknown")


def test_grants_archive_without_close_rejected() -> None:
    rec = {
        "fonte_recurso": "Grants.gov",
        "extras": {"archiveDate": "2026-12-31"},
        "link": "https://grants.gov/5",
    }
    out = extract_source_deadline_fields(rec)
    assert out.get("prazo_envio") is None


def test_grants_funding_without_close_missing_loader() -> None:
    rec = {
        "fonte_recurso": "Grants.gov",
        "titulo": "DoW research funding opportunity",
        "descricao": "Grant program for innovation.",
        "link": "https://grants.gov/6",
    }
    out = extract_source_deadline_fields(rec)
    assert out["sem_prazo_kind"] == "missing_from_loader"


# --- DOE_ARPAE ---


def test_doe_full_application_beats_concept() -> None:
    y = date.today().year + 1
    rec = {
        "fonte_recurso": "DOE_ARPAE",
        "titulo": "DE-FOA-TEST",
        "full_application_deadline": f"{y}-04-30",
        "concept_paper_deadline": f"{y}-03-15",
        "link": "https://arpa-e.energy.gov/",
    }
    out = extract_source_deadline_fields(rec)
    assert out["prazo_envio"] == f"{y}-04-30"


def test_doe_concept_paper_only_accepted() -> None:
    y = date.today().year + 1
    rec = {
        "fonte_recurso": "DOE_ARPAE",
        "concept_paper_deadline": f"{y}-03-15",
        "link": "https://arpa-e.energy.gov/",
    }
    out = extract_source_deadline_fields(rec)
    assert out["prazo_envio"] == f"{y}-03-15"
    assert "concept" in (out.get("deadline_reason") or "").lower()


def test_doe_nofo_tbd_sem_prazo() -> None:
    rec = {
        "fonte_recurso": "DOE_ARPAE",
        "descricao": "Notice Of Funding Opportunity (NOFO) 2/14/2025 09:30 AM ET TBD",
        "link": "https://arpa-e.energy.gov/",
    }
    out = extract_source_deadline_fields(rec)
    assert out.get("prazo_envio") is None
    assert out["sem_prazo_kind"] == "deadline_tbd"


def test_doe_published_date_rejected() -> None:
    rec = {
        "fonte_recurso": "DOE_ARPAE",
        "data_publicacao": "2026-05-09",
        "descricao": "Published on May 9, 2026. Official portal record.",
        "link": "https://arpa-e.energy.gov/",
    }
    out = extract_source_deadline_fields(rec)
    assert out.get("prazo_envio") is None


# --- BNDES ---


def test_bndes_inscricoes_ate() -> None:
    target = date.today() + timedelta(days=60)
    br = target.strftime("%d/%m/%Y")
    rec = {
        "fonte_recurso": "BNDES",
        "titulo": "Chamada Pública BNDES",
        "descricao": f"Inscrições até {br} para seleção de fundos.",
        "link": "https://bndes.gov.br/",
    }
    out = extract_source_deadline_fields(rec)
    assert out["prazo_envio"] == target.isoformat()


def test_bndes_prazo_final_textual() -> None:
    y = date.today().year + 1
    rec = {
        "fonte_recurso": "BNDES",
        "descricao": f"Prazo final: 15 de dezembro de {y}",
        "link": "https://bndes.gov.br/",
    }
    out = extract_source_deadline_fields(rec)
    assert out["prazo_envio"] == f"{y}-12-15"


def test_bndes_lancamento_rejeitado() -> None:
    rec = {
        "fonte_recurso": "BNDES",
        "descricao": "O Sistema BNDES lançou, em 29.10.2025, Edital de Chamada Pública.",
        "link": "https://bndes.gov.br/",
    }
    out = extract_source_deadline_fields(rec)
    assert out.get("prazo_envio") is None


def test_bndes_linha_permanente() -> None:
    rec = {
        "fonte_recurso": "BNDES",
        "titulo": "Linha permanente de financiamento BNDES",
        "descricao": "Crédito disponível de forma contínua.",
        "link": "https://bndes.gov.br/",
    }
    out = extract_source_deadline_fields(rec)
    assert out["sem_prazo_kind"] == "permanent_funding_line"


def test_bndes_chamada_sem_prazo_missing_loader() -> None:
    rec = {
        "fonte_recurso": "BNDES",
        "titulo": "Chamada Pública para Seleção de Fundos",
        "descricao": "O BNDES abriu seleção de gestores.",
        "link": "https://bndes.gov.br/",
    }
    out = extract_source_deadline_fields(rec)
    assert out["sem_prazo_kind"] == "missing_from_loader"


# --- Integração ---


def test_preserve_existing_prazo_envio() -> None:
    iso = _future_iso(30)
    rec = {"fonte_recurso": "Grants.gov", "prazo_envio": iso, "link": "https://g/1"}
    out = extract_source_deadline_fields(rec)
    assert out["deadline_backfill_status"] == "preserved_existing"
    assert out["prazo_envio"] == iso


def test_invalid_existing_plus_valid_new_is_replacement_candidate() -> None:
    iso = _future_iso(45)
    rec = {
        "fonte_recurso": "Grants.gov",
        "prazo_envio": "data-invalida",
        "extras": {"closeDate": iso},
        "link": "https://g/2",
    }
    out = extract_source_deadline_fields(rec)
    assert out["deadline_backfill_status"] == "replacement_candidate"
    assert out["prazo_envio"] == iso


def test_apply_in_memory_sets_prazo_envio() -> None:
    iso = _future_iso()
    rec = {"fonte_recurso": "Grants.gov", "extras": {"closeDate": iso}, "link": "https://g/3"}
    patched, result = apply_deadline_backfill_in_memory(rec)
    assert patched["prazo_envio"] == iso
    assert patched["extras"]["deadline_source"] == BACKFILL_SOURCE


def test_backfill_sem_prazo_nao_rebaixa_oportunidade() -> None:
    rec = {
        "fonte_recurso": "BNDES",
        "titulo": "Chamada Pública para Seleção de Fundos de Investimento",
        "descricao": "Chamada aberta para gestores.",
        "link": "https://bndes.gov.br/chamada",
    }
    enr = enrich_opportunity_record(rec, with_deadline_backfill=True)
    assert enr.get("actionability_type") in ("oportunidade_sem_prazo", "oportunidade_principal")
    assert enr.get("is_noise") is False


def test_portal_util_com_data_nao_vira_oportunidade() -> None:
    rec = {
        "fonte_recurso": "EIC",
        "titulo": "EIC Accelerator",
        "descricao": "Application deadline: March 31, 2027 hub page.",
        "link": "https://eic.ec.europa.eu/accelerator",
    }
    enr = enrich_opportunity_record(rec, with_deadline_backfill=True)
    assert enr.get("actionability_type") in ("portal_util", "desconhecido", "oportunidade_sem_prazo")
    if enr.get("actionability_type") == "portal_util":
        assert enr.get("is_noise") is False


def test_extras_patch_contains_deadline_source() -> None:
    iso = _future_iso()
    rec = {"fonte_recurso": "Grants.gov", "extras": {"closeDate": iso}, "link": "https://g/4"}
    out = extract_source_deadline_fields(rec)
    assert out["extras_patch"]["deadline_source"] == BACKFILL_SOURCE
