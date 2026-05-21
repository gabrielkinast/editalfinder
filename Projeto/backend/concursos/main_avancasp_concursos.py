#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — Avança SP (portal oficial avancasp.org.br).

Diagnóstico (2026):
- Portal: `https://www.avancasp.org.br` — CMS ProSeleta / selecao.net (mesma família Quadrix/Objetiva/IBFC).
- Listagem piloto: `/index/abertos/` (inscrições abertas).
- Detalhe: `/informacoes/{id}/` — `#TopoInformacoes`, `p.insc`, `#blocoPublicacoes`, `#blocoEventos`,
  `#blocoListaVagas`; PDFs em CDN `anexos.cdn.selecao.net.br`.
- robots.txt: Disallow `/admin/*`, `/painel/*`, `/uploads/*` — listagem e detalhe permitidos.

Saída standardized para `scripts/load_concursos_selecao.py` (`fonte=avancasp`).
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

BASE = "https://www.avancasp.org.br"
DEFAULT_LISTINGS = (f"{BASE}/index/abertos/",)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "avancasp"
BANCA = "Avança SP"

_RE_INFO_PATH = re.compile(r"^/informacoes/(\d+)/?$", re.I)
_RE_INSC_RANGE = re.compile(
    r"(\d{2}/\d{2}/\d{4})\s+\d{1,2}:\d{2}\s+a\s+(\d{2}/\d{2}/\d{4})\s+\d{1,2}:\d{2}",
    re.I,
)
_RE_INSC_RANGE_DATE_ONLY = re.compile(
    r"(\d{2}/\d{2}/\d{4})\s+a\s+(\d{2}/\d{2}/\d{4})",
    re.I,
)
_RE_NON_OPP = (
    r"^\s*resultado\s+final\s*$",
    r"divulga[cç][aã]o\s+do\s+gabarito\s+definitivo",
    r"convoca[cç][aã]o\s+para\s+t[ií]tulos?\s*$",
)

_EXCLUDE_PATH_PREFIXES = ("/painel/", "/admin/", "/login/", "/uploads/")


def _br_slash_to_iso(s: str) -> Optional[str]:
    parts = (s or "").strip().split("/")
    if len(parts) != 3:
        return None
    try:
        d, mo, y = int(parts[0]), int(parts[1]), int(parts[2])
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def _unescape_html_entities(s: str) -> str:
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
    with urlopen(req, timeout=45) as resp:
        raw = resp.read()
    for enc in ("iso-8859-1", "utf-8", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "replace")


def _load_robots_parser(base: str):
    """Carrega robots.txt com User-Agent identificado (evita 403 do fetch padrão do RobotFileParser)."""
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
    if not raw.strip() or "user-agent:" not in raw.lower():
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


def _collect_informacao_urls(html: str, listing_url: str, robots_parser) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[str] = []
    seen: Set[str] = set()
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href or href.startswith("#"):
            continue
        full = urljoin(listing_url, href).split("#")[0]
        if not full.startswith(BASE):
            continue
        path = urlparse(full).path or ""
        if not _RE_INFO_PATH.match(path):
            continue
        if any(full.lower().startswith(BASE.lower() + p) for p in _EXCLUDE_PATH_PREFIXES):
            continue
        key = full.rstrip("/")
        if key in seen:
            continue
        if _robots_disallows(full, robots_parser):
            continue
        seen.add(key)
        out.append(full.rstrip("/"))
    return out


