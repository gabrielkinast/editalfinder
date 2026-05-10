#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "CORE"
DEFAULT_INPUT = ROOT / "audit_reports_main_pipeline" / "removed_items_candidates.json"
DEFAULT_REPORT_DIR = ROOT / "audit_reports_main_pipeline"
ENV_CANDIDATES = [ROOT / ".env.staging", ROOT / ".env.local", ROOT / ".env", CORE / ".env"]
CONF_ORDER = {"high": 0, "medium": 1, "low": 2}


def _load_env_files() -> List[str]:
    loaded = []
    for p in ENV_CANDIDATES:
        if p.is_file():
            load_dotenv(dotenv_path=p, override=False)
            loaded.append(str(p.resolve()))
    return loaded


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def _mask_host(url: str) -> str:
    try:
        host = urlparse(url).hostname or ""
        return host[:3] + "***" + host[-3:] if len(host) > 6 else "***"
    except Exception:
        return "***"


def _guard(has_staging_flag: bool, apply: bool) -> Tuple[bool, Dict[str, Any]]:
    env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    reason = ""
    if not apply:
        pass
    elif not has_staging_flag:
        reason = "missing_staging_flag"
    elif env in ("production", "prod"):
        reason = "environment_marked_production"
    elif env not in ("staging", "local"):
        reason = "invalid_editalfinder_env"
    elif not url:
        reason = "missing_supabase_url"
    elif not key:
        reason = "missing_service_key"
    elif not _truthy_env("EDITALFINDER_ALLOW_STAGING_APPLY"):
        reason = "missing_allow_staging_apply"
    elif not _truthy_env("ALLOW_DEACTIVATE_REMOVED_ITEMS"):
        reason = "missing_allow_deactivate_removed_items"
    return reason == "", {
        "editalfinder_env": env,
        "has_supabase_url": bool(url),
        "has_service_key": bool(key),
        "has_allow_staging_apply": _truthy_env("EDITALFINDER_ALLOW_STAGING_APPLY"),
        "allow_deactivate_removed_items": _truthy_env("ALLOW_DEACTIVATE_REMOVED_ITEMS"),
        "url_host_masked": _mask_host(url),
        "block_reason": reason,
    }


def _client() -> Any:
    from supabase import create_client

    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    return create_client(os.getenv("SUPABASE_URL", "").strip(), key)


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _columns_available(sbx: Any, table: str) -> Tuple[bool, Dict[str, bool], str]:
    try:
        r = sbx.table(table).select("*").limit(1).execute()
        rows = getattr(r, "data", None) or []
        cols = set(rows[0].keys()) if rows and isinstance(rows[0], dict) else set()
        if not cols:
            # Empty table: probe common columns one by one with zero-row-ish limit.
            cols = set()
            for c in ("ativo", "atualizado_em", "extras", "link", "fonte_recurso", "fonte"):
                try:
                    sbx.table(table).select(c).limit(1).execute()
                    cols.add(c)
                except Exception:
                    pass
        return True, {c: c in cols for c in ("ativo", "atualizado_em", "extras", "link", "fonte_recurso", "fonte")}, ""
    except Exception as exc:
        return False, {}, str(exc)


def _candidate_allowed(c: Dict[str, Any], table: str, sources: Optional[set[str]], max_conf: str) -> bool:
    if table != "all" and c.get("table") != table:
        return False
    if sources and str(c.get("source") or "").strip().lower() not in sources:
        return False
    conf = str(c.get("confidence") or "low").strip().lower()
    return CONF_ORDER.get(conf, 99) <= CONF_ORDER.get(max_conf, 0)


def _fetch_existing(sbx: Any, table: str, link: str, source: str) -> Optional[Dict[str, Any]]:
    try:
        q = sbx.table(table).select("*").eq("link", link).limit(1)
        if source:
            q = q.eq("fonte_recurso", source)
        r = q.execute()
        rows = getattr(r, "data", None) or []
        if rows:
            return rows[0]
    except Exception:
        if source:
            try:
                r = sbx.table(table).select("*").eq("link", link).eq("fonte", source).limit(1).execute()
                rows = getattr(r, "data", None) or []
                if rows:
                    return rows[0]
            except Exception:
                return None
    return None


