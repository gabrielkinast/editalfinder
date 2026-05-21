#!/usr/bin/env python3
"""
Preparar apply staging — SOFTEX Notícias (sem executar apply).

- Gera payload a partir do standardized (validacao_status=valido)
- Dry-run load_news_research_sources.py
- consolidado_apply.json / .md
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

OUT_BASE = ROOT / "audit_reports_news_research" / "softex_noticias_dryrun"
STD_PATH = OUT_BASE / "standardized" / "softex_noticias_standardized.json"
PAYLOAD_NOTICIA = OUT_BASE / "softex_noticias_payload_noticia.json"
INPUT_DIR_REL = "audit_reports_news_research/softex_noticias_dryrun"
SOURCE_ID = "softex_noticias"


def _build_payload_noticia(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        row = dict(item)
        if str(row.get("tipo_conteudo") or "").lower() == "noticia":
            row.pop("tipo_pesquisa", None)
        if not row.get("descricao") and row.get("resumo"):
            row["descricao"] = row["resumo"]
        out.append(row)
    return out


def _row_apply_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    return {
        "titulo": item.get("titulo"),
        "data_publicacao": item.get("data_publicacao"),
        "link": item.get("link"),
        "categoria": item.get("categoria") or ex.get("categoria"),
        "eixo_estrategico": item.get("eixo_estrategico") or ex.get("eixo_estrategico"),
        "imagem_url": item.get("imagem_url"),
        "validacao_status": item.get("validacao_status"),
        "tipo_conteudo": item.get("tipo_conteudo"),
    }


def main() -> int:
    if not STD_PATH.is_file():
        print(f"[ERRO] Standardized não encontrado: {STD_PATH}", file=sys.stderr)
        return 1

    all_items: List[Dict[str, Any]] = json.loads(STD_PATH.read_text(encoding="utf-8"))
    if not isinstance(all_items, list):
        print("[ERRO] standardized não é lista", file=sys.stderr)
        return 1

    validos = [it for it in all_items if str(it.get("validacao_status") or "") == "valido"]
    payload = _build_payload_noticia(validos)

    PAYLOAD_NOTICIA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_BASE / "softex_noticias_payload_pesquisa.json").write_text("[]", encoding="utf-8")
    (OUT_BASE / "softex_noticias_review_candidates.json").write_text("[]", encoding="utf-8")

    load_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "load_news_research_sources.py"),
        "--dry-run",
        "--source",
        SOURCE_ID,
        "--input-dir",
        INPUT_DIR_REL,
    ]
    proc = subprocess.run(load_cmd, cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stdout)
        print(proc.stderr, file=sys.stderr)
        return proc.returncode

    load_summary: Dict[str, Any] = {}
    load_summary_path = OUT_BASE / "load_news_research_summary.json"
    if load_summary_path.is_file():
        load_summary = json.loads(load_summary_path.read_text(encoding="utf-8"))

    apply_cmd_ps = (
        "# NÃO EXECUTADO — apply staging (executar manualmente após validar .env.staging)\n"
        "$env:EDITALFINDER_ENV='staging'\n"
        "$env:EDITALFINDER_ALLOW_STAGING_APPLY='true'\n"
        "python scripts/load_news_research_sources.py `\n"
        "  --apply --staging --test-db-before-apply `\n"
        f"  --source {SOURCE_ID} `\n"
        f"  --input-dir {INPUT_DIR_REL}"
    )
    apply_cmd_bash = (
        "# NÃO EXECUTADO\n"
        "export EDITALFINDER_ENV=staging\n"
        "export EDITALFINDER_ALLOW_STAGING_APPLY=true\n"
        "python scripts/load_news_research_sources.py \\\n"
        "  --apply --staging --test-db-before-apply \\\n"
        f"  --source {SOURCE_ID} \\\n"
        f"  --input-dir {INPUT_DIR_REL}"
    )

    consolidado: Dict[str, Any] = {
        "fonte": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "apply_executado": False,
        "origem_standardized": str(STD_PATH.relative_to(ROOT)).replace("\\", "/"),
        "payload_noticia": str(PAYLOAD_NOTICIA.relative_to(ROOT)).replace("\\", "/"),
        "totais": {
            "standardized_total": len(all_items),
            "valido_no_payload": len(payload),
            "total_noticias": len(payload),
        },
        "loader_dryrun": {
            "comando": " ".join(load_cmd),
            "input_dir": INPUT_DIR_REL,
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "would_upsert_pesquisa": load_summary.get("would_upsert_pesquisa"),
            "errors_count": load_summary.get("errors_count"),
            "skipped": load_summary.get("skipped"),
            "apply_status": load_summary.get("apply_status"),
            "total_noticia_input": load_summary.get("total_noticia"),
            "summary_path": str(load_summary_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "noticias": [_row_apply_summary(it) for it in payload],
        "apply_staging": {
            "executado": False,
            "powershell": apply_cmd_ps,
            "bash": apply_cmd_bash,
        },
    }

    (OUT_BASE / "consolidado_apply.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# SOFTEX Notícias — preparação apply staging",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **Fonte:** `{SOURCE_ID}`",
        f"- **Apply executado:** não",
        "",
        "## Totais",
        "",
        f"- **Standardized (crawler):** {consolidado['totais']['standardized_total']}",
        f"- **Válidas no payload:** {consolidado['totais']['valido_no_payload']}",
        f"- **would_upsert_noticia:** {consolidado['loader_dryrun']['would_upsert_noticia']}",
        f"- **errors_count:** {consolidado['loader_dryrun']['errors_count']}",
        f"- **apply_status:** `{consolidado['loader_dryrun']['apply_status']}`",
        "",
        "## Dry-run loader",
        "",
        f"```text",
        " ".join(load_cmd),
        "```",
        "",
        f"- Relatório: `{consolidado['loader_dryrun']['summary_path']}`",
        f"- Payload: `{consolidado['payload_noticia']}`",
        "",
        "## Notícias no payload",
        "",
    ]
    for i, row in enumerate(consolidado["noticias"], 1):
        md.append(f"### {i}. {row.get('titulo', '')[:100]}")
        md.append("")
        md.append(f"- **Data:** {row.get('data_publicacao')}")
        md.append(f"- **Categoria:** {row.get('categoria')}")
        md.append(f"- **Eixos:** {', '.join(row.get('eixo_estrategico') or [])}")
        if row.get("imagem_url"):
            md.append(f"- **Imagem:** sim")
        md.append(f"- **Link:** {row.get('link')}")
        md.append("")

    md.extend(
        [
            "## Apply staging (não executado)",
            "",
            "```powershell",
            apply_cmd_ps,
            "```",
            "",
        ]
    )
    (OUT_BASE / "consolidado_apply.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "payload": len(payload),
                "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
                "errors_count": load_summary.get("errors_count"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(str(OUT_BASE / "consolidado_apply.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
