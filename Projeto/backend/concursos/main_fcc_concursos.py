#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — Fundação Carlos Chagas (FCC / concursosfcc.com.br).

Diagnóstico (2026):
- Listagem permitida: `concursoInscricaoAberta.html` (e `concursoEmAndamento.html`).
- Detalhe: `/concursos/{codigo}/index.html` — HTML com instituição, cargo, inscrições (box3),
  vencimento base, links/PDF (Rybená viewer), taxa.
- robots.txt: `Disallow: /concursos/` e `Disallow: /*.pdf$` — por defeito não segue detalhe/PDF;
  use `--allow-detail-despite-robots` apenas para piloto operador (sleep conservador).
- Sem API JSON pública.

Saída: `fonte=fcc`, `categoria=banca_fcc_concurso`, `fonte_tipo=banca`.
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
from urllib.parse import parse_qs, unquote, urljoin, urlparse
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

BASE = "https://www.concursosfcc.com.br"
DEFAULT_LISTINGS = (
    f"{BASE}/concursoInscricaoAberta.html",
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "fcc"
BANCA = "FCC"

_RE_DETAIL_PATH = re.compile(r"^/concursos/([a-z0-9]+)/index\.html?$", re.I)
_RE_INSC_TODOS = re.compile(
    r"per[ií]odo de inscri[cç][aã]o para todos os candidatos\s*:?\s*"
    r"(?:das?\s+\d{1,2}h\s+do\s+dia\s+)?(\d{2}/\d{2}/\d{4})[^\d]{0,80}"
    r"(?:às|as)\s+23h59min\s+do\s+dia\s+(\d{2}/\d{2}/\d{4})",
    re.I | re.DOTALL,
)
_RE_INSC_DE_ATE = re.compile(
    r"(?:das?\s+\d{1,2}h\s+do\s+dia\s+)?(\d{2}/\d{2}/\d{4})[^\d]{0,40}"
    r"(?:às|as)\s+23h59min\s+do\s+dia\s+(\d{2}/\d{2}/\d{4})",
    re.I,
)
_RE_NON_OPP = (
    r"^\s*resultado\s+final\s*$",
    r"divulga[cç][aã]o\s+do\s+gabarito",
    r"homologa[cç][aã]o\s+final",
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
            with urlopen(req, timeout=20) as r:
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


def _unwrap_pdf_href(href: str) -> str:
    h = (href or "").strip()
    if "file=" in h:
        q = parse_qs(urlparse(h).query)
        files = q.get("file") or []
        if files:
            return unquote(files[0])
    return h


def _collect_listing_items(html: str, listing_url: str) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[Dict[str, str]] = []
    seen: Set[str] = set()
    root = soup.select_one("#refazerLista") or soup
    for box in root.select("div.box5"):
        inst_a = box.select_one(".textoInstituicao2 a[href]")
        cargo_a = box.select_one(".textoConcurso2 a[href]")
        if not inst_a or not cargo_a:
            continue
        href = (inst_a.get("href") or cargo_a.get("href") or "").strip()
        if not href:
            continue
        full = urljoin(listing_url, href).split("#")[0]
        path = urlparse(full).path or ""
        if not _RE_DETAIL_PATH.match(path):
            continue
        key = full.rstrip("/").lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "url": full.rstrip("/"),
                "instituicao": normalize_text(_unescape(inst_a.get_text(" ", strip=True))),
                "cargo": normalize_text(_unescape(cargo_a.get_text(" ", strip=True))),
            }
        )
    return out


def _parse_inscricao_box(soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str], Optional[float]]:
    """Datas e taxa a partir do bloco «Inscrições (exclusivamente via Internet)»."""
    data_inicio: Optional[str] = None
    data_fim: Optional[str] = None
    taxa: Optional[float] = None
    blob = ""
    for el in soup.find_all(class_="rotuloTopico1"):
        if "inscri" not in normalize_text(el.get_text(" ", strip=True)).lower():
            continue
        nxt = el.find_next_sibling("div", class_="box3")
        if nxt:
            blob = normalize_text(_unescape(nxt.get_text("\n", strip=True)))
            break
    if not blob:
        for box in soup.select("div.box3"):
            t = normalize_text(_unescape(box.get_text("\n", strip=True)))
            if "valor da inscri" in t.lower() or "período de inscri" in t.lower():
                blob = t
                break
    if blob:
        m = _RE_INSC_TODOS.search(blob)
        if m:
            data_inicio, data_fim = _br_slash_to_iso(m.group(1)), _br_slash_to_iso(m.group(2))
        else:
            m2 = _RE_INSC_DE_ATE.search(blob)
            if m2:
                data_inicio, data_fim = _br_slash_to_iso(m2.group(1)), _br_slash_to_iso(m2.group(2))
        _, _, taxa_meta, _ = parse_remuneracao_taxa_br(blob)
        if taxa_meta is not None:
            taxa = taxa_meta
    return data_inicio, data_fim, taxa


