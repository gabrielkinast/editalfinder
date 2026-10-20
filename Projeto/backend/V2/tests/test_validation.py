from datetime import date
from uuid import UUID

import pytest
from fixtures import example, with_field

from editalfinder_v2.domain.models import (
    Evidence,
    FieldAssertion,
    OpportunityCandidate,
    RawSnapshot,
    ValidationDecision,
    ValidationReport,
)
from editalfinder_v2.domain.validation import validate


def test_legitimate_instrument_awaits_trusted_review_with_audit_trail():
    snapshot, candidate = example()
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert isinstance(report, ValidationReport)
    assert report.decision == ValidationDecision.REVIEW
    assert any(i.code == "trusted_review_required" for i in report.issues)
    assert not report.promotable
    assert report.candidate == candidate
    assert report.snapshots == (snapshot,)
    assert report.ruleset_version
    assert report.issues[0].rule_version


def replace_field(candidate, field, value):
    evidence = next((a.evidence for a in candidate.assertions if a.field == field), ())
    assertions = tuple(a for a in candidate.assertions if a.field != field)
    return OpportunityCandidate(
        id=candidate.id,
        source_id=candidate.source_id,
        source_code=candidate.source_code,
        unit=candidate.unit,
        assertions=assertions + (FieldAssertion(field=field, value=value, evidence=evidence),),
    )


@pytest.mark.parametrize(
    "kind", ["news", "aggregator", "result", "menu", "institutional", "auxiliary"]
)
def test_non_opportunity_content_awaits_trusted_review(kind):
    snapshot, candidate = example(kind=kind)
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    assert not report.promotable
    assert any(i.code == "trusted_review_required" for i in report.issues)


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", None),
        ("official_url", None),
        ("actionable", None),
        ("specific_instrument", False),
        ("content_kind", "unknown"),
        ("official_url", "https://user:secret@example.org/call"),
        ("official_url", "javascript:alert(1)"),
    ],
)
def test_incomplete_or_unproven_instrument_requires_review(field, value):
    snapshot, candidate = example()
    snapshot, candidate = with_field(snapshot, candidate, field, value)
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    expected = {
        "title": "missing_title",
        "official_url": "invalid_official_url",
        "actionable": "unproven_instrument",
        "specific_instrument": "unproven_instrument",
        "content_kind": "invalid_field_value",
    }[field]
    assert any(i.code == expected for i in report.issues)
    assert not any(i.code in {"unverifiable_evidence", "missing_evidence"} for i in report.issues)
    assert not report.promotable


def test_conflicting_deadlines_require_review_without_discarding_assertions():
    snapshot, candidate = example()
    candidate = OpportunityCandidate(
        id=candidate.id,
        source_id=candidate.source_id,
        source_code=candidate.source_code,
        unit=candidate.unit,
        assertions=candidate.assertions
        + (
            FieldAssertion(
                field="submission_deadline",
                value=date(2026, 11, 1),
                evidence=candidate.assertions[0].evidence,
            ),
        ),
    )
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    assert any(i.code == "conflicting_assertions" for i in report.issues)
    assert report.candidate == candidate


def test_future_deadline_does_not_prove_open_status_and_historical_is_valid():
    snapshot, candidate = example()
    future = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    historical = validate(candidate, (snapshot,), reference_date=date(2027, 6, 1))
    assert historical.decision == ValidationDecision.REVIEW
    assert any(i.code == "trusted_review_required" for i in historical.issues)
    assert historical.temporal_status == "encerrada"
    assert future.temporal_status == "nao_determinada"


@pytest.mark.parametrize(
    "change", ["missing", "bad_quote", "bad_pointer", "foreign_snapshot", "zero_confidence", "llm"]
)
def test_unverifiable_evidence_cannot_promote(change):
    snapshot, candidate = example()
    updates = {
        "bad_quote": {"quote": "not in snapshot"},
        "bad_pointer": {"pointer": "/missing"},
        "foreign_snapshot": {"snapshot_id": UUID(int=999)},
        "zero_confidence": {"confidence": "0"},
        "llm": {"method": "llm"},
    }
    candidate = OpportunityCandidate(
        id=candidate.id,
        source_id=candidate.source_id,
        source_code=candidate.source_code,
        unit=candidate.unit,
        assertions=tuple(
            FieldAssertion.model_validate(
                {
                    **a.model_dump(),
                    "evidence": ()
                    if change == "missing"
                    else tuple(
                        Evidence.model_validate({**e.model_dump(), **updates[change]})
                        for e in a.evidence
                    ),
                }
            )
            for a in candidate.assertions
        ),
    )
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    assert not report.promotable
    assert report.candidate == candidate
    expected = "missing_evidence" if change == "missing" else "unverifiable_evidence"
    assert any(i.code == expected for i in report.issues)


