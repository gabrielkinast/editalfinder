"""Output DTOs cannot represent invalid canonical shapes or invented precision."""

from datetime import UTC, date, datetime

import pytest
from pydantic import ValidationError
from semantic_fixtures import build_context

from editalfinder_v2.domain.geography_models import GeographyLocationClaim, NormalizedLocation
from editalfinder_v2.domain.temporal_models import NormalizedTemporalEvent, TemporalClaim


@pytest.mark.parametrize(
    "updates",
    [
        {
            "civil_date": date(2026, 1, 1),
            "local_datetime": datetime(2026, 1, 1),
            "precision": "day",
        },
        {"civil_date": date(2026, 1, 1), "precision": "second"},
        {
            "local_datetime": datetime(2026, 1, 1),
            "instant_utc": datetime(2026, 1, 1, tzinfo=UTC),
            "precision": "second",
        },
        {"local_datetime": datetime(2026, 1, 1, 12, 30, 1), "precision": "minute"},
        {"local_datetime": datetime(2026, 1, 1), "precision": "fractional_second"},
    ],
)
def test_temporal_contract_rejects_inconsistent_shape(updates: dict[str, object]) -> None:
    context, values, _, _ = build_context(temporal=[("publication_date", "2026-01-01")])
    claim = TemporalClaim(role="publication_date", value=values[0])
    with pytest.raises(ValidationError):
        NormalizedTemporalEvent.model_validate(
            {"claim": claim, "calendar_interpretation": "gregorian", **updates}
        )


@pytest.mark.parametrize(
    "updates",
    [
        {"country_code": "ZZ"},
        {"country_code": "br"},
        {"country_code": "US", "state_code": "RS"},
        {"state_code": "RS"},
        {"country_code": "BR", "state_code": "RS", "region": "sudeste"},
        {"country_code": "BR", "region": "internacional"},
        {"municipality": "Washington"},
    ],
)
def test_geographic_contract_rejects_inconsistent_canonical_shape(
    updates: dict[str, object],
) -> None:
    context, _, values, _ = build_context(
        geographic=[("elegibilidade", {"country_code": "BR", "state_code": "RS", "region": "sul"})]
    )
    claim = GeographyLocationClaim(role="elegibilidade", **values[0])
    with pytest.raises(ValidationError):
        NormalizedLocation.model_validate({"claim": claim, **updates})
