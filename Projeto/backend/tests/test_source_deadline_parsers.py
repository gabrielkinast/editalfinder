"""Testes CORE/source_deadline_parsers.py (Backend 3)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from source_deadline_parsers import (  # noqa: E402
    parse_araucaria_deadlines,
    parse_china_tender_deadlines,
    parse_grants_api_deadlines,
)


def test_china_closing_date_english() -> None:
    html = "<div>Bid closing date: 2026-08-20</div><p>Posted: 2026-01-01</p>"
    r = parse_china_tender_deadlines("", html=html)
    assert r.get("prazo_data") == "2026-08-20"
    assert r.get("deadline_source_field") == "bid_closing_date"
    assert r.get("deadline_confidence") == "alta"


def test_araucaria_inscricoes_ate() -> None:
    r = parse_araucaria_deadlines("Chamada pública — inscrições até 25/05/2026")
    assert r.get("fim_inscricao") == "2026-05-25"
    assert r.get("deadline_source_field") == "inscricoes_ate"


def test_grants_close_date() -> None:
    r = parse_grants_api_deadlines({"closeDate": "09/30/2027", "postedDate": "05/09/2026"})
    assert r.get("fim_inscricao") == "2027-09-30"
    assert r.get("deadline_source_field") == "closeDate"


def test_grants_posted_not_deadline() -> None:
    r = parse_grants_api_deadlines({"posted_date": "2026-05-09"})
    assert r.get("fim_inscricao") is None
    assert r.get("deadline_missing_in_source") is True


def test_araucaria_cronograma_sem_data() -> None:
    r = parse_araucaria_deadlines("Cronograma: fase 1 análise, fase 2 seleção — sem data limite")
    assert r.get("fim_inscricao") is None
    assert r.get("deadline_requires_pdf") is False
