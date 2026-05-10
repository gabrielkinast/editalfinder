"""Texto consolidado, descrição enriquecida e merge de extras (não destrutivo)."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from data_cleaning import clean_html, clean_text
from merge_utils import merge_extras_dict, sanitize_for_postgres


def build_full_text(
    item: Dict[str, Any],
    *,
    titulo: str,
    descricao: str,
    pdf_text: Optional[str] = None,
) -> str:
    """Concatena campos textuais relevantes para extração e classificação."""
    parts: List[str] = [titulo or "", descricao or ""]
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    for v in ex.values():
        if isinstance(v, (str, int, float)) and not isinstance(v, bool):
            s = str(v).strip()
            if s and len(s) < 8000:
                parts.append(s)
    if pdf_text:
        parts.append(pdf_text)
    return clean_text(" ".join(parts))


def enrich_description(
    item: Dict[str, Any],
    *,
    listing_desc: str,
    pdf_text: Optional[str],
    programa: Optional[str],
    valor: Optional[str],
    publico_alvo: Optional[str],
    fonte: str,
    titulo: str,
) -> Tuple[str, Dict[str, Any]]:
    """
    Prioridade (primeiro texto substancial); depois qualquer fonte claramente mais longa
    (+200 chars) não substitui por mais curta (preserva riqueza).
    """
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    detalhe = item.get("descricao") or ""
    objetivo = ex.get("objetivo") or ex.get("objective") or ""
    resumo = ex.get("resumo") or ex.get("summary") or ""
    objeto = (
        ex.get("objeto")
        or ex.get("objeto_licitacao")
        or ex.get("objeto_licitação")
        or item.get("objeto")
        or ""
    )
    if isinstance(objeto, dict):
        objeto = str(objeto.get("texto") or objeto.get("descricao") or "")

    ordered = [
        ("detalhe", detalhe),
        ("objetivo", objetivo),
        ("resumo", resumo),
        ("objeto_licitacao", str(objeto)),
        ("pdf", pdf_text or ""),
        ("listagem", listing_desc or ""),
    ]
    cleaned = [(name, clean_text(clean_html(str(val or "")))) for name, val in ordered]

    chosen = ""
    for _, c in cleaned:
        if len(c) >= 60:
            chosen = c
            break
    if not chosen:
        chosen = max((c for _, c in cleaned if c), key=len, default="")

    chosen_len = len(chosen)
    for _, c in cleaned:
        if len(c) > chosen_len + 200:
            chosen = c
            chosen_len = len(c)

    extras_patch: Dict[str, Any] = {}
    longest = max((c for _, c in cleaned if c), key=len, default="")
    if longest and len(longest) > len(chosen) + 80:
        extras_patch["descricao_completa"] = longest[:50000]

    if not chosen or len(chosen) < 40:
        bits = [titulo, fonte, programa, valor, publico_alvo]
        fallback = ". ".join(str(b) for b in bits if b and str(b).strip())
        fallback = clean_text(fallback)
        if len(fallback) > len(chosen):
            chosen = fallback
            extras_patch.setdefault("descricao_fonte", "fallback_composto")

    return chosen, extras_patch


def merge_item_extras(
    *,
    crawler_extras: Dict[str, Any],
    orphan_fields: Dict[str, Any],
    enrichment_patch: Dict[str, Any],
    core_keys: frozenset,
) -> Dict[str, Any]:
    """
    extras sempre dict: merge profundo crawler → órfãos → patch de enriquecimento.
    """
    base: Dict[str, Any] = deepcopy(crawler_extras) if isinstance(crawler_extras, dict) else {}
    orphans = {k: v for k, v in orphan_fields.items() if k not in core_keys and k != "extras"}
    merged = merge_extras_dict(base, orphans)
    merged = merge_extras_dict(merged, enrichment_patch)
    return sanitize_for_postgres(merged)
