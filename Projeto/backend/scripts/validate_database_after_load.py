#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"

import sys

if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from db import get_safe_connection_diagnostics, supabase  # noqa: E402


DEFAULT_OUT = ROOT / "audit_reports_db_validation"


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    if isinstance(v, (list, dict)) and len(v) == 0:
        return True
    return False


def _arr(v: Any) -> List[Any]:
    if isinstance(v, list):
        return v
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def _load_readiness() -> Dict[str, List[str]]:
    p = ROOT / "config" / "source_readiness.json"
    if not p.is_file():
        return {"ready": [], "ready_with_notes": [], "needs_manual_review": [], "blocked": [], "reprocess_after_fix": []}
    return json.loads(p.read_text(encoding="utf-8"))


def _fetch_all_editais(source: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    page = 0
    size = 1000
    while True:
        q = supabase.table("edital").select("*").range(page * size, page * size + size - 1)
        if source:
            q = q.eq("fonte_recurso", source)
        r = q.execute()
        data = r.data or []
        if not isinstance(data, list) or not data:
            break
        out.extend([x for x in data if isinstance(x, dict)])
        if len(data) < size:
            break
        page += 1
    return out


def _fetch_view_sample(source: str = "") -> Tuple[List[Dict[str, Any]], int]:
    q = supabase.table("vw_editais_front").select("*", count="exact")
    if source:
        q = q.eq("fonte", source)
    r = q.limit(200).execute()
    rows = r.data or []
    return ([x for x in rows if isinstance(x, dict)], int(r.count or 0))


def _source_counts(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    c = Counter()
    for r in rows:
        c[str(r.get("fonte_recurso") or "").strip() or "sem_fonte"] += 1
    return dict(c)


def _situacao_counts(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    c = Counter()
    for r in rows:
        c[str(r.get("situacao") or "").strip() or "sem_situacao"] += 1
    return dict(c)


def _dup_by_field(rows: List[Dict[str, Any]], field: str, limit_examples: int) -> Dict[str, Any]:
    bucket: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        v = r.get(field)
        if isinstance(v, str):
            v = v.strip()
        if _is_empty(v):
            continue
        bucket[str(v)].append(r)
    dups = {k: v for k, v in bucket.items() if len(v) > 1}
    examples = []
    for k, items in list(dups.items())[:limit_examples]:
        examples.append(
            {
                "field": field,
                "value": k[:500],
                "count": len(items),
                "examples": [
                    {
                        "id_edital": x.get("id_edital"),
                        "fonte_recurso": x.get("fonte_recurso"),
                        "titulo": str(x.get("titulo") or "")[:220],
                        "link": str(x.get("link") or "")[:420],
                    }
                    for x in items[:5]
                ],
            }
        )
    return {"duplicates_count": len(dups), "rows_affected": sum(len(v) for v in dups.values()), "examples": examples}


def _dup_by_composite(rows: List[Dict[str, Any]], fields: List[str], label: str, limit_examples: int) -> Dict[str, Any]:
    bucket: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        vals = []
        for f in fields:
            v = r.get(f)
            if isinstance(v, str):
                v = v.strip()
            vals.append("" if _is_empty(v) else str(v))
        if any(vals):
            key = "||".join(vals)
            bucket[key].append(r)
    dups = {k: v for k, v in bucket.items() if len(v) > 1}
    examples = []
    for k, items in list(dups.items())[:limit_examples]:
        examples.append(
            {
                "field": label,
                "value": k[:500],
                "count": len(items),
                "examples": [
                    {
                        "id_edital": x.get("id_edital"),
                        "fonte_recurso": x.get("fonte_recurso"),
                        "titulo": str(x.get("titulo") or "")[:220],
                        "link": str(x.get("link") or "")[:420],
                    }
                    for x in items[:5]
                ],
            }
        )
    return {"duplicates_count": len(dups), "rows_affected": sum(len(v) for v in dups.values()), "examples": examples}


def _extract_doc_formats(rows: List[Dict[str, Any]]) -> Dict[str, int]:
    c = Counter()
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        docs = ex.get("documentos")
        if not isinstance(docs, list):
            continue
        for d in docs:
            if not isinstance(d, dict):
                continue
            fmt = str(d.get("formato") or "").strip().lower()
            if not fmt:
                url = str(d.get("url") or d.get("link") or "").lower().split("?", 1)[0]
                fmt = url.rsplit(".", 1)[-1] if "." in url else "outro"
            c[fmt or "outro"] += 1
    return dict(c)


def _documents_check(rows: List[Dict[str, Any]], limit_examples: int) -> Dict[str, Any]:
    total = len(rows)
    com_docs = com_pdf = docs_nao_pdf = pdf_sem_docs = docs_sem_pdf = docs_vazios = 0
    ex_docs = []
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        docs = ex.get("documentos")
        pdf = r.get("pdf_url")
        docs_list = docs if isinstance(docs, list) else []
        has_docs = len(docs_list) > 0
        has_pdf = not _is_empty(pdf)
        if has_docs:
            com_docs += 1
            non_pdf_here = False
            for d in docs_list:
                if not isinstance(d, dict):
                    continue
                fmt = str(d.get("formato") or "").strip().lower()
                if not fmt:
                    u = str(d.get("url") or "").lower().split("?", 1)[0]
                    fmt = u.rsplit(".", 1)[-1] if "." in u else "outro"
                if fmt != "pdf":
                    non_pdf_here = True
            if non_pdf_here:
                docs_nao_pdf += 1
        else:
            docs_vazios += 1
        if has_pdf:
            com_pdf += 1
        if has_pdf and not has_docs:
            pdf_sem_docs += 1
        if has_docs and not has_pdf:
            docs_sem_pdf += 1
        if has_docs and len(ex_docs) < limit_examples:
            ex_docs.append(
                {
                    "id_edital": r.get("id_edital"),
                    "fonte_recurso": r.get("fonte_recurso"),
                    "titulo": str(r.get("titulo") or "")[:220],
                    "pdf_url": r.get("pdf_url"),
                    "documentos_n": len(docs_list),
                    "documentos_preview": docs_list[:3],
                }
            )

    return {
        "total": total,
        "registros_com_extras_documentos": com_docs,
        "registros_com_pdf_url": com_pdf,
        "registros_com_documentos_nao_pdf": docs_nao_pdf,
        "registros_com_pdf_sem_documentos": pdf_sem_docs,
        "registros_com_documentos_sem_pdf": docs_sem_pdf,
        "registros_com_documentos_vazios": docs_vazios,
        "formatos_detectados": _extract_doc_formats(rows),
        "examples": ex_docs,
    }


def _empty_fields(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    fields = [
        "titulo",
        "link",
        "fonte_recurso",
        "descricao",
        "extras",
        "tipo_recurso",
        "tipo_oportunidade",
        "area",
        "perfil_ideal",
        "publico_alvo_arr",
        "setor_economico",
        "area_cientifica",
        "area_tecnologica",
        "setor_estrategico",
        "validacao_status",
        "qualidade_dado",
        "pdf_url",
        "prazo_envio",
        "valor_total_texto",
        "valor_maximo",
        "valor_minimo",
    ]
    counts = {f: 0 for f in fields}
    by_source: Dict[str, Dict[str, int]] = defaultdict(lambda: {f: 0 for f in fields})
    by_source_total: Counter[str] = Counter()

    for r in rows:
        src = str(r.get("fonte_recurso") or "").strip() or "sem_fonte"
        by_source_total[src] += 1
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        for f in fields:
            if f == "tipo_oportunidade":
                v = r.get("tipo_oportunidade") or ex.get("tipo_oportunidade")
            elif f == "area":
                v = r.get("area") or ex.get("area")
            elif f == "perfil_ideal":
                v = r.get("perfil_ideal") or ex.get("perfil_ideal")
            elif f == "validacao_status":
                v = r.get("validacao_status") or ex.get("validacao_status")
            elif f == "qualidade_dado":
                v = r.get("qualidade_dado") if r.get("qualidade_dado") is not None else ex.get("qualidade_dado")
            else:
                v = r.get(f)
            if _is_empty(v):
                counts[f] += 1
                by_source[src][f] += 1

    pct = {k: round(100.0 * v / max(1, total), 2) for k, v in counts.items()}
    by_source_pct = {}
    for src, m in by_source.items():
        t = max(1, by_source_total[src])
        by_source_pct[src] = {k: round(100.0 * vv / t, 2) for k, vv in m.items()}
    return {"total": total, "empty_counts": counts, "empty_pct": pct, "by_source_empty_pct": by_source_pct}


def _rich_fields(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(rows)
    keys = [
        "area",
        "tipo_oportunidade",
        "tipo_recurso",
        "perfil_ideal",
        "publico_alvo_arr",
        "setor_economico",
        "area_cientifica",
        "area_tecnologica",
        "setor_estrategico",
        "classificacao_confianca",
        "qualidade_dado",
        "validacao_status",
    ]
    out = {}
    for k in keys:
        c = 0
        for r in rows:
            ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
            if k in ("tipo_oportunidade", "perfil_ideal", "classificacao_confianca", "qualidade_dado", "validacao_status", "area"):
                v = r.get(k) if r.get(k) is not None else ex.get(k)
            else:
                v = r.get(k)
            if not _is_empty(v):
                c += 1
        out[k] = {"count": c, "pct": round(100.0 * c / max(1, total), 2)}
    return out


def _examples(rows: List[Dict[str, Any]], limit_examples: int) -> Dict[str, List[Dict[str, Any]]]:
    good = []
    incomplete = []
    with_docs = []
    with_pdf = []
    suspeitos = []
    low_quality = []
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        row_small = {
            "id_edital": r.get("id_edital"),
            "fonte_recurso": r.get("fonte_recurso"),
            "titulo": str(r.get("titulo") or "")[:220],
            "link": str(r.get("link") or "")[:420],
            "tipo_recurso": r.get("tipo_recurso"),
            "tipo_oportunidade": r.get("tipo_oportunidade"),
            "pdf_url": r.get("pdf_url"),
            "validacao_status": ex.get("validacao_status"),
            "qualidade_dado": ex.get("qualidade_dado"),
        }
        if len(with_docs) < limit_examples and isinstance(ex.get("documentos"), list) and ex.get("documentos"):
            with_docs.append(row_small)
        if len(with_pdf) < limit_examples and not _is_empty(r.get("pdf_url")):
            with_pdf.append(row_small)
        if len(suspeitos) < limit_examples and str(ex.get("validacao_status") or "").lower() == "suspeito":
            suspeitos.append(row_small)
        if len(low_quality) < limit_examples and isinstance(ex.get("qualidade_dado"), (int, float)) and float(ex.get("qualidade_dado")) < 0.45:
            low_quality.append(row_small)
        is_incomplete = _is_empty(r.get("descricao")) or _is_empty(r.get("tipo_recurso")) or _is_empty(r.get("area"))
        if len(incomplete) < limit_examples and is_incomplete:
            incomplete.append(row_small)
        is_good = (not _is_empty(r.get("titulo"))) and (not _is_empty(r.get("link"))) and (not _is_empty(r.get("tipo_recurso")))
        if len(good) < limit_examples and is_good:
            good.append(row_small)
    return {
        "registros_bons": good[:limit_examples],
        "registros_incompletos": incomplete[:limit_examples],
        "registros_com_documentos": with_docs[:limit_examples],
        "registros_com_pdf_url": with_pdf[:limit_examples],
        "registros_suspeitos": suspeitos[:limit_examples],
        "registros_qualidade_baixa": low_quality[:limit_examples],
    }


def _view_check(table_count: int, source: str = "") -> Dict[str, Any]:
    fields = [
        "id_edital",
        "titulo",
        "descricao",
        "link",
        "fonte",
        "tipo_recurso",
        "tipo_oportunidade",
        "area",
        "publico_alvo",
        "setor_economico",
        "area_cientifica",
        "area_tecnologica",
        "setor_estrategico",
        "pdf_url",
        "extras",
    ]
    try:
        rows, count = _fetch_view_sample(source)
        sample = rows[0] if rows else {}
        fields_present = {f: (f in sample) for f in fields} if sample else {f: False for f in fields}
        return {
            "view_count": count,
            "view_has_rows": count > 0,
            "table_count": table_count,
            "count_match_table": (count == table_count) if not source else None,
            "fields_present_in_sample": fields_present,
            "error": "",
        }
    except Exception as exc:
        return {
            "view_count": 0,
            "view_has_rows": False,
            "table_count": table_count,
            "count_match_table": False,
            "fields_present_in_sample": {},
            "error": str(exc),
        }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--source", default="")
    ap.add_argument("--output-dir", default=str(DEFAULT_OUT))
    ap.add_argument("--limit-examples", type=int, default=10)
    args = ap.parse_args()

    out_dir = Path(args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    source = args.source.strip()
    if args.staging:
        env = str((__import__("os").getenv("EDITALFINDER_ENV", "") or "")).lower().strip()
        if env not in ("staging", "local"):
            raise SystemExit("EDITALFINDER_ENV não está staging/local para auditoria --staging.")

    errors = []
    try:
        rows = _fetch_all_editais(source)
    except Exception as exc:
        rows = []
        errors.append(f"Falha ao consultar public.edital: {exc}")

    readiness = _load_readiness()
    blocked_set = set(readiness.get("blocked", [])) | set(readiness.get("needs_manual_review", [])) | set(readiness.get("reprocess_after_fix", []))
    loaded_sources = set(str(r.get("fonte_recurso") or "").strip() for r in rows if str(r.get("fonte_recurso") or "").strip())
    blocked_loaded = sorted([s for s in loaded_sources if s in blocked_set])

    total = len(rows)
    ativos = sum(1 for r in rows if r.get("ativo") is True)
    inativos = sum(1 for r in rows if r.get("ativo") is False)
    situacao = _situacao_counts(rows)
    por_fonte = _source_counts(rows)

    dups = {
        "link": _dup_by_field(rows, "link", args.limit_examples),
        "hash_deduplicacao": _dup_by_field(rows, "hash_deduplicacao", args.limit_examples),
        "fonte_titulo": _dup_by_composite(rows, ["fonte_recurso", "titulo"], "fonte_recurso+titulo", args.limit_examples),
        "pdf_url": _dup_by_field(rows, "pdf_url", args.limit_examples),
        "codigo_oportunidade": _dup_by_field(rows, "codigo_oportunidade", args.limit_examples),
        "numero_edital": _dup_by_field(rows, "numero_edital", args.limit_examples),
        "numero_processo": _dup_by_field(rows, "numero_processo", args.limit_examples),
    }

    empty = _empty_fields(rows)
    docs = _documents_check(rows, args.limit_examples)
    rich = _rich_fields(rows)
    view = _view_check(total, source)
    if view.get("error"):
        errors.append(f"Falha na view vw_editais_front: {view['error']}")
    ex = _examples(rows, args.limit_examples)

    critical_alerts = []
    medium_alerts = []
    if blocked_loaded:
        critical_alerts.append(f"Fontes bloqueadas carregadas: {blocked_loaded}")
    if dups["link"]["duplicates_count"] > 0:
        critical_alerts.append(f"Duplicatas por link: {dups['link']['duplicates_count']}")
    if empty["empty_counts"].get("titulo", 0) > 0:
        critical_alerts.append("Há registros com titulo vazio")
    if empty["empty_counts"].get("link", 0) > 0:
        critical_alerts.append("Há registros com link vazio")
    if empty["empty_counts"].get("fonte_recurso", 0) > 0:
        critical_alerts.append("Há registros com fonte_recurso vazia")
    if empty["empty_pct"].get("extras", 0) > 10:
        medium_alerts.append(f"extras vazio > 10% ({empty['empty_pct']['extras']}%)")
    if empty["empty_pct"].get("tipo_recurso", 0) > 20:
        medium_alerts.append(f"tipo_recurso vazio > 20% ({empty['empty_pct']['tipo_recurso']}%)")
    if empty["empty_pct"].get("tipo_oportunidade", 0) > 20:
        medium_alerts.append(f"tipo_oportunidade vazio > 20% ({empty['empty_pct']['tipo_oportunidade']}%)")
    if empty["empty_pct"].get("area", 0) > 60:
        medium_alerts.append(f"area vazia > 60% ({empty['empty_pct']['area']}%)")
    if docs["registros_com_pdf_sem_documentos"] > 0:
        medium_alerts.append(f"pdf_url sem documentos: {docs['registros_com_pdf_sem_documentos']}")
    if not view["view_has_rows"]:
        critical_alerts.append("vw_editais_front vazia ou quebrada")
    if errors:
        critical_alerts.extend(errors)

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_filter": source,
        "db_connection_diag": get_safe_connection_diagnostics(),
        "contagem_geral": {
            "total_registros": total,
            "registros_ativos": ativos,
            "registros_inativos": inativos,
            "por_situacao": situacao,
            "por_fonte": por_fonte,
        },
        "blocked_sources_loaded": blocked_loaded,
        "critical_alerts": critical_alerts,
        "medium_alerts": medium_alerts,
        "duplicates_overview": {k: v["duplicates_count"] for k, v in dups.items()},
        "empty_fields_overview_pct": empty["empty_pct"],
        "documents_overview": {
            "com_documentos": docs["registros_com_extras_documentos"],
            "com_pdf_url": docs["registros_com_pdf_url"],
            "docs_nao_pdf": docs["registros_com_documentos_nao_pdf"],
        },
        "view_overview": {
            "view_count": view["view_count"],
            "count_match_table": view["count_match_table"],
            "view_has_rows": view["view_has_rows"],
            "error": view.get("error", ""),
        },
        "rich_fields_presence": rich,
    }

    by_source_rows = []
    for src, c in sorted(por_fonte.items(), key=lambda x: x[1], reverse=True):
        by_source_rows.append(
            {
                "fonte_recurso": src,
                "total": c,
                "empty_pct": empty["by_source_empty_pct"].get(src, {}),
            }
        )

    (out_dir / "db_validation_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "db_validation_by_source.json").write_text(json.dumps(by_source_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "db_duplicates.json").write_text(json.dumps(dups, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "db_empty_fields.json").write_text(json.dumps(empty, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "db_documents_check.json").write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "db_view_check.json").write_text(json.dumps(view, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "db_blocked_sources_check.json").write_text(
        json.dumps(
            {
                "blocked_sources_config": sorted(list(blocked_set)),
                "blocked_sources_loaded": blocked_loaded,
                "critical": len(blocked_loaded) > 0,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "db_examples.json").write_text(json.dumps(ex, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Validação pós-carga no banco",
        "",
        "## 1. Resumo executivo",
        "",
        f"- Total de registros: **{total}**",
        f"- Ativos: **{ativos}** | Inativos: **{inativos}**",
        f"- Fontes bloqueadas detectadas: **{len(blocked_loaded)}**",
        f"- Erros de consulta: **{len(errors)}**",
        "",
        "## 2. Contagens principais",
        "",
        f"- Fontes distintas: **{len(por_fonte)}**",
        f"- Registros com documentos: **{docs['registros_com_extras_documentos']}**",
        f"- Registros com pdf_url: **{docs['registros_com_pdf_url']}**",
        f"- View vw_editais_front count: **{view['view_count']}**",
        "",
        "## 3. Alertas críticos",
        "",
    ]
    if critical_alerts:
        md.extend([f"- {a}" for a in critical_alerts])
    else:
        md.append("- Nenhum alerta crítico.")
    md.extend(["", "## 4. Alertas médios", ""])
    if medium_alerts:
        md.extend([f"- {a}" for a in medium_alerts])
    else:
        md.append("- Nenhum alerta médio.")
    md.extend(["", "## 5. Fontes carregadas", ""])
    for src, c in sorted(por_fonte.items(), key=lambda x: x[1], reverse=True)[:20]:
        md.append(f"- {src}: {c}")
    md.extend(["", "## 6. Fontes bloqueadas detectadas", ""])
    if blocked_loaded:
        for s in blocked_loaded:
            md.append(f"- {s}")
    else:
        md.append("- Nenhuma.")
    md.extend(["", "## 7. Duplicatas", ""])
    for k, v in summary["duplicates_overview"].items():
        md.append(f"- {k}: {v}")
    md.extend(["", "## 8. Campos vazios (pct)", ""])
    for k, v in sorted(empty["empty_pct"].items(), key=lambda x: x[1], reverse=True)[:15]:
        md.append(f"- {k}: {v}%")
    md.extend(["", "## 9. Documentos", ""])
    md.append(f"- Com extras.documentos: {docs['registros_com_extras_documentos']}")
    md.append(f"- Com pdf_url: {docs['registros_com_pdf_url']}")
    md.append(f"- Com docs não-PDF: {docs['registros_com_documentos_nao_pdf']}")
    md.append(f"- pdf sem documentos: {docs['registros_com_pdf_sem_documentos']}")
    md.extend(["", "## 10. View frontend", ""])
    md.append(f"- View retorna registros: {view['view_has_rows']}")
    md.append(f"- Count view: {view['view_count']}")
    md.append(f"- Count bate com tabela: {view['count_match_table']}")
    if view.get("error"):
        md.append(f"- Erro da view: {view['error']}")
    md.extend(["", "## 11. Recomendações", ""])
    md.append("- Manter bloqueio de fontes fora de readiness no próximo ciclo.")
    md.append("- Investigar duplicatas por link/hash antes de promover para produção.")
    md.append("- Revisar campos com maior taxa de vazio por fonte para ajuste fino de classificação.")
    (out_dir / "db_validation_summary.md").write_text("\n".join(md), encoding="utf-8")

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
