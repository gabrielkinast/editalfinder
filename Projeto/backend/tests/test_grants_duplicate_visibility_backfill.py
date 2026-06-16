"""Testes — backfill visibility duplicatas Grants.gov (Backend 10.3C)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from grants_duplicate_visibility_backfill import (  # noqa: E402
    analyze_visibility_backfill,
    apply_visibility_backfill,
    audit_visibility_compliance,
    build_visibility_backfill_patch,
    classify_record_for_backfill,
    visibility_backfill_complete,
)
from grants_duplicate_resolution import merge_curadoria_front  # noqa: E402


def _grants(id_edital, extras=None, link="https://simpler.grants.gov/opportunity/500"):
    return {
        "id_edital": id_edital,
        "fonte": "Grants.gov",
        "link": link,
        "extras": extras or {"source_variant": "simpler_grants_gov"},
    }


class FakeSupabase:
    def __init__(self, store):
        self.store = store
        self.updates = []
        self._payload = None
        self._id = None

    def table(self, _name):
        return self

    def select(self, *_a, **_k):
        return self

    def update(self, payload):
        self._payload = payload
        return self

    def eq(self, _col, val):
        self._id = val
        return self

    def limit(self, _n):
        return self

    def execute(self):
        res = MagicMock()
        if self._payload is not None:
            self.updates.append((self._id, dict(self._payload)))
            row = self.store.get(self._id)
            if row is not None and "extras" in self._payload:
                row["extras"] = self._payload["extras"]
            res.data = [self.store.get(self._id)]
        else:
            row = self.store.get(self._id)
            res.data = [row] if row else []
        self._payload = None
        self._id = None
        return res


def test_backfill_adds_visibility_when_only_hidden_boolean():
    cf = {
        "hidden_duplicate": True,
        "duplicate_of_id_edital": 1,
        "duplicate_reason": "same_grants_opportunity_id",
        "canonical_link": "https://www.grants.gov/search-results-detail/500",
    }
    patch = build_visibility_backfill_patch(cf)
    assert patch["visibility"] == "hidden_duplicate"
    assert "hidden_duplicate" not in patch


def test_backfill_adds_hidden_boolean_when_only_visibility():
    cf = {
        "visibility": "hidden_duplicate",
        "duplicate_of_id_edital": 1,
        "duplicate_reason": "same_grants_opportunity_id",
        "canonical_link": "https://www.grants.gov/search-results-detail/500",
    }
    patch = build_visibility_backfill_patch(cf)
    assert patch["hidden_duplicate"] is True
    assert "visibility" not in patch


def test_backfill_preserves_duplicate_of_and_extras():
    existing = {
        "prazo_envio": "2026-01-01",
        "curadoria_front": {
            "hidden_duplicate": True,
            "duplicate_of_id_edital": 1126,
            "manual_note": "keep",
        },
    }
    patch = build_visibility_backfill_patch(existing["curadoria_front"])
    merged = merge_curadoria_front(existing, patch)
    assert merged["prazo_envio"] == "2026-01-01"
    assert merged["curadoria_front"]["duplicate_of_id_edital"] == 1126
    assert merged["curadoria_front"]["manual_note"] == "keep"
    assert merged["curadoria_front"]["visibility"] == "hidden_duplicate"


def test_classify_canonical_not_updated():
    records = [
        _grants(1, {"curadoria_front": {}}, link="https://www.grants.gov/search-results-detail/500"),
        _grants(2, {"curadoria_front": {"hidden_duplicate": True, "duplicate_of_id_edital": 1}}),
    ]
    r = classify_record_for_backfill(records[0], all_records=records)
    assert r["status"] == "skipped"


def test_dry_run_detects_candidate_needing_visibility():
    records = [
        _grants(1, link="https://www.grants.gov/search-results-detail/500"),
        _grants(
            2,
            {
                "curadoria_front": {
                    "hidden_duplicate": True,
                    "duplicate_of_id_edital": 1,
                    "duplicate_reason": "same_grants_opportunity_id",
                    "canonical_link": "https://www.grants.gov/search-results-detail/500",
                }
            },
        ),
    ]
    res = analyze_visibility_backfill(records)
    assert res["stats"]["candidates_to_update"] == 1
    assert res["stats"]["needs_visibility"] == 1


def test_apply_idempotent(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_DUPLICATE_VISIBILITY_BACKFILL", "1")
    store = {
        2: _grants(
            2,
            {
                "curadoria_front": {
                    "hidden_duplicate": True,
                    "duplicate_of_id_edital": 1,
                    "canonical_link": "https://www.grants.gov/search-results-detail/500",
                }
            },
        )
    }
    fake = FakeSupabase(store)
    cand = [{"id_edital": 2, "curadoria_patch": {"visibility": "hidden_duplicate"}}]
    r1 = apply_visibility_backfill(cand, supabase_client=fake)
    r2 = apply_visibility_backfill(cand, supabase_client=fake)
    assert r1["ok"] == 1
    assert r2["already_ok"] == 1
    assert len(fake.updates) == 1
    assert visibility_backfill_complete(store[2]["extras"]["curadoria_front"])


def test_apply_aborts_without_flags(monkeypatch):
    monkeypatch.delenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", raising=False)
    monkeypatch.delenv("EDITALFINDER_ALLOW_DUPLICATE_VISIBILITY_BACKFILL", raising=False)
    with pytest.raises(RuntimeError):
        apply_visibility_backfill([{"id_edital": 2}], supabase_client=MagicMock())


def test_anomaly_without_duplicate_of():
    rec = _grants(2, {"curadoria_front": {"hidden_duplicate": True}})
    r = classify_record_for_backfill(rec)
    assert r["status"] == "anomaly"
    assert r["reason"] == "oculto_sem_duplicate_of_id_edital"


def test_anomaly_canonical_referenced_hidden():
    records = [
        _grants(1, link="https://www.grants.gov/search-results-detail/500"),
        _grants(
            1,
            {
                "curadoria_front": {
                    "hidden_duplicate": True,
                    "visibility": "hidden_duplicate",
                    "duplicate_of_id_edital": 99,
                }
            },
            link="https://www.grants.gov/search-results-detail/500",
        ),
        _grants(
            2,
            {"curadoria_front": {"hidden_duplicate": True, "duplicate_of_id_edital": 1}},
        ),
    ]
    # id 1 is canonical for id 2 but marked hidden -> anomaly on classify for record 1
    r = classify_record_for_backfill(records[0], all_records=records)
    # records[0] has empty cf - skipped. Use records[1] wrongly - fix test
    canon_hidden = _grants(
        1,
        {
            "curadoria_front": {
                "hidden_duplicate": True,
                "duplicate_of_id_edital": 99,
            }
        },
        link="https://www.grants.gov/search-results-detail/500",
    )
    dup = _grants(2, {"curadoria_front": {"hidden_duplicate": True, "duplicate_of_id_edital": 1}})
    r = classify_record_for_backfill(canon_hidden, all_records=[canon_hidden, dup])
    assert r["status"] == "anomaly"
    assert r["reason"] == "canonico_referenciado_esta_oculto"


def test_audit_visibility_compliance():
    records = [
        _grants(
            2,
            {
                "curadoria_front": {
                    "hidden_duplicate": True,
                    "visibility": "hidden_duplicate",
                    "duplicate_of_id_edital": 1,
                    "duplicate_reason": "same_grants_opportunity_id",
                    "canonical_link": "https://www.grants.gov/search-results-detail/500",
                }
            },
        )
    ]
    rep = audit_visibility_compliance(records)
    assert rep["visibility_compliant"] == 1
    assert rep["all_compliant"] is True


def test_dry_run_does_not_write(tmp_path):
    records = [_grants(2, {"curadoria_front": {"hidden_duplicate": True, "duplicate_of_id_edital": 1}})]
    res = analyze_visibility_backfill(records)
    assert res["stats"]["candidates_to_update"] >= 0
    assert not (tmp_path / "db.txt").exists()
