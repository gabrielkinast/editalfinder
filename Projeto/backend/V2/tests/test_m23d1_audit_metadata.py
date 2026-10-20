"""F03: received envelopes require every field; new evaluation is a different operation."""

import copy
import hashlib
import json
from functools import lru_cache

import pytest
from m23c_fixtures import build, case_by_id
from pydantic import ValidationError

from editalfinder_v2.domain.identity_models import IdentityAudit
from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import (
    IntegrationAudit,
    IntegrationInput,
    IntegrationReport,
)
from editalfinder_v2.domain.m22b_common import M22BAudit
from editalfinder_v2.domain.models import SnapshotAudit, ValidationAudit
from editalfinder_v2.domain.semantic_common import NormalizationAudit

# Literal contract inventory, not generated from the implementation's required/default flags.
FIELDS = {
    SnapshotAudit: (
        "schema_version",
        "snapshot_id",
        "payload_digest",
        "algorithm",
        "hash_version",
        "representation",
        "contract_version",
    ),
    ValidationAudit: (
        "schema_version",
        "audit_version",
        "validation_limits_version",
        "report_digest",
        "report_hash_version",
        "contract_version",
        "candidate_id",
        "candidate_digest",
        "evidence_digests",
        "snapshots",
        "catalog_version",
        "ruleset_version",
        "rule_versions",
        "algorithm",
        "hash_version",
    ),
    IdentityAudit: (
        "schema_version",
        "report_digest",
        "algorithm",
        "hash_version",
        "limits_version",
    ),
    NormalizationAudit: (
        "schema_version",
        "report_digest",
        "algorithm",
        "hash_version",
        "limits_version",
    ),
    M22BAudit: ("schema_version", "report_digest", "algorithm", "hash_version", "limits_version"),
    IntegrationAudit: (
        "schema_version",
        "output_budget_version",
        "report_digest",
        "algorithm",
        "hash_version",
        "limits_version",
    ),
}


@lru_cache(maxsize=2)
def report(case="M23C-A-001"):
    result = integrate(build(case_by_id(case)))
    assert isinstance(result, IntegrationReport)
    return result


def at(value, path):
    for key in path:
        value = value[key]
    return value


def construct(model, data, route):
    if route == "direct":
        return model(**data)
    if route == "python":
        return model.model_validate(data)
    return model.model_validate_json(json.dumps(data))


# Each path selects one representative occurrence, including audits inside M1.audit.snapshots.
TARGETS = (
    (
        "input_snapshot",
        "M23C-A-001",
        ("input", "candidates", 0, "context", "snapshots", 0),
        SnapshotAudit,
    ),
    (
        "candidate_snapshot",
        "M23C-A-001",
        ("candidates", 0, "input", "context", "snapshots", 0),
        SnapshotAudit,
    ),
    (
        "validation_snapshot",
        "M23C-A-001",
        ("candidates", 0, "validation", "snapshots", 0),
        SnapshotAudit,
    ),
    ("validation", "M23C-A-001", ("candidates", 0, "validation"), ValidationAudit),
    ("temporal", "M23C-A-001", ("candidates", 0, "normalizations", "temporal"), NormalizationAudit),
    (
        "geography",
        "M23C-A-001",
        ("candidates", 0, "normalizations", "geography"),
        NormalizationAudit,
    ),
    ("financial", "M23C-A-001", ("candidates", 0, "normalizations", "financial"), M22BAudit),
    (
        "organizations",
        "M23C-A-001",
        ("candidates", 0, "normalizations", "organizations"),
        M22BAudit,
    ),
    ("taxonomy", "M23C-A-001", ("candidates", 0, "normalizations", "taxonomy"), M22BAudit),
    ("identity", "M23C-I-005", ("identity_results", 0), IdentityAudit),
    ("integration", "M23C-A-001", (), IntegrationAudit),
)


def audit_examples():
    r = report()
    return {
        SnapshotAudit: r.input.candidates[0].context.snapshots[0].audit,
        ValidationAudit: r.candidates[0].validation.audit,
        IdentityAudit: report("M23C-I-005").identity_results[0].audit,
        NormalizationAudit: r.candidates[0].normalizations.temporal.audit,
        M22BAudit: r.candidates[0].normalizations.financial.audit,
        IntegrationAudit: r.audit,
    }


@pytest.mark.parametrize("model", FIELDS)
@pytest.mark.parametrize("route", ["direct", "python", "json"])
def test_every_received_audit_field_is_explicitly_required(model, route):
    original = audit_examples()[model]
    data = original.model_dump(mode="json" if route == "json" else "python")
    assert set(model.model_fields) == set(FIELDS[model])
    assert construct(model, data, route) == original
    for field in FIELDS[model]:
        raw = copy.deepcopy(data)
        del raw[field]
        with pytest.raises(ValidationError) as exc:
            construct(model, raw, route)
        assert any(e["loc"] == (field,) and e["type"] == "missing" for e in exc.value.errors())


@pytest.mark.parametrize("name,case,path,model", TARGETS, ids=[t[0] for t in TARGETS])
@pytest.mark.parametrize("route", ["direct", "python", "json"])
def test_missing_nested_metadata_rejected_with_retained_outer_audit(name, case, path, model, route):
    original = report(case)
    data = original.model_dump(mode="json" if route == "json" else "python")
    for field in FIELDS[model]:
        raw = copy.deepcopy(data)
        del at(raw, path)["audit"][field]
        with pytest.raises(ValidationError) as exc:
            construct(IntegrationReport, raw, route)
        assert any(e["type"] == "missing" and e["loc"][-1] == field for e in exc.value.errors())
        assert raw.get("audit") == data.get("audit") or not path  # top audit itself is the target


