#!/usr/bin/env python3
"""
Subset top-20 Lockheed Martin Newsroom para apply staging (sem apply).
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

SOURCE_ID = "lockheed_martin_news"
ORIGIN = (
    ROOT
    / "audit_reports_news_research"
    / "lockheed_martin_news_dryrun_30"
    / "standardized"
    / "lockheed_martin_news_standardized.json"
)
DRYRUN30_SUMMARY = (
    ROOT / "audit_reports_news_research" / "lockheed_martin_news_dryrun_30" / "summary.json"
)
OUT_BASE = ROOT / "audit_reports_news_research" / "lockheed_martin_news_subset_top20"
STD_OUT = OUT_BASE / "standardized" / "lockheed_martin_news_standardized.json"
INPUT_DIR_REL = "audit_reports_news_research/lockheed_martin_news_subset_top20"
TOP_N = 20
WINDOW_MONTHS = 12


def _parse_pub_date(s: Any):
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
            row["fonte"] = "Lockheed Martin"
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
    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * WINDOW_MONTHS)
    candidatos: List[tuple] = []
    rejeitados: List[Dict[str, Any]] = []

    for it in all_items:
        if str(it.get("validacao_status") or "") != "valido":
            rejeitados.append({"link": it.get("link"), "motivo": "validacao_status!=valido"})
            continue
        dt = _parse_pub_date(it.get("data_publicacao"))
        if not dt or dt < min_dt:
            rejeitados.append({"link": it.get("link"), "motivo": "fora_janela_12m"})
            continue
        candidatos.append((dt, it))

    candidatos.sort(key=lambda x: x[0], reverse=True)
    subset = [it for _, it in candidatos[:TOP_N]]

    STD_OUT.parent.mkdir(parents=True, exist_ok=True)
    STD_OUT.write_text(json.dumps(subset, ensure_ascii=False, indent=2), encoding="utf-8")

    payload = _build_payload_noticia(subset)
    (OUT_BASE / "lockheed_martin_news_payload_noticia.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_BASE / "lockheed_martin_news_payload_pesquisa.json").write_text("[]", encoding="utf-8")
    (OUT_BASE / "lockheed_martin_news_review_candidates.json").write_text("[]", encoding="utf-8")

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
    if proc.stdout:
        print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        return proc.returncode

    load_summary: Dict[str, Any] = {}
    load_path = OUT_BASE / "load_news_research_summary.json"
    if load_path.is_file():
        load_summary = json.loads(load_path.read_text(encoding="utf-8"))

    feed_inv: Dict[str, Any] = {}
    if DRYRUN30_SUMMARY.is_file():
        feed_inv = json.loads(DRYRUN30_SUMMARY.read_text(encoding="utf-8")).get("feed_inventory") or {}

    eixos = _eixo_distribution(subset)
    consolidado = {
        "fonte": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "origem_dryrun_ampliado": str(ORIGIN.relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(STD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "feed": {
            "total_no_feed": feed_inv.get("total_no_feed"),
            "elegiveis_12m": feed_inv.get("total_elegivel_pos_filtros_pipeline")
            or feed_inv.get("total_elegivel_pos_filtros_basicos"),
            "total_dentro_12m_bruto": feed_inv.get("total_dentro_janela_meses"),
            "dryrun_ampliado_processados": 30,
            "dryrun_ampliado_validos": (
                json.loads(DRYRUN30_SUMMARY.read_text(encoding="utf-8"))
                .get("totais", {})
                .get("total_valido")
                if DRYRUN30_SUMMARY.is_file()
                else None
            ),
        },
        "subset": {
            "escolhidos": len(subset),
            "criterios": [
                "validacao_status=valido",
                "data_publicacao 12m",
                "ordenar desc",
                "top 20",
                "filtros técnicos herdados do crawl",
            ],
            "candidatos_validos_origem_30": len(candidatos),
        },
        "loader_dryrun": {
            "comando": " ".join(load_cmd),
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "errors_count": load_summary.get("errors_count"),
            "apply_status": load_summary.get("apply_status"),
        },
        "distribuicao_eixos_estrategicos": eixos,
        "itens": [
            {
                "titulo": it.get("titulo"),
                "data_publicacao": it.get("data_publicacao"),
                "link": it.get("link"),
                "eixo_estrategico": it.get("eixo_estrategico"),
            }
            for it in subset
        ],
        "observacao": (
            "Fonte corporativa/institucional Lockheed Martin Newsroom. "
            "Aplicar apenas lote controlado (20 itens); não dominar aba Notícias. "
            "Apply não executado."
        ),
        "apply_staging": {"executado": False},
    }

    (OUT_BASE / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Lockheed Martin Newsroom — subset top 20",
        "",
        f"- **source_id:** `{SOURCE_ID}`",
        "",
        "## Feed",
        "",
        f"| Total feed | {consolidado['feed'].get('total_no_feed')} |",
        f"| Dentro 12m (bruto) | {consolidado['feed'].get('total_dentro_12m_bruto')} |",
        f"| Elegíveis pipeline | {consolidado['feed'].get('elegiveis_12m')} |",
        f"| Dry-run 30 válidos | {consolidado['feed'].get('dryrun_ampliado_validos')} |",
        f"| **Subset** | **{consolidado['subset']['escolhidos']}** |",
        "",
        "## Loader",
        "",
        f"- **would_upsert_noticia:** {consolidado['loader_dryrun']['would_upsert_noticia']}",
        f"- **errors_count:** {consolidado['loader_dryrun']['errors_count']}",
        "",
        "## Eixos",
        "",
    ]
    for k, v in sorted(eixos.items(), key=lambda x: (-x[1], x[0])):
        md.append(f"- `{k}`: {v}")
    md.extend(["", "## Observação", "", consolidado["observacao"], ""])
    (OUT_BASE / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "subset": len(subset),
                "would_upsert_noticia": consolidado["loader_dryrun"]["would_upsert_noticia"],
                "errors_count": consolidado["loader_dryrun"]["errors_count"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
