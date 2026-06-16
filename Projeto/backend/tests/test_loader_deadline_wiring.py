"""Testes loader ↔ deadline_backfill wiring (Backend 10.2A)."""
from __future__ import annotations

import copy
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from deadline_backfill import (  # noqa: E402
    BACKFILL_SOURCE,
    LOADER_WIRING_VERSION,
    apply_deadline_backfill_to_payload,
    deadline_backfill_enabled,
)
from loader import map_to_db_schema  # noqa: E402


def _future(days: int = 90) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def test_flag_off_does_not_alter_payload() -> None:
    rec = {
        "fonte": "Grants.gov",
        "extras": {"closeDate": _future()},
        "link": "https://grants.gov/1",
    }
    original = copy.deepcopy(rec)
    out = apply_deadline_backfill_to_payload(rec, enabled=False)
    assert out is rec
    assert out == original
    assert not out.get("fim_inscricao")


def test_flag_on_grants_close_date_fills_prazo() -> None:
    iso = _future()
    rec = {
        "fonte": "Grants.gov",
        "titulo": "Research grant",
        "extras": {"closeDate": iso},
        "link": "https://grants.gov/2",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out["fim_inscricao"] == iso
    assert out["prazo_envio"] == iso
    assert out["extras"]["grants_close_date"] == iso
    assert out["extras"]["deadline_source_field"] == "closeDate"
    assert out["extras"]["loader_deadline_backfill"]["version"] == LOADER_WIRING_VERSION
    mapped, _ = map_to_db_schema(out)
    assert mapped["prazo_envio"] == iso


def test_grants_posted_date_not_deadline() -> None:
    rec = {
        "fonte": "Grants.gov",
        "data_publicacao": "2026-01-01",
        "extras": {"postedDate": "2026-01-01"},
        "link": "https://grants.gov/3",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out.get("fim_inscricao") is None
    assert out["extras"].get("grants_posted_date") == "2026-01-01"


def test_grants_close_explanation_sem_prazo() -> None:
    rec = {
        "fonte": "Grants.gov",
        "extras": {"closeDateExplanation": "No closing date — forecasted"},
        "link": "https://grants.gov/4",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out.get("fim_inscricao") is None
    assert out["extras"].get("sem_prazo_kind") == "deadline_explicitly_absent"


def test_doe_full_application_fills_prazo() -> None:
    y = date.today().year + 1
    rec = {
        "fonte": "DOE_ARPAE",
        "full_application_deadline": f"{y}-05-01",
        "concept_paper_deadline": f"{y}-03-01",
        "link": "https://arpa-e.energy.gov/1",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out["fim_inscricao"] == f"{y}-05-01"


def test_doe_concept_paper_only() -> None:
    y = date.today().year + 1
    rec = {
        "fonte": "DOE_ARPAE",
        "concept_paper_deadline": f"{y}-03-15",
        "link": "https://arpa-e.energy.gov/2",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out["fim_inscricao"] == f"{y}-03-15"


def test_bndes_lancamento_not_deadline() -> None:
    rec = {
        "fonte": "BNDES",
        "descricao": "O Sistema BNDES lançou, em 29.10.2025, Edital de Chamada Pública.",
        "link": "https://bndes.gov.br/1",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out.get("fim_inscricao") is None


def test_bndes_inscricoes_ate_fills_prazo() -> None:
    target = date.today() + timedelta(days=60)
    br = target.strftime("%d/%m/%Y")
    rec = {
        "fonte": "BNDES",
        "descricao": f"Inscrições até {br} para seleção de fundos.",
        "link": "https://bndes.gov.br/2",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out["fim_inscricao"] == target.isoformat()


def test_bndes_linha_permanente_sem_prazo_kind() -> None:
    rec = {
        "fonte": "BNDES",
        "titulo": "Linha permanente de financiamento",
        "descricao": "Crédito contínuo.",
        "link": "https://bndes.gov.br/3",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out.get("fim_inscricao") is None
    assert out["extras"].get("sem_prazo_kind") == "permanent_funding_line"


def test_preserve_valid_existing_prazo() -> None:
    iso = _future(30)
    rec = {
        "fonte": "Grants.gov",
        "fim_inscricao": iso,
        "extras": {"closeDate": _future(120)},
        "link": "https://grants.gov/5",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out["fim_inscricao"] == iso


def test_extras_merged_not_wiped() -> None:
    iso = _future()
    rec = {
        "fonte": "Grants.gov",
        "extras": {
            "closeDate": iso,
            "agency": "NSF",
            "custom_field": "keep_me",
        },
        "link": "https://grants.gov/6",
    }
    out = apply_deadline_backfill_to_payload(rec, enabled=True)
    assert out["extras"]["agency"] == "NSF"
    assert out["extras"]["custom_field"] == "keep_me"
    assert out["extras"]["deadline_source"] == BACKFILL_SOURCE


def test_deadline_backfill_enabled_default_false() -> None:
    assert deadline_backfill_enabled() is False
