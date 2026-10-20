"""Acceptance checks for the REAL pilot, not the synthetic M23C oracle."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "data" / "m3"


def corpus() -> tuple[dict, list[dict]]:
    manifest = json.loads((ROOT / "corpus_manifest.json").read_text())
    annotations = json.loads((ROOT / "annotations" / "records.json").read_text())
    return manifest, annotations["records"]


def test_real_corpus_offline_verifier_and_json_roundtrip() -> None:
    from editalfinder_v2.dataset_m30 import load_and_validate

    manifest, annotations = load_and_validate(ROOT)
    assert len(manifest.documents) >= 24
    assert annotations.records
    assert json.loads(manifest.model_dump_json()) == json.loads(
        (ROOT / "corpus_manifest.json").read_text()
    )
    assert json.loads(annotations.model_dump_json()) == json.loads(
        (ROOT / "annotations" / "records.json").read_text()
    )


def test_real_pilot_document_quota_and_three_modalities() -> None:
    manifest, records = corpus()
    assert 24 <= len(manifest["documents"]) <= 36
    assert {"fomento", "credito", "investimentos"} <= {r["modality"] for r in records}


def test_news_is_not_a_negative_by_document_type() -> None:
    manifest, records = corpus()
    news_ids = {
        d["document_id"]
        for d in manifest["documents"]
        if d["document_category"] == "institutional_news"
    }
    news_labels = {r["discovery_label"] for r in records if r["document_id"] in news_ids}
    assert "confirmed_opportunity" in news_labels
    assert "opportunity_signal" in news_labels
    assert "unrelated_or_non_actionable" in news_labels


def test_real_corpus_has_positive_negative_uncertain_controls() -> None:
    _, records = corpus()
    assert {"genuine_opportunity", "not_opportunity", "uncertain"} <= {
        r["opportunity_label"] for r in records
    }
    for r in records:
        if r["opportunity_label"] == "not_opportunity":
            assert r["temporal_status"] == "not_applicable"
        assert r["review_status"] == "provisional"
        assert r["reference_date"] == "2026-10-19"


def test_multiple_records_are_not_collapsed_into_document_identity() -> None:
    _, records = corpus()
    counts = Counter(r["document_id"] for r in records)
    assert max(counts.values()) > 1
    mixed = [r for r in records if r["document_id"] == "M30-C07"]
    assert len(mixed) == 2
    assert {r["opportunity_label"] for r in mixed} == {
        "genuine_opportunity",
        "not_opportunity",
    }
    a, b = sorted(mixed, key=lambda r: r["unit_locator"]["start"])
    assert a["unit_locator"]["end"] <= b["unit_locator"]["start"]
    assert a["record_id"] != b["record_id"]


def test_original_html_and_pdf_both_preserved() -> None:
    manifest, _ = corpus()
    assert {"text/html", "application/pdf"} <= {d["content_type"] for d in manifest["documents"]}


def test_budget_supplement_for_existing_proposals_is_not_new_window() -> None:
    _, records = corpus()
    record = next(r for r in records if r["document_id"] == "M30-N04")
    assert record["opportunity_label"] == "not_opportunity"
    assert any("já analisados" in e["quote"] for e in record["evidence"])


def test_future_product_launch_is_not_future_application() -> None:
    _, records = corpus()
    record = next(r for r in records if r["document_id"] == "M30-N01")
    assert record["temporal_status"] == "not_applicable"
    assert record["opportunity_label"] == "not_opportunity"
    assert any("lançamento em 2027" in e["quote"] for e in record["evidence"])


def test_no_native_domain_candidates_or_predictions_in_reference_labels() -> None:
    manifest, records = corpus()
    assert manifest["dataset_version"] == "m3.0-pilot-v1"
    for record in records:
        assert "prediction" not in record
        assert "candidate_id" not in record
        assert "opportunity_id" not in record
        assert record["annotation_method"] == "AI-assisted source reading; no model predictions"
