"""Offline identity claims. UUID kinds and identifier namespaces are not aliases."""

import hashlib
from typing import Literal, Self
from uuid import UUID

from pydantic import Field, model_validator

from .models import Contract, Digest, Evidence, OpportunityCandidate, RawSnapshot, Text

IdentifierType = Literal["url_canonica", "identificador_oficial", "identificador_fonte"]
NormalizationVersion = Literal["opaque-exact-v1", "opaque-nfc-v1", "url-conservative-v1"]
IdentityDecision = Literal[
    "exact_match", "no_supported_match", "conflict", "insufficient_information", "distinct_cycles"
]


class IdentifierNamespace(Contract):
    # Opaque authority label, never derived from a hostname or globally registered here.
    value: Text


class IdentityEvidence(Contract):
    candidate_id: UUID
    source_id: UUID
    execution_id: UUID
    evidence: Evidence


class ExternalIdentifier(Contract):
    original: Text
    identifier_type: IdentifierType
    namespace: IdentifierNamespace
    source_id: UUID
    normalization_version: NormalizationVersion = "opaque-exact-v1"
    provenance: IdentityEvidence

    @model_validator(mode="after")
    def compatible_policy(self) -> Self:
        if (self.identifier_type == "url_canonica") != (
            self.normalization_version == "url-conservative-v1"
        ):
            raise ValueError("Identifier type and normalization policy are incompatible")
        return self


class NormalizedIdentifier(ExternalIdentifier):
    normalized: str | None
    normalization_code: Literal[
        "identifier_normalized",
        "identifier_invalid",
        "identifier_limit_exceeded",
        "identifier_url_invalid",
    ]
    transformations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def bind_normalization(self) -> Self:
        from .identity_normalization import _normalization_values

        expected = _normalization_values(self)
        if (self.normalized, self.normalization_code, self.transformations) != expected:
            raise ValueError("Identifier normalization does not match original and policy")
        return self


class PublicationCycle(Contract):
    """Explicit publisher label; never inferred from dates, titles, URL or execution."""

    original: Text
    normalized: str | None = None
    namespace: IdentifierNamespace
    normalization_version: Literal["cycle-exact-v1"] = "cycle-exact-v1"
    provenance: IdentityEvidence

    @model_validator(mode="after")
    def bind_cycle(self) -> Self:
        if self.normalized is not None and self.normalized != self.original:
            raise ValueError("Publication cycle normalization must preserve the exact label")
        object.__setattr__(self, "normalized", self.original)
        return self


class IdentitySubject(Contract):
    candidate: OpportunityCandidate
    snapshots: tuple[RawSnapshot, ...]
    identifiers: tuple[ExternalIdentifier, ...] = ()
    cycle: PublicationCycle | None = None
    # Both UUIDs are caller claims, NOT inferred from snapshots, URLs or identifiers.
    claimed_opportunity_id: UUID | None = None
    claimed_document_id: UUID | None = None


class IdentityDiagnostic(Contract):
    code: Text
    message: Text
    evidence: tuple[IdentityEvidence, ...] = ()
    rule_version: Literal["m2.1-identity-v1"] = "m2.1-identity-v1"


class IdentityConflict(IdentityDiagnostic):
    pass


class IdentityAudit(Contract):
    schema_version: Literal[2] = Field(...)
    report_digest: Digest
    algorithm: Literal["sha256"]
    hash_version: Literal["identity-pydantic-json-utf8-v1"]
    limits_version: Literal["m2.1-identity-limits-v1"]


class IdentityResolutionReport(Contract):
    left: IdentitySubject
    right: IdentitySubject
    left_identifiers: tuple[NormalizedIdentifier, ...]
    right_identifiers: tuple[NormalizedIdentifier, ...]
    decision: IdentityDecision
    diagnostics: tuple[IdentityDiagnostic, ...] = Field(min_length=1)
    conflicts: tuple[IdentityConflict, ...] = ()
    supporting_evidence: tuple[IdentityEvidence, ...] = ()
    ruleset_version: Literal["m2.1-identity-v1"] = "m2.1-identity-v1"
    audit: IdentityAudit | None = None

    @model_validator(mode="after")
    def bind_audit(self) -> Self:
        expected = IdentityAudit(
            schema_version=2,
            algorithm="sha256",
            hash_version="identity-pydantic-json-utf8-v1",
            limits_version="m2.1-identity-limits-v1",
            report_digest=hashlib.sha256(
                self.model_dump_json(exclude={"audit"}).encode("utf-8")
            ).hexdigest(),
        )
        if self.audit is not None and self.audit != expected:
            raise ValueError("Identity audit does not match complete report")
        object.__setattr__(self, "audit", expected)
        if self.decision == "exact_match" and not self.supporting_evidence:
            raise ValueError("Exact identity match requires supporting evidence")
        return self

    @property
    def promotable(self) -> bool:
        return False
