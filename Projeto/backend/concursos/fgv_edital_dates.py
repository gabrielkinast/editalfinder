# -*- coding: utf-8 -*-
"""
Extração conservadora de datas de inscrição/prova (PT-BR) para o crawler FGV.

- Padrões adicionais face a `concursos.common` (só usados pelo FGV).
- Download de PDF com limite de bytes + timeout (sem OCR).
- Texto: `CORE.pdf_enrichment.extract_pdf_text_with_fallback` se disponível; senão `pypdf`.
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date
from io import BytesIO
from typing import Dict, List, Optional, Tuple
from urllib.request import Request, urlopen

from concursos.common import (
    extract_inscricao_fim_explicit_br,
    extract_inscricao_fim_from_text,
    extract_prova_from_text,
    normalize_text,
)


def _iso_from_br(m: str) -> Optional[str]:
    m = (m or "").strip()
    parts = m.split("/")
    if len(parts) != 3:
        return None
    try:
        d, mo, y = int(parts[0]), int(parts[1]), int(parts[2])
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def _first_iso(patterns: List[Tuple[str, str]], text: str) -> Tuple[Optional[str], List[str]]:
    notes: List[str] = []
    s = text or ""
    for pat, label in patterns:
        m = re.search(pat, s, re.IGNORECASE | re.DOTALL)
        if m:
            iso = _iso_from_br(m.group(1))
            if iso:
                notes.append(f"match:{label}")
                return iso, notes
    return None, notes


def _first_two_iso(
    pattern: str, label: str, text: str
) -> Tuple[Optional[str], Optional[str], List[str]]:
    notes: List[str] = []
    m = re.search(pattern, text or "", re.IGNORECASE | re.DOTALL)
    if not m:
        return None, None, notes
    a, b = _iso_from_br(m.group(1)), _iso_from_br(m.group(2))
    if a and b:
        notes.append(f"match:{label}")
        return a, b, notes
    return None, None, notes


def _month_num_from_token(tok: str) -> Optional[int]:
    """Reconhece mês em PT (com tolerância a PDF com acentos corrompidos)."""
    t = unicodedata.normalize("NFD", (tok or "").strip())
    t = "".join(c for c in t if c.isalpha()).lower()
    if len(t) < 3:
        t = re.sub(r"[^a-z]", "", (tok or "").lower())
    if t.startswith("jan"):
        return 1
    if t.startswith("fev"):
        return 2
    if t.startswith("mar"):
        return 3
    if t.startswith("abr"):
        return 4
    if t.startswith("mai"):
        return 5
    if t.startswith("jun"):
        return 6
    if t.startswith("jul"):
        return 7
    if t.startswith("ago"):
        return 8
    if t.startswith("set"):
        return 9
    if t.startswith("out"):
        return 10
    if t.startswith("nov"):
        return 11
    if t.startswith("dez"):
        return 12
    return None


def _parse_written_date_chunk(chunk: str) -> Optional[str]:
    """«30 de abril de 2026» (ou mês com caracteres corrompidos no PDF) → ISO."""
    c = normalize_text(chunk.replace("\n", " ").replace("\r", " "))
    m = re.match(r"(?i)^(\d{1,2})\s+de\s+(.+?)\s+de\s+(\d{4})$", c.strip())
    if not m:
        return None
    try:
        d, y = int(m.group(1)), int(m.group(3))
    except ValueError:
        return None
    mo = _month_num_from_token(m.group(2))
    if mo is None:
        return None
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def _written_inscricao_period(s: str) -> Tuple[Optional[str], Optional[str], List[str]]:
    """Intervalo de inscrições com datas por extenso (comum em editais FGV em PDF)."""
    notes: List[str] = []
    patterns = (
        r"(?i)(?:estar[^\n]{0,40}abertas\s+)?no\s+per[ií]odo\s+de\s+"
        r"(\d{1,2}\s+de\s+[^\d]{2,28}\s+de\s+\d{4})\s+a\s+"
        r"(\d{1,2}\s+de\s+[^\d]{2,28}\s+de\s+\d{4})",
        r"(?i)per[ií]odo\s+de\s+"
        r"(\d{1,2}\s+de\s+[^\d]{2,28}\s+de\s+\d{4})\s+a\s+"
        r"(\d{1,2}\s+de\s+[^\d]{2,28}\s+de\s+\d{4})",
        r"(?i)inscri[cç][oõ]es[^\n]{0,200}?per[ií]odo\s+de\s+"
        r"(\d{1,2}\s+de\s+[^\d]{2,28}\s+de\s+\d{4})\s+a\s+"
        r"(\d{1,2}\s+de\s+[^\d]{2,28}\s+de\s+\d{4})",
    )
    for pat in patterns:
        m = re.search(pat, s, re.IGNORECASE | re.DOTALL)
        if not m:
            continue
        a = _parse_written_date_chunk(m.group(1))
        b = _parse_written_date_chunk(m.group(2))
        if a and b:
            notes.append("match:periodo_inscricoes_por_extenso")
            return a, b, notes
    return None, None, notes


def _written_prova_date(s: str) -> Tuple[Optional[str], List[str]]:
    notes: List[str] = []
    patterns = (
        r"(?i)prova\s+objetiva[^\n]{0,160}?(\d{1,2}\s+de\s+[^\d]{2,28}\s+de\s+\d{4})",
        r"(?i)aplica[cç][aã]o\s+(?:da|de)\s+prova[^\n]{0,160}?"
        r"(\d{1,2}\s+de\s+[^\d]{2,28}\s+de\s+\d{4})",
    )
    for pat in patterns:
        m = re.search(pat, s, re.IGNORECASE | re.DOTALL)
        if not m:
            continue
        iso = _parse_written_date_chunk(m.group(1))
        if iso:
            notes.append("match:prova_por_extenso")
            return iso, notes
    return None, notes


def fgv_schedule_from_text(text: str) -> Dict[str, Any]:
    """
    Extrai data_inicio_inscricao, data_fim_inscricao, data_prova (ISO YYYY-MM-DD).
    Ordem conservadora: período explícito; frases de fim; padrão genérico; prova com contexto.
    """
    notes: List[str] = []
    s = normalize_text(text)[:120000]

    inicio: Optional[str] = None
    fim: Optional[str] = None
    prova: Optional[str] = None

    iw0, iw1, nw = _written_inscricao_period(s)
    notes.extend(nw)
    if iw0 and iw1:
        inicio, fim = iw0, iw1

    i0, i1, n = _first_two_iso(
        r"(?i)per[ií]odo\s+de\s+inscri[cç][oõ]es[^\d]{0,120}?"
        r"de\s+(\d{2}/\d{2}/\d{4})\s+a\s+(\d{2}/\d{2}/\d{4})",
        "periodo_inscricoes_de_a",
        s,
    )
    notes.extend(n)
    if i0 and i1:
        inicio, fim = i0, i1

    if not fim:
        i0, i1, n = _first_two_iso(
            r"(?i)inscri[cç][oõ]es\s+(?:somente\s+)?(?:no\s+)?per[ií]odo\s+de\s+"
            r"(\d{2}/\d{2}/\d{4})\s+a\s+(\d{2}/\d{2}/\d{4})",
            "inscricoes_periodo_de_a",
            s,
        )
        notes.extend(n)
        if i0 and i1:
            inicio = inicio or i0
            fim = i1

    fim_patterns: List[Tuple[str, str]] = [
        (
            r"(?i)encerramento\s+das?\s+inscri[cç][oõ]es[^\d]{0,55}(\d{2}/\d{2}/\d{4})",
            "encerramento_inscricoes",
        ),
        (
            r"(?i)data\s+final\s+para\s+(?:a\s+)?inscri[cç][aã]o[^\d]{0,55}(\d{2}/\d{2}/\d{4})",
            "data_final_para_inscricao",
        ),
        (
            r"(?i)prazo\s+de\s+inscri[cç][aã]o[^\d]{0,55}(\d{2}/\d{2}/\d{4})",
            "prazo_de_inscricao",
        ),
        (
            r"(?i)inscri[cç][oõ]es\s+at[eé]\s*:?\s*(\d{2}/\d{2}/\d{4})",
            "inscricoes_ate",
        ),
    ]
    fx, fn = _first_iso(fim_patterns, s)
    notes.extend(fn)
    if fx:
        fim = fim or fx

    if not fim:
        ex = extract_inscricao_fim_explicit_br(s)
        if ex:
            fim = ex
            notes.append("extract_inscricao_fim_explicit_br")
    if not fim:
        ex2 = extract_inscricao_fim_from_text(s)
        if ex2:
            fim = ex2
            notes.append("extract_inscricao_fim_from_text")

    prova_patterns: List[Tuple[str, str]] = [
        (
            r"(?i)prova\s+objetiva[^\d]{0,70}(\d{2}/\d{2}/\d{4})",
            "prova_objetiva",
        ),
        (
            r"(?i)aplica[cç][aã]o\s+da\s+prova[^\d]{0,70}(\d{2}/\d{2}/\d{4})",
            "aplicacao_da_prova",
        ),
        (
            r"(?i)aplica[cç][aã]o\s+de\s+provas?\s+objetivas?[^\d]{0,70}(\d{2}/\d{2}/\d{4})",
            "aplicacao_provas_objetivas",
        ),
    ]
    px, pn = _first_iso(prova_patterns, s)
    notes.extend(pn)
    if px:
        prova = px
    if not prova:
        pw, pnw = _written_prova_date(s)
        notes.extend(pnw)
        if pw:
            prova = pw
    if not prova:
        p2 = extract_prova_from_text(s)
        if p2:
            prova = p2
            notes.append("extract_prova_from_text")

    return {
        "data_inicio_inscricao": inicio,
        "data_fim_inscricao": fim,
        "data_prova": prova,
        "schedule_notes": notes,
    }


def fetch_pdf_bytes_capped(
    url: str,
    *,
    referer: str,
    max_bytes: int,
    timeout_s: float,
) -> Tuple[Optional[bytes], str]:
    """
    Baixa PDF até `max_bytes`. HEAD opcional para Content-Length.
    Sem OCR; não usa subprocess/curl (mantém urllib simples).
    """
    if not url or not url.lower().startswith("http"):
        return None, "pdf_url_invalida"

    ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderFGV/0.1"
    )
    base_headers = {
        "User-Agent": ua,
        "Accept": "application/pdf,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": referer or url,
    }

    try:
        req_head = Request(url, headers=base_headers, method="HEAD")
        with urlopen(req_head, timeout=min(12.0, timeout_s)) as r:
            cl = r.headers.get("Content-Length")
            if cl and str(cl).isdigit() and int(cl) > max_bytes:
                return None, f"pdf_content_length_maior_que_limite_{max_bytes}"
    except Exception:
        pass

    try:
        req = Request(url, headers=base_headers)
        out = bytearray()
        with urlopen(req, timeout=timeout_s) as resp:
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out.extend(chunk)
                if len(out) > max_bytes:
                    return None, f"pdf_download_ultrapassou_{max_bytes}_bytes"
        raw = bytes(out)
        if len(raw) < 100 or not raw[:4] == b"%PDF":
            return None, "pdf_resposta_nao_pdf_ou_muito_pequena"
        return raw, "pdf_download_ok"
    except Exception as exc:
        return None, f"pdf_download_erro:{exc.__class__.__name__}"


def extract_pdf_text_fgv(pdf_bytes: bytes, *, max_pages: int = 10) -> Tuple[Optional[str], str]:
    """Extrai texto (sem OCR). Tenta CORE; depois pypdf direto."""
    if not pdf_bytes:
        return None, "pdf_bytes_vazio"

    try:
        from CORE.pdf_enrichment import extract_pdf_text_with_fallback

        t = extract_pdf_text_with_fallback(pdf_bytes, max_pages=max_pages)
        if t and t.strip():
            return t.strip(), "CORE_pdf_enrichment"
    except Exception:
        pass

    try:
        from pypdf import PdfReader
    except Exception:
        return None, "sem_pypdf_nem_CORE"

    try:
        reader = PdfReader(BytesIO(pdf_bytes), strict=False)
        pages = reader.pages[:max_pages]
        text = "\n".join((p.extract_text() or "") for p in pages).strip()
        if text:
            return text, "pypdf_direto"
    except Exception as exc:
        return None, f"pypdf_falhou:{exc.__class__.__name__}"

    return None, "pdf_texto_vazio_ou_somente_imagem"


def fgv_merge_schedule_with_pdf_text(
    *,
    titulo: str,
    body: str,
    pdf_text: Optional[str],
    prior_inicio: Optional[str],
    prior_fim: Optional[str],
    prior_prova: Optional[str],
) -> Dict[str, Any]:
    """
    Se houver texto do PDF, re-extrai com blob PDF+HTML (PDF primeiro).
    Para cada campo, valor do merge completo tem prioridade sobre `prior_*` quando não nulo.
    """
    if pdf_text and pdf_text.strip():
        blob = f"{pdf_text.strip()[:80000]}\n{titulo}\n{body}"
        sch = fgv_schedule_from_text(blob)
        return {
            "data_inicio_inscricao": sch["data_inicio_inscricao"] or prior_inicio,
            "data_fim_inscricao": sch["data_fim_inscricao"] or prior_fim,
            "data_prova": sch["data_prova"] or prior_prova,
            "schedule_notes": list(sch["schedule_notes"]),
        }
    return {
        "data_inicio_inscricao": prior_inicio,
        "data_fim_inscricao": prior_fim,
        "data_prova": prior_prova,
        "schedule_notes": [],
    }
