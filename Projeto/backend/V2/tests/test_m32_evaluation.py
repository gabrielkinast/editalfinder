"""Evaluation tests use explicit expected geometry and semantic counterexamples."""

import pytest


def test_alignment_preserves_many_to_many_and_document_boundaries() -> None:
    from editalfinder_v2.evaluation_m32.alignment import Located, align

    refs = (Located("a", "r1", 0, 10), Located("a", "r2", 10, 20), Located("b", "r3", 0, 10))
    preds = (Located("a", "s1", 0, 15), Located("a", "s2", 5, 10))
    rows = align(refs, preds)
    assert rows[0]["covered_characters"] == 10
    assert rows[0]["fragmentation"] == 2
    assert rows[0]["edges"][0]["iou"] == 10 / 15
    assert rows[0]["edges"][0]["predicted_purity"] == 10 / 15
    assert rows[0]["representative"] == "s1"
    assert rows[1]["edges"][0]["intersection"] == 5
    assert rows[2]["covered_characters"] == 0
    assert rows[2]["representative"] is None


def test_zero_subsets_and_duplicate_spans_fail_explicitly() -> None:
    from editalfinder_v2.evaluation_m32.alignment import Located, align, fraction

    assert align((), ()) == []
    assert fraction(0, 0) == {"numerator": 0, "denominator": 0, "value": None}
    with pytest.raises(ValueError, match="duplicate_location_id"):
        align((Located("a", "x", 0, 2), Located("a", "x", 2, 4)), ())
    with pytest.raises(ValueError, match="invalid_span"):
        Located("a", "x", 1, 1)


def test_frozen_bundle_validated_without_regeneration() -> None:
    from pathlib import Path

    from editalfinder_v2.evaluation_m32.inputs import Binding, load_bundle

    root = Path(__file__).resolve().parents[1]
    binding = Binding.model_validate_json((root / "data/m32/input_binding.json").read_bytes())
    bundle = load_bundle(root / "data/m3", root / "data/m31/run-v2", binding)
    assert len(bundle.outcomes) == 28
    assert len(bundle.annotations.records) == 33
    assert bundle.locator_occurrences > 332
    assert len(bundle.evidence_timings) == 28


def test_field_roles_and_ownership_are_not_lexical_equivalence() -> None:
    from editalfinder_v2.evaluation_m32.fields import compare_field

    def claim(name: str, value: str, start: int = 0) -> dict:
        return dict(
            name=name,
            original=value,
            witness=dict(start=start, end=start + len(value), quote=value),
            segment_id="s",
        )

    assert (
        compare_field(
            "submission_deadline",
            "01/01/2027",
            [claim("publication_date_expression", "01/01/2027")],
            0,
            20,
        )["status"]
        == "ROLE_ERROR"
    )
    assert (
        compare_field(
            "credit_limit",
            "R$ 10 milhões",
            [claim("fund_capital_estimate", "R$ 10 milhões")],
            0,
            30,
        )["status"]
        == "ROLE_ERROR"
    )
    assert (
        compare_field(
            "credit_limit",
            "R$ 10 milhões",
            [claim("credit_limit", "R$ 10 milhões", 100)],
            0,
            30,
            foreign_records=((100, 130),),
        )["status"]
        == "ATTRIBUTION_ERROR"
    )
    assert compare_field("title", "Example", [], 0, 20)["status"] == "MISSING"
    assert compare_field("official_identifier", "33/2026", [], 0, 20)["status"] == "UNRESOLVED"
    assert (
        compare_field(
            "credit_limit", "até R$ 10 milhões", [claim("credit_limit", "R$ 10 milhões")], 0, 30
        )["status"]
        == "PARTIAL"
    )
    assert (
        compare_field("title", "Example", [claim("title", "Example", 100)], 0, 20)["status"]
        == "UNRESOLVED"
    )
    bad = claim("title", "Example")
    bad["witness"]["quote"] = "unrelated"
    assert compare_field("title", "Example", [bad], 0, 20)["status"] == "VALUE_ERROR"


