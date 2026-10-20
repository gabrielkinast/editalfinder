"""M2.2a.1: known offsets cannot silently omit their representable UTC instant."""

import hashlib
import json
from datetime import UTC, date, datetime, timedelta, timezone
from typing import Any

import pytest
from pydantic import ValidationError
from semantic_fixtures import build_context

from editalfinder_v2.domain.temporal_models import (
    NormalizedTemporalEvent,
    TemporalClaim,
    TemporalInput,
    TemporalReport,
)
from editalfinder_v2.domain.temporal_normalization import normalize_temporal


def event_payload(local: str, zone: str | None) -> dict[str, object]:
    return {
        "claim": {"role": "submission_deadline"},
        "local_datetime": local,
        "timezone": zone,
        "precision": "minute",
        "calendar_interpretation": "gregorian",
    }


def validate(values: dict[str, object], transport: str) -> NormalizedTemporalEvent:
    if transport == "constructor":
        return NormalizedTemporalEvent(**values)
    if transport == "python":
        return NormalizedTemporalEvent.model_validate(values)
    return NormalizedTemporalEvent.model_validate_json(json.dumps(values))


@pytest.mark.parametrize("transport", ["constructor", "python", "json"])
@pytest.mark.parametrize("zone", ["+03:00", "-03:00", "+00:00", "Z"])
def test_known_offset_requires_representable_utc(zone: str, transport: str) -> None:
    data = event_payload("2026-05-10T12:30:00" + zone, zone)
    with pytest.raises(ValidationError, match="UTC instant is required"):
        validate(data, transport)
    assert "instant_utc" not in data  # Constructor must not silently repair the caller's data.


@pytest.mark.parametrize("transport", ["constructor", "python", "json"])
@pytest.mark.parametrize("shape", ["unknown", "missing_zone", "civil", "missing_value"])
def test_overflow_diagnostic_requires_actual_conversion(shape: str, transport: str) -> None:
    data = event_payload("2026-05-10T12:30:00", "-00:00" if shape == "unknown" else None)
    if shape in {"civil", "missing_value"}:
        data = {"claim": {"role": "submission_deadline"}}
        if shape == "civil":
            data.update(
                civil_date="2026-05-10", precision="day", calendar_interpretation="gregorian"
            )
    data["diagnostics"] = diagnostic(OVERFLOW)
    with pytest.raises(ValidationError, match="UTC overflow diagnostic requires"):
        validate(data, transport)


OVERFLOW = "temporal_timezone_conversion_out_of_range"


@pytest.mark.parametrize(
    "wall",
    ["0001-01-01T00:00:00", "0001-01-01T23:59:00", "9999-12-31T00:00:00", "9999-12-31T23:59:00"],
)
def test_every_minute_offset_at_extreme_year_boundaries(wall: str) -> None:
    naive = datetime.fromisoformat(wall)
    for minutes in range(-1439, 1440):
        offset = timedelta(minutes=minutes)
        local = naive.replace(tzinfo=timezone(offset))
        zone = local.isoformat()[-6:]
        data = event_payload(local.isoformat(), zone)
        try:
            expected = (naive - offset).replace(tzinfo=UTC)
        except OverflowError:
            data["diagnostics"] = diagnostic(OVERFLOW)
            event = validate(data, "python")
            assert event.instant_utc is None
            assert [d.code for d in event.diagnostics] == [OVERFLOW]
        else:
            with pytest.raises(ValidationError, match="UTC instant is required"):
                validate(data, "python")
            data["instant_utc"] = expected.isoformat()
            event = validate(data, "python")
            assert event.instant_utc == expected
            assert event.diagnostics == ()
        assert event.local_datetime.isoformat() == local.isoformat()
        assert event.timezone == zone
        assert NormalizedTemporalEvent.model_validate_json(event.model_dump_json()) == event


def diagnostic(code: str) -> list[dict[str, object]]:
    return [{"code": code, "message": "UTC conversion unresolved.", "claim_index": 0}]


@pytest.mark.parametrize("transport", ["constructor", "python", "json"])
@pytest.mark.parametrize(
    "zone,utc",
    [("+03:00", "09:30"), ("-03:00", "15:30"), ("+00:00", "12:30"), ("Z", "12:30")],
)
def test_matching_utc_is_required_not_synthesized(zone: str, utc: str, transport: str) -> None:
    data = event_payload("2026-05-10T12:30:00" + zone, zone)
    data["instant_utc"] = "2026-05-10T" + utc + ":00Z"
    event = validate(data, transport)
    assert event.instant_utc == datetime.fromisoformat(str(data["instant_utc"]))
    assert event.instant_utc.utcoffset().total_seconds() == 0
    assert event.timezone == zone and event.diagnostics == ()
    assert NormalizedTemporalEvent.model_validate_json(event.model_dump_json()) == event
    data["instant_utc"] = "2026-05-10T00:00:00Z"
    with pytest.raises(ValidationError, match="UTC instant must correspond"):
        validate(data, transport)
    data["instant_utc"] = "2026-05-10T12:30:00+03:00"
    with pytest.raises(ValidationError, match="UTC instant must have zero offset"):
        validate(data, transport)


