"""Small, deterministic regressions for output admission; no GiB allocations."""

import json
from datetime import date
from uuid import UUID

import pytest
from m23_fixtures import adapt_records, records_for
from pydantic import ValidationError
from semantic_fixtures import build_context

from editalfinder_v2.domain import integration_budget as budget
from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import (
    CandidateIntegrationInput,
    IdentityComparison,
    IntegratedCandidate,
    IntegrationInput,
    IntegrationReport,
)
from editalfinder_v2.domain.models import FieldAssertion, OperationalError


def test_shared_payload_is_refused_before_any_domain_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import editalfinder_v2.domain.integration as core

    # About 66 KiB shared input; the legacy report repeats it 256 times.
    record = {**records_for("grant")[0], "unasserted": {"padding": "x" * 1024}}
    data = adapt_records([record] * 32)
    before = data.model_dump_json()
    calls = []
    original = core.normalize_temporal

    def counted(*args: object, **kwargs: object) -> object:
        calls.append(True)
        return original(*args, **kwargs)

    monkeypatch.setattr(core, "normalize_temporal", counted)
    result = integrate(data)
    assert isinstance(result, OperationalError)
    assert result.code == "integration_output_budget_exceeded"
    assert result.stage == "integration"
    assert result.promotable is False
    assert calls == []
    assert data.model_dump_json() == before
    assert "REJECTED" not in result.model_dump_json()
    assert json.loads(result.model_dump_json())["candidate_id"] == str(
        data.candidates[0].context.candidate.id
    )


@pytest.mark.parametrize("route", ["constructor", "python", "json"])
def test_oversized_report_is_refused_before_nested_validation(route: str) -> None:
    data = adapt_records([records_for("grant")[0]] * 32)
    payload = {
        "input": data.model_dump(mode="json") if route == "json" else data,
        "candidates": [{"invalid_nested": "must not be parsed"}],
        "identity_results": [],
    }
    with pytest.raises(ValidationError, match="integration_output_budget_exceeded") as caught:
        if route == "constructor":
            IntegrationReport(**payload)
        elif route == "python":
            IntegrationReport.model_validate(payload)
        else:
            IntegrationReport.model_validate_json(json.dumps(payload))
    assert len(caught.value.errors()) == 1
    assert caught.value.errors()[0]["loc"] == ()


def test_accepted_report_records_output_policy_in_audit() -> None:
    data = adapt_records([records_for("grant")[0]])
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    assert report.audit is not None
    assert report.audit.output_budget_version == "m2.3a.1-output-budget-v1"
    assert IntegrationReport.model_validate_json(report.model_dump_json()) == report


def set_budget(monkeypatch: pytest.MonkeyPatch, limit: int) -> None:
    import editalfinder_v2.domain.integration as core
    import editalfinder_v2.domain.integration_models as models

    for module in (budget, core, models):
        monkeypatch.setattr(module, "MAX_OUTPUT_BUDGET", limit)


@pytest.mark.parametrize("delta,accepted", [(-1, False), (0, True), (1, True)])
def test_output_budget_boundary_is_inclusive(
    monkeypatch: pytest.MonkeyPatch, delta: int, accepted: bool
) -> None:
    data = adapt_records([records_for("grant")[0]])
    cost = budget.projected_output_cost(data)
    set_budget(monkeypatch, cost + delta)
    result = integrate(data)
    assert isinstance(result, IntegrationReport if accepted else OperationalError)
    if isinstance(result, OperationalError):
        assert result.code == "integration_output_budget_exceeded"


@pytest.mark.parametrize("case", ["grant", "credit", "investment", "mixed", "ambiguous"])
def test_admitted_reports_retain_evidence_and_charge_exceeds_actual_wire(case: str) -> None:
    from m23_fixtures import build_case

    data = build_case(case)
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    assert report.input == data
    assert len(report.model_dump_json().encode()) < budget.projected_output_cost(data)
    for item, outcome in zip(data.candidates, report.candidates, strict=True):
        assert isinstance(outcome, IntegratedCandidate)
        assert outcome.input == item
        assert outcome.input.context.snapshots == item.context.snapshots
    assert IntegrationReport.model_validate(report.model_dump()) == report
    assert IntegrationReport.model_validate_json(report.model_dump_json()) == report


