#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Loader dedicado: public.concurso_selecao (módulo Concursos & Seleções).

- Lê JSON standardized (wave manual / futuros crawlers).
- Upsert por (fonte, link); não remove registos ausentes do ficheiro.
- Apply só staging/local com guardas (EDITALFINDER_ENV, EDITALFINDER_ALLOW_STAGING_APPLY, chave serviço).
- Produção bloqueada explicitamente.
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
from datetime import date, datetime, timedelta
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

DEFAULT_INPUT = ROOT / "audit_reports_main_pipeline/concursos_wave1_manual/standardized"

ALLOWED_TIPO_SELECAO = frozenset(
    {
        "concurso_publico",
        "processo_seletivo",
        "professor",
        "coordenador",
        "tecnico_administrativo",
        "estagio",
        "residencia",
        "vestibular",
        "bolsa_estudo",
        "programa_ingresso",
    }
)
ALLOWED_STATUS = frozenset(
    {
        "ativo",
        "inscricoes_abertas",
        "inscricoes_encerradas",
        "prova_proxima",
        "encerrado",
        "suspenso",
        "cancelado",
    }
)
ALLOWED_VALIDACAO = frozenset({"valido", "incompleto", "suspeito", "acesso_limitado"})
ALLOWED_FONTE_TIPO = frozenset(
    {"banca", "agregador", "instituicao", "governo", "universidade", "vestibular", "outro"}
)

DATE_FIELDS = (
    "data_publicacao",
    "data_inicio_inscricao",
    "data_fim_inscricao",
    "data_prova",
)


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
        guard = {
            "editalfinder_env": env,
            "has_supabase_url": has_url,
            "has_service_key": has_service_key,
            "has_anon_key": has_anon_key,
            "has_allow_staging_apply": has_allow_staging_apply,
            "url_host_masked": _mask_host(url),
            "block_reason": "",
            "production_blocked": env_prod,
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
        "production_blocked": env_prod,
    }
    return block_reason == "", guard


def _ex(item: Dict[str, Any]) -> Dict[str, Any]:
    e = item.get("extras")
    return e if isinstance(e, dict) else {}


def as_str_array(value: Any, *, max_n: Optional[int] = 24) -> Optional[List[str]]:
    if value is None:
        return None
    if isinstance(value, str):
        s = value.strip()
        arr = [s] if s else []
    elif isinstance(value, (list, tuple, set)):
        arr = [str(v).strip() for v in value if v is not None and str(v).strip()]
    else:
        s = str(value).strip()
        arr = [s] if s else []
    if max_n is not None and len(arr) > max_n:
        arr = arr[:max_n]
    return arr if arr else None


def _parse_date(val: Any) -> Optional[str]:
    """ISO YYYY-MM-DD ou None se vazio."""
    if val is None:
        return None
    if isinstance(val, (date, datetime)):
        return val.date().isoformat() if isinstance(val, datetime) else val.isoformat()
    s = str(val).strip()
    if not s:
        return None
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", s)
    if m:
        return m.group(1)
    return None


def _parse_optional_float(val: Any) -> Optional[float]:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _parse_optional_int(val: Any) -> Optional[int]:
    if val is None or val == "":
        return None
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return None


def _truthy_ativo(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "sim", "on")
    return bool(val)


def _parse_local_date(val: Any) -> Optional[date]:
    """Converte valor de linha (YYYY-MM-DD ou ISO) para date."""
    s = _parse_date(val)
    if not s:
        return None
    try:
        y, m, d = int(s[0:4]), int(s[5:7]), int(s[8:10])
        return date(y, m, d)
    except (ValueError, TypeError):
        return None


def _criado_em_date_from_raw(raw: Dict[str, Any]) -> Optional[date]:
    v = raw.get("criado_em")
    if v is None or (isinstance(v, str) and not str(v).strip()):
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    try:
        if "T" in s:
            return datetime.fromisoformat(s.replace("Z", "+00:00")).date()
        return _parse_local_date(s)
    except (ValueError, TypeError):
        return None


