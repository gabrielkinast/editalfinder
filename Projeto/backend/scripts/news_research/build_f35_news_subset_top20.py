#!/usr/bin/env python3
"""
Subset top-20 F-35 News para apply staging (sem apply).

Origem: audit_reports_news_research/f35_news_dryrun_30/standardized/
Saída: audit_reports_news_research/f35_news_subset_top20/
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SOURCE_ID = "f35_news"
ORIGIN = (
    ROOT
    / "audit_reports_news_research"
    / "f35_news_dryrun_30"
    / "standardized"
    / "f35_news_standardized.json"
)
DRYRUN30_SUMMARY = ROOT / "audit_reports_news_research" / "f35_news_dryrun_30" / "summary.json"
OUT_BASE = ROOT / "audit_reports_news_research" / "f35_news_subset_top20"
STD_OUT = OUT_BASE / "standardized" / "f35_news_standardized.json"
INPUT_DIR_REL = "audit_reports_news_research/f35_news_subset_top20"
TOP_N = 20
WINDOW_MONTHS = 12


def _parse_pub_date(s: Any) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _eixo_distribution(items: List[Dict[str, Any]]) -> Dict[str, int]:
    c: Counter = Counter()
    for it in items:
        for e in it.get("eixo_estrategico") or (it.get("extras") or {}).get("eixo_estrategico") or []:
            if e:
                c[str(e)] += 1
    return dict(c.most_common(20))


def _build_payload_noticia(validos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in validos:
        row = dict(item)
        ex = dict(row.get("extras") or {})
        ex["source_id"] = SOURCE_ID
        ex["subset"] = "top20_recente_12m"
        ex["subset_policy"] = "lote_controlado_fonte_corporativa"
        row["extras"] = ex
        row["fonte_recurso"] = SOURCE_ID
        if not row.get("fonte"):
            row["fonte"] = "F-35"
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

    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * WINDOW_MONTHS)
    candidatos: List[tuple[datetime, Dict[str, Any]]] = []
    rejeitados: List[Dict[str, Any]] = []

    for it in all_items:
        if str(it.get("validacao_status") or "") != "valido":
            rejeitados.append({"link": it.get("link"), "motivo": "validacao_status!=valido"})
            continue
        dt = _parse_pub_date(it.get("data_publicacao"))
        if not dt or dt < min_dt:
            rejeitados.append(
                {
                    "link": it.get("link"),
                    "motivo": "fora_janela_12m",
                    "data_publicacao": it.get("data_publicacao"),
                }
            )
            continue
        candidatos.append((dt, it))

    candidatos.sort(key=lambda x: x[0], reverse=True)
    subset = [it for _, it in candidatos[:TOP_N]]

    STD_OUT.parent.mkdir(parents=True, exist_ok=True)
    STD_OUT.write_text(json.dumps(subset, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = _build_payload_noticia(subset)
    (OUT_BASE / "f35_news_payload_noticia.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_BASE / "f35_news_payload_pesquisa.json").write_text("[]", encoding="utf-8")
    (OUT_BASE / "f35_news_review_candidates.json").write_text("[]", encoding="utf-8")

    load_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "load_news_research_sources.py"),
        "--dry-run",
        "--source",
        SOURCE_ID,
        "--input-dir",
        INPUT_DIR_REL,
    ]
    proc_load = subprocess.run(load_cmd, cwd=str(ROOT), capture_output=True, text=True)
    if proc_load.stdout:
        print(proc_load.stdout)
    if proc_load.returncode != 0:
        print(proc_load.stderr, file=sys.stderr)
        return proc_load.returncode

    load_summary: Dict[str, Any] = {}
    load_path = OUT_BASE / "load_news_research_summary.json"
    if load_path.is_file():
        load_summary = json.loads(load_path.read_text(encoding="utf-8"))

    feed_inv: Dict[str, Any] = {}
    if DRYRUN30_SUMMARY.is_file():
        s30 = json.loads(DRYRUN30_SUMMARY.read_text(encoding="utf-8"))
        feed_inv = s30.get("feed_inventory") or {}

    eixos = _eixo_distribution(subset)
    consolidado: Dict[str, Any] = {
        "fonte": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "origem_dryrun_ampliado": str(ORIGIN.relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(STD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "feed": {
            "total_no_feed": feed_inv.get("total_no_feed", 302),
            "elegiveis_12m": feed_inv.get("total_elegivel_pos_filtros_pipeline")
            or feed_inv.get("total_dentro_janela_meses", 80),
            "dryrun_ampliado_processados": 30,
            "dryrun_ampliado_validos": 30,
        },
        "subset": {
            "criterios": [
                "validacao_status=valido",
                f"data_publicacao dentro de {WINDOW_MONTHS} meses",
                "ordenar data_publicacao desc",
                f"top {TOP_N}",
            ],
            "escolhidos": TOP_N,
            "candidatos_validos_na_origem": len(candidatos),
            "rejeitados_na_filtragem": len(rejeitados),
        },
        "loader_dryrun": {
            "comando": " ".join(load_cmd),
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "would_upsert_pesquisa": load_summary.get("would_upsert_pesquisa"),
            "errors_count": load_summary.get("errors_count"),
            "apply_status": load_summary.get("apply_status"),
            "summary_path": str(load_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "distribuicao_eixos_estrategicos": eixos,
        "itens": [
            {
                "titulo": it.get("titulo"),
                "data_publicacao": it.get("data_publicacao"),
                "link": it.get("link"),
                "categoria": it.get("categoria"),
                "eixo_estrategico": it.get("eixo_estrategico"),
            }
            for it in subset
        ],
        "observacao": (
            "Fonte institucional/corporativa (Lockheed Martin / programa F-35). "
            "Aplicar apenas lote controlado (20 itens) para não dominar a aba Notícias. "
            "Apply staging não executado nesta tarefa."
        ),
        "apply_staging": {"executado": False},
    }

    (OUT_BASE / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# F-35 News — subset top 20 (staging)",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **source_id:** `{SOURCE_ID}`",
        "",
        "## Contexto do feed",
        "",
        f"| Métrica | Valor |",
        f"|---------|------:|",
        f"| Total no feed | {consolidado['feed']['total_no_feed']} |",
        f"| Elegíveis 12m | {consolidado['feed']['elegiveis_12m']} |",
        f"| Dry-run ampliado (30) válidos | {consolidado['feed']['dryrun_ampliado_validos']} |",
        f"| **Subset escolhido** | **{consolidado['subset']['escolhidos']}** |",
        "",
        "## Loader dry-run",
        "",
        f"- **would_upsert_noticia:** {consolidado['loader_dryrun']['would_upsert_noticia']}",
        f"- **errors_count:** {consolidado['loader_dryrun']['errors_count']}",
        f"- **apply_status:** {consolidado['loader_dryrun']['apply_status']}",
        "",
        "## Distribuição de eixos (subset)",
        "",
    ]
    for k, v in sorted(eixos.items(), key=lambda x: (-x[1], x[0])):
        md.append(f"- `{k}`: {v}")
    md.extend(
        [
            "",
            "## Observação",
            "",
            consolidado["observacao"],
            "",
            "## Itens (por data desc)",
            "",
        ]
    )
    for i, row in enumerate(consolidado["itens"], 1):
        md.append(f"{i}. **{row.get('data_publicacao')}** — {row.get('titulo', '')[:90]}")
        md.append(f"   - {row.get('link')}")
    md.append("")
    (OUT_BASE / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "subset": TOP_N,
                "would_upsert_noticia": consolidado["loader_dryrun"]["would_upsert_noticia"],
                "errors_count": consolidado["loader_dryrun"]["errors_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