def _parse_inscricao_dates(soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
    p_insc = soup.select_one("p.insc")
    if p_insc:
        blob = normalize_text(_unescape_html_entities(p_insc.get_text(" ", strip=True)))
        m = _RE_INSC_RANGE.search(blob)
        if m:
            return _br_slash_to_iso(m.group(1)), _br_slash_to_iso(m.group(2))
        m2 = _RE_INSC_RANGE_DATE_ONLY.search(blob)
        if m2:
            return _br_slash_to_iso(m2.group(1)), _br_slash_to_iso(m2.group(2))
    p_per = soup.select_one("p.periodoInscricoes")
    if p_per:
        txt = normalize_text(_unescape_html_entities(p_per.get_text(" ", strip=True)))
        m3 = _RE_INSC_RANGE_DATE_ONLY.search(txt)
        if m3:
            return _br_slash_to_iso(m3.group(1)), _br_slash_to_iso(m3.group(2))
    return None, None


def _pick_edital_pdf(soup: BeautifulSoup, page_url: str) -> Optional[str]:
    root = soup.select_one("#blocoPublicacoes") or soup
    best: Optional[str] = None
    best_score = -1
    for li in root.select("li.pdf"):
        a = li.find("a", href=True)
        if not a:
            continue
        href = urljoin(page_url, (a.get("href") or "").strip()).split("#")[0]
        if ".pdf" not in href.lower():
            continue
        label = normalize_text(_unescape_html_entities(a.get_text(" ", strip=True))).lower()
        score = 0
        if re.search(r"(?i)\bedital\b", label):
            score += 3
        if "completo" in label or "abertura" in label:
            score += 2
        if "cronograma" in label or "retifica" in label:
            score -= 2
        if score > best_score:
            best_score = score
            best = href
    return best if best_score > 0 else best


def _cronograma_prova_objetiva_iso(soup: BeautifulSoup) -> Optional[str]:
    tbl = soup.select_one("#blocoEventos table.tabela")
    if not tbl:
        return None
    for tr in tbl.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        ev = normalize_text(_unescape_html_entities(tds[0].get_text(" ", strip=True))).lower()
        da_raw = normalize_text(_unescape_html_entities(tds[1].get_text(" ", strip=True)))
        if ("prova objetiva" in ev or "aplica" in ev and "prova" in ev) and "gabarito" not in ev:
            m = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", da_raw)
            if m:
                return _br_slash_to_iso(m.group(1))
    return None


def _vagas_count(soup: BeautifulSoup) -> int:
    n = 0
    for div in soup.select("#blocoListaVagas div.dados table tbody tr"):
        n += 1
    if n:
        return n
    return len(soup.select("#blocoListaVagas table tbody tr"))


def _taxa_from_vagas_table(soup: BeautifulSoup) -> Optional[float]:
    vals: List[float] = []
    for tr in soup.select("#blocoListaVagas table tbody tr"):
        tds = tr.find_all("td")
        if not tds:
            continue
        cell = tds[-1].get_text(" ", strip=True)
        _, _, taxa, _ = parse_remuneracao_taxa_br(cell + "\n")
        if taxa is not None:
            vals.append(taxa)
    if not vals:
        return None
    return min(vals)


def _situacao_text(soup: BeautifulSoup) -> str:
    p = soup.select_one("p.situacaoConcurso")
    if not p:
        return ""
    return normalize_text(_unescape_html_entities(p.get_text(" ", strip=True))).lower()


def avancasp_should_discard_situacao(situacao_lower: str) -> Tuple[bool, str]:
    if "encerr" in situacao_lower or "finaliz" in situacao_lower:
        return True, "avancasp_situacao_encerrada"
    if "cancel" in situacao_lower:
        return True, "avancasp_situacao_cancelada"
    if "suspen" in situacao_lower:
        return True, "avancasp_situacao_suspensa"
    return False, ""


def avancasp_should_discard_non_opportunity(*, titulo: str, body: str) -> Tuple[bool, str]:
    blob = f"{titulo}\n{body}".lower()
    for pat in _RE_NON_OPP:
        if re.search(pat, blob, re.I):
            return True, "avancasp_nao_oportunidade_ativa"
    if re.search(r"\bhomologa[cç][aã]o\s+final\b", blob) and "inscri" not in blob[:400]:
        return True, "avancasp_nao_oportunidade_ativa"
    return False, ""


def _nivel_from_vagas_table(soup: BeautifulSoup) -> Optional[str]:
    tr0 = soup.select_one("#blocoListaVagas table tbody tr")
    if not tr0:
        return None
    tds = tr0.find_all("td")
    if len(tds) < 3:
        return None
    esc = normalize_text(_unescape_html_entities(tds[2].get_text(" ", strip=True))).lower()
    if "médio" in esc or "medio" in esc:
        return "medio"
    if "superior" in esc:
        return "superior"
    if "técnico" in esc or "tecnico" in esc:
        return "tecnico"
    if "fundamental" in esc:
        return "fundamental"
    return None


def parse_avancasp_page(url: str) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    topo = soup.select_one("#TopoInformacoes .dados")
    tit = ""
    if topo:
        h2 = topo.find("h2")
        if h2:
            tit = normalize_text(_unescape_html_entities(h2.get_text(" ", strip=True)))
    if not tit:
        og = soup.find("meta", property="og:title")
        if og and og.get("content"):
            tit = normalize_text(_unescape_html_entities(og["content"]))
    tipo_label = ""
    ptipo = soup.select_one("#TopoInformacoes .dados p.tipo")
    if ptipo:
        tipo_label = normalize_text(_unescape_html_entities(ptipo.get_text(" ", strip=True)))

    body_node = soup.select_one("#pgInformacoes") or soup.find("main") or soup.find("body")
    body = ""
    if body_node:
        for bad in body_node.find_all(["script", "style"]):
            bad.decompose()
        body = normalize_text(_unescape_html_entities(body_node.get_text(" ", strip=True)))[:20000]

    blob = f"{tipo_label}\n{tit}\n{body}"
    data_inicio, data_fim = _parse_inscricao_dates(soup)
    if not data_fim:
        data_fim = extract_inscricao_fim_explicit_br(blob)
    data_prova = _cronograma_prova_objetiva_iso(soup) or extract_prova_from_text(blob)
    dates_iso = parse_all_dates_br(blob)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    nv = _vagas_count(soup)
    numero_vagas = nv if nv > 0 else None
    taxa_tbl = _taxa_from_vagas_table(soup)
    sal_min, sal_max, taxa_meta, money_meta = parse_remuneracao_taxa_br(blob)
    taxa = taxa_tbl if taxa_tbl is not None else taxa_meta

    situacao = _situacao_text(soup)
    edital = _pick_edital_pdf(soup, url)

    cargo_txt: Optional[str] = None
    tr0 = soup.select_one("#blocoListaVagas table tbody tr")
    if tr0:
        tds = tr0.find_all("td")
        if len(tds) >= 2:
            cargo_txt = normalize_text(_unescape_html_entities(tds[1].get_text(" ", strip=True)))
            if " - " in cargo_txt:
                cargo_txt = cargo_txt.split(" - ")[0].strip()[:400]

    return {
        "titulo": tit or url,
        "tipo_label": tipo_label,
        "body": body,
        "data_inicio_inscricao": data_inicio,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "numero_vagas": numero_vagas,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "link_edital": edital,
        "situacao_lower": situacao,
        "cargo_primeira_vaga": cargo_txt,
        "nivel_primeira_vaga": _nivel_from_vagas_table(soup),
    }


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    listing_urls: Tuple[str, ...],
) -> Dict[str, Any]:
    rp = _load_robots_parser(BASE)

    all_urls: List[str] = []
    seen: Set[str] = set()
    for listing_url in listing_urls:
        if _robots_disallows(listing_url, rp):
            raise RuntimeError(f"robots.txt bloqueia listagem: {listing_url}")
        time.sleep(sleep_s)
        listing_html = _fetch(listing_url)
        for u in _collect_informacao_urls(listing_html, listing_url, rp):
            if u not in seen:
                seen.add(u)
                all_urls.append(u)

    urls = all_urls[: max(max_items * 4, 32)]
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
            parsed = parse_avancasp_page(url)
            tit = parsed["titulo"]
            body = parsed["body"]

            drop_s, why_s = avancasp_should_discard_situacao(parsed.get("situacao_lower") or "")
            if drop_s:
                discarded.append({"url": url, "titulo": tit, "motivo": why_s})
                continue

            drop_no, why_no = avancasp_should_discard_non_opportunity(titulo=tit, body=body)
            if drop_no:
                discarded.append({"url": url, "titulo": tit, "motivo": why_no})
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

            vagas = parsed["numero_vagas"]
            sal_min = parsed["salario_min"]
            sal_max = parsed["salario_max"]
            taxa = parsed["taxa_inscricao"]
            money_meta = parsed.get("money_meta") or {}

            tipo, tipo_evid = infer_tipo_selecao_meta(f"{parsed.get('tipo_label') or ''} {tit}", body)
            status = infer_status_concurso(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
            )
            if data_fim and off:
                validacao = "valido"
            else:
                validacao = "incompleto"

            geo = infer_orgao_local_from_title(tit)
            orgao = geo["orgao"] or tit[:500]
            instituicao = geo["instituicao"] or orgao
            municipio = geo["municipio"]
            estado = geo["estado"]
            nivel = parsed.get("nivel_primeira_vaga") or infer_nivel_escolaridade(tit, body)

            partial_core: Dict[str, Any] = {
                "data_fim_inscricao": data_fim,
                "data_prova": data_prova,
                "orgao": orgao,
                "estado": estado,
                "instituicao": instituicao,
                "link_edital": off,
                "numero_vagas": vagas,
            }
            missing_core = pci_missing_core_fields(partial_core)
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
                data_publicacao=data_pub,
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
            )
            if off is None and not data_fim:
                qualidade = "baixa"
            elif not data_fim and off:
                qualidade = "media"
            if validacao == "valido":
                qualidade = pci_infer_qualidade_dado(
                    titulo=tit,
                    link=url,
                    orgao=orgao,
                    instituicao=instituicao,
                    estado=estado,
                    municipio=municipio,
                    data_fim_inscricao=data_fim,
                    data_prova=data_prova,
                    data_publicacao=data_pub,
                    numero_vagas=vagas,
                    salario_min=sal_min,
                    salario_max=sal_max,
                    taxa_inscricao=taxa,
                )
                if qualidade == "baixa":
                    qualidade = "media"

            notes = list(money_meta.get("value_extraction_notes") or [])
            if not off:
                notes.append("edital_pdf_nao_encontrado_no_html")
            confidence = pci_adjust_confidence_for_ambiguity(confidence, value_extraction_notes=notes)

            extracted_fields: List[str] = []
            if sal_min is not None or sal_max is not None:
                extracted_fields.append("salario_texto")
            if taxa is not None:
                extracted_fields.append("taxa_inscricao_texto")
            if data_prova:
                extracted_fields.append("data_prova_texto")
            if data_fim:
                extracted_fields.append("data_fim_inscricao_texto")
            if data_inicio:
                extracted_fields.append("data_inicio_inscricao_texto")
            if vagas is not None:
                extracted_fields.append("numero_vagas_texto")

            cargo_txt = parsed.get("cargo_primeira_vaga")

            extras: Dict[str, Any] = {
                "crawler": "main_avancasp_concursos",
                "wave": "concursos_wave2_avancasp",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "avancasp_listing_urls": list(listing_urls),
                "official_link_missing": off is None,
                "extracted_fields": sorted(set(extracted_fields)),
                "missing_core_fields": missing_core,
                "extraction_confidence": confidence,
                "source_is_aggregator": False,
                "value_extraction_notes": notes,
                "tipo_selecao_evidencia": tipo_evid,
                "possible_fee_detected": bool(money_meta.get("possible_fee_detected")),
                "possible_salary_detected": bool(money_meta.get("possible_salary_detected")),
                "avancasp_situacao": (parsed.get("situacao_lower") or "")[:200],
            }
            row = build_concurso_item(
                titulo=tit[:500],
                link=url,
                fonte=FONT,
                fonte_tipo="banca",
                tipo_selecao=tipo,
                status=status,
                validacao_status=validacao,
                qualidade_dado=qualidade,
                extras=extras,
                categoria="banca_avancasp_concurso",
                orgao=orgao,
                instituicao=instituicao,
                banca=BANCA,
                cargo=cargo_txt,
                area=None,
                nivel_escolaridade=nivel,
                estado=estado,
                municipio=municipio,
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
                data_publicacao=data_pub,
                data_inicio_inscricao=data_inicio,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                link_edital=off,
                tags=["avancasp", "banca", "wave2"],
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
        "listing_urls": list(listing_urls),
        "total_bruto_urls": len(urls),
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
    ap = argparse.ArgumentParser(description="Crawler piloto Avança SP → standardized JSON")
    ap.add_argument("--max-items", type=int, default=10, help="Máximo de concursos gravados")
    ap.add_argument("--sleep", type=float, default=2.0, help="Pausa entre GET (segundos)")
    ap.add_argument(
        "--listings",
        type=str,
        default=",".join(DEFAULT_LISTINGS),
        help="URLs de listagem separadas por vírgula",
    )
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave2_avancasp"),
        help="Pasta wave2 Avança SP",
    )
    args = ap.parse_args()

    listing_urls = tuple(x.strip() for x in str(args.listings).split(",") if x.strip())
    if not listing_urls:
        listing_urls = DEFAULT_LISTINGS

    out_root = Path(args.output_root)
    std_dir = out_root / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)
    std_path = std_dir / f"{FONT}_standardized.json"

    try:
        report = run_crawl(max_items=args.max_items, sleep_s=args.sleep, listing_urls=listing_urls)
    except Exception as exc:
        err_payload = {"erro": str(exc), "listing_urls": list(listing_urls)}
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "crawler_summary.json").write_text(
            json.dumps(err_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_root / "crawler_summary.md").write_text(
            f"# Crawler Avança SP — falha\n\n```json\n{json.dumps(err_payload, ensure_ascii=False, indent=2)}\n```\n"
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
        "# Crawler Wave 2 — Avança SP",
        "",
        f"- **Fonte:** `{FONT}` | **banca:** {BANCA}",
        f"- **Listagens:** `{args.listings}`",
        f"- **Coleta (UTC):** `{summary['collected_at_utc']}`",
        f"- **URLs candidatas (bruto):** {summary.get('total_bruto_urls', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Válidos:** {vc.get('valido', 0)} | **Incompletos:** {vc.get('incompleto', 0)}",
        f"- **Ficheiro:** `{std_path.as_posix()}`",
        "",
        "Ver `docs/CONCURSOS_WAVE2_AVANCASP_CRAWLER.md`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
