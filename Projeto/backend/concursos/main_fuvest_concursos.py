#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto Wave 2 — Fuvest (USP).

Hubs confirmados:
- vestibular-da-usp → vestibular
- concursos → concurso_publico / processo_seletivo
- residencia → residencia
- pos-graduacao → programa_ingresso

Nota: fuvest.br pode falhar verificação SSL em alguns ambientes Windows;
o crawler usa contexto SSL dedicado (conservador, só para este host).
"""
from __future__ import annotations

import argparse
import html as html_module
import json
import re
import ssl
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
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
    infer_tipo_selecao_meta,
    normalize_text,
    parse_all_dates_br,
    parse_remuneracao_taxa_br,
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

BASE = "https://www.fuvest.br"
FUVEST_HUBS: Tuple[Tuple[str, str, str, str], ...] = (
    (f"{BASE}/vestibular-da-usp", "vestibular", "Vestibular USP — Fuvest", "vestibular"),
    (f"{BASE}/concursos/", "concurso_publico", "Concursos públicos USP — Fuvest", "concursos"),
    (f"{BASE}/residencia/", "residencia", "Residência USP — Fuvest", "residencia"),
    (f"{BASE}/pos-graduacao/", "programa_ingresso", "Pós-graduação USP — Fuvest", "pos"),
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "fuvest"
ORGAO = "Fuvest — Fundação Universitária para o Vestibular"
INSTITUICAO = "Universidade de São Paulo (USP)"
BANCA = "Fuvest"
ESTADO = "SP"
MUNICIPIO = "São Paulo"

_SSL_CTX = ssl.create_default_context()
try:
    _SSL_CTX.check_hostname = True
    _SSL_CTX.verify_mode = ssl.CERT_REQUIRED
except Exception:
    pass
# Ambientes sem cadeia ICP-Brasil: fallback só para fuvest.br
_SSL_FUVEST = ssl._create_unverified_context()

_RE_INSC_DE_ATE_SLASH = re.compile(
    r"(\d{2}/\d{2}/\d{4})\s+at[eé]\s+(\d{2}/\d{2}/\d{4})",
    re.I,
)
_RE_FUVEST_INSC_HOR = re.compile(
    r"(?:inscri[cç][ãa]o|per[ií]odo)\s*:?\s*das\s+\d{1,2}h\s+de\s+(\d{2}/\d{2}/\d{4})"
    r"\s+at[eé]\s+as\s+\d{1,2}h\s+de\s+(\d{2}/\d{2}/\d{4})",
    re.I,
)
_RE_INSC_DE_ATE_MES = re.compile(
    r"[Dd]e\s+(\d{1,2})\s+a\s+(\d{1,2})\s+de\s+"
    r"(janeiro|fevereiro|mar[cç]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
    r"\s+de\s+(\d{4})",
    re.I,
)
_MESES = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}
_RE_NON_OPP = (
    r"\bresultado\s+final\b",
    r"\bgabarito\s+definitivo\b",
    r"\blista\s+(?:de\s+)?classificat",
    r"\bconvoca[cç][aã]o\s+para\s+matr[ií]cula\b",
    r"\bdivulga[cç][aã]o\s+do\s+resultado\b",
)
_NEWS_SLUG_MARKERS = (
    "lista-",
    "motion-",
    "divulga-",
    "convocad",
    "resultado-",
    "notas-da",
    "publicacao-das",
    "candidatos-poderao",
    "candidatos-excedentes",
)


def _br_slash_to_iso(s: str) -> Optional[str]:
    parts = (s or "").strip().split("/")
    if len(parts) != 3:
        return None
    try:
        d, mo, y = int(parts[0]), int(parts[1]), int(parts[2])
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def _mes_ano_to_iso(dia: int, mes_nome: str, ano: int) -> Optional[str]:
    mo = _MESES.get(mes_nome.lower().replace("ç", "c"))
    if not mo:
        return None
    try:
        return date(ano, mo, dia).isoformat()
    except ValueError:
        return None


def _unescape(s: str) -> str:
    return html_module.unescape(s or "")


def _fetch(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        },
    )
    last_exc: Optional[Exception] = None
    for ctx in (_SSL_CTX, _SSL_FUVEST):
        try:
            with urlopen(req, timeout=45, context=ctx) as resp:
                raw = resp.read()
            for enc in ("utf-8", "iso-8859-1", "latin-1"):
                try:
                    return raw.decode(enc)
                except UnicodeDecodeError:
                    continue
            return raw.decode("utf-8", "replace")
        except ssl.SSLError as exc:
            last_exc = exc
            continue
        except Exception as exc:
            last_exc = exc
            if "certificate" in str(exc).lower():
                continue
            raise
    if last_exc:
        raise last_exc
    raise RuntimeError(f"falha ao obter {url}")


def _fetch_pdf_capped(url: str, *, referer: str, max_bytes: int = 6 * 1024 * 1024) -> Tuple[Optional[bytes], str]:
    if not url or not url.lower().startswith("http"):
        return None, "pdf_url_invalida"
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/pdf,*/*;q=0.8",
        "Referer": referer or url,
    }
    for ctx in (_SSL_CTX, _SSL_FUVEST):
        try:
            req = Request(url, headers=headers)
            out = bytearray()
            with urlopen(req, timeout=35, context=ctx) as resp:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    out.extend(chunk)
                    if len(out) > max_bytes:
                        return None, f"pdf_download_ultrapassou_{max_bytes}_bytes"
            raw = bytes(out)
            if len(raw) < 100 or raw[:4] != b"%PDF":
                return None, "pdf_resposta_nao_pdf_ou_muito_pequena"
            return raw, "pdf_download_ok"
        except Exception as exc:
            err = str(exc)
            if "certificate" in err.lower() or isinstance(exc, ssl.SSLError):
                continue
            return None, f"pdf_download_erro:{exc.__class__.__name__}"
    return None, "pdf_download_erro:ssl"


def _parse_inscricao_dates(blob: str) -> Tuple[Optional[str], Optional[str]]:
    blob = normalize_text(_unescape(blob))
    m = _RE_FUVEST_INSC_HOR.search(blob)
    if m:
        return _br_slash_to_iso(m.group(1)), _br_slash_to_iso(m.group(2))
    m2 = _RE_INSC_DE_ATE_SLASH.search(blob)
    if m2:
        return _br_slash_to_iso(m2.group(1)), _br_slash_to_iso(m2.group(2))
    m3 = _RE_INSC_DE_ATE_MES.search(blob)
    if m3:
        d1, d2, mes, ano = int(m3.group(1)), int(m3.group(2)), m3.group(3), int(m3.group(4))
        return _mes_ano_to_iso(d1, mes, ano), _mes_ano_to_iso(d2, mes, ano)
    sch = fgv_schedule_from_text(blob)
    return sch.get("data_inicio_inscricao"), sch.get("data_fim_inscricao")


def _pick_edital_pdf(soup: BeautifulSoup, page_url: str) -> Optional[str]:
    candidates: List[Tuple[int, str]] = []
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href.lower().endswith(".pdf"):
            continue
        full = urljoin(page_url, href).split("#")[0]
        label = normalize_text(_unescape(a.get_text(" ", strip=True))).lower()
        path = full.lower()
        score = 0
        if "edital" in label or "edital" in path:
            score += 10
        if "abertura" in label or "abertura" in path:
            score += 6
        if "retific" in path:
            score += 2
        if "gabarito" in label or "chamada" in path or "resolucao" in path:
            score -= 15
        if "provao" in path:
            score -= 10
        if score > 0:
            candidates.append((score, full))
    if not candidates:
        return None
    candidates.sort(key=lambda x: -x[0])
    return candidates[0][1]


def _body_text(soup: BeautifulSoup) -> str:
    node = soup.select_one("main") or soup.select_one(".entry-content") or soup.find("article")
    if not node:
        node = soup.body
    if not node:
        return ""
    for bad in node.find_all(["script", "style", "nav", "footer"]):
        bad.decompose()
    return normalize_text(_unescape(node.get_text(" ", strip=True)))[:25000]


def _page_title(soup: BeautifulSoup, fallback: str) -> str:
    h1 = soup.find("h1")
    if h1:
        t = normalize_text(_unescape(h1.get_text(" ", strip=True)))
        if t and len(t) > 4:
            return t
    if soup.title:
        t = normalize_text(_unescape(soup.title.get_text(strip=True)))
        t = re.sub(r"\s*[\|\-–]\s*Fuvest.*$", "", t, flags=re.I).strip()
        if t:
            return t
    return fallback


def _slug(path: str) -> str:
    return (path or "").strip("/").split("/")[-1].lower()


def _is_pagination_url(url: str) -> bool:
    p = urlparse(url).path.rstrip("/")
    return bool(re.search(r"/(residencia|pos-graduacao|concursos)/\d+$", p))


def _is_news_slug(slug: str) -> bool:
    if any(m in slug for m in _NEWS_SLUG_MARKERS):
        return True
    if slug.count("-") >= 6 and re.search(r"20\d{2}", slug):
        return True
    return False


def collect_child_urls(html: str, hub_url: str, hub_kind: str) -> List[Tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[Tuple[str, str]] = []
    seen: Set[str] = set()
    hub_path = urlparse(hub_url).path.strip("/").lower()

    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        full = urljoin(hub_url, href).split("#")[0].rstrip("/")
        if "fuvest.br" not in urlparse(full).netloc.lower():
            continue
        if _is_pagination_url(full):
            continue
        path = urlparse(full).path
        sl = _slug(path)
        if not sl or sl == hub_path.split("/")[-1]:
            continue
        if "acervo" in sl:
            continue
        label = normalize_text(_unescape(a.get_text(" ", strip=True)))

        keep = False
        if hub_kind == "vestibular":
            keep = False
        elif hub_kind == "concursos":
            keep = bool(
                re.search(
                    r"^(auxiliar|tecnico|educador|especialista|medico)-",
                    sl,
                )
                and re.search(r"-20\d{2}", sl)
            )
        elif hub_kind == "residencia":
            keep = sl.startswith("residencia-") and not _is_news_slug(sl)
            keep = keep or sl in (
                "residencia-medica",
                "residencia-medica-hracusp",
                "residencia-ipusp",
                "residencia-area-profissional-da-saude",
            )
        elif hub_kind == "pos":
            keep = (
                ("pos" in sl or "inscric" in sl or "processo-seletivo" in sl)
                and re.search(r"20(2[4-9])", sl)
                and not _is_news_slug(sl)
            )
        if not keep:
            continue
        if full in seen:
            continue
        seen.add(full)
        out.append((full, label or sl))
    return out


def fuvest_should_discard(titulo: str, body: str, *, link_edital: Optional[str], data_fim: Optional[str]) -> Tuple[bool, str]:
    if data_fim or link_edital:
        return False, ""
    blob = f"{titulo}\n{body}".lower()
    for pat in _RE_NON_OPP:
        if re.search(pat, blob, re.I):
            return True, "fuvest_nao_oportunidade_ativa"
    if re.search(r"inscri[cç][oõ]es\s+encerrad", blob) and not re.search(r"\d{2}/\d{2}/20(2[4-9])", blob):
        return True, "fuvest_inscricoes_encerradas_sem_data"
    return False, ""


def _categoria_for_tipo(tipo: str) -> str:
    return {
        "vestibular": "vestibular_usp",
        "concurso_publico": "concurso_fuvest_usp",
        "processo_seletivo": "processo_seletivo_fuvest_usp",
        "residencia": "residencia_usp",
        "programa_ingresso": "pos_graduacao_usp",
    }.get(tipo, "fuvest_processo")


def parse_fuvest_page(
    url: str,
    *,
    tipo_default: str,
    titulo_default: str,
    hub_kind: str,
    enrich_pdf: bool = True,
) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    tit = _page_title(soup, titulo_default)
    body = _body_text(soup)
    blob = f"{tit}\n{body}"

    tipo = tipo_default
    if hub_kind == "concursos":
        tipo, _ = infer_tipo_selecao_meta(tit, body)
        if tipo not in ("concurso_publico", "processo_seletivo"):
            tipo = tipo_default

    data_inicio, data_fim = _parse_inscricao_dates(blob)
    if not data_fim:
        data_fim = extract_inscricao_fim_explicit_br(blob)
    data_prova = extract_prova_from_text(blob)
    if not data_prova:
        sch = fgv_schedule_from_text(blob)
        data_prova = sch.get("data_prova")

    dates_iso = parse_all_dates_br(blob)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    edital = _pick_edital_pdf(soup, url)
    pdf_meta: Dict[str, Any] = {}
    if enrich_pdf and edital and (not data_fim or not data_prova):
        raw, note = _fetch_pdf_capped(edital, referer=url)
        pdf_meta["fetch_note"] = note
        if raw:
            txt, _ = extract_pdf_text_fgv(raw)
            if txt:
                sch = fgv_schedule_from_text(txt)
                pdf_meta["schedule"] = sch
                if not data_inicio:
                    data_inicio = sch.get("data_inicio_inscricao")
                if not data_fim:
                    data_fim = sch.get("data_fim_inscricao")
                if not data_prova:
                    data_prova = sch.get("data_prova")

    sal_min, sal_max, taxa, money_meta = parse_remuneracao_taxa_br(blob)

    curso: Optional[str] = None
    if tipo == "vestibular":
        curso = "Graduação — Vestibular USP"
    elif tipo == "residencia":
        curso = tit[:200] if "residência" in tit.lower() or "residencia" in tit.lower() else "Residência USP"
    elif tipo == "programa_ingresso":
        curso = "Pós-graduação stricto sensu / lato sensu"

    return {
        "titulo": tit,
        "body": body,
        "tipo_selecao": tipo,
        "data_inicio_inscricao": data_inicio,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "link_edital": edital,
        "curso": curso,
        "pdf_meta": pdf_meta,
        "hub_kind": hub_kind,
    }


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    hubs: Tuple[Tuple[str, str, str, str], ...],
    enrich_pdf: bool,
) -> Dict[str, Any]:
    queue: List[Tuple[str, str, str, str, str]] = []
    seen_urls: Set[str] = set()

    for hub_url, tipo, titulo, kind in hubs:
        norm = hub_url.rstrip("/")
        if norm not in seen_urls:
            seen_urls.add(norm)
            queue.append((norm, tipo, titulo, kind, "hub"))
        try:
            time.sleep(sleep_s)
            html = _fetch(hub_url)
            for child_url, child_label in collect_child_urls(html, hub_url, kind):
                cu = child_url.rstrip("/")
                if cu not in seen_urls:
                    seen_urls.add(cu)
                    queue.append((cu, tipo, child_label or titulo, kind, "child"))
        except Exception:
            pass

    today = date.today()
    raw_rows: List[Dict[str, Any]] = []
    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for url, tipo_default, titulo_default, hub_kind, origin in queue:
        if len(raw_rows) >= max_items:
            break
        try:
            time.sleep(sleep_s)
            parsed = parse_fuvest_page(
                url,
                tipo_default=tipo_default,
                titulo_default=titulo_default,
                hub_kind=hub_kind,
                enrich_pdf=enrich_pdf,
            )
            tit = parsed["titulo"]
            body = parsed["body"]
            tipo = parsed["tipo_selecao"]
            data_fim = parsed["data_fim_inscricao"]
            off = parsed["link_edital"]

            drop, why = fuvest_should_discard(tit, body, link_edital=off, data_fim=data_fim)
            if drop:
                discarded.append({"url": url, "titulo": tit, "motivo": why, "origin": origin})
                continue

            data_inicio = parsed["data_inicio_inscricao"]
            data_prova = parsed["data_prova"]
            data_pub = parsed["data_publicacao"]

            drop_r, why_r = recency_should_discard(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
                text_for_recent_heuristic=f"{tit} {body}",
            )
            if drop_r:
                discarded.append({"url": url, "titulo": tit, "motivo": why_r, "origin": origin})
                continue

            status = infer_status_concurso(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
            )
            validacao = "valido" if (data_fim and off) else "incompleto"

            partial_core = {
                "data_fim_inscricao": data_fim,
                "data_prova": data_prova,
                "orgao": ORGAO,
                "estado": ESTADO,
                "instituicao": INSTITUICAO,
                "link_edital": off,
                "numero_vagas": None,
            }
            missing_core = pci_missing_core_fields(partial_core)
            confidence = pci_infer_extraction_confidence(
                orgao=ORGAO,
                instituicao=INSTITUICAO,
                estado=ESTADO,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                numero_vagas=None,
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
                data_publicacao=data_pub,
                numero_vagas=None,
                salario_min=parsed.get("salario_min"),
                salario_max=parsed.get("salario_max"),
                taxa_inscricao=parsed.get("taxa_inscricao"),
            )
            if validacao == "valido" and qualidade == "baixa":
                qualidade = "media"
            elif data_fim and not off:
                qualidade = "media"
            elif not data_fim:
                qualidade = "baixa" if qualidade == "media" else qualidade

            money_meta = parsed.get("money_meta") or {}
            notes = list(money_meta.get("value_extraction_notes") or [])
            if not off:
                notes.append("edital_pdf_nao_encontrado_no_html")
            if not data_fim:
                notes.append("data_fim_inscricao_ausente")
            pdf_meta = parsed.get("pdf_meta") or {}
            if pdf_meta.get("fetch_note"):
                notes.append(f"pdf:{pdf_meta['fetch_note']}")

            extracted_fields: List[str] = []
            if data_fim:
                extracted_fields.append("data_fim_inscricao")
            if data_inicio:
                extracted_fields.append("data_inicio_inscricao")
            if data_prova:
                extracted_fields.append("data_prova")
            if off:
                extracted_fields.append("link_edital")
            if parsed.get("taxa_inscricao") is not None:
                extracted_fields.append("taxa_inscricao")

            nivel = "ensino_medio" if tipo == "vestibular" else ("superior" if tipo in ("residencia", "programa_ingresso") else None)

            extras: Dict[str, Any] = {
                "crawler": "main_fuvest_concursos",
                "wave": "concursos_wave2_fuvest",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "fuvest_hub_kind": hub_kind,
                "fuvest_origin": origin,
                "pdf_enrichment": pdf_meta,
                "extracted_fields": sorted(set(extracted_fields)),
                "missing_core_fields": missing_core,
                "extraction_confidence": pci_adjust_confidence_for_ambiguity(
                    confidence, value_extraction_notes=notes
                ),
                "value_extraction_notes": notes,
            }
            row = build_concurso_item(
                titulo=tit[:500],
                link=url,
                fonte=FONT,
                fonte_tipo="universidade",
                tipo_selecao=tipo,
                status=status,
                validacao_status=validacao,
                qualidade_dado=qualidade,
                extras=extras,
                categoria=_categoria_for_tipo(tipo),
                orgao=ORGAO,
                instituicao=INSTITUICAO,
                banca=BANCA,
                cargo=None,
                curso=parsed.get("curso"),
                area="USP",
                nivel_escolaridade=nivel,
                estado=ESTADO,
                municipio=MUNICIPIO,
                numero_vagas=None,
                salario_min=parsed.get("salario_min"),
                salario_max=parsed.get("salario_max"),
                taxa_inscricao=parsed.get("taxa_inscricao"),
                data_publicacao=data_pub,
                data_inicio_inscricao=data_inicio,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                link_edital=off,
                tags=["fuvest", "usp", "wave2", hub_kind],
            )
            verr = validate_concurso_item(row)
            if verr:
                errors.append({"url": url, "erros": verr})
                continue
            raw_rows.append(row)
        except Exception as exc:
            errors.append({"url": url, "erro": str(exc), "origin": origin})

    filled, missing = field_fill_stats(raw_rows)
    return {
        "fonte": FONT,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "hubs": [{"url": u, "tipo": t, "kind": k} for u, t, _, k in hubs],
        "total_urls_candidatas": len(queue),
        "total_discarded_all": len(discarded),
        "discarded": discarded[:200],
        "total_standardized": len(raw_rows),
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler Wave 2 — Fuvest (USP)")
    ap.add_argument("--max-items", type=int, default=12)
    ap.add_argument("--sleep", type=float, default=1.5)
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave2_fuvest"),
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
            hubs=FUVEST_HUBS,
            enrich_pdf=not args.no_pdf,
        )
    except Exception as exc:
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "crawler_summary.json").write_text(
            json.dumps({"erro": str(exc)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1

    rows = report.pop("standardized")
    std_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {**report, "standardized_path": str(std_path.resolve()), "exemplos_payload": rows[:3]}
    (out_root / "crawler_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    val_ok = sum(1 for r in rows if r.get("validacao_status") == "valido")
    md = [
        "# Crawler Wave 2 — Fuvest (USP)",
        "",
        f"- **Fonte:** `{FONT}`",
        f"- **Standardized:** {summary.get('total_standardized', 0)} (`valido`: {val_ok})",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        "",
        "Ver `docs/CONCURSOS_WAVE2_FUVEST_CRAWLER.md`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
