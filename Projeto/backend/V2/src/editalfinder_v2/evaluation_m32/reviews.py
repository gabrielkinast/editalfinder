"""Explicit AI qualitative observations, never authorized human adjudication."""

import json
from collections import Counter
from typing import Any, Literal

from pydantic import Field

from .inputs import EvaluationFault, InputBundle, Strict, parse

ERROR_CODES = (
    "SEGMENTATION_OVER",
    "SEGMENTATION_UNDER",
    "SEGMENTATION_BOUNDARY",
    "NAVIGATION_CONTAMINATION",
    "RELATED_STORY_CONTAMINATION",
    "RECORD_ATTRIBUTION",
    "DOCUMENT_ATTRIBUTION",
    "MODALITY_CONFUSION",
    "FINANCIAL_ROLE_CONFUSION",
    "FINANCIAL_VALUE_ERROR",
    "TEMPORAL_ROLE_CONFUSION",
    "TEMPORAL_AVAILABILITY_INFERENCE",
    "GEOGRAPHIC_ROLE_CONFUSION",
    "ORGANIZATION_ROLE_CONFUSION",
    "FUTURE_SIGNAL_CONFUSION",
    "OPPORTUNITY_EXISTENCE_CONFUSION",
    "UNSUPPORTED_INFERENCE",
    "EVIDENCE_LOCATOR_INVALID",
    "EVIDENCE_SEMANTIC_MISMATCH",
    "EXTRACTION_OMISSION",
    "EXCESSIVE_ABSTENTION",
    "REFERENCE_AMBIGUITY",
    "REFERENCE_POSSIBLE_ERROR",
    "CONTRACT_UNSUPPORTED",
)


class ContextProof(Strict):
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    quote: str = Field(min_length=1, max_length=20000)
    page: int | None


class Observation(Strict):
    case_id: str = Field(min_length=1)
    document_id: str
    segment_id: str
    claim_kind: Literal["field", "discovery", "modality", "temporal"]
    field_index: int | None
    field_name: str | None
    expected_claim: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    quote: str = Field(min_length=1, max_length=20000)
    judgment: Literal["supported", "partial", "unsupported", "unresolved"]
    certainty: Literal[
        "confirmed_defect", "supported_observation", "strong_hypothesis", "unresolved_disagreement"
    ]
    error_codes: tuple[str, ...]
    severity: Literal["high", "medium", "low", "info"]
    rationale: str = Field(min_length=1)
    expected_behavior: str = Field(min_length=1)
    root_cause: str
    root_cause_confidence: Literal["high", "medium", "low"]
    next_action: str
    context_evidence: tuple[ContextProof, ...] = ()


class Reviews(Strict):
    schema_version: Literal["m32-semantic-reviews-v1"]
    prediction_sha256: str
    review_status: Literal["provisional"]
    reviewer_type: Literal["AI_qualitative_not_human"]
    items: tuple[Observation, ...] = Field(max_length=512)


def apply_reviews(bundle: InputBundle, result: dict[str, Any], raw: bytes) -> None:
    if len(raw) > 2 * 1024 * 1024:
        raise EvaluationFault("semantic_review_size_limit")
    reviews = Reviews.model_validate_json(json.dumps(parse(raw)))
    if reviews.prediction_sha256 != bundle.binding.prediction_sha256:
        raise EvaluationFault("semantic_review_prediction_mismatch")
    outcomes = {d.document_id: d for d in bundle.outcomes}
    seen = set()
    ids = set()
    for item in reviews.items:
        key = (item.document_id, item.segment_id, item.claim_kind, item.field_index)
        if key in seen or item.case_id in ids:
            raise EvaluationFault("duplicate_semantic_review")
        seen.add(key)
        ids.add(item.case_id)
        if any(c not in ERROR_CODES for c in item.error_codes):
            raise EvaluationFault("unsupported_error_taxonomy_code")
        if item.document_id not in outcomes:
            raise EvaluationFault("semantic_review_document_unknown")
        segment = next(
            (s for s in outcomes[item.document_id].segments if s.segment_id == item.segment_id),
            None,
        )
        if segment is None:
            raise EvaluationFault("semantic_review_segment_unknown")
        if not segment.start <= item.start < item.end <= segment.end:
            raise EvaluationFault("semantic_review_outside_segment")
        if bundle.documents[item.document_id].text[item.start : item.end] != item.quote:
            raise EvaluationFault("semantic_review_quote_mismatch")
        for proof in item.context_evidence:
            text = bundle.documents[item.document_id].text
            if (
                not 0 <= proof.start < proof.end <= len(text)
                or text[proof.start : proof.end] != proof.quote
            ):
                raise EvaluationFault("semantic_context_quote_invalid")
            is_pdf = bundle.documents[item.document_id].provenance.content_type == "application/pdf"
            if is_pdf and (
                proof.page != text[: proof.start].count("\f") + 1 or "\f" in proof.quote
            ):
                raise EvaluationFault("semantic_context_pdf_page_invalid")
            if not is_pdf and proof.page is not None:
                raise EvaluationFault("semantic_context_html_page_invalid")
        if item.claim_kind == "field":
            if item.field_index is None or not 0 <= item.field_index < len(segment.fields):
                raise EvaluationFault("semantic_review_field_unknown")
            field = segment.fields[item.field_index]
            if (item.expected_claim, item.field_name) != (field.original, field.name):
                raise EvaluationFault("semantic_review_claim_mismatch")
            w = field.witness
            if (item.start, item.end, item.quote) != (w.start, w.end, w.quote):
                raise EvaluationFault("semantic_review_not_actual_witness")
        elif (
            item.field_index is not None
            or item.field_name is not None
            or item.expected_claim != getattr(segment, item.claim_kind)
        ):
            raise EvaluationFault("semantic_review_claim_mismatch")
    by_field = {
        (i.document_id, i.segment_id, i.field_index): i
        for i in reviews.items
        if i.claim_kind == "field"
    }
    for claim in result["extracted_claims"]:
        reviewed_item = by_field.get(
            (claim["document_id"], claim["segment_id"], claim["field_index"])
        )
        if reviewed_item is not None:
            claim["semantic_support"] = reviewed_item.judgment
            claim["semantic_case_id"] = reviewed_item.case_id
    result["semantic_evidence"] = dict(
        reviewed_claims=len(reviews.items),
        reviewed_field_claims=len(by_field),
        reviewed_nonfield_claims=len(reviews.items) - len(by_field),
        unreviewed_field_claims=len(result["extracted_claims"]) - len(by_field),
        judgments=dict(Counter(i.judgment for i in reviews.items)),
        field_judgments=dict(Counter(i.judgment for i in reviews.items if i.claim_kind == "field")),
        review_status="provisional",
        selection="purposeful error-focused, not representative",
        cases=[i.model_dump(mode="json") for i in reviews.items],
    )
