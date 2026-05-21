#!/usr/bin/env python3
"""
Dry-run MCTI Fomento → Radar/Editais/Oportunidades.

Não usa crawl_news_research_sources.py, não grava em public.noticia, não executa apply.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.radar.mcti_fomento_lib import (  # noqa: E402
    SOURCE_ID,
    crawl_mcti_fomento,
)


def _write_summary_md(out_dir: Path, summary: dict) -> None:
    lines = [
        "# MCTI Fomento — dry-run Radar/Editais",
        "",
        f"- **Gerado em:** {summary.get('generated_at')}",
        f"- **source_id:** `{summary.get('source_id')}`",
        f"- **Destino:** Radar/Editais (não `public.noticia`)",
        f"- **Apply:** não executado",
        "",
        "## Totais",
        "",
        f"- Candidatos na fila: **{summary.get('candidatos_fila', 0)}**",
        f"- Itens padronizados: **{summary.get('total_standardized', 0)}**",
        f"- Review candidates: **{summary.get('total_review', 0)}**",
        f"- Enriquecimentos HTTP: **{summary.get('page_enrich_fetches', 0)}**",
        "",
        "## Por tipo",
        "",
    ]
    for k, v in sorted((summary.get("por_tipo") or {}).items()):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Por status", ""])
    for k, v in sorted((summary.get("por_status") or {}).items()):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Por validação", ""])
    for k, v in sorted((summary.get("por_validacao") or {}).items()):
        lines.append(f"- `{k}`: {v}")
    errs = summary.get("errors") or []
    if errs:
        lines.extend(["", "## Erros de seed", ""])
        for e in errs:
            lines.append(f"- {e.get('seed')}: {e.get('error')}")
    lines.extend(
        [
            "",
            "## Artefatos",
            "",
            "- `standardized/mcti_fomento_standardized.json`",
            "- `review_candidates.json`",
            "- `summary.json`",
            "",
            "## Seeds",
            "",
        ]
    )
    for s in summary.get("seeds") or []:
        lines.append(f"- {s}")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    out_dir = ROOT / "audit_reports_radar" / "mcti_fomento_dryrun"
    std_dir = out_dir / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)

    standardized, review, _descartados, meta = crawl_mcti_fomento(ROOT, strict_curation=False)

    std_path = std_dir / "mcti_fomento_standardized.json"
    std_path.write_text(
        json.dumps(standardized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    review_path = out_dir / "review_candidates.json"
    review_path.write_text(
        json.dumps(review, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    por_tipo = Counter(r.get("tipo") for r in standardized)
    por_status = Counter(r.get("status") for r in standardized)
    por_validacao = Counter(r.get("validacao_status") for r in standardized)

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_id": SOURCE_ID,
        "pipeline": "radar_editais_dryrun",
        "apply_executed": False,
        "noticia_loader": False,
        "candidatos_fila": meta.get("candidatos_fila"),
        "page_enrich_fetches": meta.get("page_enrich_fetches"),
        "total_standardized": len(standardized),
        "total_review": len(review),
        "por_tipo": dict(por_tipo),
        "por_status": dict(por_status),
        "por_validacao": dict(por_validacao),
        "seeds": meta.get("seeds"),
        "errors": meta.get("errors"),
        "output_paths": {
            "standardized": str(std_path.relative_to(ROOT)),
            "review": str(review_path.relative_to(ROOT)),
        },
        "diagnostic_input": "audit_reports_news_research/mcti_fomento_diagnostic/",
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _write_summary_md(out_dir, summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