def _deactivation_payload(existing: Dict[str, Any], has_updated: bool, has_extras: bool, reason: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    payload: Dict[str, Any] = {"ativo": False}
    if has_updated:
        payload["atualizado_em"] = now
    if has_extras:
        ex = existing.get("extras") if isinstance(existing.get("extras"), dict) else {}
        payload["extras"] = {
            **ex,
            "deactivation_reason": reason,
            "deactivated_by": "deactivate_removed_items.py",
            "deactivated_at": now,
            "deactivation_source": "removed_items_candidates",
        }
    return payload


def _write(report_dir: Path, report: Dict[str, Any]) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "deactivate_removed_items_summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Desativação segura de resíduos",
        "",
        f"- Gerado: `{report['timestamp']}`",
        f"- Modo: **{report['mode']}**",
        f"- Ambiente: `{report['environment']}`",
        f"- Candidatos lidos: **{report['candidates_read']}**",
        f"- Candidatos filtrados: **{report['candidates_filtered']}**",
        f"- Alterados: **{report['changed']}**",
        f"- Não encontrados: **{report['not_found']}**",
        f"- Erros: **{len(report['errors'])}**",
        "",
        "Nenhum DELETE/TRUNCATE/DROP é usado. O apply, quando permitido, marca `ativo=false`.",
    ]
    if report.get("dry_run_examples"):
        lines += ["", "## Exemplos dry-run", ""]
        for item in report["dry_run_examples"][:80]:
            lines.append(f"- `{item.get('table')}` `{item.get('source')}` `{item.get('confidence')}`: {item.get('link')}")
    (report_dir / "deactivate_removed_items_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Marca resíduos como ativo=false. Dry-run por padrão; nunca usa DELETE.")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--table", choices=("edital", "noticia", "pesquisa", "all"), default="all")
    ap.add_argument("--source", default="")
    ap.add_argument("--sources", default="")
    ap.add_argument("--confidence", choices=("high", "medium", "low"), default="high")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--reason", default="removed from current backend payload")
    ap.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args()

    env_files = _load_env_files()
    if args.staging:
        os.environ.setdefault("EDITALFINDER_ENV", "staging")
    apply_mode = bool(args.apply)
    if args.apply and args.dry_run:
        print("Use apenas --dry-run ou --apply.", flush=True)
        return 2
    ok_guard, guard = _guard(args.staging, apply_mode)
    report_dir = args.report_dir if args.report_dir.is_absolute() else ROOT / args.report_dir

    data = _load_json(args.input if args.input.is_absolute() else ROOT / args.input, {})
    raw_candidates = data.get("removed_candidates") if isinstance(data, dict) else []
    if not isinstance(raw_candidates, list):
        raw_candidates = []
    sources = {x.strip().lower() for x in (args.sources or args.source).split(",") if x.strip()} or None
    selected = [c for c in raw_candidates if isinstance(c, dict) and _candidate_allowed(c, args.table, sources, args.confidence)]

    report: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": "apply" if apply_mode else "dry_run",
        "environment": os.getenv("EDITALFINDER_ENV", ""),
        "env_files_loaded": env_files,
        "input": str((args.input if args.input.is_absolute() else ROOT / args.input).resolve()),
        "candidates_read": len(raw_candidates),
        "candidates_filtered": len(selected),
        "changed": 0,
        "not_found": 0,
        "errors": [],
        "guards": guard,
        "dry_run_examples": selected[:100],
        "warnings": [],
    }

    if apply_mode and not ok_guard:
        report["errors"].append({"reason": "apply_blocked", "detail": guard.get("block_reason")})
        _write(report_dir, report)
        print(json.dumps({"ok": False, "changed": 0, "errors": len(report["errors"]), "path": str((report_dir / "deactivate_removed_items_summary.json").resolve())}, ensure_ascii=False))
        return 1
    if not apply_mode:
        _write(report_dir, report)
        print(json.dumps({"ok": True, "mode": "dry_run", "candidates_filtered": len(selected), "path": str((report_dir / "deactivate_removed_items_summary.json").resolve())}, ensure_ascii=False))
        return 0

    sbx = _client()
    col_cache: Dict[str, Dict[str, bool]] = {}
    for c in selected:
        table = str(c.get("table") or "").strip()
        link = str(c.get("link") or "").strip()
        source = str(c.get("source") or "").strip()
        if table not in ("edital", "noticia", "pesquisa") or not link:
            report["errors"].append({"reason": "invalid_candidate", "candidate": c})
            continue
        if table not in col_cache:
            ok_cols, cols, err = _columns_available(sbx, table)
            if not ok_cols:
                report["errors"].append({"table": table, "reason": "table_inaccessible", "error": err})
                continue
            if not cols.get("ativo"):
                report["errors"].append({"table": table, "reason": "missing_ativo_column_abort"})
                continue
            if not cols.get("extras"):
                report["warnings"].append({"table": table, "reason": "missing_extras_column_update_only_ativo"})
            col_cache[table] = cols
        cols = col_cache[table]
        existing = _fetch_existing(sbx, table, link, source)
        if not existing:
            report["not_found"] += 1
            continue
        payload = _deactivation_payload(existing, bool(cols.get("atualizado_em")), bool(cols.get("extras")), args.reason)
        try:
            q = sbx.table(table).update(payload).eq("link", link)
            if source:
                q = q.eq("fonte_recurso", source) if cols.get("fonte_recurso") else q.eq("fonte", source)
            r = q.execute()
            changed = len(getattr(r, "data", None) or [])
            report["changed"] += changed
            if changed == 0:
                report["not_found"] += 1
        except Exception as exc:
            report["errors"].append({"table": table, "source": source, "link": link, "reason": "update_failed", "error": str(exc)})

    _write(report_dir, report)
    print(json.dumps({"ok": len(report["errors"]) == 0, "changed": report["changed"], "errors": len(report["errors"]), "path": str((report_dir / "deactivate_removed_items_summary.json").resolve())}, ensure_ascii=False))
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
