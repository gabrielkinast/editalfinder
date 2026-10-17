"""Domain invariants and the offline boundary; all fixtures are synthetic."""

import ast
import builtins
import socket
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest
from fixtures import example
from pydantic import ValidationError

from editalfinder_v2.domain.models import Evidence, RawSnapshot, ValidationReport
from editalfinder_v2.domain.validation import evidence_matches, validate


def test_snapshot_requires_timezone_and_stores_utc():
    snapshot, _ = example()
    data = snapshot.model_dump(exclude={"audit"})
    with pytest.raises(ValidationError):
        RawSnapshot.model_validate({**data, "collected_at": datetime(2026, 1, 1)})
    utc = RawSnapshot.model_validate({**data, "collected_at": "2026-01-01T03:00:00+03:00"})
    assert utc.collected_at.isoformat() == "2026-01-01T00:00:00+00:00"


@pytest.mark.parametrize("confidence", ["-0.1", "1.1", "NaN", "Infinity"])
def test_invalid_confidence_is_not_coerced(confidence):
    snapshot, candidate = example()
    evidence = candidate.assertions[0].evidence[0]
    with pytest.raises(ValidationError):
        Evidence.model_validate({**evidence.model_dump(), "confidence": confidence})


def test_snapshot_has_reproducible_content_digest():
    import hashlib

    snapshot, _ = example()
    assert (
        snapshot.hash_payload == hashlib.sha256(snapshot.payload_json.encode("utf-8")).hexdigest()
    )
    assert snapshot.hash_version == "sha256-utf8-v1"


def test_contracts_are_frozen_and_reject_unknown_properties():
    snapshot, _ = example()
    with pytest.raises(ValidationError):
        snapshot.source_code = "other"
    with pytest.raises(ValidationError):
        RawSnapshot.model_validate({**snapshot.model_dump(exclude={"audit"}), "unexpected": 1})


@pytest.mark.parametrize(
    "pointer,quote,expected",
    [
        ("/a~1b/~0key/0", "call", True),
        ("/a~1b/~0key/00", "call", False),
        ("/a~1b/~0key/1", "call", False),
        ("/a~1b/~0key/-1", "call", False),
        ("/a~2b", "call", False),
        ("missing", "call", False),
        ("", "call", False),
    ],
)
def test_json_pointer_verification(pointer, quote, expected):
    evidence = Evidence(
        snapshot_id=UUID(int=1),
        pointer=pointer,
        quote=quote,
        method="manual_review",
        method_version="1",
        confidence="1",
    )
    assert evidence_matches(evidence, {"a/b": {"~key": ["official call"]}}) is expected


def test_engine_needs_no_filesystem_or_network(monkeypatch):
    from datetime import date

    snapshot, candidate = example()

    def forbidden(*args, **kwargs):
        raise AssertionError("I/O attempted")

    monkeypatch.setattr(builtins, "open", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    report = validate(candidate, (snapshot,), reference_date=date(2026, 6, 1))
    assert isinstance(report, ValidationReport)
    assert not report.promotable
    assert any(i.code == "trusted_review_required" for i in report.issues)


def test_domain_imports_only_stdlib_pydantic_and_own_modules():
    import sys

    root = Path(__file__).parents[1] / "src" / "editalfinder_v2"
    allowed = sys.stdlib_module_names | {"pydantic"}
    for path in root.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                assert all(a.name.split(".")[0] in allowed for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                assert node.module.split(".")[0] in allowed


@pytest.mark.parametrize("value", [1, 0, 1.0])
def test_boolean_claims_do_not_coerce_numbers(value):
    from editalfinder_v2.domain.models import FieldAssertion

    with pytest.raises(ValidationError):
        FieldAssertion(field="actionable", value=value)
