from decimal import Decimal, localcontext

import pytest

from editalfinder_v2.domain.financial_parsing import parse_financial


def test_brazilian_precision_preserved():
    result = parse_financial("BRL 1.234,500", "brazilian", "program_budget", None, "amount")
    assert result.amounts == (Decimal("1234.500"),)
    assert result.currency == "BRL"
    assert result.exponents == (-3,)
    assert result.codes == ()


@pytest.mark.parametrize(
    "text,fmt,amount",
    [
        ("USD 1,234.500", "us", "1234.500"),
        ("EUR -0.00", "decimal", "-0.00"),
        ("BRL -123.45", "decimal", "-123.45"),
        ("USD 1.2300e+10", "scientific", "1.2300e+10"),
        ("BRL 0", "unspecified", "0"),
    ],
)
def test_exact_formats(text, fmt, amount):
    with localcontext() as ctx:
        ctx.prec = 1
        result = parse_financial(text, fmt, "award_amount", None, "amount")
    assert result.amounts[0].as_tuple() == Decimal(amount).as_tuple()


@pytest.mark.parametrize(
    "text,fmt,currency,code",
    [
        ("1.234", "unspecified", "BRL", "financial_ambiguous_format"),
        ("12", "decimal", None, "financial_currency_missing"),
        ("CAD 12", "decimal", None, "financial_currency_unknown"),
        ("$ 12", "decimal", None, "financial_currency_unknown"),
        ("BRL 12", "weird", None, "financial_format_unknown"),
        ("BRL 12", "decimal", "USD", "financial_currency_conflict"),
        ("BRL NaN", "decimal", None, "financial_number_invalid"),
        ("BRL 1-2", "decimal", None, "financial_number_invalid"),
        ("BRL 1,23.4", "us", None, "financial_number_invalid"),
    ],
)
def test_unresolved(text, fmt, currency, code):
    result = parse_financial(text, fmt, "award_amount", currency, "amount")
    assert not result.amounts
    assert result.codes == (code,)


def test_explicit_ranges_and_signed_diagnostics():
    result = parse_financial("EUR -2.00 to 0.000", "decimal", "proposal_minimum", None, "amount")
    assert result.amounts == (Decimal("-2.00"), Decimal("0.000"))
    assert result.exponents == (-2, -3)
    assert result.codes == ("financial_negative_amount",)
    assert parse_financial("BRL 2 to 1", "decimal", "award_amount", None, "amount").codes == (
        "financial_range_reversed",
    )


def test_percentage_and_expenses():
    result = parse_financial("12.50%", "decimal", "funding_percentage", None, "percent")
    assert result.amounts == (Decimal("12.50"),)
    assert result.currency is None
    assert parse_financial("12%", "decimal", "award_amount", None, "amount").codes == (
        "financial_unit_role_conflict",
    )
    result = parse_financial("equipment BRL 100", "unspecified", "eligible_expenses", None, "text")
    assert result.text == "equipment BRL 100"
    assert not result.amounts


@pytest.mark.parametrize("text", ["BRL " + "1" * 257, "BRL 1e1001", "BRL 1e" + "9" * 500])
def test_numeric_limits(text):
    from editalfinder_v2.domain.financial_parsing import FinancialLimitError

    with pytest.raises(FinancialLimitError):
        parse_financial(text, "scientific", "award_amount", None, "amount")
