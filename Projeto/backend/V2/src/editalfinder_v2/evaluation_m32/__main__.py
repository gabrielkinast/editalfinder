"""Offline evaluator CLI. Read frozen inputs; create separate diagnostics only."""

import argparse
import json
import resource
from pathlib import Path
from time import perf_counter
from typing import Any

from .engine import evaluate
from .inputs import EvaluationFault, bounded, digest
from .reporting import diagnostics


def encode(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode()


def emit(root: Path, frozen: Path, binding: Path, output: Path, reviews: Path | None) -> int:
    output = output.resolve()
    repository = Path(__file__).parents[3]
    protected = (root.resolve(), frozen.resolve(), repository / "data/m3", repository / "data/m31")
    if any(output.is_relative_to(p.resolve()) for p in protected):
        raise EvaluationFault("output_overlaps_frozen_input")
    if output.exists() and any(
        (output / p).exists()
        for p in (
            "evaluation_results.json",
            "error_cases.json",
            "review_queue.json",
            "performance.json",
            "freeze.json",
            "per_document",
        )
    ):
        raise EvaluationFault("evaluation_output_already_exists")
    result, timing = evaluate(
        root,
        frozen,
        bounded(binding, 65536),
        semantic_reviews_raw=bounded(reviews, 2 * 1024 * 1024) if reviews else None,
    )
    output.mkdir(parents=True, exist_ok=True)
    raw = encode(result)
    with (output / "evaluation_results.json").open("xb") as stream:
        stream.write(raw)
    if result["status"] != "evaluated":
        print(json.dumps(result, ensure_ascii=False))
        return 2
    t = perf_counter()
    body = result["results"]
    errors, queue = diagnostics(body)
    artifacts = {"error_cases.json": encode(errors), "review_queue.json": encode(queue)}
    for doc in body["per_document"]:
        doc = dict(
            doc,
            extracted_claims=[
                f for f in body["extracted_claims"] if f["document_id"] == doc["document_id"]
            ],
            semantic_reviews=[
                c
                for c in body["semantic_evidence"].get("cases", [])
                if c["document_id"] == doc["document_id"]
            ],
            error_cases=[c for c in errors["cases"] if c["document_id"] == doc["document_id"]],
        )
        # Arbitrary IDs never become filenames; ordinal plus restricted ID transport.
        index = next(
            i for i, d in enumerate(body["per_document"]) if d["document_id"] == doc["document_id"]
        )
        name = f"per_document/document-{index:03d}.json"
        artifacts[name] = encode(doc)
    timing.update(
        diagnostic_assembly_and_serialization_seconds=perf_counter() - t,
        evaluation_result_bytes=len(raw),
        diagnostic_bytes=sum(len(v) for v in artifacts.values()),
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        rss_scope=(
            "Linux whole-process high-water mark, interpreter/imports included; not hard memory cap"
        ),
    )
    for name, payload in artifacts.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(payload)
    with (output / "performance.json").open("xb") as stream:
        stream.write(encode(timing))
    frozen_receipt = dict(
        schema_version="m32-freeze-v1",
        evaluation_result_sha256=digest(raw),
        binding_sha256=digest(bounded(binding, 65536)),
        semantic_reviews_sha256=digest(bounded(reviews, 2 * 1024 * 1024)) if reviews else None,
        prediction_sha256=body["binding"]["prediction_sha256"],
        code_sha256={
            p.name: digest(p.read_bytes()) for p in sorted(Path(__file__).parent.glob("*.py"))
        },
        artifact_sha256={name: digest(payload) for name, payload in artifacts.items()},
    )
    with (output / "freeze.json").open("xb") as stream:
        stream.write(encode(frozen_receipt))
    print(
        json.dumps(
            dict(
                status="evaluated",
                documents=body["processing"]["documents"],
                references=len(body["records"]),
                field_slots=body["field_summary"]["denominator"],
                result_sha256=digest(raw),
            )
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="M3.2 offline exploratory evaluation only")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("predictions", type=Path)
    parser.add_argument("binding", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--semantic-reviews", type=Path)
    args = parser.parse_args()
    try:
        return emit(
            args.dataset, args.predictions, args.binding, args.output, args.semantic_reviews
        )
    except (EvaluationFault, OSError, ValueError) as exc:
        print(
            json.dumps(
                dict(
                    status="operational_failure",
                    code=exc.code if isinstance(exc, EvaluationFault) else type(exc).__name__,
                )
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
