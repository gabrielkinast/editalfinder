import json

import pytest
from m22b_fixtures import build_m22b_context
from pydantic import ValidationError

from editalfinder_v2.domain.identity_models import IdentifierNamespace
from editalfinder_v2.domain.models import OperationalError
from editalfinder_v2.domain.organization_models import (
    OrganizationClaim,
    OrganizationIdentifier,
    OrganizationNormalizationReport,
)
from editalfinder_v2.domain.organization_normalization import normalize_organizations

ROLES = ["publishing", "funding", "managing", "executing", "partner", "beneficiary", "applicant"]


@pytest.mark.parametrize("role", ROLES)
def test_roles_preserve_display_without_identity(role: str) -> None:
    context, rows = build_m22b_context(
        "organization_claims", [(role, {"name": "  Cafe\u0301   ABC  "})]
    )
    claim = OrganizationClaim.model_validate({"role": role, "name": rows[0]["name"]})
    result = normalize_organizations(context, (claim,))
    assert isinstance(result, OrganizationNormalizationReport)
    org = result.organizations[0]
    assert org.claim == claim
    assert org.normalized_name == "Café ABC"
    assert org.identifiers == ()
    assert result.comparison_keys == ((),)
    assert "organization_identifier_missing" in org.diagnostics
    assert not result.promotable
    assert result.policy_version == "m2.2b-semantics-v1"
    assert type(result).model_validate_json(result.model_dump_json()) == result
    data = json.loads(result.model_dump_json())
    data.pop("audit")
    data["organizations"][0]["normalized_name"] = "CAFE"
    with pytest.raises(ValidationError):
        type(result).model_validate_json(json.dumps(data))


def test_contextual_keys_preserve_publisher_and_funder_rows() -> None:
    context, rows = build_m22b_context(
        "organization_claims",
        [
            ("publishing", {"name": "ABC", "cnpj": "04.252.011/0001-10"}),
            ("funding", {"name": "Different name", "cnpj": "04252011000110"}),
        ],
    )
    claims = tuple(
        OrganizationClaim.model_validate(
            dict(
                role=role,
                name=row["name"],
                identifiers=(
                    OrganizationIdentifier(
                        kind="cnpj",
                        value=row["cnpj"],
                        namespace=IdentifierNamespace(value="BR:CNPJ"),
                    ),
                ),
            )
        )
        for role, row in zip(["publishing", "funding"], rows, strict=True)
    )
    result = normalize_organizations(context, claims)
    assert isinstance(result, OrganizationNormalizationReport)
    assert len(result.organizations) == 2
    assert result.comparison_keys[0] == result.comparison_keys[1]
    assert result.comparison_keys[0]
    assert "contextual_identifier_shared_not_merge" in result.diagnostics
    assert "organization_evidence_invalid:0" not in result.diagnostics


def test_same_role_cross_row_components_are_rejected() -> None:
    context, rows = build_m22b_context(
        "organization_claims",
        [
            ("publishing", {"name": "ABC", "cnpj": "04252011000110"}),
            ("publishing", {"name": "DEF", "cnpj": "11222333000181"}),
        ],
    )
    claim = OrganizationClaim(
        role="publishing",
        name=rows[0]["name"],
        identifiers=(
            OrganizationIdentifier(
                kind="cnpj", value=rows[1]["cnpj"], namespace=IdentifierNamespace(value="BR:CNPJ")
            ),
        ),
    )
    result = normalize_organizations(context, (claim,))
    assert isinstance(result, OrganizationNormalizationReport)
    assert result.comparison_keys == ((),)
    assert "organization_evidence_invalid:0" in result.diagnostics


def test_role_relabel_rejected() -> None:
    context, rows = build_m22b_context("organization_claims", [("publishing", {"name": "ABC"})])
    result = normalize_organizations(
        context, (OrganizationClaim(role="funding", name=rows[0]["name"]),)
    )
    assert isinstance(result, OrganizationNormalizationReport)
    assert "organization_evidence_invalid:0" in result.diagnostics


@pytest.mark.parametrize("name", [None, "   ", "\u200b"])
def test_missing_or_invalid_names(name: str | None) -> None:
    fields = {} if name is None else {"name": name}
    context, rows = build_m22b_context("organization_claims", [("partner", fields)])
    result = normalize_organizations(
        context, (OrganizationClaim(role="partner", name=rows[0].get("name")),)
    )
    assert isinstance(result, OrganizationNormalizationReport)
    assert result.organizations[0].normalized_name is None
    assert any("name_" in d for d in result.organizations[0].diagnostics)


def test_overlong_name_operational_limit() -> None:
    context, rows = build_m22b_context("organization_claims", [("partner", {"name": "x" * 8193})])
    result = normalize_organizations(
        context, (OrganizationClaim(role="partner", name=rows[0]["name"]),)
    )
    assert isinstance(result, OperationalError)
    assert result.code == "normalization_limits_exceeded"


def test_shared_identifier_does_not_hide_comparable_conflict() -> None:
    context, rows = build_m22b_context(
        "organization_claims",
        [
            ("publishing", {"name": "A", "cnpj": "04252011000110", "institutional": "001"}),
            ("funding", {"name": "B", "cnpj": "11222333000181", "institutional": "001"}),
        ],
    )
    claims = tuple(
        OrganizationClaim.model_validate(
            dict(
                role=role,
                name=row["name"],
                identifiers=tuple(
                    OrganizationIdentifier.model_validate(
                        dict(
                            kind=kind,
                            value=row[kind],
                            namespace=IdentifierNamespace(value="authority:" + kind),
                        )
                    )
                    for kind in ["cnpj", "institutional"]
                ),
            )
        )
        for role, row in zip(["publishing", "funding"], rows, strict=True)
    )
    result = normalize_organizations(context, claims)
    assert isinstance(result, OrganizationNormalizationReport)
    assert "organization_comparable_identifier_conflict:0:1" in result.diagnostics
    assert len(result.organizations) == 2


@pytest.mark.parametrize("field", ["normalized_name", "diagnostics", "identifiers"])
def test_standalone_normalized_row_rejects_tampering(field: str) -> None:
    context, rows = build_m22b_context("organization_claims", [("partner", {"name": "ABC"})])
    result = normalize_organizations(
        context, (OrganizationClaim(role="partner", name=rows[0]["name"]),)
    )
    assert isinstance(result, OrganizationNormalizationReport)
    org = result.organizations[0]
    data = org.model_dump()
    data[field] = "wrong" if field == "normalized_name" else ("wrong",)
    with pytest.raises(ValidationError):
        type(org)(**data)
    with pytest.raises(ValidationError):
        type(org).model_validate_json(json.dumps(data, default=str))


def test_report_rejects_fabricated_keys_without_audit() -> None:
    context, rows = build_m22b_context("organization_claims", [("partner", {"name": "ABC"})])
    result = normalize_organizations(
        context, (OrganizationClaim(role="partner", name=rows[0]["name"]),)
    )
    assert isinstance(result, OrganizationNormalizationReport)
    data = result.model_dump(exclude={"audit"})
    data["comparison_keys"] = ((("fabricated",),),)
    with pytest.raises(ValidationError):
        type(result)(**data)
