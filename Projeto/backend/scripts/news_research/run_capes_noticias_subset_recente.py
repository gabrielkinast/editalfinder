#!/usr/bin/env python3
"""
Subset recente — CAPES Notícias (válido + janela 12m).

- Filtra validacao_status=valido e data_publicacao nos últimos 12 meses
- Dry-run load_news_research_sources.py
- consolidado_subset.json / .md
Sem apply.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ORIGIN = (
    ROOT
    / "audit_reports_news_research"
    / "capes_noticias_dryrun"
    / "standardized"
    / "capes_noticias_standardized.json"
)
OUT_BASE = ROOT / "audit_reports_news_research" / "capes_noticias_subset_recente"
STD_OUT = OUT_BASE / "standardized" / "capes_noticias_standardized.json"
PAYLOAD_NOTICIA = OUT_BASE / "capes_noticias_payload_noticia.json"
INPUT_DIR_REL = "audit_reports_news_research/capes_noticias_subset_recente"
SOURCE_ID = "capes_noticias"
WINDOW_MONTHS = 12


def _parse_pub_date(item: Dict[str, Any]) -> Optional[datetime]:
    raw = str(item.get("data_publicacao") or "").strip()[:10]
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _within_public_window(item: Dict[str, Any], min_dt: datetime) -> bool:
    dt = _parse_pub_date(item)
    return bool(dt and dt >= min_dt)


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


def _row_summary(item: Dict[str, Any]) -> Dict[str, Any]:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    return {
        "titulo": item.get("titulo"),
        "data_publicacao": item.get("data_publicacao"),
        "link": item.get("link"),
        "categoria": item.get("categoria") or ex.get("categoria"),
        "eixo_estrategico": item.get("eixo_estrategico") or ex.get("eixo_estrategico"),
        "imagem_url": item.get("imagem_url"),
        "validacao_status": item.get("validacao_status"),
    }


def main() -> int:
    if not ORIGIN.is_file():
        print(f"[ERRO] Origem não encontrada: {ORIGIN}", file=sys.stderr)
        return 1

    all_items: List[Dict[str, Any]] = json.loads(ORIGIN.read_text(encoding="utf-8"))
    if not isinstance(all_items, list):
        print("[ERRO] JSON de origem não é lista", file=sys.stderr)
        return 1

    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * WINDOW_MONTHS)
    recentes: List[Dict[str, Any]] = []
    excluidos: List[Dict[str, Any]] = []
    for it in all_items:
        if str(it.get("validacao_status") or "") != "valido":
            excluidos.append({**_row_summary(it), "motivo": "validacao_status!=valido"})
            continue
        if not _within_public_window(it, min_dt):
            excluidos.append({**_row_summary(it), "motivo": f"fora_janela_{WINDOW_MONTHS}m"})
            continue
        recentes.append(it)

    STD_OUT.parent.mkdir(parents=True, exist_ok=True)
    STD_OUT.write_text(json.dumps(recentes, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = _build_payload_noticia(recentes)
    PAYLOAD_NOTICIA.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_BASE / "capes_noticias_payload_pesquisa.json").write_text("[]", encoding="utf-8")
    (OUT_BASE / "capes_noticias_review_candidates.json").write_text("[]", encoding="utf-8")

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

    incluidos = [_row_summary(it) for it in recentes]
    consolidado: Dict[str, Any] = {
        "fonte": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "apply_executado": False,
        "origem_standardized": str(ORIGIN.relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(STD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "janela_publica_meses": WINDOW_MONTHS,
        "corte_data_minima": min_dt.date().isoformat(),
        "totais": {
            "original": len(all_items),
            "recente": len(recentes),
            "excluido": len(excluidos),
            "valido_original": sum(1 for it in all_items if str(it.get("validacao_status") or "") == "valido"),
        },
        "itens_incluidos": incluidos,
        "itens_excluidos": excluidos,
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
        "payload_pronto_apply": {
            "noticia": str(PAYLOAD_NOTICIA.relative_to(ROOT)).replace("\\", "/"),
            "registos": len(payload),
        },
        "apply_staging": {
            "executado": False,
            "powershell": apply_cmd_ps,
        },
    }

    (OUT_BASE / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# CAPES Notícias — subset recente (12m, consolidado)",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **Origem:** `{consolidado['origem_standardized']}`",
        f"- **Subset:** `{consolidado['subset_standardized']}`",
        f"- **Janela pública:** {WINDOW_MONTHS} meses (corte ≥ `{consolidado['corte_data_minima']}`)",
        f"- **Apply executado:** não",
        "",
        "## Totais",
        "",
        f"- **Original:** {consolidado['totais']['original']}",
        f"- **Válidas no original:** {consolidado['totais']['valido_original']}",
        f"- **Recente (válido + 12m):** {consolidado['totais']['recente']}",
        f"- **Excluídas:** {consolidado['totais']['excluido']}",
        f"- **would_upsert_noticia:** {consolidado['loader_dryrun']['would_upsert_noticia']}",
        f"- **errors_count:** {consolidado['loader_dryrun']['errors_count']}",
        "",
        "## Itens incluídos",
        "",
    ]
    for i, row in enumerate(incluidos, 1):
        md.append(f"### {i}. {str(row.get('titulo', ''))[:95]}")
        md.append("")
        md.append(f"- **Data:** {row.get('data_publicacao')}")
        md.append(f"- **Categoria:** {row.get('categoria')}")
        md.append(f"- **Eixos:** {', '.join(row.get('eixo_estrategico') or [])}")
        md.append(f"- **Link:** {row.get('link')}")
        md.append("")

    if excluidos:
        md.extend(["## Excluídas do subset", ""])
        for row in excluidos:
            md.append(f"- **{str(row.get('titulo', ''))[:80]}** — {row.get('data_publicacao')} — _{row.get('motivo')}_")
        md.append("")

    md.extend(
        [
            "## Dry-run loader",
            "",
            f"```text",
            " ".join(load_cmd),
            "```",
            "",
            f"- Relatório: `{consolidado['loader_dryrun']['summary_path']}`",
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
                "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
                "errors_count": load_summary.get("errors_count"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(str(OUT_BASE / "consolidado_subset.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
