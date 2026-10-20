"""Synthetic, scoped identity assertions; never persistence authorization."""

import json
from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from editalfinder_v2.domain.identity_models import (
    ExternalIdentifier,
    IdentifierNamespace,
    IdentityEvidence,
    IdentitySubject,
    NormalizedIdentifier,
    PublicationCycle,
)
from editalfinder_v2.domain.identity_normalization import normalize_identifier
from editalfinder_v2.domain.identity_resolution import resolve_identity
from editalfinder_v2.domain.models import (
    DocumentUnit,
    Evidence,
    FieldAssertion,
    OpportunityCandidate,
    RawSnapshot,
)


def subject(
    number=1,
    *,
    official="CALL-01",
    cycle="2026",
    namespace="issuer",
    source=10,
    url="https://example.org/call",
    opportunity=None,
    document=None,
):
    sid = UUID(int=number)
    unit = DocumentUnit(snapshot_id=sid, pointer="/record")
    values = {"official_identifier": official, "publication_cycle": cycle, "official_url": url}
    values = {k: v for k, v in values.items() if v is not None}
    snapshot = RawSnapshot(
        id=sid,
        source_id=UUID(int=source),
        source_code="fapergs",
        execution_id=UUID(int=100 + number),
        collected_at=datetime(2026, 1, 1, tzinfo=UTC),
        collector_version="synthetic-identity-1",
        url=url,
        payload_json=json.dumps({"record": values}),
    )
    assertions = tuple(
        FieldAssertion(
            field=k,
            value=v,
            evidence=(
                Evidence(
                    snapshot_id=sid,
                    pointer="/record/" + k,
                    quote=v,
                    method="structured_field",
                    method_version="synthetic-1",
                    confidence="1",
                    unit=unit,
                    semantic_role=k,
                ),
            ),
        )
        for k, v in values.items()
    )
    candidate = OpportunityCandidate(
        id=UUID(int=1000 + number),
        source_id=snapshot.source_id,
        source_code=snapshot.source_code,
        unit=unit,
        assertions=assertions,
    )

    def proof(field):
        a = next(a for a in assertions if a.field == field)
        return IdentityEvidence(
            candidate_id=candidate.id,
            source_id=snapshot.source_id,
            execution_id=snapshot.execution_id,
            evidence=a.evidence[0],
        )

    ns = IdentifierNamespace(value=namespace)
    identifiers = (
        ()
        if official is None
        else (
            ExternalIdentifier(
                original=official,
                identifier_type="identificador_oficial",
                namespace=ns,
                source_id=snapshot.source_id,
                provenance=proof("official_identifier"),
            ),
        )
    )
    identifiers += (
        ExternalIdentifier(
            original=url,
            identifier_type="url_canonica",
            namespace=IdentifierNamespace(value="url-conservative-v1"),
            source_id=snapshot.source_id,
            normalization_version="url-conservative-v1",
            provenance=proof("official_url"),
        ),
    )
    return IdentitySubject(
        candidate=candidate,
        snapshots=(snapshot,),
        identifiers=identifiers,
        cycle=None
        if cycle is None
        else PublicationCycle(
            original=cycle,
            namespace=IdentifierNamespace(value="publisher-cycle"),
            provenance=proof("publication_cycle"),
        ),
        claimed_opportunity_id=opportunity,
        claimed_document_id=document,
    )


def codes(report):
    return {d.code for d in report.diagnostics}


def test_same_official_context_and_explicit_cycle_matches_without_promotion():
    report = resolve_identity(subject(1), subject(2, url="https://other.org/detail"))
    assert report.decision == "exact_match"
    assert "official_identifier_cycle_match" in codes(report)
    assert len(report.supporting_evidence) == 4
    assert not report.promotable


@pytest.mark.parametrize(
    ("kwargs", "decision", "code"),
    [
        ({"namespace": "other"}, "no_supported_match", "namespace_scope_differs"),
        ({"source": 11}, "no_supported_match", "source_scope_differs"),
        ({"cycle": None}, "insufficient_information", "publication_cycle_missing"),
        ({"cycle": "2027"}, "distinct_cycles", "distinct_publication_cycles"),
        ({"official": None}, "insufficient_information", "official_identifier_missing"),
        (
            {"official": "OTHER", "url": "https://elsewhere.org"},
            "no_supported_match",
            "official_identifiers_differ",
        ),
        ({"official": "OTHER"}, "conflict", "document_identifier_conflict"),
    ],
)
def test_unresolved_or_distinct_reasons_are_specific(kwargs, decision, code):
    report = resolve_identity(subject(1), subject(2, **kwargs))
    assert report.decision == decision
    assert code in codes(report)
    assert not report.promotable


def test_url_only_is_insufficient_even_with_same_cycle():
    report = resolve_identity(subject(1, official=None), subject(2, official=None))
    assert report.decision == "insufficient_information"
    assert "url_is_not_opportunity_identity" in codes(report)


def test_reused_url_across_cycles_is_distinct_and_not_merged():
    report = resolve_identity(subject(1), subject(2, cycle="2027"))
    assert report.decision == "distinct_cycles"
    assert "contextual_key_reused_across_cycles" in {c.code for c in report.conflicts}