def passes_front_recency(row: Dict[str, Any], raw: Dict[str, Any], today: date) -> bool:
    """
    Espelha a cláusula de recência de public.vw_concursos_front (além de ativo/validação/status).
    """
    dfim = _parse_local_date(row.get("data_fim_inscricao"))
    dprov = _parse_local_date(row.get("data_prova"))
    dpubl = _parse_local_date(row.get("data_publicacao"))
    if dfim is not None and dfim >= today:
        return True
    if dprov is not None and dprov >= today:
        return True
    if dfim is None and dprov is None:
        if dpubl is not None and dpubl >= (today - timedelta(days=90)):
            return True
        cd = _criado_em_date_from_raw(raw)
        if cd is not None and cd >= (today - timedelta(days=90)):
            return True
        # Sem datas no JSON: após insert na BD, `criado_em` default satisfaz o ramo (c) da view.
        return True
    return False


def status_explicit_in_raw(raw: Dict[str, Any]) -> bool:
    if "status" not in raw:
        return False
    v = raw.get("status")
    if v is None:
        return False
    return str(v).strip() != ""


def apply_status_coercion_for_past_dates(row: Dict[str, Any], raw: Dict[str, Any], today: date) -> None:
    """
    Se fim de inscrições e prova já passaram e o JSON não define `status`, força `encerrado`.
    """
    dfim = _parse_local_date(row.get("data_fim_inscricao"))
    dprov = _parse_local_date(row.get("data_prova"))
    if dfim is None or dprov is None:
        return
    if dfim < today and dprov < today and not status_explicit_in_raw(raw):
        row["status"] = "encerrado"


def opt_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def map_standardized_to_row(item: Dict[str, Any], *, source_key: str) -> Dict[str, Any]:
    ex = _ex(item)

    def pick(*keys: str) -> Any:
        for k in keys:
            if k in item and item[k] is not None:
                v = item[k]
                if isinstance(v, str) and not v.strip() and k in ("banca", "link_edital"):
                    continue
                return v
            if k in ex and ex[k] is not None:
                return ex[k]
        return None

    titulo = str(pick("titulo", "title") or "").strip()
    link = str(pick("link", "url") or "").strip()
    fonte = str(pick("fonte", "fonte_nome", "source") or "").strip()
    tipo_selecao = str(pick("tipo_selecao", "tipo") or "").strip().lower()
    status = str(pick("status") or "ativo").strip().lower()
    validacao_status = str(pick("validacao_status") or "incompleto").strip().lower()

    fonte_tipo_raw = pick("fonte_tipo")
    fonte_tipo: Optional[str]
    if fonte_tipo_raw is None or str(fonte_tipo_raw).strip() == "":
        fonte_tipo = None
    else:
        fonte_tipo = str(fonte_tipo_raw).strip().lower()

    extras_out = deepcopy(ex)
    extras_out.setdefault("source_standardized_key", source_key)
    extras_out["loader"] = "load_concursos_selecao"
    extras_out["origem_pipeline"] = str(extras_out.get("origem_pipeline") or "concursos_wave1_manual")

    row: Dict[str, Any] = {
        "titulo": titulo,
        "tipo_selecao": tipo_selecao,
        "categoria": opt_str(pick("categoria")),
        "orgao": opt_str(pick("orgao")),
        "instituicao": opt_str(pick("instituicao")),
        "banca": opt_str(pick("banca")),
        "cargo": opt_str(pick("cargo")),
        "curso": opt_str(pick("curso")),
        "area": opt_str(pick("area")),
        "nivel_escolaridade": opt_str(pick("nivel_escolaridade")),
        "estado": opt_str(pick("estado", "uf")),
        "municipio": opt_str(pick("municipio")),
        "regiao": opt_str(pick("regiao")),
        "modalidade": opt_str(pick("modalidade")),
        "numero_vagas": _parse_optional_int(pick("numero_vagas", "vagas")),
        "salario_min": _parse_optional_float(pick("salario_min")),
        "salario_max": _parse_optional_float(pick("salario_max")),
        "taxa_inscricao": _parse_optional_float(pick("taxa_inscricao")),
        "data_publicacao": _parse_date(pick("data_publicacao")),
        "data_inicio_inscricao": _parse_date(pick("data_inicio_inscricao")),
        "data_fim_inscricao": _parse_date(pick("data_fim_inscricao")),
        "data_prova": _parse_date(pick("data_prova")),
        "status": status,
        "link": link,
        "link_edital": opt_str(pick("link_edital")),
        "fonte": fonte,
        "fonte_tipo": fonte_tipo,
        "validacao_status": validacao_status,
        "qualidade_dado": opt_str(pick("qualidade_dado")),
        "tags": as_str_array(pick("tags")),
        "extras": extras_out,
        "ativo": _truthy_ativo(pick("ativo")),
    }
    return row


