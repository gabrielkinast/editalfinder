"""Adversarial regressions for M1.1. All inputs are synthetic."""

import json
from datetime import date
from decimal import Decimal

import pytest
from fixtures import example, multiple_candidates

from editalfinder_v2.domain.models import (
    FieldAssertion,
    OpportunityCandidate,
    ValidationReport,
)
from editalfinder_v2.domain.validation import validate

DAY = date(2026, 6, 1)


def test_json_schema_describes_the_actual_tagged_scalar_transport():
    schema = FieldAssertion.model_json_schema(mode="serialization")
    assert schema["properties"]["value"]["discriminator"]["propertyName"] == "kind"
    validation_schema = FieldAssertion.model_json_schema(mode="validation")
    variants = validation_schema["properties"]["value"]["anyOf"]
    assert any(v.get("discriminator", {}).get("propertyName") == "kind" for v in variants)


@pytest.mark.parametrize("field", ["pointer", "quote", "method_version"])
def test_invalid_unicode_cannot_reach_audit_serialization(field):
    from pydantic import ValidationError

    from editalfinder_v2.domain.models import Evidence

    _, candidate = example()
    with pytest.raises(ValidationError, match="UTF-8|unicode"):
        Evidence.model_validate(
            {**candidate.assertions[0].evidence[0].model_dump(), field: "\ud800"}
        )


def test_report_audit_binds_snapshot_set():
    from pydantic import ValidationError

    snapshot, candidate = example()
    report = validate(candidate, (snapshot,), reference_date=DAY)
    data = json.loads(report.model_dump_json())
    assert data["audit"]["snapshots"][0]["payload_digest"] == snapshot.hash_payload
    data["snapshots"] = []
    with pytest.raises(ValidationError, match="audit"):
        ValidationReport.model_validate_json(json.dumps(data))


def test_optional_mapping_without_approved_semantics_is_explicit():
    from editalfinder_v2.domain.models import Evidence, RawSnapshot

    snapshot, candidate = example()
    payload = json.loads(snapshot.payload_json)
    payload["geographic_scope"] = "internacional"
    snapshot = RawSnapshot.model_validate(
        {
            **snapshot.model_dump(exclude={"audit"}),
            "payload_json": json.dumps(payload),
        }
    )
    evidence = Evidence.model_validate(
        {
            **candidate.assertions[0].evidence[0].model_dump(),
            "pointer": "/geographic_scope",
            "quote": "internacional",
            "semantic_role": "geographic_scope",
        }
    )
    candidate = OpportunityCandidate.model_validate(
        {
            **candidate.model_dump(),
            "assertions": candidate.assertions
            + (
                FieldAssertion(
                    field="geographic_scope", value="internacional", evidence=(evidence,)
                ),
            ),
        }
    )
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert "semantic_mapping_not_approved" in {i.code for i in report.issues}


def test_missing_identity_diagnostics_are_not_hidden_by_trust_block():
    snapshot, candidate = example()
    candidate = OpportunityCandidate.model_validate(
        {
            **candidate.model_dump(),
            "assertions": tuple(a for a in candidate.assertions if a.field != "title"),
        }
    )
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert "missing_title" in {i.code for i in report.issues}


@pytest.mark.parametrize(
    "role",
    [
        "country_origin",
        "geographic_execution",
        "beneficiaries",
        "organization_location",
        "country_of_origin",
        "total_budget",
        "result_date",
    ],
)
def test_optional_field_cannot_relabel_an_unrelated_scalar(role):
    from editalfinder_v2.domain.models import Evidence, RawSnapshot

    snapshot, candidate = example()
    payload = json.loads(snapshot.payload_json)
    payload[role] = "internacional"
    snapshot = RawSnapshot.model_validate(
        {
            **snapshot.model_dump(exclude={"audit"}),
            "payload_json": json.dumps(payload),
        }
    )
    evidence = Evidence.model_validate(
        {
            **candidate.assertions[0].evidence[0].model_dump(),
            "pointer": "/" + role,
            "quote": "internacional",
            "semantic_role": "geographic_scope",
        }
    )
    candidate = OpportunityCandidate.model_validate(
        {
            **candidate.model_dump(),
            "assertions": candidate.assertions
            + (
                FieldAssertion(
                    field="geographic_scope", value="internacional", evidence=(evidence,)
                ),
            ),
        }
    )
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert "evidence_role_mismatch" in {i.code for i in report.issues}
    assert report.decision == "REVIEW"


