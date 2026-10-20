"""Versioned synthetic declarations; no extraction, classification or golden capture."""

import json
from datetime import date
from pathlib import Path
from typing import Any

from m23_fixtures import adapt_records

from editalfinder_v2.domain.identity_models import ExternalIdentifier, IdentifierNamespace
from editalfinder_v2.domain.integration_models import IdentityComparison, IntegrationInput

FIXTURE = Path(__file__).parent / "fixtures/m23c_v1.json"


def dataset() -> dict[str, Any]:
    """Fresh decoded declarations prevent test cross-contamination."""
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def case_by_id(case_id: str) -> dict[str, Any]:
    return next(c for c in dataset()["cases"] if c["case_id"] == case_id)


def build(case: dict[str, Any]) -> IntegrationInput:
    """Use the existing adapter; changes below are EXPLICIT fixture instructions."""
    data = adapt_records(case["records"])
    candidates = list(data.candidates)
    for index, item in enumerate(candidates):
        candidate = item.context.candidate
        assertions = tuple(
            a.model_copy(update={"value": date.fromisoformat(a.value)})
            if a.field in case.get("typed_date_fields", [])
            else a
            for a in candidate.assertions
        )
        candidate = candidate.model_copy(update={"assertions": assertions})
        item = item.model_copy(
            update={"context": item.context.model_copy(update={"candidate": candidate})}
        )
        identifiers = list(item.identifiers)
        if case.get("include_url_identifiers"):
            a = next(a for a in assertions if a.field == "official_url")
            proof = item.identifiers[0].provenance.model_copy(update={"evidence": a.evidence[0]})
            identifiers.append(
                ExternalIdentifier(
                    identifier_type="url_canonica",
                    normalization_version="url-conservative-v1",
                    namespace=IdentifierNamespace(value="synthetic-publisher"),
                    original=a.value,
                    source_id=candidate.source_id,
                    provenance=proof,
                )
            )
        if index == 1 and "right_identifier_namespace" in case:
            identifiers = [
                i.model_copy(
                    update={
                        "namespace": IdentifierNamespace(value=case["right_identifier_namespace"])
                    }
                )
                for i in identifiers
            ]
        if case.get("omit_identifiers"):
            identifiers = []
        if index == 1 and case.get("foreign_identity_proof"):
            identifiers[0] = identifiers[0].model_copy(
                update={"provenance": candidates[0].identifiers[0].provenance}
            )
        candidates[index] = item.model_copy(update={"identifiers": tuple(identifiers)})
    return IntegrationInput(
        candidates=tuple(candidates),
        reference_date=date.fromisoformat(dataset()["reference_date"]),
        identity_comparisons=tuple(
            IdentityComparison(left_index=a, right_index=b)
            for a, b in case.get("identity_comparisons", [])
        ),
    )
