"""Full-result integrity against a retained envelope, not authentication."""

import hashlib
import json
from datetime import UTC, date, datetime
from uuid import UUID

import pytest
from fixtures import example
from pydantic import ValidationError

from editalfinder_v2.domain.models import (
    ReviewAttestation,
    ValidationDecision,
    ValidationReport,
    contract_digest,
)
from editalfinder_v2.domain.validation import validate

DAY = date(2026, 6, 1)


def audited_report():
    snapshot, candidate = example(deadline=date(2025, 1, 1))
    claim = ReviewAttestation(
        id=UUID(int=500),
        reviewer_identity="synthetic-reviewer",
        reviewed_at=datetime(2026, 6, 1, tzinfo=UTC),
        candidate_id=candidate.id,
        candidate_digest=contract_digest(candidate),
        evidence_digests=(contract_digest(candidate.assertions[0].evidence[0]),),
        policy_version="unapproved",
        decision=ValidationDecision.REVIEW,
        provenance="untrusted caller",
    )
    report = validate(candidate, (snapshot,), reference_date=DAY, review_attestations=(claim,))
    assert isinstance(report, ValidationReport)
    return report


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("temporal_status",), "nao_determinada"),
        (("reference_date",), "2027-01-01"),
        (("issues", 1, "message"), "texto adulterado"),
        (("issues", 1, "code"), "different_code"),
        (("issues", 1, "field"), "title"),
        (("issues", 1, "related_fields"), ["title"]),
        (("issues", 1, "evidence"), []),
        (("issues", 1, "evidence", 0, "quote"), "alterado"),
        (("review_attestations", 0, "reviewer_identity"), "someone else"),
        (("review_attestations",), []),
        (("snapshots", 0, "collector_version"), "other collector"),
        (("audit", "catalog_version"), "different catalog"),
        (("audit", "report_digest"), "0" * 64),
        (("audit", "validation_limits_version"), "unapproved"),
        (("issues", 1, "rule_id"), "different_rule"),
    ],
)
@pytest.mark.parametrize("transport", ["python", "json"])
def test_each_result_mutation_rejects_retained_audit(path, replacement, transport):
    report = audited_report()
    data = json.loads(report.model_dump_json())
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = replacement
    with pytest.raises(ValidationError, match="audit"):
        if transport == "json":
            ValidationReport.model_validate_json(json.dumps(data))
        else:
            ValidationReport.model_validate(data)


def test_decision_mutation_rejects_retained_audit_without_other_invariant_failure():
    report = audited_report()
    data = report.model_dump(exclude={"audit"})
    data["issues"] = (
        {"code": "non_opportunity", "message": "Not an instrument", "rule_id": "non_opportunity"},
    )
    data["decision"] = "REJECTED"
    rejected = ValidationReport.model_validate(data)
    tampered = json.loads(rejected.model_dump_json())
    tampered["decision"] = "REVIEW"  # Both decisions satisfy structural invariants.
    with pytest.raises(ValidationError, match="audit"):
        ValidationReport.model_validate(tampered)


def test_full_result_digest_has_explicit_representation_and_no_circular_audit():
    report = audited_report()
    expected = hashlib.sha256(report.model_dump_json(exclude={"audit"}).encode("utf-8")).hexdigest()
    assert report.audit is not None
    assert report.audit.report_digest == expected
    assert report.audit.report_hash_version == "pydantic-report-json-utf8-v1"
    assert ValidationReport.model_validate(report.model_dump()) == report
    assert ValidationReport.model_validate_json(report.model_dump_json()) == report
    assert not report.promotable


def test_reordering_diagnostics_is_detected():
    data = json.loads(audited_report().model_dump_json())
    data["issues"].reverse()
    with pytest.raises(ValidationError, match="audit"):
        ValidationReport.model_validate(data)


def test_recomputed_envelope_is_not_authentication():
    report = audited_report()
    data = report.model_dump(exclude={"audit"})
    data["reference_date"] = date(2027, 1, 1)
    rebuilt = ValidationReport.model_validate(data)
    assert rebuilt.audit != report.audit
    assert not rebuilt.promotable


def test_incomplete_old_envelope_is_not_silently_upgraded():
    data = json.loads(audited_report().model_dump_json())
    for key in (
        "report_digest",
        "report_hash_version",
        "audit_version",
        "validation_limits_version",
    ):
        del data["audit"][key]
    with pytest.raises(ValidationError, match="report_digest"):
        ValidationReport.model_validate(data)
