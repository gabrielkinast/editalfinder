"""Offline, evidence-bound consistency; synthetic inputs, no real-world certification."""

import json
from typing import Any

from m23_fixtures import adapt_records, records_for

from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import IntegratedCandidate, IntegrationReport


def run_record(**updates: Any) -> tuple[IntegrationReport, IntegratedCandidate]:
    record = {**records_for("grant")[0], **updates}
    result = integrate(adapt_records([record]))
    assert isinstance(result, IntegrationReport)
    candidate = result.candidates[0]
    assert isinstance(candidate, IntegratedCandidate)
    return result, candidate


def test_no_conflict_is_limited_rule_coverage_not_acceptance() -> None:
    report, candidate = run_record()
    assert [d.code for d in candidate.diagnostics] == ["consistency_no_conflict_detected"]
    diagnostic = candidate.diagnostics[0]
    assert diagnostic.classification == "no_conflict_detected"
    assert diagnostic.version == "m2.3b-consistency-v1"
    assert diagnostic.claim_references == diagnostic.evidence == ()
    assert report.promotable is candidate.validation.promotable is False
    assert IntegrationReport.model_validate_json(report.model_dump_json()) == report
    assert json.loads(report.model_dump_json())["candidates"][0]["diagnostics"]


def test_standalone_engine_refuses_foreign_context_before_relationships() -> None:
    from editalfinder_v2.domain.integration_consistency import evaluate_consistency

    report, first = run_record()
    _, foreign = run_record(title="Another explicitly separate source record")
    observations = evaluate_consistency(first.input, foreign.normalizations, first.validation)
    assert [d.code for d in observations] == ["consistency_context_mismatch"]
    assert observations[0].classification == "insufficient_information"
    assert observations[0].claim_references == observations[0].evidence == ()
    assert report.promotable is False


def find(candidate: IntegratedCandidate, code: str):
    matches = [d for d in candidate.diagnostics if d.code == code]
    assert len(matches) == 1, [d.code for d in candidate.diagnostics]
    return matches[0]


def test_unknown_investment_taxonomy_is_preserved_not_mapped() -> None:
    _, candidate = run_record(
        taxonomy_claims=[{"role": "resource_type", "value": "venture_capital"}]
    )
    diagnostic = find(candidate, "consistency_taxonomy_unsupported")
    assert diagnostic.classification == "insufficient_information"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [("taxonomy", 0)]
    assert diagnostic.evidence == (candidate.input.taxonomy[0].value.provenance,)
    assert diagnostic.normalization_versions[0].catalog_version == "seeds-000002"
    assert candidate.normalizations.taxonomy.classifications[0].canonical_code is None
    assert candidate.input.taxonomy[0].value.original == "venture_capital"


def test_taxonomy_relationship_never_uses_a_sibling_record_proof() -> None:
    record = records_for("grant")[0]
    data = adapt_records(
        [
            record,
            {**record, "taxonomy_claims": [{"role": "resource_type", "value": "venture_capital"}]},
        ]
    )
    left, right = data.candidates
    left = left.model_copy(update={"taxonomy": right.taxonomy})
    result = integrate(data.model_copy(update={"candidates": (left, right)}))
    assert isinstance(result, IntegrationReport)
    assert isinstance(result.candidates[0], IntegratedCandidate)
    diagnostic = find(result.candidates[0], "consistency_claim_evidence_unavailable")
    assert diagnostic.evidence == ()
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [("taxonomy", 0)]
    assert "consistency_taxonomy_unsupported" not in [
        d.code for d in result.candidates[0].diagnostics
    ]


def test_hybrid_grant_credit_is_unresolved_not_a_contradiction() -> None:
    _, candidate = run_record(
        taxonomy_claims=[
            {"role": "resource_type", "value": "financiamento_nao_reembolsavel"},
            {"role": "resource_type", "value": "credito"},
        ]
    )
    diagnostic = find(candidate, "consistency_hybrid_relationship_unverified")
    assert diagnostic.classification == "insufficient_information"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [
        ("taxonomy", 0),
        ("taxonomy", 1),
    ]
    assert diagnostic.evidence == tuple(c.value.provenance for c in candidate.input.taxonomy)
    assert not any(d.classification == "contradiction" for d in candidate.diagnostics)


def test_explicit_reversed_financial_range_has_a_single_scoped_contradiction() -> None:
    _, candidate = run_record(
        financial_claims=[
            {"role": "proposal_maximum", "value": "BRL 100 to 10", "format": "decimal"}
        ]
    )
    diagnostic = find(candidate, "consistency_financial_range_contradiction")
    assert diagnostic.classification == "contradiction"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [("financial", 0)]
    assert diagnostic.evidence == (candidate.input.financial[0].value.provenance,)
    assert diagnostic.normalization_versions[0].version == "financial-conservative-v1"


