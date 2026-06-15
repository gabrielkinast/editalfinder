"""
Recrawl/enriquecimento DOE_ARPAE (Backend 10.2C) — sem scraping agressivo.

Extrai deadlines estruturados de texto já disponível (listagem/NOFO inline).
"""
from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional

from date_parser import EN_TEXT_DEADLINE_PATTERNS, normalize_date_str
from deadline_backfill import DOE_DEADLINE_KEYS

DOE_RECrawl_VERSION = "doe_arpae_recrawl_10.2c"
_NOFO_RE = re.compile(
    r"Notice Of Funding Opportunity \(NOFO\)\s+(.+?)(?:\n|$)",
    re.I,
)
_PUBLICATION_MARKERS = re.compile(
    r"\b(published\s+on|publication\s+date|issued\s+on|release\s+date|posted\s+on)\b",
    re.I,
)


def _blob_from_item(item: Dict[str, Any]) -> str:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    parts = [
        str(item.get("titulo") or ""),
        str(item.get("descricao") or ""),
        str(item.get("objetivo") or ""),
        str(ex.get("nofo_text") or ""),
        str(ex.get("pdf_texto_extraido") or ""),
    ]
    return "\n".join(parts)


def _parse_nofo_segment(text: str) -> Dict[str, Any]:
    """Detecta NOFO com duas datas, TBD ou data única."""
    m = _NOFO_RE.search(text)
    if not m:
        return {}
    line = m.group(1)
    has_tbd = bool(re.search(r"\bTBD\b", line, re.I))
    dates: List[str] = []
    for dm in re.finditer(r"(\d{1,2}/\d{1,2}/\d{4})", line):
        iso = normalize_date_str(dm.group(1), locale="en_US")
        if iso:
            dates.append(iso)
    out: Dict[str, Any] = {"nofo_line": line[:200]}
    if has_tbd and len(dates) < 2:
        out["nofo_tbd"] = True
    if len(dates) >= 2:
        out["nofo_two_dates"] = True
        out["nofo_first_date"] = dates[0]
        out["nofo_second_date"] = dates[-1]
    elif len(dates) == 1 and not has_tbd:
        out["nofo_single_date"] = dates[0]
    return out


def extract_structured_deadlines_from_text(text: str) -> Dict[str, str]:
    """Extrai campos estruturados de deadline do texto (sem inventar prazo)."""
    found: Dict[str, str] = {}
    if not text or not text.strip():
        return found

    for pattern, field_name in EN_TEXT_DEADLINE_PATTERNS:
        if field_name in found:
            continue
        m = re.search(pattern, text, re.I)
        if not m:
            continue
        raw = m.group(1)
        if _PUBLICATION_MARKERS.search(raw):
            continue
        iso = normalize_date_str(raw, locale="en_US")
        if iso:
            found[field_name] = iso

    nofo = _parse_nofo_segment(text)
    if nofo.get("nofo_two_dates"):
        found.setdefault("full_application_deadline", nofo["nofo_second_date"])
        found.setdefault("concept_paper_deadline", nofo["nofo_first_date"])
    elif nofo.get("nofo_single_date") and "full_application_deadline" not in found:
        found.setdefault("application_deadline", nofo["nofo_single_date"])

    return found


def enrich_doe_arpae_recrawl_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enriquece item com deadlines estruturados em extras/top-level.
    Preserva URLs de detalhe e snippet NOFO; não faz fetch externo.
    """
    out = copy.deepcopy(item)
    ex = out.get("extras")
    if not isinstance(ex, dict):
        ex = {}
        out["extras"] = ex

    blob = _blob_from_item(out)
    structured = extract_structured_deadlines_from_text(blob)

    for key in DOE_DEADLINE_KEYS:
        existing = ex.get(key) or out.get(key)
        if existing and not structured.get(key):
            parsed = normalize_date_str(str(existing), locale="en_US")
            if parsed:
                structured[key] = parsed

    nofo = _parse_nofo_segment(blob)
    if nofo.get("nofo_line"):
        ex["nofo_text"] = nofo["nofo_line"]
    if nofo.get("nofo_tbd"):
        ex["nofo_tbd"] = True
    if nofo.get("nofo_two_dates"):
        ex["nofo_two_dates"] = True

    for key, iso in structured.items():
        ex[key] = iso
        out[key] = iso
        if key in ("full_application_deadline", "application_deadline", "submission_deadline"):
            if not out.get("fim_inscricao"):
                if key == "full_application_deadline" or (
                    key != "concept_paper_deadline" and not ex.get("full_application_deadline")
                ):
                    out["fim_inscricao"] = iso

    ex["doe_arpae_recrawl_version"] = DOE_RECrawl_VERSION
    ex.setdefault("url_detalhe", ex.get("url_detalhe") or out.get("link"))
    ex.setdefault("metodo_extracao", ex.get("metodo_extracao") or "doe_arpae_recrawl_10.2c")
    return out


def stats_for_doe_recrawl_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    stats: Dict[str, Any] = {
        "total": len(items),
        "with_full_application_deadline": 0,
        "with_concept_paper_deadline": 0,
        "with_submission_application_response": 0,
        "nofo_two_dates": 0,
        "nofo_tbd": 0,
        "without_structured_deadline": 0,
        "posted_only": 0,
    }
    for it in items:
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        full_app = ex.get("full_application_deadline") or it.get("full_application_deadline")
        concept = ex.get("concept_paper_deadline") or it.get("concept_paper_deadline")
        other = any(
            ex.get(k) or it.get(k)
            for k in ("application_deadline", "submission_deadline", "response_deadline", "proposal_deadline")
        )
        has_deadline = bool(full_app or concept or other or it.get("fim_inscricao"))
        if full_app:
            stats["with_full_application_deadline"] += 1
        if concept:
            stats["with_concept_paper_deadline"] += 1
        if other:
            stats["with_submission_application_response"] += 1
        if ex.get("nofo_two_dates"):
            stats["nofo_two_dates"] += 1
        if ex.get("nofo_tbd"):
            stats["nofo_tbd"] += 1
        if not has_deadline:
            stats["without_structured_deadline"] += 1
        pub = it.get("data_publicacao") or ex.get("data_publicacao") or ex.get("posted_date")
        if pub and not has_deadline:
            stats["posted_only"] += 1
    return stats
