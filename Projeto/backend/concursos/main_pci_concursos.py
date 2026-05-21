#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — PCI Concursos (listagem + páginas de notícia).

- Respeita robots.txt (não segue *.php nem caminhos Disallow).
- Intervalo configurável entre pedidos GET.
- Saída standardized para o loader `scripts/load_concursos_selecao.py`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from concursos.common import (  # noqa: E402
    build_concurso_item,
    extract_inscricao_fim_from_text,
    extract_prova_from_text,
    field_fill_stats,
    infer_nivel_escolaridade,
    infer_orgao_local_from_title,
    infer_status_concurso,
    infer_tipo_selecao,
    normalize_text,
    parse_all_dates_br,
    parse_remuneracao_taxa_br,
    parse_vagas,
    parse_vagas_cadastro_reserva,
    pci_infer_extraction_confidence,
    pci_infer_qualidade_dado,
    pci_missing_core_fields,
    recency_should_discard,
    validate_concurso_item,
)

BASE = "https://www.pciconcursos.com.br"
LISTING_PATH = "/concursos"
USER_AGENT = "EditalFinderConcursosBot/0.1 (wave1; polite crawl)"
PCI_FONT = "pci_concursos"


def _fetch(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(req, timeout=35) as resp:
        return resp.read().decode("utf-8", "replace")


def _robots_disallows(url: str, robots_parser) -> bool:
    if robots_parser is None:
        return False
    try:
        return not robots_parser.can_fetch(USER_AGENT, url)
    except Exception:
        return True


def _collect_noticia_urls(html: str, robots_parser) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[str] = []
    seen: Set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if "/noticias/" not in href:
            continue
        if href.rstrip("/").endswith("/noticias"):
            continue
        if ".php" in href.lower():
            continue
        full = href if href.startswith("http") else urljoin(BASE, href)
        if not full.startswith(BASE):
            continue
        path = urlparse(full).path or ""
        if path.count("/") < 2:
            continue
        slug = path.split("/noticias/")[-1].split("/")[0]
        if len(slug) < 12:
            continue
        if full in seen:
            continue
        if _robots_disallows(full, robots_parser):
            continue
        seen.add(full)
        out.append(full)
    return out


def _pick_official_link(soup: BeautifulSoup) -> Optional[str]:
    for a in soup.find_all("a", href=True):
        h = a["href"].strip()
        if not h.startswith("http"):
            continue
        low = h.lower()
        if "pciconcursos.com.br" in low:
            continue
        if "apostila" in low or "facebook.com" in low or "instagram.com" in low:
            continue
        if low.endswith(".pdf"):
            continue
        if "/noticias/" in low:
            continue
        return h.split("#")[0]
    return None


def _article_text(soup: BeautifulSoup) -> str:
    main = soup.find("article") or soup.find("main")
    if not main:
        main = soup.find("div", class_=re.compile(r"content", re.I))
    if main:
        return normalize_text(main.get_text(" ", strip=True))[:14000]
    return normalize_text(soup.get_text(" ", strip=True))[:14000]


def parse_noticia_page(url: str) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    og = soup.find("meta", property="og:title")
    tit = normalize_text(og.get("content") if og and og.get("content") else "")
    if not tit:
        t = soup.find("title")
        tit = normalize_text(t.get_text() if t else "")
    if not tit:
        for h in soup.find_all("h1"):
            tx = normalize_text(h.get_text())
            if len(tx) > 10:
                tit = tx
                break
    if not tit:
        tit = url
    body = _article_text(soup)
    data_fim = extract_inscricao_fim_from_text(body)
    data_prova = extract_prova_from_text(body)
    dates_iso = parse_all_dates_br(body)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    vagas = parse_vagas(body)
    if vagas is None:
        vagas = parse_vagas(tit)
    sal_min, sal_max, taxa, money_meta = parse_remuneracao_taxa_br(f"{tit}\n{body}")
    off = _pick_official_link(soup)
    return {
        "titulo": tit,
        "body": body,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "numero_vagas": vagas,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "official": off,
    }


def run_crawl(*, max_items: int, sleep_s: float, listing_url: str) -> Dict[str, Any]:
    from urllib.robotparser import RobotFileParser

    rp = RobotFileParser()
    try:
        rp.set_url(urljoin(BASE, "/robots.txt"))
        rp.read()
    except Exception:
        rp = None

    listing = listing_url
    if _robots_disallows(listing, rp):
        raise RuntimeError(f"robots.txt bloqueia listagem: {listing}")

    listing_html = _fetch(listing)
    urls = _collect_noticia_urls(listing_html, rp)[: max_items * 2]
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
            parsed = parse_noticia_page(url)
            body = parsed["body"]
            tit = parsed["titulo"]
            data_fim = parsed["data_fim_inscricao"]
            data_prova = parsed["data_prova"]
            data_pub = parsed["data_publicacao"]
            vagas = parsed["numero_vagas"]
            sal_min = parsed["salario_min"]
            sal_max = parsed["salario_max"]
            taxa = parsed["taxa_inscricao"]
            money_meta = parsed.get("money_meta") or {}
            off = parsed["official"]

            drop, why = recency_should_discard(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
                text_for_recent_heuristic=f"{tit} {body}",
            )
            if drop:
                discarded.append({"url": url, "titulo": tit, "motivo": why})
                continue

            tipo = infer_tipo_selecao(tit, body)
            status = infer_status_concurso(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
            )
            validacao = "incompleto" if not data_fim else "valido"

            geo = infer_orgao_local_from_title(tit)
            orgao = geo["orgao"]
            instituicao = geo["instituicao"]
            municipio = geo["municipio"]
            estado = geo["estado"]
            nivel = infer_nivel_escolaridade(tit, body)

            cad_res = parse_vagas_cadastro_reserva(f"{tit} {body}")

            extracted_fields: List[str] = []
            if orgao:
                extracted_fields.append("orgao_title")
            if instituicao:
                extracted_fields.append("instituicao_title")
            if municipio:
                extracted_fields.append("municipio_title")
            if estado:
                extracted_fields.append("estado_title")
            if nivel:
                extracted_fields.append("nivel_escolaridade_texto")
            if vagas is not None:
                extracted_fields.append("numero_vagas_texto")
            if sal_min is not None or sal_max is not None:
                extracted_fields.append("salario_texto")
            if taxa is not None:
                extracted_fields.append("taxa_inscricao_texto")
            if data_fim:
                extracted_fields.append("data_fim_inscricao_texto")
            if data_prova:
                extracted_fields.append("data_prova_texto")

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

            extras: Dict[str, Any] = {
                "crawler": "main_pci_concursos",
                "wave": "concursos_wave1_pci",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "pci_noticia_url": url,
                "official_link_missing": off is None,
                "extracted_fields": sorted(set(extracted_fields)),
                "missing_core_fields": missing_core,
                "extraction_confidence": confidence,
                "source_is_aggregator": True,
                "value_extraction_notes": list(money_meta.get("value_extraction_notes") or []),
                "possible_fee_detected": bool(money_meta.get("possible_fee_detected")),
                "possible_salary_detected": bool(money_meta.get("possible_salary_detected")),
            }
            if cad_res:
                extras["cadastro_reserva"] = True

            row = build_concurso_item(
                titulo=tit[:500],
                link=url,
                fonte=PCI_FONT,
                fonte_tipo="agregador",
                tipo_selecao=tipo,
                status=status,
                validacao_status=validacao,
                qualidade_dado=qualidade,
                extras=extras,
                categoria="agregado_pci",
                orgao=orgao,
                instituicao=instituicao,
                municipio=municipio,
                estado=estado,
                nivel_escolaridade=nivel,
                banca="PCI Concursos",
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
                data_publicacao=data_pub,
                data_inicio_inscricao=None,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                link_edital=off,
                tags=["pci", "wave1"],
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
        "fonte": PCI_FONT,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "listing_url": listing,
        "total_bruto_urls": len(urls),
        "total_discarded_all": len(discarded),
        "discarded": discarded[:120],
        "total_standardized": len(raw_rows),
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler piloto PCI → standardized JSON")
    ap.add_argument("--max-items", type=int, default=10, help="Máximo de notícias gravadas após filtros")
    ap.add_argument("--sleep", type=float, default=2.0, help="Pausa entre GET (segundos)")
    ap.add_argument(
        "--listing-url",
        default=BASE + LISTING_PATH,
        help="URL da listagem PCI (sem .php)",
    )
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave1_pci"),
        help="Pasta wave1 (cria standardized/ e relatórios)",
    )
    args = ap.parse_args()

    out_root = Path(args.output_root)
    std_dir = out_root / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)
    std_path = std_dir / f"{PCI_FONT}_standardized.json"

    try:
        report = run_crawl(max_items=args.max_items, sleep_s=args.sleep, listing_url=args.listing_url)
    except Exception as exc:
        err_payload = {"erro": str(exc), "listing_url": args.listing_url}
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "crawler_summary.json").write_text(
            json.dumps(err_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_root / "crawler_summary.md").write_text(
            f"# Crawler PCI — falha\n\n```json\n{json.dumps(err_payload, ensure_ascii=False, indent=2)}\n```\n"
        )
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1

    rows = report.pop("standardized")
    std_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    discarded = report.get("discarded", [])
    discarded_old_count = sum(
        1
        for d in discarded
        if any(
            x in (d.get("motivo") or "")
            for x in ("passada", "sem_datas", "antiguidade", "prova_passada")
        )
    )
    disc_examples = [d for d in discarded if d.get("motivo")][:20]
    summary = {
        **report,
        "discarded_old_items_count": discarded_old_count,
        "discarded_old_items_examples": disc_examples,
        "standardized_path": str(std_path.resolve()),
        "exemplos_payload": rows[:3],
    }
    (out_root / "crawler_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Crawler piloto — PCI Concursos",
        "",
        f"- **Fonte:** `{PCI_FONT}`",
        f"- **Coleta (UTC):** `{summary['collected_at_utc']}`",
        f"- **URLs brutas consideradas:** {summary.get('total_bruto_urls', 0)}",
        f"- **Descartados (total):** {summary.get('total_discarded_all', 0)}",
        f"- **Descartados (antiguidade / heurística):** {summary.get('discarded_old_items_count', 0)}",
        f"- **Standardized gravados:** {summary.get('total_standardized', 0)}",
        f"- **Ficheiro:** `{std_path.as_posix()}`",
        "",
        "## Campos preenchidos (contagem)",
        "",
        "```json",
        json.dumps(summary.get("field_fill", {}), ensure_ascii=False, indent=2),
        "```",
        "",
        "## Campos tipicamente ausentes neste piloto",
        "",
        ", ".join(summary.get("fields_always_missing", []) or ["(n/d)"]),
        "",
        "## Riscos",
        "",
        "- Agregador: texto editorial; datas podem estar incompletas → `validacao_status = incompleto`.",
        "- Link oficial pode faltar → `extras.official_link_missing`.",
        "- Respeitar sempre `robots.txt` e limites; não aumentar `--max-items` sem revisão.",
        "",
        "## Recomendação de apply",
        "",
        "**Não aplicar** automaticamente. Correr `scripts/load_concursos_selecao.py --dry-run` e só depois `apply` em staging com guardas.",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