def test_unknown_currency_is_insufficient_not_a_magnitude_comparison() -> None:
    _, candidate = run_record(
        financial_claims=[
            {"role": "proposal_minimum", "value": "$ 999999", "format": "decimal"},
            {"role": "proposal_maximum", "value": "BRL 10", "format": "decimal"},
        ]
    )
    diagnostic = find(candidate, "consistency_financial_interpretation_unresolved")
    assert diagnostic.classification == "insufficient_information"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [("financial", 0)]
    assert not any(
        d.classification in {"contradiction", "potential_conflict"} for d in candidate.diagnostics
    )


def test_minimum_above_maximum_is_only_potential_without_shared_instrument_scope() -> None:
    _, candidate = run_record(
        financial_claims=[
            {"role": "proposal_minimum", "value": "BRL 100", "format": "decimal"},
            {"role": "proposal_maximum", "value": "BRL 10", "format": "decimal"},
        ]
    )
    diagnostic = find(candidate, "consistency_financial_bounds_scope_unverified")
    assert diagnostic.classification == "potential_conflict"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [
        ("financial", 0),
        ("financial", 1),
    ]
    assert diagnostic.evidence == tuple(c.value.provenance for c in candidate.input.financial)


def test_different_currency_bounds_are_not_numerically_compared() -> None:
    _, candidate = run_record(
        financial_claims=[
            {"role": "proposal_minimum", "value": "USD 1000000", "format": "decimal"},
            {"role": "proposal_maximum", "value": "BRL 1", "format": "decimal"},
        ]
    )
    diagnostic = find(candidate, "consistency_financial_bounds_not_comparable")
    assert diagnostic.classification == "insufficient_information"
    assert not any(
        d.classification in {"contradiction", "potential_conflict"} for d in candidate.diagnostics
    )


def test_conflicting_deadlines_do_not_acquire_an_invented_stage_identity() -> None:
    _, candidate = run_record(
        temporal_events=[
            {"role": "submission_deadline", "value": "2026-01-01", "format": "iso"},
            {"role": "submission_deadline", "value": "2026-07-01", "format": "iso"},
        ]
    )
    diagnostic = find(candidate, "consistency_temporal_stage_unverified")
    assert diagnostic.classification == "potential_conflict"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [
        ("temporal", 0),
        ("temporal", 1),
    ]
    assert diagnostic.evidence == tuple(c.value.provenance for c in candidate.input.temporal)
    assert candidate.validation.temporal_status == "nao_determinada"


def test_opening_after_close_is_not_proven_contradiction_without_window_identity() -> None:
    _, candidate = run_record(
        temporal_events=[
            {"role": "submission_opening_date", "value": "2026-08-01", "format": "iso"},
            {"role": "submission_deadline", "value": "2026-01-01", "format": "iso"},
        ]
    )
    diagnostic = find(candidate, "consistency_temporal_window_unverified")
    assert diagnostic.classification == "potential_conflict"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [
        ("temporal", 0),
        ("temporal", 1),
    ]


def test_rectification_does_not_replace_any_deadline() -> None:
    _, candidate = run_record(
        temporal_events=[
            {"role": "submission_deadline", "value": "2026-01-01", "format": "iso"},
            {"role": "rectification_date", "value": "2026-02-01", "format": "iso"},
            {"role": "submission_deadline", "value": "2026-03-01", "format": "iso"},
        ]
    )
    diagnostic = find(candidate, "consistency_rectification_precedence_unverified")
    assert diagnostic.classification == "insufficient_information"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [
        ("temporal", 0),
        ("temporal", 1),
        ("temporal", 2),
    ]
    assert (
        tuple(e.claim for e in candidate.normalizations.temporal.events) == candidate.input.temporal
    )


def test_credit_principal_is_not_fabricated_from_a_program_budget() -> None:
    _, candidate = run_record(
        credit_principal="BRL 500000",
        financial_claims=[{"role": "program_budget", "value": "BRL 10000000", "format": "decimal"}],
        taxonomy_claims=[{"role": "resource_type", "value": "credito"}],
    )
    diagnostic = find(candidate, "consistency_credit_terms_unrepresented")
    assert diagnostic.classification == "insufficient_information"
    assert diagnostic.domains == ("taxonomy", "financial")
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [("taxonomy", 0)]
    assert candidate.input.financial[0].role == "program_budget"
    assert any(
        a.field == "credit_principal" and a.value == "BRL 500000"
        for a in candidate.input.context.candidate.assertions
    )


def test_domain_operational_error_is_never_reported_as_no_conflict() -> None:
    _, candidate = run_record(
        financial_claims=[
            {"role": "proposal_maximum", "value": "9" * 300, "currency": "BRL", "format": "decimal"}
        ]
    )
    diagnostic = find(candidate, "consistency_domain_unavailable")
    assert diagnostic.classification == "insufficient_information"
    assert diagnostic.domains == ("financial",)
    assert diagnostic.normalization_versions == diagnostic.evidence == ()
    assert "consistency_no_conflict_detected" not in [d.code for d in candidate.diagnostics]