def test_snapshot_charge_counts_candidate_occurrences_not_object_identity() -> None:
    context, *_ = build_context()
    items = tuple(
        CandidateIntegrationInput(
            context=context.model_copy(
                update={"candidate": context.candidate.model_copy(update={"id": UUID(int=500 + i)})}
            )
        )
        for i in range(32)
    )
    data = IntegrationInput(candidates=items, reference_date=date(2026, 1, 1))
    report = integrate(data)
    assert isinstance(report, IntegrationReport)
    assert report.model_dump_json().count('"payload_json"') == 256
    assert budget.projected_output_cost(data) > 8 * 32 * budget.wire_cost(context.snapshots[0])
    # Equal but distinct snapshot objects must have exactly the same admission charge.
    cloned = tuple(
        item.model_copy(
            update={
                "context": item.context.model_copy(
                    update={
                        "snapshots": tuple(
                            type(s).model_validate(s.model_dump()) for s in context.snapshots
                        )
                    }
                )
            }
        )
        for item in items
    )
    assert budget.projected_output_cost(data.model_copy(update={"candidates": cloned})) == (
        budget.projected_output_cost(data)
    )


def test_explicit_identity_pairs_increase_cost_and_can_trigger_refusal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    data = adapt_records([records_for("grant")[0]])
    compared = data.model_copy(
        update={"identity_comparisons": (IdentityComparison(left_index=0, right_index=0),)}
    )
    cost = budget.projected_output_cost(data)
    assert budget.projected_output_cost(compared) > cost
    set_budget(monkeypatch, cost)
    assert isinstance(integrate(data), IntegrationReport)
    result = integrate(compared)
    assert isinstance(result, OperationalError)
    assert result.code == "integration_output_budget_exceeded"


def test_claim_diagnostic_fanout_is_charged_without_large_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context, *_ = build_context()
    # Model-valid malformed claims remain evidence for M1; no semantic repair.
    repeated = context.candidate.model_copy(
        update={"assertions": (FieldAssertion(field="title", value="x" * 128),) * 64}
    )
    data = IntegrationInput(
        candidates=(
            CandidateIntegrationInput(context=context.model_copy(update={"candidate": repeated})),
        ),
        reference_date=date(2026, 1, 1),
    )
    cost = budget.projected_output_cost(data)
    assert cost > budget.wire_cost(data)
    set_budget(monkeypatch, cost - 1)
    result = integrate(data)
    assert isinstance(result, OperationalError)
    assert result.code == "integration_output_budget_exceeded"


@pytest.mark.parametrize("text", ['"\\\n\t' * 16, "é😀" * 16, "\x00" * 16])
def test_string_charge_covers_json_escaping_without_serialization(text: str) -> None:
    assert budget.wire_cost(text) >= len(json.dumps(text, ensure_ascii=False).encode())


def test_estimator_never_calls_serializers_or_encodes_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from editalfinder_v2.domain.models import Contract

    data = adapt_records([records_for("grant")[0]])

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("preflight must not serialize")

    monkeypatch.setattr(Contract, "model_dump", forbidden)
    monkeypatch.setattr(Contract, "model_dump_json", forbidden)
    monkeypatch.setattr(json, "dumps", forbidden)
    assert budget.projected_output_cost(data) <= budget.MAX_OUTPUT_BUDGET

    class NoEncode(str):
        def encode(self, *args: object, **kwargs: object) -> bytes:
            raise AssertionError("must not allocate UTF-8")

    assert budget.wire_cost(NoEncode("é" * 1024)) < budget.MAX_OUTPUT_BUDGET


