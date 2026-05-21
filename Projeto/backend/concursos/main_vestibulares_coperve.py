#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto Wave 2 — Vestibulares / Ingresso (UFSC — Coperve).

Diagnóstico (2026):
- Vunesp: 403/WAF e domínio vestibular indisponível em DNS — não viável com HTTP simples.
- Comvest/Unicamp: robots.txt `Disallow: /` — não adequado para crawl automatizado.
- Fuvest: HTML acessível mas falhas SSL em alguns ambientes Windows.
- **Coperve (escolhida):** `coperve.ufsc.br`, `coperve.paginas.ufsc.br`, subdomínios
  `*.ufsc.br` de processos (ex.: `vestibularunificado2026.ufsc.br`, `refugiados2026.ufsc.br`)
  e portal `vestibular.coperve.ufsc.br/inscricao/evento/{id}/dados` (período de inscrição em HTML).

Saída: `fonte=coperve`, `fonte_tipo=universidade`, `tipo_selecao` vestibular / programa_ingresso.
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

BASE_COPERVE = "https://coperve.ufsc.br"
DEFAULT_LISTINGS = (
    f"{BASE_COPERVE}/",
    f"{BASE_COPERVE}/proximos-vestibulares/",
    "https://coperve.paginas.ufsc.br/proximos-vestibulares/",
)
KNOWN_PROCESS_URLS = (
    "https://vestibularunificado2026.ufsc.br/",
    "https://vestibularunificado2026.ufsc.br/edital/",
    "https://vestibularunificado2026.ufsc.br/inscricao/",
    "https://refugiados2026.ufsc.br/",
    "https://coperve.paginas.ufsc.br/processo-seletivo-suplementares/",
    "https://coperve.paginas.ufsc.br/vagas-suplementares-para-negros/",
    "https://coperve.paginas.ufsc.br/processo-seletivo-libras/",
    "https://coperve.paginas.ufsc.br/processo-seletivo-educacao-do-campo/",
    "https://coperve.paginas.ufsc.br/processo-seletivo-refugiados/",
)
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "coperve"
INSTITUICAO = "Universidade Federal de Santa Catarina (UFSC)"
ORGAO = "Coperve — Comissão Permanente do Vestibular / UFSC"
BANCA = "Coperve"
ESTADO = "SC"
MUNICIPIO = "Florianópolis"