def test_independent_evaluation_keeps_all_denominators() -> None:
    from pathlib import Path

    from editalfinder_v2.evaluation_m32.engine import evaluate

    root = Path(__file__).resolve().parents[1]
    result, timings = evaluate(
        root / "data/m3",
        root / "data/m31/run-v2",
        (root / "data/m32/input_binding.json").read_bytes(),
    )
    assert result["status"] == "evaluated"
    body = result["results"]
    assert len(body["records"]) == 33
    assert sum(len(r["fields"]) for r in body["records"]) == 127
    assert body["field_summary"]["strict_role_value"] == {
        "numerator": 27,
        "denominator": 127,
        "value": 27 / 127,
    }
    assert sum(sum(row.values()) for row in body["discovery"]["matrix"].values()) == 33
    assert body["segmentation"]["nonempty_overlap"]["numerator"] == 32
    assert len(timings["documents"]) == 28
    assert body["semantic_evidence"]["reviewed_claims"] == 0
    assert body["semantic_evidence"]["unreviewed_field_claims"] == 332
    assert body["certified_metrics"] is None


@pytest.fixture
def frozen_case(tmp_path):
    import json
    import shutil
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    target = tmp_path / "run"
    target.mkdir()
    for name in ("predictions.json", "freeze.json"):
        shutil.copyfile(root / "data/m31/run-v2" / name, target / name)
    return root / "data/m3", target, json.loads((root / "data/m32/input_binding.json").read_bytes())


def rewrite_prediction(target, binding, body):
    import hashlib
    import json

    raw = json.dumps(body).encode()
    (target / "predictions.json").write_bytes(raw)
    receipt = json.loads((target / "freeze.json").read_bytes())
    receipt["prediction_sha256"] = hashlib.sha256(raw).hexdigest()
    binding["prediction_sha256"] = receipt["prediction_sha256"]
    (target / "freeze.json").write_text(json.dumps(receipt))


@pytest.mark.parametrize(
    "mutation",
    [
        "document_id",
        "missing_document",
        "duplicate_document",
        "duplicate_segment",
        "classification",
        "pdf_page",
        "html_offset",
        "borrowed_field",
        "approved",
        "schema_version",
        "nested_missing_version",
        "malformed_witness",
    ],
)
def test_invalid_predictions_never_produce_metrics(frozen_case, mutation) -> None:
    import json

    from editalfinder_v2.evaluation_m32.engine import evaluate

    root, target, binding = frozen_case
    body = json.loads((target / "predictions.json").read_bytes())
    doc = next(d for d in body["documents"] if d["document_id"] == "M30-F01")
    s = next(s for s in doc["segments"] if s["fields"])
    if mutation == "document_id":
        doc["document_id"] = "foreign"
    elif mutation == "missing_document":
        body["documents"].pop()
    elif mutation == "duplicate_document":
        body["documents"].append(body["documents"][0])
    elif mutation == "duplicate_segment":
        doc["segments"].append(s)
    elif mutation == "classification":
        s["discovery"] = "ACCEPTED"
    elif mutation == "pdf_page":
        pdf = next(d for d in body["documents"] if d["document_id"] == "M30-I07")
        field = next(f for s in pdf["segments"] for f in s["fields"])
        field["witness"]["page"] = 999
    elif mutation == "html_offset":
        s["end"] = 999999
    elif mutation == "borrowed_field":
        other = next(
            x for x in doc["segments"] if x["segment_id"] != s["segment_id"] and x["fields"]
        )
        s["fields"].append(other["fields"][0])
    elif mutation == "approved":
        doc["review_status"] = "approved"
    elif mutation == "schema_version":
        body["schema_version"] = "unknown"
    elif mutation == "nested_missing_version":
        del s["schema_version"]
    elif mutation == "malformed_witness":
        s["fields"][0]["witness"] = "not an object"
    rewrite_prediction(target, binding, body)
    result, _ = evaluate(root, target, json.dumps(binding).encode())
    assert result["status"] == "invalid_input", mutation
    assert result["results"] is None
    assert result["diagnostics"]


