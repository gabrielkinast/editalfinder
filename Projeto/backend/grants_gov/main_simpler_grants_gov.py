"""
Coleta Grants.gov via Simpler.Grants.gov (links canônicos).

Uso:
  python grants_gov/main_simpler_grants_gov.py
  python grants_gov/main_simpler_grants_gov.py --max-pages 3 --max-items 50

Dry-run (artefatos em audit_reports_main_pipeline/grants_simpler_dryrun/):
  python scripts/grants_simpler_dryrun.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs
from grants_gov.simpler_grants_common import collect_opportunities

DEFAULT_MAX_PAGES = 4
DEFAULT_MAX_ITEMS = 200
DEFAULT_PAGE_SIZE = 25


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Coleta Simpler.Grants.gov")
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    parser.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument(
        "--include-historic",
        action="store_true",
        help="Incluir Closed/Archived (marcados hidden_* em curadoria_front)",
    )
    args = parser.parse_args(argv)

    print("[SIMPLER_GRANTS] Iniciando coleta...")
    items, meta = collect_opportunities(
        max_pages=args.max_pages,
        page_size=args.page_size,
        max_items=args.max_items,
        include_historic=args.include_historic,
    )
    print(f"[SIMPLER_GRANTS] modo={meta.get('api_mode')} itens={len(items)}")

    out_dir = Path(__file__).parent
    save_outputs(out_dir, "grants_gov", items)

    meta_path = out_dir / "outputs" / "grants_simpler_collect_meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[SIMPLER_GRANTS] meta: {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