def _validate_row(row: Dict[str, Any], *, raw_item: Dict[str, Any]) -> List[str]:
    err: List[str] = []
    if not (row.get("titulo") or "").strip():
        err.append("titulo_obrigatorio")

    link = (row.get("link") or "").strip()
    if not link.startswith("http://") and not link.startswith("https://"):
        err.append("link_http_obrigatorio")

    if not (row.get("fonte") or "").strip():
        err.append("fonte_obrigatoria")

    ts = (row.get("tipo_selecao") or "").strip().lower()
    if ts not in ALLOWED_TIPO_SELECAO:
        err.append(f"tipo_selecao_invalido:{ts}")

    st = (row.get("status") or "").strip().lower()
    if st not in ALLOWED_STATUS:
        err.append(f"status_invalido:{st}")

    vs = (row.get("validacao_status") or "").strip().lower()
    if vs not in ALLOWED_VALIDACAO:
        err.append(f"validacao_status_invalido:{vs}")

    ft = row.get("fonte_tipo")
    if ft is not None and str(ft).strip() != "":
        fts = str(ft).strip().lower()
        if fts not in ALLOWED_FONTE_TIPO:
            err.append(f"fonte_tipo_invalido:{fts}")

    for df in DATE_FIELDS:
        if df not in raw_item:
            continue
        raw_v = raw_item.get(df)
        if raw_v is None or (isinstance(raw_v, str) and not raw_v.strip()):
            continue
        parsed = _parse_date(raw_v)
        if parsed is None:
            err.append(f"data_nao_parseavel:{df}")

    smin = row.get("salario_min")
    smax = row.get("salario_max")
    if smin is not None and smax is not None and float(smin) > float(smax):
        err.append("salario_min_gt_max")

    di = row.get("data_inicio_inscricao")
    dfim = row.get("data_fim_inscricao")
    if di and dfim and di > dfim:
        err.append("data_inicio_inscricao_gt_fim")

    return err


def _get_supabase_client():
    from supabase import create_client

    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip()
    if not url or not key:
        raise RuntimeError("SUPABASE_URL ou chave de serviço ausente")
    return create_client(url, key)


def _row_exists(sb: Any, fonte: str, link: str) -> bool:
    r = (
        sb.table("concurso_selecao")
        .select("link")
        .eq("fonte", fonte)
        .eq("link", link)
        .limit(1)
        .execute()
    )
    data = getattr(r, "data", None) or []
    return bool(data)


