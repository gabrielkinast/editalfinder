#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler — sub-wave Militar/Aeroespacial: IME (CFG, CFrm, CG, CP/IME).

Diagnóstico (2026):
- Portal Joomla `ime.eb.mil.br` + hub `inscricoes.ime.eb.br`.
- Editais PDF por processo; texto frequentemente escaneado (sem OCR).
- CFG: editais ATIVA/RESERVA 2026-2027; inscrição SIPS_CFG.
- CFrm: edital CFORM 2026; SIPS_CFrm.
- CG: legislação com MIC EQA + calendário; inscrição via portal (#cg).
- CP/IME: curso preparatório (programa_formacao); calendário 2026; vagas no HTML.
"""
from __future__ import annotations

import argparse
import html as html_module
import json
import re
import ssl
import sys
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from concursos.common import (  # noqa: E402
    build_concurso_item,
    extract_inscricao_fim_explicit_br,
    extract_prova_from_text,
    field_fill_stats,
    infer_status_concurso,
    normalize_text,
    parse_all_dates_br,
    parse_remuneracao_taxa_br,
    parse_vagas,
    pci_adjust_confidence_for_ambiguity,
    pci_infer_extraction_confidence,
    pci_infer_qualidade_dado,
    pci_missing_core_fields,
    recency_should_discard,
    validate_concurso_item,
)
from concursos.fgv_edital_dates import (  # noqa: E402
    extract_pdf_text_fgv,
    fgv_schedule_from_text,
)

BASE = "https://www.ime.eb.mil.br"
PORTAL_INSCRICOES = "https://inscricoes.ime.eb.br/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "ime"
ORGAO = "Exército Brasileiro"
INSTITUICAO = "Instituto Militar de Engenharia"
BANCA = "IME / Exército Brasileiro"
ESTADO = "RJ"
MUNICIPIO = "Rio de Janeiro"
AREA = "Engenharia / Defesa / Militar / Aeroespacial"
PDF_MAX_BYTES = 6 * 1024 * 1024
PDF_TIMEOUT_S = 40.0

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

_RE_YEAR_PATH = re.compile(r"/(20\d{2})(?:[-_/]20\d{2})?/", re.I)
_RE_NON_OPP = (
    r"resultado\s+final",
    r"gabarito\s+definitivo",
    r"classifica[cç][aã]o\s+final",
    r"aprovados\s+no\s+\d",
)


@dataclass(frozen=True)
class ProcessSpec:
    key: str
    titulo_base: str
    page_url: str
    categoria: str
    tipo_selecao: str
    nivel_escolaridade: str
    curso: str
    link_suffix: str
    extra_urls: Tuple[str, ...] = ()
    link_inscricao: Optional[str] = None
    cfg_track: Optional[str] = None  # "ativa" | "reserva"
    tags: Tuple[str, ...] = field(default_factory=tuple)


DEFAULT_PROCESSES: Tuple[ProcessSpec, ...] = (
    ProcessSpec(
        key="cfg_ativa",
        titulo_base="IME — CFG ATIVA 2026-2027",
        page_url=f"{BASE}/vestibular-e-concursos/cfg-ensino-medio/inscricoes",
        categoria="militar_aeroespacial_ime_cfg",
        tipo_selecao="vestibular",
        nivel_escolaridade="medio",
        curso="Curso de Formação e Graduação (CFG) — Quadro de Engenheiros Militares (ativa)",
        link_suffix="#cfg-ativa-2026",
        link_inscricao="https://inscricoes.ime.eb.br/SIPS_CFG/Login",
        cfg_track="ativa",
        tags=("ime", "cfg", "vestibular", "militar_aeroespacial", "wave2"),
    ),
    ProcessSpec(
        key="cfg_reserva",
        titulo_base="IME — CFG RESERVA 2026-2027",
        page_url=f"{BASE}/vestibular-e-concursos/cfg-ensino-medio/inscricoes",
        categoria="militar_aeroespacial_ime_cfg",
        tipo_selecao="vestibular",
        nivel_escolaridade="medio",
        curso="Curso de Formação e Graduação (CFG) — Oficiais da Reserva (CORE)",
        link_suffix="#cfg-reserva-2026",
        link_inscricao="https://inscricoes.ime.eb.br/SIPS_CFG/Login",
        cfg_track="reserva",
        tags=("ime", "cfg", "vestibular", "militar_aeroespacial", "wave2"),
    ),
    ProcessSpec(
        key="cfrm",
        titulo_base="IME — CFrm (Formação) 2026-2027",
        page_url=f"{BASE}/vestibular-e-concursos/cfrm/informacoes-cfrm",
        categoria="militar_aeroespacial_ime_cfrm",
        tipo_selecao="programa_ingresso",
        nivel_escolaridade="superior",
        curso="Curso de Formação (CFrm) — engenheiros formados",
        link_suffix="",
        link_inscricao="https://inscricoes.ime.eb.br/SIPS_CFrm/Login",
        tags=("ime", "cfrm", "militar_aeroespacial", "wave2"),
    ),
    ProcessSpec(
        key="cg",
        titulo_base="IME — CG (Oficiais AMAN) EQA 2025-2026",
        page_url=f"{BASE}/vestibular-e-concursos/cg/informacoes-gerais-cg",
        categoria="militar_aeroespacial_ime_cg",
        tipo_selecao="programa_ingresso",
        nivel_escolaridade="superior",
        curso="Curso de Graduação (CG) — Exame de Qualificação e Admissão (EQA)",
        link_suffix="",
        extra_urls=(f"{BASE}/vestibular-e-concursos/cg/legislacao-cg",),
        link_inscricao=f"{PORTAL_INSCRICOES}#cg",
        tags=("ime", "cg", "eqa", "militar_aeroespacial", "wave2"),
    ),
    ProcessSpec(
        key="cp_ime",
        titulo_base="IME — CP/IME 2026",
        page_url=f"{BASE}/vestibular-e-concursos/cp-ime",
        categoria="militar_aeroespacial_ime_cp",
        tipo_selecao="programa_ingresso",
        nivel_escolaridade="superior",
        curso="Curso de Preparação ao IME (CP/IME)",
        link_suffix="",
        tags=("ime", "cp_ime", "programa_formacao", "programa_ingresso", "militar_aeroespacial", "wave2"),
    ),
)


def _unescape(s: str) -> str:
    return html_module.unescape(s or "")


def _fetch(url: str) -> Tuple[str, str]:
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Referer": f"{BASE}/",
        },
    )
    with urlopen(req, timeout=45, context=_SSL_CTX) as resp:
        final = resp.geturl()
        raw = resp.read()
    for enc in ("utf-8", "iso-8859-1", "latin-1"):
        try:
            return final, raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return final, raw.decode("utf-8", "replace")


def _load_robots_parser(base: str):
    from urllib.robotparser import RobotFileParser

    netloc = urlparse(base).netloc
    raw = ""
    for scheme in ("https", "http"):
        robots_url = f"{scheme}://{netloc}/robots.txt"
        try:
            req = Request(robots_url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=15, context=_SSL_CTX) as r:
                if r.status >= 400:
                    continue
                raw = r.read().decode("utf-8", "replace")
            break
        except Exception:
            continue
    if not raw.strip():
        return None
    rp = RobotFileParser()
    rp.parse(raw.splitlines())
    return rp


def _robots_disallows(url: str, robots_parser) -> bool:
    if robots_parser is None:
        return False
    try:
        return not robots_parser.can_fetch(USER_AGENT, url)
    except Exception:
        return True


def _article_text(soup: BeautifulSoup) -> str:
    root = soup.select_one(".com-content-article__body") or soup.find("article") or soup.body
    if not root:
        return normalize_text(_unescape(soup.get_text(" ", strip=True)))
    clone = BeautifulSoup(str(root), "html.parser")
    for sel in (".article-info", "time[itemprop='datePublished']"):
        for node in clone.select(sel):
            node.decompose()
    return normalize_text(_unescape(clone.get_text(" ", strip=True)))


def _sanitize_iso_date(iso: Optional[str], *, min_year: int) -> Optional[str]:
    if not iso or len(iso) < 4:
        return None
    try:
        year = int(iso[:4])
    except ValueError:
        return None
    if year < min_year:
        return None
    return iso


def _sanitize_prova_date(iso: Optional[str], *, today: date, min_year: int) -> Optional[str]:
    iso = _sanitize_iso_date(iso, min_year=min_year)
    if not iso:
        return None
    try:
        d = date.fromisoformat(iso)
    except ValueError:
        return None
    if d < today:
        return None
    return iso


def _year_from_url(url: str) -> Optional[int]:
    m = _RE_YEAR_PATH.search(url or "")
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    m2 = re.search(r"20(\d{2})", url or "")
    if m2:
        try:
            return 2000 + int(m2.group(1))
        except ValueError:
            pass
    return None


def _score_pdf(href: str, label: str, *, process_key: str, cfg_track: Optional[str]) -> int:
    h = (href or "").lower()
    l = normalize_text(label).lower()
    blob = f"{h} {l}"
    if any(re.search(p, blob, re.I) for p in _RE_NON_OPP):
        return -20
    if "resultado" in blob and "final" in blob:
        return -20
    if "aprovados" in blob and "modulo" in blob:
        return -15
    if "locais_de_prova" in h or "locais de prova" in l:
        return 1

    score = 0
    if "edital" in l or "edital" in h:
        score += 6
    if process_key.startswith("cfg"):
        if cfg_track == "ativa" and ("ativa" in h or "ativa" in l):
            score += 8
        if cfg_track == "reserva" and ("reserva" in h or "reserva" in l):
            score += 8
        if cfg_track == "ativa" and "reserva" in h:
            score -= 6
        if cfg_track == "reserva" and "ativa" in h and "reserva" not in h:
            score -= 6
    if process_key == "cfrm" and ("cform" in h or "cfrm" in l):
        score += 5
    if process_key == "cg":
        if "mic" in h or "manual" in l:
            score += 7
        if "calendario" in h or "calendário" in l:
            score += 4
        if "portaria" in h and "eqa" not in h:
            score += 1
    if process_key == "cp_ime":
        if "calendario" in h or "calendário" in l:
            score += 6
        if "portaria" in h and "calendario" not in h:
            score -= 2

    y = _year_from_url(href)
    if y is not None:
        if y >= date.today().year - 1:
            score += 3
        if y < date.today().year - 2:
            score -= 8
    return score


def _collect_pdf_links(soup: BeautifulSoup, page_url: str) -> List[Tuple[int, str, str]]:
    out: List[Tuple[int, str, str]] = []
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"]).split("#")[0]
        if ".pdf" not in href.lower():
            continue
        label = _unescape(a.get_text(" ", strip=True))
        out.append((0, href, label))
    return out


def pick_edital_pdf(
    soup: BeautifulSoup,
    page_url: str,
    *,
    process_key: str,
    cfg_track: Optional[str] = None,
) -> Optional[str]:
    scored: List[Tuple[int, str]] = []
    for _, href, label in _collect_pdf_links(soup, page_url):
        sc = _score_pdf(href, label, process_key=process_key, cfg_track=cfg_track)
        if sc > 0:
            scored.append((sc, href))
    if not scored:
        return None
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored[0][1]


def ime_should_discard_non_opportunity(*, titulo: str, pdf_url: Optional[str]) -> Tuple[bool, str]:
    """Descarte conservador: título + URL do edital (evita falso positivo no corpo HTML)."""
    blob = f"{titulo}\n{pdf_url or ''}".lower()
    for pat in _RE_NON_OPP:
        if re.search(pat, blob, re.I):
            return True, "ime_nao_oportunidade_ativa"
    if pdf_url and "resultado" in pdf_url.lower() and "final" in pdf_url.lower():
        return True, "ime_resultado_final"
    y = _year_from_url(pdf_url or "")
    if y is not None and y < date.today().year - 2:
        return True, "ime_edital_ano_antigo"
    return False, ""


def _fetch_pdf_bytes_ssl(url: str, *, referer: str) -> Tuple[Optional[bytes], str]:
    if not url or not url.lower().startswith("http"):
        return None, "pdf_url_invalida"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/pdf,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": referer or url,
    }
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=PDF_TIMEOUT_S, context=_SSL_CTX) as resp:
            raw = resp.read(PDF_MAX_BYTES + 1)
        if len(raw) > PDF_MAX_BYTES:
            return None, f"pdf_maior_que_limite_{PDF_MAX_BYTES}"
        return raw, "ok_ssl"
    except Exception as exc:
        return None, f"pdf_download_erro:{type(exc).__name__}"


def _enrich_pdf(pdf_url: str, referer: str) -> Tuple[Optional[str], Optional[str], Optional[str], Dict[str, Any]]:
    meta: Dict[str, Any] = {"pdf_url": pdf_url}
    raw, note = _fetch_pdf_bytes_ssl(pdf_url, referer=referer)
    meta["fetch_note"] = note
    if not raw:
        return None, None, None, meta
    text, text_note = extract_pdf_text_fgv(raw)
    meta["text_extraction"] = text_note
    meta["text_len"] = len(text or "")
    if not text or len(text) < 80:
        return None, None, None, meta
    sched = fgv_schedule_from_text(text)
    meta["schedule_notes"] = sched.get("notes") or []
    return (
        sched.get("data_inicio_inscricao"),
        sched.get("data_fim_inscricao"),
        sched.get("data_prova"),
        meta,
    )


def _infer_cycle_year(blob: str, pdf_url: Optional[str]) -> int:
    y = _year_from_url(pdf_url or "")
    if y:
        return y
    for m in re.finditer(r"20(\d{2})\s*/\s*20(\d{2})", blob):
        try:
            return int("20" + m.group(2))
        except ValueError:
            pass
    for m in re.finditer(r"20(\d{2})", blob):
        yr = 2000 + int(m.group(1))
        if yr >= date.today().year - 1:
            return yr
    return date.today().year


def parse_ime_process(
    spec: ProcessSpec,
    *,
    html_by_url: Dict[str, str],
    page_url_final: str,
    enrich_pdf: bool,
) -> Dict[str, Any]:
    soups: List[BeautifulSoup] = []
    texts: List[str] = []
    for u in (spec.page_url, *spec.extra_urls):
        h = html_by_url.get(u)
        if not h:
            continue
        soup = BeautifulSoup(h, "html.parser")
        soups.append(soup)
        texts.append(_article_text(soup))
    body = "\n".join(texts)
    blob = body

    link_edital: Optional[str] = None
    for soup in soups:
        link_edital = pick_edital_pdf(
            soup,
            page_url_final,
            process_key=spec.key,
            cfg_track=spec.cfg_track,
        )
        if link_edital:
            break

    today = date.today()
    min_year = today.year - 2
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    data_prova: Optional[str] = _sanitize_prova_date(
        extract_prova_from_text(blob), today=today, min_year=min_year
    )
    pdf_meta: Dict[str, Any] = {}
    if link_edital and enrich_pdf:
        di, df, dp, pdf_meta = _enrich_pdf(link_edital, referer=spec.page_url)
        data_inicio = di
        data_fim = df or extract_inscricao_fim_explicit_br(blob)
        if dp and not data_prova:
            data_prova = _sanitize_prova_date(dp, today=today, min_year=min_year)
    else:
        data_fim = extract_inscricao_fim_explicit_br(blob)

    sal_min, sal_max, taxa, money_meta = parse_remuneracao_taxa_br(blob)
    numero_vagas: Optional[int] = None
    if spec.key == "cp_ime":
        m_v = re.search(r"n[uú]mero\s+de\s+vagas[^:]{0,120}:\s*(\d{1,4})\b", blob, re.I)
        if m_v:
            try:
                numero_vagas = int(m_v.group(1))
            except ValueError:
                numero_vagas = parse_vagas(blob)
        else:
            numero_vagas = parse_vagas(blob)
    dates_iso = [d for d in parse_all_dates_br(blob) if d.year >= min_year]
    data_pub = dates_iso[0].isoformat() if dates_iso else None
    cycle_year = _infer_cycle_year(blob, link_edital)

    return {
        "titulo": spec.titulo_base,
        "body": body,
        "tipo_selecao": spec.tipo_selecao,
        "curso": spec.curso,
        "area": AREA,
        "nivel_escolaridade": spec.nivel_escolaridade,
        "categoria": spec.categoria,
        "data_inicio_inscricao": data_inicio,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "numero_vagas": numero_vagas,
        "link_edital": link_edital,
        "link": f"{spec.page_url}{spec.link_suffix}",
        "link_inscricao": spec.link_inscricao,
        "pdf_meta": pdf_meta,
        "cycle_year": cycle_year,
        "process_key": spec.key,
        "tags": list(spec.tags),
    }


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    processes: Tuple[ProcessSpec, ...],
    enrich_pdf: bool,
) -> Dict[str, Any]:
    rp = _load_robots_parser(BASE)
    urls_to_fetch: List[str] = []
    for spec in processes:
        for u in (spec.page_url, *spec.extra_urls):
            if u not in urls_to_fetch:
                urls_to_fetch.append(u)
    for u in urls_to_fetch:
        if _robots_disallows(u, rp):
            raise RuntimeError(f"robots bloqueia URL: {u}")

    html_by_url: Dict[str, str] = {}
    page_final: Dict[str, str] = {}
    for u in urls_to_fetch:
        time.sleep(sleep_s)
        final, html = _fetch(u)
        html_by_url[u] = html
        page_final[u] = final

    today = date.today()
    raw_rows: List[Dict[str, Any]] = []
    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for spec in processes[: max_items if max_items > 0 else len(processes)]:
        parsed = parse_ime_process(
            spec,
            html_by_url=html_by_url,
            page_url_final=page_final.get(spec.page_url, spec.page_url),
            enrich_pdf=enrich_pdf,
        )
        url = parsed["link"]
        tit = parsed["titulo"]
        body = parsed.get("body") or ""
        off = parsed.get("link_edital")

        drop_no, why_no = ime_should_discard_non_opportunity(titulo=tit, pdf_url=off)
        if drop_no:
            discarded.append({"url": url, "titulo": tit, "motivo": why_no, "process": spec.key})
            continue

        data_fim = parsed.get("data_fim_inscricao")
        data_prova = parsed.get("data_prova")
        drop_r, why_r = recency_should_discard(
            data_fim_inscricao=data_fim,
            data_prova=data_prova,
            today=today,
            text_for_recent_heuristic=f"{tit} {body} {parsed.get('cycle_year')} {off}",
        )
        if drop_r:
            discarded.append({"url": url, "titulo": tit, "motivo": why_r, "process": spec.key})
            continue

        validacao = "valido" if off and data_fim else "incompleto"
        status = infer_status_concurso(
            data_fim_inscricao=data_fim,
            data_prova=data_prova,
            today=today,
        )
        missing_core = pci_missing_core_fields(
            {
                "orgao": ORGAO,
                "instituicao": INSTITUICAO,
                "estado": ESTADO,
                "data_fim_inscricao": data_fim,
                "data_prova": data_prova,
                "link_edital": off,
            }
        )
        confidence = pci_infer_extraction_confidence(
            orgao=ORGAO,
            instituicao=INSTITUICAO,
            estado=ESTADO,
            data_fim_inscricao=data_fim,
            data_prova=data_prova,
            numero_vagas=parsed.get("numero_vagas"),
            salario_max=parsed.get("salario_max"),
        )
        qualidade = pci_infer_qualidade_dado(
            titulo=tit,
            link=url,
            orgao=ORGAO,
            instituicao=INSTITUICAO,
            estado=ESTADO,
            municipio=MUNICIPIO,
            data_fim_inscricao=data_fim,
            data_prova=data_prova,
            data_publicacao=parsed.get("data_publicacao"),
            numero_vagas=parsed.get("numero_vagas"),
            salario_min=parsed.get("salario_min"),
            salario_max=parsed.get("salario_max"),
            taxa_inscricao=parsed.get("taxa_inscricao"),
        )
        if off and not data_fim:
            qualidade = "media" if qualidade == "alta" else qualidade

        money_meta = parsed.get("money_meta") or {}
        notes: List[str] = []
        if not off:
            notes.append("edital_pdf_nao_encontrado")
        elif (parsed.get("pdf_meta") or {}).get("text_len", 0) < 80:
            notes.append("edital_pdf_sem_texto_extraivel_escaneado")
        if spec.key == "cp_ime" and off and "calendario" in (off or "").lower():
            notes.append("cp_documento_calendario_como_link_edital")
        if spec.key == "cg" and off and "mic" in (off or "").lower():
            notes.append("cg_manual_instrucoes_como_link_edital")
        notes.extend(money_meta.get("value_extraction_notes") or [])

        extras: Dict[str, Any] = {
            "crawler": "main_militar_aeroespacial_ime",
            "wave": "concursos_wave2_militar_aeroespacial_ime",
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            "process_key": spec.key,
            "link_inscricao": parsed.get("link_inscricao"),
            "portal_inscricoes": PORTAL_INSCRICOES,
            "pdf_enrichment": parsed.get("pdf_meta") or {},
            "cycle_year": parsed.get("cycle_year"),
            "missing_core_fields": missing_core,
            "extraction_confidence": pci_adjust_confidence_for_ambiguity(
                confidence, value_extraction_notes=notes
            ),
            "value_extraction_notes": notes,
            "seed_urls": list(urls_to_fetch),
        }

        row = build_concurso_item(
            titulo=tit[:500],
            link=url,
            fonte=FONT,
            fonte_tipo="instituicao",
            tipo_selecao=parsed.get("tipo_selecao") or "processo_seletivo",
            status=status,
            validacao_status=validacao,
            qualidade_dado=qualidade,
            extras=extras,
            categoria=parsed.get("categoria"),
            orgao=ORGAO,
            instituicao=INSTITUICAO,
            banca=BANCA,
            cargo=None,
            curso=parsed.get("curso"),
            area=parsed.get("area"),
            nivel_escolaridade=parsed.get("nivel_escolaridade"),
            estado=ESTADO,
            municipio=MUNICIPIO,
            numero_vagas=parsed.get("numero_vagas"),
            salario_min=parsed.get("salario_min"),
            salario_max=parsed.get("salario_max"),
            taxa_inscricao=parsed.get("taxa_inscricao"),
            data_publicacao=parsed.get("data_publicacao"),
            data_inicio_inscricao=parsed.get("data_inicio_inscricao"),
            data_fim_inscricao=data_fim,
            data_prova=data_prova,
            link_edital=off,
            tags=parsed.get("tags"),
        )
        verr = validate_concurso_item(row)
        if verr:
            errors.append({"url": url, "erros": verr, "process": spec.key})
        else:
            raw_rows.append(row)

    filled, missing = field_fill_stats(raw_rows)
    val_ok = sum(1 for r in raw_rows if r.get("validacao_status") == "valido")
    inc_ok = sum(1 for r in raw_rows if r.get("validacao_status") == "incompleto")
    return {
        "fonte": FONT,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "processes": [p.key for p in processes],
        "enrich_pdf": enrich_pdf,
        "total_bruto_listing": len(processes),
        "total_discarded_all": len(discarded),
        "discarded": discarded,
        "total_standardized": len(raw_rows),
        "validacao_counts": {"valido": val_ok, "incompleto": inc_ok},
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler IME — Militar/Aeroespacial (CFG, CFrm, CG, CP)")
    ap.add_argument("--max-items", type=int, default=10)
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--no-pdf", action="store_true", help="Não baixar PDFs")
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ime"),
    )
    args = ap.parse_args()

    out_root = Path(args.output_root)
    std_dir = out_root / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)
    std_path = std_dir / f"{FONT}_standardized.json"

    try:
        report = run_crawl(
            max_items=args.max_items,
            sleep_s=args.sleep,
            processes=DEFAULT_PROCESSES,
            enrich_pdf=not args.no_pdf,
        )
    except Exception as exc:
        err_payload = {"erro": str(exc)}
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "crawler_summary.json").write_text(
            json.dumps(err_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1

    rows = report.pop("standardized")
    std_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {**report, "standardized_path": str(std_path.resolve()), "exemplos_payload": rows[:3]}
    (out_root / "crawler_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    vc = summary.get("validacao_counts") or {}
    md = [
        "# Crawler Wave 2 — Militar/Aeroespacial — IME",
        "",
        f"- **Fonte:** `{FONT}`",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Válidos:** {vc.get('valido', 0)} | **Incompletos:** {vc.get('incompleto', 0)}",
        "",
        "Ver `docs/CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_IME_CRAWLER.md`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
