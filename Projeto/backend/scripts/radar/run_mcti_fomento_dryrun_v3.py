#!/usr/bin/env python3
"""
Dry-run MCTI Fomento v3 — curadoria conservadora (pronto / review / institucional / ruído).

Saída: audit_reports_radar/mcti_fomento_dryrun_v3/
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.radar.mcti_fomento_lib import (  # noqa: E402
    NIVEL_PRONTO,
    SOURCE_ID,
    crawl_mcti_fomento_v3,
)

V2_DIR = ROOT / "audit_reports_radar" / "mcti_fomento_dryrun_v2"
V3_DIR = ROOT / "audit_reports_radar" / "mcti_fomento_dryrun_v3"


def _links_from_std(path: Path) -> Set[str]:
    if not path.is_file():
        return set()
    return {str(r.get("link")) for r in json.loads(path.read_text(encoding="utf-8")) if r.get("link")}


def _load_v2_summary() -> Dict[str, Any]:
    p = V2_DIR / "summary.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def _write_summary_md(out_dir: Path, summary: dict) -> None:
    cmp_ = summary.get("comparacao_v2_v3") or {}
    lines = [
        "# MCTI Fomento — dry-run Radar/Editais v3 (curadoria conservadora)",
        "",
        f"- **Gerado em:** {summary.get('generated_at')}",
        f"- **source_id:** `{summary.get('source_id')}`",
        f"- **Níveis:** `pronto_para_apply` | `review` | `institucional_latente` | `descartado_ruido`",
        f"- **Apply:** não executado",
        "",
        "## Totais v3",
        "",
        f"- Fila crawl (candidatos): **{summary.get('candidatos_fila', 0)}**",
        f"- **Prontos para apply** (standardized): **{summary.get('total_pronto_para_apply', 0)}**",
        f"- Review: **{summary.get('total_review', 0)}**",
        f"- Institucional latente: **{summary.get('total_institucional_latente', 0)}**",
        f"- Descartados ruído: **{summary.get('total_descartados', 0)}**",
        "",
        "## Comparação v2 → v3",
        "",
        f"| Métrica | v2 | v3 | Δ |",
        f"|---------|---:|---:|---:|",
        f"| Padronizados (v2) / Prontos (v3) | {cmp_.get('v2_total_standardized', '—')} | {cmp_.get('v3_total_pronto', '—')} | {cmp_.get('delta_pronto_vs_v2_std', '—')} |",
        f"| Review | {cmp_.get('v2_review', '—')} | {cmp_.get('v3_review', '—')} | {cmp_.get('delta_review', '—')} |",
        f"| Prontos apply | {cmp_.get('v2_pronto_apply', '—')} | {cmp_.get('v3_pronto_apply', '—')} | {cmp_.get('delta_pronto_apply', '—')} |",
        f"| Links saíram do pronto (vs v2 std) | — | — | **{cmp_.get('links_removidos_v2_std', '—')}** |",
        "",
        "## Artefatos",
        "",
        "- `standardized/mcti_fomento_standardized.json` — somente `pronto_para_apply`",
        "- `review_candidates.json`",
        "- `institucional_latente.json`",
        "- `descartados_ruido.json`",
        "- `comparacao_v2_v3.json`",
        "",
    ]
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    out_dir = V3_DIR
    std_dir = out_dir / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)

    pronto, review, institucional, descartados, meta = crawl_mcti_fomento_v3(ROOT)

    std_path = std_dir / "mcti_fomento_standardized.json"
    std_path.write_text(json.dumps(pronto, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "review_candidates.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (out_dir / "institucional_latente.json").write_text(
        json.dumps(institucional, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (out_dir / "descartados_ruido.json").write_text(
        json.dumps(descartados, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    v2 = _load_v2_summary()
    v2_std_path = V2_DIR / "standardized" / "mcti_fomento_standardized.json"
    v2_links = _links_from_std(v2_std_path)
    v3_links = {str(r.get("link")) for r in pronto if r.get("link")}

    comparacao = {
        "v2_total_standardized": int(v2.get("total_standardized") or 46),
        "v3_total_pronto": len(pronto),
        "delta_pronto_vs_v2_std": int(v2.get("total_standardized") or 46) - len(pronto),
        "v2_valido": int((v2.get("por_validacao") or {}).get("valido", 0)),
        "v3_valido": len(pronto),
        "v2_review": int(v2.get("total_review") or 0),
        "v3_review": len(review),
        "delta_review": len(review) - int(v2.get("total_review") or 0),
        "v2_pronto_apply": int(v2.get("pronto_para_apply") or 0),
        "v3_pronto_apply": len(pronto),
        "delta_pronto_apply": len(pronto) - int(v2.get("pronto_para_apply") or 0),
        "links_removidos_v2_std": len(v2_links - v3_links),
        "links_removidos_amostra": sorted(v2_links - v3_links)[:20],
        "v3_institucional_latente": len(institucional),
        "v3_descartados": len(descartados),
    }
    (out_dir / "comparacao_v2_v3.json").write_text(
        json.dumps(comparacao, ensure_ascii=False, indent=2), encoding="utf-8",
    )

    por_tipo = Counter(r.get("tipo") for r in pronto)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_id": SOURCE_ID,
        "pipeline": "radar_editais_dryrun_v3",
        "curacao": "v3_conservadora",
        "apply_executed": False,
        "candidatos_fila": meta.get("candidatos_fila"),
        "page_enrich_fetches": meta.get("page_enrich_fetches"),
        "total_pronto_para_apply": len(pronto),
        "total_standardized": len(pronto),
        "total_review": len(review),
        "total_institucional_latente": len(institucional),
        "total_descartados": len(descartados),
        "por_tipo_pronto": dict(por_tipo),
        "comparacao_v2_v3": comparacao,
        "seeds": meta.get("seeds"),
        "errors": meta.get("errors"),
        "output_paths": {
            "standardized": str(std_path.relative_to(ROOT)),
            "review": "audit_reports_radar/mcti_fomento_dryrun_v3/review_candidates.json",
            "institucional_latente": "audit_reports_radar/mcti_fomento_dryrun_v3/institucional_latente.json",
            "descartados": "audit_reports_radar/mcti_fomento_dryrun_v3/descartados_ruido.json",
            "comparacao": "audit_reports_radar/mcti_fomento_dryrun_v3/comparacao_v2_v3.json",
        },
        "nota_standardized": "Apenas itens com nivel_curacao=pronto_para_apply (>=2 sinais fortes v3).",
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    _write_summary_md(out_dir, summary)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
