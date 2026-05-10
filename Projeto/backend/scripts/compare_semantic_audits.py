#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _top_sources_from_flags(by_source: List[Dict[str, Any]], flag_name: str, n: int = 12) -> List[Dict[str, Any]]:
    rows = []
    for r in by_source:
        flags = r.get("flags") if isinstance(r.get("flags"), dict) else {}
        rows.append({"fonte": r.get("fonte"), "count": int(flags.get(flag_name, 0)), "itens": int(r.get("itens", 0))})
    rows = [x for x in rows if x["count"] > 0]
    rows.sort(key=lambda x: (-x["count"], x["fonte"] or ""))
    return rows[:n]


def _diagnose(before_dir: Path, out_dir: Path) -> Dict[str, Any]:
    examples = _load_json(before_dir / "audit_examples.json", [])
    area_excess = _load_json(before_dir / "audit_area_excess.json", [])
    by_source = _load_json(before_dir / "audit_semantic_by_source.json", [])
    summary = _load_json(before_dir / "audit_semantic_summary.json", {})

    generic_area_terms = {"tecnologia e inovação", "educação e pesquisa", "indústria", "meio ambiente", "energia"}
    generic_setor_terms = {"defesa_industrial", "aeroespacial", "ciencia_tecnologia", "industria", "energia", "nuclear"}
    generic_hits = Counter()
    setor_hits = Counter()
    source_hits = Counter()

    for row in area_excess:
        source = str(row.get("fonte") or "")
        source_hits[source] += 1
        for a in row.get("area") or []:
            if str(a).strip().lower() in generic_area_terms:
                generic_hits[str(a).strip()] += 1
        for s in row.get("setor_estrategico") or []:
            if str(s).strip().lower() in generic_setor_terms:
                setor_hits[str(s).strip()] += 1

    tipo_oportunidade_hits = Counter()
    tipo_recurso_hits = Counter()
    for ex in examples:
        to = str(ex.get("tipo_oportunidade") or "").strip()
        tr = str(ex.get("tipo_recurso") or "").strip()
        if to:
            tipo_oportunidade_hits[to] += 1
        if tr:
            tipo_recurso_hits[tr] += 1

    diagnosis = {
        "top_flags": summary.get("top20_problemas_semanticos") or [],
        "top_fontes_area_cientifica_sem_evidencia": _top_sources_from_flags(by_source, "area_cientifica_sem_evidencia"),
        "top_fontes_area_tecnologica_sem_evidencia": _top_sources_from_flags(by_source, "area_tecnologica_sem_evidencia"),
        "top_fontes_area_excessiva": _top_sources_from_flags(by_source, "area_excessiva"),
        "top_fontes_setor_estrategico_excessivo": _top_sources_from_flags(by_source, "setor_estrategico_excessivo"),
        "termos_area_genericos_mais_recorrentes": generic_hits.most_common(20),
        "setores_genericos_mais_recorrentes": setor_hits.most_common(20),
        "fontes_mais_afetadas_em_area_excessiva": source_hits.most_common(20),
        "tipo_oportunidade_mais_frequente_nos_exemplos": tipo_oportunidade_hits.most_common(20),
        "tipo_recurso_mais_frequente_nos_exemplos": tipo_recurso_hits.most_common(20),
    }

    (out_dir / "semantic_rule_diagnosis.json").write_text(
        json.dumps(diagnosis, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Diagnóstico de regras semânticas",
        "",
        "## Top flags",
        "",
    ]
    for k, v in diagnosis["top_flags"][:20]:
        md.append(f"- {k}: {v}")
    md.extend(["", "## Fontes mais afetadas", ""])
    for section in (
        "top_fontes_area_cientifica_sem_evidencia",
        "top_fontes_area_tecnologica_sem_evidencia",
        "top_fontes_area_excessiva",
        "top_fontes_setor_estrategico_excessivo",
    ):
        md.append(f"- {section}:")
        for row in diagnosis[section][:10]:
            md.append(f"  - {row['fonte']}: {row['count']} (itens={row['itens']})")
    md.extend(["", "## Termos genéricos recorrentes", ""])
    for t, c in diagnosis["termos_area_genericos_mais_recorrentes"][:10]:
        md.append(f"- area '{t}': {c}")
    for t, c in diagnosis["setores_genericos_mais_recorrentes"][:10]:
        md.append(f"- setor '{t}': {c}")
    (out_dir / "semantic_rule_diagnosis.md").write_text("\n".join(md), encoding="utf-8")
    return diagnosis


def _compare(before_dir: Path, after_dir: Path) -> Dict[str, Any]:
    before = _load_json(before_dir / "audit_semantic_summary.json", {})
    after = _load_json(after_dir / "audit_semantic_summary.json", {})
    bflags = before.get("flags_totais") if isinstance(before.get("flags_totais"), dict) else {}
    aflags = after.get("flags_totais") if isinstance(after.get("flags_totais"), dict) else {}

    keys = sorted(set(bflags) | set(aflags))
    deltas = []
    for k in keys:
        bv = int(bflags.get(k, 0))
        av = int(aflags.get(k, 0))
        deltas.append({"flag": k, "before": bv, "after": av, "delta": av - bv})
    deltas.sort(key=lambda x: (x["delta"], x["flag"]))

    cmp_json = {
        "before_itens": before.get("itens_total"),
        "after_itens": after.get("itens_total"),
        "deltas": deltas,
    }
    (after_dir / "COMPARACAO_semantic_before_after.json").write_text(
        json.dumps(cmp_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Comparação semântica before vs after",
        "",
        f"- Itens before: **{cmp_json['before_itens']}**",
        f"- Itens after: **{cmp_json['after_itens']}**",
        "",
        "## Principais melhorias (delta negativo)",
        "",
    ]
    for r in [x for x in deltas if x["delta"] < 0][:20]:
        md.append(f"- {r['flag']}: {r['before']} -> {r['after']} (delta {r['delta']})")
    md.extend(["", "## Principais pioras (delta positivo)", ""])
    for r in [x for x in deltas if x["delta"] > 0][:20]:
        md.append(f"- {r['flag']}: {r['before']} -> {r['after']} (delta +{r['delta']})")
    (after_dir / "COMPARACAO_semantic_before_after.md").write_text("\n".join(md), encoding="utf-8")
    return cmp_json


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before-dir", default="audit_reports_semantic")
    ap.add_argument("--after-dir", default="audit_reports_semantic_after")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    before_dir = (root / args.before_dir).resolve() if not Path(args.before_dir).is_absolute() else Path(args.before_dir)
    after_dir = (root / args.after_dir).resolve() if not Path(args.after_dir).is_absolute() else Path(args.after_dir)
    after_dir.mkdir(parents=True, exist_ok=True)

    _diagnose(before_dir, after_dir)
    _compare(before_dir, after_dir)
    print(after_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
