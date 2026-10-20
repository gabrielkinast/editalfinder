"""Immutable offline integration DTOs; audits are integrity, not authority."""

import hashlib
from collections.abc import Mapping
from datetime import date
from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, ValidationInfo, field_validator, model_validator

from .financial_models import FinancialClaim, FinancialReport
from .geography_models import GeographyLocationClaim, GeographyReport
from .identity_models import (
    ExternalIdentifier,
    IdentityEvidence,
    IdentityResolutionReport,
    PublicationCycle,
)
from .integration_budget import MAX_OUTPUT_BUDGET, projected_output_cost, wire_cost
from .models import Contract, Digest, OperationalError, ValidationReport
from .organization_models import OrganizationClaim, OrganizationNormalizationReport
from .semantic_common import NormalizationContext, SemanticValue
from .taxonomy_models import TaxonomyClaim, TaxonomyReport
from .temporal_models import TemporalClaim, TemporalReport

Index = Annotated[int, Field(strict=True, ge=0)]


class CandidateIntegrationInput(Contract):
    """Explicit claims for ONE candidate; no inferred associations or trust input."""

    context: NormalizationContext
    identifiers: tuple[ExternalIdentifier, ...] = ()
    cycle: PublicationCycle | None = None
    temporal: tuple[TemporalClaim, ...] = ()
    geography: tuple[GeographyLocationClaim, ...] = ()
    geographic_scope: SemanticValue | None = None
    financial: tuple[FinancialClaim, ...] = ()
    organizations: tuple[OrganizationClaim, ...] = ()
    taxonomy: tuple[TaxonomyClaim, ...] = ()
    catalog_version: str = "seeds-000002"


class IdentityComparison(Contract):
    left_index: Index
    right_index: Index


class IntegrationInput(Contract):
    candidates: tuple[CandidateIntegrationInput, ...]
    reference_date: Annotated[date, Field(strict=True)]
    identity_comparisons: tuple[IdentityComparison, ...] = ()
    integration_version: Literal["m2.3-integration-v1"] = "m2.3-integration-v1"

    @field_validator("reference_date", mode="before")
    @classmethod
    def strict_day(cls, value: object, info: ValidationInfo) -> date:
        if info.mode == "json" and isinstance(value, str):
            parsed = date.fromisoformat(value)
            if parsed.isoformat() != value:
                raise ValueError("Reference date requires YYYY-MM-DD")
            return parsed
        if type(value) is not date:
            raise ValueError("Reference date requires an explicit date, not datetime or coercion")
        return value


class DomainNormalizationResults(Contract):
    """Original domain reports, including their policies, audits and technical failures."""

    temporal: TemporalReport | OperationalError
    geography: GeographyReport | OperationalError
    financial: FinancialReport | OperationalError
    organizations: OrganizationNormalizationReport | OperationalError
    taxonomy: TaxonomyReport | OperationalError


ConsistencyDomain = Literal[
    "temporal", "geography", "financial", "organizations", "taxonomy", "validation", "integration"
]


class DomainClaimReference(Contract):
    """Index into this candidate's domain claims; scope is an explicit singleton."""

    domain: Literal[
        "temporal",
        "geography",
        "geographic_scope",
        "financial",
        "organizations",
        "taxonomy",
        "validation",
    ]
    claim_index: Index


class NormalizationVersionReference(Contract):
    domain: ConsistencyDomain
    version: str
    policy_version: str | None = None
    catalog_version: str | None = None


class IntegrationDiagnostic(Contract):
    """Consistency observations, never validation decisions or authorization.

    Only the enclosing IntegrationReport verifies evaluation/provenance. Legacy
    claim_indices is retained but new rules use domain-qualified references.
    """

    classification: Literal[
        "contradiction", "potential_conflict", "insufficient_information", "no_conflict_detected"
    ]
    domains: tuple[ConsistencyDomain, ...]
    claim_references: tuple[DomainClaimReference, ...]
    normalization_versions: tuple[NormalizationVersionReference, ...]

    code: str
    message: str
    domain: Literal[
        "integration",
        "identity",
        "temporal",
        "geography",
        "financial",
        "organizations",
        "taxonomy",
        "trust",
    ]
    claim_indices: tuple[Index, ...] = ()
    evidence: tuple[IdentityEvidence, ...]
    version: Literal["m2.3b-consistency-v1"]


class IntegratedCandidate(Contract):
    input: CandidateIntegrationInput
    normalizations: DomainNormalizationResults
    validation: ValidationReport | OperationalError
    diagnostics: tuple[IntegrationDiagnostic, ...]


class IntegrationAudit(Contract):
    """Received metadata must be explicit; absence is not historical provenance."""

    schema_version: Literal[2] = Field(...)
    output_budget_version: Literal["m2.3a.1-output-budget-v1"]
    report_digest: Digest
    algorithm: Literal["sha256"]
    hash_version: Literal["integration-pydantic-json-utf8-v1"]
    limits_version: Literal["m2.3-integration-limits-v1"]


class IntegrationReport(Contract):
    """Ordered replay-checked results, never a persistence or promotion capability.

    Ordinary construction and Python/JSON validation recompute the complete
    outputs, even without an audit. Standalone nested DTOs are not evaluated
    reports. Unchecked Pydantic copies/construction are trusted-code escapes.
    No envelope (or audit=None) means new local verification, not restoration
    of historical metadata. Supplied envelopes must be complete. Explicit input
    replay with source/current policy separation is documented in
    docs/v2/INTEGRATION_AUDIT_REPROCESSING.md.
    """

    model_config = ConfigDict(hide_input_in_errors=True)

    input: IntegrationInput
    candidates: tuple[IntegratedCandidate | OperationalError, ...]
    identity_results: tuple[IdentityResolutionReport | OperationalError, ...]
    audit: IntegrationAudit | None = None
    integration_version: Literal["m2.3-integration-v1"] = "m2.3-integration-v1"

    @model_validator(mode="before")
    @classmethod
    def admit_report(cls, value: object) -> object:
        # Reject before Pydantic constructs/audits the nested domain reports.
        # JSON decoding itself has already occurred: transport caps remain separate.
        if isinstance(value, Mapping) and (
            projected_output_cost(value.get("input")) > MAX_OUTPUT_BUDGET
            or wire_cost(value) > MAX_OUTPUT_BUDGET
        ):
            raise ValueError("integration_output_budget_exceeded")
        return value

    @model_validator(mode="after")
    def verify_outputs(self) -> Self:
        from .integration import evaluate_integration

        expected = evaluate_integration(self.input)
        if (
            isinstance(expected, OperationalError)
            or (self.candidates, self.identity_results) != expected
        ):
            raise ValueError("Integration outputs must match complete ordered input")
        # This is new local verification, not backfill of a supplied envelope.
        audit = IntegrationAudit(
            schema_version=2,
            output_budget_version="m2.3a.1-output-budget-v1",
            algorithm="sha256",
            hash_version="integration-pydantic-json-utf8-v1",
            limits_version="m2.3-integration-limits-v1",
            report_digest=hashlib.sha256(
                self.model_dump_json(exclude={"audit"}).encode("utf-8")
            ).hexdigest(),
        )
        if self.audit is not None and self.audit != audit:
            raise ValueError("Integration audit does not match complete report")
        object.__setattr__(self, "audit", audit)
        return self

    @property
    def promotable(self) -> bool:
        return False
