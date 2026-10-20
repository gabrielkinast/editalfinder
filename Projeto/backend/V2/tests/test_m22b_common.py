"""M2.2b boundaries cannot weaken older policies or introduce promotion."""

import hashlib
import json
from uuid import UUID

import pytest
from m22b_fixtures import build_m22b_context
from pydantic import ValidationError
from semantic_fixtures import build_context

from editalfinder_v2.domain.m22b_common import M22BReport, matches_m22b, prepare_m22b
from editalfinder_v2.domain.models import OperationalError
from editalfinder_v2.domain.semantic_common import PreparedContext


@pytest.mark.parametrize(
    "collection,role,component",
    [
        ("financial_claims", "program_budget", None),
        ("organization_claims", "funding", "name"),
        ("taxonomy_claims", "area", None),
    ],
)
def test_new_collection_evidence_is_bound_without_weakening_old_policy(
    collection: str, role: str, component: str | None
) -> None:
    key = component or "value"
    context, rows = build_m22b_context(collection, [(role, {key: "literal"})])
    value = rows[0][key]
    prepared = prepare_m22b(context, claim_count=1, values=(value,))
    assert isinstance(prepared, PreparedContext)
    assert matches_m22b(prepared, value, role, collection=collection, component=component)
    assert not matches_m22b(prepared, value, "other", collection=collection, component=component)
    assert not prepared.matches(value, role, component=component)


@pytest.mark.parametrize("length,limit", [(8192, False), (8193, True)])
def test_per_string_budget_includes_metadata(length: int, limit: bool) -> None:
    context, *_ = build_context()
    result = prepare_m22b(context, claim_count=0, values=(), extra_text=("x" * length,))
    if limit:
        assert isinstance(result, OperationalError)
        assert result.code == "normalization_limits_exceeded"
        assert result.stage == "normalization" and result.promotable is False
    else:
        assert isinstance(result, PreparedContext)


@pytest.mark.parametrize("count,limited", [(1200, False), (1201, True)])
def test_claim_budget_before_parsing(count: int, limited: bool) -> None:
    context, *_ = build_context()
    result = prepare_m22b(context, claim_count=count, values=())
    assert isinstance(result, OperationalError if limited else PreparedContext)
    if limited:
        assert result.code == "normalization_limits_exceeded"


@pytest.mark.parametrize("field", ["candidate_id", "source_id", "execution_id"])
def test_contextual_identifiers_must_match(field: str) -> None:
    context, rows = build_m22b_context("taxonomy_claims", [("area", {"value": "energia"})])
    original = rows[0]["value"]
    value = original.model_copy(
        update={"provenance": original.provenance.model_copy(update={field: UUID(int=999)})}
    )
    prepared = prepare_m22b(context, claim_count=1, values=(value,))
    assert isinstance(prepared, PreparedContext)
    assert not matches_m22b(prepared, value, "area", collection="taxonomy_claims")


@pytest.mark.parametrize(
    "pointer",
    [
        "/record/taxonomy_claims/00/value",
        "/record/taxonomy_claims/-1/value",
        "/record/taxonomy_claims/١/value",
        "/record/taxonomy_claims/0/role",
        "/other/taxonomy_claims/0/value",
        "/record/taxonomy_claims/" + "9" * 5000 + "/value",
    ],
)
def test_structural_pointer_not_just_matching_quote(pointer: str) -> None:
    context, rows = build_m22b_context("taxonomy_claims", [("area", {"value": "energia"})])
    original = rows[0]["value"]
    evidence = original.provenance.evidence.model_copy(update={"pointer": pointer})
    value = original.model_copy(
        update={"provenance": original.provenance.model_copy(update={"evidence": evidence})}
    )
    assertion = context.candidate.assertions[0].model_copy(update={"evidence": (evidence,)})
    candidate = context.candidate.model_copy(update={"assertions": (assertion,)})
    context = context.model_copy(update={"candidate": candidate})
    prepared = prepare_m22b(context, claim_count=1, values=(value,))
    assert isinstance(prepared, PreparedContext)
    assert not matches_m22b(prepared, value, "area", collection="taxonomy_claims")


@pytest.mark.parametrize(
    "payload",
    [
        '{"record":{"taxonomy_claims":{"0":{"role":"area","value":"energia"}}}}',
        '{"record":{"taxonomy_claims":[{"role":"resource_type","value":"energia"}]}}',
        '{"record":{"taxonomy_claims":[{"role":"area","value":true}]}}',
    ],
)
def test_payload_structure_and_scalar_type_are_authoritative(payload: str) -> None:
    context, rows = build_m22b_context("taxonomy_claims", [("area", {"value": "energia"})])
    snapshot = context.snapshots[0]
    data = snapshot.model_dump(exclude={"audit"})
    data["payload_json"] = payload
    context = context.model_copy(update={"snapshots": (type(snapshot).model_validate(data),)})
    prepared = prepare_m22b(context, claim_count=1, values=(rows[0]["value"],))
    assert isinstance(prepared, PreparedContext)
    assert not matches_m22b(prepared, rows[0]["value"], "area", collection="taxonomy_claims")


@pytest.mark.parametrize("count,limited", [(128, False), (129, True)])
def test_aggregate_metadata_limit_without_truncation(count: int, limited: bool) -> None:
    context, *_ = build_context()
    result = prepare_m22b(context, claim_count=0, values=(), extra_text=("x" * 8192,) * count)
    if limited:
        assert isinstance(result, OperationalError)
        assert result.code == "normalization_limits_exceeded"
    else:
        assert isinstance(result, PreparedContext)


def test_report_has_distinct_versioned_complete_audit() -> None:
    report = M22BReport()
    assert report.promotable is False
    assert report.policy_version == "m2.2b-semantics-v1"
    assert report.audit is not None
    assert report.audit.limits_version == "m2.2b-normalization-limits-v1"
    assert (
        report.audit.report_digest
        == hashlib.sha256(report.model_dump_json(exclude={"audit"}).encode()).hexdigest()
    )
    assert M22BReport.model_validate_json(report.model_dump_json()) == report
    data = json.loads(report.model_dump_json())
    data["audit"]["report_digest"] = "0" * 64
    with pytest.raises(ValidationError, match="Normalization audit"):
        M22BReport.model_validate_json(json.dumps(data))
