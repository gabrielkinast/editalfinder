"""Controlled offline benchmark; run in isolated sequential child processes.

PYTHONPATH=src:tests .venv/bin/python -B tests/benchmark_integration_budget.py \
    --output /absolute/results.json
For baseline, put a frozen pre-change src directory first in PYTHONPATH.
Each case is repeated in a fresh process. No time/RSS thresholds are CI gates.
"""

import argparse
import json
import os
import platform
import resource
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Any

import pydantic
from m23_fixtures import adapt_records, records_for
from pydantic import ValidationError

from editalfinder_v2.domain.integration import integrate
from editalfinder_v2.domain.integration_models import IntegrationReport
from editalfinder_v2.domain.models import OperationalError


def worker(
    count: int, padding: int, replay: Path | None, save_replay: Path | None
) -> dict[str, Any]:
    if replay is not None:
        wire = replay.read_text(encoding="utf-8")
        tracemalloc.start()
        start = time.perf_counter()
        outcome = "accepted"
        try:
            IntegrationReport.model_validate_json(wire)
        except ValidationError as exc:
            if not any(
                "integration_output_budget_exceeded" in error["msg"]
                for error in exc.errors(include_input=False)
            ):
                raise
            outcome = "budget_refused"
        elapsed = time.perf_counter() - start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {
            "mode": "legacy_replay",
            "result": outcome,
            "restore_s": elapsed,
            "restore_peak_bytes": peak,
            "wire_bytes": len(wire.encode()),
            "rss_peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        }
    record = records_for("grant")[0]
    if padding:
        record["unasserted"] = {"padding": "x" * padding}
    data = adapt_records([record] * count)
    # Fixtures/input already exist; measure the integration's additional allocations.
    tracemalloc.start()
    start = time.perf_counter()
    report = integrate(data)
    elapsed = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.reset_peak()
    start = time.perf_counter()
    wire = report.model_dump_json()
    dump_elapsed = time.perf_counter() - start
    _, dump_peak = tracemalloc.get_traced_memory()
    tracemalloc.reset_peak()
    start = time.perf_counter()
    if isinstance(report, IntegrationReport):
        restored = IntegrationReport.model_validate_json(wire)
    else:
        restored = OperationalError.model_validate_json(wire)
    restore_elapsed = time.perf_counter() - start
    _, restore_peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert restored == report
    if save_replay is not None and count == 32 and padding == 0:
        assert isinstance(report, IntegrationReport)
        save_replay.write_text(wire, encoding="utf-8")
    return {
        "mode": "integration",
        "candidates": count,
        "padding_per_record": padding,
        "result": type(report).__name__,
        "snapshot_bytes": len(data.candidates[0].context.snapshots[0].payload_json.encode()),
        "payload_occurrences": wire.count('"payload_json"'),
        "wire_bytes": len(wire.encode()),
        "integrate_s": elapsed,
        "dump_s": dump_elapsed,
        "restore_s": restore_elapsed,
        "integrate_peak_bytes": peak,
        "dump_peak_bytes": dump_peak,
        "restore_peak_bytes": restore_peak,
        "rss_peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--count", type=int, default=1, choices=(1, 4, 16, 32))
    parser.add_argument("--padding", type=int, default=0, choices=(0, 1024))
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--save-replay", type=Path)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 5:
        parser.error("repeats must be 1..5")
    if args.worker:
        print(json.dumps(worker(args.count, args.padding, args.replay, args.save_replay)))
        return
    if args.output is None:
        parser.error("--output is required")
    scenarios = [(1, 0), (4, 0), (16, 0), (32, 0), (32, 1024)]
    if args.replay is not None:
        scenarios = [(32, 0)]
    rows = []
    for count, padding in scenarios:
        samples = []
        for _ in range(args.repeats):
            command = [
                sys.executable,
                "-B",
                str(Path(__file__).resolve()),
                "--worker",
                "--count",
                str(count),
                "--padding",
                str(padding),
            ]
            if args.replay is not None:
                command += ["--replay", str(args.replay)]
            if args.save_replay is not None:
                command += ["--save-replay", str(args.save_replay)]
            result = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            samples.append(json.loads(result.stdout))
        median = {
            key: statistics.median(sample[key] for sample in samples)
            if isinstance(value, (int, float))
            else value
            for key, value in samples[0].items()
        }
        rows.append({"median": median, "samples": samples})
    output = {
        "python": platform.python_version(),
        "pydantic": pydantic.__version__,
        "platform": platform.platform(),
        "source": str(sys.modules[integrate.__module__].__file__),
        "repeats": args.repeats,
        "tracemalloc": True,
        "note": (
            "stage peaks include live objects from preceding stages; "
            "RSS is process lifetime Linux KiB"
        ),
        "results": rows,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
