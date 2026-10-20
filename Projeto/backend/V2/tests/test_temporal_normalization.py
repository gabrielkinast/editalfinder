"""Temporal roles and civil dates remain separate from opportunity acceptance."""

from datetime import date

import pytest
from semantic_fixtures import build_context

from editalfinder_v2.domain.temporal_models import (
    TemporalClaim,
    TemporalFormat,
    TemporalInput,
    TemporalReport,
    TemporalRole,
)
from editalfinder_v2.domain.temporal_normalization import normalize_temporal


def test_iso_civil_date_is_not_a_timestamp_or_a_deadline() -> None:
    context, values, _, _ = build_context(temporal=[("publication_date", "2026-05-10")])
    request = TemporalInput(
        context=context,
        events=(TemporalClaim(role="publication_date", value=values[0], format="iso"),),
    )
    result = normalize_temporal(request)
    assert isinstance(result, TemporalReport)
    assert result.events[0].civil_date == date(2026, 5, 10)
    assert result.events[0].local_datetime is None
    assert result.events[0].instant_utc is None
    assert result.events[0].precision == "day"
    assert result.events[0].claim.role == "publication_date"
    assert {d.code for d in result.diagnostics} == {"temporal_deadline_missing"}
    assert not result.promotable


def report_for(
    original: str,
    format: TemporalFormat = "iso",
    role: TemporalRole = "submission_deadline",
    calendar: str = "gregorian",
) -> TemporalReport:
    context, values, _, _ = build_context(temporal=[(role, original)])
    request = TemporalInput(
        context=context,
        events=(TemporalClaim(role=role, value=values[0], format=format, calendar=calendar),),
    )
    result = normalize_temporal(request)
    assert isinstance(result, TemporalReport)
    return result


def codes(report: TemporalReport) -> set[str]:
    return {d.code for d in report.diagnostics}


@pytest.mark.parametrize(
    "original,format,expected",
    [
        ("10/05/2026", "brazilian", date(2026, 5, 10)),
        ("1/2/2026", "brazilian", date(2026, 2, 1)),
        ("29/02/2024", "brazilian", date(2024, 2, 29)),
        ("2026-05-10", "iso", date(2026, 5, 10)),
        ("2026-05-10", "unspecified", date(2026, 5, 10)),
        ("10 de maio de 2026", "text_pt_br", date(2026, 5, 10)),
        ("1 de MARÇO de 2026", "text_pt_br", date(2026, 3, 1)),
    ],
)
def test_civil_date_formats_preserve_evidence_and_interpretation(
    original: str, format: TemporalFormat, expected: date
) -> None:
    result = report_for(original, format)
    event = result.events[0]
    assert event.civil_date == expected
    assert event.local_datetime is None and event.instant_utc is None
    assert event.claim.value.original == original
    assert event.calendar_interpretation == "gregorian"
    assert not codes(result)


@pytest.mark.parametrize(
    "original,format,code",
    [
        ("10/05/2026", "unspecified", "temporal_date_ambiguous"),
        ("05/10/2026", "unspecified", "temporal_date_ambiguous"),
        ("05/10/26", "brazilian", "temporal_date_ambiguous"),
        ("2026-02-29", "iso", "temporal_date_invalid"),
        ("31/04/2026", "brazilian", "temporal_date_invalid"),
        ("2026-13-01", "iso", "temporal_date_invalid"),
        ("0000-01-01", "iso", "temporal_date_invalid"),
        ("20260510", "iso", "temporal_date_invalid"),
        ("2026-W01-1", "iso", "temporal_date_invalid"),
        ("10 de maio", "text_pt_br", "temporal_date_ambiguous"),
        ("10 de agoſto de 2026", "text_pt_br", "temporal_date_invalid"),
        ("２０１６-01-01", "iso", "temporal_date_invalid"),
    ],
)
def test_invalid_and_ambiguous_dates_have_specific_diagnostics(
    original: str, format: TemporalFormat, code: str
) -> None:
    result = report_for(original, format)
    assert result.events[0].civil_date is None
    assert code in codes(result)
    assert "temporal_deadline_unresolved" in codes(result)


