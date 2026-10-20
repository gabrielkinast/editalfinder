"""Conservative literal/role diagnostics. Not a semantic adjudicator or normalizer."""

from typing import Any

STATUSES = (
    "MATCH",
    "PARTIAL",
    "ROLE_ERROR",
    "VALUE_ERROR",
    "ATTRIBUTION_ERROR",
    "MISSING",
    "ABSTAINED",
    "UNRESOLVED",
)
ALIASES = {
    "funding_organization": "funding_organization_expression",
    "publishing_organization": "publishing_organization_expression",
}
SUPPORTED = {
    "title",
    "opening_date",
    "submission_deadline",
    "publication_date_expression",
    "credit_limit",
    "program_budget",
    "fund_capital_estimate",
    "applicant_requirements",
    "application_instructions",
    "geographic_eligibility",
    "fund_stage_expression",
    "publishing_organization",
    "funding_organization",
}
TEMPORAL = {
    "opening_date",
    "submission_deadline",
    "publication_date_expression",
    "selection_result_date_expression",
    "rectification_date_expression",
}
FINANCIAL = {
    "credit_limit",
    "credit_minimum",
    "program_budget",
    "proposal_maximum",
    "fund_capital_estimate",
    "borrower_revenue_requirement",
}
GENERIC_MONEY = {
    "monetary_expression_unresolved",
    "financing_amount_expression",
    "proposal_amount_expression",
}


def belongs(claim: dict[str, Any], start: int, end: int) -> bool:
    w = claim["witness"]
    value = claim["original"]
    quote = w["quote"]
    cursor = 0
    while True:
        pos = quote.find(value, cursor)
        if pos < 0:
            return False
        if start <= w["start"] + pos < w["start"] + pos + len(value) <= end:
            return True
        cursor = pos + 1


def compare_field(
    name: str,
    value: str,
    candidates: list[dict[str, Any]],
    start: int,
    end: int,
    *,
    foreign_records: tuple[tuple[int, int], ...] = (),
) -> dict[str, Any]:
    """Statuses are provisional diagnostic candidates, not certified correctness.

    Discovery abstention never implies explicit field abstention. Unsupported
    target roles are unresolved, not counted as definite extraction defects.
    No currency/date/qualifier/amount normalization occurs.
    """
    strict = any(f["name"] == name and f["original"] == value for f in candidates)
    matching = [f for f in candidates if f["name"] in {name, ALIASES.get(name, name)}]
    samevalue = [f for f in candidates if f["original"] == value]
    relevant = [f for f in candidates if f in matching or f in samevalue]
    invalid = [f for f in relevant if f["original"] not in f["witness"]["quote"]]
    owned = [f for f in matching if belongs(f, start, end)]
    related = [f for f in owned if value in f["original"] or f["original"] in value]
    role_errors = [
        f
        for f in samevalue
        if belongs(f, start, end)
        and (
            (name in TEMPORAL and f["name"] in TEMPORAL and name != f["name"])
            or (name in FINANCIAL and f["name"] in FINANCIAL and name != f["name"])
        )
    ]
    if invalid:
        status, reason = "VALUE_ERROR", "value absent from its own witness"
    elif any(f["name"] == name and f["original"] == value for f in owned):
        status, reason = "MATCH", "same literal and role in record; entailment remains unreviewed"
    elif related:
        status, reason = (
            "PARTIAL",
            "same/aliased role with related literal; qualifiers may be missing or extra",
        )
    elif role_errors:
        status, reason = "ROLE_ERROR", "same literal claimed under a mutually distinct role"
    elif matching and not owned:
        foreign = any(belongs(f, a, b) for f in matching for a, b in foreign_records)
        status, reason = (
            ("ATTRIBUTION_ERROR", "value belongs to another explicitly annotated record")
            if foreign
            else (
                "UNRESOLVED",
                "outside provisional scope is not proof of foreign-record ownership",
            )
        )
    elif name in FINANCIAL and any(
        f["name"] in GENERIC_MONEY and f["original"] in value and belongs(f, start, end)
        for f in candidates
    ):
        status, reason = (
            "PARTIAL",
            "literal amount retained without requested financial role/qualifiers",
        )
    elif owned:
        status, reason = (
            "UNRESOLVED",
            (
                "same role has different literals; do not assume reference "
                "exhaustive or prediction wrong"
            ),
        )
    elif name not in SUPPORTED:
        status, reason = "UNRESOLVED", "requested target role outside implemented M31 field scope"
    else:
        status, reason = (
            "MISSING",
            "no corresponding field; absence is not explicit field abstention",
        )
    return dict(
        name=name,
        reference_value=value,
        status=status,
        reason=reason,
        strict_role_value=strict,
        scope_supported=name in SUPPORTED,
        semantic_adjudication="not_certified",
        candidates=relevant,
    )
