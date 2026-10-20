"""Financial contracts: lexical interpretation is not evidence authentication.

Format/currency/unit are untrusted adapter declarations. The source value proof
binds only literal text and role, NOT those declarations or the range policy.
Only the complete report verifies structural evidence. No DTO authorizes writes.
"""

from decimal import Decimal, InvalidOperation
from typing import Literal, Self

from pydantic import StrictInt, ValidationInfo, field_validator, model_validator

from .financial_parsing import check_numeric_limits, parse_financial
from .m22b_common import M22BReport
from .models import Contract, OperationalError
from .semantic_common import NormalizationContext, NormalizationDiagnostic, SemanticValue

FinancialRole = Literal[
    "program_budget",
    "proposal_maximum",
    "proposal_minimum",
    "individual_scholarship",
    "monthly_scholarship",
    "counterpart_contribution",
    "applicant_contribution",
    "funding_percentage",
    "eligible_expenses",
    "award_amount",
    "estimated_project_cost",
]


class FinancialClaim(Contract):
    role: FinancialRole
    value: SemanticValue | None = None
    format: str = "unspecified"
    currency: str | None = None
    unit: str = "amount"


class FinancialInput(Contract):
    context: NormalizationContext
    claims: tuple[FinancialClaim, ...] = ()
    normalization_version: Literal["financial-conservative-v1"] = "financial-conservative-v1"


class NormalizedFinancialValue(Contract):
    """Exact lexical result. Standalone instances do not attest source evidence."""

    claim: FinancialClaim
    amounts: tuple[Decimal, ...] = ()
    currency: Literal["BRL", "USD", "EUR"] | None = None
    exponents: tuple[StrictInt, ...] = ()
    text: str | None = None
    codes: tuple[str, ...] = ()
    normalization_version: Literal["financial-conservative-v1"] = "financial-conservative-v1"

    @field_validator("amounts", mode="before")
    @classmethod
    def exact_decimals(cls, value: object, info: ValidationInfo) -> object:
        if not isinstance(value, (tuple, list)) or len(value) > 2:
            raise ValueError("At most two exact Decimal endpoints required")
        result: list[Decimal] = []
        for item in value:
            if info.mode == "json" and isinstance(item, str):
                # Decimal's wire mantissa/exponent can have more lexical digits
                # than the source (e.g. 255-digit integer e9 -> exponent +263).
                # Keep construction bounded; coefficient bounds and exact source
                # reinterpretation below still enforce the original budget.
                check_numeric_limits(item, max_exponent=1256, max_digits=260)
                try:
                    item = Decimal(item)
                except InvalidOperation as exc:
                    raise ValueError("Invalid exact Decimal string") from exc
            if not isinstance(item, Decimal) or not item.is_finite():
                raise ValueError("Python amounts require finite Decimal, never coercion")
            tup = item.as_tuple()
            if (
                len(tup.digits) > 256
                or not isinstance(tup.exponent, int)
                or abs(tup.exponent) > 1256
            ):
                raise ValueError("Decimal exceeds financial bounds")
            result.append(item)
        return tuple(result)

    @model_validator(mode="after")
    def exact_interpretation(self) -> Self:
        if self.claim.value is None:
            raise ValueError("Lexical interpretation requires original text")
        expected = parse_financial(
            self.claim.value.original,
            self.claim.format,
            self.claim.role,
            self.claim.currency,
            self.claim.unit,
        )
        if (
            tuple(v.as_tuple() for v in self.amounts)
            != tuple(v.as_tuple() for v in expected.amounts)
            or self.currency != expected.currency
            or self.exponents != expected.exponents
            or self.text != expected.text
            or self.codes != expected.codes
        ):
            raise ValueError("Financial interpretation must exactly match the source declaration")
        return self


class FinancialClaimResult(Contract):
    """Locally consistent pairing; only a complete report checks evidence."""

    claim: FinancialClaim
    normalized: NormalizedFinancialValue | None = None
    diagnostics: tuple[NormalizationDiagnostic, ...] = ()

    @model_validator(mode="after")
    def same_claim(self) -> Self:
        if self.normalized is not None and self.normalized.claim != self.claim:
            raise ValueError("Financial result must preserve its interpretation's claim")
        return self


class FinancialReport(M22BReport):
    input: FinancialInput
    claims: tuple[FinancialClaimResult, ...]
    diagnostics: tuple[NormalizationDiagnostic, ...] = ()
    normalization_version: Literal["financial-conservative-v1"] = "financial-conservative-v1"

    @model_validator(mode="after")
    def verify_interpretation(self) -> Self:
        from .financial_normalization import evaluate_financial

        expected = evaluate_financial(self.input)
        if isinstance(expected, OperationalError):
            raise ValueError("Operationally invalid input cannot produce a financial report")
        claims, diagnostics = expected
        if self.claims != claims or self.diagnostics != diagnostics:
            raise ValueError("Financial report does not match evidence and interpretation")
        return self
