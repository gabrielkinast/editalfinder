"""Indexed comparison of scoped identity claims. No authorization, merge or I/O."""

import unicodedata
from uuid import UUID

from pydantic import JsonValue

from .identity_models import (
    IdentityConflict,
    IdentityDecision,
    IdentityDiagnostic,
    IdentityEvidence,
    IdentityResolutionReport,
    IdentitySubject,
    NormalizedIdentifier,
)
from .identity_normalization import normalize_identifier
from .models import OperationalError, RawSnapshot, contract_digest
from .safety import parse_payload, resolve_pointer
from .validation import evidence_matches

MAX_IDENTITY_IDENTIFIERS = 10_000
MAX_IDENTITY_SNAPSHOTS = 32
MAX_IDENTITY_PAYLOAD_BYTES = 8 * 1024 * 1024
MAX_IDENTITY_TEXT_CHARS = 1024 * 1024
MAX_IDENTITY_ASSERTION_EVIDENCE = 30_000
IdentityKey = tuple[str, str, UUID, str, str]


def _within_limits(subject: IdentitySubject) -> bool:
    candidate = subject.candidate
    return (
        len(subject.identifiers) <= MAX_IDENTITY_IDENTIFIERS
        and len(candidate.assertions) <= MAX_IDENTITY_IDENTIFIERS + 2
        and len(candidate.references) <= 1000
        and len(subject.snapshots) <= MAX_IDENTITY_SNAPSHOTS
        and sum(len(s.payload_json.encode("utf-8")) for s in subject.snapshots)
        <= MAX_IDENTITY_PAYLOAD_BYTES
        and sum(len(i.original) for i in subject.identifiers) <= MAX_IDENTITY_TEXT_CHARS
        and sum(len(a.evidence) for a in candidate.assertions) <= MAX_IDENTITY_ASSERTION_EVIDENCE
    )


def _safe_label(value: str) -> bool:
    return bool(value.strip()) and not any(
        unicodedata.category(c) in {"Cc", "Cf", "Cs"} for c in value
    )


def _verify_subject(subject: IdentitySubject) -> tuple[str | None, tuple[IdentityEvidence, ...]]:
    candidate = subject.candidate
    snapshots: dict[UUID, RawSnapshot] = {}
    payloads: dict[UUID, JsonValue] = {}
    for snapshot in subject.snapshots:
        if snapshot.id in snapshots:
            return "identity_duplicate_snapshot_id", ()
        snapshots[snapshot.id] = snapshot
        try:
            payloads[snapshot.id] = parse_payload(snapshot.payload_json)
        except (ValueError, RecursionError):
            return "identity_invalid_snapshot_json", ()
    # A proof must already belong to the exact assertion in this candidate.
    assertion_evidence: set[tuple[str, str, str]] = set()
    ambiguous_fields = {a.field for a in candidate.assertions if a.ambiguous}
    values_by_field: dict[str, set[tuple[str, str]]] = {}
    for assertion in candidate.assertions:
        if assertion.value is not None:
            values_by_field.setdefault(assertion.field, set()).add(
                (type(assertion.value).__name__, str(assertion.value))
            )
        if isinstance(assertion.value, str):
            for evidence in assertion.evidence:
                assertion_evidence.add(
                    (assertion.field, assertion.value, contract_digest(evidence))
                )
    roles = {
        "identificador_oficial": "official_identifier",
        "identificador_fonte": "source_identifier",
        "url_canonica": "official_url",
    }
    claims = [
        (i.original, i.namespace.value, i.provenance, i.source_id, roles[i.identifier_type])
        for i in subject.identifiers
    ]
    if subject.cycle is not None:
        claims.append(
            (
                subject.cycle.original,
                subject.cycle.namespace.value,
                subject.cycle.provenance,
                candidate.source_id,
                "publication_cycle",
            )
        )
    for original, namespace, proof, source_id, expected_role in claims:
        evidence = proof.evidence
        field = evidence.semantic_role
        supporting_snapshot = snapshots.get(evidence.snapshot_id)
        token = field.replace("~", "~0").replace("/", "~1") if field is not None else ""
        resolved, node = resolve_pointer(payloads.get(evidence.snapshot_id), evidence.pointer)
        if (
            not resolved
            or not isinstance(node, str)
            or node != original
            or not _safe_label(namespace)
            or not _safe_label(original)
            or candidate.unit is None
            or proof.candidate_id != candidate.id
            or proof.source_id != candidate.source_id
            or source_id != candidate.source_id
            or supporting_snapshot is None
            or proof.execution_id != supporting_snapshot.execution_id
            or supporting_snapshot.source_id != candidate.source_id
            or supporting_snapshot.source_code != candidate.source_code
            or evidence.snapshot_id != candidate.unit.snapshot_id
            or evidence.unit != candidate.unit
            or field is None
            or field != expected_role
            or field in ambiguous_fields
            or len(values_by_field.get(field, ())) != 1
            or evidence.pointer != candidate.unit.pointer + "/" + token
            or evidence.quote != original
            or (field, original, contract_digest(evidence)) not in assertion_evidence
            or not evidence_matches(
                evidence, payloads.get(evidence.snapshot_id), claimed_text=original
            )
        ):
            return "identity_evidence_invalid", (proof,)
    return None, ()


