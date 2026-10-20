"""Controlled offline benchmark: fresh sequential children, small synthetic payloads.

PYTHONPATH=src:tests .venv/bin/python -B tests/benchmark_m23b_consistency.py \
    --output /absolute/results.json

tracemalloc peaks are Python allocations across integrate/dump/replay, NOT RSS caps.
"""

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path

from m23_fixtures import adapt_records, build_case, records_for

from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_budget import projected_output_cost
from editalfinder_v2.domain.integration_models import IntegratedCandidate, IntegrationReport
from editalfinder_v2.domain.models import OperationalError

CASES = ("grant", "ambiguous", "investment", "diagnostic_24", "refused_32")


def child(case: str) -> dict[str, object]:
    if case == "diagnostic_24":
        rows = [
            {"role": role, "value": f"unsupported-{i}"}
            for role in ("area", "resource_type", "opportunity_type")
            for i in range(8)
        ]
        data = adapt_records([{**records_for("grant")[0], "taxonomy_claims": rows}])
    elif case == "refused_32":
        data = adapt_records([records_for("grant")[0]] * 32)
    else:
        data = build_case(case)
    charge = projected_output_cost(data)
    tracemalloc.start()
    started = time.perf_counter()
    report = integrate(data)
    integrated = time.perf_counter()
    wire = report.model_dump_json()
    dumped = time.perf_counter()
    restored = type(report).model_validate_json(wire)
    replayed = time.perf_counter()
    assert restored == report
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "case": case,
        "result": type(report).__name__,
        "error_code": report.code if isinstance(report, OperationalError) else None,
        "diagnostics": sum(
            len(c.diagnostics) for c in report.candidates if isinstance(c, IntegratedCandidate)
        )
        if isinstance(report, IntegrationReport)
        else 0,
        "charge_bytes": charge,
        "output_bytes": len(wire.encode("utf-8")),
        "integrate_seconds": integrated - started,
        "dump_seconds": dumped - integrated,
        "replay_seconds": replayed - dumped,
        "tracemalloc_peak_bytes": peak,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child", choices=CASES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.child:
        print(json.dumps(child(args.child)))
        return
    assert args.output is not None, "--output required for parent"
    results = []
    for case in CASES:
        samples = []
        for _ in range(3):
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            completed = subprocess.run(
                [sys.executable, "-B", __file__, "--child", case],
                env=env,
                check=True,
                capture_output=True,
                text=True,
            )
            samples.append(json.loads(completed.stdout))
        numeric = ("integrate_seconds", "dump_seconds", "replay_seconds", "tracemalloc_peak_bytes")
        results.append(
            {
                "case": case,
                "samples": samples,
                "median": {k: statistics.median(s[k] for s in samples) for k in numeric},
            }
        )
    args.output.write_text(
        json.dumps(
            {
                "method": "3 fresh sequential child processes per case",
                "python": sys.version,
                "results": results,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(args.output.resolve())


if __name__ == "__main__":
    main()
