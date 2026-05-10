#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_IN = ROOT / "audit_reports_duplicates_db"
DEFAULT_OUT = ROOT / "audit_reports_dedup_plan"


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    if isinstance(v, (list, dict)) and len(v) == 0:
        return True
    return False


def _quality(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0


def _score_item(it: Dict[str, Any]) -> Tuple[float, int, int, int, int, int, str]:
    q = _quality(it.get("qualidade_dado"))
    has_desc = 1 if not _is_empty(it.get("descricao")) else 0
    has_pdf = 1 if not _is_empty(it.get("pdf_url")) else 0
    has_docs = 1 if bool(it.get("extras_documentos")) else 0
    has_tipo = 1 if (not _is_empty(it.get("tipo_recurso")) and not _is_empty(it.get("tipo_oportunidade"))) else 0
    has_area = 1 if not _is_empty(it.get("area")) else 0
    updated = str(it.get("atualizado_em") or "")
    return (q, has_desc, has_pdf, has_docs, has_tipo, has_area, updated)


def _choose_canonical(group: Dict[str, Any]) -> Any:
    items = group.get("itens") or []
    if not isinstance(items, list) or not items:
        return group.get("registro_canonico_sugerido")
    ranked = sorted(items, key=_score_item, reverse=True)
    cid = ranked[0].get("id_edital")
    return cid if cid is not None else group.get("registro_canonico_sugerido")


def _titles_compatible(items: List[Dict[str, Any]]) -> bool:
    titles = {str(i.get("titulo") or "").strip().lower() for i in items if str(i.get("titulo") or "").strip()}
    return len(titles) <= 2


def _sources_compatible(items: List[Dict[str, Any]]) -> bool:
    src = {str(i.get("fonte_recurso") or "").strip().lower() for i in items if str(i.get("fonte_recurso") or "").strip()}
    return len(src) <= 1


def _plan_for_group(group: Dict[str, Any], include_fuzzy: bool) -> Dict[str, Any]:
    crit = str(group.get("criterio") or "")
    items = group.get("itens") or []
    qnt = int(group.get("quantidade") or len(items) or 0)
    canonical = _choose_canonical(group)
    ids = [x.get("id_edital") for x in items if x.get("id_edital") is not None]
    merge_candidates = [i for i in ids if i != canonical]
    same_src = _sources_compatible(items)
    same_title = _titles_compatible(items)

    rec = "revisar_manual"
    conf = "baixa"
    reason = ""
    risks: List[str] = []

    strong = {"link", "codigo_oportunidade", "numero_processo"}
    moderate = {"fonte_titulo_normalizado", "numero_edital"}
    is_fuzzy = crit.startswith("fuzzy")

    if crit in strong:
        rec, conf, reason = "merge_seguro", "alta", f"critério forte: {crit}"
    elif crit == "hash_deduplicacao":
        if same_src and same_title:
            rec, conf, reason = "merge_seguro", "alta", "hash igual com fonte/título compatíveis"
        elif same_title:
            rec, conf, reason = "revisar_manual", "média", "hash igual e títulos próximos, mas fonte difere"
            risks.append("fontes_diferentes")
        else:
            rec, conf, reason = "revisar_manual", "baixa", "hash igual com baixa compatibilidade semântica"
            risks.append("titulos_diferentes")
    elif crit == "pdf_url":
        if same_src and same_title:
            rec, conf, reason = "revisar_manual", "média", "pdf compartilhado pode representar chamadas distintas"
            risks.append("pdf_compartilhado")
        else:
            rec, conf, reason = "revisar_manual", "baixa", "pdf igual sem compatibilidade título/fonte"
            risks.extend(["pdf_compartilhado", "fontes_ou_titulos_divergentes"])
    elif crit in moderate:
        if same_src and same_title:
            rec, conf, reason = "duplicata_possivel", "média", f"critério moderado: {crit}"
            rec = "revisar_manual"
        else:
            rec, conf, reason = "manter_todos", "baixa", f"{crit} com forte divergência"
            risks.append("divergencia_semantica")
    elif is_fuzzy:
        if include_fuzzy:
            rec, conf, reason = "revisar_manual", "baixa", "fuzzy exige validação humana"
            risks.append("fuzzy_match")
        else:
            rec, conf, reason = "manter_todos", "baixa", "fuzzy desconsiderado nesta execução"
    else:
        rec, conf, reason = "revisar_manual", "baixa", "critério não classificado automaticamente"

    if not merge_candidates:
        rec, conf = "manter_todos", "baixa"
        reason = "grupo sem candidatos de merge distintos do canônico"

    return {
        "criterio": crit,
        "quantidade": qnt,
        "chave_grupo": group.get("chave_grupo"),
        "id_canonico_sugerido": canonical,
        "ids_candidatos_merge": merge_candidates,
        "motivo": reason,
        "confianca": conf,
        "campos_a_preservar": [
            "titulo",
            "descricao",
            "tipo_recurso",
            "tipo_oportunidade",
            "area",
            "pdf_url",
            "extras",
            "atualizado_em",
        ],
        "documentos_a_mesclar": "extras.documentos por URL única",
        "extras_a_mesclar": True,
        "riscos": risks,
        "recomendacao_final": rec,
        "itens": items[:10],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--input-dir", default=str(DEFAULT_IN))
    ap.add_argument("--output-dir", default=str(DEFAULT_OUT))
    ap.add_argument("--only-strong", action="store_true")
    ap.add_argument("--include-fuzzy", action="store_true")
    ap.add_argument("--limit-examples", type=int, default=10)
    args = ap.parse_args()

    in_dir = Path(args.input_dir).resolve() if not Path(args.input_dir).is_absolute() else Path(args.input_dir)
    out_dir = Path(args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_groups = []
    files_map = {
        "duplicates_by_link.json": "link",
        "duplicates_by_hash.json": "hash_deduplicacao",
        "duplicates_by_pdf.json": "pdf_url",
        "duplicates_by_source_title.json": "fonte_titulo_normalizado",
        "duplicates_by_codigo_oportunidade.json": "codigo_oportunidade",
        "duplicates_by_numero_edital.json": "numero_edital",
        "duplicates_by_numero_processo.json": "numero_processo",
        "duplicates_possible_fuzzy.json": "fuzzy",
    }
    for fn, _ in files_map.items():
        data = _load_json(in_dir / fn, [])
        if isinstance(data, list):
            raw_groups.extend([g for g in data if isinstance(g, dict)])

    if args.only_strong:
        strong_criteria = {"link", "codigo_oportunidade", "numero_processo", "hash_deduplicacao"}
        raw_groups = [g for g in raw_groups if str(g.get("criterio") or "") in strong_criteria]
    if not args.include_fuzzy:
        raw_groups = [g for g in raw_groups if not str(g.get("criterio") or "").startswith("fuzzy")]

    planned = [_plan_for_group(g, include_fuzzy=args.include_fuzzy) for g in raw_groups]

    safe_merge = [p for p in planned if p["recomendacao_final"] == "merge_seguro"]
    manual = [p for p in planned if p["recomendacao_final"] == "revisar_manual"]
    keep = [p for p in planned if p["recomendacao_final"] == "manter_todos"]

    canonical_examples = [
        {
            "criterio": p["criterio"],
            "chave_grupo": p["chave_grupo"],
            "id_canonico_sugerido": p["id_canonico_sugerido"],
            "ids_candidatos_merge": p["ids_candidatos_merge"],
            "confianca": p["confianca"],
        }
        for p in sorted(planned, key=lambda x: x["quantidade"], reverse=True)[: max(10, args.limit_examples)]
    ]

    summary = {
        "data_plano": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_dir": str(in_dir),
        "total_grupos_avaliados": len(planned),
        "merge_seguro": len(safe_merge),
        "revisar_manual": len(manual),
        "manter_todos": len(keep),
        "only_strong": bool(args.only_strong),
        "include_fuzzy": bool(args.include_fuzzy),
        "proposal_future_implementation": {
            "merge_extras": "merge profundo sem sobrescrever não-vazio por vazio",
            "merge_documentos": "dedupe por URL em extras.documentos",
            "preservar_ids_antigos": "registrar em extras.merged_from_ids",
            "historico": "registrar operação em edital_historico",
            "desativar_duplicatas": "marcar ativo=false no futuro sem delete",
        },
    }

    (out_dir / "dedup_plan_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "merge_safe_candidates.json").write_text(json.dumps(safe_merge, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "manual_review_candidates.json").write_text(json.dumps(manual, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "keep_all_candidates.json").write_text(json.dumps(keep, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "canonical_selection_examples.json").write_text(
        json.dumps(canonical_examples, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Plano de deduplicação (dry-run)",
        "",
        f"- Grupos avaliados: **{summary['total_grupos_avaliados']}**",
        f"- merge_seguro: **{summary['merge_seguro']}**",
        f"- revisar_manual: **{summary['revisar_manual']}**",
        f"- manter_todos: **{summary['manter_todos']}**",
        "",
        "## Top 10 grupos",
        "",
    ]
    top10 = sorted(planned, key=lambda x: x["quantidade"], reverse=True)[:10]
    for p in top10:
        md.append(
            f"- {p['criterio']} | qtd={p['quantidade']} | canônico={p['id_canonico_sugerido']} | recomendação={p['recomendacao_final']} | confiança={p['confianca']}"
        )
    md.extend(
        [
            "",
            "## Proposta futura (não executada)",
            "",
            "- Mesclar `extras` por merge profundo.",
            "- Mesclar `extras.documentos` por URL única.",
            "- Preservar IDs antigos em `extras.merged_from_ids`.",
            "- Registrar eventos em `edital_historico`.",
            "- Em etapa futura, marcar duplicatas como `ativo=false` sem delete.",
        ]
    )
    (out_dir / "dedup_plan_summary.md").write_text("\n".join(md), encoding="utf-8")

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
