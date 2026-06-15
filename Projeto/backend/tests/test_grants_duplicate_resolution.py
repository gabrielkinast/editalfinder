"""Testes da resolução de duplicatas Grants.gov (Backend 10.3B)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from grants_duplicate_resolution import (  # noqa: E402
    apply_hide_candidates,
    build_curadoria_patch,
    build_duplicate_groups,
    build_duplicate_targets_from_groups,
    build_hide_candidates,
    group_grants_by_opportunity_id,
    merge_curadoria_front,
    pick_canonical_record,
)

DETAIL = "https://www.grants.gov/search-results-detail"


def _target(id_edital, dup_of, opp="500", **kw):
    return {
        "id_edital": id_edital,
        "duplicate_of_id_edital": dup_of,
        "new_link": f"{DETAIL}/{opp}",
        "opportunity_id": opp,
        "titulo": kw.get("titulo", "Opp"),
        **kw,
    }


def _grants_rec(id_edital, link="", extras=None, fonte="Grants.gov"):
    return {
        "id_edital": id_edital,
        "fonte": fonte,
        "link": link,
        "extras": extras or {"source_variant": "simpler_grants_gov"},
    }


class FakeSupabase:
    """Fake mínimo que suporta select(...).eq(...).limit(...).execute() e update(...).eq(...).execute()."""

    def __init__(self, store):
        self.store = store  # id_edital -> row dict
        self.updates = []  # (id_edital, payload)
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


# --------------------------------------------------------------------------
# dry-run / build_hide_candidates
# --------------------------------------------------------------------------

def test_dry_run_creates_candidates_from_targets():
    res = build_hide_candidates([_target(2, 1), _target(3, 1, opp="600")])
    assert res["stats"]["candidates_to_hide"] == 2
    assert res["stats"]["invalid_duplicates"] == 0
    assert all("curadoria_patch" in c for c in res["candidates_to_hide"])


def test_dry_run_ignores_item_without_id_edital():
    res = build_hide_candidates([{"duplicate_of_id_edital": 1, "new_link": f"{DETAIL}/500"}])
    assert res["stats"]["candidates_to_hide"] == 0
    assert res["invalid_duplicates"][0]["reason"] == "sem_id_edital"


def test_dry_run_invalidates_without_canonical_id():
    res = build_hide_candidates([{"id_edital": 2, "new_link": f"{DETAIL}/500"}])
    assert res["invalid_duplicates"][0]["reason"] == "sem_duplicate_of_id_edital"


def test_dry_run_invalidates_bad_canonical_link():
    res = build_hide_candidates([{"id_edital": 2, "duplicate_of_id_edital": 1, "new_link": "https://x.com/a"}])
    assert res["invalid_duplicates"][0]["reason"] == "canonical_link_invalido"


def test_dry_run_invalidates_self_reference():
    res = build_hide_candidates([_target(1, 1)])
    assert res["invalid_duplicates"][0]["reason"] == "duplicado_e_o_proprio_canonico"


def test_dry_run_invalidates_canonical_not_grants():
    records = {
        1: {"id_edital": 1, "fonte": "BNDES", "link": "https://bndes.gov.br/x"},
        2: _grants_rec(2, link=f"{DETAIL}/500"),
    }
    res = build_hide_candidates([_target(2, 1)], records_by_id=records)
    assert res["invalid_duplicates"][0]["reason"] == "canonico_nao_e_grants"


def test_dry_run_valid_with_records():
    records = {
        1: _grants_rec(1, link=f"{DETAIL}/500"),
        2: _grants_rec(2, link="https://simpler.grants.gov/opportunity/500"),
    }
    res = build_hide_candidates([_target(2, 1)], records_by_id=records)
    assert res["stats"]["candidates_to_hide"] == 1
    assert res["stats"]["distinct_canonical_records"] == 1


def test_dry_run_already_hidden_goes_to_already_hidden():
    hidden_extras = {"curadoria_front": {"hidden_duplicate": True}}
    records = {
        1: _grants_rec(1, link=f"{DETAIL}/500"),
        2: _grants_rec(2, link="https://simpler.grants.gov/opportunity/500", extras=hidden_extras),
    }
    res = build_hide_candidates([_target(2, 1)], records_by_id=records)
    assert res["stats"]["already_hidden"] == 1
    assert res["stats"]["candidates_to_hide"] == 0


# --------------------------------------------------------------------------
# merge / curadoria
# --------------------------------------------------------------------------

def test_merge_preserves_existing_extras():
    existing = {
        "prazo_envio": "2026-01-01",
        "curadoria_front": {"manual_flag": "keep", "nota": "x"},
        "outro": 1,
    }
    patch = build_curadoria_patch(duplicate_of_id_edital=1, canonical_link=f"{DETAIL}/500", now="2026-01-01T00:00:00Z")
    merged = merge_curadoria_front(existing, patch)
    assert merged["prazo_envio"] == "2026-01-01"
    assert merged["outro"] == 1
    assert merged["curadoria_front"]["manual_flag"] == "keep"
    assert merged["curadoria_front"]["nota"] == "x"
    assert merged["curadoria_front"]["hidden_duplicate"] is True
    # não muta o original
    assert "hidden_duplicate" not in existing["curadoria_front"]


def test_curadoria_patch_fields():
    patch = build_curadoria_patch(duplicate_of_id_edital=1126, canonical_link=f"{DETAIL}/362201", now="2026-06-09T00:00:00Z")
    assert patch["hidden_duplicate"] is True
    assert patch["visibility"] == "hidden_duplicate"
    assert patch["duplicate_of_id_edital"] == 1126
    assert patch["duplicate_reason"] == "same_grants_opportunity_id"
    assert patch["resolved_by"] == "backend_10.3b"
    assert patch["canonical_link"] == f"{DETAIL}/362201"


# --------------------------------------------------------------------------
# apply — proteções
# --------------------------------------------------------------------------

def test_apply_aborts_without_any_flag(monkeypatch):
    monkeypatch.delenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", raising=False)
    monkeypatch.delenv("EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION", raising=False)
    with pytest.raises(RuntimeError):
        apply_hide_candidates([_target(2, 1)], supabase_client=MagicMock())


def test_apply_aborts_without_duplicate_flag(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.delenv("EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION", raising=False)
    with pytest.raises(RuntimeError):
        apply_hide_candidates([_target(2, 1)], supabase_client=MagicMock())


def test_apply_large_batch_requires_confirm(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION", "1")
    cands = [_target(i, 1, opp=str(i)) for i in range(2, 105)]
    with pytest.raises(RuntimeError):
        apply_hide_candidates(cands, confirm_large=False, supabase_client=MagicMock())


# --------------------------------------------------------------------------
# apply — comportamento
# --------------------------------------------------------------------------

def _enable(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_DUPLICATE_RESOLUTION", "1")


def test_apply_updates_only_extras(monkeypatch):
    _enable(monkeypatch)
    store = {
        1: _grants_rec(1, link=f"{DETAIL}/500"),
        2: _grants_rec(2, link="https://simpler.grants.gov/opportunity/500", extras={"prazo_envio": "2026-01-01"}),
    }
    fake = FakeSupabase(store)
    res = apply_hide_candidates([_target(2, 1)], supabase_client=fake)
    assert res["ok"] == 1
    assert len(fake.updates) == 1
    upd_id, payload = fake.updates[0]
    assert upd_id == 2
    assert set(payload.keys()) == {"extras"}


def test_apply_does_not_touch_link_or_deadline(monkeypatch):
    _enable(monkeypatch)
    store = {2: _grants_rec(2, link="https://simpler.grants.gov/opportunity/500", extras={"prazo_envio": "2026-01-01", "fim_inscricao": "2026-02-01"})}
    fake = FakeSupabase(store)
    apply_hide_candidates([_target(2, 1)], supabase_client=fake)
    _, payload = fake.updates[0]
    assert "link" not in payload
    assert "prazo_envio" not in payload
    assert "titulo" not in payload
    # extras preservou prazo dentro do JSON
    assert payload["extras"]["prazo_envio"] == "2026-01-01"
    assert payload["extras"]["fim_inscricao"] == "2026-02-01"
    assert payload["extras"]["curadoria_front"]["hidden_duplicate"] is True


def test_apply_canonical_record_never_modified(monkeypatch):
    _enable(monkeypatch)
    store = {
        1: _grants_rec(1, link=f"{DETAIL}/500"),
        2: _grants_rec(2, link="https://simpler.grants.gov/opportunity/500"),
    }
    fake = FakeSupabase(store)
    apply_hide_candidates([_target(2, 1)], supabase_client=fake)
    touched_ids = {u[0] for u in fake.updates}
    assert touched_ids == {2}
    assert 1 not in touched_ids


def test_apply_is_idempotent(monkeypatch):
    _enable(monkeypatch)
    store = {2: _grants_rec(2, link="https://simpler.grants.gov/opportunity/500", extras={})}
    fake = FakeSupabase(store)
    r1 = apply_hide_candidates([_target(2, 1)], supabase_client=fake)
    r2 = apply_hide_candidates([_target(2, 1)], supabase_client=fake)
    assert r1["ok"] == 1
    assert r2["ok"] == 0
    assert r2["already_hidden"] == 1
    # apenas uma escrita real
    assert len(fake.updates) == 1


# --------------------------------------------------------------------------
# agrupamento / canônico
# --------------------------------------------------------------------------

def test_pick_canonical_prefers_canonical_link():
    group = [
        _grants_rec(10, link="https://simpler.grants.gov/opportunity/500"),
        _grants_rec(11, link=f"{DETAIL}/500"),
    ]
    canon = pick_canonical_record(group)
    assert canon["id_edital"] == 11


def test_pick_canonical_prefers_better_deadline():
    group = [
        {**_grants_rec(20, link=f"{DETAIL}/600"), "prazo_envio": "2025-01-01"},
        {**_grants_rec(21, link=f"{DETAIL}/600"), "prazo_envio": "2027-06-01"},
    ]
    canon = pick_canonical_record(group)
    assert canon["id_edital"] == 21


def test_group_grants_by_opportunity_id_only_multi():
    records = [
        _grants_rec(1, link=f"{DETAIL}/100"),
        _grants_rec(2, link="https://simpler.grants.gov/opportunity/100"),
        _grants_rec(3, link=f"{DETAIL}/200"),
    ]
    groups = group_grants_by_opportunity_id(records)
    assert list(groups.keys()) == ["100"]
    assert len(groups["100"]) == 2


def test_build_duplicate_targets_from_groups():
    records = [
        _grants_rec(1, link=f"{DETAIL}/500"),
        _grants_rec(2, link="https://simpler.grants.gov/opportunity/500"),
    ]
    groups = group_grants_by_opportunity_id(records)
    targets = build_duplicate_targets_from_groups(groups)
    assert len(targets) == 1
    assert targets[0]["id_edital"] == 2
    assert targets[0]["duplicate_of_id_edital"] == 1


def test_build_duplicate_groups_from_targets():
    targets = [_target(2, 1), _target(3, 1, opp="600")]
    groups = build_duplicate_groups(targets)
    assert len(groups) == 2
    by_opp = {g["opportunity_id"]: g for g in groups}
    assert by_opp["500"]["canonical_id_edital"] == 1
    assert 2 in by_opp["500"]["duplicate_ids"]


def test_idempotent_patch_skips_second_apply(monkeypatch):
    _enable(monkeypatch)
    patch = build_curadoria_patch(duplicate_of_id_edital=1, canonical_link=f"{DETAIL}/500", now="2026-01-01T00:00:00Z")
    store = {
        2: _grants_rec(
            2,
            link="https://simpler.grants.gov/opportunity/500",
            extras={"curadoria_front": {**patch}},
        ),
    }
    fake = FakeSupabase(store)
    r2 = apply_hide_candidates([_target(2, 1)], supabase_client=fake)
    assert r2["already_hidden"] == 1
    assert len(fake.updates) == 0
