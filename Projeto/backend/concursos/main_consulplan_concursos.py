#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — Instituto Consulplan (ASP.NET — concursosNovo.aspx).

Diagnóstico (2026):
- Listagem única: `concursosNovo.aspx` com três blocos server-side:
  - `PanelRepeaterAbertas_e_Aguardando` (abertas/aguardando)
  - `PanelRepeaterAndamento` (em andamento)
  - `PanelRepeaterConcluidos` (encerrados — **ignorado**)
- Detalhe: `getConc.aspx?key=...` — título, botão inscrição, tabela de publicações (PDF CDN).
- Datas: frequentemente só no PDF do edital; enriquecimento conservador via `fgv_edital_dates`.
- robots.txt: inexistente (404); excluímos `/admin/`, `/painel/` no código.

Saída: `fonte=consulplan`, `categoria=banca_consulplan_concurso`.
"""
from __future__ import annotations

import argparse
import html as html_module
import json
import re
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
    infer_nivel_escolaridade,
    infer_orgao_local_from_title,
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
    fetch_pdf_bytes_capped,
    fgv_schedule_from_text,
)

BASE = "https://institutoconsulplan.org.br"
DEFAULT_LISTING = f"{BASE}/concursosNovo.aspx"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "consulplan"
BANCA = "Instituto Consulplan"
PDF_MAX_BYTES = 6 * 1024 * 1024
PDF_TIMEOUT_S = 35.0

LISTING_PANELS: Dict[str, str] = {
    "ContentPlaceHolder1_PanelRepeaterAbertas_e_Aguardando": "abertas",
    "ContentPlaceHolder1_PanelRepeaterAndamento": "andamento",
}

_EXCLUDE_PATH_PREFIXES = ("/painel/", "/admin/", "/login/")

_RE_NON_OPP = (
    r"^\s*resultado\s+final\s*$",
    r"divulga[cç][aã]o\s+do\s+gabarito",
    r"gabarito\s+definitivo",
    r"convoca[cç][aã]o\s+para\s+t[ií]tulos?",
    r"homologa[cç][aã]o\s+final",
    r"classifica[cç][aã]o\s+final",
    r"lista\s+de\s+aprovados",
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


def _fetch(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Referer": DEFAULT_LISTING,
        },
    )
    with urlopen(req, timeout=45) as resp:
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
            with urlopen(req, timeout=15) as r:
                if r.status >= 400:
                    continue
                raw = r.read().decode("utf-8", "replace")
            break
        except Exception:
            continue
    if not raw.strip() or "user-agent:" not in raw.lower():
        return None
    rp = RobotFileParser()
    rp.parse(raw.splitlines())
    return rp


def _robots_disallows(url: str, robots_parser) -> bool:
    path = urlparse(url).path.lower()
    if any(path.startswith(p) for p in _EXCLUDE_PATH_PREFIXES):
        return True
    if robots_parser is None:
        return False
    try:
        return not robots_parser.can_fetch(USER_AGENT, url)
    except Exception:
        return True


def _is_allowed_detail_url(url: str) -> bool:
    p = urlparse(url)
    if p.netloc and "institutoconsulplan.org.br" not in p.netloc.lower():
        return False
    return "getconc.aspx" in (p.path or "").lower()


def collect_listing_cards(html: str, listing_url: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[Dict[str, str]] = []
    seen: Set[str] = set()
    for panel_id, secao in LISTING_PANELS.items():
        panel = soup.find(id=panel_id)
        if not panel:
            continue
        for thumb in panel.select("div.thumbnail"):
            h5 = thumb.select_one("h5")
            h6 = thumb.select_one("h6")
            a = thumb.select_one("a[href*='getConc.aspx']")
            if not a:
                continue
            href = (a.get("href") or "").strip()
            full = urljoin(listing_url, href).split("#")[0]
            if not _is_allowed_detail_url(full):
                continue
            key = full.lower()
            if key in seen:
                continue
            seen.add(key)
            orgao = normalize_text(_unescape(h5.get_text(" ", strip=True) if h5 else ""))
            cargo = normalize_text(_unescape(h6.get_text(" ", strip=True) if h6 else ""))
            out.append(
                {
                    "url": full,
                    "orgao": orgao,
                    "cargo": cargo,
                    "secao_listagem": secao,
                }
            )
    return out


def _pick_edital_pdf(soup: BeautifulSoup) -> Optional[str]:
    candidates: List[Tuple[int, str]] = []
    for tr in soup.select("table tr"):
        links = tr.find_all("a", href=True)
        if not links:
            continue
        label = normalize_text(_unescape(links[0].get_text(" ", strip=True))).lower()
        href = (links[0].get("href") or "").strip()
        if ".pdf" not in href.lower():
            continue
        if "pdfviewer" in href.lower():
            continue
        score = 0
        if "edital" in label:
            score += 4
        if "abertura" in label:
            score += 3
        if "retifica" in label:
            score -= 2
        if "gabarito" in label or "resultado" in label or "convoca" in label:
            score -= 5
        if score > 0:
            candidates.append((score, href.split("#")[0]))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (-x[0], x[1]))
    return candidates[0][1]


def consulplan_should_discard_publication_label(label: str) -> Tuple[bool, str]:
    blob = (label or "").lower()
    for pat in _RE_NON_OPP:
        if re.search(pat, blob, re.I):
            return True, "consulplan_publicacao_nao_oportunidade"
    return False, ""


def consulplan_should_discard_non_opportunity(*, titulo: str, body: str) -> Tuple[bool, str]:
    blob = f"{titulo}\n{body}".lower()
    for pat in _RE_NON_OPP:
        if re.search(pat, blob, re.I):
            return True, "consulplan_nao_oportunidade_ativa"
    return False, ""


def _enrich_from_pdf(
    pdf_url: str, referer: str
) -> Tuple[Optional[str], Optional[str], Optional[str], Dict[str, Any]]:
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
    if not text:
        return None, None, None, meta
    sched = fgv_schedule_from_text(text)
    meta["schedule_notes"] = sched.get("notes") or []
    return (
        sched.get("data_inicio_inscricao"),
        sched.get("data_fim_inscricao"),
        sched.get("data_prova"),
        meta,
    )


def parse_consulplan_detail(
    url: str,
    listing_meta: Dict[str, str],
    *,
    enrich_pdf: bool,
) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    lbl = soup.select_one("#ContentPlaceHolder1_lblNomeConcurso")
    nome = normalize_text(_unescape(lbl.get_text(" ", strip=True))) if lbl else ""
    orgao = listing_meta.get("orgao") or nome
    cargo = listing_meta.get("cargo") or ""
    titulo = f"{orgao} — {cargo}".strip(" —") if orgao and cargo else (nome or orgao or url)

    body_node = soup.select_one("div.container") or soup.find("body")
    body = ""
    if body_node:
        for bad in body_node.find_all(["script", "style"]):
            bad.decompose()
        body = normalize_text(_unescape(body_node.get_text(" ", strip=True)))[:25000]

    for tr in soup.select("table tr"):
        first_a = tr.find("a", href=True)
        if first_a:
            lab = normalize_text(_unescape(first_a.get_text(" ", strip=True)))
            drop, _ = consulplan_should_discard_publication_label(lab)
            if drop and "edital" not in lab.lower():
                continue

    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    data_prova: Optional[str] = None
    data_inicio, data_fim = _parse_inscricao_from_body(body)
    if not data_fim:
        data_fim = extract_inscricao_fim_explicit_br(body)
    data_prova = extract_prova_from_text(body)
    dates_iso = parse_all_dates_br(body)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    off = _pick_edital_pdf(soup)
    sal_min, sal_max, taxa_meta, money_meta = parse_remuneracao_taxa_br(body)
    pdf_meta: Dict[str, Any] = {}
    if enrich_pdf and off and ".pdf" in off.lower() and not data_fim:
        di, df, dp, pdf_meta = _enrich_from_pdf(off, referer=url)
        data_inicio = data_inicio or di
        data_fim = data_fim or df
        data_prova = data_prova or dp

    tipo_selecao, tipo_evid = infer_tipo_selecao_meta(f"{titulo}\n{cargo}", body)
    loc = infer_orgao_local_from_title(f"{titulo}\n{orgao}")
    nivel = infer_nivel_escolaridade(titulo, body)

    has_inscricao_btn = bool(soup.select_one("#ContentPlaceHolder1_btnInscricao"))

    return {
        "titulo": titulo,
        "orgao": orgao or nome,
        "instituicao": orgao or nome,
        "cargo": cargo or None,
        "body": body,
        "tipo_selecao": tipo_selecao,
        "tipo_selecao_evidencia": tipo_evid,
        "data_inicio_inscricao": data_inicio,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa_meta,
        "money_meta": money_meta,
        "link_edital": off,
        "numero_vagas": None,
        "estado": loc.get("estado"),
        "municipio": loc.get("municipio"),
        "nivel_escolaridade": nivel,
        "secao_listagem": listing_meta.get("secao_listagem"),
        "has_inscricao_btn": has_inscricao_btn,
        "pdf_meta": pdf_meta,
    }


def _parse_inscricao_from_body(body: str) -> Tuple[Optional[str], Optional[str]]:
    m = re.search(
        r"(?i)inscri[cç][oõ]es?\s*:?\s*"
        r"(\d{2}/\d{2}/\d{4})\s+\d{1,2}:\d{2}\s+a\s+"
        r"(\d{2}/\d{2}/\d{4})\s+\d{1,2}:\d{2}",
        body or "",
    )
    if m:
        return _br_slash_to_iso(m.group(1)), _br_slash_to_iso(m.group(2))
    m2 = re.search(
        r"(?i)(?:per[ií]odo\s+de\s+)?inscri[cç][oõ]es[^\d]{0,40}"
        r"(\d{2}/\d{2}/\d{4})\s+a\s+(\d{2}/\d{2}/\d{4})",
        body or "",
    )
    if m2:
        return _br_slash_to_iso(m2.group(1)), _br_slash_to_iso(m2.group(2))
    return None, None


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    listing_url: str,
    enrich_pdf: bool,
) -> Dict[str, Any]:
    rp = _load_robots_parser(BASE)
    if _robots_disallows(listing_url, rp):
        raise RuntimeError(f"robots bloqueia listagem: {listing_url}")

    time.sleep(sleep_s)
    listing_html = _fetch(listing_url)
    cards = collect_listing_cards(listing_html, listing_url)

    today = date.today()
    raw_rows: List[Dict[str, Any]] = []
    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for meta in cards:
        if len(raw_rows) >= max_items:
            break
        url = meta["url"]
        if _robots_disallows(url, rp):
            discarded.append({"url": url, "motivo": "robots_disallow"})
            continue
        try:
            time.sleep(sleep_s)
            parsed = parse_consulplan_detail(url, meta, enrich_pdf=enrich_pdf)
            tit = parsed["titulo"]
            body = parsed.get("body") or ""

            drop_no, why_no = consulplan_should_discard_non_opportunity(titulo=tit, body=body)
            if drop_no:
                discarded.append({"url": url, "titulo": tit, "motivo": why_no})
                continue

            data_fim = parsed.get("data_fim_inscricao")
            data_prova = parsed.get("data_prova")
            off = parsed.get("link_edital")
            secao = meta.get("secao_listagem") or ""

            # Painel «abertas»: manter como incompleto se houver edital ou inscrição ativa.
            skip_recency = secao == "abertas" and bool(off or parsed.get("has_inscricao_btn"))
            if not skip_recency:
                drop_r, why_r = recency_should_discard(
                    data_fim_inscricao=data_fim,
                    data_prova=data_prova,
                    today=today,
                    text_for_recent_heuristic=f"{tit} {body} {meta.get('cargo', '')}",
                )
                if drop_r:
                    discarded.append({"url": url, "titulo": tit, "motivo": why_r})
                    continue

            validacao = "valido" if off and data_fim else "incompleto"
            status = infer_status_concurso(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
            )
            orgao = parsed.get("orgao")
            instituicao = parsed.get("instituicao") or orgao
            estado = parsed.get("estado")
            municipio = parsed.get("municipio")
            sal_min = parsed.get("salario_min")
            sal_max = parsed.get("salario_max")
            taxa = parsed.get("taxa_inscricao")
            vagas = parsed.get("numero_vagas")
            money_meta = parsed.get("money_meta") or {}

            missing_core = pci_missing_core_fields(
                {
                    "orgao": orgao,
                    "instituicao": instituicao,
                    "estado": estado,
                    "data_fim_inscricao": data_fim,
                    "data_prova": data_prova,
                    "link_edital": off,
                    "numero_vagas": vagas,
                }
            )
            confidence = pci_infer_extraction_confidence(
                orgao=orgao,
                instituicao=instituicao,
                estado=estado,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                numero_vagas=vagas,
                salario_max=sal_max,
            )
            qualidade = pci_infer_qualidade_dado(
                titulo=tit,
                link=url,
                orgao=orgao,
                instituicao=instituicao,
                estado=estado,
                municipio=municipio,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                data_publicacao=parsed.get("data_publicacao"),
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
            )
            if validacao == "incompleto" and off:
                qualidade = "media" if qualidade == "alta" else qualidade

            notes = list(money_meta.get("value_extraction_notes") or [])
            if not off:
                notes.append("edital_pdf_nao_encontrado_no_html")
            if parsed.get("pdf_meta"):
                notes.append(f"pdf_enrich:{parsed['pdf_meta'].get('fetch_note', 'ok')}")

            extras: Dict[str, Any] = {
                "crawler": "main_consulplan_concursos",
                "wave": "concursos_wave2_consulplan",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "listing_url": listing_url,
                "secao_listagem": parsed.get("secao_listagem"),
                "has_inscricao_btn": parsed.get("has_inscricao_btn"),
                "pdf_enrichment": parsed.get("pdf_meta") or {},
                "missing_core_fields": missing_core,
                "extraction_confidence": pci_adjust_confidence_for_ambiguity(
                    confidence, value_extraction_notes=notes
                ),
                "value_extraction_notes": notes,
                "tipo_selecao_evidencia": parsed.get("tipo_selecao_evidencia"),
            }

            row = build_concurso_item(
                titulo=tit[:500],
                link=url,
                fonte=FONT,
                fonte_tipo="banca",
                tipo_selecao=parsed.get("tipo_selecao") or "concurso_publico",
                status=status,
                validacao_status=validacao,
                qualidade_dado=qualidade,
                extras=extras,
                categoria="banca_consulplan_concurso",
                orgao=orgao,
                instituicao=instituicao,
                banca=BANCA,
                cargo=parsed.get("cargo"),
                area=None,
                nivel_escolaridade=parsed.get("nivel_escolaridade"),
                estado=estado,
                municipio=municipio,
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
                data_publicacao=parsed.get("data_publicacao"),
                data_inicio_inscricao=parsed.get("data_inicio_inscricao"),
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                link_edital=off,
                tags=["consulplan", "banca", "wave2"],
            )
            verr = validate_concurso_item(row)
            if verr:
                errors.append({"url": url, "erros": verr})
                continue
            raw_rows.append(row)
        except Exception as exc:
            errors.append({"url": url, "erro": str(exc)})

    filled, missing = field_fill_stats(raw_rows)
    val_ok = sum(1 for r in raw_rows if r.get("validacao_status") == "valido")
    inc_ok = sum(1 for r in raw_rows if r.get("validacao_status") == "incompleto")
    return {
        "fonte": FONT,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "listing_url": listing_url,
        "enrich_pdf": enrich_pdf,
        "total_bruto_listing": len(cards),
        "total_discarded_all": len(discarded),
        "discarded": discarded[:200],
        "total_standardized": len(raw_rows),
        "validacao_counts": {"valido": val_ok, "incompleto": inc_ok},
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler piloto Consulplan → standardized JSON")
    ap.add_argument("--max-items", type=int, default=10)
    ap.add_argument("--sleep", type=float, default=2.0)
    ap.add_argument("--listing", type=str, default=DEFAULT_LISTING)
    ap.add_argument(
        "--no-pdf",
        action="store_true",
        help="Não baixar PDF para extrair datas quando o HTML não tiver data_fim",
    )
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave2_consulplan"),
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
            listing_url=args.listing.strip(),
            enrich_pdf=not args.no_pdf,
        )
    except Exception as exc:
        err_payload = {"erro": str(exc), "listing": args.listing}
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "crawler_summary.json").write_text(
            json.dumps(err_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1

    rows = report.pop("standardized")
    std_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        **report,
        "standardized_path": str(std_path.resolve()),
        "exemplos_payload": rows[:3],
    }
    (out_root / "crawler_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    vc = summary.get("validacao_counts") or {}
    md = [
        "# Crawler Wave 2 — Instituto Consulplan",
        "",
        f"- **Fonte:** `{FONT}` | **banca:** {BANCA}",
        f"- **Listagem:** `{args.listing}`",
        f"- **PDF enrich:** {not args.no_pdf}",
        f"- **Candidatos (abertas+andamento):** {summary.get('total_bruto_listing', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Válidos:** {vc.get('valido', 0)} | **Incompletos:** {vc.get('incompleto', 0)}",
        "",
        "Ver `docs/CONCURSOS_WAVE2_CONSULPLAN_CRAWLER.md`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
