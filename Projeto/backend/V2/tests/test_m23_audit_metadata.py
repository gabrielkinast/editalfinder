"""Strict received audit metadata, distinct from newly generated verification."""

import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import pytest
from m23_fixtures import adapt_records, build_case, records_for
from pydantic import ValidationError

from editalfinder_v2.domain import integration_budget
from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import IntegrationAudit, IntegrationReport
from editalfinder_v2.domain.models import OperationalError

REQUIRED = (
    "schema_version",
    "output_budget_version",
    "report_digest",
    "algorithm",
    "hash_version",
    "limits_version",
)
ROUTES = ("constructor", "python", "json")


@pytest.fixture(scope="module")
def original() -> IntegrationReport:
    report = integrate(build_case("grant"))
    assert isinstance(report, IntegrationReport)
    assert report.audit is not None
    return report


def validate_route(model: type[Any], payload: dict[str, Any], route: str) -> Any:
    if route == "constructor":
        return model(**payload)
    if route == "python":
        return model.model_validate(payload)
    return model.model_validate_json(json.dumps(payload))


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("target", ["audit", "report"])
@pytest.mark.parametrize("missing", REQUIRED)
def test_each_received_metadata_field_is_required(
    original: IntegrationReport, route: str, target: str, missing: str
) -> None:
    assert original.audit is not None
    audit = original.audit.model_dump()
    del audit[missing]
    if target == "audit":
        model = IntegrationAudit
        payload = audit
        location = (missing,)
    else:
        model = IntegrationReport
        payload = (
            json.loads(original.model_dump_json()) if route == "json" else original.model_dump()
        )
        payload["audit"] = audit
        location = ("audit", missing)
    with pytest.raises(ValidationError) as caught:
        validate_route(model, payload, route)
    assert any(
        error["type"] == "missing" and error["loc"] == location
        for error in caught.value.errors(include_input=False)
    )
    assert missing in original.audit.model_fields_set


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("target", ["audit", "report"])
def test_digest_only_envelope_is_not_silently_completed(
    original: IntegrationReport, route: str, target: str
) -> None:
    assert original.audit is not None
    audit = {"report_digest": original.audit.report_digest}
    if target == "audit":
        model = IntegrationAudit
        payload = audit
    else:
        model = IntegrationReport
        payload = (
            json.loads(original.model_dump_json()) if route == "json" else original.model_dump()
        )
        payload["audit"] = audit
    with pytest.raises(ValidationError) as caught:
        validate_route(model, payload, route)
    assert len(caught.value.errors(include_input=False)) == len(REQUIRED) - 1


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("target", ["audit", "report"])
def test_complete_received_envelope_roundtrips_unchanged(
    original: IntegrationReport, route: str, target: str
) -> None:
    assert original.audit is not None
    value = original.audit if target == "audit" else original
    payload = json.loads(value.model_dump_json()) if route == "json" else value.model_dump()
    restored = validate_route(type(value), payload, route)
    assert restored == value
    assert restored.model_dump_json() == value.model_dump_json()


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("missing_audit", [True, False])
def test_no_envelope_means_new_local_generation_not_metadata_backfill(
    original: IntegrationReport, route: str, missing_audit: bool
) -> None:
    payload = json.loads(original.model_dump_json()) if route == "json" else original.model_dump()
    if missing_audit:
        payload.pop("audit")
    else:
        payload["audit"] = None
    restored = validate_route(IntegrationReport, payload, route)
    assert restored == original
    assert set(restored.audit.model_fields_set) == set(REQUIRED)


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("field", REQUIRED)
def test_explicit_null_metadata_is_not_absence_or_default(
    original: IntegrationReport, route: str, field: str
) -> None:
    assert original.audit is not None
    payload = original.audit.model_dump()
    payload[field] = None
    with pytest.raises(ValidationError):
        validate_route(IntegrationAudit, payload, route)


def test_audit_json_schema_declares_every_field_required() -> None:
    assert set(IntegrationAudit.model_json_schema()["required"]) == set(REQUIRED)
    assert all(field.is_required() for field in IntegrationAudit.model_fields.values())


Reprocess = Callable[[str], tuple[dict[str, object], IntegrationReport | OperationalError]]


