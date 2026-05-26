#!/usr/bin/env python3
"""
Gera payload para tabela sombra Backend 7 — sem escrita por padrão.

Uso:
  python scripts/generate_backend_enrichment_shadow_payload.py --from-db --limit 5000

Escrita opcional (somente tabela sombra):
  EDITALFINDER_ALLOW_SHADOW_WRITE=true python scripts/generate_backend_enrichment_shadow_payload.py --from-db --limit 5000 --write-shadow
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from _backend_shadow_common import (  # noqa: E402
    SHADOW_WRITE_ENV,
    analyze_shadow_batch,
    build_shadow_payload,
    field_coverage,
    shadow_write_allowed,
    write_shadow_rows,
)

OUT_DIR = ROOT / "outputs" / "backend_7_shadow_payload"


def build_summary(
    total: int,
    coverage: Dict[str, int],
    analysis: Dict[str, Any],
    *,
    write_result: Dict[str, Any] | None = None,
) -> str:
    lines = [
        "# Payload tabela sombra — Backend 7",
        "",
        f"**Registros processados:** {total}",
        "",
        "## Cobertura por campo",
        "",
    ]
    for col, n in sorted(coverage.items(), key=lambda x: -x[1]):
        pct = 100 * n / max(1, total)
        lines.append(f"- `{col}`: {n} ({pct:.1f}%)")
    lines.extend(
        [
            "",
            "## Revisão humana",
            f"- Baixa confiança (qualquer campo): **{len(analysis['low_confidence_rows'])}**",
            f"- Prazo baixa confiança: **{len(analysis['deadline_low_confidence'])}**",
            f"- Mudanças sensíveis de tipo (notícia/pesquisa/concurso): **{len(analysis['risky_kind_changes'])}**",
            f"- Área baixa confiança ou sem classificação: **{len(analysis['risky_area_changes'])}**",
            "",
        ]
    )
    if write_result:
        lines.append(f"**Escrita sombra:** {write_result.get('written', 0)} linhas em `{write_result.get('table')}`.")
    else:
        lines.append("Nenhuma escrita no banco (modo dry-run). Use `--write-shadow` com env de proteção.")
    lines.extend(
        [
            "",
            f"Para gravar: `{SHADOW_WRITE_ENV}=true` + `--write-shadow`",
            "",
            "Artefatos: `shadow_payload.json`, `low_confidence_rows.json`, `risky_kind_changes.json`,",
            "`risky_area_changes.json`, `deadline_low_confidence.json`.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument(
        "--write-shadow",
        action="store_true",
        help=f"Grava na tabela sombra (exige {SHADOW_WRITE_ENV}=true)",
    )
    args = ap.parse_args()

    if args.write_shadow and not shadow_write_allowed():
        print(f"[ERRO] --write-shadow exige {SHADOW_WRITE_ENV}=true")
        return 2

    records = load_records(from_db=args.from_db, input_path=args.input, limit=args.limit)
    if not records:
        write_md(OUT_DIR / "summary.md", "# Sem dados")
        return 1

    payloads = [build_shadow_payload(r) for r in records]
    analysis = analyze_shadow_batch(records, payloads)
    coverage = field_coverage(payloads)

    write_json(OUT_DIR / "shadow_payload.json", payloads)
    write_md(
        OUT_DIR / "summary.md",
        build_summary(len(records), coverage, analysis),
    )
    write_json(OUT_DIR / "low_confidence_rows.json", analysis["low_confidence_rows"])
    write_json(OUT_DIR / "risky_kind_changes.json", analysis["risky_kind_changes"])
    write_json(OUT_DIR / "risky_area_changes.json", analysis["risky_area_changes"])
    write_json(OUT_DIR / "deadline_low_confidence.json", analysis["deadline_low_confidence"])
    write_json(
        OUT_DIR / "field_coverage.json",
        {"total": len(records), "coverage": coverage},
    )

    write_result = None
    if args.write_shadow:
        write_result = write_shadow_rows(payloads)
        write_md(
            OUT_DIR / "summary.md",
            build_summary(len(records), coverage, analysis, write_result=write_result),
        )
        print(f"[write-shadow] {write_result['written']} -> {write_result['table']}")

    print(f"[generate_shadow_payload] {len(records)} -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
