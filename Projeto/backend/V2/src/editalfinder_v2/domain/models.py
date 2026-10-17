"""Immutable transport contracts; no acquisition, inference or persistence."""

import hashlib
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Literal, Self
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_serializer,
    field_validator,
    model_validator,
)

from .policies import CATALOG_VERSION, VALIDATION_LIMITS_VERSION

Text = Annotated[str, Field(min_length=1)]
Confidence = Annotated[Decimal, Field(ge=0, le=1, allow_inf_nan=False)]


class Contract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)
    schema_version: Literal[2] = 2

    @field_validator("*", mode="before")
    @classmethod
    def utf8_strings(cls, value: object) -> object:
        if isinstance(value, str):
            try:
                value.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise ValueError("Strings must be valid UTF-8") from exc
        return value


Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


class SnapshotAudit(Contract):
    snapshot_id: UUID
    payload_digest: Digest
    algorithm: Literal["sha256"] = "sha256"
    hash_version: Literal["sha256-utf8-v1"] = "sha256-utf8-v1"
    representation: Literal["sanitized-json-text-utf8"] = "sanitized-json-text-utf8"
    contract_version: Literal["2"] = "2"


class RawSnapshot(Contract):
    id: UUID
    source_id: UUID
    source_code: Text
    execution_id: UUID
    collected_at: AwareDatetime
    collector_version: Text
    url: Text
    payload_json: Text
    audit: SnapshotAudit | None = None

    @model_validator(mode="after")
    def bind_audit(self) -> Self:
        try:
            expected = SnapshotAudit(snapshot_id=self.id, payload_digest=self.hash_payload)
        except UnicodeEncodeError as exc:
            raise ValueError("Snapshot must be valid UTF-8") from exc
        if self.audit is not None and self.audit != expected:
            raise ValueError("Snapshot audit does not match identity or payload bytes")
        object.__setattr__(self, "audit", expected)
        return self

    @field_validator("collected_at")
    @classmethod
    def utc_timestamp(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)

    @property
    def hash_payload(self) -> str:
        """Digest of the exact sanitized UTF-8 snapshot, not opportunity identity."""
        return hashlib.sha256(self.payload_json.encode("utf-8")).hexdigest()

    @property
    def hash_version(self) -> str:
        return "sha256-utf8-v1"


class DocumentUnit(Contract):
    """Structural unit within one immutable snapshot, not opportunity identity."""

    snapshot_id: UUID
    pointer: str


class Evidence(Contract):
    snapshot_id: UUID
    pointer: str
    quote: Text
    method: Text
    method_version: Text
    confidence: Confidence
    unit: DocumentUnit | None = None
    semantic_role: str | None = None


