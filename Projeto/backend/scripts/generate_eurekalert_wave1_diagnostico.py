#!/usr/bin/env python3
"""Agrega crawl_meta + standardized para relatório Wave 1 EurekAlert."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
META_PATH = ROOT / "audit_reports_news_research" / "eurekalert_science_filtered_crawl_meta.json"
STD_PATH = ROOT / "audit_reports_news_research" / "standardized" / "eurekalert_science_filtered_standardized.json"
OUT_MD = ROOT / "audit_reports_news_research" / "eurekalert_wave1_diagnostico.md"
OUT_JSON = ROOT / "audit_reports_news_research" / "eurekalert_wave1_diagnostico.json"

SOURCE_ID = "eurekalert_science_filtered"


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    meta = _load_json(META_PATH, {})
    std: List[Dict[str, Any]] = _load_json(STD_PATH, [])
    if not isinstance(std, list):
        std = []

    fs = (meta.get("theme_filter_stats") or {}) if isinstance(meta, dict) else {}
    extracted = int(fs.get("extracted_total") or 0)
    passed_theme = int(fs.get("passed_theme_filters") or 0)
    rej_excl = int(fs.get("rejected_exclude_keyword") or 0)
    rej_med = int(fs.get("rejected_exclude_medical_generic") or 0)
    rej_req = int(fs.get("rejected_require_any_keyword") or 0)

    without_date = sum(1 for it in std if isinstance(it, dict) and not it.get("data_publicacao"))
    tipo_counts: Dict[str, int] = {}
    for it in std:
        if not isinstance(it, dict):
            continue
        tc = str(it.get("tipo_conteudo") or "desconhecido").strip() or "desconhecido"
        tipo_counts[tc] = tipo_counts.get(tc, 0) + 1

    mk = fs.get("matched_keyword_counts")
    if not isinstance(mk, dict):
        mk = {}
    top_keywords = sorted(mk.items(), key=lambda x: -x[1])[:30]

    max_cfg = int(meta.get("max_items") or 40)
    volume_ok = bool(passed_theme) and passed_theme <= max_cfg + 10

    build_hint = _load_json(
        ROOT / "audit_reports_news_research_loader" / "eurekalert_wave1_dry_run.json", {}
    )
    payload_n = int(build_hint.get("payload_noticia_count") or 0) if isinstance(build_hint, dict) else 0
    payload_p = int(build_hint.get("payload_pesquisa_count") or 0) if isinstance(build_hint, dict) else 0

    report: Dict[str, Any] = {
        "fonte": SOURCE_ID,
        "seeds_usados": meta.get("seed_urls_used") or [],
        "itens_extraidos_antes_filtro_tematico": extracted,
        "passaram_filtro_tematico": passed_theme,
        "rejeitados_require_any": rej_req,
        "rejeitados_exclude": rej_excl,
        "rejeitados_exclude_medicina_saude_generica_heuristica": rej_med,
        "itens_raw_apos_filtro_max_items": meta.get("raw_total"),
        "sem_data_publicacao_no_standardized": without_date,
        "contagem_tipo_conteudo_standardized": tipo_counts,
        "top_matched_keywords": top_keywords,
        "volume_aceitavel_heuristica": volume_ok,
        "payload_build_hint_noticia": payload_n,
        "payload_build_hint_pesquisa": payload_p,
        "apto_apply_staging_build_readiness": (
            (build_hint.get("readiness_apply_staging") or {}).get("ok")
            if isinstance(build_hint, dict)
            else None
        ),
        "nota": "Contagem de saúde/medicina baseada em substrings do exclude_keyword. Datas: meta/JSON-LD na página; fallback do prefixo de data no título (listings EurekAlert).",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# EurekAlert — diagnóstico Wave 1",
        "",
        "## Seeds / URLs usados",
        "",
    ]
    for u in report["seeds_usados"] or []:
        md.append(f"- `{u}`")
    if not report["seeds_usados"]:
        md.append("- *(sem `eurekalert_science_filtered_crawl_meta.json` — correr o crawl)*")
    md.extend(
        [
            "",
            "## Contagens (crawl + filtros)",
            "",
            f"- Itens extraídos do feed/listing (antes do filtro temático, incl. duplicados de link contados no loop): **{extracted}**",
            f"- Passaram require_any + exclude (e limites IAEA N/A): **{passed_theme}**",
            f"- Rejeitados `require_any_keyword` (nenhum termo forte no blob): **{rej_req}**",
            f"- Rejeitados `exclude_keywords`: **{rej_excl}** (heurística medicina/saúde genérica: **{rej_med}**)",
            "",
            "## Standardized (após crawl)",
            "",
            f"- Itens no ficheiro standardized: **{len(std)}** (`raw_total` no meta: **{meta.get('raw_total')!r}**)",
            f"- Sem `data_publicacao`: **{without_date}**",
            "",
            "## Tipo de conteúdo (standardized)",
            "",
        ]
    )
    for k, v in sorted(tipo_counts.items(), key=lambda x: -x[1]):
        md.append(f"- `{k}`: **{v}**")
    md.extend(
        [
            "",
            "## Termos fortes (matches no filtro; top 30)",
            "",
        ]
    )
    for kw, n in top_keywords:
        md.append(f"- `{kw}`: **{n}**")
    if not top_keywords:
        md.append("- *(vazio — sem crawl_meta ou sem matches)*")
    md.extend(
        [
            "",
            "## Volume",
            "",
            f"- Passaram filtro temático (≤ max_items **{max_cfg}**): **{passed_theme}** → heurística aceitável: **{volume_ok}**",
            f"- Build local (`eurekalert_wave1_dry_run.json`): notícias **{payload_n}**, pesquisas **{payload_p}**",
            "",
            "---",
            "",
            "Gerado por `scripts/generate_eurekalert_wave1_diagnostico.py`.",
        ]
    )
    OUT_MD.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"written": [str(OUT_MD), str(OUT_JSON)]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