@pytest.mark.parametrize("route", ["direct", "python", "json"])
def test_snapshot_metadata_inside_validation_audit_is_also_required(route):
    data = report().model_dump(mode="json" if route == "json" else "python")
    for field in FIELDS[SnapshotAudit]:
        raw = copy.deepcopy(data)
        del raw["candidates"][0]["validation"]["audit"]["snapshots"][0][field]
        with pytest.raises(ValidationError) as exc:
            construct(IntegrationReport, raw, route)
        assert any(e["type"] == "missing" and e["loc"][-1] == field for e in exc.value.errors())


@pytest.mark.parametrize("name,case,path,model", TARGETS, ids=[t[0] for t in TARGETS])
def test_complete_standalone_reports_roundtrip_and_without_audit_generate_local_audits(
    name, case, path, model
):
    r = report(case)
    target = r
    for key in path:
        target = target[key] if isinstance(key, int) else getattr(target, key)
    assert target.audit is not None
    assert type(target).model_validate_json(target.model_dump_json()) == target
    data = target.model_dump()
    data["audit"] = None
    assert type(target).model_validate(data) == target
    del data["audit"]
    assert type(target).model_validate(data) == target
    assert not getattr(target, "promotable", False)


@pytest.mark.parametrize("name,case,path,model", TARGETS, ids=[t[0] for t in TARGETS])
def test_supplied_audit_tampering_still_rejected(name, case, path, model):
    data = json.loads(report(case).model_dump_json())
    audit = at(data, path)["audit"]
    key = "payload_digest" if model is SnapshotAudit else "report_digest"
    audit[key] = "f" * 64
    with pytest.raises(ValidationError):
        IntegrationReport.model_validate_json(json.dumps(data))


# Policy/schema versions live on several report bodies, not inside their audit DTO.
# A retained audit cannot justify inventing omitted body metadata either.
@pytest.mark.parametrize("name,case,path,model", TARGETS, ids=[t[0] for t in TARGETS])
@pytest.mark.parametrize("route", ["direct", "python", "json"])
def test_received_report_policy_versions_are_not_backfilled(name, case, path, model, route):
    original = report(case)
    raw_base = original.model_dump(mode="json" if route == "json" else "python")
    body = at(raw_base, path)
    versions = [key for key in body if key.endswith("_version")]
    assert versions
    for field in versions:
        raw = copy.deepcopy(raw_base)
        del at(raw, path)[field]
        with pytest.raises(ValidationError):
            construct(IntegrationReport, raw, route)


@pytest.mark.parametrize("model", FIELDS)
def test_received_audit_null_fields_and_unknown_metadata_are_not_local_generation(model):
    data = audit_examples()[model].model_dump(mode="json")
    for field in FIELDS[model]:
        raw = copy.deepcopy(data)
        raw[field] = None
        with pytest.raises(ValidationError):
            model.model_validate_json(json.dumps(raw))
    with pytest.raises(ValidationError) as exc:
        model.model_validate(dict(data, trusted_review=True))
    assert any(e["type"] == "extra_forbidden" for e in exc.value.errors())


@pytest.mark.parametrize(
    "name,case,path,model", [t for t in TARGETS if t[2]], ids=[t[0] for t in TARGETS if t[2]]
)
def test_absent_outer_audit_does_not_repair_supplied_incomplete_nested_envelopes(
    name, case, path, model
):
    data = report(case).model_dump()
    data["audit"] = None
    del at(data, path)["audit"]["hash_version"]
    with pytest.raises(ValidationError):
        IntegrationReport.model_validate(data)


def test_local_recomputation_keeps_complete_deterministic_reports():
    data = build(case_by_id("M23C-I-005"))
    first, second = integrate(data), integrate(data)
    assert first.model_dump_json() == second.model_dump_json()
    assert first == report("M23C-I-005")
    assert not first.promotable


def test_explicit_reprocessing_preserves_incomplete_archival_output_envelope():
    archived = json.loads(report("M23C-I-005").model_dump_json())
    del archived["identity_results"][0]["audit"]["hash_version"]
    source_bytes = json.dumps(archived).encode()
    before = hashlib.sha256(source_bytes).hexdigest()
    with pytest.raises(ValidationError):
        IntegrationReport.model_validate_json(source_bytes)
    # Approved input-only reprocessing: outputs and archival envelope are NOT verified.
    current_input = IntegrationInput.model_validate_json(json.dumps(archived["input"]))
    new = integrate(current_input)
    assert new == report("M23C-I-005")
    assert "hash_version" not in archived["identity_results"][0]["audit"]
    assert hashlib.sha256(source_bytes).hexdigest() == before
    assert source_bytes == json.dumps(archived).encode()
    assert not new.promotable


def test_incomplete_input_snapshot_requires_explicit_new_local_evaluation():
    archived = json.loads(report().model_dump_json())
    del archived["input"]["candidates"][0]["context"]["snapshots"][0]["audit"]["hash_version"]
    preserved = json.dumps(archived)
    with pytest.raises(ValidationError):
        IntegrationInput.model_validate_json(json.dumps(archived["input"]))
    current_input_data = copy.deepcopy(archived["input"])
    # Explicitly discard the supplied incomplete envelope in a separate copy, never the archive.
    del current_input_data["candidates"][0]["context"]["snapshots"][0]["audit"]
    new = integrate(IntegrationInput.model_validate_json(json.dumps(current_input_data)))
    assert new == report()
    assert preserved == json.dumps(archived)
    assert not new.promotable
