#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — Instituto AOCP (site público + API JSON oficial).

Diagnóstico (2026):
- **Site:** `https://www.institutoaocp.org.br/concursos/status/inscricoes-abertas` (SPA; dados via API).
- **API primária:** `https://link.institutoaocp.org.br/api/concursos` — lista + detalhe `{id}`.
- **API fallback:** `https://link.aocp.com.br/api/concursos` (legado, muitos FINISHED).
- Ficha pública: `https://www.institutoaocp.org.br/concursos/{id}/`.
- **robots.txt:** sinais de conteúdo Cloudflare; sem `Disallow` explícito para `/api/concursos` nas cópias analisadas;
  o script usa `RobotFileParser` + `--sleep` conservador.

Saída standardized para `scripts/load_concursos_selecao.py` (`fonte=aocp`).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from concursos.common import (  # noqa: E402
    build_concurso_item,
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

API_BASES: Tuple[str, ...] = (
    "https://link.institutoaocp.org.br",
    "https://link.aocp.com.br",
)
SITE_BASE = "https://www.institutoaocp.org.br"
SITE_BASE_LEGACY = "https://www.aocp.com.br"
DEFAULT_LISTING_PAGES = (
    f"{SITE_BASE}/concursos/status/inscricoes-abertas",
    f"{SITE_BASE}/concursos/status/novos",
)
STATUS_BY_LISTING_SLUG = {
    # IN_PROGRESS na API inclui processos com inscrição já encerrada (status desatualizado).
    # NEW traz editais «em breve» com `dataInscricao` futura na lista.
    "inscricoes-abertas": ("IN_PROGRESS", "NEW"),
    "novos": ("NEW",),
    "em-andamento": ("IN_PROGRESS", "SUBSCRIBE"),
}
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "aocp"
BANCA = "Instituto AOCP"

_RE_NON_OPP = (
    r"divulgado\s+o\s+edital\s+de\s+resultado\s+final",
    r"\bresultado\s+final\b",
    r"gabarito\s+definitivo",
    r"homologa[cç][aã]o\s+do\s+resultado\s+final",
    r"convoca[cç][aã]o\s+para\s+t[ií]tulos?\s*$",
)


def _load_robots_parser(base: str):
    """Carrega robots.txt. Se não houver blocos `User-agent:` (ex.: só comentários),
    devolve None — interpretação conservadora: não há restrições máquina-legíveis via RobotFileParser."""
    from urllib.robotparser import RobotFileParser

    netloc = urlsplit(base).netloc
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


def _robots_disallows(url: str, rp) -> bool:
    if rp is None:
        return False
    try:
        return not rp.can_fetch(USER_AGENT, url)
    except Exception:
        return True


def _fetch_json(url: str) -> Any:
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
    )
    with urlopen(req, timeout=60) as resp:
        raw = resp.read()
    return json.loads(raw.decode("utf-8"))


