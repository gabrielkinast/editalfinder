"""Offline microbenchmark. Run from V2 with PYTHONPATH=src:tests.

Optional --baseline points to the pre-indexing validation.py for a same-process
comparison (both engines use the current full-result audit models).
"""

import argparse
import importlib.util
import json
import platform
import statistics
from datetime import date
from pathlib import Path
from time import perf_counter

from fixtures import example

from editalfinder_v2.domain.models import FieldAssertion, OpportunityCandidate, ValidationReport
from editalfinder_v2.domain.validation import validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--repeats", type=int, default=7)
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    engines = {"indexed": validate}
    if args.baseline:
        spec = importlib.util.spec_from_file_location(
            "editalfinder_v2.domain._benchmark_baseline", args.baseline
        )
        if spec is None or spec.loader is None:
            raise ValueError("Cannot load baseline module")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        engines["baseline"] = module.validate
    snapshot, original = example()
    rows = []
    for scenario in ("unique_null", "repeated_null", "unique_evidence"):
        for size in (100, 300, 600, 1200):
            assertions = tuple(
                FieldAssertion(
                    field="unsupported" if scenario == "repeated_null" else f"unsupported_{i}",
                    value="invalid" if scenario == "unique_evidence" else None,
                    evidence=original.assertions[0].evidence
                    if scenario == "unique_evidence"
                    else (),
                )
                for i in range(size)
            )
            candidate = OpportunityCandidate.model_validate(
                {**original.model_dump(), "assertions": assertions}
            )
            reports = []
            row = {"scenario": scenario, "assertions": size, "median_seconds": {}}
            for name, engine in engines.items():
                report = engine(candidate, (snapshot,), reference_date=date(2026, 6, 1))
                assert isinstance(report, ValidationReport)
                reports.append(report)
                samples = []
                for _ in range(args.repeats):
                    start = perf_counter()
                    engine(candidate, (snapshot,), reference_date=date(2026, 6, 1))
                    samples.append(perf_counter() - start)
                row["median_seconds"][name] = statistics.median(samples)
            assert all(report == reports[0] for report in reports), scenario
            row["identical_reports"] = True
            rows.append(row)
    print(
        json.dumps(
            {"python": platform.python_version(), "repeats": args.repeats, "rows": rows}, indent=2
        )
    )


if __name__ == "__main__":
    main()
