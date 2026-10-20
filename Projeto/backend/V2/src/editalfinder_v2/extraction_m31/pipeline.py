"""Offline orchestration; no reference annotation access, domain calls or writes."""

from .models import DocumentOutcome
from .reader import InputDocument
from .rules import predict
from .structure import segment


def verify_evidence(document: InputDocument, result: DocumentOutcome) -> None:
    """External-input boundary; substring validity is not semantic certification."""
    if result.provenance != document.provenance:
        raise ValueError("input_provenance_mismatch")
    expected = segment(document)
    if [(s.segment_id, s.start, s.end) for s in result.segments] != [
        (f"segment-{i:04d}", unit.start, unit.end) for i, unit in enumerate(expected)
    ]:
        raise ValueError("segment_structure_mismatch")
    for unit, reconstructed in zip(result.segments, expected, strict=True):
        if unit.end > len(document.text):
            raise ValueError("segment_out_of_bounds")
        for w in unit.witnesses + tuple(f.witness for f in unit.fields):
            if document.text[w.start : w.end] != w.quote:
                raise ValueError("evidence_quote_mismatch")
            admitted = any(
                not b.excluded and b.start <= w.start < w.end <= b.end for b in reconstructed.blocks
            )
            if not admitted:
                raise ValueError("evidence_in_excluded_or_foreign_block")
            if document.provenance.content_type == "application/pdf":
                page = document.text[: w.start].count("\f") + 1
                if w.page != page or "\f" in w.quote:
                    raise ValueError("invalid_physical_pdf_page")
            elif w.page is not None:
                raise ValueError("html_page_must_be_null")


def extract_document(document: InputDocument, run_id: str, reference_date: str) -> DocumentOutcome:
    units = segment(document)
    predictions = tuple(
        predict(document, unit, run_id, i, reference_date) for i, unit in enumerate(units)
    )
    result = DocumentOutcome(
        run_id=run_id,
        document_id=document.provenance.document_id,
        provenance=document.provenance,
        status="processed",
        segments=predictions,
        diagnostics=document.limitations,
        reference_date=reference_date,
    )
    verify_evidence(document, result)
    return result