def test_self_declared_attestation_does_not_authorize_acceptance():
    from datetime import UTC, datetime
    from uuid import UUID

    from editalfinder_v2.domain.models import ReviewAttestation, contract_digest

    snapshot, candidate = example()
    claim = ReviewAttestation(
        id=UUID(int=500),
        reviewer_identity="synthetic-reviewer",
        reviewed_at=datetime(2026, 6, 1, tzinfo=UTC),
        candidate_id=candidate.id,
        candidate_digest=contract_digest(candidate),
        evidence_digests=tuple(
            contract_digest(e) for a in candidate.assertions for e in a.evidence
        ),
        policy_version="unapproved",
        decision="ACCEPTED",
        provenance="untrusted caller",
    )
    report = validate(candidate, (snapshot,), reference_date=DAY, review_attestations=(claim,))
    assert report.decision == "REVIEW"
    assert "untrusted_review_attestation" in {i.code for i in report.issues}
    assert report.review_attestations == (claim,)
    assert not report.promotable


def test_report_records_catalog_candidate_and_evidence_digests():
    snapshot, candidate = example()
    report = validate(candidate, (snapshot,), reference_date=DAY)
    data = json.loads(report.model_dump_json())
    assert data["audit"]["catalog_version"] == "seeds-000002"
    assert data["audit"]["candidate_id"] == str(candidate.id)
    assert len(data["audit"]["candidate_digest"]) == 64
    assert len(data["audit"]["evidence_digests"]) == 6
    assert ValidationReport.model_validate_json(report.model_dump_json()) == report


def test_hash_envelope_is_serialized_and_tampering_is_rejected():
    from pydantic import ValidationError

    from editalfinder_v2.domain.models import RawSnapshot

    snapshot, _ = example()
    data = json.loads(snapshot.model_dump_json())
    assert data["audit"]["payload_digest"] == snapshot.hash_payload
    assert data["audit"]["snapshot_id"] == str(snapshot.id)
    assert data["audit"]["algorithm"] == "sha256"
    assert data["audit"]["hash_version"] == "sha256-utf8-v1"
    data["payload_json"] += " "
    with pytest.raises(ValidationError, match="audit"):
        RawSnapshot.model_validate_json(json.dumps(data))


def test_arbitrary_accepted_report_is_not_promotion_authority():
    from pydantic import ValidationError

    _, candidate = example()
    try:
        report = ValidationReport(
            candidate=candidate,
            snapshots=(),
            reference_date=DAY,
            decision="ACCEPTED",
            issues=(),
        )
    except ValidationError:
        return
    assert not report.promotable


def test_manual_label_is_not_human_review_authority():
    snapshot, candidate = example()
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert "trusted_review_required" in {i.code for i in report.issues}
    assert report.decision == "REVIEW"
    assert not report.promotable


def test_cross_record_evidence_cannot_form_one_instrument():
    snapshot, (instrument, news) = multiple_candidates()
    mixed = OpportunityCandidate.model_validate(
        {
            **instrument.model_dump(),
            "assertions": tuple(
                next(n for n in news.assertions if n.field == a.field)
                if a.field in {"title", "official_url"}
                else a
                for a in instrument.assertions
            ),
        }
    )
    report = validate(mixed, (snapshot,), reference_date=DAY)
    assert "evidence_scope_mismatch" in {i.code for i in report.issues}
    assert report.decision == "REVIEW"


def test_invalid_title_date_cannot_change_decision_in_json_transport():
    snapshot, candidate = example()
    payload = json.loads(snapshot.payload_json)
    payload["title"] = "2026-01-01"
    snapshot = type(snapshot).model_validate(
        {**snapshot.model_dump(exclude={"audit"}), "payload_json": json.dumps(payload)}
    )
    original = candidate.assertions[0]
    evidence = original.evidence[0].model_dump()
    evidence["quote"] = payload["title"]
    assertion = FieldAssertion(field="title", value=date(2026, 1, 1), evidence=(evidence,))
    candidate = OpportunityCandidate.model_validate(
        {**candidate.model_dump(), "assertions": (assertion,) + candidate.assertions[1:]}
    )
    before = validate(candidate, (snapshot,), reference_date=DAY)
    restored = OpportunityCandidate.model_validate_json(candidate.model_dump_json())
    after = validate(restored, (snapshot,), reference_date=DAY)
    assert type(restored.assertions[0].value) is date
    assert before == after
    assert "invalid_field_value" in {i.code for i in after.issues}


