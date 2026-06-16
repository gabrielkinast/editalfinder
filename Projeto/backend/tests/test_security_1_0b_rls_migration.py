"""Testes estáticos — migration SECURITY 1.0B (sem Supabase)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "migrations" / "20260610_security_1_0b_edital_admin_write_policy.sql"


@pytest.fixture
def migration_sql() -> str:
    assert MIGRATION.is_file(), f"Missing migration: {MIGRATION}"
    return MIGRATION.read_text(encoding="utf-8")


def test_migration_contains_select_policy_for_authenticated_admin(migration_sql: str) -> None:
    low = migration_sql.lower()
    assert "edital_admin_select" in low
    assert "for select" in low
    assert "to authenticated" in low
    assert "using (public.current_app_user_is_admin())" in low
    active = re.sub(r"--.*$", "", migration_sql, flags=re.MULTILINE).lower()
    assert "edital_admin_select" in active
    assert "to anon" not in active.split("edital_admin_select")[1].split("edital_admin_insert")[0]


def test_migration_contains_insert_policy_for_authenticated_admin(migration_sql: str) -> None:
    low = migration_sql.lower()
    assert "edital_admin_insert" in low
    assert "for insert" in low
    assert "to authenticated" in low
    assert "with check (public.current_app_user_is_admin())" in low


def test_migration_contains_update_policy_for_authenticated_admin(migration_sql: str) -> None:
    low = migration_sql.lower()
    assert "edital_admin_update" in low
    assert "for update" in low
    assert "using (public.current_app_user_is_admin())" in low


def test_migration_does_not_create_delete_policy(migration_sql: str) -> None:
    active = re.sub(r"--.*$", "", migration_sql, flags=re.MULTILINE).lower()
    assert "for delete" not in active


def test_migration_does_not_use_permissive_with_check_true(migration_sql: str) -> None:
    active = re.sub(r"--.*$", "", migration_sql, flags=re.MULTILINE)
    assert not re.search(r"with\s+check\s*\(\s*true\s*\)", active, re.I)


def test_migration_enables_rls_on_edital(migration_sql: str) -> None:
    assert "alter table public.edital enable row level security" in migration_sql.lower()


def test_migration_uses_security_definer_admin_function(migration_sql: str) -> None:
    assert "security definer" in migration_sql.lower()
    assert "create or replace function public.current_app_user_is_admin()" in migration_sql.lower()
    assert "set search_path = public" in migration_sql.lower()


def test_migration_documents_manual_apply(migration_sql: str) -> None:
    assert "NÃO APLICAR AUTOMATICAMENTE" in migration_sql or "NAO APLICAR AUTOMATICAMENTE" in migration_sql.upper()


def test_migration_rollback_drops_select_policy(migration_sql: str) -> None:
    low = migration_sql.lower()
    assert "drop policy if exists edital_admin_select" in low


def test_checklist_script_passes() -> None:
    import subprocess
    import sys

    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "security_1_0b_rls_checklist.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
