"""Independent exploratory measurements. Never calls extraction or M31 compare()."""

import json
from collections import Counter
from pathlib import Path
from time import perf_counter
from typing import Any

from pydantic import ValidationError

from .alignment import Located, align, fraction
from .fields import STATUSES, compare_field
from .inputs import Binding, EvaluationFault, InputBundle, load_bundle, parse

VERSION = "m32-evaluation-v1"
RELEVANT = {"confirmed_opportunity", "announced_future_opportunity", "opportunity_signal"}


def matrix(rows: list[dict[str, Any]], label: str, prediction: str) -> dict[str, Any]:
    cells: dict[str, dict[str, int]] = {}
    for row in rows:
        target = row["reference"][label]
        observed = (
            row["representative_prediction"][prediction]
            if row["representative_prediction"]
            else row["status"]
        )
        cell = cells.setdefault(target, {})
        cell[observed] = cell.get(observed, 0) + 1
    return dict(unit="provisional_reference_record", denominator=len(rows), matrix=cells)


def calculate(bundle: InputBundle) -> tuple[dict[str, Any], dict[str, Any]]:
    refs = bundle.annotations.records
    outcomes = {d.document_id: d for d in bundle.outcomes}
    timings: dict[str, Any] = dict(
        documents={
            d: dict(
                v, alignment_seconds=0.0, field_comparison_seconds=0.0, record_assembly_seconds=0.0
            )
            for d, v in bundle.evidence_timings.items()
        },
        records=[],
    )
    graph: list[dict[str, Any]] = []
    alignment_times: dict[str, float] = {}
    for ref in refs:
        t = perf_counter()
        graph.extend(
            align(
                (
                    Located(
                        ref.document_id, ref.record_id, ref.unit_locator.start, ref.unit_locator.end
                    ),
                ),
                tuple(
                    Located(ref.document_id, s.segment_id, s.start, s.end)
                    for s in outcomes[ref.document_id].segments
                ),
            )
        )
        elapsed = perf_counter() - t
        alignment_times[ref.record_id] = elapsed
        timings["documents"][ref.document_id]["alignment_seconds"] += elapsed
    timings["alignment_total_seconds"] = sum(alignment_times.values())
    rows = []
    owners: dict[tuple[str, str], list[str]] = {}
    extracted = []
    field_counts: Counter[str] = Counter()
    fields_total = strict_count = 0
    for ref, alignment in zip(refs, graph, strict=True):
        t = perf_counter()
        outcome = outcomes[ref.document_id]
        segments = {s.segment_id: s for s in outcome.segments}
        overlapping = [segments[e["segment_id"]] for e in alignment["edges"]]
        for s in overlapping:
            owners.setdefault((ref.document_id, s.segment_id), []).append(ref.record_id)
        representative = segments.get(alignment["representative"])
        status = (
            "operational_failure"
            if outcome.status == "operational_failure"
            else "overlap"
            if overlapping
            else "no_overlap"
        )
        prediction = (
            {
                "segment_id": representative.segment_id,
                "discovery": representative.discovery,
                "modality": representative.modality,
                "temporal": representative.temporal,
                "start": representative.start,
                "end": representative.end,
            }
            if representative
            else None
        )
        values = [
            dict(f.model_dump(mode="json"), segment_id=s.segment_id, field_index=i)
            for s in overlapping
            for i, f in enumerate(s.fields)
        ]
        tf = perf_counter()
        field_rows = []
        for name, field in ref.fields.items():
            item = compare_field(
                name,
                field.value,
                values,
                ref.unit_locator.start,
                ref.unit_locator.end,
                foreign_records=tuple(
                    (other.unit_locator.start, other.unit_locator.end)
                    for other in refs
                    if other.document_id == ref.document_id and other.record_id != ref.record_id
                ),
            )
            item["reference_evidence"] = [
                e.model_dump() for e in ref.evidence if e.evidence_id in field.evidence_ids
            ]
            field_rows.append(item)
            field_counts[item["status"]] += 1
            strict_count += item["strict_role_value"]
            fields_total += 1
        finished = perf_counter()
        timings["documents"][ref.document_id]["field_comparison_seconds"] += finished - tf
        timings["documents"][ref.document_id]["record_assembly_seconds"] += tf - t
        timings["records"].append(
            dict(
                record_id=ref.record_id,
                document_id=ref.document_id,
                field_comparison_seconds=finished - tf,
                assembly_seconds=tf - t,
                alignment_seconds=alignment_times[ref.record_id],
                total_seconds=finished - t + alignment_times[ref.record_id],
            )
        )
        label = ref.model_dump(
            include={
                "discovery_label",
                "modality",
                "temporal_status",
                "opportunity_label",
                "review_status",
            }
        )
        disagreements = []
        for key, pkey in [
            ("discovery_label", "discovery"),
            ("modality", "modality"),
            ("temporal_status", "temporal"),
        ]:
            if prediction is None or prediction[pkey] != label[key]:
                disagreements.append(key)
        text = bundle.documents[ref.document_id].text
        pdf = bundle.documents[ref.document_id].provenance.content_type == "application/pdf"
        pages = sorted({e.page for e in ref.evidence if e.page is not None})
        rows.append(
            dict(
                alignment,
                status=status,
                reference=label,
                representative_prediction=prediction,
                disagreements=disagreements,
                fields=field_rows,
                all_overlap_predictions=[
                    dict(
                        segment_id=s.segment_id,
                        discovery=s.discovery,
                        modality=s.modality,
                        temporal=s.temporal,
                    )
                    for s in overlapping
                ],
                discovery_histogram=dict(Counter(s.discovery for s in overlapping)),
                reference_evidence=[e.model_dump() for e in ref.evidence],
                rationale=ref.rationale,
                uncertainty_notes=ref.uncertainty_notes,
                location_convention="frozen_pdf_text_unicode_not_visual_geometry"
                if pdf
                else "html_unicode_codepoints",
                physical_reference_evidence_pages=pages,
                representative_quote=(
                    text[representative.start : representative.end] if representative else None
                ),
            )
        )
    all_segments = [s for d in bundle.outcomes for s in d.segments]
    per_document = []
    for doc in bundle.manifest.documents:
        document_outcome = outcomes[doc.document_id]
        own_refs = [r for r in rows if r["document_id"] == doc.document_id]
        own_segments = []
        text = bundle.documents[doc.document_id].text
        for s in document_outcome.segments:
            linked = owners.get((doc.document_id, s.segment_id), [])
            own_segments.append(
                dict(
                    segment_id=s.segment_id,
                    start=s.start,
                    end=s.end,
                    discovery=s.discovery,
                    modality=s.modality,
                    temporal=s.temporal,
                    diagnostics=list(s.diagnostics),
                    reference_records=linked,
                    field_count=len(s.fields),
                    unannotated_not_negative=not linked,
                    physical_page=(
                        text[: s.start].count("\f") + 1
                        if doc.content_type == "application/pdf"
                        else None
                    ),
                )
            )
            for i, f in enumerate(s.fields):
                extracted.append(
                    dict(
                        document_id=doc.document_id,
                        segment_id=s.segment_id,
                        field_index=i,
                        **f.model_dump(mode="json"),
                        reference_records=linked,
                        semantic_support="unreviewed",
                    )
                )
        per_document.append(
            dict(
                document_id=doc.document_id,
                status=document_outcome.status,
                diagnostics=list(document_outcome.diagnostics),
                provenance=doc.model_dump(),
                records=own_refs,
                segments=own_segments,
            )
        )
    multi = [
        dict(document_id=k[0], segment_id=k[1], reference_records=v)
        for k, v in sorted(owners.items())
        if len(v) > 1
    ]
    unannotated = [
        dict(document_id=d.document_id, segment_id=s.segment_id, discovery=s.discovery)
        for d in bundle.outcomes
        for s in d.segments
        if (d.document_id, s.segment_id) not in owners
    ]
    abstained = [
        (d.document_id, s) for d in bundle.outcomes for s in d.segments if s.discovery == "abstain"
    ]
    exact = sum(r["any_exact_boundary"] for r in rows)
    # Alignment work was measured globally, not misreported as per-record work.
    result: dict[str, Any] = dict(
        trust_status="PROVISIONAL / EXPLORATORY",
        certified_metrics=None,
        binding=bundle.binding.model_dump(mode="json"),
        processing=dict(
            documents=len(bundle.manifest.documents),
            processed=sum(d.status == "processed" for d in bundle.outcomes),
            operational_failures=sum(d.status == "operational_failure" for d in bundle.outcomes),
            missing_document_outcomes=0,
        ),
        segmentation=dict(
            reference_records=len(refs),
            passive_segments=len(all_segments),
            nonempty_overlap=fraction(sum(bool(r["edges"]) for r in rows), len(refs)),
            exact_boundaries=fraction(exact, len(refs)),
            oversegmented_references=sum(r["fragmentation"] > 1 for r in rows),
            segments_overlapping_multiple_references=multi,
            coverage_unit="Unicode characters in frozen text views; PDF not visual geometry",
        ),
        records=rows,
        per_document=per_document,
        discovery=matrix(rows, "discovery_label", "discovery"),
        broad_relevance=dict(
            unit="reference_record",
            denominator=len(rows),
            matrix=dict(
                Counter(
                    str(
                        (
                            r["reference"]["discovery_label"] in RELEVANT,
                            None
                            if not r["representative_prediction"]
                            or r["representative_prediction"]["discovery"] == "abstain"
                            else r["representative_prediction"]["discovery"] in RELEVANT,
                        )
                    )
                    for r in rows
                )
            ),
        ),
        modality=matrix(rows, "modality", "modality"),
        temporal=matrix(rows, "temporal_status", "temporal"),
        temporal_expression_roles=dict(
            Counter(
                f["name"]
                for f in extracted
                if "date" in f["name"] or "deadline" in f["name"] or "temporal" in f["name"]
            )
        ),
        field_summary=dict(
            unit="provisional_reference_field",
            denominator=fields_total,
            strict_role_value=fraction(strict_count, fields_total),
            diagnostic_candidates={k: field_counts[k] for k in STATUSES},
            unsupported_target_roles=sum(
                not f["scope_supported"] for r in rows for f in r["fields"]
            ),
            missing_reference_fields_in_denominator=True,
        ),
        extracted_claims=extracted,
        locator_integrity=dict(
            occurrences=bundle.locator_occurrences,
            unique_locators=bundle.unique_locators,
            verified_occurrences=bundle.locator_occurrences,
            invalid=0,
            semantic_entailment_implied=False,
        ),
        semantic_evidence=dict(
            reviewed_claims=0, unreviewed_field_claims=len(extracted), judgments={}
        ),
        abstention=dict(
            unit="passive_segment",
            denominator=len(all_segments),
            count=len(abstained),
            rate=fraction(len(abstained), len(all_segments)),
            overlapping_references=sum((d, s.segment_id) in owners for d, s in abstained),
            outside_reference_scope=sum((d, s.segment_id) not in owners for d, s in abstained),
            explicit_field_abstentions=0,
            diagnostics=dict(Counter(code for _, s in abstained for code in s.diagnostics)),
            note=(
                "Discovery abstention is not field abstention, missing opportunity "
                "or proof of missing source information"
            ),
        ),
        unannotated_segments_not_negatives=unannotated,
    )
    result["modality_strata"] = {
        mode: dict(
            reference_records=sum(r["reference"]["modality"] == mode for r in rows),
            discovery=matrix(
                [r for r in rows if r["reference"]["modality"] == mode],
                "discovery_label",
                "discovery",
            ),
            modality=matrix(
                [r for r in rows if r["reference"]["modality"] == mode], "modality", "modality"
            ),
            fields=dict(
                Counter(
                    f["status"]
                    for r in rows
                    if r["reference"]["modality"] == mode
                    for f in r["fields"]
                )
            ),
        )
        for mode in ("fomento", "credito", "investimentos", "undetermined")
    }
    result["temporal"]["applicable_reference_records"] = sum(
        r["reference"]["temporal_status"] != "not_applicable" for r in rows
    )
    result["temporal"]["not_applicable_reference_records"] = sum(
        r["reference"]["temporal_status"] == "not_applicable" for r in rows
    )
    result["temporal"]["open_vs_known_nonopen"] = [
        r["record_id"]
        for r in rows
        if r["representative_prediction"]
        and r["representative_prediction"]["temporal"] == "open"
        and r["reference"]["temporal_status"] in {"closed", "future", "not_applicable"}
    ]
    result["temporal"]["open_vs_unknown"] = [
        r["record_id"]
        for r in rows
        if r["representative_prediction"]
        and r["representative_prediction"]["temporal"] == "open"
        and r["reference"]["temporal_status"] == "undetermined"
    ]
    if sum(field_counts.values()) != fields_total or any(
        sum(sum(v.values()) for v in result[task]["matrix"].values()) != len(refs)
        for task in ("discovery", "modality", "temporal")
    ):
        raise EvaluationFault("denominator_inconsistency")
    return result, timings


