#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"

import sys

if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from db import get_safe_connection_diagnostics, supabase  # noqa: E402


DEFAULT_OUT = ROOT / "audit_reports_duplicates_db"


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    if isinstance(v, (list, dict)) and len(v) == 0:
        return True
    return False


def _norm_text(s: Any) -> str:
    t = str(s or "").strip().lower()
    t = (
        t.replace("á", "a")
        .replace("à", "a")
        .replace("â", "a")
        .replace("ã", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("õ", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )
    t = re.sub(r"\s+", " ", t)
    return t


def _arr(v: Any) -> List[Any]:
    if isinstance(v, list):
        return v
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def _fetch_all_editais(source: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    page = 0
    size = 1000
    while True:
        q = supabase.table("edital").select("*").range(page * size, page * size + size - 1)
        if source:
            q = q.eq("fonte_recurso", source)
        r = q.execute()
        rows = r.data or []
        if not rows:
            break
        out.extend([x for x in rows if isinstance(x, dict)])
        if len(rows) < size:
            break
        page += 1
    return out


def _completeness_score(r: Dict[str, Any]) -> int:
    ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
    points = 0
    for f in ("descricao", "pdf_url", "tipo_recurso", "tipo_oportunidade", "prazo_envio"):
        if not _is_empty(r.get(f)):
            points += 1
    if isinstance(ex.get("documentos"), list) and ex.get("documentos"):
        points += 1
    for f in ("area", "perfil_ideal", "publico_alvo_arr", "setor_economico", "area_cientifica", "area_tecnologica", "setor_estrategico"):
        if not _is_empty(r.get(f)):
            points += 1
    return points


def _quality_value(r: Dict[str, Any]) -> float:
    ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
    v = ex.get("qualidade_dado")
    try:
        return float(v)
    except Exception:
        return 0.0


def _updated_at(r: Dict[str, Any]) -> str:
    return str(r.get("atualizado_em") or "")


def _canonical_id(rows: List[Dict[str, Any]]) -> Any:
    ranked = sorted(
        rows,
        key=lambda r: (
            _quality_value(r),
            _completeness_score(r),
            1 if not _is_empty(r.get("descricao")) else 0,
            1 if not _is_empty(r.get("pdf_url")) else 0,
            1 if isinstance((r.get("extras") or {}).get("documentos"), list) and (r.get("extras") or {}).get("documentos") else 0,
            _updated_at(r),
        ),
        reverse=True,
    )
    return ranked[0].get("id_edital") if ranked else None


def _recommend_group(criteria: str, rows: List[Dict[str, Any]]) -> str:
    if criteria == "link":
        return "duplicata_provavel"
    if criteria in ("codigo_oportunidade", "numero_processo"):
        return "duplicata_provavel"
    if criteria == "hash_deduplicacao":
        fontes = {str(r.get("fonte_recurso") or "") for r in rows}
        tit = {_norm_text(r.get("titulo")) for r in rows}
        return "duplicata_provavel" if len(fontes) <= 2 and len(tit) <= 2 else "precisa_revisao_manual"
    if criteria == "fonte_titulo_normalizado":
        links = {_norm_text(r.get("link")) for r in rows}
        return "duplicata_provavel" if len(links) == 1 else "duplicata_possivel"
    if criteria == "pdf_url":
        return "precisa_revisao_manual"
    if criteria == "numero_edital":
        return "duplicata_possivel"
    if criteria.startswith("fuzzy"):
        return "duplicata_possivel"
    return "precisa_revisao_manual"


def _group_payload(criteria: str, key: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    ex_docs = []
    for r in rows:
        ex = r.get("extras") if isinstance(r.get("extras"), dict) else {}
        ex_docs.append(
            {
                "id_edital": r.get("id_edital"),
                "fonte_recurso": r.get("fonte_recurso"),
                "titulo": str(r.get("titulo") or "")[:240],
                "link": str(r.get("link") or "")[:500],
                "pdf_url": r.get("pdf_url"),
                "hash_deduplicacao": r.get("hash_deduplicacao"),
                "codigo_oportunidade": r.get("codigo_oportunidade"),
                "numero_edital": r.get("numero_edital"),
                "numero_processo": r.get("numero_processo"),
                "prazo_envio": r.get("prazo_envio"),
                "qualidade_dado": ex.get("qualidade_dado"),
                "validacao_status": ex.get("validacao_status"),
                "atualizado_em": r.get("atualizado_em"),
                "extras_documentos": isinstance(ex.get("documentos"), list) and len(ex.get("documentos")) > 0,
            }
        )
    rec = _recommend_group(criteria, rows)
    canonical = _canonical_id(rows)
    return {
        "criterio": criteria,
        "chave_grupo": key[:600],
        "quantidade": len(rows),
        "ids": [r.get("id_edital") for r in rows],
        "itens": ex_docs,
        "classificacao": rec,
        "recomendacao": rec,
        "registro_canonico_sugerido": canonical,
        "merge_sugestao": {
            "canonico_id": canonical,
            "preservar_campos_ricos": True,
            "mesclar_documentos_extras": True,
            "nao_sobrescrever_por_vazio": True,
            "preservar_historico_ids": [r.get("id_edital") for r in rows if r.get("id_edital") != canonical],
        },
    }


def _groups_by_field(rows: List[Dict[str, Any]], field: str, criteria: str) -> List[Dict[str, Any]]:
    g: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        v = r.get(field)
        if isinstance(v, str):
            v = v.strip()
        if _is_empty(v):
            continue
        g[str(v)].append(r)
    out = []
    for k, items in g.items():
        if len(items) > 1:
            out.append(_group_payload(criteria, k, items))
    return sorted(out, key=lambda x: x["quantidade"], reverse=True)


def _groups_by_source_title(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    g: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        fonte = _norm_text(r.get("fonte_recurso"))
        titulo = _norm_text(r.get("titulo"))
        if not fonte or not titulo:
            continue
        g[f"{fonte}||{titulo}"].append(r)
    out = []
    for k, items in g.items():
        if len(items) > 1:
            out.append(_group_payload("fonte_titulo_normalizado", k, items))
    return sorted(out, key=lambda x: x["quantidade"], reverse=True)


def _fuzzy_groups(rows: List[Dict[str, Any]], limit_examples: int) -> List[Dict[str, Any]]:
    by_source: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        src = _norm_text(r.get("fonte_recurso"))
        if src and _norm_text(r.get("titulo")):
            by_source[src].append(r)

    groups = []
    seen = set()
    for src, items in by_source.items():
        n = len(items)
        for i in range(n):
            ti = _norm_text(items[i].get("titulo"))
            if len(ti) < 12:
                continue
            cluster = [items[i]]
            for j in range(i + 1, n):
                tj = _norm_text(items[j].get("titulo"))
                if len(tj) < 12:
                    continue
                ratio = SequenceMatcher(None, ti, tj).ratio()
                if ratio >= 0.92:
                    cluster.append(items[j])
            if len(cluster) > 1:
                ids = tuple(sorted(str(x.get("id_edital")) for x in cluster))
                if ids in seen:
                    continue
                seen.add(ids)
                key = f"{src}::{ti[:180]}"
                payload = _group_payload("fuzzy_titulo_mesma_fonte", key, cluster)
                groups.append(payload)
                if len(groups) >= limit_examples * 6:
                    return sorted(groups, key=lambda x: x["quantidade"], reverse=True)

    # fuzzy + prazo e fuzzy + orgao/instituicao (subconjuntos dos pares já detectados)
    enrich = []
    for g in groups:
        itens = g["itens"]
        if len(itens) < 2:
            continue
        prazo_vals = {str(x.get("prazo_envio") or "") for x in itens if str(x.get("prazo_envio") or "")}
        if prazo_vals:
            gg = dict(g)
            gg["criterio"] = "fuzzy_titulo_prazo"
            enrich.append(gg)
        org_vals = {
            _norm_text((rows_map.get(x.get("id_edital")) or {}).get("orgao_responsavel"))
            or _norm_text((rows_map.get(x.get("id_edital")) or {}).get("instituicao"))
            for x in itens
        }
        org_vals = {x for x in org_vals if x}
        if org_vals:
            gg = dict(g)
            gg["criterio"] = "fuzzy_titulo_orgao_ou_instituicao"
            enrich.append(gg)
    all_groups = groups + enrich
    return sorted(all_groups, key=lambda x: x["quantidade"], reverse=True)


def _top_sources(groups: List[Dict[str, Any]]) -> Dict[str, int]:
    c = Counter()
    for g in groups:
        for it in g.get("itens", []):
            src = str(it.get("fonte_recurso") or "")
            if src:
                c[src] += 1
    return dict(c.most_common(20))


def _sql_inspection_snippets() -> List[str]:
    return [
        "-- Duplicatas por link",
        "select link, count(*) as n from public.edital where link is not null and btrim(link) <> '' group by 1 having count(*) > 1 order by n desc;",
        "-- Duplicatas por hash_deduplicacao",
        "select hash_deduplicacao, count(*) as n from public.edital where hash_deduplicacao is not null and btrim(hash_deduplicacao) <> '' group by 1 having count(*) > 1 order by n desc;",
        "-- Duplicatas por fonte + titulo normalizado",
        "select lower(fonte_recurso) as fonte, lower(regexp_replace(titulo, '\\s+', ' ', 'g')) as titulo_norm, count(*) as n from public.edital where titulo is not null and btrim(titulo) <> '' group by 1,2 having count(*) > 1 order by n desc;",
        "-- Duplicatas por pdf_url",
        "select pdf_url, count(*) as n from public.edital where pdf_url is not null and btrim(pdf_url) <> '' group by 1 having count(*) > 1 order by n desc;",
    ]


rows_map: Dict[Any, Dict[str, Any]] = {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--source", default="")
    ap.add_argument("--output-dir", default=str(DEFAULT_OUT))
    ap.add_argument("--limit-examples", type=int, default=10)
    args = ap.parse_args()

    if args.staging:
        import os

        env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
        if env not in ("staging", "local"):
            raise SystemExit("EDITALFINDER_ENV não está staging/local para --staging.")

    out_dir = Path(args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = _fetch_all_editais(args.source.strip())
    global rows_map
    rows_map = {r.get("id_edital"): r for r in rows if r.get("id_edital") is not None}

    by_link = _groups_by_field(rows, "link", "link")
    by_hash = _groups_by_field(rows, "hash_deduplicacao", "hash_deduplicacao")
    by_pdf = _groups_by_field(rows, "pdf_url", "pdf_url")
    by_source_title = _groups_by_source_title(rows)
    by_codigo = _groups_by_field(rows, "codigo_oportunidade", "codigo_oportunidade")
    by_num_edital = _groups_by_field(rows, "numero_edital", "numero_edital")
    by_num_processo = _groups_by_field(rows, "numero_processo", "numero_processo")
    by_fuzzy = _fuzzy_groups(rows, args.limit_examples)

    groups_all = by_link + by_hash + by_pdf + by_source_title + by_codigo + by_num_edital + by_num_processo + by_fuzzy
    top_sources = _top_sources(groups_all)

    def _count(groups: List[Dict[str, Any]]) -> Dict[str, int]:
        return {
            "grupos": len(groups),
            "linhas_afetadas": sum(g.get("quantidade", 0) for g in groups),
        }

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source_filter": args.source.strip(),
        "db_connection_diag": get_safe_connection_diagnostics(),
        "total_registros_analisados": len(rows),
        "totais_por_criterio": {
            "link": _count(by_link),
            "hash_deduplicacao": _count(by_hash),
            "pdf_url": _count(by_pdf),
            "fonte_titulo_normalizado": _count(by_source_title),
            "codigo_oportunidade": _count(by_codigo),
            "numero_edital": _count(by_num_edital),
            "numero_processo": _count(by_num_processo),
            "fuzzy": _count(by_fuzzy),
        },
        "top_fontes_com_duplicatas": top_sources,
    }

    (out_dir / "duplicates_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "duplicates_by_link.json").write_text(json.dumps(by_link, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "duplicates_by_hash.json").write_text(json.dumps(by_hash, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "duplicates_by_pdf.json").write_text(json.dumps(by_pdf, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "duplicates_by_source_title.json").write_text(json.dumps(by_source_title, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "duplicates_by_codigo_oportunidade.json").write_text(json.dumps(by_codigo, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "duplicates_by_numero_edital.json").write_text(json.dumps(by_num_edital, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "duplicates_by_numero_processo.json").write_text(json.dumps(by_num_processo, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "duplicates_possible_fuzzy.json").write_text(json.dumps(by_fuzzy, ensure_ascii=False, indent=2), encoding="utf-8")

    probable = [g for g in groups_all if g.get("classificacao") == "duplicata_provavel"]
    false_pos = [g for g in groups_all if g.get("classificacao") == "falso_positivo_provavel"]
    rec_md = [
        "# Recomendações de deduplicação futura",
        "",
        "- Não executar merge automático sem revisão humana dos grupos `precisa_revisao_manual`.",
        "- Priorizar dedupe por `link`, `codigo_oportunidade`, `numero_processo` e `hash_deduplicacao` (alto sinal).",
        "- Em `pdf_url`, tratar como revisão manual (documento compartilhado entre oportunidades é comum).",
        "- Definir canônico pelo score composto: qualidade_dado + completude + atualizado_em.",
        "- Mesclar `extras.documentos` por URL única e preservar arrays ricos sem sobrescrever por vazio.",
        "- Guardar histórico de IDs mesclados em tabela auxiliar/auditoria antes de qualquer purge.",
        "",
        "## SQLs seguros para inspeção manual",
        "",
    ]
    rec_md.extend([f"`{q}`" for q in _sql_inspection_snippets()])
    (out_dir / "dedup_recommendations.md").write_text("\n".join(rec_md), encoding="utf-8")

    md = [
        "# Auditoria de duplicatas no banco",
        "",
        f"- Total registros analisados: **{len(rows)}**",
        "",
        "## Quantidade por critério",
        "",
    ]
    for k, v in summary["totais_por_criterio"].items():
        md.append(f"- {k}: grupos={v['grupos']}, linhas_afetadas={v['linhas_afetadas']}")
    md.extend(["", "## Top fontes com duplicatas", ""])
    for src, n in top_sources.items():
        md.append(f"- {src}: {n}")
    md.extend(["", "## Top duplicatas prováveis", ""])
    for g in sorted(probable, key=lambda x: x.get("quantidade", 0), reverse=True)[: args.limit_examples]:
        md.append(
            f"- {g.get('criterio')} | qtd={g.get('quantidade')} | canonico={g.get('registro_canonico_sugerido')} | chave={str(g.get('chave_grupo'))[:120]}"
        )
    md.extend(["", "## Falsos positivos prováveis", ""])
    if false_pos:
        for g in false_pos[: args.limit_examples]:
            md.append(f"- {g.get('criterio')} | qtd={g.get('quantidade')} | chave={str(g.get('chave_grupo'))[:120]}")
    else:
        md.append("- Nenhum grupo classificado como falso_positivo_provavel.")
    md.extend(["", "## Recomendações", "", "- Ver `dedup_recommendations.md` para estratégia e SQLs de inspeção (somente SELECT)."])
    (out_dir / "duplicates_summary.md").write_text("\n".join(md), encoding="utf-8")

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