@pytest.mark.parametrize(
    "calendar,code",
    [
        ("unspecified", "temporal_calendar_unspecified"),
        ("unsupported", "temporal_calendar_unsupported"),
    ],
)
def test_calendar_interpretation_is_not_invented(calendar: str, code: str) -> None:
    result = report_for("2026-05-10", calendar=calendar)
    assert result.events[0].civil_date is None
    assert code in codes(result)


def test_mutated_value_retaining_original_proof_cannot_normalize() -> None:
    context, values, _, _ = build_context(temporal=[("submission_deadline", "2026-05-10")])
    claim = TemporalClaim(
        role="submission_deadline",
        format="iso",
        value=values[0].model_copy(update={"original": "2026-12-31"}),
    )
    result = normalize_temporal(TemporalInput(context=context, events=(claim,)))
    assert isinstance(result, TemporalReport)
    assert result.events[0].civil_date is None
    assert "normalization_evidence_invalid" in codes(result)


@pytest.mark.parametrize(
    "original,utc,precision",
    [
        ("2026-05-10T12:30-03:00", "2026-05-10T15:30:00+00:00", "minute"),
        ("2026-05-10T12:30:40+02:30", "2026-05-10T10:00:40+00:00", "second"),
        ("2026-05-10T12:30:40.123Z", "2026-05-10T12:30:40.123000+00:00", "fractional_second"),
        ("2026-01-01T01:00+14:00", "2025-12-31T11:00:00+00:00", "minute"),
    ],
)
def test_explicit_offsets_convert_without_losing_source_precision(
    original: str, utc: str, precision: str
) -> None:
    result = report_for(original)
    event = result.events[0]
    assert event.civil_date is None
    assert event.local_datetime is not None
    assert event.instant_utc is not None and event.instant_utc.isoformat() == utc
    assert event.precision == precision
    assert event.fractional_digits == (3 if ".123Z" in original else None)
    assert event.claim.value.original == original
    assert not codes(result)


@pytest.mark.parametrize(
    "original,code,zone",
    [
        ("2026-05-10T12:30", "temporal_timezone_missing", None),
        ("2026-05-10T12:30:00-00:00", "temporal_timezone_unknown", "-00:00"),
    ],
)
def test_unknown_timezone_is_not_utc(original: str, code: str, zone: str | None) -> None:
    result = report_for(original)
    event = result.events[0]
    assert event.local_datetime is not None and event.local_datetime.tzinfo is None
    assert event.instant_utc is None
    assert event.timezone == zone
    assert code in codes(result)


@pytest.mark.parametrize(
    "original",
    [
        "2026-05-10T24:00Z",
        "2026-05-10T12:30:60Z",
        "2026-05-10T12:30+24:00",
        "2026-05-10T12:30+01:99",
        "2026-05-10T12:30EST",
        "2026-05-10T12:30 America/Sao_Paulo",
        "2026-05-10T12:30:01.1234567Z",
        "2026-05-10T12:30:00+00:00:30",
    ],
)
def test_invalid_timestamp_does_not_gain_a_calendar_value(original: str) -> None:
    result = report_for(original)
    assert result.events[0].civil_date is None
    assert result.events[0].local_datetime is None
    assert "temporal_date_invalid" in codes(result)


@pytest.mark.parametrize("original", ["0001-01-01T00:00+14:00", "9999-12-31T23:59-14:00"])
def test_utc_conversion_overflow_is_diagnostic_not_exception(original: str) -> None:
    result = report_for(original)
    assert result.events[0].local_datetime is not None
    assert result.events[0].instant_utc is None
    assert "temporal_timezone_conversion_out_of_range" in codes(result)


