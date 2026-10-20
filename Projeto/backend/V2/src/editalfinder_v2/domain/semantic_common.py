"""Shared, offline semantic evidence boundary; no extraction or identity resolution."""

import hashlib
import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Self
from uuid import UUID

from pydantic import Field, JsonValue, model_validator

from .identity_models import IdentityEvidence
from .models import (
    Contract,
    Digest,
    OperationalError,
    OpportunityCandidate,
    RawSnapshot,
    Text,
    contract_digest,
)
from .policies import MAX_ASSERTIONS, MAX_CANDIDATE_EVIDENCE, MAX_FIELD_EVIDENCE
from .safety import parse_payload, resolve_pointer
from .validation import evidence_matches

MAX_NORMALIZATION_CLAIMS = 1200
MAX_NORMALIZATION_SNAPSHOTS = 32
MAX_NORMALIZATION_PAYLOAD_BYTES = 8 * 1024 * 1024
MAX_NORMALIZATION_TEXT_CHARS = 1024 * 1024


class SemanticValue(Contract):
    original: str
    provenance: IdentityEvidence


class NormalizationContext(Contract):
    candidate: OpportunityCandidate
    snapshots: tuple[RawSnapshot, ...]


class NormalizationDiagnostic(Contract):
    code: Text
    message: Text
    claim_index: int | None = None
    evidence: tuple[IdentityEvidence, ...] = ()


class NormalizationAudit(Contract):
    schema_version: Literal[2] = Field(...)
    report_digest: Digest
    algorithm: Literal["sha256"]
    hash_version: Literal["normalization-pydantic-json-utf8-v1"]
    limits_version: Literal["m2.2a-normalization-limits-v1"]


class AuditedNormalizationReport(Contract):
    audit: NormalizationAudit | None = None
    policy_version: Literal["m2.2a-semantics-v1"] = "m2.2a-semantics-v1"

    @model_validator(mode="after")
    def bind_audit(self) -> Self:
        expected = NormalizationAudit(
            schema_version=2,
            algorithm="sha256",
            hash_version="normalization-pydantic-json-utf8-v1",
            limits_version="m2.2a-normalization-limits-v1",
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


@dataclass(frozen=True)
class PreparedContext:
    context: NormalizationContext
    snapshots: Mapping[UUID, RawSnapshot]
    payloads: Mapping[UUID, JsonValue]
    assertion_evidence: frozenset[tuple[str, str, str]]
    ambiguous_fields: frozenset[str]

    def matches(
        self,
        value: SemanticValue,
        role: str,
        *,
        collection: Literal["temporal_events", "geographic_locations"] | None = None,
        component: str | None = None,
    ) -> bool:
        """Bind a literal to an explicit role in this candidate's structural unit.

        Collections are source-adapter schemas, not inferred PDF structure. In a
        collection, a role-bearing object AND a matching assertion are required.
        Multiple values for one role are allowed here so the normalizer can
        preserve and diagnose conflicts instead of hiding them as missing data.
        """
        candidate = self.context.candidate
        proof = value.provenance
        evidence = proof.evidence
        unit = candidate.unit
        snapshot = self.snapshots.get(evidence.snapshot_id)
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
            or field in self.ambiguous_fields
            or evidence.quote != value.original
            or (field, value.original, contract_digest(evidence)) not in self.assertion_evidence
        ):
            return False
        payload = self.payloads[evidence.snapshot_id]
        resolved, node = resolve_pointer(payload, evidence.pointer)
        if not resolved or not isinstance(node, str) or node != value.original:
            return False
        token = field.replace("~", "~0").replace("/", "~1")
        direct_pointer = unit.pointer + "/" + token
        if evidence.pointer != direct_pointer:
            if collection is None:
                return False
            prefix = unit.pointer + "/" + collection
            if not evidence.pointer.startswith(prefix + "/"):
                return False
            pieces = evidence.pointer[len(prefix) + 1 :].split("/")
            if (
                len(pieces) != 2
                or not re.fullmatch(r"0|[1-9][0-9]*", pieces[0], flags=re.ASCII)
                or pieces[1] != (component or "value")
            ):
                return False
            ok, rows = resolve_pointer(payload, prefix)
            if not ok or not isinstance(rows, list):
                return False
            ok, source_role = resolve_pointer(payload, prefix + "/" + pieces[0] + "/role")
            if not ok or not isinstance(source_role, str) or source_role != role:
                return False
        return evidence_matches(evidence, payload, claimed_text=value.original)


def prepare_context(
    context: NormalizationContext, *, claim_count: int, text_chars: int = 0
) -> PreparedContext | OperationalError:
    """Index once, retaining M1 evidence limits; refuse, never truncate."""
    candidate = context.candidate

    def failure(code: str) -> OperationalError:
        return OperationalError(candidate_id=candidate.id, code=code, stage="normalization")

    if (
        not 0 <= claim_count <= MAX_NORMALIZATION_CLAIMS
        or not 0 <= text_chars <= MAX_NORMALIZATION_TEXT_CHARS
        or len(candidate.assertions) > MAX_ASSERTIONS
        or len(candidate.references) > 1000
        or len(context.snapshots) > MAX_NORMALIZATION_SNAPSHOTS
        or sum(len(a.evidence) for a in candidate.assertions) > MAX_CANDIDATE_EVIDENCE
        or sum(len(s.payload_json) for s in context.snapshots) > MAX_NORMALIZATION_PAYLOAD_BYTES
    ):
        return failure("normalization_limits_exceeded")
    if (
        sum(len(s.payload_json.encode("utf-8")) for s in context.snapshots)
        > MAX_NORMALIZATION_PAYLOAD_BYTES
    ):
        return failure("normalization_limits_exceeded")
    snapshots: dict[UUID, RawSnapshot] = {}
    payloads: dict[UUID, JsonValue] = {}
    for snapshot in context.snapshots:
        if snapshot.id in snapshots:
            return failure("normalization_duplicate_snapshot_id")
        snapshots[snapshot.id] = snapshot
        try:
            payloads[snapshot.id] = parse_payload(snapshot.payload_json)
        except (ValueError, RecursionError):
            return failure("normalization_invalid_snapshot_json")
    evidence_index: set[tuple[str, str, str]] = set()
    field_counts: dict[str, int] = {}
    ambiguous: set[str] = set()
    for assertion in candidate.assertions:
        field_counts[assertion.field] = field_counts.get(assertion.field, 0) + len(
            assertion.evidence
        )
        if field_counts[assertion.field] > MAX_FIELD_EVIDENCE:
            return failure("normalization_limits_exceeded")
        if assertion.ambiguous:
            ambiguous.add(assertion.field)
        if isinstance(assertion.value, str):
            evidence_index.update(
                (assertion.field, assertion.value, contract_digest(e)) for e in assertion.evidence
            )
    return PreparedContext(
        context,
        MappingProxyType(snapshots),
        MappingProxyType(payloads),
        frozenset(evidence_index),
        frozenset(ambiguous),
    )
