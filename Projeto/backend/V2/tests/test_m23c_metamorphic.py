"""Per-candidate semantic invariance is not batch-order invariance."""

import copy

import pytest
from m23c_fixtures import build, case_by_id
from test_m23c_pipeline import check_candidate, projection

from editalfinder_v2.domain.financial_models import FinancialClaim
from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import IntegratedCandidate, IntegrationReport
from editalfinder_v2.domain.models import OperationalError


def evaluated(data):
    result = integrate(data)
    assert isinstance(result, IntegrationReport)
    return result


def test_reordering_candidates_preserves_semantics_but_obeys_order():
    data = build(case_by_id("M23C-E-001"))
    first = evaluated(data)
    order = (4, 2, 0, 3, 1)
    second = evaluated(
        data.model_copy(update={"candidates": tuple(data.candidates[i] for i in order)})
    )
    assert second.candidates == tuple(first.candidates[i] for i in order)
    assert second.audit != first.audit


@pytest.mark.parametrize("news", [False, True])
def test_unrelated_record_cannot_change_candidate_conclusions(news):
    case = case_by_id("M23C-A-001")
    before = evaluated(build(case)).candidates[0]
    extra = copy.deepcopy(case_by_id("M23C-F-001")["records"][0])
    if not news:
        extra = {"title": "Registro não relacionado", "unrelated_money": "USD 999999999"}
    case["records"].append(extra)
    after = evaluated(build(case)).candidates[0]
    # Complete snapshots/audits legitimately change. Semantic outputs must not.
    assert projection(before) == projection(after)
    assert before.diagnostics == after.diagnostics
    assert before.validation.issues == after.validation.issues
    assert before.validation.decision == after.validation.decision
    assert after.validation.promotable is False


@pytest.mark.parametrize("country", ["US", "PT", "FR"])
def test_publisher_country_does_not_change_applicant_eligibility(country):
    case = case_by_id("M23C-H-001")
    baseline = evaluated(build(case)).candidates[0]
    case["records"][0]["geographic_locations"][4]["country_code"] = country
    changed = evaluated(build(case)).candidates[0]

    def eligibility(c):
        return [
            location for location in projection(c)["geography"] if location[0] == "elegibilidade"
        ]

    assert eligibility(baseline) == eligibility(changed)
    assert changed.normalizations.geography.locations[0].municipality_verified is False
    assert changed.normalizations.geography.scope == "nao_identificado"


def test_unrelated_monetary_value_does_not_relabel_existing_amounts():
    case = case_by_id("M23C-A-001")
    before = evaluated(build(case)).candidates[0]
    case["records"][0]["financial_claims"].append(
        {"role": "estimated_project_cost", "value": "USD 999999", "format": "decimal"}
    )
    after = evaluated(build(case)).candidates[0]
    assert projection(after)["financial"][:2] == projection(before)["financial"]
    assert len(after.normalizations.financial.claims) == 3
    assert [d.code for d in after.diagnostics] == [d.code for d in before.diagnostics]


def test_identity_cycle_change_does_not_preserve_exact_match():
    case = case_by_id("M23C-I-005")
    assert evaluated(build(case)).identity_results[0].decision == "exact_match"
    case["records"][1]["publication_cycle"] = "2027"
    result = evaluated(build(case))
    assert [r.decision for r in result.identity_results] == ["distinct_cycles"] * 2
    assert len(result.candidates) == 2
    for c in result.candidates:
        assert c.validation.promotable is False
        assert c.input.context.candidate.unit.pointer in {"/records/0", "/records/1"}


def test_exact_contextual_identity_does_not_move_claims_or_evidence():
    case = case_by_id("M23C-I-005")
    case["records"][0]["financial_claims"] = [
        {"role": "program_budget", "value": "BRL 10000000", "format": "decimal"}
    ]
    case["records"][1]["financial_claims"] = [
        {"role": "proposal_maximum", "value": "BRL 500000", "format": "decimal"}
    ]
    data = build(case)
    result = evaluated(data)
    assert result.identity_results[0].decision == "exact_match"
    assert len(result.candidates) == 2
    assert projection(result.candidates[0])["financial"] == [
        ["program_budget", ["10000000"], "BRL"]
    ]
    assert projection(result.candidates[1])["financial"] == [
        ["proposal_maximum", ["500000"], "BRL"]
    ]
    assert tuple(c.input for c in result.candidates) == data.candidates


