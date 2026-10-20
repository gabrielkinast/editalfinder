"""Pure-boundary regressions; original validation failed the first three cases."""

import json

import pytest

from editalfinder_v2.domain.safety import parse_payload, resolve_pointer, valid_url


def test_extreme_array_index_is_rejected_without_exception():
    assert resolve_pointer(["Edital 01/2026"], "/" + "9" * 5000) == (False, None)


def test_url_control_is_rejected():
    assert not valid_url("https://example.org/\x00call")


def test_numeric_overflow_is_rejected():
    with pytest.raises(ValueError):
        parse_payload('{"amount":1e999}')


@pytest.mark.parametrize(
    "payload,pointer,expected",
    [
        (None, "", (True, None)),
        ({"": None}, "/", (True, None)),
        ({"a/b": {"~key": [False]}}, "/a~1b/~0key/0", (True, False)),
        ({"~1": "literal"}, "/~01", (True, "literal")),
        ({"01": 1}, "/01", (True, 1)),
        ({"missing": None}, "/other", (False, None)),
        (["first"], "/1", (False, None)),
        ("scalar", "/key", (False, None)),
    ],
)
def test_pointer_resolution(payload, pointer, expected):
    assert resolve_pointer(payload, pointer) == expected


@pytest.mark.parametrize(
    "pointer", ["x", "#", "/~", "/~2", "/-", "/01", "/-1", "/+0", "/١", "/1.0", "/" + "9" * 4095]
)
def test_invalid_array_pointers(pointer):
    assert resolve_pointer(["first"], pointer) == (False, None)


def test_pointer_exact_limits():
    key = "x" * 4095
    assert resolve_pointer({key: 1}, "/" + key) == (True, 1)
    assert resolve_pointer({key + "x": 1}, "/" + key + "x") == (False, None)
    payload = "leaf"
    for _ in range(65):
        payload = {"a": payload}
    assert resolve_pointer(payload, "/a" * 64) == (True, {"a": "leaf"})
    assert resolve_pointer(payload, "/a" * 65) == (False, None)


@pytest.mark.parametrize(
    "text",
    [
        '{"a":1,"a":2}',
        '{"nested":{"a":1,"\\u0061":2}}',
        "NaN",
        "Infinity",
        "-Infinity",
        "-1e999",
        "1e-999",
        "-1e-999",
        "1.7976931348623159e308",
        '"\\ud800"',
        '"\\udfff"',
        '{"\\ud800":1}',
        '"\ud800"',
        "[1,]",
        "true false",
        "",
        "01",
        "1" * 257,
        "0." + "1" * 255,
        "1e" + "0" * 255,
        "[" * 65 + "0" + "]" * 65,
    ],
)
def test_unsafe_payloads_raise_value_error(text):
    with pytest.raises(ValueError):
        parse_payload(text)


@pytest.mark.parametrize("value", [None, True, False, 0, -13, 1.25, "ação 😀", {"a": [None, True]}])
def test_standard_payload_roundtrip(value):
    assert parse_payload(json.dumps(value)) == value


def test_json_depth_ignores_string_delimiters():
    assert parse_payload('"[{}]\\""') == '[{}]"'
    assert parse_payload("[" * 64 + "0" + "]" * 64)


def test_payload_byte_limit_is_utf8_not_character_count():
    assert len(parse_payload('"' + "a" * (2 * 1024 * 1024 - 2) + '"')) == 2097150
    for text in ['"' + "a" * (2 * 1024 * 1024 - 1) + '"', '"' + "é" * 1048576 + '"']:
        with pytest.raises(ValueError):
            parse_payload(text)


def test_payload_node_limit_includes_root():
    assert len(parse_payload("[" + ",".join(["0"] * 99999) + "]")) == 99999
    with pytest.raises(ValueError):
        parse_payload("[" + ",".join(["0"] * 100000) + "]")


def test_numeric_token_boundary():
    assert parse_payload("1" * 256) == int("1" * 256)
    assert parse_payload("1e308") == 1e308


@pytest.mark.parametrize(
    "value",
    [
        None,
        1,
        [],
        "",
        "ftp://example.org",
        "//example.org",
        "https:///path",
        "https://user:secret@example.org",
        "https://@example.org",
        "https://example.org\\evil",
        "https://example.org/a b",
        "\x00https://example.org",
        "https://example.org/\n",
        "https://example.org/\x7f",
        "https://example.org/\u0085",
        "https://example.org/\u200b",
        "https://example.org/%",
        "https://example.org/%xz",
        "https://example.org/%0a",
        "https://example.org/%00",
        "https://example.org/%5C",
        "https://example.org:",
        "https://example.org:0",
        "https://example.org:65536",
        "https://example.org:+80",
        "https://example.org:abc",
        "https://example.org:" + "9" * 5000,
        "https://[::1",
        "https://[::1]evil",
        "https://[example.org]",
        "https://::1",
        "https://[fe80::1%25eth0]",
        "https://example..org",
        "https://-example.org",
        "https://example-.org",
        "https://bad_host.org",
        "https://%65xample.org",
        "https://example.org%2f.evil",
        "https://a" + "a" * 63 + ".org",
        "https://999.1.1.1",
        "https://127.1",
        "https://127.00.0.1",
        "https://\ud800.org",
        "https://xn--.org",
        "https://example.org/\ud800",
    ],
)
def test_malformed_urls_are_rejected(value):
    assert not valid_url(value)


@pytest.mark.parametrize(
    "value",
    [
        "https://example.org",
        "HTTP://EXAMPLE.ORG:80/a?b=c#d",
        "https://example.org:65535",
        "https://example.org./path",
        "https://127.0.0.1:8080/a",
        "http://[::1]:80",
        "https://[2001:db8::1]/",
        "https://münchen.de/ação",
        "https://xn--mnchen-3ya.de/",
        "https://例え.テスト/",
        "https://example.org/a%20b?next=%2Fcall",
    ],
)
def test_valid_http_urls_are_allowed(value):
    assert valid_url(value)
