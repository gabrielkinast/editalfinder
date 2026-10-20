"""Adversarial boundaries for the implemented, deliberately incomplete rules."""

import hashlib
import json
from datetime import date
from decimal import localcontext
from typing import Any

import pytest
from m23_fixtures import adapt_records, build_case, records_for
from pydantic import ValidationError
from test_m23b_consistency import organization_case, run_record

from editalfinder_v2.domain import integration_budget as budget
from editalfinder_v2.domain.financial_models import FinancialClaim, FinancialReport
from editalfinder_v2.domain.geography_models import GeographyReport
from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import (
    DomainClaimReference,
    IdentityComparison,
    IntegratedCandidate,
    IntegrationReport,
)
from editalfinder_v2.domain.models import OperationalError, ValidationReport
from editalfinder_v2.domain.organization_models import OrganizationNormalizationReport
from editalfinder_v2.domain.taxonomy_models import TaxonomyReport
from editalfinder_v2.domain.temporal_models import TemporalReport
from editalfinder_v2.domain.validation import validate


def assert_no_conflict(candidate: IntegratedCandidate) -> None:
    assert not any(
        d.classification in {"contradiction", "potential_conflict"} for d in candidate.diagnostics
    )


@pytest.mark.parametrize(
    "roles",
    [
        ("program_budget", "proposal_maximum"),
        ("award_amount", "estimated_project_cost"),
        ("applicant_contribution", "counterpart_contribution"),
        ("individual_scholarship", "award_amount"),
    ],
)
def test_unrelated_financial_roles_are_never_compared(roles: tuple[str, str]) -> None:
    _, candidate = run_record(
        financial_claims=[
            {"role": roles[0], "value": "BRL 10000000", "format": "decimal"},
            {"role": roles[1], "value": "BRL 1", "format": "decimal"},
        ]
    )
    assert_no_conflict(candidate)
    assert tuple(c.role for c in candidate.input.financial) == roles


@pytest.mark.parametrize(
    "value,currency", [("100", None), ("$ 100", None), ("JPY 100", "JPY"), ("BRL 100", "USD")]
)
def test_unresolved_currency_cannot_be_compared(value: str, currency: str | None) -> None:
    _, candidate = run_record(
        financial_claims=[
            {"role": "proposal_minimum", "value": value, "currency": currency, "format": "decimal"},
            {"role": "proposal_maximum", "value": "BRL 1", "format": "decimal"},
        ]
    )
    assert_no_conflict(candidate)
    assert isinstance(candidate.normalizations.financial, FinancialReport)
    normalized = candidate.normalizations.financial.claims[0].normalized
    assert normalized is not None and normalized.amounts == ()


@pytest.mark.parametrize("currency", ["BRL", "USD", "EUR"])
def test_decimal_context_cannot_change_financial_consistency(currency: str) -> None:
    rows = [
        {"role": "proposal_minimum", "value": f"{currency} 100.00000001", "format": "decimal"},
        {"role": "proposal_maximum", "value": f"{currency} 100.00000000", "format": "decimal"},
    ]
    normal, _ = run_record(financial_claims=rows)
    with localcontext() as context:
        context.prec = 2
        low_precision, _ = run_record(financial_claims=rows)
    assert low_precision.model_dump_json() == normal.model_dump_json()


@pytest.mark.parametrize(
    "role", ["credit_principal", "equity_investment", "valuation", "interest_rate"]
)
def test_unapproved_financial_roles_are_not_introduced(role: str) -> None:
    with pytest.raises(ValidationError):
        FinancialClaim.model_validate({"role": role})


def test_monthly_scholarship_and_total_award_are_distinct() -> None:
    _, candidate = run_record(
        financial_claims=[
            {
                "role": "monthly_scholarship",
                "value": "BRL 2000",
                "format": "decimal",
                "unit": "per_month",
            },
            {"role": "award_amount", "value": "BRL 1000", "format": "decimal"},
        ]
    )
    assert_no_conflict(candidate)
    assert candidate.input.financial[0].unit == "per_month"


@pytest.mark.parametrize(
    "expression", ["investimento", "venture_capital", "equity", "co_investment"]
)
def test_unsupported_investment_is_not_coerced_into_fallbacks(expression: str) -> None:
    report, candidate = run_record(
        investment_instrument="Explicit source description",
        investment_ticket="BRL 100 to 200",
        financial_claims=[
            {"role": "estimated_project_cost", "value": "BRL 300", "format": "decimal"}
        ],
        taxonomy_claims=[{"role": "resource_type", "value": expression}],
    )
    assert isinstance(candidate.normalizations.taxonomy, TaxonomyReport)
    classification = candidate.normalizations.taxonomy.classifications[0]
    assert classification.canonical_code is None
    assert classification.claim.value.original == expression
    assert any(d.code == "consistency_taxonomy_unsupported" for d in candidate.diagnostics)
    assert_no_conflict(candidate)
    assert report.input.candidates[0] == candidate.input
    assert candidate.input.financial[0].role == "estimated_project_cost"


