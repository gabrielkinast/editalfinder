"""Contract-led E2E verification through integrate, not chained normalizer calls."""

import hashlib
from collections import Counter
from typing import Any

import pytest
from m23c_fixtures import build, dataset

from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import IntegratedCandidate, IntegrationReport
from editalfinder_v2.domain.models import ValidationReport


def projection(candidate: IntegratedCandidate) -> dict[str, Any]:
    n = candidate.normalizations
    return {
        "financial": [
            [c.claim.role, [str(a) for a in c.normalized.amounts], c.normalized.currency]
            for c in n.financial.claims
        ],
        "temporal": [
            [
                e.claim.role,
                e.civil_date.isoformat() if e.civil_date else None,
                e.timezone,
                e.instant_utc.isoformat() if e.instant_utc else None,
            ]
            for e in n.temporal.events
        ],
        "geography": [
            [loc.role, loc.country_code, loc.state_code, loc.municipality]
            for loc in n.geography.locations
        ],
        "taxonomy": [
            [t.claim.role, t.canonical_code, t.status] for t in n.taxonomy.classifications
        ],
        "organizations": [
            [o.claim.role, o.claim.name.original] for o in n.organizations.organizations
        ],
    }


def check_candidate(candidate: IntegratedCandidate, expected: dict[str, Any]) -> None:
    assert projection(candidate) == expected["expected_normalized_roles"]
    assert [d.code for d in candidate.diagnostics] == expected["expected_diagnostic_codes"]
    v = candidate.validation
    assert isinstance(v, ValidationReport)
    constraints = expected["expected_validation_constraints"]
    assert v.decision.value == constraints["decision"]
    assert v.promotable is constraints["promotable"]
    assert v.temporal_status == constraints["temporal_status"]
    assert set(constraints["required_issue_codes"]) <= {i.code for i in v.issues}
    assert v.review_attestations == ()
    assert v.candidate == candidate.input.context.candidate
    assert v.snapshots == candidate.input.context.snapshots
    for d in candidate.diagnostics:
        assert d.version == "m2.3b-consistency-v1"
        for proof in d.evidence:
            assert proof.candidate_id == v.candidate.id
            assert proof.evidence.unit == v.candidate.unit
            assert proof.evidence.pointer.startswith(v.candidate.unit.pointer + "/")
        for ref in d.claim_references:
            collection = (
                v.candidate.assertions
                if ref.domain == "validation"
                else (candidate.input.geographic_scope,)
                if ref.domain == "geographic_scope"
                else getattr(candidate.input, ref.domain)
            )
            assert 0 <= ref.claim_index < len(collection)
    for domain in ("temporal", "geography", "financial", "organizations", "taxonomy"):
        report = getattr(candidate.normalizations, domain)
        assert report.audit is not None
        assert (report.context if domain == "organizations" else report.input.context) == (
            candidate.input.context
        )
        assert report.promotable is False


@pytest.mark.parametrize("case", dataset()["cases"], ids=lambda c: c["case_id"])
def test_frozen_manual_manifest_through_real_orchestrator(case: dict[str, Any]) -> None:
    data = build(case)
    result = integrate(data)
    assert isinstance(result, IntegrationReport)
    assert result.input == data
    assert len(result.candidates) == len(case["expected_candidates"])
    assert result.promotable is False
    for index, (candidate, expected) in enumerate(
        zip(result.candidates, case["expected_candidates"], strict=True)
    ):
        assert isinstance(candidate, IntegratedCandidate)
        assert candidate.input == data.candidates[index]
        check_candidate(candidate, expected)
    assert len(result.identity_results) == len(case["expected_identity_behavior"])
    for index, (identity, expected) in enumerate(
        zip(result.identity_results, case["expected_identity_behavior"], strict=True)
    ):
        pair = data.identity_comparisons[index]
        assert identity.left.candidate == data.candidates[pair.left_index].context.candidate
        assert identity.right.candidate == data.candidates[pair.right_index].context.candidate
        assert identity.decision == expected["decision"]
        assert [d.code for d in identity.diagnostics] == expected["codes"]
        assert identity.promotable is False
    wire = result.model_dump_json()
    assert IntegrationReport.model_validate_json(wire) == result
    assert IntegrationReport.model_validate(result.model_dump()) == result
    assert integrate(data).model_dump_json() == wire
    assert (
        result.audit.report_digest
        == hashlib.sha256(result.model_dump_json(exclude={"audit"}).encode("utf-8")).hexdigest()
    )


def test_manifest_is_versioned_complete_and_has_all_required_categories() -> None:
    manifest = dataset()
    assert manifest["dataset_version"] == "m2.3c-synthetic-structured-v1"
    cases = manifest["cases"]
    assert len({c["case_id"] for c in cases}) == len(cases) == 26
    assert set(Counter(c["scenario_category"] for c in cases)) == set("ABCDEFGHI")
    assert sum(c["scenario_category"] == "F" for c in cases) == 6
    for case in cases:
        assert len(case["records"]) == len(case["expected_candidates"])
        for expected in case["expected_candidates"]:
            assert expected["expected_evidence_scope"] == "candidate_record_only"
            assert expected["expected_audit_behavior"] == "full_replay_and_retained_digest"
            assert expected["expected_operational_status"] == "integrated"
            assert set(expected) <= set(manifest["contract_support"])
