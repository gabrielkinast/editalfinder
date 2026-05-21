#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — Cebraspe (API pública PAS + páginas web de referência).

Diagnóstico (2026):
- As rotas https://www.cebraspe.org.br/concursos/* devolvem shell SPA (“habilitar javascript”);
  a listagem real é alimentada por JSON em https://apis.cebraspe.org.br/cebraspe/ (mesmo host
  referenciado no bundle `main.*.chunk.js` do site).
- Endpoint utilizado neste piloto: `GET pas/subprogramas` — Programa de Avaliação Seriada (PAS)
  associado ao portal de concursos Cebraspe. Outros “concursos públicos” da banca podem existir
  noutros canais; não há endpoint público descoberto aqui além de PAS.

- Respeita pausa entre pedidos; um único GET à API para a listagem (sem scraping agressivo).
- Saída standardized para `scripts/load_concursos_selecao.py` (`fonte=cebraspe`).
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

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from concursos.common import (  # noqa: E402
    build_concurso_item,
    field_fill_stats,
    infer_nivel_escolaridade,
    infer_status_concurso,
    infer_tipo_selecao_meta,
    normalize_text,
    pci_adjust_confidence_for_ambiguity,
    pci_infer_extraction_confidence,
    pci_infer_qualidade_dado,
    pci_missing_core_fields,
    recency_should_discard,
    validate_concurso_item,
)

API_PAS_SUBPROGRAMAS = "https://apis.cebraspe.org.br/cebraspe/pas/subprogramas"
PUBLIC_BASE = "https://www.cebraspe.org.br"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "cebraspe"
BANCA = "Cebraspe"


