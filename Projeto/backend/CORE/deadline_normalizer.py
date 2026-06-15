"""
Normalização central de prazos para registros edital (Backend 1 / 10.1D).

Fonte única para scripts de auditoria e futura integração no transformer/view.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from date_parser import (
    REJECT_CONTEXT_PATTERNS,
    extract_deadline_from_text_enriched,
    normalize_date_str,
)

PrazoStatus = str
Confidence = str

# Campos nunca usados como prazo de submissão
PUBLICATION_FIELD_KEYS = frozenset(
    {
        "data_publicacao",
        "posted_date",
        "postedDate",
        "post_date",
        "openDate",
        "open_date",
        "data_abertura",
        "inscricoes_inicio",
        "inicio_inscricao",
    }
)

# archiveDate só com contexto explícito (prioridade baixa)
ARCHIVE_FIELD_KEYS = frozenset({"archiveDate", "archive_date"})

# Prioridade: menor número = preferido
PRIORITY_FIELD_CANDIDATES: List[Tuple[str, int, Confidence]] = [
    ("full_application_deadline", 1, "alta"),
    ("application_deadline", 2, "alta"),
    ("applicationDeadline", 3, "alta"),
    ("proposal_deadline", 4, "alta"),
    ("prazo_envio", 5, "alta"),
    ("fim_inscricao", 6, "alta"),
    ("closeDate", 7, "alta"),
    ("close_date", 8, "alta"),
    ("opportunityCloseDate", 9, "alta"),
    ("closingDate", 10, "alta"),
    ("closing_date", 11, "alta"),
    ("applicationDueDate", 12, "alta"),
    ("application_due_date", 13, "alta"),
    ("submission_deadline", 14, "alta"),
    ("prazo", 15, "alta"),
    ("prazo_envio_raw", 16, "alta"),
    ("fim_inscricao_raw", 17, "alta"),
    ("data_limite", 18, "alta"),
    ("validade_data", 19, "alta"),
    ("validade", 20, "media"),
    ("deadline", 21, "media"),
    ("due_date", 22, "media"),
    ("response_deadline", 23, "media"),
    ("prazo_final", 24, "media"),
    ("encerramento", 25, "media"),
    ("data_encerramento", 26, "media"),
    ("data_fim", 27, "media"),
    ("data_fim_inscricao", 28, "media"),
    ("concept_paper_deadline", 29, "media"),
    ("grants_close_date", 30, "alta"),
    ("archiveDate", 40, "baixa"),
    ("archive_date", 41, "baixa"),
]

EN_SOURCES = (
    "grants.gov",
    "doe",
    "arpa",
    "nsf",
    "nih",
    "nasa",
    "darpa",
    "eureka",
    "erc",
    "ukri",
    "dod",
    "sbir",
    "sttr",
    "horizon",
    "nato",
    "iarpa",
)

BR_SOURCES = (
    "bndes",
    "cnpq",
    "fapesp",
    "fapesc",
    "finep",
    "capes",
    "faperj",
    "fapemig",
    "badesul",
    "bdmg",
    "bnb",
    "embrapii",
    "amazul",
    "aneel",
    "senai",
)


@dataclass(order=True)
class DeadlineCandidate:
    priority: int
    confidence_rank: int
    iso_date: str = field(compare=False)
    raw: str = field(compare=False, default="")
    source_field: str = field(compare=False, default="")
    confidence: Confidence = field(compare=False, default="media")
    reason: str = field(compare=False, default="")
    origin: str = field(compare=False, default="field")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.iso_date,
            "confidence": self.confidence,
            "source": self.origin,
            "reason": self.reason,
            "source_field": self.source_field,
            "raw": self.raw,
        }


def _confidence_rank(conf: Confidence) -> int:
    return {"alta": 0, "media": 1, "baixa": 2, "nenhuma": 3}.get(conf, 2)


def infer_locale_from_source(source: Optional[str]) -> str:
    s = (source or "").lower()
    if any(h in s for h in EN_SOURCES):
        return "en_US"
    if any(h in s for h in BR_SOURCES):
        return "pt_BR"
    return "pt_BR"


def parse_deadline_date(
    value: Any,
    *,
    locale_hint: Optional[str] = None,
    source: Optional[str] = None,
    source_field: str = "",
) -> Optional[Dict[str, Any]]:
    """
    Parse robusto de data de prazo.

    Retorna dict com date (ISO), confidence, source, reason — ou None.
    """
    locale = locale_hint or infer_locale_from_source(source)
    if value is None:
        return None
    if isinstance(value, (date, datetime)):
        d = value.date() if isinstance(value, datetime) else value
        if 2000 <= d.year <= 2035:
            return {
                "date": d.isoformat(),
                "confidence": "alta",
                "source": "field",
                "reason": f"campo_estruturado:{source_field or 'date'}",
            }
        return None

    s = str(value).strip()
    if not s:
        return None
    if re.search(r"no\s+closing\s+date|forecasted|^\s*tbd\s*$", s, re.I):
        return None

    iso = normalize_date_str(s, locale=locale)
    if not iso:
        return None

    conf: Confidence = "alta" if source_field in (
        "full_application_deadline",
        "application_deadline",
        "closeDate",
        "close_date",
        "prazo_envio",
        "fim_inscricao",
    ) else "media"
    return {
        "date": iso,
        "confidence": conf,
        "source": "field",
        "reason": f"parse:{source_field or 'valor'}",
    }


def _today() -> date:
    return date.today()


def _get_nested(record: Dict[str, Any], key: str) -> Tuple[Any, Optional[str]]:
    if key in record and record[key] not in (None, ""):
        return record[key], key
    extras = record.get("extras")
    if isinstance(extras, dict) and extras.get(key) not in (None, ""):
        return extras.get(key), f"extras.{key}"
    return None, None


def _record_source_name(record: Dict[str, Any]) -> str:
    return str(
        record.get("fonte_recurso")
        or record.get("fonte")
        or record.get("fonte_normalizada")
        or ""
    )


def _context_rejected(ctx: str) -> bool:
    low = ctx.lower()
    return any(re.search(p, low, re.I) for p in REJECT_CONTEXT_PATTERNS)


def _extract_us_nofo_dates(text: str) -> List[str]:
    """Datas M/D/YYYY em linha NOFO (DOE/ARPA-E)."""
    dates: List[str] = []
    m = re.search(r"Notice Of Funding Opportunity \(NOFO\)\s+(.+?)(?:\n|$)", text, re.I)
    if not m:
        return dates
    line = m.group(1)
    for dm in re.finditer(r"(\d{1,2}/\d{1,2}/\d{4})", line):
        iso = normalize_date_str(dm.group(1), locale="en_US")
        if iso:
            dates.append(iso)
    return dates


def _extract_doe_nofo_candidate(text: str) -> Optional[DeadlineCandidate]:
    m = re.search(r"Notice Of Funding Opportunity \(NOFO\)\s+(.+?)(?:\n|$)", text, re.I)
    if not m:
        return None
    line = m.group(1)
    dates = _extract_us_nofo_dates(text)
    if not dates:
        return None
    has_tbd = bool(re.search(r"\bTBD\b", line, re.I))
    if len(dates) >= 2:
        chosen = dates[-1]
        return DeadlineCandidate(
            priority=8,
            confidence_rank=0,
            iso_date=chosen,
            raw=line[:120],
            source_field="nofo_line",
            confidence="alta",
            reason="doe_nofo:prefer_full_application_date",
            origin="profile",
        )
    if len(dates) == 1 and not has_tbd:
        return DeadlineCandidate(
            priority=12,
            confidence_rank=1,
            iso_date=dates[0],
            raw=line[:120],
            source_field="nofo_line",
            confidence="media",
            reason="doe_nofo:single_date",
            origin="profile",
        )
    if has_tbd:
        return None
    return None


def _extract_grants_close_explanation_reject(record: Dict[str, Any]) -> bool:
    extras = record.get("extras")
    if not isinstance(extras, dict):
        return False
    expl = str(extras.get("closeDateExplanation") or extras.get("close_date_explanation") or "")
    return bool(re.search(r"no\s+closing\s+date|forecasted", expl, re.I))


def extract_deadline_from_known_fields(record: Dict[str, Any]) -> List[DeadlineCandidate]:
    locale = infer_locale_from_source(_record_source_name(record))
    found: List[DeadlineCandidate] = []
    seen_iso: set = set()

    for field_name, priority, conf in PRIORITY_FIELD_CANDIDATES:
        if field_name in PUBLICATION_FIELD_KEYS:
            continue
        val, source_field = _get_nested(record, field_name)
        if val is None or val == "":
            continue
        if field_name in ARCHIVE_FIELD_KEYS:
            has_close = any(_get_nested(record, k)[0] for k in ("closeDate", "close_date", "prazo_envio", "fim_inscricao"))
            if has_close:
                continue
            blob = " ".join(
                str(record.get(k) or "")
                for k in ("titulo", "descricao")
            )
            extras = record.get("extras")
            if isinstance(extras, dict):
                blob += " " + str(extras.get("closeDateExplanation") or "")
            if not re.search(r"close|deadline|closing", blob, re.I):
                continue
        parsed = parse_deadline_date(val, locale_hint=locale, source=_record_source_name(record), source_field=field_name)
        if not parsed:
            continue
        iso = parsed["date"]
        if iso in seen_iso:
            continue
        seen_iso.add(iso)
        found.append(
            DeadlineCandidate(
                priority=priority,
                confidence_rank=_confidence_rank(conf),
                iso_date=iso,
                raw=str(val)[:120],
                source_field=source_field or field_name,
                confidence=conf,
                reason=parsed.get("reason") or f"campo:{field_name}",
                origin="field",
            )
        )
    return found


def extract_deadline_from_structured_metadata(record: Dict[str, Any]) -> List[DeadlineCandidate]:
    """Campos aninhados / aliases Grants.gov em extras."""
    found: List[DeadlineCandidate] = []
    extras = record.get("extras")
    if not isinstance(extras, dict):
        return found
    locale = infer_locale_from_source(_record_source_name(record))
    nested_keys = (
        "closeDate",
        "close_date",
        "opportunityCloseDate",
        "applicationDeadline",
        "grants_close_date",
        "full_application_deadline",
        "concept_paper_deadline",
        "submission_deadline",
        "deadline_source_field",
    )
    for key in nested_keys:
        val = extras.get(key)
        if not val:
            continue
        if key == "deadline_source_field":
            continue
        parsed = parse_deadline_date(val, locale_hint=locale, source=_record_source_name(record), source_field=key)
        if parsed:
            prio = 7 if "close" in key.lower() else 14
            found.append(
                DeadlineCandidate(
                    priority=prio,
                    confidence_rank=0,
                    iso_date=parsed["date"],
                    raw=str(val)[:120],
                    source_field=f"extras.{key}",
                    confidence="alta",
                    reason=f"extras:{key}",
                    origin="field",
                )
            )
    return found


def extract_deadline_from_title(record: Dict[str, Any]) -> List[DeadlineCandidate]:
    locale = infer_locale_from_source(_record_source_name(record))
    titulo = str(record.get("titulo") or "")
    iso, field_name, raw = extract_deadline_from_text_enriched(titulo, locale=locale)
    if not iso:
        return []
    return [
        DeadlineCandidate(
            priority=25,
            confidence_rank=2,
            iso_date=iso,
            raw=raw or titulo[:120],
            source_field=field_name or "titulo",
            confidence="baixa",
            reason="extraido_titulo",
            origin="title",
        )
    ]


def extract_deadline_from_description(record: Dict[str, Any]) -> List[DeadlineCandidate]:
    locale = infer_locale_from_source(_record_source_name(record))
    parts = [
        record.get("descricao"),
        record.get("objetivo"),
        record.get("resumo"),
    ]
    extras = record.get("extras")
    if isinstance(extras, dict):
        for k in ("descricao_longa", "full_text", "texto", "body", "closeDateExplanation"):
            parts.append(extras.get(k))
    blob = "\n".join(str(p) for p in parts if p)
    if len(blob) < 15:
        return []

    found: List[DeadlineCandidate] = []

    # Perfil DOE/ARPA-E
    src = _record_source_name(record).lower()
    if "arpa" in src or "doe" in src:
        nofo = _extract_doe_nofo_candidate(blob)
        if nofo:
            found.append(nofo)

    iso, field_name, raw = extract_deadline_from_text_enriched(blob, locale=locale)
    if iso:
        conf: Confidence = "media" if field_name and "deadline" in field_name else "baixa"
        prio = 18 if conf == "media" else 28
        found.append(
            DeadlineCandidate(
                priority=prio,
                confidence_rank=_confidence_rank(conf),
                iso_date=iso,
                raw=raw or blob[:120],
                source_field=field_name or "texto_derivado",
                confidence=conf,
                reason="extraido_descricao",
                origin="text",
            )
        )
    return found


def reject_publication_dates(candidates: List[DeadlineCandidate], record: Dict[str, Any]) -> List[DeadlineCandidate]:
    pub = record.get("data_publicacao")
    pub_iso = None
    if pub:
        pub_iso = normalize_date_str(str(pub), locale=infer_locale_from_source(_record_source_name(record)))
    out: List[DeadlineCandidate] = []
    for c in candidates:
        if pub_iso and c.iso_date == pub_iso and c.origin in ("text", "title"):
            continue
        if c.raw and _context_rejected(c.raw):
            continue
        out.append(c)
    return out


def reject_result_dates(candidates: List[DeadlineCandidate], record: Dict[str, Any]) -> List[DeadlineCandidate]:
    combined = " ".join(
        str(record.get(k) or "")
        for k in ("titulo", "descricao")
    ).lower()
    if not re.search(r"\bresultado\b", combined):
        return candidates
    return [c for c in candidates if c.origin == "field" or "prazo" in c.reason or "deadline" in c.reason]


def choose_best_deadline(candidates: List[DeadlineCandidate], *, source: str = "") -> Optional[DeadlineCandidate]:
    if not candidates:
        return None
    # full_application > application > proposal > submission > close
    type_boost = {
        "full_application_deadline": -5,
        "application_deadline": -4,
        "proposal_deadline": -3,
        "submission_deadline": -2,
        "close_date": -1,
        "closeDate": -1,
        "nofo_line": -2,
    }
    adjusted: List[DeadlineCandidate] = []
    for c in candidates:
        boost = 0
        for key, delta in type_boost.items():
            if key in (c.source_field or "") or key in (c.reason or ""):
                boost = min(boost, delta)
        adjusted.append(
            DeadlineCandidate(
                priority=c.priority + boost,
                confidence_rank=c.confidence_rank,
                iso_date=c.iso_date,
                raw=c.raw,
                source_field=c.source_field,
                confidence=c.confidence,
                reason=c.reason,
                origin=c.origin,
            )
        )
    return sorted(adjusted)[0]


def _status_from_iso(iso: str, ref: Optional[date] = None) -> PrazoStatus:
    ref = ref or _today()
    try:
        d = date.fromisoformat(iso[:10])
    except ValueError:
        return "prazo_invalido"
    if d.year < 2000:
        return "prazo_invalido"
    days = (d - ref).days
    if days < 0:
        return "encerrado"
    if days <= 7:
        return "vencendo_7"
    if days <= 30:
        return "vencendo_30"
    return "prazo_confortavel"


def resolve_deadline_candidates(record: Dict[str, Any]) -> Tuple[Optional[DeadlineCandidate], List[str]]:
    notes: List[str] = []
    if _extract_grants_close_explanation_reject(record):
        notes.append("grants:close_explanation_sem_prazo")
        return None, notes

    candidates: List[DeadlineCandidate] = []
    candidates += extract_deadline_from_known_fields(record)
    candidates += extract_deadline_from_structured_metadata(record)
    candidates += extract_deadline_from_title(record)
    candidates += extract_deadline_from_description(record)

    candidates = reject_publication_dates(candidates, record)
    candidates = reject_result_dates(candidates, record)

    if not candidates:
        return None, notes

    best = choose_best_deadline(candidates, source=_record_source_name(record))
    if best:
        notes.append(f"escolhido:{best.source_field}")
    return best, notes


def has_useful_deadline(record: Dict[str, Any]) -> bool:
    """True quando há prazo parseável e não inválido (Backend 10.1D)."""
    dl = normalize_deadline(record)
    return bool(dl.get("prazo_data")) and dl.get("prazo_status") not in ("prazo_invalido", "sem_prazo")


def normalize_deadline(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normaliza prazo de um registro (linha edital, item transformado ou dict da view).

    Retorno padronizado para Backend 1 / futura view.
    """
    notes: List[str] = []
    best, resolve_notes = resolve_deadline_candidates(record)
    notes.extend(resolve_notes)

    prazo_data: Optional[str] = None
    prazo_raw: Optional[str] = None
    source_field: Optional[str] = None
    confidence: Confidence = "nenhuma"
    prazo_fonte: Optional[str] = None
    prazo_detectado = False

    if best:
        prazo_data = best.iso_date
        prazo_raw = best.raw
        source_field = best.source_field
        confidence = best.confidence
        prazo_fonte = best.origin
        prazo_detectado = True
        notes.append(best.reason)

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
        "prazo_detectado": prazo_detectado,
        "prazo_fonte": prazo_fonte,
        "validade_reason": notes[-1] if notes else None,
    }


def deadline_flags(prazo_status: str) -> Dict[str, bool]:
    """Flags booleanas alinhadas à proposta de view."""
    return {
        "is_aberto": prazo_status in ("vencendo_7", "vencendo_30", "prazo_confortavel"),
        "is_vencendo_7": prazo_status == "vencendo_7",
        "is_vencendo_30": prazo_status in ("vencendo_7", "vencendo_30"),
    }
