"""Testes apply controlado Grants.gov (Backend 10.2B)."""
from __future__ import annotations

import copy
import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from deadline_backfill import controlled_apply_enabled, deadline_backfill_enabled  # noqa: E402
from grants_controlled_apply import (  # noqa: E402
    DEFAULT_MAX_APPLY_BATCH,
    apply_grants_candidates,
    build_candidate_entry,
    classify_apply_action,
    is_grants_gov_record,
    load_candidates_file,
    merge_extras_for_apply,
    resolve_prazo_for_apply,
    run_grants_deadline_dry_run,
    validate_candidates_batch,
    validate_dry_run_report_recent,
)


def _future(days: int = 90) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _grants_item(close: str | None = None, *, posted: str | None = None, explanation: str | None = None) -> dict:
    extras: dict = {"opportunity_id": "99"}
    if close:
        extras["closeDate"] = close
        extras["close_date"] = close
    if posted:
        extras["postedDate"] = posted
    if explanation:
        extras["closeDateExplanation"] = explanation
    item = {
        "titulo": "Defense grant opportunity",
        "descricao": "Military funding grant program",
        "link": f"https://simpler.grants.gov/opportunity/{close or 'x'}",
        "fonte": "Grants.gov",
        "extras": extras,
    }
    if close:
        item["fim_inscricao"] = close
    return item


def test_recrawl_close_date_generates_update_candidate() -> None:
    iso = _future()
    report = run_grants_deadline_dry_run([_grants_item(iso)])
    assert report["stats"]["candidates_to_update"] == 1
    cand = report["candidates_to_update"][0]
    assert cand["after"]["fim_inscricao"] == iso
    assert is_grants_gov_record(cand["payload_after"])


def test_posted_only_not_update_candidate() -> None:
    report = run_grants_deadline_dry_run([_grants_item(None, posted="2026-01-01")])
    assert report["stats"]["candidates_to_update"] == 0
    assert report["stats"]["postedDate_only"] == 1


def test_no_closing_date_sem_prazo_kind() -> None:
    report = run_grants_deadline_dry_run(
        [_grants_item(None, explanation="No closing date — forecasted")]
    )
    assert report["stats"]["no_closing_date_explanation"] == 1
    entry = report["no_deadline"][0]
    assert entry["meta"]["sem_prazo_kind"] == "deadline_explicitly_absent"


def test_non_grants_rejected_in_dry_run() -> None:
    item = {
        "fonte": "BNDES",
        "link": "https://bndes.gov/1",
        "extras": {"closeDate": _future()},
    }
    report = run_grants_deadline_dry_run([item])
    assert report["stats"]["rejected"] == 1


def test_apply_aborts_without_controlled_apply_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", raising=False)
    monkeypatch.setenv("EDITALFINDER_ENABLE_DEADLINE_BACKFILL", "1")
    assert not controlled_apply_enabled()
    with pytest.raises(RuntimeError, match="ALLOW_CONTROLLED_APPLY"):
        apply_grants_candidates([{"payload_after": _grants_item(_future())}])


def test_apply_aborts_wrong_source() -> None:
    candidates = [
        {
            "fonte": "BNDES",
            "source_key": "bndes",
            "payload_after": {"fonte": "BNDES", "link": "https://bndes.gov/x"},
        }
    ]
    with pytest.raises(RuntimeError, match="Grants.gov"):
        validate_candidates_batch(candidates)


def test_merge_extras_preserves_existing() -> None:
    existing = {"agency": "DoD", "custom_field": "keep"}
    new = {"grants_close_date": _future(), "agency": "DoD Updated"}
    merged = merge_extras_for_apply(existing, new)
    assert merged["custom_field"] == "keep"
    assert merged["grants_close_date"] == new["grants_close_date"]
    assert merged["agency"] == "DoD Updated"


def test_resolve_prazo_preserves_valid_existing() -> None:
    existing_iso = _future(120)
    new_iso = _future(30)
    existing = {"prazo_envio": existing_iso, "fonte_recurso": "Grants.gov"}
    mapped = {"prazo_envio": new_iso, "fonte_recurso": "Grants.gov"}
    assert resolve_prazo_for_apply(existing, mapped, {}) == existing_iso


def test_large_batch_requires_confirmation() -> None:
    big = [{"fonte": "Grants.gov", "source_key": "grants_gov", "payload_after": _grants_item(_future())}] * (
        DEFAULT_MAX_APPLY_BATCH + 1
    )
    with pytest.raises(RuntimeError, match="confirm-large"):
        validate_candidates_batch(big, confirm_large=False)
    validate_candidates_batch(big, confirm_large=True)


def test_dry_run_report_contains_before_after() -> None:
    iso = _future()
    report = run_grants_deadline_dry_run([_grants_item(iso)])
    assert report["before_after"]
    row = report["before_after"][0]
    assert "before" in row and "after" in row
    assert row["after"]["fim_inscricao"] == iso


