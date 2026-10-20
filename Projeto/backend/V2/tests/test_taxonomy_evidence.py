import json
from uuid import UUID

import pytest
from m22b_fixtures import build_m22b_context
from pydantic import ValidationError

from editalfinder_v2.domain.models import OperationalError
from editalfinder_v2.domain.taxonomy_models import TaxonomyClaim, TaxonomyInput
from editalfinder_v2.domain.taxonomy_normalization import normalize_taxonomy


def sample():
    context, values = build_m22b_context(
        "taxonomy_claims", [("opportunity_type", {"value": "bolsa"})]
    )
    return TaxonomyInput(
        context=context, claims=(TaxonomyClaim(role="opportunity_type", value=values[0]["value"]),)
    )


@pytest.mark.parametrize(
    "mutation",
    ["role", "candidate", "execution", "source", "pointer", "unit", "collection", "source_role"],
)
def test_evidence_rebinding_rejected(mutation):
    data = sample().model_dump(mode="json")
    proof = data["claims"][0]["value"]["provenance"]
    if mutation == "role":
        data["claims"][0]["role"] = "resource_type"
    elif mutation in ("candidate", "execution", "source"):
        proof[mutation + "_id"] = str(UUID(int=999))
    elif mutation == "pointer":
        proof["evidence"]["pointer"] = "/other/taxonomy_claims/0/value"
    elif mutation == "unit":
        proof["evidence"]["unit"]["pointer"] = "/other"
    elif mutation == "collection":
        proof["evidence"]["pointer"] = "/record/organization_claims/0/value"
    else:
        snapshot = data["context"]["snapshots"][0]
        payload = json.loads(snapshot["payload_json"])
        payload["record"]["taxonomy_claims"][0]["role"] = "resource_type"
        snapshot["payload_json"] = json.dumps(payload)
        snapshot.pop("audit")
    report = normalize_taxonomy(TaxonomyInput.model_validate(data))
    assert report.classifications[0].canonical_code is None
    assert [d.code for d in report.classifications[0].diagnostics] == [
        "normalization_evidence_invalid"
    ]


@pytest.mark.parametrize("limit", ["claims", "value", "catalog"])
def test_limits(limit):
    data = sample()
    if limit == "claims":
        data = data.model_copy(update={"claims": data.claims * 1201})
    elif limit == "value":
        claim = data.claims[0]
        data = data.model_copy(
            update={
                "claims": (
                    claim.model_copy(
                        update={"value": claim.value.model_copy(update={"original": "x" * 8193})}
                    ),
                )
            }
        )
    else:
        data = data.model_copy(update={"catalog_version": "x" * 8193})
    result = normalize_taxonomy(data)
    assert isinstance(result, OperationalError)
    assert result.code == "normalization_limits_exceeded"


@pytest.mark.parametrize("value", [True, False, 1, 1.0])
def test_numeric_bool_not_text(value):
    data = sample().model_dump(mode="json")
    data["claims"][0]["value"]["original"] = value
    with pytest.raises(ValidationError):
        TaxonomyInput.model_validate(data)
    with pytest.raises(ValidationError):
        TaxonomyInput.model_validate_json(json.dumps(data))
