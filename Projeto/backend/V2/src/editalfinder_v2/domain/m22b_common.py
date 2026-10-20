"""M2.2b-only offline boundaries; older normalization policies remain unchanged."""

import hashlib
import re
from typing import Literal, Self

from pydantic import Field, model_validator

from .models import Contract, Digest, OperationalError, contract_digest
from .safety import resolve_pointer
from .semantic_common import NormalizationContext, PreparedContext, SemanticValue, prepare_context
from .validation import evidence_matches

MAX_VALUE_CHARS = 8192

Collection = Literal["financial_claims", "organization_claims", "taxonomy_claims"]


def prepare_m22b(
    context: NormalizationContext,
    *,
    claim_count: int,
    values: tuple[SemanticValue, ...],
    extra_text: tuple[str, ...] = (),
) -> PreparedContext | OperationalError:
    texts = tuple(v.original for v in values) + extra_text
    if any(len(text) > MAX_VALUE_CHARS for text in texts):
        return OperationalError(
            candidate_id=context.candidate.id,
            code="normalization_limits_exceeded",
            stage="normalization",
        )
    return prepare_context(
        context,
        claim_count=max(claim_count, len(values)),
        text_chars=sum(len(text) for text in texts),
    )


def matches_m22b(
    prepared: PreparedContext,
    value: SemanticValue,
    role: str,
    *,
    collection: Collection,
    component: str | None = None,
) -> bool:
    """Bind declared scalar fields/role-labelled rows, never arbitrary prose.

    Preserve the older matcher's collection API; reuse its direct-field path
    and the same indexed contextual invariants for the new collections.
    """
    if collection not in {"financial_claims", "organization_claims", "taxonomy_claims"}:
        return False
    if prepared.matches(value, role, component=component):
        return True
    candidate = prepared.context.candidate
    unit = candidate.unit
    proof = value.provenance
    evidence = proof.evidence
    snapshot = prepared.snapshots.get(evidence.snapshot_id)
    field = role if component is None else f"{role}.{component}"
    if (
        unit is None
        or snapshot is None
        or proof.candidate_id != candidate.id
        or proof.source_id != candidate.source_id
        or proof.execution_id != snapshot.execution_id
        or snapshot.source_id != candidate.source_id
        or snapshot.source_code != candidate.source_code
        or evidence.snapshot_id != unit.snapshot_id
        or evidence.unit != unit
        or evidence.semantic_role != field
        or field in prepared.ambiguous_fields
        or evidence.quote != value.original
        or (field, value.original, contract_digest(evidence)) not in prepared.assertion_evidence
    ):
        return False
    prefix = unit.pointer + "/" + collection
    if not evidence.pointer.startswith(prefix + "/"):
        return False
    pieces = evidence.pointer[len(prefix) + 1 :].split("/")
    if (
        len(pieces) != 2
        or not re.fullmatch(r"0|[1-9][0-9]*", pieces[0], re.ASCII)
        or pieces[1] != (component or "value")
    ):
        return False
    payload = prepared.payloads[evidence.snapshot_id]
    ok, rows = resolve_pointer(payload, prefix)
    if not ok or not isinstance(rows, list):
        return False
    ok, source_role = resolve_pointer(payload, prefix + "/" + pieces[0] + "/role")
    if not ok or source_role != role or not isinstance(source_role, str):
        return False
    ok, node = resolve_pointer(payload, evidence.pointer)
    return (
        ok
        and isinstance(node, str)
        and node == value.original
        and evidence_matches(evidence, payload, claimed_text=value.original)
    )


class M22BAudit(Contract):
    schema_version: Literal[2] = Field(...)
    report_digest: Digest
    algorithm: Literal["sha256"]
    hash_version: Literal["normalization-pydantic-json-utf8-v1"]
    limits_version: Literal["m2.2b-normalization-limits-v1"]


class M22BReport(Contract):
    audit: M22BAudit | None = None
    policy_version: Literal["m2.2b-semantics-v1"] = "m2.2b-semantics-v1"

    @model_validator(mode="after")
    def bind_audit(self) -> Self:
        expected = M22BAudit(
            schema_version=2,
            algorithm="sha256",
            hash_version="normalization-pydantic-json-utf8-v1",
            limits_version="m2.2b-normalization-limits-v1",
            report_digest=hashlib.sha256(
                self.model_dump_json(exclude={"audit"}).encode("utf-8")
            ).hexdigest(),
        )
        if self.audit is not None and self.audit != expected:
            raise ValueError("Normalization audit does not match complete report")
        object.__setattr__(self, "audit", expected)
        return self

    @property
    def promotable(self) -> bool:
        return False
