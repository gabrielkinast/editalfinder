#!/usr/bin/env python3
"""
Subset AFRL News válido para apply staging (sem apply).

Origem: audit_reports_news_research/afrl_strategic_dryrun/standardized/
Inclui afrl_news + afrl_mission_highlights (notícias válidas, 12m).
Exclui diretorias RA/RJ/RR (pesquisa incompleta).
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LOADER_SOURCE = "afrl_news"
ALLOWED_FONTES_RECURSO = frozenset({"afrl_news", "afrl_mission_highlights"})
DRYRUN_DIR = ROOT / "audit_reports_news_research" / "afrl_strategic_dryrun"
ORIGIN_NEWS = DRYRUN_DIR / "standardized" / "afrl_news_standardized.json"
ORIGIN_HL = DRYRUN_DIR / "standardized" / "afrl_mission_highlights_standardized.json"
OUT_BASE = ROOT / "audit_reports_news_research" / "afrl_news_subset_valido"
STD_OUT = OUT_BASE / "standardized" / "afrl_news_standardized.json"
INPUT_DIR_REL = "audit_reports_news_research/afrl_news_subset_valido"
WINDOW_MONTHS = 12
DISPLAY_FONTE = "AFRL"


def _parse_pub_date(s: Any) -> Optional[datetime]:
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


def _load_items(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _filter_item(it: Dict[str, Any], min_dt: datetime) -> Tuple[bool, str]:
    fr = str(it.get("fonte_recurso") or "").strip()
    if fr not in ALLOWED_FONTES_RECURSO:
        return False, f"fonte_recurso_excluida:{fr}"
    if str(it.get("tipo_conteudo") or "").strip().lower() != "noticia":
        return False, "tipo_conteudo!=noticia"
    if str(it.get("validacao_status") or "") != "valido":
        return False, "validacao_status!=valido"
    dt = _parse_pub_date(it.get("data_publicacao"))
    if not dt or dt < min_dt:
        return False, "fora_janela_12m_ou_sem_data"
    return True, ""


def _prepare_subset(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        row = dict(item)
        ex = dict(row.get("extras") or {})
        ex["subset"] = "afrl_news_valido_12m"
        ex["subset_policy"] = "apply_controlado_fonte_oficial_afrl"
        row["extras"] = ex
        row["fonte"] = DISPLAY_FONTE
        if not row.get("descricao") and row.get("resumo"):
            row["descricao"] = row["resumo"]
        row.pop("tipo_pesquisa", None)
        out.append(row)
    return out


def main() -> int:
    if not ORIGIN_NEWS.is_file():
        print(f"[ERRO] Não encontrado: {ORIGIN_NEWS}", file=sys.stderr)
        return 1

    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * WINDOW_MONTHS)
    items_news = _load_items(ORIGIN_NEWS)
    items_hl = _load_items(ORIGIN_HL)
    all_in = items_news + items_hl

    validos_origem = Counter()
    for it in items_news:
        if str(it.get("validacao_status") or "") == "valido":
            validos_origem["afrl_news"] += 1
    for it in items_hl:
        if str(it.get("validacao_status") or "") == "valido":
            validos_origem["afrl_mission_highlights"] += 1

    chosen: List[Dict[str, Any]] = []
    rejeitados: List[Dict[str, Any]] = []
    seen_links: set = set()
    by_fonte: Counter = Counter()

    for it in all_in:
        ok, why = _filter_item(it, min_dt)
        lk = str(it.get("link") or "").strip()
        if not ok:
            rejeitados.append({"link": lk, "fonte_recurso": it.get("fonte_recurso"), "motivo": why})
            continue
        if lk in seen_links:
            rejeitados.append({"link": lk, "motivo": "link_duplicado"})
            continue
        seen_links.add(lk)
        fr = str(it.get("fonte_recurso") or "")
        by_fonte[fr] += 1
        chosen.append(it)

    chosen.sort(
        key=lambda x: _parse_pub_date(x.get("data_publicacao")) or datetime(1970, 1, 1, tzinfo=timezone.utc),
        reverse=True,
    )
    subset = _prepare_subset(chosen)

    STD_OUT.parent.mkdir(parents=True, exist_ok=True)
    STD_OUT.write_text(json.dumps(subset, ensure_ascii=False, indent=2), encoding="utf-8")

    (OUT_BASE / "afrl_news_payload_pesquisa.json").write_text("[]", encoding="utf-8")
    (OUT_BASE / "afrl_news_review_candidates.json").write_text("[]", encoding="utf-8")

    load_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "load_news_research_sources.py"),
        "--dry-run",
        "--source",
        LOADER_SOURCE,
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

    eixos = _eixo_distribution(subset)
    n_news = by_fonte.get("afrl_news", 0)
    n_hl = by_fonte.get("afrl_mission_highlights", 0)

    consolidado: Dict[str, Any] = {
        "fonte": LOADER_SOURCE,
        "nome_exibicao": DISPLAY_FONTE,
        "loader_source_id": LOADER_SOURCE,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "origem_dryrun": str(DRYRUN_DIR.relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(STD_OUT.relative_to(ROOT)).replace("\\", "/"),
        "totais_origem": {
            "afrl_news_standardized": len(items_news),
            "afrl_mission_highlights_standardized": len(items_hl),
        },
        "validos_no_dryrun": dict(validos_origem),
        "highlights_validos_fora_12m": sum(
            1
            for it in items_hl
            if str(it.get("validacao_status") or "") == "valido"
            and not _filter_item(it, min_dt)[0]
        ),
        "filtros": {
            "fonte_recurso": sorted(ALLOWED_FONTES_RECURSO),
            "tipo_conteudo": "noticia",
            "validacao_status": "valido",
            "janela_meses": WINDOW_MONTHS,
            "excluido": [
                "afrl_air_warfare_research",
                "afrl_space_warfare_research",
                "afrl_technology_transition",
                "pesquisa_incompleta",
                "review_candidates",
            ],
        },
        "contagem_por_fonte_recurso": {
            "afrl_news": n_news,
            "afrl_mission_highlights": n_hl,
        },
        "subset": {
            "escolhidos": len(subset),
            "rejeitados_na_filtragem": len(rejeitados),
        },
        "loader_dryrun": {
            "comando": " ".join(load_cmd),
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "would_upsert_pesquisa": load_summary.get("would_upsert_pesquisa"),
            "errors_count": load_summary.get("errors_count"),
            "apply_status": load_summary.get("apply_status"),
            "routing_skipped_count": load_summary.get("routing_skipped_count"),
        },
        "eixos_estrategicos": eixos,
        "itens": [
            {
                "titulo": it.get("titulo"),
                "data_publicacao": it.get("data_publicacao"),
                "link": it.get("link"),
                "fonte_recurso": it.get("fonte_recurso"),
                "diretoria_origem": (it.get("extras") or {}).get("diretoria_origem"),
                "relevancia_afrl": (it.get("extras") or {}).get("relevancia_afrl"),
            }
            for it in subset
        ],
        "observacoes": [
            "Fonte oficial/institucional AFRL (U.S. Air Force Research Laboratory); apply controlado.",
            "RA/RJ/RR permanecem latentes/incompletos (pesquisa sem data) — não incluídos neste subset.",
            "Apply não executado nesta tarefa.",
        ],
        "apply_staging": {"executado": False},
    }

    (OUT_BASE / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# AFRL News — subset válido (staging)",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **Loader `--source`:** `{LOADER_SOURCE}`",
        "",
        "## Observações",
        "",
    ]
    for obs in consolidado["observacoes"]:
        md.append(f"- {obs}")
    md.extend(
        [
            "",
            "## Contagem por fonte",
            "",
            f"| fonte_recurso | Itens no subset |",
            f"|---------------|----------------:|",
            f"| afrl_news | {n_news} |",
            f"| afrl_mission_highlights | {n_hl} |",
            f"| **Total subset** | **{len(subset)}** |",
            "",
            "## Loader dry-run",
            "",
            f"- **would_upsert_noticia:** {consolidado['loader_dryrun']['would_upsert_noticia']}",
            f"- **errors_count:** {consolidado['loader_dryrun']['errors_count']}",
            f"- **apply_status:** {consolidado['loader_dryrun']['apply_status']}",
            "",
            "## Eixos estratégicos",
            "",
        ]
    )
    for k, v in sorted(eixos.items(), key=lambda x: (-x[1], x[0])):
        md.append(f"- `{k}`: {v}")
    md.extend(["", "## Itens", ""])
    for i, row in enumerate(consolidado["itens"], 1):
        fr = row.get("fonte_recurso") or ""
        extra = f" ({row.get('diretoria_origem')})" if row.get("diretoria_origem") else ""
        md.append(
            f"{i}. **{row.get('data_publicacao')}** `[{fr}]`{extra} — "
            f"{(row.get('titulo') or '')[:85]}"
        )
        md.append(f"   - {row.get('link')}")
    md.append("")
    (OUT_BASE / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "afrl_news": n_news,
                "afrl_mission_highlights": n_hl,
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
