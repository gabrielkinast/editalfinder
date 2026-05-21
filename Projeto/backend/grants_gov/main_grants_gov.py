"""
Grants.gov — ponto de entrada do pipeline.

A partir da migração Simpler, delega para main_simpler_grants_gov (links canônicos
https://simpler.grants.gov/opportunity/...). O módulo legado search2 + view-opportunity
permanece em grants_gov/_legacy_main_grants_gov.py apenas para referência.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from grants_gov.main_simpler_grants_gov import main as simpler_main


def main() -> None:
    print("[GRANTS_GOV] Redirecionando para coleta Simpler.Grants.gov...")
    simpler_main()


if __name__ == "__main__":
    main()
