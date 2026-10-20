"""Conservative offline organization normalization; no registry calls or merge."""

import re
import unicodedata
from typing import Literal

from .identity_models import IdentityEvidence
from .m22b_common import matches_m22b, prepare_m22b
from .models import OperationalError
from .organization_models import (
    NormalizedOrganization,
    NormalizedOrganizationIdentifier,
    OrganizationClaim,
    OrganizationDiagnostic,
    OrganizationIdentifier,
    OrganizationNormalizationReport,
)
from .semantic_common import NormalizationContext

IdentifierValues = tuple[
    str | None,
    Literal["valid", "invalid", "unsupported", "limit_exceeded"],
    Literal["valid", "invalid", "not_checked", "not_applicable"],
    tuple[str, ...],
]


def _identifier_values(claim: OrganizationIdentifier) -> IdentifierValues:
    original = claim.value.original
    namespace = claim.namespace.value
    if len(namespace) > 8192 or not _opaque_valid(namespace):
        return None, "invalid", "not_checked", ("namespace_invalid",)
    if len(original) > 8192:
        return None, "limit_exceeded", "not_checked", ("identifier_limit_exceeded",)
    if claim.kind == "institutional":
        if not _opaque_valid(original):
            return None, "invalid", "not_applicable", ("identifier_invalid",)
        # Same opaque policy as M2.1; never create an opportunity ExternalIdentifier.
        normalized = (
            unicodedata.normalize("NFC", original)
            if claim.normalization_version == "opaque-nfc-v1"
            else original
        )
        return normalized, "valid", "not_applicable", ("institutional_existence_unverified",)
    if re.search("[A-Za-z]", original):
        return None, "unsupported", "not_checked", ("cnpj_alphanumeric_unsupported",)
    normalized = original
    if re.fullmatch(r"[0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2}", original):
        normalized = original.replace(".", "").replace("/", "").replace("-", "")
    if not re.fullmatch("[0-9]{14}", normalized):
        return None, "invalid", "not_checked", ("cnpj_syntax_invalid",)
    digits = [int(c) for c in normalized]
    valid = len(set(digits)) > 1
    for end, weights in [
        (12, (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)),
        (13, (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)),
    ]:
        remainder = sum(d * w for d, w in zip(digits[:end], weights, strict=True)) % 11
        valid = valid and digits[end] == (0 if remainder < 2 else 11 - remainder)
    if not valid:
        return None, "valid", "invalid", ("cnpj_checksum_invalid",)
    return normalized, "valid", "valid", ("cnpj_checksum_valid_existence_unverified",)


def _opaque_valid(text: str) -> bool:
    return bool(text.strip()) and not any(
        unicodedata.category(c) in {"Cc", "Cf", "Cs"} for c in text
    )


def normalize_organization_identifier(
    claim: OrganizationIdentifier,
) -> NormalizedOrganizationIdentifier:
    normalized, syntax, checksum, diagnostics = _identifier_values(claim)
    return NormalizedOrganizationIdentifier(
        claim=claim,
        normalized=normalized,
        syntax_status=syntax,
        checksum_status=checksum,
        diagnostics=diagnostics,
    )


def _organization_values(
    claim: OrganizationClaim,
) -> tuple[str | None, tuple[NormalizedOrganizationIdentifier, ...], tuple[str, ...]]:
    name = None
    codes: list[str] = []
    if claim.name is None:
        codes.append("organization_name_missing")
    elif len(claim.name.original) > 8192 or not _opaque_valid(claim.name.original):
        codes.append("organization_name_invalid")
    else:
        name = " ".join(unicodedata.normalize("NFC", claim.name.original).split())
    identifiers = tuple(normalize_organization_identifier(i) for i in claim.identifiers)
    if not identifiers:
        codes.append("organization_identifier_missing")
    return name, identifiers, tuple(codes)


ReportValues = tuple[
    tuple[NormalizedOrganization, ...],
    tuple[tuple[tuple[str, ...], ...], ...],
    tuple[str, ...],
    tuple[OrganizationDiagnostic, ...],
]


