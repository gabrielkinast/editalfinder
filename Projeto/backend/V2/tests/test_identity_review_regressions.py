"""Regressions for the three independent identity review findings."""

import json
from datetime import timedelta
from uuid import UUID

import pytest
from test_identity import codes, subject

from editalfinder_v2.domain.identity_models import IdentityResolutionReport, IdentitySubject
from editalfinder_v2.domain.identity_normalization import normalize_identifier
from editalfinder_v2.domain.identity_resolution import resolve_identity
from editalfinder_v2.domain.models import OperationalError
from editalfinder_v2.domain.url_identity import normalize_url


@pytest.mark.parametrize(
    "fields",
    [
        ("official_identifier",),
        ("publication_cycle",),
        ("official_identifier", "publication_cycle"),
    ],
)
@pytest.mark.parametrize("reverse", [False, True])
def test_boolean_payload_cannot_prove_textual_identity(fields, reverse):
    left = subject(1, official="true", cycle="false")
    raw = subject(2, official="true", cycle="false").model_dump()
    snapshot = raw["snapshots"][0]
    payload = json.loads(snapshot["payload_json"])
    for field in fields:
        payload["record"][field] = field == "official_identifier"
    snapshot["payload_json"] = json.dumps(payload)
    snapshot.pop("audit")
    right = IdentitySubject.model_validate(raw)
    report = resolve_identity(right, left) if reverse else resolve_identity(left, right)
    assert isinstance(report, IdentityResolutionReport)
    assert report.decision == "insufficient_information"
    assert codes(report) == {"identity_evidence_invalid"}


@pytest.mark.parametrize(
    "mutation", ["payload", "url", "collected_at", "collector_version", "execution", "source"]
)
@pytest.mark.parametrize("reverse", [False, True])
def test_shared_snapshot_uuid_requires_identical_context(mutation, reverse):
    left = subject(1)
    raw = subject(1).model_dump()
    snapshot = raw["snapshots"][0]
    if mutation == "payload":
        raw = subject(1, url="https://example.org/different").model_dump()
    elif mutation == "url":
        snapshot["url"] = "https://example.org/other-fetch"
    elif mutation == "collected_at":
        snapshot["collected_at"] += timedelta(seconds=1)
    elif mutation == "collector_version":
        snapshot["collector_version"] = "synthetic-identity-2"
    elif mutation == "execution":
        snapshot["execution_id"] = UUID(int=999)
        for identifier in raw["identifiers"]:
            identifier["provenance"]["execution_id"] = snapshot["execution_id"]
        raw["cycle"]["provenance"]["execution_id"] = snapshot["execution_id"]
    else:
        snapshot["source_code"] = "other-source-code"
        raw["candidate"]["source_code"] = snapshot["source_code"]
    right = IdentitySubject.model_validate(raw)
    # Each subject is internally valid; only the pair has conflicting context.
    self_report = resolve_identity(right, right)
    assert isinstance(self_report, IdentityResolutionReport)
    assert self_report.decision == "exact_match"
    report = resolve_identity(right, left) if reverse else resolve_identity(left, right)
    assert isinstance(report, OperationalError)
    assert report.code == "identity_snapshot_context_conflict"
    assert report.stage == "identity"


def test_identical_shared_snapshot_is_accepted():
    left = subject(1)
    right = IdentitySubject.model_validate_json(left.model_dump_json())
    assert left.snapshots == right.snapshots
    assert left.snapshots[0] is not right.snapshots[0]
    report = resolve_identity(left, right)
    assert isinstance(report, IdentityResolutionReport)
    assert report.decision == "exact_match"


@pytest.mark.parametrize("scheme", ["httpſ", "HTTPſ"])
@pytest.mark.parametrize("port", ["", ":443"])
@pytest.mark.parametrize("api", ["url", "identifier", "identity"])
def test_unicode_scheme_is_rejected_without_crashing(scheme, port, api):
    url = f"{scheme}://example.com{port}/call"
    if api == "url":
        result = normalize_url(url)
        assert result.code == "url_invalid"
        assert result.normalized is None
    elif api == "identifier":
        result = normalize_identifier(subject(1, url=url).identifiers[-1])
        assert result.normalization_code == "identifier_url_invalid"
        assert result.normalized is None
    else:
        report = resolve_identity(subject(1, url=url), subject(2))
        assert isinstance(report, IdentityResolutionReport)
        assert report.decision == "insufficient_information"
        assert codes(report) == {"identifier_url_invalid"}


def test_ascii_scheme_keeps_unicode_hostname_and_path_supported():
    url = "HTTPS://café.example:443/ação"
    result = normalize_url(url)
    assert result.code == "url_normalized"
    assert result.normalized == "https://xn--caf-dma.example/ação"
    identifier = normalize_identifier(subject(1, url=url).identifiers[-1])
    assert identifier.normalized == result.normalized
    report = resolve_identity(subject(1, url=url), subject(2, url=url))
    assert isinstance(report, IdentityResolutionReport)
    assert report.decision == "exact_match"


def test_textual_boolean_labels_still_match():
    report = resolve_identity(
        subject(1, official="true", cycle="false"),
        subject(2, official="true", cycle="false"),
    )
    assert isinstance(report, IdentityResolutionReport)
    assert report.decision == "exact_match"
