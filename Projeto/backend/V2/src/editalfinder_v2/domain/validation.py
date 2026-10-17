"""Deterministic validation of already extracted assertions (no I/O)."""

import json
from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import JsonValue

from .models import (
    Evidence,
    OperationalError,
    OpportunityCandidate,
    RawSnapshot,
    ReviewAttestation,
    ValidationDecision,
    ValidationIssue,
    ValidationReport,
)
from .policies import (
    BOOL_FIELDS,
    DATE_FIELDS,
    DOMAINS,
    MAX_ASSERTIONS,
    MAX_CANDIDATE_EVIDENCE,
    MAX_FIELD_EVIDENCE,
    SOURCES,
    SUPPORTED_FIELDS,
    TEXT_FIELDS,
)
from .safety import parse_payload, resolve_pointer, valid_url

NON_OPPORTUNITIES = frozenset(
    {"news", "aggregator", "result", "menu", "institutional", "auxiliary"}
)


def evidence_matches(
    evidence: Evidence, payload: JsonValue, *, claimed_text: str | None = None
) -> bool:
    """Resolve an RFC 6901 pointer and verify the exact quoted substring."""
    if evidence.method not in {
        "manual_review",
        "structured_field",
        "deterministic_rule",
    }:
        return False
    if evidence.confidence <= 0 or not evidence.quote.strip():
        return False
    resolved, node = resolve_pointer(payload, evidence.pointer)
    if not resolved:
        return False
    node_text = node if isinstance(node, str) else json.dumps(node, ensure_ascii=False)
    return (
        isinstance(node, (str, bool))
        and evidence.quote in node_text
        and (claimed_text is None or claimed_text == node_text)
    )


