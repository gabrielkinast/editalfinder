"""Offline integration orchestration and recomputation boundary tests."""

import hashlib
import json
from datetime import UTC, date, datetime

import pytest
from m23_fixtures import adapt_records, build_case, records_for
from pydantic import ValidationError
from semantic_fixtures import build_context

from editalfinder_v2.domain.financial_models import FinancialInput, FinancialReport
from editalfinder_v2.domain.financial_normalization import normalize_financial
from editalfinder_v2.domain.geography_models import GeographyInput
from editalfinder_v2.domain.geography_normalization import normalize_geography
from editalfinder_v2.domain.identity_models import IdentityResolutionReport, IdentitySubject
from editalfinder_v2.domain.identity_resolution import resolve_identity
from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import (
    CandidateIntegrationInput,
    IdentityComparison,
    IntegratedCandidate,
    IntegrationInput,
    IntegrationReport,
)
from editalfinder_v2.domain.models import OperationalError
from editalfinder_v2.domain.organization_normalization import normalize_organizations
from editalfinder_v2.domain.taxonomy_models import TaxonomyInput
from editalfinder_v2.domain.taxonomy_normalization import normalize_taxonomy
from editalfinder_v2.domain.temporal_models import TemporalClaim, TemporalInput, TemporalReport
from editalfinder_v2.domain.temporal_normalization import normalize_temporal
from editalfinder_v2.domain.validation import validate


def test_empty_integration_is_deterministic_and_roundtrips() -> None:
    data = IntegrationInput(candidates=(), reference_date=date(2026, 1, 1))
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    assert report.candidates == report.identity_results == ()
    assert report.promotable is False
    assert report.audit is not None
    assert integrate(data) == report
    assert IntegrationReport.model_validate_json(report.model_dump_json()) == report


def test_candidate_reuses_all_domain_results_without_projection() -> None:
    data = build_case("grant")
    original = data.model_dump_json()
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    assert len(report.candidates) == 1
    result = report.candidates[0]
    assert isinstance(result, IntegratedCandidate)
    item = data.candidates[0]
    context = item.context
    assert result.input == item
    assert result.normalizations.temporal == normalize_temporal(
        TemporalInput(context=context, events=item.temporal)
    )
    assert result.normalizations.geography == normalize_geography(
        GeographyInput(context=context, locations=item.geography, scope=item.geographic_scope)
    )
    assert result.normalizations.financial == normalize_financial(
        FinancialInput(context=context, claims=item.financial)
    )
    assert result.normalizations.organizations == normalize_organizations(
        context, item.organizations
    )
    assert result.normalizations.taxonomy == normalize_taxonomy(
        TaxonomyInput(context=context, claims=item.taxonomy, catalog_version=item.catalog_version)
    )
    assert result.validation == validate(
        context.candidate, context.snapshots, reference_date=data.reference_date
    )
    assert result.validation.promotable is False
    # M2.3b intentionally replaces the reserved empty consistency output.
    assert tuple(d.code for d in result.diagnostics) == ("consistency_no_conflict_detected",)
    assert report.identity_results == ()
    assert data.model_dump_json() == original
    assert integrate(data) == report
    assert IntegrationReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("kind", ["candidates", "pairs", "claims", "payload"])
def test_global_resource_limits_return_operational_error(kind: str) -> None:
    from uuid import UUID

    base = build_case("grant")
    item = base.candidates[0]
    if kind == "candidates":
        data = base.model_copy(update={"candidates": (item,) * 33})
    elif kind == "pairs":
        data = base.model_copy(
            update={"identity_comparisons": (IdentityComparison(left_index=0, right_index=0),) * 65}
        )
    elif kind == "claims":
        large = item.model_copy(
            update={"temporal": (TemporalClaim(role="selection_result_date"),) * 4801}
        )
        data = base.model_copy(update={"candidates": (large,)})
    else:
        # Three distinct snapshot UUIDs, each below the domain's 8 MiB ceiling.
        items = []
        for index in range(3):
            snapshot = item.context.snapshots[0]
            snapshot = type(snapshot).model_validate(
                {
                    **snapshot.model_dump(exclude={"audit"}),
                    "id": UUID(int=24000 + index),
                    "payload_json": '"' + "é" * (3 * 1024 * 1024) + '"',
                }
            )
            context = item.context.model_copy(update={"snapshots": (snapshot,)})
            candidate = context.candidate.model_copy(update={"id": UUID(int=25000 + index)})
            items.append(
                item.model_copy(
                    update={"context": context.model_copy(update={"candidate": candidate})}
                )
            )
        data = base.model_copy(update={"candidates": tuple(items)})
    result = integrate(data)
    assert isinstance(result, OperationalError)
    assert result.code == "integration_limits_exceeded"
    assert result.stage == "integration"
    assert result.candidate_id == data.candidates[0].context.candidate.id
    assert result.promotable is False


