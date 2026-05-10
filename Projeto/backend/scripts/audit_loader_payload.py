#!/usr/bin/env python3
"""Alias para auditoria focada em payload do loader (usa audit_pipeline)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    args = sys.argv[1:]
    cmd = [sys.executable, str(ROOT / "scripts" / "audit_pipeline.py")] + args
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
