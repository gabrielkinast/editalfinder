"""Testes payload tabela sombra Backend 7."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_shadow_common import (  # noqa: E402
    SHADOW_PAYLOAD_KEYS,
    SHADOW_WRITE_ENV,
    analyze_shadow_batch,
    build_shadow_payload,
    shadow_write_allowed,
    write_shadow_rows,
)


def test_payload_contains_id_edital() -> None:
    rec = {"id_edital": 42, "titulo": "Chamada pública de fomento"}
    payload = build_shadow_payload(rec)
    assert payload["id_edital"] == 42


def test_payload_only_expected_keys() -> None:
    rec = {"id_edital": 1, "titulo": "Edital energia solar"}
    payload = build_shadow_payload(rec)
    assert set(payload.keys()) == set(SHADOW_PAYLOAD_KEYS)


def test_secondary_and_flags_are_lists() -> None:
    rec = {
        "id_edital": 2,
        "titulo": "Programa NATO counter-drone military security",
    }
    payload = build_shadow_payload(rec)
    assert isinstance(payload["area_tematica_secondary"], list)
    assert isinstance(payload["qualidade_flags"], list)
    assert isinstance(payload["backend_enrichment"], dict)


def test_low_confidence_goes_to_review() -> None:
    rec = {"id_edital": 3, "titulo": "Informações gerais", "descricao": "Portal institucional"}
    payload = build_shadow_payload(rec)
    analysis = analyze_shadow_batch([rec], [payload], review_limit=10)
    assert analysis["low_confidence_rows"] or analysis["risky_area_changes"]


def test_write_shadow_aborts_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(SHADOW_WRITE_ENV, raising=False)
    with pytest.raises(PermissionError, match=SHADOW_WRITE_ENV):
        write_shadow_rows([{"id_edital": 1, "enrichment_version": "backend_6.0"}])


def test_write_shadow_allowed_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(SHADOW_WRITE_ENV, "true")
    assert shadow_write_allowed()


def test_generate_script_aborts_write_without_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(SHADOW_WRITE_ENV, raising=False)
    from generate_backend_enrichment_shadow_payload import main

    with patch.object(sys, "argv", ["generate_backend_enrichment_shadow_payload.py", "--write-shadow"]):
        code = main()
    assert code == 2


def test_write_shadow_never_targets_edital_table(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(SHADOW_WRITE_ENV, "true")
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    mock_table.upsert.return_value.execute.return_value = MagicMock(data=[])

    with patch("db.supabase", mock_client):
        row = build_shadow_payload({"id_edital": 99, "titulo": "Chamada pública"})
        result = write_shadow_rows([row])

    mock_client.table.assert_called_with("editais_backend_enrichment_shadow")
    assert mock_client.table.call_args[0][0] != "edital"
    assert result["written"] == 1
