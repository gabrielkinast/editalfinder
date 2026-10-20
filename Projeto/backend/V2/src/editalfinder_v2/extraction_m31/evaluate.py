"""Separate exploratory comparisons AFTER prediction freeze; never inference input."""

from collections import Counter
from typing import Any

from .models import DocumentOutcome


def overlap(a: int, b: int, c: int, d: int) -> int:
    return max(0, min(b, d) - max(a, c))


def compare(
    results: tuple[DocumentOutcome, ...], references: list[dict[str, Any]]
) -> dict[str, Any]:
    """All reference slots retained. No binary recoding of uncertain or missing.

    Matching is solely same-document span overlap, independent of labels/fields.
    Best segment = largest intersection, then earliest position. Other overlaps
    retained to expose oversegmentation; this is not identity resolution.
    """
    by_document = {r.document_id: r for r in results}
    comparisons: list[dict[str, Any]] = []
    ownership: Counter[tuple[str, str]] = Counter()
    for reference in references:
        result = by_document.get(reference["document_id"])
        row: dict[str, Any] = dict(
            reference_record=reference["record_id"], document_id=reference["document_id"]
        )
        start, end = reference["unit_locator"]["start"], reference["unit_locator"]["end"]
        row["reference"] = {
            k: reference[k]
            for k in ("discovery_label", "modality", "temporal_status", "opportunity_label")
        }
        if result is None or result.status == "operational_failure":
            row.update(
                status="missing_document" if result is None else "operational_failure",
                overlapping_segments=[],
                best_segment=None,
            )
            comparisons.append(row)
            continue
        candidates = [s for s in result.segments if overlap(start, end, s.start, s.end) > 0]
        if not candidates:
            row.update(status="no_overlap", overlapping_segments=[], best_segment=None)
            comparisons.append(row)
            continue
        best = max(candidates, key=lambda s: (overlap(start, end, s.start, s.end), -s.start))
        intersections = sorted((max(start, s.start), min(end, s.end)) for s in candidates)
        covered = 0
        cursor = start
        for a, b in intersections:
            covered += max(0, b - max(a, cursor))
            cursor = max(cursor, b)
        predicted_fields = [f for s in candidates for f in s.fields]
        field_rows = []
        for name, field in reference["fields"].items():
            exact = [f for f in predicted_fields if f.name == name and f.original == field["value"]]
            # Role and lexical match alone do not prove same stage or entailment.
            field_rows.append(
                dict(
                    name=name,
                    reference=field["value"],
                    exact_role_value=bool(exact),
                    candidates=[
                        f.model_dump(mode="json") for f in predicted_fields if f.name == name
                    ],
                )
            )
        for s in candidates:
            ownership[(result.document_id, s.segment_id)] += 1
        row.update(
            status="overlap_comparison",
            best_segment=best.segment_id,
            overlapping_segments=[s.segment_id for s in candidates],
            reference_span_characters=end - start,
            covered_reference_characters=covered,
            boundary_exact=(start, end) == (best.start, best.end),
            prediction=dict(
                discovery_label=best.discovery,
                modality=best.modality,
                temporal_status=best.temporal,
            ),
            disagreements=[
                name
                for name, pred in [
                    ("discovery_label", best.discovery),
                    ("modality", best.modality),
                    ("temporal_status", best.temporal),
                ]
                if pred != reference[name]
            ],
            field_comparisons=field_rows,
            all_overlap_predictions=[
                dict(
                    segment_id=s.segment_id,
                    discovery=s.discovery,
                    modality=s.modality,
                    temporal=s.temporal,
                )
                for s in candidates
            ],
        )
        comparisons.append(row)
    segments = [s for r in results for s in r.segments]
    out_of_scope = [
        dict(document_id=r.document_id, segment_id=s.segment_id, discovery=s.discovery)
        for r in results
        for s in r.segments
        if (r.document_id, s.segment_id) not in ownership
    ]
    return dict(
        version="m31-exploratory-comparison-v1",
        status="PROVISIONAL / EXPLORATORY",
        certified_metrics=None,
        reference_records=len(references),
        document_outcomes=len(results),
        operational_failures=sum(r.status == "operational_failure" for r in results),
        predicted_segments=len(segments),
        discoveries=dict(Counter(s.discovery for s in segments)),
        modalities=dict(Counter(s.modality for s in segments)),
        temporal=dict(Counter(s.temporal for s in segments)),
        fields=sum(len(s.fields) for s in segments),
        uncertain_references=sum(r["opportunity_label"] == "uncertain" for r in references),
        abstentions=sum(s.discovery == "abstain" for s in segments),
        comparisons=comparisons,
        segmentation=dict(
            oversegmented_references=sum(len(r["overlapping_segments"]) > 1 for r in comparisons),
            segments_overlapping_multiple_references=[
                dict(document_id=d, segment_id=s, reference_count=count)
                for (d, s), count in ownership.items()
                if count > 1
            ],
        ),
        unannotated_predictions_not_negatives=out_of_scope,
        attribution="Resolved witnesses do not prove semantic entailment. "
        "Best-span matching is diagnostic, not canonical identity. "
        "All exposed documents are development data.",
    )
