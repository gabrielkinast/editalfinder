"""Empty assertions are retained and diagnosed, independently of geographic scope."""

import hashlib
import json
from typing import get_args

import pytest
from pydantic import ValidationError
from test_geography_normalization import report_for

from editalfinder_v2.domain.geography_models import GeographyReport, LocationRole
from editalfinder_v2.domain.geography_normalization import normalize_geography


@pytest.mark.parametrize("role", get_args(LocationRole))
@pytest.mark.parametrize("scope", [None, "brasil", "internacional", "misto", "nao_identificado"])
def test_empty_claim_has_own_diagnostic_not_invented_location(
    role: LocationRole, scope: str | None
) -> None:
    report = report_for([(role, {})], scope)
    assert len(report.locations) == 1
    location = report.locations[0]
    assert location.claim == report.input.locations[0]
    assert location.role == role
    assert [(d.code, d.claim_index, d.evidence) for d in location.diagnostics] == [
        ("geo_location_empty", 0, ())
    ]
    assert [(d.code, d.claim_index) for d in report.diagnostics] == (
        [("geo_scope_missing", None)] if scope is None else []
    ) + [("geo_location_empty", 0)]
    assert report.scope == (scope if scope is not None else "nao_identificado")
    for key in ("country_code", "state_code", "municipality", "region"):
        assert getattr(location, key) is None
        assert getattr(location.claim, key) is None
        assert getattr(location.confidence, key) is None
    assert location.municipality_verified is False
    assert report.promotable is False
    assert GeographyReport.model_validate_json(report.model_dump_json()) == report
    assert normalize_geography(report.input) == report


@pytest.mark.parametrize(
    "fields,expected,diagnostics",
    [
        ({"country_code": "US"}, ("US", None, None, None), []),
        ({"country_code": "br", "state_code": "rs"}, ("BR", "RS", None, None), []),
        ({"country_code": "BR", "state_code": "SP"}, ("BR", "SP", None, None), []),
        ({"country_code": "BR", "region": "sul"}, ("BR", None, None, "sul"), []),
        (
            {"country_code": "US", "municipality": " Washington "},
            ("US", None, "Washington", None),
            [("geo_municipality_unverified", 0)],
        ),
        ({"state_code": "RS"}, (None, None, None, None), [("geo_country_state_conflict", 0)]),
        ({"region": "sul"}, (None, None, None, None), [("geo_country_region_conflict", 0)]),
        (
            {"municipality": "Porto Alegre"},
            (None, None, None, None),
            [("geo_municipality_country_missing", 0)],
        ),
        ({"country_code": "ZZ"}, (None, None, None, None), [("geo_country_invalid", 0)]),
    ],
)
def test_supplied_components_are_not_absent_even_when_unresolved(
    fields: dict[str, str], expected: tuple[str | None, ...], diagnostics: list[tuple[str, int]]
) -> None:
    report = report_for([("execucao", fields)], "misto")
    location = report.locations[0]
    assert (
        tuple(
            getattr(location, key)
            for key in ("country_code", "state_code", "municipality", "region")
        )
        == expected
    )
    assert [(d.code, d.claim_index) for d in report.diagnostics] == diagnostics
    for key, original in fields.items():
        raw = getattr(location.claim, key)
        assert raw.original == original
        assert raw == getattr(report.input.locations[0], key)
        assert raw.provenance.evidence.quote == original
    for issue in location.diagnostics:
        assert issue.evidence
        assert all(
            proof in [getattr(location.claim, key).provenance for key in fields]
            for proof in issue.evidence
        )
    assert location.municipality_verified is False
    assert GeographyReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("empty_index", [0, 1, 2])
def test_one_empty_claim_among_valid_locations(empty_index: int) -> None:
    rows: list[tuple[LocationRole, dict[str, str]]] = [
        ("elegibilidade", {"country_code": "US"}),
        ("execucao", {"country_code": "BR", "state_code": "SP"}),
    ]
    rows.insert(empty_index, ("beneficiarios", {}))
    report = report_for(rows, "misto")
    assert len(report.locations) == 3
    assert [(d.code, d.claim_index) for d in report.diagnostics] == [
        ("geo_location_empty", empty_index)
    ]
    assert report.locations[empty_index].role == "beneficiarios"
    assert report.locations[empty_index].claim == report.input.locations[empty_index]
    assert GeographyReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("transport", ["python", "json"])
@pytest.mark.parametrize("field", ["diagnostics", "role", "index"])
def test_multiple_locations_empty_indices_serialization_and_audit(
    transport: str, field: str
) -> None:
    report = report_for(
        [
            ("elegibilidade", {}),
            ("origem", {"country_code": "br"}),
            ("execucao", {}),
            ("organizacao_responsavel", {"country_code": "US"}),
        ],
        "misto",
    )
    assert [v.role for v in report.locations] == [
        "elegibilidade",
        "origem",
        "execucao",
        "organizacao_responsavel",
    ]
    assert [(d.code, d.claim_index) for d in report.diagnostics] == [
        ("geo_location_empty", 0),
        ("geo_location_empty", 2),
    ]
    assert report.locations[0].country_code is report.locations[2].country_code is None
    assert report.locations[1].claim.country_code.original == "br"
    assert report.locations[1].country_code == "BR"
    assert (
        report.audit.report_digest
        == hashlib.sha256(report.model_dump_json(exclude={"audit"}).encode()).hexdigest()
    )
    assert GeographyReport.model_validate(report.model_dump()) == report
    assert GeographyReport.model_validate_json(report.model_dump_json()) == report
    data = report.model_dump(mode="json")
    if field == "diagnostics":
        data["locations"][0]["diagnostics"] = []
        data["diagnostics"] = data["diagnostics"][1:]
    elif field == "role":
        data["locations"][0]["claim"]["role"] = "beneficiarios"
    else:
        data["locations"][2]["diagnostics"][0]["claim_index"] = 0
        data["diagnostics"][1]["claim_index"] = 0
    with pytest.raises(ValidationError, match="Normalization audit"):
        if transport == "python":
            GeographyReport.model_validate(data)
        else:
            GeographyReport.model_validate_json(json.dumps(data))