_RE_EVENTO_DADOS = re.compile(
    r"vestibular\.coperve\.ufsc\.br/inscricao/evento/(\d+)/dados",
    re.I,
)
_RE_INSC_DE_ATE = re.compile(
    r"[Dd]e\s+(\d{2}/\d{2}/\d{4})\s+\d{1,2}:\d{2}\s+a\s+(\d{2}/\d{2}/\d{4})",
    re.I,
)
_RE_INSC_ATE_ONLY = re.compile(
    r"inscri[cç][oõ]es?\s+encerrad[ao]s?\s+no\s+dia\s+(\d{1,2})\s+de\s+"
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
_EXCLUDE_HOST_SUBSTR = (
    "facebook.com",
    "twitter.com",
    "whatsapp:",
    "repositorio.ufsc.br",
    "dados.coperve.ufsc.br",
)
_EXCLUDE_PATH = (
    "/vestibulares-anteriores",
    "/anos-anteriores",
    "/calendar/",
    "concursos.ufsc.br",
    "/treinandoparaovestibular",
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


def _is_process_candidate(url: str) -> bool:
    low = url.lower()
    if not low.startswith("http"):
        return False
    if any(x in low for x in _EXCLUDE_HOST_SUBSTR):
        return False
    if any(x in low for x in _EXCLUDE_PATH):
        return False
    host = urlparse(url).netloc.lower()
    if not (host.endswith(".ufsc.br") or host == "ufsc.br"):
        return False
    if _RE_EVENTO_DADOS.search(url):
        return False
    path = urlparse(url).path.lower()
    if re.search(
        r"vestibular|processo-seletivo|processo_seletivo|refugiados|ingresso|"
        r"vagas-suplementares|edital|inscricao",
        path,
    ):
        return True
    if host.startswith("vestibularunificado") or host.startswith("refugiados"):
        return True
    if "coperve.paginas.ufsc.br" in host and "processo" in path:
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
        full = urljoin(page_url, href).split("#")[0]
        if not _is_process_candidate(full):
            continue
        key = full.rstrip("/")
        if key in seen:
            continue
        if _robots_disallows(full, robots_parser):
            continue
        seen.add(key)
        out.append(key)
    return out


def _find_evento_dados_url(html: str, page_url: str) -> Optional[str]:
    for m in _RE_EVENTO_DADOS.finditer(html):
        return f"https://vestibular.coperve.ufsc.br/inscricao/evento/{m.group(1)}/dados"
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.find_all("a", href=True):
        full = urljoin(page_url, a["href"])
        if _RE_EVENTO_DADOS.search(full):
            return full.split("#")[0]
    return None


def _parse_inscricao_from_blob(blob: str) -> Tuple[Optional[str], Optional[str]]:
    blob = normalize_text(_unescape(blob))
    m = _RE_INSC_DE_ATE.search(blob)
    if m:
        return _br_slash_to_iso(m.group(1)), _br_slash_to_iso(m.group(2))
    m2 = _RE_INSC_ATE_ONLY.search(blob)
    if m2:
        dia = int(m2.group(1))
        mes = _MESES.get(m2.group(2).lower().replace("ç", "c"))
        ano = int(m2.group(3))
        if mes:
            try:
                return None, date(ano, mes, dia).isoformat()
            except ValueError:
                pass
    fim = extract_inscricao_fim_explicit_br(blob)
    if fim:
        return None, fim
    return None, None


def _pick_edital_pdf(soup: BeautifulSoup, page_url: str) -> Optional[str]:
    best: Optional[str] = None
    for a in soup.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href.lower().endswith(".pdf"):
            continue
        full = urljoin(page_url, href).split("#")[0]
        if "repositorio.ufsc.br" in full:
            continue
        label = normalize_text(_unescape(a.get_text(" ", strip=True))).lower()
        path_low = full.lower()
        if re.search(r"edital|programa", label) or re.search(r"edital|programa", path_low):
            if "edital" in label or "edital" in path_low:
                return full
            if best is None:
                best = full
    return best


def _infer_tipo_vestibular(titulo: str, body: str) -> Tuple[str, str]:
    blob = f"{titulo}\n{body}".lower()
    if re.search(r"processo\s+seletivo|vagas\s+suplementares|refugiados|hist[oó]rico\s+escolar", blob):
        return "programa_ingresso", "texto:processo_seletivo_ingresso"
    if "vestibular" in blob:
        return "vestibular", "texto:vestibular"
    return "vestibular", "fallback:vestibular_ufsc"


def _body_text(soup: BeautifulSoup) -> str:
    node = (
        soup.select_one(".entry-content")
        or soup.select_one("article")
        or soup.select_one("main")
        or soup.find("body")
    )
    if not node:
        return ""
    for bad in node.find_all(["script", "style", "nav", "footer"]):
        bad.decompose()
    return normalize_text(_unescape(node.get_text(" ", strip=True)))[:25000]


def _page_title(soup: BeautifulSoup) -> str:
    h1 = soup.find("h1")
    if h1:
        t = normalize_text(_unescape(h1.get_text(" ", strip=True)))
        if t and "coperve" not in t.lower()[:12]:
            return t
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return normalize_text(_unescape(og["content"]))
    if soup.title:
        t = normalize_text(_unescape(soup.title.get_text(strip=True)))
        t = re.sub(r"\s*[\|\-–]\s*Coperve.*$", "", t, flags=re.I).strip()
        return t
    return ""


def coperve_should_discard_closed(titulo: str, body: str) -> Tuple[bool, str]:
    blob = f"{titulo}\n{body}".lower()
    if re.search(r"inscri[cç][oõ]es\s+encerrad", blob) and "abertas" not in blob[:300]:
        if not re.search(r"de\s+\d{2}/\d{2}/\d{4}\s+\d{1,2}:\d{2}\s+a\s+\d{2}/\d{2}/\d{4}", blob):
            return True, "coperve_inscricoes_encerradas_sem_periodo_futuro"
    if re.search(r"\brealizado\b|\bencerrado\b|\banos?\s+anteriores\b", titulo.lower()):
        return True, "coperve_processo_encerrado_titulo"
    return False, ""


def parse_coperve_process(url: str, *, extra_html: Optional[str] = None) -> Dict[str, Any]:
    html = extra_html if extra_html is not None else _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    tit = _page_title(soup) or url
    body = _body_text(soup)
    blob = f"{tit}\n{body}"

    data_inicio, data_fim = _parse_inscricao_from_blob(blob)
    event_url = _find_evento_dados_url(html, url)
    if event_url and extra_html is None:
        try:
            ev_html = _fetch(event_url)
            ei, ef = _parse_inscricao_from_blob(ev_html)
            if ei:
                data_inicio = ei
            if ef:
                data_fim = ef
        except Exception:
            event_url = event_url

    data_prova = extract_prova_from_text(blob)
    dates_iso = parse_all_dates_br(blob)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    _, _, taxa, money_meta = parse_remuneracao_taxa_br(blob)
    edital = _pick_edital_pdf(soup, url)
    tipo, tipo_evid = _infer_tipo_vestibular(tit, body)

    curso: Optional[str] = None
    if re.search(r"curso[s]?\s+de\s+", blob, re.I):
        m = re.search(r"curso[s]?\s+de\s+([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s\-]{3,60})", blob, re.I)
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
        "evento_inscricao_url": event_url,
        "curso": curso,
    }


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    listing_urls: Tuple[str, ...],
) -> Dict[str, Any]:
    rp = _load_robots_parser(BASE_COPERVE)

    all_urls: List[str] = []
    seen: Set[str] = set()
    for u in KNOWN_PROCESS_URLS:
        if u not in seen:
            seen.add(u.rstrip("/"))
            all_urls.append(u.rstrip("/"))

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
            parsed = parse_coperve_process(url)
            tit = parsed["titulo"]
            body = parsed["body"]

            drop_c, why_c = coperve_should_discard_closed(tit, body)
            if drop_c:
                discarded.append({"url": url, "titulo": tit, "motivo": why_c})
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
            if not off:
                notes.append("edital_pdf_nao_encontrado_no_html")

            extracted_fields: List[str] = []
            if data_fim:
                extracted_fields.append("data_fim_inscricao_texto")
            if data_inicio:
                extracted_fields.append("data_inicio_inscricao_texto")
            if data_prova:
                extracted_fields.append("data_prova_texto")
            if taxa is not None:
                extracted_fields.append("taxa_inscricao_texto")
            if parsed.get("evento_inscricao_url"):
                extracted_fields.append("portal_inscricao_evento")

            extras: Dict[str, Any] = {
                "crawler": "main_vestibulares_coperve",
                "wave": "concursos_wave2_vestibulares_coperve",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "listing_urls": list(listing_urls),
                "portal_inscricao_url": parsed.get("evento_inscricao_url"),
                "official_link_missing": off is None,
                "extracted_fields": sorted(set(extracted_fields)),
                "missing_core_fields": missing_core,
                "extraction_confidence": confidence,
                "source_is_aggregator": False,
                "value_extraction_notes": notes,
                "tipo_selecao_evidencia": tipo_evid,
                "diagnostico_fontes_alternativas": {
                    "vunesp": "403/WAF ou DNS",
                    "comvest": "robots Disallow /",
                    "fuvest": "SSL variável por ambiente",
                },
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
                categoria="vestibular_ufsc_coperve",
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
                tags=["coperve", "ufsc", "wave2", "vestibular"],
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
        "fonte_escolhida_nota": (
            "UFSC/Coperve — Vunesp indisponível (403); Comvest bloqueado em robots; Fuvest com SSL intermitente."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler Wave 2 — Vestibulares UFSC/Coperve")
    ap.add_argument("--max-items", type=int, default=12, help="Máximo de processos gravados")
    ap.add_argument("--sleep", type=float, default=1.5, help="Pausa entre GET (segundos)")
    ap.add_argument(
        "--listings",
        type=str,
        default=",".join(DEFAULT_LISTINGS),
        help="URLs hub separadas por vírgula",
    )
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave2_vestibulares_coperve"),
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
            f"# Crawler Coperve Vestibulares — falha\n\n```json\n{json.dumps(err_payload, indent=2)}\n```\n"
        )
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1

    rows = report.pop("standardized")
    std_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {**report, "standardized_path": str(std_path.resolve()), "exemplos_payload": rows[:3]}
    (out_root / "crawler_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md = [
        "# Crawler Wave 2 — Vestibulares UFSC (Coperve)",
        "",
        f"- **Fonte:** `{FONT}` | **tipo:** vestibular / programa_ingresso",
        f"- **Coleta (UTC):** `{summary['collected_at_utc']}`",
        f"- **URLs candidatas:** {summary.get('total_bruto_urls', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Nota:** {summary.get('fonte_escolhida_nota', '')}",
        "",
        "## Dry-run loader",
        "",
        "```bash",
        "python scripts/load_concursos_selecao.py --dry-run \\",
        "  --input-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_coperve/standardized \\",
        "  --output-dir audit_reports_main_pipeline/concursos_wave2_vestibulares_coperve/loader_dryrun \\",
        "  --sources coperve",
        "```",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