def _key(identifier: NormalizedIdentifier) -> IdentityKey:
    assert identifier.normalized is not None
    return (
        identifier.identifier_type,
        identifier.namespace.value,
        identifier.source_id,
        identifier.normalization_version,
        identifier.normalized,
    )


def resolve_identity(
    left: IdentitySubject,
    right: IdentitySubject,
) -> IdentityResolutionReport | OperationalError:
    """Compare only supplied records; exact_match is scoped equality, never a merge."""
    if not _within_limits(left) or not _within_limits(right):
        return OperationalError(
            candidate_id=left.candidate.id, code="identity_limits_exceeded", stage="identity"
        )
    for subject in (left, right):
        error, witnesses = _verify_subject(subject)
        if error is not None:
            if error != "identity_evidence_invalid":
                return OperationalError(
                    candidate_id=subject.candidate.id, code=error, stage="identity"
                )
            return IdentityResolutionReport(
                left=left,
                right=right,
                left_identifiers=(),
                right_identifiers=(),
                decision="insufficient_information",
                diagnostics=(
                    IdentityDiagnostic(
                        code=error,
                        message="Identity proof does not bind the original value to this record.",
                        evidence=witnesses,
                    ),
                ),
            )
    left_snapshots = {snapshot.id: snapshot for snapshot in left.snapshots}
    for snapshot in right.snapshots:
        if snapshot.id in left_snapshots and snapshot != left_snapshots[snapshot.id]:
            return OperationalError(
                candidate_id=right.candidate.id,
                code="identity_snapshot_context_conflict",
                stage="identity",
            )
    left_ids = tuple(normalize_identifier(i) for i in left.identifiers)
    right_ids = tuple(normalize_identifier(i) for i in right.identifiers)
    diagnostics: list[IdentityDiagnostic] = []
    conflicts: list[IdentityConflict] = []
    supporting: tuple[IdentityEvidence, ...] = ()

    def diagnostic(
        code: str,
        message: str,
        evidence: tuple[IdentityEvidence, ...] = (),
        *,
        conflict: bool = False,
    ) -> None:
        diagnostics.append(IdentityDiagnostic(code=code, message=message, evidence=evidence))
        if conflict:
            conflicts.append(IdentityConflict(code=code, message=message, evidence=evidence))

    def finish(decision: IdentityDecision) -> IdentityResolutionReport:
        return IdentityResolutionReport(
            left=left,
            right=right,
            left_identifiers=left_ids,
            right_identifiers=right_ids,
            decision=decision,
            diagnostics=tuple(diagnostics),
            conflicts=tuple(conflicts),
            supporting_evidence=supporting,
        )

    invalid = [i for i in (*left_ids, *right_ids) if i.normalized is None]
    if invalid:
        for identifier in invalid:
            diagnostic(
                identifier.normalization_code,
                "Identifier is outside its normalization domain.",
                (identifier.provenance,),
            )
        return finish("insufficient_information")
    # Unique indexed keys avoid identifier-pair cross products; duplicates remain in DTOs.
    indexes = []
    for identifiers in (left_ids, right_ids):
        index: dict[IdentityKey, NormalizedIdentifier] = {}
        for identifier in identifiers:
            index.setdefault(_key(identifier), identifier)
        indexes.append(index)
    li, ri = indexes
    if (
        left.candidate.source_id == right.candidate.source_id
        and left.candidate.source_code != right.candidate.source_code
    ):
        diagnostic(
            "source_context_conflict",
            "Same source UUID claims different source codes.",
            tuple(i.provenance for i in (*left_ids[:1], *right_ids[:1])),
            conflict=True,
        )
        return finish("conflict")
    official_left = {k for k in li if k[0] == "identificador_oficial"}
    official_right = {k for k in ri if k[0] == "identificador_oficial"}
    urls = {k for k in li.keys() & ri.keys() if k[0] == "url_canonica"}
    apparent_document = (
        left.candidate.unit is not None and left.candidate.unit == right.candidate.unit
    ) or (
        left.claimed_document_id is not None
        and left.claimed_document_id == right.claimed_document_id
    )
    if urls:
        diagnostic(
            "url_is_not_opportunity_identity",
            "Shared URL is a locator claim, not an opportunity identity.",
            (li[min(urls)].provenance, ri[min(urls)].provenance),
        )
    if not official_left or not official_right:
        diagnostic(
            "official_identifier_missing",
            "An evidenced official identifier is required on both records.",
        )
        return finish("insufficient_information")
    if left.candidate.source_id != right.candidate.source_id:
        diagnostic("source_scope_differs", "Cross-source equivalence policies are not approved.")
        return finish("no_supported_match")
    namespaces_left = {k[1] for k in official_left}
    namespaces_right = {k[1] for k in official_right}
    if not namespaces_left & namespaces_right:
        diagnostic(
            "namespace_scope_differs",
            "Values from distinct authority namespaces are not comparable.",
        )
        return finish("no_supported_match")
    lc, rc = left.cycle, right.cycle
    if lc is None or rc is None:
        diagnostic(
            "publication_cycle_missing",
            "URL and official number may be reused; explicit cycles are required.",
        )
        return finish("insufficient_information")
    if lc.namespace != rc.namespace:
        diagnostic(
            "cycle_namespace_differs",
            "Publisher cycle namespaces are not comparable.",
            (lc.provenance, rc.provenance),
        )
        return finish("insufficient_information")
    matches = official_left & official_right
    if lc.original != rc.original:
        diagnostic(
            "distinct_publication_cycles",
            "Explicit publisher cycle labels differ within the same scope.",
            (lc.provenance, rc.provenance),
        )
        if matches or urls:
            key = min(matches or urls)
            diagnostic(
                "contextual_key_reused_across_cycles",
                "SQL key lacks cycle; reuse cannot be persisted safely without policy review.",
                (li[key].provenance, ri[key].provenance),
                conflict=True,
            )
        return finish("distinct_cycles")
    # Different asserted owners for an identical official contextual key are a conflict.
    if (
        matches
        and left.claimed_opportunity_id is not None
        and right.claimed_opportunity_id is not None
        and left.claimed_opportunity_id != right.claimed_opportunity_id
    ):
        key = min(matches)
        diagnostic(
            "opportunity_claim_conflict",
            "Same official key and cycle claims incompatible opportunity UUIDs.",
            (li[key].provenance, ri[key].provenance),
            conflict=True,
        )
        return finish("conflict")
    by_namespace_left: dict[tuple[str, str], set[str]] = {}
    by_namespace_right: dict[tuple[str, str], set[str]] = {}
    for keys, grouped in ((official_left, by_namespace_left), (official_right, by_namespace_right)):
        for key in keys:
            grouped.setdefault((key[1], key[3]), set()).add(key[4])
    comparable = by_namespace_left.keys() & by_namespace_right.keys()
    disagreement = any(by_namespace_left[n] != by_namespace_right[n] for n in comparable)
    if disagreement and (
        matches
        or urls
        or apparent_document
        or (
            left.claimed_opportunity_id is not None
            and left.claimed_opportunity_id == right.claimed_opportunity_id
        )
    ):
        diagnostic(
            "document_identifier_conflict",
            "Associated records assert different official identifiers in a comparable namespace.",
            (li[min(official_left)].provenance, ri[min(official_right)].provenance),
            conflict=True,
        )
        return finish("conflict")
    if not matches:
        code = "official_identifiers_differ" if comparable else "normalization_policy_differs"
        diagnostic(
            code, "No identical official contextual key under the same normalization policy."
        )
        return finish("no_supported_match")
    supporting = tuple(
        proof for key in sorted(matches) for proof in (li[key].provenance, ri[key].provenance)
    ) + (lc.provenance, rc.provenance)
    diagnostic(
        "official_identifier_cycle_match",
        "Exact source-scoped official identifier and evidenced publisher cycle agree.",
        supporting,
    )
    return finish("exact_match")
