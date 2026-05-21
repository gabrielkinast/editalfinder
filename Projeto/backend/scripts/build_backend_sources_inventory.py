#!/usr/bin/env python3
"""Gera docs/BACKEND_SOURCES_INVENTORY.json (one-off doc build)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]


def mk(
    src_id: str,
    name: str,
    module: str,
    source_type: str,
    pipeline: str,
    config: Optional[str],
    artifacts: str,
    dest: str,
    status: str,
    reason: str,
    std: Any = None,
    val: Any = None,
    err: Any = None,
    wu: Any = None,
    apply: Any = None,
    notes: str = "",
) -> Dict[str, Any]:
    return {
        "source_id": src_id,
        "name": name,
        "module": module,
        "source_type": source_type,
        "pipeline_script": pipeline,
        "config_file": config,
        "artifacts_dir": artifacts,
        "destination": dest,
        "status": status,
        "status_reason": reason,
        "last_known_result": {
            "standardized": std,
            "validos": val,
            "errors_count": err,
            "would_upsert": wu,
            "apply_executed": apply,
        },
        "notes": notes,
    }


def _load_summary(path: Path) -> Dict[str, Any]:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    sources: List[Dict[str, Any]] = []

    concursos_rows = [
        ("pci_concursos", "PCI Concursos", "agregador", "concursos/main_pci_concursos.py", "concursos_wave1_pci", "descoberta", "Agregador; 12 apply staging; 0 validos", 12, 0, 0, 12, True),
        ("fundatec", "Fundatec", "banca", "concursos/main_fundatec_concursos.py", "concursos_wave1_fundatec", "aplicada", "Subset 2 validos apply staging", 7, 2, 0, 2, True),
        ("quadrix", "Quadrix", "banca", "concursos/main_quadrix_concursos.py", "concursos_wave1_quadrix", "aplicada", "10/10 validos wave1", 10, 10, 0, 10, True),
        ("legalle", "Legalle", "banca", "concursos/main_legalle_concursos.py", "concursos_wave1_legalle", "aplicada", "5 validos apply", 5, 5, 0, 5, True),
        ("objetiva", "Objetiva", "banca", "concursos/main_objetiva_concursos.py", "concursos_wave1_objetiva", "aplicada", "3 validos apply", 3, 3, 0, 3, True),
        ("ibfc", "IBFC", "banca", "concursos/main_ibfc_concursos.py", "concursos_wave1_ibfc", "aplicada", "1 valido apply", 1, 1, 0, 1, True),
        ("fgv", "FGV Conhecimento", "banca", "concursos/main_fgv_concursos.py", "concursos_wave1_fgv", "implementada_latente", "3 std, 1 valido; sem apply", 3, 1, 0, 0, False),
        ("cebraspe", "Cebraspe", "banca", "concursos/main_cebraspe_concursos.py", "concursos_wave1_cebraspe", "implementada_latente", "PAS API; 0 std ativo wave1", 0, 0, 0, 0, False),
        ("aocp", "AOCP", "banca", "concursos/main_aocp_concursos.py", "concursos_wave2_aocp", "implementada_latente", "Wave2: 2 std, 1 valido; sem apply", 2, 1, 0, 0, False),
        ("avancasp", "Avança SP", "banca", "concursos/main_avancasp_concursos.py", "concursos_wave2_avancasp", "aplicada", "Wave2: 5/5 validos staging apply", 5, 5, 0, 5, True),
        ("fcc", "FCC", "banca", "concursos/main_fcc_concursos.py", "concursos_wave2_fcc", "nao_recomendado", "robots.txt; modo completo bloqueado; 2/4 validos", 4, 2, 0, 0, False),
        ("consulplan", "Consulplan", "banca", "concursos/main_consulplan_concursos.py", "concursos_wave2_consulplan", "precisa_melhoria", "0/10 validos; PDF enrich fraco", 10, 0, 0, 0, False),
        ("fuvest", "Fuvest", "universidade", "concursos/main_fuvest_concursos.py", "concursos_wave2_fuvest", "precisa_melhoria", "0/2 validos", 2, 0, 0, 0, False),
        ("comvest", "Comvest (Unicamp)", "universidade", "concursos/main_vestibulares_comvest.py", "concursos_wave2_comvest", "precisa_melhoria", "Sem data_fim_inscricao no site", 2, 0, 0, 0, False),
        ("coperve", "Coperve UFSC", "universidade", "concursos/main_vestibulares_coperve.py", "concursos_wave2_coperve", "implementada_latente", "9 std, 0 validos", 9, 0, 0, 0, False),
        ("ufrgs_cv", "UFRGS/COPERSE", "universidade", "concursos/main_vestibulares_ufrgs.py", "concursos_wave2_ufrgs_cv", "implementada_latente", "7 std, 0 validos", 7, 0, 0, 0, False),
        ("ita_vestibular", "ITA Vestibular", "universidade", "concursos/main_militar_aeroespacial_ita.py", "concursos_wave2_militar_aeroespacial_ita", "precisa_melhoria", "PDF escaneado; 0/1 valido", 1, 0, 0, 0, False),
        ("ime", "IME (CFG/CFrm/CG/CP)", "instituicao_militar", "concursos/main_militar_aeroespacial_ime.py", "concursos_wave2_militar_aeroespacial_ime", "precisa_melhoria", "5 std; OCR/datas PDF", 5, 0, 0, 0, False),
        ("embarcatech", "EmbarcaTech (Softex)", "residencia", "concursos/main_residencias_embarcatech.py", "concursos_wave2_residencias_embarcatech", "precisa_melhoria", "2 std; fetch errors", 2, 0, 2, 0, False),
    ]
    for sid, name, stype, pipe, art, status, reason, std, val, err, wu, apply in concursos_rows:
        sources.append(
            mk(
                sid,
                name,
                "concursos_selecoes",
                stype,
                pipe,
                "docs/CONCURSOS_FONTES_WAVE1.md",
                f"audit_reports_main_pipeline/{art}",
                "public.concurso_selecao → vw_concursos_front",
                status,
                reason,
                std,
                val,
                err,
                wu,
                apply,
            )
        )

    sources.append(
        mk(
            "mcti_fomento_transformacao_digital",
            "MCTI Fomento (Transformação Digital)",
            "radar_editais",
            "governo",
            "scripts/radar/run_mcti_fomento_dryrun_v3.py",
            "docs/MCTI_FOMENTO_RADAR_EDITAIS_PLAN.md",
            "audit_reports_radar/mcti_fomento_dryrun_v3",
            "public.edital (futuro; apply_status não_recomendado)",
            "nao_recomendado",
            "Curadoria v3: 5 prontos técnicos são editais/chamamentos históricos (2020–2024); sem oportunidade ativa",
            5,
            5,
            0,
            0,
            False,
            "apply_status=não_recomendado; reexecutar periodicamente",
        )
    )

    nr_cfg = json.loads((ROOT / "config/news_research_sources.json").read_text(encoding="utf-8"))
    dryrun = {
        "defesanet": ("pronta_para_apply", "audit_reports_news_research/defesanet_dryrun"),
        "brisa_news": ("implementada_latente", "audit_reports_news_research/brisa_news_dryrun"),
        "brisa_artigos": ("implementada_latente", "audit_reports_news_research/brisa_artigos_dryrun"),
        "exercito_brasileiro": ("pronta_para_apply", "audit_reports_news_research/exercito_brasileiro_dryrun"),
        "softex_noticias": ("pronta_para_apply", "audit_reports_news_research/softex_noticias_dryrun"),
        "capes_noticias": ("pronta_para_apply", "audit_reports_news_research/capes_noticias_dryrun"),
        "ita_projetos": ("precisa_melhoria", "audit_reports_news_research/ita_projetos_dryrun"),
        "ita_lab_guerra_eletronica": ("implementada_latente", "audit_reports_news_research/ita_lab_guerra_eletronica_dryrun"),
    }
    for s in nr_cfg["sources"]:
        sid = s["id"]
        kinds = s.get("kind") or ["noticia"]
        if sid in dryrun:
            st, art = dryrun[sid]
        else:
            st, art = "dryrun_ok", f"audit_reports_news_research_loader/ ({sid})"
        sm = _load_summary(ROOT / art / "summary.json") if "dryrun" in art else {}
        std = sm.get("totais", {}).get("standardized") or sm.get("total_standardized")
        val = (sm.get("validacao_status_counts") or {}).get("valido")
        dest = "public.noticia"
        if "pesquisa" in kinds and "noticia" not in kinds:
            dest = "public.pesquisa"
        elif "pesquisa" in kinds and "noticia" in kinds:
            dest = "public.noticia + public.pesquisa (roteamento por item)"
        if "edital_referencia" in kinds:
            dest += "; review_for_edital em dry-run (não auto public.edital)"
        intl = sid in ("nasa_news", "darpa_news", "darpa_opportunities_research", "iaea_news_publications", "eurekalert_science_filtered")
        if intl and sid not in dryrun:
            cfg_st = s.get("status", "")
            if cfg_st == "experimental_wave":
                st = "precisa_melhoria"
            elif cfg_st == "needs_cleanup":
                st = "precisa_melhoria"
            else:
                st = "pronta_para_apply"
        sources.append(
            mk(
                sid,
                s.get("name", sid),
                "noticias_pesquisas",
                kinds[0] if len(kinds) == 1 else "noticia+pesquisa",
                "scripts/crawl_news_research_sources.py"
                + ("; scripts/news_research/run_*_dryrun.py" if sid in dryrun else "; scripts/build_*_payloads.py"),
                "config/news_research_sources.json",
                art,
                f"{dest} → vw_noticias_front / vw_pesquisas_front",
                st,
                (s.get("status_notes") or "")[:200],
                std,
                val,
                0,
                None,
                False,
            )
        )

    sr = json.loads((ROOT / "config/source_readiness.json").read_text(encoding="utf-8"))
    bucket_status = {
        "ready": "aplicada",
        "ready_with_notes": "pronta_para_apply",
        "needs_manual_review": "precisa_melhoria",
        "blocked": "nao_recomendado",
        "reprocess_after_fix": "precisa_melhoria",
    }
    for bucket, status in bucket_status.items():
        for sid in sr.get(bucket, []):
            if sid in ("mcti",):
                continue
            main_guess = f"{sid}/main_{sid.replace('-', '_')}.py"
            sources.append(
                mk(
                    sid,
                    sid.replace("_", " ").title(),
                    "editais_radar",
                    "instituicao_governo_internacional",
                    main_guess,
                    "config/source_readiness.json",
                    f"{sid}/outputs/; audit_reports_retransform/standardized/",
                    "public.edital → vw_editais_front",
                    status,
                    f"source_readiness.json → {bucket}",
                    None,
                    None,
                    None,
                    None,
                    None,
                    notes=f"Loader: scripts/load_ready_sources.py; {bucket}",
                )
            )

    totals: Dict[str, int] = {"sources": len(sources)}
    for row in sources:
        totals[row["status"]] = totals.get(row["status"], 0) + 1
    for k in ("aplicada", "pronta_para_apply", "implementada_latente", "precisa_melhoria", "nao_recomendado", "descoberta"):
        totals.setdefault(k, 0)

    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "totals": totals,
        "sources": sources,
        "meta": {
            "edital_readiness_counts": {b: len(sr.get(b, [])) for b in bucket_status},
            "news_research_config_count": len(nr_cfg["sources"]),
            "concursos_tracked_count": len(concursos_rows),
        },
    }
    (ROOT / "docs/BACKEND_SOURCES_INVENTORY.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