def main() -> int:
    ap = argparse.ArgumentParser(description="Loader concurso_selecao (standardized → Supabase)")
    ap.add_argument("--input-dir", default=str(DEFAULT_INPUT))
    ap.add_argument(
        "--sources",
        default="concursos_wave1_manual",
        help="Chaves separadas por vírgula (ficheiros {chave}_standardized.json)",
    )
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--dry-run", action="store_true", help="Validar e gravar relatórios; sem escrita Supabase")
    ap.add_argument(
        "--apply-staging",
        action="store_true",
        help="Upsert em Supabase (exige --staging, EDITALFINDER_ENV staging|local, EDITALFINDER_ALLOW_STAGING_APPLY)",
    )
    ap.add_argument("--staging", action="store_true", help="Obrigatório com --apply-staging")
    args = ap.parse_args()

    if args.apply_staging and args.dry_run:
        print("[ERRO] Não combine --apply-staging com --dry-run", file=sys.stderr)
        return 2
    if args.apply_staging and not args.staging:
        print("[ERRO] --apply-staging exige --staging", file=sys.stderr)
        return 2

    apply_requested = bool(args.apply_staging)
    dry_run = not apply_requested
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
            print(f"[AVISO] JSON não é lista: {path}", file=sys.stderr)
            continue
        for it in raw:
            if isinstance(it, dict):
                all_items.append((key, it))

    prepared: List[Dict[str, Any]] = []
    validation_errors: List[Dict[str, Any]] = []
    map_errors: List[Dict[str, Any]] = []
    apply_errors: List[Dict[str, Any]] = []
    by_source: Dict[str, Dict[str, int]] = {}
    dup_keys: List[Dict[str, Any]] = []

    for sk in sorted(selected):
        by_source.setdefault(sk, {"would_upsert": 0, "errors": 0})

    today = date.today()
    expired_items: List[Dict[str, Any]] = []

    seen_conflict: Set[Tuple[str, str]] = set()
    for src_key, it in all_items:
        try:
            row = map_standardized_to_row(it, source_key=src_key)
            row = sanitize_for_postgres(row)  # type: ignore[assignment]
            apply_status_coercion_for_past_dates(row, it, today)
            row = sanitize_for_postgres(row)  # type: ignore[assignment]
            miss = _validate_row(row, raw_item=it)
            fk = (str(row.get("fonte") or ""), str(row.get("link") or ""))
            if fk[0] and fk[1]:
                if fk in seen_conflict:
                    dup_keys.append({"fonte": fk[0], "link": fk[1], "titulo": row.get("titulo")})
                seen_conflict.add(fk)
            if miss:
                validation_errors.append(
                    {
                        "fonte": src_key,
                        "link": row.get("link"),
                        "titulo": row.get("titulo"),
                        "erros": miss,
                    }
                )
                by_source[src_key]["errors"] += 1
                continue
            if not passes_front_recency(row, it, today):
                expired_items.append(
                    {
                        "fonte": src_key,
                        "link": row.get("link"),
                        "titulo": row.get("titulo"),
                        "motivo": "fora_regra_recencia_vw_concursos_front",
                    }
                )
                print(
                    "[AVISO] Item antigo (não entra em vw_concursos_front com a regra de recência atual): "
                    f"{(row.get('titulo') or '')[:120]} — {row.get('link')}",
                    file=sys.stderr,
                )
            prepared.append(row)
            by_source[src_key]["would_upsert"] += 1
        except Exception as exc:
            map_errors.append({"fonte": src_key, "link": it.get("link"), "erro": str(exc)})
            by_source[src_key]["errors"] += 1

    env_safe, env_guard = _environment_guard(apply_requested=apply_requested, staging_flag=bool(args.staging))

    tipo_c = Counter(str(r.get("tipo_selecao") or "") for r in prepared)
    status_c = Counter(str(r.get("status") or "") for r in prepared)
    vs_c = Counter(str(r.get("validacao_status") or "") for r in prepared)

    inserted = updated = 0
    apply_status = "dry_run_only"
    apply_block = ""

    if apply_requested:
        if not env_safe:
            apply_status = "blocked"
            apply_block = env_guard.get("block_reason") or "unknown"
            apply_errors.append({"table": "_guard", "erro": "apply_bloqueado", "detalhe": apply_block})
        else:
            try:
                sb = _get_supabase_client()
                for row in prepared:
                    fonte = str(row.get("fonte") or "")
                    link = str(row.get("link") or "")
                    existed = _row_exists(sb, fonte, link)
                    payload = {k: v for k, v in row.items() if k not in ("id_concurso", "criado_em", "atualizado_em")}
                    sb.table("concurso_selecao").upsert(payload, on_conflict="fonte,link").execute()
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

    summary: Dict[str, Any] = {
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "modo": "dry_run" if dry_run else "apply_staging",
        "staging_flag": bool(args.staging),
        "apply_staging_requested": bool(args.apply_staging),
        "input_dir": str(input_dir.resolve()),
        "output_dir": str(out_dir.resolve()),
        "sources_selected": sorted(selected),
        "total_items": len(all_items),
        "would_upsert_total": len(prepared),
        "inserted": inserted,
        "updated": updated,
        "upserted_total": (inserted + updated) if (apply_requested and apply_status == "applied") else 0,
        "errors_count": errors_count,
        "map_errors_count": map_errors_count,
        "apply_errors_count": len(apply_errors),
        "errors_total_written": len(errors_out),
        "duplicate_fonte_link_in_batch": len(dup_keys),
        "expired_items_count": len(expired_items),
        "expired_items": expired_items,
        "by_source": by_source,
        "tipo_selecao_counts": dict(tipo_c),
        "status_counts": dict(status_c),
        "validacao_status_counts": dict(vs_c),
        "environment_guard": env_guard,
        "apply_status": apply_status if apply_requested else "dry_run_only",
        "apply_block_reason": apply_block,
    }
    if dry_run:
        summary["nota"] = "Nenhuma escrita no Supabase (dry-run)."
    if dup_keys:
        summary["duplicate_keys_sample"] = dup_keys[:10]

    prefix = "load_concursos_selecao"
    (out_dir / f"{prefix}_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / f"{prefix}_by_source.json").write_text(
        json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / f"{prefix}_errors.json").write_text(
        json.dumps(errors_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    examples = prepared[:12]
    (out_dir / f"{prefix}_payload_examples.json").write_text(
        json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / f"{prefix}_warnings.json").write_text(
        json.dumps(expired_items, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md_sum = [
        f"# Load concurso_selecao — resumo",
        "",
        f"- Execução: `{summary['data_execucao']}`",
        f"- Modo: **{summary['modo']}**",
        f"- `total_items`: **{summary['total_items']}**",
        f"- `would_upsert_total`: **{summary['would_upsert_total']}**",
        f"- `errors_count` (validação): **{summary['errors_count']}**",
        f"- `map_errors_count`: **{summary['map_errors_count']}**",
        f"- `apply_status`: **{summary['apply_status']}**",
        f"- Duplicados (fonte,link) no mesmo lote: **{summary['duplicate_fonte_link_in_batch']}**",
        f"- `expired_items_count` (fora da recência da front): **{summary.get('expired_items_count', 0)}**",
        "",
        "## environment_guard",
        "",
        "```json",
        json.dumps(env_guard, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    (out_dir / f"{prefix}_summary.md").write_text("\n".join(md_sum), encoding="utf-8")

    md_err_lines = [
        "# Load concurso_selecao — erros",
        "",
        f"Total entradas: **{len(errors_out)}**",
        "",
        "Detalhe completo em `load_concursos_selecao_errors.json` (mesmo diretório).",
        "",
    ]
    if errors_out:
        md_err_lines.append("## Resumo")
        for i, e in enumerate(errors_out[:50], 1):
            md_err_lines.append(f"{i}. `{e.get('fonte')}` — {e.get('titulo') or e.get('erro') or e.get('detalhe')}")
        if len(errors_out) > 50:
            md_err_lines.append(f"\n… e mais **{len(errors_out) - 50}** entradas (ver JSON).")
    (out_dir / f"{prefix}_errors.md").write_text("\n".join(md_err_lines), encoding="utf-8")

    print(out_dir.resolve())

    if errors_count > 0 or map_errors_count > 0:
        return 1
    if apply_requested and apply_status not in ("applied",):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
