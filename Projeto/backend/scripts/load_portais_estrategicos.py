#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loader dedicado: public.portal_estrategico (Fornecedores & Investimentos / portais estratégicos).

- Lê standardized JSON (Recovery D.1 fornecedores final ou equivalente).
- Nunca escreve em public.edital.
- Apply só staging com guardas (EDITALFINDER_ENV, EDITALFINDER_ALLOW_STAGING_APPLY, chave serviço).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from copy import deepcopy
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
_ENV_CANDIDATES = [
    ROOT / ".env.staging",
    ROOT / ".env.local",
    ROOT / ".env",
    CORE / ".env",
]
for _p in _ENV_CANDIDATES:
    if _p.is_file():
        load_dotenv(dotenv_path=_p, override=False)

if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from merge_utils import sanitize_for_postgres  # noqa: E402

DEFAULT_INPUT = ROOT / "audit_reports_main_pipeline/recovery_d1_fornecedores_final/standardized"

ALLOWED_CATEGORIAS = frozenset({"fornecedores", "investimentos"})
PORTAL_TIPO_FORNECEDORES = frozenset(
    {"registration", "hub", "access_limited", "documentation", "supplier_resource", "procurement"}
)
PORTAL_TIPO_INVESTIMENTOS = frozenset(
    {
        "investment",
        "credit_investment",
        "development_agency",
        "market_access",
        "internationalization",
        "startup_program",
        "corporate_venture",
        "accelerator",
        "funding_hub",
        "other",
    }
)
ALLOWED_PORTAL_TIPO = PORTAL_TIPO_FORNECEDORES | PORTAL_TIPO_INVESTIMENTOS
# Valores aceites pela CHECK em public.portal_estrategico (Supabase/staging).
PORTAL_TIPO_DB_ALLOWED = PORTAL_TIPO_FORNECEDORES
# Taxonomia Wave investimentos → coluna `portal_tipo` na BD (CHECK legado).
INVESTIMENTO_SEMANTIC_TO_DB: Dict[str, str] = {k: "hub" for k in PORTAL_TIPO_INVESTIMENTOS}
INVESTIMENTO_SEMANTIC_TO_DB["accelerator"] = "procurement"
INVESTIMENTO_SEMANTIC_TO_DB["corporate_venture"] = "procurement"
INVESTIMENTO_SEMANTIC_TO_DB["startup_program"] = "registration"
ALLOWED_VALIDACAO = frozenset({"incompleto", "acesso_limitado", "valido", "validado"})
ALLOWED_QUALIDADE = frozenset({"alta", "media", "baixa", "desconhecida"})


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def _mask_host(url: str) -> str:
    if not url:
        return ""
    try:
        h = (urlparse(url).hostname or "").strip()
    except Exception:
        return "***"
    if len(h) <= 6:
        return (h[0] + "***" + h[-1]) if h else ""
    return h[:3] + "***" + h[-3:]


def _environment_guard(*, apply_requested: bool, staging_flag: bool) -> Tuple[bool, Dict[str, Any]]:
    url = os.getenv("SUPABASE_URL", "").strip()
    env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
    has_url = bool(url)
    has_service_key = bool(
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    )
    has_anon_key = bool(os.getenv("SUPABASE_ANON_KEY", "").strip())
    has_allow_staging_apply = _truthy_env("EDITALFINDER_ALLOW_STAGING_APPLY")
    env_ok = env in ("staging", "local")
    env_prod = env in ("production", "prod")

    block_reason = ""
    if not apply_requested:
        block_reason = ""
        guard = {
            "editalfinder_env": env,
            "has_supabase_url": has_url,
            "has_service_key": has_service_key,
            "has_anon_key": has_anon_key,
            "has_allow_staging_apply": has_allow_staging_apply,
            "url_host_masked": _mask_host(url),
            "block_reason": block_reason,
        }
        return True, guard

    if not staging_flag:
        block_reason = "missing_staging_flag"
    elif env_prod:
        block_reason = "environment_marked_production"
    elif not env_ok:
        block_reason = "invalid_editalfinder_env"
    elif not has_url:
        block_reason = "missing_supabase_url"
    elif not has_service_key:
        block_reason = "missing_service_key"
    elif not has_allow_staging_apply:
        block_reason = "missing_allow_staging_apply"

    guard = {
        "editalfinder_env": env,
        "has_supabase_url": has_url,
        "has_service_key": has_service_key,
        "has_anon_key": has_anon_key,
        "has_allow_staging_apply": has_allow_staging_apply,
        "url_host_masked": _mask_host(url),
        "block_reason": block_reason,
    }
    return block_reason == "", guard


