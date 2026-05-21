#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto Wave 2 — Vestibulares / Ingresso (UFRGS — CV / COPERSE).

Diagnóstico (2026):
- Legado `www.ufrgs.br/cv/` instável/inacessível em vários clientes HTTP.
- Portal ativo: **vestibular.ufrgs.br** (hub) → páginas **WordPress** em `www.ufrgs.br/coperse/`
  (Coordenação de Processos Seletivos de Graduação — sucessor do CV).
- Processos: vestibular, PSU/extravestibular, processos seletivos específicos; editais em PDF
  (`wp-content/uploads/...`).
- `www.ufrgs.br/vestibular/cv20xx/` — frequentemente **403** a bots; preferir COPERSE.
- Extração PDF opcional (sem OCR) via helpers de `fgv_edital_dates.py`.

Saída: `fonte=ufrgs_cv`, `fonte_tipo=universidade`.
"""
from __future__ import annotations

import argparse
import html as html_module
import json
import re
import sys
import time
import unicodedata
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
    fetch_pdf_bytes_capped,
    fgv_schedule_from_text,
)

BASE_HUB = "https://vestibular.ufrgs.br"
BASE_COPERSE = "https://www.ufrgs.br/coperse"
DEFAULT_LISTINGS = (
    BASE_COPERSE + "/concurso-vestibular/",
    BASE_COPERSE + "/sobre-o-vestibular-2/",
    BASE_HUB + "/",
)
KNOWN_PROCESS_URLS = (
    BASE_COPERSE + "/concurso-vestibular/",
    BASE_COPERSE + "/sobre-o-vestibular-2/",
    BASE_COPERSE + "/processo-seletivo-simplificado-cln-2026-1/",
    BASE_COPERSE + "/processo-seletivo-estudantes-indigenas/",
    BASE_COPERSE + "/psu-2024-extravestibular/",
    BASE_COPERSE + "/processo-seletivo-especifico-para-ingresso-de-estudantes-indigenas-2024/",
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "ufrgs_cv"
INSTITUICAO = "Universidade Federal do Rio Grande do Sul"
ORGAO = "UFRGS"
BANCA = "CV/UFRGS — COPERSE"
ESTADO = "RS"
MUNICIPIO = "Porto Alegre"

_RE_INSC_DE_ATE = re.compile(
    r"[Dd]e\s+(\d{2}/\d{2}/\d{4})\s+\d{1,2}:\d{2}\s+a\s+(\d{2}/\d{2}/\d{4})",
    re.I,
)
_RE_INSC_DE_A_MES = re.compile(
    r"(?i)de\s+(\d{1,2})\s+a\s+(\d{1,2})\s+de\s+"
    r"(janeiro|fevereiro|mar[cç]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
    r"\s+de\s+(\d{4})",
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
_RE_YEAR_IN_PATH = re.compile(r"(?:20(2[4-9]|3[0-9]))|(?:cv-20\d{2})|(?:psu-20\d{2})", re.I)
_EXCLUDE_PATH_PARTS = (
    "/concurso-vestibular-anteriores",
    "/aquisicao-de-provas/",
    "/cv-201",
    "/cv-2020",
    "/cv-2021",
    "/cv-2022",
    "/cv-2023",
    "/extravestibular-201",
    "/psu-201",
    "/psu-2020",
    "/psu-2022",
    "/psu-2023",
    "/faqwd/",
    "/wp-json/",
    "/wp-content/themes/",
    "/wp-admin/",
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


def _unescape(s: str) -> str:
    return html_module.unescape(s or "")


def _month_token(tok: str) -> Optional[int]:
    t = unicodedata.normalize("NFD", (tok or "").strip())
    t = "".join(c for c in t if c.isalpha()).lower()
    for name, num in _MESES.items():
        if t.startswith(name[:3]):
            return num
    return _MESES.get(t)


def _fetch(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Referer": BASE_HUB + "/",
        },
    )
    with urlopen(req, timeout=45) as resp:
        raw = resp.read()
    for enc in ("utf-8", "iso-8859-1", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def _load_robots_parser(base: str):
    from urllib.robotparser import RobotFileParser

    netloc = urlparse(base).netloc
    raw = ""
    for scheme in ("https", "http"):
        robots_url = f"{scheme}://{netloc}/robots.txt"
        try:
            req = Request(robots_url, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=20) as r:
                raw = r.read().decode("utf-8", "replace")
            break
        except Exception:
            continue
    if not raw.strip():
        return None
    if "user-agent:" not in raw.lower():
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


def _is_process_url(url: str) -> bool:
    low = url.lower().split("#")[0]
    if not low.startswith("http"):
        return False
    if "ufrgs.br" not in low:
        return False
    for ex in _EXCLUDE_PATH_PARTS:
        if ex in low:
            return False
    if "facebook" in low or "twitter" in low or "mailto:" in low:
        return False
    host = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    if host == "vestibular.ufrgs.br" and path in ("", "/"):
        return False
    if "/coperse/" not in low and "vestibular.ufrgs" not in host:
        return False
    if re.search(
        r"vestibular|concurso-vestibular|processo-seletivo|psu-|pse-|extravestibular|/cv-20",
        path,
    ):
        if _RE_YEAR_IN_PATH.search(low) or "concurso-vestibular" in path:
            return True
        if "processo-seletivo" in path and re.search(r"20(2[4-9]|3[0-9])", low):
            return True
    return False


def _collect_process_urls(html: str, page_url: str, robots_parser) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[str] = []
    seen: Set[str] = set()
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href or href.startswith("#"):
            continue
        full = urljoin(page_url, href).split("#")[0].rstrip("/")
        if not _is_process_url(full):
            continue
        if full in seen:
            continue
        if _robots_disallows(full, robots_parser):
            continue
        seen.add(full)
        out.append(full)
    return out


def _parse_inscricao_dates(blob: str) -> Tuple[Optional[str], Optional[str]]:
    blob = normalize_text(_unescape(blob))
    m = _RE_INSC_DE_ATE.search(blob)
    if m:
        return _br_slash_to_iso(m.group(1)), _br_slash_to_iso(m.group(2))
    m2 = _RE_INSC_DE_A_MES.search(blob)
    if m2:
        try:
            d1, d2 = int(m2.group(1)), int(m2.group(2))
            mo = _month_token(m2.group(3))
            y = int(m2.group(4))
            if mo:
                return date(y, mo, d1).isoformat(), date(y, mo, d2).isoformat()
        except ValueError:
            pass
    sch = fgv_schedule_from_text(blob)
    return sch.get("data_inicio_inscricao"), sch.get("data_fim_inscricao")


def _pick_edital_pdf(soup: BeautifulSoup, page_url: str) -> Optional[str]:
    best: Optional[str] = None
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href.lower().endswith(".pdf"):
            continue
        full = urljoin(page_url, href).split("#")[0]
        if "ufrgs.br" not in full.lower():
            continue
        label = normalize_text(_unescape(a.get_text(" ", strip=True))).lower()
        path_low = full.lower()
        if re.search(r"edital|manual\s+do\s+candidato|guia", label + " " + path_low):
            if "edital" in label or "edital" in path_low:
                if "retifica" not in label or best is None:
                    return full
            if best is None and "manual" in label:
                best = full
    return best


def _pdf_schedule(pdf_url: str, referer: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"pdf_fetch_note": "", "schedule": {}}
    try:
        raw, note = fetch_pdf_bytes_capped(
            pdf_url,
            referer=referer,
            max_bytes=6 * 1024 * 1024,
            timeout_s=35,
        )
        out["pdf_fetch_note"] = note
        if not raw:
            return out
        text = extract_pdf_text_fgv(raw)
        out["pdf_text_len"] = len(text or "")
        out["schedule"] = fgv_schedule_from_text(text or "")
    except Exception as exc:
        out["pdf_fetch_note"] = f"erro:{exc}"
    return out


def _page_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        t = normalize_text(_unescape(h1.get_text(" ", strip=True)))
        if t and len(t) > 3:
            return t
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return normalize_text(_unescape(og["content"]))
    if soup.title:
        t = normalize_text(_unescape(soup.title.get_text(strip=True)))
        return re.sub(r"\s*[\|\-–]\s*COPERSE.*$", "", t, flags=re.I).strip()
    return ""


def _body_text(soup: BeautifulSoup) -> str:
    node = (
        soup.select_one(".entry-content")
        or soup.select_one("article")
        or soup.select_one("main")
        or soup.find("body")
    )
    if not node:
        return ""
    for bad in node.find_all(["script", "style", "nav", "footer", "header"]):
        bad.decompose()
    return normalize_text(_unescape(node.get_text(" ", strip=True)))[:30000]


def _infer_tipo(titulo: str, body: str) -> Tuple[str, str]:
    blob = f"{titulo}\n{body}".lower()
    if re.search(r"processo\s+seletivo|psu\b|pse\b|extravestibular|vagas\s+suplementares", blob):
        return "programa_ingresso", "texto:processo_seletivo_ufrgs"
    if "vestibular" in blob:
        return "vestibular", "texto:vestibular"
    return "vestibular", "fallback:vestibular_ufrgs"


def ufrgs_should_discard(titulo: str, body: str) -> Tuple[bool, str]:
    blob = f"{titulo}\n{body}".lower()
    if re.search(r"\bedi[cç][oõ]es\s+anteriores\b", titulo.lower()):
        return True, "ufrgs_edicao_anterior"
    if re.search(r"\baquisi[cç][aã]o\s+de\s+provas\b", blob):
        return True, "ufrgs_aquisicao_provas_arquivo"
    if re.search(r"inscri[cç][oõ]es\s+encerrad", blob) and not re.search(
        r"de\s+\d{1,2}\s+a\s+\d{1,2}\s+de\s+\w+\s+de\s+20\d{2}", blob
    ):
        if not re.search(r"\d{2}/\d{2}/20(2[6-9]|3\d)", blob):
            return True, "ufrgs_inscricoes_encerradas"
    return False, ""


def parse_ufrgs_process(
    url: str,
    *,
    enrich_pdf: bool = True,
    max_pdf_mb: float = 6.0,
) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    tit = _page_title(soup) or url
    body = _body_text(soup)
    blob = f"{tit}\n{body}"

    data_inicio, data_fim = _parse_inscricao_dates(blob)
    data_prova = extract_prova_from_text(blob)
    sch_notes: List[str] = []

    edital = _pick_edital_pdf(soup, url)
    pdf_meta: Dict[str, Any] = {}
    if enrich_pdf and edital and (not data_fim or not data_prova):
        pdf_meta = _pdf_schedule(edital, referer=url)
        sch = pdf_meta.get("schedule") or {}
        sch_notes = list(sch.get("schedule_notes") or [])
        if not data_inicio and sch.get("data_inicio_inscricao"):
            data_inicio = sch["data_inicio_inscricao"]
        if not data_fim and sch.get("data_fim_inscricao"):
            data_fim = sch["data_fim_inscricao"]
        if not data_prova and sch.get("data_prova"):
            data_prova = sch["data_prova"]

    if not data_fim:
        data_fim = extract_inscricao_fim_explicit_br(blob)

    dates_iso = parse_all_dates_br(blob)
    data_pub = dates_iso[0].isoformat() if dates_iso else None
    _, _, taxa, money_meta = parse_remuneracao_taxa_br(blob)
    tipo, tipo_evid = _infer_tipo(tit, body)

    curso: Optional[str] = None
    m = re.search(
        r"(?i)(?:curso|bacharelado|licenciatura)\s+(?:em|de)\s+([A-Za-zÀ-ÿ][^\n.;]{3,80})",
        blob,
    )
    if m:
        curso = m.group(1).strip()[:200]

    return {
        "titulo": tit,
        "body": body,
        "tipo_selecao": tipo,
        "tipo_evidencia": tipo_evid,
        "data_inicio_inscricao": data_inicio,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "link_edital": edital,
        "curso": curso,
        "pdf_meta": pdf_meta,
        "schedule_notes": sch_notes,
    }


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    listing_urls: Tuple[str, ...],
    enrich_pdf: bool,
) -> Dict[str, Any]:
    rp = _load_robots_parser("https://www.ufrgs.br")

    all_urls: List[str] = []
    seen: Set[str] = set()
    for u in KNOWN_PROCESS_URLS:
        k = u.rstrip("/")
        if k not in seen:
            seen.add(k)
            all_urls.append(k)

    for listing_url in listing_urls:
        if _robots_disallows(listing_url, rp):
            raise RuntimeError(f"robots.txt bloqueia listagem: {listing_url}")
        time.sleep(sleep_s)
        listing_html = _fetch(listing_url)
        for u in _collect_process_urls(listing_html, listing_url, rp):
            if u not in seen:
                seen.add(u)
                all_urls.append(u)

    urls = all_urls[: max(max_items * 3, 24)]
    today = date.today()
    raw_rows: List[Dict[str, Any]] = []
    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for url in urls:
        if len(raw_rows) >= max_items:
            break
        if _robots_disallows(url, rp):
            discarded.append({"url": url, "motivo": "robots_disallow"})
            continue
        try:
            time.sleep(sleep_s)
            parsed = parse_ufrgs_process(url, enrich_pdf=enrich_pdf)
            tit = parsed["titulo"]
            body = parsed["body"]

            drop, why = ufrgs_should_discard(tit, body)
            if drop:
                discarded.append({"url": url, "titulo": tit, "motivo": why})
                continue

            data_inicio = parsed["data_inicio_inscricao"]
            data_fim = parsed["data_fim_inscricao"]
            data_prova = parsed["data_prova"]
            data_pub = parsed["data_publicacao"]
            off = parsed["link_edital"]

            drop_r, why_r = recency_should_discard(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
                text_for_recent_heuristic=f"{tit} {body}",
            )
            if drop_r:
                discarded.append({"url": url, "titulo": tit, "motivo": why_r})
                continue

            taxa = parsed["taxa_inscricao"]
            money_meta = parsed.get("money_meta") or {}
            tipo = parsed["tipo_selecao"]
            tipo_evid = parsed.get("tipo_evidencia") or ""

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
                salario_max=None,
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
                salario_min=None,
                salario_max=None,
                taxa_inscricao=taxa,
            )
            if validacao == "valido" and qualidade == "baixa":
                qualidade = "media"
            elif not data_fim and off:
                qualidade = "media"
            elif not off and not data_fim:
                qualidade = "baixa"

            notes = list(money_meta.get("value_extraction_notes") or [])
            notes.extend(parsed.get("schedule_notes") or [])
            if not off:
                notes.append("edital_pdf_nao_encontrado_no_html")
            pdf_meta = parsed.get("pdf_meta") or {}
            if pdf_meta.get("pdf_fetch_note"):
                notes.append(f"pdf:{pdf_meta['pdf_fetch_note']}")
            confidence = pci_adjust_confidence_for_ambiguity(confidence, value_extraction_notes=notes)

            extracted_fields: List[str] = []
            if data_fim:
                extracted_fields.append("data_fim_inscricao_texto")
            if data_inicio:
                extracted_fields.append("data_inicio_inscricao_texto")
            if data_prova:
                extracted_fields.append("data_prova_texto")
            if taxa is not None:
                extracted_fields.append("taxa_inscricao_texto")
            if off:
                extracted_fields.append("link_edital_pdf")

            extras: Dict[str, Any] = {
                "crawler": "main_vestibulares_ufrgs",
                "wave": "concursos_wave2_vestibulares_ufrgs",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "listing_urls": list(listing_urls),
                "portal_hub": BASE_HUB,
                "coperse_base": BASE_COPERSE,
                "official_link_missing": off is None,
                "extracted_fields": sorted(set(extracted_fields)),
                "missing_core_fields": missing_core,
                "extraction_confidence": confidence,
                "source_is_aggregator": False,
                "value_extraction_notes": notes,
                "tipo_selecao_evidencia": tipo_evid,
                "pdf_enrichment": pdf_meta,
                "nota_cv_coperse": (
                    "Conteúdo oficial migrado para www.ufrgs.br/coperse; vestibular.ufrgs.br é hub."
                ),
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
                categoria="vestibular_ufrgs_cv",
                orgao=ORGAO,
                instituicao=INSTITUICAO,
                banca=BANCA,
                cargo=None,
                curso=parsed.get("curso"),
                area=None,
                nivel_escolaridade="ensino_medio",
                estado=ESTADO,
                municipio=MUNICIPIO,
                numero_vagas=None,
                salario_min=None,
                salario_max=None,
                taxa_inscricao=taxa,
                data_publicacao=data_pub,
                data_inicio_inscricao=data_inicio,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                link_edital=off,
                tags=["ufrgs", "ufrgs_cv", "coperse", "wave2", "vestibular"],
            )
            verr = validate_concurso_item(row)
            if verr:
                errors.append({"url": url, "erros": verr})
                continue
            raw_rows.append(row)
        except Exception as exc:
            errors.append({"url": url, "erro": str(exc)})

    filled, missing = field_fill_stats(raw_rows)
    return {
        "fonte": FONT,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "listing_urls": list(listing_urls),
        "known_process_urls": list(KNOWN_PROCESS_URLS),
        "total_bruto_urls": len(urls),
        "total_discarded_all": len(discarded),
        "discarded": discarded[:200],
        "total_standardized": len(raw_rows),
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
        "diagnostico_portal": {
            "hub": BASE_HUB,
            "coperse": BASE_COPERSE,
            "cv_legado": "www.ufrgs.br/cv/ inacessível em testes HTTP",
            "tipo_conteudo": "HTML WordPress + PDF editais",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler Wave 2 — Vestibulares UFRGS (CV/COPERSE)")
    ap.add_argument("--max-items", type=int, default=12)
    ap.add_argument("--sleep", type=float, default=1.5)
    ap.add_argument("--listings", type=str, default=",".join(DEFAULT_LISTINGS))
    ap.add_argument("--no-pdf", action="store_true", help="Não baixar PDF para enriquecer datas")
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave2_vestibulares_ufrgs"),
    )
    args = ap.parse_args()

    listing_urls = tuple(x.strip() for x in str(args.listings).split(",") if x.strip())
    out_root = Path(args.output_root)
    std_dir = out_root / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)
    std_path = std_dir / f"{FONT}_standardized.json"

    try:
        report = run_crawl(
            max_items=args.max_items,
            sleep_s=args.sleep,
            listing_urls=listing_urls,
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

    val_ok = sum(1 for r in rows if r.get("validacao_status") == "valido")
    md = [
        "# Crawler Wave 2 — Vestibulares UFRGS (CV / COPERSE)",
        "",
        f"- **Fonte:** `{FONT}`",
        f"- **Hub:** {BASE_HUB}",
        f"- **Coleta (UTC):** `{summary['collected_at_utc']}`",
        f"- **URLs candidatas:** {summary.get('total_bruto_urls', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)} (`valido`: {val_ok})",
        "",
        "## Loader dry-run",
        "",
        "```bash",
        "python scripts/load_concursos_selecao.py --dry-run \\",
        "  --input-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_ufrgs/standardized \\",
        "  --output-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_ufrgs/loader_dryrun \\",
        "  --sources ufrgs_cv",
        "```",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
