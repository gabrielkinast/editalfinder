"""Role-labelled synthetic structures, not native extraction or editorial policy."""

import json

from semantic_fixtures import build_context

from editalfinder_v2.domain.identity_models import IdentityEvidence
from editalfinder_v2.domain.models import (
    Evidence,
    FieldAssertion,
    OpportunityCandidate,
    RawSnapshot,
)
from editalfinder_v2.domain.semantic_common import NormalizationContext, SemanticValue


def build_m22b_context(
    collection: str, rows: list[tuple[str, dict[str, str]]]
) -> tuple[NormalizationContext, tuple[dict[str, SemanticValue], ...]]:
    base, *_ = build_context()
    snapshot = base.snapshots[0]
    candidate = base.candidate
    assertions: list[FieldAssertion] = []
    values: list[dict[str, SemanticValue]] = []
    for index, (role, fields) in enumerate(rows):
        row_values: dict[str, SemanticValue] = {}
        for key, original in fields.items():
            field = role if key == "value" else f"{role}.{key}"
            proof = Evidence(
                snapshot_id=snapshot.id,
                unit=candidate.unit,
                pointer=f"/record/{collection}/{index}/{key}",
                quote=original,
                method="structured_field",
                method_version="m22b-fixture-1",
                confidence="0.9",
                semantic_role=field,
            )
            assertions.append(FieldAssertion(field=field, value=original, evidence=(proof,)))
            row_values[key] = SemanticValue(
                original=original,
                provenance=IdentityEvidence(
                    candidate_id=candidate.id,
                    source_id=candidate.source_id,
                    execution_id=snapshot.execution_id,
                    evidence=proof,
                ),
            )
        values.append(row_values)
    snapshot_data = snapshot.model_dump(exclude={"audit"})
    snapshot_data["payload_json"] = json.dumps(
        {"record": {collection: [{"role": role, **fields} for role, fields in rows]}},
        ensure_ascii=False,
    )
    candidate_data = candidate.model_dump()
    candidate_data["assertions"] = tuple(assertions)
    return (
        NormalizationContext(
            candidate=OpportunityCandidate.model_validate(candidate_data),
            snapshots=(RawSnapshot.model_validate(snapshot_data),),
        ),
        tuple(values),
    )
