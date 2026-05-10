#!/usr/bin/env python3
"""
Agrega contagens de itens official_link_only / validacao acesso_limitado nos standardized JSON.

Saídas: audit_reports_access/official_link_only_summary.{json,md}
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "audit_reports_access"


def _load_list(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        return []
    return [x for x in raw if isinstance(x, dict)]


def _scan_file(path: Path, fonte: str, acc: Dict[str, Any]) -> None:
    for it in _load_list(path):
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        if ex.get("extraction_mode") == "official_link_only":
            acc["official_link_only_total"] += 1
            acc["by_source_olo"][fonte] += 1
            acc["access_reason_counts"][str(ex.get("access_reason") or "unknown")] += 1
            if len(acc["examples"]) < 40:
                acc["examples"].append(
                    {
                        "fonte": fonte,
                        "titulo": str(it.get("titulo") or "")[:200],
                        "link": it.get("link"),
                        "access_reason": ex.get("access_reason"),
                    }
                )
        if str(ex.get("validacao_status") or "") == "acesso_limitado":
            acc["access_limited_total"] += 1
            acc["by_source_access_limited"][fonte] += 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Agrega official_link_only / acesso_limitado em standardized JSON.")
    ap.add_argument(
        "--extra-dirs",
        nargs="*",
        default=[],
        help="Pastas adicionais (relativas ao repo ou absolutas) com *_standardized.json.",
    )
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    acc: Dict[str, Any] = {
        "official_link_only_total": 0,
        "access_limited_total": 0,
        "by_source_olo": Counter(),
        "by_source_access_limited": Counter(),
        "access_reason_counts": Counter(),
        "examples": [],
    }

    dirs: List[Path] = [
        ROOT / "CORE" / "transformer",
        ROOT / "audit_reports_retransform" / "standardized",
    ]
    for raw in args.extra_dirs:
        p = Path(raw)
        if not p.is_absolute():
            p = (ROOT / p).resolve()
        else:
            p = p.resolve()
        if p.is_dir():
            dirs.append(p)
    for d in dirs:
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*_standardized.json")):
            fonte = path.name.replace("_standardized.json", "").lower()
            _scan_file(path, fonte, acc)

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "official_link_only_total": acc["official_link_only_total"],
        "access_limited_total": acc["access_limited_total"],
        "official_link_only_by_source": dict(acc["by_source_olo"]),
        "access_limited_by_source": dict(acc["by_source_access_limited"]),
        "access_reason_counts": dict(acc["access_reason_counts"]),
        "access_limited_examples": acc["examples"][:25],
    }
    (OUT_DIR / "official_link_only_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Official link only / acesso limitado",
        "",
        f"- `official_link_only_total`: **{summary['official_link_only_total']}**",
        f"- `access_limited_total` (validacao_status): **{summary['access_limited_total']}**",
        "",
        "## Por fonte (official_link_only)",
        "",
    ]
    for k, v in sorted(summary["official_link_only_by_source"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## access_reason", ""])
    for k, v in sorted(summary["access_reason_counts"].items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Exemplos", ""])
    for ex in summary["access_limited_examples"][:15]:
        lines.append(f"- **{ex.get('fonte')}**: {ex.get('titulo', '')[:80]}… — `{ex.get('link')}`")
    lines.extend(
        [
            "",
            "## Readiness",
            "",
            "Se `official_link_only_total / itens_transformados >= 0.35` numa fonte (ver `retransform_by_source.json`), "
            "`build_loader_readiness.py` despromove de `pronto_para_loader` para `pronto_com_observacoes`.",
            "Fontes dependentes de link-only não devem ir a **ready** pleno sem revisão humana.",
        ]
    )
    (OUT_DIR / "official_link_only_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(OUT_DIR.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