@pytest.mark.parametrize(
    "code,role",
    [
        ("bolsa", "unspecified"),
        ("bolsa", "resource_type"),
        ("misto", "resource_type"),
        ("multidisciplinar", "area"),
        ("outra", "opportunity_type"),
    ],
)
def test_only_explicit_codes_and_dimensions_can_map(code: str, role: str) -> None:
    _, candidate = run_record(taxonomy_claims=[{"role": role, "value": code}])
    assert isinstance(candidate.normalizations.taxonomy, TaxonomyReport)
    row = candidate.normalizations.taxonomy.classifications[0]
    assert row.status == ("ambiguous" if role == "unspecified" else "mapped")
    assert row.canonical_code == (None if role == "unspecified" else code)
    assert_no_conflict(candidate)


@pytest.mark.parametrize("kind", ["news", "result"])
def test_keywords_and_canonical_categories_never_override_m1(kind: str) -> None:
    _, candidate = run_record(
        content_kind=kind,
        actionable=True,
        title="Edital bolsas venture capital credit — explicit news/result",
        taxonomy_claims=[{"role": "resource_type", "value": "bolsa"}],
    )
    assert isinstance(candidate.validation, ValidationReport)
    assert candidate.validation == validate(
        candidate.input.context.candidate,
        candidate.input.context.snapshots,
        reference_date=candidate.validation.reference_date,
    )
    assert candidate.validation.promotable is False
    assert_no_conflict(candidate)


@pytest.mark.parametrize(
    "events",
    [
        [("submission_opening_date", "2026-01-01"), ("submission_deadline", "2026-02-01")],
        [
            ("preliminary_application_deadline", "2026-01-01"),
            ("full_application_deadline", "2026-03-01"),
        ],
        [("submission_deadline", "2026-01-01"), ("selection_result_date", "2026-03-01")],
        [("publication_date", "2026-01-01")],
        [],
    ],
)
def test_legitimate_temporal_roles_and_missing_deadline_do_not_create_conflicts(events) -> None:
    _, candidate = run_record(
        temporal_events=[{"role": r, "value": v, "format": "iso"} for r, v in events]
    )
    assert_no_conflict(candidate)
    assert isinstance(candidate.normalizations.temporal, TemporalReport)
    for event in candidate.normalizations.temporal.events:
        assert event.local_datetime is event.instant_utc is event.timezone is None


@pytest.mark.parametrize("suffix", ["", "-00:00"])
def test_unknown_timezones_are_not_compared_as_utc_instants(suffix: str) -> None:
    _, candidate = run_record(
        temporal_events=[
            {"role": "submission_deadline", "value": "2026-01-01T10:00" + suffix, "format": "iso"},
            {"role": "submission_deadline", "value": "2026-01-01T11:00" + suffix, "format": "iso"},
        ]
    )
    assert_no_conflict(candidate)
    assert all(d.classification == "insufficient_information" for d in candidate.diagnostics)
    assert isinstance(candidate.normalizations.temporal, TemporalReport)
    assert all(e.instant_utc is None for e in candidate.normalizations.temporal.events)


def test_m2_dates_do_not_invent_expiration_or_use_current_time() -> None:
    data = build_case("grant")
    reports = [
        integrate(data.model_copy(update={"reference_date": date(y, 1, 1)})) for y in (1, 9999)
    ]
    assert all(isinstance(r, IntegrationReport) for r in reports)
    left, right = (r.candidates[0] for r in reports)
    assert left.diagnostics == right.diagnostics
    assert left.normalizations == right.normalizations
    assert left.validation.temporal_status == right.validation.temporal_status == "nao_determinada"


