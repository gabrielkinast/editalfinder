#!/usr/bin/env python3
"""
Dry-run Backend 2: enriquecimento de prazos e classificação sem gravar no banco.

Uso:
  python scripts/dry_run_backend_enrichment.py --from-db --limit 5000
  python scripts/dry_run_backend_enrichment.py --input exports/editais.json
  python scripts/dry_run_backend_enrichment.py --output outputs/backend_enrichment_dry_run/
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from deadline_normalizer import normalize_deadline  # noqa: E402
from opportunity_enricher import enrich_opportunity_record  # noqa: E402

DEFAULT_OUT = ROOT / "outputs" / "backend_enrichment_dry_run"


def _pct(n: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{100 * n / total:.1f}%"


def _had_db_structured_before(rec: Dict[str, Any]) -> bool:
    """Prazo já persistido (colunas da tabela), sem re-parse de texto."""
    for k in ("prazo_envio", "fim_inscricao", "prazo"):
        v = rec.get(k)
        if not v:
            continue
        s = str(v).strip()[:10]
        if len(s) >= 8 and s[4:5] == "-":
            return True
    return False


def _had_inferred_before(rec: Dict[str, Any]) -> bool:
    """Inclui normalização sobre o registro bruto (equivale a re-rodar normalizer)."""
    return bool(normalize_deadline(rec).get("prazo_data"))


def _implicit_db_kind(rec: Dict[str, Any]) -> str:
    """Registros na tabela edital são tratados como 'edital' até roteamento explícito."""
    return "edital"


def run_dry_run(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    status_before = Counter()
    status_after = Counter()
    conf_after = Counter()
    kind_after = Counter()
    mod_after = Counter()
    scope_after = Counter()
    flags_c = Counter()
    fonte_gain: Counter = Counter()
    fonte_still: Counter = Counter()

    gains_prazo_db = 0
    gains_prazo_inferred = 0
    still_sem = 0
    low_conf = 0
    kind_changes: List[Dict[str, Any]] = []
    low_conf_review: List[Dict[str, Any]] = []
    changes_by_field: Counter = Counter()
    samples: List[Dict[str, Any]] = []

    for rec in records:
        before_dl = normalize_deadline(rec)
        status_before[before_dl["prazo_status"]] += 1
        had_db = _had_db_structured_before(rec)
        had_inferred = _had_inferred_before(rec)

        enriched = enrich_opportunity_record(rec)
        after_dl = {
            "prazo_data": enriched.get("prazo_data"),
            "prazo_status": enriched.get("prazo_status"),
            "prazo_confidence": enriched.get("prazo_confidence"),
        }
        status_after[enriched.get("prazo_status") or "sem_prazo"] += 1
        conf_after[enriched.get("prazo_confidence") or "nenhuma"] += 1
        kind_after[enriched.get("tipo_registro") or "desconhecido"] += 1
        mod_after[enriched.get("modalidade_normalizada") or "sem_classificacao"] += 1
        scope_after[enriched.get("escopo_geografico") or "desconhecido"] += 1

        for f in enriched.get("qualidade_flags") or []:
            flags_c[f] += 1

        fonte = str(rec.get("fonte_recurso") or rec.get("fonte") or "—")[:80]
        if enriched.get("prazo_data") and not had_db:
            gains_prazo_db += 1
            fonte_gain[fonte] += 1
        if enriched.get("prazo_data") and not had_inferred:
            gains_prazo_inferred += 1
        if enriched.get("prazo_status") == "sem_prazo":
            still_sem += 1
            fonte_still[fonte] += 1
        if enriched.get("prazo_confidence") == "baixa":
            low_conf += 1

        implicit = _implicit_db_kind(rec)
        new_kind = enriched.get("tipo_registro")
        if new_kind and new_kind != implicit:
            changes_by_field["tipo_registro"] += 1
            if len(kind_changes) < 200:
                kind_changes.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:120],
                        "fonte_recurso": rec.get("fonte_recurso"),
                        "kind_antes": implicit,
                        "kind_depois": new_kind,
                        "kind_confidence": enriched.get("kind_confidence"),
                        "kind_reasons": enriched.get("kind_reasons"),
                        "modalidade": enriched.get("modalidade_normalizada"),
                    }
                )

        if "revisao_humana" in (enriched.get("qualidade_flags") or []):
            if len(low_conf_review) < 300:
                low_conf_review.append(
                    {
                        "id_edital": rec.get("id_edital"),
                        "titulo": (rec.get("titulo") or "")[:100],
                        "fonte_recurso": rec.get("fonte_recurso"),
                        "qualidade_flags": enriched.get("qualidade_flags"),
                        "prazo_status": enriched.get("prazo_status"),
                        "prazo_confidence": enriched.get("prazo_confidence"),
                        "tipo_registro": new_kind,
                        "modalidade_normalizada": enriched.get("modalidade_normalizada"),
                    }
                )

        if enriched.get("prazo_data") and not rec.get("prazo_data"):
            changes_by_field["prazo_data"] += 1
        if enriched.get("modalidade_normalizada"):
            changes_by_field["modalidade_normalizada"] += 1
        if enriched.get("escopo_geografico"):
            changes_by_field["escopo_geografico"] += 1
        if enriched.get("fonte_normalizada"):
            changes_by_field["fonte_normalizada"] += 1

        if len(samples) < 25:
            samples.append(
                {
                    "id_edital": rec.get("id_edital"),
                    "titulo": (rec.get("titulo") or "")[:80],
                    "antes": {
                        "prazo_envio": rec.get("prazo_envio"),
                        "prazo_status": before_dl["prazo_status"],
                    },
                    "depois": {
                        "prazo_data": enriched.get("prazo_data"),
                        "prazo_status": enriched.get("prazo_status"),
                        "prazo_confidence": enriched.get("prazo_confidence"),
                        "tipo_registro": new_kind,
                        "modalidade_normalizada": enriched.get("modalidade_normalizada"),
                        "escopo_geografico": enriched.get("escopo_geografico"),
                        "qualidade_flags": enriched.get("qualidade_flags"),
                    },
                }
            )

    return {
        "total": total,
        "prazo_status_before": dict(status_before),
        "prazo_status_after": dict(status_after),
        "prazo_confidence_after": dict(conf_after),
        "gains_prazo_data_db_columns": gains_prazo_db,
        "gains_prazo_data_new_inference": gains_prazo_inferred,
        "still_sem_prazo": still_sem,
        "low_confidence_prazo": low_conf,
        "tipo_registro": dict(kind_after),
        "modalidade_normalizada": dict(mod_after),
        "escopo_geografico": dict(scope_after),
        "qualidade_flags": dict(flags_c),
        "kind_changes_count": changes_by_field.get("tipo_registro", 0),
        "top_fontes_gain": fonte_gain.most_common(20),
        "top_fontes_sem_prazo": fonte_still.most_common(20),
        "changes_by_field": dict(changes_by_field),
        "samples": samples,
        "kind_changes": kind_changes,
        "low_confidence_review": low_conf_review,
    }


def build_summary_md(r: Dict[str, Any]) -> str:
    t = r["total"]
    lines = [
        "# Dry-run Backend 2 — enriquecimento",
        "",
        f"**Registros analisados:** {t}",
        "",
        "## Prazos",
        "",
        f"- Ganham `prazo_data` sem `prazo_envio`/`fim_inscricao` na BD: **{r['gains_prazo_data_db_columns']}** ({_pct(r['gains_prazo_data_db_columns'], t)})",
        f"- Ganho *novo* (nem normalizer no registro bruto): **{r['gains_prazo_data_new_inference']}**",
        f"- Continuam `sem_prazo`: **{r['still_sem_prazo']}** ({_pct(r['still_sem_prazo'], t)})",
        f"- Prazo com confiança baixa: **{r['low_confidence_prazo']}**",
        "",
        "### prazo_status (antes → depois)",
        "",
        "**Antes:**",
    ]
    for k, v in sorted(r["prazo_status_before"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v} ({_pct(v, t)})")
    lines.append("")
    lines.append("**Depois (enriquecido):**")
    for k, v in sorted(r["prazo_status_after"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v} ({_pct(v, t)})")
    lines.extend(["", "### Confiança de prazo (depois)", ""])
    for k, v in r["prazo_confidence_after"].items():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "### Top fontes — melhora de prazo", ""])
    for fonte, cnt in r["top_fontes_gain"]:
        lines.append(f"- {fonte}: +{cnt}")
    lines.extend(["", "### Top fontes — ainda sem prazo", ""])
    for fonte, cnt in r["top_fontes_sem_prazo"][:15]:
        lines.append(f"- {fonte}: {cnt}")
    lines.extend(
        [
            "",
            "## Classificação",
            "",
            "### tipo_registro",
            "",
        ]
    )
    for k, v in sorted(r["tipo_registro"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v} ({_pct(v, t)})")
    lines.extend(["", "### modalidade_normalizada", ""])
    for k, v in sorted(r["modalidade_normalizada"].items(), key=lambda x: -x[1])[:15]:
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "### escopo_geografico", ""])
    for k, v in sorted(r["escopo_geografico"].items(), key=lambda x: -x[1]):
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            f"### Mudanças de kind (edital na BD → outro tipo): **{r['kind_changes_count']}**",
            "",
            "## Qualidade (flags)",
            "",
        ]
    )
    for k, v in sorted(r["qualidade_flags"].items(), key=lambda x: -x[1])[:20]:
        lines.append(f"- `{k}`: {v}")
    lines.extend(
        [
            "",
            "## Artefatos",
            "",
            "- `enriched_sample.json` — amostra antes/depois",
            "- `changes_by_field.json` — contagem por campo novo",
            "- `low_confidence_review.json` — revisão humana sugerida",
            "- `kind_changes_review.json` — kind diferente de edital implícito",
            "",
            "**Nenhum UPDATE foi executado.** Integração real exige migration + backfill com relatório.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run enriquecimento Backend 2")
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    out_dir = args.output
    records = load_records(from_db=args.from_db, input_path=args.input, limit=args.limit)
    if not records:
        write_md(out_dir / "summary.md", "# Sem dados\n\nUse --from-db ou --input.")
        write_json(out_dir / "report.json", {"total": 0, "error": "no_data"})
        print("[dry_run_backend_enrichment] sem registros", file=sys.stderr)
        return 1

    report = run_dry_run(records)
    write_md(out_dir / "summary.md", build_summary_md(report))
    write_json(out_dir / "report.json", {k: v for k, v in report.items() if k not in ("samples", "kind_changes", "low_confidence_review")})
    write_json(out_dir / "enriched_sample.json", report["samples"])
    write_json(out_dir / "changes_by_field.json", report["changes_by_field"])
    write_json(out_dir / "low_confidence_review.json", report["low_confidence_review"])
    write_json(out_dir / "kind_changes_review.json", report["kind_changes"])
    print(f"[dry_run_backend_enrichment] {report['total']} registros -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
