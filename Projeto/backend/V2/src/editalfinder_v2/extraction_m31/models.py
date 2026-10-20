"""Immutable versioned predictions; no review or validation authority."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .reader import Provenance

VERSION: Literal["m31-deterministic-v2"] = "m31-deterministic-v2"
Discovery = Literal[
    "confirmed_opportunity",
    "announced_future_opportunity",
    "opportunity_signal",
    "unrelated_or_non_actionable",
    "abstain",
]
Modality = Literal["fomento", "credito", "investimentos", "undetermined"]
Temporal = Literal["open", "closed", "future", "continuous", "undetermined", "not_applicable"]


class Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True, hide_input_in_errors=True)
    schema_version: Literal["m31-extraction-v1"] = "m31-extraction-v1"


class Witness(Frozen):
    run_id: str
    document_id: str
    raw_sha256: str
    text_sha256: str
    segment_id: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    page: int | None
    quote: str = Field(min_length=1, max_length=20000)


class ExtractedField(Frozen):
    name: str
    original: str = Field(min_length=1)
    witness: Witness
    method_version: Literal["m31-deterministic-v2"] = VERSION
    uncertainty: str = "heuristic role assignment; not authenticated or normalized"
    diagnostic_status: Literal["traceable_not_semantically_certified"] = (
        "traceable_not_semantically_certified"
    )

    @model_validator(mode="after")
    def literal(self) -> Self:
        if self.original not in self.witness.quote:
            raise ValueError("field_value_witness_mismatch")
        return self


class Segment(Frozen):
    segment_id: str
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    discovery: Discovery
    modality: Modality
    temporal: Temporal
    fields: tuple[ExtractedField, ...]
    witnesses: tuple[Witness, ...]
    diagnostics: tuple[str, ...]
    method_version: Literal["m31-deterministic-v2"] = VERSION

    @model_validator(mode="after")
    def owned(self) -> Self:
        if self.end <= self.start:
            raise ValueError("invalid_segment_boundary")
        for w in self.witnesses + tuple(f.witness for f in self.fields):
            if w.segment_id != self.segment_id or not self.start <= w.start < w.end <= self.end:
                raise ValueError("cross_record_evidence")
        if self.discovery != "abstain" and not self.witnesses:
            raise ValueError("prediction_requires_evidence")
        if self.temporal in {"open", "continuous"} and self.discovery != "confirmed_opportunity":
            raise ValueError("availability_without_confirmed_instrument")
        return self


class DocumentOutcome(Frozen):
    run_id: str
    document_id: str
    provenance: Provenance | None
    status: Literal["processed", "operational_failure"]
    segments: tuple[Segment, ...]
    diagnostics: tuple[str, ...]
    reference_date: str
    method_version: Literal["m31-deterministic-v2"] = VERSION
    bridge_status: Literal["not_implemented_context_authorization_missing"] = (
        "not_implemented_context_authorization_missing"
    )
    promotable: Literal[False] = False

    @model_validator(mode="after")
    def owned(self) -> Self:
        if self.status == "operational_failure":
            if self.segments or not self.diagnostics:
                raise ValueError("failure_cannot_carry_predictions")
            return self
        if self.provenance is None or self.provenance.document_id != self.document_id:
            raise ValueError("document_provenance_mismatch")
        if len({s.segment_id for s in self.segments}) != len(self.segments):
            raise ValueError("duplicate_segment_id")
        for segment in self.segments:
            for w in segment.witnesses + tuple(f.witness for f in segment.fields):
                if (
                    w.document_id != self.document_id
                    or w.run_id != self.run_id
                    or w.raw_sha256 != self.provenance.raw_sha256
                    or w.text_sha256 != self.provenance.text_sha256
                ):
                    raise ValueError("cross_document_or_run_evidence")
        return self
