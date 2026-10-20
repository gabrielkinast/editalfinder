"""Synthetic structured source records, manually reviewed; not an editorial gold set."""

import json
from datetime import UTC, date, datetime
from uuid import UUID

from editalfinder_v2.domain.models import (
    DocumentUnit,
    Evidence,
    FieldAssertion,
    OpportunityCandidate,
    RawSnapshot,
)


def example(
    *,
    kind: str = "instrument",
    deadline: date | None = date(2026, 12, 1),
    reason: str | None = None,
) -> tuple[RawSnapshot, OpportunityCandidate]:
    values: dict[str, str | bool | date | None] = {
        "title": "Edital 01/2026",
        "official_url": "https://example.org/call/1",
        "content_kind": kind,
        "specific_instrument": kind == "instrument",
        "actionable": kind == "instrument",
        "submission_deadline": deadline,
    }
    if reason is not None:
        values["no_deadline_reason"] = reason
    payload = {
        key: value.isoformat() if type(value) is date else value for key, value in values.items()
    }
    snapshot = RawSnapshot(
        id=UUID(int=1),
        source_code="fapergs",
        source_id=UUID(int=2),
        execution_id=UUID(int=3),
        collected_at=datetime(2026, 1, 1, tzinfo=UTC),
        collector_version="fixture-1",
        url="https://example.org/call/1",
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    candidate = OpportunityCandidate(
        id=UUID(int=4),
        source_code="fapergs",
        source_id=snapshot.source_id,
        unit=DocumentUnit(snapshot_id=snapshot.id, pointer=""),
        assertions=tuple(
            FieldAssertion(
                field=key,
                value=value,
                evidence=()
                if value is None
                else (
                    Evidence(
                        snapshot_id=snapshot.id,
                        unit=DocumentUnit(snapshot_id=snapshot.id, pointer=""),
                        semantic_role=key,
                        pointer="/" + key,
                        quote=payload[key]
                        if isinstance(payload[key], str)
                        else json.dumps(payload[key]),
                        method="manual_review",
                        method_version="1",
                        confidence="1",
                    ),
                ),
            )
            for key, value in values.items()
        ),
    )
    return snapshot, candidate


def with_field(snapshot, candidate, field, value):
    """Change a single structured field and its exact proof, not unrelated evidence."""
    payload = json.loads(snapshot.payload_json)
    payload[field] = value.isoformat() if type(value) is date else value
    snapshot = RawSnapshot.model_validate(
        {
            **snapshot.model_dump(exclude={"audit"}),
            "payload_json": json.dumps(payload),
        }
    )
    assertion = FieldAssertion(
        field=field,
        value=value,
        evidence=()
        if value is None
        else (
            Evidence(
                snapshot_id=snapshot.id,
                unit=candidate.unit,
                semantic_role=field,
                pointer="/" + field,
                quote=payload[field] if type(payload[field]) is str else json.dumps(payload[field]),
                method="structured_field",
                method_version="fixture-1",
                confidence="1",
            ),
        ),
    )
    candidate = OpportunityCandidate.model_validate(
        {
            **candidate.model_dump(),
            "assertions": tuple(a for a in candidate.assertions if a.field != field) + (assertion,),
        }
    )
    return snapshot, candidate


def multiple_candidates() -> tuple[RawSnapshot, tuple[OpportunityCandidate, ...]]:
    instrument_snapshot, instrument = example()
    news_snapshot, news = example(kind="news")
    snapshot = RawSnapshot.model_validate(
        {
            **instrument_snapshot.model_dump(exclude={"audit"}),
            "url": "https://example.org/listing",
            "payload_json": json.dumps(
                {
                    "records": [
                        json.loads(instrument_snapshot.payload_json),
                        json.loads(news_snapshot.payload_json),
                    ]
                }
            ),
        }
    )
    candidates = tuple(
        OpportunityCandidate.model_validate(
            {
                **candidate.model_dump(),
                "id": UUID(int=4 + index),
                "unit": DocumentUnit(snapshot_id=snapshot.id, pointer=f"/records/{index}"),
                "assertions": tuple(
                    FieldAssertion.model_validate(
                        {
                            **assertion.model_dump(),
                            "evidence": tuple(
                                Evidence.model_validate(
                                    {
                                        **evidence.model_dump(),
                                        "pointer": f"/records/{index}" + evidence.pointer,
                                        "unit": DocumentUnit(
                                            snapshot_id=snapshot.id, pointer=f"/records/{index}"
                                        ),
                                    }
                                )
                                for evidence in assertion.evidence
                            ),
                        }
                    )
                    for assertion in candidate.assertions
                ),
            }
        )
        for index, candidate in enumerate((instrument, news))
    )
    return snapshot, candidates
