"""Batch inference from local manifest/raw/text only. No label module imports."""

import hashlib
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from pydantic import ValidationError

from .models import VERSION, DocumentOutcome
from .pipeline import verify_evidence
from .reader import InputFailure, read_document
from .rules import predict
from .structure import segment

# Categories, category evidence, publication dates, organization labels and
# annotation fields are deliberately discarded BEFORE entering the reader.
INPUT_KEYS = (
    "document_id",
    "original_url",
    "content_type",
    "raw_path",
    "text_path",
    "sha256",
    "text_sha256",
    "byte_length",
    "derivation_method",
)


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputFailure("duplicate_json_member")
        result[key] = value
    return result


def run(
    root: Path, reference_date: str
) -> tuple[tuple[DocumentOutcome, ...], list[dict[str, Any]]]:
    """Stable prediction ID from config/code and allowed inputs; timings separate."""
    from datetime import date

    if date.fromisoformat(reference_date).isoformat() != reference_date:
        raise InputFailure("invalid_reference_date")
    with (root / "corpus_manifest.json").open("rb") as stream:
        raw = stream.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise InputFailure("manifest_size_limit")
    manifest = json.loads(raw, object_pairs_hook=strict_pairs)
    entries = manifest["documents"]
    if not isinstance(entries, list) or len(entries) > 64:
        raise InputFailure("manifest_document_limit")
    ids = [e["document_id"] for e in entries]
    if len(set(ids)) != len(ids):
        raise InputFailure("duplicate_document_id")
    inputs = [{key: e.get(key) for key in INPUT_KEYS} for e in entries]
    code = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(Path(__file__).parent.glob("*.py"))
        if p.name != "evaluate.py"
    }
    config = dict(method=VERSION, reference_date=reference_date, inputs=inputs, code=code)
    run_id = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()
    results: list[DocumentOutcome] = []
    timings: list[dict[str, Any]] = []
    for meta in inputs:
        start = perf_counter()
        timing: dict[str, Any] = dict(
            document_id=meta["document_id"],
            read_seconds=None,
            segmentation_seconds=None,
            extraction_seconds=None,
            evidence_verification_seconds=None,
        )
        try:
            doc = read_document(root, meta)
            t = perf_counter()
            timing["read_seconds"] = t - start
            units = segment(doc)
            u = perf_counter()
            timing["segmentation_seconds"] = u - t
            predictions = tuple(
                predict(doc, unit, run_id, i, reference_date) for i, unit in enumerate(units)
            )
            result = DocumentOutcome(
                run_id=run_id,
                document_id=doc.provenance.document_id,
                provenance=doc.provenance,
                status="processed",
                segments=predictions,
                diagnostics=doc.limitations,
                reference_date=reference_date,
            )
            v = perf_counter()
            timing["extraction_seconds"] = v - u
            verify_evidence(doc, result)
            timing["evidence_verification_seconds"] = perf_counter() - v
        except (InputFailure, OSError, UnicodeError, KeyError, TypeError, ValidationError) as exc:
            code_name = str(exc) if isinstance(exc, InputFailure) else type(exc).__name__
            result = DocumentOutcome(
                run_id=run_id,
                document_id=str(meta["document_id"]),
                provenance=None,
                status="operational_failure",
                segments=(),
                diagnostics=(code_name,),
                reference_date=reference_date,
            )
        timing["total_seconds"] = perf_counter() - start
        timing["segments"] = len(result.segments)
        timing["fields"] = sum(len(s.fields) for s in result.segments)
        timing["input_metadata"] = meta
        results.append(result)
        timings.append(timing)
    return tuple(results), timings
