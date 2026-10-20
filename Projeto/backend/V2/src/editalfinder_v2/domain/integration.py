"""Deterministic offline integration, with no projection or authorization.

Limits policy m2.3-integration-limits-v1: at most 32 candidates, 64 explicitly
requested comparisons, 4,800 combined claims and 16 MiB of unique snapshot
representations (UTF-8 payload bytes). Claims include identifiers, cycle and
scope. Shared identical snapshots count once; conflicting representations still
consume the budget. Existing per-candidate/domain limits remain in force.
M2.3a.1 additionally checks the conservative 64 MiB expanded-output/work
budget BEFORE constructing any domain report (integration_budget.py). Exceeding
it returns integration_output_budget_exceeded without truncating the request.

Global limit, duplicate candidate UUID and out-of-range comparison errors abort
the batch as OperationalError, attributed to its first candidate (nil UUID for
an empty batch). Conflicting snapshot UUIDs fail every affected owner only.
Context-preflight failures occupy that candidate's ordered slot; comparisons
involving those slots return integration_identity_context_failed. Later domain
failures remain in their own result slots and never become semantic rejection.

M2.3b observes consistency over candidate-local reports. It does not project M2
values into M1 assertions, change M1 decisions, merge identities, authenticate
review or enable writes.
"""

from uuid import UUID

from .financial_models import FinancialInput
from .financial_normalization import normalize_financial
from .geography_models import GeographyInput
from .geography_normalization import normalize_geography
from .identity_models import IdentityResolutionReport, IdentitySubject
from .identity_resolution import resolve_identity
from .integration_budget import MAX_OUTPUT_BUDGET, integration_claim_count, projected_output_cost
from .integration_consistency import evaluate_consistency
from .integration_models import (
    DomainNormalizationResults,
    IntegratedCandidate,
    IntegrationInput,
    IntegrationReport,
)
from .models import OperationalError, RawSnapshot
from .organization_normalization import normalize_organizations
from .semantic_common import prepare_context
from .taxonomy_models import TaxonomyInput
from .taxonomy_normalization import normalize_taxonomy
from .temporal_models import TemporalInput
from .temporal_normalization import normalize_temporal
from .validation import validate

IntegrationOutputs = tuple[
    tuple[IntegratedCandidate | OperationalError, ...],
    tuple[IdentityResolutionReport | OperationalError, ...],
]


def evaluate_integration(data: IntegrationInput) -> IntegrationOutputs | OperationalError:
    """Evaluate components without constructing a recursive integration report."""
    candidate_id = data.candidates[0].context.candidate.id if data.candidates else UUID(int=0)
    claim_counts = tuple(integration_claim_count(item) for item in data.candidates)
    if len(data.candidates) > 32 or len(data.identity_comparisons) > 64 or sum(claim_counts) > 4800:
        return OperationalError(
            candidate_id=candidate_id, code="integration_limits_exceeded", stage="integration"
        )
    # Count each distinct immutable snapshot representation once. Conflicting UUID
    # representations still consume resources; their affected owners are handled below.
    unique_snapshots = {s for item in data.candidates for s in item.context.snapshots}
    if sum(len(s.payload_json.encode("utf-8")) for s in unique_snapshots) > 16 * 1024 * 1024:
        return OperationalError(
            candidate_id=candidate_id, code="integration_limits_exceeded", stage="integration"
        )
    ids = [item.context.candidate.id for item in data.candidates]
    if len(set(ids)) != len(ids):
        return OperationalError(
            candidate_id=candidate_id,
            code="integration_duplicate_candidate_id",
            stage="integration",
        )
    if any(
        pair.left_index >= len(ids) or pair.right_index >= len(ids)
        for pair in data.identity_comparisons
    ):
        return OperationalError(
            candidate_id=candidate_id,
            code="integration_identity_index_invalid",
            stage="integration",
        )
    if projected_output_cost(data) > MAX_OUTPUT_BUDGET:
        return OperationalError(
            candidate_id=candidate_id,
            code="integration_output_budget_exceeded",
            stage="integration",
        )
    snapshots_by_id: dict[UUID, RawSnapshot] = {}
    conflicting: set[UUID] = set()
    for snapshot in unique_snapshots:
        previous = snapshots_by_id.setdefault(snapshot.id, snapshot)
        if previous != snapshot:
            conflicting.add(snapshot.id)
    candidates: list[IntegratedCandidate | OperationalError] = []
    for item, count in zip(data.candidates, claim_counts, strict=True):
        context = item.context
        if any(s.id in conflicting for s in context.snapshots):
            candidates.append(
                OperationalError(
                    candidate_id=context.candidate.id,
                    code="integration_snapshot_identity_conflict",
                    stage="integration",
                )
            )
            continue
        prepared = prepare_context(context, claim_count=count)
        if isinstance(prepared, OperationalError):
            candidates.append(prepared)
            continue
        normalizations = DomainNormalizationResults(
            temporal=normalize_temporal(TemporalInput(context=context, events=item.temporal)),
            geography=normalize_geography(
                GeographyInput(
                    context=context, locations=item.geography, scope=item.geographic_scope
                )
            ),
            financial=normalize_financial(FinancialInput(context=context, claims=item.financial)),
            organizations=normalize_organizations(context, item.organizations),
            taxonomy=normalize_taxonomy(
                TaxonomyInput(
                    context=context, claims=item.taxonomy, catalog_version=item.catalog_version
                )
            ),
        )
        validation = validate(
            context.candidate, context.snapshots, reference_date=data.reference_date
        )
        diagnostics = evaluate_consistency(item, normalizations, validation)
        if isinstance(diagnostics, OperationalError):
            candidates.append(diagnostics)
            continue
        candidates.append(
            IntegratedCandidate(
                input=item,
                normalizations=normalizations,
                validation=validation,
                diagnostics=diagnostics,
            )
        )
    identity_results: list[IdentityResolutionReport | OperationalError] = []
    for pair in data.identity_comparisons:
        left, right = candidates[pair.left_index], candidates[pair.right_index]
        failed = next((c for c in (left, right) if isinstance(c, OperationalError)), None)
        if failed is not None:
            identity_results.append(
                OperationalError(
                    candidate_id=failed.candidate_id,
                    code="integration_identity_context_failed",
                    stage="integration",
                )
            )
            continue
        subjects = tuple(
            IdentitySubject(
                candidate=item.context.candidate,
                snapshots=item.context.snapshots,
                identifiers=item.identifiers,
                cycle=item.cycle,
            )
            for item in (data.candidates[pair.left_index], data.candidates[pair.right_index])
        )
        identity_results.append(resolve_identity(subjects[0], subjects[1]))
    return tuple(candidates), tuple(identity_results)


def integrate(data: IntegrationInput) -> IntegrationReport | OperationalError:
    outputs = evaluate_integration(data)
    if isinstance(outputs, OperationalError):
        return outputs
    candidates, identity_results = outputs
    return IntegrationReport(input=data, candidates=candidates, identity_results=identity_results)
