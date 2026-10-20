"""Bounded operational scenarios; never reinterpret the admission charge as RSS."""

import json

import pytest
from m23c_fixtures import FIXTURE, build, case_by_id

from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_budget import (
    MAX_OUTPUT_BUDGET,
    projected_output_cost,
    wire_cost,
)
from editalfinder_v2.domain.integration_models import IdentityComparison, IntegrationReport
from editalfinder_v2.domain.models import OperationalError

OPERATIONAL = FIXTURE.with_name("m23c_operational_v1.json")


def operational_cases():
    return json.loads(OPERATIONAL.read_text(encoding="utf-8"))["cases"]


def padded_batch(padding):
    case = case_by_id("M23C-I-005")
    record = case["records"][0]
    record["unasserted"] = {"padding": "x" * padding}
    case["records"] = [record] * 4
    case["identity_comparisons"] = []
    return build(case)


def resource_input(kind):
    if kind == "small":
        return build(case_by_id("M23C-A-001"))
    if kind == "shared":
        return build(case_by_id("M23C-E-001"))
    if kind in {"near", "over"}:
        # Search ONLY the admission estimator, not semantic outputs. Bounded <= 400 KiB padding.
        # Adjacent padding sizes straddle the actual fixed 64 MiB policy without monkeypatching.
        low, high = 0, 100000
        assert projected_output_cost(padded_batch(low)) < MAX_OUTPUT_BUDGET
        assert projected_output_cost(padded_batch(high)) > MAX_OUTPUT_BUDGET
        while low + 1 < high:
            mid = (low + high) // 2
            if projected_output_cost(padded_batch(mid)) <= MAX_OUTPUT_BUDGET:
                low = mid
            else:
                high = mid
        return padded_batch(low if kind == "near" else high)
    data = build(case_by_id("M23C-I-005"))
    if kind == "duplicate":
        return data.model_copy(update={"candidates": (data.candidates[0],) * 2})
    if kind == "comparisons":
        return data.model_copy(
            update={"identity_comparisons": (IdentityComparison(left_index=0, right_index=1),) * 65}
        )
    assert kind == "collision"
    first, second = data.candidates
    snapshot = second.context.snapshots[0]
    raw = snapshot.model_dump()
    raw["payload_json"] += " "
    raw.pop("audit")
    changed_snapshot = type(snapshot).model_validate(raw)
    second = second.model_copy(
        update={"context": second.context.model_copy(update={"snapshots": (changed_snapshot,)})}
    )
    # Rebind a healthy control to fresh candidate/snapshot UUIDs; no shared owner.
    from uuid import UUID

    from m23_fixtures import adapt_records

    independent_data = adapt_records([case_by_id("M23C-A-001")["records"][0]])
    independent_wire = independent_data.model_dump_json()
    independent_wire = independent_wire.replace(str(snapshot.id), str(UUID(int=999002)))
    independent_wire = independent_wire.replace(
        str(independent_data.candidates[0].context.candidate.id), str(UUID(int=999001))
    )
    mapping = json.loads(independent_wire)
    for s in mapping["candidates"][0]["context"]["snapshots"]:
        s.pop("audit")
    from editalfinder_v2.domain.integration_models import IntegrationInput

    independent = IntegrationInput.model_validate_json(json.dumps(mapping)).candidates[0]
    return data.model_copy(update={"candidates": (first, second, independent)})


@pytest.mark.parametrize("case", operational_cases(), ids=lambda c: c["case_id"])
def test_frozen_operational_manifest(case):
    data = resource_input(case["builder"])
    before = data.model_dump_json()
    result = integrate(data)
    assert type(result).__name__ == case["expected_operational_status"]
    assert data.model_dump_json() == before
    assert result.promotable is False
    if isinstance(result, OperationalError):
        assert result.code == case["expected_error_code"]
        assert result.stage == "integration"
        assert "decision" not in result.model_dump()
    elif case["builder"] == "collision":
        assert [c.code for c in result.candidates[:2]] == [case["expected_error_code"]] * 2
        assert not isinstance(result.candidates[2], OperationalError)
        assert result.identity_results[0].code == "integration_identity_context_failed"
    else:
        assert len(result.candidates) == len(data.candidates)
        assert result.input == data
        charge = projected_output_cost(data)
        assert wire_cost(result) <= charge
        assert len(result.model_dump_json().encode("utf-8")) < charge
        assert IntegrationReport.model_validate_json(result.model_dump_json()) == result
        if case["builder"] == "near":
            assert MAX_OUTPUT_BUDGET * 99 // 100 <= charge <= MAX_OUTPUT_BUDGET
            assert (
                max(
                    len(s.payload_json.encode())
                    for c in data.candidates
                    for s in c.context.snapshots
                )
                < 2 * 1024 * 1024
            )


def test_real_budget_boundary_keeps_every_candidate_or_returns_error():
    near, over = resource_input("near"), resource_input("over")
    assert MAX_OUTPUT_BUDGET == 64 * 1024 * 1024
    assert projected_output_cost(near) <= MAX_OUTPUT_BUDGET < projected_output_cost(over)
    assert len(near.candidates) == len(over.candidates) == 4
    assert isinstance(integrate(near), IntegrationReport)
    refused = integrate(over)
    assert isinstance(refused, OperationalError)
    assert refused.code == "integration_output_budget_exceeded"