def test_classify_preserve_when_db_has_valid_different_prazo() -> None:
    existing_iso = _future(100)
    new_iso = _future(50)
    item = _grants_item(new_iso)
    db = {"prazo_envio": existing_iso, "fonte_recurso": "Grants.gov", "link": item["link"]}
    action, meta = classify_apply_action(item, db_record=db)
    assert action == "preserve"
    assert "nao_sobrescrever" in meta.get("reason", "")


def test_load_candidates_file_from_list(tmp_path: Path) -> None:
    cand = build_candidate_entry(
        _grants_item(_future()),
        action="update",
        meta={"deadline_backfill_status": "new_deadline_found"},
    )
    path = tmp_path / "candidates.json"
    path.write_text(json.dumps([cand]), encoding="utf-8")
    loaded = load_candidates_file(path)
    assert len(loaded) == 1
    assert loaded[0]["action"] == "update"


def test_validate_dry_run_report_missing(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="dry-run ausente"):
        validate_dry_run_report_recent(tmp_path)


@patch.dict(os.environ, {"EDITALFINDER_ALLOW_CONTROLLED_APPLY": "1", "EDITALFINDER_ENABLE_DEADLINE_BACKFILL": "1"})
def test_apply_grants_with_mocks(tmp_path: Path) -> None:
    assert controlled_apply_enabled()
    assert deadline_backfill_enabled()

    summary = tmp_path / "outputs" / "grants_deadline_apply" / "summary.md"
    summary.parent.mkdir(parents=True)
    summary.write_text("# dry-run ok", encoding="utf-8")

    iso = _future()
    item = _grants_item(iso)
    cand = build_candidate_entry(item, action="update", meta={"deadline_backfill_status": "new_deadline_found"})

    mock_loader = MagicMock()
    mock_loader.fetch_edital_by_link.return_value = {
        "fonte_recurso": "Grants.gov",
        "prazo_envio": None,
        "extras": {"legacy_key": "preserved"},
    }
    mock_loader.map_to_db_schema.return_value = (
        {"link": item["link"], "prazo_envio": iso, "fonte_recurso": "Grants.gov"},
        {"grants_close_date": iso},
    )
    mock_loader._merge_db_row.return_value = {
        "link": item["link"],
        "prazo_envio": iso,
        "fonte_recurso": "Grants.gov",
        "extras": {"legacy_key": "preserved", "grants_close_date": iso},
    }
    mock_loader.inserir_ou_atualizar_edital.return_value = ("ok", 42)

    with patch.dict(sys.modules, {"loader": mock_loader}):
        result = apply_grants_candidates(
            [cand],
            root=tmp_path,
            skip_dry_run_check=False,
        )
    assert result["ok"] == 1
    mock_loader.inserir_ou_atualizar_edital.assert_called_once()


@patch.dict(os.environ, {"EDITALFINDER_ALLOW_CONTROLLED_APPLY": "1", "EDITALFINDER_ENABLE_DEADLINE_BACKFILL": "1"})
def test_apply_grants_continues_without_organization_id(tmp_path: Path) -> None:
    """Apply não aborta quando lookup de organização está indisponível."""
    summary = tmp_path / "outputs" / "grants_deadline_apply" / "summary.md"
    summary.parent.mkdir(parents=True)
    summary.write_text("# dry-run ok", encoding="utf-8")

    iso = _future()
    item = _grants_item(iso)
    cand = build_candidate_entry(item, action="update", meta={"deadline_backfill_status": "new_deadline_found"})

    mock_loader = MagicMock()
    mock_loader.get_default_org_id.return_value = None
    mock_loader.fetch_edital_by_link.return_value = {
        "fonte_recurso": "Grants.gov",
        "prazo_envio": None,
        "extras": {"orgao_responsavel": "DoD"},
    }
    mock_loader.map_to_db_schema.return_value = (
        {
            "link": item["link"],
            "prazo_envio": iso,
            "fonte_recurso": "Grants.gov",
            "orgao_responsavel": "DoD",
        },
        {"grants_close_date": iso, "orgao_responsavel": "DoD"},
    )
    mock_loader._merge_db_row.return_value = {
        "link": item["link"],
        "prazo_envio": iso,
        "fonte_recurso": "Grants.gov",
        "orgao_responsavel": "DoD",
        "extras": {"orgao_responsavel": "DoD"},
    }
    mock_loader.inserir_ou_atualizar_edital.return_value = ("ok", 99)

    with patch.dict(sys.modules, {"loader": mock_loader}):
        result = apply_grants_candidates([cand], root=tmp_path, skip_dry_run_check=False)

    assert result["ok"] == 1
    assert "id_organizacao" not in mock_loader._merge_db_row.return_value
