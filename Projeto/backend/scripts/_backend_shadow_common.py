"""Utilitários compartilhados — tabela sombra Backend 7."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from opportunity_enricher import ENRICHMENT_VERSION, enrich_opportunity_record

SHADOW_TABLE_NAME = "editais_backend_enrichment_shadow"

SHADOW_PAYLOAD_KEYS: Tuple[str, ...] = (
    "id_edital",
    "prazo_data",
    "prazo_raw",
    "prazo_status",
    "prazo_confidence",
    "prazo_source_field",
    "tipo_registro",
    "kind_confidence",
    "modalidade_normalizada",
    "modalidade_label",
    "modalidade_confidence",
    "escopo_geografico",
    "escopo_confidence",
    "fonte_normalizada",
    "pais_origem",
    "source_scope",
    "area_tematica_normalizada",
    "area_tematica_label",
    "area_tematica_confidence",
    "area_tematica_secondary",
    "qualidade_flags",
    "backend_enrichment",
    "enrichment_version",
)

SHADOW_WRITE_ENV = "EDITALFINDER_ALLOW_SHADOW_WRITE"


def shadow_write_allowed() -> bool:
    return os.getenv(SHADOW_WRITE_ENV, "").strip().lower() in ("1", "true", "yes", "on")


def _as_json_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def build_shadow_payload(record: Dict[str, Any]) -> Dict[str, Any]:
    """Gera uma linha para editais_backend_enrichment_shadow."""
    enriched = enrich_opportunity_record(record)
    be = enriched.get("extras", {}).get("backend_enrichment") or {}

    payload: Dict[str, Any] = {
        "id_edital": record.get("id_edital"),
        "prazo_data": enriched.get("prazo_data"),
        "prazo_raw": enriched.get("prazo_raw"),
        "prazo_status": enriched.get("prazo_status"),
        "prazo_confidence": enriched.get("prazo_confidence"),
        "prazo_source_field": enriched.get("prazo_source_field"),
        "tipo_registro": enriched.get("tipo_registro"),
        "kind_confidence": enriched.get("kind_confidence"),
        "modalidade_normalizada": enriched.get("modalidade_normalizada"),
        "modalidade_label": enriched.get("modalidade_label"),
        "modalidade_confidence": enriched.get("modalidade_confidence"),
        "escopo_geografico": enriched.get("escopo_geografico"),
        "escopo_confidence": enriched.get("escopo_confidence"),
        "fonte_normalizada": enriched.get("fonte_normalizada"),
        "pais_origem": enriched.get("pais_origem"),
        "source_scope": enriched.get("source_scope"),
        "area_tematica_normalizada": enriched.get("area_tematica_normalizada"),
        "area_tematica_label": enriched.get("area_tematica_label"),
        "area_tematica_confidence": enriched.get("area_tematica_confidence"),
        "area_tematica_secondary": _as_json_list(enriched.get("area_tematica_secondary")),
        "qualidade_flags": _as_json_list(enriched.get("qualidade_flags")),
        "backend_enrichment": be,
        "enrichment_version": ENRICHMENT_VERSION,
    }
    return payload


def _row_preview(rec: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id_edital": payload.get("id_edital"),
        "titulo": (rec.get("titulo") or "")[:100],
        "fonte_recurso": rec.get("fonte_recurso") or rec.get("fonte"),
    }


def analyze_shadow_batch(
    records: List[Dict[str, Any]],
    payloads: List[Dict[str, Any]],
    *,
    review_limit: int = 500,
) -> Dict[str, Any]:
    low_confidence_rows: List[Dict[str, Any]] = []
    risky_kind_changes: List[Dict[str, Any]] = []
    risky_area_changes: List[Dict[str, Any]] = []
    deadline_low_confidence: List[Dict[str, Any]] = []

    for rec, payload in zip(records, payloads):
        preview = _row_preview(rec, payload)
        low_flags = [
            k
            for k, v in (
                ("prazo_confidence", payload.get("prazo_confidence")),
                ("kind_confidence", payload.get("kind_confidence")),
                ("area_tematica_confidence", payload.get("area_tematica_confidence")),
                ("modalidade_confidence", payload.get("modalidade_confidence")),
                ("escopo_confidence", payload.get("escopo_confidence")),
            )
            if v == "baixa"
        ]
        if low_flags and len(low_confidence_rows) < review_limit:
            low_confidence_rows.append({**preview, "low_confidence_fields": low_flags, "payload": payload})

        if payload.get("prazo_confidence") == "baixa" and len(deadline_low_confidence) < review_limit:
            deadline_low_confidence.append(
                {
                    **preview,
                    "prazo_status": payload.get("prazo_status"),
                    "prazo_raw": payload.get("prazo_raw"),
                    "prazo_data": payload.get("prazo_data"),
                }
            )

        new_kind = payload.get("tipo_registro")
        if new_kind in ("noticia", "pesquisa", "concurso") and len(risky_kind_changes) < review_limit:
            risky_kind_changes.append(
                {
                    **preview,
                    "tipo_registro_novo": new_kind,
                    "kind_confidence": payload.get("kind_confidence"),
                    "qualidade_flags": payload.get("qualidade_flags"),
                }
            )

        area_conf = payload.get("area_tematica_confidence")
        area_key = payload.get("area_tematica_normalizada")
        if (area_conf == "baixa" or area_key == "sem_classificacao") and len(risky_area_changes) < review_limit:
            risky_area_changes.append(
                {
                    **preview,
                    "area_tematica_label": payload.get("area_tematica_label"),
                    "area_tematica_normalizada": area_key,
                    "area_tematica_confidence": area_conf,
                    "secondary": payload.get("area_tematica_secondary"),
                }
            )

    return {
        "low_confidence_rows": low_confidence_rows,
        "risky_kind_changes": risky_kind_changes,
        "risky_area_changes": risky_area_changes,
        "deadline_low_confidence": deadline_low_confidence,
    }


def field_coverage(payloads: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for col in SHADOW_PAYLOAD_KEYS:
        if col == "id_edital":
            continue
        n = 0
        for p in payloads:
            v = p.get(col)
            if v not in (None, "", [], {}):
                n += 1
        counts[col] = n
    return counts


def write_shadow_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Upsert na tabela sombra. Exige EDITALFINDER_ALLOW_SHADOW_WRITE=true.
    Nunca escreve em public.edital.
    """
    if not shadow_write_allowed():
        raise PermissionError(
            f"Escrita bloqueada. Defina {SHADOW_WRITE_ENV}=true para gravar na tabela sombra."
        )
    if not rows:
        return {"written": 0, "table": SHADOW_TABLE_NAME}

    import db  # noqa: WPS433

    if not db.supabase:
        raise RuntimeError("Supabase não configurado.")

    now = datetime.now(timezone.utc).isoformat()
    batch: List[Dict[str, Any]] = []
    for row in rows:
        if not row.get("id_edital"):
            continue
        item = {k: row[k] for k in SHADOW_PAYLOAD_KEYS if k in row}
        item["updated_at"] = now
        batch.append(item)

    written = 0
    chunk = 100
    for i in range(0, len(batch), chunk):
        part = batch[i : i + chunk]
        db.supabase.table(SHADOW_TABLE_NAME).upsert(part, on_conflict="id_edital").execute()
        written += len(part)

    return {"written": written, "table": SHADOW_TABLE_NAME}


def load_shadow_rows_from_db(
    id_editais: Optional[List[Any]] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    import db  # noqa: WPS433

    if not db.supabase:
        raise RuntimeError("Supabase não configurado.")

    cols = ", ".join(SHADOW_PAYLOAD_KEYS)
    if id_editais:
        resp = db.supabase.table(SHADOW_TABLE_NAME).select(cols).in_("id_edital", id_editais).execute()
        return resp.data or []

    rows: List[Dict[str, Any]] = []
    offset = 0
    page = 500
    while True:
        end = offset + page - 1
        q = db.supabase.table(SHADOW_TABLE_NAME).select(cols).range(offset, end)
        resp = q.execute()
        part = resp.data or []
        if not part:
            break
        rows.extend(part)
        if limit and len(rows) >= limit:
            return rows[:limit]
        if len(part) < page:
            break
        offset += page
    return rows