def _ex(item: Dict[str, Any]) -> Dict[str, Any]:
    e = item.get("extras")
    return e if isinstance(e, dict) else {}


def as_array(value: Any, *, max_n: Optional[int] = None) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        s = value.strip()
        arr = [s] if s else []
    elif isinstance(value, (list, tuple, set)):
        arr = [str(v).strip() for v in value if v is not None and str(v).strip()]
    else:
        s = str(value).strip()
        arr = [s] if s else []
    if max_n is not None and len(arr) > max_n:
        return arr[:max_n]
    return arr


def _parse_date(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, (date, datetime)):
        return val.isoformat()[:10]
    s = str(val).strip()
    if not s:
        return None
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", s)
    if m:
        return m.group(1)
    return None


def _map_qualidade_text(item: Dict[str, Any], ex: Dict[str, Any]) -> str:
    raw = item.get("qualidade_dado")
    if raw is None:
        raw = ex.get("qualidade_dado")
    if isinstance(raw, str):
        s = raw.strip().lower()
        if s in ALLOWED_QUALIDADE:
            return s
        if s in ("médio", "medio"):
            return "media"
        if s in ("alto",):
            return "alta"
        if s in ("baixo",):
            return "baixa"
    try:
        n = float(raw)  # type: ignore[arg-type]
        n = int(round(n))
    except (TypeError, ValueError):
        return "desconhecida"
    if n >= 75:
        return "alta"
    if n >= 45:
        return "media"
    if n > 0:
        return "baixa"
    return "desconhecida"


def _is_investimentos_batch(item: Dict[str, Any], ex: Dict[str, Any]) -> bool:
    fs = str(item.get("frontend_section") or ex.get("frontend_section") or "").strip().lower()
    cat = str(ex.get("categoria_portal") or item.get("categoria_portal") or "").strip().lower()
    return fs == "investimentos" or cat == "investimentos"


def _to_db_portal_tipo(semantic: str) -> str:
    """Mapeia `portal_tipo` semântico para o conjunto permitido pelo CHECK na BD."""
    s = (semantic or "").strip().lower()
    if not s:
        return "hub"
    if s in PORTAL_TIPO_DB_ALLOWED:
        return s
    if s in PORTAL_TIPO_INVESTIMENTOS:
        return INVESTIMENTO_SEMANTIC_TO_DB.get(s, "hub")
    return "hub"


def _infer_portal_tipo_investimentos(tipo_op: str, tipo_rec: str) -> str:
    t = (tipo_op or "").strip().lower()
    r = (tipo_rec or "").strip().lower()
    if "credit" in t or "credit_investment" in r:
        return "credit_investment"
    if t in ("internationalization_portal", "internacionalizacao_portal"):
        return "internationalization"
    if t in ("development_agency", "agencia_desenvolvimento"):
        return "development_agency"
    if t in ("market_access", "acesso_mercado"):
        return "market_access"
    if t in ("startup_program", "startup"):
        return "startup_program"
    if t in ("corporate_venture", "venture"):
        return "corporate_venture"
    if t in ("accelerator", "aceleradora"):
        return "accelerator"
    if t == "programa_agregado":
        return "funding_hub"
    if t in ("investment_portal", "funding_opportunity", "funding_hub"):
        return "investment" if "hub" not in t else "funding_hub"
    if "hub" in t or "hub" in r:
        return "funding_hub"
    return "investment"


