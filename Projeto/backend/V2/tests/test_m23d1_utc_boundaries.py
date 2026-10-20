"""F01: UTC representational overflow must cross the structured Pydantic boundary."""

import json
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import pytest
from m23c_fixtures import build, case_by_id
from pydantic import ValidationError

from editalfinder_v2.domain.integration_models import IntegrationInput
from editalfinder_v2.domain.models import RawSnapshot, ReviewAttestation

EXTREMES = ("0001-01-01T00:00:00+23:59", "9999-12-31T23:59:59-23:59")


def timestamp_input(model: type[RawSnapshot] | type[ReviewAttestation], stamp: Any) -> dict:
    if model is RawSnapshot:
        return dict(
            id=str(UUID(int=1)),
            source_id=str(UUID(int=2)),
            source_code="fapergs",
            execution_id=str(UUID(int=3)),
            collected_at=stamp,
            collector_version="m23d1-synthetic",
            url="https://example.org/",
            payload_json="{}",
        )
    return dict(
        id=str(UUID(int=4)),
        reviewer_identity="untrusted-synthetic",
        reviewed_at=stamp,
        candidate_id=str(UUID(int=5)),
        candidate_digest="0" * 64,
        evidence_digests=["0" * 64],
        policy_version="untrusted-test",
        decision="REVIEW",
        provenance="synthetic, not authorization",
    )


def construct(model, data, route):
    if route == "direct":
        return model(**data)
    if route == "python":
        return model.model_validate(data)
    return model.model_validate_json(json.dumps(data))


@pytest.mark.parametrize("model", [RawSnapshot, ReviewAttestation])
@pytest.mark.parametrize("route", ["direct", "python", "json"])
@pytest.mark.parametrize("stamp", EXTREMES)
def test_utc_overflow_is_a_deterministic_validation_error(model, route, stamp):
    errors = []
    for _ in range(2):
        with pytest.raises(ValidationError) as exc:
            construct(model, timestamp_input(model, stamp), route)
        errors.append(
            exc.value.errors(include_input=False, include_context=False, include_url=False)
        )
    field = "collected_at" if model is RawSnapshot else "reviewed_at"
    assert (
        errors[0]
        == errors[1]
        == [
            {
                "type": "value_error",
                "loc": (field,),
                "msg": "Value error, UTC timestamp is outside the representable datetime range",
            }
        ]
    )


@pytest.mark.parametrize("model", [RawSnapshot, ReviewAttestation])
@pytest.mark.parametrize("stamp", EXTREMES)
def test_python_datetime_overflow_is_also_structured(model, stamp):
    with pytest.raises(ValidationError, match="UTC timestamp is outside"):
        model.model_validate(timestamp_input(model, datetime.fromisoformat(stamp)))


@pytest.mark.parametrize("route", ["python", "json"])
@pytest.mark.parametrize("stamp", EXTREMES)
def test_nested_snapshot_utc_overflow_preserves_error_location(route, stamp):
    raw = json.loads(build(case_by_id("M23C-A-001")).model_dump_json())
    raw["candidates"][0]["context"]["snapshots"][0]["collected_at"] = stamp
    if route == "python":
        raw["reference_date"] = datetime.fromisoformat(raw["reference_date"]).date()
    with pytest.raises(ValidationError) as exc:
        construct(IntegrationInput, raw, route)
    assert any(
        e["loc"] == ("candidates", 0, "context", "snapshots", 0, "collected_at")
        and e["type"] == "value_error"
        and "UTC timestamp is outside" in e["msg"]
        for e in exc.value.errors(include_input=False)
    )


@pytest.mark.parametrize("model", [RawSnapshot, ReviewAttestation])
@pytest.mark.parametrize("route", ["direct", "python", "json"])
@pytest.mark.parametrize(
    ("stamp", "expected"),
    [
        ("0001-01-02T00:00:00+23:59", "0001-01-01T00:01:00+00:00"),
        ("9999-12-30T23:59:59-23:59", "9999-12-31T23:58:59+00:00"),
        ("0001-01-01T00:00:00-23:59", "0001-01-01T23:59:00+00:00"),
        ("9999-12-31T23:59:59+23:59", "9999-12-31T00:00:59+00:00"),
        ("2026-03-12T10:15:30-03:00", "2026-03-12T13:15:30+00:00"),
        ("2026-03-12T10:15:30Z", "2026-03-12T10:15:30+00:00"),
    ],
)
def test_representable_timestamp_converts_without_clamping(model, route, stamp, expected):
    result = construct(model, timestamp_input(model, stamp), route)
    value = result.collected_at if model is RawSnapshot else result.reviewed_at
    assert value.isoformat() == expected
    assert value.tzinfo is UTC


@pytest.mark.parametrize("model", [RawSnapshot, ReviewAttestation])
@pytest.mark.parametrize("route", ["direct", "python", "json"])
def test_naive_timestamps_remain_invalid(model, route):
    with pytest.raises(ValidationError) as exc:
        construct(model, timestamp_input(model, "2026-03-12T10:15:30"), route)
    assert exc.value.errors(include_input=False)[0]["type"] == "timezone_aware"