def test_malformed_snapshot_is_operational_failure_not_rejection():
    from editalfinder_v2.domain.models import OperationalError

    snapshot, candidate = example()
    broken = RawSnapshot.model_validate(
        {**snapshot.model_dump(exclude={"audit"}), "payload_json": "not json"}
    )
    result = validate(candidate, (broken,), reference_date=date(2026, 6, 1))
    assert isinstance(result, OperationalError)
    assert result.code == "invalid_snapshot_json"
    assert not result.promotable
    assert not hasattr(result, "decision")


def test_upstream_failure_has_no_semantic_decision():
    from editalfinder_v2.domain.models import OperationalError

    snapshot, candidate = example()
    error = OperationalError(candidate_id=candidate.id, code="parse_failed", stage="parsing")
    result = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1), errors=(error,))
    assert isinstance(result, OperationalError)
    assert result == error
    assert not result.promotable


def test_multiple_candidates_share_page_but_not_decisions():
    snapshot, candidate = example()
    incomplete = replace_field(candidate, "title", None)
    incomplete = OpportunityCandidate.model_validate({**incomplete.model_dump(), "id": UUID(int=5)})
    reports = [
        validate(c, (snapshot,), reference_date=date(2026, 6, 1)) for c in (candidate, incomplete)
    ]
    assert [r.decision for r in reports] == [ValidationDecision.REVIEW, ValidationDecision.REVIEW]
    assert [r.candidate.id for r in reports] == [UUID(int=4), UUID(int=5)]


def test_repeated_validation_and_json_roundtrip_are_identical():
    snapshot, candidate = example()
    first = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    second = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert first.model_dump_json() == second.model_dump_json()
    assert ValidationReport.model_validate_json(first.model_dump_json()) == first
    assert RawSnapshot.model_validate_json(snapshot.model_dump_json()) == snapshot


@pytest.mark.parametrize(
    "field,value",
    [
        ("opportunity_type", "grant"),
        ("resource_type", "Oportunidade Publica"),
        ("area", "Bolsas"),
        ("geographic_scope", "Nacional"),
        ("no_deadline_reason", "permanente"),
        ("submission_deadline", "next Friday"),
        ("opening_date", date(2027, 1, 1)),
        ("unknown_field", "anything"),
        ("title", "Home"),
        ("minimum_amount", "-1"),
        ("maximum_amount", "500"),
        ("actionable", "true"),
    ],
)
def test_invalid_or_unsupported_assertions_require_review(field, value):
    snapshot, candidate = example()
    snapshot, candidate = with_field(snapshot, candidate, field, value)
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    expected = (
        "unsupported_field"
        if field in {"unknown_field", "minimum_amount", "maximum_amount"}
        else "generic_title"
        if field == "title"
        else "inconsistent_dates"
        if field == "opening_date"
        else "invalid_field_value"
    )
    assert any(i.code == expected for i in report.issues)
    assert not any(i.code in {"missing_evidence", "unverifiable_evidence"} for i in report.issues)


def test_unknown_classification_is_not_invented():
    snapshot, candidate = example()
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    assert any(i.code == "trusted_review_required" for i in report.issues)
    assert not any(
        a.field in {"opportunity_type", "resource_type", "area"}
        for a in report.candidate.assertions
    )


def test_missing_deadline_is_not_silently_continuous():
    snapshot, candidate = example()
    candidate = replace_field(candidate, "submission_deadline", None)
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    assert not any(a.field == "no_deadline_reason" for a in report.candidate.assertions)


def test_explicit_no_deadline_reason_is_supported():
    snapshot, candidate = example(deadline=None, reason="nao_informado")
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    assert any(i.code == "trusted_review_required" for i in report.issues)


def test_unapproved_source_cannot_promote():
    snapshot, candidate = example()
    candidate = OpportunityCandidate.model_validate(
        {**candidate.model_dump(), "source_code": "japan_jsps"}
    )
    snapshot = RawSnapshot.model_validate(
        {
            **snapshot.model_dump(exclude={"audit"}),
            "source_code": "japan_jsps",
        }
    )
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    assert any(i.code == "source_outside_baseline" for i in report.issues)
    assert not any(i.code == "unverifiable_evidence" for i in report.issues)


