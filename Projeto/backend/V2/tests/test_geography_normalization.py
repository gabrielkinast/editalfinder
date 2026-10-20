"""Semantic geography: missing is unknown, source/sede never imply eligibility."""

import pytest
from semantic_fixtures import build_context

from editalfinder_v2.domain.geography_models import (
    GeographyInput,
    GeographyLocationClaim,
    GeographyReport,
    LocationRole,
)
from editalfinder_v2.domain.geography_normalization import normalize_geography


def test_missing_geography_never_defaults_to_brazil() -> None:
    context, _, _, _ = build_context()
    result = normalize_geography(GeographyInput(context=context))
    assert isinstance(result, GeographyReport)
    assert result.scope == "nao_identificado"
    assert result.locations == ()
    assert {d.code for d in result.diagnostics} == {"geo_scope_missing", "geo_locations_missing"}
    assert not result.promotable


def report_for(
    rows: list[tuple[LocationRole, dict[str, str]]], scope: str | None = None
) -> GeographyReport:
    context, _, values, scope_value = build_context(geographic=rows, scope=scope)
    result = normalize_geography(
        GeographyInput(
            context=context,
            locations=tuple(
                GeographyLocationClaim(role=role, **fields)
                for (role, _), fields in zip(rows, values, strict=True)
            ),
            scope=scope_value,
        )
    )
    assert isinstance(result, GeographyReport)
    return result


def codes(report: GeographyReport) -> set[str]:
    return {d.code for d in report.diagnostics}


@pytest.mark.parametrize(
    "country,state,region",
    [
        ("br", "rs", "sul"),
        ("BR", "SP", "sudeste"),
        ("US", None, None),
        ("DE", None, None),
        ("BR", "TO", "norte"),
    ],
)
def test_codes_are_normalized_without_scope_inference(
    country: str, state: str | None, region: str | None
) -> None:
    fields = {"country_code": country}
    if state is not None:
        fields["state_code"] = state
    if region is not None:
        fields["region"] = region
    result = report_for([("elegibilidade", fields)])
    location = result.locations[0]
    assert location.country_code == country.upper()
    assert location.state_code == (state.upper() if state else None)
    assert location.region == region
    assert location.role == "elegibilidade"
    assert result.scope == "nao_identificado"
    assert codes(result) == {"geo_scope_missing"}
    assert (
        location.confidence.country_code
        == result.input.locations[0].country_code.provenance.evidence.confidence
    )


@pytest.mark.parametrize("country", ["Brasil", "BRA", "ZZ", "EU", "UK", "B1", "ＢＲ", "bK", " br "])
def test_invalid_country_is_not_only_a_two_letter_regex(country: str) -> None:
    result = report_for([("elegibilidade", {"country_code": country})])
    assert result.locations[0].country_code is None
    assert "geo_country_invalid" in codes(result)
    assert result.input.locations[0].country_code.original == country


@pytest.mark.parametrize(
    "fields,code",
    [
        ({"country_code": "US", "state_code": "RS"}, "geo_country_state_conflict"),
        ({"state_code": "RS"}, "geo_country_state_conflict"),
        ({"country_code": "US", "region": "sul"}, "geo_country_region_conflict"),
        ({"region": "sul"}, "geo_country_region_conflict"),
        ({"country_code": "BR", "state_code": "ZZ"}, "geo_state_invalid"),
        ({"country_code": "BR", "region": "Nacional"}, "geo_region_invalid"),
        (
            {"country_code": "BR", "state_code": "RS", "region": "sudeste"},
            "geo_state_region_conflict",
        ),
    ],
)
def test_geography_conflicts_are_visible_and_do_not_form_invalid_locations(
    fields: dict[str, str], code: str
) -> None:
    result = report_for([("elegibilidade", fields)])
    assert code in codes(result)
    location = result.locations[0]
    if code == "geo_country_state_conflict":
        assert location.state_code is None
    if code == "geo_country_region_conflict":
        assert location.region is None
    if code == "geo_state_region_conflict":
        assert location.state_code is None and location.region is None
    for key, original in fields.items():
        assert getattr(location.claim, key).original == original


def test_region_is_not_silently_derived_from_uf() -> None:
    result = report_for([("execucao", {"country_code": "BR", "state_code": "RS"})])
    assert result.locations[0].region is None


