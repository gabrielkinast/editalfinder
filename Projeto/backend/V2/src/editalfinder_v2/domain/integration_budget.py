"""Conservative, allocation-light admission for the existing expanded report DTOs.

This is a byte-equivalent output/work budget, not an OS RSS guarantee. No report
is built or serialized to decide admission. Unknown shapes, cycles and excessive
traversal fail closed. Input transport/deserialization still needs its own limits.

A snapshot occurs up to eight times per candidate (batch input, candidate input,
five normalization inputs, M1) and once for each side of each identity result.
Non-snapshot input is charged 16-fold for normalized DTOs, evidence, diagnostics,
audits and serializer envelopes, plus 16 times the largest same-field assertion
count to cover M1's field-evidence diagnostic fan-out. Each result also reserves
64 KiB for fixed fields/messages. String charging uses six bytes per code point
plus scalar overhead, covering default UTF-8 JSON escaping without encoding
a large string. Custom ASCII-escaping/pretty-print options are not this budget.
These are deliberately pessimistic admission charges, not output compression.

M2.3b uses the existing reserves: temporal/taxonomy proofs gain at most three
additional observations per claim; financial proofs one. Shared scope and
organization witness repetition use the existing field-fanout reserve. Qualified
references, versions and fixed messages use body/fixed reserves, never snapshots.
The admission formula and its version are unchanged; no limit is relaxed.

Keep these charges in sync with any future report layout or diagnostic policy.
M1/M2 DTOs, normalization rules and integrity algorithms are not modified.
"""

from collections import Counter
from collections.abc import Iterator, Mapping
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel

from .models import FieldAssertion
from .semantic_common import MAX_NORMALIZATION_CLAIMS

OUTPUT_BUDGET_VERSION = "m2.3a.1-output-budget-v1"
MAX_OUTPUT_BUDGET = 64 * 1024 * 1024
MAX_BUDGET_NODES = 100_000
MAX_BUDGET_DEPTH = 64
RESULT_RESERVE = 64 * 1024
BODY_MULTIPLIER = 16
FIELD_FANOUT_MULTIPLIER = 16
SNAPSHOT_MULTIPLICITY = 8


def _field(value: object, name: str) -> object:
    if isinstance(value, BaseModel):
        return getattr(value, name, None)
    if isinstance(value, Mapping):
        return value.get(name)
    return None


def _sequence(value: object) -> tuple[object, ...] | list[object]:
    return value if isinstance(value, (tuple, list)) else ()


def wire_cost(value: object, *, omit_snapshots: bool = False) -> int:
    """Saturating structural charge; no model_dump, json.dumps or UTF-8 buffer.

    Memoization saves traversal, NOT multiplicity: every occurrence adds its full
    charge. An active-path set rejects cycles in raw Python transport mappings.
    Node/depth ceilings bound the estimator itself, independently of input size.
    """
    ceiling = MAX_OUTPUT_BUDGET + 1
    memo: dict[int, int] = {}
    active: set[int] = set()
    nodes = 0

    def visit(item: object, depth: int) -> int:
        nonlocal nodes
        nodes += 1
        if nodes > MAX_BUDGET_NODES or depth > MAX_BUDGET_DEPTH:
            return ceiling
        if isinstance(item, str):
            return min(ceiling, 6 * len(item) + 64)
        if isinstance(item, UUID):
            return 6 * 36 + 64
        if isinstance(item, datetime):
            return 6 * 64 + 64
        if isinstance(item, date):
            return 6 * 10 + 64
        if item is None or isinstance(item, (bool, float, Enum)):
            return 128
        if isinstance(item, int):
            return min(ceiling, item.bit_length() + 64)
        if isinstance(item, Decimal):
            # Decimal JSON is textual. Do not expand exponents to fixed notation.
            parts = item.as_tuple()
            return min(ceiling, 6 * (len(parts.digits) + len(str(parts.exponent)) + 16) + 64)
        key = id(item)
        if key in active:
            return ceiling
        if key in memo:
            return memo[key]
        active.add(key)
        total = 64
        entries: Iterator[tuple[object, object]]
        if isinstance(item, BaseModel):
            entries = ((name, getattr(item, name)) for name in type(item).model_fields)
        elif isinstance(item, Mapping):
            entries = iter(item.items())
        elif isinstance(item, (tuple, list)):
            entries = ((None, child) for child in item)
        else:
            active.remove(key)
            return ceiling
        for name, child in entries:
            if omit_snapshots and name == "snapshots":
                continue
            if name is not None:
                if not isinstance(name, str):
                    total = ceiling
                    break
                total += 6 * len(name) + 64
            if isinstance(item, FieldAssertion) and name == "value":
                # M1's JSON serializer adds {kind,data}. Charge container, keys,
                # longest tag and child separators without temporary memoized DTOs.
                total += 64 + 2 * (6 * 4 + 64) + (6 * 7 + 64) + 2 * 16
                total += visit(child, depth + 2) + 16
            else:
                total += visit(child, depth + 1) + 16
            if total >= ceiling:
                total = ceiling
                break
        active.remove(key)
        memo[key] = total
        return total

    return visit(value, 0)


