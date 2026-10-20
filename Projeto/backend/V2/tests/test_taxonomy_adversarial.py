"""Taxonomy boundary regressions; no source authority or actionability claims."""

import hashlib
import json

import pytest
from pydantic import ValidationError
from test_taxonomy_normalization import run_rows

from editalfinder_v2.domain.models import OperationalError
from editalfinder_v2.domain.policies import AREAS, OPPORTUNITY_TYPES, RESOURCE_TYPES
from editalfinder_v2.domain.taxonomy_models import (
    NormalizedTaxonomy,
    TaxonomyInput,
    TaxonomyReport,
)
from editalfinder_v2.domain.taxonomy_normalization import normalize_taxonomy


@pytest.mark.parametrize("role", ["opportunity_type", "resource_type", "area"])
def test_each_dimension_refuses_foreign_codes_and_unknowns(role):
    catalogs = {
        "opportunity_type": OPPORTUNITY_TYPES,
        "resource_type": RESOURCE_TYPES,
        "area": AREAS,
    }
    foreign = (AREAS | OPPORTUNITY_TYPES | RESOURCE_TYPES) - catalogs[role]
    report = run_rows([(role, code) for code in sorted(foreign | {"unknown"})])
    assert isinstance(report, TaxonomyReport)
    assert all(item.status == "unknown" for item in report.classifications)
    assert all(item.canonical_code is None for item in report.classifications)


@pytest.mark.parametrize("count", [1200, 1201])
def test_public_input_claim_budget(count):
    original = run_rows([("area", "energia")]).input
    data = original.model_dump(mode="json")
    data["claims"] *= count
    result = normalize_taxonomy(TaxonomyInput.model_validate_json(json.dumps(data)))
    if count == 1200:
        assert isinstance(result, TaxonomyReport)
        assert len(result.classifications) == count
    else:
        assert isinstance(result, OperationalError)
        assert result.code == "normalization_limits_exceeded"
        assert result.stage == "normalization"


def test_public_input_aggregate_text_budget():
    original = run_rows([("area", "energia")]).input
    data = original.model_dump(mode="json")
    data["claims"][0]["value"]["original"] = "x" * 8192
    data["claims"] *= 129
    result = normalize_taxonomy(TaxonomyInput.model_validate_json(json.dumps(data)))
    assert isinstance(result, OperationalError)
    assert result.code == "normalization_limits_exceeded"


@pytest.mark.parametrize("boundary", ["constructor", "python", "json"])
@pytest.mark.parametrize("mutation", ["reorder", "index", "evidence", "message", "refusal"])
def test_report_recomputes_outputs_without_audit(boundary, mutation):
    report = run_rows([("area", "energia"), ("area", "unknown")])
    data = report.model_dump(mode="json", exclude={"audit"})
    if mutation == "reorder":
        data["classifications"].reverse()
    elif mutation == "refusal":
        first = data["classifications"][0]
        first.update(canonical_code=None, dimension=None, mapping_rule=None, status="unknown")
        first["diagnostics"] = [
            {
                "code": "normalization_evidence_invalid",
                "message": "fabricated refusal",
                "claim_index": 0,
                "evidence": [first["claim"]["value"]["provenance"]],
            }
        ]
    else:
        diagnostic = data["classifications"][1]["diagnostics"][0]
        if mutation == "index":
            diagnostic["claim_index"] = 0
        elif mutation == "evidence":
            diagnostic["evidence"] = []
        else:
            diagnostic["message"] = "fabricated explanation"
    with pytest.raises(ValidationError):
        if boundary == "constructor":
            TaxonomyReport(**data)
        elif boundary == "python":
            TaxonomyReport.model_validate(data)
        else:
            TaxonomyReport.model_validate_json(json.dumps(data))


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "foreign", "index", "no_index"])
@pytest.mark.parametrize("boundary", ["constructor", "python", "json"])
def test_standalone_diagnostic_binds_claim_evidence(mutation, boundary):
    report = run_rows([("area", "unknown"), ("area", "edital")])
    data = report.classifications[0].model_dump(mode="json")
    diagnostic = data["diagnostics"][0]
    if mutation == "missing":
        diagnostic["evidence"] = []
    elif mutation == "duplicate":
        diagnostic["evidence"] *= 2
    elif mutation == "foreign":
        diagnostic["evidence"] = [report.input.claims[1].value.provenance.model_dump(mode="json")]
    elif mutation == "index":
        diagnostic["claim_index"] = -1
    else:
        diagnostic["claim_index"] = None
    with pytest.raises(ValidationError):
        if boundary == "constructor":
            NormalizedTaxonomy(**data)
        elif boundary == "python":
            NormalizedTaxonomy.model_validate(data)
        else:
            NormalizedTaxonomy.model_validate_json(json.dumps(data))


def test_report_rejects_over_limit_input_even_without_audit():
    report = run_rows([("area", "energia")])
    data = report.model_dump(mode="json", exclude={"audit"})
    data["input"]["claims"] *= 1201
    data["classifications"] *= 1201
    with pytest.raises(ValidationError):
        TaxonomyReport.model_validate_json(json.dumps(data))


def test_multi_area_order_diagnostics_and_immutable_roundtrip():
    report = run_rows([("area", "energia"), ("area", "engenharias"), ("area", "edital")])
    assert [c.canonical_code for c in report.classifications] == ["energia", "engenharias", None]
    diagnostic = report.classifications[2].diagnostics[0]
    assert diagnostic.code == "taxonomy_mapping_not_approved"
    assert diagnostic.claim_index == 2
    assert diagnostic.evidence == (report.input.claims[2].value.provenance,)
    assert report == TaxonomyReport(**report.model_dump())
    assert report == TaxonomyReport.model_validate(report.model_dump())
    assert report == TaxonomyReport.model_validate_json(report.model_dump_json())
    for obj, field, value in [
        (report, "classifications", ()),
        (report.input, "claims", ()),
        (report.classifications[0], "canonical_code", "invented"),
        (report.input.claims[0], "role", "resource_type"),
    ]:
        with pytest.raises(ValidationError):
            setattr(obj, field, value)
    assert (
        report.audit.report_digest
        == hashlib.sha256(report.model_dump_json(exclude={"audit"}).encode("utf-8")).hexdigest()
    )
    changed = report.model_dump(mode="json")
    changed["audit"]["report_digest"] = "0" * 64
    with pytest.raises(ValidationError):
        TaxonomyReport.model_validate(changed)


@pytest.mark.parametrize("text", ["Notícia: edital de bolsa", "Resultado da seleção: bolsa"])
def test_news_and_selection_result_prose_never_classifies(text):
    report = run_rows([("opportunity_type", text)])
    assert report.classifications[0].status == "unknown"
    assert report.classifications[0].canonical_code is None
    assert report.promotable is False
    assert "decision" not in report.model_dump()
    assert "actionable" not in report.model_dump()