@pytest.mark.parametrize(
    "country,municipality", [("BR", "Porto Alegre"), ("US", "Washington"), ("BR", "Atlantis")]
)
def test_municipality_text_is_preserved_not_certified(country: str, municipality: str) -> None:
    result = report_for(
        [("beneficiarios", {"country_code": country, "municipality": municipality})]
    )
    assert result.locations[0].municipality == municipality
    assert not result.locations[0].municipality_verified
    assert "geo_municipality_unverified" in codes(result)


@pytest.mark.parametrize("municipality", ["N/A", "Não informado", " ", "\u0000", "city\u200bname"])
def test_invalid_municipality_is_not_a_certified_place(municipality: str) -> None:
    result = report_for([("execucao", {"country_code": "BR", "municipality": municipality})])
    assert result.locations[0].municipality is None
    assert {"geo_municipality_invalid", "normalization_evidence_invalid"} & codes(result)


def test_municipality_does_not_fill_missing_country() -> None:
    result = report_for([("execucao", {"municipality": "Porto Alegre"})])
    assert result.locations[0].country_code is None
    assert result.locations[0].municipality is None
    assert "geo_municipality_country_missing" in codes(result)


@pytest.mark.parametrize(
    "scope,countries,expected",
    [
        ("misto", ["BR", "US", "DE"], None),
        ("brasil", ["BR"], None),
        ("internacional", ["US", "DE"], None),
        ("brasil", ["BR", "US"], "geo_scope_conflict"),
        ("internacional", ["BR"], "geo_scope_conflict"),
        ("global", ["US"], "geo_scope_invalid"),
    ],
)
def test_explicit_scope_and_multiple_locations(
    scope: str, countries: list[str], expected: str | None
) -> None:
    result = report_for(
        [("elegibilidade", {"country_code": country}) for country in countries], scope
    )
    assert [v.country_code for v in result.locations] == countries
    assert "geo_scope_missing" not in codes(result)
    if expected is None:
        assert result.scope == scope
        assert not codes(result)
    else:
        assert expected in codes(result)
        assert result.scope == (scope if expected == "geo_scope_conflict" else "nao_identificado")


@pytest.mark.parametrize(
    "role", ["origem", "organizacao_responsavel", "execucao", "beneficiarios", "nao_especificado"]
)
def test_non_eligibility_countries_do_not_acquire_eligibility(role: LocationRole) -> None:
    result = report_for([(role, {"country_code": "US"})], "brasil")
    assert result.locations[0].role == role
    assert result.scope == "brasil"
    assert not codes(result)


def test_country_evidence_cannot_be_used_as_scope_evidence() -> None:
    context, _, values, _ = build_context(geographic=[("origem", {"country_code": "BR"})])
    result = normalize_geography(GeographyInput(context=context, scope=values[0]["country_code"]))
    assert isinstance(result, GeographyReport)
    assert result.scope == "nao_identificado"
    assert "normalization_evidence_invalid" in codes(result)


def test_cannot_mix_components_from_different_source_rows() -> None:
    context, _, values, _ = build_context(
        geographic=[
            ("elegibilidade", {"country_code": "BR"}),
            ("elegibilidade", {"country_code": "US", "state_code": "SP"}),
        ]
    )
    claim = GeographyLocationClaim(
        role="elegibilidade",
        country_code=values[0]["country_code"],
        state_code=values[1]["state_code"],
    )
    result = normalize_geography(GeographyInput(context=context, locations=(claim,)))
    assert isinstance(result, GeographyReport)
    assert "geo_location_context_conflict" in codes(result)
    assert result.locations[0].country_code is None
    assert result.locations[0].state_code is None


def test_organization_country_cannot_be_relabelled_as_eligibility() -> None:
    context, _, values, _ = build_context(
        geographic=[("organizacao_responsavel", {"country_code": "US"})]
    )
    result = normalize_geography(
        GeographyInput(
            context=context,
            locations=(
                GeographyLocationClaim(
                    role="elegibilidade", country_code=values[0]["country_code"]
                ),
            ),
        )
    )
    assert isinstance(result, GeographyReport)
    assert result.locations[0].country_code is None
    assert "normalization_evidence_invalid" in codes(result)
