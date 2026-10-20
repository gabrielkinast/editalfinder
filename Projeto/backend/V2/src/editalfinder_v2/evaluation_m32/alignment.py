"""Same-document geometric relationship graph, never canonical identity matching."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Located:
    document_id: str
    identifier: str
    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0 or self.end <= self.start:
            raise ValueError("invalid_span")


def fraction(numerator: int, denominator: int) -> dict[str, Any]:
    if not 0 <= numerator <= denominator:
        raise ValueError("invalid_denominator")
    return dict(
        numerator=numerator,
        denominator=denominator,
        value=numerator / denominator if denominator else None,
    )


def align(
    references: tuple[Located, ...], predictions: tuple[Located, ...]
) -> list[dict[str, Any]]:
    for items in (references, predictions):
        keys = [(s.document_id, s.identifier) for s in items]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate_location_id")
    by_document: dict[str, list[Located]] = {}
    for s in predictions:
        by_document.setdefault(s.document_id, []).append(s)
    rows: list[dict[str, Any]] = []
    for ref in references:
        edges: list[dict[str, Any]] = []
        for s in by_document.get(ref.document_id, []):
            start, end = max(ref.start, s.start), min(ref.end, s.end)
            if end <= start:
                continue
            intersection = end - start
            edges.append(
                dict(
                    segment_id=s.identifier,
                    start=s.start,
                    end=s.end,
                    intersection_start=start,
                    intersection_end=end,
                    intersection=intersection,
                    iou=intersection / (ref.end - ref.start + s.end - s.start - intersection),
                    predicted_purity=intersection / (s.end - s.start),
                    reference_fraction=intersection / (ref.end - ref.start),
                    exact=(ref.start, ref.end) == (s.start, s.end),
                )
            )
        edges.sort(key=lambda e: (e["start"], e["end"], e["segment_id"]))
        covered, cursor = 0, ref.start
        for edge in edges:
            a, b = edge["intersection_start"], edge["intersection_end"]
            covered += max(0, b - max(a, cursor))
            cursor = max(cursor, b)
        representative = (
            min(edges, key=lambda e: (-e["intersection"], e["start"], e["end"], e["segment_id"]))
            if edges
            else None
        )
        rows.append(
            dict(
                record_id=ref.identifier,
                document_id=ref.document_id,
                start=ref.start,
                end=ref.end,
                edges=edges,
                representative=representative["segment_id"] if representative else None,
                covered_characters=covered,
                reference_characters=ref.end - ref.start,
                coverage=fraction(covered, ref.end - ref.start),
                fragmentation=len(edges),
                any_exact_boundary=any(e["exact"] for e in edges),
            )
        )
    return rows
