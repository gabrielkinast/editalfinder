"""Finite metamorphic domains, serialization, retained-audit and evidence probes."""

import hashlib
from itertools import product

import pytest
from pydantic import ValidationError
from semantic_fixtures import build_context
from test_geography_normalization import codes, report_for

from editalfinder_v2.domain.geography_catalog import COUNTRY_CODES, REGION_STATES
from editalfinder_v2.domain.geography_models import (
    GeographyInput,
    GeographyLocationClaim,
    GeographyReport,
)
from editalfinder_v2.domain.geography_normalization import normalize_geography
from editalfinder_v2.domain.models import OperationalError


@pytest.mark.parametrize("country", sorted(COUNTRY_CODES))
def test_country_case_normalization_and_canonical_idempotence(country: str) -> None:
    lower = report_for([("elegibilidade", {"country_code": country.lower()})])
    canonical = report_for([("elegibilidade", {"country_code": country})])
    assert lower.locations[0].country_code == canonical.locations[0].country_code == country
    assert lower.input.locations[0].country_code.original == country.lower()
    assert canonical == normalize_geography(canonical.input)
    assert GeographyReport.model_validate_json(canonical.model_dump_json()) == canonical
    assert lower.audit != canonical.audit
    assert not canonical.promotable


def test_all_27_states_and_five_region_cross_product() -> None:
    states = set().union(*REGION_STATES.values())
    assert len(COUNTRY_CODES) == 249
    assert len(states) == 27
    assert len(REGION_STATES) == 5
    for state, region in product(sorted(states), sorted(REGION_STATES)):
        result = report_for(
            [("execucao", {"country_code": "BR", "state_code": state.lower(), "region": region})]
        )
        if state in REGION_STATES[region]:
            assert result.locations[0].state_code == state
            assert result.locations[0].region == region
            assert "geo_state_region_conflict" not in codes(result)
        else:
            assert "geo_state_region_conflict" in codes(result)
            assert result.locations[0].state_code is None
            assert result.locations[0].region is None


@pytest.mark.parametrize(
    "field", ["country_code", "state_code", "municipality", "region", "diagnostics", "confidence"]
)
@pytest.mark.parametrize("transport", ["python", "json"])
def test_retained_audit_detects_location_changes(field: str, transport: str) -> None:
    result = report_for(
        [
            (
                "elegibilidade",
                {
                    "country_code": "BR",
                    "municipality": "Porto Alegre",
                },
            )
        ],
        "brasil",
    )
    data = result.model_dump(mode="json" if transport == "json" else "python")
    data["locations"][0][field] = {
        "country_code": "US",
        "state_code": "SP",
        "municipality": "Washington",
        "region": "sudeste",
        "diagnostics": [],
        "confidence": {"country_code": "0.5"},
    }[field]
    with pytest.raises(ValidationError, match="Normalization audit"):
        GeographyReport.model_validate(data)


def test_audit_representation_is_complete_and_non_circular() -> None:
    result = report_for([("origem", {"country_code": "US"})], "brasil")
    assert result.audit is not None
    assert (
        result.audit.report_digest
        == hashlib.sha256(result.model_dump_json(exclude={"audit"}).encode()).hexdigest()
    )
    data = result.model_dump()
    data["scope"] = "internacional"
    with pytest.raises(ValidationError, match="Normalization audit"):
        GeographyReport.model_validate(data)
    data["audit"] = None
    recreated = GeographyReport.model_validate(data)
    assert not recreated.promotable
    assert recreated.audit != result.audit


@pytest.mark.parametrize("count", [64, 65])
def test_repeated_geo_evidence_retains_m1_field_budget(count: int) -> None:
    context, _, values, _ = build_context(
        geographic=[("elegibilidade", {"country_code": "BR"})] * count
    )
    request = GeographyInput(
        context=context,
        locations=tuple(
            GeographyLocationClaim(role="elegibilidade", country_code=v["country_code"])
            for v in values
        ),
    )
    result = normalize_geography(request)
    if count == 64:
        assert isinstance(result, GeographyReport)
        assert len(result.locations) == count
    else:
        assert isinstance(result, OperationalError)
        assert result.code == "normalization_limits_exceeded"
        assert not result.promotable


def test_component_budget_counts_values_not_only_locations() -> None:
    context, _, values, _ = build_context(
        geographic=[("execucao", {"country_code": "BR", "state_code": "RS"})]
    )
    request = GeographyInput(
        context=context,
        locations=tuple(GeographyLocationClaim(role="execucao", **values[0]) for _ in range(601)),
    )
    result = normalize_geography(request)
    assert isinstance(result, OperationalError)
    assert result.code == "normalization_limits_exceeded"


def test_empty_quote_rejected_at_contract_boundary() -> None:
    with pytest.raises(ValidationError):
        build_context(geographic=[("execucao", {"municipality": ""})])
