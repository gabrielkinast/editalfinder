# -*- coding: utf-8 -*-
"""Helpers partilhados — crawlers Concursos & Seleções (sem Supabase)."""
from __future__ import annotations

import re
import unicodedata
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

_RE_DATE_BR = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})\b")
# Valor monetário BR: R$ 1.719,26 | R$ 10.868,68 | R$ 15,6 mil
# Não capturar "R$ 9,5" quando for "R$ 9,5 mil" — o sufixo "mil" é tratado só em _RE_MONEY_MIL.
_RE_MONEY_FULL = re.compile(
    r"R\$\s*([\d]{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:,\d{1,2})?)(?!\s*mil\b)"
    r"(?=\s*(?:[\s,.\d]|$))",
    re.IGNORECASE,
)
_RE_MONEY_MIL = re.compile(
    r"R\$\s*(\d+(?:,\d+)?)\s*mil\b",
    re.IGNORECASE,
)
_RE_MIL_BARE = re.compile(
    r"(?:sal[aá]rios?\s+de\s+)?(?:at[eé]\s+)?R\$\s*(\d+)\s*mil\b",
    re.IGNORECASE,
)
_RE_ATE_MONEY = re.compile(
    r"at[eé]\s+R\$\s*([\d]{1,3}(?:\.\d{3})*(?:,\d{1,2})?|\d+(?:,\d{1,2})?)(?!\s*mil\b)",
    re.IGNORECASE,
)
# Contexto para separar taxa de inscrição vs remuneração (janela em torno de R$)
_CTX_LOOKBACK = 140
_CTX_LOOKAHEAD = 100
_RE_CTX_FEE = re.compile(
    r"(taxa\s*d[e']?\s*inscri|taxa\s+de\s+inscri|taxa\s+de\s+r\$|\btaxa\b.{0,55}r\$|r\$.{0,55}\btaxa\b|"
    r"valor\s*d[ao]\s*inscri|valor\s+de\s+inscri[cç]|custos?\s*d[ao]\s*inscri|"
    r"pagamento\s+d[ao]\s*inscri|pagamento\s+da\s+inscri|inscri[cç][aã]o.{0,60}r\$|r\$.{0,60}inscri[cç][aã]o|"
    r"valor\s+da\s+inscri|\bboleto\b.{0,45}r\$|r\$.{0,45}\bboleto\b|"
    r"\bcandidato\s+paga\b.{0,50}r\$|\bpaga\b.{0,50}r\$|r\$.{0,50}referentes)",
    re.IGNORECASE | re.DOTALL,
)
_RE_CTX_SAL = re.compile(
    r"(sal[aá]rios?\s+de|sal[aá]rio|remunera[cç][aã]o|vencimentos?|subs[ií]dio|ganhos|retribui[cç][aã]o|"
    r"pagamento\s+pelo\s+cargo|remunera[cç][aã]o\s+de)",
    re.IGNORECASE,
)
_RE_VAGAS = re.compile(
    r"(\d{1,2}(?:\.\d{3})+|\d{1,6})\s+vagas",
    re.IGNORECASE,
)
_RE_VAGAS_WORD = re.compile(
    r"(\d{1,2}(?:\.\d{3})+|\d{1,6})\s+vagas?\b",
    re.IGNORECASE,
)
_RE_OPORTUNIDADES = re.compile(
    r"(\d{1,2}(?:\.\d{3})+|\d{1,6})\s+oportunidades?\b",
    re.IGNORECASE,
)
_RE_VAGAS_CTX_EXCLUDE = re.compile(
    r"(?:not[ií]cias\s+relacionad|mais\s+lidas?|compartilhe|facebook|twitter|instagram|"
    r"newsletter|últimas\s+not|ultimas\s+not|deixe\s+seu\s+coment)",
    re.IGNORECASE,
)
_RE_VAGAS_CTX_INCLUDE = re.compile(
    r"(?:inscri|concurso|processo|sele[cç][aã]o|edital|oferta|disponib|total|"
    r"\bh[aá]\s+\d|\bs[aã]o\s+\d|\bexist(em|e)\s+\d|oportunidade|cargo|nível|nivel|"
    r"vaga\s+para|ofertad[ao]s?|abert[ao]s?|níveis|niveis|cadastro\s+reserva)",
    re.IGNORECASE,
)
_RE_VAGAS_CERTAME_PARA = re.compile(
    r"(?i)\b(concurso\s+público|concurso\s+publico|processo\s+seletivo|edital\b|"
    r"sele[cç][aã]o\s+pública|sele[cç][aã]o\s+publica|cadastro\s+reserva)\b",
)
_RE_CADASTRO_RESERVA = re.compile(r"cadastro\s+reserva", re.IGNORECASE)
_UFS = frozenset(
    "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()
)
_RE_INSCR_ATE = re.compile(
    r"(?:inscri[cç][aã]o|inscri[cç][oõ]es)[^\n]{0,60}?(?:até|ate)\s*:?\s*(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)
_RE_PROVA = re.compile(
    r"(?:prova|exame|etapa\s*escrita)[^\n]{0,50}?(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)


def normalize_text(s: Any) -> str:
    if s is None:
        return ""
    t = unicodedata.normalize("NFKC", str(s))
    t = re.sub(r"\s+", " ", t).strip()
    return t


def parse_date_br(text: Any) -> Optional[str]:
    """
    Primeira data dd/mm/aaaa encontrada no texto → 'YYYY-MM-DD' ou None.
    """
    if text is None:
        return None
    m = _RE_DATE_BR.search(str(text))
    if not m:
        return None
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def parse_all_dates_br(text: str) -> List[date]:
    out: List[date] = []
    for m in _RE_DATE_BR.finditer(text or ""):
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            out.append(date(y, mo, d))
        except ValueError:
            continue
    return sorted(set(out))


def _br_money_token_to_float(token: str) -> Optional[float]:
    """Token como '1.719,26' ou '10868,68' → float."""
    if not token:
        return None
    t = token.strip()
    if re.search(r"mil\b", t, re.I):
        return None
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".")
    elif "," in t:
        parts = t.split(",")
        if len(parts[-1]) <= 2 and parts[-1].isdigit():
            t = "".join(parts[:-1]) + "." + parts[-1]
        else:
            t = t.replace(",", ".")
    else:
        if t.count(".") >= 1 and all(len(p) == 3 for p in t.split(".")[1:]):
            t = t.replace(".", "")
        elif t.count(".") == 1 and len(t.split(".")[-1]) == 3:
            t = t.replace(".", "")
    try:
        return float(t)
    except ValueError:
        return None


def parse_money_br(text: Any) -> Optional[float]:
    """
    Extrai um valor monetário em R$ (texto PT-BR).
    Suporta milhares com ponto, decimais com vírgula, e sufixo 'mil'.
    """
    if text is None:
        return None
    s = str(text)
    mm = _RE_MONEY_MIL.search(s)
    if mm:
        base = mm.group(1).replace(",", ".")
        try:
            return round(float(base) * 1000, 2)
        except ValueError:
            pass
    mb = _RE_MIL_BARE.search(s)
    if mb:
        try:
            return float(mb.group(1)) * 1000
        except ValueError:
            pass
    for m in _RE_MONEY_FULL.finditer(s):
        tail = s[m.end() : m.end() + 24].lower()
        if re.search(r",\d+\s*mil\b", tail):
            continue
        raw = m.group(1).strip()
        v = _br_money_token_to_float(raw)
        if v is not None:
            return v
    return None


def _money_context_window(s: str, start: int, end: int) -> str:
    lo = s.lower()
    a = max(0, start - _CTX_LOOKBACK)
    b = min(len(lo), end + _CTX_LOOKAHEAD)
    return lo[a:b]


def _classify_money_value(*, val: float, ctx: str, kind: str) -> str:
    """
    Retorna 'fee', 'sal' ou 'amb' (ambíguo: não enviar a salário sem revisão).
    Conservador: faixa 40–250 com léxico de taxa/inscrição → taxa; salário exige
    contexto explícito (salário/remuneração/… ou mil / até com remuneração).
    """
    has_fee = bool(_RE_CTX_FEE.search(ctx))
    has_sal = bool(_RE_CTX_SAL.search(ctx))

    if 40 <= val <= 250 and has_fee:
        return "fee"

    if kind in ("mil", "mil_bare"):
        return "sal"

    if kind == "ate":
        if has_fee and not has_sal:
            return "fee"
        if has_sal or "mil" in ctx:
            return "sal"
        if 40 <= val <= 250:
            return "amb"
        return "sal"

    # kind == "full" — na faixa típica de taxa, não promover a salário só por "salários" longe no mesmo artigo
    if 40 <= val <= 250:
        if has_fee:
            return "fee"
        return "amb"

    if has_fee and not has_sal:
        return "fee"
    if has_sal and not has_fee:
        return "sal"
    if has_fee and has_sal:
        if val >= 800:
            return "sal"
        if val <= 400:
            return "fee"
        return "amb"
    if val <= 350:
        return "fee"
    if val >= 1200:
        return "sal"
    if "mil" in ctx:
        return "sal"
    return "amb"


def _collect_money_spans(s: str) -> List[Tuple[int, int, float, str]]:
    """Spans não sobrepostos (prioriza ocorrência mais longa primeiro por start)."""
    raw: List[Tuple[int, int, float, str]] = []
    for m in _RE_ATE_MONEY.finditer(s):
        rest = s[m.end() : m.end() + 28].lstrip()
        if re.match(r",\d+\s*mil\b", rest, re.I) or re.match(r"\d+,\d+\s*mil\b", rest, re.I):
            continue
        v = _br_money_token_to_float(m.group(1))
        if v is not None:
            raw.append((m.start(), m.end(), v, "ate"))
    for m in _RE_MONEY_MIL.finditer(s):
        base = m.group(1).replace(",", ".")
        try:
            raw.append((m.start(), m.end(), float(base) * 1000, "mil"))
        except ValueError:
            continue
    for m in _RE_MIL_BARE.finditer(s):
        try:
            raw.append((m.start(), m.end(), float(m.group(1)) * 1000, "mil_bare"))
        except ValueError:
            continue
    for m in _RE_MONEY_FULL.finditer(s):
        tail = s[m.end() : m.end() + 24].lower()
        if re.search(r",\d+\s*mil\b", tail):
            continue
        v = _br_money_token_to_float(m.group(1))
        if v is not None:
            raw.append((m.start(), m.end(), v, "full"))
    raw.sort(key=lambda t: (t[0], -(t[1] - t[0])))
    merged: List[Tuple[int, int, float, str]] = []
    last_end = -1
    for st, en, val, kind in raw:
        if st < last_end:
            continue
        merged.append((st, en, val, kind))
        last_end = en
    return merged


def parse_remuneracao_taxa_br(text: Any) -> Tuple[Optional[float], Optional[float], Optional[float], Dict[str, Any]]:
    """
    Separa valores monetários em remuneração vs taxa de inscrição por contexto local.
    Retorna (salario_min, salario_max, taxa_inscricao, meta).
    meta: value_extraction_notes (list[str]), possible_fee_detected, possible_salary_detected.
    """
    meta: Dict[str, Any] = {
        "value_extraction_notes": [],
        "possible_fee_detected": False,
        "possible_salary_detected": False,
    }
    if text is None:
        return None, None, None, meta
    s = str(text)
    notes: List[str] = []
    fee_vals: List[float] = []
    sal_vals: List[Tuple[float, str]] = []
    ambiguous = False

    spans = _collect_money_spans(s)
    for st, en, val, kind in spans:
        ctx = _money_context_window(s, st, en)
        cls = _classify_money_value(val=val, ctx=ctx, kind=kind)
        if cls == "fee":
            fee_vals.append(val)
        elif cls == "sal":
            sal_vals.append((val, kind))
        else:
            ambiguous = True
            notes.append(f"valor_ambiguo_excluido_de_salario:{round(val, 2)}")

    taxa: Optional[float] = None
    if fee_vals:
        ufee = sorted({round(v, 2) for v in fee_vals})
        taxa = ufee[0] if len(ufee) == 1 else min(ufee)

    smin: Optional[float] = None
    smax: Optional[float] = None
    if sal_vals:
        only_ate = len(sal_vals) == 1 and sal_vals[0][1] == "ate"
        vals_only = [v for v, _ in sal_vals]
        usal = sorted({round(v, 2) for v in vals_only})
        if only_ate:
            smin, smax = None, usal[0]
        elif len(usal) == 1:
            k0 = sal_vals[0][1]
            if k0 in ("mil", "mil_bare"):
                smin, smax = None, usal[0]
            else:
                smin, smax = usal[0], usal[0]
        else:
            smin, smax = min(usal), max(usal)
    elif not sal_vals:
        for ate in _RE_ATE_MONEY.finditer(s):
            rest = s[ate.end() : ate.end() + 28].lstrip()
            if re.match(r",\d+\s*mil\b", rest, re.I) or re.match(r"\d+,\d+\s*mil\b", rest, re.I):
                continue
            v = _br_money_token_to_float(ate.group(1))
            if v is not None:
                ctx = _money_context_window(s, ate.start(), ate.end())
                if _classify_money_value(val=v, ctx=ctx, kind="ate") == "sal":
                    smin, smax = None, v
                    break

    meta["value_extraction_notes"] = notes
    meta["possible_fee_detected"] = bool(fee_vals or ambiguous)
    meta["possible_salary_detected"] = bool(sal_vals or smin is not None or smax is not None)
    return smin, smax, taxa, meta


def parse_salario_min_max_br(text: Any) -> Tuple[Optional[float], Optional[float]]:
    """
    Heurística: retorna (salario_min, salario_max) ignorando taxas de inscrição.
    Ver parse_remuneracao_taxa_br para taxa_inscricao e notas.
    """
    smin, smax, _, _ = parse_remuneracao_taxa_br(text)
    return smin, smax


def parse_vagas_cadastro_reserva(text: Any) -> bool:
    if text is None:
        return False
    return bool(_RE_CADASTRO_RESERVA.search(str(text)))


def parse_vagas(text: Any) -> Optional[int]:
    """
    Número de vagas antes da palavra 'vagas'.
    Aceita '1.100 vagas' (milhar PT), '4 vagas', evita ano a 4 dígitos (1990–2100).
    """
    if text is None:
        return None
    s = str(text)
    if parse_vagas_cadastro_reserva(s) and not _RE_VAGAS.search(s):
        return None
    for m in _RE_VAGAS.finditer(s):
        raw = m.group(1)
        if "." in raw:
            digits = raw.replace(".", "")
            try:
                n = int(digits)
            except ValueError:
                continue
        else:
            try:
                n = int(raw)
            except ValueError:
                continue
        if 1990 <= n <= 2100 and len(raw) == 4 and "." not in raw:
            continue
        return n
    return None


def _vagas_raw_to_int(raw: str) -> Optional[int]:
    if "." in raw:
        digits = raw.replace(".", "")
        try:
            n = int(digits)
        except ValueError:
            return None
    else:
        try:
            n = int(raw)
        except ValueError:
            return None
    if 1990 <= n <= 2100 and len(raw) == 4 and "." not in raw:
        return None
    return n


def _split_body_paragraphs(head: str) -> List[str]:
    return [p.strip() for p in re.split(r"\n\s*\n+", head) if len(p.strip()) > 10]


def _certame_paragraphs_for_vagas(full: str, scan_limit: int) -> List[str]:
    head = (full or "")[:scan_limit]
    paras = _split_body_paragraphs(head)
    if not paras:
        return [head.strip()] if head.strip() else []
    picked = [p for p in paras if _RE_VAGAS_CERTAME_PARA.search(p)]
    if not picked:
        return paras[:2]
    return picked[:8]


def _vagas_hits_in_paragraph(para: str, para_idx: int) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    if parse_vagas_cadastro_reserva(para) and not _RE_VAGAS_WORD.search(para):
        return out
    for rx in (_RE_VAGAS_WORD, _RE_OPORTUNIDADES):
        for m in rx.finditer(para):
            raw = m.group(1)
            n = _vagas_raw_to_int(raw)
            if n is None:
                continue
            win_start = max(0, m.start() - 160)
            win = para[win_start : m.start()]
            tail = win[-220:] if len(win) > 220 else win
            if _RE_VAGAS_CTX_EXCLUDE.search(tail):
                continue
            if not _RE_VAGAS_CTX_INCLUDE.search(win):
                continue
            out.append((n, para_idx))
    return out


def parse_vagas_certame(
    text: Any,
    *,
    scan_limit: int = 4500,
    paragraph_scope: bool = False,
    title_for_crosscheck: str = "",
) -> Tuple[Optional[int], List[str]]:
    """
    Vagas só com evidência de certame no trecho antes do número (evita rodapé/sidebar).
    Com paragraph_scope=True: só parágrafos com léxico de certame; o mesmo número em
    parágrafos distintos → null + nota vagas_ambiguas_nao_preenchidas.
    """
    notes: List[str] = []
    if text is None:
        return None, notes
    raw_full = str(text)
    head = raw_full[:scan_limit]

    if paragraph_scope:
        paras = _certame_paragraphs_for_vagas(raw_full, scan_limit)
        if not paras:
            notes.append("vagas_sem_contexto_certame_ou_excluidas_rodape")
            return None, notes
        hits_detail: List[Tuple[int, int]] = []
        for pi, para in enumerate(paras):
            hits_detail.extend(_vagas_hits_in_paragraph(para, pi))
        if not hits_detail:
            notes.append("vagas_sem_contexto_certame_ou_excluidas_rodape")
            return None, notes
        uniq = sorted({t[0] for t in hits_detail})
        if len(uniq) > 1:
            notes.append(f"vagas_ambiguas_candidatos:{uniq}")
            notes.append("vagas_ambiguas_nao_preenchidas")
            return None, notes
        n0 = uniq[0]
        paras_with = {t[1] for t in hits_detail if t[0] == n0}
        if len(paras_with) > 1:
            notes.append("vagas_ambiguas_nao_preenchidas")
            return None, notes
        tit = normalize_text(title_for_crosscheck or "")
        if tit:
            tnums = [int(x) for x in re.findall(r"(?i)\b(\d{1,4})\s+vagas?\b", tit)]
            if tnums and n0 not in tnums:
                notes.append("vagas_ambiguas_nao_preenchidas")
                return None, notes
        if len(hits_detail) > 1 and len(paras_with) == 1:
            notes.append("vagas_valor_repetido_multiplas_ocorrencias")
        return n0, notes

    s = head
    if parse_vagas_cadastro_reserva(s) and not _RE_VAGAS_WORD.search(s):
        return None, notes

    hits: List[int] = []
    for n, _ in _vagas_hits_in_paragraph(s, 0):
        hits.append(n)

    if not hits:
        notes.append("vagas_sem_contexto_certame_ou_excluidas_rodape")
        return None, notes
    uniq = sorted(set(hits))
    if len(uniq) > 1:
        notes.append(f"vagas_ambiguas_candidatos:{uniq}")
        notes.append("vagas_ambiguas_nao_preenchidas")
        return None, notes
    if len(hits) > 1 and len(uniq) == 1:
        notes.append("vagas_valor_repetido_multiplas_ocorrencias")
    return uniq[0], notes


def infer_tipo_selecao_meta(title: str, body: str) -> Tuple[str, str]:
    """
    (tipo_selecao, evidência curta para auditoria).
    Ordem: estágio → misto concurso+PS → processo seletivo → concurso público → demais.
    """
    tl = normalize_text(title).lower()
    bl = normalize_text(body).lower()
    blob = f"{tl} {bl}"

    if re.search(r"(?i)\best[aá]gios?\b", normalize_text(title)) or re.search(
        r"(?i)\bsele[cç][aã]o\s+de\s+est[aá]gio\b", tl
    ):
        return "estagio", "titulo:estagio"

    if re.search(r"(?i)\bconcursos?\s+públicos?\s+e\s+processo\s+seletivo\b", blob):
        return "processo_seletivo", "texto:concursos_publicos_e_processo_seletivo"

    if re.search(r"(?i)\bprocesso\s+seletivo\b", blob):
        ev = "texto:processo_seletivo"
        if re.search(r"(?i)\bconcursos?\s+públicos?\b|\bconcurso\s+público\b", blob):
            ev = "misto:concurso_publico_e_processo_seletivo"
        return "processo_seletivo", ev

    if re.search(r"(?i)\bconcursos?\s+públicos?\b|\bconcurso\s+público\b", blob):
        return "concurso_publico", "texto:concurso_publico"

    if re.search(r"\bsele[cç][aã]o\b", blob):
        return "processo_seletivo", "texto:selecao_generica"

    if "professor" in blob:
        return "professor", "texto:professor"
    if "residência" in blob or "residencia" in blob:
        return "residencia", "texto:residencia"
    if "vestibular" in blob:
        return "vestibular", "texto:vestibular"
    if re.search(r"\bbolsa\b", blob):
        return "bolsa_estudo", "texto:bolsa"
    if "sisu" in blob and "ingresso" in blob:
        return "programa_ingresso", "texto:sisu"
    return "concurso_publico", "fallback:default_concurso_publico"


def infer_tipo_selecao(title: str, body: str) -> str:
    """Ver infer_tipo_selecao_meta."""
    return infer_tipo_selecao_meta(title, body)[0]


def strip_orgao_title_noise(titulo: str) -> str:
    """Corta sufixos editoriais do título antes de inferir órgão/município."""
    t = normalize_text(titulo)
    if not t:
        return t
    parts = re.split(
        r"(?i)(?<=\S)\s+(?:abre|publica|retifica|divulga|anuncia|oferece)\s+",
        t,
        maxsplit=1,
    )
    t = parts[0].strip()
    parts = re.split(r"(?i)(?<=\S)\s+com\s+sal[aá]rios?\s+", t, maxsplit=1)
    t = parts[0].strip()
    parts = re.split(r"(?i)(?<=\S)\s+com\s+vagas\s+", t, maxsplit=1)
    t = parts[0].strip()
    parts = re.split(r"(?i)(?<=\S)\s+para\s+", t, maxsplit=1)
    t = parts[0].strip()
    return t


def infer_orgao_local_from_title(titulo: str) -> Dict[str, Optional[str]]:
    """
    Extrai órgão / instituição / município / UF a partir do título (padrões frequentes PCI).
    Não inventa município quando o padrão não é claro.
    """
    out: Dict[str, Optional[str]] = {
        "orgao": None,
        "instituicao": None,
        "municipio": None,
        "estado": None,
    }
    if not titulo:
        return out
    t = strip_orgao_title_noise(titulo)
    if not t:
        return out

    al = re.match(r"(?i)^Assembleia\s+Legislativa\s+do\s+([A-Z]{2})$", t)
    if al:
        ufc = al.group(1).upper()
        if ufc in _UFS:
            out["orgao"] = f"Assembleia Legislativa do {ufc}"
            out["estado"] = ufc
            return out

    if re.search(r"(?i)instituto\s+militar\s+de\s+engenharia", t) or re.search(
        r"(?i)(?:^|[\s,;(-])ime(?:[\s,;)-]|$)",
        t,
    ):
        nome = "Instituto Militar de Engenharia"
        out["orgao"] = nome
        out["instituicao"] = nome
        return out
    if re.search(r"(?i)marinha\s+do\s+brasil", t):
        out["orgao"] = "Marinha do Brasil"
        return out
    if re.match(r"(?i)marinha\b", t) and not re.search(r"(?i)mercante", t):
        out["orgao"] = "Marinha do Brasil"
        return out
    if re.search(r"(?i)ex[eé]rcito\s+brasileiro", t):
        out["orgao"] = "Exército Brasileiro"
        return out
    if re.search(r"(?i)for[cç]a\s+a[eé]rea\s+brasileira", t):
        out["orgao"] = "Força Aérea Brasileira"
        return out

    muf = None
    for m in re.finditer(r"(?i)\s-\s([A-Z]{2})(?=\s|$|,|;|\.)", t):
        cand = m.group(1).upper()
        if cand in _UFS:
            muf = m
    uf: Optional[str] = None
    core = t
    if muf:
        uf = muf.group(1).upper()
        core = t[: muf.start()].strip()

    uni_patterns = (
        r"(?i)^(Universidade\s+Federal\s+de\s+.+)$",
        r"(?i)^(Universidade\s+Estadual\s+de\s+.+)$",
        r"(?i)^(Universidade\s+Federal\s+do\s+.+)$",
        r"(?i)^(Universidade\s+Estadual\s+do\s+.+)$",
        r"(?i)^(Universidade\s+Federal\s+da\s+.+)$",
        r"(?i)^(Universidade\s+Estadual\s+da\s+.+)$",
    )
    for pat in uni_patterns:
        um = re.match(pat, core)
        if um:
            nome = normalize_text(um.group(1))
            out["orgao"] = nome
            out["instituicao"] = nome
            out["estado"] = uf
            return out

    pm = re.match(r"(?i)^Prefeitura\s+de\s+(.+)$", core)
    if pm:
        mun = normalize_text(pm.group(1))
        out["orgao"] = f"Prefeitura de {mun}"
        out["municipio"] = mun
        out["estado"] = uf
        return out

    cmm = re.match(r"(?i)^Câmara\s+Municipal\s+de\s+(.+)$", core)
    if cmm:
        mun = normalize_text(cmm.group(1))
        out["orgao"] = f"Câmara Municipal de {mun}"
        out["municipio"] = mun
        out["estado"] = uf
        return out

    cm = re.match(r"(?i)^Câmara\s+de\s+(.+)$", core)
    if cm:
        mun = normalize_text(cm.group(1))
        out["orgao"] = f"Câmara de {mun}"
        out["municipio"] = mun
        out["estado"] = uf
        return out

    return out


def infer_nivel_escolaridade(title: str, body: str) -> Optional[str]:
    blob = normalize_text(f"{title} {body}").lower()
    if re.search(r"nível\s+médio|nivel\s+medio|ensino\s+médio|ensino\s+medio", blob):
        return "medio"
    if re.search(r"nível\s+superior|nivel\s+superior|gradua[çc][aã]o", blob):
        return "superior"
    if re.search(r"nível\s+fundamental|nivel\s+fundamental|ensino\s+fundamental", blob):
        return "fundamental"
    if re.search(r"nível\s+técnico|nivel\s+tecnico|curso\s+técnico|técnico\s+em", blob):
        return "tecnico"
    return None


PCI_CORE_FIELD_KEYS = (
    "data_fim_inscricao",
    "data_prova",
    "orgao",
    "estado",
    "instituicao",
    "link_edital",
    "numero_vagas",
)


def pci_missing_core_fields(partial: Dict[str, Any]) -> List[str]:
    miss: List[str] = []
    for k in PCI_CORE_FIELD_KEYS:
        v = partial.get(k)
        if v is None or (isinstance(v, str) and not str(v).strip()):
            miss.append(k)
    return miss


def pci_infer_qualidade_dado(
    *,
    titulo: str,
    link: str,
    orgao: Optional[str],
    instituicao: Optional[str],
    estado: Optional[str],
    municipio: Optional[str],
    data_fim_inscricao: Optional[str],
    data_prova: Optional[str],
    data_publicacao: Optional[str],
    numero_vagas: Optional[int],
    salario_min: Optional[float],
    salario_max: Optional[float],
    taxa_inscricao: Optional[float],
) -> str:
    """
    Etiqueta de qualidade do agregador PCI (sem DB).
    - alta: título + link + órgão/instituição + local (UF ou município) + datas principais (fim inscrição e prova).
    - baixa: só descoberta mínima (título + link) sem datas nem órgão/local nem vagas/remuneração/taxa.
    - media: casos intermédios.
    """
    if not normalize_text(titulo) or not str(link or "").strip().lower().startswith("http"):
        return "baixa"

    has_org = bool((orgao or "").strip()) or bool((instituicao or "").strip())
    has_local = bool((estado or "").strip()) or bool((municipio or "").strip())
    has_main_dates = bool(data_fim_inscricao) and bool(data_prova)
    has_vagas = numero_vagas is not None
    has_sal = salario_min is not None or salario_max is not None
    has_taxa = taxa_inscricao is not None
    has_any_date = bool(data_fim_inscricao or data_prova or data_publicacao)

    if has_org and has_local and has_main_dates:
        return "alta"

    if (
        not has_org
        and not has_local
        and not has_any_date
        and not has_vagas
        and not has_sal
        and not has_taxa
    ):
        return "baixa"

    return "media"


def pci_infer_extraction_confidence(
    *,
    orgao: Optional[str],
    instituicao: Optional[str],
    estado: Optional[str],
    data_fim_inscricao: Optional[str],
    data_prova: Optional[str],
    numero_vagas: Optional[int],
    salario_max: Optional[float],
) -> str:
    has_org = bool((orgao or "").strip()) or bool((instituicao or "").strip())
    has_geo = bool((estado or "").strip())
    has_dates = bool(data_fim_inscricao or data_prova)
    has_val = numero_vagas is not None or salario_max is not None
    score = (2 if has_org else 0) + (1 if has_geo else 0) + (2 if has_dates else 0) + (1 if has_val else 0)
    if has_org and has_dates and has_val:
        return "alta"
    if score >= 4:
        return "alta"
    if score >= 2:
        return "media"
    return "baixa"


def pci_adjust_confidence_for_ambiguity(base: str, *, value_extraction_notes: List[str]) -> str:
    """Reduz confiança quando há valores ou vagas excluídos por ambiguidade."""
    blob = " ".join(value_extraction_notes or [])
    if "valor_ambiguo" in blob or "vagas_ambiguas_nao_preenchidas" in blob:
        if base == "alta":
            return "media"
        if base == "media":
            return "baixa"
    return base


def infer_status_concurso(
    *,
    data_fim_inscricao: Optional[str],
    data_prova: Optional[str],
    today: date,
) -> str:
    """Heurística conservadora (não substitui curadoria)."""
    df = _iso_to_date(data_fim_inscricao)
    dp = _iso_to_date(data_prova)
    if df is not None and df >= today:
        return "inscricoes_abertas"
    if dp is not None and dp >= today:
        if df is not None and df < today:
            return "prova_proxima"
        return "ativo"
    if df is not None and df < today and (dp is None or dp < today):
        return "encerrado"
    return "ativo"


def _iso_to_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", str(s))
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None


def _br_slash_to_iso(s: str) -> Optional[str]:
    parts = s.strip().split("/")
    if len(parts) != 3:
        return None
    try:
        d, mo, y = int(parts[0]), int(parts[1]), int(parts[2])
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def extract_inscricao_fim_explicit_br(text: str) -> Optional[str]:
    """
    Datas de encerramento de inscrições só com frases inequívocas (evita data editorial).
    """
    if not text:
        return None
    s = str(text)
    patterns = (
        r"(?:inscri[cç][aã]o|inscri[cç][oõ]es)\s+(?:seguem\s+)?at[eé]\s*:?\s*(\d{2}/\d{2}/\d{4})",
        r"(?:podem|pode)\s+se\s+inscrever\s+at[eé]\s*:?\s*(\d{2}/\d{2}/\d{4})",
        r"prazo\s+(?:de\s+(?:inscri[cç][aã]o|inscri[cç][oõ]es)\s+)?at[eé]\s*:?\s*(\d{2}/\d{2}/\d{4})",
        r"per[ií]odo\s+de\s+(?:inscri[cç][aã]o|inscri[cç][oõ]es)[^\n]{0,120}?at[eé]\s*:?\s*(\d{2}/\d{2}/\d{4})",
        r"(?:inscri[cç][aã]o|inscri[cç][oõ]es)\s+[^\n]{0,50}?encerram\s+(?:em\s+)?(\d{2}/\d{2}/\d{4})",
    )
    for pat in patterns:
        m = re.search(pat, s, re.IGNORECASE)
        if m:
            iso = _br_slash_to_iso(m.group(1))
            if iso:
                return iso
    return None


def extract_inscricao_fim_from_text(text: str) -> Optional[str]:
    m = _RE_INSCR_ATE.search(text or "")
    if m:
        return _br_slash_to_iso(m.group(1))
    return None


def extract_prova_from_text(text: str) -> Optional[str]:
    m = _RE_PROVA.search(text or "")
    if m:
        return _br_slash_to_iso(m.group(1))
    return None


def build_concurso_item(
    *,
    titulo: str,
    link: str,
    fonte: str,
    fonte_tipo: str,
    tipo_selecao: str,
    status: str,
    validacao_status: str,
    qualidade_dado: str,
    extras: Dict[str, Any],
    categoria: Optional[str] = None,
    orgao: Optional[str] = None,
    instituicao: Optional[str] = None,
    banca: Optional[str] = None,
    cargo: Optional[str] = None,
    curso: Optional[str] = None,
    area: Optional[str] = None,
    nivel_escolaridade: Optional[str] = None,
    estado: Optional[str] = None,
    municipio: Optional[str] = None,
    regiao: Optional[str] = None,
    modalidade: Optional[str] = None,
    numero_vagas: Optional[int] = None,
    salario_min: Optional[float] = None,
    salario_max: Optional[float] = None,
    taxa_inscricao: Optional[float] = None,
    data_publicacao: Optional[str] = None,
    data_inicio_inscricao: Optional[str] = None,
    data_fim_inscricao: Optional[str] = None,
    data_prova: Optional[str] = None,
    link_edital: Optional[str] = None,
    tags: Optional[List[str]] = None,
    ativo: bool = True,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "titulo": titulo,
        "tipo_selecao": tipo_selecao,
        "categoria": categoria,
        "orgao": orgao,
        "instituicao": instituicao,
        "banca": banca,
        "cargo": cargo,
        "curso": curso,
        "area": area,
        "nivel_escolaridade": nivel_escolaridade,
        "estado": estado,
        "municipio": municipio,
        "regiao": regiao,
        "modalidade": modalidade,
        "numero_vagas": numero_vagas,
        "salario_min": salario_min,
        "salario_max": salario_max,
        "taxa_inscricao": taxa_inscricao,
        "data_publicacao": data_publicacao,
        "data_inicio_inscricao": data_inicio_inscricao,
        "data_fim_inscricao": data_fim_inscricao,
        "data_prova": data_prova,
        "status": status,
        "link": link,
        "link_edital": link_edital,
        "fonte": fonte,
        "fonte_tipo": fonte_tipo,
        "validacao_status": validacao_status,
        "qualidade_dado": qualidade_dado,
        "tags": tags or [],
        "extras": extras or {},
        "ativo": ativo,
    }
    return row


def validate_concurso_item(row: Dict[str, Any]) -> List[str]:
    err: List[str] = []
    if not normalize_text(row.get("titulo")):
        err.append("titulo_obrigatorio")
    lk = normalize_text(row.get("link"))
    if not lk.startswith("http://") and not lk.startswith("https://"):
        err.append("link_http_obrigatorio")
    if not normalize_text(row.get("fonte")):
        err.append("fonte_obrigatoria")
    return err


def recency_should_discard(
    *,
    data_fim_inscricao: Optional[str],
    data_prova: Optional[str],
    today: date,
    text_for_recent_heuristic: str,
) -> Tuple[bool, str]:
    """
    Regra do crawler (wave1):
    - Descartar se data_fim_inscricao < hoje, exceto se data_prova futura.
    - Sem data_fim: manter se data_prova futura; se ambas ausentes, exigir indício
      recente (ano atual ou anterior no texto); caso contrário descartar.
    - Com ambas passadas: descartar.
    """
    df = _iso_to_date(data_fim_inscricao)
    dp = _iso_to_date(data_prova)
    if df is not None and df < today:
        if dp is not None and dp >= today:
            return False, ""
        return True, "data_fim_inscricao_passada_sem_prova_futura"
    if df is None and dp is not None and dp >= today:
        return False, ""
    if df is None and dp is not None and dp < today:
        return True, "data_prova_passada_sem_fim_inscricao"
    if df is None and dp is None:
        t = (text_for_recent_heuristic or "").lower()
        ynow = today.year
        if str(ynow) in t or str(ynow - 1) in t:
            return False, ""
        return True, "sem_datas_e_sem_indicio_recente"
    if df is not None and df >= today:
        return False, ""
    return False, ""


def field_fill_stats(rows: List[Dict[str, Any]]) -> Tuple[Dict[str, int], List[str]]:
    keys = [
        "titulo",
        "tipo_selecao",
        "categoria",
        "orgao",
        "instituicao",
        "banca",
        "cargo",
        "curso",
        "area",
        "nivel_escolaridade",
        "estado",
        "municipio",
        "regiao",
        "modalidade",
        "numero_vagas",
        "salario_min",
        "salario_max",
        "taxa_inscricao",
        "data_publicacao",
        "data_inicio_inscricao",
        "data_fim_inscricao",
        "data_prova",
        "status",
        "link",
        "link_edital",
        "fonte",
        "fonte_tipo",
        "validacao_status",
        "qualidade_dado",
        "tags",
        "extras",
        "ativo",
    ]
    filled: Dict[str, int] = {k: 0 for k in keys}
    for row in rows:
        for k in keys:
            v = row.get(k)
            ok = False
            if k == "tags":
                ok = isinstance(v, list) and len(v) > 0
            elif k == "extras":
                ok = isinstance(v, dict) and len(v) > 0
            elif k in ("numero_vagas", "salario_min", "salario_max", "taxa_inscricao"):
                ok = v is not None
            elif k == "ativo":
                ok = True
            else:
                ok = v is not None and str(v).strip() != ""
            if ok:
                filled[k] += 1
    missing = [k for k, n in filled.items() if n == 0 and k not in ("ativo",)]
    return filled, missing
