"""Regressions from independent M2.2a review: canonical DTO validation, not factory-only."""

import json

import pytest
from pydantic import ValidationError

from editalfinder_v2.domain.temporal_models import NormalizedTemporalEvent, TemporalClaim


@pytest.mark.parametrize("transport", ["constructor", "python", "json"])
@pytest.mark.parametrize(
    "changes,message",
    [
        ({"timezone": "-00:00"}, "Unknown timezone"),
        ({"timezone": None}, "Unknown timezone"),
        ({"timezone": "+03:00"}, "Timezone offset"),
        ({"timezone": "Europe/Paris"}, "Timezone label"),
        ({"timezone": "+01:99"}, "Timezone label"),
        ({"timezone": "+24:00"}, "Timezone label"),
        ({"timezone": "+٠١:00"}, "Timezone label"),
        ({"instant_utc": "2026-01-01T15:30:00+03:00"}, "UTC instant"),
        ({"instant_utc": "2026-01-01T12:31:00Z"}, "UTC instant"),
    ],
)
def test_public_temporal_dto_rejects_inconsistent_timezone_and_utc(
    changes: dict[str, object], message: str, transport: str
) -> None:
    values = dict(
        claim=TemporalClaim(role="submission_deadline").model_dump(mode="json"),
        local_datetime="2026-01-01T12:30:00Z",
        instant_utc="2026-01-01T12:30:00Z",
        timezone="Z",
        precision="minute",
        calendar_interpretation="gregorian",
    )
    values.update(changes)
    with pytest.raises(ValidationError, match=message):
        if transport == "constructor":
            NormalizedTemporalEvent(**values)
        elif transport == "python":
            NormalizedTemporalEvent.model_validate(values)
        else:
            NormalizedTemporalEvent.model_validate_json(json.dumps(values))


@pytest.mark.parametrize("transport", ["constructor", "python", "json"])
@pytest.mark.parametrize("digits", range(1, 6))
def test_fractional_source_precision_cannot_gain_finer_digits(digits: int, transport: str) -> None:
    values = dict(
        claim=TemporalClaim(role="submission_deadline").model_dump(mode="json"),
        local_datetime="2026-01-01T12:30:00.123456Z",
        timezone="Z",
        precision="fractional_second",
        fractional_digits=digits,
        calendar_interpretation="gregorian",
    )
    with pytest.raises(ValidationError, match="Fractional precision"):
        if transport == "constructor":
            NormalizedTemporalEvent(**values)
        elif transport == "python":
            NormalizedTemporalEvent.model_validate(values)
        else:
            NormalizedTemporalEvent.model_validate_json(json.dumps(values))


@pytest.mark.parametrize("zone", [None, "-00:00"])
def test_naive_local_time_retains_unknown_zone_without_utc(zone: str | None) -> None:
    event = NormalizedTemporalEvent(
        claim=TemporalClaim(role="submission_deadline"),
        local_datetime="2026-01-01T12:30:00",
        timezone=zone,
        precision="minute",
        calendar_interpretation="gregorian",
    )
    assert event.instant_utc is None
    assert event.local_datetime.tzinfo is None
    assert NormalizedTemporalEvent.model_validate_json(event.model_dump_json()) == event


@pytest.mark.parametrize("digits", range(1, 7))
def test_exact_declared_fractional_precision_and_utc_roundtrip(digits: int) -> None:
    original = "2026-01-01T12:30:00." + "1" * digits + "Z"
    event = NormalizedTemporalEvent(
        claim=TemporalClaim(role="submission_deadline"),
        local_datetime=original,
        instant_utc=original,
        timezone="Z",
        precision="fractional_second",
        fractional_digits=digits,
        calendar_interpretation="gregorian",
    )
    assert NormalizedTemporalEvent.model_validate_json(event.model_dump_json()) == event


def test_offset_cross_day_and_utc_are_consistent() -> None:
    event = NormalizedTemporalEvent(
        claim=TemporalClaim(role="submission_deadline"),
        local_datetime="2026-01-01T01:00:00+14:00",
        instant_utc="2025-12-31T11:00:00Z",
        timezone="+14:00",
        precision="minute",
        calendar_interpretation="gregorian",
    )
    assert NormalizedTemporalEvent.model_validate_json(event.model_dump_json()) == event
