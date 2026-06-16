#!/usr/bin/env python3
"""
Consolidação cross-source pós-apply (Backend 10.3).

Somente leitura — não grava no banco.

Uso:
  python scripts/consolidate_post_apply_quality.py --sources grants_gov doe_arpae bndes --limit 1000
  python scripts/consolidate_post_apply_quality.py --from-db --with-backfill --output outputs/post_apply_consolidation
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from post_apply_consolidation import (  # noqa: E402
    DEFAULT_SOURCES,
    run_post_apply_consolidation,
    supabase_configured,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Consolidação pós-apply cross-source (Backend 10.3)")
    parser.add_argument(
        "--sources",
        nargs="+",
        default=list(DEFAULT_SOURCES),
        help="Fontes a consolidar (default: grants_gov doe_arpae bndes)",
    )
    parser.add_argument("--limit", type=int, default=1000, help="Limite de registros por fonte")
    parser.add_argument(
        "--from-db",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Carregar do Supabase (default: true se configurado)",
    )
    parser.add_argument(
        "--with-backfill",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enriquecer com deadline backfill em memória (default: true)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs" / "post_apply_consolidation",
        help="Diretório de saída",
    )
    args = parser.parse_args()

    from_db = args.from_db if args.from_db is not None else supabase_configured()

    result = run_post_apply_consolidation(
        ROOT,
        sources=args.sources,
        from_db=from_db,
        with_backfill=args.with_backfill,
        limit=args.limit,
        output_dir=args.output,
    )
    t = result["consolidated"]["totals"]
    db_note = "db" if from_db and supabase_configured() else "fallback"
    print(
        f"[consolidate_post_apply_quality] sources={args.sources} origin={db_note} "
        f"records={t.get('records')} actionable={t.get('actionable')} "
        f"-> {result['output_dir']}"
    )
    for ap in result["apply_summaries"]:
        print(
            f"  apply {ap.get('label')}: ok={ap.get('ok', 'unknown')} "
            f"errors={ap.get('errors', 'unknown')} status={ap.get('status')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