def _salario_vencimento(soup: BeautifulSoup) -> Tuple[Optional[float], Optional[float]]:
    for rot in soup.find_all(class_="rotuloTopico1"):
        if "vencimento" not in normalize_text(rot.get_text(" ", strip=True)).lower():
            continue
        nxt = rot.find_next_sibling("div", class_="box2")
        if nxt:
            sal_min, sal_max, _, _ = parse_remuneracao_taxa_br(
                normalize_text(_unescape(nxt.get_text(" ", strip=True)))
            )
            if sal_min is not None or sal_max is not None:
                return sal_min, sal_max
    return None, None


def _pick_edital_link(soup: BeautifulSoup, page_url: str) -> Optional[str]:
    candidates: List[Tuple[int, str]] = []
    for block in soup.select("div.campoLinkArquivo"):
        a = block.find("a", href=True)
        if not a:
            continue
        label = normalize_text(_unescape(a.get_text(" ", strip=True))).lower()
        href = _unwrap_pdf_href(urljoin(page_url, a["href"]))
        if not href.lower().startswith("http"):
            continue
        score = 0
        if "edital" in label:
            score += 3
        if "abertura" in label or "abertura de inscri" in label:
            score += 5
        if "retifica" in label:
            score -= 2
        if href.lower().endswith(".pdf") or ".pdf" in href.lower():
            score += 2
        if score > 0:
            candidates.append((score, href))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (-x[0], x[1]))
    return candidates[0][1]


def _situacao_opcao(soup: BeautifulSoup) -> str:
    el = soup.select_one("#opcaoConcursos")
    if el:
        return normalize_text(_unescape(el.get_text(" ", strip=True))).lower()
    return ""


def _cargos_text(soup: BeautifulSoup) -> Optional[str]:
    for rot in soup.find_all(class_="rotuloTopico1"):
        if normalize_text(rot.get_text(" ", strip=True)).lower() != "cargos":
            continue
        nxt = rot.find_next_sibling("div", class_="box2")
        if not nxt:
            nxt = rot.find_next_sibling("div", class_="box2")
        if nxt:
            return normalize_text(_unescape(nxt.get_text(" ", strip=True)))[:800]
    return None


def fcc_should_discard_situacao(situacao: str) -> Tuple[bool, str]:
    s = (situacao or "").lower()
    if "encerr" in s or "finaliz" in s:
        return True, "fcc_situacao_encerrada"
    if "cancel" in s:
        return True, "fcc_situacao_cancelada"
    if "suspen" in s:
        return True, "fcc_situacao_suspensa"
    return False, ""


def fcc_should_discard_non_opportunity(*, titulo: str, body: str) -> Tuple[bool, str]:
    blob = f"{titulo}\n{body}".lower()
    for pat in _RE_NON_OPP:
        if re.search(pat, blob, re.I):
            return True, "fcc_nao_oportunidade_ativa"
    return False, ""