@pytest.mark.parametrize("transport", ["constructor", "python", "json"])
@pytest.mark.parametrize("zone", [None, "-00:00"])
def test_unresolved_local_time_stays_naive(zone: str | None, transport: str) -> None:
    event = validate(event_payload("2026-05-10T12:30:00", zone), transport)
    assert event.local_datetime == datetime(2026, 5, 10, 12, 30)
    assert event.local_datetime.tzinfo is None and event.instant_utc is None
    assert event.timezone == zone
    assert NormalizedTemporalEvent.model_validate_json(event.model_dump_json()) == event


@pytest.mark.parametrize("transport", ["constructor", "python", "json"])
def test_civil_date_never_acquires_time(transport: str) -> None:
    event = validate(
        {
            "claim": {"role": "submission_deadline"},
            "civil_date": "2026-05-10",
            "precision": "day",
            "calendar_interpretation": "gregorian",
        },
        transport,
    )
    assert event.civil_date == date(2026, 5, 10)
    assert event.local_datetime is event.instant_utc is event.timezone is None
    assert NormalizedTemporalEvent.model_validate_json(event.model_dump_json()) == event


@pytest.mark.parametrize("transport", ["constructor", "python", "json"])
@pytest.mark.parametrize(
    "local,zone", [("0001-01-01T00:00:00+14:00", "+14:00"), ("9999-12-31T23:59:00-14:00", "-14:00")]
)
def test_overflow_requires_exact_diagnostic(local: str, zone: str, transport: str) -> None:
    data = event_payload(local, zone)
    for issues in ([], diagnostic("temporal_timezone_unknown")):
        data["diagnostics"] = issues
        with pytest.raises(ValidationError, match="UTC overflow requires"):
            validate(data, transport)
    data["diagnostics"] = diagnostic(OVERFLOW)
    event = validate(data, transport)
    assert event.local_datetime.isoformat() == local
    assert event.instant_utc is None
    assert [(d.code, d.claim_index) for d in event.diagnostics] == [(OVERFLOW, 0)]
    assert NormalizedTemporalEvent.model_validate_json(event.model_dump_json()) == event
    data["instant_utc"] = "2026-05-10T09:30:00Z"
    with pytest.raises(ValidationError, match="UTC instant is outside"):
        validate(data, transport)


@pytest.mark.parametrize("transport", ["constructor", "python", "json"])
@pytest.mark.parametrize("present", [False, True])
def test_false_overflow_diagnostic_cannot_excuse_representable_time(
    present: bool, transport: str
) -> None:
    data = event_payload("2026-05-10T12:30:00+03:00", "+03:00")
    data["diagnostics"] = diagnostic(OVERFLOW)
    if present:
        data["instant_utc"] = "2026-05-10T09:30:00Z"
    with pytest.raises(ValidationError, match="UTC overflow diagnostic requires"):
        validate(data, transport)


@pytest.mark.parametrize(
    "original",
    [
        "2026-05-10T12:30:00+03:00",
        "0001-01-01T00:00:00+14:00",
        "9999-12-31T23:59:00-14:00",
        "2026-05-10T12:30:00-00:00",
        "2026-05-10T12:30:00",
        "2026-05-10",
    ],
)
def test_report_roundtrip_and_audit_bind_temporal_contract(original: str) -> None:
    context, values, _, _ = build_context(temporal=[("submission_deadline", original)])
    report = normalize_temporal(
        TemporalInput(
            context=context, events=(TemporalClaim(role="submission_deadline", value=values[0]),)
        )
    )
    assert isinstance(report, TemporalReport)
    assert report.events[0].claim.value == values[0]
    assert (
        report.audit.report_digest
        == hashlib.sha256(report.model_dump_json(exclude={"audit"}).encode()).hexdigest()
    )
    assert TemporalReport.model_validate(report.model_dump()) == report
    assert TemporalReport.model_validate_json(report.model_dump_json()) == report
    assert normalize_temporal(report.input) == report
    assert report.promotable is False
    data: dict[str, Any] = json.loads(report.model_dump_json())
    data["events"][0]["claim"]["role"] = "publication_date"
    with pytest.raises(ValidationError, match="Normalization audit"):
        TemporalReport.model_validate_json(json.dumps(data))


@pytest.mark.parametrize("transport", ["python", "json"])
def test_report_cannot_wrap_incomplete_known_offset(transport: str) -> None:
    context, *_ = build_context()
    data = {
        "input": TemporalInput(context=context).model_dump(mode="json"),
        "events": [event_payload("2026-05-10T12:30:00+03:00", "+03:00")],
    }
    with pytest.raises(ValidationError, match="UTC instant is required"):
        if transport == "python":
            TemporalReport.model_validate(data)
        else:
            TemporalReport.model_validate_json(json.dumps(data))
