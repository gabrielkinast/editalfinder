#!/usr/bin/env python3
"""
Dry-run piloto BRISA News — Notícias Estratégicas.

Gera artefatos em audit_reports_news_research/brisa_news_dryrun/
Sem apply em Supabase.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.crawl_news_research_sources import (  # noqa: E402
    CONFIG_DEFAULT,
    _load_json,
    crawl_source,
)

OUT = ROOT / "audit_reports_news_research" / "brisa_news_dryrun"
SOURCE_ID = "brisa_news"


def main() -> int:
    cfg = _load_json(Path(CONFIG_DEFAULT), {})
    sources = cfg.get("sources") if isinstance(cfg, dict) else []
    src = next((s for s in sources if str(s.get("id")) == SOURCE_ID), None)
    if not src:
        print(f"[ERRO] Fonte {SOURCE_ID} não encontrada em {CONFIG_DEFAULT}", file=sys.stderr)
        return 1

    raw_items, std_items, meta = crawl_source(src)

    std_dir = OUT / "standardized"
    raw_dir = OUT / "raw"
    std_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    (raw_dir / f"{SOURCE_ID}_raw.json").write_text(
        json.dumps(raw_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (std_dir / f"{SOURCE_ID}_standardized.json").write_text(
        json.dumps(std_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (std_dir / "exemplos.json").write_text(
        json.dumps(std_items[:5], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / f"{SOURCE_ID}_crawl_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    val_counts: dict = {}
    for it in std_items:
        v = str(it.get("validacao_status") or "unknown")
        val_counts[v] = val_counts.get(v, 0) + 1

    warnings = []
    if meta.get("errors"):
        warnings.append({"tipo": "fetch_errors", "detalhe": meta["errors"]})
    if meta.get("note_low_volume"):
        warnings.append({"tipo": "volume_baixo_feed", "detalhe": meta["note_low_volume"]})
    if meta.get("without_date_total"):
        warnings.append({"tipo": "sem_data", "count": meta["without_date_total"]})
    outside = meta.get("within_window_total", 0)
    total = meta.get("raw_total", 0)
    if total and outside < total:
        warnings.append(
            {
                "tipo": "fora_janela_12m",
                "count": total - outside,
                "detalhe": "Itens mantidos com data_publicacao; ver within_window no meta.",
            }
        )
    if not std_items:
        warnings.append({"tipo": "nenhum_item_standardized", "detalhe": "verificar RSS ou filtros"})

    summary = {
        "fonte": SOURCE_ID,
        "nome_exibicao": src.get("name"),
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run",
        "apply": False,
        "diagnostico": {
            "url_listagem": "https://brisabr.com.br/news/",
            "rss_seed": "https://brisabr.com.br/news/feed/",
            "robots_txt": "Disallow: /wp-admin/ (resto permitido)",
            "cms": "WordPress",
            "listagem": "RSS 2.0 seção News; HTML /news/ espelha os mesmos ~4 posts",
            "data_publicacao": "pubDate RSS + enrich meta opcional",
            "autor": "dc:creator (ex.: Pamela Souza)",
            "imagem": "og:image no enrich (budget limitado)",
            "copyright": "Apenas resumo RSS/meta; sem corpo integral",
            "nao_concursos": "Secção /news/ apenas — /artigos/ excluído",
        },
        "config": {
            "max_items": src.get("max_items"),
            "time_window_months": src.get("time_window_months"),
            "page_enrich_max": src.get("page_enrich_max"),
        },
        "totais": {
            "raw_apos_filtros": meta.get("raw_total"),
            "standardized": len(std_items),
            "within_window_12m": meta.get("within_window_total"),
            "sem_data": meta.get("without_date_total"),
            "page_enrich_fetches": meta.get("page_enrich_fetch_total"),
            "discarded_post_enrich": meta.get("discarded_post_enrich_total", 0),
        },
        "validacao_status_counts": val_counts,
        "warnings": warnings,
        "errors": meta.get("errors") or [],
        "paths": {
            "standardized": str((std_dir / f"{SOURCE_ID}_standardized.json").resolve()),
            "exemplos": str((std_dir / "exemplos.json").resolve()),
            "raw": str((raw_dir / f"{SOURCE_ID}_raw.json").resolve()),
            "crawl_meta": str((OUT / f"{SOURCE_ID}_crawl_meta.json").resolve()),
        },
    }

    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# BRISA News — dry-run (Notícias Estratégicas)",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Modo:** dry-run (sem apply)",
        f"- **Fonte:** `{SOURCE_ID}` — {summary['nome_exibicao']}",
        "",
        "## Diagnóstico",
        "",
        "| Aspeto | Detalhe |",
        "|--------|---------|",
        f"| Listagem | {summary['diagnostico']['url_listagem']} |",
        f"| RSS | `{summary['diagnostico']['rss_seed']}` |",
        f"| robots.txt | {summary['diagnostico']['robots_txt']} |",
        f"| CMS | {summary['diagnostico']['cms']} |",
        f"| Canal | {summary['diagnostico']['listagem']} |",
        f"| Data | {summary['diagnostico']['data_publicacao']} |",
        f"| Autor | {summary['diagnostico']['autor']} |",
        f"| Imagem | {summary['diagnostico']['imagem']} |",
        f"| Copyright | {summary['diagnostico']['copyright']} |",
        f"| Concursos | {summary['diagnostico']['nao_concursos']} |",
        "",
        "## Resultados",
        "",
        f"- **Standardized:** {summary['totais']['standardized']}",
        f"- **Na janela 12m:** {summary['totais']['within_window_12m']}",
        f"- **Enrich páginas:** {summary['totais']['page_enrich_fetches']}",
        "",
        "### Validação",
        "",
    ]
    for k, v in val_counts.items():
        md.append(f"- `{k}`: **{v}**")
    if warnings:
        md.extend(["", "## Warnings", ""])
        for w in warnings:
            md.append(f"- {w}")
    md.extend(
        [
            "",
            "## Artefatos",
            "",
            f"- `{summary['paths']['standardized']}`",
            f"- `{summary['paths']['raw']}`",
            "",
            "Ver [STRATEGIC_NEWS_RESEARCH_SOURCES.md](../docs/STRATEGIC_NEWS_RESEARCH_SOURCES.md).",
            "",
        ]
    )
    (OUT / "summary.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({"summary": summary["totais"], "validacao": val_counts}, ensure_ascii=False, indent=2))
    print(summary["paths"]["standardized"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
