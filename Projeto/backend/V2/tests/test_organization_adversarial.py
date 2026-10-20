"""Adversarial public organization contracts; no registry or persistence."""

import json
from uuid import UUID

import pytest
from m22b_fixtures import build_m22b_context
from pydantic import ValidationError

from editalfinder_v2.domain.identity_models import IdentifierNamespace
from editalfinder_v2.domain.models import OperationalError
from editalfinder_v2.domain.organization_models import (
    OrganizationClaim,
    OrganizationDiagnostic,
    OrganizationIdentifier,
    OrganizationNormalizationReport,
)
from editalfinder_v2.domain.organization_normalization import normalize_organizations
from editalfinder_v2.domain.semantic_common import SemanticValue


@pytest.mark.parametrize(
    "tamper", ["name", "candidate_id", "source_id", "execution_id", "quote", "pointer"]
)
def test_evidence_isolation_suppresses_all_keys(tamper: str) -> None:
    context, rows = build_m22b_context(
        "organization_claims",
        [
            ("publishing", {"name": "ABC", "institutional": "001"}),
        ],
    )
    data = rows[0]["name"].model_dump()
    if tamper == "name":
        data["original"] = "XYZ"
    elif tamper in {"candidate_id", "source_id", "execution_id"}:
        data["provenance"][tamper] = UUID(int=999)
    else:
        data["provenance"]["evidence"][tamper] = "XYZ" if tamper == "quote" else "/other/name"
    claim = OrganizationClaim(
        role="publishing",
        name=SemanticValue.model_validate(data),
        identifiers=(
            OrganizationIdentifier(
                kind="institutional",
                value=rows[0]["institutional"],
                namespace=IdentifierNamespace(value="authority"),
            ),
        ),
    )
    result = normalize_organizations(context, (claim,))
    assert isinstance(result, OrganizationNormalizationReport)
    assert result.comparison_keys == ((),)
    assert result.diagnostics == (
        "organization_identity_unverified",
        "organization_evidence_invalid:0",
    )


@pytest.mark.parametrize("difference", ["namespace", "policy", "invalid_checksum"])
def test_incomparable_identifiers_do_not_claim_conflicts(difference: str) -> None:
    context, rows = build_m22b_context(
        "organization_claims",
        [
            ("publishing", {"cnpj": "04252011000110"}),
            (
                "funding",
                {
                    "cnpj": "11222333000181"
                    if difference != "invalid_checksum"
                    else "04252011000111"
                },
            ),
        ],
    )
    claims = tuple(
        OrganizationClaim.model_validate(
            dict(
                role=role,
                identifiers=(
                    OrganizationIdentifier.model_validate(
                        dict(
                            kind="cnpj",
                            value=row["cnpj"],
                            namespace=IdentifierNamespace(
                                value="other" if index and difference == "namespace" else "BR:CNPJ"
                            ),
                            normalization_version="opaque-nfc-v1"
                            if index and difference == "policy"
                            else "opaque-exact-v1",
                        )
                    ),
                ),
            )
        )
        for index, (role, row) in enumerate(zip(["publishing", "funding"], rows, strict=True))
    )
    result = normalize_organizations(context, claims)
    assert isinstance(result, OrganizationNormalizationReport)
    assert result.diagnostics == ("organization_identity_unverified",)
    assert not any(
        d.code == "organization_comparable_identifier_conflict"
        for d in result.structured_diagnostics
    )


@pytest.mark.parametrize("count", [1200, 1201])
def test_claim_budget_public_boundary(count: int) -> None:
    context, _ = build_m22b_context("organization_claims", [])
    result = normalize_organizations(context, (OrganizationClaim(role="partner"),) * count)
    if count == 1200:
        assert isinstance(result, OrganizationNormalizationReport)
        assert len(result.organizations) == count
        assert result.diagnostics == ("organization_identity_unverified",)
    else:
        assert isinstance(result, OperationalError)
        assert result.code == "normalization_limits_exceeded"


