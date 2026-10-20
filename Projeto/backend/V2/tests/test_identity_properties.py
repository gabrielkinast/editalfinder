"""Seeded metamorphic properties without adding a testing dependency."""

import random

from test_identity import codes, subject

from editalfinder_v2.domain.identity_resolution import resolve_identity
from editalfinder_v2.domain.url_identity import URLNormalization, normalize_url


def test_generated_url_results_roundtrip_and_successes_are_idempotent():
    rng = random.Random(2101)
    tokens = [
        "a",
        "/",
        "%2f",
        "%7e",
        "%",
        "é",
        "e\u0301",
        "?",
        "#",
        "&",
        "=",
        "+",
        "%20",
        "%00",
        "\u200b",
        "1",
        "ß",
    ]
    hosts = ["HTTPS://EXAMPLE.ORG:443/", "http://bücher.de/", "https://[::1]/", "https://faß.de/"]
    for _ in range(1000):
        text = rng.choice(hosts) + "".join(rng.choices(tokens, k=rng.randrange(0, 25)))
        for policy in ("preserve-v1", "drop-known-tracking-v1"):
            result = normalize_url(text, tracking_policy=policy)
            assert result.original == text
            assert URLNormalization.model_validate_json(result.model_dump_json()) == result
            if result.normalized is not None:
                second = normalize_url(result.normalized, tracking_policy=policy)
                assert second.normalized == result.normalized
                assert not second.transformations


def test_scoped_identity_decisions_are_symmetric_for_generated_contexts():
    rng = random.Random(2102)
    for _ in range(100):
        subjects = [
            subject(
                number,
                official=rng.choice(["A", "B", None]),
                cycle=rng.choice(["2026", "2027", None]),
                namespace=rng.choice(["issuer", "other"]),
            )
            for number in (1, 2)
        ]
        left, right = subjects
        first, reverse = resolve_identity(left, right), resolve_identity(right, left)
        assert first.decision == reverse.decision
        assert codes(first) == codes(reverse)