def parse_fcc_detail_page(url: str, listing_meta: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    inst = ""
    cargo = ""
    ti = soup.select_one("div.textoInstituicao")
    tc = soup.select_one("div.textoConcurso")
    if ti:
        inst = normalize_text(_unescape(ti.get_text(" ", strip=True)))
    if tc:
        cargo = normalize_text(_unescape(tc.get_text(" ", strip=True)))
    if listing_meta:
        inst = inst or listing_meta.get("instituicao") or ""
        cargo = cargo or listing_meta.get("cargo") or ""
    titulo = f"{inst} — {cargo}".strip(" —") if inst and cargo else (inst or cargo or url)

    body_node = soup.select_one("#centro2") or soup.find("body")
    body = ""
    if body_node:
        for bad in body_node.find_all(["script", "style"]):
            bad.decompose()
        body = normalize_text(_unescape(body_node.get_text(" ", strip=True)))[:25000]

    data_inicio, data_fim, taxa_box = _parse_inscricao_box(soup)
    if not data_fim:
        data_fim = extract_inscricao_fim_explicit_br(body)
    sal_min, sal_max = _salario_vencimento(soup)
    if sal_min is None and sal_max is None:
        sal_min, sal_max, _, _ = parse_remuneracao_taxa_br(body)
    taxa = taxa_box
    if taxa is None:
        _, _, taxa_meta, _ = parse_remuneracao_taxa_br(body)
        taxa = taxa_meta

    data_prova = extract_prova_from_text(body)
    dates_iso = parse_all_dates_br(body)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    edital = _pick_edital_link(soup, url)
    situacao = _situacao_opcao(soup)
    cargos_blob = _cargos_text(soup)
    cargo_field = cargo or None
    if cargos_blob and not cargo_field:
        cargo_field = cargos_blob.split("\n")[0][:400]

    loc = infer_orgao_local_from_title(f"{titulo}\n{inst}")
    tipo_selecao, _ = infer_tipo_selecao_meta(titulo, body)
    nivel = infer_nivel_escolaridade(titulo, body)

    return {
        "titulo": titulo,
        "instituicao": inst or (listing_meta.get("instituicao") if listing_meta else "") or None,
        "orgao": inst or None,
        "cargo": cargo_field,
        "body": body,
        "tipo_selecao": tipo_selecao,
        "data_inicio_inscricao": data_inicio,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "link_edital": edital,
        "situacao_lower": situacao,
        "estado": loc.get("estado"),
        "municipio": loc.get("municipio"),
        "nivel_escolaridade": nivel,
        "numero_vagas": None,
    }


def parse_fcc_listing_stub(listing_meta: Dict[str, str]) -> Dict[str, Any]:
    """Registo mínimo quando robots bloqueia página de detalhe."""
    inst = listing_meta.get("instituicao") or ""
    cargo = listing_meta.get("cargo") or ""
    url = listing_meta["url"]
    titulo = f"{inst} — {cargo}".strip(" —") if inst and cargo else url
    loc = infer_orgao_local_from_title(titulo)
    tipo_selecao, _ = infer_tipo_selecao_meta(titulo, "")
    return {
        "titulo": titulo,
        "instituicao": inst,
        "orgao": inst or None,
        "cargo": cargo or None,
        "body": "",
        "tipo_selecao": tipo_selecao,
        "data_inicio_inscricao": None,
        "data_fim_inscricao": None,
        "data_prova": None,
        "data_publicacao": None,
        "salario_min": None,
        "salario_max": None,
        "taxa_inscricao": None,
        "link_edital": None,
        "situacao_lower": "inscrições abertas",
        "estado": loc.get("estado"),
        "municipio": loc.get("municipio"),
        "nivel_escolaridade": infer_nivel_escolaridade(titulo, ""),
        "numero_vagas": None,
    }


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    listing_urls: Tuple[str, ...],
    allow_detail_despite_robots: bool,
) -> Dict[str, Any]:
    rp = _load_robots_parser(BASE)
    listing_items: List[Dict[str, str]] = []
    seen_url: Set[str] = set()

    for listing_url in listing_urls:
        if _robots_disallows(listing_url, rp):
            raise RuntimeError(f"robots.txt bloqueia listagem: {listing_url}")
        time.sleep(sleep_s)
        html = _fetch(listing_url)
        for it in _collect_listing_items(html, listing_url):
            u = it["url"].rstrip("/")
            if u not in seen_url:
                seen_url.add(u)
                listing_items.append(it)

    today = date.today()
    raw_rows: List[Dict[str, Any]] = []
    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    robots_skipped_detail = 0

    for meta in listing_items:
        if len(raw_rows) >= max_items:
            break
        url = meta["url"]
        detail_blocked = _robots_disallows(url, rp)
        if detail_blocked and not allow_detail_despite_robots:
            robots_skipped_detail += 1
            try:
                parsed = parse_fcc_listing_stub(meta)
            except Exception as exc:
                errors.append({"url": url, "erro": str(exc)})
                continue
        else:
            if detail_blocked and allow_detail_despite_robots:
                pass
            try:
                time.sleep(sleep_s)
                parsed = parse_fcc_detail_page(url, listing_meta=meta)
            except Exception as exc:
                errors.append({"url": url, "erro": str(exc)})
                continue

        try:
            tit = parsed["titulo"]
            body = parsed.get("body") or ""

            drop_s, why_s = fcc_should_discard_situacao(parsed.get("situacao_lower") or "")
            if drop_s:
                discarded.append({"url": url, "titulo": tit, "motivo": why_s})
                continue
            drop_n, why_n = fcc_should_discard_non_opportunity(titulo=tit, body=body)
            if drop_n:
                discarded.append({"url": url, "titulo": tit, "motivo": why_n})
                continue

            data_fim = parsed.get("data_fim_inscricao")
            data_prova = parsed.get("data_prova")
            drop_r, why_r = recency_should_discard(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
                text_for_recent_heuristic=body[:3000],
            )
            if drop_r:
                discarded.append({"url": url, "titulo": tit, "motivo": why_r})
                continue

            off = parsed.get("link_edital")
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
            missing_core = pci_missing_core_fields(
                {
                    "orgao": orgao,
                    "instituicao": instituicao,
                    "estado": estado,
                    "data_fim_inscricao": data_fim,
                    "data_prova": data_prova,
                    "numero_vagas": parsed.get("numero_vagas"),
                    "salario_max": sal_max,
                }
            )
            confidence = pci_infer_extraction_confidence(
                orgao=orgao,
                instituicao=instituicao,
                estado=estado,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                numero_vagas=parsed.get("numero_vagas"),
                salario_max=sal_max,
            )
            notes: List[str] = []
            if detail_blocked and allow_detail_despite_robots:
                notes.append("detail_fetched_despite_robots_disallow_concursos")
            if detail_blocked and not allow_detail_despite_robots:
                notes.append("detail_skipped_robots_disallow_concursos")
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
                numero_vagas=parsed.get("numero_vagas"),
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
            )
            if validacao == "incompleto" and not detail_blocked:
                qualidade = "media" if qualidade == "alta" else qualidade

            extras: Dict[str, Any] = {
                "crawler": "main_fcc_concursos",
                "wave": "concursos_wave2_fcc",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "listing_urls": list(listing_urls),
                "fcc_codigo": urlparse(url).path.split("/")[2] if "/concursos/" in url else None,
                "missing_core_fields": missing_core,
                "extraction_confidence": pci_adjust_confidence_for_ambiguity(
                    confidence, value_extraction_notes=notes
                ),
                "value_extraction_notes": notes,
                "robots_detail_blocked": detail_blocked,
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
                categoria="banca_fcc_concurso",
                orgao=orgao,
                instituicao=instituicao,
                banca=BANCA,
                cargo=parsed.get("cargo"),
                area=None,
                nivel_escolaridade=parsed.get("nivel_escolaridade"),
                estado=estado,
                municipio=municipio,
                numero_vagas=parsed.get("numero_vagas"),
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
                data_publicacao=parsed.get("data_publicacao"),
                data_inicio_inscricao=parsed.get("data_inicio_inscricao"),
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                link_edital=off,
                tags=["fcc", "banca", "wave2"],
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
        "allow_detail_despite_robots": allow_detail_despite_robots,
        "robots_skipped_detail_count": robots_skipped_detail,
        "total_bruto_listing": len(listing_items),
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
    ap = argparse.ArgumentParser(description="Crawler piloto FCC → standardized JSON")
    ap.add_argument("--max-items", type=int, default=20)
    ap.add_argument("--sleep", type=float, default=2.0, help="Pausa entre GET (segundos)")
    ap.add_argument(
        "--listings",
        type=str,
        default=",".join(DEFAULT_LISTINGS),
        help="URLs de listagem separadas por vírgula",
    )
    ap.add_argument(
        "--allow-detail-despite-robots",
        action="store_true",
        help="Buscar /concursos/... apesar de Disallow em robots.txt (piloto operador)",
    )
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave2_fcc"),
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
        report = run_crawl(
            max_items=args.max_items,
            sleep_s=args.sleep,
            listing_urls=listing_urls,
            allow_detail_despite_robots=bool(args.allow_detail_despite_robots),
        )
    except Exception as exc:
        err_payload = {"erro": str(exc), "listing_urls": list(listing_urls)}
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
        "# Crawler Wave 2 — FCC (Fundação Carlos Chagas)",
        "",
        f"- **Fonte:** `{FONT}` | **banca:** {BANCA}",
        f"- **Listagens:** {', '.join(listing_urls)}",
        f"- **allow_detail_despite_robots:** {summary.get('allow_detail_despite_robots')}",
        f"- **Detalhes omitidos (robots):** {summary.get('robots_skipped_detail_count', 0)}",
        f"- **Candidatos listagem:** {summary.get('total_bruto_listing', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Válidos:** {vc.get('valido', 0)} | **Incompletos:** {vc.get('incompleto', 0)}",
        "",
        "## Apply staging",
        "",
        "Dry-run apenas; apply não executado nesta wave.",
        "",
        "Ver `docs/CONCURSOS_WAVE2_FCC_CRAWLER.md`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
