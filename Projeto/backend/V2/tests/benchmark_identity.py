"""Offline M2.1 benchmarks; run with PYTHONPATH=src:tests.

Two subjects, N identifiers EACH. Duplicate-heavy input stresses preservation;
namespace-diverse input stresses distinct indexed contextual keys. Namespaces
are synthetic claims, not a registry of approved publisher authorities.
"""

import json
import platform
import statistics
from time import perf_counter

import pydantic
from test_identity import subject

from editalfinder_v2.domain.identity_models import (
    ExternalIdentifier,
    IdentifierNamespace,
    IdentityResolutionReport,
    IdentitySubject,
)
from editalfinder_v2.domain.identity_resolution import resolve_identity


def expanded(number, count, scenario):
    original = subject(number)
    base = original.identifiers[0]
    if scenario == "duplicates":
        identifiers = (base,) * count
    else:
        identifiers = tuple(
            ExternalIdentifier.model_validate(
                {
                    **base.model_dump(),
                    "namespace": IdentifierNamespace(value=f"synthetic-issuer-{i}"),
                }
            )
            for i in range(count)
        )
    return IdentitySubject.model_validate({**original.model_dump(), "identifiers": identifiers})


def main():
    rows = []
    for scenario in ("duplicates", "distinct_namespaces"):
        for count in (100, 1000, 10_000):
            left, right = expanded(1, count, scenario), expanded(2, count, scenario)
            report = resolve_identity(left, right)
            assert isinstance(report, IdentityResolutionReport)
            assert report.decision == "exact_match"
            samples = []
            for _ in range(5):
                start = perf_counter()
                result = resolve_identity(left, right)
                samples.append(perf_counter() - start)
                assert result == report
            rows.append(
                {
                    "scenario": scenario,
                    "identifiers_per_subject": count,
                    "repeats": 5,
                    "median_seconds": statistics.median(samples),
                    "min_seconds": min(samples),
                    "max_seconds": max(samples),
                    "supporting_evidence": len(report.supporting_evidence),
                    "serialized_report_bytes": len(report.model_dump_json().encode("utf-8")),
                }
            )
    print(
        json.dumps(
            {
                "python": platform.python_version(),
                "pydantic": pydantic.__version__,
                "platform": platform.platform(),
                "rows": rows,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
