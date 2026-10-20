"""Synthetic miniature fixtures only; these are not the pilot corpus."""

import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


def fixture_data(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    text = "Inscrições abertas. Apoio de R$ 100 até 2026-12-01."
    raw = f"<!doctype html><html><body>{text}</body></html>".encode()
    (root / "raw").mkdir()
    (root / "text").mkdir()
    (root / "annotations").mkdir()
    (root / "raw/one.html").write_bytes(raw)
    (root / "text/one.txt").write_text(text, encoding="utf-8")
    manifest = {
        "dataset_version": "m3.0-pilot-v1",
        "protocol_version": "m3.0-annotation-v1",
        "reference_date": "2026-10-19",
        "documents": [
            {
                "document_id": "doc1",
                "original_url": "https://example.org/call",
                "final_url": "https://example.org/call",
                "source_organization": "Synthetic",
                "retrieved_at": "2026-10-19T12:00:00Z",
                "original_filename": "one.html",
                "content_type": "text/html",
                "byte_length": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "raw_path": "raw/one.html",
                "text_path": "text/one.txt",
                "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "publication_date": None,
                "document_version": None,
                "source_authority_notes": "Synthetic test source",
                "retrieval_status": "acquired",
                "restrictions": "Synthetic fixture only",
                "document_category": "application_call",
                "category_evidence": "Inscrições abertas.",
                "derivation_method": "synthetic fixture",
            }
        ],
    }
    record = {
        "annotation_id": "a1",
        "record_id": "r1",
        "document_id": "doc1",
        "unit_locator": {"start": 0, "end": len(text)},
        "discovery_label": "confirmed_opportunity",
        "opportunity_label": "genuine_opportunity",
        "temporal_status": "open",
        "reference_date": "2026-10-19",
        "modality": "fomento",
        "review_status": "provisional",
        "annotation_method": "AI-assisted source reading; no model predictions",
        "protocol_version": "m3.0-annotation-v1",
        "rationale": "Synthetic evidence",
        "uncertainty_notes": [],
        "evidence": [
            {"evidence_id": "e1", "start": 0, "end": len(text), "quote": text, "page": None}
        ],
        "label_evidence": {
            k: ["e1"]
            for k in ("discovery_label", "opportunity_label", "temporal_status", "modality")
        },
        "fields": {"amount": {"value": "R$ 100", "evidence_ids": ["e1"]}},
    }
    annotations = {
        "dataset_version": manifest["dataset_version"],
        "protocol_version": manifest["protocol_version"],
        "records": [record],
    }
    return manifest, annotations


def save(root: Path, manifest: dict[str, Any], annotations: dict[str, Any]) -> None:
    (root / "corpus_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (root / "annotations/records.json").write_text(json.dumps(annotations), encoding="utf-8")


def load(root: Path) -> Any:
    return importlib.import_module("editalfinder_v2.dataset_m30").load_and_validate(root)


@pytest.mark.parametrize(
    ("target", "key", "value"),
    [
        ("manifest", "reference_date", "20261019"),
        ("document", "publication_date", "2026-02-30"),
        ("document", "retrieved_at", "2026-10-19T12:00:00"),
        ("document", "retrieved_at", "2026-10-19T12:00:00-03:00"),
        ("document", "source_authority_notes", "   "),
        ("document", "byte_length", "100"),
        ("document", "byte_length", True),
        ("document", "byte_length", 5242881),
        ("document", "sha256", "bad"),
        ("document", "unexpected", "value"),
        ("manifest", "dataset_version", "wrong"),
        ("annotations", "protocol_version", "wrong"),
        ("record", "protocol_version", "wrong"),
        ("record", "review_status", "approved"),
        ("record", "review_status", "human_verified"),
        ("record", "opportunity_label", "probably_positive"),
        ("document", "content_type", "application/javascript"),
        ("record", "review_status", "independently_reviewed"),
        ("record", "review_status", "disputed"),
        ("record", "reference_date", "2026-99-99"),
        ("record", "unit_locator", {"start": 4, "end": 3}),
        ("record", "label_evidence", {"discovery_label": ["e1"]}),
    ],
)
def test_schema_rejections(tmp_path: Path, target: str, key: str, value: Any) -> None:
    manifest, annotations = fixture_data(tmp_path)
    targets = {
        "manifest": manifest,
        "document": manifest["documents"][0],
        "annotations": annotations,
        "record": annotations["records"][0],
    }
    targets[target][key] = value
    save(tmp_path, manifest, annotations)
    with pytest.raises(ValueError):
        load(tmp_path)


@pytest.mark.parametrize(
    "key",
    [
        "publication_date",
        "document_version",
        "restrictions",
        "source_authority_notes",
        "derivation_method",
        "retrieved_at",
    ],
)
def test_provenance_cannot_be_omitted(tmp_path: Path, key: str) -> None:
    manifest, annotations = fixture_data(tmp_path)
    del manifest["documents"][0][key]
    save(tmp_path, manifest, annotations)
    with pytest.raises(ValueError):
        load(tmp_path)


@pytest.mark.parametrize(
    "damage",
    [
        "raw_hash",
        "text_hash",
        "length",
        "signature",
        "utf8",
        "category",
        "raw_missing",
        "text_missing",
        "manifest_missing",
        "annotations_missing",
        "escape",
        "symlink",
        "duplicate_json",
        "nonfinite_json",
        "oversize_json",
    ],
)
def test_integrity_failures(tmp_path: Path, damage: str) -> None:
    manifest, annotations = fixture_data(tmp_path)
    doc = manifest["documents"][0]
    save(tmp_path, manifest, annotations)
    if damage == "raw_hash":
        (tmp_path / doc["raw_path"]).write_bytes(b"tampered")
    elif damage == "text_hash":
        (tmp_path / doc["text_path"]).write_bytes(b"tampered")
    elif damage == "length":
        doc["byte_length"] += 1
    elif damage == "signature":
        raw = b"not html"
        (tmp_path / doc["raw_path"]).write_bytes(raw)
        doc.update(byte_length=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    elif damage == "utf8":
        (tmp_path / doc["text_path"]).write_bytes(b"\xff")
        doc["text_sha256"] = hashlib.sha256(b"\xff").hexdigest()
    elif damage == "category":
        doc["category_evidence"] = "absent"
    elif damage.endswith("_missing"):
        name = {
            "raw_missing": doc["raw_path"],
            "text_missing": doc["text_path"],
            "manifest_missing": "corpus_manifest.json",
            "annotations_missing": "annotations/records.json",
        }
        (tmp_path / name[damage]).unlink()
    elif damage in {"escape", "symlink"}:
        outside = tmp_path.parent / (tmp_path.name + "-outside")
        outside.write_bytes((tmp_path / doc["raw_path"]).read_bytes())
        if damage == "escape":
            doc["raw_path"] = "../" + outside.name
        else:
            (tmp_path / "link").symlink_to(outside)
            doc["raw_path"] = "link"
    elif damage == "duplicate_json":
        path = tmp_path / "corpus_manifest.json"
        path.write_text(path.read_text().replace("{", '{"dataset_version":"wrong",', 1))
    elif damage == "nonfinite_json":
        path = tmp_path / "corpus_manifest.json"
        path.write_text(path.read_text().replace("{", '{"ignored":NaN,', 1))
    elif damage == "oversize_json":
        path = tmp_path / "corpus_manifest.json"
        path.write_bytes(path.read_bytes() + b" " * (16 * 1024 * 1024))
    if damage in {"length", "signature", "utf8", "category", "escape", "symlink"}:
        save(tmp_path, manifest, annotations)
    with pytest.raises(ValueError):
        load(tmp_path)


@pytest.mark.parametrize(
    "damage",
    [
        "document_id",
        "record_id",
        "annotation_id",
        "unknown_document",
        "reference_date",
        "unit_end",
        "outside_unit",
        "quote",
        "evidence_id",
        "label_link",
        "field_link",
        "field_verbatim",
        "html_page",
        "genuine_signal",
        "announced_negative",
        "unrelated_genuine",
        "negative_open",
        "confirmed_na",
        "signal_open",
        "announced_continuous",
    ],
)
def test_record_consistency(tmp_path: Path, damage: str) -> None:
    manifest, annotations = fixture_data(tmp_path)
    record = annotations["records"][0]
    evidence = record["evidence"][0]
    if damage == "document_id":
        manifest["documents"].append(dict(manifest["documents"][0]))
    elif damage in {"record_id", "annotation_id"}:
        second = dict(record, record_id="r2", annotation_id="a2")
        second[damage] = record[damage]
        annotations["records"].append(second)
    elif damage == "unknown_document":
        record["document_id"] = "unknown"
    elif damage == "reference_date":
        record["reference_date"] = "2026-10-18"
    elif damage == "unit_end":
        record["unit_locator"]["end"] += 1
    elif damage == "outside_unit":
        record["unit_locator"]["start"] = 1
    elif damage == "quote":
        evidence["quote"] = "not in text"
    elif damage == "evidence_id":
        record["evidence"].append(dict(evidence))
    elif damage == "label_link":
        record["label_evidence"]["modality"] = ["missing"]
    elif damage == "field_link":
        record["fields"]["amount"]["evidence_ids"] = ["missing"]
    elif damage == "field_verbatim":
        record["fields"]["amount"]["value"] = "BRL_100"
    elif damage == "html_page":
        evidence["page"] = 1
    else:
        changes = {
            "genuine_signal": {"discovery_label": "opportunity_signal"},
            "announced_negative": {
                "discovery_label": "announced_future_opportunity",
                "opportunity_label": "not_opportunity",
            },
            "unrelated_genuine": {"discovery_label": "unrelated_or_non_actionable"},
            "negative_open": {
                "discovery_label": "unrelated_or_non_actionable",
                "opportunity_label": "not_opportunity",
            },
            "confirmed_na": {"temporal_status": "not_applicable"},
            "signal_open": {
                "discovery_label": "opportunity_signal",
                "opportunity_label": "uncertain",
            },
            "announced_continuous": {
                "discovery_label": "announced_future_opportunity",
                "opportunity_label": "uncertain",
                "temporal_status": "continuous",
            },
        }
        record.update(changes[damage])
    save(tmp_path, manifest, annotations)
    with pytest.raises(ValueError):
        load(tmp_path)


@pytest.mark.parametrize("page", [None, 0, 1, 2, 3])
def test_pdf_page_containment(tmp_path: Path, page: int | None) -> None:
    manifest, annotations = fixture_data(tmp_path)
    doc = manifest["documents"][0]
    record = annotations["records"][0]
    text = record["evidence"][0]["quote"]
    prefix = "Page one\f"
    frozen = (prefix + text).encode()
    raw = b"%PDF-1.4\nsynthetic signature fixture, not an actual PDF"
    (tmp_path / doc["raw_path"]).write_bytes(raw)
    (tmp_path / doc["text_path"]).write_bytes(frozen)
    doc.update(
        content_type="application/pdf",
        byte_length=len(raw),
        sha256=hashlib.sha256(raw).hexdigest(),
        text_sha256=hashlib.sha256(frozen).hexdigest(),
    )
    record["unit_locator"]["end"] = len(prefix + text)
    record["evidence"][0].update(start=len(prefix), end=len(prefix + text), page=page)
    save(tmp_path, manifest, annotations)
    if page == 2:
        load(tmp_path)
    else:
        with pytest.raises(ValueError):
            load(tmp_path)


@pytest.mark.parametrize(
    ("discovery", "opportunity", "temporal", "category"),
    [
        ("confirmed_opportunity", "genuine_opportunity", "closed", "application_call"),
        ("announced_future_opportunity", "uncertain", "future", "institutional_news"),
        ("opportunity_signal", "uncertain", "undetermined", "program_information"),
        ("unrelated_or_non_actionable", "not_opportunity", "not_applicable", "selection_result"),
    ],
)
def test_valid_label_combinations(
    tmp_path: Path, discovery: str, opportunity: str, temporal: str, category: str
) -> None:
    manifest, annotations = fixture_data(tmp_path)
    manifest["documents"][0]["document_category"] = category
    annotations["records"][0].update(
        discovery_label=discovery,
        opportunity_label=opportunity,
        temporal_status=temporal,
        modality="undetermined",
    )
    save(tmp_path, manifest, annotations)
    load(tmp_path)


def test_multiple_records_and_distinct_documents_can_share_url_hash(tmp_path: Path) -> None:
    manifest, annotations = fixture_data(tmp_path)
    manifest["documents"].append(dict(manifest["documents"][0], document_id="doc2"))
    record = annotations["records"][0]
    annotations["records"].extend(
        [
            dict(record, record_id="r2", annotation_id="a2"),
            dict(record, record_id="r3", annotation_id="a3", document_id="doc2"),
        ]
    )
    save(tmp_path, manifest, annotations)
    actual_manifest, actual_annotations = load(tmp_path)
    assert len(actual_manifest.documents) == 2
    assert len(actual_annotations.records) == 3


@pytest.mark.parametrize("valid", [True, False])
def test_cli(tmp_path: Path, valid: bool) -> None:
    manifest, annotations = fixture_data(tmp_path)
    save(tmp_path, manifest, annotations)
    if not valid:
        (tmp_path / "corpus_manifest.json").unlink()
    source = Path(__file__).resolve().parents[1] / "src"
    result = subprocess.run(
        [sys.executable, "-B", "-m", "editalfinder_v2.dataset_m30", str(tmp_path)],
        env={**os.environ, "PYTHONPATH": str(source)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == (0 if valid else 1)
    if valid:
        assert "Validated 1 documents and 1 records" in result.stdout
    else:
        assert "Dataset validation failed:" in result.stderr
        assert "Traceback" not in result.stderr


@pytest.mark.parametrize(
    ("discovery", "opportunity", "temporal"),
    [
        ("confirmed_opportunity", "uncertain", "undetermined"),
        ("opportunity_signal", "uncertain", "not_applicable"),
        ("announced_future_opportunity", "uncertain", "not_applicable"),
    ],
)
def test_bidirectional_pilot_label_contract(
    tmp_path: Path, discovery: str, opportunity: str, temporal: str
) -> None:
    manifest, annotations = fixture_data(tmp_path)
    annotations["records"][0].update(
        discovery_label=discovery, opportunity_label=opportunity, temporal_status=temporal
    )
    save(tmp_path, manifest, annotations)
    with pytest.raises(ValueError):
        load(tmp_path)


@pytest.mark.parametrize(
    "url",
    [
        "/relative",
        "javascript:alert(1)",
        "https://name:password@example.org/call",
        "https://example.org/a b",
        "https://example.org:444/call",
        "https://[broken/call",
        "http://example.org/call",
    ],
)
def test_acquisition_provenance_urls_follow_explicit_https_policy(tmp_path: Path, url: str) -> None:
    manifest, annotations = fixture_data(tmp_path)
    manifest["documents"][0]["original_url"] = url
    save(tmp_path, manifest, annotations)
    with pytest.raises(ValueError):
        load(tmp_path)


def test_explicit_schema_roundtrip(tmp_path: Path) -> None:
    manifest, annotations = fixture_data(tmp_path)
    save(tmp_path, manifest, annotations)
    actual_manifest, actual_annotations = load(tmp_path)
    assert json.loads(actual_manifest.model_dump_json()) == manifest
    assert json.loads(actual_annotations.model_dump_json()) == annotations
    assert (
        type(actual_manifest).model_validate_json(actual_manifest.model_dump_json())
        == actual_manifest
    )
