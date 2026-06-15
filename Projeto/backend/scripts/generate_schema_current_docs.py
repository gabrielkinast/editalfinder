#!/usr/bin/env python3
"""Gera schema_current.sql a partir do OpenAPI do Supabase (somente leitura)."""
from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "CORE"))

from db import SUPABASE_KEY, SUPABASE_URL  # noqa: E402

BASE_TABLES = [
    "edital",
    "noticia",
    "pesquisa",
    "edital_anexo",
    "edital_extra_campo",
    "carga_execucao",
    "edital_historico",
    "cliente",
    "usuario",
    "edital_favorito",
    "edital_feedback",
    "concurso_selecao",
    "portal_estrategico",
]

PK_MAP = {
    "edital": "id_edital",
    "noticia": "id",
    "pesquisa": "id",
    "edital_anexo": "id_anexo",
    "edital_extra_campo": "id_extra",
    "carga_execucao": "id_execucao",
    "edital_historico": "id_historico",
    "cliente": "id_cliente",
    "usuario": "id_usuario",
    "edital_favorito": "id_favorito",
    "edital_feedback": "id_feedback",
    "concurso_selecao": "id_concurso",
    "portal_estrategico": "id_portal",
}

UNIQUE_LINK = {"edital", "noticia", "pesquisa", "portal_estrategico"}


def pg_type(meta: dict) -> str:
    fmt = (meta.get("format") or "").lower()
    typ = meta.get("type")
    if typ == "array":
        return "text[]"
    if fmt == "uuid":
        return "uuid"
    if fmt == "bigint":
        return "bigint"
    if fmt == "integer":
        return "integer"
    if fmt == "numeric":
        return "numeric"
    if fmt == "double precision":
        return "double precision"
    if fmt == "boolean":
        return "boolean"
    if fmt == "date":
        return "date"
    if "timestamp" in fmt:
        return "timestamptz"
    if typ == "boolean":
        return "boolean"
    if typ == "integer":
        return "integer"
    if typ == "number":
        return "numeric"
    return "jsonb" if typ is None else "text"


