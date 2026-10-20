"""M1.1a Unicode transport and URL safety must not regress in identity DTOs."""

import pytest
from pydantic import ValidationError

from editalfinder_v2.domain.url_identity import normalize_url


@pytest.mark.parametrize(
    "suffix", ["/%00", "/%0A", "/%7f", "/%5C", "/\u200b", "/?q=\u202e", "/#\u2060"]
)
def test_unsafe_url_controls_cannot_be_normalized_as_valid(suffix):
    result = normalize_url("https://example.org" + suffix)
    assert result.code == "url_invalid"
    assert result.normalized is None


def test_invalid_unicode_is_rejected_at_the_same_contract_boundary_as_m11a():
    with pytest.raises(ValidationError, match="UTF-8"):
        normalize_url("https://example.org/\ud800")
