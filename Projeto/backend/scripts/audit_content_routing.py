#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from content_routing import destination_table_for_item, infer_content_type  # noqa: E402


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _rows_from_standardized(input_dir: Path, sources: set[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for p in sorted(input_dir.glob("*_standardized.json")):
        src = p.name.replace("_standardized.json", "")
        if sources and src not in sources:
            continue
        data = _load_json(p, [])
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            continue
        for it in data:
            if isinstance(it, dict):
                row = dict(it)
                row.setdefault("fonte", row.get("fonte") or src)
                rows.append(row)
    return rows


def _rows_from_db(limit: int) -> List[Dict[str, Any]]:
    from db import supabase  # noqa: E402

    out: List[Dict[str, Any]] = []
    page = 0
    size = 1000
    while True:
        if limit and len(out) >= limit:
            return out[:limit]
        r = supabase.table("edital").select("*").range(page * size, page * size + size - 1).execute()
        chunk = r.data or []
        if not chunk:
            break
        out.extend([x for x in chunk if isinstance(x, dict)])
        if len(chunk) < size:
            break
        page += 1
    return out[:limit] if limit else out


def _example(row: Dict[str, Any], destination: str) -> Dict[str, Any]:
    ex = row.get("extras") if isinstance(row.get("extras"), dict) else {}
    return {
        "destination_table": destination,
        "content_type": infer_content_type(row),
        "fonte": row.get("fonte") or row.get("fonte_recurso"),
        "titulo": str(row.get("titulo") or "")[:240],
        "link": str(row.get("link") or "")[:500],
        "tipo_oportunidade": row.get("tipo_oportunidade") or ex.get("tipo_oportunidade"),
        "tipo_recurso": row.get("tipo_recurso") or ex.get("tipo_recurso"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Audita roteamento de conteudo: edital/noticia/pesquisa.")
    ap.add_argument("--input-dir", default="audit_reports_retransform/standardized")
    ap.add_argument("--sources", default="")
    ap.add_argument("--db", action="store_true", help="Audita public.edital no Supabase em vez de arquivos standardized.")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--output-dir", default="audit_reports_content_routing")
    args = ap.parse_args()

    sources = {s.strip().lower() for s in args.sources.split(",") if s.strip()}
    if args.db:
        env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
        if env not in ("staging", "local"):
            raise SystemExit("Defina EDITALFINDER_ENV=staging/local para auditar DB.")
        rows = _rows_from_db(args.limit)
        source_label = "db:public.edital"
    else:
        input_dir = (ROOT / args.input_dir).resolve() if not Path(args.input_dir).is_absolute() else Path(args.input_dir)
        rows = _rows_from_standardized(input_dir, sources)
        if args.limit:
            rows = rows[: args.limit]
        source_label = str(input_dir)

    counts: Counter[str] = Counter()
    by_source: Dict[str, Counter[str]] = {}
    non_edital_examples: List[Dict[str, Any]] = []
    for row in rows:
        dest = destination_table_for_item(row)
        counts[dest] += 1
        src = str(row.get("fonte") or row.get("fonte_recurso") or "").strip().lower() or "desconhecida"
        by_source.setdefault(src, Counter())[dest] += 1
        if dest != "edital" and len(non_edital_examples) < 200:
            non_edital_examples.append(_example(row, dest))

    out_dir = (ROOT / args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": source_label,
        "rows_total": len(rows),
        "destination_counts": dict(counts),
        "non_edital_total": counts.get("noticia", 0) + counts.get("pesquisa", 0),
    }
    by_source_json = [
        {"fonte": src, "destination_counts": dict(counter)}
        for src, counter in sorted(by_source.items())
    ]
    (out_dir / "content_routing_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "content_routing_by_source.json").write_text(json.dumps(by_source_json, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "content_routing_non_edital_examples.json").write_text(
        json.dumps(non_edital_examples, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = [
        "# Auditoria de roteamento de conteudo",
        "",
        f"- Origem: `{source_label}`",
        f"- Registros avaliados: **{len(rows)}**",
        f"- Editais: **{counts.get('edital', 0)}**",
        f"- Noticias: **{counts.get('noticia', 0)}**",
        f"- Pesquisas: **{counts.get('pesquisa', 0)}**",
        "",
        "## Exemplos nao-edital",
        "",
    ]
    for ex in non_edital_examples[:40]:
        md.append(f"- `{ex['destination_table']}` | {ex.get('fonte')}: {ex.get('titulo')} — {ex.get('link')}")
    (out_dir / "content_routing_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