def _fetch_json(url: str, *, sleep_s: float) -> Any:
    time.sleep(sleep_s)
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json, */*;q=0.1",
            "Accept-Language": "pt-BR,pt;q=0.9",
        },
    )
    with urlopen(req, timeout=45) as resp:
        raw = resp.read().decode("utf-8", "replace")
    return json.loads(raw)


def _iso_to_date_str(iso: Optional[str]) -> Optional[str]:
    if not iso or not isinstance(iso, str):
        return None
    s = iso.strip()
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return s[:10]
    return None


_RE_BR_DATA = re.compile(r"^(\d{1,2})/(\d{1,2})/(\d{4})$")


def _br_data_to_iso(s: Optional[str]) -> Optional[str]:
    if not s or not isinstance(s, str):
        return None
    m = _RE_BR_DATA.match(s.strip())
    if not m:
        return None
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        return date(y, mo, d).isoformat()
    except ValueError:
        return None


def _iso_dt_to_date_str(iso: Optional[str]) -> Optional[str]:
    return _iso_to_date_str(iso)


def _etapa_inicio_fim(etapa: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    ev = etapa.get("eventoDaEtapa") or {}
    ini = _iso_dt_to_date_str(ev.get("dataIniInscricao")) or _br_data_to_iso(
        etapa.get("strDataInicioInscricao")
    )
    fim = _iso_dt_to_date_str(ev.get("dataFimInscricao")) or _br_data_to_iso(
        etapa.get("strDataFimInscricao")
    )
    return ini, fim


def _etapa_data_prova(etapa: Dict[str, Any]) -> Optional[str]:
    return _iso_dt_to_date_str(etapa.get("dataProva"))


def _first_edital_url(etapa: Dict[str, Any]) -> Optional[str]:
    ar = etapa.get("arquivosEdital")
    if isinstance(ar, list):
        for item in ar:
            if isinstance(item, dict):
                u = item.get("url") or item.get("link") or item.get("href")
                if u and str(u).strip().lower().startswith("http"):
                    return str(u).strip().split("#")[0]
    return None


def _etapa_parece_resultado_ou_gabarito(etapa: Dict[str, Any]) -> bool:
    blob = f"{etapa.get('etapaDescricao', '')}".lower()
    if re.search(r"(?i)\b(gabarito|resultado\s+final|homologa[cç][aã]o|convoca[cç][aã]o\s+final)\b", blob):
        return True
    if etapa.get("arquivosGabarito"):
        return True
    return False


def _etapa_encerrada(etapa: Dict[str, Any], today: date) -> bool:
    if etapa.get("provaRealizada") == 1:
        return True
    _, fim = _etapa_inicio_fim(etapa)
    dp = _etapa_data_prova(etapa)
    df = None
    if fim:
        try:
            df = date.fromisoformat(fim)
        except ValueError:
            df = None
    dprov = None
    if dp:
        try:
            dprov = date.fromisoformat(dp)
        except ValueError:
            dprov = None
    if df is not None and df < today and (dprov is None or dprov < today):
        return True
    if df is None and dprov is not None and dprov < today:
        return True
    return False


def _pick_primary_etapa(etapas: List[Dict[str, Any]], today: date) -> Optional[Dict[str, Any]]:
    """Escolhe uma etapa representativa: vigente > inscrições/prova futuras > primeira ainda não encerrada."""
    if not etapas:
        return None
    candidatas: List[Dict[str, Any]] = []
    for e in etapas:
        if _etapa_parece_resultado_ou_gabarito(e) and _etapa_encerrada(e, today):
            continue
        if _etapa_parece_resultado_ou_gabarito(e):
            ev = e.get("eventoDaEtapa") or {}
            fim = _iso_dt_to_date_str(ev.get("dataFimInscricao"))
            if fim:
                try:
                    if date.fromisoformat(fim) < today:
                        continue
                except ValueError:
                    pass
        candidatas.append(e)
    pool = candidatas or etapas

    for e in pool:
        if e.get("isEtapaVigente") is True:
            return e
    for e in pool:
        _, fim = _etapa_inicio_fim(e)
        if fim:
            try:
                if date.fromisoformat(fim) >= today:
                    return e
            except ValueError:
                continue
    for e in pool:
        dp = _etapa_data_prova(e)
        if dp:
            try:
                if date.fromisoformat(dp) >= today:
                    return e
            except ValueError:
                continue
    return pool[0]


def _subprograma_discard_reason(
    sp: Dict[str, Any], etapa: Dict[str, Any], today: date
) -> Tuple[bool, str]:
    if _etapa_parece_resultado_ou_gabarito(etapa) and _etapa_encerrada(etapa, today):
        return True, "etapa_resultado_ou_gabarito_encerrada"
    if _etapa_encerrada(etapa, today):
        return True, "cebraspe_pas_etapa_encerrada"
    return False, ""


def _build_titulo(sp: Dict[str, Any], etapa: Dict[str, Any]) -> str:
    desc = normalize_text(str(sp.get("subProgramaDescricao") or "PAS"))
    et = normalize_text(str(etapa.get("etapaDescricao") or ""))
    if et:
        return normalize_text(f"PAS — {desc} — {et} (Cebraspe)")
    return normalize_text(f"PAS — {desc} (Cebraspe)")


def run_crawl(*, max_items: int, sleep_s: float, as_of: Optional[date] = None) -> Dict[str, Any]:
    """as_of: data de referência para encerramento/recência (default: hoje). Útil para reproduzir cenários com API histórica."""
    today = as_of or date.today()
    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    raw_rows: List[Dict[str, Any]] = []

    try:
        data = _fetch_json(API_PAS_SUBPROGRAMAS, sleep_s=sleep_s)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {
            "fonte": FONT,
            "collected_at_utc": datetime.now(timezone.utc).isoformat(),
            "as_of_date": (as_of or date.today()).isoformat(),
            "api_url": API_PAS_SUBPROGRAMAS,
            "total_bruto_api": 0,
            "total_discarded_all": 0,
            "discarded": [],
            "total_standardized": 0,
            "errors": [{"erro": str(exc), "fase": "fetch_api"}],
            "field_fill": {},
            "fields_always_missing": [],
            "standardized": [],
        }

    if not isinstance(data, list):
        errors.append({"erro": "api_formato_inesperado", "tipo": type(data).__name__})
        data = []

    total_bruto = len(data)

    for sp in data:
        if len(raw_rows) >= max_items:
            break
        sid = sp.get("subProgramaId")
        etapas = sp.get("etapas") if isinstance(sp.get("etapas"), list) else []
        etapa = _pick_primary_etapa(etapas, today)
        if etapa is None:
            discarded.append(
                {
                    "subProgramaId": sid,
                    "motivo": "sem_etapas",
                }
            )
            continue

        drop, why = _subprograma_discard_reason(sp, etapa, today)
        if drop:
            discarded.append({"subProgramaId": sid, "motivo": why})
            continue

        tit = _build_titulo(sp, etapa)
        blob = f"{tit}\n{etapa.get('etapaDescricao', '')}"
        tipo, tipo_evid = infer_tipo_selecao_meta(tit, blob)
        if tipo not in ("programa_ingresso", "vestibular"):
            tipo = "programa_ingresso"

        ini, fim = _etapa_inicio_fim(etapa)
        d_prova = _etapa_data_prova(etapa)
        off = _first_edital_url(etapa)

        drop_r, why_r = recency_should_discard(
            data_fim_inscricao=fim,
            data_prova=d_prova,
            today=today,
            text_for_recent_heuristic=blob,
        )
        if drop_r:
            discarded.append({"subProgramaId": sid, "titulo": tit, "motivo": why_r})
            continue

        status = infer_status_concurso(
            data_fim_inscricao=fim,
            data_prova=d_prova,
            today=today,
        )

        if fim and off:
            validacao = "valido"
        else:
            validacao = "incompleto"

        orgao = "Universidade de Brasília"
        instituicao = "Universidade de Brasília"
        municipio = "Brasília"
        estado = "DF"
        nivel = infer_nivel_escolaridade(tit, blob) or "superior"

        partial_core: Dict[str, Any] = {
            "data_fim_inscricao": fim,
            "data_prova": d_prova,
            "orgao": orgao,
            "estado": estado,
            "instituicao": instituicao,
            "link_edital": off,
            "numero_vagas": None,
        }
        missing_core = pci_missing_core_fields(partial_core)
        confidence = pci_infer_extraction_confidence(
            orgao=orgao,
            instituicao=instituicao,
            estado=estado,
            data_fim_inscricao=fim,
            data_prova=d_prova,
            numero_vagas=None,
            salario_max=None,
        )
        qualidade = pci_infer_qualidade_dado(
            titulo=tit,
            link=f"{PUBLIC_BASE}/concursos/pas/{sid}",
            orgao=orgao,
            instituicao=instituicao,
            estado=estado,
            municipio=municipio,
            data_fim_inscricao=fim,
            data_prova=d_prova,
            data_publicacao=None,
            numero_vagas=None,
            salario_min=None,
            salario_max=None,
            taxa_inscricao=None,
        )
        if validacao != "valido":
            qualidade = qualidade if qualidade in ("baixa", "media") else "media"

        notes: List[str] = [
            "fonte_api_pas_subprogramas",
            f"subProgramaId={sid}",
            f"etapaId={etapa.get('etapaId')}",
        ]
        if off is None:
            notes.append("link_edital_ausente_na_api")
        confidence = pci_adjust_confidence_for_ambiguity(confidence, value_extraction_notes=notes)

        extras: Dict[str, Any] = {
            "crawler": "main_cebraspe_concursos",
            "wave": "concursos_wave1_cebraspe",
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
            "cebraspe_api_url": API_PAS_SUBPROGRAMAS,
            "cebraspe_subprograma_id": sid,
            "cebraspe_etapa_id": etapa.get("etapaId"),
            "cebraspe_periodo": sp.get("periodo"),
            "official_link_missing": off is None,
            "extracted_fields": sorted(
                {
                    "data_fim_inscricao_api",
                    "data_inicio_inscricao_api",
                    "data_prova_api",
                    "orgao_inferido_pas_unb",
                }
            ),
            "missing_core_fields": missing_core,
            "extraction_confidence": confidence,
            "source_is_aggregator": False,
            "value_extraction_notes": notes,
            "tipo_selecao_evidencia": tipo_evid,
            "possible_fee_detected": False,
            "possible_salary_detected": False,
        }

        row = build_concurso_item(
            titulo=tit[:500],
            link=f"{PUBLIC_BASE}/concursos/pas/{sid}",
            fonte=FONT,
            fonte_tipo="banca",
            tipo_selecao=tipo,
            status=status,
            validacao_status=validacao,
            qualidade_dado=qualidade,
            extras=extras,
            categoria="banca_cebraspe_pas",
            orgao=orgao,
            instituicao=instituicao,
            banca=BANCA,
            cargo=None,
            area=None,
            nivel_escolaridade=nivel,
            estado=estado,
            municipio=municipio,
            numero_vagas=None,
            salario_min=None,
            salario_max=None,
            taxa_inscricao=None,
            data_publicacao=None,
            data_inicio_inscricao=ini,
            data_fim_inscricao=fim,
            data_prova=d_prova,
            link_edital=off,
            tags=["cebraspe", "wave1", "pas"],
        )
        verr = validate_concurso_item(row)
        if verr:
            errors.append({"subProgramaId": sid, "erros": verr})
            continue
        raw_rows.append(row)

    filled, missing = field_fill_stats(raw_rows)
    return {
        "fonte": FONT,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "as_of_date": today.isoformat(),
        "api_url": API_PAS_SUBPROGRAMAS,
        "total_bruto_api": total_bruto,
        "total_discarded_all": len(discarded),
        "discarded": discarded[:200],
        "total_standardized": len(raw_rows),
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler piloto Cebraspe (API PAS) → standardized JSON")
    ap.add_argument("--max-items", type=int, default=12, help="Máximo de subprogramas gravados")
    ap.add_argument("--sleep", type=float, default=1.5, help="Pausa antes do GET à API (segundos)")
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave1_cebraspe"),
        help="Pasta wave1 Cebraspe",
    )
    ap.add_argument(
        "--as-of-date",
        type=str,
        default="",
        help="Data de referência YYYY-MM-DD (encerrados/recência). Vazio = hoje.",
    )
    args = ap.parse_args()
    as_of: Optional[date] = None
    if str(args.as_of_date).strip():
        try:
            as_of = date.fromisoformat(str(args.as_of_date).strip()[:10])
        except ValueError:
            print("[AVISO] --as-of-date inválido; usando hoje.", file=sys.stderr)

    out_root = Path(args.output_root)
    std_dir = out_root / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)
    std_path = std_dir / f"{FONT}_standardized.json"

    try:
        report = run_crawl(max_items=args.max_items, sleep_s=args.sleep, as_of=as_of)
    except Exception as exc:
        err_payload = {"erro": str(exc)}
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "crawler_summary.json").write_text(
            json.dumps(err_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_root / "crawler_summary.md").write_text(
            f"# Crawler Cebraspe — falha\n\n```json\n{json.dumps(err_payload, ensure_ascii=False, indent=2)}\n```\n"
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
        "# Crawler piloto — Cebraspe (API PAS)",
        "",
        f"- **Fonte:** `{FONT}`",
        f"- **API:** `{API_PAS_SUBPROGRAMAS}`",
        f"- **Coleta (UTC):** `{summary['collected_at_utc']}`",
        f"- **as_of_date:** `{summary.get('as_of_date', '')}`",
        f"- **Itens brutos (API):** {summary.get('total_bruto_api', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Ficheiro:** `{std_path.as_posix()}`",
        "",
        "## Nota",
        "",
        "Listagem web `/concursos/*` é SPA; este piloto usa apenas o JSON oficial exposto pela app.",
        "",
        "## Próximo passo",
        "",
        "`python scripts/load_concursos_selecao.py --dry-run --input-dir audit_reports_main_pipeline/concursos_wave1_cebraspe/standardized --output-dir audit_reports_main_pipeline/concursos_wave1_cebraspe/loader_dryrun --sources cebraspe`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
