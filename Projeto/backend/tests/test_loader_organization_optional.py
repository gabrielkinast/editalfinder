"""Testes: organização opcional no loader (Backend 10.2B hotfix)."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

import loader  # noqa: E402


class PGRST205Error(Exception):
    code = "PGRST205"
    message = "Could not find the table 'public.organizacao' in the schema cache"


class OtherSupabaseError(Exception):
    code = "42501"
    message = "permission denied for table organizacao"


@pytest.fixture(autouse=True)
def _reset_org_lookup_state() -> None:
    loader.reset_organization_lookup_state()


def test_is_missing_organization_table_error_pgrst205() -> None:
    assert loader.is_missing_organization_table_error(PGRST205Error()) is True
    assert loader.is_missing_organization_table_error(
        Exception("PGRST205: Could not find the table 'public.organizacao' in the schema cache")
    ) is True


def test_is_missing_organization_table_error_other() -> None:
    assert loader.is_missing_organization_table_error(OtherSupabaseError()) is False
    assert loader.is_missing_organization_table_error(RuntimeError("timeout")) is False


def test_pgrst205_disables_lookup_and_returns_none() -> None:
    mock_table = MagicMock()
    mock_table.select.return_value.limit.return_value.execute.side_effect = PGRST205Error()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_table

    with patch.object(loader, "supabase", mock_supabase):
        assert loader.get_default_org_id() is None
        assert loader._ORGANIZATION_LOOKUP_AVAILABLE is False
        assert loader.get_default_org_id() is None

    assert mock_supabase.table.call_count == 1


def test_warning_emitted_only_once() -> None:
    mock_table = MagicMock()
    mock_table.select.return_value.limit.return_value.execute.side_effect = PGRST205Error()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_table

    with patch.object(loader.logger, "warning") as mock_warn:
        with patch.object(loader, "supabase", mock_supabase):
            loader.get_default_org_id()
            loader.get_default_org_id()

    assert mock_warn.call_count == 1
    assert "organizacao" in str(mock_warn.call_args).lower()


def test_map_to_db_schema_keeps_orgao_responsavel_without_org_id() -> None:
    mock_table = MagicMock()
    mock_table.select.return_value.limit.return_value.execute.side_effect = PGRST205Error()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_table

    item = {
        "titulo": "Grant",
        "fonte": "Grants.gov",
        "link": "https://simpler.grants.gov/opportunity/1",
        "extras": {"agency": "DoD"},
    }
    with patch.object(loader, "supabase", mock_supabase):
        mapped, extras = loader.map_to_db_schema(item)

    assert "id_organizacao" not in mapped
    assert extras.get("orgao_responsavel") == "DoD"


def test_strip_payload_removes_invalid_org_fields() -> None:
    row: dict[str, Any] = {
        "titulo": "X",
        "link": "https://example.com",
        "fonte_recurso": "Grants.gov",
        "orgao_responsavel": "DoD",
        "id_organizacao": None,
        "organizacao_responsavel": "bad",
        "organizacao": {"id": 1},
        "organization": {"name": "x"},
        "org": "y",
    }
    out = loader._strip_payload(row)
    assert out.get("orgao_responsavel") == "DoD"
    assert "id_organizacao" not in out
    assert "organizacao_responsavel" not in out
    assert "organizacao" not in out
    assert "organization" not in out
    assert "org" not in out


def test_non_pgrst205_error_propagates() -> None:
    mock_table = MagicMock()
    mock_table.select.return_value.limit.return_value.execute.side_effect = OtherSupabaseError()
    mock_supabase = MagicMock()
    mock_supabase.table.return_value = mock_table

    with patch.object(loader, "supabase", mock_supabase), pytest.raises(OtherSupabaseError):
        loader.get_default_org_id()


def test_resolve_orgao_fallback_chain() -> None:
    assert loader.resolve_orgao_responsavel_text({"fonte": "Grants.gov"}, {}) == "Grants.gov"
    assert loader.resolve_orgao_responsavel_text({}, {"agency": "NASA"}) == "NASA"
    assert loader.resolve_orgao_responsavel_text({}, {}) == "Não informado"


def test_merge_db_row_continues_after_org_lookup_unavailable() -> None:
    loader.disable_organization_lookup_for_session()
    mapped = {
        "titulo": "Grant",
        "link": "https://simpler.grants.gov/opportunity/9",
        "fonte_recurso": "Grants.gov",
        "prazo_envio": "2026-12-31",
    }
    extras = {"orgao_responsavel": "DoD", "agency": "DoD"}
    row = loader._merge_db_row(None, mapped, extras, {"fonte": "Grants.gov", "extras": extras})
    assert row["link"] == mapped["link"]
    assert "organizacao_responsavel" not in row
