"""Finite temporal domains: calendar boundaries, role isolation, audit and replay."""

from datetime import UTC, date, datetime, timedelta, timezone
from itertools import product
from typing import get_args

import pytest
from pydantic import ValidationError
from semantic_fixtures import build_context
from test_temporal_normalization import codes, report_for

from editalfinder_v2.domain.models import OperationalError
from editalfinder_v2.domain.temporal_models import (
    TemporalClaim,
    TemporalInput,
    TemporalReport,
    TemporalRole,
)
from editalfinder_v2.domain.temporal_normalization import MONTHS_PT, normalize_temporal


def test_calendar_boundaries_iso_br_and_portuguese_agree_without_changing_role() -> None:
    months = {number: month for month, number in MONTHS_PT.items()}
    for year, month, day in product(
        (1, 1900, 2000, 2024, 2026, 2100, 9999), range(1, 13), (1, 28, 29, 30, 31)
    ):
        try:
            expected = date(year, month, day)
        except ValueError:
            continue
        iso = report_for(expected.isoformat())
        br = report_for(f"{day:02}/{month:02}/{year:04}", "brazilian")
        pt = report_for(f"{day} de {months[month]} de {year:04}", "text_pt_br")
        assert (
            iso.events[0].civil_date
            == br.events[0].civil_date
            == pt.events[0].civil_date
            == expected
        )
        canonical = report_for(iso.events[0].civil_date.isoformat())
        assert canonical.events[0].civil_date == expected
        assert iso == normalize_temporal(iso.input)
        assert TemporalReport.model_validate_json(iso.model_dump_json()) == iso


@pytest.mark.parametrize("digits", range(1, 7))
def test_fractional_precision_roundtrip_preserves_exact_source_digit_count(digits: int) -> None:
    original = "2026-05-10T12:30:40." + "1" * digits + "Z"
    report = report_for(original)
    assert report.events[0].precision == "fractional_second"
    assert report.events[0].fractional_digits == digits
    assert TemporalReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("offset", [-720, -180, 0, 330, 840])
def test_utc_conversion_matches_explicit_fixed_offset_arithmetic(offset: int) -> None:
    delta = timedelta(minutes=offset)
    local = datetime(2026, 1, 1, 0, 15, tzinfo=timezone(delta))
    report = report_for(local.isoformat())
    assert report.events[0].instant_utc == local.astimezone(UTC)
    assert report.events[0].local_datetime == local
    assert report.events[0].civil_date is None


@pytest.mark.parametrize("role", [r for r in get_args(TemporalRole) if r != "publication_date"])
def test_publication_evidence_cannot_be_relabelled_to_other_temporal_roles(
    role: TemporalRole,
) -> None:
    context, values, _, _ = build_context(temporal=[("publication_date", "2026-05-10")])
    report = normalize_temporal(
        TemporalInput(
            context=context, events=(TemporalClaim(role=role, format="iso", value=values[0]),)
        )
    )
    assert isinstance(report, TemporalReport)
    assert report.events[0].civil_date is None
    assert "normalization_evidence_invalid" in codes(report)


@pytest.mark.parametrize("field", ["civil_date", "claim", "diagnostics", "calendar_interpretation"])
@pytest.mark.parametrize("transport", ["python", "json"])
def test_audit_rejects_valid_shape_changes_with_retained_envelope(
    field: str, transport: str
) -> None:
    report = report_for("2026-05-10", role="publication_date")
    data = report.model_dump(mode="json" if transport == "json" else "python")
    if field == "civil_date":
        data["events"][0][field] = "2026-07-20" if transport == "json" else date(2026, 7, 20)
    elif field == "claim":
        data["events"][0][field]["role"] = "submission_deadline"
    elif field == "diagnostics":
        data[field] = []
    else:
        data["input"]["events"][0]["calendar"] = "unspecified"
    with pytest.raises(ValidationError, match="Normalization audit"):
        TemporalReport.model_validate(data)


@pytest.mark.parametrize("field", ["timezone", "precision", "fractional_digits", "instant_utc"])
def test_timestamp_audit_covers_timezone_precision_fraction_and_utc(field: str) -> None:
    report = report_for("2026-05-10T12:30:40.123Z")
    data = report.model_dump()
    updates = {
        "timezone": "+00:00",
        "precision": "second",
        "fractional_digits": 4,
        "instant_utc": datetime(2026, 5, 10, 12, 30, 41, 123000, tzinfo=UTC),
    }
    if field == "precision":
        # Keep an otherwise consistent shape; source lexical precision still changes.
        data["events"][0]["precision"] = "fractional_second"
        data["events"][0]["fractional_digits"] = 6
    else:
        data["events"][0][field] = updates[field]
        if field == "instant_utc":
            # Mutate the coherent pair so rejection exercises the retained audit,
            # not only the local UTC-consistency invariant.
            data["events"][0]["local_datetime"] = updates[field]
    with pytest.raises(ValidationError, match="Normalization audit"):
        TemporalReport.model_validate(data)


@pytest.mark.parametrize("count", [64, 65])
def test_temporal_evidence_budget_inclusive_without_truncation(count: int) -> None:
    context, values, _, _ = build_context(temporal=[("submission_deadline", "2026-05-10")] * count)
    request = TemporalInput(
        context=context,
        events=tuple(
            TemporalClaim(role="submission_deadline", format="iso", value=v) for v in values
        ),
    )
    report = normalize_temporal(request)
    if count == 64:
        assert isinstance(report, TemporalReport)
        assert len(report.events) == 64
    else:
        assert isinstance(report, OperationalError)
        assert report.code == "normalization_limits_exceeded"
        assert not report.promotable


def test_input_and_output_do_not_mutate_and_have_no_accepted_path() -> None:
    report = report_for("2026-05-10")
    before = report.input.model_dump_json()
    again = normalize_temporal(report.input)
    assert again == report
    assert before == report.input.model_dump_json()
    assert not report.promotable and not hasattr(report, "decision")
    with pytest.raises(ValidationError, match="frozen_instance"):
        report.events[0].civil_date = date(2026, 7, 20)
