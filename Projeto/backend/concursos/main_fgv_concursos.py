#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — FGV Conhecimento (listagem HTML + páginas de concurso Drupal).

Diagnóstico (2026):
- Listagem: https://conhecimento.fgv.br/concursos — HTML com links `.../concursos/{slug}`.
- Detalhe: páginas por slug; conteúdo principal em `article` / `div.region-content`;
  estado **Em Andamento** presente no HTML para concursos ativos; **Realizado** para encerrados.
- Editais: frequentemente PDF em `conhecimento.fgv.br/sites/default/files/concursos/*.pdf`;
  inscrições via portal FGV (não usado como `link_edital` se existir PDF de edital).

- robots.txt Drupal (admin/search disallow); rotas `/concursos/` permitidas.
- Saída standardized para `scripts/load_concursos_selecao.py` (`fonte=fgv`).
"""
from __future__ import annotations

import argparse
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
    _iso_to_date,
    build_concurso_item,
    field_fill_stats,
    infer_nivel_escolaridade,
    infer_orgao_local_from_title,
    infer_status_concurso,
    infer_tipo_selecao_meta,
    normalize_text,
    parse_all_dates_br,
    parse_remuneracao_taxa_br,
    parse_vagas_certame,
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
    fgv_merge_schedule_with_pdf_text,
    fgv_schedule_from_text,
)

BASE = "https://conhecimento.fgv.br"
LISTING_URL = f"{BASE}/concursos"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "fgv"
BANCA = "FGV"


_RE_FGV_SLUG = re.compile(r"^/concursos/([a-z0-9._-]+)/?$", re.I)
_EXCLUDE_SLUGS = frozenset({"nosso-portfolio", "concursos"})

_RE_NON_OPP = (
    r"prova\s+(?:foi\s+)?realizada",
    r"\bresultado\s+final\b",
    r"\bgabarito\b",
    r"homologa[cç][aã]o\s+final",
)


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
        return resp.read().decode("utf-8", "replace")


def _robots_disallows(url: str, robots_parser) -> bool:
    if robots_parser is None:
        return False
    try:
        return not robots_parser.can_fetch(USER_AGENT, url)
    except Exception:
        return True


def _collect_concurso_urls(html: str, listing_url: str, robots_parser) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[str] = []
    seen: Set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        full = urljoin(listing_url, href).split("#")[0]
        if not full.startswith(f"{BASE}/concursos/"):
            continue
        path = urlparse(full).path or ""
        m = _RE_FGV_SLUG.match(path)
        if not m:
            continue
        slug = m.group(1).lower()
        if slug in _EXCLUDE_SLUGS or "portfolio" in slug:
            continue
        if full.rstrip("/") in seen:
            continue
        if _robots_disallows(full, robots_parser):
            continue
        seen.add(full.rstrip("/"))
        out.append(full.rstrip("/"))
    return out


def _fgv_main_body_text(soup: BeautifulSoup) -> str:
    node = soup.find("article") or soup.select_one("div.region-content") or soup.find("main")
    if node:
        for bad in node.find_all(["script", "style", "nav", "footer", "aside"]):
            bad.decompose()
        return normalize_text(node.get_text(" ", strip=True))[:16000]
    return normalize_text(soup.get_text(" ", strip=True))[:16000]


def _fgv_title(soup: BeautifulSoup, url: str) -> str:
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return normalize_text(og["content"])
    h1 = soup.find("h1")
    if h1:
        return normalize_text(h1.get_text())
    t = soup.find("title")
    if t:
        return normalize_text(t.get_text())
    return url


def _pick_edital_pdf_url(soup: BeautifulSoup, page_url: str) -> Optional[str]:
    """Prioriza âncora cujo texto começa por «Edital»; senão PDF cujo path contém «edital»."""
    best: Optional[str] = None
    for a in soup.find_all("a", href=True):
        h = a["href"].strip()
        if not h.lower().endswith(".pdf"):
            continue
        full = urljoin(page_url, h).split("#")[0]
        low = full.lower()
        if "termos" in low or "cookies" in low or "privacidade" in low or "lgpd" in low:
            continue
        label = normalize_text(a.get_text(" ", strip=True) or "")
        if re.match(r"(?i)^edital", label):
            return full
        if "edital" in low and "retifica" not in label.lower():
            best = best or full
    for a in soup.find_all("a", href=True):
        h = a["href"].strip()
        if not h.lower().endswith(".pdf"):
            continue
        full = urljoin(page_url, h).split("#")[0]
        if "edital" in full.lower():
            return full
    return best


def _fgv_em_andamento(html: str) -> bool:
    return "Em Andamento" in html


def _fgv_realizado(html: str) -> bool:
    return bool(re.search(r"\bRealizado\b", html))


def fgv_should_discard_non_opportunity(
    *, titulo: str, body: str, link_edital: Optional[str], data_fim_inscricao: Optional[str], today: date
) -> Tuple[bool, str]:
    blob = f"{titulo}\n{body}".lower()
    df = _iso_to_date(data_fim_inscricao)
    if df is not None and df >= today:
        return False, ""
    if re.search(r"(?i)retifica[cç][aã]o", blob) and not link_edital:
        return True, "fgv_nao_oportunidade_ativa"
    for pat in _RE_NON_OPP:
        if re.search(pat, blob):
            return True, "fgv_nao_oportunidade_ativa"
    return False, ""


def fgv_strip_if_low_trust(
    *,
    link_edital: Optional[str],
    data_fim_inscricao: Optional[str],
    numero_vagas: Optional[int],
    salario_min: Optional[float],
    salario_max: Optional[float],
    taxa_inscricao: Optional[float],
) -> Tuple[Optional[int], Optional[float], Optional[float], Optional[float], List[str]]:
    notes: List[str] = []
    if link_edital is None and data_fim_inscricao is None:
        if (
            numero_vagas is not None
            or salario_min is not None
            or salario_max is not None
            or taxa_inscricao is not None
        ):
            notes.append("valores_suprimidos_sem_edital_pdf_nem_data_fim")
        return None, None, None, None, notes
    return numero_vagas, salario_min, salario_max, taxa_inscricao, notes


def _title_for_geo(titulo: str) -> str:
    t = normalize_text(titulo)
    t = re.sub(r"\s*\|\s*FGV.*$", "", t, flags=re.I)
    t = re.sub(r"\s*-\s*FGV\s*$", "", t, flags=re.I)
    return t


def _fgv_entity_suffix_from_title(titulo: str) -> Optional[str]:
    """
    Extrai o nome do órgão/entidade a partir do título oficial FGV, p.ex.
    «Concurso Público para o Tribunal …» / «Processo Seletivo Simplificado para a Secretaria …».
    Usa apenas texto já presente no título (sem inferência geográfica além do helper PCI no sufixo).
    """
    t = normalize_text(titulo)
    if not t:
        return None
    m = re.search(
        r"(?i)(?:concurso\s+p[úu]blico|processo\s+seletivo(?:\s+simplificado)?)\s+para\s+(?:o|a)\s+(.+)$",
        t,
    )
    if not m:
        return None
    rest = normalize_text(m.group(1))
    rest = re.split(r"(?i)\s*[|\-–—]\s*", rest)[0].strip()
    return rest or None


def _fgv_org_geo_from_title(titulo: str) -> Dict[str, Optional[str]]:
    """Órgão/instituição/local a partir do padrão «… para o/a …» + heurísticas PCI no sufixo."""
    rest = _fgv_entity_suffix_from_title(titulo)
    if not rest:
        return {"orgao": None, "instituicao": None, "municipio": None, "estado": None}
    sub = infer_orgao_local_from_title(rest)
    if sub.get("orgao"):
        return sub
    return {
        "orgao": rest,
        "instituicao": rest,
        "municipio": sub.get("municipio"),
        "estado": sub.get("estado"),
    }


def parse_concurso_page(url: str) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    tit = _fgv_title(soup, url)
    body = _fgv_main_body_text(soup)
    blob = f"{tit}\n{body}"
    sch = fgv_schedule_from_text(blob)
    data_fim = sch["data_fim_inscricao"]
    data_inicio = sch["data_inicio_inscricao"]
    data_prova = sch["data_prova"]
    schedule_notes_html = list(sch.get("schedule_notes") or [])
    dates_iso = parse_all_dates_br(body)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    vagas, vagas_notes = parse_vagas_certame(
        body,
        scan_limit=6000,
        paragraph_scope=True,
        title_for_crosscheck=tit,
    )
    sal_min, sal_max, taxa, money_meta = parse_remuneracao_taxa_br(blob)
    edital = _pick_edital_pdf_url(soup, url)

    return {
        "titulo": tit,
        "body": body,
        "html_flags": {"em_andamento": _fgv_em_andamento(html), "realizado": _fgv_realizado(html)},
        "data_fim_inscricao": data_fim,
        "data_inicio_inscricao": data_inicio,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "numero_vagas": vagas,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "link_edital": edital,
        "vagas_extraction_notes": vagas_notes,
        "schedule_notes_html": schedule_notes_html,
    }


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    listing_url: str,
    max_pdf_bytes: int,
    max_pdfs: int,
    pdf_timeout_s: float,
) -> Dict[str, Any]:
    from urllib.robotparser import RobotFileParser

    rp: Optional[Any] = None
    for robots_url in (f"{BASE}/robots.txt",):
        try:
            r2 = RobotFileParser()
            r2.set_url(robots_url)
            r2.read()
            rp = r2
            break
        except Exception:
            continue

    if _robots_disallows(listing_url, rp):
        raise RuntimeError(f"robots.txt bloqueia listagem: {listing_url}")

    time.sleep(sleep_s)
    listing_html = _fetch(listing_url)
    urls = _collect_concurso_urls(listing_html, listing_url, rp)[: max(max_items * 4, 24)]

    max_pdfs_eff = max(0, int(max_pdfs))
    pdf_remaining = max_pdfs_eff
    pdf_stats = {
        "max_pdf_bytes": max_pdf_bytes,
        "max_pdfs_per_run": max_pdfs,
        "pdf_timeout_s": pdf_timeout_s,
        "attempts": 0,
        "download_ok": 0,
        "text_extracted": 0,
        "skipped_limit_reached": 0,
    }

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
            parsed = parse_concurso_page(url)
            tit = parsed["titulo"]
            body = parsed["body"]
            flags = parsed.get("html_flags") or {}

            if not flags.get("em_andamento"):
                if flags.get("realizado") or "realizado" in body.lower()[:500]:
                    discarded.append({"url": url, "titulo": tit, "motivo": "fgv_nao_em_andamento"})
                else:
                    discarded.append({"url": url, "titulo": tit, "motivo": "fgv_sem_marca_em_andamento"})
                continue

            off = parsed["link_edital"]
            data_fim = parsed["data_fim_inscricao"]
            data_inicio = parsed.get("data_inicio_inscricao")
            data_prova = parsed["data_prova"]
            data_pub = parsed["data_publicacao"]

            drop_no, why_no = fgv_should_discard_non_opportunity(
                titulo=tit,
                body=body,
                link_edital=off,
                data_fim_inscricao=data_fim,
                today=today,
            )
            if drop_no:
                discarded.append({"url": url, "titulo": tit, "motivo": why_no})
                continue

            pdf_checked = False
            pdf_date_notes: List[str] = []
            html_sched = parsed.get("schedule_notes_html") or []
            for sn in html_sched:
                pdf_date_notes.append(f"schedule_html:{sn}")

            drop_r, why_r = recency_should_discard(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
                text_for_recent_heuristic=f"{tit} {body}",
            )
            if (
                drop_r
                and why_r == "data_prova_passada_sem_fim_inscricao"
                and data_prova
                and _iso_to_date(data_prova) == today
            ):
                drop_r, why_r = False, ""
            if drop_r:
                discarded.append({"url": url, "titulo": tit, "motivo": why_r})
                continue

            needs_pdf_for_dates = bool(
                off
                and str(off).lower().startswith("http")
                and str(off).lower().endswith(".pdf")
                and (data_fim is None or data_inicio is None or data_prova is None)
            )
            if needs_pdf_for_dates:
                if max_pdfs_eff <= 0:
                    pdf_date_notes.append("pdf_enriquecimento_desativado_max_pdfs_0")
                elif pdf_remaining <= 0:
                    pdf_stats["skipped_limit_reached"] += 1
                    pdf_date_notes.append("pdf_nao_baixado:limite_max_pdfs_por_execucao")
                else:
                    pdf_remaining -= 1
                    pdf_checked = True
                    pdf_stats["attempts"] += 1
                    time.sleep(sleep_s)
                    raw_pdf, fetch_note = fetch_pdf_bytes_capped(
                        str(off),
                        referer=url,
                        max_bytes=max_pdf_bytes,
                        timeout_s=pdf_timeout_s,
                    )
                    pdf_date_notes.append(f"pdf_fetch:{fetch_note}")
                    if raw_pdf:
                        pdf_stats["download_ok"] += 1
                        pt, eng = extract_pdf_text_fgv(raw_pdf)
                        pdf_date_notes.append(f"pdf_text:{eng}")
                        if pt and pt.strip():
                            pdf_stats["text_extracted"] += 1
                        merged = fgv_merge_schedule_with_pdf_text(
                            titulo=tit,
                            body=body,
                            pdf_text=pt,
                            prior_inicio=data_inicio,
                            prior_fim=data_fim,
                            prior_prova=data_prova,
                        )
                        data_inicio = merged["data_inicio_inscricao"]
                        data_fim = merged["data_fim_inscricao"]
                        data_prova = merged["data_prova"]
                        for sn in merged["schedule_notes"]:
                            pdf_date_notes.append(f"schedule_pdf:{sn}")
            elif off and str(off).lower().startswith("http") and str(off).lower().endswith(".pdf"):
                pdf_date_notes.append("pdf_nao_baixado:datas_ja_extraidas_html_sem_lacunas")
            else:
                if not off:
                    pdf_date_notes.append("pdf_nao_baixado:sem_link_edital")
                else:
                    pdf_date_notes.append("pdf_nao_baixado:url_edital_nao_e_pdf")

            drop_r2, why_r2 = recency_should_discard(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
                text_for_recent_heuristic=f"{tit} {body}",
            )
            if (
                drop_r2
                and why_r2 == "data_prova_passada_sem_fim_inscricao"
                and data_prova
                and _iso_to_date(data_prova) == today
            ):
                drop_r2, why_r2 = False, ""
            if drop_r2:
                discarded.append({"url": url, "titulo": tit, "motivo": why_r2})
                continue

            vagas = parsed["numero_vagas"]
            sal_min = parsed["salario_min"]
            sal_max = parsed["salario_max"]
            taxa = parsed["taxa_inscricao"]
            money_meta = parsed.get("money_meta") or {}

            vagas, sal_min, sal_max, taxa, strip_notes = fgv_strip_if_low_trust(
                link_edital=off,
                data_fim_inscricao=data_fim,
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
            )

            tipo, tipo_evid = infer_tipo_selecao_meta(tit, body)
            status = infer_status_concurso(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
            )

            if data_fim and off:
                validacao = "valido"
            else:
                validacao = "incompleto"

            tit_geo = _title_for_geo(tit)
            geo_pci = infer_orgao_local_from_title(tit_geo)
            geo_fgv = _fgv_org_geo_from_title(tit_geo)
            orgao = geo_fgv["orgao"] or geo_pci["orgao"]
            instituicao = geo_fgv["instituicao"] or geo_pci["instituicao"] or orgao
            municipio = geo_fgv["municipio"] or geo_pci["municipio"]
            estado = geo_fgv["estado"] or geo_pci["estado"]
            nivel = infer_nivel_escolaridade(tit, body)

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
            notes.extend(parsed.get("vagas_extraction_notes") or [])
            notes.extend(strip_notes)
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

            extras: Dict[str, Any] = {
                "crawler": "main_fgv_concursos",
                "wave": "concursos_wave1_fgv",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "fgv_listing_url": listing_url,
                "official_link_missing": off is None,
                "extracted_fields": sorted(set(extracted_fields)),
                "missing_core_fields": missing_core,
                "extraction_confidence": confidence,
                "source_is_aggregator": False,
                "value_extraction_notes": notes,
                "tipo_selecao_evidencia": tipo_evid,
                "possible_fee_detected": bool(money_meta.get("possible_fee_detected")),
                "possible_salary_detected": bool(money_meta.get("possible_salary_detected")),
                "pdf_checked": pdf_checked,
                "pdf_date_extraction_notes": pdf_date_notes[:80],
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
                categoria="banca_fgv_conhecimento",
                orgao=orgao,
                instituicao=instituicao,
                banca=BANCA,
                cargo=None,
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
                tags=["fgv", "wave1"],
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
        "listing_url": listing_url,
        "total_bruto_urls": len(urls),
        "total_discarded_all": len(discarded),
        "discarded": discarded[:200],
        "total_standardized": len(raw_rows),
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "pdf_enrichment": pdf_stats,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler piloto FGV Conhecimento → standardized JSON")
    ap.add_argument("--max-items", type=int, default=10, help="Máximo de concursos gravados")
    ap.add_argument("--sleep", type=float, default=1.5, help="Pausa entre GET (segundos)")
    ap.add_argument("--listing-url", type=str, default=LISTING_URL, help="URL da listagem")
    ap.add_argument(
        "--max-pdf-mb",
        type=float,
        default=4.0,
        help="Tamanho máximo (MiB) por PDF de edital a baixar",
    )
    ap.add_argument(
        "--max-pdfs",
        type=int,
        default=6,
        help="Máximo de PDFs a processar por execução (pedidos GET)",
    )
    ap.add_argument(
        "--pdf-timeout",
        type=float,
        default=25.0,
        help="Timeout (s) por download de PDF",
    )
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave1_fgv"),
        help="Pasta wave1 FGV",
    )
    args = ap.parse_args()

    out_root = Path(args.output_root)
    std_dir = out_root / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)
    std_path = std_dir / f"{FONT}_standardized.json"

    try:
        max_pdf_bytes = int(max(0.5, float(args.max_pdf_mb)) * 1024 * 1024)
        report = run_crawl(
            max_items=args.max_items,
            sleep_s=args.sleep,
            listing_url=args.listing_url,
            max_pdf_bytes=max_pdf_bytes,
            max_pdfs=max(0, int(args.max_pdfs)),
            pdf_timeout_s=float(args.pdf_timeout),
        )
    except Exception as exc:
        err_payload = {"erro": str(exc), "listing_url": args.listing_url}
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "crawler_summary.json").write_text(
            json.dumps(err_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_root / "crawler_summary.md").write_text(
            f"# Crawler FGV — falha\n\n```json\n{json.dumps(err_payload, ensure_ascii=False, indent=2)}\n```\n"
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
        "# Crawler piloto — FGV Conhecimento",
        "",
        f"- **Fonte:** `{FONT}`",
        f"- **Listagem:** `{args.listing_url}`",
        f"- **Coleta (UTC):** `{summary['collected_at_utc']}`",
        f"- **URLs candidatas (bruto):** {summary.get('total_bruto_urls', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **PDF (enriquecimento):** `{json.dumps(summary.get('pdf_enrichment') or {}, ensure_ascii=False)}`",
        f"- **Ficheiro:** `{std_path.as_posix()}`",
        "",
        "## Próximo passo",
        "",
        "`python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_fgv/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_fgv/loader_dryrun_v2 --sources fgv`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
