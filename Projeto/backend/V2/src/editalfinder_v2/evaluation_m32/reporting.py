"""Traceable diagnostic ledger and adjudication queue, not revised source labels."""

from typing import Any


def diagnostics(result: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for row in result["records"]:
        for dimension in row["disagreements"]:
            code = {
                "discovery_label": "OPPORTUNITY_EXISTENCE_CONFUSION",
                "modality": "MODALITY_CONFUSION",
                "temporal_status": "TEMPORAL_AVAILABILITY_INFERENCE",
            }[dimension]
            predicted = row["representative_prediction"]
            high = bool(
                predicted
                and (
                    dimension == "discovery_label"
                    and predicted["discovery"] == "confirmed_opportunity"
                    or dimension == "temporal_status"
                    and predicted["temporal"] == "open"
                )
            )
            quote = row["representative_quote"] or row["reference_evidence"][0]["quote"]
            start = predicted["start"] if predicted else row["reference_evidence"][0]["start"]
            cases.append(
                dict(
                    case_id=row["record_id"] + ":" + dimension,
                    error_codes=[code, "REFERENCE_AMBIGUITY"],
                    severity="high" if high else "medium",
                    document_id=row["document_id"],
                    record_id=row["record_id"],
                    segment_id=predicted["segment_id"] if predicted else None,
                    dimension=dimension,
                    certainty="unresolved_disagreement",
                    review_status="provisional",
                    supporting_evidence=dict(
                        start=start, end=start + min(len(quote), 1200), quote=quote[:1200]
                    ),
                    reference=row["reference"],
                    observed=predicted,
                    expected_behavior=(
                        "Resolve this dimension from same-record evidence; provisional "
                        "label is comparison, not authority."
                    ),
                    root_cause=(
                        "Context fragmentation or semantic rule/reference ambiguity; see "
                        "all-overlap graph before adjudication."
                    ),
                    root_cause_confidence="low",
                    next_action=(
                        "Compare full frozen context and request authorized adjudication; "
                        "do not rewrite labels."
                    ),
                )
            )
        if row["fragmentation"] != 1 or not row["any_exact_boundary"]:
            cases.append(
                dict(
                    case_id=row["record_id"] + ":segmentation",
                    error_codes=[
                        "SEGMENTATION_OVER"
                        if row["fragmentation"] > 1
                        else "EXTRACTION_OMISSION"
                        if not row["fragmentation"]
                        else "SEGMENTATION_BOUNDARY"
                    ],
                    severity="medium",
                    document_id=row["document_id"],
                    record_id=row["record_id"],
                    segment_id=row["representative"],
                    dimension="structural",
                    certainty="supported_observation",
                    review_status="provisional",
                    supporting_evidence=dict(
                        reference_span=[row["start"], row["end"]], edges=row["edges"]
                    ),
                    reference=row["reference"],
                    observed=dict(fragmentation=row["fragmentation"], coverage=row["coverage"]),
                    expected_behavior=(
                        "A meaningful record should retain its own associated context; "
                        "whitespace-only boundary differences are not semantic defects."
                    ),
                    root_cause=(
                        "Structure-derived units differ from provisional annotated record spans."
                    ),
                    root_cause_confidence="high",
                    next_action=(
                        "Inspect semantic usefulness of boundaries before changing segmentation."
                    ),
                )
            )
    for item in result["semantic_evidence"].get("cases", []):
        if not item["error_codes"]:
            continue
        cases.append(
            dict(
                item,
                observed=item["expected_claim"],
                review_status="provisional",
                supporting_evidence=dict(start=item["start"], end=item["end"], quote=item["quote"]),
            )
        )
    by_record = {r["record_id"]: r for r in result["records"]}
    queue = []
    severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    for case in cases:
        if case["certainty"] == "supported_observation" and case.get("dimension") == "structural":
            continue
        record = by_record.get(case.get("record_id"))
        queue.append(
            dict(
                item_id="adjudicate:" + case["case_id"],
                document_id=case["document_id"],
                record_id=case.get("record_id"),
                segment_id=case.get("segment_id"),
                frozen_source_evidence=case["supporting_evidence"],
                reference_label=record["reference"] if record else None,
                prediction=case["observed"],
                error_codes=case["error_codes"],
                proposed_severity=case["severity"],
                question=(
                    "Does the frozen context support the asserted role/stage/access for "
                    "this audience, or should prediction/reference remain unresolved? "
                )
                + case.get("rationale", ""),
                current_review_status="provisional_pending_authorized_adjudication",
                machine_locator_validity_is_not_semantic_approval=True,
            )
        )
    queue.sort(
        key=lambda q: (severity_order[q["proposed_severity"]], q["document_id"], q["item_id"])
    )
    return dict(
        schema_version="m32-error-cases-v1", trust_status="PROVISIONAL / EXPLORATORY", cases=cases
    ), dict(schema_version="m32-review-queue-v1", review_status="provisional", items=queue)
