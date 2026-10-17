"""Integration regressions exercise the public engine, not only safety helpers."""

import json
from datetime import date
from uuid import UUID

import pytest
from fixtures import example, with_field
from pydantic import ValidationError

from editalfinder_v2.domain.models import (
    CrossDocumentReference,
    DocumentUnit,
    Evidence,
    FieldAssertion,
    OperationalError,
    OpportunityCandidate,
    RawSnapshot,
    ValidationDecision,
    ValidationIssue,
    ValidationReport,
)
from editalfinder_v2.domain.validation import validate

DAY = date(2026, 6, 1)


@pytest.mark.parametrize("number", ["NaN", "Infinity", "-Infinity", "1e999", "-1e999"])
def test_unused_nonfinite_numeric_field_is_operational_error(number):
    snapshot, candidate = example()
    payload = snapshot.payload_json[:-1] + ', "unused":' + number + "}"
    snapshot = RawSnapshot.model_validate(
        {**snapshot.model_dump(exclude={"audit"}), "payload_json": payload}
    )
    result = validate(candidate, (snapshot,), reference_date=DAY)
    assert isinstance(result, OperationalError)
    assert result.code == "invalid_snapshot_json"
    assert not result.promotable


@pytest.mark.parametrize("pointer", ["/" + "9" * 5000, "/" + "9" * 4095, "/00", "/-", "/~2"])
def test_malformed_array_pointer_produces_structured_review(pointer):
    snapshot, candidate = example()
    snapshot = RawSnapshot.model_validate(
        {**snapshot.model_dump(exclude={"audit"}), "payload_json": '["Edital 01/2026"]'}
    )
    evidence = Evidence.model_validate(
        {**candidate.assertions[0].evidence[0].model_dump(), "pointer": pointer}
    )
    candidate = OpportunityCandidate.model_validate(
        {
            **candidate.model_dump(),
            "assertions": (
                FieldAssertion(field="title", value="Edital 01/2026", evidence=(evidence,)),
            ),
        }
    )
    result = validate(candidate, (snapshot,), reference_date=DAY)
    assert isinstance(result, ValidationReport)
    assert result.decision == ValidationDecision.REVIEW
    assert "unverifiable_evidence" in {i.code for i in result.issues}


@pytest.mark.parametrize(
    "url",
    [
        "https://bad\u0001host/call",
        "https://user@example.org/call",
        "https://example.org:0/call",
        "https://example.org:65536/call",
        "https://example.org:/call",
        "https://example.org/%00",
        "https://example.org/\ncall",
        "ftp://example.org/call",
        "https://bad_host.org/call",
    ],
)
def test_malformed_official_url_has_specific_diagnosis_with_matching_evidence(url):
    snapshot, candidate = example()
    snapshot, candidate = with_field(snapshot, candidate, "official_url", url)
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert isinstance(report, ValidationReport)
    assert "invalid_official_url" in {i.code for i in report.issues}
    assert "unverifiable_evidence" not in {i.code for i in report.issues}


def test_cross_document_claim_is_not_verified_by_equal_urls():
    snapshot, candidate = example()
    target = DocumentUnit(snapshot_id=UUID(int=77), pointer="")
    relation = CrossDocumentReference(
        origin=candidate.unit,
        target=target,
        relationship="detail",
        link_evidence=candidate.assertions[1].evidence[0],
    )
    candidate = OpportunityCandidate.model_validate(
        {**candidate.model_dump(), "references": (relation,)}
    )
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert isinstance(report, ValidationReport)
    assert "cross_document_relationship_unverified" in {i.code for i in report.issues}
    assert report.candidate.references == (relation,)


def test_external_report_even_with_plausible_diagnostics_never_authorizes_promotion():
    snapshot, candidate = example()
    evidence = tuple(e for a in candidate.assertions for e in a.evidence)
    forged = ValidationReport(
        candidate=candidate,
        snapshots=(snapshot,),
        reference_date=DAY,
        decision=ValidationDecision.ACCEPTED,
        issues=(
            ValidationIssue(
                code="instrument_verified",
                message="Caller assertion, not proof",
                rule_id="instrument_verified",
                evidence=evidence,
            ),
        ),
    )
    assert not forged.promotable
    restored = ValidationReport.model_validate_json(forged.model_dump_json())
    assert not restored.promotable
    actual = validate(
        restored.candidate, restored.snapshots, reference_date=restored.reference_date
    )
    assert actual.decision == ValidationDecision.REVIEW


def test_mutating_report_candidate_without_updating_retained_audit_is_rejected():
    snapshot, candidate = example()
    report = validate(candidate, (snapshot,), reference_date=DAY)
    data = json.loads(report.model_dump_json())
    data["candidate"]["id"] = str(UUID(int=100))
    with pytest.raises(ValidationError, match="audit"):
        ValidationReport.model_validate_json(json.dumps(data))


def test_old_contract_version_is_not_silently_upgraded():
    _, candidate = example()
    with pytest.raises(ValidationError):
        OpportunityCandidate.model_validate({**candidate.model_dump(), "schema_version": 1})


@pytest.mark.parametrize(
    "value",
    [
        {"kind": "boolean", "data": 1},
        {"kind": "text", "data": True},
        {"kind": "date", "data": "not a date"},
        {"kind": "decimal", "data": "NaN"},
        {"kind": "unknown", "data": "test"},
        {"kind": "null", "data": ""},
        {"kind": "text", "data": "\ud800"},
        {"kind": "text", "data": "x", "extra": 1},
    ],
)
def test_malformed_typed_scalar_is_rejected_at_boundary(value):
    with pytest.raises(ValidationError):
        FieldAssertion.model_validate({"field": "title", "value": value})
