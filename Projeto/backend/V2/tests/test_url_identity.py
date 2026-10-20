"""Conservative, offline URL identity contracts."""

import importlib.util

import pytest
from pydantic import ValidationError

from editalfinder_v2.domain.url_identity import URLNormalization, normalize_url


@pytest.mark.parametrize(
    "value",
    [
        "",
        "ftp://example.com",
        "https:///x",
        "https://user:pass@example.com",
        "https://example.com\\x",
        " https://example.com",
        "https://example.com/\n",
        "https://example.com/%",
        "https://example.com/%xz",
        "https://example.com:abc",
        "https://example.com:",
        "https://example.com:65536",
        "https://example.com:-1",
        "https://example.com:0",
        "https://a..b",
        "https://-bad.com",
        "https://bad_.com",
        "https://127.1",
        "https://0127.0.0.1",
        "https://999.1.1.1",
        "https://[bad]",
        "https://[::1%25eth0]",
        "https://xn--.com",
        "https://example.com/\x7f",
        "https://example.com/<x>",
    ],
)
def test_invalid_values_are_structured(value: str) -> None:
    result = normalize_url(value)
    assert result.original == value
    assert result.normalized is None
    assert result.code == "url_invalid"
    assert result.transformations == ()


@pytest.mark.parametrize("value", ["https://faß.de", "https://Ａ.com", "https://a\u200db.com"])
def test_irreversible_idna_is_ambiguous(value: str) -> None:
    assert normalize_url(value).code == "url_ambiguous_idna"


def test_limits() -> None:
    assert normalize_url("https://example.com/" + "a" * 8192).code == "url_limit_exceeded"


def test_output_limits_keep_successes_idempotent() -> None:
    value = "https://bücher.de/" + "a" * (8192 - len("https://bücher.de/"))
    assert normalize_url(value).code == "url_limit_exceeded"


def test_contract_rejects_forgery_and_versions() -> None:
    result = normalize_url("HTTPS://EXAMPLE.COM")
    assert URLNormalization.model_validate_json(result.model_dump_json()) == result
    for field, forged in [
        ("normalized", "https://evil.com"),
        ("code", "url_invalid"),
        ("transformations", ()),
        ("normalization_version", "future"),
        ("schema_version", 1),
        ("extra", True),
    ]:
        payload = result.model_dump()
        payload[field] = forged
        with pytest.raises(ValidationError):
            URLNormalization.model_validate(payload)
    with pytest.raises(ValidationError):
        result.normalized = "https://evil.com"  # type: ignore[misc]  # Exercise frozen contract.


@pytest.mark.parametrize(
    "value",
    [
        "http://example.com",
        "https://example.com",
        "https://example.com/",
        "https://example.com//a/.././b%2F%7E%2E",
        "https://example.com?",
        "https://example.com#",
        "https://example.com?#",
        "https://example.com#!/route?x=1",
        "https://example.com/#/spa",
        "https://example.com/?a=1&b=2",
        "https://example.com/?b=2&a=1",
        "https://example.com/?a&a=&a=1&&",
        "https://example.com/?q=+&q=%20",
        "https://example.com/café?e=e\u0301#ç",
        "https://example.com./",
        "https://example.com/?utm_source=x",
        "https://127.0.0.1:8080/",
        "https://[2001:0db8::1]:8080/",
    ],
)
def test_preserves_distinct_identity(value: str) -> None:
    result = normalize_url(value)
    assert result.normalized == value
    assert result.transformations == ()
    assert normalize_url(result.normalized) == result


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("https://BÜCHER.de", "https://xn--bcher-kva.de"),
        ("https://bu\u0308cher.de", "https://xn--bcher-kva.de"),
        ("https://XN--BCHER-KVA.de", "https://xn--bcher-kva.de"),
        ("http://EXAMPLE.COM.:00080", "http://example.com."),
        ("https://[2001:DB8::1]:0443", "https://[2001:db8::1]"),
        ("https://example.com:0008080", "https://example.com:8080"),
    ],
)
def test_safe_hosts(value: str, expected: str) -> None:
    result = normalize_url(value)
    assert result.normalized == expected
    assert normalize_url(expected).normalized == expected
    assert URLNormalization.model_validate_json(result.model_dump_json()) == result


def test_tracking_policy_only_drops_exact_raw_names() -> None:
    value = (
        "https://example.com/?utm_source=x&&UTM_source=y&utm_id=1&%75tm_source=z"
        "&utm_medium&utm_campaign=&utm_term=x&utm_content=z&a=1&a=2&#utm_source=keep"
    )
    assert normalize_url(value).normalized == value
    result = normalize_url(value, tracking_policy="drop-known-tracking-v1")
    assert result.normalized == (
        "https://example.com/?&UTM_source=y&utm_id=1&%75tm_source=z&a=1&a=2&#utm_source=keep"
    )
    assert any(step.code == "drop_known_tracking" for step in result.transformations)
    assert (
        normalize_url(
            "https://e.com/?utm_source=x", tracking_policy="drop-known-tracking-v1"
        ).normalized
        == "https://e.com/?"
    )
    assert result.normalized is not None
    assert (
        normalize_url(result.normalized, tracking_policy="drop-known-tracking-v1").normalized
        == result.normalized
    )
    assert URLNormalization.model_validate_json(result.model_dump_json()) == result


def test_normalizes_only_safe_equivalences() -> None:
    assert importlib.util.find_spec("editalfinder_v2.domain.url_identity") is not None
    from editalfinder_v2.domain.url_identity import normalize_url

    result = normalize_url("HTTPS://EXAMPLE.COM:0443/a%2fb?x=%aa#SPA")
    assert result.normalized == "https://example.com/a%2Fb?x=%AA#SPA"
    assert result.original == "HTTPS://EXAMPLE.COM:0443/a%2fb?x=%aa#SPA"
    assert result.code == "url_normalized"
    assert result.transformations