@pytest.mark.parametrize(
    "scope,locations",
    [
        ("brasil", [{"role": "elegibilidade", "country_code": "BR"}]),
        (
            "internacional",
            [
                {"role": "elegibilidade", "country_code": "US"},
                {"role": "elegibilidade", "country_code": "DE"},
            ],
        ),
        (
            "misto",
            [
                {"role": "elegibilidade", "country_code": "BR"},
                {"role": "elegibilidade", "country_code": "US"},
            ],
        ),
        (
            "brasil",
            [
                {"role": "origem", "country_code": "US"},
                {"role": "elegibilidade", "country_code": "BR"},
            ],
        ),
        (
            "brasil",
            [
                {"role": "execucao", "country_code": "US"},
                {"role": "elegibilidade", "country_code": "BR"},
            ],
        ),
        ("nao_identificado", [{"role": "organizacao_responsavel", "country_code": "BR"}]),
    ],
)
def test_location_roles_do_not_become_eligibility(
    scope: str, locations: list[dict[str, str]]
) -> None:
    _, candidate = run_record(geographic_scope=scope, geographic_locations=locations)
    assert_no_conflict(candidate)
    assert tuple(c.role for c in candidate.input.geography) == tuple(
        row["role"] for row in locations
    )
    assert isinstance(candidate.normalizations.geography, GeographyReport)
    assert candidate.normalizations.geography.scope == scope


def test_municipality_remains_uncertified() -> None:
    _, candidate = run_record(
        geographic_locations=[
            {"role": "elegibilidade", "country_code": "BR", "municipality": "Porto Alegre"}
        ]
    )
    assert isinstance(candidate.normalizations.geography, GeographyReport)
    assert candidate.normalizations.geography.locations[0].municipality_verified is False
    assert_no_conflict(candidate)


@pytest.mark.parametrize(
    "roles",
    [
        ["publishing", "funding"],
        ["funding", "funding"],
        ["publishing", "funding", "partner"],
    ],
)
def test_multiple_entities_or_multiple_roles_are_not_conflicts(roles: list[str]) -> None:
    _, candidate = run_record(
        organization_claims=[{"role": r, "name": "Same or similar name"} for r in roles]
    )
    assert_no_conflict(candidate)
    assert len(candidate.input.organizations) == len(roles)


def test_exact_organization_keys_are_not_legal_identity_or_merge_permission() -> None:
    report, candidate = organization_case(("ORG-A", "ORG-A"))
    assert isinstance(candidate.normalizations.organizations, OrganizationNormalizationReport)
    assert (
        "contextual_identifier_shared_not_merge"
        in candidate.normalizations.organizations.diagnostics
    )
    assert len(candidate.input.organizations) == 2
    assert_no_conflict(candidate)
    assert report.promotable is False


@pytest.mark.parametrize("route", ["constructor", "python", "json"])
@pytest.mark.parametrize("retained_audit", [False, True])
@pytest.mark.parametrize(
    "mutation",
    [
        "missing_all",
        "missing_one",
        "order",
        "message",
        "code",
        "classification",
        "domain",
        "qualified_domain",
        "claim_index",
        "evidence",
        "versions",
        "legacy_indices",
    ],
)
def test_diagnostic_forgery_is_rejected_even_without_audit(route, retained_audit, mutation) -> None:
    report, _ = run_record(
        temporal_events=[
            {"role": "submission_deadline", "value": "2026-01-01", "format": "iso"},
            {"role": "submission_deadline", "value": "2026-02-01", "format": "iso"},
        ],
        financial_claims=[
            {"role": "proposal_maximum", "value": "BRL 10 to 1", "format": "decimal"}
        ],
        taxonomy_claims=[{"role": "resource_type", "value": "equity"}],
    )
    payload = json.loads(report.model_dump_json()) if route == "json" else report.model_dump()
    if not retained_audit:
        payload.pop("audit")
    diagnostics = [dict(d) for d in payload["candidates"][0]["diagnostics"]]
    if mutation == "missing_all":
        diagnostics = []
    elif mutation == "missing_one":
        diagnostics.pop()
    elif mutation == "order":
        diagnostics.reverse()
    elif mutation == "message":
        diagnostics[0]["message"] += " forged"
    elif mutation == "code":
        diagnostics[0]["code"] = "forged"
    elif mutation == "classification":
        diagnostics[0]["classification"] = "no_conflict_detected"
    elif mutation == "domain":
        diagnostics[0]["domains"] = ["financial"]
    elif mutation == "qualified_domain":
        refs = [dict(r) for r in diagnostics[0]["claim_references"]]
        refs[0]["domain"] = "financial"
        diagnostics[0]["claim_references"] = refs
    elif mutation == "claim_index":
        refs = [dict(r) for r in diagnostics[0]["claim_references"]]
        refs[0]["claim_index"] += 1
        diagnostics[0]["claim_references"] = refs
    elif mutation == "evidence":
        diagnostics[0]["evidence"] = []
    elif mutation == "versions":
        diagnostics[0]["normalization_versions"] = []
    else:
        diagnostics[0]["claim_indices"] = [0]
    candidates = [dict(c) for c in payload["candidates"]]
    candidates[0]["diagnostics"] = diagnostics
    payload["candidates"] = candidates
    with pytest.raises(ValidationError):
        if route == "constructor":
            IntegrationReport(**payload)
        elif route == "python":
            IntegrationReport.model_validate(payload)
        else:
            IntegrationReport.model_validate_json(json.dumps(payload))


