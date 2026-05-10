#!/usr/bin/env python3
"""
Preparação dry-run controlada — Onda C (ukri_funding, eit, esa_osip).
Não apply; backup/restauro de audit_reports_loader_ready após captura do resumo.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CRED = ROOT / "audit_reports_credito"
MAIN = ROOT / "audit_reports_main_pipeline"
LOADER_READY = ROOT / "audit_reports_loader_ready"
LFIX = CRED / "lote_inovacao_internacional_onda_c_fix" / "standardized"
DRY_STD = CRED / "onda_c_dryrun_standardized"
READINESS_TMP = CRED / "onda_c_readiness_for_dryrun.json"
SEM_OUT = CRED / "onda_c_dryrun_semantic"

SOURCES = ["ukri_funding", "eit", "esa_osip"]
EXCLUDED = ["innovate_uk", "eurostars", "esa_star"]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _arr(v: Any) -> List[Any]:
    if isinstance(v, list):
        return v
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def _mtime(p: Path) -> str:
    if not p.is_file():
        return ""
    try:
        return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()
    except OSError:
        return ""


def _load_json(p: Path, default: Any) -> Any:
    if not p.is_file():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def _write_json(p: Path, data: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def scan_setor_estrategico_gt3(std_dir: Path) -> Dict[str, Any]:
    total = 0
    examples: List[Dict[str, Any]] = []
    for name in SOURCES:
        p = std_dir / f"{name}_standardized.json"
        if not p.is_file():
            continue
        data = _load_json(p, [])
        if isinstance(data, dict):
            data = [data]
        for it in data:
            if not isinstance(it, dict):
                continue
            ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
            se = _arr(ex.get("setor_estrategico"))
            if len(se) > 3:
                total += 1
                if len(examples) < 30:
                    examples.append(
                        {
                            "fonte": name,
                            "titulo": str(it.get("titulo") or "")[:200],
                            "link": str(it.get("link") or "")[:300],
                            "setor_estrategico_len": len(se),
                        }
                    )
    return {"count_gt3": total, "examples": examples}


def main() -> int:
    t0 = time.time()
    errors: List[str] = []
    warnings: List[str] = []

    # --- Part 0 snapshot ---
    key_paths = [
        ROOT / "main.py",
        ROOT / "international_onda_c_common.py",
        ROOT / "config" / "source_readiness.json",
        CRED / "lote_inovacao_internacional_onda_c_diagnostico.json",
        LFIX / "ukri_funding_standardized.json",
        LFIX / "eit_standardized.json",
        LFIX / "esa_osip_standardized.json",
    ]
    files_info = []
    for p in key_paths:
        files_info.append(
            {
                "path": str(p.relative_to(ROOT)).replace("\\", "/"),
                "exists": p.is_file(),
                "mtime_utc": _mtime(p) if p.is_file() else None,
            }
        )
    onda_reports = sorted(str(p.relative_to(ROOT)).replace("\\", "/") for p in CRED.glob("lote_inovacao_internacional_onda_c*") if p.is_file())
    onda_dirs = sorted(
        {str(p.relative_to(ROOT)).replace("\\", "/") for p in CRED.glob("lote_inovacao_internacional_onda_c*") if p.is_dir()}
    )
    readiness_curated = _load_json(ROOT / "config" / "source_readiness.json", {})
    snap = {
        "timestamp_utc": _now_iso(),
        "cwd": str(ROOT.resolve()),
        "git_present": (ROOT / ".git").is_dir(),
        "recomendacao_git": "Inicializar repositório Git na pasta do projeto, criar branch e commit antes de novas alterações (não executado automaticamente).",
        "ficheiros_chave": files_info,
        "relatorios_onda_c_glob": onda_reports[:80],
        "pastas_onda_c_glob": onda_dirs[:40],
        "fontes_onda_c": SOURCES + EXCLUDED,
        "readiness_curado_resumo": {
            "ready_n": len(readiness_curated.get("ready") or []),
            "ready_with_notes_n": len(readiness_curated.get("ready_with_notes") or []),
            "needs_manual_review_n": len(readiness_curated.get("needs_manual_review") or []),
            "blocked_n": len(readiness_curated.get("blocked") or []),
        },
    }
    _write_json(MAIN / "pre_dryrun_state_snapshot.json", snap)
    (MAIN / "pre_dryrun_state_snapshot.md").write_text(
        "\n".join(
            [
                "# Snapshot pré dry-run (sem Git)",
                "",
                f"- **Quando:** `{snap['timestamp_utc']}`",
                f"- **Pasta:** `{snap['cwd']}`",
                f"- **`.git` presente:** {snap['git_present']}",
                "",
                "## Ficheiros-chave (existência + mtime UTC)",
                "",
                "```json",
                json.dumps(snap["ficheiros_chave"], ensure_ascii=False, indent=2),
                "```",
                "",
                "## Relatórios Onda C (amostra)",
                "",
                *[f"- `{x}`" for x in snap["relatorios_onda_c_glob"][:25]],
                "",
                "## Readiness curado (`config/source_readiness.json`)",
                "",
                "```json",
                json.dumps(snap["readiness_curado_resumo"], ensure_ascii=False, indent=2),
                "```",
                "",
                "## Git",
                "",
                snap["recomendacao_git"],
            ]
        ),
        encoding="utf-8",
    )

    # --- Part 1 file check ---
    crawlers = {
        "international_onda_c_common.py": ROOT / "international_onda_c_common.py",
        "innovate_uk/main_innovate_uk.py": ROOT / "innovate_uk" / "main_innovate_uk.py",
        "ukri_funding/main_ukri_funding.py": ROOT / "ukri_funding" / "main_ukri_funding.py",
        "eurostars/main_eurostars.py": ROOT / "eurostars" / "main_eurostars.py",
        "eit/main_eit.py": ROOT / "eit" / "main_eit.py",
        "esa_star/main_esa_star.py": ROOT / "esa_star" / "main_esa_star.py",
        "esa_osip/main_esa_osip.py": ROOT / "esa_osip" / "main_esa_osip.py",
    }
    std_expected = [f"{s}_standardized.json" for s in SOURCES]
    extra_reports = [
        CRED / "lote_inovacao_internacional_onda_c_diagnostico.md",
        CRED / "lote_inovacao_internacional_onda_c_diagnostico.json",
        CRED / "lote_inovacao_internacional_onda_c_by_source.json",
        CRED / "lote_inovacao_internacional_onda_c_examples.json",
    ]
    fc = {
        "timestamp_utc": _now_iso(),
        "crawlers": {k: {"exists": v.is_file(), "path": str(v.relative_to(ROOT)).replace("\\", "/")} for k, v in crawlers.items()},
        "standardized_lote_fix": {
            f: {"exists": (LFIX / f).is_file(), "mtime_utc": _mtime(LFIX / f)} for f in std_expected
        },
        "relatorios": {str(p.relative_to(ROOT)).replace("\\", "/"): p.is_file() for p in extra_reports},
        "pasta_semantic": {
            "path": "audit_reports_credito/lote_inovacao_internacional_onda_c_semantic",
            "exists": (CRED / "lote_inovacao_internacional_onda_c_semantic").is_dir(),
        },
        "pasta_docs": {
            "path": "audit_reports_credito/lote_inovacao_internacional_onda_c_docs",
            "exists": (CRED / "lote_inovacao_internacional_onda_c_docs").is_dir(),
        },
    }
    _write_json(CRED / "onda_c_pre_dryrun_file_check.json", fc)
    (CRED / "onda_c_pre_dryrun_file_check.md").write_text(
        "\n".join(
            [
                "# Onda C — verificação de ficheiros (pré dry-run)",
                "",
                f"**{fc['timestamp_utc']}**",
                "",
                "## Crawlers",
                "",
                "```json",
                json.dumps(fc["crawlers"], ensure_ascii=False, indent=2),
                "```",
                "",
                "## Standardized esperados (lote fix)",
                "",
                "```json",
                json.dumps(fc["standardized_lote_fix"], ensure_ascii=False, indent=2),
                "```",
            ]
        ),
        encoding="utf-8",
    )

    # --- Part 2 py_compile ---
    py_targets = [
        "international_onda_c_common.py",
        "ukri_funding/main_ukri_funding.py",
        "eit/main_eit.py",
        "esa_osip/main_esa_osip.py",
        "CORE/taxonomy_filtros.py",
        "CORE/transformer.py",
        "scripts/load_ready_sources.py",
        "main.py",
    ]
    pc_results = []
    for rel in py_targets:
        p = ROOT / rel.replace("/", os.sep)
        rec: Dict[str, Any] = {"path": rel, "exists": p.is_file()}
        if not p.is_file():
            rec["status"] = "skipped_missing"
            warnings.append(f"py_compile skip (missing): {rel}")
        else:
            r = subprocess.run([sys.executable, "-m", "py_compile", str(p)], cwd=str(ROOT), capture_output=True, text=True)
            rec["exit_code"] = r.returncode
            rec["status"] = "ok" if r.returncode == 0 else "error"
            rec["stderr_tail"] = (r.stderr or "")[-800:]
            if r.returncode != 0:
                errors.append(f"py_compile failed: {rel}")
        pc_results.append(rec)
    pc = {"timestamp_utc": _now_iso(), "results": pc_results, "warnings": warnings, "errors": errors}
    _write_json(CRED / "onda_c_pre_dryrun_pycompile.json", pc)
    (CRED / "onda_c_pre_dryrun_pycompile.md").write_text(
        "\n".join(
            [
                "# Onda C — py_compile",
                "",
                f"**{pc['timestamp_utc']}**",
                "",
                "```json",
                json.dumps(pc_results, ensure_ascii=False, indent=2),
                "```",
            ]
        ),
        encoding="utf-8",
    )

    # --- Part 3 readiness temporário ---
    readiness_body = {
        "data_auditoria": _now_iso(),
        "fontes_total": 3,
        "status_distribution": {
            "pronto_para_loader": 0,
            "pronto_com_observacoes": 3,
            "bloquear_temporariamente": 0,
            "precisa_revisao_manual": 0,
            "reprocessar_depois_de_ajuste": 0,
        },
        "fontes_prontas_para_loader": list(SOURCES),
        "fontes_bloqueadas_temporariamente": [],
        "fontes_para_revisao": [],
        "nota": "Apenas ukri_funding, eit, esa_osip como pronto_com_observacoes (lista única). innovate_uk, eurostars, esa_star fora de propósito.",
        "top20_problemas_semanticos": [],
        "top20_ajustes_recomendados": [],
    }
    _write_json(READINESS_TMP, readiness_body)

    # --- Part 4 copy standardized ---
    DRY_STD.mkdir(parents=True, exist_ok=True)
    copy_log = []
    for s in SOURCES:
        src = LFIX / f"{s}_standardized.json"
        dst = DRY_STD / f"{s}_standardized.json"
        if not src.is_file():
            warnings.append(f"Standardized em falta: {src}")
            copy_log.append({"fonte": s, "ok": False, "reason": "missing_source"})
            continue
        shutil.copy2(src, dst)
        copy_log.append({"fonte": s, "ok": True, "from": str(src.relative_to(ROOT)).replace("\\", "/"), "to": str(dst.relative_to(ROOT)).replace("\\", "/")})
    cp = {"timestamp_utc": _now_iso(), "copies": copy_log}
    _write_json(CRED / "onda_c_dryrun_standardized_copy.json", cp)
    (CRED / "onda_c_dryrun_standardized_copy.md").write_text(
        "\n".join(
            [
                "# Cópia standardized — dry-run isolado",
                "",
                f"**{cp['timestamp_utc']}**",
                f"- Destino: `{DRY_STD.relative_to(ROOT).as_posix()}/`",
                "",
                "```json",
                json.dumps(copy_log, ensure_ascii=False, indent=2),
                "```",
            ]
        ),
        encoding="utf-8",
    )

    # --- Part 5 loader dry-run ---
    backup_sum = LOADER_READY / "load_ready_summary.json"
    backup_by = LOADER_READY / "load_ready_by_source.json"
    bak_sum = LOADER_READY / "load_ready_summary.backup_pre_onda_c_dryrun.json"
    bak_by = LOADER_READY / "load_ready_by_source.backup_pre_onda_c_dryrun.json"
    had_sum = backup_sum.is_file()
    had_by = backup_by.is_file()
    if had_sum:
        shutil.copy2(backup_sum, bak_sum)
    if had_by:
        shutil.copy2(backup_by, bak_by)

    cmd = [
        sys.executable,
        str(SCRIPTS / "load_ready_sources.py"),
        "--dry-run",
        "--sources",
        ",".join(SOURCES),
        "--exclude-blocked",
        "--input-dir",
        str(DRY_STD.relative_to(ROOT)).replace("\\", "/"),
        "--readiness",
        str(READINESS_TMP.relative_to(ROOT)).replace("\\", "/"),
    ]
    lr = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    loader_stdout_tail = (lr.stdout or "")[-4000:]
    loader_stderr_tail = (lr.stderr or "")[-4000:]
    supabase_hint = any(
        x in (loader_stdout_tail + loader_stderr_tail).lower()
        for x in ("supabase", "postgres", "connection", "401", "403")
    )
    if supabase_hint:
        warnings.append("Saída do loader menciona Supabase/conexão — dry-run ainda pode inicializar diagnósticos; nenhum apply foi pedido.")

    summary_src = _load_json(backup_sum, {})
    by_src = _load_json(backup_by, [])

    if backup_sum.is_file():
        shutil.copy2(backup_sum, CRED / "onda_c_loader_dryrun_summary_loader_ready.json")
    _write_json(
        CRED / "onda_c_loader_dryrun.json",
        {
            "timestamp_utc": _now_iso(),
            "comando": " ".join(cmd),
            "exit_code": lr.returncode,
            "loader_stdout_tail": loader_stdout_tail,
            "loader_stderr_tail": loader_stderr_tail,
            "summary": summary_src,
            "by_source": by_src,
        },
    )

    # Restore global loader reports
    if had_sum and bak_sum.is_file():
        shutil.copy2(bak_sum, backup_sum)
    if had_by and bak_by.is_file():
        shutil.copy2(bak_by, backup_by)

    if lr.returncode != 0:
        errors.append(f"load_ready_sources exit {lr.returncode}")

    md_loader = [
        "# Onda C — loader dry-run (isolado)",
        "",
        f"- **Exit:** {lr.returncode}",
        f"- **Comando:** `{' '.join(cmd)}`",
        "",
        "## Métricas (load_ready_summary embutido)",
        "",
    ]
    if isinstance(summary_src, dict):
        for k in (
            "sources_selected",
            "itens_standardized_total",
            "would_upsert_total",
            "would_ignore_total",
            "mapping_errors_total",
            "critical_empty_items_total",
            "documentos_perdidos_no_payload_total",
            "mode",
        ):
            if k in summary_src:
                md_loader.append(f"- **{k}:** {summary_src.get(k)}")
        md_loader.extend(["", "```json", json.dumps(summary_src, ensure_ascii=False, indent=2)[:15000], "```"])
    (CRED / "onda_c_loader_dryrun.md").write_text("\n".join(md_loader), encoding="utf-8")

    # --- Part 6 semantic audit ---
    SEM_OUT.mkdir(parents=True, exist_ok=True)
    sem_cmd = [
        sys.executable,
        str(SCRIPTS / "audit_semantic_classification.py"),
        "--input-dir",
        str(DRY_STD.relative_to(ROOT)).replace("\\", "/"),
        "--output-dir",
        str(SEM_OUT.relative_to(ROOT)).replace("\\", "/"),
    ]
    sr = subprocess.run(sem_cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if sr.returncode != 0:
        errors.append(f"audit_semantic_classification exit {sr.returncode}")

    sem_summary = _load_json(SEM_OUT / "audit_semantic_summary.json", {})
    setor_scan = scan_setor_estrategico_gt3(DRY_STD)
    sem_bundle = {
        "timestamp_utc": _now_iso(),
        "comando": " ".join(sem_cmd),
        "exit_code": sr.returncode,
        "audit_semantic_summary": sem_summary,
        "setor_estrategico_gt3_scan": setor_scan,
        "stderr_tail": (sr.stderr or "")[-2000:],
    }
    _write_json(CRED / "onda_c_dryrun_semantic_summary.json", sem_bundle)
    (CRED / "onda_c_dryrun_semantic_summary.md").write_text(
        "\n".join(
            [
                "# Onda C — auditoria semântica (dry-run dir)",
                "",
                f"- **Exit:** {sr.returncode}",
                "",
                "## setor_estrategico > 3 (varredura direta nos 3 JSON)",
                "",
                f"- **count:** {setor_scan['count_gt3']}",
                "",
                "## audit_semantic_summary (flags)",
                "",
                "```json",
                json.dumps(sem_summary, ensure_ascii=False, indent=2)[:12000],
                "```",
            ]
        ),
        encoding="utf-8",
    )

    # --- Part 7 recommendation ---
    gates = {}
    if isinstance(summary_src, dict):
        gates = {
            "sources_selected_eq_3": int(summary_src.get("sources_selected") or 0) == 3,
            "would_upsert_gt_0": int(summary_src.get("would_upsert_total") or 0) > 0,
            "mapping_errors_0": int(summary_src.get("mapping_errors_total") or 0) == 0,
            "critical_empty_0": int(summary_src.get("critical_empty_items_total") or 0) == 0,
            "docs_lost_0": int(summary_src.get("documentos_perdidos_no_payload_total") or 0) == 0,
        }
    gates["setor_estrategico_gt3_scan_0"] = setor_scan["count_gt3"] == 0
    flags_tot = (sem_summary.get("flags_totais") or {}) if isinstance(sem_summary, dict) else {}
    gates["flags_semanticos_resumo"] = {
        "publico_alvo_sem_evidencia": int(flags_tot.get("publico_alvo_sem_evidencia", 0) or 0),
        "classificacao_muito_ampla": int(flags_tot.get("classificacao_muito_ampla", 0) or 0),
        "area_cientifica_sem_evidencia": int(flags_tot.get("area_cientifica_sem_evidencia", 0) or 0),
    }

    core_gates_ok = all(
        [
            gates["sources_selected_eq_3"],
            gates["would_upsert_gt_0"],
            gates["mapping_errors_0"],
            gates["critical_empty_0"],
            gates["docs_lost_0"],
            gates["setor_estrategico_gt3_scan_0"],
        ]
    )
    all_ok = core_gates_ok and lr.returncode == 0 and sr.returncode == 0
    rec = {
        "timestamp_utc": _now_iso(),
        "gates": gates,
        "all_gates_pass": all_ok,
        "excluded_sources_reminder": EXCLUDED,
        "recommendation_pt": (
            "Pode preparar promoção para ready_with_notes e apply staging controlado em etapa separada."
            if all_ok
            else "Não promover nem apply até corrigir gates falhados ou revisar erros do loader/auditoria."
        ),
    }
    _write_json(CRED / "onda_c_apply_readiness_recommendation.json", rec)
    (CRED / "onda_c_apply_readiness_recommendation.md").write_text(
        "\n".join(
            [
                "# Recomendação — apply futuro (Onda C, 3 fontes)",
                "",
                "```json",
                json.dumps(rec, ensure_ascii=False, indent=2),
                "```",
            ]
        ),
        encoding="utf-8",
    )

    # --- Part 8 final summary ---
    final = {
        "timestamp_utc": _now_iso(),
        "duracao_segundos": round(time.time() - t0, 2),
        "apply_executado": False,
        "supabase_staging_tocado": False,
        "schema_alterado": False,
        "opportunity_gate_global_alterado": False,
        "errors": errors,
        "warnings": warnings,
        "artefatos": [
            "audit_reports_main_pipeline/pre_dryrun_state_snapshot.md",
            "audit_reports_main_pipeline/pre_dryrun_state_snapshot.json",
            "audit_reports_credito/onda_c_pre_dryrun_file_check.md",
            "audit_reports_credito/onda_c_pre_dryrun_file_check.json",
            "audit_reports_credito/onda_c_pre_dryrun_pycompile.md",
            "audit_reports_credito/onda_c_pre_dryrun_pycompile.json",
            "audit_reports_credito/onda_c_readiness_for_dryrun.json",
            "audit_reports_credito/onda_c_dryrun_standardized/",
            "audit_reports_credito/onda_c_dryrun_standardized_copy.md",
            "audit_reports_credito/onda_c_dryrun_standardized_copy.json",
            "audit_reports_credito/onda_c_loader_dryrun.md",
            "audit_reports_credito/onda_c_loader_dryrun.json",
            "audit_reports_credito/onda_c_dryrun_semantic/",
            "audit_reports_credito/onda_c_dryrun_semantic_summary.md",
            "audit_reports_credito/onda_c_dryrun_semantic_summary.json",
            "audit_reports_credito/onda_c_apply_readiness_recommendation.md",
            "audit_reports_credito/onda_c_apply_readiness_recommendation.json",
        ],
        "loader_backup_note": "Se existia load_ready_summary.json global, foi guardado em load_ready_summary.backup_pre_onda_c_dryrun.json durante a captura e restaurado após copiar para onda_c_loader_dryrun.json.",
        "proximos_comandos_seguros": [
            "Revisar audit_reports_credito/onda_c_apply_readiness_recommendation.md",
            "Promover manualmente fontes em config/source_readiness.json após aprovação humana",
            "Copiar standardized do lote fix para audit_reports_retransform/standardized e dry-run global com readiness oficial",
        ],
    }
    _write_json(CRED / "onda_c_dryrun_preparation_summary.json", final)
    (CRED / "onda_c_dryrun_preparation_summary.md").write_text(
        "\n".join(
            [
                "# Onda C — resumo final de preparo (dry-run controlado)",
                "",
                f"- **Quando:** `{final['timestamp_utc']}`",
                f"- **Duração (s):** {final['duracao_segundos']}",
                "",
                "## Confirmações",
                "",
                f"- apply_executado: **{final['apply_executado']}**",
                f"- supabase_staging_tocado: **{final['supabase_staging_tocado']}**",
                f"- schema_alterado: **{final['schema_alterado']}**",
                f"- opportunity_gate_global_alterado: **{final['opportunity_gate_global_alterado']}**",
                "",
                "## Erros / avisos do script",
                "",
                "```json",
                json.dumps({"errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2),
                "```",
                "",
                "## Artefatos",
                "",
                *[f"- `{a}`" for a in final["artefatos"]],
                "",
                "## Nota backup loader",
                "",
                final["loader_backup_note"],
            ]
        ),
        encoding="utf-8",
    )

    print(json.dumps({"ok": not errors, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
