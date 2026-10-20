import json
from decimal import Decimal, localcontext
from typing import get_args

import pytest
from pydantic import ValidationError
from test_financial_normalization import request

from editalfinder_v2.domain.financial_models import (
    FinancialInput,
    FinancialReport,
    FinancialRole,
    NormalizedFinancialValue,
)
from editalfinder_v2.domain.financial_normalization import normalize_financial
from editalfinder_v2.domain.models import OperationalError


@pytest.mark.parametrize("role", get_args(FinancialRole))
def test_all_roles_remain_distinct(role):
    unit = {
        "monthly_scholarship": "per_month",
        "funding_percentage": "percent",
        "eligible_expenses": "text",
    }.get(role, "amount")
    text = {"funding_percentage": "12%", "eligible_expenses": "travel BRL 10"}.get(role, "BRL 10")
    report = normalize_financial(request(text, role, unit=unit))
    assert isinstance(report, FinancialReport)
    assert report.claims[0].claim.role == role
    assert report.claims[0].normalized is not None
    assert FinancialReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("text", ["BRL 1.00e-1000", "BRL 1e1000", "BRL -0.000"])
def test_extreme_roundtrip_context_independent(text):
    with localcontext() as ctx:
        ctx.prec = 1
        ctx.Emax = 1
        ctx.Emin = -1
        report = normalize_financial(request(text, format="scientific"))
        assert FinancialReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("item", ["garbage", "NaN", "sNaN", "Infinity", "1e99999999", 1, 1.5, True])
def test_json_public_amount_validation(item):
    report = normalize_financial(request())
    data = json.loads(report.claims[0].normalized.model_dump_json())
    data["amounts"] = [item]
    with pytest.raises(ValidationError):
        NormalizedFinancialValue.model_validate_json(json.dumps(data))


def test_missing_and_oversized_metadata_and_claim_count():
    value = request()
    report = normalize_financial(FinancialInput(context=value.context))
    assert report.diagnostics[0].code == "financial_claims_missing"
    for update in ({"format": "x" * 8193}, {"unit": "x" * 8193}, {"currency": "x" * 8193}):
        result = normalize_financial(
            value.model_copy(update={"claims": (value.claims[0].model_copy(update=update),)})
        )
        assert isinstance(result, OperationalError)
    result = normalize_financial(value.model_copy(update={"claims": value.claims * 1201}))
    assert isinstance(result, OperationalError)


def test_audit_and_diagnostics_tampering_rejected():
    report = normalize_financial(request("BRL -1"))
    data = report.model_dump()
    data["diagnostics"] = ()
    with pytest.raises(ValidationError):
        FinancialReport.model_validate(data)
    data["audit"] = None
    with pytest.raises(ValidationError):
        FinancialReport.model_validate(data)
    with pytest.raises(ValidationError):
        report.normalization_version = "different"


def test_decimal_zero_sign_cannot_be_forged():
    report = normalize_financial(request("BRL -0.00"))
    parsed = report.claims[0].normalized
    with pytest.raises(ValidationError):
        NormalizedFinancialValue.model_validate(
            parsed.model_dump() | {"amounts": (Decimal("0.00"),)}
        )