def test_component_budget_counts_identifiers_not_only_claims() -> None:
    context, rows = build_m22b_context(
        "organization_claims", [("partner", {"institutional": "001"})]
    )
    identifier = OrganizationIdentifier(
        kind="institutional",
        value=rows[0]["institutional"],
        namespace=IdentifierNamespace(value="authority"),
    )
    result = normalize_organizations(
        context, (OrganizationClaim(role="partner", identifiers=(identifier,) * 1201),)
    )
    assert isinstance(result, OperationalError)
    assert result.code == "normalization_limits_exceeded"


def test_conflict_witness_evidence_belongs_to_reported_rows() -> None:
    context, rows = build_m22b_context(
        "organization_claims",
        [
            ("publishing", {"institutional": "A"}),
            ("funding", {"institutional": "B"}),
            ("partner", {"institutional": "A"}),
        ],
    )
    claims = tuple(
        OrganizationClaim.model_validate(
            dict(
                role=role,
                identifiers=(
                    OrganizationIdentifier(
                        kind="institutional",
                        value=row["institutional"],
                        namespace=IdentifierNamespace(value="authority"),
                    ),
                ),
            )
        )
        for role, row in zip(["publishing", "funding", "partner"], rows, strict=True)
    )
    result = normalize_organizations(context, claims)
    assert isinstance(result, OrganizationNormalizationReport)
    conflicts = [
        d
        for d in result.structured_diagnostics
        if d.code == "organization_comparable_identifier_conflict"
    ]
    assert [(d.claim_index, d.related_claim_index) for d in conflicts] == [(0, 1), (1, 2)]
    assert conflicts[1].evidence == (
        rows[1]["institutional"].provenance,
        rows[2]["institutional"].provenance,
    )


@pytest.mark.parametrize("field", ["claim_index", "related_claim_index", "identifier_index"])
@pytest.mark.parametrize("bad_index", [-1, True, "0"])
def test_public_diagnostic_rejects_invalid_indices(field: str, bad_index: object) -> None:
    data = {
        "code": "organization_evidence_invalid",
        "message": "Unsupported evidence.",
        field: bad_index,
    }
    with pytest.raises(ValidationError):
        OrganizationDiagnostic.model_validate(data)
    with pytest.raises(ValidationError):
        OrganizationDiagnostic.model_validate_json(json.dumps(data))


def test_conflicts_are_linear_bounded_witnesses_not_all_pairs() -> None:
    context, rows = build_m22b_context(
        "organization_claims", [("partner", {"institutional": str(index)}) for index in range(50)]
    )
    claims = tuple(
        OrganizationClaim(
            role="partner",
            identifiers=(
                OrganizationIdentifier(
                    kind="institutional",
                    value=row["institutional"],
                    namespace=IdentifierNamespace(value="authority"),
                ),
            ),
        )
        for row in rows
    )
    result = normalize_organizations(context, claims)
    assert isinstance(result, OrganizationNormalizationReport)
    conflicts = [
        d
        for d in result.structured_diagnostics
        if d.code == "organization_comparable_identifier_conflict"
    ]
    assert len(conflicts) == 49
    assert all(d.claim_index == 0 and len(d.evidence) == 2 for d in conflicts)
    assert "contextual_identifier_shared_not_merge" not in result.diagnostics
    assert len(result.organizations) == 50


@pytest.mark.parametrize(
    "names", [("ABC", "ABC"), ("ABC", "Alpha Beta Company"), ("example.org", "https://example.org")]
)
def test_names_never_supply_identity_or_merge(names: tuple[str, str]) -> None:
    context, rows = build_m22b_context(
        "organization_claims", [("partner", {"name": name}) for name in names]
    )
    claims = tuple(OrganizationClaim(role="partner", name=row["name"]) for row in rows)
    result = normalize_organizations(context, claims)
    assert isinstance(result, OrganizationNormalizationReport)
    assert result.claims == claims
    assert result.comparison_keys == ((), ())
    assert result.diagnostics == ("organization_identity_unverified",)
    assert len(result.organizations) == 2
    assert not result.promotable


def test_aggregate_text_budget_rejects_without_truncation() -> None:
    context, rows = build_m22b_context(
        "organization_claims", [("partner", {"institutional": "x" * 8192})]
    )
    identifier = OrganizationIdentifier(
        kind="institutional",
        value=rows[0]["institutional"],
        namespace=IdentifierNamespace(value="authority"),
    )
    claim = OrganizationClaim(role="partner", identifiers=(identifier,) * 129)
    result = normalize_organizations(context, (claim,))
    assert isinstance(result, OperationalError)
    assert result.code == "normalization_limits_exceeded"