def map_standardized_to_portal_estrategico(item: Dict[str, Any], *, source_key: str) -> Dict[str, Any]:
    ex = _ex(item)
    titulo = str(item.get("titulo") or item.get("title") or "").strip()
    link = str(item.get("link") or "").strip()
    fonte = str(item.get("fonte") or item.get("fonte_nome") or item.get("source") or "").strip()
    fonte_recurso = str(item.get("fonte_recurso") or item.get("source") or source_key or "").strip()

    tipo_op = str(item.get("tipo_oportunidade") or ex.get("tipo_oportunidade") or "").strip()
    tipo_rec = str(item.get("tipo_recurso") or ex.get("tipo_recurso") or "").strip()
    vs_raw = str(item.get("validacao_status") or ex.get("validacao_status") or "incompleto").strip().lower()

    inv_batch = _is_investimentos_batch(item, ex)
    categoria = str(ex.get("categoria_portal") or item.get("categoria_portal") or ("investimentos" if inv_batch else "fornecedores")).strip().lower()
    portal_tipo_semantico = str(item.get("portal_tipo") or ex.get("portal_tipo") or "").strip().lower()
    if not portal_tipo_semantico:
        if inv_batch:
            portal_tipo_semantico = _infer_portal_tipo_investimentos(tipo_op, tipo_rec)
        elif tipo_op == "programa_agregado":
            portal_tipo_semantico = "hub"
        elif vs_raw == "acesso_limitado":
            portal_tipo_semantico = "access_limited"
        elif "supplier_registration" in tipo_op.lower():
            portal_tipo_semantico = "registration"
        elif tipo_op == "documentacao_fornecedor" or tipo_rec == "recurso_fornecedor":
            portal_tipo_semantico = "supplier_resource"
        else:
            portal_tipo_semantico = "hub"
    portal_tipo_col = _to_db_portal_tipo(portal_tipo_semantico)

    resumo = str(item.get("resumo") or item.get("descricao_curta") or item.get("descricao") or "")[:8000]
    descricao = str(item.get("descricao") or item.get("resumo") or resumo or "")[:12000]

    pais = str(item.get("pais") or ex.get("pais") or "").strip() or None
    estado = str(item.get("estado") or item.get("uf") or ex.get("estado") or "").strip() or None
    regiao = str(item.get("regiao") or ex.get("regiao") or "").strip() or None

    setor_estrategico = as_array(item.get("setor_estrategico") or ex.get("setor_estrategico"), max_n=3)
    setor_economico = as_array(item.get("setor_economico") or ex.get("setor_economico"), max_n=3)
    area_tecnologica = as_array(item.get("area_tecnologica") or ex.get("area_tecnologica"), max_n=3)
    area_cientifica = as_array(item.get("area_cientifica") or ex.get("area_cientifica"), max_n=3)
    perfil_ideal = as_array(item.get("perfil_ideal") or ex.get("perfil_ideal"), max_n=3)
    publico_alvo = as_array(item.get("publico_alvo") or ex.get("publico_alvo"), max_n=3)
    tags = as_array(item.get("tags") or ex.get("tags"), max_n=20)

    data_publicacao = _parse_date(item.get("data_publicacao") or ex.get("data_publicacao_original"))
    prazo_envio = _parse_date(
        item.get("prazo_envio") or item.get("fim_inscricao") or ex.get("prazo_envio") or ex.get("fim_inscricao_original")
    )

    ativo = item.get("ativo")
    if ativo is None:
        ativo = True
    elif isinstance(ativo, str):
        ativo = ativo.strip().lower() in ("1", "true", "yes", "sim")

    validacao_status = vs_raw if vs_raw else "incompleto"
    qualidade_dado = _map_qualidade_text(item, ex)

    frontend_section = str(
        item.get("frontend_section") or ex.get("frontend_section") or ("investimentos" if inv_batch else "fornecedores")
    ).strip().lower()
    mostrar_no_radar = item.get("mostrar_no_radar")
    if mostrar_no_radar is None:
        mostrar_no_radar = ex.get("mostrar_no_radar")
    if mostrar_no_radar is None:
        mostrar_no_radar = False
    mostrar_em_fornecedores = item.get("mostrar_em_fornecedores")
    if mostrar_em_fornecedores is None:
        mostrar_em_fornecedores = ex.get("mostrar_em_fornecedores")
    if mostrar_em_fornecedores is None:
        mostrar_em_fornecedores = True
    mostrar_em_investimentos = item.get("mostrar_em_investimentos")
    if mostrar_em_investimentos is None:
        mostrar_em_investimentos = ex.get("mostrar_em_investimentos")
    if mostrar_em_investimentos is None:
        mostrar_em_investimentos = False
    mostrar_em_procurement = item.get("mostrar_em_procurement")
    if mostrar_em_procurement is None:
        mostrar_em_procurement = ex.get("mostrar_em_procurement")
    if mostrar_em_procurement is None:
        mostrar_em_procurement = False

    acesso_tipo = str(ex.get("acesso_tipo") or "").strip().lower()
    if not acesso_tipo:
        if validacao_status == "acesso_limitado" or portal_tipo_col == "access_limited":
            acesso_tipo = "acesso_limitado"
        else:
            acesso_tipo = "publico"

    acesso_obs = str(ex.get("acesso_observacao") or item.get("acesso_observacao") or "").strip() or None
    requer_login = ex.get("requer_login")
    if requer_login is None:
        requer_login = item.get("requer_login")
    if requer_login is None:
        requer_login = (
            portal_tipo_col in ("access_limited", "registration")
            or acesso_tipo == "acesso_limitado"
            or str(ex.get("portal_tipo") or "").strip().lower() == "access_limited"
        )
    elif isinstance(requer_login, str):
        requer_login = requer_login.strip().lower() in ("1", "true", "yes")

    decisao_qa = str(
        ex.get("recovery_d1_decisao_qa") or ex.get("recovery_d_fornecedores_decisao_qa") or item.get("decisao_qa") or ""
    ).strip() or None
    motivo_qa = str(ex.get("recovery_d1_motivo_qa") or item.get("motivo_qa") or "").strip() or None
    acao_rec = str(ex.get("recovery_d1_acao_recomendada") or item.get("acao_recomendada") or "").strip() or None

    id_edital = item.get("id_edital")
    try:
        id_edital_int = int(id_edital) if id_edital is not None and str(id_edital).strip().isdigit() else None
    except Exception:
        id_edital_int = None

    extras_out = deepcopy(ex)
    extras_out["loaded_to"] = "portal_estrategico"
    extras_out["source_standardized"] = True
    extras_out["loader"] = "load_portais_estrategicos"
    if inv_batch:
        extras_out["portal_tipo_wave1"] = portal_tipo_semantico
        extras_out["portal_tipo_db"] = portal_tipo_col
        extras_out["portal_tipo"] = portal_tipo_col
    if not str(extras_out.get("wave") or "").strip():
        extras_out["wave"] = "investimentos_wave1" if inv_batch else "recovery_d1_fornecedores"
    extras_out["loaded_wave"] = str(extras_out.get("wave") or ("investimentos_wave1" if inv_batch else "recovery_d1_fornecedores"))
    extras_out.setdefault("source_standardized_key", source_key)

    origem_pipeline = str(ex.get("origem_pipeline") or item.get("origem_pipeline") or "").strip()
    if not origem_pipeline:
        origem_pipeline = "investimentos_wave1" if inv_batch else "recovery_d1_fornecedores_final"
    wave_db = str(ex.get("wave") or item.get("wave") or "").strip()
    if not wave_db:
        wave_db = "investimentos_wave1" if inv_batch else "recovery_d1_fornecedores"

    row: Dict[str, Any] = {
        "id_edital": id_edital_int,
        "titulo": titulo,
        "link": link,
        "fonte": fonte or None,
        "fonte_recurso": fonte_recurso or None,
        "categoria": categoria,
        "portal_tipo": portal_tipo_col,
        "tipo_oportunidade": tipo_op or None,
        "tipo_recurso": tipo_rec or None,
        "resumo": resumo or None,
        "descricao": descricao or None,
        "pais": pais,
        "estado": estado,
        "regiao": regiao,
        "setor_estrategico": setor_estrategico,
        "setor_economico": setor_economico,
        "area_tecnologica": area_tecnologica,
        "area_cientifica": area_cientifica,
        "perfil_ideal": perfil_ideal,
        "publico_alvo": publico_alvo,
        "tags": tags,
        "data_publicacao": data_publicacao,
        "prazo_envio": prazo_envio,
        "ativo": bool(ativo),
        "validacao_status": validacao_status,
        "qualidade_dado": qualidade_dado,
        "frontend_section": frontend_section,
        "mostrar_no_radar": bool(mostrar_no_radar),
        "mostrar_em_fornecedores": bool(mostrar_em_fornecedores),
        "mostrar_em_investimentos": bool(mostrar_em_investimentos),
        "mostrar_em_procurement": bool(mostrar_em_procurement),
        "acesso_tipo": acesso_tipo,
        "acesso_observacao": acesso_obs,
        "requer_login": bool(requer_login),
        "decisao_qa": decisao_qa,
        "motivo_qa": motivo_qa,
        "acao_recomendada": acao_rec,
        "origem_pipeline": origem_pipeline,
        "wave": wave_db,
        "extras": extras_out,
        "updated_at": datetime.now().isoformat(),
    }
    return row


