#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — sub-wave Militar/Aeroespacial: ITA Vestibular.

Diagnóstico (2026):
- Portal legado em frames: `vestibular.ita.br` (topo.htm + principal.htm).
- Edital PDF em `instrucoes/edital_2026_retificado.pdf` (topo); cronograma na principal (provas 2026).
- PDF escaneado (sem texto extraível) — datas de inscrição via HTML limitadas.
- `fonte=ita`, `tipo_selecao=vestibular`, `categoria=militar_aeroespacial_ita_vestibular`.

IME: `concursos/main_militar_aeroespacial_ime.py` — ver `docs/CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_IME_CRAWLER.md`.
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

BASE = "https://www.vestibular.ita.br"
DEFAULT_SEEDS = (
    f"{BASE}/principal.htm",
    f"{BASE}/topo.htm",
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "ita"
ORGAO = "Instituto Tecnológico de Aeronáutica (ITA)"
INSTITUICAO = "Instituto Tecnológico de Aeronáutica"
BANCA = "ITA — Comissão de Vestibular"
ESTADO = "SP"
MUNICIPIO = "São José dos Campos"
PDF_MAX_BYTES = 6 * 1024 * 1024
PDF_TIMEOUT_S = 40.0

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

_RE_VEST_YEAR = re.compile(r"vestibular\s+(\d{4})", re.I)
_RE_PROVA_1_FASE = re.compile(
    r"1[aªº]?\s*fase\s*:?\s*(\d{1,2})\s+set\s+(\d{4})",
    re.I,
)
_RE_PROVA_2_FASE = re.compile(
    r"2[aªº]?\s*fase\s*:?\s*(\d{1,2})\s+a\s+(\d{1,2})\s+out\s+(\d{4})",
    re.I,
)
_RE_NON_OPP = (
    r"gabarito\s+definitivo",
    r"resultado\s+final",
    r"classifica[cç][aã]o\s+final",
)


def _unescape(s: str) -> str:
    return html_module.unescape(s or "")


def _fetch(url: str) -> str:
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
        raw = resp.read()
    for enc in ("iso-8859-1", "utf-8", "latin-1"):
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


def _pick_edital_pdf(soup: BeautifulSoup, page_url: str) -> Optional[str]:
    candidates: List[Tuple[int, str]] = []
    for a in soup.find_all("a", href=True):
        href = urljoin(page_url, a["href"]).split("#")[0]
        if ".pdf" not in href.lower():
            continue
        label = normalize_text(_unescape(a.get_text(" ", strip=True))).lower()
        score = 0
        if "edital" in label:
            score += 5
        if "retific" in label:
            score += 1
        if "programa" in label or "matérias" in label or "materias" in label:
            score -= 3
        if "orienta" in label and "reda" in label:
            score -= 3
        if score > 0:
            candidates.append((score, href))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (-x[0], x[1]))
    return candidates[0][1]


def _parse_vestibular_year(blob: str) -> Optional[int]:
    m = _RE_VEST_YEAR.search(blob)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return None


def _parse_prova_dates(blob: str) -> Tuple[Optional[str], Optional[str]]:
    """Retorna (1ª fase ISO, 2ª fase fim ISO)."""
    p1: Optional[str] = None
    p2_end: Optional[str] = None
    m1 = _RE_PROVA_1_FASE.search(blob)
    if m1:
        try:
            p1 = date(int(m1.group(2)), 9, int(m1.group(1))).isoformat()
        except ValueError:
            pass
    m2 = _RE_PROVA_2_FASE.search(blob)
    if m2:
        try:
            p2_end = date(int(m2.group(3)), 10, int(m2.group(2))).isoformat()
        except ValueError:
            pass
    return p1, p2_end


def ita_should_discard_non_opportunity(*, titulo: str, body: str) -> Tuple[bool, str]:
    blob = f"{titulo}\n{body}".lower()
    for pat in _RE_NON_OPP:
        if re.search(pat, blob, re.I):
            return True, "ita_nao_oportunidade_ativa"
    return False, ""


def _enrich_pdf(pdf_url: str, referer: str) -> Tuple[Optional[str], Optional[str], Optional[str], Dict[str, Any]]:
    meta: Dict[str, Any] = {"pdf_url": pdf_url}
    raw, note = fetch_pdf_bytes_capped(
        pdf_url,
        referer=referer,
        max_bytes=PDF_MAX_BYTES,
        timeout_s=PDF_TIMEOUT_S,
    )
    meta["fetch_note"] = note
    if not raw:
        return None, None, None, meta
    text = extract_pdf_text_fgv(raw)
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