def test_structured_identifier_diagnostic_preserves_unverified_existence() -> None:
    context, rows = build_m22b_context(
        "organization_claims", [("partner", {"cnpj": "04252011000111"})]
    )
    claim = OrganizationClaim(
        role="partner",
        identifiers=(
            OrganizationIdentifier(
                kind="cnpj", value=rows[0]["cnpj"], namespace=IdentifierNamespace(value="BR:CNPJ")
            ),
        ),
    )
    result = normalize_organizations(context, (claim,))
    assert isinstance(result, OrganizationNormalizationReport)
    identifier = result.organizations[0].identifiers[0]
    assert identifier.diagnostics == ("cnpj_checksum_invalid",)
    assert identifier.syntax_status == "valid"
    assert identifier.checksum_status == "invalid"
    assert identifier.existence_status == "unverified"
    assert result.comparison_keys == ((),)
    diagnostic = next(d for d in result.structured_diagnostics if d.code == "cnpj_checksum_invalid")
    assert diagnostic.claim_index == 0
    assert diagnostic.identifier_index == 0
    assert diagnostic.evidence == (rows[0]["cnpj"].provenance,)
    for field, value in [
        ("existence_status", "verified"),
        ("checksum_status", "valid"),
        ("syntax_status", "invalid"),
        ("diagnostics", []),
    ]:
        data = json.loads(identifier.model_dump_json())
        data[field] = value
        with pytest.raises(ValidationError):
            type(identifier)(**data)
        with pytest.raises(ValidationError):
            type(identifier).model_validate_json(json.dumps(data))


def test_shared_key_diagnostic_identifies_both_claims_and_exact_proofs() -> None:
    context, rows = build_m22b_context(
        "organization_claims",
        [("publishing", {"cnpj": "04.252.011/0001-10"}), ("funding", {"cnpj": "04252011000110"})],
    )
    claims = tuple(
        OrganizationClaim.model_validate(
            {
                "role": role,
                "identifiers": (
                    OrganizationIdentifier(
                        kind="cnpj",
                        value=row["cnpj"],
                        namespace=IdentifierNamespace(value="BR:CNPJ"),
                    ),
                ),
            }
        )
        for role, row in zip(("publishing", "funding"), rows, strict=True)
    )
    report = normalize_organizations(context, claims)
    assert isinstance(report, OrganizationNormalizationReport)
    issue = next(
        d
        for d in report.structured_diagnostics
        if d.code == "contextual_identifier_shared_not_merge"
    )
    assert (issue.claim_index, issue.related_claim_index) == (0, 1)
    assert issue.evidence == (rows[0]["cnpj"].provenance, rows[1]["cnpj"].provenance)
    assert OrganizationNormalizationReport.model_validate_json(report.model_dump_json()) == report


def test_structured_diagnostics_bind_claim_evidence_and_json() -> None:
    context, rows = build_m22b_context("organization_claims", [("publishing", {"name": "A"})])
    claim = OrganizationClaim(role="funding", name=rows[0]["name"])
    result = normalize_organizations(context, (claim,))
    assert isinstance(result, OrganizationNormalizationReport)
    diagnostic = next(
        d for d in result.structured_diagnostics if d.code == "organization_evidence_invalid"
    )
    assert diagnostic.claim_index == 0
    assert diagnostic.evidence == (rows[0]["name"].provenance,)
    assert result.diagnostics == (
        "organization_identity_unverified",
        "organization_evidence_invalid:0",
    )
    assert type(result).model_validate_json(result.model_dump_json()) == result
    for field, value in [("claim_index", 1), ("evidence", []), ("code", "invented")]:
        data = json.loads(result.model_dump_json())
        data.pop("audit")
        target = next(
            d
            for d in data["structured_diagnostics"]
            if d["code"] == "organization_evidence_invalid"
        )
        target[field] = value
        with pytest.raises(ValidationError):
            type(result).model_validate(data)
        with pytest.raises(ValidationError):
            type(result).model_validate_json(json.dumps(data))