@pytest.mark.parametrize("kind", ["cycle", "depth", "nodes", "unknown"])
def test_estimator_itself_is_bounded(monkeypatch: pytest.MonkeyPatch, kind: str) -> None:
    if kind == "cycle":
        value = []
        value.append(value)
    elif kind == "depth":
        value = "x"
        for _ in range(budget.MAX_BUDGET_DEPTH + 1):
            value = [value]
    elif kind == "nodes":
        monkeypatch.setattr(budget, "MAX_BUDGET_NODES", 10)
        value = [str(i) for i in range(20)]
    else:
        value = object()
    assert budget.wire_cost(value) > budget.MAX_OUTPUT_BUDGET


def test_raw_output_is_bounded_even_with_small_declared_input() -> None:
    data = adapt_records([])
    # Shared references allocate only KiB here, but must be charged at each occurrence.
    payload = {"input": data, "candidates": ["x" * 1024] * 11000, "identity_results": []}
    with pytest.raises(ValidationError, match="integration_output_budget_exceeded") as caught:
        IntegrationReport.model_validate(payload)
    assert len(caught.value.errors()) == 1


def test_budget_audit_policy_cannot_be_changed() -> None:
    report = integrate(adapt_records([records_for("grant")[0]]))
    assert isinstance(report, IntegrationReport)
    payload = json.loads(report.model_dump_json())
    payload["audit"]["output_budget_version"] = "ignore-budget"
    with pytest.raises(ValidationError):
        IntegrationReport.model_validate_json(json.dumps(payload))


def test_budget_errors_do_not_format_rejected_payloads() -> None:
    payload = {
        "input": adapt_records([records_for("grant")[0]] * 32),
        "candidates": [],
        "identity_results": [],
    }
    with pytest.raises(ValidationError) as caught:
        IntegrationReport.model_validate(payload)
    message = str(caught.value)
    assert "integration_output_budget_exceeded" in message
    assert "input_value" not in message
    assert len(message) < 1024


def test_shared_snapshot_alone_can_exhaust_budget_without_claim_amplification() -> None:
    small = adapt_records([{}] * 32)
    assert isinstance(integrate(small), IntegrationReport)
    large = adapt_records([{"unasserted": {"padding": "x" * 2048}}] * 32)
    assert all(not item.context.candidate.assertions for item in large.candidates)
    assert len(large.candidates[0].context.snapshots[0].payload_json.encode()) < 100_000
    result = integrate(large)
    assert isinstance(result, OperationalError)
    assert result.code == "integration_output_budget_exceeded"


@pytest.mark.parametrize("kind", ["uuid", "datetime", "decimal"])
def test_python_scalar_charge_covers_its_json_text(kind: str) -> None:
    from datetime import UTC, datetime
    from decimal import Decimal

    value = {
        "uuid": UUID(int=23),
        "datetime": datetime(2026, 1, 1, tzinfo=UTC),
        "decimal": Decimal("1234567890123456789012345678901234567890"),
    }[kind]
    text = value.isoformat() if kind == "datetime" else str(value)
    assert budget.wire_cost(value) >= budget.wire_cost(text)


@pytest.mark.parametrize("case", ["grant", "mixed", "ambiguous"])
def test_projected_cost_is_not_larger_after_json_transport(case: str) -> None:
    from m23_fixtures import build_case

    data = build_case(case)
    assert budget.projected_output_cost(data) >= budget.projected_output_cost(
        json.loads(data.model_dump_json())
    )


def test_tagged_scalar_charges_do_not_reuse_temporary_object_ids() -> None:
    assertions = [FieldAssertion(field="title", value="x" * size) for size in (1, 64, 1024)]
    expected = 64 + sum(budget.wire_cost(item) + 16 for item in assertions)
    assert budget.wire_cost(assertions) == expected
    assert budget.wire_cost(list(reversed(assertions))) == expected
