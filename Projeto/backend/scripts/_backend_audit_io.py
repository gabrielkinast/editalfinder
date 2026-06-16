"""Utilitários compartilhados para auditorias Backend 1 (somente leitura)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_records_from_json(path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        rows = raw
    elif isinstance(raw, dict) and "items" in raw:
        rows = raw["items"]
    else:
        rows = [raw]
    if limit:
        return rows[:limit]
    return rows


def iter_records_from_db(
    limit: Optional[int] = None,
    page_size: int = 500,
) -> Iterator[Dict[str, Any]]:
    import db  # noqa: WPS433

    if not db.supabase:
        raise RuntimeError("Supabase não configurado. Defina SUPABASE_URL e chave em .env.staging")
    offset = 0
    n = 0
    while True:
        q = (
            db.supabase.table("edital")
            .select("*")
            .range(offset, offset + page_size - 1)
        )
        resp = q.execute()
        rows = resp.data or []
        if not rows:
            break
        for row in rows:
            yield row
            n += 1
            if limit and n >= limit:
                return
        if len(rows) < page_size:
            break
        offset += page_size


def _norm_fonte(s: str) -> str:
    return (s or "").strip().lower().replace(".", "").replace(" ", "_")


SOURCE_FILTER_ALIASES: Dict[str, Tuple[str, ...]] = {
    "grants_gov": ("grants.gov", "grants_gov", "grants gov"),
    "bndes": ("bndes",),
    "doe_arpae": ("doe_arpae", "arpa-e", "arpa e", "doe arpa"),
}


def filter_records_by_source(
    records: List[Dict[str, Any]],
    source: Optional[str],
) -> List[Dict[str, Any]]:
    """Filtra por chave lógica (ex.: grants_gov) ou substring em fonte_recurso."""
    if not source:
        return records
    key = source.strip().lower()
    aliases = SOURCE_FILTER_ALIASES.get(key, (key,))
    out: List[Dict[str, Any]] = []
    for rec in records:
        fonte = str(rec.get("fonte_recurso") or rec.get("fonte") or "")
        norm = _norm_fonte(fonte)
        if any(a.replace(".", "").replace(" ", "_") in norm or a in fonte.lower() for a in aliases):
            out.append(rec)
    return out


def load_records(
    *,
    from_db: bool = False,
    input_path: Optional[Path] = None,
    limit: Optional[int] = None,
    source: Optional[str] = None,
) -> List[Dict[str, Any]]:
    if from_db:
        rows = list(iter_records_from_db(limit=limit))
        return filter_records_by_source(rows, source)
    if input_path and input_path.exists():
        rows = load_records_from_json(input_path, limit=limit)
        return filter_records_by_source(rows, source)
    return []


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
