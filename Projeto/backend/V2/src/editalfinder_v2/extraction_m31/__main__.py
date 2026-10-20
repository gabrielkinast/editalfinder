"""Explicit two-step CLI: freeze predictions, then compare provisional references."""

import argparse
import hashlib
import json
import resource
from pathlib import Path
from typing import Any

from .models import VERSION, DocumentOutcome
from .reader import InputFailure, read_document
from .run import run


def save_new(path: Path, value: Any) -> None:
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def read_prediction(path: Path, *, limit: int = 32 * 1024 * 1024) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise InputFailure("prediction_transport_limit")
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded experimental offline extraction")
    subs = parser.add_subparsers(dest="action", required=True)
    for action in ("predict", "evaluate"):
        sub = subs.add_parser(action)
        sub.add_argument("root", type=Path)
        sub.add_argument("output", type=Path)
        if action == "predict":
            sub.add_argument("--reference-date", required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    if output.is_relative_to(root):
        parser.error("output must be outside frozen input root")
    if args.action == "predict":
        # New run directories only. Never replace an existing frozen prediction.
        output.mkdir(parents=True, exist_ok=False)
        results, timings = run(root, args.reference_date)
        body = dict(
            schema_version="m31-run-v1",
            method_version=VERSION,
            reference_date=args.reference_date,
            documents=[r.model_dump(mode="json") for r in results],
        )
        save_new(output / "predictions.json", body)
        digest = hashlib.sha256((output / "predictions.json").read_bytes()).hexdigest()
        save_new(
            output / "freeze.json",
            dict(
                prediction_sha256=digest,
                input_manifest_sha256=hashlib.sha256(
                    (root / "corpus_manifest.json").read_bytes()
                ).hexdigest(),
                run_id=results[0].run_id if results else None,
                reference_date=args.reference_date,
                method_version=VERSION,
                code_sha256={
                    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in sorted(Path(__file__).parent.glob("*.py"))
                },
                label_access_during_inference=False,
            ),
        )
        save_new(
            output / "performance.json",
            dict(
                documents=timings,
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                rss_scope=(
                    "Linux process high-water mark including interpreter and imports; "
                    "not per-document allocation"
                ),
                prediction_bytes=(output / "predictions.json").stat().st_size,
            ),
        )
        print(
            json.dumps(
                dict(
                    documents=len(results),
                    segments=sum(len(r.segments) for r in results),
                    failures=sum(r.status == "operational_failure" for r in results),
                    prediction_sha256=digest,
                )
            )
        )
    else:
        # These imports and label reads occur ONLY after frozen prediction hash
        # verification. The prediction engine has no import edge to this evaluator.
        from ..dataset_m30 import load_and_validate
        from .evaluate import compare
        from .pipeline import verify_evidence

        raw = read_prediction(output / "predictions.json")
        receipt = json.loads((output / "freeze.json").read_bytes())
        digest = hashlib.sha256(raw).hexdigest()
        if receipt["prediction_sha256"] != digest:
            raise InputFailure("frozen_prediction_hash_mismatch")
        manifest, annotations = load_and_validate(root)
        if (
            receipt["input_manifest_sha256"]
            != hashlib.sha256((root / "corpus_manifest.json").read_bytes()).hexdigest()
        ):
            raise InputFailure("evaluation_manifest_mismatch")
        body = json.loads(raw)
        if body["schema_version"] != "m31-run-v1" or body["method_version"] != VERSION:
            raise InputFailure("prediction_version_mismatch")
        if body["reference_date"] != manifest.reference_date:
            raise InputFailure("prediction_reference_date_mismatch")
        results = tuple(
            DocumentOutcome.model_validate_json(json.dumps(r)) for r in body["documents"]
        )
        if [r.document_id for r in results] != [d.document_id for d in manifest.documents]:
            raise InputFailure("missing_duplicate_or_reordered_document_outcomes")
        for result, meta in zip(results, manifest.documents, strict=True):
            if (
                result.reference_date != manifest.reference_date
                or result.run_id != receipt["run_id"]
            ):
                raise InputFailure("prediction_run_context_mismatch")
            if result.status == "processed":
                verify_evidence(read_document(root, meta.model_dump()), result)
        report = compare(results, [r.model_dump() for r in annotations.records])
        report.update(
            prediction_sha256=digest,
            annotation_sha256=hashlib.sha256(
                (root / "annotations/records.json").read_bytes()
            ).hexdigest(),
            input_manifest_sha256=receipt["input_manifest_sha256"],
            reference_date=manifest.reference_date,
            evidence_locator_verification=(
                "PASS for all processed documents; not semantic entailment"
            ),
        )
        save_new(output / "evaluation.json", report)
        print(
            json.dumps(
                {
                    k: v
                    for k, v in report.items()
                    if k
                    in {
                        "status",
                        "reference_records",
                        "predicted_segments",
                        "fields",
                        "operational_failures",
                    }
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
