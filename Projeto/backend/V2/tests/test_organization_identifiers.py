"""Organization identifier syntax is not legal identity or registry existence."""

from uuid import UUID

import pytest
from pydantic import ValidationError

from editalfinder_v2.domain.identity_models import IdentifierNamespace, IdentityEvidence
from editalfinder_v2.domain.models import Evidence
from editalfinder_v2.domain.organization_models import OrganizationIdentifier
from editalfinder_v2.domain.organization_normalization import normalize_organization_identifier
from editalfinder_v2.domain.semantic_common import SemanticValue


def value(text: str) -> SemanticValue:
    return SemanticValue(
        original=text,
        provenance=IdentityEvidence(
            candidate_id=UUID(int=1),
            source_id=UUID(int=2),
            execution_id=UUID(int=3),
            evidence=Evidence(
                snapshot_id=UUID(int=4),
                pointer="/record/publishing.cnpj",
                quote=text,
                method="literal",
                method_version="1",
                confidence=1,
            ),
        ),
    )


@pytest.mark.parametrize("original", ["04.252.011/0001-10", "04252011000110"])
def test_numeric_cnpj(original: str) -> None:
    claim = OrganizationIdentifier(
        value=value(original), kind="cnpj", namespace=IdentifierNamespace(value="BR:CNPJ")
    )
    result = normalize_organization_identifier(claim)
    assert result.normalized == "04252011000110"
    assert result.syntax_status == "valid"
    assert result.checksum_status == "valid"
    assert result.existence_status == "unverified"
    assert result.claim == claim
    assert type(result).model_validate_json(result.model_dump_json()) == result
    data = result.model_dump()
    data["normalized"] = "11222333000181"
    with pytest.raises(ValidationError):
        type(result).model_validate(data)


@pytest.mark.parametrize(
    ("text", "syntax", "checksum"),
    [
        ("04252011000111", "valid", "invalid"),
        ("00000000000000", "valid", "invalid"),
        ("１１２２２３３３０００１８１", "invalid", "not_checked"),
        ("04 252 011 0001 10", "invalid", "not_checked"),
        ("04.252.011/0001-10 ", "invalid", "not_checked"),
        ("12ABC34501DE35", "unsupported", "not_checked"),
        ("x" * 8193, "limit_exceeded", "not_checked"),
        (" ", "invalid", "not_checked"),
    ],
)
def test_cnpj_rejects_without_inventing_policy(text: str, syntax: str, checksum: str) -> None:
    result = normalize_organization_identifier(
        OrganizationIdentifier(
            value=value(text), kind="cnpj", namespace=IdentifierNamespace(value="BR:CNPJ")
        )
    )
    assert result.syntax_status == syntax
    assert result.checksum_status == checksum
    assert result.normalized is None


@pytest.mark.parametrize(
    ("policy", "expected"),
    [
        ("opaque-exact-v1", " e\u0301-001 "),
        ("opaque-nfc-v1", " é-001 "),
    ],
)
def test_institutional_opaque_policy(policy: str, expected: str) -> None:
    claim = OrganizationIdentifier.model_validate(
        dict(
            value=value(" e\u0301-001 "),
            kind="institutional",
            namespace=IdentifierNamespace(value="explicit authority"),
            normalization_version=policy,
        )
    )
    result = normalize_organization_identifier(claim)
    assert result.normalized == expected
    assert result.checksum_status == "not_applicable"


@pytest.mark.parametrize("namespace", [" ", "\u200b", "a" * 8193])
def test_invalid_namespace_is_not_comparable(namespace: str) -> None:
    result = normalize_organization_identifier(
        OrganizationIdentifier(
            value=value("04252011000110"),
            kind="cnpj",
            namespace=IdentifierNamespace(value=namespace),
        )
    )
    assert result.normalized is None
    assert "namespace_invalid" in result.diagnostics