def _validate_portal_row(row: Dict[str, Any]) -> List[str]:
    err: List[str] = []
    if not (row.get("titulo") or "").strip():
        err.append("titulo_obrigatorio")
    link = (row.get("link") or "").strip()
    if not link.startswith("http://") and not link.startswith("https://"):
        err.append("link_http_obrigatorio")
    cat = (row.get("categoria") or "").strip().lower()
    if cat not in ALLOWED_CATEGORIAS:
        err.append(f"categoria_invalida:{cat}")
    pt = (row.get("portal_tipo") or "").strip().lower()
    if not pt or pt not in PORTAL_TIPO_DB_ALLOWED:
        err.append(f"portal_tipo_invalido_bd:{pt}")
    vs = (row.get("validacao_status") or "").strip().lower()
    if vs not in ALLOWED_VALIDACAO:
        err.append(f"validacao_status_invalido:{vs}")
    if vs == "suspeito":
        err.append("validacao_suspeito_proibido_lote")
    q = (row.get("qualidade_dado") or "").strip().lower()
    if q not in ALLOWED_QUALIDADE:
        err.append(f"qualidade_dado_invalido:{q}")
    fs = (row.get("frontend_section") or "").strip().lower()
    if not fs:
        err.append("frontend_section_obrigatorio")
    if row.get("mostrar_no_radar") is not False:
        err.append("mostrar_no_radar_deve_ser_false_lote")
    ses = row.get("setor_estrategico") or []
    if isinstance(ses, list) and len(ses) > 3:
        err.append("setor_estrategico_gt3")

    if cat == "investimentos" or fs == "investimentos":
        if fs != "investimentos":
            err.append("frontend_section_deve_ser_investimentos_lote")
        if cat != "investimentos":
            err.append("categoria_deve_ser_investimentos_lote")
        if row.get("mostrar_em_investimentos") is not True:
            err.append("mostrar_em_investimentos_deve_ser_true_lote")
        if row.get("mostrar_em_fornecedores") is not False:
            err.append("mostrar_em_fornecedores_deve_ser_false_lote_investimentos")
        exv = row.get("extras") if isinstance(row.get("extras"), dict) else {}
        w1 = str(exv.get("portal_tipo_wave1") or "").strip().lower()
        if not w1 or w1 not in PORTAL_TIPO_INVESTIMENTOS:
            err.append("extras.portal_tipo_wave1_invalido_ou_ausente")
    elif cat == "fornecedores" or fs == "fornecedores":
        if fs != "fornecedores":
            err.append("frontend_section_deve_ser_fornecedores_lote")
        if row.get("mostrar_em_fornecedores") is not True:
            err.append("mostrar_em_fornecedores_deve_ser_true_lote")
    else:
        err.append("lote_secao_desconhecido")
    return err


