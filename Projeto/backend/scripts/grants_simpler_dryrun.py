#!/usr/bin/env python3
"""
Dry-run Simpler.Grants.gov — não aplica no Supabase.

Gera audit_reports_main_pipeline/grants_simpler_dryrun/:
  raw/grants_simpler_raw.json
  standardized/grants_simpler_standardized.json  (cópia pré-transformer)
  summary.json, summary.md
  review_candidates.json
  descartados_historico.json

Parâmetros iniciais: páginas 1–3, Posted+Forecasted, max 50 itens.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grants_gov.simpler_grants_common import STATUS_HISTORIC, collect_opportunities

OUT_DIR = ROOT / "audit_reports_main_pipeline" / "grants_simpler_dryrun"
MAX_PAGES = 3
MAX_ITEMS = 50
PAGE_SIZE = 25


def _review_candidates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for it in items:
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        cur = ex.get("curadoria_front") if isinstance(ex.get("curadoria_front"), dict) else {}
        vis = cur.get("visibility") or ""
        if vis.startswith("review_") or vis.startswith("hidden_"):
            out.append(
                {
                    "titulo": it.get("titulo"),
                    "link": it.get("link"),
                    "opportunity_number": ex.get("opportunity_number"),
                    "visibility": vis,
                    "reason": cur.get("reason"),
                    "opportunity_status": ex.get("opportunity_status"),
                }
            )
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "raw").mkdir(exist_ok=True)
    (OUT_DIR / "standardized").mkdir(exist_ok=True)

    items, meta = collect_opportunities(
        max_pages=MAX_PAGES,
        page_size=PAGE_SIZE,
        max_items=MAX_ITEMS,
        include_historic=False,
    )

    raw_path = OUT_DIR / "raw" / "grants_simpler_raw.json"
    raw_path.write_text(
        json.dumps({"meta": meta, "items": items}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    std_path = OUT_DIR / "standardized" / "grants_simpler_standardized.json"
    std_path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    review = _review_candidates(items)
    (OUT_DIR / "review_candidates.json").write_text(
        json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    descartados: List[Dict[str, Any]] = []
    (OUT_DIR / "descartados_historico.json").write_text(
        json.dumps(descartados, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    summary = {
        **meta,
        "output_dir": str(OUT_DIR),
        "items_written": len(items),
        "review_candidates": len(review),
        "historic_statuses_excluded": sorted(STATUS_HISTORIC),
        "dryrun_params": {
            "max_pages": MAX_PAGES,
            "max_items": MAX_ITEMS,
            "page_size": PAGE_SIZE,
        },
    }
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md = [
        "# Dry-run Simpler.Grants.gov",
        "",
        f"- **Modo API:** `{meta.get('api_mode')}`",
        f"- **Itens pipeline:** {len(items)}",
        f"- **Revisão (curadoria):** {len(review)}",
        f"- **Páginas:** {MAX_PAGES} | **Max itens:** {MAX_ITEMS}",
        "",
        "## Diagnóstico",
        "",
        "- HTML SSR em `/search` não lista oportunidades (SPA); dados via API ou fallback `search2`.",
        "- Link canônico: `https://simpler.grants.gov/opportunity/{legacy_id|uuid}`",
        "- `robots.txt`: Allow `/`; Disallow `/api/`",
        "- Rate limit API: 60 req/min (usar `SIMPLER_GRANTS_SLEEP_SEC`, default 0.35s)",
        "",
        "## Artefatos",
        "",
        f"- `{raw_path.relative_to(ROOT)}`",
        f"- `{std_path.relative_to(ROOT)}`",
        "",
        "**Não executar apply** — apenas revisão humana.",
    ]
    if meta.get("api_key_missing"):
        md.append("")
        md.append(
            "> Defina `SIMPLER_GRANTS_API_KEY` para busca direta na API Simpler; "
            "sem chave, o dry-run usa `api.grants.gov/search2` + links Simpler."
        )
    (OUT_DIR / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"[dryrun] {len(items)} itens -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
