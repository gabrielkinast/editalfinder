#!/usr/bin/env python3
"""
Loader dedicado notícia/pesquisa (Onda 1 NASA e extensões futuras).

Não usa fluxo de edital. Apply só com guardas de staging explícitas.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"

# Mesma ordem e regra que CORE/db.py (override=False: não sobrescreve env já exportado)
_ENV_CANDIDATES = [
    ROOT / ".env.staging",
    ROOT / ".env.local",
    ROOT / ".env",
    CORE / ".env",
]
for _env_path in _ENV_CANDIDATES:
    if _env_path.is_file():
        load_dotenv(dotenv_path=_env_path, override=False)

if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from merge_utils import sanitize_for_postgres  # noqa: E402

DEFAULT_INPUT_DIR = ROOT / "audit_reports_news_research_loader"

SOURCE_FILES = {
    "nasa_news": {
        "noticia": "nasa_wave1_payload_noticia.json",
        "pesquisa": "nasa_wave1_payload_pesquisa.json",
        "review": "nasa_wave1_review_candidates.json",
    },
    "darpa_news": {
        "noticia": "darpa_news_wave1_payload_noticia.json",
        "pesquisa": "darpa_news_wave1_payload_pesquisa.json",
        "review": "darpa_news_wave1_review_candidates.json",
    },
    "iaea_news_publications": {
        "noticia": "iaea_wave1_payload_noticia.json",
        "pesquisa": "iaea_wave1_payload_pesquisa.json",
        "review": "iaea_wave1_review_candidates.json",
    },
    "eurekalert_science_filtered": {
        "noticia": "eurekalert_wave1_payload_noticia.json",
        "pesquisa": "eurekalert_wave1_payload_pesquisa.json",
        "review": "eurekalert_wave1_review_candidates.json",
    },
    "exercito_brasileiro": {
        "noticia": "exercito_brasileiro_subset_valido_payload_noticia.json",
        "pesquisa": "exercito_brasileiro_subset_valido_payload_pesquisa.json",
        "review": "exercito_brasileiro_subset_valido_review_candidates.json",
    },
    "softex_noticias": {
        "noticia": "softex_noticias_payload_noticia.json",
        "pesquisa": "softex_noticias_payload_pesquisa.json",
        "review": "softex_noticias_review_candidates.json",
    },
    "capes_noticias": {
        "noticia": "capes_noticias_payload_noticia.json",
        "pesquisa": "capes_noticias_payload_pesquisa.json",
        "review": "capes_noticias_review_candidates.json",
    },
    "f35_news": {
        "noticia": "standardized/f35_news_standardized.json",
        "pesquisa": "f35_news_payload_pesquisa.json",
        "review": "f35_news_review_candidates.json",
    },
    "lockheed_martin_news": {
        "noticia": "standardized/lockheed_martin_news_standardized.json",
        "pesquisa": "lockheed_martin_news_payload_pesquisa.json",
        "review": "lockheed_martin_news_review_candidates.json",
    },
    "mcti_noticias": {
        "noticia": "standardized/mcti_noticias_standardized.json",
        "pesquisa": "mcti_noticias_payload_pesquisa.json",
        "review": "mcti_noticias_review_candidates.json",
    },
    "war_gov_news": {
        "noticia": "standardized/war_gov_news_standardized.json",
        "pesquisa": "war_gov_news_payload_pesquisa.json",
        "review": "war_gov_news_review_candidates.json",
    },
    "nato_news": {
        "noticia": "standardized/nato_news_standardized.json",
        "pesquisa": "nato_news_payload_pesquisa.json",
        "review": "nato_news_review_candidates.json",
    },
    "afrl_news": {
        "noticia": "standardized/afrl_news_standardized.json",
        "pesquisa": "afrl_news_payload_pesquisa.json",
        "review": "afrl_news_review_candidates.json",
    },
    "darpa_programs_research": {
        "noticia": "darpa_programs_payload_noticia.json",
        "pesquisa": "standardized/darpa_programs_research_standardized.json",
        "review": "darpa_programs_review_candidates.json",
    },
    "afrl_technology_areas": {
        "noticia": "afrl_technology_areas_payload_noticia.json",
        "pesquisa": "standardized/afrl_technology_areas_standardized.json",
        "review": "afrl_technology_areas_review_candidates.json",
    },
    "arl_news": {
        "noticia": "standardized/arl_news_standardized.json",
        "pesquisa": "arl_news_payload_pesquisa.json",
        "review": "arl_news_review_candidates.json",
    },
    "arl_resources": {
        "noticia": "arl_resources_payload_noticia.json",
        "pesquisa": "standardized/arl_resources_standardized.json",
        "review": "arl_resources_review_candidates.json",
    },
    "space_force_news": {
        "noticia": "standardized/space_force_news_standardized.json",
        "pesquisa": "space_force_news_payload_pesquisa.json",
        "review": "space_force_news_review_candidates.json",
    },
}

# Presets de ficheiros por onda (payloads gerados localmente, ex.: build_nasa_wave2_payloads.py)
WAVE_FILE_PRESETS: Dict[str, Dict[str, str]] = {
    "nasa_wave2": {
        "noticia": "nasa_wave2_payload_noticia.json",
        "pesquisa": "nasa_wave2_payload_pesquisa.json",
        "review": "nasa_wave2_review_candidates.json",
    },
    "darpa_news_wave1": {
        "noticia": "darpa_news_wave1_payload_noticia.json",
        "pesquisa": "darpa_news_wave1_payload_pesquisa.json",
        "review": "darpa_news_wave1_review_candidates.json",
    },
    "iaea_wave1": {
        "noticia": "iaea_wave1_payload_noticia.json",
        "pesquisa": "iaea_wave1_payload_pesquisa.json",
        "review": "iaea_wave1_review_candidates.json",
    },
    "eurekalert_wave1": {
        "noticia": "eurekalert_wave1_payload_noticia.json",
        "pesquisa": "eurekalert_wave1_payload_pesquisa.json",
        "review": "eurekalert_wave1_review_candidates.json",
    },
    "exercito_brasileiro_subset_valido": {
        "noticia": "exercito_brasileiro_subset_valido_payload_noticia.json",
        "pesquisa": "exercito_brasileiro_subset_valido_payload_pesquisa.json",
        "review": "exercito_brasileiro_subset_valido_review_candidates.json",
    },
    "softex_noticias_dryrun": {
        "noticia": "softex_noticias_payload_noticia.json",
        "pesquisa": "softex_noticias_payload_pesquisa.json",
        "review": "softex_noticias_review_candidates.json",
    },
    "capes_noticias_subset_recente": {
        "noticia": "capes_noticias_payload_noticia.json",
        "pesquisa": "capes_noticias_payload_pesquisa.json",
        "review": "capes_noticias_review_candidates.json",
    },
    "f35_news_subset_top20": {
        "noticia": "standardized/f35_news_standardized.json",
        "pesquisa": "f35_news_payload_pesquisa.json",
        "review": "f35_news_review_candidates.json",
    },
    "lockheed_martin_news": {
        "noticia": "standardized/lockheed_martin_news_standardized.json",
        "pesquisa": "lockheed_martin_news_payload_pesquisa.json",
        "review": "lockheed_martin_news_review_candidates.json",
    },
    "lockheed_martin_news_subset_top20": {
        "noticia": "standardized/lockheed_martin_news_standardized.json",
        "pesquisa": "lockheed_martin_news_payload_pesquisa.json",
        "review": "lockheed_martin_news_review_candidates.json",
    },
    "war_gov_news_subset_top20": {
        "noticia": "standardized/war_gov_news_standardized.json",
        "pesquisa": "war_gov_news_payload_pesquisa.json",
        "review": "war_gov_news_review_candidates.json",
    },
    "nato_news_subset_top20": {
        "noticia": "standardized/nato_news_standardized.json",
        "pesquisa": "nato_news_payload_pesquisa.json",
        "review": "nato_news_review_candidates.json",
    },
    "afrl_news_subset_valido": {
        "noticia": "standardized/afrl_news_standardized.json",
        "pesquisa": "afrl_news_payload_pesquisa.json",
        "review": "afrl_news_review_candidates.json",
    },
    "afrl_technology_areas": {
        "noticia": "afrl_technology_areas_payload_noticia.json",
        "pesquisa": "standardized/afrl_technology_areas_standardized.json",
        "review": "afrl_technology_areas_review_candidates.json",
    },
    "arl_news": {
        "noticia": "standardized/arl_news_standardized.json",
        "pesquisa": "arl_news_payload_pesquisa.json",
        "review": "arl_news_review_candidates.json",
    },
    "arl_resources": {
        "noticia": "arl_resources_payload_noticia.json",
        "pesquisa": "standardized/arl_resources_standardized.json",
        "review": "arl_resources_review_candidates.json",
    },
    "space_force_news": {
        "noticia": "standardized/space_force_news_standardized.json",
        "pesquisa": "space_force_news_payload_pesquisa.json",
        "review": "space_force_news_review_candidates.json",
    },
    "darpa_programs_research_subset_valido": {
        "noticia": "darpa_programs_payload_noticia.json",
        "pesquisa": "standardized/darpa_programs_research_standardized.json",
        "review": "darpa_programs_review_candidates.json",
    },
    "darpa_programs_research_subset_valido_v2": {
        "noticia": "darpa_programs_payload_noticia.json",
        "pesquisa": "standardized/darpa_programs_research_standardized.json",
        "review": "darpa_programs_review_candidates.json",
    },
    "afrl_technology_areas_subset_valido": {
        "noticia": "afrl_technology_areas_payload_noticia.json",
        "pesquisa": "standardized/afrl_technology_areas_standardized.json",
        "review": "afrl_technology_areas_review_candidates.json",
    },
    "arl_news_subset_valido": {
        "noticia": "standardized/arl_news_standardized.json",
        "pesquisa": "arl_news_payload_pesquisa.json",
        "review": "arl_news_review_candidates.json",
    },
    "arl_resources_subset_valido": {
        "noticia": "arl_resources_payload_noticia.json",
        "pesquisa": "standardized/arl_resources_standardized.json",
        "review": "arl_resources_review_candidates.json",
    },
    "space_force_news_subset_valido": {
        "noticia": "standardized/space_force_news_standardized.json",
        "pesquisa": "space_force_news_payload_pesquisa.json",
        "review": "space_force_news_review_candidates.json",
    },
}


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def _mask_host(url: str) -> str:
    if not url:
        return ""
    try:
        h = (urlparse(url).hostname or "") or ""
        if len(h) <= 6:
            return h[:1] + "***" + h[-1:] if h else ""
        return h[:3] + "***" + h[-3:]
    except Exception:
        return "***"


def _confirm_staging_allowed(has_staging_flag: bool) -> Tuple[bool, Dict[str, Any]]:
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
    if not has_staging_flag:
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

    safe = block_reason == ""
    guard = {
        "editalfinder_env": env,
        "has_supabase_url": has_url,
        "has_service_key": has_service_key,
        "has_anon_key": has_anon_key,
        "has_allow_staging_apply": has_allow_staging_apply,
        "url_host_masked": _mask_host(url),
        "block_reason": block_reason,
    }
    return safe, guard


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_payload_path(input_dir: Path, default_relative: str, override: str) -> Path:
    """Caminho absoluto, relativo ao repo (ROOT) ou a input_dir."""
    o = (override or "").strip()
    if o:
        p = Path(o)
        if p.is_absolute():
            return p
        from_root = ROOT / p
        if from_root.is_file():
            return from_root
        from_input = input_dir / p
        if from_input.is_file():
            return from_input
        return from_root
    return input_dir / default_relative


def _normalize_str_array(value: Any) -> Optional[List[str]]:
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        return [s] if s else None
    if isinstance(value, (list, tuple, set)):
        out = [str(v).strip() for v in value if v is not None and str(v).strip()]
        return out or None
    s = str(value).strip()
    return [s] if s else None


def _normalize_documentos(value: Any) -> List[Dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    out: List[Dict[str, Any]] = []
    for d in value:
        if isinstance(d, dict):
            out.append(d)
    return out


def _validate_noticia_payload(row: Dict[str, Any]) -> List[str]:
    miss: List[str] = []
    for k in ("titulo", "resumo", "link", "data_publicacao", "tipo_conteudo", "validacao_status"):
        if row.get(k) in (None, "", [], {}):
            miss.append(k)
    if row.get("qualidade_dado") is None:
        miss.append("qualidade_dado")
    if not (row.get("fonte") or row.get("fonte_recurso")):
        miss.append("fonte_ou_fonte_recurso")
    return miss


def _validate_pesquisa_payload(row: Dict[str, Any]) -> List[str]:
    miss: List[str] = []
    ex = row.get("extras") if isinstance(row.get("extras"), dict) else {}
    fr = str(row.get("fonte_recurso") or "").strip()
    catalog_sem_data = bool(
        ex.get("catalogo_institucional")
        or ex.get("pesquisa_sem_data_catalogo")
        or (
            str(row.get("tipo_pesquisa") or "") in ("area_tecnologica", "portal_institucional")
            and fr
            in (
                "afrl_technology_areas",
                "arl_resources",
                "afnwc_innovation",
                "afnwc_weapon_systems",
            )
        )
    )
    required = ["titulo", "descricao", "link", "tipo_pesquisa", "validacao_status"]
    if not catalog_sem_data:
        required.append("data_publicacao")
    for k in required:
        if row.get(k) in (None, "", [], {}):
            miss.append(k)
    if row.get("qualidade_dado") is None:
        miss.append("qualidade_dado")
    if not row.get("fonte_recurso"):
        miss.append("fonte_recurso")
    return miss


def _norm_attr(p: Dict[str, Any], attr: str, arrays_normalized: List[str], prefix: str) -> Optional[List[str]]:
    raw = p.get(attr)
    norm = _normalize_str_array(raw)
    if raw is not None and norm != raw:
        arrays_normalized.append(f"{prefix}:{p.get('link')}:{attr}")
    return norm


def _row_noticia_from_payload(p: Dict[str, Any], arrays_normalized: List[str]) -> Dict[str, Any]:
    ex = dict(p.get("extras") or {})
    ac = _norm_attr(p, "area_cientifica", arrays_normalized, "noticia")
    at = _norm_attr(p, "area_tecnologica", arrays_normalized, "noticia")
    se = _norm_attr(p, "setor_estrategico", arrays_normalized, "noticia")
    tg = _norm_attr(p, "tags", arrays_normalized, "noticia")
    tipo = str(p.get("tipo_conteudo") or "noticia").strip() or "noticia"
    ct = tipo if tipo in ("noticia", "pesquisa") else "noticia"
    return sanitize_for_postgres(
        {
            "titulo": p.get("titulo"),
            "resumo": p.get("resumo"),
            "link": str(p.get("link") or "").strip(),
            "fonte": p.get("fonte"),
            "fonte_recurso": p.get("fonte_recurso") or p.get("fonte"),
            "data_publicacao": p.get("data_publicacao"),
            "pais": p.get("pais"),
            "regiao": p.get("regiao"),
            "idioma": p.get("idioma_original"),
            "idioma_original": p.get("idioma_original"),
            "origem_portal": ex.get("origem_portal") or p.get("fonte"),
            "tipo_conteudo": tipo,
            "content_type": ct,
            "area_cientifica": ac,
            "area_tecnologica": at,
            "setor_estrategico": se,
            "tags": tg,
            "qualidade_dado": p.get("qualidade_dado"),
            "validacao_status": p.get("validacao_status"),
            "extras": ex,
            "ultima_coleta": datetime.now(timezone.utc).isoformat(),
        }
    )


def _is_darpa_news_misroute(fonte_recurso: str) -> bool:
    fr = fonte_recurso.strip().lower()
    return fr in ("darpa news", "darpa_news")


def _row_allowed_for_noticia(row: Dict[str, Any], source_id: str) -> Tuple[bool, str]:
    fr = str(row.get("fonte_recurso") or "").strip()
    if source_id == "darpa_programs_research" or fr == "darpa_programs_research":
        return False, "darpa_programs_somente_pesquisa"
    if source_id == "darpa_opportunities_research":
        return False, "darpa_opportunities_review_only"
    if _is_darpa_news_misroute(fr) and source_id != "darpa_news":
        return False, "darpa_news_nao_em_noticia_de_outra_fonte"
    return True, ""


def _row_allowed_for_pesquisa(row: Dict[str, Any], source_id: str) -> Tuple[bool, str]:
    fr = str(row.get("fonte_recurso") or "").strip()
    if source_id == "darpa_news":
        return False, "darpa_news_somente_noticia"
    if source_id == "darpa_opportunities_research":
        return False, "darpa_opportunities_review_only"
    if _is_darpa_news_misroute(fr):
        return False, "darpa_news_nunca_em_pesquisa"
    if source_id == "darpa_programs_research":
        if fr and fr != "darpa_programs_research":
            return False, f"fonte_recurso_inesperada:{fr}"
        tc = str(row.get("tipo_conteudo") or "").strip().lower()
        tp = str(row.get("tipo_pesquisa") or "").strip()
        if tc and tc != "pesquisa":
            return False, "tipo_conteudo_nao_pesquisa"
        if tp and tp != "programa_pesquisa":
            return False, "tipo_pesquisa_nao_programa"
    return True, ""


def _pesquisa_type_fields(p: Dict[str, Any], source_id: str) -> Dict[str, Optional[str]]:
    ex = p.get("extras") if isinstance(p.get("extras"), dict) else {}
    fr = str(p.get("fonte_recurso") or source_id or "").strip()
    tipo_pesquisa = str(p.get("tipo_pesquisa") or ex.get("tipo_pesquisa") or "").strip() or None
    tipo_recurso = str(p.get("tipo_recurso") or ex.get("tipo_recurso") or "").strip() or None
    tipo_oportunidade = str(p.get("tipo_oportunidade") or ex.get("tipo_oportunidade") or "").strip() or None
    if fr == "darpa_programs_research" or source_id == "darpa_programs_research":
        tipo_pesquisa = tipo_pesquisa or "programa_pesquisa"
        tipo_recurso = tipo_recurso or "programa_estrategico"
        tipo_oportunidade = tipo_oportunidade or "pesquisa_estrategica"
    if fr == "afrl_technology_areas" or source_id == "afrl_technology_areas":
        tipo_pesquisa = tipo_pesquisa or "area_tecnologica"
        tipo_recurso = tipo_recurso or "area_tecnologica"
        tipo_oportunidade = tipo_oportunidade or "pesquisa_estrategica"
    if fr == "arl_resources" or source_id == "arl_resources":
        tipo_oportunidade = tipo_oportunidade or "pesquisa_estrategica"
    return {
        "tipo_pesquisa": tipo_pesquisa,
        "tipo_recurso": tipo_recurso,
        "tipo_oportunidade": tipo_oportunidade,
    }


def _row_pesquisa_from_payload(
    p: Dict[str, Any], arrays_normalized: List[str], source_id: str = ""
) -> Dict[str, Any]:
    ex = dict(p.get("extras") or {})
    raw_docs = p.get("documentos")
    docs = _normalize_documentos(raw_docs)
    if raw_docs is not None and docs != raw_docs:
        arrays_normalized.append(f"pesquisa:{p.get('link')}:documentos")
    ac = _norm_attr(p, "area_cientifica", arrays_normalized, "pesquisa")
    at = _norm_attr(p, "area_tecnologica", arrays_normalized, "pesquisa")
    se = _norm_attr(p, "setor_estrategico", arrays_normalized, "pesquisa")
    tg = _norm_attr(p, "tags", arrays_normalized, "pesquisa")
    types = _pesquisa_type_fields(p, source_id)
    ex = {
        **ex,
        "tipo_pesquisa": types["tipo_pesquisa"],
        "tipo_recurso": types["tipo_recurso"],
        "tipo_oportunidade": types["tipo_oportunidade"],
        "documentos": docs,
    }
    display_fonte = str(p.get("fonte") or "").strip() or "DARPA"
    fonte_recurso = str(p.get("fonte_recurso") or source_id or "").strip()
    return sanitize_for_postgres(
        {
            "titulo": p.get("titulo"),
            "descricao": p.get("descricao"),
            "resumo": (p.get("descricao") or "")[:1200] if p.get("descricao") else None,
            "link": str(p.get("link") or "").strip(),
            "fonte": display_fonte,
            "fonte_recurso": fonte_recurso,
            "data_publicacao": p.get("data_publicacao"),
            "pais": p.get("pais"),
            "regiao": p.get("regiao"),
            "idioma": p.get("idioma_original"),
            "idioma_original": p.get("idioma_original"),
            "origem_portal": ex.get("origem_portal") or display_fonte,
            "area_cientifica": ac,
            "area_tecnologica": at,
            "setor_estrategico": se,
            "tags": tg,
            "tipo_oportunidade": types["tipo_oportunidade"],
            "tipo_recurso": types["tipo_recurso"],
            "content_type": "pesquisa",
            "url_documento": p.get("pdf_url"),
            "qualidade_dado": p.get("qualidade_dado"),
            "validacao_status": p.get("validacao_status"),
            "extras": ex,
            "ultima_coleta": datetime.now(timezone.utc).isoformat(),
        }
    )


def _get_supabase():
    import importlib

    # db.py valida URL/chave ao importar
    return importlib.import_module("db")


def _test_tables_news(sbx: Any) -> Tuple[bool, str]:
    try:
        sbx.table("noticia").select("link").limit(1).execute()
        sbx.table("pesquisa").select("link").limit(1).execute()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def _exists_link(sbx: Any, table: str, link: str) -> bool:
    try:
        r = sbx.table(table).select("link").eq("link", link).limit(1).execute()
        return bool(r.data)
    except Exception:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Loader notícia/pesquisa (staging seguro).")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--source", default="nasa_news", help="Fonte lógica (ex.: nasa_news).")
    ap.add_argument(
        "--wave",
        default="",
        help="Preset de ficheiros de payload, ex.: nasa_wave2, darpa_news_wave1, iaea_wave1 (sobrescreve nomes em input-dir).",
    )
    ap.add_argument("--noticia-payload", default="", help="Caminho alternativo ao JSON de notícias.")
    ap.add_argument("--pesquisa-payload", default="", help="Caminho alternativo ao JSON de pesquisa.")
    ap.add_argument("--review-payload", default="", help="Caminho alternativo ao JSON de review_for_edital (só auditoria).")
    ap.add_argument("--input-dir", default=str(DEFAULT_INPUT_DIR))
    ap.add_argument("--test-db-before-apply", action="store_true")
    args = ap.parse_args()

    if args.apply and args.dry_run:
        print("Use apenas um de --apply ou --dry-run.", file=sys.stderr)
        return 2
    if not args.apply and not args.dry_run:
        print("Especifique --dry-run ou --apply.", file=sys.stderr)
        return 2

    src = str(args.source or "").strip()
    if src not in SOURCE_FILES:
        print(f"Fonte não suportada: {src!r}. Opções: {list(SOURCE_FILES)}", file=sys.stderr)
        return 2

    wave = str(args.wave or "").strip()
    if wave and wave not in WAVE_FILE_PRESETS:
        print(f"--wave desconhecido: {wave!r}. Opções: {list(WAVE_FILE_PRESETS)}", file=sys.stderr)
        return 2

    in_dir = Path(args.input_dir)
    out_dir = in_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if wave:
        files = dict(WAVE_FILE_PRESETS[wave])
    else:
        files = dict(SOURCE_FILES[src])

    path_noticia = _resolve_payload_path(in_dir, files["noticia"], str(args.noticia_payload or ""))
    path_pesquisa = _resolve_payload_path(in_dir, files["pesquisa"], str(args.pesquisa_payload or ""))
    path_review = _resolve_payload_path(in_dir, files["review"], str(args.review_payload or ""))

    raw_n = _load_json(path_noticia, [])
    raw_p = _load_json(path_pesquisa, [])
    raw_rev = _load_json(path_review, [])
    if not isinstance(raw_n, list):
        raw_n = []
    if not isinstance(raw_p, list):
        raw_p = []
    if not isinstance(raw_rev, list):
        raw_rev = []

    errors: List[Dict[str, Any]] = []
    skipped = 0
    arrays_normalized: List[str] = []
    examples: List[Dict[str, Any]] = []

    routing_skipped: List[Dict[str, Any]] = []

    prepared_n: List[Dict[str, Any]] = []
    for i, row in enumerate(raw_n):
        if not isinstance(row, dict):
            skipped += 1
            continue
        ok_route, why_route = _row_allowed_for_noticia(row, src)
        if not ok_route:
            routing_skipped.append({"table": "noticia", "index": i, "link": row.get("link"), "motivo": why_route})
            skipped += 1
            continue
        miss = _validate_noticia_payload(row)
        if miss:
            errors.append({"table": "noticia", "index": i, "link": row.get("link"), "erro": "validacao", "missing": miss})
            skipped += 1
            continue
        an: List[str] = []
        prepared_n.append(_row_noticia_from_payload(row, an))
        arrays_normalized.extend(an)
        if len(examples) < 6:
            examples.append({"table": "noticia", "link": prepared_n[-1].get("link"), "titulo": prepared_n[-1].get("titulo")})

    prepared_p: List[Dict[str, Any]] = []
    for i, row in enumerate(raw_p):
        if not isinstance(row, dict):
            skipped += 1
            continue
        ok_route, why_route = _row_allowed_for_pesquisa(row, src)
        if not ok_route:
            routing_skipped.append({"table": "pesquisa", "index": i, "link": row.get("link"), "motivo": why_route})
            skipped += 1
            continue
        miss = _validate_pesquisa_payload(row)
        if miss:
            errors.append({"table": "pesquisa", "index": i, "link": row.get("link"), "erro": "validacao", "missing": miss})
            skipped += 1
            continue
        an: List[str] = []
        prepared_p.append(_row_pesquisa_from_payload(row, an, source_id=src))
        arrays_normalized.extend(an)
        if len(examples) < 10:
            examples.append({"table": "pesquisa", "link": prepared_p[-1].get("link"), "titulo": prepared_p[-1].get("titulo")})

    review_ignored = len(raw_rev)

    def _count_pesquisa_field(key: str) -> int:
        n = 0
        for r in prepared_p:
            if r.get(key):
                n += 1
                continue
            ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
            if ex.get(key):
                n += 1
        return n

    pesquisa_n = len(prepared_p)
    tipo_pesquisa_filled = _count_pesquisa_field("tipo_pesquisa")
    tipo_recurso_filled = sum(1 for r in prepared_p if r.get("tipo_recurso"))
    tipo_oportunidade_filled = sum(1 for r in prepared_p if r.get("tipo_oportunidade"))

    env_safe, env_guard = _confirm_staging_allowed(bool(args.staging))

    summary: Dict[str, Any] = {
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run" if args.dry_run else "apply",
        "source": src,
        "wave": wave or None,
        "payload_noticia_path": str(path_noticia.resolve()) if path_noticia.is_file() else str(path_noticia),
        "payload_pesquisa_path": str(path_pesquisa.resolve()) if path_pesquisa.is_file() else str(path_pesquisa),
        "payload_review_path": str(path_review.resolve()) if path_review.is_file() else str(path_review),
        "input_dir": str(in_dir.resolve()),
        "total_noticia": len(raw_n),
        "total_pesquisa": len(raw_p),
        "would_upsert_noticia": len(prepared_n),
        "would_upsert_pesquisa": len(prepared_p),
        "inserted_noticia": 0,
        "updated_noticia": 0,
        "inserted_pesquisa": 0,
        "updated_pesquisa": 0,
        "skipped": skipped,
        "errors_count": len(errors),
        "review_candidates_ignored": review_ignored,
        "routing_skipped": routing_skipped,
        "routing_skipped_count": len(routing_skipped),
        "pesquisa_tipo_pesquisa_filled": tipo_pesquisa_filled,
        "pesquisa_tipo_pesquisa_total": pesquisa_n,
        "pesquisa_tipo_recurso_filled": tipo_recurso_filled,
        "pesquisa_tipo_oportunidade_filled": tipo_oportunidade_filled,
        "arrays_normalized_count": len(arrays_normalized),
        "arrays_normalized_sample": arrays_normalized[:40],
        "environment_guard": env_guard,
        "environment_safe": env_safe,
        "env_files_loaded": [str(p) for p in _ENV_CANDIDATES if p.is_file()],
        "apply_executado": False,
        "apply_block_reason": "",
    }

    by_table = {
        "noticia": {
            "total_input": len(raw_n),
            "would_upsert": len(prepared_n),
            "inserted": 0,
            "updated": 0,
        },
        "pesquisa": {
            "total_input": len(raw_p),
            "would_upsert": len(prepared_p),
            "inserted": 0,
            "updated": 0,
        },
    }

    if args.dry_run:
        summary["apply_status"] = "dry_run_only"
        summary["nota"] = "Nenhuma escrita no Supabase."
    elif args.apply:
        if not env_safe:
            summary["apply_status"] = "blocked"
            summary["apply_block_reason"] = env_guard.get("block_reason") or "unknown"
            errors.append(
                {
                    "table": "_guard",
                    "erro": "apply_bloqueado",
                    "detalhe": summary["apply_block_reason"],
                }
            )
        elif not args.test_db_before_apply:
            summary["apply_status"] = "blocked_missing_test_db_flag"
            errors.append(
                {
                    "table": "_guard",
                    "erro": "exija --test-db-before-apply para apply",
                }
            )
        else:
            try:
                db = _get_supabase()
                ok_t, err_t = _test_tables_news(db.supabase)
                if not ok_t:
                    summary["apply_status"] = "aborted_db_test"
                    summary["apply_block_reason"] = err_t
                    errors.append({"table": "_db_test", "erro": err_t})
                else:
                    ins_n = upd_n = ins_p = upd_p = 0
                    for row in prepared_n:
                        lk = row.get("link")
                        existed = _exists_link(db.supabase, "noticia", str(lk))
                        db.supabase.table("noticia").upsert(row, on_conflict="link").execute()
                        if existed:
                            upd_n += 1
                        else:
                            ins_n += 1
                    for row in prepared_p:
                        lk = row.get("link")
                        existed = _exists_link(db.supabase, "pesquisa", str(lk))
                        db.supabase.table("pesquisa").upsert(row, on_conflict="link").execute()
                        if existed:
                            upd_p += 1
                        else:
                            ins_p += 1
                    summary["inserted_noticia"] = ins_n
                    summary["updated_noticia"] = upd_n
                    summary["inserted_pesquisa"] = ins_p
                    summary["updated_pesquisa"] = upd_p
                    summary["apply_executado"] = True
                    summary["apply_status"] = "applied"
                    by_table["noticia"]["inserted"] = ins_n
                    by_table["noticia"]["updated"] = upd_n
                    by_table["pesquisa"]["inserted"] = ins_p
                    by_table["pesquisa"]["updated"] = upd_p
            except Exception as exc:
                summary["apply_status"] = "error"
                summary["apply_block_reason"] = str(exc)
                errors.append({"table": "_apply", "erro": str(exc)})

    summary["errors_count"] = len(errors)

    (out_dir / "load_news_research_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "load_news_research_by_table.json").write_text(
        json.dumps(by_table, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "load_news_research_errors.json").write_text(
        json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "load_news_research_payload_examples.json").write_text(
        json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Load news/research (notícia / pesquisa)",
        "",
        f"- Execução: `{summary['data_execucao']}`",
        f"- Modo: **{summary['modo']}**",
        f"- Fonte: `{summary['source']}`",
        f"- Wave: `{summary.get('wave') or '—'}`",
        f"- Payload notícia: `{summary.get('payload_noticia_path', '')}`",
        f"- Payload pesquisa: `{summary.get('payload_pesquisa_path', '')}`",
        f"- Review (auditoria, não carregado): `{summary.get('payload_review_path', '')}`",
        f"- Diretório: `{summary['input_dir']}`",
        "",
        "## Métricas",
        "",
        f"- total_noticia (input): **{summary['total_noticia']}**",
        f"- total_pesquisa (input): **{summary['total_pesquisa']}**",
        f"- would_upsert_noticia: **{summary['would_upsert_noticia']}**",
        f"- would_upsert_pesquisa: **{summary['would_upsert_pesquisa']}**",
        f"- pesquisa tipo_pesquisa preenchido: **{summary.get('pesquisa_tipo_pesquisa_filled', 0)}** / **{summary.get('pesquisa_tipo_pesquisa_total', 0)}**",
        f"- pesquisa tipo_recurso preenchido: **{summary.get('pesquisa_tipo_recurso_filled', 0)}** / **{summary.get('pesquisa_tipo_pesquisa_total', 0)}**",
        f"- pesquisa tipo_oportunidade preenchido: **{summary.get('pesquisa_tipo_oportunidade_filled', 0)}** / **{summary.get('pesquisa_tipo_pesquisa_total', 0)}**",
        f"- routing_skipped: **{summary.get('routing_skipped_count', 0)}**",
        f"- inserted_noticia / updated_noticia: **{summary['inserted_noticia']}** / **{summary['updated_noticia']}**",
        f"- inserted_pesquisa / updated_pesquisa: **{summary['inserted_pesquisa']}** / **{summary['updated_pesquisa']}**",
        f"- skipped: **{summary['skipped']}**",
        f"- errors: **{summary['errors_count']}**",
        f"- review_candidates_ignored: **{summary['review_candidates_ignored']}**",
        f"- arrays_normalized_count: **{summary['arrays_normalized_count']}**",
        "",
        "## Environment guard (mascarado)",
        "",
        "```json",
        json.dumps(env_guard, ensure_ascii=False, indent=2),
        "```",
        "",
        f"- environment_safe (para **apply**): **{env_safe}**",
        f"- apply_status: `{summary.get('apply_status', '')}`",
        "",
        "> Em `--dry-run`, não é obrigatório `environment_safe`; o bloco acima apenas documenta o ambiente atual.",
        "",
        "## Apply staging (não executado por padrão)",
        "",
        "Pré-requisitos no ambiente:",
        "",
        "- `EDITALFINDER_ENV=staging` ou `local`",
        "- `EDITALFINDER_ALLOW_STAGING_APPLY=true`",
        "- `SUPABASE_URL` + chave de serviço (`SUPABASE_SERVICE_ROLE_KEY` ou `SUPABASE_KEY`)",
        "- Flags: `--apply --staging --test-db-before-apply`",
        "",
        "```text",
        "# Exemplo (não executar até validar .env.staging):",
        "# set EDITALFINDER_ENV=staging",
        "# set EDITALFINDER_ALLOW_STAGING_APPLY=true",
        "# CORE\\.venv\\Scripts\\python.exe scripts\\load_news_research_sources.py ^",
        "#   --apply --staging --test-db-before-apply --wave nasa_wave2 ^",
        "#   --input-dir audit_reports_news_research_loader",
        "```",
        "",
    ]
    (out_dir / "load_news_research_summary.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({"ok": True, "apply_status": summary.get("apply_status"), "would_n": len(prepared_n), "would_p": len(prepared_p)}, ensure_ascii=False))

    val_errors = [e for e in errors if e.get("erro") == "validacao"]
    if val_errors:
        return 1
    if args.dry_run:
        return 0
    if args.apply and not summary.get("apply_executado"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