@pytest.fixture(scope="module")
def documented_reprocess() -> Reprocess:
    path = Path(__file__).parents[1] / "docs/v2/INTEGRATION_AUDIT_REPROCESSING.md"
    text = path.read_text(encoding="utf-8")
    snippet = text.split("```python\n", 1)[1].split("\n```", 1)[0]
    namespace: dict[str, Any] = {}
    exec(compile(snippet, str(path), "exec"), namespace)
    return cast(Reprocess, namespace["reprocess_archived_report"])


@pytest.mark.parametrize("kind", ["digest_only", "pre_budget", "unknown_policy", "absent", "null"])
def test_documented_historical_reprocessing_keeps_source_and_new_policies_separate(
    original: IntegrationReport, documented_reprocess: Reprocess, kind: str
) -> None:
    source = json.loads(original.model_dump_json())
    if kind == "digest_only":
        source["audit"] = {"report_digest": source["audit"]["report_digest"]}
    elif kind == "pre_budget":
        del source["audit"]["output_budget_version"]
    elif kind == "unknown_policy":
        source["audit"]["output_budget_version"] = "declared-original-policy-unknown"
    elif kind == "absent":
        source.pop("audit")
    else:
        source["audit"] = None
    # Explicit INPUT replay does not claim to validate any historical outputs.
    source["candidates"] = [{"historical_output": "unverified"}]
    text = json.dumps(source, ensure_ascii=False, indent=2)
    archived = text.encode("utf-8")
    receipt, result = documented_reprocess(text)
    assert isinstance(result, IntegrationReport)
    assert result == original
    assert receipt["operation"] == "reprocess_input_under_current_policy"
    assert receipt["source_report_sha256"] == hashlib.sha256(archived).hexdigest()
    assert receipt["source_audit_present"] == ("audit" in source)
    assert receipt["source_audit"] == source.get("audit")
    assert receipt["original_policy_inferred"] is False
    assert receipt["historical_outputs_verified"] is False
    assert receipt["operational_error"] is None
    assert result.audit is not None
    assert receipt["verification_audit"] == result.audit.model_dump(mode="json")
    assert result.audit.output_budget_version == "m2.3a.1-output-budget-v1"
    assert result.input == original.input
    assert result.promotable is False
    assert text.encode("utf-8") == archived
    assert json.loads(text) == source
    preserved = receipt["source_audit"]
    if kind == "digest_only":
        assert isinstance(preserved, dict)
        assert set(preserved) == {"report_digest"}
    elif kind == "pre_budget":
        assert isinstance(preserved, dict)
        assert "output_budget_version" not in preserved
    elif kind == "unknown_policy":
        assert isinstance(preserved, dict)
        assert preserved["output_budget_version"] == "declared-original-policy-unknown"


def test_documented_reprocessing_preserves_64_mib_budget_and_operational_failure(
    documented_reprocess: Reprocess,
) -> None:
    assert integration_budget.MAX_OUTPUT_BUDGET == 64 * 1024 * 1024
    data = adapt_records([records_for("grant")[0]] * 32)
    source = json.dumps(
        {
            "input": data.model_dump(mode="json"),
            "audit": {"limits_version": "declared-historical-limits"},
        }
    )
    receipt, result = documented_reprocess(source)
    assert isinstance(result, OperationalError)
    assert result.code == "integration_output_budget_exceeded"
    assert receipt["source_audit"] == {"limits_version": "declared-historical-limits"}
    assert receipt["verification_policy"] == {
        "integration_version": data.integration_version,
        "limits_version": "m2.3-integration-limits-v1",
        "output_budget_version": "m2.3a.1-output-budget-v1",
    }
    assert receipt["verification_audit"] is None
    assert receipt["operational_error"] == result.model_dump(mode="json")
    assert result.promotable is False


def test_documented_reprocessing_does_not_migrate_incompatible_input_schema(
    original: IntegrationReport,
    documented_reprocess: Reprocess,
) -> None:
    source = json.loads(original.model_dump_json())
    source["input"]["schema_version"] = 1
    with pytest.raises(ValidationError):
        documented_reprocess(json.dumps(source))