def _get_supabase_client():
    from supabase import create_client

    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL ou chave de serviço ausente")
    return create_client(url, key)


def _portal_exists(sb: Any, link: str) -> bool:
    r = sb.table("portal_estrategico").select("link").eq("link", link).limit(1).execute()
    data = getattr(r, "data", None) or []
    return bool(data)


def main() -> int:
    ap = argparse.ArgumentParser(description="Loader portal_estrategico (standardized → Supabase)")
    ap.add_argument("--input-dir", default=str(DEFAULT_INPUT))
    ap.add_argument("--sources", default="general_dynamics_suppliers,lockheed_martin_suppliers,bae_systems_suppliers")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--dry-run", action="store_true", help="Validar e reportar; sem escrita Supabase")
    ap.add_argument("--apply", action="store_true", help="Upsert em Supabase (exige --staging e guardas)")
    ap.add_argument("--staging", action="store_true", help="Obrigatório com --apply")
    args = ap.parse_args()

    if args.apply and args.dry_run:
        print("[ERRO] Não combine --apply com --dry-run", file=sys.stderr)
        return 2
    dry_run = not bool(args.apply)
    if args.apply and not args.staging:
        print("[ERRO] --apply exige --staging", file=sys.stderr)
        return 2

    input_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    selected: Set[str] = {x.strip().lower() for x in str(args.sources).split(",") if x.strip()}
    all_items: List[Tuple[str, Dict[str, Any]]] = []
    for key in sorted(selected):
        path = input_dir / f"{key}_standardized.json"
        if not path.is_file():
            print(f"[AVISO] Ficheiro ausente: {path}", file=sys.stderr)
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            continue
        for it in raw:
            if isinstance(it, dict):
                all_items.append((key, it))

    prepared: List[Dict[str, Any]] = []
    validation_errors: List[Dict[str, Any]] = []
    map_errors: List[Dict[str, Any]] = []
    apply_errors: List[Dict[str, Any]] = []
    by_source: Dict[str, Dict[str, int]] = {}

    for sk in sorted(selected):
        by_source.setdefault(sk, {"would_upsert": 0, "errors": 0})

    for src_key, it in all_items:
        try:
            row = map_standardized_to_portal_estrategico(it, source_key=src_key)
            row = sanitize_for_postgres(row)  # type: ignore[assignment]
            miss = _validate_portal_row(row)
            if miss:
                validation_errors.append(
                    {"fonte": src_key, "link": row.get("link"), "titulo": row.get("titulo"), "erros": miss}
                )
                by_source[src_key]["errors"] += 1
                continue
            prepared.append(row)
            by_source[src_key]["would_upsert"] += 1
        except Exception as exc:
            map_errors.append({"fonte": src_key, "link": it.get("link"), "erro": str(exc)})
            by_source[src_key]["errors"] += 1

    env_safe, env_guard = _environment_guard(apply_requested=bool(args.apply), staging_flag=bool(args.staging))

    portal_tipo_c = Counter(str(r.get("portal_tipo") or "") for r in prepared)
    vs_c = Counter(str(r.get("validacao_status") or "") for r in prepared)
    fs_c = Counter(str(r.get("frontend_section") or "") for r in prepared)
    mradar_true = sum(1 for r in prepared if r.get("mostrar_no_radar") is True)
    mforn_true = sum(1 for r in prepared if r.get("mostrar_em_fornecedores") is True)
    minvest_true = sum(1 for r in prepared if r.get("mostrar_em_investimentos") is True)

    inserted = updated = 0
    apply_status = "dry_run_only"
    apply_block = ""

    if args.apply:
        if not env_safe:
            apply_status = "blocked"
            apply_block = env_guard.get("block_reason") or "unknown"
            apply_errors.append({"table": "_guard", "erro": "apply_bloqueado", "detalhe": apply_block})
        else:
            try:
                sb = _get_supabase_client()
                for row in prepared:
                    lk = str(row.get("link") or "")
                    existed = _portal_exists(sb, lk)
                    sb.table("portal_estrategico").upsert(row, on_conflict="link").execute()
                    if existed:
                        updated += 1
                    else:
                        inserted += 1
                apply_status = "applied"
            except Exception as exc:
                apply_status = "error"
                apply_block = str(exc)
                apply_errors.append({"table": "_apply", "erro": str(exc)})

    errors_out = validation_errors + map_errors + apply_errors
    errors_count = len(validation_errors)
    map_errors_count = len(map_errors)
    skipped = len(all_items) - len(prepared) - errors_count - map_errors_count

    summary: Dict[str, Any] = {
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run" if dry_run else "apply",
        "staging_flag": bool(args.staging),
        "apply_requested": bool(args.apply),
        "input_dir": str(input_dir.resolve()),
        "output_dir": str(out_dir.resolve()),
        "sources_selected": sorted(selected),
        "total_items": len(all_items),
        "would_upsert_total": len(prepared),
        "inserted": inserted,
        "updated": updated,
        "upserted_total": (inserted + updated) if (args.apply and apply_status == "applied") else 0,
        "skipped": skipped,
        "errors_count": errors_count,
        "map_errors_count": map_errors_count,
        "apply_errors_count": len(apply_errors),
        "errors_total_written": len(errors_out),
        "by_source": by_source,
        "portal_tipo_counts": dict(portal_tipo_c),
        "validacao_status_counts": dict(vs_c),
        "frontend_section_counts": dict(fs_c),
        "mostrar_no_radar_true_count": mradar_true,
        "mostrar_em_fornecedores_true_count": mforn_true,
        "mostrar_em_investimentos_true_count": minvest_true,
        "environment_guard": env_guard,
        "apply_status": apply_status,
        "apply_block_reason": apply_block,
    }

    if dry_run:
        summary["apply_status"] = "dry_run_only"
        summary["nota"] = "Nenhuma escrita no Supabase."

    (out_dir / "load_portais_estrategicos_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "load_portais_estrategicos_by_source.json").write_text(
        json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "load_portais_estrategicos_errors.json").write_text(
        json.dumps(errors_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    examples = [{"link": r.get("link"), "titulo": r.get("titulo"), "portal_tipo": r.get("portal_tipo")} for r in prepared[:8]]
    (out_dir / "load_portais_estrategicos_payload_examples.json").write_text(
        json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Load portais estratégicos",
        "",
        f"- Execução: `{summary['data_execucao']}`",
        f"- Modo: **{summary['modo']}**",
        f"- `total_items`: **{summary['total_items']}**",
        f"- `would_upsert_total`: **{summary['would_upsert_total']}**",
        f"- `errors_count` (validação): **{summary['errors_count']}**",
        f"- `map_errors_count`: **{summary['map_errors_count']}**",
        f"- `mostrar_no_radar_true_count`: **{summary['mostrar_no_radar_true_count']}**",
        f"- `mostrar_em_fornecedores_true_count`: **{summary['mostrar_em_fornecedores_true_count']}**",
        f"- `mostrar_em_investimentos_true_count`: **{summary.get('mostrar_em_investimentos_true_count', 0)}**",
        f"- `apply_status`: **{summary['apply_status']}**",
        "",
        "## environment_guard",
        "",
        "```json",
        json.dumps(env_guard, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    (out_dir / "load_portais_estrategicos_summary.md").write_text("\n".join(md), encoding="utf-8")

    print(out_dir.resolve())
    if summary["errors_count"] > 0 or summary["map_errors_count"] > 0:
        return 1
    if args.apply and apply_status not in ("applied",):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
