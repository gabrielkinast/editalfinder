#!/usr/bin/env python3
"""
Auditoria de prazos por fonte_recurso (Backend 3) — somente leitura.

Uso:
  python scripts/audit_deadline_by_source_backend.py --from-db --limit 5000
  python scripts/audit_deadline_by_source_backend.py --source "Grants.gov"
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _backend_audit_io import load_records, write_json, write_md  # noqa: E402
from deadline_normalizer import normalize_deadline  # noqa: E402

OUT_DIR = ROOT / "outputs" / "audit_deadline_by_source_backend"

SOURCE_CRAWLER_MAP = {
    "china international tendering": ("china_mofcom_tendering", "china_mofcom_tendering/main_china_mofcom_tendering.py"),
    "china international technology transfer center": ("china_mofcom_tendering", "china_mofcom_tendering/main_china_mofcom_tendering.py"),
    "fundação araucária": ("fappr", "fappr/main_fappr.py + extrair_informacoes_fappr.py"),
    "fundacao araucaria": ("fappr", "fappr/main_fappr.py + extrair_informacoes_fappr.py"),
    "grants.gov": ("grants_gov", "grants_gov/main_simpler_grants_gov.py"),
    "grants.gov (eua)": ("grants_gov", "grants_gov/main_simpler_grants_gov.py"),
}

RECOMMENDATIONS = {
    "china": "Extrair bid/tender closing date no detail HTML; flag deadline_missing_in_source se só publicação.",
    "araucaria": "Expandir regex PT + texto PDF já extraído; deadline_requires_pdf quando só link PDF.",
    "grants": "Garantir close_date ISO em fim_inscricao; não usar postedDate como prazo.",
    "default": "Revisar crawler e preencher prazo_envio_raw + extras.deadline antes do loader.",
}


def _pct(n: int, t: int) -> str:
    return f"{100 * n / t:.1f}%" if t else "0%"


def _db_has_prazo(rec: Dict[str, Any]) -> bool:
    for k in ("prazo_envio", "fim_inscricao"):
        v = rec.get(k)
        if v and str(v).strip()[:10]:
            s = str(v).strip()[:10]
            if len(s) >= 8 and s[4:5] == "-":
                return True
    return False


def _source_bucket(fonte: str) -> str:
    f = fonte.lower()
    if "china" in f or "mofcom" in f:
        return "china"
    if "araucária" in f or "araucaria" in f:
        return "araucaria"
    if "grants" in f:
        return "grants"
    return "other"


def _recommendation(fonte: str) -> str:
    return RECOMMENDATIONS.get(_source_bucket(fonte), RECOMMENDATIONS["default"])


def _crawler_for(fonte: str) -> str:
    key = fonte.strip().lower()[:80]
    for pat, (_, path) in SOURCE_CRAWLER_MAP.items():
        if pat in key or key in pat:
            return path
    return "transformer.py (genérico) / scraper da fonte"


def audit_records(records: List[Dict[str, Any]], *, source_filter: Optional[str] = None) -> Dict[str, Any]:
    by_fonte: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in records:
        fonte = str(rec.get("fonte_recurso") or rec.get("fonte") or "—")
        if source_filter and source_filter.lower() not in fonte.lower():
            continue
        by_fonte[fonte].append(rec)

    ranked: List[Dict[str, Any]] = []
    examples: Dict[str, List[Dict[str, Any]]] = {}

    for fonte, rows in sorted(by_fonte.items(), key=lambda x: -len(x[1])):
        total = len(rows)
        structured_db = 0
        text_derived = 0
        sem = 0
        field_c = Counter()
        for rec in rows:
            if _db_has_prazo(rec):
                structured_db += 1
            dl = normalize_deadline(rec)
            if dl.get("prazo_data") and not _db_has_prazo(rec):
                text_derived += 1
            if dl["prazo_status"] == "sem_prazo":
                sem += 1
            if dl.get("prazo_source_field"):
                field_c[dl["prazo_source_field"]] += 1
            ex = rec.get("extras") if isinstance(rec.get("extras"), dict) else {}
            for fk in ("deadline", "close_date", "grants_close_date", "fim_inscricao_original"):
                if ex.get(fk):
                    field_c[f"extras.{fk}"] += 1

        entry = {
            "fonte_recurso": fonte,
            "total": total,
            "com_prazo_db": structured_db,
            "sem_prazo": sem,
            "prazo_texto_derivado": text_derived,
            "pct_sem_prazo": round(100 * sem / total, 1) if total else 0,
            "top_campos_prazo": field_c.most_common(8),
            "crawler_provavel": _crawler_for(fonte),
            "recomendacao": _recommendation(fonte),
        }
        ranked.append(entry)

        ex_list = []
        for rec in rows:
            dl = normalize_deadline(rec)
            if dl["prazo_status"] in ("sem_prazo", "prazo_invalido") or (
                dl.get("prazo_confidence") == "baixa"
            ):
                if len(ex_list) < 4:
                    ex = rec.get("extras") if isinstance(rec.get("extras"), dict) else {}
                    ex_list.append(
                        {
                            "id_edital": rec.get("id_edital"),
                            "titulo": (rec.get("titulo") or "")[:100],
                            "link": (rec.get("link") or "")[:120],
                            "prazo_envio": rec.get("prazo_envio"),
                            "prazo_status": dl["prazo_status"],
                            "prazo_confidence": dl["prazo_confidence"],
                            "extras_deadline_keys": [k for k in ex if "deadline" in k.lower() or "prazo" in k.lower() or "close" in k.lower()][:12],
                        }
                    )
        if ex_list:
            examples[fonte] = ex_list

    ranked.sort(key=lambda x: (-x["sem_prazo"], -x["pct_sem_prazo"]))
    return {
        "total_records": len(records),
        "sources_count": len(ranked),
        "sources_ranked": ranked,
        "examples_by_source": examples,
    }


def build_summary_md(report: Dict[str, Any]) -> str:
    lines = [
        "# Auditoria de prazos por fonte — Backend 3",
        "",
        f"**Registros:** {report['total_records']} | **Fontes:** {report['sources_count']}",
        "",
        "## Top fontes problemáticas (sem prazo)",
        "",
        "| Fonte | Total | Com prazo BD | Sem prazo | % sem |",
        "|-------|------:|-------------:|----------:|------:|",
    ]
    for s in report["sources_ranked"][:25]:
        lines.append(
            f"| {s['fonte_recurso'][:50]} | {s['total']} | {s['com_prazo_db']} | {s['sem_prazo']} | {s['pct_sem_prazo']}% |"
        )
    lines.extend(["", "## Recomendações (top 3 foco Backend 3)", ""])
    focus = [s for s in report["sources_ranked"] if _source_bucket(s["fonte_recurso"]) in ("china", "araucaria", "grants")]
    for s in focus[:5]:
        lines.append(f"### {s['fonte_recurso']}")
        lines.append(f"- Crawler: `{s['crawler_provavel']}`")
        lines.append(f"- {s['recomendacao']}")
        lines.append("")
    lines.append("Ver `sources_ranked.json` e `examples_by_source.json`.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-db", action="store_true")
    ap.add_argument("--input", type=Path)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--source", type=str, help="Filtrar por substring em fonte_recurso")
    args = ap.parse_args()

    records = load_records(from_db=args.from_db, input_path=args.input, limit=args.limit)
    if not records:
        write_md(OUT_DIR / "summary.md", "# Sem dados")
        return 1

    report = audit_records(records, source_filter=args.source)
    write_json(OUT_DIR / "sources_ranked.json", report["sources_ranked"])
    write_json(OUT_DIR / "examples_by_source.json", report["examples_by_source"])
    write_json(OUT_DIR / "report.json", {k: v for k, v in report.items() if k != "examples_by_source"})
    write_md(OUT_DIR / "summary.md", build_summary_md(report))
    print(f"[audit_deadline_by_source] {report['sources_count']} fontes -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
