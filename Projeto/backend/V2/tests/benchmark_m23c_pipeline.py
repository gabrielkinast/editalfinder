"""Sequential fresh-process benchmark of the frozen M2.3c structured pipeline."""

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path

import pydantic
from m23c_fixtures import build, case_by_id
from test_m23c_resources import resource_input

from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_budget import projected_output_cost
from editalfinder_v2.domain.integration_models import IntegrationReport
from editalfinder_v2.domain.models import OperationalError

CASES = ("M23C-A-001", "M23C-B-001", "M23C-C-001", "M23C-E-001", "near", "over")


def measure(case):
    data = resource_input(case) if case in {"near", "over"} else build(case_by_id(case))
    charge = projected_output_cost(data)
    # Construction and admission-estimator search excluded; complete integration, including
    # IntegrationReport's own recomputation, serialization and received validation included.
    tracemalloc.start()
    started = time.perf_counter()
    report = integrate(data)
    integrated = time.perf_counter()
    wire = report.model_dump_json()
    dumped = time.perf_counter()
    restored = type(report).model_validate_json(wire)
    validated = time.perf_counter()
    assert restored == report
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert isinstance(report, OperationalError if case == "over" else IntegrationReport)
    return {
        "case_id": case,
        "result": type(report).__name__,
        "error_code": report.code if isinstance(report, OperationalError) else None,
        "charge_bytes": charge,
        "unique_snapshot_bytes": sum(
            len(s.payload_json.encode("utf-8"))
            for s in {s for c in data.candidates for s in c.context.snapshots}
        ),
        "serialized_bytes": len(wire.encode("utf-8")),
        "integration_seconds": integrated - started,
        "serialization_seconds": dumped - integrated,
        "validation_seconds": validated - dumped,
        "tracemalloc_peak_bytes": peak,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--child", choices=CASES)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.child:
        print(json.dumps(measure(args.child)))
        return
    assert args.output is not None
    results = []
    for case in CASES:
        samples = []
        for _ in range(3):
            child = subprocess.run(
                [sys.executable, "-B", __file__, "--child", case],
                check=True,
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            samples.append(json.loads(child.stdout))
        numeric = (
            "integration_seconds",
            "serialization_seconds",
            "validation_seconds",
            "tracemalloc_peak_bytes",
        )
        results.append(
            {
                "case_id": case,
                "samples": samples,
                "median": {k: statistics.median(s[k] for s in samples) for k in numeric},
            }
        )
    output = {
        "methodology": "3 fresh sequential processes per case; input construction excluded; "
        "tracemalloc covers integrate/dump/received DTO validation; no timing acceptance threshold",
        "caveats": "Admission budget is not RSS. Over case validates OperationalError, "
        "not a report. Synthetic offline data cannot establish extraction precision/recall "
        "or production SLA.",
        "environment": {
            "python": sys.version,
            "pydantic": pydantic.__version__,
            "platform": platform.platform(),
            "cpu_count": os.cpu_count(),
            "processor": platform.processor(),
        },
        "results": results,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
