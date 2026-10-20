"""Pure geographic normalization; no source inference or geographic lookup."""

import re
import unicodedata
from typing import cast

from .geography_catalog import COUNTRY_CODES, REGION_STATES, STATE_CODES
from .geography_models import (
    GeographicConfidence,
    GeographicScope,
    GeographyInput,
    GeographyReport,
    LocationRole,
    NormalizedLocation,
)
from .models import OperationalError
from .semantic_common import NormalizationDiagnostic, SemanticValue, prepare_context


def normalize_geography(value: GeographyInput) -> GeographyReport | OperationalError:
    values = [
        v
        for claim in value.locations
        for v in (claim.country_code, claim.state_code, claim.region, claim.municipality)
        if v is not None
    ] + ([value.scope] if value.scope is not None else [])
    prepared = prepare_context(
        value.context,
        claim_count=max(len(value.locations), len(values)),
        text_chars=sum(len(v.original) for v in values),
    )
    if isinstance(prepared, OperationalError):
        return prepared
    diagnostics: list[NormalizationDiagnostic] = []
    scope: GeographicScope = "nao_identificado"
    if value.scope is None:
        diagnostics.append(
            NormalizationDiagnostic(
                code="geo_scope_missing", message="Scope requires its own evidence."
            )
        )
    elif not prepared.matches(value.scope, "geographic_scope"):
        diagnostics.append(
            NormalizationDiagnostic(
                code="normalization_evidence_invalid",
                message="Scope evidence does not bind this role.",
                evidence=(value.scope.provenance,),
            )
        )
    elif value.scope.original not in {"brasil", "internacional", "misto", "nao_identificado"}:
        diagnostics.append(
            NormalizationDiagnostic(
                code="geo_scope_invalid",
                message="Scope is outside the approved vocabulary.",
                evidence=(value.scope.provenance,),
            )
        )
    else:
        scope = cast(GeographicScope, value.scope.original)
    if not value.locations:
        diagnostics.append(
            NormalizationDiagnostic(code="geo_locations_missing", message="No locations supplied.")
        )
    locations: list[NormalizedLocation] = []
    for index, claim in enumerate(value.locations):
        issues: list[NormalizationDiagnostic] = []
        component_values = tuple(
            v
            for v in (claim.country_code, claim.state_code, claim.region, claim.municipality)
            if v is not None
        )
        if not component_values:
            issues.append(
                NormalizationDiagnostic(
                    code="geo_location_empty",
                    message="Location claim has no geographic components.",
                    claim_index=index,
                )
            )
        origins = {v.provenance.evidence.pointer.rsplit("/", 1)[0] for v in component_values}
        if len(origins) > 1:
            issue = NormalizationDiagnostic(
                code="geo_location_context_conflict",
                message="Location components come from different source objects.",
                claim_index=index,
                evidence=tuple(v.provenance for v in component_values),
            )
            locations.append(NormalizedLocation(claim=claim, diagnostics=(issue,)))
            diagnostics.append(issue)
            continue

        def diagnostic(
            code: str,
            proof: SemanticValue,
            *,
            issues: list[NormalizationDiagnostic] = issues,
            index: int = index,
        ) -> None:
            issues.append(
                NormalizationDiagnostic(
                    code=code,
                    message="Geographic value is outside its supported semantic domain.",
                    claim_index=index,
                    evidence=(proof.provenance,),
                )
            )

        def component(
            raw: SemanticValue | None,
            key: str,
            allowed: frozenset[str],
            *,
            role: LocationRole = claim.role,
        ) -> str | None:
            if raw is None:
                return None
            if not prepared.matches(raw, role, collection="geographic_locations", component=key):
                diagnostic("normalization_evidence_invalid", raw)
                return None
            original = raw.original
            normalized = original.upper() if key != "region" else original
            if (
                key != "region" and not re.fullmatch(r"[A-Za-z]{2}", original, re.ASCII)
            ) or normalized not in allowed:
                diagnostic(
                    {
                        "country_code": "geo_country_invalid",
                        "state_code": "geo_state_invalid",
                        "region": "geo_region_invalid",
                    }[key],
                    raw,
                )
                return None
            return normalized

        country = component(claim.country_code, "country_code", COUNTRY_CODES)
        state = component(claim.state_code, "state_code", STATE_CODES)
        region = component(claim.region, "region", frozenset(REGION_STATES))
        if state is not None and country != "BR":
            assert claim.state_code is not None
            diagnostic("geo_country_state_conflict", claim.state_code)
            state = None
        if region is not None and country != "BR":
            assert claim.region is not None
            diagnostic("geo_country_region_conflict", claim.region)
            region = None
        if state is not None and region is not None and state not in REGION_STATES[region]:
            assert claim.state_code is not None and claim.region is not None
            diagnostic("geo_state_region_conflict", claim.state_code)
            state = region = None
        municipality: str | None = None
        if claim.municipality is not None:
            raw = claim.municipality
            if not prepared.matches(
                raw, claim.role, collection="geographic_locations", component="municipality"
            ):
                diagnostic("normalization_evidence_invalid", raw)
            elif (
                not raw.original.strip()
                or raw.original.strip().casefold()
                in {"n/a", "não informado", "nao informado", "null", "none"}
                or any(unicodedata.category(c) in {"Cc", "Cf", "Cs"} for c in raw.original)
            ):
                diagnostic("geo_municipality_invalid", raw)
            elif country is None:
                diagnostic("geo_municipality_country_missing", raw)
            else:
                municipality = raw.original.strip()
                diagnostic("geo_municipality_unverified", raw)
        location = NormalizedLocation(
            claim=claim,
            country_code=country,
            state_code=state,
            region=region,
            municipality=municipality,
            confidence=GeographicConfidence(
                municipality=claim.municipality.provenance.evidence.confidence
                if municipality is not None and claim.municipality is not None
                else None,
                country_code=claim.country_code.provenance.evidence.confidence
                if country is not None and claim.country_code is not None
                else None,
                state_code=claim.state_code.provenance.evidence.confidence
                if state is not None and claim.state_code is not None
                else None,
                region=claim.region.provenance.evidence.confidence
                if region is not None and claim.region is not None
                else None,
            ),
            diagnostics=tuple(issues),
        )
        locations.append(location)
        diagnostics.extend(issues)
    for index, location in enumerate(locations):
        country = location.country_code
        if (
            location.role == "elegibilidade"
            and country is not None
            and (
                (scope == "brasil" and country != "BR")
                or (scope == "internacional" and country == "BR")
            )
        ):
            assert location.claim.country_code is not None and value.scope is not None
            diagnostics.append(
                NormalizationDiagnostic(
                    code="geo_scope_conflict",
                    message="Explicit scope conflicts with an eligibility location.",
                    claim_index=index,
                    evidence=(value.scope.provenance, location.claim.country_code.provenance),
                )
            )
    return GeographyReport(
        input=value,
        scope=scope,
        locations=tuple(locations),
        diagnostics=tuple(diagnostics),
    )