@pytest.mark.parametrize("value", [True, "0", -1, 0.0])
def test_domain_qualified_indices_cannot_be_coerced(value: Any) -> None:
    with pytest.raises(ValidationError):
        DomainClaimReference.model_validate({"domain": "financial", "claim_index": value})


def test_identity_match_is_not_evidence_merge_authority() -> None:
    record = records_for("grant")[0]
    left = {
        **record,
        "financial_claims": [{"role": "proposal_minimum", "value": "BRL 100", "format": "decimal"}],
    }
    right = {
        **record,
        "financial_claims": [{"role": "proposal_maximum", "value": "BRL 1", "format": "decimal"}],
    }
    data = adapt_records([left, right])
    data = data.model_copy(
        update={"identity_comparisons": (IdentityComparison(left_index=0, right_index=1),)}
    )
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    assert report.identity_results[0].decision == "exact_match"
    assert len(report.candidates) == 2
    for candidate in report.candidates:
        assert isinstance(candidate, IntegratedCandidate)
        assert_no_conflict(candidate)
        assert len(candidate.input.financial) == 1
        assert all(
            p.candidate_id == candidate.input.context.candidate.id
            for d in candidate.diagnostics
            for p in d.evidence
        )


def test_many_bounded_diagnostics_are_fully_preserved_and_charged() -> None:
    rows = [
        {"role": r, "value": f"unsupported-{i}"}
        for r in ("area", "resource_type", "opportunity_type")
        for i in range(8)
    ]
    data = adapt_records([{**records_for("grant")[0], "taxonomy_claims": rows}])
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    candidate = report.candidates[0]
    assert isinstance(candidate, IntegratedCandidate)
    assert len(candidate.diagnostics) == len(rows)
    assert [d.claim_references[0].claim_index for d in candidate.diagnostics] == list(
        range(len(rows))
    )
    assert budget.wire_cost(report) < budget.projected_output_cost(data) <= 64 * 1024 * 1024
    assert IntegrationReport.model_validate_json(report.model_dump_json()) == report


def test_report_digest_covers_all_diagnostics_and_nested_metadata() -> None:
    report, candidate = run_record(taxonomy_claims=[{"role": "unspecified", "value": "bolsa"}])
    assert report.audit is not None
    assert (
        report.audit.report_digest
        == hashlib.sha256(report.model_dump_json(exclude={"audit"}).encode()).hexdigest()
    )
    assert candidate.diagnostics[0].claim_indices == ()
    with pytest.raises(ValidationError):
        candidate.diagnostics[0].message = "forged"
    with pytest.raises(ValidationError):
        candidate.diagnostics[0].claim_references[0].claim_index = 8
    text = report.model_dump_json()
    assert integrate(report.input).model_dump_json() == text
    assert IntegrationReport.model_validate_json(text) == report


def test_snapshot_collision_is_operational_even_with_consistency_claims() -> None:
    data = adapt_records([records_for("grant")[0], records_for("grant")[0]])
    left, right = data.candidates
    snapshot = right.context.snapshots[0]
    changed = type(snapshot).model_validate(
        {**snapshot.model_dump(exclude={"audit"}), "payload_json": snapshot.payload_json + " "}
    )
    right = right.model_copy(
        update={"context": right.context.model_copy(update={"snapshots": (changed,)})}
    )
    report = integrate(data.model_copy(update={"candidates": (left, right)}))
    assert isinstance(report, IntegrationReport)
    assert all(
        isinstance(c, OperationalError) and c.code == "integration_snapshot_identity_conflict"
        for c in report.candidates
    )


@pytest.mark.parametrize(
    "field",
    [
        "classification",
        "domains",
        "claim_references",
        "normalization_versions",
        "version",
        "evidence",
    ],
)
@pytest.mark.parametrize("route", ["constructor", "python", "json"])
def test_received_consistency_metadata_is_explicit_not_defaulted(field: str, route: str) -> None:
    from editalfinder_v2.domain.integration_models import IntegrationDiagnostic

    _, candidate = run_record(taxonomy_claims=[{"role": "resource_type", "value": "equity"}])
    diagnostic = candidate.diagnostics[0]
    payload = (
        json.loads(diagnostic.model_dump_json()) if route == "json" else diagnostic.model_dump()
    )
    del payload[field]
    with pytest.raises(ValidationError) as caught:
        if route == "constructor":
            IntegrationDiagnostic(**payload)
        elif route == "python":
            IntegrationDiagnostic.model_validate(payload)
        else:
            IntegrationDiagnostic.model_validate_json(json.dumps(payload))
    assert any(
        e["type"] == "missing" and e["loc"] == (field,)
        for e in caught.value.errors(include_input=False)
    )