def fetch_spec() -> dict:
    req = urllib.request.Request(
        SUPABASE_URL.rstrip("/") + "/rest/v1/",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Accept": "application/openapi+json",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def build_table_sql(tname: str, schema: dict) -> list[str]:
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    pk = PK_MAP.get(tname)
    lines = [
        f"-- Table: public.{tname} ({len(props)} columns)",
        f"create table if not exists public.{tname} (",
    ]
    col_lines: list[str] = []
    for col, meta in sorted(props.items(), key=lambda x: (x[0] != pk, x[0])):
        sql_t = pg_type(meta)
        if col == pk and sql_t == "bigint":
            decl = f"  {col} bigserial"
        elif col == pk and sql_t == "uuid":
            decl = f"  {col} uuid"
        else:
            decl = f"  {col} {sql_t}"
        if col in required:
            decl += " not null"
        if col == "extras" and col in required:
            decl += " default '{}'::jsonb"
        if col == "ativo" and col in required:
            decl += " default true"
        if col in ("criado_em", "created_at") and col in required:
            decl += " default now()"
        if col in ("atualizado_em", "updated_at") and col in required:
            decl += " default now()"
        if col == "content_type" and tname == "noticia":
            decl += " default 'noticia'"
        if col == "content_type" and tname == "pesquisa":
            decl += " default 'pesquisa'"
        col_lines.append(decl)
    if pk:
        col_lines.append(f"  constraint {tname}_pkey primary key ({pk})")
    if tname in UNIQUE_LINK and "link" in props:
        col_lines.append(f"  constraint {tname}_link_key unique (link)")
    if tname == "concurso_selecao":
        col_lines.append("  constraint concurso_selecao_fonte_link_key unique (fonte, link)")
    lines.append(",\n".join(col_lines))
    lines.append(");")
    return lines


def main() -> None:
    spec = fetch_spec()
    defs = spec["definitions"]
    lines: list[str] = [
        "-- EditalFinder — Current Database Schema",
        "-- Generated from current database/migrations/backend usage",
        f"-- Date: {date.today().isoformat()}",
        "-- Source: Supabase public schema (PostgREST OpenAPI introspection, read-only)",
        "-- WARNING: Documentation/audit schema. Review before applying as migration.",
        "",
        "-- Dialect: PostgreSQL 15+ (Supabase)",
        "-- No INSERT/data.",
        "",
        "create extension if not exists pgcrypto;",
        "",
    ]

    for tname in BASE_TABLES:
        schema = defs.get(tname)
        if not schema:
            lines.append(f"-- NOTE: public.{tname} not in PostgREST cache")
            lines.append("")
            continue
        lines.extend(build_table_sql(tname, schema))
        lines.append("")

    lines.extend(
        [
            "-- -----------------------------------------------------------------------------",
            "-- Foreign keys",
            "-- -----------------------------------------------------------------------------",
            "alter table public.edital_anexo",
            "  add constraint edital_anexo_id_edital_fkey",
            "  foreign key (id_edital) references public.edital (id_edital) on delete cascade;",
            "",
            "alter table public.edital_extra_campo",
            "  add constraint edital_extra_campo_id_edital_fkey",
            "  foreign key (id_edital) references public.edital (id_edital) on delete cascade;",
            "",
            "alter table public.edital_historico",
            "  add constraint edital_historico_id_edital_fkey",
            "  foreign key (id_edital) references public.edital (id_edital) on delete cascade;",
            "",
            "alter table public.edital_historico",
            "  add constraint edital_historico_id_execucao_fkey",
            "  foreign key (id_execucao) references public.carga_execucao (id_execucao) on delete set null;",
            "",
            "-- -----------------------------------------------------------------------------",
            "-- Indexes (from migrations; safe IF NOT EXISTS)",
            "-- -----------------------------------------------------------------------------",
            "create unique index if not exists edital_link_key on public.edital (link);",
            "create index if not exists idx_edital_fonte_recurso on public.edital (fonte_recurso);",
            "create index if not exists idx_edital_data_publicacao on public.edital (data_publicacao desc);",
            "create index if not exists idx_edital_prazo_envio on public.edital (prazo_envio);",
            "create index if not exists idx_edital_validacao_status on public.edital (validacao_status);",
            "create index if not exists idx_edital_origem_portal on public.edital (origem_portal);",
            "create index if not exists idx_edital_extras_gin on public.edital using gin (extras);",
            "create index if not exists idx_edital_tags_gin on public.edital using gin (tags);",
            "create index if not exists idx_edital_perfil_ideal_gin on public.edital using gin (perfil_ideal);",
            "create index if not exists idx_noticia_link on public.noticia (link);",
            "create index if not exists idx_pesquisa_link on public.pesquisa (link);",
            "create index if not exists idx_edital_anexo_edital on public.edital_anexo (id_edital);",
            "create index if not exists idx_edital_extra_edital on public.edital_extra_campo (id_edital);",
            "create index if not exists idx_carga_execucao_data_inicio_desc on public.carga_execucao (data_inicio desc);",
            "create index if not exists idx_edital_historico_id_edital on public.edital_historico (id_edital);",
            "",
        ]
    )

    view_path = ROOT / "migrations" / "20260505_recreate_edital_views_credito_staging.sql"
    if view_path.is_file():
        raw = view_path.read_text(encoding="utf-8")
        lines.append("-- -----------------------------------------------------------------------------")
        lines.append("-- Views: editais (latest migration body)")
        lines.append("-- -----------------------------------------------------------------------------")
        for row in raw.splitlines():
            s = row.strip().lower()
            if s in ("begin;", "commit;"):
                continue
            lines.append(row)

    out = ROOT / "database" / "schema_current.sql"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