@pytest.mark.parametrize("kind", ["duplicate", "index", "empty_index"])
def test_invalid_batch_topology_is_operational(kind: str) -> None:
    from uuid import UUID

    data = build_case("grant")
    expected = "integration_identity_index_invalid"
    if kind == "duplicate":
        data = data.model_copy(update={"candidates": data.candidates * 2})
        expected = "integration_duplicate_candidate_id"
    else:
        data = data.model_copy(
            update={
                "candidates": () if kind == "empty_index" else data.candidates,
                "identity_comparisons": (IdentityComparison(left_index=0, right_index=1),),
            }
        )
    result = integrate(data)
    assert isinstance(result, OperationalError)
    assert result.code == expected
    assert result.stage == "integration"
    assert result.candidate_id == (
        data.candidates[0].context.candidate.id if data.candidates else UUID(int=0)
    )


@pytest.mark.parametrize("kind", ["json", "duplicate_snapshot", "combined_claims"])
def test_candidate_preflight_failure_does_not_discard_healthy_candidate(kind: str) -> None:
    data = build_case("grant")
    item = data.candidates[0]
    context = item.context
    if kind == "json":
        snapshot = context.snapshots[0]
        malformed = type(snapshot).model_validate(
            {**snapshot.model_dump(exclude={"audit"}), "payload_json": '{"bad":'}
        )
        item = item.model_copy(
            update={"context": context.model_copy(update={"snapshots": (malformed,)})}
        )
        code = "normalization_invalid_snapshot_json"
    elif kind == "duplicate_snapshot":
        item = item.model_copy(
            update={"context": context.model_copy(update={"snapshots": context.snapshots * 2})}
        )
        code = "normalization_duplicate_snapshot_id"
    else:
        # Each domain alone is below 1200; combined candidate work is not.
        item = item.model_copy(
            update={
                "temporal": (TemporalClaim(role="selection_result_date"),) * 600,
                "financial": item.financial * 301,
            }
        )
        code = "normalization_limits_exceeded"
    healthy_context, *_ = build_context()
    healthy = CandidateIntegrationInput(context=healthy_context)
    data = data.model_copy(update={"candidates": (item, healthy)})
    result = integrate(data)
    assert isinstance(result, IntegrationReport)
    assert isinstance(result.candidates[0], OperationalError)
    assert result.candidates[0].code == code
    assert isinstance(result.candidates[1], IntegratedCandidate)
    assert result.candidates[1].input == healthy
    assert IntegrationReport.model_validate_json(result.model_dump_json()) == result


@pytest.mark.parametrize("kind", ["payload", "metadata"])
def test_shared_snapshot_collision_marks_every_owner_only(kind: str) -> None:
    data = build_case("mixed")
    left, right = data.candidates[:2]
    snapshot = right.context.snapshots[0]
    change = (
        {"payload_json": snapshot.payload_json + " "}
        if kind == "payload"
        else {"collector_version": "different-collector"}
    )
    changed = type(snapshot).model_validate({**snapshot.model_dump(exclude={"audit"}), **change})
    right = right.model_copy(
        update={"context": right.context.model_copy(update={"snapshots": (changed,)})}
    )
    healthy_context, *_ = build_context()
    healthy = CandidateIntegrationInput(context=healthy_context)
    data = data.model_copy(update={"candidates": (left, right, healthy)})
    result = integrate(data)
    assert isinstance(result, IntegrationReport)
    assert len(result.candidates) == 3
    for outcome in result.candidates[:2]:
        assert isinstance(outcome, OperationalError)
        assert outcome.code == "integration_snapshot_identity_conflict"
        assert outcome.stage == "integration"
    assert isinstance(result.candidates[2], IntegratedCandidate)


