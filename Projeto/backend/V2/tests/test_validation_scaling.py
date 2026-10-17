"""Deterministic work-count and size-bound regressions; no timing assertions."""

from datetime import date

import pytest
from fixtures import example

from editalfinder_v2.domain.models import (
    FieldAssertion,
    OperationalError,
    OpportunityCandidate,
    ValidationReport,
)
from editalfinder_v2.domain.validation import validate

DAY = date(2026, 6, 1)


def candidate_with(assertions):
    snapshot, candidate = example()
    return snapshot, OpportunityCandidate.model_validate(
        {**candidate.model_dump(), "assertions": assertions}
    )


@pytest.mark.parametrize("n", [100, 300, 1200])
def test_field_access_work_is_linear_for_unique_unsupported_fields(monkeypatch, n):
    snapshot, candidate = candidate_with(
        tuple(FieldAssertion(field=f"unsupported_{i}", value=None) for i in range(n))
    )
    accesses = 0
    original = FieldAssertion.__getattribute__

    def counted(self, name):
        nonlocal accesses
        if name == "field":
            accesses += 1
        return original(self, name)

    monkeypatch.setattr(FieldAssertion, "__getattribute__", counted)
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert isinstance(report, ValidationReport)
    assert sum(i.code == "unsupported_field" for i in report.issues) == n
    assert accesses <= 20 * n, accesses


@pytest.mark.parametrize("size", [1199, 1200, 1201])
def test_assertion_budget_boundary(size):
    snapshot, candidate = candidate_with(
        tuple(FieldAssertion(field=f"unsupported_{i}", value=None) for i in range(size))
    )
    result = validate(candidate, (snapshot,), reference_date=DAY)
    if size > 1200:
        assert isinstance(result, OperationalError)
        assert result.code == "validation_limits_exceeded"
        assert result.stage == "validation"
        assert not result.promotable
    else:
        assert isinstance(result, ValidationReport)
        assert len(result.candidate.assertions) == size
        assert not result.promotable


@pytest.mark.parametrize("count", [63, 64, 65])
def test_per_field_evidence_budget_boundary(count):
    snapshot, candidate = example()
    title = candidate.assertions[0]
    snapshot, candidate = candidate_with(
        (FieldAssertion(field="title", value=title.value, evidence=title.evidence * count),)
    )
    result = validate(candidate, (snapshot,), reference_date=DAY)
    if count > 64:
        assert isinstance(result, OperationalError)
        assert result.code == "validation_limits_exceeded"
    else:
        assert isinstance(result, ValidationReport)
        assert len(result.candidate.assertions[0].evidence) == count


@pytest.mark.parametrize("count", [2399, 2400, 2401])
def test_total_evidence_budget_boundary(count):
    _, candidate = example()
    evidence = candidate.assertions[0].evidence[0]
    snapshot, candidate = candidate_with(
        tuple(
            FieldAssertion(
                field=f"unsupported_{i}", value=None, evidence=(evidence,) * min(4, count - 4 * i)
            )
            for i in range((count + 3) // 4)
        )
    )
    result = validate(candidate, (snapshot,), reference_date=DAY)
    if count > 2400:
        assert isinstance(result, OperationalError)
        assert result.code == "validation_limits_exceeded"
    else:
        assert isinstance(result, ValidationReport)
        assert sum(len(a.evidence) for a in result.candidate.assertions) == count


def test_related_evidence_preserves_assertion_order_duplicates_and_null_context():
    snapshot, candidate = example()
    title = candidate.assertions[0]
    assertions = (
        title,
        FieldAssertion(field="title", value=None, evidence=title.evidence),
        FieldAssertion(field="official_url", value="bad", evidence=title.evidence),
        FieldAssertion(field="title", value="conflict", evidence=title.evidence),
    )
    snapshot, candidate = candidate_with(assertions)
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert isinstance(report, ValidationReport)
    conflicts = [i for i in report.issues if i.code == "conflicting_assertions"]
    assert len(conflicts) == 1
    assert conflicts[0].field == "title"
    assert conflicts[0].evidence == title.evidence * 3


def test_multi_field_diagnostic_preserves_global_evidence_order():
    snapshot, candidate = example(kind="news")
    by_field = {a.field: a for a in candidate.assertions}
    actionable = FieldAssertion(
        field="actionable", value=True, evidence=by_field["actionable"].evidence
    )
    assertions = (
        actionable,
        by_field["title"],
        by_field["content_kind"],
        by_field["specific_instrument"],
        FieldAssertion(field="actionable", value=None, evidence=actionable.evidence),
    )
    candidate = OpportunityCandidate.model_validate(
        {**candidate.model_dump(), "assertions": assertions}
    )
    report = validate(candidate, (snapshot,), reference_date=DAY)
    assert isinstance(report, ValidationReport)
    conflict = next(i for i in report.issues if i.code == "conflicting_intent")
    assert conflict.evidence == (
        actionable.evidence
        + by_field["content_kind"].evidence
        + by_field["specific_instrument"].evidence
        + actionable.evidence
    )


@pytest.mark.parametrize("extra", [0, 1])
def test_field_budget_counts_duplicate_evidence_across_null_assertions(extra):
    _, candidate = example()
    evidence = candidate.assertions[0].evidence
    snapshot, candidate = candidate_with(
        (
            FieldAssertion(field="title", value=None, evidence=evidence * 32),
            FieldAssertion(field="title", value=None, evidence=evidence * (32 + extra)),
        )
    )
    result = validate(candidate, (snapshot,), reference_date=DAY)
    if extra:
        assert isinstance(result, OperationalError)
        assert result.code == "validation_limits_exceeded"
    else:
        assert isinstance(result, ValidationReport)
