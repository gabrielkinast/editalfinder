"""Offline conservative identity, not URL authorization or an SSRF boundary.

Path/query/fragment Unicode is preserved verbatim (no NFC or UTF-8 quoting).
Only host Unicode uses NFC and reversible stdlib IDNA. No DNS is performed.
"""

import ipaddress
import re
import unicodedata
from typing import Literal, Self

from pydantic import model_validator

from .models import Contract

TrackingPolicy = Literal["preserve-v1", "drop-known-tracking-v1"]
Trace = tuple[str, str, str]
Outcome = tuple[str | None, str, tuple[Trace, ...]]


class URLTransformation(Contract):
    code: str
    before: str
    after: str


class URLNormalization(Contract):
    original: str
    normalized: str | None
    code: Literal["url_normalized", "url_invalid", "url_ambiguous_idna", "url_limit_exceeded"]
    normalization_version: Literal["url-conservative-v1"] = "url-conservative-v1"
    tracking_policy: TrackingPolicy = "preserve-v1"
    transformations: tuple[URLTransformation, ...] = ()

    @model_validator(mode="after")
    def replay(self) -> Self:
        expected = _normalize(self.original, self.tracking_policy)
        actual = (
            self.normalized,
            self.code,
            tuple((step.code, step.before, step.after) for step in self.transformations),
        )
        if actual != expected:
            raise ValueError("URL normalization must reproduce the original and policy")
        return self


class _AmbiguousIDNA(ValueError):
    pass


def _host(value: str) -> str:
    if value.startswith("["):
        if not value.endswith("]") or "%" in value:
            raise ValueError("Invalid IPv6")
        ipaddress.IPv6Address(value[1:-1])
        # Preserve the IPv6 spelling except hex case; no extra equivalence claims.
        return value.lower()
    lowered = unicodedata.normalize("NFC", value).lower()
    encoded = lowered.encode("idna").decode("ascii").lower()
    decoded = encoded.encode("ascii").decode("idna").lower()
    if not value.isascii() and decoded != lowered:
        raise _AmbiguousIDNA
    if decoded.encode("idna").decode("ascii").lower() != encoded:
        raise ValueError("Invalid punycode")
    body = encoded[:-1] if encoded.endswith(".") else encoded
    if not body or len(body) > 253:
        raise ValueError("Invalid hostname length")
    labels = body.split(".")
    if any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", x) for x in labels):
        raise ValueError("Invalid hostname label")
    if labels[-1].isdigit() or labels[-1].startswith("0x"):
        ipaddress.IPv4Address(body)
    return encoded


def _normalize(value: str, policy: TrackingPolicy) -> Outcome:
    if len(value) > 8192:
        return None, "url_limit_exceeded", ()
    try:
        if len(value.encode("utf-8")) > 32768:
            return None, "url_limit_exceeded", ()
        if any(c.isspace() or unicodedata.category(c) == "Cc" or c in '\\<>"`{}|^' for c in value):
            raise ValueError("Unsafe URL characters")
        if re.search(r"%(?![0-9a-fA-F]{2})", value):
            raise ValueError("Malformed percent escape")
        if re.search(r"%(?:0[0-9a-f]|1[0-9a-f]|7f|5c)", value, re.IGNORECASE):
            raise ValueError("Encoded control or backslash")
        match = re.fullmatch(r"(https?)://([^/?#]+)(.*)", value, re.IGNORECASE | re.ASCII)
        if match is None:
            raise ValueError("Expected HTTP(S) authority")
        scheme, authority, suffix = match.groups()
        if any(unicodedata.category(c) in {"Cf", "Cs"} for c in suffix):
            raise ValueError("Unsafe Unicode URL suffix")
        if "@" in authority or "%" in authority:
            raise ValueError("Credentials or encoded authority")
        if authority.startswith("["):
            close = authority.index("]")
            raw_host, port_suffix = authority[: close + 1], authority[close + 1 :]
        else:
            raw_host, separator, port = authority.partition(":")
            port_suffix = separator + port
        host = _host(raw_host)
        port_normalized = ""
        if port_suffix:
            if not re.fullmatch(r":[0-9]+", port_suffix):
                raise ValueError("Invalid port")
            digits = port_suffix[1:].lstrip("0") or "0"
            if len(digits) > 5 or not 1 <= int(digits) <= 65535:
                raise ValueError("Port out of range")
            if int(digits) != {"http": 80, "https": 443}[scheme.lower()]:
                port_normalized = ":" + digits
        traces: list[Trace] = []
        for code, before, after in (
            ("scheme_lowercase", scheme, scheme.lower()),
            ("host_canonicalize", raw_host, host),
            ("port_canonicalize", port_suffix, port_normalized),
        ):
            if before != after:
                traces.append((code, before, after))
        if policy == "drop-known-tracking-v1":
            path_query, marker, fragment = suffix.partition("#")
            path, query_marker, query = path_query.partition("?")
            if query_marker:
                names = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"}
                kept = "&".join(
                    pair for pair in query.split("&") if pair.partition("=")[0] not in names
                )
                if kept != query:
                    traces.append(("drop_known_tracking", query, kept))
                suffix = path + "?" + kept + marker + fragment
        escaped = re.sub(r"%[0-9a-fA-F]{2}", lambda m: m[0].upper(), suffix)
        if escaped != suffix:
            traces.append(("percent_hex_uppercase", suffix, escaped))
        normalized = scheme.lower() + "://" + host + port_normalized + escaped
        if len(normalized) > 8192 or len(normalized.encode("utf-8")) > 32768:
            return None, "url_limit_exceeded", ()
        return normalized, "url_normalized", tuple(traces)
    except _AmbiguousIDNA:
        return None, "url_ambiguous_idna", ()
    except (ValueError, UnicodeError):
        return None, "url_invalid", ()


def normalize_url(
    value: str, *, tracking_policy: TrackingPolicy = "preserve-v1"
) -> URLNormalization:
    """Return a replay-validated result, including for malformed string input.

    Inputs must be valid UTF-8 text, as for every M1.1a Contract. Lone surrogates
    raise Pydantic ValidationError instead of creating an unserializable DTO.
    """
    normalized, code, traces = _normalize(value, tracking_policy)
    return URLNormalization(
        original=value,
        normalized=normalized,
        code=code,
        tracking_policy=tracking_policy,
        transformations=tuple(URLTransformation(code=c, before=b, after=a) for c, b, a in traces),
    )
