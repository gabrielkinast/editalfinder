#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def _load(p: Path) -> Dict[str, Any]:
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _get(d: Dict[str, Any], k: str) -> int:
    v = d.get(k)
    return int(v) if isinstance(v, (int, float)) else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", type=Path, required=True)
    ap.add_argument("--after", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    b = _load(args.before)
    a = _load(args.after)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    keys = [
        "itens_analisados",
        "raw_com_documentos",
        "transformado_com_documentos",
        "payload_com_documentos",
        "bruto_com_documentos_pdf",
        "bruto_com_documentos_nao_pdf",
        "transformado_com_documentos_pdf",
        "transformado_com_documentos_nao_pdf",
        "payload_com_documentos_pdf",
        "payload_com_documentos_nao_pdf",
        "perdas_pdf",
        "perdas_nao_pdf",
        "perdas_total",
        "downloads_falharam",
    ]

    lines = [
        "# Comparação auditoria de documentos",
        "",
        f"- Antes: `{args.before}`",
        f"- Depois: `{args.after}`",
        "",
        "| Métrica | Antes | Depois | Delta |",
        "|---|---:|---:|---:|",
    ]
    for k in keys:
        bv = _get(b, k)
        av = _get(a, k)
        lines.append(f"| {k} | {bv} | {av} | {av - bv} |")

    bfmt = b.get("formatos_detectados") if isinstance(b.get("formatos_detectados"), dict) else {}
    afmt = a.get("formatos_detectados") if isinstance(a.get("formatos_detectados"), dict) else {}
    lines.extend(["", "## Formatos detectados (depois)", ""])
    for k, v in sorted(afmt.items(), key=lambda kv: kv[1], reverse=True):
        bv = int(bfmt.get(k) or 0)
        lines.append(f"- {k}: {bv} -> {int(v)} (delta {int(v)-bv})")

    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
