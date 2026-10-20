"""Product safety and the precise unsupported portions of the approved contracts."""

import copy

import pytest
from m23c_fixtures import build, case_by_id
from test_m23c_metamorphic import evaluated
from test_m23c_pipeline import check_candidate

from editalfinder_v2.domain.integration_models import IntegratedCandidate


@pytest.mark.parametrize("case_id", ["M23C-A-001", "M23C-B-001", "M23C-C-001", "M23C-D-001"])
def test_originals_and_claim_roles_survive_without_financial_inventions(case_id):
    data = build(case_by_id(case_id))
    result = evaluated(data)
    candidate = result.candidates[0]
    assert isinstance(candidate, IntegratedCandidate)
    assert candidate.input == data.candidates[0]
    n = candidate.normalizations
    assert tuple(e.claim for e in n.temporal.events) == candidate.input.temporal
    assert tuple(f.claim for f in n.financial.claims) == candidate.input.financial
    assert tuple(g.claim for g in n.geography.locations) == candidate.input.geography
    assert tuple(t.claim for t in n.taxonomy.classifications) == candidate.input.taxonomy
    assert tuple(o.claim for o in n.organizations.organizations) == candidate.input.organizations
    fields = {a.field for a in candidate.input.context.candidate.assertions}
    assert not fields & {
        "interest_rate",
        "grace_period",
        "amortization_schedule",
        "equity_percentage",
        "valuation",
        "approved_credit",
        "approved_investment",
        "funded_project_count",
        "guaranteed_award_amount",
        "creditworthiness",
    }
    if case_id == "M23C-A-001":
        assert [f.claim.role for f in n.financial.claims] == ["program_budget", "proposal_maximum"]
    elif case_id == "M23C-B-001":
        raw = {a.field: a.value for a in candidate.input.context.candidate.assertions}
        assert raw["credit_principal"] == "BRL 2000000"
        assert raw["guarantees"] == "Sujeitas à avaliação individual"
        assert n.financial.claims == ()
        assert n.taxonomy.classifications[0].canonical_code == "financiamento_reembolsavel"
    elif case_id == "M23C-C-001":
        classification = n.taxonomy.classifications[0]
        assert classification.claim.value.original == "venture_capital"
        assert classification.canonical_code is None
        assert [d.code for d in classification.diagnostics] == ["taxonomy_mapping_not_approved"]
        raw = {a.field: a.value for a in candidate.input.context.candidate.assertions}
        assert raw["investment_ticket"] == "BRL 500000 to 2000000"
        assert raw["investment_instrument"] == "Participação societária / venture capital"
        assert n.financial.claims == ()
    else:
        assert [d.classification for d in candidate.diagnostics] == ["insufficient_information"] * 2
        assert len(n.financial.claims) == 1
        raw = {a.field: a.value for a in candidate.input.context.candidate.assertions}
        assert raw["grant_component"] == "BRL 500000 não reembolsáveis"
        assert raw["credit_component"] == "BRL 2000000 reembolsáveis"


@pytest.mark.parametrize("case_id", [f"M23C-F-00{i}" for i in range(1, 7)])
def test_negative_controls_do_not_acquire_actionability_or_promotion(case_id):
    case = case_by_id(case_id)
    candidate = evaluated(build(case)).candidates[0]
    assert candidate.validation.decision.value == "REVIEW"
    assert candidate.validation.promotable is False
    assert candidate.validation.review_attestations == ()
    values = {a.field: a.value for a in candidate.validation.candidate.assertions}
    if case_id == "M23C-F-004":
        assert candidate.validation.temporal_status == "encerrada"
    else:
        assert values["actionable"] is False
        assert candidate.validation.temporal_status == "nao_determinada"
    assert not any(i.code == "instrument_verified" for i in candidate.validation.issues)


@pytest.mark.parametrize("case_id", ["M23C-G-002", "M23C-G-003", "M23C-G-004"])
def test_local_deadline_time_is_preserved_without_inventing_cutoff_timezone(case_id):
    candidate = evaluated(build(case_by_id(case_id))).candidates[0]
    event = candidate.normalizations.temporal.events[0]
    assert (
        event.local_datetime.hour,
        event.local_datetime.minute,
        event.local_datetime.second,
    ) == (18, 0, 0)
    assert event.precision == "second"
    if case_id == "M23C-G-002":
        assert event.instant_utc.isoformat() == "2026-05-20T21:00:00+00:00"
        assert event.diagnostics == ()
    else:
        assert event.instant_utc is None
        assert event.local_datetime.tzinfo is None
        expected = (
            "temporal_timezone_unknown" if case_id.endswith("3") else "temporal_timezone_missing"
        )
        assert [d.code for d in event.diagnostics] == [expected]
    assert candidate.validation.temporal_status == "nao_determinada"


def test_rectification_preserves_original_and_amended_stage_without_a_winner():
    candidate = evaluated(build(case_by_id("M23C-G-001"))).candidates[0]
    events = candidate.normalizations.temporal.events
    assert len(events) == 7
    full = [e for e in events if e.claim.role == "full_application_deadline"]
    assert [e.civil_date.isoformat() for e in full] == ["2026-05-20", "2026-05-25"]
    assert all(e.timezone is None and e.instant_utc is None for e in events)
    assert [d.classification for d in candidate.diagnostics] == [
        "potential_conflict",
        "insufficient_information",
    ]
    assert candidate.validation.temporal_status == "nao_determinada"


def test_municipality_and_absent_eligibility_are_not_certified_or_defaulted():
    candidate = evaluated(build(case_by_id("M23C-H-001"))).candidates[0]
    loc = candidate.normalizations.geography.locations[0]
    assert loc.municipality == "Município Sintético"
    assert loc.municipality_verified is False
    assert "geo_municipality_unverified" in {d.code for d in loc.diagnostics}
    missing = evaluated(build(case_by_id("M23C-H-002"))).candidates[0]
    assert missing.normalizations.geography.scope == "nao_identificado"
    assert [loc.role for loc in missing.normalizations.geography.locations] == ["origem"]
    assert not any(
        loc.role == "elegibilidade" for loc in missing.normalizations.geography.locations
    )


@pytest.mark.parametrize(
    "domain", ["financial", "temporal", "geography", "taxonomy", "organizations"]
)
def test_manual_manifest_rejects_mutated_semantic_role_expectations(domain):
    case = case_by_id("M23C-A-001")
    candidate = evaluated(build(case)).candidates[0]
    oracle = copy.deepcopy(case["expected_candidates"][0])
    oracle["expected_normalized_roles"][domain][0][0] = "fabricated_role"
    with pytest.raises(AssertionError):
        check_candidate(candidate, oracle)
