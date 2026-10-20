"""Identity boundary, deterministic normalization and resource regressions."""

from uuid import UUID

import pytest
from pydantic import ValidationError
from test_identity import codes, subject

from editalfinder_v2.domain.identity_models import ExternalIdentifier, IdentitySubject
from editalfinder_v2.domain.identity_normalization import normalize_identifier
from editalfinder_v2.domain.identity_resolution import resolve_identity
from editalfinder_v2.domain.models import OperationalError


@pytest.mark.parametrize("count", [100, 1000, 10_000, 10_001])
def test_identifier_budget_is_inclusive_and_duplicates_do_not_create_pair_products(count):
    left = subject(1)
    right = subject(2)
    left = IdentitySubject.model_validate(
        {**left.model_dump(), "identifiers": (left.identifiers[0],) * count}
    )
    right = IdentitySubject.model_validate(
        {**right.model_dump(), "identifiers": (right.identifiers[0],) * count}
    )
    report = resolve_identity(left, right)
    if count > 10_000:
        assert isinstance(report, OperationalError)
        assert report.code == "identity_limits_exceeded"
        assert report.stage == "identity"
    else:
        assert report.decision == "exact_match"
        assert len(report.left_identifiers) == count
        assert len(report.supporting_evidence) == 4


@pytest.mark.parametrize(
    "mutation", ["cycle_proof", "ambiguous", "missing_snapshot", "source_field"]
)
def test_unsupported_identity_context_has_specific_invalid_evidence_diagnosis(mutation):
    raw = subject(2).model_dump()
    if mutation == "cycle_proof":
        raw["cycle"]["provenance"] = raw["identifiers"][0]["provenance"]
    elif mutation == "ambiguous":
        raw["candidate"]["assertions"][0]["ambiguous"] = True
    elif mutation == "missing_snapshot":
        raw["snapshots"] = ()
    else:
        raw["identifiers"][0]["source_id"] = UUID(int=999)
    report = resolve_identity(subject(1), IdentitySubject.model_validate(raw))
    assert report.decision == "insufficient_information"
    assert "identity_evidence_invalid" in codes(report)


@pytest.mark.parametrize("problem", ["duplicate", "invalid_json"])
def test_snapshot_operational_errors_have_no_semantic_decision(problem):
    raw = subject(2).model_dump()
    if problem == "duplicate":
        raw["snapshots"] *= 2
    else:
        raw["snapshots"][0]["payload_json"] = '{"invalid":1e999}'
        raw["snapshots"][0].pop("audit")
    report = resolve_identity(subject(1), IdentitySubject.model_validate(raw))
    assert isinstance(report, OperationalError)
    assert report.code == (
        "identity_duplicate_snapshot_id"
        if problem == "duplicate"
        else "identity_invalid_snapshot_json"
    )
    assert not report.promotable


@pytest.mark.parametrize("original", ["001/2026", " A-01 ", "Ａ-01", "ß", "Cafe\u0301"])
@pytest.mark.parametrize("policy", ["opaque-exact-v1", "opaque-nfc-v1"])
def test_opaque_normalization_is_idempotent_and_keeps_version(original, policy):
    raw = subject(1).identifiers[0].model_dump()
    raw.update(original=original, normalization_version=policy)
    first = normalize_identifier(ExternalIdentifier.model_validate(raw))
    assert normalize_identifier(first) == first
    raw["original"] = first.normalized
    second = normalize_identifier(ExternalIdentifier.model_validate(raw))
    assert second.normalized == first.normalized
    assert first.normalization_version == policy
    assert first.original == original


def test_unknown_normalization_version_is_not_silently_upgraded():
    raw = subject(1).identifiers[0].model_dump()
    raw["normalization_version"] = "future-version"
    with pytest.raises(ValidationError, match="normalization_version"):
        ExternalIdentifier.model_validate(raw)


def test_cycle_preserves_exact_original_and_rejects_a_forged_normalized_label():
    from editalfinder_v2.domain.identity_models import PublicationCycle

    cycle = subject(1).cycle
    assert cycle.normalized == cycle.original
    assert PublicationCycle.model_validate_json(cycle.model_dump_json()) == cycle
    raw = cycle.model_dump()
    raw["normalized"] = "2027"
    with pytest.raises(ValidationError, match="cycle normalization"):
        PublicationCycle.model_validate(raw)
