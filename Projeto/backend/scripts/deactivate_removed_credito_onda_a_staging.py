#!/usr/bin/env python3
"""
Desativa em staging registros em public.edital (ativo=false) cujo par (link, fonte)
consta na lista gerada por credito_brasil_onda_a_removed_links.json.

- Por defeito: apenas simula (dry-run). Carrega `.env.staging`, `.env.local`, `.env`, `CORE/.env` (dotenv, override=False) e imprime guards mascarados; não importa Supabase até `--apply`.
- Com --apply --staging: executa UPDATE; exige guards alinhados ao loader +
  ALLOW_CREDITO_ONDA_A_DEACTIVATE=1.
- Nunca apaga registros (sem DELETE).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "CORE"
DEFAULT_JSON = ROOT / "audit_reports_credito" / "credito_brasil_onda_a_removed_links.json"

_ENV_CANDIDATES = [
    ROOT / ".env.staging",
    ROOT / ".env.local",
    ROOT / ".env",
    CORE / ".env",
]


def _load_env_files() -> List[str]:
    loaded: List[str] = []
    for p in _ENV_CANDIDATES:
        if p.is_file():
            load_dotenv(dotenv_path=p, override=False)
            loaded.append(str(p.resolve()))
    return loaded


_ENV_FILES_LOADED: List[str] = _load_env_files()


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def _mask_host(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    try:
        host = (urlparse(u).hostname or "").strip()
    except Exception:
        host = ""
    if not host:
        return ""
    if len(host) <= 6:
        return host[0] + "***" + host[-1]
    return host[:3] + "***" + host[-3:]


def _confirm_staging_allowed(has_staging_flag: bool) -> Tuple[bool, Dict[str, Any]]:
    url = os.getenv("SUPABASE_URL", "").strip()
    env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
    has_service_key = bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    )
    has_allow_staging_apply = _truthy_env("EDITALFINDER_ALLOW_STAGING_APPLY")
    has_onda_a_flag = _truthy_env("ALLOW_CREDITO_ONDA_A_DEACTIVATE")
    env_ok = env in ("staging", "local")
    env_prod = env in ("production", "prod")

    block_reason = ""
    if not has_staging_flag:
        block_reason = "missing_staging_flag"
    elif env_prod:
        block_reason = "environment_marked_production"
    elif not env_ok:
        block_reason = "invalid_editalfinder_env"
    elif not url:
        block_reason = "missing_supabase_url"
    elif not has_service_key:
        block_reason = "missing_service_key"
    elif not has_allow_staging_apply:
        block_reason = "missing_allow_staging_apply"
    elif not has_onda_a_flag:
        block_reason = "missing_allow_credito_onda_a_deactivate"

    safe = block_reason == ""
    guard: Dict[str, Any] = {
        "env_files_loaded": list(_ENV_FILES_LOADED),
        "editalfinder_env": env,
        "has_supabase_url": bool(url),
        "has_service_key": has_service_key,
        "has_allow_staging_apply": has_allow_staging_apply,
        "allow_credito_onda_a_deactivate": has_onda_a_flag,
        "url_host_masked": _mask_host(url),
        "block_reason": block_reason,
    }
    return safe, guard


def _load_targets(
    path: Path,
    *,
    only_sources: Optional[Set[str]],
) -> List[Dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: List[Dict[str, str]] = []
    for src, block in (data.get("por_fonte") or {}).items():
        src_l = str(src).strip().lower()
        if only_sources is not None and src_l not in only_sources:
            continue
        for it in block.get("removidos") or []:
            link = str(it.get("link") or "").strip()
            if not link:
                continue
            out.append({"fonte": src_l, "link": link, "titulo": str(it.get("titulo") or "")})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Desativa links listados no JSON (staging, sem DELETE).")
    ap.add_argument("--input-json", type=Path, default=DEFAULT_JSON, help="JSON de links removidos")
    ap.add_argument(
        "--sources",
        default="",
        help="CSV de fontes a considerar (ex.: banco_da_amazonia,bdmg). Vazio = todas com removidos.",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Executa UPDATE ativo=false (obrigatório usar com --staging e guards de ambiente).",
    )
    ap.add_argument("--staging", action="store_true", help="Obrigatório junto com --apply")
    args = ap.parse_args()

    only: Optional[Set[str]] = None
    if args.sources.strip():
        only = {x.strip().lower() for x in args.sources.split(",") if x.strip()}

    path = args.input_json
    if not path.is_file():
        print(f"ERRO: ficheiro não encontrado: {path}", file=sys.stderr)
        return 2

    targets = _load_targets(path, only_sources=only)
    apply_mode = bool(args.apply)

    if not apply_mode:
        _, guard_preview = _confirm_staging_allowed(False)
        guard_preview["apply_mode"] = False
        guard_preview["nota"] = (
            "Pré-visualização de ambiente (apply ainda bloqueado sem --apply --staging). "
            "env_files_loaded reflete ficheiros .env carregados ao iniciar o script."
        )
        print(json.dumps({"guards": guard_preview}, ensure_ascii=False, indent=2))
        print(f"[dry-run] {len(targets)} pares (fonte, link) seriam candidatos a ativo=false:")
        for t in targets[:500]:
            print(f"  - fonte={t['fonte']} link={t['link']}")
        if len(targets) > 500:
            print(f"  ... e mais {len(targets) - 500} linhas.")
        print("[dry-run] Nenhuma escrita na base. Use --apply --staging com guards para executar.")
        return 0

    if not args.staging:
        print("ERRO: --apply exige --staging.", file=sys.stderr)
        return 2

    safe, guard = _confirm_staging_allowed(True)
    print(json.dumps({"guards": guard}, ensure_ascii=False, indent=2))
    if not safe:
        print(f"ERRO: apply bloqueado: {guard.get('block_reason')}", file=sys.stderr)
        return 3

    # Import pesado / exige env apenas no apply
    sys.path.insert(0, str(ROOT))
    from CORE.db import supabase  # noqa: WPS433

    updated_total = 0
    errors: List[Dict[str, Any]] = []
    for t in targets:
        try:
            r = (
                supabase.table("edital")
                .update({"ativo": False})
                .eq("link", t["link"])
                .eq("fonte", t["fonte"])
                .select("id,link,fonte,ativo")
                .execute()
            )
            n = len(r.data) if r.data is not None else 0
            updated_total += n
            if n == 0:
                errors.append({"reason": "no_matching_row", **t})
        except Exception as exc:  # noqa: BLE001
            errors.append({"reason": "exception", "error": str(exc), **t})

    summary = {
        "apply": True,
        "targets": len(targets),
        "rows_returned_after_update": updated_total,
        "no_match_or_errors": len(errors),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        print(json.dumps(errors[:100], ensure_ascii=False, indent=2))
    return 0 if len(errors) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
