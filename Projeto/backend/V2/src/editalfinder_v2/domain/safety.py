"""Pure, bounded validation of untrusted JSON, RFC 6901 pointers and HTTP URLs.

No fetching or DNS resolution occurs here; URL validity is not an SSRF policy.
JSON limits: 2 MiB UTF-8, 64 nested containers, 100,000 value nodes (including
root, excluding object keys), and 256 characters per numeric token. Invalid
payloads raise ValueError; missing/invalid pointers return (False, None).
"""

import json
import math
import re
import unicodedata
from ipaddress import IPv4Address, IPv6Address
from typing import Never, cast
from urllib.parse import urlsplit

from pydantic import JsonValue

MAX_PAYLOAD_BYTES = 2 * 1024 * 1024
MAX_DEPTH = 64
MAX_NODES = 100_000
MAX_NUMBER_LENGTH = 256
MAX_POINTER_LENGTH = 4096


def resolve_pointer(payload: JsonValue, pointer: str) -> tuple[bool, JsonValue]:
    """Resolve a plain (not URI-fragment) pointer without unbounded int parsing."""
    if len(pointer) > MAX_POINTER_LENGTH:
        return False, None
    if not pointer:
        return True, payload
    if (
        not pointer.startswith("/")
        or pointer.count("/") > MAX_DEPTH
        or re.search(r"~(?![01])", pointer)
    ):
        return False, None
    node = payload
    for token in pointer.split("/")[1:]:
        key = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if key not in node:
                return False, None
            node = node[key]
        elif isinstance(node, list):
            if not re.fullmatch(r"0|[1-9][0-9]*", key):
                return False, None
            # Compare decimal strings before int(): even a bounded pointer can
            # carry thousands of index digits, while len(list) fits Py_ssize_t.
            size = str(len(node))
            if len(key) > len(size) or (len(key) == len(size) and key >= size):
                return False, None
            node = node[int(key)]
        else:
            return False, None
    return True, node


def _unique_object(pairs: list[tuple[str, JsonValue]]) -> dict[str, JsonValue]:
    result: dict[str, JsonValue] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON member")
        key.encode("utf-8")  # Reject unpaired escaped surrogates in keys too.
        result[key] = value
    return result


def _invalid_constant(value: str) -> Never:
    raise ValueError("Non-finite JSON number")


def _integer(token: str) -> int:
    if len(token) > MAX_NUMBER_LENGTH:
        raise ValueError("JSON numeric token too long")
    return int(token)


def _float(token: str) -> float:
    if len(token) > MAX_NUMBER_LENGTH:
        raise ValueError("JSON numeric token too long")
    value = float(token)
    if not math.isfinite(value):
        raise ValueError("Non-finite JSON number")
    if value == 0 and re.search(r"[1-9]", token.lower().split("e", 1)[0]):
        raise ValueError("JSON number underflows the supported float representation")
    return value


def _check_depth(text: str) -> None:
    """Bound decoder recursion before decoding; json.loads checks syntax."""
    depth = 0
    in_string = False
    escaped = False
    for char in text:
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > MAX_DEPTH:
                raise ValueError("JSON nesting limit exceeded")
        elif char in "]}":
            depth -= 1


def parse_payload(text: str) -> JsonValue:
    """Decode strict JSON within explicit resource limits; never accept infinity."""
    # Character precheck avoids allocating a UTF-8 copy of an oversized input.
    if len(text) > MAX_PAYLOAD_BYTES or len(text.encode("utf-8")) > MAX_PAYLOAD_BYTES:
        raise ValueError("JSON byte limit exceeded")
    _check_depth(text)
    try:
        value = cast(
            JsonValue,
            json.loads(
                text,
                object_pairs_hook=_unique_object,
                parse_constant=_invalid_constant,
                parse_int=_integer,
                parse_float=_float,
            ),
        )
    except RecursionError as exc:
        raise ValueError("JSON nesting limit exceeded") from exc
    pending = [value]
    count = 0
    while pending:
        node = pending.pop()
        count += 1
        if count > MAX_NODES:
            raise ValueError("JSON node limit exceeded")
        if isinstance(node, str):
            node.encode("utf-8")
        elif isinstance(node, dict):
            pending.extend(node.values())
        elif isinstance(node, list):
            pending.extend(node)
        if count + len(pending) > MAX_NODES:
            raise ValueError("JSON node limit exceeded")
    return value


def _valid_host(host: str) -> bool:
    if not host or "%" in host:
        return False
    if ":" in host:
        IPv6Address(host)
        return True
    ascii_host = host.encode("idna").decode("ascii").lower()
    if ascii_host.endswith("."):
        ascii_host = ascii_host[:-1]
    if not ascii_host or len(ascii_host) > 253:
        return False
    if re.fullmatch(r"[0-9.]+", ascii_host):
        IPv4Address(ascii_host)
        return True
    for label in ascii_host.split("."):
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label):
            return False
        if label.startswith("xn--"):
            # ASCII input bypasses IDNA encoding validation; check A-labels.
            decoded = label.encode("ascii").decode("idna")
            if decoded.encode("idna").decode("ascii").lower() != label:
                return False
    return True


def valid_url(value: object) -> bool:
    """Accept well-formed HTTP(S) URLs, not credentials or parser ambiguities."""
    if not isinstance(value, str) or not value:
        return False
    if any(
        char.isspace() or char == "\\" or unicodedata.category(char) in {"Cc", "Cf", "Cs"}
        for char in value
    ):
        return False
    if re.search(r"%(?![0-9a-fA-F]{2})", value):
        return False
    if re.search(r"%(?:0[0-9a-f]|1[0-9a-f]|7f|5c)", value, re.IGNORECASE):
        return False
    try:
        url = urlsplit(value)
        if url.scheme not in {"http", "https"} or not url.netloc or "@" in url.netloc:
            return False
        authority = url.netloc
        if authority.startswith("["):
            closing = authority.find("]")
            if closing < 0:
                return False
            IPv6Address(authority[1:closing])
            suffix = authority[closing + 1 :]
            if suffix and not suffix.startswith(":"):
                return False
        else:
            if "[" in authority or "]" in authority or authority.count(":") > 1:
                return False
            suffix = ":" + authority.split(":", 1)[1] if ":" in authority else ""
        if suffix:
            port = suffix[1:]
            if not re.fullmatch(r"[0-9]{1,5}", port) or not 1 <= int(port) <= 65535:
                return False
        return url.hostname is not None and _valid_host(url.hostname)
    except (ValueError, UnicodeError):
        return False
