"""Immutable offline geography, not a database projection or geographic resolver."""

from typing import Literal, Self

from pydantic import model_validator

from .geography_catalog import COUNTRY_CODES, REGION_STATES, STATE_CODES
from .models import Confidence, Contract
from .semantic_common import (
    AuditedNormalizationReport,
    NormalizationContext,
    NormalizationDiagnostic,
    SemanticValue,
)

LocationRole = Literal[
    "elegibilidade",
    "execucao",
    "beneficiarios",
    "origem",
    "organizacao_responsavel",
    "nao_especificado",
]
GeographicScope = Literal["brasil", "internacional", "misto", "nao_identificado"]
GeographicComponent = Literal["country_code", "state_code", "municipality", "region"]


class GeographyLocationClaim(Contract):
    role: LocationRole
    country_code: SemanticValue | None = None
    state_code: SemanticValue | None = None
    municipality: SemanticValue | None = None
    region: SemanticValue | None = None


class GeographyInput(Contract):
    context: NormalizationContext
    locations: tuple[GeographyLocationClaim, ...] = ()
    scope: SemanticValue | None = None
    normalization_version: Literal["geography-conservative-v1"] = "geography-conservative-v1"


class GeographicConfidence(Contract):
    country_code: Confidence | None = None
    state_code: Confidence | None = None
    municipality: Confidence | None = None
    region: Confidence | None = None


class NormalizedLocation(Contract):
    claim: GeographyLocationClaim
    country_code: str | None = None
    state_code: str | None = None
    municipality: str | None = None
    region: str | None = None
    municipality_verified: Literal[False] = False
    confidence: GeographicConfidence = GeographicConfidence()
    diagnostics: tuple[NormalizationDiagnostic, ...] = ()
    normalization_version: Literal["geography-conservative-v1"] = "geography-conservative-v1"

    @model_validator(mode="after")
    def consistent_geography(self) -> Self:
        if self.country_code is not None and self.country_code not in COUNTRY_CODES:
            raise ValueError("Country must be an assigned uppercase ISO alpha-2 code")
        if self.state_code is not None and (
            self.country_code != "BR" or self.state_code not in STATE_CODES
        ):
            raise ValueError("Brazilian UF requires BR and an official uppercase code")
        if self.region is not None:
            if self.country_code != "BR" or self.region not in REGION_STATES:
                raise ValueError("Brazilian region requires BR and an official region")
            if self.state_code is not None and self.state_code not in REGION_STATES[self.region]:
                raise ValueError("Brazilian UF and region conflict")
        if self.municipality is not None and (
            self.country_code is None or not self.municipality.strip()
        ):
            raise ValueError("Municipality text requires country and cannot be empty")
        return self

    @property
    def role(self) -> LocationRole:
        return self.claim.role


class GeographyReport(AuditedNormalizationReport):
    input: GeographyInput
    scope: GeographicScope
    locations: tuple[NormalizedLocation, ...] = ()
    diagnostics: tuple[NormalizationDiagnostic, ...] = ()
    normalization_version: Literal["geography-conservative-v1"] = "geography-conservative-v1"
    country_catalog_version: Literal["iso3166-1-iso-codes-4.20.1"] = "iso3166-1-iso-codes-4.20.1"
