#!/usr/bin/env python3
"""
Subset top-20 War.gov / U.S. DoD News para apply staging (sem apply).

Origem: audit_reports_news_research/war_gov_news_dryrun_100/standardized/
Comparação 30 vs 100 em war_gov_news_dryrun_100/comparacao_dryrun_30_vs_100.*
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

SOURCE_ID = "war_gov_news"
DRYRUN_30 = ROOT / "audit_reports_news_research" / "war_gov_news_dryrun"
DRYRUN_100 = ROOT / "audit_reports_news_research" / "war_gov_news_dryrun_100"
ORIGIN = DRYRUN_100 / "standardized" / "war_gov_news_standardized.json"
SUMMARY_30 = DRYRUN_30 / "summary.json"
SUMMARY_100 = DRYRUN_100 / "summary.json"
OUT_BASE = ROOT / "audit_reports_news_research" / "war_gov_news_subset_top20"
STD_OUT = OUT_BASE / "standardized" / "war_gov_news_standardized.json"
INPUT_DIR_REL = "audit_reports_news_research/war_gov_news_subset_top20"
TOP_N = 20
WINDOW_MONTHS = 12
DISPLAY_FONTE = "U.S. Department of Defense / War.gov"


def _parse_pub_date(s: Any) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _load_summary(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _examples_from_summary(summary: Dict[str, Any], key: str, n: int = 5) -> List[Dict[str, Any]]:
    return (summary.get("exemplos") or {}).get(key) or []


def _examples_from_discard(path: Path, n: int = 5) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    items = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(items, list):
        return []
    out: List[Dict[str, Any]] = []
    for it in items[:n]:
        out.append(
            {
                "titulo": (it.get("titulo") or "")[:200],
                "link": (it.get("link") or "")[:800],
                "motivos_descarte": (it.get("motivos_descarte") or [])[:6],
                "motivo": it.get("motivo"),
            }
        )
    return out


def _build_comparison(s30: Dict[str, Any], s100: Dict[str, Any]) -> Dict[str, Any]:
    t30 = s30.get("totais") or {}
    t100 = s100.get("totais") or {}
    d30 = s30.get("distribuicao") or {}
    d100 = s100.get("distribuicao") or {}

    def _delta(a: Any, b: Any) -> Any:
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return b - a
        return None

    return {
        "fonte": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dryrun_30_dir": "audit_reports_news_research/war_gov_news_dryrun",
        "dryrun_100_dir": "audit_reports_news_research/war_gov_news_dryrun_100",
        "metricas": {
            "max_items": {"dryrun_30": 30, "dryrun_100": 100},
            "total_raw": {"dryrun_30": t30.get("total_raw"), "dryrun_100": t100.get("total_raw"), "delta": _delta(t30.get("total_raw"), t100.get("total_raw"))},
            "standardized": {
                "dryrun_30": t30.get("standardized"),
                "dryrun_100": t100.get("standardized"),
                "delta": _delta(t30.get("standardized"), t100.get("standardized")),
            },
            "total_valido": {
                "dryrun_30": t30.get("total_valido"),
                "dryrun_100": t100.get("total_valido"),
                "delta": _delta(t30.get("total_valido"), t100.get("total_valido")),
            },
            "descartados_ruido": {
                "dryrun_30": t30.get("descartados_ruido"),
                "dryrun_100": t100.get("descartados_ruido"),
                "delta": _delta(t30.get("descartados_ruido"), t100.get("descartados_ruido")),
            },
            "review": {"dryrun_30": t30.get("review"), "dryrun_100": t100.get("review")},
            "errors_count": {"dryrun_30": t30.get("errors_count"), "dryrun_100": t100.get("errors_count")},
        },
        "eixos_estrategicos": {
            "dryrun_30": d30.get("eixo_estrategico") or {},
            "dryrun_100": d100.get("eixo_estrategico") or {},
        },
        "relevancia_war_gov": {
            "dryrun_30": d30.get("relevancia_war_gov") or {},
            "dryrun_100": d100.get("relevancia_war_gov") or {},
        },
        "exemplos": {
            "mantidos_30": _examples_from_summary(s30, "mantidos"),
            "mantidos_100": _examples_from_summary(s100, "mantidos"),
            "descartados_30": _examples_from_summary(s30, "descartados") or _examples_from_discard(DRYRUN_30 / "descartados_ruido.json"),
            "descartados_100": _examples_from_summary(s100, "descartados") or _examples_from_discard(DRYRUN_100 / "descartados_ruido.json"),
            "review_30": _examples_from_summary(s30, "review"),
            "review_100": _examples_from_summary(s100, "review"),
        },
        "avaliacao": {
            "dryrun_30": s30.get("avaliacao_fonte"),
            "dryrun_100": s100.get("avaliacao_fonte"),
        },
        "observacao_fonte": (
            "Fonte oficial governamental EUA (U.S. Department of Defense / War.gov); "
            "não é jornalismo independente."
        ),
    }


def _comparison_md(comp: Dict[str, Any]) -> str:
    m = comp["metricas"]
    lines = [
        "# War.gov News — comparação dry-run 30 vs 100",
        "",
        f"- **Execução:** {comp['data_execucao']}",
        f"- **source_id:** `{SOURCE_ID}`",
        "",
        comp["observacao_fonte"],
        "",
        "## Métricas",
        "",
        "| Métrica | Dry-run 30 | Dry-run 100 | Δ |",
        "|---------|----------:|------------:|--:|",
    ]
    for key in ("total_raw", "standardized", "total_valido", "descartados_ruido"):
        row = m[key]
        delta = row.get("delta")
        dstr = f"+{delta}" if isinstance(delta, int) and delta > 0 else (str(delta) if delta is not None else "—")
        lines.append(
            f"| {key} | {row.get('dryrun_30')} | {row.get('dryrun_100')} | {dstr} |"
        )
    lines.extend(["", "## Eixos estratégicos (mantidos)", "", "### Dry-run 30", ""])
    for k, v in sorted((comp["eixos_estrategicos"]["dryrun_30"] or {}).items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "### Dry-run 100", ""])
    for k, v in sorted((comp["eixos_estrategicos"]["dryrun_100"] or {}).items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Exemplos mantidos (100)", ""])
    for ex in comp["exemplos"].get("mantidos_100") or []:
        lines.append(f"- [{ex.get('titulo', '')[:80]}]({ex.get('link', '')})")
    lines.extend(["", "## Exemplos descartados (100)", ""])
    for ex in comp["exemplos"].get("descartados_100") or []:
        lines.append(f"- {ex.get('titulo', '')[:80]} — {ex.get('motivos_descarte', [])[:3]}")
    lines.append("")
    return "\n".join(lines)


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
        ex["subset_policy"] = "lote_controlado_fonte_oficial_governamental"
        row["extras"] = ex
        row["fonte_recurso"] = SOURCE_ID
        row["fonte"] = DISPLAY_FONTE
        if str(row.get("tipo_conteudo") or "").lower() == "noticia":
            row.pop("tipo_pesquisa", None)
        if not row.get("descricao") and row.get("resumo"):
            row["descricao"] = row["resumo"]
        out.append(row)
    return out


def main() -> int:
    if not ORIGIN.is_file():
        print(f"[ERRO] Origem não encontrada: {ORIGIN}", file=sys.stderr)
        print("Execute primeiro: python scripts/news_research/run_war_gov_news_dryrun.py --max-items 100 --output-dir audit_reports_news_research/war_gov_news_dryrun_100", file=sys.stderr)
        return 1

    s30 = _load_summary(SUMMARY_30)
    s100 = _load_summary(SUMMARY_100)
    comp = _build_comparison(s30, s100)
    DRYRUN_100.mkdir(parents=True, exist_ok=True)
    (DRYRUN_100 / "comparacao_dryrun_30_vs_100.json").write_text(
        json.dumps(comp, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (DRYRUN_100 / "comparacao_dryrun_30_vs_100.md").write_text(_comparison_md(comp), encoding="utf-8")

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
    (OUT_BASE / "war_gov_news_payload_noticia.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_BASE / "war_gov_news_payload_pesquisa.json").write_text("[]", encoding="utf-8")
    (OUT_BASE / "war_gov_news_review_candidates.json").write_text("[]", encoding="utf-8")

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

    t100 = s100.get("totais") or {}
    eixos = _eixo_distribution(subset)
    consolidado: Dict[str, Any] = {
        "fonte": SOURCE_ID,
        "nome_exibicao": DISPLAY_FONTE,
        "fonte_recurso": SOURCE_ID,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "origem_dryrun_ampliado": str(ORIGIN.relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(STD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "dryrun_ampliado": {
            "max_items": 100,
            "total_raw": t100.get("total_raw"),
            "standardized": t100.get("standardized"),
            "total_valido": t100.get("total_valido"),
            "descartados_ruido": t100.get("descartados_ruido"),
            "errors_count": t100.get("errors_count"),
        },
        "comparacao_30_vs_100": str((DRYRUN_100 / "comparacao_dryrun_30_vs_100.json").relative_to(ROOT)).replace("\\", "/"),
        "subset": {
            "criterios": [
                "validacao_status=valido",
                f"data_publicacao dentro de {WINDOW_MONTHS} meses",
                "ordenar data_publicacao desc",
                f"top {TOP_N}",
                "itens já passaram filtro técnico forte no crawl",
            ],
            "escolhidos": len(subset),
            "candidatos_validos_na_origem": len(candidatos),
            "rejeitados_na_filtragem_subset": len(rejeitados),
        },
        "loader_dryrun": {
            "comando": " ".join(load_cmd),
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "would_upsert_pesquisa": load_summary.get("would_upsert_pesquisa"),
            "errors_count": load_summary.get("errors_count"),
            "apply_status": load_summary.get("apply_status"),
            "summary_path": str(load_path.relative_to(ROOT)).replace("\\", "/") if load_path.is_file() else None,
        },
        "distribuicao_eixos_estrategicos": eixos,
        "itens": [
            {
                "titulo": it.get("titulo"),
                "data_publicacao": it.get("data_publicacao"),
                "link": it.get("link"),
                "relevancia_war_gov": (it.get("extras") or {}).get("relevancia_war_gov"),
                "eixo_estrategico": it.get("eixo_estrategico"),
            }
            for it in subset
        ],
        "observacao": (
            "Fonte oficial governamental dos EUA (U.S. Department of Defense / War.gov). "
            "Não confundir com fonte jornalística independente. "
            "Aplicar apenas lote controlado (subset top 20) para não dominar a aba Notícias. "
            "Apply não executado nesta tarefa."
        ),
        "apply_staging": {"executado": False},
    }

    (OUT_BASE / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# War.gov News — subset top 20 (staging)",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **source_id:** `{SOURCE_ID}`",
        f"- **Exibição:** {DISPLAY_FONTE}",
        "",
        consolidado["observacao"],
        "",
        "## Dry-run ampliado (100)",
        "",
        "| Métrica | Valor |",
        "|---------|------:|",
        f"| Total raw | {consolidado['dryrun_ampliado']['total_raw']} |",
        f"| Standardized | {consolidado['dryrun_ampliado']['standardized']} |",
        f"| Válidos | {consolidado['dryrun_ampliado']['total_valido']} |",
        f"| Descartados | {consolidado['dryrun_ampliado']['descartados_ruido']} |",
        f"| **Subset escolhido** | **{consolidado['subset']['escolhidos']}** |",
        "",
        "## Loader dry-run",
        "",
        f"- **would_upsert_noticia:** {consolidado['loader_dryrun']['would_upsert_noticia']}",
        f"- **errors_count:** {consolidado['loader_dryrun']['errors_count']}",
        f"- **apply_status:** {consolidado['loader_dryrun']['apply_status']}",
        "",
        "## Eixos estratégicos (subset)",
        "",
    ]
    for k, v in sorted(eixos.items(), key=lambda x: (-x[1], x[0])):
        md.append(f"- `{k}`: {v}")
    md.extend(["", "## Itens", ""])
    for i, row in enumerate(consolidado["itens"], 1):
        md.append(
            f"{i}. **{row.get('data_publicacao')}** ({row.get('relevancia_war_gov')}) — "
            f"{row.get('titulo', '')[:90]}"
        )
        md.append(f"   - {row.get('link')}")
    md.append("")
    (OUT_BASE / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "subset": len(subset),
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