def _report_values(
    context: NormalizationContext,
    claims: tuple[OrganizationClaim, ...],
) -> ReportValues | OperationalError:
    values = tuple(
        v
        for c in claims
        for v in (*((c.name,) if c.name else ()), *(i.value for i in c.identifiers))
    )
    prepared = prepare_m22b(
        context,
        claim_count=len(claims),
        values=values,
        extra_text=tuple(i.namespace.value for c in claims for i in c.identifiers),
    )
    if isinstance(prepared, OperationalError):
        return prepared
    organizations = []
    keys: list[tuple[tuple[str, ...], ...]] = []
    report_codes = ["organization_identity_unverified"]
    structured = [
        OrganizationDiagnostic(code=report_codes[0], message="Legal identity is unverified.")
    ]
    key_evidence: dict[tuple[int, tuple[str, ...]], IdentityEvidence] = {}
    shared_reported = False
    seen: dict[tuple[str, ...], int] = {}
    # At most two distinct representatives per comparable namespace/policy/source.
    # One witness per component suffices; do not enumerate quadratic row pairs.
    comparable: dict[tuple[str, ...], list[tuple[str, int]]] = {}
    conflicts: set[tuple[int, int]] = set()
    for index, claim in enumerate(claims):
        name, identifiers, diagnostics = _organization_values(claim)
        organizations.append(
            NormalizedOrganization(
                claim=claim, normalized_name=name, identifiers=identifiers, diagnostics=diagnostics
            )
        )
        components = ([("name", claim.name)] if claim.name is not None else []) + [
            (i.kind, i.value) for i in claim.identifiers
        ]
        for code in diagnostics:
            structured.append(
                OrganizationDiagnostic(
                    code=code,
                    message=code,
                    claim_index=index,
                    evidence=(claim.name.provenance,) if claim.name else (),
                )
            )
        for identifier_index, identifier in enumerate(identifiers):
            for code in identifier.diagnostics:
                structured.append(
                    OrganizationDiagnostic(
                        code=code,
                        message=code,
                        claim_index=index,
                        identifier_index=identifier_index,
                        evidence=(identifier.claim.value.provenance,),
                    )
                )
        # All components must belong to ONE role-bearing object (or direct record).
        parents = {
            (v.provenance.evidence.snapshot_id, v.provenance.evidence.pointer.rsplit("/", 1)[0])
            for _, v in components
        }
        supported = len(parents) <= 1 and all(
            matches_m22b(
                prepared, v, claim.role, collection="organization_claims", component=component
            )
            for component, v in components
        )
        if not supported:
            report_codes.append(f"organization_evidence_invalid:{index}")
            structured.append(
                OrganizationDiagnostic(
                    code="organization_evidence_invalid",
                    message="Claim evidence is not supported.",
                    claim_index=index,
                    evidence=tuple(v.provenance for _, v in components),
                )
            )
        row_keys = tuple(
            (
                i.claim.kind,
                i.claim.namespace.value,
                str(i.claim.value.provenance.source_id),
                i.claim.normalization_version,
                i.normalized,
            )
            for i in identifiers
            if supported and i.normalized is not None
        )
        for identifier in identifiers:
            if supported and identifier.normalized is not None:
                key = (
                    identifier.claim.kind,
                    identifier.claim.namespace.value,
                    str(identifier.claim.value.provenance.source_id),
                    identifier.claim.normalization_version,
                    identifier.normalized,
                )
                key_evidence.setdefault((index, key), identifier.claim.value.provenance)
        shared_key = next((key for key in row_keys if key in seen), None)
        if not shared_reported and shared_key is not None:
            shared_reported = True
            shared_witness = seen[shared_key]
            report_codes.append("contextual_identifier_shared_not_merge")
            structured.append(
                OrganizationDiagnostic(
                    code="contextual_identifier_shared_not_merge",
                    message="Shared contextual identifiers do not authorize a merge.",
                    claim_index=shared_witness,
                    related_claim_index=index,
                    evidence=(
                        key_evidence[(shared_witness, shared_key)],
                        key_evidence[(index, shared_key)],
                    ),
                )
            )
        for key in row_keys:
            representatives = comparable.setdefault(key[:-1], [])
            witness = next((row for value, row in representatives if value != key[-1]), None)
            if witness is not None and (witness, index) not in conflicts:
                conflicts.add((witness, index))
                report_codes.append(
                    f"organization_comparable_identifier_conflict:{witness}:{index}"
                )
                other_value = next(
                    value for value, row in representatives if row == witness and value != key[-1]
                )
                structured.append(
                    OrganizationDiagnostic(
                        code="organization_comparable_identifier_conflict",
                        message="Comparable identifiers differ; no legal identity decision.",
                        claim_index=witness,
                        related_claim_index=index,
                        evidence=(
                            key_evidence[(witness, (*key[:-1], other_value))],
                            key_evidence[(index, key)],
                        ),
                    )
                )
            if len(representatives) < 2 and all(value != key[-1] for value, _ in representatives):
                representatives.append((key[-1], index))
        for key in row_keys:
            seen.setdefault(key, index)
        keys.append(row_keys)
    return tuple(organizations), tuple(keys), tuple(report_codes), tuple(structured)


def normalize_organizations(
    context: NormalizationContext,
    claims: tuple[OrganizationClaim, ...],
) -> OrganizationNormalizationReport | OperationalError:
    values = _report_values(context, claims)
    if isinstance(values, OperationalError):
        return values
    organizations, keys, diagnostics, structured = values
    return OrganizationNormalizationReport(
        context=context,
        claims=claims,
        organizations=organizations,
        comparison_keys=keys,
        diagnostics=diagnostics,
        structured_diagnostics=structured,
    )