def _parse_aocp_datetime_to_iso_date(s: Optional[str]) -> Optional[str]:
    if not s or not str(s).strip():
        return None
    s = str(s).strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m2 = re.match(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m2:
        d, mo, y = int(m2.group(1)), int(m2.group(2)), int(m2.group(3))
        try:
            return date(y, mo, d).isoformat()
        except ValueError:
            return None
    return None


def _pick_link_edital(publicacoes: Any) -> Optional[str]:
    if not isinstance(publicacoes, list):
        return None
    best: Optional[str] = None
    for pub in publicacoes:
        if not isinstance(pub, dict):
            continue
        nome = normalize_text(str(pub.get("nome") or "")).lower()
        url = (pub.get("url") or "").strip()
        if not url.lower().endswith(".pdf"):
            continue
        if re.search(r"edital\s+de\s+abertura|edital\s+n[ºo°]?\s*\d", nome) and "homolog" not in nome:
            return url.split("#")[0]
        if "abertura" in nome and "homolog" not in nome and best is None:
            best = url.split("#")[0]
    return best


def aocp_should_discard_non_opportunity(*, titulo: str, chamada: str) -> Tuple[bool, str]:
    blob = f"{titulo}\n{chamada}".lower()
    for pat in _RE_NON_OPP:
        if re.search(pat, blob, re.I):
            return True, "aocp_nao_oportunidade_ativa"
    return False, ""


def _api_list_url(api_base: str) -> str:
    return f"{api_base.rstrip('/')}/api/concursos"


def _fetch_concursos_list() -> Tuple[List[Dict[str, Any]], str]:
    """Tenta API primária (institutoaocp) e fallback (link.aocp legado)."""
    last_err: Optional[Exception] = None
    for base in API_BASES:
        url = _api_list_url(base)
        try:
            data = _fetch_json(url)
            if isinstance(data, list) and data:
                return data, base
        except Exception as exc:
            last_err = exc
            continue
    if last_err:
        raise last_err
    raise RuntimeError("Nenhuma API AOCP retornou lista")


def _detail_for_list_id(list_id: int, api_base: str) -> Optional[Dict[str, Any]]:
    url = f"{api_base.rstrip('/')}/api/concursos/{list_id}"
    data = _fetch_json(url)
    if isinstance(data, list) and data and isinstance(data[0], dict):
        return data[0]
    return None


def _parse_vagas_remuneracao(detail: Dict[str, Any], blob: str) -> Tuple[Optional[int], Optional[float], Optional[float], Optional[float], Dict[str, Any]]:
    nv = detail.get("vagas")
    numero = int(nv) if isinstance(nv, int) else (int(nv) if isinstance(nv, str) and nv.isdigit() else None)
    rem = detail.get("remuneracao")
    sal_min = sal_max = None
    money_meta: Dict[str, Any] = {}
    if rem is not None and str(rem).strip():
        blob2 = f"{blob}\n{rem}"
        sal_min, sal_max, taxa, money_meta = parse_remuneracao_taxa_br(blob2)
        return numero, sal_min, sal_max, taxa, money_meta
    sal_min, sal_max, taxa, money_meta = parse_remuneracao_taxa_br(blob)
    return numero, sal_min, sal_max, taxa, money_meta


def _status_filter_from_arg(include_only_status: str) -> Tuple[str, ...]:
    raw = include_only_status.strip()
    if not raw:
        return ("IN_PROGRESS",)
    if "," in raw:
        return tuple(s.strip().upper() for s in raw.split(",") if s.strip())
    slug = raw.lower()
    if slug in STATUS_BY_LISTING_SLUG:
        return STATUS_BY_LISTING_SLUG[slug]
    return (raw.upper(),)


def run_crawl(
    *,
    max_items: int,
    sleep_s: float,
    include_only_status: str,
    api_base_override: Optional[str] = None,
) -> Dict[str, Any]:
    rp_site = _load_robots_parser(SITE_BASE)
    time.sleep(sleep_s)
    if api_base_override:
        raw_list = _fetch_json(_api_list_url(api_base_override))
        api_base_used = api_base_override
    else:
        raw_list, api_base_used = _fetch_concursos_list()

    rp_api = _load_robots_parser(api_base_used)
    list_url = _api_list_url(api_base_used)
    if _robots_disallows(list_url, rp_api):
        raise RuntimeError(f"robots.txt bloqueia listagem: {list_url}")

    want_statuses = _status_filter_from_arg(include_only_status)
    candidates: List[Dict[str, Any]] = []
    for it in raw_list:
        if not isinstance(it, dict):
            continue
        st = str(it.get("status") or "").strip().upper()
        if st in want_statuses:
            candidates.append(it)

    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    raw_rows: List[Dict[str, Any]] = []
    today = date.today()

    for it in candidates:
        if len(raw_rows) >= max_items:
            break
        lid = it.get("id")
        if not isinstance(lid, int):
            continue
        nome_l = normalize_text(str(it.get("nome") or ""))
        cham_l = normalize_text(str(it.get("chamada") or ""))
        drop_no, why_no = aocp_should_discard_non_opportunity(titulo=nome_l, chamada=cham_l)
        if drop_no:
            discarded.append({"id": lid, "titulo": nome_l, "motivo": why_no})
            continue

        detail_url = f"{api_base_used.rstrip('/')}/api/concursos/{lid}"
        if _robots_disallows(detail_url, rp_api):
            discarded.append({"id": lid, "motivo": "robots_disallow_detail"})
            continue

        try:
            time.sleep(sleep_s)
            detail = _detail_for_list_id(lid, api_base_used)
            if not detail:
                errors.append({"id": lid, "erro": "detalhe_vazio"})
                continue

            tit = normalize_text(str(detail.get("nome") or nome_l))
            cham = normalize_text(str(detail.get("chamada") or cham_l))
            blob = f"{tit}\n{cham}"

            drop_no2, why_no2 = aocp_should_discard_non_opportunity(titulo=tit, chamada=cham)
            if drop_no2:
                discarded.append({"id": lid, "titulo": tit, "motivo": why_no2})
                continue

            di = _parse_aocp_datetime_to_iso_date(detail.get("dataInicioInscricao"))
            df = _parse_aocp_datetime_to_iso_date(detail.get("dataFinalInscricao"))
            if not df:
                df = _parse_aocp_datetime_to_iso_date(str(it.get("dataInscricao") or ""))

            pub = detail.get("publicacoes")
            link_edital = _pick_link_edital(pub)

            data_prova = extract_prova_from_text(blob)
            dates_iso = parse_all_dates_br(blob)
            data_pub = dates_iso[0].isoformat() if dates_iso else di

            numero, sal_min, sal_max, taxa, money_meta = _parse_vagas_remuneracao(detail, blob)

            st_detail = str(detail.get("status") or it.get("status") or "").upper()
            if st_detail not in ("NEW", "SUBSCRIBE"):
                drop_r, why_r = recency_should_discard(
                    data_fim_inscricao=df,
                    data_prova=data_prova,
                    today=today,
                    text_for_recent_heuristic=blob,
                )
                if drop_r:
                    discarded.append({"id": lid, "titulo": tit, "motivo": why_r})
                    continue

            tipo, tipo_evid = infer_tipo_selecao_meta(tit, blob)
            status = infer_status_concurso(
                data_fim_inscricao=df,
                data_prova=data_prova,
                today=today,
            )
            if df and link_edital:
                validacao = "valido"
            else:
                validacao = "incompleto"

            geo = infer_orgao_local_from_title(tit)
            orgao = geo["orgao"] or tit[:500]
            instituicao = geo["instituicao"] or orgao
            municipio = geo["municipio"]
            estado = geo["estado"]
            nivel = infer_nivel_escolaridade(tit, blob)

            cargo_txt: Optional[str] = None
            cargos = detail.get("cargos")
            if isinstance(cargos, str) and cargos.strip():
                cargo_txt = cargos.strip()[:400]
            elif isinstance(cargos, list) and cargos:
                cargo_txt = str(cargos[0])[:400] if cargos[0] else None

            link_publico = f"{SITE_BASE}/concursos/{lid}/"
            if _robots_disallows(link_publico, rp_site):
                link_publico = f"{SITE_BASE_LEGACY}/concursos/{lid}/"
            if _robots_disallows(link_publico, rp_site):
                discarded.append({"id": lid, "titulo": tit, "motivo": "robots_disallow_pagina_publica"})
                continue

            partial_core: Dict[str, Any] = {
                "data_fim_inscricao": df,
                "data_prova": data_prova,
                "orgao": orgao,
                "estado": estado,
                "instituicao": instituicao,
                "link_edital": link_edital,
                "numero_vagas": numero,
            }
            missing_core = pci_missing_core_fields(partial_core)
            confidence = pci_infer_extraction_confidence(
                orgao=orgao,
                instituicao=instituicao,
                estado=estado,
                data_fim_inscricao=df,
                data_prova=data_prova,
                numero_vagas=numero,
                salario_max=sal_max,
            )
            qualidade = pci_infer_qualidade_dado(
                titulo=tit,
                link=link_publico,
                orgao=orgao,
                instituicao=instituicao,
                estado=estado,
                municipio=municipio,
                data_fim_inscricao=df,
                data_prova=data_prova,
                data_publicacao=data_pub,
                numero_vagas=numero,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
            )
            if link_edital is None and not df:
                qualidade = "baixa"
            elif not df and link_edital:
                qualidade = "media"
            if validacao == "valido":
                qualidade = pci_infer_qualidade_dado(
                    titulo=tit,
                    link=link_publico,
                    orgao=orgao,
                    instituicao=instituicao,
                    estado=estado,
                    municipio=municipio,
                    data_fim_inscricao=df,
                    data_prova=data_prova,
                    data_publicacao=data_pub,
                    numero_vagas=numero,
                    salario_min=sal_min,
                    salario_max=sal_max,
                    taxa_inscricao=taxa,
                )
                if qualidade == "baixa":
                    qualidade = "media"

            notes = list((money_meta or {}).get("value_extraction_notes") or [])
            if not link_edital:
                notes.append("edital_pdf_nao_identificado_em_publicacoes")
            confidence = pci_adjust_confidence_for_ambiguity(confidence, value_extraction_notes=notes)

            extracted_fields: List[str] = []
            if sal_min is not None or sal_max is not None:
                extracted_fields.append("salario_texto")
            if taxa is not None:
                extracted_fields.append("taxa_inscricao_texto")
            if data_prova:
                extracted_fields.append("data_prova_texto")
            if df:
                extracted_fields.append("data_fim_inscricao_texto")
            if di:
                extracted_fields.append("data_inicio_inscricao_texto")
            if numero is not None:
                extracted_fields.append("numero_vagas_texto")

            extras: Dict[str, Any] = {
                "crawler": "main_aocp_concursos",
                "wave": "concursos_wave1_aocp",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "aocp_api_list": list_url,
                "aocp_api_base": api_base_used,
                "aocp_listing_pages": list(DEFAULT_LISTING_PAGES),
                "aocp_list_id": lid,
                "aocp_api_status_list": str(it.get("status") or ""),
                "aocp_api_status_detail": str(detail.get("status") or ""),
                "official_link_missing": link_edital is None,
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
                link=link_publico,
                fonte=FONT,
                fonte_tipo="banca",
                tipo_selecao=tipo,
                status=status,
                validacao_status=validacao,
                qualidade_dado=qualidade,
                extras=extras,
                categoria="banca_aocp_concurso",
                orgao=orgao,
                instituicao=instituicao,
                banca=BANCA,
                cargo=cargo_txt,
                area=None,
                nivel_escolaridade=nivel,
                estado=estado,
                municipio=municipio,
                numero_vagas=numero,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
                data_publicacao=data_pub,
                data_inicio_inscricao=di,
                data_fim_inscricao=df,
                data_prova=data_prova,
                link_edital=link_edital,
                tags=["aocp", "wave1"],
            )
            verr = validate_concurso_item(row)
            if verr:
                errors.append({"id": lid, "erros": verr})
                continue
            raw_rows.append(row)
        except Exception as exc:
            errors.append({"id": lid, "erro": str(exc)})

    filled, missing = field_fill_stats(raw_rows)
    return {
        "fonte": FONT,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "list_url": list_url,
        "api_base": api_base_used,
        "include_only_status": list(want_statuses),
        "total_lista_api": len(raw_list),
        "total_bruto_lista_filtrada": len(candidates),
        "total_discarded_all": len(discarded),
        "discarded": discarded[:200],
        "total_standardized": len(raw_rows),
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler piloto AOCP → standardized JSON")
    ap.add_argument("--max-items", type=int, default=10, help="Máximo de concursos gravados (após filtros)")
    ap.add_argument("--sleep", type=float, default=1.5, help="Pausa entre pedidos (segundos)")
    ap.add_argument(
        "--include-only-status",
        type=str,
        default="inscricoes-abertas",
        help="Status API (IN_PROGRESS, NEW, …) ou slug de listagem (inscricoes-abertas, novos)",
    )
    ap.add_argument(
        "--api-base",
        type=str,
        default="",
        help="Forçar base da API (ex.: https://link.institutoaocp.org.br)",
    )
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave1_aocp"),
        help="Pasta wave1 AOCP",
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
            include_only_status=args.include_only_status,
            api_base_override=(args.api_base.strip() or None),
        )
    except Exception as exc:
        err_payload = {"erro": str(exc)}
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "crawler_summary.json").write_text(
            json.dumps(err_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_root / "crawler_summary.md").write_text(
            f"# Crawler AOCP — falha\n\n```json\n{json.dumps(err_payload, ensure_ascii=False, indent=2)}\n```\n"
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
        "# Crawler piloto — Instituto AOCP",
        "",
        f"- **Fonte:** `{FONT}`",
        f"- **API lista:** `{summary.get('list_url', '')}`",
        f"- **Filtro status lista:** `{summary.get('include_only_status', [])}`",
        f"- **Coleta (UTC):** `{summary['collected_at_utc']}`",
        f"- **Registos na API (total):** {summary.get('total_lista_api', 0)}",
        f"- **Candidatos (lista filtrada `{args.include_only_status}`):** {summary.get('total_bruto_lista_filtrada', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Ficheiro:** `{std_path.as_posix()}`",
        "",
        "## Próximo passo",
        "",
        "`python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_aocp/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_aocp/loader_dryrun --sources aocp`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