def evaluate(
    root: Path,
    frozen: Path,
    binding_raw: bytes,
    *,
    schema_version: str = VERSION,
    semantic_reviews_raw: bytes | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    t = perf_counter()
    try:
        if schema_version != VERSION:
            raise EvaluationFault("unsupported_evaluation_schema")
        if len(binding_raw) > 65536:
            raise EvaluationFault("binding_size_limit")
        binding = Binding.model_validate_json(json.dumps(parse(binding_raw)))
        bundle = load_bundle(root, frozen, binding)
        body, timings = calculate(bundle)
        if semantic_reviews_raw is not None:
            from .reviews import apply_reviews

            apply_reviews(bundle, body, semantic_reviews_raw)
        timings["total_seconds"] = perf_counter() - t
        return dict(
            schema_version=VERSION, status="evaluated", diagnostics=[], results=body
        ), timings
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        if isinstance(exc, EvaluationFault):
            code, location = exc.code, exc.location
        elif isinstance(exc, ValidationError):
            code, location = (
                "schema_or_reference_invalid",
                str(exc.errors(include_input=False)[0]["loc"]),
            )
        else:
            code, location = "invalid_evaluation_input", type(exc).__name__
        return dict(
            schema_version=VERSION,
            status="invalid_input",
            diagnostics=[dict(code=code, location=location)],
            results=None,
        ), dict(total_seconds=perf_counter() - t)
