"""Exact seed classifications, never actionability or prose inference."""

from typing import Literal, Self

from pydantic import Field, model_validator

from .m22b_common import M22BReport
from .models import Contract, OperationalError
from .policies import AREAS, CATALOG_VERSION, OPPORTUNITY_TYPES, RESOURCE_TYPES
from .semantic_common import NormalizationContext, NormalizationDiagnostic, SemanticValue

TaxonomyDimension = Literal["opportunity_type", "resource_type", "area"]
TaxonomyRole = Literal["opportunity_type", "resource_type", "area", "unspecified"]


class TaxonomyClaim(Contract):
    role: TaxonomyRole
    value: SemanticValue


class TaxonomyInput(Contract):
    context: NormalizationContext
    claims: tuple[TaxonomyClaim, ...] = ()
    catalog_version: str = CATALOG_VERSION
    normalization_version: Literal["taxonomy-conservative-v1"] = "taxonomy-conservative-v1"


class NormalizedTaxonomy(Contract):
    claim: TaxonomyClaim
    catalog_version: str = CATALOG_VERSION
    canonical_code: str | None = None
    dimension: TaxonomyDimension | None = None
    mapping_rule: Literal["exact-code-v1"] | None = None
    status: Literal["mapped", "unknown", "ambiguous"] = "unknown"
    candidate_dimensions: tuple[TaxonomyDimension, ...] = Field(default=(), max_length=3)
    diagnostics: tuple[NormalizationDiagnostic, ...] = ()
    normalization_version: Literal["taxonomy-conservative-v1"] = "taxonomy-conservative-v1"

    @model_validator(mode="after")
    def consistent_mapping(self) -> Self:
        dimensions = exact_dimensions(self.claim.value.original, self.claim.role)
        codes = tuple(d.code for d in self.diagnostics)
        if any(
            d.claim_index is None
            or d.claim_index < 0
            or d.evidence != (self.claim.value.provenance,)
            for d in self.diagnostics
        ):
            raise ValueError("Taxonomy diagnostic requires its claim index and exact evidence")
        expected_code = None
        if self.catalog_version != CATALOG_VERSION:
            expected_code = "catalog_version_unsupported"
        elif codes == ("normalization_evidence_invalid",):
            # A standalone classification cannot authenticate its context. The
            # report independently verifies this refusal against the evidence.
            expected_code = "normalization_evidence_invalid"
        elif not dimensions:
            expected_code = "taxonomy_mapping_not_approved"
        elif self.claim.role == "unspecified":
            expected_code = (
                "taxonomy_mapping_ambiguous"
                if len(dimensions) > 1
                else "taxonomy_dimension_missing"
            )
        if expected_code is None:
            if (
                self.canonical_code != self.claim.value.original
                or self.dimension != self.claim.role
                or self.mapping_rule != "exact-code-v1"
                or self.status != "mapped"
                or self.candidate_dimensions
                or codes
            ):
                raise ValueError("Exact approved dimension/code requires its canonical mapping")
        else:
            ambiguous = expected_code == "taxonomy_mapping_ambiguous"
            if (
                codes != (expected_code,)
                or self.canonical_code is not None
                or self.dimension is not None
                or self.mapping_rule is not None
                or self.status != ("ambiguous" if ambiguous else "unknown")
                or self.candidate_dimensions != (dimensions if ambiguous else ())
            ):
                raise ValueError("Unresolved taxonomy must preserve its precise diagnostic")
        return self


class TaxonomyReport(M22BReport):
    input: TaxonomyInput
    classifications: tuple[NormalizedTaxonomy, ...] = ()
    diagnostics: tuple[NormalizationDiagnostic, ...] = ()
    normalization_version: Literal["taxonomy-conservative-v1"] = "taxonomy-conservative-v1"

    @model_validator(mode="after")
    def consistent_report(self) -> Self:
        # Local import avoids the DTO/normalizer import cycle. Recompute rather
        # than trusting an absent or caller-recomputed, unauthenticated audit.
        from .taxonomy_normalization import taxonomy_components

        expected = taxonomy_components(self.input)
        if isinstance(expected, OperationalError):
            raise ValueError(f"Taxonomy report input cannot normalize: {expected.code}")
        if (self.classifications, self.diagnostics) != expected:
            raise ValueError("Taxonomy outputs must match complete ordered input and evidence")
        return self


def exact_dimensions(original: str, role: TaxonomyRole) -> tuple[TaxonomyDimension, ...]:
    """No case folding, trimming, aliases or caller-provided catalogs."""
    catalogs: tuple[tuple[TaxonomyDimension, frozenset[str]], ...] = (
        ("opportunity_type", OPPORTUNITY_TYPES),
        ("resource_type", RESOURCE_TYPES),
        ("area", AREAS),
    )
    return tuple(
        dimension
        for dimension, codes in catalogs
        if (role == "unspecified" or role == dimension) and original in codes
    )
