"""Testes apply controlado DOE_ARPAE (Backend 10.2C)."""
from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from deadline_backfill import controlled_apply_enabled, deadline_backfill_enabled, extract_source_deadline_fields  # noqa: E402
from doe_arpae_controlled_apply import (  # noqa: E402
    DEFAULT_MAX_APPLY_BATCH,
    apply_doe_arpae_candidates,
    build_candidate_entry,
    classify_apply_action,
    is_doe_arpae_record,
    load_candidates_file,
    merge_extras_for_apply,
    resolve_prazo_for_apply,
    run_doe_arpae_deadline_dry_run,
    validate_candidates_batch,
    validate_dry_run_report_recent,
)
from doe_arpae_recrawl import enrich_doe_arpae_recrawl_item  # noqa: E402


def _future(days: int = 400) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


def _us_date(iso: str) -> str:
    y, m, d = iso.split("-")
    return f"{int(m)}/{int(d)}/{y}"


def _doe_item(
    *,
    full_app: str | None = None,
    concept: str | None = None,
    nofo_desc: str | None = None,
    fonte: str = "DOE_ARPAE",
) -> dict:
    desc = nofo_desc or ""
    if full_app:
        desc += f" Full Application Deadline: {_us_date(full_app)}"
    if concept:
        desc += f" Concept Paper Deadline: {_us_date(concept)}"
    item = {
        "titulo": "DE-FOA-TEST",
        "descricao": desc.strip(),
        "link": f"https://arpa-e-foa.energy.gov/Default.aspx#FoaId{full_app or concept or 'x'}",
        "fonte": fonte,
        "extras": {"orgao_responsavel": "ARPA-E"},
    }
    return enrich_doe_arpae_recrawl_item(item)


def test_full_application_beats_concept_paper() -> None:
    full = _future(500)
    concept = _future(450)
    item = _doe_item(full_app=full, concept=concept)
    out = extract_source_deadline_fields(item)
    assert out["prazo_envio"] == full


def test_concept_paper_only_generates_candidate() -> None:
    concept = _future(450)
    item = _doe_item(concept=concept)
    report = run_doe_arpae_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] == 1


def test_nofo_two_dates_candidate() -> None:
    item = _doe_item(
        nofo_desc="DE-FOA-0003556 Notice Of Funding Opportunity (NOFO) 2/19/2027 09:30 AM ET 3/5/2028 09:30 AM ET"
    )
    out = extract_source_deadline_fields(item)
    assert out["prazo_envio"] == "2028-03-05"
    report = run_doe_arpae_deadline_dry_run([item])
    assert report["stats"]["candidates_to_update"] == 1


def test_nofo_tbd_no_prazo() -> None:
    item = _doe_item(nofo_desc="Notice Of Funding Opportunity (NOFO) 2/14/2027 09:30 AM ET TBD")
    out = extract_source_deadline_fields(item)
    assert out.get("prazo_envio") is None
    assert out["sem_prazo_kind"] == "deadline_tbd"
    report = run_doe_arpae_deadline_dry_run([item])
    assert report["stats"]["no_deadline"] >= 1


def test_publication_date_rejected() -> None:
    item = enrich_doe_arpae_recrawl_item(
        {
            "fonte": "DOE_ARPAE",
            "data_publicacao": "2026-05-09",
            "descricao": "Published on May 9, 2026. Official portal record.",
            "link": "https://arpa-e-foa.energy.gov/x",
        }
    )
    out = extract_source_deadline_fields(item)
    assert out.get("prazo_envio") is None


def test_dry_run_before_after() -> None:
    item = _doe_item(full_app=_future())
    report = run_doe_arpae_deadline_dry_run([item])
    assert report["before_after"]
    assert report["before_after"][0]["after"]["fim_inscricao"]


def test_non_doe_rejected() -> None:
    item = {"fonte": "Grants.gov", "link": "https://grants.gov/1"}
    report = run_doe_arpae_deadline_dry_run([item])
    assert report["stats"]["rejected"] == 1


def test_apply_aborts_without_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", raising=False)
    monkeypatch.setenv("EDITALFINDER_ENABLE_DEADLINE_BACKFILL", "1")
    with pytest.raises(RuntimeError, match="ALLOW_CONTROLLED_APPLY"):
        apply_doe_arpae_candidates([{"payload_after": _doe_item(full_app=_future())}])


