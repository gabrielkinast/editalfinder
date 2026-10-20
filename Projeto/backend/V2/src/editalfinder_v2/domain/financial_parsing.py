"""Exact bounded parsing. Only ` to `, ` até ` and ` .. ` delimit ranges.

No scaling words, conversion, locale inference, hyphen ranges or persistence mapping.
Currency prefixes BRL/USD/EUR and unambiguous R$/US$/€ are supported. A single
prefix governs the whole range; repeated endpoint currencies are not supported.
Missing/unknown/conflicting currency leaves monetary quantities unresolved (empty
amounts, diagnostic, original retained by the claim), rather than interpreting a
currency-free number as money. Percentages are unscaled points, not fractions.
Source budgets count all ASCII digits, including exponent digits, across both
endpoints: 256 digits, explicit exponent magnitude 1000, 8192 text characters.
These are operational budgets, not database precision or permissible award limits.
"""

import re
from dataclasses import dataclass
from decimal import Decimal

MAX_FINANCIAL_DIGITS = 256
MAX_FINANCIAL_EXPONENT = 1000


class FinancialLimitError(ValueError):
    """Refusal before Decimal construction, not a semantic classification."""


@dataclass(frozen=True)
class FinancialParse:
    amounts: tuple[Decimal, ...] = ()
    currency: str | None = None
    exponents: tuple[int, ...] = ()
    text: str | None = None
    codes: tuple[str, ...] = ()


def check_numeric_limits(
    original: str,
    *,
    max_exponent: int = MAX_FINANCIAL_EXPONENT,
    max_digits: int = MAX_FINANCIAL_DIGITS,
) -> None:
    if len(original) > 8192:
        raise FinancialLimitError("financial text limit")
    if sum(c in "0123456789" for c in original) > max_digits:
        raise FinancialLimitError("financial digit limit")
    for match in re.finditer(r"[eE]([+-]?)([0-9]+)", original):
        digits = match[2].lstrip("0") or "0"
        if len(digits) > 4 or int(digits) > max_exponent:
            raise FinancialLimitError("financial exponent limit")


def parse_financial(
    original: str, format: str, role: str, currency: str | None, unit: str
) -> FinancialParse:
    def failure(code: str) -> FinancialParse:
        return FinancialParse(codes=(code,))

    if len(original) > 8192:
        raise FinancialLimitError("financial text limit")
    if role == "eligible_expenses":
        if unit != "text" or currency is not None:
            return failure("financial_unit_role_conflict")
        return FinancialParse(text=original, codes=("financial_expenses_text_only",))
    check_numeric_limits(original)
    if format not in {"unspecified", "brazilian", "us", "decimal", "scientific"}:
        return failure("financial_format_unknown")
    percent = role == "funding_percentage"
    if (
        (percent and (unit != "percent" or currency is not None))
        or (not percent and (unit not in {"amount", "per_month", "per_year"} or "%" in original))
        or (role == "monthly_scholarship" and unit != "per_month")
    ):
        return failure("financial_unit_role_conflict")
    text = original.strip()
    prefixes = {"BRL": "BRL", "USD": "USD", "EUR": "EUR", "R$": "BRL", "US$": "USD", "€": "EUR"}
    explicit: str | None = None
    for prefix, code in prefixes.items():
        if text.startswith(prefix):
            explicit = code
            text = text[len(prefix) :].strip()
            break
    if percent:
        if explicit is not None:
            return failure("financial_unit_role_conflict")
        text = text.removesuffix("%").strip()
    else:
        if currency is not None and currency not in {"BRL", "USD", "EUR"}:
            return failure("financial_currency_unknown")
        if explicit and currency and explicit != currency:
            return failure("financial_currency_conflict")
        currency = explicit or currency
        if currency is None:
            unknown = re.match(r"[A-Za-z$€£¥]", text)
            return failure(
                "financial_currency_unknown" if unknown else "financial_currency_missing"
            )
    pieces = re.split(r" (?:to|até|\.\.) ", text)
    if not 1 <= len(pieces) <= 2:
        return failure("financial_number_invalid")
    patterns = {
        "brazilian": r"[+-]?(?:[0-9]+|[0-9]{1,3}(?:\.[0-9]{3})+)(?:,[0-9]+)?",
        "us": r"[+-]?(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?",
        "decimal": r"[+-]?[0-9]+(?:\.[0-9]+)?",
        "scientific": r"[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?",
        "unspecified": r"[+-]?[0-9]+",
    }
    if format == "unspecified" and any(c in piece for piece in pieces for c in ".,eE"):
        return failure("financial_ambiguous_format")
    amounts: list[Decimal] = []
    exponents: list[int] = []
    for piece in pieces:
        if not re.fullmatch(patterns[format], piece):
            return failure("financial_number_invalid")
        if format == "brazilian":
            piece = piece.replace(".", "").replace(",", ".")
        elif format == "us":
            piece = piece.replace(",", "")
        amount = Decimal(piece)  # string construction is exact and context-independent
        exponent = amount.as_tuple().exponent
        assert isinstance(exponent, int)
        amounts.append(amount)
        exponents.append(exponent)
    codes: list[str] = []
    if any(v < 0 for v in amounts):
        codes.append("financial_negative_amount")
    if percent and any(v < 0 or v > 100 for v in amounts):
        codes.append("financial_percentage_out_of_range")
    if len(amounts) == 2 and amounts[0] > amounts[1]:
        codes.append("financial_range_reversed")
    return FinancialParse(tuple(amounts), currency, tuple(exponents), codes=tuple(codes))
