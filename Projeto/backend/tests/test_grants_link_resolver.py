"""Testes do canonicalizador de links Grants.gov (Backend 10.3A)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from grants_link_apply import (  # noqa: E402
    apply_grants_link_candidates,
    validate_link_fix_candidate,
)
from grants_link_resolver import (  # noqa: E402
    audit_grants_links,
    build_link_fix_candidates,
    is_safe_grants_link,
    normalize_grants_gov_link,
)

DETAIL = "https://www.grants.gov/search-results-detail"
SEARCH = "https://www.grants.gov/search-grants"


def _grants(link="", **extras):
    return {
        "fonte": "Grants.gov",
        "link": link,
        "extras": {"source_variant": "simpler_grants_gov", **extras},
    }


# --------------------------------------------------------------------------
# Resolver — regras centrais
# --------------------------------------------------------------------------

def test_page_not_found_with_numeric_id_becomes_detail():
    rec = _grants("https://www.grants.gov/page-not-found", opportunity_id="360262")
    res = normalize_grants_gov_link(rec)
    assert res["canonical_link"] == f"{DETAIL}/360262"
    assert res["link_status"] == "canonical_detail"
    assert res["old_link_invalid"] is True


def test_empty_link_with_numeric_id_becomes_detail():
    rec = _grants("", opportunity_id="12345")
    res = normalize_grants_gov_link(rec)
    assert res["canonical_link"] == f"{DETAIL}/12345"
    assert res["link_status"] == "canonical_detail"


def test_canonical_without_www_is_normalized_with_www():
    rec = _grants("https://grants.gov/search-results-detail/777")
    res = normalize_grants_gov_link(rec)
    assert res["canonical_link"] == f"{DETAIL}/777"
    assert res["link_status"] == "canonical_detail"


def test_canonical_with_www_is_preserved():
    rec = _grants(f"{DETAIL}/888")
    res = normalize_grants_gov_link(rec)
    assert res["canonical_link"] == f"{DETAIL}/888"
    assert res["link_status"] == "canonical_detail"


def test_opportunity_number_without_id_search_fallback():
    rec = _grants("https://www.grants.gov/page-not-found", opportunity_number="DE-FOA-0003329")
    res = normalize_grants_gov_link(rec)
    assert res["link_status"] == "search_fallback"
    assert "search-grants?keywords=DE-FOA-0003329" in res["canonical_link"]


def test_search_fallback_encodes_keywords():
    rec = _grants("", opportunity_number="ABC 123/45")
    res = normalize_grants_gov_link(rec)
    assert res["link_status"] == "search_fallback"
    # espaço e barra precisam estar encoded
    assert " " not in res["canonical_link"]
    assert res["canonical_link"].startswith(f"{SEARCH}?keywords=")


def test_no_id_no_number_search_grants_missing():
    rec = _grants("https://www.grants.gov/page-not-found")
    res = normalize_grants_gov_link(rec)
    assert res["canonical_link"] == SEARCH
    assert res["link_status"] == "missing"


def test_rejects_javascript_scheme():
    rec = _grants("javascript:alert(1)", opportunity_number="FON-9")
    res = normalize_grants_gov_link(rec)
    assert not res["canonical_link"].lower().startswith("javascript:")
    assert is_safe_grants_link(res["canonical_link"])
    assert res["old_link_invalid"] is True


def test_rejects_external_domain():
    rec = _grants("https://evil.example.com/search-results-detail/1")
    res = normalize_grants_gov_link(rec)
    # domínio externo nunca preservado; sem id/number cai para search-grants
    assert res["canonical_link"] == SEARCH
    assert "example.com" not in res["canonical_link"]
    assert res["old_link_invalid"] is True


def test_funding_opportunity_number_in_extras_recognized():
    rec = {"fonte": "Grants.gov", "link": "", "extras": {"fundingOpportunityNumber": "DE-FOA-1"}}
    res = normalize_grants_gov_link(rec)
    assert res["link_status"] == "search_fallback"
    assert res["opportunity_number"] == "DE-FOA-1"


def test_opportunity_id_in_extras_recognized():
    rec = {"fonte": "Grants.gov", "link": "", "extras": {"opportunityId": "555"}}
    res = normalize_grants_gov_link(rec)
    assert res["canonical_link"] == f"{DETAIL}/555"
    assert res["opportunity_id"] == "555"


def test_non_numeric_id_not_used_as_opportunity_id():
    rec = {"fonte": "Grants.gov", "link": "", "id": "abc-uuid-not-numeric"}
    res = normalize_grants_gov_link(rec)
    assert res["opportunity_id"] == ""
    assert res["link_status"] in ("missing",)


def test_uuid_simpler_link_without_numeric_falls_back():
    rec = _grants("https://simpler.grants.gov/opportunity/3b1f0c2e-1111-2222-3333-444455556666")
    res = normalize_grants_gov_link(rec)
    assert res["link_status"] == "missing"
    assert res["canonical_link"] == SEARCH


def test_simpler_numeric_link_extracts_id():
    rec = _grants("https://simpler.grants.gov/opportunity/360262")
    res = normalize_grants_gov_link(rec)
    assert res["canonical_link"] == f"{DETAIL}/360262"


def test_resolver_returns_readable_reason():
    rec = _grants("", opportunity_id="1")
    res = normalize_grants_gov_link(rec)
    assert isinstance(res["reason"], str) and res["reason"]


def test_not_grants_record_is_invalid():
    rec = {"fonte": "BNDES", "link": "https://bndes.gov.br/x"}
    res = normalize_grants_gov_link(rec)
    assert res["link_status"] == "invalid"
    assert res["canonical_link"] is None


# --------------------------------------------------------------------------
# Auditoria e dry-run
# --------------------------------------------------------------------------

def test_audit_counts_buckets():
    records = [
        _grants("https://www.grants.gov/page-not-found", opportunity_id="1"),
        _grants(f"{DETAIL}/2"),
        _grants("", opportunity_number="FON-3"),
        _grants("https://www.grants.gov/page-not-found"),
    ]
    audit = audit_grants_links(records)
    s = audit["stats"]
    assert s["total_grants"] == 4
    assert s["already_valid"] == 1
    assert s["page_not_found"] >= 2
    assert s["candidates_to_update"] >= 2


def test_dry_run_generates_candidates_to_update():
    records = [
        _grants("https://www.grants.gov/page-not-found", opportunity_id="999"),
        _grants(f"{DETAIL}/2"),
    ]
    result = build_link_fix_candidates(records)
    assert result["stats"]["candidates_to_update"] == 1
    cand = result["candidates_to_update"][0]
    assert cand["new_link"] == f"{DETAIL}/999"
    assert cand["old_link"].endswith("page-not-found")


def test_dry_run_detects_duplicate_targets():
    # Dois registros distintos resolvem para o mesmo canônico (mesma opp).
    a = _grants("https://simpler.grants.gov/opportunity/500")
    a["id_edital"] = 1
    b = _grants("https://www.grants.gov/web/grants/view-opportunity.html?oppId=500")
    b["id_edital"] = 2
    result = build_link_fix_candidates([a, b])
    assert result["stats"]["candidates_to_update"] == 1
    assert result["stats"]["duplicate_targets"] == 1
    dup = result["duplicate_targets"][0]
    assert dup["new_link"] == f"{DETAIL}/500"
    assert dup.get("duplicate_of_id_edital") == 1


def test_apply_skips_duplicate_target_in_batch(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_LINK_FIX", "1")
    client = MagicMock()
    cands = [
        {"id_edital": 1, "fonte": "Grants.gov", "old_link": "https://simpler.grants.gov/opportunity/500",
         "new_link": f"{DETAIL}/500"},
        {"id_edital": 2, "fonte": "Grants.gov", "old_link": "https://www.grants.gov/web/grants/view-opportunity.html?oppId=500",
         "new_link": f"{DETAIL}/500"},
    ]
    res = apply_grants_link_candidates(cands, supabase_client=client)
    assert res["ok"] == 1
    assert res["duplicate"] == 1
    assert res["errors"] == 0


def test_apply_unique_violation_counts_as_duplicate(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_LINK_FIX", "1")
    client = MagicMock()
    client.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
        'duplicate key value violates unique constraint "edital_link_key" (23505)'
    )
    res = apply_grants_link_candidates(
        [{"id_edital": 7, "fonte": "Grants.gov", "old_link": "x", "new_link": f"{DETAIL}/7"}],
        supabase_client=client,
    )
    assert res["errors"] == 0
    assert res["duplicate"] == 1


# --------------------------------------------------------------------------
# Apply controlado — proteções
# --------------------------------------------------------------------------

def test_apply_aborts_without_flags(monkeypatch):
    monkeypatch.delenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", raising=False)
    monkeypatch.delenv("EDITALFINDER_ALLOW_LINK_FIX", raising=False)
    with pytest.raises(RuntimeError):
        apply_grants_link_candidates([{"id_edital": 1, "new_link": f"{DETAIL}/1"}])


def test_apply_aborts_without_link_fix_flag(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.delenv("EDITALFINDER_ALLOW_LINK_FIX", raising=False)
    with pytest.raises(RuntimeError):
        apply_grants_link_candidates([{"id_edital": 1, "new_link": f"{DETAIL}/1"}])


def test_apply_rejects_non_grants_source(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_LINK_FIX", "1")
    client = MagicMock()
    with pytest.raises(RuntimeError):
        apply_grants_link_candidates(
            [{"id_edital": 1, "fonte": "BNDES", "new_link": f"{DETAIL}/1"}],
            supabase_client=client,
        )
    client.table.assert_not_called()


def test_apply_skips_link_outside_grants(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_LINK_FIX", "1")
    client = MagicMock()
    res = apply_grants_link_candidates(
        [{"id_edital": 1, "fonte": "Grants.gov", "old_link": "x", "new_link": "https://evil.com/x"}],
        supabase_client=client,
    )
    assert res["ok"] == 0
    assert res["skipped"] == 1
    client.table.return_value.update.assert_not_called()


def test_apply_skips_page_not_found_new_link(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_LINK_FIX", "1")
    client = MagicMock()
    res = apply_grants_link_candidates(
        [{"id_edital": 1, "fonte": "Grants.gov", "old_link": "x",
          "new_link": "https://www.grants.gov/page-not-found"}],
        supabase_client=client,
    )
    assert res["skipped"] == 1
    assert res["ok"] == 0


def test_apply_updates_by_id_edital(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_LINK_FIX", "1")
    client = MagicMock()
    res = apply_grants_link_candidates(
        [{"id_edital": 42, "fonte": "Grants.gov",
          "old_link": "https://www.grants.gov/page-not-found",
          "new_link": f"{DETAIL}/360262"}],
        supabase_client=client,
    )
    assert res["ok"] == 1
    client.table.assert_called_with("edital")
    client.table.return_value.update.assert_called_with({"link": f"{DETAIL}/360262"})


def test_apply_skips_candidate_without_id_edital(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_LINK_FIX", "1")
    client = MagicMock()
    res = apply_grants_link_candidates(
        [{"fonte": "Grants.gov", "old_link": "x", "new_link": f"{DETAIL}/1"}],
        supabase_client=client,
    )
    assert res["skipped"] == 1
    assert res["ok"] == 0


def test_apply_large_batch_requires_confirm(monkeypatch):
    monkeypatch.setenv("EDITALFINDER_ALLOW_CONTROLLED_APPLY", "1")
    monkeypatch.setenv("EDITALFINDER_ALLOW_LINK_FIX", "1")
    cands = [
        {"id_edital": i, "fonte": "Grants.gov", "old_link": "x", "new_link": f"{DETAIL}/{i}"}
        for i in range(101)
    ]
    with pytest.raises(RuntimeError):
        apply_grants_link_candidates(cands, supabase_client=MagicMock())


def test_validate_candidate_reasons():
    assert validate_link_fix_candidate({"id_edital": 1, "fonte": "Grants.gov",
                                        "old_link": "x", "new_link": f"{DETAIL}/1"}) is None
    assert validate_link_fix_candidate({"id_edital": 1, "fonte": "BNDES",
                                        "new_link": f"{DETAIL}/1"}) == "fonte_nao_grants"