def test_matching_official_identifier_claiming_two_opportunities_is_conflict():
    report = resolve_identity(
        subject(1, opportunity=UUID(int=50)), subject(2, opportunity=UUID(int=51))
    )
    assert report.decision == "conflict"
    assert "opportunity_claim_conflict" in codes(report)


def test_equal_candidate_source_document_or_hash_never_suffices():
    left = subject(1, official=None, document=UUID(int=500))
    right = subject(2, official=None, document=UUID(int=500))
    assert resolve_identity(left, right).decision == "insufficient_information"


@pytest.mark.parametrize(
    "mutation", ["candidate", "source", "execution", "unit", "pointer", "quote", "role", "value"]
)
def test_identity_proof_is_bound_to_candidate_source_execution_record_and_value(mutation):
    right = subject(2)
    raw = right.model_dump()
    proof = raw["identifiers"][0]["provenance"]
    if mutation == "candidate":
        proof["candidate_id"] = UUID(int=999)
    elif mutation == "source":
        proof["source_id"] = UUID(int=999)
    elif mutation == "execution":
        proof["execution_id"] = UUID(int=999)
    elif mutation == "unit":
        proof["evidence"]["unit"]["pointer"] = "/other"
    elif mutation == "pointer":
        proof["evidence"]["pointer"] = "/record/official_url"
    elif mutation == "quote":
        proof["evidence"]["quote"] = "CALL"
    elif mutation == "role":
        proof["evidence"]["semantic_role"] = "title"
    else:
        raw["identifiers"][0]["original"] = "SOMETHING-ELSE"
    report = resolve_identity(subject(1), IdentitySubject.model_validate(raw))
    assert report.decision == "insufficient_information"
    assert "identity_evidence_invalid" in codes(report)


def test_normalization_is_exact_by_default_and_nfc_requires_explicit_policy():
    ident = subject(1, official="Cafe\u0301").identifiers[0]
    exact = normalize_identifier(ident)
    assert exact.normalized == ident.original
    raw = ident.model_dump()
    raw["normalization_version"] = "opaque-nfc-v1"
    nfc = normalize_identifier(ExternalIdentifier.model_validate(raw))
    assert nfc.normalized == "Café"
    assert nfc.original == "Cafe\u0301"
    assert nfc.transformations == ("unicode_nfc",)
    assert NormalizedIdentifier.model_validate_json(nfc.model_dump_json()) == nfc
    forged = nfc.model_dump()
    forged["normalized"] = "different"
    with pytest.raises(ValidationError, match="normalization"):
        NormalizedIdentifier.model_validate(forged)


def test_report_roundtrip_retained_audit_detects_decision_or_evidence_tampering():
    from editalfinder_v2.domain.identity_models import IdentityResolutionReport

    report = resolve_identity(subject(1), subject(2))
    assert IdentityResolutionReport.model_validate_json(report.model_dump_json()) == report
    for key, replacement in [("decision", "no_supported_match"), ("supporting_evidence", ())]:
        data = report.model_dump()
        data[key] = replacement
        with pytest.raises(ValidationError, match="audit"):
            IdentityResolutionReport.model_validate(data)


def test_resolution_is_deterministic_and_symmetric_in_decision():
    left, right = subject(1), subject(2)
    first = resolve_identity(left, right)
    assert resolve_identity(left, right).model_dump_json() == first.model_dump_json()
    assert resolve_identity(right, left).decision == first.decision


def test_structurally_matching_title_is_not_an_official_identifier():
    forged = []
    for number in (1, 2):
        raw = subject(number).model_dump()
        raw["candidate"]["assertions"][0]["field"] = "title"
        raw["candidate"]["assertions"][0]["evidence"][0]["semantic_role"] = "title"
        raw["candidate"]["assertions"][0]["evidence"][0]["pointer"] = "/record/title"
        e = raw["candidate"]["assertions"][0]["evidence"][0]
        raw["identifiers"][0]["provenance"]["evidence"] = e
        payload = json.loads(raw["snapshots"][0]["payload_json"])
        payload["record"]["title"] = payload["record"].pop("official_identifier")
        raw["snapshots"][0]["payload_json"] = json.dumps(payload)
        raw["snapshots"][0].pop("audit")
        forged.append(IdentitySubject.model_validate(raw))
    report = resolve_identity(*forged)
    assert report.decision == "insufficient_information"
    assert "identity_evidence_invalid" in codes(report)


def test_same_source_uuid_with_different_codes_is_conflict():
    right = subject(2).model_dump()
    right["candidate"]["source_code"] = "fapesp"
    right["snapshots"][0]["source_code"] = "fapesp"
    report = resolve_identity(subject(1), IdentitySubject.model_validate(right))
    assert report.decision == "conflict"
    assert "source_context_conflict" in codes(report)


def test_typed_conflicting_assertion_does_not_hide_behind_matching_string():
    right = subject(2).model_dump()
    right["candidate"]["assertions"] += ({"field": "official_identifier", "value": True},)
    report = resolve_identity(subject(1), IdentitySubject.model_validate(right))
    assert report.decision == "insufficient_information"
    assert "identity_evidence_invalid" in codes(report)
