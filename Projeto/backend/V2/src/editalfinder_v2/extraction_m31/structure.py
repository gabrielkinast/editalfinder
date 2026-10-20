"""Reusable structural segmentation. No known document or reference record IDs."""

import re
from dataclasses import dataclass

from .reader import Block, InputDocument, InputFailure


@dataclass(frozen=True)
class Unit:
    start: int
    end: int
    blocks: tuple[Block, ...]
    method: str


def segment(document: InputDocument) -> tuple[Unit, ...]:
    """Call listings group heading-local content; all other data nodes stay local.

    A paragraph fallback intentionally oversegments instead of borrowing from
    unrelated neighboring instruments. Unclassified blocks remain abstentions.
    """
    active = [b for b in document.blocks if not b.excluded]
    units: list[Unit] = []
    i = 0
    while i < len(active):
        b = active[i]
        value = document.text[b.start : b.end]
        if b.end - b.start > 20000:
            raise InputFailure("segment_size_limit")
        listing = b.heading and bool(re.match(r"Chamada\b", value, re.I))
        end = i + 1
        if listing:
            owner = b.containers[-1] if b.containers else None
            while end < len(active) and not active[end].heading and active[end].page == b.page:
                if owner is None or owner not in active[end].containers:
                    break
                if active[end].end - b.start > 20000:
                    raise InputFailure("segment_size_limit")
                end += 1
        blocks = tuple(active[i:end])
        units.append(
            Unit(
                b.start,
                blocks[-1].end,
                blocks,
                "call-heading-local-v1" if listing else "passive-block-local-v1",
            )
        )
        i = end
    if len(units) > 3000:
        raise InputFailure("segment_count_limit")
    return tuple(units)
