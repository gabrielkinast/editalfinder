#!/usr/bin/env python3
"""
SECURITY 1.0B — checklist read-only da migration RLS edital (sem conectar ao Supabase).

Uso:
  python backend/scripts/security_1_0b_rls_checklist.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "20260610_security_1_0b_edital_admin_write_policy.sql"


def read_migration() -> str:
    if not MIGRATION.is_file():
        raise FileNotFoundError(f"Migration não encontrada: {MIGRATION}")
    return MIGRATION.read_text(encoding="utf-8")


def run_checks(sql: str) -> dict:
    low = sql.lower()
    checks: list[dict] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    active = re.sub(r"--.*$", "", sql, flags=re.MULTILINE).lower()

    add("migration_file_exists", True, str(MIGRATION))
    add("contains_for_select", "for select" in low)
    add("contains_edital_admin_select", "edital_admin_select" in low)
    add("select_uses_current_app_user_is_admin", "edital_admin_select" in low and "using (public.current_app_user_is_admin())" in low)
    add("contains_for_insert", "for insert" in low)
    add("contains_for_update", "for update" in low)
    add("contains_to_authenticated", "to authenticated" in low)
    add("contains_with_check", "with check" in low)
    add("uses_current_app_user_is_admin", "current_app_user_is_admin()" in sql)
    add("enables_rls_edital", "alter table public.edital enable row level security" in low)
    add("no_for_delete", "for delete" not in active)
    add("no_disable_rls", "disable row level security" not in low or "rollback" in low)
    add("rollback_drops_edital_admin_select", "drop policy if exists edital_admin_select" in low)
    add(
        "no_permissive_with_check_true",
        not re.search(r"with\s+check\s*\(\s*true\s*\)", active, re.I),
    )
    add(
        "no_permissive_using_true_on_edital_admin",
        not re.search(
            r"policy\s+edital_admin_(select|insert|update)[\s\S]*?using\s*\(\s*true\s*\)",
            low,
            re.I,
        ),
    )
    add("has_rollback_section", "rollback" in low)
    add("has_manual_apply_warning", "não aplicar automaticamente" in low or "nao aplicar automaticamente" in low)

    failed = [c for c in checks if not c["ok"]]
    return {
        "migration": str(MIGRATION.relative_to(ROOT.parent)),
        "passed": len(checks) - len(failed),
        "failed": len(failed),
        "ok": len(failed) == 0,
        "checks": checks,
    }


def main() -> int:
    try:
        sql = read_migration()
        report = run_checks(sql)
    except FileNotFoundError as e:
        print(json.dumps({"ok": False, "error": str(e)}, indent=2))
        return 1

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