def parse_ita_vestibular(
    *,
    principal_html: str,
    topo_html: str,
    principal_url: str,
    enrich_pdf: bool,
) -> Dict[str, Any]:
    soup_p = BeautifulSoup(principal_html, "html.parser")
    soup_t = BeautifulSoup(topo_html, "html.parser")
    body = normalize_text(_unescape(soup_p.get_text(" ", strip=True)))
    topo_text = normalize_text(_unescape(soup_t.get_text(" ", strip=True)))
    blob = f"{body}\n{topo_text}"

    year = _parse_vestibular_year(blob) or 2027
    titulo = f"ITA — Vestibular {year}"
    prova1, prova2_fim = _parse_prova_dates(blob)
    data_prova = prova1 or prova2_fim or extract_prova_from_text(blob)

    off = _pick_edital_pdf(soup_t, f"{BASE}/topo.htm") or _pick_edital_pdf(soup_p, principal_url)
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    pdf_meta: Dict[str, Any] = {}
    if off and enrich_pdf:
        di, df, dp, pdf_meta = _enrich_pdf(off, referer=principal_url)
        data_inicio = di
        data_fim = df or extract_inscricao_fim_explicit_br(blob)
        if dp and not data_prova:
            data_prova = dp
    else:
        data_fim = extract_inscricao_fim_explicit_br(blob)

    sal_min, sal_max, taxa, money_meta = parse_remuneracao_taxa_br(blob)
    dates_iso = parse_all_dates_br(blob)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    return {
        "titulo": titulo,
        "body": body,
        "tipo_selecao": "vestibular",
        "curso": "Graduação em Engenharia (vestibular ITA)",
        "area": "Engenharia / Aeroespacial",
        "nivel_escolaridade": "medio",
        "data_inicio_inscricao": data_inicio,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_prova_2_fase_fim": prova2_fim,
        "data_publicacao": data_pub,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "link_edital": off,
        "link": principal_url,
        "pdf_meta": pdf_meta,
        "vestibular_year": year,
    }


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    seed_urls: Tuple[str, ...],
    enrich_pdf: bool,
) -> Dict[str, Any]:
    rp = _load_robots_parser(BASE)
    for u in seed_urls:
        if _robots_disallows(u, rp):
            raise RuntimeError(f"robots bloqueia URL: {u}")

    time.sleep(sleep_s)
    principal_url = f"{BASE}/principal.htm"
    topo_url = f"{BASE}/topo.htm"
    principal_html = _fetch(principal_url)
    time.sleep(sleep_s)
    topo_html = _fetch(topo_url)

    parsed = parse_ita_vestibular(
        principal_html=principal_html,
        topo_html=topo_html,
        principal_url=principal_url,
        enrich_pdf=enrich_pdf,
    )

    today = date.today()
    raw_rows: List[Dict[str, Any]] = []
    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    url = parsed["link"]
    tit = parsed["titulo"]
    body = parsed.get("body") or ""

    drop_no, why_no = ita_should_discard_non_opportunity(titulo=tit, body=body)
    if drop_no:
        discarded.append({"url": url, "titulo": tit, "motivo": why_no})
    else:
        data_fim = parsed.get("data_fim_inscricao")
        data_prova = parsed.get("data_prova")
        drop_r, why_r = recency_should_discard(
            data_fim_inscricao=data_fim,
            data_prova=data_prova,
            today=today,
            text_for_recent_heuristic=f"{tit} {body} vestibular {parsed.get('vestibular_year')}",
        )
        if drop_r:
            discarded.append({"url": url, "titulo": tit, "motivo": why_r})
        else:
            off = parsed.get("link_edital")
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
                data_publicacao=parsed.get("data_publicacao"),
                numero_vagas=None,
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
            if parsed.get("pdf_meta", {}).get("text_len", 0) < 80:
                notes.append("edital_pdf_sem_texto_extraivel")
            notes.extend(money_meta.get("value_extraction_notes") or [])

            extras: Dict[str, Any] = {
                "crawler": "main_militar_aeroespacial_ita",
                "wave": "concursos_wave2_militar_aeroespacial_ita",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "seed_urls": list(seed_urls),
                "pdf_enrichment": parsed.get("pdf_meta") or {},
                "data_prova_2_fase_fim": parsed.get("data_prova_2_fase_fim"),
                "vestibular_year": parsed.get("vestibular_year"),
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
                fonte_tipo="instituicao",
                tipo_selecao=parsed.get("tipo_selecao") or "vestibular",
                status=status,
                validacao_status=validacao,
                qualidade_dado=qualidade,
                extras=extras,
                categoria="militar_aeroespacial_ita_vestibular",
                orgao=ORGAO,
                instituicao=INSTITUICAO,
                banca=BANCA,
                cargo=None,
                curso=parsed.get("curso"),
                area=parsed.get("area"),
                nivel_escolaridade=parsed.get("nivel_escolaridade"),
                estado=ESTADO,
                municipio=MUNICIPIO,
                numero_vagas=None,
                salario_min=parsed.get("salario_min"),
                salario_max=parsed.get("salario_max"),
                taxa_inscricao=parsed.get("taxa_inscricao"),
                data_publicacao=parsed.get("data_publicacao"),
                data_inicio_inscricao=parsed.get("data_inicio_inscricao"),
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                link_edital=off,
                tags=["ita", "vestibular", "militar_aeroespacial", "wave2"],
            )
            verr = validate_concurso_item(row)
            if verr:
                errors.append({"url": url, "erros": verr})
            else:
                raw_rows.append(row)

    filled, missing = field_fill_stats(raw_rows)
    val_ok = sum(1 for r in raw_rows if r.get("validacao_status") == "valido")
    inc_ok = sum(1 for r in raw_rows if r.get("validacao_status") == "incompleto")
    return {
        "fonte": FONT,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed_urls": list(seed_urls),
        "enrich_pdf": enrich_pdf,
        "total_bruto_listing": 1,
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
    ap = argparse.ArgumentParser(description="Crawler piloto ITA Vestibular (militar/aeroespacial)")
    ap.add_argument("--max-items", type=int, default=5)
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--no-pdf", action="store_true", help="Não baixar PDF do edital")
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave2_militar_aeroespacial_ita"),
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
            seed_urls=DEFAULT_SEEDS,
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
        "# Crawler Wave 2 — Militar/Aeroespacial — ITA Vestibular",
        "",
        f"- **Fonte:** `{FONT}`",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Válidos:** {vc.get('valido', 0)} | **Incompletos:** {vc.get('incompleto', 0)}",
        "",
        "Ver `docs/CONCURSOS_WAVE2_MILITAR_AEROESPACIAL_ITA_CRAWLER.md`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
