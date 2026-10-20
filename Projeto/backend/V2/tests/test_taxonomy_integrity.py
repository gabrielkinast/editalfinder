import json

import pytest
from pydantic import ValidationError
from test_taxonomy_evidence import sample

from editalfinder_v2.domain.taxonomy_models import NormalizedTaxonomy, TaxonomyInput, TaxonomyReport
from editalfinder_v2.domain.taxonomy_normalization import normalize_taxonomy


@pytest.mark.parametrize(
    "changes",
    [
        {"canonical_code": "invented"},
        {"canonical_code": None},
        {"dimension": "area"},
        {"dimension": None},
        {"mapping_rule": None},
        {"mapping_rule": "invented-v1"},
        {"catalog_version": "future"},
        {"status": "unknown"},
        {"candidate_dimensions": ["area"]},
        {"canonical_code": None, "dimension": None, "mapping_rule": None, "status": "unknown"},
    ],
)
def test_normalized_dto_rejects_contradictions(changes):
    data = normalize_taxonomy(sample()).classifications[0].model_dump(mode="json")
    data.update(changes)
    with pytest.raises(ValidationError):
        NormalizedTaxonomy.model_validate(data)
    with pytest.raises(ValidationError):
        NormalizedTaxonomy.model_validate_json(json.dumps(data))


@pytest.mark.parametrize(
    "mutation", ["omitted", "duplicate", "input_role", "input_catalog", "diagnostics", "evidence"]
)
def test_report_rejects_forgery_even_without_old_audit(mutation):
    data = normalize_taxonomy(sample()).model_dump(mode="json", exclude={"audit"})
    if mutation == "omitted":
        data["classifications"] = []
    elif mutation == "duplicate":
        data["classifications"] *= 2
    elif mutation == "input_role":
        data["input"]["claims"][0]["role"] = "resource_type"
    elif mutation == "input_catalog":
        data["input"]["catalog_version"] = "future"
    elif mutation == "diagnostics":
        data["diagnostics"] = [{"code": "fake", "message": "fake"}]
    else:
        data["input"]["context"]["candidate"]["assertions"] = []
    with pytest.raises(ValidationError):
        TaxonomyReport.model_validate_json(json.dumps(data))


def test_unapproved_mutable_catalog_rejected():
    data = sample().model_dump()
    data["catalog"] = {"area": ["invented"]}
    with pytest.raises(ValidationError):
        TaxonomyInput.model_validate(data)
