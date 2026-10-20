"""Adversarial financial boundaries; no source authentication or promotion."""

from decimal import Decimal, localcontext

import pytest
from pydantic import ValidationError
from test_financial_normalization import request

from editalfinder_v2.domain.financial_models import FinancialReport
from editalfinder_v2.domain.financial_normalization import normalize_financial


@pytest.mark.parametrize("digits,exponent", [(255, "9"), (253, "999"), (252, "1000")])
def test_scientific_serialization_does_not_reapply_source_digit_budget(digits, exponent):
    original = "BRL " + "9" * digits + "e" + exponent
    report = normalize_financial(request(original, format="scientific"))
    assert isinstance(report, FinancialReport)
    expected = Decimal("9" * digits + "e" + exponent)
    assert report.claims[0].normalized.amounts[0].as_tuple() == expected.as_tuple()
    restored = FinancialReport.model_validate_json(report.model_dump_json())
    assert restored == report
    assert restored.claims[0].normalized.amounts[0].as_tuple() == expected.as_tuple()


def test_accepted_fractional_scientific_value_roundtrips_at_limit():
    original = "BRL 0." + "0" * 249 + "1e-1000"
    with localcontext() as ctx:
        ctx.prec = 1
        ctx.Emin = -1
        ctx.Emax = 1
        report = normalize_financial(request(original, format="scientific"))
        assert isinstance(report, FinancialReport)
        assert report.claims[0].normalized is not None
        assert report.claims[0].normalized.amounts[0].as_tuple() == Decimal("1e-1250").as_tuple()
        assert FinancialReport.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("delimiter", [" to ", " até ", " .. "])
def test_integer_ranges_do_not_infer_locale(delimiter):
    report = normalize_financial(request("BRL 1" + delimiter + "2", format="unspecified"))
    assert isinstance(report, FinancialReport)
    assert report.claims[0].normalized.amounts == (Decimal("1"), Decimal("2"))
    assert report.diagnostics == ()


def test_standalone_result_cannot_relabel_interpretation():
    from editalfinder_v2.domain.financial_models import FinancialClaimResult

    report = normalize_financial(request())
    assert isinstance(report, FinancialReport)
    normalized = report.claims[0].normalized
    with pytest.raises(ValidationError):
        FinancialClaimResult(claim=request(role="program_budget").claims[0], normalized=normalized)


@pytest.mark.parametrize("exponent", [0.0, False, "0"])
def test_public_exponents_are_exact_integers(exponent):
    from editalfinder_v2.domain.financial_models import NormalizedFinancialValue

    report = normalize_financial(request("BRL 1"))
    assert isinstance(report, FinancialReport)
    normalized = report.claims[0].normalized
    assert normalized is not None
    with pytest.raises(ValidationError):
        NormalizedFinancialValue.model_validate(
            normalized.model_dump() | {"exponents": (exponent,)}
        )


# Characterization coverage for preexisting behavior, not new implementation.
@pytest.mark.parametrize(
    "original,fmt,currency,exact",
    [
        ("R$1.500,50", "brazilian", "BRL", "1500.50"),
        ("BRL1500.50", "decimal", "BRL", "1500.50"),
        ("US$25,000.00", "us", "USD", "25000.00"),
        ("€2.500,00", "brazilian", "EUR", "2500.00"),
    ],
)
def test_requested_formats_preserve_original_and_precision(original, fmt, currency, exact):
    value = request(original, format=fmt)
    report = normalize_financial(value)
    assert isinstance(report, FinancialReport)
    normalized = report.claims[0].normalized
    assert normalized is not None
    assert normalized.claim == value.claims[0]
    assert normalized.currency == currency
    assert normalized.amounts[0].as_tuple() == Decimal(exact).as_tuple()
    assert normalized.exponents == (-2,)
    assert report.model_dump_json() == normalize_financial(value).model_dump_json()
    assert not report.promotable


@pytest.mark.parametrize(
    "original,code",
    [
        ("1500.50", "financial_currency_missing"),
        ("$1500.50", "financial_currency_unknown"),
    ],
)
def test_unresolved_currency_retains_original_and_indexed_evidence(original, code):
    value = request(original)
    report = normalize_financial(value)
    assert isinstance(report, FinancialReport)
    normalized = report.claims[0].normalized
    assert normalized is not None
    assert normalized.claim.value.original == original
    assert normalized.amounts == ()
    assert normalized.currency is None
    assert report.diagnostics == report.claims[0].diagnostics
    (issue,) = report.diagnostics
    assert issue.code == code
    assert issue.claim_index == 0
    assert issue.evidence == (value.claims[0].value.provenance,)


@pytest.mark.parametrize(
    "original,expected,codes",
    [
        ("0.000%", ("0.000",), ()),
        ("100.000%", ("100.000",), ()),
        ("100.0001%", ("100.0001",), ("financial_percentage_out_of_range",)),
        (
            "101 to -0.1%",
            ("101", "-0.1"),
            (
                "financial_negative_amount",
                "financial_percentage_out_of_range",
                "financial_range_reversed",
            ),
        ),
    ],
)
def test_percentage_points_are_not_scaled_or_clamped(original, expected, codes):
    report = normalize_financial(request(original, "funding_percentage", unit="percent"))
    assert isinstance(report, FinancialReport)
    normalized = report.claims[0].normalized
    assert normalized is not None
    assert tuple(a.as_tuple() for a in normalized.amounts) == tuple(
        Decimal(a).as_tuple() for a in expected
    )
    assert normalized.codes == codes
    assert normalized.currency is None


def test_numeric_limit_preflight_precedes_evidence_and_never_truncates():
    from editalfinder_v2.domain.financial_models import FinancialInput
    from editalfinder_v2.domain.models import OperationalError

    valid = request("BRL 1")
    oversized = request("BRL " + "9" * 257)
    value = FinancialInput(context=valid.context, claims=valid.claims + oversized.claims)
    result = normalize_financial(value)
    assert isinstance(result, OperationalError)
    assert result.code == "normalization_limits_exceeded"
    assert result.stage == "normalization"
    assert result.candidate_id == valid.context.candidate.id


def test_digit_budget_is_source_wide_and_boundary_is_accepted():
    from editalfinder_v2.domain.models import OperationalError

    accepted = normalize_financial(request("BRL " + "9" * 128 + " to " + "9" * 128))
    assert isinstance(accepted, FinancialReport)
    assert FinancialReport.model_validate_json(accepted.model_dump_json()) == accepted
    refused = normalize_financial(request("BRL " + "9" * 128 + " to " + "9" * 129))
    assert isinstance(refused, OperationalError)