def test_apply_aborts_wrong_source() -> None:
    with pytest.raises(RuntimeError, match="DOE_ARPAE"):
        validate_candidates_batch(
            [{"fonte": "Grants.gov", "payload_after": {"fonte": "Grants.gov", "link": "x"}}]
        )


def test_merge_extras_preserves_existing() -> None:
    merged = merge_extras_for_apply(
        {"legacy": "keep", "orgao_responsavel": "ARPA-E"},
        {"full_application_deadline": _future()},
    )
    assert merged["legacy"] == "keep"
    assert merged["full_application_deadline"] == _future()


def test_resolve_prazo_preserves_valid_existing() -> None:
    existing_iso = _future(500)
    new_iso = _future(300)
    existing = {"prazo_envio": existing_iso, "fonte_recurso": "DOE_ARPAE"}
    mapped = {"prazo_envio": new_iso, "fonte_recurso": "DOE_ARPAE"}
    assert resolve_prazo_for_apply(existing, mapped, {}) == existing_iso


def test_large_batch_requires_confirmation() -> None:
    cand = build_candidate_entry(
        _doe_item(full_app=_future()),
        action="update",
        meta={"deadline_backfill_status": "new_deadline_found"},
    )
    big = [cand] * (DEFAULT_MAX_APPLY_BATCH + 1)
    with pytest.raises(RuntimeError, match="confirm-large"):
        validate_candidates_batch(big, confirm_large=False)


def test_classify_preserve_different_valid_prazo() -> None:
    existing_iso = _future(500)
    new_iso = _future(300)
    item = _doe_item(full_app=new_iso)
    db = {"prazo_envio": existing_iso, "fonte_recurso": "DOE_ARPAE", "link": item["link"]}
    action, meta = classify_apply_action(item, db_record=db)
    assert action == "preserve"


def test_is_doe_arpae_record() -> None:
    assert is_doe_arpae_record({"fonte": "DOE_ARPAE"})
    assert is_doe_arpae_record({"fonte_recurso": "ARPA-E"})
    assert not is_doe_arpae_record({"fonte": "Grants.gov"})


def test_validate_dry_run_report_missing(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="dry-run ausente"):
        validate_dry_run_report_recent(tmp_path)


@patch.dict(os.environ, {"EDITALFINDER_ALLOW_CONTROLLED_APPLY": "1", "EDITALFINDER_ENABLE_DEADLINE_BACKFILL": "1"})
def test_apply_doe_with_mocks(tmp_path: Path) -> None:
    assert controlled_apply_enabled()
    assert deadline_backfill_enabled()

    summary = tmp_path / "outputs" / "doe_arpae_deadline_apply" / "summary.md"
    summary.parent.mkdir(parents=True)
    summary.write_text("# dry-run ok", encoding="utf-8")

    iso = _future()
    item = _doe_item(full_app=iso)
    cand = build_candidate_entry(item, action="update", meta={"deadline_backfill_status": "new_deadline_found"})

    mock_loader = MagicMock()
    mock_loader.fetch_edital_by_link.return_value = {
        "fonte_recurso": "DOE_ARPAE",
        "prazo_envio": None,
        "extras": {"legacy_key": "preserved"},
    }
    mock_loader.map_to_db_schema.return_value = (
        {"link": item["link"], "prazo_envio": iso, "fonte_recurso": "DOE_ARPAE"},
        {"full_application_deadline": iso},
    )
    mock_loader._merge_db_row.return_value = {
        "link": item["link"],
        "prazo_envio": iso,
        "fonte_recurso": "DOE_ARPAE",
        "extras": {"legacy_key": "preserved", "full_application_deadline": iso},
    }
    mock_loader.inserir_ou_atualizar_edital.return_value = ("ok", 77)

    with patch.dict(sys.modules, {"loader": mock_loader}):
        result = apply_doe_arpae_candidates([cand], root=tmp_path, skip_dry_run_check=False)

    assert result["ok"] == 1


def test_load_candidates_file(tmp_path: Path) -> None:
    cand = build_candidate_entry(
        _doe_item(full_app=_future()),
        action="update",
        meta={},
    )
    path = tmp_path / "candidates.json"
    path.write_text(json.dumps([cand]), encoding="utf-8")
    assert len(load_candidates_file(path)) == 1
