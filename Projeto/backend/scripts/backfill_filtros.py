#!/usr/bin/env python3
"""
Backfill seguro: preenche colunas de filtro (schema estendido) a partir de extras JSONB
e/ou fragmentos em edital_extra_campo. Não apaga dados; em --apply só atualiza
campos vazios/nulos quando o novo valor é mais informativo.

Uso (na raiz do repo):
  python scripts/backfill_filtros.py --dry-run
  python scripts/backfill_filtros.py --apply

Requer variáveis Supabase em CORE/.env e migração aplicada em staging (colunas novas).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "CORE"
sys.path.insert(0, str(CORE))

from db import supabase  # noqa: E402
from taxonomy_filtros import extras_to_filter_columns  # noqa: E402


def _is_empty_col(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, str) and not val.strip():
        return True
    if isinstance(val, list) and len(val) == 0:
        return True
    return False


def fetch_fragments(id_edital: int) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        r = (
            supabase.table("edital_extra_campo")
            .select("chave", "valor")
            .eq("id_edital", id_edital)
            .execute()
        )
        for row in r.data or []:
            if not isinstance(row, dict):
                continue
            k, raw = row.get("chave"), row.get("valor")
            if not k:
                continue
            if isinstance(raw, str):
                try:
                    out[str(k)] = json.loads(raw)
                except Exception:
                    out[str(k)] = raw
            else:
                out[str(k)] = raw
    except Exception:
        pass
    return out


def build_patch(row: Dict[str, Any], apply_extras_column: bool) -> Dict[str, Any]:
    """Monta patch só com campos que hoje estão vazios e podem ser preenchidos."""
    id_edital = row.get("id_edital")
    merged_extras: Dict[str, Any] = {}
    if isinstance(row.get("extras"), dict):
        merged_extras.update(row["extras"])
    merged_extras = {**fetch_fragments(int(id_edital)), **merged_extras}

    pseudo = {
        "titulo": row.get("titulo"),
        "tipo_recurso": row.get("tipo_recurso") or merged_extras.get("tipo_recurso"),
        "programa": row.get("programa"),
        "acao": row.get("acao"),
        "extras": merged_extras,
    }
    candidates = extras_to_filter_columns(pseudo, merged_extras)
    patch: Dict[str, Any] = {}

    for key, val in candidates.items():
        if _is_empty_col(row.get(key)) and not _is_empty_col(val):
            patch[key] = val

    if apply_extras_column and _is_empty_col(row.get("extras")) and merged_extras:
        patch["extras"] = merged_extras

    return patch


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Somente imprimir alterações")
    ap.add_argument("--apply", action="store_true", help="Aplicar updates no banco")
    ap.add_argument("--limit", type=int, default=500, help="Máximo de linhas por página")
    args = ap.parse_args()

    if args.apply and args.dry_run:
        print("Use apenas um de --apply ou --dry-run")
        sys.exit(2)
    if not args.apply and not args.dry_run:
        print("Informe --dry-run ou --apply")
        sys.exit(2)

    offset = 0
    total_would = 0
    total_applied = 0
    has_extras_col = True

    while True:
        try:
            r = (
                supabase.table("edital")
                .select("*")
                .range(offset, offset + args.limit - 1)
                .execute()
            )
        except Exception as e:
            print("Erro ao listar edital:", e)
            sys.exit(1)
        rows = r.data or []
        if not rows:
            break

        for row in rows:
            if not isinstance(row, dict):
                continue
            try:
                patch = build_patch(row, apply_extras_column=has_extras_col)
            except Exception as e:
                print("skip id", row.get("id_edital"), e)
                continue
            if not patch:
                continue
            total_would += 1
            if args.dry_run:
                print(
                    f"[dry-run] id_edital={row.get('id_edital')} link={row.get('link')!r} "
                    f"patch_keys={list(patch.keys())}"
                )
            if args.apply:
                try:
                    supabase.table("edital").update(patch).eq(
                        "id_edital", row["id_edital"]
                    ).execute()
                    total_applied += 1
                except Exception as e:
                    err = str(e).lower()
                    if "extras" in err and "column" in err:
                        has_extras_col = False
                        patch2 = {k: v for k, v in patch.items() if k != "extras"}
                        if patch2:
                            supabase.table("edital").update(patch2).eq(
                                "id_edital", row["id_edital"]
                            ).execute()
                            total_applied += 1
                    else:
                        print("erro update", row.get("id_edital"), e)

        if len(rows) < args.limit:
            break
        offset += args.limit

    mode = "dry-run" if args.dry_run else "apply"
    print(f"Concluído ({mode}): linhas com patch possível = {total_would}, aplicados = {total_applied}")


if __name__ == "__main__":
    main()
