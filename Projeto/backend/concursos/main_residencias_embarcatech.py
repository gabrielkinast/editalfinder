#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto Wave 2 — Residências / Formação (EmbarcaTech — Softex).

Diagnóstico (2026):
- Programa nacional de **residência tecnológica** (sistemas embarcados / IoT), coordenado pela Softex.
- Hub: `https://embarcatech.softex.br/inscricoes/` — links para editais/inscrições de IFs e parceiros.
- Detalhe: HTML institucional + PDF (ex. IFRN `ead.ifrn.edu.br/portal/edital-...`).
- BRISA/CAPES/MCTI: não usados neste piloto (ver `docs/CONCURSOS_WAVE2_RESIDENCIAS_FONTES.md`).

Saída: `fonte=embarcatech`, `tipo_selecao=residencia`, `categoria=residencia_tecnologica`.
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

BASE = "https://embarcatech.softex.br"
DEFAULT_LISTINGS = (
    f"{BASE}/inscricoes/",
    f"{BASE}/capacitacao-e-residencia/",
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "embarcatech"
ORGAO = "Softex — Programa EmbarcaTech"
INSTITUICAO_PADRAO = "Softex (Associação de Exportação de Software)"
BANCA = "Softex"

_RE_INSC_DE_ATE = re.compile(
    r"[Dd]e\s+(\d{2}/\d{2}/\d{4})\s+\d{1,2}:\d{2}?\s*a\s+(\d{2}/\d{2}/\d{4})",
    re.I,
)
_RE_INSC_ATE = re.compile(
    r"at[eé]\s+(\d{2}/\d{2}/\d{4})",
    re.I,
)
_RE_VAGAS = re.compile(
    r"(\d{1,4})\s+vagas?\b",
    re.I,
)
_HOST_INST = {
    "ifrn.edu.br": "Instituto Federal do Rio Grande do Norte (IFRN)",
    "ifpi.edu.br": "Instituto Federal do Piauí (IFPI)",
    "ifce.edu.br": "Instituto Federal do Ceará (IFCE)",
    "cepedi.org.br": "CEPEDI — Bahia",
    "hardware.org.br": "Instituto Hardware BR",
    "processoseletivo.ifrn.edu.br": "IFRN",
}


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
            "Referer": BASE + "/",
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


def _infer_instituicao(url: str) -> str:
    host = urlparse(url).netloc.lower().replace("www.", "")
    for key, name in _HOST_INST.items():
        if key in host:
            return name
    return INSTITUICAO_PADRAO


def _is_institutional_process_url(url: str) -> bool:
    low = url.lower().split("#")[0]
    if not low.startswith("http"):
        return False
    if "cdn-cgi" in low or "mailto:" in low:
        return False
    host = urlparse(url).netloc.lower().replace("www.", "")
    if host in ("embarcatech.softex.br", "softex.br"):
        return False
    if host.endswith("embarcatech.softex.br"):
        return False
    if re.search(r"edital|inscri|processo.?seletivo|residencia", low):
        return True
    if any(k in host for k in ("ifrn.edu.br", "ifpi.edu.br", "ifce.edu.br", "cepedi.org.br", "hardware.org.br")):
        return True
    return False


def _collect_process_urls(html: str, page_url: str, robots_parser) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[str] = []
    seen: Set[str] = set()
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue
        full = urljoin(page_url, href).split("#")[0].rstrip("/")
        if not _is_institutional_process_url(full):
            continue
        if full in seen:
            continue
        if _robots_disallows(full, robots_parser):
            continue
        seen.add(full)
        out.append(full)
    return out


def _parse_table_dates(soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
    for tr in soup.find_all("tr"):
        cells = [normalize_text(_unescape(td.get_text(" ", strip=True))) for td in tr.find_all(["td", "th"])]
        row = " | ".join(cells).lower()
        if "inscri" not in row:
            continue
        blob = " ".join(cells)
        m = _RE_INSC_DE_ATE.search(blob)
        if m:
            return _br_slash_to_iso(m.group(1)), _br_slash_to_iso(m.group(2))
        m2 = re.search(
            r"(\d{2}/\d{2}/\d{4})\s+at[eé]\s+(\d{2}/\d{2}/\d{4})",
            blob,
            re.I,
        )
        if m2:
            return _br_slash_to_iso(m2.group(1)), _br_slash_to_iso(m2.group(2))
        m3 = _RE_INSC_ATE.search(blob)
        if m3:
            return None, _br_slash_to_iso(m3.group(1))
    return None, None


def _parse_inscricao_dates(blob: str) -> Tuple[Optional[str], Optional[str]]:
    blob = normalize_text(_unescape(blob))
    m = _RE_INSC_DE_ATE.search(blob)
    if m:
        return _br_slash_to_iso(m.group(1)), _br_slash_to_iso(m.group(2))
    m2 = re.search(
        r"(\d{2}/\d{2}/\d{4})\s+at[eé]\s+(\d{2}/\d{2}/\d{4})",
        blob,
        re.I,
    )
    if m2:
        return _br_slash_to_iso(m2.group(1)), _br_slash_to_iso(m2.group(2))
    sch = fgv_schedule_from_text(blob)
    return sch.get("data_inicio_inscricao"), sch.get("data_fim_inscricao")


def _pick_edital_pdf(soup: BeautifulSoup, page_url: str) -> Optional[str]:
    best: Optional[str] = None
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href.lower().endswith(".pdf"):
            continue
        full = urljoin(page_url, href).split("#")[0]
        label = normalize_text(_unescape(a.get_text(" ", strip=True))).lower()
        if "edital" in label or "edital" in full.lower():
            return full
        if best is None and re.search(r"edital|retific", full, re.I):
            best = full
    return best


def _bolsa_from_text(blob: str) -> Tuple[Optional[float], Optional[float]]:
    sal_min, sal_max, _, _ = parse_remuneracao_taxa_br(blob)
    if sal_min is not None or sal_max is not None:
        return sal_min, sal_max
    m = re.search(r"bolsa[^\d]{0,40}R\$\s*([\d.,]+)", blob, re.I)
    if m:
        tok = m.group(1).replace(".", "").replace(",", ".")
        try:
            v = float(tok)
            return v, v
        except ValueError:
            pass
    return None, None


def _infer_valor_tipo(titulo: str, body: str, has_bolsa: bool) -> Optional[str]:
    """extras.valor_tipo quando há bolsa/auxílio mapeado em salario_min/max."""
    if not has_bolsa:
        return None
    blob = f"{titulo}\n{body}".lower()
    if "auxilio" in blob or "auxílio" in blob:
        return "auxilio"
    return "bolsa"


def _vagas_from_text(blob: str) -> Optional[int]:
    m = _RE_VAGAS.search(blob)
    if m:
        try:
            n = int(m.group(1))
            return n if n > 0 else None
        except ValueError:
            pass
    return None


def _page_title(soup: BeautifulSoup, fallback: str) -> str:
    h1 = soup.find("h1")
    if h1:
        t = normalize_text(_unescape(h1.get_text(" ", strip=True)))
        if t and len(t) > 5:
            return t
    if soup.title:
        t = normalize_text(_unescape(soup.title.get_text(strip=True)))
        if "embarcatech" in t.lower():
            t = re.sub(r"\s*[\|\-–]\s*EmbarcaTech.*$", "", t, flags=re.I).strip()
        if t:
            return t
    return fallback


def _body_text(soup: BeautifulSoup) -> str:
    node = soup.select_one(".entry-content") or soup.select_one("article") or soup.find("main") or soup.body
    if not node:
        return ""
    for bad in node.find_all(["script", "style", "nav", "footer"]):
        bad.decompose()
    return normalize_text(_unescape(node.get_text(" ", strip=True)))[:25000]


def embarcatech_should_discard(
    titulo: str,
    body: str,
    *,
    data_fim: Optional[str] = None,
    link_edital: Optional[str] = None,
) -> Tuple[bool, str]:
    blob = f"{titulo}\n{body}".lower()
    if data_fim or link_edital:
        return False, ""
    if re.search(r"\bresultado\s+final\b|\bgabarito\s+definitivo\b", blob):
        return True, "embarcatech_nao_oportunidade_ativa"
    if re.search(r"inscri[cç][oõ]es\s+encerrad", blob) and not re.search(r"\d{2}/\d{2}/20(2[4-9])", blob):
        return True, "embarcatech_inscricoes_encerradas"
    return False, ""


def parse_embarcatech_process(
    url: str,
    *,
    hub_title: str = "",
    enrich_pdf: bool = True,
) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    tit = _page_title(soup, hub_title or url)
    if "embarcatech" in tit.lower() and len(tit) < 25 and hub_title:
        tit = hub_title
    body = _body_text(soup)
    blob = f"{tit}\n{body}"

    data_inicio, data_fim = _parse_table_dates(soup)
    if not data_fim:
        di, df = _parse_inscricao_dates(blob)
        data_inicio = data_inicio or di
        data_fim = data_fim or df
    data_prova = extract_prova_from_text(blob)
    dates_iso = parse_all_dates_br(blob)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    edital = _pick_edital_pdf(soup, url)
    pdf_meta: Dict[str, Any] = {}
    if enrich_pdf and edital and (not data_fim or not data_prova):
        try:
            raw, note = fetch_pdf_bytes_capped(
                edital,
                referer=url,
                max_bytes=6 * 1024 * 1024,
                timeout_s=35,
            )
            pdf_meta["fetch_note"] = note
            if raw:
                sch = fgv_schedule_from_text(extract_pdf_text_fgv(raw) or "")
                pdf_meta["schedule"] = sch
                if not data_inicio:
                    data_inicio = sch.get("data_inicio_inscricao")
                if not data_fim:
                    data_fim = sch.get("data_fim_inscricao")
                if not data_prova:
                    data_prova = sch.get("data_prova")
        except Exception as exc:
            pdf_meta["fetch_note"] = f"erro:{exc}"

    if not data_fim:
        data_fim = extract_inscricao_fim_explicit_br(blob)

    sal_min, sal_max = _bolsa_from_text(blob)
    _, _, taxa, money_meta = parse_remuneracao_taxa_br(blob)
    vagas = _vagas_from_text(blob)

    curso: Optional[str] = None
    if re.search(r"sistemas\s+embarcados|internet das coisas|iot|embarcados", blob, re.I):
        curso = "Sistemas Embarcados / IoT"

    return {
        "titulo": tit,
        "body": body,
        "data_inicio_inscricao": data_inicio,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "numero_vagas": vagas,
        "link_edital": edital,
        "instituicao": _infer_instituicao(url),
        "curso": curso,
        "pdf_meta": pdf_meta,
    }


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    listing_urls: Tuple[str, ...],
    enrich_pdf: bool,
) -> Dict[str, Any]:
    rp = _load_robots_parser(BASE)

    all_urls: List[Tuple[str, str]] = []
    seen: Set[str] = set()
    for listing_url in listing_urls:
        if _robots_disallows(listing_url, rp):
            raise RuntimeError(f"robots.txt bloqueia listagem: {listing_url}")
        time.sleep(sleep_s)
        html = _fetch(listing_url)
        for u in _collect_process_urls(html, listing_url, rp):
            if u not in seen:
                seen.add(u)
                label = ""
                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all("a", href=True):
                    if urljoin(listing_url, a["href"]).split("#")[0].rstrip("/") == u:
                        label = normalize_text(_unescape(a.get_text(" ", strip=True)))
                        break
                all_urls.append((u, label))

    today = date.today()
    raw_rows: List[Dict[str, Any]] = []
    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for url, hub_label in all_urls:
        if len(raw_rows) >= max_items:
            break
        if _robots_disallows(url, rp):
            discarded.append({"url": url, "motivo": "robots_disallow"})
            continue
        try:
            time.sleep(sleep_s)
            titulo_hub = hub_label or "EmbarcaTech — Residência Tecnológica"
            if hub_label and len(hub_label) > 8 and "resultado" not in hub_label.lower():
                titulo_hub = f"EmbarcaTech — {hub_label}"
            parsed = parse_embarcatech_process(url, hub_title=titulo_hub, enrich_pdf=enrich_pdf)
            tit = parsed["titulo"]
            body = parsed["body"]
            off_pre = parsed.get("link_edital")
            df_pre = parsed.get("data_fim_inscricao")

            drop, why = embarcatech_should_discard(
                tit, body, data_fim=df_pre, link_edital=off_pre
            )
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

            inst = parsed.get("instituicao") or INSTITUICAO_PADRAO
            sal_min = parsed.get("salario_min")
            sal_max = parsed.get("salario_max")
            taxa = parsed.get("taxa_inscricao")
            vagas = parsed.get("numero_vagas")
            money_meta = parsed.get("money_meta") or {}

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
                "estado": None,
                "instituicao": inst,
                "link_edital": off,
                "numero_vagas": vagas,
            }
            missing_core = pci_missing_core_fields(partial_core)
            confidence = pci_infer_extraction_confidence(
                orgao=ORGAO,
                instituicao=inst,
                estado=None,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                numero_vagas=vagas,
                salario_max=sal_max,
            )
            qualidade = pci_infer_qualidade_dado(
                titulo=tit,
                link=url,
                orgao=ORGAO,
                instituicao=inst,
                estado=None,
                municipio=None,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                data_publicacao=data_pub,
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
            )
            if validacao == "valido" and qualidade == "baixa":
                qualidade = "media"
            elif not data_fim and off:
                qualidade = "media"
            elif not off:
                qualidade = "baixa"

            notes = list(money_meta.get("value_extraction_notes") or [])
            if not off:
                notes.append("edital_pdf_nao_encontrado_no_html")
            pdf_meta = parsed.get("pdf_meta") or {}
            if pdf_meta.get("fetch_note"):
                notes.append(f"pdf:{pdf_meta['fetch_note']}")

            extracted_fields: List[str] = []
            if data_fim:
                extracted_fields.append("data_fim_inscricao_texto")
            if data_inicio:
                extracted_fields.append("data_inicio_inscricao_texto")
            if data_prova:
                extracted_fields.append("data_prova_texto")
            if sal_min is not None or sal_max is not None:
                extracted_fields.append("bolsa_texto")
            if vagas is not None:
                extracted_fields.append("numero_vagas_texto")

            valor_tipo = _infer_valor_tipo(tit, body, sal_min is not None or sal_max is not None)

            extras: Dict[str, Any] = {
                "crawler": "main_residencias_embarcatech",
                "wave": "concursos_wave2_residencias_embarcatech",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "listing_urls": list(listing_urls),
                "hub_label": hub_label,
                "pdf_enrichment": pdf_meta,
                "extracted_fields": sorted(set(extracted_fields)),
                "missing_core_fields": missing_core,
                "extraction_confidence": pci_adjust_confidence_for_ambiguity(
                    confidence, value_extraction_notes=notes
                ),
                "source_is_aggregator": True,
                "aggregator_note": "Hub Softex lista editais de IFs executoras",
                "value_extraction_notes": notes,
            }
            if valor_tipo:
                extras["valor_tipo"] = valor_tipo
            row = build_concurso_item(
                titulo=tit[:500],
                link=url,
                fonte=FONT,
                fonte_tipo="governo",
                tipo_selecao="residencia",
                status=status,
                validacao_status=validacao,
                qualidade_dado=qualidade,
                extras=extras,
                categoria="residencia_tecnologica",
                orgao=ORGAO,
                instituicao=inst,
                banca=BANCA,
                cargo=None,
                curso=parsed.get("curso"),
                area="TIC / Sistemas Embarcados",
                nivel_escolaridade="superior",
                estado=None,
                municipio=None,
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
                data_publicacao=data_pub,
                data_inicio_inscricao=data_inicio,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                link_edital=off,
                tags=["embarcatech", "softex", "residencia_tecnologica", "wave2"],
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
        "total_bruto_urls": len(all_urls),
        "total_discarded_all": len(discarded),
        "discarded": discarded[:200],
        "total_standardized": len(raw_rows),
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler Wave 2 — Residências EmbarcaTech (Softex)")
    ap.add_argument("--max-items", type=int, default=10)
    ap.add_argument("--sleep", type=float, default=1.5)
    ap.add_argument("--listings", type=str, default=",".join(DEFAULT_LISTINGS))
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave2_residencias_embarcatech"),
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
    inc_ok = sum(1 for r in rows if r.get("validacao_status") == "incompleto")
    summary["validacao_counts"] = {"valido": val_ok, "incompleto": inc_ok}
    filled = summary.get("field_fill") or {}
    md = [
        "# Crawler Wave 2 — Residências EmbarcaTech (Softex)",
        "",
        f"- **Fonte:** `{FONT}` | **tipo:** `residencia` | **categoria:** `residencia_tecnologica`",
        f"- **URLs bruto:** {summary.get('total_bruto_urls', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Válidos:** {val_ok} | **Incompletos:** {inc_ok}",
        f"- **Erros crawl:** {len(summary.get('errors', []))}",
        "",
        "## Campos (preenchidos / ausentes)",
        "",
        f"- Preenchidos: `{', '.join(sorted(filled.keys())[:12])}` …" if filled else "- (sem itens)",
        f"- Sempre ausentes: `{', '.join(summary.get('fields_always_missing') or [])}`",
        "",
        "## Apply staging",
        "",
        "**Não recomendado** enquanto `valido` = 0 (exige `link_edital` + `data_fim_inscricao`).",
        "",
        "Ver `docs/CONCURSOS_WAVE2_RESIDENCIAS_EMBARCA_TECH_CRAWLER.md`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
