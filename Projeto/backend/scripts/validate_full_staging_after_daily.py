#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "CORE"
DEFAULT_REPORT_DIR = ROOT / "audit_reports_main_pipeline"

ENV_CANDIDATES = [
    ROOT / ".env.staging",
    ROOT / ".env.local",
    ROOT / ".env",
    CORE / ".env",
]

NOISE_TITLES = (
    "entre em contato",
    "fale conosco",
    "ouvidoria",
    "internet banking",
    "conta pj",
    "conta digital",
    "acesse sua conta",
    "abra sua conta",
    "atendimento",
    "faq",
    "quem somos",
    "trabalhe conosco",
    "menu",
)

EXPERIMENTAL_SOURCES = {"eurekalert_science_filtered"}


def _load_env_files() -> List[str]:
    loaded: List[str] = []
    for p in ENV_CANDIDATES:
        if p.is_file():
            load_dotenv(dotenv_path=p, override=False)
            loaded.append(str(p.resolve()))
    return loaded


def _mask_host(url: str) -> str:
    if not url:
        return ""
    try:
        host = urlparse(url).hostname or ""
        return host[:3] + "***" + host[-3:] if len(host) > 6 else "***"
    except Exception:
        return "***"


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def _guard() -> Tuple[bool, Dict[str, Any]]:
    env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
    url = os.getenv("SUPABASE_URL", "").strip()
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.getenv("SUPABASE_KEY", "").strip()
        or os.getenv("SUPABASE_ANON_KEY", "").strip()
    )
    reason = ""
    if env in ("production", "prod"):
        reason = "environment_marked_production"
    elif env not in ("staging", "local"):
        reason = "invalid_editalfinder_env"
    elif not url:
        reason = "missing_supabase_url"
    elif not key:
        reason = "missing_supabase_key"
    return reason == "", {
        "editalfinder_env": env,
        "has_supabase_url": bool(url),
        "has_key": bool(key),
        "url_host_masked": _mask_host(url),
        "block_reason": reason,
    }


def _client() -> Any:
    from supabase import create_client

    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.getenv("SUPABASE_KEY", "").strip()
        or os.getenv("SUPABASE_ANON_KEY", "").strip()
    )
    return create_client(os.getenv("SUPABASE_URL", "").strip(), key)


def _is_empty(v: Any) -> bool:
    return v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, (list, dict)) and not v)


def _as_list(v: Any) -> List[Any]:
    if isinstance(v, list):
        return v
    return []


def _row_source(row: Dict[str, Any]) -> str:
    return str(row.get("fonte_recurso") or row.get("fonte") or "sem_fonte").strip() or "sem_fonte"


def _noise_term(row: Dict[str, Any]) -> str:
    title = str(row.get("titulo") or "").casefold()
    for term in NOISE_TITLES:
        if term in title:
            return term
    if title in {"menu", "faq"}:
        return title
    return ""


def _credit_incoherent_reason(row: Dict[str, Any]) -> str:
    ex = row.get("extras") if isinstance(row.get("extras"), dict) else {}
    blob = " ".join(
        str(x or "")
        for x in (
            row.get("titulo"),
            row.get("descricao"),
            row.get("tipo_recurso"),
            row.get("tipo_oportunidade"),
            row.get("natureza_recurso"),
            row.get("linha_credito"),
            ex.get("tipo_recurso"),
            ex.get("tipo_oportunidade"),
            ex.get("natureza_recurso"),
            ex.get("linha_credito"),
        )
    ).casefold()
    tipo_recurso = str(row.get("tipo_recurso") or ex.get("tipo_recurso") or "").casefold()
    tipo_oportunidade = str(row.get("tipo_oportunidade") or ex.get("tipo_oportunidade") or "").strip()
    natureza = str(row.get("natureza_recurso") or ex.get("natureza_recurso") or "").strip()
    reemb = row.get("reembolsavel")
    has_credit = any(x in blob for x in ("crédito", "credito", "financiamento", "linha de crédito", "linha de credito"))
    has_grant = any(x in blob for x in ("subvenção", "subvencao"))
    if has_grant and "subven" in tipo_recurso:
        return "subvenção detectada sem evidência suficiente de recurso não reembolsável"
    if has_credit and _is_empty(reemb) and not natureza:
        return "crédito/financiamento sem reembolsavel nem natureza_recurso preenchidos"
    if has_credit and not tipo_oportunidade:
        return "linha de crédito/financiamento sem tipo_oportunidade"
    return "campos de crédito/financiamento incoerentes"


