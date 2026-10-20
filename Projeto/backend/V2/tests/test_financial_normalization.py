from decimal import Decimal

import pytest
from m22b_fixtures import build_m22b_context
from pydantic import ValidationError


def request(text="BRL 12.300", role="award_amount", format="decimal", **kwargs):
    from editalfinder_v2.domain.financial_models import FinancialClaim, FinancialInput

    context, rows = build_m22b_context("financial_claims", [(role, {"value": text})])
    return FinancialInput(
        context=context,
        claims=(FinancialClaim(role=role, value=rows[0]["value"], format=format, **kwargs),),
    )


def test_report_roundtrip_and_exact_value():
    from editalfinder_v2.domain.financial_models import FinancialReport
    from editalfinder_v2.domain.financial_normalization import normalize_financial

    report = normalize_financial(request())
    assert isinstance(report, FinancialReport)
    assert report.claims[0].normalized.amounts == (Decimal("12.300"),)
    assert not report.promotable
    assert report.audit is not None
    assert FinancialReport.model_validate_json(report.model_dump_json()) == report


def test_evidence_isolation():
    from editalfinder_v2.domain.financial_normalization import normalize_financial

    value = request()
    value = value.model_copy(
        update={"claims": (value.claims[0].model_copy(update={"role": "program_budget"}),)}
    )
    report = normalize_financial(value)
    assert report.claims[0].normalized is None
    assert report.diagnostics[0].code == "normalization_evidence_invalid"


@pytest.mark.parametrize("amount", [1, True, 1.0, "1", Decimal("NaN"), Decimal("Infinity")])
def test_public_dto_rejects_coercion_and_nonfinite(amount):
    from editalfinder_v2.domain.financial_models import NormalizedFinancialValue

    with pytest.raises(ValidationError):
        NormalizedFinancialValue(claim=request().claims[0], amounts=(amount,))


def test_forged_values_and_report_diagnostics():
    from editalfinder_v2.domain.financial_models import FinancialReport, NormalizedFinancialValue
    from editalfinder_v2.domain.financial_normalization import normalize_financial

    report = normalize_financial(request())
    normalized = report.claims[0].normalized
    for update in (
        {"amounts": (Decimal("99"),)},
        {"currency": None},
        {"exponents": (-2,)},
        {"codes": ("invented",)},
        {"amounts": (Decimal("12.30"),)},
    ):
        with pytest.raises(ValidationError):
            NormalizedFinancialValue.model_validate(normalized.model_dump() | update)
    data = report.model_dump()
    data["audit"] = None
    data["claims"] = ()
    with pytest.raises(ValidationError):
        FinancialReport.model_validate(data)


@pytest.mark.parametrize("text", ["BRL " + "1" * 257, "BRL 1e1001", "BRL " + "x" * 8193])
def test_limits_return_structured_error(text):
    from editalfinder_v2.domain.financial_normalization import normalize_financial
    from editalfinder_v2.domain.models import OperationalError

    result = normalize_financial(request(text))
    assert isinstance(result, OperationalError)
    assert result.code == "normalization_limits_exceeded"
