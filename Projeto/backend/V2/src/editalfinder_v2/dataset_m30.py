"""Offline M3 pilot transport schema, deliberately independent of domain contracts.

Offsets are Unicode codepoints in frozen UTF-8 text, never byte offsets. Validation
checks integrity and explicit annotation consistency, not semantic truth or extraction.
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator


def nonblank(value: str) -> str:
    if not value.strip():
        raise ValueError("Text must not be blank")
    value.encode("utf-8")
    return value


def iso_date(value: str) -> str:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise ValueError("Date must be ISO YYYY-MM-DD")
    date.fromisoformat(value)
    return value


def utc_datetime(value: str) -> str:
    if not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
        r"(?:\.[0-9]+)?(?:Z|\+00:00)",
        value,
    ):
        raise ValueError("retrieved_at must be an aware UTC ISO timestamp")
    parsed = datetime.fromisoformat(value)
    if parsed.utcoffset() != timedelta(0):
        raise ValueError("retrieved_at must be UTC")
    return value


def public_https_locator(value: str) -> str:
    """Pilot provenance syntax policy only; no DNS, officiality or identity inference."""
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.port not in (None, 443)
        or any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value)
    ):
        raise ValueError("Pilot provenance requires absolute HTTPS without credentials or controls")
    return value


Text = Annotated[str, Field(min_length=1), AfterValidator(nonblank)]
SourceURL = Annotated[Text, AfterValidator(public_https_locator)]
ISODate = Annotated[str, AfterValidator(iso_date)]
UTCTimestamp = Annotated[str, AfterValidator(utc_datetime)]
Digest = Annotated[str, Field(pattern=r"^[0-9a-fA-F]{64}$")]
DatasetVersion = Literal["m3.0-pilot-v1"]
ProtocolVersion = Literal["m3.0-annotation-v1"]


class DatasetModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", allow_inf_nan=False)


class Document(DatasetModel):
    document_id: Text
    original_url: SourceURL
    final_url: SourceURL
    source_organization: Text
    retrieved_at: UTCTimestamp
    original_filename: Text
    content_type: Literal["text/html", "application/pdf"]
    byte_length: Annotated[int, Field(gt=0, le=5 * 1024 * 1024)]
    sha256: Digest
    raw_path: Text
    text_path: Text
    text_sha256: Digest
    publication_date: ISODate | None
    document_version: Text | None
    source_authority_notes: Text
    retrieval_status: Literal["acquired"]
    restrictions: Text
    document_category: Literal[
        "application_call",
        "financing_program",
        "investment_program",
        "institutional_news",
        "selection_result",
        "program_information",
        "rectification",
        "other_document",
    ]
    category_evidence: Text
    derivation_method: Text


class Manifest(DatasetModel):
    dataset_version: DatasetVersion
    protocol_version: ProtocolVersion
    reference_date: ISODate
    documents: list[Document]


class Span(DatasetModel):
    start: Annotated[int, Field(ge=0)]
    end: Annotated[int, Field(gt=0)]

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.end <= self.start:
            raise ValueError("Span must be nonempty and ordered")
        return self


class Evidence(Span):
    evidence_id: Text
    quote: Text
    page: Annotated[int, Field(gt=0)] | None


class AnnotatedField(DatasetModel):
    value: Text
    evidence_ids: Annotated[list[Text], Field(min_length=1)]


class Record(DatasetModel):
    annotation_id: Text
    record_id: Text
    document_id: Text
    unit_locator: Span
    discovery_label: Literal[
        "confirmed_opportunity",
        "announced_future_opportunity",
        "opportunity_signal",
        "unrelated_or_non_actionable",
    ]
    opportunity_label: Literal["genuine_opportunity", "not_opportunity", "uncertain"]
    temporal_status: Literal[
        "open", "closed", "future", "continuous", "undetermined", "not_applicable"
    ]
    reference_date: ISODate
    modality: Literal["fomento", "credito", "investimentos", "undetermined"]
    review_status: Literal["provisional", "independently_reviewed", "disputed", "approved"]
    annotation_method: Literal["AI-assisted source reading; no model predictions"]
    protocol_version: ProtocolVersion
    rationale: Text
    uncertainty_notes: list[Text]
    evidence: Annotated[list[Evidence], Field(min_length=1)]
    label_evidence: dict[str, Annotated[list[Text], Field(min_length=1)]]
    fields: dict[str, AnnotatedField]

    @model_validator(mode="after")
    def pilot_rules(self) -> Self:
        if self.review_status != "provisional":
            raise ValueError("Pilot has no authorized review object; only provisional is accepted")
        required = {"discovery_label", "opportunity_label", "temporal_status", "modality"}
        if not required.issubset(self.label_evidence):
            raise ValueError("All four labels require explicit evidence links")
        if self.discovery_label == "confirmed_opportunity":
            if self.opportunity_label != "genuine_opportunity":
                raise ValueError("Confirmed discovery requires genuine_opportunity")
        if self.temporal_status == "not_applicable" and self.opportunity_label != "not_opportunity":
            raise ValueError("not_applicable is reserved for non-opportunity records")
        if self.opportunity_label == "genuine_opportunity":
            if self.discovery_label != "confirmed_opportunity":
                raise ValueError("Genuine opportunity requires confirmed discovery")
        if self.discovery_label in {"announced_future_opportunity", "opportunity_signal"}:
            if self.opportunity_label != "uncertain":
                raise ValueError("Announcements and signals must remain uncertain")
            if self.temporal_status in {"open", "continuous"}:
                raise ValueError("Announcements and signals cannot be open or continuous")
        if self.discovery_label == "unrelated_or_non_actionable":
            if self.opportunity_label != "not_opportunity":
                raise ValueError("Unrelated discovery requires not_opportunity")
        if self.opportunity_label == "not_opportunity" and self.temporal_status != "not_applicable":
            raise ValueError("Negative opportunities require not_applicable temporal status")
        if (
            self.discovery_label == "confirmed_opportunity"
            and self.temporal_status == "not_applicable"
        ):
            raise ValueError("Confirmed discovery cannot have not_applicable temporal status")
        unique_ids([item.evidence_id for item in self.evidence], "evidence_id")
        evidence = {item.evidence_id: item for item in self.evidence}
        for links in self.label_evidence.values():
            if any(link not in evidence for link in links):
                raise ValueError("Unknown label evidence reference")
        for field in self.fields.values():
            if any(link not in evidence for link in field.evidence_ids):
                raise ValueError("Unknown field evidence reference")
            if not any(field.value in evidence[link].quote for link in field.evidence_ids):
                raise ValueError("Field value must appear verbatim in a referenced quote")
        return self


class Annotations(DatasetModel):
    dataset_version: DatasetVersion
    protocol_version: ProtocolVersion
    records: list[Record]


MAX_RAW_BYTES = 5 * 1024 * 1024
MAX_TEXT_BYTES = 16 * 1024 * 1024
MAX_JSON_BYTES = 16 * 1024 * 1024


def read_bounded(root: Path, name: str, limit: int) -> bytes:
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"Path must be relative and contained in dataset root: {name}")
    try:
        path = (root / relative).resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Not a contained regular file: {name}")
        with path.open("rb") as stream:
            data = stream.read(limit + 1)
        if len(data) > limit:
            raise ValueError(f"File exceeds {limit} bytes: {name}")
        return data
    except (OSError, RuntimeError) as exc:
        raise ValueError(f"Cannot read dataset file {name}: {exc}") from exc


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> object:
    raise ValueError(f"Nonfinite JSON number: {value}")


def read_json(root: Path, name: str) -> object:
    try:
        return json.loads(
            read_bounded(root, name, MAX_JSON_BYTES).decode("utf-8"),
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
        )
    except (UnicodeError, RecursionError) as exc:
        raise ValueError(f"Invalid UTF-8 JSON: {name}") from exc


def document_text(root: Path, document: Document) -> str:
    raw = read_bounded(root, document.raw_path, MAX_RAW_BYTES)
    if len(raw) != document.byte_length:
        raise ValueError(f"Raw byte length mismatch: {document.document_id}")
    if hashlib.sha256(raw).hexdigest() != document.sha256.lower():
        raise ValueError(f"Raw SHA256 mismatch: {document.document_id}")
    if document.content_type == "application/pdf":
        signature_ok = raw.startswith(b"%PDF-")
    else:
        signature_ok = re.search(rb"<!doctype\s+html\b|<html(?:\s|>)", raw, re.I) is not None
    if not signature_ok:
        raise ValueError(f"Raw signature/content type mismatch: {document.document_id}")
    frozen = read_bounded(root, document.text_path, MAX_TEXT_BYTES)
    if hashlib.sha256(frozen).hexdigest() != document.text_sha256.lower():
        raise ValueError(f"Text SHA256 mismatch: {document.document_id}")
    try:
        text = frozen.decode("utf-8")
    except UnicodeError as exc:
        raise ValueError(f"Derived text is not UTF-8: {document.document_id}") from exc
    if document.category_evidence not in text:
        raise ValueError(f"Category evidence absent from text: {document.document_id}")
    return text


def unique_ids(values: list[str], kind: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {kind}")


def validate_spans(record: Record, document: Document, text: str) -> None:
    unit = record.unit_locator
    if unit.end > len(text):
        raise ValueError(f"Unit extends beyond derived text: {record.record_id}")
    pages: list[tuple[int, int]] = []
    start = 0
    for page in text.split("\f"):
        pages.append((start, start + len(page)))
        start += len(page) + 1
    for evidence in record.evidence:
        if not unit.start <= evidence.start < evidence.end <= unit.end:
            raise ValueError(f"Evidence outside unit: {record.record_id}/{evidence.evidence_id}")
        if text[evidence.start : evidence.end] != evidence.quote:
            raise ValueError(f"Evidence quote mismatch: {record.record_id}/{evidence.evidence_id}")
        if document.content_type == "text/html":
            if evidence.page is not None:
                raise ValueError("HTML evidence page must be null")
        else:
            if evidence.page is None or evidence.page > len(pages):
                raise ValueError("PDF evidence requires a valid page number")
            page_start, page_end = pages[evidence.page - 1]
            if not page_start <= evidence.start < evidence.end <= page_end:
                raise ValueError("PDF evidence span must be contained in its specified page")


def load_and_validate(root: Path) -> tuple[Manifest, Annotations]:
    """Load bounded local inputs; raise ValueError on schema or integrity failure.

    No extraction, network, domain conversion, or semantic label inference occurs.
    An unknown deadline does not establish continuous availability: annotators must
    justify that label with source evidence under the annotation protocol.
    """
    root = root.resolve()
    manifest = Manifest.model_validate(read_json(root, "corpus_manifest.json"))
    annotations = Annotations.model_validate(read_json(root, "annotations/records.json"))
    unique_ids([doc.document_id for doc in manifest.documents], "document_id")
    unique_ids([record.record_id for record in annotations.records], "record_id")
    unique_ids([record.annotation_id for record in annotations.records], "annotation_id")
    documents = {doc.document_id: doc for doc in manifest.documents}
    texts = {doc.document_id: document_text(root, doc) for doc in manifest.documents}
    for record in annotations.records:
        if record.document_id not in documents:
            raise ValueError(f"Unknown document reference: {record.document_id}")
        if record.reference_date != manifest.reference_date:
            raise ValueError(f"Reference date differs from manifest: {record.record_id}")
        validate_spans(record, documents[record.document_id], texts[record.document_id])
    return manifest, annotations


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify the offline M3 pilot dataset")
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    try:
        manifest, annotations = load_and_validate(args.root)
    except ValueError as exc:
        print(f"Dataset validation failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"Validated {len(manifest.documents)} documents and {len(annotations.records)} records "
        f"({manifest.dataset_version}; {manifest.protocol_version})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
