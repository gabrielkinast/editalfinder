"""Synthetic role-labelled source data; no production extraction or source policy."""

import json
from datetime import UTC, datetime
from uuid import UUID

from editalfinder_v2.domain.identity_models import IdentityEvidence
from editalfinder_v2.domain.models import (
    DocumentUnit,
    Evidence,
    FieldAssertion,
    OpportunityCandidate,
    RawSnapshot,
)
from editalfinder_v2.domain.semantic_common import NormalizationContext, SemanticValue


def build_context(
    temporal: list[tuple[str, str]] | None = None,
    geographic: list[tuple[str, dict[str, str]]] | None = None,
    scope: str | None = None,
) -> tuple[
    NormalizationContext,
    tuple[SemanticValue, ...],
    tuple[dict[str, SemanticValue], ...],
    SemanticValue | None,
]:
    sid, source, execution, cid = (UUID(int=i) for i in range(1, 5))
    unit = DocumentUnit(snapshot_id=sid, pointer="/record")
    assertions: list[FieldAssertion] = []

    def value(original: str, role: str, pointer: str) -> SemanticValue:
        proof = Evidence(
            snapshot_id=sid,
            pointer=pointer,
            quote=original,
            method="structured_field",
            method_version="fixture-1",
            confidence="0.9",
            unit=unit,
            semantic_role=role,
        )
        assertions.append(FieldAssertion(field=role, value=original, evidence=(proof,)))
        return SemanticValue(
            original=original,
            provenance=IdentityEvidence(
                candidate_id=cid, source_id=source, execution_id=execution, evidence=proof
            ),
        )

    temporal_values = tuple(
        value(original, role, f"/record/temporal_events/{i}/value")
        for i, (role, original) in enumerate(temporal or [])
    )
    geographic_values = tuple(
        {
            key: value(original, f"{role}.{key}", f"/record/geographic_locations/{i}/{key}")
            for key, original in fields.items()
        }
        for i, (role, fields) in enumerate(geographic or [])
    )
    scope_value = value(scope, "geographic_scope", "/record/geographic_scope") if scope else None
    record: dict[str, object] = {
        "temporal_events": [
            {"role": role, "value": original} for role, original in (temporal or [])
        ],
        "geographic_locations": [{"role": role, **fields} for role, fields in (geographic or [])],
    }
    if scope is not None:
        record["geographic_scope"] = scope
    snapshot = RawSnapshot(
        id=sid,
        source_id=source,
        source_code="synthetic-source",
        execution_id=execution,
        collected_at=datetime(2026, 1, 1, tzinfo=UTC),
        collector_version="fixture-1",
        url="https://example.org.br/opportunity",
        payload_json=json.dumps({"record": record}, ensure_ascii=False),
    )
    candidate = OpportunityCandidate(
        id=cid,
        source_id=source,
        source_code="synthetic-source",
        assertions=tuple(assertions),
        unit=unit,
    )
    return (
        NormalizationContext(candidate=candidate, snapshots=(snapshot,)),
        temporal_values,
        geographic_values,
        scope_value,
    )