@pytest.mark.parametrize(
    "case", ["stale_hash", "missing_artifact", "evaluation_version", "duplicate_json", "nonfinite"]
)
def test_transport_failures_are_structured(frozen_case, case) -> None:
    import json

    from editalfinder_v2.evaluation_m32.engine import evaluate

    root, target, binding = frozen_case
    kwargs = {}
    if case == "stale_hash":
        (target / "predictions.json").write_text("{}")
    elif case == "missing_artifact":
        (target / "predictions.json").unlink()
    elif case == "evaluation_version":
        kwargs["schema_version"] = "m32-other"
    elif case == "duplicate_json":
        (target / "predictions.json").write_text('{"x":1,"x":2}')
    elif case == "nonfinite":
        (target / "predictions.json").write_text('{"x":1e999}')
    result, _ = evaluate(root, target, json.dumps(binding).encode(), **kwargs)
    assert result["status"] == "invalid_input" and result["results"] is None


def test_unknown_labels_and_navigation_are_not_negatives() -> None:
    from editalfinder_v2.evaluation_m32.engine import matrix

    assert matrix([], "modality", "modality") == dict(
        unit="provisional_reference_record", denominator=0, matrix={}
    )
    row = dict(
        reference={"discovery_label": "opportunity_signal"},
        representative_prediction={"discovery": "abstain"},
    )
    assert matrix([row], "discovery_label", "discovery")["matrix"] == {
        "opportunity_signal": {"abstain": 1}
    }


def test_semantic_reviews_do_not_inherit_locator_authority(frozen_case) -> None:
    import json

    from editalfinder_v2.evaluation_m32.engine import evaluate

    root, target, binding = frozen_case
    body = json.loads((target / "predictions.json").read_bytes())
    doc = next(d for d in body["documents"] if d["document_id"] == "M30-N04")
    seg = next(s for s in doc["segments"] if s["segment_id"] == "segment-0010")
    field = seg["fields"][0]
    w = field["witness"]
    item = dict(
        case_id="review-counterexample",
        document_id=doc["document_id"],
        segment_id=seg["segment_id"],
        claim_kind="field",
        field_index=0,
        field_name=field["name"],
        expected_claim=field["original"],
        start=w["start"],
        end=w["end"],
        quote=w["quote"],
        judgment="unsupported",
        certainty="confirmed_defect",
        error_codes=["FINANCIAL_ROLE_CONFUSION"],
        severity="high",
        rationale="Regional program allocation is not the amount per proposal.",
        expected_behavior="Preserve regional allocation role.",
        root_cause="100-character context sees per proposal later.",
        root_cause_confidence="high",
        next_action="Review role association in M3.3.",
    )
    reviews = dict(
        schema_version="m32-semantic-reviews-v1",
        prediction_sha256=binding["prediction_sha256"],
        review_status="provisional",
        reviewer_type="AI_qualitative_not_human",
        items=[item],
    )
    result, _ = evaluate(
        root,
        target,
        json.dumps(binding).encode(),
        semantic_reviews_raw=json.dumps(reviews).encode(),
    )
    assert result["status"] == "evaluated"
    assert result["results"]["locator_integrity"]["invalid"] == 0
    assert result["results"]["semantic_evidence"]["judgments"] == {"unsupported": 1}
    assert result["results"]["semantic_evidence"]["unreviewed_field_claims"] == 331
    reviews["review_status"] = "approved"
    result, _ = evaluate(
        root,
        target,
        json.dumps(binding).encode(),
        semantic_reviews_raw=json.dumps(reviews).encode(),
    )
    assert result["status"] == "invalid_input" and result["results"] is None


@pytest.mark.parametrize(
    "mutation",
    ["unknown_document", "approved_reference", "missing_reference", "annotation_version"],
)
def test_reference_failures_cannot_shrink_support(frozen_case, tmp_path, mutation) -> None:
    import hashlib
    import json
    import shutil

    from editalfinder_v2.evaluation_m32.engine import evaluate

    root, target, binding = frozen_case
    copied = tmp_path / "dataset"
    shutil.copytree(root, copied)
    path = copied / "annotations/records.json"
    body = json.loads(path.read_bytes())
    if mutation == "unknown_document":
        body["records"][0]["document_id"] = "foreign"
    elif mutation == "approved_reference":
        body["records"][0]["review_status"] = "approved"
    elif mutation == "missing_reference":
        body["records"].pop()
    elif mutation == "annotation_version":
        body["protocol_version"] = "unknown"
    raw = json.dumps(body).encode()
    path.write_bytes(raw)
    binding["annotation_sha256"] = hashlib.sha256(raw).hexdigest()
    result, _ = evaluate(copied, target, json.dumps(binding).encode())
    assert result["status"] == "invalid_input" and result["results"] is None


