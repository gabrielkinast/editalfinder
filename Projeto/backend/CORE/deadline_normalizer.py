"""
Normalização central de prazos para registros edital (Backend 1).

Fonte única para scripts de auditoria e futura integração no transformer/view.
Reutiliza date_parser quando possível.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from date_parser import extract_deadline_from_text, normalize_date_str

PrazoStatus = str
Confidence = str

FIELD_CANDIDATES: List[Tuple[str, str, Confidence]] = [
    ("prazo_envio", "prazo_envio", "alta"),
    ("fim_inscricao", "fim_inscricao", "alta"),
    ("prazo", "prazo", "alta"),
    ("prazo_envio_raw", "prazo_envio_raw", "alta"),
    ("fim_inscricao_raw", "fim_inscricao_raw", "alta"),
    ("data_limite", "data_limite", "alta"),
    ("data_encerramento", "data_encerramento", "media"),
    ("data_fim", "data_fim", "media"),
    ("deadline", "deadline", "media"),
    ("closing_date", "closing_date", "media"),
    ("submission_deadline", "submission_deadline", "media"),
    ("due_date", "due_date", "media"),
    ("prazo_final", "prazo_final", "media"),
    ("encerramento", "encerramento", "media"),
    ("close_date", "close_date", "media"),
    ("data_fim_inscricao", "data_fim_inscricao", "media"),
]

EXTRAS_DEADLINE_KEYS = (
    "prazo",
    "deadline",
    "data_limite",
    "data_fim",
    "fim_inscricao",
    "fim_inscricao_original",
    "close_date",
    "closing_date",
    "submission_deadline",
    "due_date",
)

EN_MONTH = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def _today() -> date:
    return date.today()


def _parse_raw_value(raw: Any) -> Tuple[Optional[str], Optional[str]]:
    """Retorna (iso_date, raw_string)."""
    if raw is None:
        return None, None
    if isinstance(raw, (date, datetime)):
        d = raw.date() if isinstance(raw, datetime) else raw
        if 2000 <= d.year <= 2035:
            return d.isoformat(), d.isoformat()
        return None, str(raw)
    s = str(raw).strip()
    if not s:
        return None, None
    iso = normalize_date_str(s)
    if iso:
        return iso, s
    iso_en = _parse_english_date_phrase(s)
    if iso_en:
        return iso_en, s
    return None, s


def _parse_english_date_phrase(text: str) -> Optional[str]:
    t = text.lower().strip()
    m = re.search(
        r"(january|february|march|april|may|june|july|august|september|october|november|december|"
        r"jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{1,2}),?\s+(\d{4})",
        t,
    )
    if m:
        month_name, day, year = m.groups()
        month = EN_MONTH.get(month_name)
        if month:
            try:
                d = date(int(year), month, int(day))
                if 2000 <= d.year <= 2035:
                    return d.isoformat()
            except ValueError:
                pass
    m2 = re.search(r"(\d{1,2})\s+([a-z]{3,9})\s+(\d{4})", t)
    if m2:
        day, month_name, year = m2.groups()
        month = EN_MONTH.get(month_name)
        if month:
            try:
                d = date(int(year), month, int(day))
                if 2000 <= d.year <= 2035:
                    return d.isoformat()
            except ValueError:
                pass
    return None


def _get_nested(record: Dict[str, Any], key: str) -> Tuple[Any, Optional[str]]:
    """Retorna (valor, nome_do_campo_origem). extras.* quando o valor veio de extras."""
    if key in record and record[key] not in (None, ""):
        return record[key], key
    extras = record.get("extras")
    if isinstance(extras, dict) and extras.get(key) not in (None, ""):
        return extras.get(key), f"extras.{key}"
    return None, None


def _collect_field_candidates(record: Dict[str, Any]) -> List[Tuple[str, Any, str, Confidence]]:
    found: List[Tuple[str, Any, str, Confidence]] = []
    seen_raw: set = set()
    for field, _default_source, conf in FIELD_CANDIDATES:
        val, source_field = _get_nested(record, field)
        if val is None or val == "":
            continue
        source_field = source_field or field
        sig = str(val).strip()[:120]
        if sig in seen_raw:
            continue
        seen_raw.add(sig)
        found.append((field, val, source_field, conf))  # source_field pode ser extras.*
    extras = record.get("extras")
    if isinstance(extras, dict):
        for k in EXTRAS_DEADLINE_KEYS:
            val = extras.get(k)
            if val is None or val == "":
                continue
            sig = str(val).strip()[:120]
            if sig in seen_raw:
                continue
            seen_raw.add(sig)
            found.append((f"extras.{k}", val, f"extras.{k}", "media"))
    return found


def _status_from_iso(iso: str, ref: Optional[date] = None) -> PrazoStatus:
    ref = ref or _today()
    try:
        d = date.fromisoformat(iso[:10])
    except ValueError:
        return "prazo_invalido"
    days = (d - ref).days
    if days < 0:
        return "encerrado"
    if days <= 7:
        return "vencendo_7"
    if days <= 30:
        return "vencendo_30"
    return "prazo_confortavel"


def _extract_from_text_blob(record: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    parts = [
        record.get("titulo"),
        record.get("descricao"),
        record.get("objetivo"),
        record.get("resumo"),
    ]
    extras = record.get("extras")
    if isinstance(extras, dict):
        for k in ("descricao_longa", "full_text", "texto", "body"):
            parts.append(extras.get(k))
    blob = "\n".join(str(p) for p in parts if p)
    if len(blob) < 20:
        return None, None
    iso = extract_deadline_from_text(blob)
    if iso:
        return iso, blob[:500]
    for line in blob.splitlines()[:40]:
        iso_en = _parse_english_date_phrase(line)
        if iso_en:
            return iso_en, line[:200]
    return None, None


def normalize_deadline(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza prazo de um registro (linha edital, item transformado ou dict da view).

    Retorno padronizado para Backend 1 / futura view.
    """
    notes: List[str] = []
    candidates = _collect_field_candidates(record)

    prazo_data: Optional[str] = None
    prazo_raw: Optional[str] = None
    source_field: Optional[str] = None
    confidence: Confidence = "nenhuma"

    for _field, val, src, conf in candidates:
        iso, raw_s = _parse_raw_value(val)
        if iso:
            prazo_data = iso
            prazo_raw = raw_s
            source_field = src
            confidence = conf
            break
        if raw_s and not prazo_data:
            prazo_raw = prazo_raw or raw_s
            source_field = source_field or src
            notes.append(f"valor_nao_parseavel:{src}")

    if not prazo_data:
        iso_txt, raw_txt = _extract_from_text_blob(record)
        if iso_txt:
            prazo_data = iso_txt
            prazo_raw = raw_txt or prazo_raw
            source_field = "texto_derivado"
            confidence = "baixa"
            notes.append("extraido_de_texto")
        elif prazo_raw or candidates:
            confidence = "baixa" if prazo_raw else "nenhuma"
            if prazo_raw and not prazo_data:
                notes.append("prazo_bruto_sem_data_valida")

    if prazo_data:
        prazo_status = _status_from_iso(prazo_data)
    elif prazo_raw:
        prazo_status = "prazo_invalido"
    else:
        prazo_status = "sem_prazo"
        confidence = "nenhuma"

    situacao = str(record.get("situacao") or "").lower()
    if situacao in ("encerrado", "encerrada", "fechado", "inativo") and prazo_status == "sem_prazo":
        prazo_status = "encerrado"
        notes.append("inferido_por_situacao")

    return {
        "prazo_data": prazo_data,
        "prazo_raw": prazo_raw,
        "prazo_status": prazo_status,
        "prazo_confidence": confidence,
        "prazo_source_field": source_field,
        "prazo_notes": notes,
    }


def deadline_flags(prazo_status: str) -> Dict[str, bool]:
    """Flags booleanas alinhadas à proposta de view."""
    return {
        "is_aberto": prazo_status in ("vencendo_7", "vencendo_30", "prazo_confortavel"),
        "is_vencendo_7": prazo_status == "vencendo_7",
        "is_vencendo_30": prazo_status in ("vencendo_7", "vencendo_30"),
    }
