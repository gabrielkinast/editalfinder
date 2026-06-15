"""
Consolidação cross-source pós-apply (Backend 10.3).

Somente leitura — não grava no banco.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from deadline_backfill import normalize_backfill_source
from opportunity_enricher import enrich_opportunity_record

CONSOLIDATION_VERSION = "post_apply_consolidation_10.3"

DEFAULT_SOURCES: Tuple[str, ...] = ("grants_gov", "doe_arpae", "bndes")

SOURCE_META: Dict[str, Dict[str, str]] = {
    "grants_gov": {
        "label": "Grants.gov",
        "apply_dir": "grants_deadline_apply",
        "recrawl_path": "recrawl/grants_gov/grants_gov_recrawl.json",
    },
    "doe_arpae": {
        "label": "DOE_ARPAE",
        "apply_dir": "doe_arpae_deadline_apply",
        "recrawl_path": "recrawl/doe_arpae/doe_arpae_recrawl.json",
    },
    "bndes": {
        "label": "BNDES",
        "apply_dir": "bndes_deadline_apply",
        "recrawl_path": "recrawl/bndes/bndes_recrawl.json",
    },
}

SOURCE_OBSERVATIONS: Dict[str, List[str]] = {
    "grants_gov": [
        "closeDate estruturado após apply controlado (151 updates).",
        "Apply grande já executado com 0 erros.",
        "Revisar oportunidades sem prazo remanescentes.",
    ],
    "doe_arpae": [
        "Ganho pequeno mas seguro (4 updates, 0 erros).",
        "Muitos NOFO TBD / detail / PDF ainda pendentes.",
    ],
    "bndes": [
        "1 prazo semanticamente limpo aplicado (FIP IA 2026).",
        "Páginas com resultado final não devem virar oportunidade aberta.",
        "Detail/PDF extraction funcionando; falsos positivos bloqueados.",
        "Algumas chamadas permanecem encerradas/pós-resultado.",
    ],
}

_RESULTADO_FINAL_RE = re.compile(r"resultado\s+final", re.I)


def _pct(n: int, total: int) -> str:
    if not total:
        return "0%"
    return f"{100 * n / total:.1f}%"


def supabase_configured() -> bool:
    try:
        import db  # noqa: WPS433

        return bool(getattr(db, "supabase", None))
    except Exception:
        return False


def read_apply_log(root: Path, source_key: str) -> Dict[str, Any]:
    """Lê apply_log.json; retorna unknown-safe dict se ausente."""
    apply_dir = SOURCE_META.get(source_key, {}).get("apply_dir", f"{source_key}_deadline_apply")
    path = root / "outputs" / apply_dir / "apply_log.json"
    unknown = {
        "source_key": source_key,
        "label": SOURCE_META.get(source_key, {}).get("label", source_key),
        "path": str(path),
        "status": "unknown",
        "ok": None,
        "errors": None,
        "total_candidates": None,
        "applied_at": None,
    }
    if not path.exists():
        return unknown
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {**unknown, "status": "read_error"}
    ok = int(data.get("ok") or 0)
    errors = int(data.get("errors") or 0)
    status = "ok" if errors == 0 and ok > 0 else ("partial" if ok > 0 else "empty")
    if errors > 0:
        status = "errors"
    return {
        "source_key": source_key,
        "label": SOURCE_META.get(source_key, {}).get("label", source_key),
        "path": str(path),
        "status": status,
        "ok": ok,
        "errors": errors,
        "skipped": int(data.get("skipped") or 0),
        "total_candidates": int(data.get("total_candidates") or 0),
        "applied_at": data.get("applied_at"),
        "version": data.get("version"),
        "log_sample": (data.get("log") or [])[:5],
    }


def read_dry_run_bundle(root: Path, source_key: str) -> Dict[str, Any]:
    apply_dir = SOURCE_META.get(source_key, {}).get("apply_dir", f"{source_key}_deadline_apply")
    base = root / "outputs" / apply_dir
    out: Dict[str, Any] = {"source_key": source_key, "base_path": str(base)}
    for name in ("report.json", "rejected.json", "no_deadline.json", "pdf_candidates.json"):
        path = base / name
        if not path.exists():
            out[name.replace(".json", "")] = None
            continue
        try:
            out[name.replace(".json", "")] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            out[name.replace(".json", "")] = None
    return out


def load_source_records(
    root: Path,
    source_key: str,
    *,
    from_db: bool = True,
    limit: Optional[int] = None,
) -> Tuple[List[Dict[str, Any]], str]:
    """
    Carrega registros da fonte.
    Retorna (records, data_origin).
    """
    if from_db and supabase_configured():
        try:
            from _backend_audit_io import iter_records_from_db, filter_records_by_source  # noqa: WPS433

            rows = list(iter_records_from_db(limit=limit))
            filtered = filter_records_by_source(rows, source_key)
            if filtered:
                return filtered, "database"
        except Exception:
            pass

    meta = SOURCE_META.get(source_key, {})
    recrawl_rel = meta.get("recrawl_path")
    if recrawl_rel:
        path = root / "outputs" / recrawl_rel
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            rows = raw if isinstance(raw, list) else raw.get("items") or []
            if limit:
                rows = rows[:limit]
            return rows, "recrawl_fallback"

    return [], "none"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _bndes_has_resultado_final(rec: Dict[str, Any]) -> bool:
    if normalize_backfill_source(rec) != "bndes":
        return False
    return bool(_RESULTADO_FINAL_RE.search(_record_blob(rec)))


def _record_blob(rec: Dict[str, Any]) -> str:
    ex = rec.get("extras") if isinstance(rec.get("extras"), dict) else {}
    parts = [
        str(rec.get("titulo") or ""),
        str(rec.get("descricao") or ""),
        str(ex.get("bndes_detail_text") or ""),
        str(ex.get("pdf_texto_extraido") or ""),
    ]
    return " ".join(parts).lower()


def _extras_sem_prazo_kind(rec: Dict[str, Any]) -> Optional[str]:
    ex = rec.get("extras") if isinstance(rec.get("extras"), dict) else {}
    return ex.get("sem_prazo_kind")


def _is_hidden_duplicate(rec: Dict[str, Any]) -> bool:
    """True se o registro foi marcado como duplicata oculta (Backend 10.3B)."""
    ex = rec.get("extras") if isinstance(rec.get("extras"), dict) else {}
    if not isinstance(ex, dict):
        return False
    cf = ex.get("curadoria_front")
    return bool(isinstance(cf, dict) and cf.get("hidden_duplicate") is True)


def _bndes_post_resultado(rec: Dict[str, Any], enr: Dict[str, Any]) -> bool:
    if normalize_backfill_source(rec) != "bndes":
        return False
    blob = _record_blob(rec)
    if not _RESULTADO_FINAL_RE.search(blob):
        return False
    vs = enr.get("validade_status")
    at = enr.get("actionability_type")
    return vs in ("aberto", "vencendo_7", "vencendo_30") or at in (
        "oportunidade_principal",
        "oportunidade_sem_prazo",
    )


def analyze_source_records(
    records: List[Dict[str, Any]],
    *,
    source_key: str,
    with_backfill: bool = True,
) -> Dict[str, Any]:
    total = len(records)
    actionable = 0
    oportunidade_principal = 0
    oportunidade_sem_prazo = 0
    noise_probable = 0
    portal_util = 0
    resultado_count = 0
    hidden_duplicates = 0
    hidden_duplicate_review: List[Dict[str, Any]] = []
    validade_c = Counter()
    prazo_status_c = Counter()
    quality_level_c = Counter()
    sem_prazo_kind_c = Counter()
    backfill_status_c = Counter()

    no_deadline_review: List[Dict[str, Any]] = []
    rejected_review: List[Dict[str, Any]] = []
    pdf_detail_review: List[Dict[str, Any]] = []
    manual_review: List[Dict[str, Any]] = []
    bndes_post_result_open: List[Dict[str, Any]] = []
    bndes_resultado_final: List[Dict[str, Any]] = []

    for rec in records:
        enr = enrich_opportunity_record(rec, with_deadline_backfill=with_backfill)
        vs = enr.get("validade_status") or "desconhecido"
        ps = enr.get("prazo_status") or "sem_prazo"
        at = enr.get("actionability_type") or "desconhecido"
        ex_sk = _extras_sem_prazo_kind(rec)
        validade_c[vs] += 1
        prazo_status_c[ps] += 1
        quality_level_c[enr.get("quality_level") or "revisao"] += 1
        ex_sk = _extras_sem_prazo_kind(rec)
        if enr.get("sem_prazo_kind"):
            sem_prazo_kind_c[enr.get("sem_prazo_kind")] += 1
        elif ex_sk:
            sem_prazo_kind_c[ex_sk] += 1
        if enr.get("deadline_backfill_status"):
            backfill_status_c[enr.get("deadline_backfill_status")] += 1

        if enr.get("is_actionable_opportunity"):
            actionable += 1
        if at == "oportunidade_principal":
            oportunidade_principal += 1
        if at == "oportunidade_sem_prazo":
            oportunidade_sem_prazo += 1
        if enr.get("is_noise"):
            noise_probable += 1
        if at == "portal_util":
            portal_util += 1
        if at == "resultado":
            resultado_count += 1
        if _is_hidden_duplicate(rec):
            hidden_duplicates += 1

        entry = {
            "id_edital": rec.get("id_edital"),
            "link": rec.get("link"),
            "titulo": (rec.get("titulo") or "")[:120],
            "validade_status": vs,
            "prazo_status": ps,
            "actionability_type": at,
            "sem_prazo_kind": enr.get("sem_prazo_kind"),
            "quality_level": enr.get("quality_level"),
            "is_noise": enr.get("is_noise"),
        }

        if vs == "sem_prazo" and enr.get("is_actionable_opportunity") and len(no_deadline_review) < 80:
            no_deadline_review.append(entry)

        sk = ex_sk if ex_sk == "deadline_in_pdf_or_detail" else (enr.get("sem_prazo_kind") or ex_sk)
        if sk == "deadline_in_pdf_or_detail" and len(pdf_detail_review) < 80:
            pdf_detail_review.append({**entry, "sem_prazo_kind": sk})

        if enr.get("deadline_backfill_status") == "rejected_deadline" and len(rejected_review) < 80:
            rejected_review.append({**entry, "reason": enr.get("deadline_reason")})

        if (
            enr.get("is_actionable_opportunity")
            and vs in ("aberto", "vencendo_7", "vencendo_30")
            and (enr.get("quality_level") == "revisao" or enr.get("prazo_confidence") in ("baixa", "nenhuma"))
            and len(manual_review) < 60
        ):
            manual_review.append(entry)

        if _bndes_has_resultado_final(rec) and len(bndes_resultado_final) < 40:
            bndes_resultado_final.append({**entry, "resultado_final_detected": True})

        if _bndes_post_resultado(rec, enr) and len(bndes_post_result_open) < 40:
            bndes_post_result_open.append(entry)

        if _is_hidden_duplicate(rec) and len(hidden_duplicate_review) < 200:
            cf = (rec.get("extras") or {}).get("curadoria_front") or {}
            hidden_duplicate_review.append(
                {
                    **entry,
                    "duplicate_of_id_edital": cf.get("duplicate_of_id_edital"),
                    "duplicate_reason": cf.get("duplicate_reason"),
                    "canonical_link": cf.get("canonical_link"),
                }
            )

    prazo_util = sum(
        validade_c.get(k, 0)
        for k in ("aberto", "vencendo_7", "vencendo_30", "encerrado")
    )

    return {
        "source_key": source_key,
        "label": SOURCE_META.get(source_key, {}).get("label", source_key),
        "total": total,
        "actionable": actionable,
        "oportunidade_principal": oportunidade_principal,
        "oportunidade_sem_prazo": oportunidade_sem_prazo,
        "com_prazo_util": prazo_util,
        "aberto": validade_c.get("aberto", 0),
        "vencendo_7": validade_c.get("vencendo_7", 0),
        "vencendo_30": validade_c.get("vencendo_30", 0),
        "encerrado": validade_c.get("encerrado", 0),
        "sem_prazo": validade_c.get("sem_prazo", 0),
        "nao_aplicavel": validade_c.get("nao_aplicavel", 0),
        "desconhecido": validade_c.get("desconhecido", 0),
        "noise_probable": noise_probable,
        "portal_util": portal_util,
        "resultado_actionability": resultado_count,
        "hidden_duplicates": hidden_duplicates,
        "validade_distribution": dict(validade_c),
        "prazo_status_distribution": dict(prazo_status_c),
        "quality_level_distribution": dict(quality_level_c),
        "sem_prazo_kind_distribution": dict(sem_prazo_kind_c),
        "deadline_backfill_status_distribution": dict(backfill_status_c),
        "observations": SOURCE_OBSERVATIONS.get(source_key, []),
        "bndes_post_resultado_still_open": bndes_post_result_open,
        "bndes_resultado_final_detected": bndes_resultado_final,
        "reviews": {
            "no_deadline": no_deadline_review,
            "rejected_or_blocked": rejected_review,
            "pdf_detail_candidates": pdf_detail_review,
            "manual_review": manual_review,
            "hidden_duplicates": hidden_duplicate_review,
        },
    }


def _sum_sources(metrics: List[Dict[str, Any]], key: str) -> int:
    return sum(int(m.get(key) or 0) for m in metrics)


def build_consolidated_metrics(
    source_metrics: List[Dict[str, Any]],
    apply_summaries: List[Dict[str, Any]],
    *,
    sources: List[str],
    data_origins: Dict[str, str],
) -> Dict[str, Any]:
    quality_merged: Counter = Counter()
    for sm in source_metrics:
        quality_merged.update(sm.get("quality_level_distribution") or {})

    return {
        "version": CONSOLIDATION_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources_analyzed": sources,
        "data_origins": data_origins,
        "totals": {
            "records": _sum_sources(source_metrics, "total"),
            "actionable": _sum_sources(source_metrics, "actionable"),
            "oportunidade_principal": _sum_sources(source_metrics, "oportunidade_principal"),
            "oportunidade_sem_prazo": _sum_sources(source_metrics, "oportunidade_sem_prazo"),
            "com_prazo_util": _sum_sources(source_metrics, "com_prazo_util"),
            "aberto": _sum_sources(source_metrics, "aberto"),
            "vencendo_7": _sum_sources(source_metrics, "vencendo_7"),
            "vencendo_30": _sum_sources(source_metrics, "vencendo_30"),
            "encerrado": _sum_sources(source_metrics, "encerrado"),
            "sem_prazo": _sum_sources(source_metrics, "sem_prazo"),
            "nao_aplicavel": _sum_sources(source_metrics, "nao_aplicavel"),
            "noise_probable": _sum_sources(source_metrics, "noise_probable"),
            "portal_util": _sum_sources(source_metrics, "portal_util"),
            "hidden_duplicates": _sum_sources(source_metrics, "hidden_duplicates"),
        },
        "quality_level_distribution": dict(quality_merged),
        "apply_summaries": apply_summaries,
        "semantic_notes": {
            "sem_prazo_not_noise": True,
            "encerrado_not_noise": True,
            "resultado_not_always_noise": True,
            "portal_util_not_error": True,
            "bndes_resultado_final_not_open_opportunity": True,
        },
    }


def build_next_actions(
    source_metrics: List[Dict[str, Any]],
    apply_summaries: List[Dict[str, Any]],
) -> str:
    lines = [
        "# Próximas ações — consolidação pós-apply (Backend 10.3)",
        "",
        "Gerado automaticamente. **Nenhum apply** foi executado por este relatório.",
        "",
    ]

    def section(title: str, items: List[str]) -> None:
        lines.append(f"### {title}")
        lines.append("")
        if items:
            for it in items:
                lines.append(f"- {it}")
        else:
            lines.append("- _(nenhum)_")
        lines.append("")

    apply_done: List[str] = []
    manual: List[str] = []
    detail_fetch: List[str] = []
    semantics: List[str] = []
    badges: List[str] = [
        "Aberto",
        "Vencendo 7 dias",
        "Vencendo 30 dias",
        "Encerrado",
        "Sem prazo informado",
        "Prazo em PDF/detalhe",
        "Chamada encerrada",
        "Resultado publicado",
        "Linha permanente",
    ]

    for ap in apply_summaries:
        if ap.get("status") == "ok" and (ap.get("errors") or 0) == 0:
            apply_done.append(
                f"**{ap.get('label')}**: {ap.get('ok')} updates aplicados, 0 erros "
                f"(`{ap.get('path', 'unknown')}`)"
            )

    for sm in source_metrics:
        label = sm.get("label") or sm.get("source_key")
        sk = sm.get("source_key")
        pdf_n = len(sm.get("reviews", {}).get("pdf_detail_candidates") or [])
        pdf_n += int((sm.get("sem_prazo_kind_distribution") or {}).get("deadline_in_pdf_or_detail", 0))
        if pdf_n:
            detail_fetch.append(f"**{label}**: {pdf_n} registros com `deadline_in_pdf_or_detail` na amostra.")
        manual_n = len(sm.get("reviews", {}).get("manual_review") or [])
        if manual_n:
            manual.append(f"**{label}**: {manual_n} oportunidades acionáveis com prazo ambíguo/baixa confiança.")
        if sk == "bndes":
            post_res = sm.get("bndes_post_resultado_still_open") or []
            resultado_n = len(sm.get("bndes_resultado_final_detected") or [])
            if post_res:
                semantics.append(
                    f"**BNDES**: {len(post_res)} registros com 'Resultado Final' ainda classificados como abertos "
                    "— revisar semântica pós-resultado."
                )
            elif resultado_n:
                semantics.append(
                    f"**BNDES**: {resultado_n} registros com 'Resultado Final' — "
                    "não promover como oportunidade aberta; usar badges pós-resultado."
                )
            else:
                semantics.append(
                    "**BNDES**: reforçar badges pós-resultado (Chamada encerrada / Resultado publicado)."
                )

    section("APPLY_DONE_OK", apply_done)
    section("NEEDS_MANUAL_REVIEW", manual)
    section("NEEDS_DETAIL_FETCH", detail_fetch)
    section("NEEDS_SOURCE_SEMANTICS", semantics)
    section("READY_FOR_FRONTEND_BADGES", badges)
    section(
        "SECURITY_NEXT",
        [
            "Recomendado avançar para **SECURITY 1.0A** quando backend estiver consolidado "
            "(auth, rate limits, secrets rotation).",
        ],
    )

    lines.extend(
        [
            "## Interpretação",
            "",
            "- `sem_prazo` **não** é ruído — pode ser oportunidade real sem deadline estruturado.",
            "- `encerrado` **não** é ruído — indica prazo conhecido já vencido.",
            "- `resultado` **não** é necessariamente ruído — documento auxiliar pós-edital.",
            "- `portal_util` **não** é erro — hub/navegação útil sem prazo.",
            "",
        ]
    )
    return "\n".join(lines)


def build_summary_md(
    consolidated: Dict[str, Any],
    source_metrics: List[Dict[str, Any]],
    apply_summaries: List[Dict[str, Any]],
) -> str:
    t = consolidated["totals"]
    lines = [
        "# Consolidação pós-apply — qualidade cross-source (Backend 10.3)",
        "",
        f"Gerado em: `{consolidated.get('generated_at')}`",
        "",
        "## Resumo geral",
        "",
        f"- Fontes analisadas: **{', '.join(consolidated.get('sources_analyzed') or [])}**",
        f"- Total de registros: **{t.get('records', 0)}**",
        f"- Oportunidades acionáveis: **{t.get('actionable', 0)}** ({_pct(t.get('actionable', 0), t.get('records', 0))})",
        f"- oportunidade_principal: **{t.get('oportunidade_principal', 0)}**",
        f"- oportunidade_sem_prazo: **{t.get('oportunidade_sem_prazo', 0)}**",
        f"- Com prazo útil: **{t.get('com_prazo_util', 0)}**",
        f"- Aberto: **{t.get('aberto', 0)}**",
        f"- Vencendo 7 dias: **{t.get('vencendo_7', 0)}**",
        f"- Vencendo 30 dias: **{t.get('vencendo_30', 0)}**",
        f"- Encerrado: **{t.get('encerrado', 0)}**",
        f"- sem_prazo: **{t.get('sem_prazo', 0)}**",
        f"- nao_aplicavel: **{t.get('nao_aplicavel', 0)}**",
        f"- Ruído provável (is_noise): **{t.get('noise_probable', 0)}**",
        f"- portal_util: **{t.get('portal_util', 0)}**",
        f"- Duplicatas ocultas (hidden_duplicate): **{t.get('hidden_duplicates', 0)}**",
        "",
        "### quality_level",
        "",
    ]
    for level, count in sorted((consolidated.get("quality_level_distribution") or {}).items()):
        lines.append(f"- {level}: **{count}**")

    lines.extend(["", "## Aplicações executadas", "", "| Fonte | Updates aplicados | Erros | Último apply log | Status |", "|------|-------------------|-------|------------------|--------|"])
    for ap in apply_summaries:
        ok = ap.get("ok")
        err = ap.get("errors")
        lines.append(
            f"| {ap.get('label')} | {ok if ok is not None else 'unknown'} | "
            f"{err if err is not None else 'unknown'} | `{ap.get('path', 'unknown')}` | {ap.get('status', 'unknown')} |"
        )

    lines.extend(
        [
            "",
            "## Semântica (não confundir)",
            "",
            "- **sem_prazo** ≠ ruído — oportunidade pode existir sem deadline no registro.",
            "- **encerrado** ≠ ruído — prazo conhecido já vencido.",
            "- **resultado** ≠ ruído automático — documento pós-edital.",
            "- **portal_util** ≠ erro — navegação útil.",
            "- **BNDES** com Resultado Final divulgado **não** deve aparecer como oportunidade aberta.",
            "",
        ]
    )

    origins = consolidated.get("data_origins") or {}
    if any(v != "database" for v in origins.values()):
        lines.extend(
            [
                "## Limitação de dados",
                "",
                "Métricas de registros podem vir de recrawl fallback (Supabase indisponível):",
                "",
            ]
        )
        for sk, origin in origins.items():
            lines.append(f"- `{sk}`: **{origin}**")
        lines.append("")

    for sm in source_metrics:
        label = sm.get("label") or sm.get("source_key")
        lines.extend(
            [
                f"## {label}",
                "",
                f"- Total analisado: **{sm.get('total', 0)}** (origem: `{origins.get(sm.get('source_key'), '?')}`)",
                f"- Oportunidades acionáveis: **{sm.get('actionable', 0)}**",
                f"- oportunidade_principal: **{sm.get('oportunidade_principal', 0)}**",
                f"- oportunidade_sem_prazo: **{sm.get('oportunidade_sem_prazo', 0)}**",
                f"- Aberto: **{sm.get('aberto', 0)}** | vencendo_7: **{sm.get('vencendo_7', 0)}** | "
                f"vencendo_30: **{sm.get('vencendo_30', 0)}** | encerrado: **{sm.get('encerrado', 0)}**",
                f"- sem_prazo: **{sm.get('sem_prazo', 0)}** | nao_aplicavel: **{sm.get('nao_aplicavel', 0)}**",
                f"- Ruído provável: **{sm.get('noise_probable', 0)}**",
                f"- portal_util: **{sm.get('portal_util', 0)}** | resultado (actionability): **{sm.get('resultado_actionability', 0)}**",
                "",
                "**Observações:**",
            ]
        )
        for obs in sm.get("observations") or []:
            lines.append(f"- {obs}")
        lines.append("")

    return "\n".join(lines)


def run_post_apply_consolidation(
    root: Path,
    *,
    sources: Optional[List[str]] = None,
    from_db: bool = True,
    with_backfill: bool = True,
    limit: Optional[int] = 1000,
    output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Executa consolidação completa (somente leitura)."""
    srcs = list(sources or DEFAULT_SOURCES)
    out_dir = output_dir or (root / "outputs" / "post_apply_consolidation")
    out_dir.mkdir(parents=True, exist_ok=True)

    source_metrics: List[Dict[str, Any]] = []
    data_origins: Dict[str, str] = {}
    apply_summaries = [read_apply_log(root, sk) for sk in srcs]

    all_no_deadline: List[Dict[str, Any]] = []
    all_rejected: List[Dict[str, Any]] = []
    all_pdf: List[Dict[str, Any]] = []
    all_hidden_duplicates: List[Dict[str, Any]] = []

    for sk in srcs:
        records, origin = load_source_records(root, sk, from_db=from_db, limit=limit)
        data_origins[sk] = origin
        sm = analyze_source_records(records, source_key=sk, with_backfill=with_backfill)
        sm["data_origin"] = origin
        sm["record_count_loaded"] = len(records)
        source_metrics.append(sm)

        dry = read_dry_run_bundle(root, sk)
        sm["dry_run_stats"] = (dry.get("report") or {}).get("stats")
        for item in sm.get("reviews", {}).get("no_deadline") or []:
            item["source_key"] = sk
            all_no_deadline.append(item)
        for item in sm.get("reviews", {}).get("rejected_or_blocked") or []:
            item["source_key"] = sk
            all_rejected.append(item)
        for item in sm.get("reviews", {}).get("pdf_detail_candidates") or []:
            item["source_key"] = sk
            all_pdf.append(item)
        for item in sm.get("reviews", {}).get("hidden_duplicates") or []:
            item["source_key"] = sk
            all_hidden_duplicates.append(item)

        if dry.get("rejected") and isinstance(dry["rejected"], list):
            for item in dry["rejected"][:30]:
                all_rejected.append(
                    {
                        "source_key": sk,
                        "link": item.get("link"),
                        "titulo": item.get("titulo"),
                        "action": item.get("action"),
                        "meta": item.get("meta"),
                        "origin": "dry_run_rejected.json",
                    }
                )

    consolidated = build_consolidated_metrics(
        source_metrics, apply_summaries, sources=srcs, data_origins=data_origins
    )

    deadline_by_source = {
        sm["source_key"]: {
            "validade_distribution": sm.get("validade_distribution"),
            "prazo_status_distribution": sm.get("prazo_status_distribution"),
            "aberto": sm.get("aberto"),
            "vencendo_7": sm.get("vencendo_7"),
            "vencendo_30": sm.get("vencendo_30"),
            "encerrado": sm.get("encerrado"),
            "sem_prazo": sm.get("sem_prazo"),
        }
        for sm in source_metrics
    }

    actionability_by_source = {
        sm["source_key"]: {
            "actionable": sm.get("actionable"),
            "oportunidade_principal": sm.get("oportunidade_principal"),
            "oportunidade_sem_prazo": sm.get("oportunidade_sem_prazo"),
            "noise_probable": sm.get("noise_probable"),
            "portal_util": sm.get("portal_util"),
            "resultado_actionability": sm.get("resultado_actionability"),
            "quality_level_distribution": sm.get("quality_level_distribution"),
        }
        for sm in source_metrics
    }

    source_breakdown = {sm["source_key"]: sm for sm in source_metrics}
    next_actions = build_next_actions(source_metrics, apply_summaries)
    summary_md = build_summary_md(consolidated, source_metrics, apply_summaries)

    _write_md(out_dir / "summary.md", summary_md)
    _write_json(out_dir / "consolidated_metrics.json", consolidated)
    _write_json(out_dir / "source_breakdown.json", source_breakdown)
    _write_json(out_dir / "deadline_status_by_source.json", deadline_by_source)
    _write_json(out_dir / "actionability_by_source.json", actionability_by_source)
    _write_json(out_dir / "no_deadline_review.json", all_no_deadline[:200])
    _write_json(out_dir / "rejected_or_blocked_review.json", all_rejected[:200])
    _write_json(out_dir / "pdf_detail_candidates_review.json", all_pdf[:200])
    _write_json(out_dir / "hidden_duplicates_review.json", all_hidden_duplicates[:200])
    _write_json(out_dir / "applied_updates_summary.json", apply_summaries)
    _write_md(out_dir / "next_actions.md", next_actions)

    return {
        "output_dir": str(out_dir),
        "consolidated": consolidated,
        "source_metrics": source_metrics,
        "apply_summaries": apply_summaries,
    }
