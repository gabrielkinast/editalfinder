"""
Extrator de prazo de SUBMISSÃO BNDES (Backend 10.2D hotfix / 10.2D-HOTFIX.2).

prazo_envio = envio/recebimento de propostas — nunca dúvidas, resultado ou diligência.
O bloco "Como participar" tem prioridade máxima sobre datas administrativas.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from date_parser import extract_deadline_from_text_enriched, normalize_date_str

SUBMISSION_DEADLINE_KIND = "submission_deadline"

COMO_PARTICIPAR_HEADING = "como participar"

COMO_PARTICIPAR_START_PATTERNS: Tuple[str, ...] = (
    r"como\s+participar",
    r"participa[cç][aã]o",
    r"envio\s+de\s+propostas",
    r"apresenta[cç][aã]o\s+de\s+propostas",
)

SECTION_END_MARKERS: Tuple[str, ...] = (
    r"resultado\s+final",
    r"\bresultado\b",
    r"contato",
    r"saiba\s+mais",
    r"hist[oó]rico",
    r"perguntas",
    r"d[uú]vidas",
    r"cronograma",
    r"anexos",
)

# Contextos de submissão — alta prioridade
SUBMISSION_SECTION_MARKERS = (
    r"como\s+participar",
    r"as\s+propostas\s+dever[aã]o\s+ser\s+encaminhadas",
    r"toda\s+a\s+documenta[cç][aã]o\s+necess[aá]ria\s+dever[aá]\s+ser\s+encaminhada",
    r"prazo\s+para\s+recebimento\s+das\s+propostas",
    r"prazo\s+para\s+recebimento\s+de\s+propostas",
    r"recebimento\s+de\s+propostas",
    r"envio\s+de\s+propostas",
    r"apresenta[cç][aã]o\s+de\s+propostas",
    r"portal\s+do\s+cliente",
    r"documenta[cç][aã]o\s+dever[aá]\s+ser\s+encaminhada",
)

SUBMISSION_PROXIMITY_MARKERS = (
    r"propostas?\s+dever[aã]o\s+ser\s+enviadas",
    r"documenta[cç][aã]o\s+dever[aá]\s+ser\s+encaminhada",
    r"portal\s+do\s+cliente",
    r"envio\s+das\s+propostas",
    r"recebimento\s+das\s+propostas",
    r"apresenta[cç][aã]o\s+das\s+propostas",
    r"encaminhada",
    r"submiss",
)

# Prazo único de submissão
SUBMISSION_SINGLE_DATE_PATTERNS: List[Tuple[str, str]] = [
    (
        r"(?:propostas|inscri[cç][oõ]es)\s+at[eé]\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        "bndes_propostas_ate",
    ),
    (
        r"(?:propostas|inscri[cç][oõ]es)\s+at[eé]\s+(\d{1,2}\s+de\s+[a-zA-ZçÇãõáéíóú]+\s+de\s+\d{4})",
        "bndes_propostas_ate_extenso",
    ),
    (
        r"prazo\s+para\s+recebimento\s+das\s+propostas\s*[:\s]*at[eé]\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        "bndes_recebimento_ate",
    ),
    (
        r"prazo\s+para\s+recebimento\s+de\s+propostas\s+foi\s+postergad[oa]\s+para\s+at[eé]\s+(?:as|às)\s*18h\s+(?:de\s+|do\s+dia\s+)?(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        "bndes_recebimento_postergado",
    ),
]

# Intervalo típico BNDES: fim = prazo de submissão
SUBMISSION_RANGE_PATTERNS: List[Tuple[str, str]] = [
    (
        r"a\s+partir\s+de\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})\s+at[eé]\s+(?:as|às)\s*18h\s+(?:de\s+|do\s+dia\s+)?(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        "bndes_range_apartir_ate_18h",
    ),
    (
        r"de\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})\s+at[eé]\s+(?:as|às)\s*18h\s+(?:de\s+|do\s+dia\s+)?(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        "bndes_range_de_ate_18h",
    ),
    (
        r"prazo\s+para\s+recebimento\s+das\s+propostas\s*[:\s]*de\s+(\d{1,2}[./]\d{1,2}[./]\d{2,4})\s+at[eé]\s+(?:as|às)\s*18h\s+(?:de\s+|do\s+dia\s+)?(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
        "bndes_recebimento_propostas_range",
    ),
]

SUBMISSION_ATE_18H_PATTERN = (
    r"at[eé]\s+(?:as|às)\s*18h\s+(?:de\s+|do\s+dia\s+)?(\d{1,2}[./]\d{1,2}[./]\d{2,4})",
    "bndes_ate_18h_dia",
)

# Contextos administrativos — nunca viram prazo_envio
REJECT_CONTEXT_PATTERNS: List[Tuple[str, str]] = [
    (r"resultado\s+final", "resultado_final"),
    (r"resultado\s+da\s+chamada", "resultado_chamada"),
    (r"divulga[cç][aã]o\s+do\s+resultado\s+final", "divulgacao_resultado_final"),
    (r"divulga[cç][aã]o\s+do\s+resultado", "divulgacao_resultado"),
    (r"resultado\s+de\s+primeira\s+fase", "resultado_primeira_fase"),
    (r"resultado\s+de\s+segunda\s+fase", "resultado_segunda_fase"),
    (r"convocadas\s+para\s+an[aá]lise\s+gerencial", "convocacao_analise"),
    (r"an[aá]lise\s+gerencial\s+e\s+jur[ií]dica", "analise_gerencial_juridica"),
    (r"due\s+diligence", "due_diligence"),
    (r"poder[aã]o\s+ser\s+convocadas", "convocacao_diligencia"),
    (r"convocadas\s+em\s+at[eé]", "convocacao_ate"),
    (r"convocadas\s+em\s+prazo\s+m[aá]ximo", "convocacao_prazo_maximo"),
    (r"convocadas\s+at[eé]", "convocacao_ate"),
    (r"aprova[cç][aã]o\s+(?:da\s+diretoria\s+)?at[eé]", "aprovacao_diretoria"),
    (r"prazo\s+para\s+encaminhamento\s+de\s+d[uú]vidas", "duvidas_encaminhamento"),
    (r"d[uú]vidas\s+ser[aã]o\s+respondidas\s+at[eé]", "duvidas_resposta"),
    (r"reuni[oõ]es\s+de\s+feedback", "reunioes_feedback"),
    (r"apresenta[cç][aã]o\s+ao\s+comit[eê]\s+de\s+sele[cç][aã]o", "apresentacao_comite"),
    (r"publicado\s+em", "publicado_em"),
    (r"atualizado\s+em", "atualizado_em"),
    (r"lan[cç]ou,?\s+em", "lancamento"),
    (r"lan[cç]ado,?\s+em", "lancamento"),
    (r"lan[cç]amento\s+em", "lancamento"),
]

_DATE_TOKEN = (
    r"(\d{1,2}[./]\d{1,2}[./]\d{2,4}"
    r"|\d{1,2}\s+de\s+[a-zA-ZçÇãõáéíóú]+\s+de\s+\d{4})"
)


def _parse_pt_date(raw: str) -> Optional[str]:
    if not raw:
        return None
    return normalize_date_str(raw.strip(), locale="pt_BR")


def _context_slice(text: str, start: int, end: int, *, before: int = 100, after: int = 80) -> str:
    return text[max(0, start - before) : min(len(text), end + after)]


def _is_reject_context(ctx: str) -> bool:
    low = ctx.lower()
    return any(re.search(p, low, re.I) for p, _ in REJECT_CONTEXT_PATTERNS)


def extract_bndes_section(text: str, heading: str, max_chars: int = 5000) -> str:
    """
    Isola bloco semântico por heading (ex.: "Como participar").

    Início: Como participar / Participação / Envio de propostas / etc.
    Fim provável: Resultado / Contato / Dúvidas / Cronograma / Anexos / etc.
    """
    if not text or not text.strip():
        return ""

    heading_key = heading.strip().lower()
    if heading_key == COMO_PARTICIPAR_HEADING:
        start_patterns = COMO_PARTICIPAR_START_PATTERNS
    else:
        start_patterns = (re.escape(heading.strip()),)

    best_start: Optional[int] = None
    for pattern in start_patterns:
        m = re.search(pattern, text, re.I)
        if m and (best_start is None or m.start() < best_start):
            best_start = m.start()

    if best_start is None:
        return ""

    tail = text[best_start:]
    end_rel = len(tail)
    for marker in SECTION_END_MARKERS:
        m = re.search(marker, tail[20:], re.I)
        if m:
            end_rel = min(end_rel, 20 + m.start())

    block = tail[:end_rel].strip()
    return block[:max_chars]


def _extract_como_participar_block(text: str) -> Optional[str]:
    block = extract_bndes_section(text, COMO_PARTICIPAR_HEADING)
    return block or None


def _dates_in_span(span: str) -> List[Tuple[str, str]]:
    found: List[Tuple[str, str]] = []
    for m in re.finditer(_DATE_TOKEN, span, re.I):
        iso = _parse_pt_date(m.group(1))
        if iso:
            found.append((iso, m.group(1)))
    return found


def _submission_range_end_isos(text: str) -> set[str]:
    """Datas-fim de intervalos de submissão — nunca entram em ignored_dates."""
    protected: set[str] = set()
    for pattern, _ in SUBMISSION_RANGE_PATTERNS:
        for m in re.finditer(pattern, text, re.I):
            iso = _parse_pt_date(m.group(2))
            if iso:
                protected.add(iso)
    for pattern, _ in SUBMISSION_SINGLE_DATE_PATTERNS:
        for m in re.finditer(pattern, text, re.I):
            iso = _parse_pt_date(m.group(1))
            if iso:
                protected.add(iso)
    pattern, _ = SUBMISSION_ATE_18H_PATTERN
    for m in re.finditer(pattern, text, re.I):
        iso = _parse_pt_date(m.group(1))
        if iso:
            protected.add(iso)
    return protected


def collect_bndes_ignored_dates(text: str, *, exclude_block: Optional[str] = None) -> List[Dict[str, Any]]:
    """Datas em contexto administrativo (dúvidas, resultado, diligência)."""
    ignored: List[Dict[str, Any]] = []
    seen: set[str] = set()
    protected = _submission_range_end_isos(text)
    if exclude_block:
        protected |= _submission_range_end_isos(exclude_block)

    for pattern, reason in REJECT_CONTEXT_PATTERNS:
        for m in re.finditer(pattern, text, re.I):
            ctx = _context_slice(text, m.start(), m.end(), before=0, after=120)
            for iso, raw in _dates_in_span(ctx):
                if iso in protected:
                    continue
                key = f"{iso}:{reason}"
                if key in seen:
                    continue
                seen.add(key)
                ignored.append(
                    {
                        "iso": iso,
                        "raw": raw,
                        "reason": reason,
                        "context": ctx.strip()[:160],
                    }
                )
    return ignored


def _score_submission_context(ctx: str, *, in_como_participar: bool = False) -> float:
    low = ctx.lower()
    score = 0.85
    if in_como_participar or re.search(r"como\s+participar", low, re.I):
        score = max(score, 0.99)
    for marker in SUBMISSION_SECTION_MARKERS:
        if re.search(marker, low, re.I):
            score = max(score, 0.94)
    if re.search(r"proposta|recebimento|encaminhada|submiss", low, re.I):
        score = max(score, 0.90)
    if _is_reject_context(ctx):
        return 0.0
    return score


def _has_submission_proximity(ctx: str) -> bool:
    low = ctx.lower()
    return any(re.search(p, low, re.I) for p in SUBMISSION_PROXIMITY_MARKERS)


def _candidates_from_ranges(
    text: str,
    *,
    base_confidence: float = 0.92,
    in_como_participar: bool = False,
) -> List[Tuple[str, float, str, str]]:
    out: List[Tuple[str, float, str, str]] = []
    for pattern, field in SUBMISSION_RANGE_PATTERNS:
        for m in re.finditer(pattern, text, re.I):
            end_raw = m.group(2)
            iso = _parse_pt_date(end_raw)
            if not iso:
                continue
            ctx = _context_slice(text, m.start(), m.end(), before=80, after=0)
            score = _score_submission_context(ctx, in_como_participar=in_como_participar)
            if in_como_participar:
                score = max(score, 0.99)
            else:
                score = max(score, 0.93)
            if score <= 0:
                continue
            conf = min(0.99, base_confidence + (score - 0.85) * 0.5)
            out.append((iso, conf, field, m.group(0)[:160]))
    return out


def _candidates_from_single_dates(
    text: str,
    *,
    base_confidence: float = 0.90,
    in_como_participar: bool = False,
) -> List[Tuple[str, float, str, str]]:
    out: List[Tuple[str, float, str, str]] = []
    for pattern, field in SUBMISSION_SINGLE_DATE_PATTERNS:
        for m in re.finditer(pattern, text, re.I):
            iso = _parse_pt_date(m.group(1))
            if not iso:
                continue
            ctx = _context_slice(text, m.start(), m.end(), before=40, after=0)
            score = _score_submission_context(ctx, in_como_participar=in_como_participar)
            if in_como_participar:
                score = max(score, 0.98)
            else:
                score = max(score, 0.91)
            if score <= 0:
                continue
            conf = min(0.98, base_confidence + (score - 0.85) * 0.4)
            out.append((iso, conf, field, m.group(0)[:160]))
    return out


def _candidates_from_ate_18h(
    text: str,
    *,
    base_confidence: float = 0.88,
    in_como_participar: bool = False,
) -> List[Tuple[str, float, str, str]]:
    out: List[Tuple[str, float, str, str]] = []
    pattern, field = SUBMISSION_ATE_18H_PATTERN
    for m in re.finditer(pattern, text, re.I):
        iso = _parse_pt_date(m.group(1))
        if not iso:
            continue
        ctx = _context_slice(text, m.start(), m.end(), before=120, after=0)
        if not in_como_participar and not _has_submission_proximity(ctx):
            continue
        score = _score_submission_context(ctx, in_como_participar=in_como_participar)
        if in_como_participar:
            score = max(score, 0.96)
        if score <= 0:
            continue
        conf = min(0.97, base_confidence + (score - 0.85) * 0.4)
        out.append((iso, conf, field, m.group(0)[:160]))
    return out


def _candidates_from_markers(
    text: str,
    *,
    base_confidence: float = 0.88,
    in_como_participar: bool = False,
) -> List[Tuple[str, float, str, str]]:
    out: List[Tuple[str, float, str, str]] = []
    for marker in SUBMISSION_SECTION_MARKERS:
        if marker.startswith("como"):
            continue
        for m in re.finditer(marker, text, re.I):
            ctx = _context_slice(text, m.start(), m.end(), before=10, after=160)
            if _is_reject_context(ctx):
                continue
            iso, field, raw = extract_deadline_from_text_enriched(ctx, locale="pt_BR")
            if iso and field:
                score = _score_submission_context(ctx, in_como_participar=in_como_participar)
                if in_como_participar:
                    score = max(score, 0.95)
                if score <= 0:
                    continue
                out.append((iso, min(0.97, base_confidence + (score - 0.85) * 0.4), field, raw or ctx[:120]))
    return out


def _collect_block_candidates(block: str, *, in_como_participar: bool) -> List[Tuple[str, float, str, str]]:
    candidates: List[Tuple[str, float, str, str]] = []
    base_boost = 0.96 if in_como_participar else 0.92
    candidates.extend(
        _candidates_from_ranges(block, base_confidence=base_boost, in_como_participar=in_como_participar)
    )
    candidates.extend(
        _candidates_from_single_dates(block, base_confidence=base_boost - 0.01, in_como_participar=in_como_participar)
    )
    candidates.extend(
        _candidates_from_ate_18h(block, base_confidence=base_boost - 0.02, in_como_participar=in_como_participar)
    )
    candidates.extend(
        _candidates_from_markers(block, base_confidence=base_boost - 0.03, in_como_participar=in_como_participar)
    )
    return candidates


def extract_bndes_submission_deadline(text: str) -> Dict[str, Any]:
    """
    Extrai prazo de envio/submissão de propostas BNDES.

    Retorna deadline_kind=submission_deadline somente para prazo real de proposta.
    Bloco "Como participar" vence todas as outras datas quando contém padrão de envio.
    """
    empty: Dict[str, Any] = {
        "iso": None,
        "deadline_kind": None,
        "confidence": 0.0,
        "field": None,
        "raw": None,
        "ignored_dates": [],
        "source_block": None,
    }
    if not text or not text.strip():
        return empty

    cp_block = _extract_como_participar_block(text)
    ignored = collect_bndes_ignored_dates(text, exclude_block=cp_block)
    ignored_isos = {i["iso"] for i in ignored if i.get("iso")}

    if cp_block:
        cp_candidates = _collect_block_candidates(cp_block, in_como_participar=True)
        cp_valid = [(iso, conf, field, raw) for iso, conf, field, raw in cp_candidates if iso not in ignored_isos]
        if cp_valid:
            cp_valid.sort(key=lambda x: (-x[1], x[0]))
            iso, conf, field, raw = cp_valid[0]
            return {
                "iso": iso,
                "deadline_kind": SUBMISSION_DEADLINE_KIND,
                "confidence": round(min(0.995, conf + 0.01), 3),
                "field": field,
                "raw": raw,
                "ignored_dates": ignored,
                "source_block": "como_participar",
            }

    candidates: List[Tuple[str, float, str, str]] = []
    candidates.extend(_collect_block_candidates(text, in_como_participar=False))

    search_blocks = [cp_block, text] if cp_block else [text]
    for block in search_blocks:
        if not block:
            continue
        iso_kw, field_kw, raw_kw = extract_deadline_from_text_enriched(block, locale="pt_BR")
        if iso_kw and field_kw:
            idx = block.lower().find((raw_kw or iso_kw).lower()[:8]) if raw_kw or iso_kw else -1
            ctx = _context_slice(block, max(0, idx), max(0, idx) + len(raw_kw or ""), before=80, after=0)
            score = _score_submission_context(ctx, in_como_participar=bool(cp_block and block == cp_block))
            if score > 0 and iso_kw not in ignored_isos:
                candidates.append((iso_kw, score, field_kw, raw_kw or ctx[:120]))
                break

    valid = [(iso, conf, field, raw) for iso, conf, field, raw in candidates if iso not in ignored_isos]
    if not valid:
        return {**empty, "ignored_dates": ignored}

    valid.sort(key=lambda x: (-x[1], x[0]))
    iso, conf, field, raw = valid[0]

    return {
        "iso": iso,
        "deadline_kind": SUBMISSION_DEADLINE_KIND,
        "confidence": round(conf, 3),
        "field": field,
        "raw": raw,
        "ignored_dates": ignored,
        "source_block": "full_text",
    }


def merge_bndes_text_blob(record: Dict[str, Any]) -> str:
    """Texto completo para parsing (listagem + detalhe + PDF)."""
    ex = record.get("extras") if isinstance(record.get("extras"), dict) else {}
    parts = [
        str(record.get("titulo") or ""),
        str(record.get("descricao") or ""),
        str(record.get("objetivo") or ""),
        str(ex.get("bndes_detail_text") or ""),
        str(ex.get("pdf_texto_extraido") or ""),
    ]
    return "\n".join(p for p in parts if p.strip())