def test_standalone_consistency_admits_before_building_inputs_and_returns_operational_error(
    monkeypatch,
) -> None:
    import editalfinder_v2.domain.integration_consistency as engine
    from editalfinder_v2.domain.integration_models import DomainNormalizationResults
    from editalfinder_v2.domain.temporal_models import TemporalClaim

    item = build_case("grant").candidates[0]
    item = item.model_copy(update={"temporal": (TemporalClaim(role="submission_deadline"),) * 1201})
    error = OperationalError(
        candidate_id=item.context.candidate.id, code="not_evaluated", stage="normalization"
    )
    reports = DomainNormalizationResults(
        temporal=error, geography=error, financial=error, organizations=error, taxonomy=error
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("must admit resources before building secondary inputs")

    monkeypatch.setattr(engine, "TemporalInput", forbidden)
    result = engine.evaluate_consistency(item, reports, error)
    assert isinstance(result, OperationalError)
    assert result.code == "normalization_limits_exceeded"
    assert result.promotable is False
    assert "REJECTED" not in result.model_dump_json()


@pytest.mark.parametrize(
    "domain",
    ["temporal", "geography", "geographic_scope", "organizations", "financial", "taxonomy"],
)
def test_every_exported_proof_stays_inside_its_source_record(domain: str) -> None:
    record = records_for("grant")[0]
    data = adapt_records([record, record])
    left, right = data.candidates
    left = left.model_copy(update={domain: getattr(right, domain)})
    report = integrate(data.model_copy(update={"candidates": (left, right)}))
    assert isinstance(report, IntegrationReport)
    assert len(report.candidates) == 2
    for original, result in zip((left, right), report.candidates, strict=True):
        assert isinstance(result, IntegratedCandidate)
        assert result.input == original
        for diagnostic in result.diagnostics:
            for proof in diagnostic.evidence:
                assert proof.candidate_id == original.context.candidate.id
                assert proof.source_id == original.context.candidate.source_id
                assert proof.evidence.unit == original.context.candidate.unit
    assert IntegrationReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize(
    "model,extra",
    [("temporal", "stage_id"), ("temporal", "window_id"), ("financial", "instrument_id")],
)
def test_unavailable_relationship_scopes_are_not_silently_invented(model: str, extra: str) -> None:
    from editalfinder_v2.domain.temporal_models import TemporalClaim

    target = TemporalClaim if model == "temporal" else FinancialClaim
    role = "submission_deadline" if model == "temporal" else "proposal_maximum"
    with pytest.raises(ValidationError) as caught:
        target.model_validate({"role": role, extra: "claimed-but-not-approved"})
    assert any(
        e["type"] == "extra_forbidden" and e["loc"] == (extra,)
        for e in caught.value.errors(include_input=False)
    )


def test_supported_cnpj_checksum_does_not_claim_registry_existence() -> None:
    from m22b_fixtures import build_m22b_context

    from editalfinder_v2.domain.identity_models import IdentifierNamespace
    from editalfinder_v2.domain.integration_models import (
        CandidateIntegrationInput,
        IntegrationInput,
    )
    from editalfinder_v2.domain.organization_models import OrganizationClaim, OrganizationIdentifier

    context, rows = build_m22b_context(
        "organization_claims",
        [("funding", {"name": "Declared entity", "cnpj": "11.222.333/0001-81"})],
    )
    claim = OrganizationClaim(
        role="funding",
        name=rows[0]["name"],
        identifiers=(
            OrganizationIdentifier(
                kind="cnpj", namespace=IdentifierNamespace(value="cnpj"), value=rows[0]["cnpj"]
            ),
        ),
    )
    report = integrate(
        IntegrationInput(
            candidates=(CandidateIntegrationInput(context=context, organizations=(claim,)),),
            reference_date=date(2026, 1, 1),
        )
    )
    assert isinstance(report, IntegrationReport)
    candidate = report.candidates[0]
    assert isinstance(candidate, IntegratedCandidate)
    assert isinstance(candidate.normalizations.organizations, OrganizationNormalizationReport)
    identifier = candidate.normalizations.organizations.organizations[0].identifiers[0]
    assert identifier.checksum_status == "valid"
    assert identifier.existence_status == "unverified"
    assert_no_conflict(candidate)