def _credit_validation_exempt(row: Dict[str, Any]) -> bool:
    ex = row.get("extras") if isinstance(row.get("extras"), dict) else {}
    corpus = " ".join(
        str(x or "")
        for x in (
            row.get("titulo"),
            row.get("descricao"),
            row.get("link"),
            row.get("tipo_recurso"),
            row.get("tipo_oportunidade"),
            row.get("natureza_recurso"),
            ex.get("tipo_recurso"),
            ex.get("tipo_oportunidade"),
            ex.get("natureza_recurso"),
            ex.get("linha_credito"),
        )
    ).casefold()
    tipo_blob = " ".join(
        str(x or "")
        for x in (
            row.get("tipo_recurso"),
            row.get("tipo_oportunidade"),
            row.get("natureza_recurso"),
            ex.get("tipo_recurso"),
            ex.get("tipo_oportunidade"),
            ex.get("natureza_recurso"),
        )
    ).casefold()
    exempt_type_markers = (
        "equity",
        "venture",
        "investimento",
        "fundo_investimento",
        "fundo de investimento",
        "apoio_inovacao",
        "apoio inovação",
        "apoio à inovação",
        "cooperacao",
        "cooperação",
        "cooperacao_pdi",
        "cooperação pdi",
        "p&d",
        "pd&i",
        "pdi",
        "nao_reembolsavel",
        "não reembolsável",
        "nao reembolsavel",
        "grant",
        "subvenção",
        "subvencao",
        "fomento",
    )
    if any(m in tipo_blob for m in exempt_type_markers):
        return True
    fund_markers = (
        "fundo de investimento",
        "fundos de investimento",
        "fundos da série criatec",
        "fundos da serie criatec",
        "criatec",
        "venture capital",
        "capital semente",
        "fip",
        "fidc",
        "participações",
        "participacoes",
        "cotas do fidc",
        "gestor do fundo",
        "mercado de capitais",
    )
    if any(m in corpus for m in fund_markers):
        return True
    embrapii_markers = (
        "embrapii",
        "cooperação",
        "cooperacao",
        "inovação",
        "inovacao",
        "pd&i",
        "pdi",
        "centro de competência",
        "centro de competencia",
    )
    source = str(row.get("fonte_recurso") or row.get("fonte") or "").casefold()
    if "embrapii" in source and any(m in corpus for m in embrapii_markers):
        return True
    return False


def _problem_reason(name: str, row: Dict[str, Any]) -> str:
    if name == "prazo_vencido_ativo_true":
        return f"prazo_envio vencido ({row.get('prazo_envio')}) e ativo=true"
    if name in ("titulo_ruidoso", "titulo_ruidoso_ativo_true", "titulo_ruidoso_inativo"):
        term = _noise_term(row)
        base = f"título contém termo ruidoso: {term}" if term else "título parece institucional/ruidoso"
        if name == "titulo_ruidoso_ativo_true":
            return base + " (ativo=true ou ativo nulo)"
        if name == "titulo_ruidoso_inativo":
            return base + " (ativo=false; histórico)"
        return base
    if name == "credito_tipo_recurso_incoerente":
        return _credit_incoherent_reason(row)
    if name == "setor_estrategico_muito_amplo":
        return f"setor_estrategico contém {len(_as_list(row.get('setor_estrategico')))} valores; limite recomendado é 3"
    if name == "suspeito_ativo_true":
        return "validacao_status=suspeito e ativo=true"
    if name == "links_duplicados":
        return f"link duplicado no banco ({row.get('_duplicate_count', 2)} ocorrências)"
    if name == "sem_titulo":
        return "registro sem título"
    if name == "sem_link":
        return "registro sem link"
    if name in ("sem_fonte_recurso", "sem_fonte"):
        return "registro sem fonte_recurso/fonte"
    if name == "validacao_status_vazio":
        return "validacao_status vazio"
    if name == "qualidade_dado_nula":
        return "qualidade_dado nula"
    if name == "arrays_invalidos":
        return "campo esperado como array chegou com outro tipo"
    if name == "extras_nao_json":
        return "extras não retornou como objeto JSON"
    return name.replace("_", " ")


