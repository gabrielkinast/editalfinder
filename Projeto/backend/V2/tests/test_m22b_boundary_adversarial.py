"""Independent boundary controls for the preexisting M2.2b evidence helper."""

import json
from uuid import UUID

import pytest
from m22b_fixtures import build_m22b_context

from editalfinder_v2.domain.m22b_common import matches_m22b, prepare_m22b
from editalfinder_v2.domain.models import OperationalError, RawSnapshot
from editalfinder_v2.domain.semantic_common import (
    NormalizationContext,
    PreparedContext,
    SemanticValue,
)


@pytest.mark.parametrize(
    "collection,role,key",
    [
        ("financial_claims", "program_budget", "value"),
        ("organization_claims", "funding", "name"),
        ("taxonomy_claims", "area", "value"),
    ],
)
@pytest.mark.parametrize("shape", ["direct", "sibling", "parent", "quote_only"])
def test_exact_unit_and_direct_field_not_just_shared_literal(
    collection: str, role: str, key: str, shape: str
) -> None:
    context, rows = build_m22b_context(collection, [(role, {key: "literal"})])
    value = rows[0][key]
    field = role if key == "value" else f"{role}.{key}"
    pointer = {
        "direct": f"/record/{field}",
        "sibling": f"/sibling/{field}",
        "parent": f"/{field}",
        "quote_only": "/record/description",
    }[shape]
    proof = value.provenance.evidence.model_dump()
    proof["pointer"] = pointer
    assertion = context.candidate.assertions[0].model_dump()
    assertion["evidence"] = (proof,)
    candidate = context.candidate.model_dump()
    candidate["assertions"] = (assertion,)
    raw = context.snapshots[0].model_dump(exclude={"audit"})
    raw["payload_json"] = json.dumps(
        {
            "record": {field: "literal", "description": "literal"},
            "sibling": {field: "literal"},
            field: "literal",
        }
    )
    rebound = value.model_dump()
    rebound["provenance"]["evidence"] = proof
    value = SemanticValue.model_validate(rebound)
    context = NormalizationContext.model_validate({"candidate": candidate, "snapshots": [raw]})
    prepared = prepare_m22b(context, claim_count=1, values=(value,))
    assert isinstance(prepared, PreparedContext)
    assert matches_m22b(
        prepared, value, role, collection=collection, component=None if key == "value" else key
    ) is (shape == "direct")


@pytest.mark.parametrize("case", ["membership", "ambiguous", "snapshot", "source_code"])
def test_context_never_certifies_a_detached_or_ambiguous_proof(case: str) -> None:
    context, rows = build_m22b_context("taxonomy_claims", [("area", {"value": "energia"})])
    data = context.model_dump()
    if case == "membership":
        data["candidate"]["assertions"] = ()
    elif case == "ambiguous":
        data["candidate"]["assertions"][0]["ambiguous"] = True
    elif case == "snapshot":
        data["snapshots"] = ()
    else:
        data["candidate"]["source_code"] = "other-source"
    context = NormalizationContext.model_validate(data)
    value = rows[0]["value"]
    prepared = prepare_m22b(context, claim_count=1, values=(value,))
    assert isinstance(prepared, PreparedContext)
    assert not matches_m22b(prepared, value, "area", collection="taxonomy_claims")


@pytest.mark.parametrize("limit", ["components", "duplicate_snapshot", "invalid_json"])
def test_common_operational_errors_remain_structured(limit: str) -> None:
    context, rows = build_m22b_context("taxonomy_claims", [("area", {"value": "energia"})])
    values = (rows[0]["value"],)
    expected = "normalization_limits_exceeded"
    if limit == "components":
        values *= 1201
    elif limit == "duplicate_snapshot":
        context = NormalizationContext(candidate=context.candidate, snapshots=context.snapshots * 2)
        expected = "normalization_duplicate_snapshot_id"
    else:
        raw = context.snapshots[0].model_dump(exclude={"audit"})
        raw["id"] = UUID(int=1)
        raw["payload_json"] = '{"record":'
        context = NormalizationContext(
            candidate=context.candidate, snapshots=(RawSnapshot.model_validate(raw),)
        )
        expected = "normalization_invalid_snapshot_json"
    result = prepare_m22b(context, claim_count=1, values=values)
    assert isinstance(result, OperationalError)
    assert (result.code, result.stage, result.promotable) == (expected, "normalization", False)
