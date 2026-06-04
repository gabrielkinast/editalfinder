"""Testes CORE/deadline_normalizer.py (Backend 1)."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from deadline_normalizer import normalize_deadline  # noqa: E402


def test_dd_mm_yyyy_field() -> None:
    r = {"prazo_envio": "25/05/2026", "titulo": "Chamada X"}
    dl = normalize_deadline(r)
    assert dl["prazo_data"] == "2026-05-25"
    assert dl["prazo_confidence"] == "alta"
    assert dl["prazo_status"] in ("vencendo_7", "vencendo_30", "prazo_confortavel", "encerrado")


def test_english_deadline_in_text() -> None:
    r = {
        "titulo": "Grant opportunity",
        "descricao": "Submission deadline: May 25, 2026 for proposals.",
    }
    dl = normalize_deadline(r)
    assert dl["prazo_data"] == "2026-05-25"
    assert dl["prazo_confidence"] == "baixa"
    assert "extraido_de_texto" in dl["prazo_notes"]


def test_sem_prazo() -> None:
    dl = normalize_deadline({"titulo": "Portal institucional", "fonte_recurso": "X"})
    assert dl["prazo_status"] == "sem_prazo"
    assert dl["prazo_data"] is None
    assert dl["prazo_confidence"] == "nenhuma"


def test_prazo_invalido() -> None:
    dl = normalize_deadline({"prazo_envio": "em breve", "titulo": "Edital"})
    assert dl["prazo_status"] == "prazo_invalido"
    assert dl["prazo_raw"] == "em breve"


def test_extras_deadline() -> None:
    dl = normalize_deadline(
        {
            "titulo": "Test",
            "extras": {"deadline": "2026-06-01"},
        }
    )
    assert dl["prazo_data"] == "2026-06-01"
    assert dl["prazo_source_field"] == "extras.deadline"


def test_encerrado_past() -> None:
    past = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")
    dl = normalize_deadline({"prazo_envio": past})
    assert dl["prazo_status"] == "encerrado"
