#!/usr/bin/env python3
"""
Orquestrador principal EditalFinder: pipeline diário (editais + notícia/pesquisa), validações e limpezas seguras.

Segurança:
- `python main.py` (sem subcomando): apenas ajuda; nada executa.
- Apply em staging só com subcomando explícito e `--apply-staging` onde aplicável.
- Nunca DELETE/TRUNCATE/DROP (delegado a scripts que também evitam remoção).

Pipeline legado monolítico (crawler + transformer + loader CORE): ver `main_legacy_pipeline.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
CORE = ROOT / "CORE"
SCRIPTS = ROOT / "scripts"
DEFAULT_REPORT_DIR = ROOT / "audit_reports_main_pipeline"
READINESS_PATH = ROOT / "audit_reports_retransform" / "readiness_for_loader.json"
SOURCE_READINESS_PATH = ROOT / "config" / "source_readiness.json"
PIPELINE_SOURCES_PATH = ROOT / "config" / "pipeline_sources.json"
LOADER_SUMMARY_PATH = ROOT / "audit_reports_loader_ready" / "load_ready_summary.json"
NEWS_LOADER_DIR = ROOT / "audit_reports_news_research_loader"
NEWS_SUMMARY_PATH = NEWS_LOADER_DIR / "load_news_research_summary.json"

WAVE_BUILD_SCRIPT: Dict[str, str] = {
    "nasa_wave2": "build_nasa_wave2_payloads.py",
    "darpa_news_wave1": "build_darpa_news_wave_payloads.py",
    "iaea_wave1": "build_iaea_wave1_payloads.py",
    "eurekalert_wave1": "build_eurekalert_wave1_payloads.py",
}

DEFAULT_NEWS_WAVES: List[Dict[str, Any]] = [
    {"source": "nasa_news", "wave": "nasa_wave2", "experimental": False},
    {"source": "darpa_news", "wave": "darpa_news_wave1", "experimental": False},
    {"source": "iaea_news_publications", "wave": "iaea_wave1", "experimental": False},
    {"source": "eurekalert_science_filtered", "wave": "eurekalert_wave1", "experimental": True},
]


def load_env_files() -> List[str]:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return []
    loaded: List[str] = []
    for p in (ROOT / ".env.staging", ROOT / ".env.local", ROOT / ".env", CORE / ".env"):
        if p.is_file():
            load_dotenv(dotenv_path=p, override=False)
            loaded.append(str(p.resolve()))
    return loaded


_ENV_LOADED_AT_IMPORT = load_env_files()


def read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def tail_text(text: str, max_lines: int = 32, max_chars: int = 12000) -> str:
    if not text:
        return ""
    lines = text.splitlines()
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    out = "\n".join(lines)
    if len(out) > max_chars:
        out = out[-max_chars:]
    return out


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def abort_if_production() -> None:
    env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
    if env in ("production", "prod"):
        raise SystemExit("ABORTADO: EDITALFINDER_ENV indica produção. Este orquestrador só opera em staging/local.")


def check_staging_apply_environment() -> Tuple[bool, Dict[str, Any]]:
    """Guards mínimos antes de apply (alinhado aos loaders)."""
    abort_if_production()
    env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
    url = os.getenv("SUPABASE_URL", "").strip()
    has_key = bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    )
    allow = _truthy_env("EDITALFINDER_ALLOW_STAGING_APPLY")
    ok = env in ("staging", "local") and bool(url) and has_key and allow
    block = ""
    if env not in ("staging", "local"):
        block = "invalid_editalfinder_env"
    elif not url:
        block = "missing_supabase_url"
    elif not has_key:
        block = "missing_service_key"
    elif not allow:
        block = "missing_allow_staging_apply"
    diag = {
        "env_files_loaded_at_import": _ENV_LOADED_AT_IMPORT,
        "editalfinder_env": env,
        "has_supabase_url": bool(url),
        "has_service_key": has_key,
        "has_allow_staging_apply": allow,
        "environment_safe_for_apply": ok,
        "block_reason": block if not ok else "",
    }
    return ok, diag


def load_pipeline_sources_config() -> Dict[str, Any]:
    raw = read_json(PIPELINE_SOURCES_PATH, {})
    if not isinstance(raw, dict) or not raw:
        return {
            "_warning": "config/pipeline_sources.json ausente; usando defaults em código.",
            "edital": {
                "stable_apply_sources": [],
                "exclude_from_daily": [],
                "experimental_sources": [],
            },
            "news_research": {"active_waves": list(DEFAULT_NEWS_WAVES)},
        }
    return raw


def load_curated_readiness() -> Dict[str, List[str]]:
    data = read_json(SOURCE_READINESS_PATH, {})
    if not isinstance(data, dict):
        data = {}
    keys = ("ready", "ready_with_notes", "needs_manual_review", "blocked", "reprocess_after_fix")
    return {k: [str(x).strip().lower() for x in (data.get(k) or []) if str(x).strip()] for k in keys}


def get_edital_sources_allowed(
    *,
    cli_sources: Optional[Set[str]],
    pipeline_cfg: Dict[str, Any],
) -> Tuple[List[str], Dict[str, Any]]:
    """Fontes para pipeline de edital: ready ∪ ready_with_notes, excluindo blocked, review, reprocess."""
    r = load_curated_readiness()
    blocked = set(r["blocked"]) | set(r["needs_manual_review"]) | set(r["reprocess_after_fix"])
    allowed = (set(r["ready"]) | set(r["ready_with_notes"])) - blocked
    edital_cfg = (pipeline_cfg.get("edital") or {}) if isinstance(pipeline_cfg, dict) else {}
    stable = [str(x).strip().lower() for x in (edital_cfg.get("stable_apply_sources") or []) if str(x).strip()]
    exclude_daily = {str(x).strip().lower() for x in (edital_cfg.get("exclude_from_daily") or []) if str(x).strip()}
    if stable:
        allowed = allowed & set(stable)
    allowed -= exclude_daily
    if cli_sources:
        allowed = allowed & set(x.lower() for x in cli_sources)
    meta = {
        "ready_count": len(r["ready"]),
        "ready_with_notes_count": len(r["ready_with_notes"]),
        "needs_manual_review_count": len(r["needs_manual_review"]),
        "blocked_count": len(r["blocked"]),
        "reprocess_after_fix_count": len(r["reprocess_after_fix"]),
        "selected_after_policy": sorted(allowed),
        "skipped_by_cli": sorted(set(cli_sources or []) - allowed) if cli_sources else [],
    }
    return sorted(allowed), meta


def resolve_crawler_task(fonte: str) -> Optional[Tuple[Path, str]]:
    try:
        from main_legacy_pipeline import SCRAPERS as LEGACY_SCRAPERS
    except Exception:
        LEGACY_SCRAPERS = []
    for folder, script in LEGACY_SCRAPERS:
        if folder.lower() == fonte.lower():
            base = ROOT / folder
            if (base / script).is_file():
                return base, script
    alt = ROOT / fonte / f"main_{fonte}.py"
    if alt.is_file():
        return ROOT / fonte, f"main_{fonte}.py"
    return None


def run_command_step(
    name: str,
    cmd: List[str],
    *,
    cwd: Path,
    env: Optional[Dict[str, str]] = None,
    artifacts: Optional[List[str]] = None,
    skip: bool = False,
) -> Dict[str, Any]:
    rec: Dict[str, Any] = {
        "nome": name,
        "comando": " ".join(cmd),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": "",
        "duration_seconds": 0.0,
        "exit_code": -1,
        "stdout_tail": "",
        "stderr_tail": "",
        "status": "skipped",
        "artefatos_gerados": artifacts or [],
    }
    if skip:
        rec["finished_at"] = datetime.now(timezone.utc).isoformat()
        return rec
    t0 = time.time()
    try:
        r = subprocess.run(
            cmd,
            cwd=str(cwd),
            env={**os.environ, **(env or {})},
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        rec["exit_code"] = int(r.returncode)
        rec["stdout_tail"] = tail_text(r.stdout or "")
        rec["stderr_tail"] = tail_text(r.stderr or "")
        rec["status"] = "success" if r.returncode == 0 else "error"
    except Exception as exc:
        rec["exit_code"] = 1
        rec["stderr_tail"] = tail_text(str(exc))
        rec["status"] = "error"
    rec["duration_seconds"] = round(time.time() - t0, 3)
    rec["finished_at"] = datetime.now(timezone.utc).isoformat()
    return rec


def parse_edital_loader_gates(summary_path: Path) -> Tuple[bool, Dict[str, Any]]:
    s = read_json(summary_path, {})
    if not isinstance(s, dict) or not s:
        return False, {"reason": "missing_or_empty_summary", "path": str(summary_path)}
    gates = {
        "sources_selected": int(s.get("sources_selected") or 0),
        "would_upsert_total": int(s.get("would_upsert_total") or 0),
        "mapping_errors_total": int(s.get("mapping_errors_total") or 0),
        "critical_empty_items_total": int(s.get("critical_empty_items_total") or 0),
        "documentos_perdidos_no_payload_total": int(s.get("documentos_perdidos_no_payload_total") or 0),
    }
    ok = (
        gates["sources_selected"] > 0
        and gates["mapping_errors_total"] == 0
        and gates["critical_empty_items_total"] == 0
        and gates["documentos_perdidos_no_payload_total"] == 0
    )
    return ok, gates


def sync_retransform_to_canonical(
    retransform_std_dir: Path,
    sources: Sequence[str],
) -> List[str]:
    """Copia standardized do output do retransform para audit_reports_retransform/standardized."""
    dest_dir = ROOT / "audit_reports_retransform" / "standardized"
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied: List[str] = []
    for src in sources:
        src_f = retransform_std_dir / f"{src}_standardized.json"
        if src_f.is_file():
            shutil.copy2(src_f, dest_dir / src_f.name)
            copied.append(str((dest_dir / src_f.name).resolve()))
    return copied


def run_edital_pipeline(
    *,
    sources: List[str],
    report_dir: Path,
    skip_crawl: bool,
    skip_transform: bool,
    apply_staging: bool,
    update_canonical: bool,
    fail_fast: bool,
    continue_on_warning: bool,
    skip_edital_audits: bool = False,
) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = []
    retransform_dir = report_dir / "retransform_daily"
    retransform_std = retransform_dir / "standardized"
    critical_failed = False
    warnings: List[str] = []

    if not sources:
        steps.append(
            run_command_step(
                "edital:skip_no_sources",
                [sys.executable, "-c", "print('no sources')"],
                cwd=ROOT,
                skip=True,
            )
        )
        return {
            "steps": steps,
            "sources": [],
            "loader_gates_ok": False,
            "apply_executed": False,
            "critical_failed": True,
            "warnings": ["Nenhuma fonte edital elegível após readiness/filtros."],
        }

    if not skip_crawl:
        for src in sources:
            task = resolve_crawler_task(src)
            if not task:
                msg = f"Crawler não mapeado para fonte `{src}` (ver main_legacy_pipeline.SCRAPERS)."
                warnings.append(msg)
                steps.append(
                    run_command_step(f"crawl:{src}", [sys.executable, "-c", "pass"], cwd=ROOT, skip=True)
                )
                steps[-1]["status"] = "warning"
                steps[-1]["stderr_tail"] = msg
                if fail_fast:
                    critical_failed = True
                    break
                continue
            base, script = task
            st = run_command_step(
                f"crawl:{src}",
                [sys.executable, script],
                cwd=base,
            )
            steps.append(st)
            if st["status"] != "success" and fail_fast:
                critical_failed = True
                break
            if st["status"] != "success" and not continue_on_warning:
                warnings.append(f"Crawler falhou: {src}")

    if critical_failed:
        return {
            "steps": steps,
            "sources": sources,
            "loader_gates_ok": False,
            "apply_executed": False,
            "critical_failed": True,
            "warnings": warnings,
        }

    if not skip_transform:
        src_csv = ",".join(sources)
        steps.append(
            run_command_step(
                "retransform_all",
                [
                    sys.executable,
                    str(SCRIPTS / "retransform_all.py"),
                    "--sources",
                    src_csv,
                    "--dry-run",
                    "--output-dir",
                    str(retransform_dir),
                ],
                cwd=ROOT,
            )
        )
        if steps[-1]["status"] != "success":
            critical_failed = True

    if apply_staging or update_canonical:
        if retransform_std.is_dir():
            copied = sync_retransform_to_canonical(retransform_std, sources)
            steps.append(
                {
                    "nome": "sync_canonical_standardized",
                    "comando": f"copy {len(copied)} ficheiros",
                    "started_at": datetime.now(timezone.utc).isoformat(),
                    "finished_at": datetime.now(timezone.utc).isoformat(),
                    "duration_seconds": 0.0,
                    "exit_code": 0,
                    "stdout_tail": "\n".join(copied[:20]),
                    "stderr_tail": "",
                    "status": "success",
                    "artefatos_gerados": copied,
                }
            )
        elif apply_staging:
            warnings.append("retransform_daily/standardized ausente; apply usa canonical existente.")

    if not critical_failed and not skip_edital_audits:
        src_csv = ",".join(sources)
        steps.append(
            run_command_step(
                "audit_semantic_classification",
                [
                    sys.executable,
                    str(SCRIPTS / "audit_semantic_classification.py"),
                    "--input-dir",
                    str(retransform_std if retransform_std.is_dir() else ROOT / "audit_reports_retransform" / "standardized"),
                    "--output-dir",
                    str(report_dir / "semantic_daily"),
                ],
                cwd=ROOT,
            )
        )
        steps.append(
            run_command_step(
                "audit_docs_pipeline",
                [
                    sys.executable,
                    str(SCRIPTS / "audit_docs_pipeline.py"),
                    "--sources",
                    src_csv,
                    "--output-dir",
                    str(report_dir / "docs_daily"),
                ],
                cwd=ROOT,
            )
        )
        steps.append(
            run_command_step(
                "audit_source_access_methods",
                [
                    sys.executable,
                    str(SCRIPTS / "audit_source_access_methods.py"),
                    "--sources",
                    src_csv,
                ],
                cwd=ROOT,
            )
        )
    elif not critical_failed and skip_edital_audits:
        steps.append(
            run_command_step(
                "edital:skip_audits",
                [sys.executable, "-c", "print('skip_edital_audits=1')"],
                cwd=ROOT,
                skip=True,
            )
        )
        steps[-1]["status"] = "skipped"
        steps[-1]["stderr_tail"] = "Auditorias edital omitidas (--skip-edital-audits)."

    loader_gates_ok = False
    if not critical_failed:
        src_csv = ",".join(sources)
        steps.append(
            run_command_step(
                "load_ready_sources_dry_run",
                [
                    sys.executable,
                    str(SCRIPTS / "load_ready_sources.py"),
                    "--dry-run",
                    "--sources",
                    src_csv,
                    "--exclude-blocked",
                    "--input-dir",
                    "audit_reports_retransform/standardized",
                    "--readiness",
                    "audit_reports_retransform/readiness_for_loader.json",
                ],
                cwd=ROOT,
            )
        )
        loader_gates_ok, gate_report = parse_edital_loader_gates(LOADER_SUMMARY_PATH)
        steps[-1]["gate_report"] = gate_report
        if not loader_gates_ok:
            critical_failed = True
        if steps[-1]["status"] != "success":
            critical_failed = True

    apply_executed = False
    inserted = updated = 0
    if apply_staging and not critical_failed:
        ok, env_diag = check_staging_apply_environment()
        if not ok:
            critical_failed = True
            warnings.append(f"Ambiente inseguro para apply: {env_diag.get('block_reason')}")
        else:
            steps.append(
                run_command_step(
                    "load_ready_sources_apply",
                    [
                        sys.executable,
                        str(SCRIPTS / "load_ready_sources.py"),
                        "--apply",
                        "--staging",
                        "--test-db-before-apply",
                        "--sources",
                        ",".join(sources),
                        "--exclude-blocked",
                        "--input-dir",
                        "audit_reports_retransform/standardized",
                        "--readiness",
                        "audit_reports_retransform/readiness_for_loader.json",
                    ],
                    cwd=ROOT,
                )
            )
            apply_executed = steps[-1]["status"] == "success"
            s = read_json(LOADER_SUMMARY_PATH, {})
            inserted = int(s.get("apply_inserted_total") or 0)
            updated = int(s.get("apply_updated_total") or 0)

    return {
        "steps": steps,
        "sources": sources,
        "loader_gates_ok": loader_gates_ok,
        "apply_executed": apply_executed,
        "apply_inserted": inserted,
        "apply_updated": updated,
        "critical_failed": critical_failed,
        "warnings": warnings,
    }


def run_news_research_pipeline(
    *,
    report_dir: Path,
    skip_crawl: bool,
    waves: List[Dict[str, Any]],
    apply_staging: bool,
    fail_fast: bool,
    news_source_filter: str = "",
) -> Dict[str, Any]:
    steps: List[Dict[str, Any]] = []
    critical_failed = False
    news_summaries: List[Dict[str, Any]] = []

    if not skip_crawl:
        crawl_cmd = [sys.executable, str(SCRIPTS / "crawl_news_research_sources.py")]
        if news_source_filter.strip():
            crawl_cmd += ["--sources", news_source_filter.strip()]
        steps.append(
            run_command_step(
                "crawl_news_research_sources",
                crawl_cmd,
                cwd=ROOT,
            )
        )
        if steps[-1]["status"] != "success" and fail_fast:
            critical_failed = True

    if not critical_failed:
        steps.append(
            run_command_step(
                "audit_news_research_pipeline",
                [sys.executable, str(SCRIPTS / "audit_news_research_pipeline.py")],
                cwd=ROOT,
            )
        )
        if steps[-1]["status"] != "success" and fail_fast:
            critical_failed = True

    for w in waves:
        if critical_failed and fail_fast:
            break
        src = str(w.get("source") or "")
        wave = str(w.get("wave") or "")
        bscript = WAVE_BUILD_SCRIPT.get(wave)
        if bscript:
            steps.append(
                run_command_step(
                    f"build_payloads:{wave}",
                    [sys.executable, str(SCRIPTS / bscript)],
                    cwd=ROOT,
                )
            )
            if steps[-1]["status"] != "success":
                critical_failed = True
                continue
        ld = run_command_step(
            f"load_news_research_dry_run:{src}:{wave}",
            [
                sys.executable,
                str(SCRIPTS / "load_news_research_sources.py"),
                "--dry-run",
                "--source",
                src,
                "--wave",
                wave,
                "--input-dir",
                str(NEWS_LOADER_DIR),
            ],
            cwd=ROOT,
        )
        steps.append(ld)
        summ = read_json(NEWS_SUMMARY_PATH, {})
        news_summaries.append({"source": src, "wave": wave, "summary": summ})
        err_ct = int((summ or {}).get("errors_count") or 0) if isinstance(summ, dict) else 1
        if ld["status"] != "success" or err_ct > 0:
            critical_failed = True

        if apply_staging and not critical_failed:
            ok, _ = check_staging_apply_environment()
            if not ok:
                critical_failed = True
                break
            st_apply = run_command_step(
                f"load_news_research_apply:{src}:{wave}",
                [
                    sys.executable,
                    str(SCRIPTS / "load_news_research_sources.py"),
                    "--apply",
                    "--staging",
                    "--test-db-before-apply",
                    "--source",
                    src,
                    "--wave",
                    wave,
                    "--input-dir",
                    str(NEWS_LOADER_DIR),
                ],
                cwd=ROOT,
            )
            steps.append(st_apply)
            if st_apply["status"] != "success":
                critical_failed = True

    return {
        "steps": steps,
        "critical_failed": critical_failed,
        "summaries": news_summaries,
    }


def command_status(report_dir: Path) -> int:
    r = load_curated_readiness()
    print("=== EditalFinder status (readiness curado) ===")
    print(f"ready: {len(r['ready'])}")
    print(f"ready_with_notes: {len(r['ready_with_notes'])}")
    print(f"needs_manual_review: {len(r['needs_manual_review'])}")
    print(f"blocked: {len(r['blocked'])}")
    print(f"reprocess_after_fix: {len(r['reprocess_after_fix'])}")
    if LOADER_SUMMARY_PATH.is_file():
        s = read_json(LOADER_SUMMARY_PATH, {})
        print("\nÚltimo load_ready_summary (audit_reports_loader_ready):")
        print(f"  mode: {s.get('mode')}  sources_selected: {s.get('sources_selected')}")
        print(f"  would_upsert_total: {s.get('would_upsert_total')}")
    lr = report_dir / "last_run_summary.json"
    if lr.is_file():
        print(f"\nÚltimo main pipeline: {lr}")
        print(json.dumps(read_json(lr, {}), ensure_ascii=False, indent=2)[:2000])
    return 0


def command_list_readiness() -> int:
    r = load_curated_readiness()
    rf = read_json(READINESS_PATH, {})
    print("=== config/source_readiness.json ===")
    for k in ("ready", "ready_with_notes", "needs_manual_review", "blocked", "reprocess_after_fix"):
        print(f"\n{k.upper()} ({len(r[k])}):")
        for x in sorted(r[k])[:400]:
            print(f"  - {x}")
        if len(r[k]) > 400:
            print(f"  ... +{len(r[k]) - 400} mais")
    print("\n=== audit_reports_retransform/readiness_for_loader.json (fontes_prontas_para_loader) ===")
    fp = rf.get("fontes_prontas_para_loader") or []
    if isinstance(fp, list):
        print(f"total: {len(fp)}")
        for x in fp[:60]:
            print(f"  - {x}")
        if len(fp) > 60:
            print(f"  ... +{len(fp) - 60}")
    return 0


def write_last_run_artifacts(
    report_dir: Path,
    *,
    modo: str,
    steps: List[Dict[str, Any]],
    summary: Dict[str, Any],
    errors: List[Any],
) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    write_json(report_dir / "last_run_steps.json", steps)
    write_json(report_dir / "last_run_errors.json", errors)
    write_json(report_dir / "last_run_summary.json", summary)
    md = [
        f"# Última execução — {summary.get('data_execucao', '')}",
        "",
        f"- modo: **{modo}**",
        f"- ambiente: `{summary.get('ambiente', '')}`",
        f"- recomendação: {summary.get('recomendacao_final', '')}",
        "",
        "## Resumo",
        "",
        "```json",
        json.dumps(summary, ensure_ascii=False, indent=2)[:12000],
        "```",
        "",
        "## Passos",
        "",
    ]
    for st in steps:
        md.append(f"- **{st.get('nome')}**: {st.get('status')} (exit {st.get('exit_code')})")
    (report_dir / "last_run_summary.md").write_text("\n".join(md), encoding="utf-8")


def main() -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    common.add_argument("--fail-fast", action="store_true")
    common.add_argument("--continue-on-warning", action="store_true")
    common.add_argument("--skip-crawl", action="store_true")
    common.add_argument("--skip-transform", action="store_true")

    parser = argparse.ArgumentParser(
        description="Orquestrador EditalFinder (pipelines diários, validação, apply staging explícito)."
    )
    sub = parser.add_subparsers(dest="command", help="Subcomando")

    sub.add_parser("status", help="Resumo de readiness e últimos artefatos.", parents=[common])

    sub.add_parser("list-readiness", help="Lista categorias de readiness.")

    p_daily = sub.add_parser("daily", help="Pipeline completo diário.", parents=[common])
    p_daily.add_argument("--sources", default="", help="CSV de fontes edital (intersecta com readiness).")
    p_daily.add_argument("--skip-edital", action="store_true")
    p_daily.add_argument("--skip-news", action="store_true")
    p_daily.add_argument(
        "--news-source",
        default="",
        help="Restringe crawl_news_research_sources.py --sources a este id.",
    )
    p_daily.add_argument("--skip-experimental-news", action="store_true")
    p_daily.add_argument(
        "--update-canonical-standardized",
        action="store_true",
        help="Em dry-run também copia standardized do retransform para audit_reports_retransform/standardized.",
    )
    p_daily.add_argument(
        "--deactivate-removed",
        action="store_true",
        help="Detecta resíduos após apply. Sem --apply-deactivation, apenas gera relatório/dry-run.",
    )
    p_daily.add_argument(
        "--apply-deactivation",
        action="store_true",
        help="Com --deactivate-removed e --apply-staging, aplica ativo=false se guards permitirem.",
    )
    p_daily.add_argument(
        "--deactivation-confidence",
        choices=("high", "medium", "low"),
        default="high",
        help="Confiança mínima/abrangência para desativação: high, medium ou low.",
    )
    p_daily.add_argument(
        "--skip-edital-audits",
        action="store_true",
        help="Não executa audit_semantic / audit_docs / audit_source_access (dry-run mais rápido).",
    )
    g = p_daily.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply-staging", action="store_true")

    p_val = sub.add_parser("validate-staging", help="Validação global pós-carga (somente SELECT).", parents=[common])
    p_val.add_argument(
        "--filter-sources",
        default="",
        help="CSV opcional: restringe public.edital na validação global.",
    )
    p_val.add_argument("--include-news", action="store_true")
    p_val.add_argument("--include-edital", action="store_true")
    p_val.add_argument("--fail-on-critical", action="store_true")

    p_dr = sub.add_parser("detect-residues", help="Detecta resíduos ativos vs payload atual (somente SELECT).", parents=[common])
    p_dr.add_argument("--table", choices=("edital", "noticia", "pesquisa"), default="edital")
    p_dr.add_argument("--source", default="")
    p_dr.add_argument("--sources", default="")
    p_dr.add_argument("--wave", default="")

    p_ae = sub.add_parser("apply-edital", help="Apenas pipeline edital (dry-run ou apply).", parents=[common])
    p_ae.add_argument("--sources", required=True)
    p_ae.add_argument(
        "--update-canonical-standardized",
        action="store_true",
        help="Copia standardized do retransform para audit_reports_retransform/standardized antes do loader.",
    )
    p_ae.add_argument(
        "--skip-edital-audits",
        action="store_true",
        help="Omitir auditorias pesadas antes do loader dry-run/apply.",
    )
    ae_g = p_ae.add_mutually_exclusive_group(required=True)
    ae_g.add_argument("--dry-run", action="store_true")
    ae_g.add_argument("--apply-staging", action="store_true")

    p_an = sub.add_parser("apply-news", help="Uma fonte/onda news/research.", parents=[common])
    p_an.add_argument("--source", required=True)
    p_an.add_argument("--wave", required=True)
    an_g = p_an.add_mutually_exclusive_group(required=True)
    an_g.add_argument("--dry-run", action="store_true")
    an_g.add_argument("--apply-staging", action="store_true")

    p_pe = sub.add_parser(
        "apply-portais",
        help="Loader portal_estrategico (standardized Recovery D.1 fornecedores; não usa edital).",
        parents=[common],
    )
    p_pe.add_argument(
        "--sources",
        default="general_dynamics_suppliers,lockheed_martin_suppliers,bae_systems_suppliers",
        help="Lista separada por vírgulas (chaves *_standardized.json).",
    )
    p_pe.add_argument(
        "--input-dir",
        default=str(DEFAULT_REPORT_DIR / "recovery_d1_fornecedores_final" / "standardized"),
        help="Pasta com JSON standardized.",
    )
    p_pe.add_argument(
        "--output-dir",
        default=str(DEFAULT_REPORT_DIR / "portais_estrategicos_apply"),
        help="Pasta de relatórios do loader.",
    )
    p_pe.add_argument("--staging", action="store_true", help="Obrigatório com --apply-staging.")
    pe_g = p_pe.add_mutually_exclusive_group(required=True)
    pe_g.add_argument("--dry-run", action="store_true")
    pe_g.add_argument("--apply-staging", action="store_true")

    p_cl = sub.add_parser("clean-staging", help="Limpeza segura (ativo=false; sem DELETE).", parents=[common])
    p_cl.add_argument("--group", required=True, choices=("credito_onda_a", "removed_items"))
    p_cl.add_argument("--source", default="")
    p_cl.add_argument("--sources", default="")
    p_cl.add_argument("--apply-deactivation", action="store_true")
    p_cl.add_argument("--deactivation-confidence", choices=("high", "medium", "low"), default="high")
    cl_g = p_cl.add_mutually_exclusive_group(required=False)
    cl_g.add_argument("--dry-run", action="store_true")
    cl_g.add_argument("--apply-staging", action="store_true")

    if len(sys.argv) <= 1:
        parser.print_help()
        print(
            "\nNota: pipeline monolítico legado em `main_legacy_pipeline.py` "
            "(crawlers + CORE/transformer + CORE/loader).\n"
            "Sem subcomando, este ficheiro não executa nada destrutivo."
        )
        return 0

    args = parser.parse_args()

    report_dir = Path(getattr(args, "report_dir", DEFAULT_REPORT_DIR))
    report_dir.mkdir(parents=True, exist_ok=True)

    cli_sources: Set[str] = set()
    if getattr(args, "sources", None) and str(args.sources).strip():
        cli_sources = {x.strip().lower() for x in str(args.sources).split(",") if x.strip()}

    if args.command == "status":
        return command_status(report_dir)
    if args.command == "list-readiness":
        return command_list_readiness()

    pipeline_cfg = load_pipeline_sources_config()
    all_steps: List[Dict[str, Any]] = []
    errors: List[Any] = []
    summary: Dict[str, Any] = {
        "data_execucao": datetime.now(timezone.utc).isoformat(),
        "ambiente": os.getenv("EDITALFINDER_ENV", ""),
        "modo": "",
        "env_files_loaded": _ENV_LOADED_AT_IMPORT,
        "edital": {},
        "news_research": {},
        "validacoes": [],
        "recomendacao_final": "",
    }

    if args.command == "daily":
        plan_apply = bool(args.apply_staging)
        summary["modo"] = "dry-run" if args.dry_run else "apply-staging"
        allowed, meta = get_edital_sources_allowed(
            cli_sources=cli_sources if cli_sources else None, pipeline_cfg=pipeline_cfg
        )
        summary["readiness_meta"] = meta
        waves_cfg = (pipeline_cfg.get("news_research") or {}).get("active_waves") or DEFAULT_NEWS_WAVES
        waves: List[Dict[str, Any]] = [dict(w) for w in waves_cfg if isinstance(w, dict)]
        if args.skip_experimental_news:
            waves = [w for w in waves if not w.get("experimental")]

        # Fase 1: sempre dry-run completo (loaders sem --apply), mesmo quando plan_apply.
        edital_result: Optional[Dict[str, Any]] = None
        if not args.skip_edital:
            edital_result = run_edital_pipeline(
                sources=allowed,
                report_dir=report_dir,
                skip_crawl=args.skip_crawl,
                skip_transform=args.skip_transform,
                apply_staging=False,
                update_canonical=bool(args.update_canonical_standardized or plan_apply),
                fail_fast=args.fail_fast,
                continue_on_warning=args.continue_on_warning,
                skip_edital_audits=bool(getattr(args, "skip_edital_audits", False)),
            )
            all_steps.extend(edital_result["steps"])
            summary["edital"] = {
                "fontes": edital_result["sources"],
                "loader_gates_ok": edital_result["loader_gates_ok"],
                "apply_executed": False,
                "apply_inserted": 0,
                "apply_updated": 0,
                "critical_failed": edital_result["critical_failed"],
                "warnings": edital_result["warnings"],
            }
            s = read_json(LOADER_SUMMARY_PATH, {})
            summary["edital"]["would_upsert_total"] = s.get("would_upsert_total")
            if edital_result["critical_failed"]:
                errors.append({"fase": "edital", "detalhe": edital_result})

        news_failed = False
        news_result: Optional[Dict[str, Any]] = None
        if not args.skip_news:
            news_result = run_news_research_pipeline(
                report_dir=report_dir,
                skip_crawl=args.skip_crawl,
                waves=waves,
                apply_staging=False,
                fail_fast=args.fail_fast,
                news_source_filter=args.news_source or "",
            )
            all_steps.extend(news_result["steps"])
            summary["news_research"] = {
                "waves": waves,
                "critical_failed": news_result["critical_failed"],
                "summaries": news_result["summaries"],
            }
            news_failed = news_result["critical_failed"]

        block_dry = (edital_result and edital_result["critical_failed"]) or news_failed
        if block_dry:
            summary["recomendacao_final"] = "Dry-run com falhas; apply não será tentado."
            write_last_run_artifacts(report_dir, modo=summary["modo"], steps=all_steps, summary=summary, errors=errors)
            return 1

        # Fase 2: apply apenas se plan_apply e ambiente seguro.
        if plan_apply:
            ok, diag = check_staging_apply_environment()
            summary["environment_guard"] = diag
            if not ok:
                errors.append({"fase": "pre_apply", "erro": diag.get("block_reason")})
                summary["recomendacao_final"] = "Abortar: ambiente não seguro para apply."
                write_last_run_artifacts(report_dir, modo=summary["modo"], steps=all_steps, summary=summary, errors=errors)
                return 1

            if not args.skip_edital and edital_result:
                st_apply_edital = run_command_step(
                    "load_ready_sources_apply",
                    [
                        sys.executable,
                        str(SCRIPTS / "load_ready_sources.py"),
                        "--apply",
                        "--staging",
                        "--test-db-before-apply",
                        "--sources",
                        ",".join(edital_result["sources"]),
                        "--exclude-blocked",
                        "--input-dir",
                        "audit_reports_retransform/standardized",
                        "--readiness",
                        "audit_reports_retransform/readiness_for_loader.json",
                    ],
                    cwd=ROOT,
                )
                all_steps.append(st_apply_edital)
                s2 = read_json(LOADER_SUMMARY_PATH, {})
                summary["edital"]["apply_executed"] = st_apply_edital["status"] == "success"
                summary["edital"]["apply_inserted"] = int(s2.get("apply_inserted_total") or 0)
                summary["edital"]["apply_updated"] = int(s2.get("apply_updated_total") or 0)
                if st_apply_edital["status"] != "success":
                    errors.append({"fase": "apply_edital", "step": st_apply_edital})

            if not args.skip_news and news_result:
                for w in waves:
                    src = str(w.get("source") or "")
                    wave = str(w.get("wave") or "")
                    st_na = run_command_step(
                        f"load_news_research_apply:{src}:{wave}",
                        [
                            sys.executable,
                            str(SCRIPTS / "load_news_research_sources.py"),
                            "--apply",
                            "--staging",
                            "--test-db-before-apply",
                            "--source",
                            src,
                            "--wave",
                            wave,
                            "--input-dir",
                            str(NEWS_LOADER_DIR),
                        ],
                        cwd=ROOT,
                    )
                    all_steps.append(st_na)
                    if st_na["status"] != "success":
                        errors.append({"fase": "apply_news", "step": st_na})

            if not args.skip_edital and edital_result and summary["edital"].get("apply_executed"):
                for src in edital_result["sources"]:
                    st = run_command_step(
                        f"validate_database_after_load:{src}",
                        [
                            sys.executable,
                            str(SCRIPTS / "validate_database_after_load.py"),
                            "--staging",
                            "--source",
                            src,
                            "--output-dir",
                            str(report_dir / "validate_edital" / src),
                        ],
                        cwd=ROOT,
                    )
                    all_steps.append(st)
                    summary["validacoes"].append({"script": "validate_database_after_load", "fonte": src, "step": st})

            if not args.skip_news and news_result:
                for w in waves:
                    src = str(w.get("source") or "")
                    wave = str(w.get("wave") or "")
                    st = run_command_step(
                        f"validate_news_research_after_load:{src}:{wave}",
                        [
                            sys.executable,
                            str(SCRIPTS / "validate_news_research_after_load.py"),
                            "--staging",
                            "--source",
                            src,
                            "--wave",
                            wave,
                            "--input-dir",
                            str(NEWS_LOADER_DIR),
                        ],
                        cwd=ROOT,
                    )
                    all_steps.append(st)
                    summary["validacoes"].append(
                        {"script": "validate_news_research_after_load", "source": src, "wave": wave, "step": st}
                    )

            st_full = run_command_step(
                "validate_full_staging_after_daily",
                [
                    sys.executable,
                    str(SCRIPTS / "validate_full_staging_after_daily.py"),
                    "--staging",
                    "--report-dir",
                    str(report_dir),
                ],
                cwd=ROOT,
            )
            all_steps.append(st_full)
            summary["validacoes"].append({"script": "validate_full_staging_after_daily", "step": st_full})
            if st_full["status"] != "success":
                errors.append({"fase": "validate_full_staging_after_daily", "step": st_full})

            if args.deactivate_removed:
                detect_cmd = [
                    sys.executable,
                    str(SCRIPTS / "detect_removed_items.py"),
                    "--staging",
                    "--table",
                    "edital",
                    "--sources",
                    ",".join(edital_result["sources"] if edital_result else allowed),
                    "--report-dir",
                    str(report_dir),
                ]
                st_detect = run_command_step("detect_removed_items:edital", detect_cmd, cwd=ROOT)
                all_steps.append(st_detect)
                summary["residues_detected"] = st_detect["status"] == "success"

                dry_cmd = [
                    sys.executable,
                    str(SCRIPTS / "deactivate_removed_items.py"),
                    "--input",
                    str(report_dir / "removed_items_candidates.json"),
                    "--table",
                    "edital",
                    "--confidence",
                    str(args.deactivation_confidence),
                    "--dry-run",
                    "--report-dir",
                    str(report_dir),
                ]
                st_dry = run_command_step("deactivate_removed_items_dry_run", dry_cmd, cwd=ROOT)
                all_steps.append(st_dry)
                summary["residues_deactivation_dry_run"] = st_dry["status"] == "success"

                if args.apply_deactivation:
                    apply_cmd = [
                        sys.executable,
                        str(SCRIPTS / "deactivate_removed_items.py"),
                        "--input",
                        str(report_dir / "removed_items_candidates.json"),
                        "--table",
                        "edital",
                        "--confidence",
                        str(args.deactivation_confidence),
                        "--apply",
                        "--staging",
                        "--report-dir",
                        str(report_dir),
                    ]
                    st_apply_deact = run_command_step("deactivate_removed_items_apply", apply_cmd, cwd=ROOT)
                    all_steps.append(st_apply_deact)
                    summary["residues_deactivated"] = st_apply_deact["status"] == "success"
                    if st_apply_deact["status"] != "success":
                        errors.append({"fase": "deactivate_removed_items", "step": st_apply_deact})
                else:
                    summary["residues_deactivated"] = False
                    summary["residues_deactivation_note"] = "Use --apply-deactivation com guards para aplicar ativo=false."

        summary["recomendacao_final"] = "OK" if not errors else "Rever erros e relatórios."
        write_last_run_artifacts(report_dir, modo=summary["modo"], steps=all_steps, summary=summary, errors=errors)
        return 0 if not errors else 1

    if args.command == "validate-staging":
        abort_if_production()
        cmd = [
            sys.executable,
            str(SCRIPTS / "validate_full_staging_after_daily.py"),
            "--staging",
            "--report-dir",
            str(report_dir),
        ]
        if getattr(args, "filter_sources", ""):
            cmd += ["--sources", str(args.filter_sources)]
        if getattr(args, "include_news", False):
            cmd.append("--include-news")
        if getattr(args, "include_edital", False):
            cmd.append("--include-edital")
        if getattr(args, "fail_on_critical", False):
            cmd.append("--fail-on-critical")
        steps = [run_command_step("validate_full_staging_after_daily", cmd, cwd=ROOT)]
        write_last_run_artifacts(
            report_dir,
            modo="validate-staging",
            steps=steps,
            summary={
                "data_execucao": datetime.now(timezone.utc).isoformat(),
                "modo": "validate-staging",
                "post_daily_validation": read_json(report_dir / "post_daily_validation.json", {}),
            },
            errors=[] if steps[0]["status"] == "success" else [{"fase": "validate-staging", "step": steps[0]}],
        )
        return 0 if all(x["status"] == "success" for x in steps) else 1

    if args.command == "detect-residues":
        abort_if_production()
        cmd = [
            sys.executable,
            str(SCRIPTS / "detect_removed_items.py"),
            "--staging",
            "--table",
            str(args.table),
            "--report-dir",
            str(report_dir),
        ]
        if args.sources:
            cmd += ["--sources", str(args.sources)]
        if args.source:
            cmd += ["--source", str(args.source)]
        if args.wave:
            cmd += ["--wave", str(args.wave)]
        st = run_command_step("detect_removed_items", cmd, cwd=ROOT)
        write_last_run_artifacts(
            report_dir,
            modo="detect-residues",
            steps=[st],
            summary={
                "data_execucao": datetime.now(timezone.utc).isoformat(),
                "modo": "detect-residues",
                "removed_items_candidates": read_json(report_dir / "removed_items_candidates.json", {}),
            },
            errors=[] if st["status"] == "success" else [{"fase": "detect-residues", "step": st}],
        )
        return 0 if st["status"] == "success" else 1

    if args.command == "apply-edital":
        summary["modo"] = "apply-edital-dry-run" if args.dry_run else "apply-edital-apply"
        allowed, meta = get_edital_sources_allowed(
            cli_sources={x.strip().lower() for x in args.sources.split(",") if x.strip()},
            pipeline_cfg=pipeline_cfg,
        )
        summary["readiness_meta"] = meta
        res = run_edital_pipeline(
            sources=allowed,
            report_dir=report_dir,
            skip_crawl=args.skip_crawl,
            skip_transform=args.skip_transform,
            apply_staging=bool(args.apply_staging),
            update_canonical=bool(args.update_canonical_standardized or args.apply_staging),
            fail_fast=args.fail_fast,
            continue_on_warning=args.continue_on_warning,
            skip_edital_audits=bool(getattr(args, "skip_edital_audits", False)),
        )
        all_steps.extend(res["steps"])
        summary["edital"] = res
        write_last_run_artifacts(report_dir, modo=summary["modo"], steps=all_steps, summary=summary, errors=errors)
        return 0 if not res["critical_failed"] else 1

    if args.command == "apply-portais":
        if args.apply_staging and not args.staging:
            print("[ERRO] apply-portais: --apply-staging exige também --staging", file=sys.stderr)
            return 2
        in_dir = Path(args.input_dir)
        if not in_dir.is_absolute():
            in_dir = ROOT / in_dir
        out_dir = Path(args.output_dir)
        if not out_dir.is_absolute():
            out_dir = ROOT / out_dir
        cmd = [
            sys.executable,
            str(SCRIPTS / "load_portais_estrategicos.py"),
            "--sources",
            str(args.sources),
            "--input-dir",
            str(in_dir),
            "--output-dir",
            str(out_dir),
        ]
        if args.dry_run:
            cmd.append("--dry-run")
        else:
            cmd += ["--apply", "--staging"]
        st = run_command_step("apply_portais_estrategicos", cmd, cwd=ROOT)
        write_last_run_artifacts(
            report_dir,
            modo="apply-portais-dry-run" if args.dry_run else "apply-portais-apply",
            steps=[st],
            summary={
                "data_execucao": datetime.now(timezone.utc).isoformat(),
                "command": "apply-portais",
                "output_dir": str(out_dir),
            },
            errors=[] if st["status"] == "success" else [{"fase": "apply-portais", "step": st}],
        )
        return 0 if st["status"] == "success" else 1

    if args.command == "apply-news":
        waves = [{"source": args.source, "wave": args.wave, "experimental": False}]
        res = run_news_research_pipeline(
            report_dir=report_dir,
            skip_crawl=args.skip_crawl,
            waves=waves,
            apply_staging=bool(args.apply_staging),
            fail_fast=args.fail_fast,
        )
        all_steps.extend(res["steps"])
        summary["modo"] = "apply-news-dry-run" if args.dry_run else "apply-news-apply"
        summary["news_research"] = res
        write_last_run_artifacts(report_dir, modo=summary["modo"], steps=all_steps, summary=summary, errors=errors)
        return 0 if not res["critical_failed"] else 1

    if args.command == "clean-staging":
        if args.group == "credito_onda_a":
            cmd = [
                sys.executable,
                str(SCRIPTS / "deactivate_removed_credito_onda_a_staging.py"),
                "--sources",
                "banco_da_amazonia,bdmg",
            ]
            if args.apply_staging:
                cmd += ["--apply", "--staging"]
            st = run_command_step("clean_credito_onda_a", cmd, cwd=ROOT)
            write_last_run_artifacts(
                report_dir,
                modo="clean-staging-apply" if args.apply_staging else "clean-staging-dry-run",
                steps=[st],
                summary={"data_execucao": datetime.now(timezone.utc).isoformat(), "group": args.group},
                errors=[],
            )
            return 0 if st["status"] == "success" else 1
        if args.group == "removed_items":
            cmd = [
                sys.executable,
                str(SCRIPTS / "deactivate_removed_items.py"),
                "--input",
                str(report_dir / "removed_items_candidates.json"),
                "--table",
                "all",
                "--confidence",
                str(args.deactivation_confidence),
                "--report-dir",
                str(report_dir),
            ]
            if args.sources:
                cmd += ["--sources", str(args.sources)]
            if args.source:
                cmd += ["--source", str(args.source)]
            if args.apply_staging:
                if not args.apply_deactivation:
                    cmd.append("--dry-run")
                else:
                    cmd += ["--apply", "--staging"]
            else:
                cmd.append("--dry-run")
            st = run_command_step("clean_removed_items", cmd, cwd=ROOT)
            write_last_run_artifacts(
                report_dir,
                modo="clean-staging-removed-items-apply" if args.apply_staging and args.apply_deactivation else "clean-staging-removed-items-dry-run",
                steps=[st],
                summary={
                    "data_execucao": datetime.now(timezone.utc).isoformat(),
                    "group": args.group,
                    "deactivate_removed_items": read_json(report_dir / "deactivate_removed_items_summary.json", {}),
                },
                errors=[] if st["status"] == "success" else [{"fase": "clean-staging", "step": st}],
            )
            return 0 if st["status"] == "success" else 1

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
