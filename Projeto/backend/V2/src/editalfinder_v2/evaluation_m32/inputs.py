"""Bounded immutable-artifact input boundary. Hashes are not authentication."""

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from ..dataset_m30 import Annotations, Manifest, load_and_validate
from ..extraction_m31.models import DocumentOutcome
from ..extraction_m31.pipeline import verify_evidence
from ..extraction_m31.reader import InputDocument, read_document


class EvaluationFault(ValueError):
    def __init__(self, code: str, location: str = "") -> None:
        self.code, self.location = code, location
        super().__init__(code)


class Strict(BaseModel):
    model_config = ConfigDict(
        extra="forbid", frozen=True, strict=True, allow_inf_nan=False, hide_input_in_errors=True
    )


class Binding(Strict):
    schema_version: Literal["m32-binding-v1"]
    dataset_version: Literal["m3.0-pilot-v1"]
    protocol_version: Literal["m3.0-annotation-v1"]
    reference_date: str
    prediction_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    annotation_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    expected_document_ids: tuple[str, ...]
    expected_record_ids: tuple[str, ...]


class Receipt(Strict):
    prediction_sha256: str
    input_manifest_sha256: str
    run_id: str
    reference_date: str
    method_version: Literal["m31-deterministic-v2"]
    code_sha256: dict[str, str]
    label_access_during_inference: Literal[False]


class Envelope(Strict):
    schema_version: Literal["m31-run-v1"]
    method_version: Literal["m31-deterministic-v2"]
    reference_date: str
    documents: tuple[DocumentOutcome, ...]


@dataclass(frozen=True)
class InputBundle:
    binding: Binding
    manifest: Manifest
    annotations: Annotations
    outcomes: tuple[DocumentOutcome, ...]
    documents: dict[str, InputDocument]
    locator_occurrences: int
    unique_locators: int
    evidence_timings: dict[str, dict[str, float]]


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def bounded(path: Path, limit: int) -> bytes:
    try:
        with path.open("rb") as stream:
            raw = stream.read(limit + 1)
    except OSError as exc:
        raise EvaluationFault("missing_or_unreadable_artifact", path.name) from exc
    if len(raw) > limit:
        raise EvaluationFault("input_size_limit", path.name)
    return raw


def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise EvaluationFault("duplicate_json_member", key)
        result[key] = value
    return result


def finite(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise EvaluationFault("nonfinite_json_number")
    return result


def reject(value: str) -> None:
    raise EvaluationFault("nonfinite_json_number")


def parse(raw: bytes) -> Any:
    return json.loads(raw, object_pairs_hook=pairs, parse_float=finite, parse_constant=reject)


def load_bundle(root: Path, frozen: Path, binding: Binding) -> InputBundle:
    root, frozen = root.resolve(), frozen.resolve()
    manifest_raw = bounded(root / "corpus_manifest.json", 1024 * 1024)
    annotation_raw = bounded(root / "annotations/records.json", 1024 * 1024)
    raw = bounded(frozen / "predictions.json", 32 * 1024 * 1024)
    receipt = Receipt.model_validate_json(json.dumps(parse(bounded(frozen / "freeze.json", 65536))))
    # Parse with duplicate/nonfinite rejection BEFORE Pydantic JSON transport conversion.
    m, a, p = parse(manifest_raw), parse(annotation_raw), parse(raw)
    if digest(raw) != receipt.prediction_sha256 or digest(raw) != binding.prediction_sha256:
        raise EvaluationFault("prediction_hash_mismatch")
    if (
        digest(manifest_raw) != receipt.input_manifest_sha256
        or digest(manifest_raw) != binding.manifest_sha256
    ):
        raise EvaluationFault("manifest_hash_mismatch")
    if digest(annotation_raw) != binding.annotation_sha256:
        raise EvaluationFault("annotation_hash_mismatch")
    if (
        m["dataset_version"],
        m["protocol_version"],
        a["dataset_version"],
        a["protocol_version"],
    ) != (
        binding.dataset_version,
        binding.protocol_version,
        binding.dataset_version,
        binding.protocol_version,
    ):
        raise EvaluationFault("dataset_or_annotation_version_mismatch")
    if not 0 < len(m["documents"]) <= 64 or len(a["records"]) > 256:
        raise EvaluationFault("evaluation_work_limit")
    if len(binding.expected_document_ids) != len(set(binding.expected_document_ids)) or len(
        binding.expected_record_ids
    ) != len(set(binding.expected_record_ids)):
        raise EvaluationFault("duplicate_binding_id")
    if tuple(d["document_id"] for d in m["documents"]) != binding.expected_document_ids:
        raise EvaluationFault("manifest_document_set_mismatch")
    if tuple(r["record_id"] for r in a["records"]) != binding.expected_record_ids:
        raise EvaluationFault("reference_set_mismatch")
    # The approved dataset verifier remains the authority for annotations/spans.
    manifest, annotations = load_and_validate(root)
    for doc in manifest.documents:
        bounded(root / doc.text_path, 1024 * 1024)
    envelope = Envelope.model_validate_json(json.dumps(p))
    for received in p["documents"]:
        versioned = [(received, True)]
        for unit in received["segments"]:
            versioned.append((unit, True))
            versioned.extend((w, False) for w in unit["witnesses"])
            for field in unit["fields"]:
                versioned.extend(((field, True), (field["witness"], False)))
        for node, has_method in versioned:
            if node.get("schema_version") != "m31-extraction-v1" or (
                has_method and node.get("method_version") != "m31-deterministic-v2"
            ):
                raise EvaluationFault("missing_or_unsupported_nested_version")
    if tuple(d.document_id for d in envelope.documents) != binding.expected_document_ids:
        raise EvaluationFault("missing_duplicate_or_wrong_prediction_document")
    if not (
        envelope.reference_date
        == manifest.reference_date
        == binding.reference_date
        == receipt.reference_date
    ):
        raise EvaluationFault("reference_date_mismatch")
    code_root = Path(__file__).parents[1] / "extraction_m31"
    expected_code = {p.name: digest(p.read_bytes()) for p in code_root.glob("*.py")}
    if receipt.code_sha256 != expected_code:
        raise EvaluationFault("extractor_code_mismatch")
    documents: dict[str, InputDocument] = {}
    timings: dict[str, dict[str, float]] = {}
    locators = set()
    count = 0
    for result, meta in zip(envelope.documents, manifest.documents, strict=True):
        if result.run_id != receipt.run_id or result.reference_date != binding.reference_date:
            raise EvaluationFault("prediction_context_mismatch", result.document_id)
        if len(result.segments) > 3000:
            raise EvaluationFault("segment_work_limit", result.document_id)
        t = perf_counter()
        document = read_document(root, meta.model_dump())
        u = perf_counter()
        documents[result.document_id] = document
        if result.status == "processed":
            try:
                verify_evidence(document, result)
            except ValueError as exc:
                raise EvaluationFault(
                    "evidence_or_structure_invalid", result.document_id + ":" + str(exc)
                ) from exc
        timings[result.document_id] = dict(read_seconds=u - t, evidence_seconds=perf_counter() - u)
        for segment in result.segments:
            for w in segment.witnesses + tuple(f.witness for f in segment.fields):
                count += 1
                locators.add((w.document_id, w.segment_id, w.start, w.end, w.page, w.quote))
    return InputBundle(
        binding, manifest, annotations, envelope.documents, documents, count, len(locators), timings
    )