def _example(row: Dict[str, Any], problem: str = "") -> Dict[str, Any]:
    return {
        "id": row.get("id") or row.get("id_edital") or row.get("id_noticia") or row.get("id_pesquisa"),
        "fonte_recurso": row.get("fonte_recurso"),
        "fonte": row.get("fonte"),
        "titulo": str(row.get("titulo") or "")[:220],
        "link": str(row.get("link") or "")[:420],
        "tipo_oportunidade": row.get("tipo_oportunidade"),
        "tipo_recurso": row.get("tipo_recurso"),
        "validacao_status": row.get("validacao_status"),
        "qualidade_dado": row.get("qualidade_dado"),
        "prazo_envio": row.get("prazo_envio"),
        "setor_estrategico": row.get("setor_estrategico"),
        "ativo": row.get("ativo"),
        "motivo": _problem_reason(problem, row) if problem else "",
    }


def _add_problem(
    problems: Dict[str, Dict[str, Any]],
    name: str,
    rows: Iterable[Dict[str, Any]],
    *,
    severity: str,
    max_examples: int = 30,
) -> None:
    rows_l = list(rows)
    by_source = Counter(_row_source(r) for r in rows_l)
    problems[name] = {
        "severity": severity,
        "count": len(rows_l),
        "examples": [_example(r, name) for r in rows_l[:max_examples]],
        "by_source": dict(sorted(by_source.items())),
    }


def _fetch_all(sbx: Any, table: str, select: str = "*", source: str = "") -> Tuple[bool, str, List[Dict[str, Any]]]:
    out: List[Dict[str, Any]] = []
    size = 1000
    page = 0
    try:
        while True:
            q = sbx.table(table).select(select).range(page * size, page * size + size - 1)
            if source:
                if table == "edital":
                    q = q.eq("fonte_recurso", source)
                else:
                    # fonte_recurso is present in the current staging contract; fallback is handled by a retry.
                    q = q.eq("fonte_recurso", source)
            r = q.execute()
            data = getattr(r, "data", None) or []
            if not isinstance(data, list) or not data:
                break
            out.extend([x for x in data if isinstance(x, dict)])
            if len(data) < size:
                break
            page += 1
        return True, "", out
    except Exception as exc:
        if source and table in ("noticia", "pesquisa") and "fonte_recurso" in str(exc).lower():
            return _fetch_all_fonte_fallback(sbx, table, select, source)
        return False, str(exc), []


