"""Pure temporal normalizer; no ranking dates or consulting clocks."""

import re
import unicodedata
from datetime import UTC, date, datetime
from types import MappingProxyType

from .models import OperationalError
from .semantic_common import NormalizationDiagnostic, PreparedContext, prepare_context
from .temporal_models import (
    NormalizedTemporalEvent,
    TemporalClaim,
    TemporalFormat,
    TemporalInput,
    TemporalReport,
)

DEADLINE_ROLES = frozenset(
    {
        "submission_deadline",
        "preliminary_application_deadline",
        "full_application_deadline",
    }
)
MONTHS_PT = MappingProxyType(
    {
        name: i
        for i, name in enumerate(
            (
                "janeiro",
                "fevereiro",
                "março",
                "abril",
                "maio",
                "junho",
                "julho",
                "agosto",
                "setembro",
                "outubro",
                "novembro",
                "dezembro",
            ),
            1,
        )
    }
)
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", re.ASCII)


def _civil(original: str, format: TemporalFormat) -> tuple[date | None, str | None]:
    text = original.strip()
    try:
        if format in {"iso", "unspecified"} and ISO_DATE.fullmatch(text):
            return date.fromisoformat(text), None
        if format == "brazilian":
            match = re.fullmatch(r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})", text, re.ASCII)
            if match:
                day, month, year = map(int, match.groups())
                return date(year, month, day), None
            if re.fullmatch(r"[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}", text, re.ASCII):
                return None, "temporal_date_ambiguous"
        if format == "text_pt_br":
            text = unicodedata.normalize("NFC", text).lower()
            match = re.fullmatch(r"([0-9]{1,2}) de ([a-zç]+) de ([0-9]{4})", text, re.ASCII)
            if match and match[2] in MONTHS_PT:
                return date(int(match[3]), MONTHS_PT[match[2]], int(match[1])), None
            if re.fullmatch(r"[0-9]{1,2} de [a-zç]+", text, re.ASCII):
                return None, "temporal_date_ambiguous"
        if format == "unspecified" and "/" in text:
            return None, "temporal_date_ambiguous"
    except ValueError:
        return None, "temporal_date_invalid"
    return None, "temporal_date_invalid"


def _timestamp(claim: TemporalClaim, index: int) -> NormalizedTemporalEvent | None:
    assert claim.value is not None
    text = claim.value.original.strip()
    match = re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}"
        r"(?::(?P<seconds>[0-9]{2})(?P<fraction>\.[0-9]{1,6})?)?"
        r"(?P<zone>Z|[+-][0-9]{2}:[0-9]{2})?",
        text,
        re.ASCII,
    )
    if not match:
        return None
    zone = match["zone"]
    # datetime.fromisoformat normalizes out-of-range offset minutes; reject first.
    if zone not in {None, "Z"} and (int(zone[1:3]) > 23 or int(zone[4:6]) > 59):
        return None
    try:
        local = datetime.fromisoformat(text[:-6] if zone == "-00:00" else text)
    except ValueError:
        return None
    instant: datetime | None = None
    issue: str | None = None
    if zone is None:
        issue = "temporal_timezone_missing"
    elif zone == "-00:00":
        issue = "temporal_timezone_unknown"
    else:
        try:
            instant = local.astimezone(UTC)
        except (ValueError, OverflowError):
            issue = "temporal_timezone_conversion_out_of_range"
    return NormalizedTemporalEvent(
        claim=claim,
        local_datetime=local,
        instant_utc=instant,
        timezone=zone,
        precision="fractional_second"
        if match["fraction"]
        else "second"
        if match["seconds"]
        else "minute",
        fractional_digits=len(match["fraction"]) - 1 if match["fraction"] else None,
        calendar_interpretation="gregorian",
        diagnostics=(
            NormalizationDiagnostic(
                code=issue,
                message="Timezone information does not provide a representable UTC instant.",
                claim_index=index,
                evidence=(claim.value.provenance,),
            ),
        )
        if issue is not None
        else (),
    )