def test_shared_document_hash_does_not_establish_identity():
    data = build(case_by_id("M23C-I-006"))
    assert (
        data.candidates[0].context.snapshots[0].audit
        == data.candidates[1].context.snapshots[0].audit
    )
    result = evaluated(data)
    assert all(r.decision == "insufficient_information" for r in result.identity_results)
    assert len(result.candidates) == 2


def test_chimeric_news_candidate_cannot_borrow_actionability_money_or_deadline():
    case = case_by_id("M23C-E-001")
    data = build(case)
    baseline = evaluated(data)
    grant, credit, _, news, _ = data.candidates
    donated = tuple(
        a
        for a in grant.context.candidate.assertions
        if a.field in {"actionable", "submission_deadline"}
    ) + tuple(a for a in credit.context.candidate.assertions if a.field == "credit_principal")
    local = tuple(a for a in news.context.candidate.assertions if a.field != "actionable")
    candidate = news.context.candidate.model_copy(update={"assertions": local + donated})
    foreign_money = next(a for a in donated if a.field == "credit_principal")
    proof = credit.identifiers[0].provenance.model_copy(
        update={"evidence": foreign_money.evidence[0]}
    )
    from editalfinder_v2.domain.semantic_common import SemanticValue

    chimera = news.model_copy(
        update={
            "context": news.context.model_copy(update={"candidate": candidate}),
            "temporal": grant.temporal,
            "financial": (
                FinancialClaim(
                    role="proposal_maximum",
                    value=SemanticValue(original=foreign_money.value, provenance=proof),
                    format="decimal",
                ),
            ),
        }
    )
    changed = evaluated(
        data.model_copy(
            update={"candidates": (grant, credit, data.candidates[2], chimera, data.candidates[4])}
        )
    )
    assert changed.candidates[:3] == baseline.candidates[:3]
    assert changed.candidates[4] == baseline.candidates[4]
    bad = changed.candidates[3]
    assert isinstance(bad, IntegratedCandidate)
    assert bad.validation.decision.value == "REVIEW"
    assert bad.validation.promotable is changed.promotable is False
    assert "evidence_scope_mismatch" in {i.code for i in bad.validation.issues}
    assert all(
        e.civil_date is None and e.instant_utc is None for e in bad.normalizations.temporal.events
    )
    assert all(c.normalized is None for c in bad.normalizations.financial.claims)
    rejected = [d for d in bad.diagnostics if d.code == "consistency_claim_evidence_unavailable"]
    assert len(rejected) == len(grant.temporal) + 1
    assert all(d.evidence == () for d in rejected)


@pytest.mark.parametrize(
    "field", ["financial", "temporal", "taxonomy", "geography", "organizations"]
)
def test_foreign_domain_claims_never_become_local_normalized_facts(field):
    data = build(case_by_id("M23C-E-001"))
    donor, receiver = data.candidates[0], data.candidates[3]
    changed = receiver.model_copy(update={field: getattr(donor, field)})
    result = evaluated(data.model_copy(update={"candidates": (changed,)})).candidates[0]
    domain = getattr(result.normalizations, field)
    assert not isinstance(domain, OperationalError)
    if field == "financial":
        assert all(c.normalized is None for c in domain.claims)
    elif field == "temporal":
        assert all(e.civil_date is None and e.instant_utc is None for e in domain.events)
    elif field == "taxonomy":
        assert all(t.canonical_code is None for t in domain.classifications)
    elif field == "geography":
        assert all(loc.country_code is None and loc.state_code is None for loc in domain.locations)
    else:
        # M2.2b explicitly preserves lexical presentation even for unsupported proof.
        assert domain.comparison_keys == tuple(() for _ in donor.organizations)
        invalid = [
            d for d in domain.structured_diagnostics if d.code == "organization_evidence_invalid"
        ]
        assert [d.claim_index for d in invalid] == list(range(len(donor.organizations)))
        assert all(o.normalized_name == o.claim.name.original for o in domain.organizations)
    assert result.validation.promotable is False


@pytest.mark.parametrize("case_id", ["M23C-A-001", "M23C-B-001", "M23C-C-001"])
def test_manual_oracle_detects_a_changed_expected_diagnostic(case_id):
    case = case_by_id(case_id)
    candidate = evaluated(build(case)).candidates[0]
    forged_oracle = copy.deepcopy(case["expected_candidates"][0])
    forged_oracle["expected_diagnostic_codes"] = ["fabricated_approval"]
    with pytest.raises(AssertionError):
        check_candidate(candidate, forged_oracle)