@pytest.mark.parametrize("cycle", ["2026", "2027"])
def test_identity_compares_only_requested_pairs_in_order_without_merging(cycle: str) -> None:
    record = records_for("grant")[0]
    other = {**record, "publication_cycle": cycle}
    data = adapt_records([record, other])
    pairs = (
        IdentityComparison(left_index=1, right_index=0),
        IdentityComparison(left_index=0, right_index=1),
        IdentityComparison(left_index=0, right_index=0),
    )
    data = data.model_copy(update={"identity_comparisons": pairs})
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    assert len(report.candidates) == 2
    assert len(report.identity_results) == len(pairs)
    subjects = tuple(
        IdentitySubject(
            candidate=item.context.candidate,
            snapshots=item.context.snapshots,
            identifiers=item.identifiers,
            cycle=item.cycle,
        )
        for item in data.candidates
    )
    assert report.identity_results == tuple(
        resolve_identity(subjects[p.left_index], subjects[p.right_index]) for p in pairs
    )
    assert isinstance(report.identity_results[0], IdentityResolutionReport)
    assert report.identity_results[0].decision == (
        "exact_match" if cycle == "2026" else "distinct_cycles"
    )
    assert report.promotable is False
    assert IntegrationReport.model_validate_json(report.model_dump_json()) == report


def test_identity_pair_with_failed_preflight_has_no_semantic_decision() -> None:
    data = build_case("grant")
    item = data.candidates[0]
    item = item.model_copy(
        update={
            "context": item.context.model_copy(update={"snapshots": item.context.snapshots * 2})
        }
    )
    healthy_context, *_ = build_context()
    data = data.model_copy(
        update={
            "candidates": (item, CandidateIntegrationInput(context=healthy_context)),
            "identity_comparisons": (IdentityComparison(left_index=1, right_index=0),),
        }
    )
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    assert len(report.identity_results) == 1
    error = report.identity_results[0]
    assert isinstance(error, OperationalError)
    assert error.code == "integration_identity_context_failed"
    assert error.candidate_id == item.context.candidate.id
    assert error.stage == "integration"


@pytest.mark.parametrize(
    "value", ["2026-01-01", datetime(2026, 1, 1), datetime(2026, 1, 1, tzinfo=UTC), True, 1]
)
def test_reference_date_rejects_python_coercion(value: object) -> None:
    with pytest.raises(ValidationError):
        IntegrationInput.model_validate({"candidates": (), "reference_date": value})


@pytest.mark.parametrize("value", [True, -1, "0", 0.0])
def test_identity_indices_are_strict_nonnegative_integers(value: object) -> None:
    with pytest.raises(ValidationError):
        IdentityComparison.model_validate({"left_index": value, "right_index": 0})


@pytest.mark.parametrize("field", ["authorized", "promotable", "review_attestations"])
def test_caller_cannot_supply_integration_authority(field: str) -> None:
    data = build_case("grant").model_dump()
    data[field] = True
    with pytest.raises(ValidationError):
        IntegrationInput.model_validate(data)
    candidate = build_case("grant").candidates[0].model_dump()
    candidate[field] = True
    with pytest.raises(ValidationError):
        CandidateIntegrationInput.model_validate(candidate)