def test_canonical_scholarship_in_news_does_not_establish_actionability() -> None:
    from editalfinder_v2.domain.validation import validate

    _, candidate = run_record(
        content_kind="news",
        actionable=False,
        taxonomy_claims=[{"role": "resource_type", "value": "bolsa"}],
    )
    diagnostic = find(candidate, "consistency_taxonomy_not_actionability")
    assert diagnostic.classification == "insufficient_information"
    assert diagnostic.domains == ("taxonomy", "validation")
    assert diagnostic.claim_references[0].domain == "taxonomy"
    assert diagnostic.claim_references[1].domain == "validation"
    assert diagnostic.evidence[0] == candidate.input.taxonomy[0].value.provenance
    assert candidate.validation == validate(
        candidate.input.context.candidate,
        candidate.input.context.snapshots,
        reference_date=candidate.validation.reference_date,
    )


def test_international_scope_and_brazilian_eligibility_do_not_prove_contradiction() -> None:
    _, candidate = run_record(
        geographic_scope="internacional",
        geographic_locations=[
            {"role": "elegibilidade", "country_code": "BR"},
            {"role": "origem", "country_code": "US"},
        ],
    )
    diagnostic = find(candidate, "consistency_geographic_scope_relationship_unverified")
    assert diagnostic.classification == "insufficient_information"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [
        ("geographic_scope", 0),
        ("geography", 0),
    ]
    assert diagnostic.evidence == (
        candidate.input.geographic_scope.provenance,
        candidate.input.geography[0].country_code.provenance,
    )
    assert not any(
        d.classification in {"contradiction", "potential_conflict"} for d in candidate.diagnostics
    )


def organization_case(values=("ORG-A", "ORG-B")):
    from datetime import date

    from m22b_fixtures import build_m22b_context

    from editalfinder_v2.domain.identity_models import IdentifierNamespace
    from editalfinder_v2.domain.integration_models import (
        CandidateIntegrationInput,
        IntegrationInput,
    )
    from editalfinder_v2.domain.organization_models import OrganizationClaim, OrganizationIdentifier

    context, rows = build_m22b_context(
        "organization_claims",
        [("funding", {"name": "Similar entity", "institutional": v}) for v in values],
    )
    claims = tuple(
        OrganizationClaim(
            role="funding",
            name=row["name"],
            identifiers=(
                OrganizationIdentifier(
                    kind="institutional",
                    value=row["institutional"],
                    namespace=IdentifierNamespace(value="declared-source-namespace"),
                ),
            ),
        )
        for row in rows
    )
    result = integrate(
        IntegrationInput(
            candidates=(CandidateIntegrationInput(context=context, organizations=claims),),
            reference_date=date(2026, 1, 1),
        )
    )
    assert isinstance(result, IntegrationReport)
    assert isinstance(result.candidates[0], IntegratedCandidate)
    return result, result.candidates[0]


def test_comparable_organization_identifiers_do_not_establish_shared_legal_identity() -> None:
    _, candidate = organization_case()
    diagnostic = find(candidate, "consistency_organization_identity_unverified")
    assert diagnostic.classification == "insufficient_information"
    assert [(r.domain, r.claim_index) for r in diagnostic.claim_references] == [
        ("organizations", 0),
        ("organizations", 1),
    ]
    assert diagnostic.evidence == tuple(
        c.identifiers[0].value.provenance for c in candidate.input.organizations
    )
    assert not any(
        d.classification in {"contradiction", "potential_conflict"} for d in candidate.diagnostics
    )


def test_temporal_evidence_from_another_candidate_cannot_support_a_relationship() -> None:
    record = records_for("grant")[0]
    data = adapt_records([record, record])
    left, right = data.candidates
    left = left.model_copy(update={"temporal": right.temporal})
    result = integrate(data.model_copy(update={"candidates": (left, right)}))
    assert isinstance(result, IntegrationReport)
    candidate = result.candidates[0]
    assert isinstance(candidate, IntegratedCandidate)
    issues = [
        d for d in candidate.diagnostics if d.code == "consistency_claim_evidence_unavailable"
    ]
    assert len(issues) == len(left.temporal)
    assert all(d.evidence == () for d in issues)
    assert [d.claim_references[0].claim_index for d in issues] == list(range(len(left.temporal)))


def test_foreign_operational_failure_is_not_attributed_to_the_current_candidate() -> None:
    from uuid import UUID

    from editalfinder_v2.domain.integration_consistency import evaluate_consistency
    from editalfinder_v2.domain.models import OperationalError

    _, candidate = run_record()
    foreign = OperationalError(candidate_id=UUID(int=9876), code="foreign", stage="normalization")
    outputs = candidate.normalizations.model_copy(update={"financial": foreign})
    observations = evaluate_consistency(candidate.input, outputs, candidate.validation)
    assert [d.code for d in observations] == ["consistency_context_mismatch"]
    assert observations[0].domains == ("integration",)
    assert observations[0].normalization_versions == observations[0].evidence == ()