def validate(
    candidate: OpportunityCandidate,
    snapshots: tuple[RawSnapshot, ...],
    *,
    reference_date: date,
    errors: tuple[OperationalError, ...] = (),
    review_attestations: tuple[ReviewAttestation, ...] = (),
) -> ValidationReport | OperationalError:
    if errors:
        if any(e.candidate_id != candidate.id for e in errors):
            return OperationalError(
                candidate_id=candidate.id, code="error_context_mismatch", stage="validation"
            )
        return errors[0]
    # Bound diagnostic evidence amplification before parsing or constructing reports.
    if len(candidate.assertions) > MAX_ASSERTIONS:
        return OperationalError(
            candidate_id=candidate.id, code="validation_limits_exceeded", stage="validation"
        )
    known_by_field: dict[str, dict[tuple[str, str], str | bool | date | Decimal]] = {}
    evidence_by_field: dict[str, list[tuple[int, Evidence]]] = {}
    evidence_count = 0
    for index, assertion in enumerate(candidate.assertions):
        field = assertion.field
        known = known_by_field.setdefault(field, {})
        if assertion.value is not None:
            known[(type(assertion.value).__name__, str(assertion.value))] = assertion.value
        evidence_count += len(assertion.evidence)
        related_evidence = evidence_by_field.setdefault(field, [])
        if (
            evidence_count > MAX_CANDIDATE_EVIDENCE
            or len(related_evidence) + len(assertion.evidence) > MAX_FIELD_EVIDENCE
        ):
            return OperationalError(
                candidate_id=candidate.id, code="validation_limits_exceeded", stage="validation"
            )
        related_evidence.extend((index, e) for e in assertion.evidence)

    payloads: dict[UUID, JsonValue] = {}
    snapshots_by_id: dict[UUID, RawSnapshot] = {}
    for snapshot in snapshots:
        if snapshot.id in payloads:
            return OperationalError(
                candidate_id=candidate.id, code="duplicate_snapshot_id", stage="validation"
            )
        try:
            payloads[snapshot.id] = parse_payload(snapshot.payload_json)
            snapshots_by_id[snapshot.id] = snapshot
        except (ValueError, RecursionError):
            return OperationalError(
                candidate_id=candidate.id, code="invalid_snapshot_json", stage="validation"
            )
    issues: list[ValidationIssue] = []
    # Null means absence, never an overwrite. Conflicting non-null values stay unresolved.
    values: dict[str, str | bool | date | Decimal | None] = {}
    for field, known_values in sorted(known_by_field.items()):
        values[field] = next(iter(known_values.values())) if len(known_values) == 1 else None

    def issue(
        code: str, message: str, field: str | None = None, *, fields: tuple[str, ...] = ()
    ) -> None:
        related = (field,) if field is not None else fields
        # Keep original assertion/evidence order, including duplicates and null context.
        indexed = [item for key in set(related) for item in evidence_by_field.get(key, ())]
        evidence = tuple(e for _, e in sorted(indexed, key=lambda item: item[0]))
        issues.append(
            ValidationIssue(
                code=code,
                message=message,
                rule_id=code,
                field=field,
                related_fields=related,
                evidence=evidence,
            )
        )

    if review_attestations:
        issue(
            "untrusted_review_attestation",
            "Review declarations are preserved but no authentication boundary is configured.",
        )
    if candidate.source_code not in SOURCES:
        issue("source_outside_baseline", "Source is not in the approved pilot baseline.")
    if candidate.unit is None:
        issue("missing_candidate_unit", "Candidate requires an explicit structural unit.")
    if candidate.references:
        issue(
            "cross_document_relationship_unverified",
            "Cross-document association rules are not approved; references are claims only.",
        )
    for assertion in candidate.assertions:
        field, value = assertion.field, assertion.value
        if field in {"specific_instrument", "actionable", "content_kind"} and value is not None:
            issue(
                "trusted_review_required",
                "Extraction method is not review authorization; no trusted adapter is installed.",
                field,
            )
            if not assertion.evidence or any(
                e.method != "manual_review" for e in assertion.evidence
            ):
                issue("intent_rule_not_approved", "Automated intent rules await approval.", field)
        if value is not None and field in {
            "geographic_scope",
            "opportunity_type",
            "resource_type",
            "area",
        }:
            issue(
                "semantic_mapping_not_approved",
                "Structural equality is not an approved source-specific semantic mapping.",
                field,
            )
        if assertion.ambiguous:
            issue("ambiguous_assertion", "Ambiguity requires human resolution.", field)
        if field not in SUPPORTED_FIELDS:
            issue("unsupported_field", "Field validation is not implemented in M1.", field)
        if value is not None:
            if (
                (field in DATE_FIELDS and type(value) is not date)
                or (field in BOOL_FIELDS and type(value) is not bool)
                or (field in TEXT_FIELDS and not isinstance(value, str))
                or (field in DOMAINS and value not in DOMAINS[field])
            ):
                issue("invalid_field_value", "Value violates the field contract.", field)
            if isinstance(value, str) and (
                not value.strip()
                or "\u0000" in value
                or value.strip().casefold() in {"n/a", "não informado"}
            ):
                issue("invalid_text", "Placeholders and NUL are not canonical values.", field)
        if assertion.value is None:
            continue
        if not assertion.evidence:
            issue(
                "missing_evidence",
                "Every non-null assertion needs verifiable evidence.",
                assertion.field,
            )
        for evidence in assertion.evidence:
            if (
                candidate.unit is None
                or evidence.unit != candidate.unit
                or evidence.snapshot_id != candidate.unit.snapshot_id
            ):
                issue("evidence_scope_mismatch", "Evidence is outside the candidate unit.", field)
            else:
                token = field.replace("~", "~0").replace("/", "~1")
                expected = candidate.unit.pointer + "/" + token
                if evidence.semantic_role != field or evidence.pointer != expected:
                    issue(
                        "evidence_role_mismatch",
                        "Role must match the direct structural field, not an unrelated scalar.",
                        field,
                    )
            supporting_snapshot = snapshots_by_id.get(evidence.snapshot_id)
            if type(assertion.value) is bool:
                claimed_text = json.dumps(assertion.value)
            elif type(assertion.value) is date:
                claimed_text = assertion.value.isoformat()
            else:
                claimed_text = str(assertion.value)
            if (
                supporting_snapshot is None
                or supporting_snapshot.source_id != candidate.source_id
                or supporting_snapshot.source_code != candidate.source_code
                or not evidence_matches(
                    evidence, payloads.get(evidence.snapshot_id), claimed_text=claimed_text
                )
            ):
                issue(
                    "unverifiable_evidence",
                    "Evidence context, method or quote is invalid.",
                    assertion.field,
                )

    for field in sorted(values):
        alternatives = known_by_field[field]
        if len(alternatives) > 1 and field != "area":
            issue(
                "conflicting_assertions", "Conflicting values require explicit resolution.", field
            )

    kind = values.get("content_kind")
    if kind in NON_OPPORTUNITIES and (
        values.get("specific_instrument") is True or values.get("actionable") is True
    ):
        issue(
            "conflicting_intent",
            "Non-opportunity kind contradicts instrument claims.",
            fields=("content_kind", "specific_instrument", "actionable"),
        )
    if kind in NON_OPPORTUNITIES:
        decision = ValidationDecision.REVIEW
        if not issues:
            issue(
                "non_opportunity",
                "Content is not an independent actionable instrument.",
                fields=("content_kind", "specific_instrument", "actionable"),
            )
            decision = ValidationDecision.REJECTED
    else:
        title = values.get("title")
        if not isinstance(title, str) or not title.strip():
            issue("missing_title", "An official specific title is required.", "title")
        if not valid_url(values.get("official_url")):
            issue(
                "invalid_official_url",
                "Absolute HTTP(S) URL without credentials required.",
                "official_url",
            )
        for field in ("specific_instrument", "actionable"):
            if values.get(field) is not True:
                issue("unproven_instrument", "Specificity and actionability need evidence.", field)
        if kind != "instrument":
            issue("unknown_content_kind", "Content nature is unresolved.", "content_kind")
        decision = ValidationDecision.REVIEW if issues else ValidationDecision.ACCEPTED

    deadline = values.get("submission_deadline")
    opening = values.get("opening_date")
    reason = values.get("no_deadline_reason")
    if kind == "instrument":
        if (deadline is None) == (reason is None):
            issue(
                "deadline_reason_inconsistent",
                "Deadline or explicit reason, never both, required.",
                fields=("submission_deadline", "no_deadline_reason"),
            )
        if type(deadline) is date and type(opening) is date and opening > deadline:
            issue(
                "inconsistent_dates",
                "Opening is after submission deadline.",
                fields=("opening_date", "submission_deadline"),
            )
        title = values.get("title")
        if isinstance(title, str) and title.strip().casefold() in {
            "home",
            "japanese",
            "edital",
            "chamada",
            "oportunidade",
        }:
            issue("generic_title", "Generic title does not identify an instrument.", "title")
    if decision == ValidationDecision.ACCEPTED:
        if issues:
            decision = ValidationDecision.REVIEW
        else:
            issue(
                "instrument_verified",
                "Specific actionable instrument evidenced.",
                fields=(
                    "title",
                    "official_url",
                    "content_kind",
                    "specific_instrument",
                    "actionable",
                ),
            )

    temporal = "nao_determinada"
    if (
        kind == "instrument"
        and type(deadline) is date
        and deadline < reference_date
        and not any(
            i.field == "submission_deadline" or "submission_deadline" in i.related_fields
            for i in issues
        )
    ):
        temporal = "encerrada"
    return ValidationReport(
        candidate=candidate,
        snapshots=snapshots,
        reference_date=reference_date,
        decision=decision,
        issues=tuple(issues),
        temporal_status=temporal,
        review_attestations=review_attestations,
    )