class ScalarEnvelope(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class TextScalar(ScalarEnvelope):
    kind: Literal["text"] = "text"
    data: str


class BooleanScalar(ScalarEnvelope):
    kind: Literal["boolean"] = "boolean"
    data: bool


class DateScalar(ScalarEnvelope):
    kind: Literal["date"] = "date"
    data: str


class DecimalScalar(ScalarEnvelope):
    kind: Literal["decimal"] = "decimal"
    data: str


class NullScalar(ScalarEnvelope):
    kind: Literal["null"] = "null"
    data: None = None


ScalarWire = Annotated[
    TextScalar | BooleanScalar | DateScalar | DecimalScalar | NullScalar,
    Field(discriminator="kind"),
]
SCALAR_ADAPTER: TypeAdapter[ScalarWire] = TypeAdapter(ScalarWire)


class FieldAssertion(Contract):
    field: Text
    value: str | bool | date | Decimal | None
    evidence: tuple[Evidence, ...] = ()
    ambiguous: bool = False

    @field_validator(
        "value",
        mode="before",
        json_schema_input_type=ScalarWire | str | bool | date | Decimal | None,
    )
    @classmethod
    def restore_scalar(cls, value: object) -> object:
        # Tags belong to transport, not field semantics. Invalid semantic types
        # remain invalid after transport instead of becoming plausible strings.
        if isinstance(value, dict):
            tagged = SCALAR_ADAPTER.validate_python(value)
            if isinstance(tagged, DateScalar):
                value = date.fromisoformat(tagged.data)
            elif isinstance(tagged, DecimalScalar):
                try:
                    value = Decimal(tagged.data)
                except ArithmeticError as exc:
                    raise ValueError("Invalid decimal") from exc
            else:
                value = tagged.data
        if value is not None and type(value) not in {str, bool, date, Decimal}:
            raise ValueError("Explicit str, bool, date, Decimal or None required")
        if isinstance(value, Decimal) and not value.is_finite():
            raise ValueError("Non-finite scalar")
        if isinstance(value, str):
            try:
                value.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise ValueError("Scalar must be valid UTF-8") from exc
        return value

    @field_serializer("value", when_used="json")
    def serialize_scalar(self, value: str | bool | date | Decimal | None) -> ScalarWire:
        if value is None:
            return NullScalar()
        if isinstance(value, date):
            return DateScalar(data=value.isoformat())
        if isinstance(value, Decimal):
            return DecimalScalar(data=str(value))
        if isinstance(value, bool):
            return BooleanScalar(data=value)
        return TextScalar(data=value)


class CrossDocumentReference(Contract):
    """An untrusted relationship claim, never an identity shortcut."""

    origin: DocumentUnit
    target: DocumentUnit
    relationship: Literal["detail", "amendment", "attachment"]
    link_evidence: Evidence


class OpportunityCandidate(Contract):
    id: UUID
    source_id: UUID
    source_code: Text
    assertions: tuple[FieldAssertion, ...] = ()
    unit: DocumentUnit | None = None
    references: tuple[CrossDocumentReference, ...] = ()


class OperationalError(Contract):
    """An operational failure has no semantic decision and cannot promote."""

    candidate_id: UUID
    code: Text
    stage: Text
    contract_version: Literal["2"] = "2"

    @property
    def promotable(self) -> bool:
        return False


class ValidationDecision(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    REVIEW = "REVIEW"


class ValidationIssue(Contract):
    code: Text
    message: Text
    rule_id: Text
    rule_version: Literal["m1.1-1"] = "m1.1-1"
    field: str | None = None
    related_fields: tuple[str, ...] = ()
    evidence: tuple[Evidence, ...] = ()


def contract_digest(value: Contract) -> str:
    """Exact Pydantic JSON UTF-8 bytes, no semantic or opportunity identity claim."""
    return hashlib.sha256(value.model_dump_json().encode("utf-8")).hexdigest()


class ReviewAttestation(Contract):
    """Untrusted review declaration. No domain field authenticates its author."""

    id: UUID
    reviewer_identity: Text
    reviewed_at: AwareDatetime
    candidate_id: UUID
    candidate_digest: Digest
    evidence_digests: tuple[Digest, ...] = Field(min_length=1)
    policy_version: Text
    decision: ValidationDecision
    provenance: Text

    @field_validator("reviewed_at")
    @classmethod
    def utc_review(cls, value: datetime) -> datetime:
        return value.astimezone(UTC)


class ValidationAudit(Contract):
    audit_version: Literal["m1.1a-full-report-1"] = "m1.1a-full-report-1"
    validation_limits_version: Literal["m1.1a-limits-1"] = "m1.1a-limits-1"
    report_digest: Digest
    report_hash_version: Literal["pydantic-report-json-utf8-v1"] = "pydantic-report-json-utf8-v1"
    contract_version: Literal["2"] = "2"
    candidate_id: UUID
    candidate_digest: Digest
    evidence_digests: tuple[Digest, ...]
    snapshots: tuple[SnapshotAudit, ...]
    catalog_version: Text
    ruleset_version: Literal["m1.1-hardening-1"] = "m1.1-hardening-1"
    rule_versions: tuple[tuple[str, str], ...]
    algorithm: Literal["sha256"] = "sha256"
    hash_version: Literal["pydantic-json-utf8-v2"] = "pydantic-json-utf8-v2"


class ValidationReport(Contract):
    candidate: OpportunityCandidate
    snapshots: tuple[RawSnapshot, ...]
    reference_date: date
    decision: ValidationDecision
    issues: tuple[ValidationIssue, ...]
    ruleset_version: Literal["m1.1-hardening-1"] = "m1.1-hardening-1"
    temporal_status: Literal["encerrada", "nao_determinada"] = "nao_determinada"
    audit: ValidationAudit | None = None
    review_attestations: tuple[ReviewAttestation, ...] = ()

    @model_validator(mode="after")
    def bind_validation_audit(self) -> Self:
        expected = ValidationAudit(
            validation_limits_version=VALIDATION_LIMITS_VERSION,
            report_digest=hashlib.sha256(
                self.model_dump_json(exclude={"audit"}).encode("utf-8")
            ).hexdigest(),
            candidate_id=self.candidate.id,
            candidate_digest=contract_digest(self.candidate),
            evidence_digests=tuple(
                sorted({contract_digest(e) for a in self.candidate.assertions for e in a.evidence})
            ),
            snapshots=tuple(s.audit for s in self.snapshots if s.audit is not None),
            catalog_version=CATALOG_VERSION,
            rule_versions=tuple(sorted({(i.rule_id, i.rule_version) for i in self.issues})),
        )
        if self.audit is not None and self.audit != expected:
            raise ValueError("Validation audit does not match full report, context or versions")
        object.__setattr__(self, "audit", expected)
        return self

    @model_validator(mode="after")
    def consistent_decision(self) -> Self:
        codes = {issue.code for issue in self.issues}
        if not self.issues:
            raise ValueError("Every decision requires structured diagnostics")
        if self.decision == ValidationDecision.ACCEPTED:
            if not self.snapshots or codes != {"instrument_verified"}:
                raise ValueError("ACCEPTED requires evidence and no blocking diagnostics")
            if not self.candidate.assertions or not all(i.evidence for i in self.issues):
                raise ValueError("ACCEPTED requires supporting assertions and evidence")
        elif "instrument_verified" in codes:
            raise ValueError("Non-accepted report cannot certify an instrument")
        if self.decision == ValidationDecision.REJECTED and codes != {"non_opportunity"}:
            raise ValueError("REJECTED requires an uncontradicted non-opportunity diagnosis")
        return self

    @property
    def promotable(self) -> bool:
        """DTOs describe results; they never grant persistence authorization."""
        return False
