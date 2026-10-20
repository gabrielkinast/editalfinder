import pytest
from m22b_fixtures import build_m22b_context

from editalfinder_v2.domain.policies import AREAS, OPPORTUNITY_TYPES, RESOURCE_TYPES


def run_rows(rows, **kwargs):
    from editalfinder_v2.domain.taxonomy_models import TaxonomyClaim, TaxonomyInput
    from editalfinder_v2.domain.taxonomy_normalization import normalize_taxonomy

    context, values = build_m22b_context("taxonomy_claims", [(r, {"value": v}) for r, v in rows])
    return normalize_taxonomy(
        TaxonomyInput(
            context=context,
            claims=tuple(
                TaxonomyClaim(role=r, value=v["value"])
                for (r, _), v in zip(rows, values, strict=True)
            ),
            **kwargs,
        )
    )


@pytest.mark.parametrize(
    "role,codes",
    [
        ("opportunity_type", OPPORTUNITY_TYPES),
        ("resource_type", RESOURCE_TYPES),
        ("area", AREAS),
    ],
)
def test_exact_codes_independent(role, codes):
    report = run_rows([(role, code) for code in sorted(codes)])
    assert [n.canonical_code for n in report.classifications] == sorted(codes)
    assert all(
        n.dimension == role and n.mapping_rule == "exact-code-v1" for n in report.classifications
    )
    assert report.promotable is False
    assert "decision" not in report.model_dump()
    assert report.audit is not None


@pytest.mark.parametrize(
    "text",
    [
        "Bolsa",
        "edital ",
        "notícia sobre edital",
        "resultado de bolsa",
        "Ciências da saúde",
        "unknown",
        "123",
        "true",
    ],
)
def test_unapproved_text_preserved(text):
    result = run_rows([("opportunity_type", text)]).classifications[0]
    assert result.claim.value.original == text
    assert result.canonical_code is None
    assert result.status == "unknown"
    assert [d.code for d in result.diagnostics] == ["taxonomy_mapping_not_approved"]


def test_ambiguous_exact_code_never_selects_dimension():
    result = run_rows([("unspecified", "bolsa")]).classifications[0]
    assert result.canonical_code is None and result.dimension is None
    assert result.mapping_rule is None
    assert result.status == "ambiguous"
    assert result.candidate_dimensions == ("opportunity_type", "resource_type")
    assert [d.code for d in result.diagnostics] == ["taxonomy_mapping_ambiguous"]


def test_unspecified_unique_code_still_requires_declared_dimension():
    result = run_rows([("unspecified", "edital")]).classifications[0]
    assert result.canonical_code is None
    assert [d.code for d in result.diagnostics] == ["taxonomy_dimension_missing"]


def test_unsupported_catalog_never_maps():
    report = run_rows([("area", "engenharias")], catalog_version="unapproved-v9")
    assert report.classifications[0].canonical_code is None
    assert [d.code for d in report.classifications[0].diagnostics] == [
        "catalog_version_unsupported"
    ]


def test_absent_classifications_diagnostic():
    report = run_rows([])
    assert [d.code for d in report.diagnostics] == ["taxonomy_classifications_missing"]
    assert type(report).model_validate_json(report.model_dump_json()) == report