def _fetch_all_fonte_fallback(sbx: Any, table: str, select: str, source: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
    out: List[Dict[str, Any]] = []
    size = 1000
    page = 0
    try:
        while True:
            r = (
                sbx.table(table)
                .select(select)
                .eq("fonte", source)
                .range(page * size, page * size + size - 1)
                .execute()
            )
            data = getattr(r, "data", None) or []
            if not isinstance(data, list) or not data:
                break
            out.extend([x for x in data if isinstance(x, dict)])
            if len(data) < size:
                break
            page += 1
        return True, "", out
    except Exception as exc:
        return False, str(exc), []


def _dup_links(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        link = str(r.get("link") or "").strip()
        if link:
            buckets[link].append(r)
    out = []
    for link, items in buckets.items():
        if len(items) > 1:
            ex = dict(items[0])
            ex["_duplicate_count"] = len(items)
            out.append(ex)
    return out


def _expired_active(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    today = date.today()
    out = []
    for r in rows:
        if r.get("ativo") is False:
            continue
        raw = str(r.get("prazo_envio") or "")[:10]
        if not raw:
            continue
        try:
            if date.fromisoformat(raw) < today:
                out.append(r)
        except Exception:
            continue
    return out


def _noise_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        title = str(r.get("titulo") or "").strip().casefold()
        if not title:
            continue
        if any(n in title for n in NOISE_TITLES) or title in {"menu", "faq"}:
            out.append(r)
    return out


def _noise_rows_active(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ruído de título ainda relevante para dashboards (mesma regra que prazo_vencido_ativo_true: ignora só ativo=false explícito)."""
    return [r for r in _noise_rows(rows) if r.get("ativo") is not False]


def _noise_rows_inactive(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Ruído já desativado (histórico); não deve inflacionar o mesmo contador que exige ação."""
    return [r for r in _noise_rows(rows) if r.get("ativo") is False]


def _credit_incoherent(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        if _credit_validation_exempt(r):
            continue
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        blob = " ".join(
            str(x or "")
            for x in (
                r.get("titulo"),
                r.get("descricao"),
                r.get("tipo_recurso"),
                r.get("tipo_oportunidade"),
                r.get("natureza_recurso"),
                r.get("linha_credito"),
                ex.get("tipo_recurso"),
                ex.get("tipo_oportunidade"),
                ex.get("natureza_recurso"),
                ex.get("linha_credito"),
            )
        ).casefold()
        has_credit = any(x in blob for x in ("crédito", "credito", "financiamento", "linha de crédito", "linha de credito"))
        has_grant = any(x in blob for x in ("subvenção", "subvencao"))
        tipo_recurso = str(r.get("tipo_recurso") or ex.get("tipo_recurso") or "").casefold()
        tipo_oportunidade = str(r.get("tipo_oportunidade") or ex.get("tipo_oportunidade") or "").strip()
        natureza = str(r.get("natureza_recurso") or ex.get("natureza_recurso") or "").strip()
        reemb = r.get("reembolsavel")
        if has_grant and "subven" in tipo_recurso and not any(x in blob for x in ("não reembols", "nao reembols", "grant", "subvenção", "subvencao")):
            out.append(r)
        elif has_credit and _is_empty(reemb) and not natureza:
            out.append(r)
        elif has_credit and not tipo_oportunidade:
            out.append(r)
    return out


def _broad_sector(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [r for r in rows if len(_as_list(r.get("setor_estrategico"))) > 3]


def _suspect_active(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        r
        for r in rows
        if r.get("ativo") is not False and str(r.get("validacao_status") or "").strip().casefold() == "suspeito"
    ]


def _bad_arrays(rows: List[Dict[str, Any]], fields: Tuple[str, ...]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        for f in fields:
            v = r.get(f)
            if v is not None and not isinstance(v, list):
                out.append(r)
                break
    return out


def _non_json_extras(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [r for r in rows if r.get("extras") is not None and not isinstance(r.get("extras"), dict)]


def _experimental_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        src = str(r.get("fonte_recurso") or r.get("fonte") or ex.get("fonte_recurso") or "").strip()
        if src in EXPERIMENTAL_SOURCES or ex.get("experimental_source") or "experimental" in str(ex.get("source_status") or "").lower():
            out.append(r)
    return out


def _review_for_edital_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        if ex.get("review_for_edital") or str(r.get("content_type") or "").strip() == "review_for_edital":
            out.append(r)
    return out


def _noticia_tipo_pesquisa(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        if ex.get("tipo_pesquisa"):
            out.append(r)
    return out


def _bio_defense_incoherent(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    bad_terms = ("defesa", "militar", "dual-use", "dual use", "pentagon", "warfighter")
    out = []
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        if ex.get("defense_semantica") != "biologica_agro":
            continue
        blob = " ".join(str(x).casefold() for f in ("setor_estrategico", "area_tecnologica") for x in _as_list(r.get(f)))
        if any(t in blob for t in bad_terms):
            out.append(r)
    return out


def _pesquisa_missing_docs(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        docs = r.get("documentos") or ex.get("documentos")
        if _is_empty(r.get("pdf_url")) and _is_empty(r.get("url_documento")) and not isinstance(docs, list):
            out.append(r)
    return out


def _counts(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "total": len(rows),
        "ativo_true": sum(1 for r in rows if r.get("ativo") is True),
        "ativo_false": sum(1 for r in rows if r.get("ativo") is False),
        "ativo_null_or_missing": sum(1 for r in rows if r.get("ativo") is None),
    }


def _validate_edital(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    problems: Dict[str, Dict[str, Any]] = {}
    _add_problem(problems, "links_duplicados", _dup_links(rows), severity="critical")
    _add_problem(problems, "sem_titulo", [r for r in rows if _is_empty(r.get("titulo"))], severity="critical")
    _add_problem(problems, "sem_link", [r for r in rows if _is_empty(r.get("link"))], severity="critical")
    _add_problem(problems, "sem_fonte_recurso", [r for r in rows if _is_empty(r.get("fonte_recurso"))], severity="warning")
    _add_problem(problems, "validacao_status_vazio", [r for r in rows if _is_empty(r.get("validacao_status"))], severity="warning")
    _add_problem(problems, "qualidade_dado_nula", [r for r in rows if r.get("qualidade_dado") is None], severity="warning")
    _add_problem(problems, "arrays_invalidos", _bad_arrays(rows, ("area", "perfil_ideal", "setor_estrategico", "area_cientifica", "area_tecnologica", "setor_economico")), severity="warning")
    _add_problem(problems, "extras_nao_json", _non_json_extras(rows), severity="warning")
    _add_problem(problems, "prazo_vencido_ativo_true", _expired_active(rows), severity="warning")
    _add_problem(problems, "titulo_ruidoso_ativo_true", _noise_rows_active(rows), severity="warning")
    _add_problem(problems, "titulo_ruidoso_inativo", _noise_rows_inactive(rows), severity="info")
    _add_problem(problems, "credito_tipo_recurso_incoerente", _credit_incoherent(rows), severity="warning")
    _add_problem(problems, "setor_estrategico_muito_amplo", _broad_sector(rows), severity="warning")
    _add_problem(problems, "suspeito_ativo_true", _suspect_active(rows), severity="warning")
    return {"counts": _counts(rows), "problems": problems}


def _validate_noticia(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    problems: Dict[str, Dict[str, Any]] = {}
    _add_problem(problems, "links_duplicados", _dup_links(rows), severity="critical")
    _add_problem(problems, "sem_data_publicacao", [r for r in rows if _is_empty(r.get("data_publicacao"))], severity="warning")
    _add_problem(problems, "sem_resumo", [r for r in rows if _is_empty(r.get("resumo"))], severity="warning")
    _add_problem(problems, "sem_fonte", [r for r in rows if _is_empty(r.get("fonte_recurso")) and _is_empty(r.get("fonte"))], severity="warning")
    _add_problem(problems, "review_for_edital_indevido", _review_for_edital_rows(rows), severity="warning")
    _add_problem(problems, "tipo_pesquisa_incoerente", _noticia_tipo_pesquisa(rows), severity="warning")
    _add_problem(problems, "extras_nao_json", _non_json_extras(rows), severity="warning")
    _add_problem(problems, "fonte_experimental", _experimental_rows(rows), severity="warning")
    return {"counts": _counts(rows), "problems": problems}


def _validate_pesquisa(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    problems: Dict[str, Dict[str, Any]] = {}
    _add_problem(problems, "links_duplicados", _dup_links(rows), severity="critical")
    _add_problem(problems, "sem_descricao", [r for r in rows if _is_empty(r.get("descricao")) and _is_empty(r.get("resumo"))], severity="warning")
    _add_problem(problems, "sem_fonte_recurso", [r for r in rows if _is_empty(r.get("fonte_recurso")) and _is_empty(r.get("fonte"))], severity="warning")
    no_date = []
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        if _is_empty(r.get("data_publicacao")) and not ex.get("missing_date_justification"):
            no_date.append(r)
    _add_problem(problems, "sem_data_publicacao_sem_justificativa", no_date, severity="warning")
    _add_problem(problems, "setor_area_incoerente", _bio_defense_incoherent(rows), severity="warning")
    _add_problem(problems, "extras_nao_json", _non_json_extras(rows), severity="warning")
    _add_problem(problems, "sem_pdf_ou_documentos", _pesquisa_missing_docs(rows), severity="warning")
    return {"counts": _counts(rows), "problems": problems}


def _view_check(sbx: Any, view: str) -> Dict[str, Any]:
    required_any = {
        "id": ("id", "id_edital", "id_noticia", "id_pesquisa"),
        "titulo": ("titulo",),
        "fonte": ("fonte", "fonte_recurso"),
        "link": ("link",),
        "data_or_deadline": ("data_publicacao", "prazo_envio", "fim_inscricao"),
    }
    try:
        r = sbx.table(view).select("*").limit(5).execute()
        rows = getattr(r, "data", None) or []
        cols = set(rows[0].keys()) if rows and isinstance(rows[0], dict) else set()
        missing = {
            label: list(options)
            for label, options in required_any.items()
            if cols and not any(o in cols for o in options)
        }
        return {
            "ok": len(missing) == 0,
            "accessible": True,
            "sample_count": len(rows) if isinstance(rows, list) else 0,
            "columns_seen": sorted(cols),
            "missing_column_groups": missing,
            "error": "",
        }
    except Exception as exc:
        return {
            "ok": False,
            "accessible": False,
            "sample_count": 0,
            "columns_seen": [],
            "missing_column_groups": {},
            "error": str(exc),
        }


def _collect_problem_summaries(table_report: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    critical: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []
    for table, block in table_report.items():
        for name, problem in (block.get("problems") or {}).items():
            if int(problem.get("count") or 0) <= 0:
                continue
            item = {"table": table, "problem": name, "count": problem.get("count")}
            sev = problem.get("severity") or "warning"
            if sev == "critical":
                critical.append(item)
            elif sev == "warning":
                warnings.append(item)
            # severity "info" (ex.: titulo_ruidoso_inativo) fica só em tables.*.problems
    return critical, warnings


def _warnings_by_source(tables: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
    out: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0})
    for _table, block in tables.items():
        for problem_name, problem in (block.get("problems") or {}).items():
            if (problem.get("severity") or "warning") != "warning":
                continue
            for source, count in (problem.get("by_source") or {}).items():
                n = int(count or 0)
                out[source]["total"] += n
                out[source][problem_name] = out[source].get(problem_name, 0) + n
    return dict(sorted(out.items(), key=lambda kv: (-kv[1].get("total", 0), kv[0])))


def _problem_examples_flat(tables: Dict[str, Any], *, per_problem: int = 30) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for table, block in tables.items():
        for problem_name, problem in (block.get("problems") or {}).items():
            count = int(problem.get("count") or 0)
            if count <= 0:
                continue
            key = f"{table}.{problem_name}"
            out[key] = {
                "table": table,
                "problem": problem_name,
                "severity": problem.get("severity"),
                "count": count,
                "examples": (problem.get("examples") or [])[:per_problem],
                "by_source": problem.get("by_source") or {},
            }
    return out


def _warning_recommendations(warnings_by_source: Dict[str, Dict[str, int]]) -> List[str]:
    recs = [
        "Priorizar problemas com maior total por fonte; eles indicam ajuste de crawler, transformer ou regra de curadoria.",
        "Para titulo_ruidoso_ativo_true e prazo_vencido_ativo_true, revisar desativação; titulo_ruidoso_inativo (severity info) conta histórico ativo=false.",
        "Para credito_tipo_recurso_incoerente, ajustar calibração de crédito por fonte antes de novo apply.",
        "Para setor_estrategico_muito_amplo, limitar taxonomia a evidências fortes ou mover excesso para extras.",
        "Para suspeito_ativo_true, revisar se o frontend deve ocultar ou badgear esses itens até curadoria.",
    ]
    if warnings_by_source:
        top = next(iter(warnings_by_source.items()))
        recs.append(f"Fonte com maior volume de warnings: {top[0]} ({top[1].get('total', 0)} ocorrências).")
    return recs


def _escape_md(v: Any, limit: int = 140) -> str:
    s = str(v or "").replace("\n", " ").replace("\r", " ").replace("|", "\\|").strip()
    if len(s) > limit:
        return s[: limit - 3] + "..."
    return s


def _write_warning_examples(report_dir: Path, report: Dict[str, Any]) -> None:
    examples_by_problem = _problem_examples_flat(report.get("tables", {}), per_problem=30)
    payload = {
        "timestamp": report.get("timestamp"),
        "environment": report.get("environment"),
        "ok": report.get("ok"),
        "summary_by_warning": {
            k: {
                "table": v.get("table"),
                "problem": v.get("problem"),
                "severity": v.get("severity"),
                "count": v.get("count"),
                "by_source": v.get("by_source"),
            }
            for k, v in examples_by_problem.items()
        },
        "examples_by_warning": examples_by_problem,
        "warnings_by_source": report.get("warnings_by_source") or {},
        "recommendations": _warning_recommendations(report.get("warnings_by_source") or {}),
    }
    (report_dir / "post_daily_warning_examples.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = [
        "# Exemplos acionáveis de warnings",
        "",
        f"- Gerado: `{payload['timestamp']}`",
        f"- Ambiente: `{payload['environment']}`",
        "",
        "## Resumo por warning",
        "",
        "| Problema | Severidade | Count | Top fontes |",
        "|---|---:|---:|---|",
    ]
    for key, item in payload["summary_by_warning"].items():
        by_source = item.get("by_source") or {}
        top_sources = sorted(by_source.items(), key=lambda kv: (-int(kv[1] or 0), kv[0]))[:5]
        top_txt = ", ".join(f"{src}={n}" for src, n in top_sources)
        lines.append(f"| `{_escape_md(key, 80)}` | {_escape_md(item.get('severity'))} | {item.get('count')} | {_escape_md(top_txt, 220)} |")

    lines += ["", "## Exemplos por warning", ""]
    for key, item in payload["examples_by_warning"].items():
        lines += [
            f"### `{key}`",
            "",
            "| Fonte | Título | Link | Motivo |",
            "|---|---|---|---|",
        ]
        for ex in (item.get("examples") or [])[:10]:
            source = ex.get("fonte_recurso") or ex.get("fonte")
            lines.append(
                f"| {_escape_md(source, 60)} | {_escape_md(ex.get('titulo'), 120)} | "
                f"{_escape_md(ex.get('link'), 140)} | {_escape_md(ex.get('motivo'), 180)} |"
            )
        lines.append("")

    lines += ["## Resumo por fonte", "", "| Fonte | Total | Principais warnings |", "|---|---:|---|"]
    for source, vals in (payload["warnings_by_source"] or {}).items():
        parts = [(k, v) for k, v in vals.items() if k != "total"]
        parts = sorted(parts, key=lambda kv: (-int(kv[1] or 0), kv[0]))[:6]
        lines.append(f"| {_escape_md(source, 80)} | {vals.get('total', 0)} | {_escape_md(', '.join(f'{k}={v}' for k, v in parts), 260)} |")

    lines += ["", "## Recomendações", ""]
    for rec in payload["recommendations"]:
        lines.append(f"- {rec}")
    (report_dir / "post_daily_warning_examples.md").write_text("\n".join(lines), encoding="utf-8")


def _recent_apply_zero_expected(report_dir: Path) -> Optional[Dict[str, Any]]:
    p = report_dir / "last_run_summary.json"
    if not p.is_file():
        return None
    try:
        s = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None
    if s.get("modo") != "apply-staging":
        return None
    ed = s.get("edital") if isinstance(s.get("edital"), dict) else {}
    would = int(ed.get("would_upsert_total") or 0)
    changed = int(ed.get("apply_inserted") or 0) + int(ed.get("apply_updated") or 0)
    if ed.get("apply_executed") and would > 0 and changed == 0:
        return {"fase": "edital", "would_upsert_total": would, "apply_changed": changed}
    return None


def _write_reports(report_dir: Path, report: Dict[str, Any]) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "post_daily_validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    lines = [
        "# Validação global pós-daily",
        "",
        f"- Gerado: `{report['timestamp']}`",
        f"- Ambiente: `{report['environment']}`",
        f"- OK geral: **{report['ok']}**",
        f"- Critical errors: **{len(report['critical_errors'])}**",
        f"- Warnings: **{len(report['warnings'])}**",
        "",
        "## Contagens",
        "",
    ]
    for table, block in report.get("tables", {}).items():
        c = block.get("counts") or {}
        lines.append(
            f"- `{table}`: total={c.get('total', 0)}, ativo_true={c.get('ativo_true', 0)}, "
            f"ativo_false={c.get('ativo_false', 0)}"
        )
    lines += ["", "## Problemas", ""]
    for item in report["critical_errors"][:80]:
        lines.append(f"- **CRITICAL** `{item.get('table')}` / `{item.get('problem')}`: {item.get('count')}")
    for item in report["warnings"][:120]:
        lines.append(f"- WARNING `{item.get('table')}` / `{item.get('problem')}`: {item.get('count')}")

    lines += ["", "## Exemplos por warning", ""]
    lines += ["| Problema | Fonte | Título | Link | Motivo |", "|---|---|---|---|---|"]
    flat_examples = _problem_examples_flat(report.get("tables", {}), per_problem=10)
    for key, item in flat_examples.items():
        if item.get("severity") != "warning":
            continue
        for ex in (item.get("examples") or [])[:10]:
            source = ex.get("fonte_recurso") or ex.get("fonte")
            lines.append(
                f"| `{_escape_md(key, 80)}` | {_escape_md(source, 60)} | "
                f"{_escape_md(ex.get('titulo'), 110)} | {_escape_md(ex.get('link'), 130)} | "
                f"{_escape_md(ex.get('motivo'), 170)} |"
            )

    lines += ["", "## Warnings por fonte", ""]
    for source, vals in (report.get("warnings_by_source") or {}).items():
        parts = [(k, v) for k, v in vals.items() if k != "total"]
        parts = sorted(parts, key=lambda kv: (-int(kv[1] or 0), kv[0]))[:6]
        detail = ", ".join(f"{k}={v}" for k, v in parts)
        lines.append(f"- `{source}`: total={vals.get('total', 0)} ({detail})")

    lines += ["", "## Views", ""]
    for view, v in report.get("views", {}).items():
        lines.append(f"- `{view}`: ok={v.get('ok')} accessible={v.get('accessible')} sample={v.get('sample_count')}")
    lines += ["", "## Recomendações", ""]
    for rec in report.get("recommendations", []):
        lines.append(f"- {rec}")
    (report_dir / "post_daily_validation.md").write_text("\n".join(lines), encoding="utf-8")
    _write_warning_examples(report_dir, report)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validação global pós-daily em staging (somente SELECT).")
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    ap.add_argument("--sources", default="", help="CSV opcional para filtrar public.edital.")
    ap.add_argument("--include-news", action="store_true")
    ap.add_argument("--include-edital", action="store_true")
    ap.add_argument("--fail-on-critical", action="store_true")
    args = ap.parse_args()

    env_files = _load_env_files()
    if args.staging:
        os.environ.setdefault("EDITALFINDER_ENV", "staging")
    ok_guard, guard = _guard()
    report_dir = args.report_dir if args.report_dir.is_absolute() else ROOT / args.report_dir
    if not ok_guard:
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "environment": os.getenv("EDITALFINDER_ENV", ""),
            "env_files_loaded": env_files,
            "ok": False,
            "critical_errors": [{"table": "_environment", "problem": guard.get("block_reason"), "count": 1}],
            "warnings": [],
            "counts": {},
            "tables": {},
            "views": {},
            "warnings_by_source": {},
            "environment_guard": guard,
            "recommendations": ["Corrigir variáveis de ambiente de staging antes de validar."],
        }
        _write_reports(report_dir, report)
        return 1 if args.fail_on_critical else 0

    include_edital = args.include_edital or not args.include_news
    include_news = args.include_news or not args.include_edital
    sources = [x.strip().lower() for x in args.sources.split(",") if x.strip()]
    sbx = _client()

    tables: Dict[str, Any] = {}
    critical: List[Dict[str, Any]] = []
    warnings: List[Dict[str, Any]] = []

    if include_edital:
        edital_rows: List[Dict[str, Any]] = []
        if sources:
            for src in sources:
                ok, err, rows = _fetch_all(sbx, "edital", "*", src)
                if not ok:
                    critical.append({"table": "edital", "problem": "tabela_inacessivel", "source": src, "detail": err, "count": 1})
                edital_rows.extend(rows)
        else:
            ok, err, edital_rows = _fetch_all(sbx, "edital")
            if not ok:
                critical.append({"table": "edital", "problem": "tabela_inacessivel", "detail": err, "count": 1})
        tables["edital"] = _validate_edital(edital_rows)

    if include_news:
        for table, validator in (("noticia", _validate_noticia), ("pesquisa", _validate_pesquisa)):
            ok, err, rows = _fetch_all(sbx, table)
            if not ok:
                critical.append({"table": table, "problem": "tabela_inacessivel", "detail": err, "count": 1})
                rows = []
            tables[table] = validator(rows)

    c2, w2 = _collect_problem_summaries(tables)
    critical.extend(c2)
    warnings.extend(w2)

    apply_zero = _recent_apply_zero_expected(report_dir)
    if apply_zero:
        critical.append({"table": "_last_apply", "problem": "apply_recente_zero_itens_quando_esperado", "count": 1, "detail": apply_zero})

    views = {
        v: _view_check(sbx, v)
        for v in ("vw_editais_front", "vw_editais_admin", "vw_noticias_front", "vw_pesquisas_front")
    }
    for view, vr in views.items():
        if not vr.get("accessible"):
            critical.append({"table": view, "problem": "view_inacessivel", "count": 1, "detail": vr.get("error")})
        elif not vr.get("ok"):
            warnings.append({"table": view, "problem": "view_colunas_principais_ausentes", "count": 1})

    recommendations = []
    if critical:
        recommendations.append("Revisar critical_errors antes de considerar o staging saudável.")
    if warnings:
        recommendations.append("Usar warnings para priorizar limpeza, ajustes de classificação e filtros de frontend.")
    recommendations.append("Frontend deve ocultar ativo=false por padrão e expor badges para acesso limitado/fonte experimental.")

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": os.getenv("EDITALFINDER_ENV", ""),
        "env_files_loaded": env_files,
        "ok": len(critical) == 0,
        "critical_errors": critical,
        "warnings": warnings,
        "counts": {k: v.get("counts", {}) for k, v in tables.items()},
        "tables": tables,
        "views": views,
        "warnings_by_source": _warnings_by_source(tables),
        "environment_guard": guard,
        "recommendations": recommendations,
    }
    _write_reports(report_dir, report)
    print(json.dumps({"ok": report["ok"], "critical_errors": len(critical), "warnings": len(warnings), "path": str((report_dir / "post_daily_validation.json").resolve())}, ensure_ascii=False))
    return 1 if critical and args.fail_on_critical else 0


if __name__ == "__main__":
    raise SystemExit(main())