def integration_claim_count(item: object) -> int:
    """Same resource count used by orchestration and its output forecast."""
    return (
        sum(
            len(_sequence(_field(item, name)))
            for name in (
                "identifiers",
                "temporal",
                "geography",
                "financial",
                "organizations",
                "taxonomy",
            )
        )
        + int(_field(item, "cycle") is not None)
        + int(_field(item, "geographic_scope") is not None)
    )


def projected_output_cost(data: object) -> int:
    """Charge all candidate and requested-pair repetitions before domain reports."""
    ceiling = MAX_OUTPUT_BUDGET + 1
    total = RESULT_RESERVE
    candidates = _sequence(_field(data, "candidates"))
    pairs = _sequence(_field(data, "identity_comparisons"))
    if len(candidates) > 32 or len(pairs) > 64:
        return ceiling
    bodies: list[int] = []
    snapshots: list[int] = []
    snapshot_cache: dict[int, int] = {}
    for item in candidates:
        candidate = _field(_field(item, "context"), "candidate")
        counts = Counter(
            field
            for assertion in _sequence(_field(candidate, "assertions"))
            if isinstance(field := _field(assertion, "field"), str)
        )
        factor = BODY_MULTIPLIER + FIELD_FANOUT_MULTIPLIER * max(counts.values(), default=0)
        # This resource count guarantees prepare_context returns OperationalError:
        # only the original input remains in the outer report, never domain output.
        # Import its ceiling rather than introducing a second normalization policy.
        if integration_claim_count(item) > MAX_NORMALIZATION_CLAIMS:
            factor = 1
        body = wire_cost(item, omit_snapshots=True) * factor
        snapshot_cost = 0
        for snapshot in _sequence(_field(_field(item, "context"), "snapshots")):
            key = id(snapshot)
            if key not in snapshot_cache:
                snapshot_cache[key] = wire_cost(snapshot)
            snapshot_cost += snapshot_cache[key]
            if snapshot_cost > MAX_OUTPUT_BUDGET:
                return ceiling
        total += RESULT_RESERVE + body + SNAPSHOT_MULTIPLICITY * snapshot_cost
        if total > MAX_OUTPUT_BUDGET:
            return ceiling
        bodies.append(body)
        snapshots.append(snapshot_cost)
    for pair in pairs:
        total += RESULT_RESERVE
        for name in ("left_index", "right_index"):
            index = _field(pair, name)
            if type(index) is int and 0 <= index < len(candidates):
                total += bodies[index] + snapshots[index]
        if total > MAX_OUTPUT_BUDGET:
            return ceiling
    return total
