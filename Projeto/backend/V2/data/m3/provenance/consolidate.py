"""Explicit offline consolidation of AI curation batches, not a label generator.

Run only after all four batches are complete and reviewed. No extraction, network,
identity resolution or production domain call. Semantic decisions remain in each
curation record. This script sorts/serializes/counts; it never infers a label.
"""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "m3.0-pilot-v1"
PROTOCOL = "m3.0-annotation-v1"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    docs, records = [], []
    for name in ["parent", "fomento", "investment", "supplement"]:
        batch = json.loads((ROOT / "provenance" / (name + "_curation.json")).read_text())
        docs.extend(batch["documents"])
        records.extend(batch["records"])
    docs.sort(key=lambda d: d["document_id"])
    records.sort(key=lambda r: r["annotation_id"])
    assert len({d["document_id"] for d in docs}) == len(docs), "Duplicate document IDs"
    assert len({r["annotation_id"] for r in records}) == len(records), "Duplicate annotation IDs"
    assert 24 <= len(docs) <= 36, "Pilot quota not satisfied; do not fabricate"
    manifest = {
        "dataset_version": VERSION,
        "protocol_version": PROTOCOL,
        "reference_date": "2026-10-19",
        "documents": docs,
    }
    annotations = {"dataset_version": VERSION, "protocol_version": PROTOCOL, "records": records}
    write_json(ROOT / "corpus_manifest.json", manifest)
    write_json(ROOT / "annotations" / "records.json", annotations)
    coverage = {
        "dataset_version": VERSION,
        "protocol_version": PROTOCOL,
        "reference_date": "2026-10-19",
        "documents": len(docs),
        "records": len(records),
        "document_types": dict(Counter(d["content_type"] for d in docs)),
        "source_organizations": dict(Counter(d["source_organization"] for d in docs)),
        "document_categories": dict(Counter(d["document_category"] for d in docs)),
        "discovery_labels": dict(Counter(r["discovery_label"] for r in records)),
        "opportunity_labels": dict(Counter(r["opportunity_label"] for r in records)),
        "temporal_statuses": dict(Counter(r["temporal_status"] for r in records)),
        "record_modalities": dict(Counter(r["modality"] for r in records)),
        "documents_per_modality_nonexclusive": {
            modality: len({r["document_id"] for r in records if r["modality"] == modality})
            for modality in sorted({r["modality"] for r in records})
        },
        "review_statuses": dict(Counter(r["review_status"] for r in records)),
        "annotated_fields": dict(Counter(k for r in records for k in r["fields"])),
        "evidence_items": sum(len(r["evidence"]) for r in records),
        "raw_total_bytes": sum(d["byte_length"] for d in docs),
        "max_raw_bytes": max(d["byte_length"] for d in docs),
        "verified_document_publication_dates": sum(d["publication_date"] is not None for d in docs),
        "multi_record_document_ids": sorted(
            k for k, v in Counter(r["document_id"] for r in records).items() if v > 1
        ),
        "missing_discovery_classes": sorted(
            {
                "confirmed_opportunity",
                "announced_future_opportunity",
                "opportunity_signal",
                "unrelated_or_non_actionable",
            }
            - {r["discovery_label"] for r in records}
        ),
        "missing_temporal_classes": sorted(
            {"open", "closed", "future", "continuous", "undetermined", "not_applicable"}
            - {r["temporal_status"] for r in records}
        ),
        "metrics": None,
        "limitation": (
            "Counts only. All labels provisional; no predictions compared, "
            "no statistical representativeness or human ground truth claim."
        ),
    }
    write_json(ROOT / "evaluation" / "coverage.json", coverage)
    write_json(
        ROOT / "provenance" / "selected_urls.json",
        [
            {
                "document_id": d["document_id"],
                "original_url": d["original_url"],
                "final_url": d["final_url"],
                "source_organization": d["source_organization"],
            }
            for d in docs
        ],
    )
    md = [
        "# Provisional reference labels — M3.0",
        "",
        "AI-assisted source reading, not human ground truth. "
        "All review statuses remain provisional.",
        f"Dataset {VERSION}; protocol {PROTOCOL}; explicit reference day 2026-10-19.",
        "Exact quotes and character spans below refer to frozen UTF-8 text views, "
        "not raw-byte offsets.",
        "Unannotated navigation/related-story text is out of scope, not negative.",
        "",
    ]
    for d in docs:
        md += [
            f"## {d['document_id']} — {d['source_organization']}",
            "",
            f"Source: {d['original_url']}",
            f"Final URL: {d['final_url']}",
            f"Raw: {d['raw_path']} ({d['byte_length']} bytes); SHA-256 {d['sha256']}",
            f"Text: {d['text_path']}; SHA-256 {d['text_sha256']}",
            f"Document category: {d['document_category']}",
            "Category evidence: " + d["category_evidence"].replace("\n", " / "),
            "",
        ]
        for r in (r for r in records if r["document_id"] == d["document_id"]):
            md += [
                f"### {r['annotation_id']} / {r['record_id']}",
                "",
                f"Record scope: [{r['unit_locator']['start']}, "
                f"{r['unit_locator']['end']}) codepoints.",
                f"Discovery: {r['discovery_label']}; existence: {r['opportunity_label']}.",
                f"Temporal: {r['temporal_status']} at {r['reference_date']}; "
                f"modality: {r['modality']}.",
                f"Review: {r['review_status']}; method: {r['annotation_method']}.",
                f"Protocol: {r['protocol_version']}",
                "",
                "Rationale: " + r["rationale"],
                "",
                "Uncertainties:",
            ]
            md.extend("- " + u for u in r["uncertainty_notes"])
            md += ["", "Label witnesses:"]
            md.extend(f"- {key}: {', '.join(value)}" for key, value in r["label_evidence"].items())
            md += ["", "Fields (original expressions only):"]
            md.extend(
                f"- {key}: {value['value']} — evidence {', '.join(value['evidence_ids'])}"
                for key, value in r["fields"].items()
            )
            md += ["", "Evidence:"]
            for e in r["evidence"]:
                md += [
                    "",
                    f"{e['evidence_id']} — [{e['start']}, {e['end']}); "
                    f"PDF page: {e['page'] if e['page'] is not None else 'not applicable (HTML)'}",
                    "",
                ]
                md.extend(("> " + line.rstrip()).rstrip() for line in e["quote"].splitlines())
            md += [""]
    (ROOT / "annotations" / "REFERENCE_LABELS.md").write_text(
        "\n".join(md).rstrip() + "\n", encoding="utf-8"
    )
    print(json.dumps(coverage, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
