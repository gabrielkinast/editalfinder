#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"

import sys

if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from db import supabase  # noqa: E402


def _print_rows(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        print("Nenhuma execução encontrada.")
        return
    for r in rows:
        print(
            f"{r.get('data_inicio')} | env={r.get('ambiente')} | status={r.get('status')} | "
            f"proc={r.get('itens_processados')} ins={r.get('itens_inseridos')} "
            f"upd={r.get('itens_atualizados')} err={r.get('erros')} fontes={r.get('fontes_carregadas')}"
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    if args.staging:
        env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
        if env not in ("staging", "local"):
            raise SystemExit("EDITALFINDER_ENV deve ser staging/local para --staging.")

    try:
        resp = (
            supabase.table("carga_execucao")
            .select(
                "id_execucao,ambiente,status,data_inicio,itens_processados,itens_inseridos,itens_atualizados,erros,fontes_carregadas"
            )
            .order("data_inicio", desc=True)
            .limit(max(1, args.limit))
            .execute()
        )
        rows = resp.data or []
        _print_rows([x for x in rows if isinstance(x, dict)])
        return 0
    except Exception as exc:
        print(f"Falha ao consultar carga_execucao: {exc}")
        hist = ROOT / "audit_reports_loader_ready" / "load_execution_history.jsonl"
        if hist.is_file():
            print("Fallback: histórico local JSONL")
            out = []
            for ln in hist.read_text(encoding="utf-8").splitlines():
                try:
                    out.append(json.loads(ln))
                except Exception:
                    continue
            out = sorted(out, key=lambda x: str(x.get("data_inicio") or ""), reverse=True)[: max(1, args.limit)]
            _print_rows(out)
            return 0
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