@pytest.mark.parametrize("route", ["constructor", "python", "json"])
@pytest.mark.parametrize(
    "mutation",
    [
        "omission",
        "order",
        "diagnostic",
        "normalization",
        "validation",
        "identity",
        "candidate_input",
    ],
)
def test_report_recomputes_complete_outputs_without_audit(route: str, mutation: str) -> None:
    data = build_case("mixed")
    data = data.model_copy(
        update={"identity_comparisons": (IdentityComparison(left_index=0, right_index=1),)}
    )
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    payload = json.loads(report.model_dump_json()) if route == "json" else report.model_dump()
    payload["candidates"] = list(payload["candidates"])
    payload.pop("audit")
    if mutation == "omission":
        payload["candidates"].pop()
    elif mutation == "order":
        payload["candidates"].reverse()
    elif mutation == "diagnostic":
        payload["candidates"][0]["diagnostics"] = [
            {
                **payload["candidates"][0]["diagnostics"][0],
                "code": "fake",
                "message": "Invented consistency decision",
                "domain": "trust",
            }
        ]
    elif mutation == "normalization":
        payload["candidates"][0]["normalizations"]["temporal"] = {
            "candidate_id": str(data.candidates[0].context.candidate.id),
            "code": "invented_failure",
            "stage": "normalization",
        }
    elif mutation == "validation":
        payload["candidates"][0]["validation"] = {
            "candidate_id": str(data.candidates[0].context.candidate.id),
            "code": "invented_failure",
            "stage": "validation",
        }
    elif mutation == "identity":
        payload["identity_results"] = []
    else:
        payload["candidates"][0]["input"]["identifiers"] = []
    with pytest.raises(ValidationError, match="Integration outputs must match"):
        if route == "constructor":
            IntegrationReport(**payload)
        elif route == "python":
            IntegrationReport.model_validate(payload)
        else:
            IntegrationReport.model_validate_json(json.dumps(payload))


def test_complete_report_digest_rejects_retained_envelope_after_valid_recomputation() -> None:
    data = build_case("grant")
    first = integrate(data)
    second = integrate(data.model_copy(update={"reference_date": date(2026, 1, 2)}))
    assert isinstance(first, IntegrationReport) and isinstance(second, IntegrationReport)
    assert first.audit is not None
    assert (
        first.audit.report_digest
        == hashlib.sha256(first.model_dump_json(exclude={"audit"}).encode("utf-8")).hexdigest()
    )
    payload = second.model_dump()
    payload["audit"] = first.audit
    with pytest.raises(ValidationError, match="Integration audit does not match"):
        IntegrationReport.model_validate(payload)
    with pytest.raises(ValidationError):
        first.input = data


def test_domain_operational_error_is_retained_without_poisoning_other_domains() -> None:
    data = build_case("grant")
    item = data.candidates[0]
    claim = item.financial[0]
    assert claim.value is not None
    bad = claim.model_copy(
        update={"value": claim.value.model_copy(update={"original": "9" * 10000})}
    )
    data = data.model_copy(update={"candidates": (item.model_copy(update={"financial": (bad,)}),)})
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    result = report.candidates[0]
    assert isinstance(result, IntegratedCandidate)
    assert isinstance(result.normalizations.financial, OperationalError)
    assert result.normalizations.financial.code == "normalization_limits_exceeded"
    assert isinstance(result.normalizations.temporal, TemporalReport)
    assert result.validation == validate(
        item.context.candidate, item.context.snapshots, reference_date=data.reference_date
    )
    assert report.promotable is False


def test_foreign_claim_evidence_is_not_imported_from_sibling_candidate() -> None:
    record = records_for("grant")[0]
    data = adapt_records([record, record])
    left, right = data.candidates
    left = left.model_copy(update={"temporal": right.temporal, "financial": right.financial})
    data = data.model_copy(update={"candidates": (left, right)})
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    outcome = report.candidates[0]
    assert isinstance(outcome, IntegratedCandidate)
    assert isinstance(outcome.normalizations.temporal, TemporalReport)
    assert all(
        event.civil_date is None and event.local_datetime is None
        for event in outcome.normalizations.temporal.events
    )
    assert "normalization_evidence_invalid" in {
        d.code for d in outcome.normalizations.temporal.diagnostics
    }
    assert isinstance(outcome.normalizations.financial, FinancialReport)
    assert all(c.normalized is None for c in outcome.normalizations.financial.claims)
    assert outcome.input.context.candidate == left.context.candidate
    assert isinstance(report.candidates[1], IntegratedCandidate)
    assert report.candidates[1].input == right


def test_roles_and_unresolved_alternatives_are_not_collapsed() -> None:
    data = build_case("ambiguous")
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    outcome = report.candidates[0]
    assert isinstance(outcome, IntegratedCandidate)
    temporal = outcome.normalizations.temporal
    assert isinstance(temporal, TemporalReport)
    assert tuple(e.claim for e in temporal.events) == data.candidates[0].temporal
    assert "temporal_deadline_conflict" in {d.code for d in temporal.diagnostics}
    assert outcome.input == data.candidates[0]
    assert outcome.validation.promotable is False
