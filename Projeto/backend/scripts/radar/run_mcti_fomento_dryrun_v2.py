#!/usr/bin/env python3
"""
Dry-run MCTI Fomento v2 — curadoria endurecida (allowlist/blocklist).

Saída: audit_reports_radar/mcti_fomento_dryrun_v2/
Compara com v1 em audit_reports_radar/mcti_fomento_dryrun/
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from typing import Set
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.radar.mcti_fomento_lib import (  # noqa: E402
    SOURCE_ID,
    crawl_mcti_fomento,
)

V1_DIR = ROOT / "audit_reports_radar" / "mcti_fomento_dryrun"
V2_DIR = ROOT / "audit_reports_radar" / "mcti_fomento_dryrun_v2"


def _load_v1_summary() -> dict:
    p = V1_DIR / "summary.json"
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def _write_summary_md(out_dir: Path, summary: dict) -> None:
    cmp_ = summary.get("comparacao_v1_v2") or {}
    lines = [
        "# MCTI Fomento — dry-run Radar/Editais v2 (curadoria endurecida)",
        "",
        f"- **Gerado em:** {summary.get('generated_at')}",
        f"- **source_id:** `{summary.get('source_id')}`",
        f"- **Curadoria:** allowlist/blocklist v2",
        f"- **Apply:** não executado",
        "",
        "## Totais v2",
        "",
        f"- Candidatos na fila (após filtro): **{summary.get('candidatos_fila', 0)}**",
        f"- Padronizados: **{summary.get('total_standardized', 0)}**",
        f"- Review candidates: **{summary.get('total_review', 0)}**",
        f"- Descartados (ruído/institucional): **{summary.get('total_descartados', 0)}**",
        f"- Prontos para apply (`valido` + status ativo/latente): **{summary.get('pronto_para_apply', 0)}**",
        f"- Enriquecimentos HTTP: **{summary.get('page_enrich_fetches', 0)}**",
        "",
        "## Comparação v1 → v2",
        "",
        f"| Métrica | v1 | v2 | Δ |",
        f"|---------|---:|---:|---:|",
        f"| Padronizados | {cmp_.get('v1_total_standardized', '—')} | {cmp_.get('v2_total_standardized', '—')} | {cmp_.get('delta_standardized', '—')} |",
        f"| Válidos | {cmp_.get('v1_valido', '—')} | {cmp_.get('v2_valido', '—')} | {cmp_.get('delta_valido', '—')} |",
        f"| Review | {cmp_.get('v1_review', '—')} | {cmp_.get('v2_review', '—')} | {cmp_.get('delta_review', '—')} |",
        f"| Prontos apply | {cmp_.get('v1_pronto_apply', '—')} | {cmp_.get('v2_pronto_apply', '—')} | {cmp_.get('delta_pronto_apply', '—')} |",
        f"| Links removidos do standardized | — | — | **{cmp_.get('links_removidos_do_standardized', '—')}** |",
        f"| Descartados (links únicos) | — | **{cmp_.get('descartados_links_unicos', '—')}** | — |",
        "",
        "## Por tipo (v2)",
        "",
    ]
    for k, v in sorted((summary.get("por_tipo") or {}).items()):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Por validação (v2)", ""])
    for k, v in sorted((summary.get("por_validacao") or {}).items()):
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            "## Artefatos",
            "",
            "- `standardized/mcti_fomento_standardized.json`",
            "- `review_candidates.json`",
            "- `descartados_ruido.json`",
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
    out_dir = V2_DIR
    std_dir = out_dir / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)

    standardized, review, descartados, meta = crawl_mcti_fomento(ROOT, strict_curation=True)

    std_path = std_dir / "mcti_fomento_standardized.json"
    std_path.write_text(json.dumps(standardized, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path = out_dir / "review_candidates.json"
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")
    desc_path = out_dir / "descartados_ruido.json"
    desc_path.write_text(json.dumps(descartados, ensure_ascii=False, indent=2), encoding="utf-8")

    por_tipo = Counter(r.get("tipo") for r in standardized)
    por_status = Counter(r.get("status") for r in standardized)
    por_validacao = Counter(r.get("validacao_status") for r in standardized)
    por_decisao = Counter(d.get("decisao") for d in descartados)

    v1 = _load_v1_summary()
    v1_std = int(v1.get("total_standardized") or 0)
    v2_std = len(standardized)
    v1_valido = int((v1.get("por_validacao") or {}).get("valido", 0))
    v2_valido = int(por_validacao.get("valido", 0))
    v1_review = int(v1.get("total_review") or 0)
    v1_pronto = int(v1.get("pronto_para_apply") or v1_valido)
    v2_pronto = int(meta.get("pronto_para_apply", 0))

    v1_links: Set[str] = set()
    v1_path = V1_DIR / "standardized" / "mcti_fomento_standardized.json"
    if v1_path.is_file():
        for row in json.loads(v1_path.read_text(encoding="utf-8")):
            if isinstance(row, dict) and row.get("link"):
                v1_links.add(str(row["link"]))
    v2_links = {str(r.get("link")) for r in standardized if r.get("link")}
    removidos_do_standardized = sorted(v1_links - v2_links)

    comparacao = {
        "v1_total_standardized": v1_std,
        "v2_total_standardized": v2_std,
        "delta_standardized": v1_std - v2_std,
        "v1_valido": v1_valido,
        "v2_valido": v2_valido,
        "delta_valido": v2_valido - v1_valido,
        "v1_review": v1_review,
        "v2_review": len(review),
        "delta_review": len(review) - v1_review,
        "v1_pronto_apply": v1_pronto,
        "v2_pronto_apply": v2_pronto,
        "delta_pronto_apply": v2_pronto - v1_pronto,
        "links_removidos_do_standardized": len(removidos_do_standardized),
        "links_removidos_amostra": removidos_do_standardized[:15],
        "descartados_total_registros": len(descartados),
        "descartados_links_unicos": len({d.get("link") for d in descartados if d.get("link")}),
        "ruidos_removidos": len(removidos_do_standardized),
        "v1_path": str(V1_DIR.relative_to(ROOT)) if V1_DIR.is_dir() else None,
    }

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_id": SOURCE_ID,
        "pipeline": "radar_editais_dryrun_v2",
        "curacao": "strict_allowlist_blocklist",
        "apply_executed": False,
        "noticia_loader": False,
        "candidatos_fila": meta.get("candidatos_fila"),
        "page_enrich_fetches": meta.get("page_enrich_fetches"),
        "total_standardized": v2_std,
        "total_review": len(review),
        "total_descartados": len(descartados),
        "por_decisao_descartados": dict(por_decisao),
        "pronto_para_apply": meta.get("pronto_para_apply", 0),
        "por_tipo": dict(por_tipo),
        "por_status": dict(por_status),
        "por_validacao": dict(por_validacao),
        "comparacao_v1_v2": comparacao,
        "seeds": meta.get("seeds"),
        "errors": meta.get("errors"),
        "output_paths": {
            "standardized": str(std_path.relative_to(ROOT)),
            "review": str(review_path.relative_to(ROOT)),
            "descartados": str(desc_path.relative_to(ROOT)),
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
