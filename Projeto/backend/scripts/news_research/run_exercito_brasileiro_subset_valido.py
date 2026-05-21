#!/usr/bin/env python3
"""
Subset válido — Exército Brasileiro Notícias.

- Filtra validacao_status=valido do dry-run do crawler
- Dry-run do roteador (dry_run_news_research_loader.py)
- consolidado_subset.json / .md
Sem apply.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ORIGIN = (
    ROOT
    / "audit_reports_news_research"
    / "exercito_brasileiro_dryrun"
    / "standardized"
    / "exercito_brasileiro_standardized.json"
)
OUT_BASE = ROOT / "audit_reports_news_research" / "exercito_brasileiro_subset_valido"
STD_OUT = OUT_BASE / "standardized" / "exercito_brasileiro_standardized.json"
LOADER_DRYRUN = OUT_BASE / "loader_dryrun"
LOADER_APPLY_DRYRUN = OUT_BASE / "load_news_research_dryrun"
PAYLOAD_NOTICIA = OUT_BASE / "exercito_brasileiro_subset_valido_payload_noticia.json"
PAYLOAD_NOTICIA_REL = "audit_reports_news_research/exercito_brasileiro_subset_valido/exercito_brasileiro_subset_valido_payload_noticia.json"
INPUT_DIR_REL = "audit_reports_news_research/exercito_brasileiro_subset_valido"
SOURCE_ID = "exercito_brasileiro"


def _motivo_incompleto(item: Dict[str, Any]) -> str:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    parts: List[str] = []
    if ex.get("missing_summary"):
        resumo = str(item.get("resumo") or "").strip()
        parts.append(f"resumo_curto_ou_rotulo_editorial ({len(resumo)} chars)")
    if not item.get("data_publicacao"):
        parts.append("sem_data_publicacao")
    if str(item.get("validacao_status") or "") == "incompleto":
        if not parts:
            parts.append("validacao_status=incompleto (resumo < 40 chars no pipeline)")
    return "; ".join(parts) if parts else "validacao_status=incompleto"


def _row_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    return {
        "titulo": item.get("titulo"),
        "data_publicacao": item.get("data_publicacao"),
        "link": item.get("link"),
        "categoria": item.get("categoria") or ex.get("categoria"),
        "eixo_estrategico": item.get("eixo_estrategico") or ex.get("eixo_estrategico"),
        "imagem_url": item.get("imagem_url"),
        "qualidade_dado": item.get("qualidade_dado"),
        "validacao_status": item.get("validacao_status"),
    }


def _build_payload_noticia(validos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in validos:
        row = dict(item)
        if str(row.get("tipo_conteudo") or "").lower() == "noticia":
            row.pop("tipo_pesquisa", None)
        if not row.get("descricao") and row.get("resumo"):
            row["descricao"] = row["resumo"]
        out.append(row)
    return out


def main() -> int:
    if not ORIGIN.is_file():
        print(f"[ERRO] Origem não encontrada: {ORIGIN}", file=sys.stderr)
        return 1

    all_items: List[Dict[str, Any]] = json.loads(ORIGIN.read_text(encoding="utf-8"))
    if not isinstance(all_items, list):
        print("[ERRO] JSON de origem não é lista", file=sys.stderr)
        return 1

    validos = [it for it in all_items if str(it.get("validacao_status") or "") == "valido"]
    incompletos = [it for it in all_items if str(it.get("validacao_status") or "") != "valido"]

    STD_OUT.parent.mkdir(parents=True, exist_ok=True)
    STD_OUT.write_text(json.dumps(validos, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = _build_payload_noticia(validos)
    PAYLOAD_NOTICIA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_BASE / "exercito_brasileiro_subset_valido_payload_pesquisa.json").write_text("[]", encoding="utf-8")
    (OUT_BASE / "exercito_brasileiro_subset_valido_review_candidates.json").write_text("[]", encoding="utf-8")

    LOADER_DRYRUN.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "dry_run_news_research_loader.py"),
        "--input-dir",
        str(STD_OUT.parent),
        "--output-dir",
        str(LOADER_DRYRUN),
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stdout)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode

    loader_summary: Dict[str, Any] = {}
    loader_summary_path = LOADER_DRYRUN / "dry_run_summary.json"
    if loader_summary_path.is_file():
        loader_summary = json.loads(loader_summary_path.read_text(encoding="utf-8"))

    incluidos = [_row_summary(it) for it in validos]
    excluidos = [
        {
            **_row_summary(it),
            "motivo": _motivo_incompleto(it),
            "resumo_amostra": (str(it.get("resumo") or ""))[:120],
        }
        for it in incompletos
    ]

    apply_cmd_ps = (
        "# NÃO EXECUTADO — apply staging futuro (após validar .env.staging)\n"
        "$env:EDITALFINDER_ENV='staging'\n"
        "$env:EDITALFINDER_ALLOW_STAGING_APPLY='true'\n"
        "python scripts/load_news_research_sources.py `\n"
        "  --apply --staging --test-db-before-apply `\n"
        f"  --source {SOURCE_ID} `\n"
        f"  --noticia-payload {PAYLOAD_NOTICIA_REL} `\n"
        f"  --input-dir {INPUT_DIR_REL}"
    )
    apply_cmd_bash = (
        "# NÃO EXECUTADO\n"
        "export EDITALFINDER_ENV=staging\n"
        "export EDITALFINDER_ALLOW_STAGING_APPLY=true\n"
        "python scripts/load_news_research_sources.py \\\n"
        "  --apply --staging --test-db-before-apply \\\n"
        f"  --source {SOURCE_ID} \\\n"
        f"  --noticia-payload {PAYLOAD_NOTICIA_REL} \\\n"
        f"  --input-dir {INPUT_DIR_REL}"
    )
    load_dryrun_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "load_news_research_sources.py"),
        "--dry-run",
        "--source",
        SOURCE_ID,
        "--noticia-payload",
        PAYLOAD_NOTICIA_REL,
        "--input-dir",
        INPUT_DIR_REL,
    ]
    LOADER_APPLY_DRYRUN.mkdir(parents=True, exist_ok=True)
    proc_load = subprocess.run(load_dryrun_cmd, cwd=str(ROOT), capture_output=True, text=True)
    load_summary: Dict[str, Any] = {}
    load_summary_path = OUT_BASE / "load_news_research_summary.json"
    if load_summary_path.is_file():
        load_summary = json.loads(load_summary_path.read_text(encoding="utf-8"))
    if proc_load.returncode != 0:
        print(proc_load.stdout, file=sys.stdout)
        print(proc_load.stderr, file=sys.stderr)
        return proc_load.returncode

    consolidado: Dict[str, Any] = {
        "fonte": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "origem": str(ORIGIN.relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(STD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "totais": {
            "original": len(all_items),
            "valido": len(validos),
            "incompleto": len(incompletos),
        },
        "itens_incluidos": incluidos,
        "itens_excluidos_incompletos": excluidos,
        "loader_dryrun": {
            "comando": " ".join(cmd),
            "output_dir": str(LOADER_DRYRUN.relative_to(ROOT)).replace("\\", "/"),
            "resumo": loader_summary.get("por_destino_simulado") or loader_summary.get("por_destino"),
            "total_depois_dedupe": loader_summary.get("total_itens_depois_dedupe"),
            "missing_summary_total": loader_summary.get("missing_summary_total"),
        },
        "load_news_research_dryrun": {
            "comando": " ".join(load_dryrun_cmd),
            "source_id": SOURCE_ID,
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "errors_count": load_summary.get("errors_count"),
            "apply_status": load_summary.get("apply_status"),
            "summary_path": str(load_summary_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "payload_pronto_apply": {
            "noticia": str(PAYLOAD_NOTICIA.relative_to(ROOT)).replace("\\", "/"),
            "registos": len(payload),
        },
        "apply_staging": {
            "executado": False,
            "powershell": apply_cmd_ps,
            "bash": apply_cmd_bash,
        },
    }

    (OUT_BASE / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Exército Brasileiro — subset válido (consolidado)",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **Origem:** `{consolidado['origem']}`",
        f"- **Subset:** `{consolidado['subset_standardized']}`",
        "",
        "## Totais",
        "",
        f"- **Original:** {consolidado['totais']['original']}",
        f"- **Válido (incluído):** {consolidado['totais']['valido']}",
        f"- **Incompleto (excluído):** {consolidado['totais']['incompleto']}",
        "",
        "## Itens incluídos",
        "",
    ]
    for i, row in enumerate(incluidos, 1):
        md.append(f"### {i}. {row.get('titulo', '')[:100]}")
        md.append("")
        md.append(f"- **Data:** {row.get('data_publicacao')}")
        md.append(f"- **Categoria:** {row.get('categoria')}")
        md.append(f"- **Eixos:** {', '.join(row.get('eixo_estrategico') or [])}")
        if row.get("imagem_url"):
            md.append(f"- **Imagem:** `{row['imagem_url'][:90]}…`" if len(str(row["imagem_url"])) > 90 else f"- **Imagem:** `{row['imagem_url']}`")
        else:
            md.append("- **Imagem:** —")
        md.append(f"- **Link:** {row.get('link')}")
        md.append("")

    md.extend(["## Incompletos (excluídos do subset)", ""])
    for row in excluidos:
        md.append(f"- **{row.get('titulo', '')[:80]}**")
        md.append(f"  - Data: {row.get('data_publicacao')}")
        md.append(f"  - Motivo: {row.get('motivo')}")
        md.append(f"  - Resumo: {row.get('resumo_amostra', '')}")
        md.append("")

    ld = consolidado.get("loader_dryrun") or {}
    lnd = consolidado.get("load_news_research_dryrun") or {}
    md.extend(
        [
            "## Dry-run roteador (`dry_run_news_research_loader`)",
            "",
            f"- **Comando:** `{ld.get('comando', '')}`",
            f"- **Simulado public.noticia:** {(ld.get('resumo') or {}).get('public.noticia', '—')}",
            "",
            "## Dry-run carga (`load_news_research_sources`)",
            "",
            f"- **Comando:** `{lnd.get('comando', '')}`",
            f"- **would_upsert_noticia:** {lnd.get('would_upsert_noticia', '—')}",
            f"- **errors_count:** {lnd.get('errors_count', '—')}",
            f"- **Relatório:** `{lnd.get('summary_path', '')}`",
            "",
            "## Apply staging (não executado)",
            "",
            "```powershell",
            apply_cmd_ps,
            "```",
            "",
        ]
    )
    (OUT_BASE / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "totais": consolidado["totais"],
                "loader": ld.get("resumo"),
                "paths": {
                    "subset": str(STD_OUT),
                    "consolidado": str(OUT_BASE / "consolidado_subset.json"),
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
