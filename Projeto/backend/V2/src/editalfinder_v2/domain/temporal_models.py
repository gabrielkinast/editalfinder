"""Explicit temporal roles; dates, local times and instants are not aliases."""

import re
from datetime import UTC, date, datetime, timedelta
from typing import Literal, Self

from pydantic import AwareDatetime, Field, model_validator

from .models import Contract
from .semantic_common import (
    AuditedNormalizationReport,
    NormalizationContext,
    NormalizationDiagnostic,
    SemanticValue,
)

TemporalRole = Literal[
    "publication_date",
    "submission_opening_date",
    "submission_deadline",
    "preliminary_application_deadline",
    "full_application_deadline",
    "selection_result_date",
    "contracting_date",
    "project_execution_date",
    "administrative_validity",
    "rectification_date",
]
TemporalFormat = Literal["iso", "brazilian", "text_pt_br", "unspecified"]
TemporalPrecision = Literal["day", "minute", "second", "fractional_second"]


class TemporalClaim(Contract):
    role: TemporalRole
    value: SemanticValue | None = None
    format: TemporalFormat = "unspecified"
    calendar: Literal["gregorian", "unspecified", "unsupported"] = "gregorian"


class TemporalInput(Contract):
    context: NormalizationContext
    events: tuple[TemporalClaim, ...] = ()
    normalization_version: Literal["temporal-conservative-v1"] = "temporal-conservative-v1"


class NormalizedTemporalEvent(Contract):
    claim: TemporalClaim
    civil_date: date | None = None
    local_datetime: datetime | None = None
    instant_utc: AwareDatetime | None = None
    timezone: str | None = None
    precision: TemporalPrecision | None = None
    fractional_digits: int | None = Field(default=None, ge=1, le=6)
    calendar_interpretation: Literal["gregorian"] | None = None
    diagnostics: tuple[NormalizationDiagnostic, ...] = ()
    normalization_version: Literal["temporal-conservative-v1"] = "temporal-conservative-v1"

    @model_validator(mode="after")
    def consistent_shape(self) -> Self:
        overflow_diagnostic = any(
            d.code == "temporal_timezone_conversion_out_of_range" for d in self.diagnostics
        )
        if overflow_diagnostic and (
            self.local_datetime is None or self.timezone in {None, "-00:00"}
        ):
            raise ValueError("UTC overflow diagnostic requires a known-offset local datetime")
        if self.civil_date is not None:
            if (
                self.local_datetime is not None
                or self.instant_utc is not None
                or self.timezone is not None
                or self.precision != "day"
                or self.fractional_digits is not None
                or self.calendar_interpretation != "gregorian"
            ):
                raise ValueError("Civil dates cannot acquire time, timezone or sub-day precision")
        elif self.local_datetime is not None:
            local = self.local_datetime
            if self.calendar_interpretation != "gregorian" or self.precision not in {
                "minute",
                "second",
                "fractional_second",
            }:
                raise ValueError("Local datetime requires explicit interpretation and precision")
            if self.precision == "minute" and (local.second or local.microsecond):
                raise ValueError("Minute precision cannot acquire seconds")
            if self.precision == "second" and local.microsecond:
                raise ValueError("Second precision cannot acquire fractional seconds")
            if (self.precision == "fractional_second") != (self.fractional_digits is not None):
                raise ValueError("Fractional precision requires source digit count")
            if self.fractional_digits is not None and local.microsecond % (
                10 ** (6 - self.fractional_digits)
            ):
                raise ValueError("Fractional precision cannot acquire finer source digits")
            local_offset = local.utcoffset()
            if self.timezone is None or self.timezone == "-00:00":
                if local_offset is not None or self.instant_utc is not None:
                    raise ValueError(
                        "Unknown timezone requires naive local time and no UTC instant"
                    )
            else:
                if self.timezone == "Z":
                    expected_offset = timedelta(0)
                elif re.fullmatch(r"[+-](?:[01][0-9]|2[0-3]):[0-5][0-9]", self.timezone):
                    expected_offset = timedelta(
                        hours=int(self.timezone[1:3]), minutes=int(self.timezone[4:6])
                    )
                    if self.timezone[0] == "-":
                        expected_offset = -expected_offset
                else:
                    raise ValueError("Timezone label must be Z or an ASCII offset within range")
                if local_offset != expected_offset:
                    raise ValueError("Timezone offset must match the aware local datetime")
                try:
                    expected_instant = local.astimezone(UTC)
                except (ValueError, OverflowError) as exc:
                    if self.instant_utc is not None:
                        raise ValueError("UTC instant is outside the representable range") from exc
                    if not overflow_diagnostic:
                        raise ValueError("UTC overflow requires its structured diagnostic") from exc
                else:
                    if overflow_diagnostic:
                        raise ValueError("UTC overflow diagnostic requires an out-of-range instant")
                    if self.instant_utc is None:
                        raise ValueError("UTC instant is required for a known representable offset")
                    if self.instant_utc.utcoffset() != timedelta(0):
                        raise ValueError("UTC instant must have zero offset")
                    if self.instant_utc != expected_instant:
                        raise ValueError("UTC instant must correspond to the local datetime")
        elif any(
            v is not None
            for v in (
                self.instant_utc,
                self.timezone,
                self.precision,
                self.fractional_digits,
                self.calendar_interpretation,
            )
        ):
            raise ValueError("Missing temporal value cannot acquire temporal metadata")
        return self


class TemporalReport(AuditedNormalizationReport):
    input: TemporalInput
    events: tuple[NormalizedTemporalEvent, ...]
    diagnostics: tuple[NormalizationDiagnostic, ...] = ()
    normalization_version: Literal["temporal-conservative-v1"] = "temporal-conservative-v1"