@pytest.mark.parametrize("value", ["2026-01-01", date(2026, 1, 1), True, Decimal("1.20"), None])
def test_scalar_types_survive_json_roundtrip(value):
    assertion = FieldAssertion(field="title", value=value)
    restored = FieldAssertion.model_validate_json(assertion.model_dump_json())
    assert type(restored.value) is type(value)
    assert restored == assertion


def test_structurally_valid_fixture_has_only_trust_diagnostics():
    snapshot, candidate = example()
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert {i.code for i in report.issues} == {"trusted_review_required"}
    assert {i.field for i in report.issues} == {
        "content_kind",
        "specific_instrument",
        "actionable",
    }


@pytest.mark.parametrize("prefix", ["", "/records", "/records/0"])
def test_forging_same_unit_for_all_evidence_does_not_hide_cross_record_paths(prefix):
    from editalfinder_v2.domain.models import DocumentUnit, Evidence

    snapshot, (instrument, news) = multiple_candidates()
    unit = DocumentUnit(snapshot_id=snapshot.id, pointer=prefix)
    assertions = tuple(
        FieldAssertion.model_validate(
            {
                **a.model_dump(),
                "evidence": tuple(
                    Evidence.model_validate({**e.model_dump(), "unit": unit}) for e in a.evidence
                ),
            }
        )
        for a in tuple(news.assertions[:2]) + tuple(instrument.assertions[2:])
    )
    candidate = OpportunityCandidate.model_validate(
        {
            **instrument.model_dump(),
            "unit": unit,
            "assertions": assertions,
        }
    )
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert "evidence_role_mismatch" in {i.code for i in report.issues}
    assert report.decision == "REVIEW"


@pytest.mark.parametrize("extra", ["duplicate", "null", "conflict"])
def test_order_and_duplicate_assertions_do_not_resolve_conflicts(extra):
    snapshot, candidate = example()
    title = candidate.assertions[0]
    addition = (
        title
        if extra == "duplicate"
        else FieldAssertion(
            field="title",
            value=None if extra == "null" else "Conflicting title",
            evidence=() if extra == "null" else title.evidence,
        )
    )
    assertions = candidate.assertions + (addition,)
    outcomes = []
    for sequence in (assertions, tuple(reversed(assertions))):
        modified = OpportunityCandidate.model_validate(
            {**candidate.model_dump(), "assertions": sequence}
        )
        restored = OpportunityCandidate.model_validate_json(modified.model_dump_json())
        report = validate(modified, (snapshot,), reference_date=DAY)
        assert validate(restored, (snapshot,), reference_date=DAY) == report
        codes = sorted((i.code, i.field or "") for i in report.issues)
        outcomes.append((report.decision, codes))
        assert (
            ("conflicting_assertions", "title") in codes
            if extra == "conflict"
            else ("conflicting_assertions", "title") not in codes
        )
    assert outcomes[0] == outcomes[1]


def test_candidates_on_one_snapshot_do_not_share_identity_or_issues():
    snapshot, candidates = multiple_candidates()
    reports = [validate(c, (snapshot,), reference_date=DAY) for c in candidates]
    for report, candidate in zip(reports, candidates, strict=True):
        assert report.candidate == candidate
        assert {i.code for i in report.issues} == {"trusted_review_required"}
        assert all(e.unit == candidate.unit for i in report.issues for e in i.evidence)
    assert reports[0].audit.candidate_digest != reports[1].audit.candidate_digest


@pytest.mark.parametrize("value", [date(2026, 1, 1), Decimal("1.2"), True, "2026-01-01", None])
@pytest.mark.parametrize("field", ["title", "submission_deadline", "actionable", "maximum_amount"])
def test_decision_and_diagnostics_stable_for_supported_scalar_types(field, value):
    snapshot, candidate = example()
    assertion = FieldAssertion(field=field, value=value, evidence=candidate.assertions[0].evidence)
    modified = OpportunityCandidate.model_validate(
        {
            **candidate.model_dump(),
            "assertions": tuple(a for a in candidate.assertions if a.field != field) + (assertion,),
        }
    )
    restored = OpportunityCandidate.model_validate_json(modified.model_dump_json())
    assert validate(modified, (snapshot,), reference_date=DAY) == validate(
        restored,
        (snapshot,),
        reference_date=DAY,
    )
