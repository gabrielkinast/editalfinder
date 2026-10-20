"""Offline explicit-code taxonomy normalization; no decision or persistence."""

from .m22b_common import matches_m22b, prepare_m22b
from .models import OperationalError
from .policies import CATALOG_VERSION
from .semantic_common import NormalizationDiagnostic
from .taxonomy_models import NormalizedTaxonomy, TaxonomyInput, TaxonomyReport, exact_dimensions


def taxonomy_components(
    data: TaxonomyInput,
) -> tuple[tuple[NormalizedTaxonomy, ...], tuple[NormalizationDiagnostic, ...]] | OperationalError:
    """Reproducible components also checked on report deserialization."""
    prepared = prepare_m22b(
        data.context,
        claim_count=len(data.claims),
        values=tuple(claim.value for claim in data.claims),
        extra_text=(data.catalog_version,),
    )
    if isinstance(prepared, OperationalError):
        return prepared
    classifications = []
    for index, claim in enumerate(data.claims):
        dimensions = exact_dimensions(claim.value.original, claim.role)
        code = None
        if data.catalog_version != CATALOG_VERSION:
            code = "catalog_version_unsupported"
        elif not matches_m22b(prepared, claim.value, claim.role, collection="taxonomy_claims"):
            code = "normalization_evidence_invalid"
        elif not dimensions:
            code = "taxonomy_mapping_not_approved"
        elif claim.role == "unspecified":
            code = (
                "taxonomy_mapping_ambiguous"
                if len(dimensions) > 1
                else "taxonomy_dimension_missing"
            )
        issues = (
            ()
            if code is None
            else (
                NormalizationDiagnostic(
                    code=code,
                    message="Only approved exact codes with explicit dimensions may map.",
                    claim_index=index,
                    evidence=(claim.value.provenance,),
                ),
            )
        )
        classifications.append(
            NormalizedTaxonomy(
                claim=claim,
                catalog_version=data.catalog_version,
                canonical_code=claim.value.original if code is None else None,
                dimension=dimensions[0] if code is None else None,
                mapping_rule="exact-code-v1" if code is None else None,
                status="mapped"
                if code is None
                else ("ambiguous" if code == "taxonomy_mapping_ambiguous" else "unknown"),
                candidate_dimensions=dimensions if code == "taxonomy_mapping_ambiguous" else (),
                diagnostics=issues,
            )
        )
    diagnostics = (
        ()
        if data.claims
        else (
            NormalizationDiagnostic(
                code="taxonomy_classifications_missing",
                message="No classifications supplied.",
            ),
        )
    )
    return tuple(classifications), diagnostics


def normalize_taxonomy(data: TaxonomyInput) -> TaxonomyReport | OperationalError:
    components = taxonomy_components(data)
    if isinstance(components, OperationalError):
        return components
    classifications, diagnostics = components
    return TaxonomyReport(input=data, classifications=classifications, diagnostics=diagnostics)
