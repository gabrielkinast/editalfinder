#!/usr/bin/env python3
"""
Dry-run — ITA Projetos + LAB Guerra Eletrônica (Pesquisas Estratégicas).

Gera artefatos por fonte em audit_reports_news_research/{source_id}_dryrun/
Sem apply em Supabase.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.crawl_news_research_sources import CONFIG_DEFAULT, _load_json, crawl_source  # noqa: E402

SOURCES: Tuple[str, ...] = ("ita_projetos", "ita_lab_guerra_eletronica")

DIAGNOSTICO: Dict[str, Dict[str, str]] = {
    "ita_projetos": {
        "url": "http://www.ita.br/projetos",
        "tipo_pagina": "listagem/catálogo Drupal de projetos de pesquisa",
        "cms": "Drupal (site ITA)",
        "rss": "Não identificado no hub",
        "recorrencia": "Catálogo institucional (não feed de notícias)",
        "datas": "Ausentes nas fichas auditadas; validacao_status tipicamente incompleto",
        "destino": "public.pesquisa — tipo_pesquisa=projeto_pesquisa",
        "https": "HTTPS www.ita.br com timeout frequente; usar HTTP no crawl",
    },
    "ita_lab_guerra_eletronica": {
        "url": "http://www.ita.br/laboratorios/guerraeletronica",
        "tipo_pagina": "página institucional estática de laboratório",
        "cms": "Drupal (site ITA)",
        "rss": "Não aplicável",
        "recorrencia": "Portal institucional único (não série temporal)",
        "datas": "Sem data de publicação",
        "destino": "public.pesquisa — tipo_pesquisa=portal_institucional",
        "https": "HTTPS www.ita.br com timeout frequente; usar HTTP no crawl",
    },
}


def _run_one(src: Dict[str, Any]) -> Dict[str, Any]:
    sid = str(src.get("id") or "")
    tw = int(src.get("time_window_months") or 24)
    out = ROOT / "audit_reports_news_research" / f"{sid}_dryrun"
    std_dir = out / "standardized"
    raw_dir = out / "raw"
    std_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_items, std_items, meta = crawl_source(src)

    (raw_dir / f"{sid}_raw.json").write_text(
        json.dumps(raw_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (std_dir / f"{sid}_standardized.json").write_text(
        json.dumps(std_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (std_dir / "exemplos.json").write_text(
        json.dumps(std_items[:5], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / f"{sid}_crawl_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    val_counts: Dict[str, int] = {}
    tipo_counts: Dict[str, int] = {}
    tp_counts: Dict[str, int] = {}
    for it in std_items:
        v = str(it.get("validacao_status") or "unknown")
        val_counts[v] = val_counts.get(v, 0) + 1
        tc = str(it.get("tipo_conteudo") or "unknown")
        tipo_counts[tc] = tipo_counts.get(tc, 0) + 1
        tp = str(it.get("tipo_pesquisa") or "—")
        tp_counts[tp] = tp_counts.get(tp, 0) + 1

    warnings: List[Dict[str, Any]] = []
    if meta.get("errors"):
        warnings.append({"tipo": "fetch_errors", "detalhe": meta["errors"]})
    if meta.get("without_date_total"):
        warnings.append(
            {
                "tipo": "sem_data_publicacao",
                "count": meta["without_date_total"],
                "detalhe": "Esperado para catálogo/portal ITA; janela 24m não filtra standardized.",
            }
        )
    if not std_items:
        warnings.append({"tipo": "nenhum_item_standardized", "detalhe": "verificar HTTP/enrich/filtros"})

    diag = DIAGNOSTICO.get(sid, {})
    summary = {
        "fonte": sid,
        "nome_exibicao": src.get("name"),
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run",
        "apply": False,
        "destino_produto": "public.pesquisa (via vw_pesquisas_front, após apply futuro)",
        "diagnostico": diag,
        "config": {
            "max_items": src.get("max_items"),
            "time_window_months": tw,
            "page_enrich_max": src.get("page_enrich_max"),
            "method": src.get("method"),
        },
        "totais": {
            "raw_apos_filtros": meta.get("raw_total"),
            "standardized": len(std_items),
            f"within_window_{tw}m": meta.get("within_window_total"),
            "sem_data": meta.get("without_date_total"),
            "page_enrich_fetches": meta.get("page_enrich_fetch_total"),
            "discarded_post_enrich": meta.get("discarded_post_enrich_total", 0),
        },
        "tipo_conteudo_counts": tipo_counts,
        "tipo_pesquisa_counts": tp_counts,
        "validacao_status_counts": val_counts,
        "itens": [
            {
                "titulo": it.get("titulo"),
                "link": it.get("link"),
                "data_publicacao": it.get("data_publicacao"),
                "tipo_pesquisa": it.get("tipo_pesquisa"),
                "categoria": it.get("categoria")
                or (it.get("extras") or {}).get("categoria"),
                "eixo_estrategico": it.get("eixo_estrategico")
                or (it.get("extras") or {}).get("eixo_estrategico"),
                "validacao_status": it.get("validacao_status"),
                "resumo_len": len(str(it.get("resumo") or "")),
            }
            for it in std_items
        ],
        "warnings": warnings,
        "errors": meta.get("errors") or [],
        "crawl_meta": {
            k: meta.get(k)
            for k in (
                "listing_method",
                "page_kind",
                "note_no_rss",
                "note_no_publication_date",
                "note_static_lab",
            )
            if meta.get(k) is not None
        },
        "paths": {
            "standardized": str((std_dir / f"{sid}_standardized.json").resolve()),
            "raw": str((raw_dir / f"{sid}_raw.json").resolve()),
            "crawl_meta": str((out / f"{sid}_crawl_meta.json").resolve()),
        },
    }

    (out / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        f"# {summary['nome_exibicao']} — dry-run (Pesquisas Estratégicas)",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Modo:** dry-run (sem apply)",
        f"- **Fonte:** `{sid}`",
        f"- **Diagnóstico:** {diag.get('tipo_pagina', '')}",
        "",
        "## Diagnóstico",
        "",
        "| Aspeto | Detalhe |",
        "|--------|---------|",
    ]
    for k, v in diag.items():
        md.append(f"| {k} | {v} |")
    md.extend(
        [
            "",
            "## Resultados",
            "",
            f"- **Standardized:** {summary['totais']['standardized']}",
            f"- **Na janela {tw}m:** {summary['totais'][f'within_window_{tw}m']}",
            f"- **Sem data:** {summary['totais']['sem_data']}",
            f"- **Enrich:** {summary['totais']['page_enrich_fetches']}",
            "",
            "### tipo_pesquisa",
            "",
        ]
    )
    for k, v in tp_counts.items():
        md.append(f"- `{k}`: **{v}**")
    md.extend(["", "### Validação", ""])
    for k, v in val_counts.items():
        md.append(f"- `{k}`: **{v}**")
    md.extend(["", "## Itens", ""])
    for i, row in enumerate(summary["itens"], 1):
        md.append(f"### {i}. {str(row.get('titulo', ''))[:90]}")
        md.append("")
        md.append(f"- **Link:** {row.get('link')}")
        md.append(f"- **Data:** {row.get('data_publicacao') or '—'}")
        md.append(f"- **tipo_pesquisa:** `{row.get('tipo_pesquisa')}`")
        md.append(f"- **Categoria:** {row.get('categoria')}")
        md.append(f"- **Eixos:** {', '.join(row.get('eixo_estrategico') or [])}")
        md.append(f"- **Validação:** `{row.get('validacao_status')}`")
        md.append("")
    if warnings:
        md.extend(["## Warnings", ""])
        for w in warnings:
            md.append(f"- {w}")
    md.append("")
    (out / "summary.md").write_text("\n".join(md), encoding="utf-8")
    return summary


def main() -> int:
    cfg = _load_json(Path(CONFIG_DEFAULT), {})
    sources = cfg.get("sources") if isinstance(cfg, dict) else []
    by_id = {str(s.get("id")): s for s in sources if isinstance(s, dict)}
    results = []
    for sid in SOURCES:
        src = by_id.get(sid)
        if not src:
            print(f"[ERRO] Fonte {sid} não encontrada", file=sys.stderr)
            return 1
        results.append(_run_one(src))
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
