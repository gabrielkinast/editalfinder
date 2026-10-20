"""Frozen SYNTHETIC cases; this adapter is test-only, not extraction or policy."""

import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from editalfinder_v2.domain.financial_models import FinancialClaim
from editalfinder_v2.domain.geography_models import GeographyLocationClaim
from editalfinder_v2.domain.identity_models import (
    ExternalIdentifier,
    IdentifierNamespace,
    IdentityEvidence,
    PublicationCycle,
)
from editalfinder_v2.domain.integration_models import CandidateIntegrationInput, IntegrationInput
from editalfinder_v2.domain.models import (
    DocumentUnit,
    Evidence,
    FieldAssertion,
    OpportunityCandidate,
    RawSnapshot,
)
from editalfinder_v2.domain.organization_models import OrganizationClaim
from editalfinder_v2.domain.semantic_common import NormalizationContext, SemanticValue
from editalfinder_v2.domain.taxonomy_models import TaxonomyClaim
from editalfinder_v2.domain.temporal_models import TemporalClaim

FIXTURE = Path(__file__).parent / "fixtures/m23_cases.json"


def records_for(case: str) -> list[dict[str, Any]]:
    """Return a fresh copy so one mutation cannot contaminate another scenario."""
    return json.loads(FIXTURE.read_text(encoding="utf-8"))[case]["records"]


def build_case(case: str) -> IntegrationInput:
    return adapt_records(records_for(case))


def adapt_records(records: list[dict[str, Any]]) -> IntegrationInput:
    """Explicit fixture declarations; no meaning inferred from title/keywords."""
    sid, source, execution = UUID(int=23001), UUID(int=23002), UUID(int=23003)
    snapshot = RawSnapshot(
        id=sid,
        source_id=source,
        source_code="fapergs",
        execution_id=execution,
        collected_at=datetime(2026, 1, 1, tzinfo=UTC),
        collector_version="m23-synthetic-v1",
        url="https://example.org/synthetic-only",
        payload_json=json.dumps({"records": records}, ensure_ascii=False),
    )
    inputs = []
    for index, record in enumerate(records):
        cid = UUID(int=23100 + index)
        unit = DocumentUnit(snapshot_id=sid, pointer=f"/records/{index}")
        assertions = []

        def value(
            original: str | bool,
            role: str,
            pointer: str,
            *,
            bound_unit: DocumentUnit = unit,
            bound_assertions: list[FieldAssertion] = assertions,
            bound_cid: UUID = cid,
        ) -> SemanticValue:
            literal = json.dumps(original) if type(original) is bool else original
            evidence = Evidence(
                snapshot_id=sid,
                pointer=pointer,
                quote=literal,
                method="structured_field",
                method_version="m23-synthetic-v1",
                confidence="1",
                unit=bound_unit,
                semantic_role=role,
            )
            bound_assertions.append(
                FieldAssertion(field=role, value=original, evidence=(evidence,))
            )
            return SemanticValue(
                original=literal,
                provenance=IdentityEvidence(
                    candidate_id=bound_cid,
                    source_id=source,
                    execution_id=execution,
                    evidence=evidence,
                ),
            )

        direct = {
            key: value(original, key, unit.pointer + "/" + key)
            for key, original in record.items()
            if type(original) in {str, bool}
        }
        collections = {}
        for collection in (
            "temporal_events",
            "geographic_locations",
            "financial_claims",
            "organization_claims",
            "taxonomy_claims",
        ):
            rows = []
            for row_index, row in enumerate(record.get(collection, [])):
                components = {}
                for key, original in row.items():
                    if key in {"role", "format", "unit", "currency"}:
                        continue
                    role = row["role"] if key == "value" else row["role"] + "." + key
                    components[key] = value(
                        original, role, f"{unit.pointer}/{collection}/{row_index}/{key}"
                    )
                rows.append(components)
            collections[collection] = rows
        candidate = OpportunityCandidate(
            id=cid,
            source_id=source,
            source_code=snapshot.source_code,
            assertions=tuple(assertions),
            unit=unit,
        )
        namespace = IdentifierNamespace(value="synthetic-publisher")
        identifiers = (
            (
                ExternalIdentifier(
                    identifier_type="identificador_oficial",
                    original=direct["official_identifier"].original,
                    namespace=namespace,
                    source_id=source,
                    provenance=direct["official_identifier"].provenance,
                ),
            )
            if "official_identifier" in direct
            else ()
        )
        cycle = (
            PublicationCycle(
                original=direct["publication_cycle"].original,
                namespace=namespace,
                provenance=direct["publication_cycle"].provenance,
            )
            if "publication_cycle" in direct
            else None
        )
        inputs.append(
            CandidateIntegrationInput(
                context=NormalizationContext(candidate=candidate, snapshots=(snapshot,)),
                identifiers=identifiers,
                cycle=cycle,
                temporal=tuple(
                    TemporalClaim(role=row["role"], value=components["value"], format=row["format"])
                    for row, components in zip(
                        record.get("temporal_events", []),
                        collections["temporal_events"],
                        strict=True,
                    )
                ),
                geography=tuple(
                    GeographyLocationClaim(role=row["role"], **components)
                    for row, components in zip(
                        record.get("geographic_locations", []),
                        collections["geographic_locations"],
                        strict=True,
                    )
                ),
                geographic_scope=direct.get("geographic_scope"),
                financial=tuple(
                    FinancialClaim(
                        role=row["role"],
                        value=components.get("value"),
                        format=row.get("format", "unspecified"),
                        currency=row.get("currency"),
                        unit=row.get("unit", "amount"),
                    )
                    for row, components in zip(
                        record.get("financial_claims", []),
                        collections["financial_claims"],
                        strict=True,
                    )
                ),
                organizations=tuple(
                    OrganizationClaim(role=row["role"], name=components.get("name"))
                    for row, components in zip(
                        record.get("organization_claims", []),
                        collections["organization_claims"],
                        strict=True,
                    )
                ),
                taxonomy=tuple(
                    TaxonomyClaim(role=row["role"], value=components["value"])
                    for row, components in zip(
                        record.get("taxonomy_claims", []),
                        collections["taxonomy_claims"],
                        strict=True,
                    )
                ),
            )
        )
    return IntegrationInput(candidates=tuple(inputs), reference_date=date(2026, 1, 1))
