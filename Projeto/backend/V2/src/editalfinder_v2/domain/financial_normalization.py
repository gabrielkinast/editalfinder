"""Pure role-bound financial normalization, without promotion or SQL projection."""

from .financial_models import (
    FinancialClaimResult,
    FinancialInput,
    FinancialReport,
    NormalizedFinancialValue,
)
from .financial_parsing import FinancialLimitError, check_numeric_limits, parse_financial
from .m22b_common import matches_m22b, prepare_m22b
from .models import OperationalError
from .semantic_common import NormalizationDiagnostic


def evaluate_financial(
    value: FinancialInput,
) -> (
    tuple[tuple[FinancialClaimResult, ...], tuple[NormalizationDiagnostic, ...]] | OperationalError
):
    prepared = prepare_m22b(
        value.context,
        claim_count=len(value.claims),
        values=tuple(c.value for c in value.claims if c.value is not None),
        extra_text=tuple(
            s for c in value.claims for s in (c.format, c.currency, c.unit) if s is not None
        ),
    )
    if isinstance(prepared, OperationalError):
        return prepared
    # Preflight all claims, including those whose evidence will fail. Never partially emit.
    try:
        for claim in value.claims:
            if claim.value is not None and claim.role != "eligible_expenses":
                check_numeric_limits(claim.value.original)
    except FinancialLimitError:
        return OperationalError(
            candidate_id=value.context.candidate.id,
            code="normalization_limits_exceeded",
            stage="normalization",
        )
    results: list[FinancialClaimResult] = []
    diagnostics: list[NormalizationDiagnostic] = []
    for index, claim in enumerate(value.claims):
        normalized = None
        codes: tuple[str, ...]
        if claim.value is None:
            codes = ("financial_value_missing",)
        elif not matches_m22b(prepared, claim.value, claim.role, collection="financial_claims"):
            codes = ("normalization_evidence_invalid",)
        else:
            parsed = parse_financial(
                claim.value.original, claim.format, claim.role, claim.currency, claim.unit
            )
            normalized = NormalizedFinancialValue(
                claim=claim,
                amounts=parsed.amounts,
                currency=parsed.currency,
                exponents=parsed.exponents,
                text=parsed.text,
                codes=parsed.codes,
            )
            codes = parsed.codes
        issues = tuple(
            NormalizationDiagnostic(
                code=code,
                message="Financial interpretation is conservative and not persistable.",
                claim_index=index,
                evidence=(claim.value.provenance,) if claim.value is not None else (),
            )
            for code in codes
        )
        results.append(FinancialClaimResult(claim=claim, normalized=normalized, diagnostics=issues))
        diagnostics.extend(issues)
    if not value.claims:
        diagnostics.append(
            NormalizationDiagnostic(
                code="financial_claims_missing", message="No financial claims supplied."
            )
        )
    return tuple(results), tuple(diagnostics)


def normalize_financial(value: FinancialInput) -> FinancialReport | OperationalError:
    result = evaluate_financial(value)
    if isinstance(result, OperationalError):
        return result
    claims, diagnostics = result
    return FinancialReport(input=value, claims=claims, diagnostics=diagnostics)
