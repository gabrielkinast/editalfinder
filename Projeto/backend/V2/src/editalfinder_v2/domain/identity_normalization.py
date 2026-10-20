"""Normalization is explicit and separate from evidence verification or matching."""

import unicodedata
from typing import Literal

from .identity_models import ExternalIdentifier, NormalizedIdentifier

NormalizationCode = Literal[
    "identifier_normalized",
    "identifier_invalid",
    "identifier_limit_exceeded",
    "identifier_url_invalid",
]
MAX_IDENTIFIER_CHARS = 8192


def _normalization_values(
    value: ExternalIdentifier,
) -> tuple[str | None, NormalizationCode, tuple[str, ...]]:
    original = value.original
    if len(original) > MAX_IDENTIFIER_CHARS:
        return None, "identifier_limit_exceeded", ()
    if not original.strip() or any(unicodedata.category(c) in {"Cc", "Cf", "Cs"} for c in original):
        return None, "identifier_invalid", ()
    if value.identifier_type == "url_canonica":
        from .url_identity import normalize_url

        result = normalize_url(original)
        if result.normalized is None:
            return None, "identifier_url_invalid", ()
        return (
            result.normalized,
            "identifier_normalized",
            tuple(t.code for t in result.transformations),
        )
    normalized = original
    if value.normalization_version == "opaque-nfc-v1":
        normalized = unicodedata.normalize("NFC", original)
    changes = ("unicode_nfc",) if normalized != original else ()
    return normalized, "identifier_normalized", changes


def normalize_identifier(value: ExternalIdentifier) -> NormalizedIdentifier:
    """Preserve case, whitespace, punctuation and zeroes; NFC is opt-in only."""
    normalized, code, changes = _normalization_values(value)
    return NormalizedIdentifier(
        **value.model_dump(include=set(ExternalIdentifier.model_fields)),
        normalized=normalized,
        normalization_code=code,
        transformations=changes,
    )
