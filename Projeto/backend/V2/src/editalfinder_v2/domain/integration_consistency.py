"""Small deterministic observations over approved, candidate-local domain reports.

No parser, normalizer, validation decision, identity merge or authorization lives
here. Only IntegrationReport's complete replay makes observations evaluated output.
Rules and unsupported relationships: docs/v2/INTEGRATION_CONSISTENCY_M23B.md.
"""

from decimal import Decimal
from typing import Literal

from .financial_models import FinancialInput, FinancialReport
from .geography_models import GeographyInput, GeographyReport
from .identity_models import IdentityEvidence
from .integration_budget import integration_claim_count
from .integration_models import (
    CandidateIntegrationInput,
    ConsistencyDomain,
    DomainClaimReference,
    DomainNormalizationResults,
    IntegrationDiagnostic,
    NormalizationVersionReference,
)
from .m22b_common import matches_m22b
from .models import OperationalError, ValidationReport
from .organization_models import OrganizationNormalizationReport
from .semantic_common import SemanticValue, prepare_context
from .taxonomy_models import TaxonomyInput, TaxonomyReport
from .temporal_models import TemporalInput, TemporalReport


def evaluate_consistency(
    candidate_input: CandidateIntegrationInput,
    normalized_results: DomainNormalizationResults,
    validation_result: ValidationReport | OperationalError,
) -> tuple[IntegrationDiagnostic, ...] | OperationalError:
    """Observe this candidate only; no relationship is inferred from identity."""
    context = candidate_input.context
    item = candidate_input
    prepared = prepare_context(context, claim_count=integration_claim_count(item))
    if isinstance(prepared, OperationalError):
        return prepared
    reports: tuple[
        tuple[
            ConsistencyDomain,
            TemporalReport
            | GeographyReport
            | FinancialReport
            | OrganizationNormalizationReport
            | TaxonomyReport
            | OperationalError,
        ],
        ...,
    ] = (
        ("temporal", normalized_results.temporal),
        ("geography", normalized_results.geography),
        ("financial", normalized_results.financial),
        ("organizations", normalized_results.organizations),
        ("taxonomy", normalized_results.taxonomy),
    )
    expected = {
        "temporal": TemporalInput(context=context, events=item.temporal),
        "geography": GeographyInput(
            context=context, locations=item.geography, scope=item.geographic_scope
        ),
        "financial": FinancialInput(context=context, claims=item.financial),
        "taxonomy": TaxonomyInput(
            context=context, claims=item.taxonomy, catalog_version=item.catalog_version
        ),
    }
    mismatch = any(
        (report.context != context or report.claims != item.organizations)
        if isinstance(report, OrganizationNormalizationReport)
        else report.input != expected[domain]
        for domain, report in reports
        if not isinstance(report, OperationalError)
    )
    if isinstance(validation_result, ValidationReport):
        mismatch |= (
            validation_result.candidate != context.candidate
            or validation_result.snapshots != context.snapshots
        )
    mismatch |= any(
        isinstance(report, OperationalError) and report.candidate_id != context.candidate.id
        for _, report in reports
    )
    mismatch |= (
        isinstance(validation_result, OperationalError)
        and validation_result.candidate_id != context.candidate.id
    )
    if mismatch:
        return (
            IntegrationDiagnostic(
                code="consistency_context_mismatch",
                message="Reports are not bound to this candidate's complete domain input.",
                domain="integration",
                classification="insufficient_information",
                domains=("integration",),
                claim_references=(),
                evidence=(),
                normalization_versions=(),
                version="m2.3b-consistency-v1",
            ),
        )
    versions = {
        domain: NormalizationVersionReference(
            domain=domain,
            version=report.normalization_version,
            policy_version=report.policy_version,
            catalog_version=report.input.catalog_version
            if isinstance(report, TaxonomyReport)
            else None,
        )
        for domain, report in reports
        if not isinstance(report, OperationalError)
    }
    if isinstance(validation_result, ValidationReport):
        versions["validation"] = NormalizationVersionReference(
            domain="validation",
            version=validation_result.ruleset_version,
            catalog_version=validation_result.audit.catalog_version
            if validation_result.audit is not None
            else None,
        )
    observations: list[IntegrationDiagnostic] = []

    def emit(
        code: str,
        message: str,
        classification: Literal[
            "contradiction",
            "potential_conflict",
            "insufficient_information",
            "no_conflict_detected",
        ],
        references: tuple[DomainClaimReference, ...] = (),
        evidence: tuple[IdentityEvidence, ...] = (),
        domains: tuple[ConsistencyDomain, ...] = (),
    ) -> None:
        affected = domains or tuple(
            dict.fromkeys(
                ("geography" if r.domain == "geographic_scope" else r.domain) for r in references
            )
        )
        observations.append(
            IntegrationDiagnostic(
                version="m2.3b-consistency-v1",
                code=code,
                message=message,
                domain="integration",
                classification=classification,
                domains=affected,
                claim_references=references,
                evidence=evidence,
                normalization_versions=tuple(versions[d] for d in affected if d in versions),
            )
        )

    for domain, report in reports:
        if isinstance(report, OperationalError):
            emit(
                "consistency_domain_unavailable",
                "A domain returned an operational failure; no semantic consistency"
                " conclusion for that domain.",
                "insufficient_information",
                domains=(domain,),
            )
    if isinstance(validation_result, OperationalError):
        emit(
            "consistency_domain_unavailable",
            "Validation failed operationally; consistency diagnostics cannot replace M1.",
            "insufficient_information",
            domains=("validation",),
        )

    def temporal_rules() -> None:
        temporal = normalized_results.temporal
        if isinstance(temporal, TemporalReport):
            valid_events = {
                i: event
                for i, event in enumerate(temporal.events)
                if event.claim.value is not None
                and prepared.matches(
                    event.claim.value, event.claim.role, collection="temporal_events"
                )
            }
            for i in range(len(temporal.events)):
                if i not in valid_events:
                    emit(
                        "consistency_claim_evidence_unavailable",
                        "Temporal claim lacks candidate-local evidence; no relationship inferred.",
                        "insufficient_information",
                        (DomainClaimReference(domain="temporal", claim_index=i),),
                    )
            for issue in temporal.diagnostics:
                if issue.code not in {
                    "temporal_deadline_conflict",
                    "temporal_deadline_not_comparable",
                }:
                    continue
                origins = set(issue.evidence)
                related_events = [
                    (i, e)
                    for i, e in valid_events.items()
                    if e.claim.value is not None and e.claim.value.provenance in origins
                ]
                if len(related_events) < 2:
                    continue
                comparable = all(e.civil_date is not None for _, e in related_events) or all(
                    e.instant_utc is not None for _, e in related_events
                )
                emit(
                    "consistency_temporal_stage_unverified",
                    "Distinct deadlines retain their roles; stage identity, timezone "
                    "comparability and document precedence must not be inferred.",
                    "potential_conflict" if comparable else "insufficient_information",
                    tuple(
                        DomainClaimReference(domain="temporal", claim_index=i)
                        for i, _ in related_events
                    ),
                    tuple(
                        e.claim.value.provenance
                        for _, e in related_events
                        if e.claim.value is not None
                    ),
                )
            openings = [
                (i, e) for i, e in valid_events.items() if e.claim.role == "submission_opening_date"
            ]
            closings = [
                (i, e) for i, e in valid_events.items() if e.claim.role == "submission_deadline"
            ]
            phased = any(
                e.claim.role in {"preliminary_application_deadline", "full_application_deadline"}
                for e in temporal.events
            )
            if len(openings) == len(closings) == 1 and not phased:
                left_index, left = openings[0]
                right_index, right = closings[0]
                comparable = (left.civil_date is not None and right.civil_date is not None) or (
                    left.instant_utc is not None and right.instant_utc is not None
                )
                reversed_window = (
                    left.civil_date > right.civil_date
                    if left.civil_date is not None and right.civil_date is not None
                    else left.instant_utc > right.instant_utc
                    if left.instant_utc is not None and right.instant_utc is not None
                    else False
                )
                if reversed_window or not comparable:
                    emit(
                        "consistency_temporal_window_unverified",
                        "Opening/closing relationship lacks explicit shared window "
                        "identity; no phase, cutoff or timezone is invented.",
                        "potential_conflict" if comparable else "insufficient_information",
                        (
                            DomainClaimReference(domain="temporal", claim_index=left_index),
                            DomainClaimReference(domain="temporal", claim_index=right_index),
                        ),
                        tuple(
                            e.claim.value.provenance
                            for e in (left, right)
                            if e.claim.value is not None
                        ),
                    )
            if any(e.claim.role == "rectification_date" for e in valid_events.values()):
                related_events = [
                    (i, e)
                    for i, e in valid_events.items()
                    if e.claim.role
                    in {
                        "rectification_date",
                        "submission_deadline",
                        "preliminary_application_deadline",
                        "full_application_deadline",
                    }
                ]
                emit(
                    "consistency_rectification_precedence_unverified",
                    "Rectification does not establish target event, supersession or "
                    "valid deadline; every original event is preserved.",
                    "insufficient_information",
                    tuple(
                        DomainClaimReference(domain="temporal", claim_index=i)
                        for i, _ in related_events
                    ),
                    tuple(
                        e.claim.value.provenance
                        for _, e in related_events
                        if e.claim.value is not None
                    ),
                )

    temporal_rules()

    def geography_rules() -> None:
        geography = normalized_results.geography
        scope = item.geographic_scope
        if (
            isinstance(geography, GeographyReport)
            and scope is not None
            and prepared.matches(scope, "geographic_scope")
        ):
            for issue in geography.diagnostics:
                if issue.code != "geo_scope_conflict" or issue.claim_index is None:
                    continue
                index = issue.claim_index
                location_claim = item.geography[index]
                country = location_claim.country_code
                if (
                    country is not None
                    and location_claim.role == "elegibilidade"
                    and prepared.matches(
                        country,
                        location_claim.role,
                        collection="geographic_locations",
                        component="country_code",
                    )
                ):
                    emit(
                        "consistency_geographic_scope_relationship_unverified",
                        "Generic scope and applicant eligibility are distinct; exclusivity"
                        " is not established by the scope label or source country.",
                        "insufficient_information",
                        (
                            DomainClaimReference(domain="geographic_scope", claim_index=0),
                            DomainClaimReference(domain="geography", claim_index=index),
                        ),
                        (scope.provenance, country.provenance),
                    )

    geography_rules()

    def organizations_rules() -> None:
        organizations = normalized_results.organizations
        if isinstance(organizations, OrganizationNormalizationReport):
            for issue in organizations.structured_diagnostics:
                if issue.code != "organization_comparable_identifier_conflict":
                    continue
                if issue.claim_index is None or issue.related_claim_index is None:
                    continue
                emit(
                    "consistency_organization_identity_unverified",
                    "Comparable identifier witnesses differ, but shared legal-entity "
                    "identity/cardinality is unverified; multiple funders remain "
                    "legitimate.",
                    "insufficient_information",
                    (
                        DomainClaimReference(domain="organizations", claim_index=issue.claim_index),
                        DomainClaimReference(
                            domain="organizations", claim_index=issue.related_claim_index
                        ),
                    ),
                    issue.evidence,
                )

    organizations_rules()

    def financial_rules() -> None:
        financial = normalized_results.financial
        if isinstance(financial, FinancialReport):
            minima: dict[tuple[str, str], tuple[Decimal, int, IdentityEvidence]] = {}
            maxima: dict[tuple[str, str], tuple[Decimal, int, IdentityEvidence]] = {}
            for index, result in enumerate(financial.claims):
                value = result.claim.value
                refs = (DomainClaimReference(domain="financial", claim_index=index),)
                if value is None:
                    emit(
                        "consistency_financial_interpretation_unresolved",
                        "Financial terms are absent; no financial relationship can be established.",
                        "insufficient_information",
                        refs,
                    )
                    continue
                if not matches_m22b(
                    prepared, value, result.claim.role, collection="financial_claims"
                ):
                    emit(
                        "consistency_claim_evidence_unavailable",
                        "Claim lacks candidate-local evidence; no relationship inferred.",
                        "insufficient_information",
                        refs,
                    )
                    continue
                if result.normalized is None or (
                    result.normalized.codes
                    and "financial_range_reversed" not in result.normalized.codes
                    and result.normalized.codes != ("financial_expenses_text_only",)
                ):
                    emit(
                        "consistency_financial_interpretation_unresolved",
                        "Financial interpretation is unresolved or outside supported "
                        "semantics; no magnitude inference.",
                        "insufficient_information",
                        refs,
                        (value.provenance,),
                    )
                if (
                    value is not None
                    and result.normalized is not None
                    and "financial_range_reversed" in result.normalized.codes
                    and matches_m22b(
                        prepared, value, result.claim.role, collection="financial_claims"
                    )
                ):
                    emit(
                        "consistency_financial_range_contradiction",
                        "One explicitly declared financial range has reversed endpoints "
                        "under its supplied interpretation; no cross-instrument "
                        "comparison.",
                        "contradiction",
                        (DomainClaimReference(domain="financial", claim_index=index),),
                        (value.provenance,),
                    )
                normalized = result.normalized
                if (
                    normalized is not None
                    and not normalized.codes
                    and len(normalized.amounts) == 1
                    and normalized.currency is not None
                ):
                    key: tuple[str, str] = (normalized.currency, result.claim.unit)
                    target = minima if result.claim.role == "proposal_minimum" else maxima
                    if result.claim.role in {"proposal_minimum", "proposal_maximum"}:
                        amount = normalized.amounts[0]
                        previous = target.get(key)
                        if previous is None or (
                            amount > previous[0] if target is minima else amount < previous[0]
                        ):
                            target[key] = (amount, index, value.provenance)
            for key, (amount, index, proof) in minima.items():
                other = maxima.get(key)
                if other is not None and amount > other[0]:
                    emit(
                        "consistency_financial_bounds_scope_unverified",
                        "Minimum exceeds maximum in comparable declared currency/unit, but"
                        " a shared instrument/award scope is not established.",
                        "potential_conflict",
                        (
                            DomainClaimReference(domain="financial", claim_index=index),
                            DomainClaimReference(domain="financial", claim_index=other[1]),
                        ),
                        (proof, other[2]),
                    )
            if minima and maxima and (minima.keys() != maxima.keys()):
                unmatched = [row for key, row in minima.items() if key not in maxima] + [
                    row for key, row in maxima.items() if key not in minima
                ]
                emit(
                    "consistency_financial_bounds_not_comparable",
                    "Supplied bounds have unmatched currencies or units; no numerical "
                    "comparison or conversion is authorized.",
                    "insufficient_information",
                    tuple(
                        DomainClaimReference(domain="financial", claim_index=row[1])
                        for row in unmatched
                    ),
                    tuple(row[2] for row in unmatched),
                )

    financial_rules()

    def taxonomy_rules() -> None:
        taxonomy = normalized_results.taxonomy
        if isinstance(taxonomy, TaxonomyReport):
            for index, classification in enumerate(taxonomy.classifications):
                tax_claim = classification.claim
                refs = (DomainClaimReference(domain="taxonomy", claim_index=index),)
                if not matches_m22b(
                    prepared, tax_claim.value, tax_claim.role, collection="taxonomy_claims"
                ):
                    emit(
                        "consistency_claim_evidence_unavailable",
                        "Claim lacks candidate-local evidence; no relationship inferred.",
                        "insufficient_information",
                        refs,
                    )
                elif classification.status != "mapped":
                    emit(
                        "consistency_taxonomy_unsupported",
                        "The declared classification has no approved unambiguous mapping; "
                        "original retained.",
                        "insufficient_information",
                        refs,
                        (tax_claim.value.provenance,),
                    )
            mapped_rows = [
                (i, row)
                for i, row in enumerate(taxonomy.classifications)
                if row.status == "mapped"
                and matches_m22b(
                    prepared, row.claim.value, row.claim.role, collection="taxonomy_claims"
                )
            ]
            resource_rows = [(i, row) for i, row in mapped_rows if row.dimension == "resource_type"]
            kind_references: list[DomainClaimReference] = []
            kind_evidence: list[IdentityEvidence] = []
            if mapped_rows and isinstance(validation_result, ValidationReport):
                for i, assertion in enumerate(context.candidate.assertions):
                    if assertion.field != "content_kind" or assertion.value not in {
                        "news",
                        "result",
                    }:
                        continue
                    for raw_proof in assertion.evidence:
                        snapshot = prepared.snapshots.get(raw_proof.snapshot_id)
                        if snapshot is None:
                            continue
                        origin = IdentityEvidence(
                            candidate_id=context.candidate.id,
                            source_id=context.candidate.source_id,
                            execution_id=snapshot.execution_id,
                            evidence=raw_proof,
                        )
                        value = SemanticValue(original=str(assertion.value), provenance=origin)
                        if prepared.matches(value, "content_kind"):
                            kind_references.append(
                                DomainClaimReference(domain="validation", claim_index=i)
                            )
                            kind_evidence.append(origin)
                if kind_references:
                    emit(
                        "consistency_taxonomy_not_actionability",
                        "An approved classification in declared news/results does not "
                        "establish an actionable opportunity; M1 decision is unchanged.",
                        "insufficient_information",
                        tuple(
                            DomainClaimReference(domain="taxonomy", claim_index=i)
                            for i, _ in mapped_rows
                        )
                        + tuple(kind_references),
                        tuple(row.claim.value.provenance for _, row in mapped_rows)
                        + tuple(kind_evidence),
                        domains=("taxonomy", "validation"),
                    )
            codes = {row.canonical_code for _, row in resource_rows}
            if "financiamento_nao_reembolsavel" in codes and codes & {
                "credito",
                "financiamento_reembolsavel",
            }:
                related = [
                    (i, row)
                    for i, row in resource_rows
                    if row.canonical_code
                    in {"financiamento_nao_reembolsavel", "credito", "financiamento_reembolsavel"}
                ]
                emit(
                    "consistency_hybrid_relationship_unverified",
                    "Grant and repayable classifications can form a legitimate hybrid;"
                    " their relationship is unverified.",
                    "insufficient_information",
                    tuple(
                        DomainClaimReference(domain="taxonomy", claim_index=i) for i, _ in related
                    ),
                    tuple(row.claim.value.provenance for _, row in related),
                    domains=("taxonomy", "financial"),
                )
            credit_rows = [
                (i, row)
                for i, row in resource_rows
                if row.canonical_code in {"credito", "financiamento_reembolsavel"}
            ]
            if credit_rows:
                emit(
                    "consistency_credit_terms_unrepresented",
                    "Credit classification does not prove principal, interest, "
                    "guarantee or repayment terms; current FinancialRole has no "
                    "credit-principal role.",
                    "insufficient_information",
                    tuple(
                        DomainClaimReference(domain="taxonomy", claim_index=i)
                        for i, _ in credit_rows
                    ),
                    tuple(row.claim.value.provenance for _, row in credit_rows),
                    domains=("taxonomy", "financial"),
                )

    taxonomy_rules()

    if not observations:
        emit(
            "consistency_no_conflict_detected",
            "No conflict established by implemented consistency rules; not a "
            "guarantee of complete consistency, eligibility or actionability.",
            "no_conflict_detected",
            domains=tuple(versions),
        )
    return tuple(observations)
