#!/usr/bin/env python3
"""
Dry-run piloto SOFTEX Notícias — Notícias Estratégicas.

Gera artefatos em audit_reports_news_research/softex_noticias_dryrun/
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

OUT = ROOT / "audit_reports_news_research" / "softex_noticias_dryrun"
SOURCE_ID = "softex_noticias"


def main() -> int:
    cfg = _load_json(Path(CONFIG_DEFAULT), {})
    sources = cfg.get("sources") if isinstance(cfg, dict) else []
    src = next((s for s in sources if str(s.get("id")) == SOURCE_ID), None)
    if not src:
        print(f"[ERRO] Fonte {SOURCE_ID} não encontrada em {CONFIG_DEFAULT}", file=sys.stderr)
        return 1

    raw_items, std_items, meta = crawl_source(src)
    tw = int(src.get("time_window_months") or 12)

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
    tipo_counts: dict = {}
    for it in std_items:
        v = str(it.get("validacao_status") or "unknown")
        val_counts[v] = val_counts.get(v, 0) + 1
        tc = str(it.get("tipo_conteudo") or "unknown")
        tipo_counts[tc] = tipo_counts.get(tc, 0) + 1

    warnings = []
    if meta.get("errors"):
        warnings.append({"tipo": "fetch_errors", "detalhe": meta["errors"]})
    if meta.get("without_date_total"):
        warnings.append({"tipo": "sem_data", "count": meta["without_date_total"]})
    within = meta.get("within_window_total", 0)
    total = meta.get("raw_total", 0)
    if total and within < total:
        warnings.append(
            {
                "tipo": f"fora_janela_{tw}m",
                "count": total - within,
                "detalhe": f"Itens mantidos no standardized; view pública usa {tw} meses.",
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
            "url_hub": "https://softex.br/noticias/",
            "rss_seed": "https://softex.br/feed/",
            "rss_noticias_feed": "https://softex.br/noticias/feed/ (403 — não usar)",
            "robots_txt": "Disallow: /wp-admin/ (resto permitido)",
            "cms": "WordPress",
            "listagem": "RSS 2.0 global; hub HTML /noticias/",
            "permalink": "Slugs na raiz do domínio (ex. /softex-participa-da-inauguracao-.../)",
            "data_publicacao": "pubDate RSS + enrich meta opcional",
            "autor": "dc:creator quando presente no feed",
            "imagem": "og:image no enrich (budget limitado)",
            "copyright": "Apenas resumo RSS/meta; sem corpo integral",
        },
        "config": {
            "max_items": src.get("max_items"),
            "time_window_months": tw,
            "page_enrich_max": src.get("page_enrich_max"),
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
        "# SOFTEX Notícias — dry-run (Notícias Estratégicas)",
        "",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Modo:** dry-run (sem apply)",
        f"- **Fonte:** `{SOURCE_ID}` — {summary['nome_exibicao']}",
        "",
        "## Diagnóstico",
        "",
        "| Aspeto | Detalhe |",
        "|--------|---------|",
        f"| Hub | {summary['diagnostico']['url_hub']} |",
        f"| RSS | `{summary['diagnostico']['rss_seed']}` |",
        f"| RSS /noticias/feed | {summary['diagnostico']['rss_noticias_feed']} |",
        f"| robots.txt | {summary['diagnostico']['robots_txt']} |",
        f"| CMS | {summary['diagnostico']['cms']} |",
        f"| Permalink | {summary['diagnostico']['permalink']} |",
        f"| Data | {summary['diagnostico']['data_publicacao']} |",
        f"| Copyright | {summary['diagnostico']['copyright']} |",
        "",
        "## Resultados",
        "",
        f"- **Standardized:** {summary['totais']['standardized']}",
        f"- **Na janela {tw}m:** {summary['totais'][f'within_window_{tw}m']}",
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
