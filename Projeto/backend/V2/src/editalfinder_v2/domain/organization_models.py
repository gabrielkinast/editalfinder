"""Offline organizations, NOT a mapper for SQL public.organizacao.

SQL has UUID id, optional slug codigo, nome_canonico, pais_codigo and
site_oficial, but no CNPJ column or organization identifier table. These
claims cannot be persisted as M2.1 opportunity identifiers or invented FKs.
"""

from typing import Literal, Self

from pydantic import Field, model_validator

from .identity_models import IdentifierNamespace
from .m22b_common import M22BReport
from .models import Contract, OperationalError
from .semantic_common import NormalizationContext, NormalizationDiagnostic, SemanticValue

OrganizationRole = Literal[
    "publishing", "funding", "managing", "executing", "partner", "beneficiary", "applicant"
]


class OrganizationIdentifier(Contract):
    value: SemanticValue
    kind: Literal["cnpj", "institutional"]
    namespace: IdentifierNamespace
    normalization_version: Literal["opaque-exact-v1", "opaque-nfc-v1"] = "opaque-exact-v1"


class NormalizedOrganizationIdentifier(Contract):
    claim: OrganizationIdentifier
    normalized: str | None
    syntax_status: Literal["valid", "invalid", "unsupported", "limit_exceeded"]
    checksum_status: Literal["valid", "invalid", "not_checked", "not_applicable"]
    existence_status: Literal["unverified"] = "unverified"
    diagnostics: tuple[str, ...]
    normalization_version: Literal["organization-conservative-v1"] = "organization-conservative-v1"

    @model_validator(mode="after")
    def consistent(self) -> Self:
        from .organization_normalization import _identifier_values

        if (self.normalized, self.syntax_status, self.checksum_status, self.diagnostics) != (
            _identifier_values(self.claim)
        ):
            raise ValueError("Inconsistent organization identifier normalization")
        return self


class OrganizationClaim(Contract):
    role: OrganizationRole
    name: SemanticValue | None = None
    identifiers: tuple[OrganizationIdentifier, ...] = ()


class NormalizedOrganization(Contract):
    """Lexical normalization only; supported contextual keys live in the report."""

    claim: OrganizationClaim
    normalized_name: str | None
    identifiers: tuple[NormalizedOrganizationIdentifier, ...]
    diagnostics: tuple[str, ...]
    normalization_version: Literal["organization-conservative-v1"] = "organization-conservative-v1"

    @model_validator(mode="after")
    def consistent(self) -> Self:
        from .organization_normalization import _organization_values

        if (self.normalized_name, self.identifiers, self.diagnostics) != (
            _organization_values(self.claim)
        ):
            raise ValueError("Inconsistent organization normalization")
        return self


class OrganizationDiagnostic(NormalizationDiagnostic):
    """Report-scoped evidence, including bounded conflict witnesses (not a merge)."""

    claim_index: int | None = Field(default=None, ge=0, strict=True)
    related_claim_index: int | None = Field(default=None, ge=0, strict=True)
    identifier_index: int | None = Field(default=None, ge=0, strict=True)


class OrganizationNormalizationReport(M22BReport):
    context: NormalizationContext
    claims: tuple[OrganizationClaim, ...]
    organizations: tuple[NormalizedOrganization, ...]
    comparison_keys: tuple[tuple[tuple[str, ...], ...], ...]
    structured_diagnostics: tuple[OrganizationDiagnostic, ...]
    diagnostics: tuple[str, ...]
    normalization_version: Literal["organization-conservative-v1"] = "organization-conservative-v1"

    @model_validator(mode="after")
    def consistent(self) -> Self:
        from .organization_normalization import _report_values

        expected = _report_values(self.context, self.claims)
        if (
            isinstance(expected, OperationalError)
            or (
                self.organizations,
                self.comparison_keys,
                self.diagnostics,
                self.structured_diagnostics,
            )
            != expected
        ):
            raise ValueError("Inconsistent organization context or derived report")
        return self