def test_cli_is_reproducible_and_refuses_frozen_or_existing_outputs(tmp_path) -> None:
    import os
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    prefix = [
        sys.executable,
        "-B",
        "-m",
        "editalfinder_v2.evaluation_m32",
        str(root / "data/m3"),
        str(root / "data/m31/run-v2"),
        str(root / "data/m32/input_binding.json"),
    ]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONPATH=str(root / "src"))
    for name in ("first", "second"):
        proc = subprocess.run(
            prefix + [str(tmp_path / name)], capture_output=True, text=True, env=env
        )
        assert proc.returncode == 0, proc.stderr + proc.stdout
    assert (tmp_path / "first/evaluation_results.json").read_bytes() == (
        tmp_path / "second/evaluation_results.json"
    ).read_bytes()
    assert len(list((tmp_path / "first/per_document").glob("*.json"))) == 28
    for bad in (tmp_path / "first", root / "data/m31/run-v2", root / "data/m3/forbidden"):
        proc = subprocess.run(prefix + [str(bad)], capture_output=True, text=True, env=env)
        assert proc.returncode != 0


def test_operational_failures_keep_reference_and_field_denominators(frozen_case) -> None:
    import json

    from editalfinder_v2.evaluation_m32.engine import evaluate

    root, target, binding = frozen_case
    body = json.loads((target / "predictions.json").read_bytes())
    doc = body["documents"][0]
    doc.update(
        status="operational_failure",
        segments=[],
        provenance=None,
        diagnostics=["simulated_io_failure"],
    )
    rewrite_prediction(target, binding, body)
    result, _ = evaluate(root, target, json.dumps(binding).encode())
    assert result["status"] == "evaluated"
    measured = result["results"]
    assert measured["processing"]["operational_failures"] == 1
    assert len(measured["records"]) == 33 and measured["field_summary"]["denominator"] == 127
    assert measured["discovery"]["matrix"]["confirmed_opportunity"]["operational_failure"] == 1
    assert measured["discovery"]["matrix"]["announced_future_opportunity"] == {
        "opportunity_signal": 1
    }
    assert all(x["discovery"] != "REJECTED" for x in measured["unannotated_segments_not_negatives"])


def test_semantic_review_quote_and_approval_tampering_rejected() -> None:
    import json
    from pathlib import Path

    from editalfinder_v2.evaluation_m32.engine import evaluate

    root = Path(__file__).resolve().parents[1]
    base = json.loads((root / "data/m32/semantic_reviews.json").read_bytes())
    for mutation in (
        "duplicate",
        "quote",
        "field_index",
        "future_claim",
        "context_page",
        "hash",
        "approved",
    ):
        reviews = json.loads(json.dumps(base))
        if mutation == "duplicate":
            reviews["items"].append(reviews["items"][0])
        elif mutation == "quote":
            reviews["items"][0]["quote"] = "fabricated quote"
        elif mutation == "field_index":
            reviews["items"][-1]["field_index"] = 9999
        elif mutation == "future_claim":
            reviews["items"][0]["expected_claim"] = "announced_future_opportunity"
        elif mutation == "context_page":
            next(x for x in reviews["items"] if x["context_evidence"])["context_evidence"][0][
                "page"
            ] = 999
        elif mutation == "hash":
            reviews["prediction_sha256"] = "0" * 64
        elif mutation == "approved":
            reviews["review_status"] = "approved"
        result, _ = evaluate(
            root / "data/m3",
            root / "data/m31/run-v2",
            (root / "data/m32/input_binding.json").read_bytes(),
            semantic_reviews_raw=json.dumps(reviews).encode(),
        )
        assert result["status"] == "invalid_input" and result["results"] is None, mutation
