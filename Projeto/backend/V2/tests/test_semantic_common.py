"""Adversarial regression tests for the shared evidence and audit boundary."""

import json
from uuid import UUID

import pytest
from pydantic import ValidationError
from semantic_fixtures import build_context

from editalfinder_v2.domain.models import OperationalError, RawSnapshot
from editalfinder_v2.domain.semantic_common import (
    AuditedNormalizationReport,
    NormalizationContext,
    NormalizationDiagnostic,
    PreparedContext,
    SemanticValue,
    prepare_context,
)


def prepared(context: NormalizationContext) -> PreparedContext:
    result = prepare_context(context, claim_count=1)
    assert isinstance(result, PreparedContext)
    return result


def test_literal_and_role_bound_to_current_unit() -> None:
    context, values, _, _ = build_context(temporal=[("publication_date", "2026-01-10")])
    assert prepared(context).matches(values[0], "publication_date", collection="temporal_events")
    assert not prepared(context).matches(
        values[0], "submission_deadline", collection="temporal_events"
    )
    assert not prepared(context).matches(
        values[0].model_copy(update={"original": "2026-12-31"}),
        "publication_date",
        collection="temporal_events",
    )


@pytest.mark.parametrize("member", ["candidate_id", "source_id", "execution_id"])
def test_provenance_is_not_a_free_citation(member: str) -> None:
    context, values, _, _ = build_context(temporal=[("publication_date", "2026-01-10")])
    forged = values[0].model_copy(
        update={"provenance": values[0].provenance.model_copy(update={member: UUID(int=99)})}
    )
    assert not prepared(context).matches(forged, "publication_date", collection="temporal_events")


@pytest.mark.parametrize("bad_node", [True, False, 2026, None, ["2026-01-10"]])
def test_json_literal_type_must_be_text(bad_node: object) -> None:
    context, values, _, _ = build_context(temporal=[("publication_date", "2026-01-10")])
    data = json.loads(context.snapshots[0].payload_json)
    data["record"]["temporal_events"][0]["value"] = bad_node
    snapshot = RawSnapshot.model_validate(
        {**context.snapshots[0].model_dump(), "payload_json": json.dumps(data), "audit": None}
    )
    modified = context.model_copy(update={"snapshots": (snapshot,)})
    assert not prepared(modified).matches(
        values[0], "publication_date", collection="temporal_events"
    )


def test_structured_role_cannot_be_relabelled_in_evidence_only() -> None:
    context, values, _, _ = build_context(temporal=[("publication_date", "2026-01-10")])
    proof = values[0].provenance.evidence.model_copy(
        update={"semantic_role": "submission_deadline"}
    )
    value = SemanticValue(
        original=values[0].original,
        provenance=values[0].provenance.model_copy(update={"evidence": proof}),
    )
    assertion = context.candidate.assertions[0].model_copy(
        update={"field": "submission_deadline", "evidence": (proof,)}
    )
    context = context.model_copy(
        update={"candidate": context.candidate.model_copy(update={"assertions": (assertion,)})}
    )
    assert not prepared(context).matches(value, "submission_deadline", collection="temporal_events")


@pytest.mark.parametrize("mutation", ["assertions", "unit", "ambiguity", "source_code"])
def test_missing_membership_ambiguous_and_foreign_scope(mutation: str) -> None:
    context, values, _, _ = build_context(temporal=[("publication_date", "2026-01-10")])
    candidate = context.candidate
    if mutation == "assertions":
        candidate = candidate.model_copy(update={"assertions": ()})
    elif mutation == "ambiguity":
        candidate = candidate.model_copy(
            update={"assertions": (candidate.assertions[0].model_copy(update={"ambiguous": True}),)}
        )
    elif mutation == "unit":
        assert candidate.unit is not None
        candidate = candidate.model_copy(
            update={"unit": candidate.unit.model_copy(update={"pointer": "/sibling"})}
        )
    else:
        candidate = candidate.model_copy(update={"source_code": "other"})
    assert not prepared(context.model_copy(update={"candidate": candidate})).matches(
        values[0], "publication_date", collection="temporal_events"
    )


def test_duplicate_snapshots_fail_without_semantic_result() -> None:
    context, _, _, _ = build_context()
    outcome = prepare_context(
        context.model_copy(update={"snapshots": context.snapshots * 2}), claim_count=0
    )
    assert isinstance(outcome, OperationalError)
    assert outcome.code == "normalization_duplicate_snapshot_id"
    assert not outcome.promotable


@pytest.mark.parametrize("count", [1201, -1])
def test_claim_budget_is_explicit(count: int) -> None:
    context, _, _, _ = build_context()
    outcome = prepare_context(context, claim_count=count)
    assert isinstance(outcome, OperationalError)
    assert outcome.code == "normalization_limits_exceeded"


def test_limit_boundary_is_inclusive() -> None:
    context, _, _, _ = build_context()
    assert isinstance(prepare_context(context, claim_count=1200), PreparedContext)


class ExampleReport(AuditedNormalizationReport):
    original: str
    normalized: str | None
    diagnostics: tuple[NormalizationDiagnostic, ...] = ()


def test_audit_covers_result_diagnostics_and_policy_without_circularity() -> None:
    report = ExampleReport(original="br", normalized="BR")
    assert report.audit is not None
    assert not report.promotable
    assert ExampleReport.model_validate_json(report.model_dump_json()) == report
    for update in (
        {"original": "us"},
        {"normalized": "US"},
        {"diagnostics": [{"code": "altered", "message": "altered"}]},
        {"policy_version": "other"},
        {"audit": {**report.audit.model_dump(), "limits_version": "other"}},
    ):
        with pytest.raises(ValidationError):
            ExampleReport.model_validate({**report.model_dump(), **update})


def test_audit_is_integrity_not_authentication() -> None:
    report = ExampleReport(original="br", normalized="BR")
    recreated = ExampleReport.model_validate(
        {**report.model_dump(), "normalized": "US", "audit": None}
    )
    assert recreated.audit != report.audit
    assert not recreated.promotable