def _event(claim: TemporalClaim, index: int, prepared: PreparedContext) -> NormalizedTemporalEvent:
    def failure(code: str) -> NormalizedTemporalEvent:
        return NormalizedTemporalEvent(
            claim=claim,
            diagnostics=(
                NormalizationDiagnostic(
                    code=code,
                    message="Temporal value is outside the declared interpretation.",
                    claim_index=index,
                    evidence=(claim.value.provenance,) if claim.value is not None else (),
                ),
            ),
        )

    if claim.value is None:
        return failure("temporal_value_missing")
    if not prepared.matches(claim.value, claim.role, collection="temporal_events"):
        return failure("normalization_evidence_invalid")
    if claim.calendar != "gregorian":
        return failure("temporal_calendar_" + claim.calendar)
    if claim.format in {"iso", "unspecified"}:
        timestamp = _timestamp(claim, index)
        if timestamp is not None:
            return timestamp
    civil, error = _civil(claim.value.original, claim.format)
    if error is not None:
        return failure(error)
    return NormalizedTemporalEvent(
        claim=claim, civil_date=civil, precision="day", calendar_interpretation="gregorian"
    )


def normalize_temporal(value: TemporalInput) -> TemporalReport | OperationalError:
    prepared = prepare_context(
        value.context,
        claim_count=len(value.events),
        text_chars=sum(len(c.value.original) for c in value.events if c.value is not None),
    )
    if isinstance(prepared, OperationalError):
        return prepared
    events = tuple(_event(claim, index, prepared) for index, claim in enumerate(value.events))
    diagnostics = [d for event in events for d in event.diagnostics]
    deadlines = [event for event in events if event.claim.role in DEADLINE_ROLES]
    if not deadlines:
        diagnostics.append(
            NormalizationDiagnostic(
                code="temporal_deadline_missing",
                message="No submission deadline supplied; continuity is unknown.",
            )
        )
    elif not any(
        event.civil_date is not None or event.local_datetime is not None for event in deadlines
    ):
        diagnostics.append(
            NormalizationDiagnostic(
                code="temporal_deadline_unresolved",
                message="Supplied deadline claims have no usable normalized value.",
            )
        )
    groups: dict[str, list[tuple[int, NormalizedTemporalEvent, str, str]]] = {}
    for index, event in enumerate(events):
        if event.civil_date is not None:
            kind, normalized = "civil", event.civil_date.isoformat()
        elif event.instant_utc is not None:
            kind, normalized = "instant", event.instant_utc.isoformat()
        elif event.local_datetime is not None:
            kind = "local" if event.local_datetime.tzinfo is None else "unrepresentable"
            normalized = event.local_datetime.isoformat()
        else:
            continue
        if event.claim.role in DEADLINE_ROLES:
            groups.setdefault(event.claim.role, []).append((index, event, kind, normalized))
        elif event.claim.role == "rectification_date":
            assert event.claim.value is not None
            diagnostics.append(
                NormalizationDiagnostic(
                    code="temporal_rectification_requires_review",
                    message="Rectification preserved; replacement relationship is unverified.",
                    claim_index=index,
                    evidence=(event.claim.value.provenance,),
                )
            )
    for group in groups.values():
        keys = {(kind, normalized) for _, _, kind, normalized in group}
        if len(keys) <= 1:
            continue
        comparable = len({kind for kind, _ in keys}) == 1 and group[0][2] != "unrepresentable"
        diagnostics.append(
            NormalizationDiagnostic(
                code="temporal_deadline_conflict"
                if comparable
                else "temporal_deadline_not_comparable",
                message="Distinct deadline claims remain unresolved; no event is selected.",
                claim_index=group[0][0],
                evidence=tuple(
                    event.claim.value.provenance
                    for _, event, _, _ in group
                    if event.claim.value is not None
                ),
            )
        )
    return TemporalReport(input=value, events=events, diagnostics=tuple(diagnostics))
