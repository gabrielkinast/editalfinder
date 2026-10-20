"""Real report boundaries, including no-envelope complete replay; no fictional API."""

import copy
import json

import pytest
from m23c_fixtures import build, case_by_id
from pydantic import ValidationError

from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import IntegrationInput, IntegrationReport

# Valid DTO-shaped mutations: the boundary must not trust nested results or labels.
MUTATIONS = [
    ("snapshot", ("input", "candidates", 0, "context", "snapshots", 0, "payload_json"), "{}"),
    (
        "record_scope",
        ("input", "candidates", 0, "context", "candidate", "unit", "pointer"),
        "/records/9",
    ),
    (
        "pointer",
        ("input", "candidates", 0, "financial", 0, "value", "provenance", "evidence", "pointer"),
        "/records/4/title",
    ),
    ("role", ("input", "candidates", 0, "financial", 0, "role"), "award_amount"),
    (
        "amount",
        ("candidates", 0, "normalizations", "financial", "claims", 0, "normalized", "amounts", 0),
        "1",
    ),
    ("currency", ("input", "candidates", 0, "financial", 0, "currency"), "USD"),
    ("eligibility", ("input", "candidates", 0, "geography", 0, "role"), "origem"),
    ("stage", ("input", "candidates", 0, "temporal", 0, "role"), "selection_result_date"),
    ("organization", ("input", "candidates", 0, "organizations", 0, "role"), "applicant"),
    ("taxonomy", ("input", "candidates", 0, "taxonomy", 0, "role"), "area"),
    ("diagnostic", ("candidates", 0, "diagnostics", 0, "code"), "fabricated_approval"),
    ("validation", ("candidates", 0, "validation", "decision"), "ACCEPTED"),
]


def without_audits(value):
    if isinstance(value, dict):
        return {k: without_audits(v) for k, v in value.items() if k != "audit"}
    if isinstance(value, list):
        return [without_audits(v) for v in value]
    return value


@pytest.fixture(scope="module")
def grant_report():
    result = integrate(build(case_by_id("M23C-A-001")))
    assert isinstance(result, IntegrationReport)
    return result


@pytest.mark.parametrize("retain_audit", [True, False])
@pytest.mark.parametrize("mutation", MUTATIONS, ids=lambda m: m[0])
def test_received_report_rejects_tampering_with_or_without_envelopes(
    grant_report, mutation, retain_audit
):
    payload = json.loads(grant_report.model_dump_json())
    _, path, replacement = mutation
    target = payload
    for token in path[:-1]:
        target = target[token]
    assert target[path[-1]] != replacement
    target[path[-1]] = replacement
    if not retain_audit:
        payload = without_audits(payload)
    with pytest.raises(ValidationError):
        IntegrationReport.model_validate_json(json.dumps(payload))


@pytest.mark.parametrize("route", ["constructor", "python", "json"])
@pytest.mark.parametrize(
    "mutation",
    ["diagnostic_evidence", "identity_decision", "identity_order", "audit_version", "digest"],
)
def test_identity_diagnostic_and_audit_forgery_in_all_routes(route, mutation):
    case = case_by_id("M23C-I-005")
    # Credit produces a diagnostic with real claim evidence, unlike no-conflict summary.
    case["records"][0]["taxonomy_claims"] = [{"role": "resource_type", "value": "credito"}]
    report = integrate(build(case))
    assert isinstance(report, IntegrationReport)
    payload = json.loads(report.model_dump_json()) if route == "json" else report.model_dump()
    if mutation == "diagnostic_evidence":
        diagnostics = list(payload["candidates"][0]["diagnostics"])
        evidence = list(diagnostics[0]["evidence"])
        evidence[0]["evidence"]["pointer"] = "/records/1/title"
        diagnostics[0]["evidence"] = evidence
    elif mutation == "identity_decision":
        payload["identity_results"][0]["decision"] = "no_supported_match"
    elif mutation == "identity_order":
        payload["identity_results"] = list(reversed(payload["identity_results"]))
    elif mutation == "audit_version":
        payload["audit"]["output_budget_version"] = "historical-unknown"
    else:
        payload["audit"]["report_digest"] = "0" * 64
    with pytest.raises(ValidationError):
        if route == "constructor":
            IntegrationReport(**payload)
        elif route == "python":
            IntegrationReport.model_validate(payload)
        else:
            IntegrationReport.model_validate_json(json.dumps(payload))


def test_historical_policy_is_not_backfilled_by_current_input_reprocessing(grant_report):
    archived = json.loads(grant_report.model_dump_json())
    archived["audit"].pop("output_budget_version")
    original = copy.deepcopy(archived)
    with pytest.raises(ValidationError):
        IntegrationReport.model_validate_json(json.dumps(archived))
    current = integrate(IntegrationInput.model_validate_json(json.dumps(archived["input"])))
    assert current == grant_report
    assert archived == original
    assert "output_budget_version" not in archived["audit"]
    assert current.audit.output_budget_version == "m2.3a.1-output-budget-v1"


@pytest.mark.parametrize(
    "authority", ["trusted_review", "promotable", "accepted", "merge_authorized"]
)
def test_input_has_no_review_promotion_or_merge_authority(authority):
    data = build(case_by_id("M23C-A-001")).model_dump()
    data[authority] = True
    with pytest.raises(ValidationError):
        IntegrationInput.model_validate(data)


def test_manual_review_method_still_has_no_authenticated_authority():
    data = build(case_by_id("M23C-A-001"))
    item = data.candidates[0]
    c = item.context.candidate
    assertions = tuple(
        a.model_copy(
            update={
                "evidence": tuple(
                    e.model_copy(update={"method": "manual_review"}) for e in a.evidence
                )
            }
        )
        for a in c.assertions
    )
    changed = item.model_copy(
        update={
            "context": item.context.model_copy(
                update={"candidate": c.model_copy(update={"assertions": assertions})}
            )
        }
    )
    result = integrate(data.model_copy(update={"candidates": (changed,)}))
    assert isinstance(result, IntegrationReport)
    v = result.candidates[0].validation
    assert v.decision.value == "REVIEW"
    assert "trusted_review_required" in {i.code for i in v.issues}
    assert v.review_attestations == ()
    assert result.promotable is v.promotable is False
