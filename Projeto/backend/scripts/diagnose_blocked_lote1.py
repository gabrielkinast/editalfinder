#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent.parent
LOT = [
    "badesul",
    "petrobras",
    "senai",
    "softex",
    "plataforma_industria",
    "pncp",
    "marinha",
    "amazul",
    "dcta_ita_iae",
]


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _safe_int(v: Any) -> int:
    try:
        return int(v)
    except Exception:
        return 0


def _detect_raw_output_path(source: str) -> Path | None:
    candidates = [
        ROOT / source / "outputs" / f"{source}_editais.json",
        ROOT / source / "outputs" / "plataforma_editais.json",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return None


def _classificacao_rejeitados(tipos: Dict[str, int]) -> Dict[str, int]:
    out = {
        "oportunidade_real": 0,
        "noticia": 0,
        "pagina_generica": 0,
        "erro_login_restrito": 0,
        "documento_oficial": 0,
        "licitacao_compra_publica": 0,
        "linha_credito_fomento": 0,
        "ruido_duvidoso": 0,
    }
    for k, v in (tipos or {}).items():
        n = _safe_int(v)
        lk = str(k).lower()
        if "licitacao" in lk or "compra_publica" in lk:
            out["licitacao_compra_publica"] += n
        elif "erro_login_restrito" in lk:
            out["erro_login_restrito"] += n
        elif "pagina_generica" in lk:
            out["pagina_generica"] += n
        elif "noticia" in lk:
            out["noticia"] += n
        elif "oportunidade_real" in lk:
            out["oportunidade_real"] += n
        elif "duvidoso" in lk:
            out["ruido_duvidoso"] += n
        else:
            out["ruido_duvidoso"] += n
    return out


def _recomendacao_status(src: Dict[str, Any], rejected_cls: Dict[str, int]) -> str:
    transformados = _safe_int(src.get("transformados"))
    bruto = _safe_int(src.get("bruto_total"))
    rejeitados = _safe_int(src.get("rejeitados"))
    if bruto == 0:
        return "manter_bloqueada"
    if transformados > 0 and rejeitados <= max(1, transformados):
        return "pronta_para_reprocessar"
    if src.get("parece_problema_crawler"):
        return "ajuste_local_crawler"
    if src.get("parece_problema_gate_transformer"):
        return "ajuste_local_gate_transformer"
    if rejected_cls.get("erro_login_restrito", 0) > 0:
        return "manter_bloqueada"
    return "precisa_revisao_manual"


def main() -> int:
    risk_rows = _load_json(ROOT / "audit_reports_retransform_risks" / "risk_by_source.json", [])
    sem_rows = _load_json(ROOT / "audit_reports_semantic" / "audit_semantic_by_source.json", [])
    readiness = _load_json(ROOT / "audit_reports_retransform" / "readiness_for_loader.json", {})
    src_ready_cfg = _load_json(ROOT / "config" / "source_readiness.json", {})

    risk_map = {str(r.get("fonte", "")).lower(): r for r in risk_rows if isinstance(r, dict)}
    sem_map = {str(r.get("fonte", "")).lower(): r for r in sem_rows if isinstance(r, dict)}
    blocked_set = set(src_ready_cfg.get("blocked") or [])

    by_source: List[Dict[str, Any]] = []
    examples: List[Dict[str, Any]] = []

    for source in LOT:
        r = risk_map.get(source, {})
        s = sem_map.get(source, {})
        standardized_path = ROOT / "audit_reports_retransform" / "standardized" / f"{source}_standardized.json"
        standardized_items = _load_json(standardized_path, [])
        standardized_n = len(standardized_items) if isinstance(standardized_items, list) else 0

        raw_path = _detect_raw_output_path(source)
        raw_items = _load_json(raw_path, []) if raw_path else []
        raw_n = len(raw_items) if isinstance(raw_items, list) else 0

        tipos_rejeitados = r.get("tipos_rejeitados_estimados") if isinstance(r.get("tipos_rejeitados_estimados"), dict) else {}
        cls = _classificacao_rejeitados(tipos_rejeitados)

        row = {
            "fonte": source,
            "crawler_roda": raw_path is not None and raw_n > 0,
            "output_bruto_existe": raw_path is not None,
            "output_bruto_path": str(raw_path.relative_to(ROOT)) if raw_path else "",
            "itens_brutos": _safe_int(r.get("bruto_total")) if r else raw_n,
            "itens_transformados": _safe_int(r.get("transformados")) if r else standardized_n,
            "itens_rejeitados": _safe_int(r.get("rejeitados")) if r else max(raw_n - standardized_n, 0),
            "motivos_rejeicao": r.get("motivos_rejeicao") if isinstance(r.get("motivos_rejeicao"), dict) else {},
            "rejeitados_classificacao": cls,
            "parece_problema_crawler": bool(r.get("parece_problema_crawler")),
            "parece_problema_transformer": bool(r.get("parece_problema_gate_transformer")),
            "parece_problema_gate": bool(r.get("parece_problema_gate_transformer")),
            "parece_problema_taxonomia": bool((s.get("flags") or {})),
            "parece_problema_documentos_pdf": False,
            "parece_problema_links_urls": bool(r.get("parece_problema_crawler")) or "plataforma" in source,
            "parece_sem_oportunidade_momento": bool(r.get("parece_sem_oportunidade_real")),
            "semantica_flags": s.get("flags") if isinstance(s.get("flags"), dict) else {},
            "semantica_flag_rate_pct": s.get("flag_rate_pct"),
            "qualidade_media_semantica": s.get("qualidade_media"),
            "diagnostico_curto": r.get("diagnostico", "sem_diagnostico"),
            "recomendacao_tecnica": r.get("recomendacao", ""),
            "recomendacao_status": _recomendacao_status(r, cls),
            "status_atual_readiness": (
                "blocked" if source in blocked_set else "nao_blocked_no_cfg"
            ),
        }
        by_source.append(row)

        for ex in (r.get("exemplos_rejeitados") or [])[:3]:
            if isinstance(ex, dict):
                examples.append(
                    {
                        "fonte": source,
                        "titulo": ex.get("titulo"),
                        "link": ex.get("link"),
                        "motivo_rejeicao": ex.get("motivo_rejeicao"),
                        "tipo_estimado": ex.get("tipo_estimado"),
                        "descricao_curta": ex.get("descricao_curta"),
                    }
                )

    summary = {
        "lote": "lote1",
        "fontes": LOT,
        "fontes_total": len(LOT),
        "bloqueadas_no_cfg": sum(1 for s in LOT if s in blocked_set),
        "itens_brutos_total": sum(_safe_int(r["itens_brutos"]) for r in by_source),
        "itens_transformados_total": sum(_safe_int(r["itens_transformados"]) for r in by_source),
        "itens_rejeitados_total": sum(_safe_int(r["itens_rejeitados"]) for r in by_source),
        "fontes_com_output_bruto": sum(1 for r in by_source if r["output_bruto_existe"]),
        "fontes_com_transformados": sum(1 for r in by_source if _safe_int(r["itens_transformados"]) > 0),
        "fontes_com_sinal_gate_transformer": [r["fonte"] for r in by_source if r["parece_problema_gate"]],
        "fontes_com_sinal_crawler": [r["fonte"] for r in by_source if r["parece_problema_crawler"]],
        "recomendacao_status_count": {},
        "readiness_base_status_distribution": readiness.get("status_distribution", {}),
    }
    for r in by_source:
        k = r["recomendacao_status"]
        summary["recomendacao_status_count"][k] = summary["recomendacao_status_count"].get(k, 0) + 1

    out_dir = ROOT / "audit_reports_blocked_sources"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "lote1_by_source.json").write_text(json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "lote1_examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "lote1_diagnostico.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md: List[str] = []
    md.append("# Diagnóstico inicial — fontes bloqueadas (Lote 1)")
    md.append("")
    md.append("## Resumo")
    md.append(f"- Fontes no lote: **{summary['fontes_total']}**")
    md.append(f"- Bloqueadas no config atual: **{summary['bloqueadas_no_cfg']}**")
    md.append(f"- Itens brutos (total): **{summary['itens_brutos_total']}**")
    md.append(f"- Itens transformados (total): **{summary['itens_transformados_total']}**")
    md.append(f"- Itens rejeitados (total): **{summary['itens_rejeitados_total']}**")
    md.append(f"- Fontes com output bruto: **{summary['fontes_com_output_bruto']}**")
    md.append(f"- Fontes com transformados > 0: **{summary['fontes_com_transformados']}**")
    md.append("")
    md.append("## Diagnóstico por fonte")
    for r in by_source:
        md.append("")
        md.append(f"### {r['fonte']}")
        md.append(f"- crawler roda: **{r['crawler_roda']}**")
        md.append(f"- output bruto existe: **{r['output_bruto_existe']}** (`{r['output_bruto_path']}`)")
        md.append(f"- bruto/transformados/rejeitados: **{r['itens_brutos']}/{r['itens_transformados']}/{r['itens_rejeitados']}**")
        md.append(f"- motivos de rejeição: `{r['motivos_rejeicao']}`")
        md.append(f"- classificação rejeitados: `{r['rejeitados_classificacao']}`")
        md.append(f"- problema no crawler: **{r['parece_problema_crawler']}**")
        md.append(f"- problema no transformer/gate: **{r['parece_problema_transformer']}**")
        md.append(f"- problema em taxonomia: **{r['parece_problema_taxonomia']}**")
        md.append(f"- problema docs/pdf: **{r['parece_problema_documentos_pdf']}**")
        md.append(f"- problema links/URLs: **{r['parece_problema_links_urls']}**")
        md.append(f"- sem oportunidade real no momento: **{r['parece_sem_oportunidade_momento']}**")
        md.append(f"- recomendação técnica: {r['recomendacao_tecnica']}")
        md.append(f"- recomendação de status: **{r['recomendacao_status']}**")
    (out_dir / "lote1_diagnostico.md").write_text("\n".join(md), encoding="utf-8")
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