def report_events(rows: list[tuple[TemporalRole, str]]) -> TemporalReport:
    context, values, _, _ = build_context(temporal=rows)
    result = normalize_temporal(
        TemporalInput(
            context=context,
            events=tuple(
                TemporalClaim(role=role, value=raw, format="iso")
                for (role, _), raw in zip(rows, values, strict=True)
            ),
        )
    )
    assert isinstance(result, TemporalReport)
    return result


@pytest.mark.parametrize(
    "role",
    [
        "publication_date",
        "submission_opening_date",
        "selection_result_date",
        "contracting_date",
        "project_execution_date",
        "administrative_validity",
        "rectification_date",
    ],
)
def test_non_deadline_roles_never_gain_deadline_semantics(role: TemporalRole) -> None:
    result = report_events([(role, "2026-12-31")])
    assert result.events[0].claim.role == role
    assert "temporal_deadline_missing" in codes(result)
    assert result.input.events[0].role == role


def test_preliminary_and_full_proposal_stages_are_preserved_without_selection() -> None:
    rows = [
        ("preliminary_application_deadline", "2026-05-10"),
        ("full_application_deadline", "2026-07-20"),
    ]
    result = report_events(rows)
    assert [e.civil_date for e in result.events] == [date(2026, 5, 10), date(2026, 7, 20)]
    assert [e.claim.role for e in result.events] == [role for role, _ in rows]
    assert not codes(result)
    assert not hasattr(result, "selected_deadline")


def test_conflicting_deadlines_not_resolved_by_latest_first_or_confidence() -> None:
    rows = [("submission_deadline", "2026-05-10"), ("submission_deadline", "2026-07-20")]
    for current in (rows, rows[::-1]):
        result = report_events(current)
        assert "temporal_deadline_conflict" in codes(result)
        assert [e.civil_date.isoformat() for e in result.events] == [raw for _, raw in current]
        diagnostic = next(d for d in result.diagnostics if d.code == "temporal_deadline_conflict")
        assert len(diagnostic.evidence) == 2


def test_rectification_preserves_old_new_and_rectification_dates_for_review() -> None:
    result = report_events(
        [
            ("submission_deadline", "2026-05-10"),
            ("rectification_date", "2026-05-05"),
            ("submission_deadline", "2026-07-20"),
        ]
    )
    assert len(result.events) == 3
    assert {"temporal_deadline_conflict", "temporal_rectification_requires_review"} <= codes(result)
    assert result.events[1].claim.role == "rectification_date"


def test_mixed_civil_and_instant_precision_is_unresolved_not_assumed_equal() -> None:
    result = report_events(
        [("submission_deadline", "2026-05-10"), ("submission_deadline", "2026-05-10T12:00Z")]
    )
    assert "temporal_deadline_not_comparable" in codes(result)
    assert "temporal_deadline_conflict" not in codes(result)


def test_equal_instants_at_different_offsets_are_not_false_conflicts() -> None:
    result = report_events(
        [
            ("submission_deadline", "2026-05-10T12:00-03:00"),
            ("submission_deadline", "2026-05-10T15:00Z"),
        ]
    )
    assert "temporal_deadline_conflict" not in codes(result)


def test_missing_deadline_never_means_continuous_applications() -> None:
    context, _, _, _ = build_context()
    result = normalize_temporal(TemporalInput(context=context))
    assert isinstance(result, TemporalReport)
    assert result.events == ()
    assert codes(result) == {"temporal_deadline_missing"}
    assert "fluxo_continuo" not in result.model_dump_json()


def test_missing_event_value_is_diagnosed_without_a_sentinel_date() -> None:
    context, _, _, _ = build_context()
    result = normalize_temporal(
        TemporalInput(context=context, events=(TemporalClaim(role="submission_deadline"),))
    )
    assert isinstance(result, TemporalReport)
    assert result.events[0].civil_date is None
    assert codes(result) == {"temporal_value_missing", "temporal_deadline_unresolved"}
