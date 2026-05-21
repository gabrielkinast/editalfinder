#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — Legalle Concursos (portal oficial de editais).

Diagnóstico (2026):
- Portal: `https://portal.editais.legalleconcursos.com.br` — HTML (Bootstrap / ACT SISTEMAS).
- Listagens: `/edital/index/abertos/` (inscrições abertas), `/edital/index/1/` (em andamento).
- Detalhe: `/edital/ver/{id}/` — bloco superior (tipo + órgão, inscrições, local), aba
  `#arquivos` (PDFs em `cdn.legalle.com.br`), aba `#vagas` (cargos, requisitos, remuneração).
- `robots.txt`: frequentemente 404; sem regras `User-agent:` → não bloquear via RobotFileParser.

Saída standardized para `scripts/load_concursos_selecao.py` (`fonte=legalle`).
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

BASE = "https://portal.editais.legalleconcursos.com.br"
DEFAULT_LISTINGS = (
    f"{BASE}/edital/index/abertos/",
    f"{BASE}/edital/index/1/",
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "legalle"
BANCA = "Legalle"

_RE_VER_PATH = re.compile(r"^/edital/ver/(\d+)/?$", re.I)
_RE_INSC_LEGALLE = re.compile(
    r"Inscri[cç][oõ]es\s+de\s+(\d{2}/\d{2}/\d{4})\s*-\s*\d{1,2}:\d{2}\s+"
    r"(?:at[eé]|a)\s+(\d{2}/\d{2}/\d{4})",
    re.I | re.S,
)
_RE_LOCAL_UF = re.compile(
    r"^([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s.'()-]+?)\s*-\s*([A-Z]{2})$",
)
_RE_NON_OPP = (
    r"divulgado\s+o\s+edital\s+de\s+resultado\s+final",
    r"\bresultado\s+final\b",
    r"gabarito\s+definitivo",
    r"homologa[cç][aã]o\s+do\s+resultado\s+final",
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


def _collect_ver_urls(html: str, listing_url: str, robots_parser) -> List[str]:
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
        if not _RE_VER_PATH.match(path):
            continue
        if any(full.lower().startswith(BASE.lower() + p) for p in _EXCLUDE_PATH_PREFIXES):
            continue
        key = full.rstrip("/")
        if key in seen:
            continue
        if _robots_disallows(full, robots_parser):
            continue
        seen.add(key)
        out.append(key)
    return out


def _parse_inscricao_dates(soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
    for p in soup.select("div.col-sm-10 p"):
        blob = normalize_text(_unescape_html_entities(p.get_text(" ", strip=True)))
        if "inscri" not in blob.lower():
            continue
        m = _RE_INSC_LEGALLE.search(blob)
        if m:
            return _br_slash_to_iso(m.group(1)), _br_slash_to_iso(m.group(2))
    return None, None


def _parse_header(soup: BeautifulSoup) -> Tuple[str, str, str]:
    tipo_label = ""
    orgao = ""
    p = soup.select_one("div.col-sm-10 p.text-16")
    if not p:
        p = soup.select_one("div.col-sm-10 p u")
        if p and p.parent:
            p = p.parent
    if p:
        u = p.find("u")
        if u:
            tipo_label = normalize_text(_unescape_html_entities(u.get_text(" ", strip=True)))
        full = p.get_text("\n", strip=True)
        lines = [normalize_text(x) for x in full.split("\n") if normalize_text(x)]
        if len(lines) >= 2:
            orgao = lines[-1]
        elif lines:
            orgao = lines[0] if not tipo_label else lines[0]
    titulo = f"{tipo_label} — {orgao}".strip(" —") if orgao else tipo_label
    return tipo_label, orgao, titulo


def _parse_localidade(soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
    for p in soup.select("div.col-sm-10 p"):
        txt = normalize_text(_unescape_html_entities(p.get_text(" ", strip=True)))
        if "inscri" in txt.lower():
            continue
        m = _RE_LOCAL_UF.match(txt)
        if m:
            return normalize_text(m.group(1)), m.group(2).upper()
    return None, None


def _pick_edital_pdf(soup: BeautifulSoup) -> Optional[str]:
    root = soup.select_one("#arquivos") or soup
    best: Optional[str] = None
    for item in root.select(".list-group-item"):
        label_el = item.select_one("p.text-secondary, p.mb-0")
        a = item.select_one("a[href*='.pdf']")
        if not label_el or not a:
            continue
        label = normalize_text(_unescape_html_entities(label_el.get_text(" ", strip=True))).lower()
        href = (a.get("href") or "").strip().split("#")[0]
        if not href.lower().endswith(".pdf"):
            continue
        if any(
            x in label
            for x in (
                "resultado",
                "gabarito",
                "homologa",
                "convoca",
                "retifica",
                "extrato",
            )
        ):
            continue
        if re.search(r"abertura.*inscri", label) or re.search(r"edital.*abertura", label):
            return href
        if "abertura" in label and "homolog" not in label and best is None:
            best = href
        if re.search(r"edital\s+n[ºo°]?\s*\d", label) and "abertura" in label and best is None:
            best = href
    return best


def _parse_remuneracao_val(text: str) -> Optional[float]:
    m = re.search(
        r"Remunera[cç][aã]o:\s*([\d.]{1,15},\d{2})",
        text,
        re.I,
    )
    if not m:
        return None
    try:
        return float(m.group(1).replace(".", "").replace(",", "."))
    except ValueError:
        return None


def _parse_vagas_section(
    soup: BeautifulSoup,
) -> Tuple[Optional[str], Optional[str], Optional[int], Optional[float], Optional[float]]:
    root = soup.select_one("#vagas")
    if not root:
        return None, None, None, None, None
    cargo: Optional[str] = None
    nivel: Optional[str] = None
    salarios: List[float] = []
    n_cargos = 0
    for item in root.select(".list-group-item.text-dark"):
        sp = item.select_one("span[data-toggle='collapse']")
        if sp:
            ct = normalize_text(_unescape_html_entities(sp.get_text(" ", strip=True)))
            if ct:
                if not cargo:
                    cargo = ct[:400]
                n_cargos += 1
        blob = item.get_text(" ", strip=True).lower()
        if "ensino superior" in blob or "bacharel" in blob:
            if not nivel:
                nivel = "superior"
        elif "ensino médio" in blob or "ensino medio" in blob:
            if not nivel:
                nivel = "medio"
        elif "técnico" in blob or "tecnico" in blob:
            if not nivel:
                nivel = "tecnico"
        rem = _parse_remuneracao_val(item.get_text(" ", strip=True))
        if rem is not None:
            salarios.append(rem)
    numero = n_cargos if n_cargos > 0 else None
    sal_min = min(salarios) if salarios else None
    sal_max = max(salarios) if salarios else None
    return cargo, nivel, numero, sal_min, sal_max


def legalle_should_discard_non_opportunity(*, titulo: str, body: str) -> Tuple[bool, str]:
    blob = f"{titulo}\n{body}".lower()
    for pat in _RE_NON_OPP:
        if re.search(pat, blob, re.I):
            return True, "legalle_nao_oportunidade_ativa"
    if re.search(r"\bhomologa[cç][aã]o\s+final\b", blob) and "inscri" not in blob[:500]:
        return True, "legalle_nao_oportunidade_ativa"
    return False, ""


def parse_legalle_page(url: str) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    tipo_label, orgao, tit = _parse_header(soup)
    if not tit:
        tit = orgao or url

    body_node = soup.select_one("div.container.bg-white") or soup.find("body")
    body = ""
    if body_node:
        for bad in body_node.find_all(["script", "style"]):
            bad.decompose()
        body = normalize_text(_unescape_html_entities(body_node.get_text(" ", strip=True)))[:25000]

    blob = f"{tipo_label}\n{tit}\n{body}"
    data_inicio, data_fim = _parse_inscricao_dates(soup)
    if not data_fim:
        data_fim = extract_inscricao_fim_explicit_br(blob)
    data_prova = extract_prova_from_text(blob)
    dates_iso = parse_all_dates_br(blob)
    data_pub = dates_iso[0].isoformat() if dates_iso else data_inicio

    municipio, estado = _parse_localidade(soup)
    cargo_v, nivel_v, numero_v, sal_min_v, sal_max_v = _parse_vagas_section(soup)
    sal_min, sal_max, taxa_meta, money_meta = parse_remuneracao_taxa_br(blob)
    sal_min = sal_min_v if sal_min_v is not None else sal_min
    sal_max = sal_max_v if sal_max_v is not None else sal_max
    taxa = taxa_meta
    edital = _pick_edital_pdf(soup)

    return {
        "titulo": tit,
        "tipo_label": tipo_label,
        "orgao": orgao,
        "body": body,
        "data_inicio_inscricao": data_inicio,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "numero_vagas": numero_v,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "link_edital": edital,
        "cargo_primeira_vaga": cargo_v,
        "nivel_primeira_vaga": nivel_v,
        "municipio": municipio,
        "estado": estado,
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
        for u in _collect_ver_urls(listing_html, listing_url, rp):
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
            parsed = parse_legalle_page(url)
            tit = parsed["titulo"]
            body = parsed["body"]

            drop_no, why_no = legalle_should_discard_non_opportunity(titulo=tit, body=body)
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
            validacao = "valido" if (data_fim and off) else "incompleto"

            orgao = parsed.get("orgao") or tit[:500]
            geo = infer_orgao_local_from_title(f"{orgao} {tit}")
            instituicao = geo["instituicao"] or orgao
            orgao_out = geo["orgao"] or orgao
            municipio = parsed.get("municipio") or geo["municipio"]
            estado = parsed.get("estado") or geo["estado"]
            nivel = parsed.get("nivel_primeira_vaga") or infer_nivel_escolaridade(tit, body)

            partial_core: Dict[str, Any] = {
                "data_fim_inscricao": data_fim,
                "data_prova": data_prova,
                "orgao": orgao_out,
                "estado": estado,
                "instituicao": instituicao,
                "link_edital": off,
                "numero_vagas": vagas,
            }
            missing_core = pci_missing_core_fields(partial_core)
            confidence = pci_infer_extraction_confidence(
                orgao=orgao_out,
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
                orgao=orgao_out,
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
                    orgao=orgao_out,
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
                notes.append("edital_pdf_nao_encontrado_em_arquivos")
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

            extras: Dict[str, Any] = {
                "crawler": "main_legalle_concursos",
                "wave": "concursos_wave1_legalle",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "legalle_listing_urls": list(listing_urls),
                "official_link_missing": off is None,
                "extracted_fields": sorted(set(extracted_fields)),
                "missing_core_fields": missing_core,
                "extraction_confidence": confidence,
                "source_is_aggregator": False,
                "value_extraction_notes": notes,
                "tipo_selecao_evidencia": tipo_evid,
                "possible_fee_detected": bool(money_meta.get("possible_fee_detected")),
                "possible_salary_detected": bool(money_meta.get("possible_salary_detected")),
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
                categoria="banca_legalle_concurso",
                orgao=orgao_out,
                instituicao=instituicao,
                banca=BANCA,
                cargo=parsed.get("cargo_primeira_vaga"),
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
                tags=["legalle", "wave1"],
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
        "total_bruto_urls": len(urls),
        "total_discarded_all": len(discarded),
        "discarded": discarded[:200],
        "total_standardized": len(raw_rows),
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler piloto Legalle → standardized JSON")
    ap.add_argument("--max-items", type=int, default=10, help="Máximo de concursos gravados")
    ap.add_argument("--sleep", type=float, default=1.5, help="Pausa entre GET (segundos)")
    ap.add_argument(
        "--listings",
        type=str,
        default=",".join(DEFAULT_LISTINGS),
        help="URLs de listagem separadas por vírgula",
    )
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave1_legalle"),
        help="Pasta wave1 Legalle",
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
            f"# Crawler Legalle — falha\n\n```json\n{json.dumps(err_payload, ensure_ascii=False, indent=2)}\n```\n"
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

    md = [
        "# Crawler piloto — Legalle Concursos",
        "",
        f"- **Fonte:** `{FONT}`",
        f"- **Listagens:** `{args.listings}`",
        f"- **Coleta (UTC):** `{summary['collected_at_utc']}`",
        f"- **URLs candidatas (bruto):** {summary.get('total_bruto_urls', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Ficheiro:** `{std_path.as_posix()}`",
        "",
        "## Próximo passo",
        "",
        "`python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_legalle/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_legalle/loader_dryrun --sources legalle`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