def test_ambiguous_assertion_cannot_promote():
    snapshot, candidate = example()
    assertions = tuple(
        FieldAssertion.model_validate({**a.model_dump(), "ambiguous": True})
        if a.field == "submission_deadline"
        else a
        for a in candidate.assertions
    )
    candidate = OpportunityCandidate.model_validate(
        {**candidate.model_dump(), "assertions": assertions}
    )
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW


@pytest.mark.parametrize(
    "field,value",
    [
        ("title", "Invented official title"),
        ("official_url", "https://unrelated.example.org/other"),
    ],
)
def test_identity_values_must_be_tied_to_evidence(field, value):
    snapshot, candidate = example()
    candidate = replace_field(candidate, field, value)
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW


def test_source_code_and_uuid_must_match_across_snapshots():
    snapshot, candidate = example()
    snapshot = RawSnapshot.model_validate(
        {**snapshot.model_dump(exclude={"audit"}), "source_id": UUID(int=99)}
    )
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW


def test_rejection_also_requires_evidence():
    snapshot, candidate = example()
    candidate = replace_field(candidate, "content_kind", "news")
    candidate = replace_field(candidate, "actionable", False)
    candidate = replace_field(candidate, "specific_instrument", False)
    candidate = OpportunityCandidate.model_validate(
        {
            **candidate.model_dump(),
            "assertions": tuple(
                FieldAssertion(field=a.field, value=a.value) for a in candidate.assertions
            ),
        }
    )
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW


@pytest.mark.parametrize(
    "payload", ['{"body":"first","body":"second"}', '{"amount":NaN}', '{"amount":Infinity}']
)
def test_nonstandard_or_duplicate_json_is_operational_error(payload):
    from editalfinder_v2.domain.models import OperationalError

    snapshot, candidate = example()
    snapshot = RawSnapshot.model_validate(
        {**snapshot.model_dump(exclude={"audit"}), "payload_json": payload}
    )
    result = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert isinstance(result, OperationalError)
    assert result.code == "invalid_snapshot_json"


def test_duplicate_snapshot_identity_is_operational_error():
    from editalfinder_v2.domain.models import OperationalError

    snapshot, candidate = example()
    result = validate(candidate, (snapshot, snapshot), reference_date=date(2026, 6, 1))
    assert isinstance(result, OperationalError)
    assert result.code == "duplicate_snapshot_id"


@pytest.mark.parametrize("method", ["deterministic_rule", "structured_field"])
def test_unapproved_automatic_intent_rules_require_review(method):
    snapshot, candidate = example()
    assertions = tuple(
        FieldAssertion.model_validate(
            {
                **a.model_dump(),
                "evidence": tuple(
                    Evidence.model_validate({**e.model_dump(), "method": method})
                    for e in a.evidence
                ),
            }
        )
        for a in candidate.assertions
    )
    candidate = OpportunityCandidate.model_validate(
        {**candidate.model_dump(), "assertions": assertions}
    )
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW


@pytest.mark.parametrize("null_first", [True, False])
def test_null_duplicate_does_not_override_known_value(null_first):
    snapshot, candidate = example()
    absent = FieldAssertion(field="title", value=None)
    assertions = (
        (absent,) + candidate.assertions if null_first else candidate.assertions + (absent,)
    )
    candidate = OpportunityCandidate.model_validate(
        {**candidate.model_dump(), "assertions": assertions}
    )
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    assert any(i.code == "trusted_review_required" for i in report.issues)


def test_field_issue_contains_only_relevant_evidence():
    snapshot, candidate = example()
    candidate = replace_field(candidate, "submission_deadline", "2099-01-01")
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW
    issue = next(i for i in report.issues if i.field == "submission_deadline")
    expected = tuple(
        e for a in candidate.assertions if a.field == "submission_deadline" for e in a.evidence
    )
    assert issue.evidence == expected
    assert issue.related_fields == ("submission_deadline",)


def test_invented_deadline_does_not_match_unrelated_quote():
    snapshot, candidate = example()
    candidate = replace_field(candidate, "submission_deadline", date(2099, 1, 1))
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert report.decision == ValidationDecision.REVIEW


def test_page_candidates_preserve_independent_intent_and_diagnostics():
    from fixtures import multiple_candidates

    snapshot, candidates = multiple_candidates()
    reports = [validate(c, (snapshot,), reference_date=date(2026, 6, 1)) for c in candidates]
    assert [r.decision for r in reports] == [
        ValidationDecision.REVIEW,
        ValidationDecision.REVIEW,
    ]
    assert reports[0].candidate.id != reports[1].candidate.id
    assert reports[0].snapshots == reports[1].snapshots
