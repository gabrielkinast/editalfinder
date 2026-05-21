#!/usr/bin/env python3
"""
Dry-run de roteamento news/research → public.noticia / public.pesquisa (sem DB, sem apply).

Deduplica por link antes das métricas finais. review_for_edital só com sinais fortes em título ou URL.
Não importa loader/db: evita Supabase.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from content_routing import infer_content_type  # noqa: E402

DEFAULT_INPUT = ROOT / "audit_reports_news_research" / "standardized"
DEFAULT_OUT = ROOT / "audit_reports_news_research_loader"

NOTICIA_FIELDS: Tuple[str, ...] = (
    "titulo",
    "resumo",
    "link",
    "fonte",
    "fonte_recurso",
    "data_publicacao",
    "pais",
    "regiao",
    "idioma_original",
    "tipo_conteudo",
    "area_cientifica",
    "area_tecnologica",
    "setor_estrategico",
    "tags",
    "extras",
    "qualidade_dado",
    "validacao_status",
)

PESQUISA_FIELDS: Tuple[str, ...] = (
    "titulo",
    "descricao",
    "link",
    "fonte_recurso",
    "data_publicacao",
    "tipo_pesquisa",
    "area_cientifica",
    "area_tecnologica",
    "setor_estrategico",
    "documentos",
    "pdf_url",
    "idioma_original",
    "pais",
    "regiao",
    "tags",
    "extras",
    "qualidade_dado",
    "validacao_status",
)

# Frases fortes (título ou URL). Não usar "request" isolado.
_STRONG_TITLE_URL_PHRASES: Tuple[str, ...] = (
    "solicitation",
    "broad agency announcement",
    "proposers day",
    "funding opportunity",
    "research opportunity",
    "call for proposals",
    "notice of funding",
    "notice of funding opportunity",
)

_STRONG_TITLE_URL_REGEX: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\bbaa\b", re.I),
    re.compile(r"\brfp\b", re.I),
    re.compile(r"\brfi\b", re.I),
    re.compile(r"\bnofo\b", re.I),
    re.compile(r"request\s+for\s+proposals", re.I),
    re.compile(r"request\s+for\s+information", re.I),
)

# IAEA: oportunidades acionáveis (não carregar como notícia/pesquisa; revisão humana)
_IAEA_ACTIONABLE_PHRASES: Tuple[str, ...] = (
    "call for applications",
    "call for papers",
    "call for submissions",
    "call for proposals",
    "apply by ",
    "deadline:",
    "funding opportunity",
    "vacancies at the iaea",
    "vacancy at the iaea",
    "internship programme",
    "internship program",
    "request for expressions of interest",
    "expression of interest",
)


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_date(v: Any) -> Optional[datetime]:
    if not v:
        return None
    s = str(v).strip()
    if not s:
        return None
    for p in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            dt = datetime.strptime(s[:19], p)
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def _strip_html(text: Any, max_len: int = 2800) -> str:
    if text is None:
        return ""
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", str(text))
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if max_len and len(t) > max_len:
        t = t[: max_len - 1].rsplit(" ", 1)[0] + "…"
    return t


def _extras(item: Dict[str, Any]) -> Dict[str, Any]:
    ex = item.get("extras")
    return ex if isinstance(ex, dict) else {}


def _summary_blob(item: Dict[str, Any]) -> str:
    ex = _extras(item)
    return _strip_html(
        item.get("resumo") or item.get("descricao") or ex.get("descricao_original") or "",
        max_len=3000,
    )


def _missing_summary_flag(item: Dict[str, Any]) -> bool:
    ex = _extras(item)
    if "missing_summary" in ex:
        return bool(ex.get("missing_summary"))
    return len(_summary_blob(item)) < 40


def _is_generic(item: Dict[str, Any]) -> bool:
    lk = str(item.get("link") or "").lower()
    title = str(item.get("titulo") or "").strip().lower()
    if any(x in lk for x in ("/about", "/contact", "/privacy", "/terms", "/login", "/careers", "/jobs")):
        return True
    if title in ("home", "news", "publications", "nasa", "darpa", "iaea", "eurekalert", "programs"):
        return True
    if lk.rstrip("/") in (
        "https://www.darpa.mil/work-with-us/opportunities",
        "https://www.darpa.mil/research/programs",
    ):
        return True
    return False


def _iaea_actionable_opportunity(item: Dict[str, Any]) -> bool:
    blob = f"{item.get('titulo','')} {item.get('link','')}".lower()
    return any(p in blob for p in _IAEA_ACTIONABLE_PHRASES)


def _strong_edital_title_url(item: Dict[str, Any]) -> bool:
    """Sinal forte apenas em título ou URL (evita falso positivo por corpo/notícia)."""
    tit = str(item.get("titulo") or "")
    url = str(item.get("link") or "")
    blob = f"{tit} {url}".lower()
    if any(p in blob for p in _STRONG_TITLE_URL_PHRASES):
        return True
    comb = f"{tit} {url}"
    for rx in _STRONG_TITLE_URL_REGEX:
        if rx.search(comb):
            return True
    return False


def _infer_legacy_table(item: Dict[str, Any]) -> str:
    try:
        return infer_content_type(item)
    except Exception:
        return "desconhecido"


def route_item(source_id: str, item: Dict[str, Any]) -> Tuple[str, str]:
    """
    Retorna (routing_decision, motivo_curto).
    routing_decision: noticia | pesquisa | review_for_edital | rejected_noise
    """
    link = str(item.get("link") or "").strip()
    tit = str(item.get("titulo") or "").strip()

    if not link.startswith("http") or len(tit) < 3:
        return "rejected_noise", "link_invalido_ou_titulo_curto"
    if _is_generic(item):
        return "rejected_noise", "conteudo_generico_ou_hub"

    tipo = str(item.get("tipo_conteudo") or "").strip().lower()
    legacy = _infer_legacy_table(item)

    if source_id == "iaea_news_publications" and _iaea_actionable_opportunity(item):
        return "review_for_edital", "iaea_oportunidade_acionavel_titulo_ou_url"

    if _strong_edital_title_url(item):
        return "review_for_edital", "sinal_forte_titulo_ou_url"

    if source_id == "iaea_news_publications":
        if tipo == "pesquisa":
            return "pesquisa", "iaea_tipo_conteudo_pesquisa_ou_seed_publications"
        return "noticia", "iaea_tipo_conteudo_noticia_ou_seed_news"

    if source_id == "eurekalert_science_filtered":
        if tipo == "pesquisa":
            return "pesquisa", "eurekalert_tipo_conteudo_pesquisa"
        return "noticia", "eurekalert_tipo_conteudo_noticia"

    if source_id in ("brisa_artigos", "defesanet", "brisa_news", "exercito_brasileiro", "softex_noticias"):
        if source_id == "brisa_artigos":
            return "pesquisa", "brisa_artigos_feed_pesquisa"
        return "noticia", f"{source_id}_noticias_estrategicas"

    if source_id == "darpa_news":
        return "noticia", "darpa_news_somente_public_noticia"

    if source_id == "nasa_news":
        if tipo == "pesquisa":
            return "pesquisa", "tipo_conteudo_pesquisa_fonte_news"
        return "noticia", "tipo_conteudo_noticia_ou_default_news"

    if source_id == "darpa_opportunities_research":
        return "review_for_edital", "darpa_opportunity_rss_nao_auto_edital"

    if source_id == "darpa_programs_research":
        return "pesquisa", "darpa_program_catalogo_sitemap"

    if legacy == "edital":
        if tipo == "pesquisa":
            return "pesquisa", "infer_edital_sem_sinal_forte_para_pesquisa"
        return "noticia", "infer_edital_sem_sinal_forte_para_noticia"

    if tipo == "pesquisa":
        return "pesquisa", "tipo_conteudo_pesquisa"
    if tipo == "noticia":
        return "noticia", "tipo_conteudo_noticia"
    return "pesquisa", "fallback_pesquisa"


def _field_present(item: Dict[str, Any], key: str) -> bool:
    ex = _extras(item)
    if key == "extras":
        return bool(ex)
    array_keys = frozenset({"area_cientifica", "area_tecnologica", "setor_estrategico", "tags", "documentos"})
    if key in item:
        v = item.get(key)
        if isinstance(v, (list, tuple, set)) and key in array_keys:
            return True
        if v not in (None, "", [], {}):
            return True
    if key in ex:
        v = ex.get(key)
        if isinstance(v, (list, tuple, set)) and key in array_keys:
            return True
        if v not in (None, "", [], {}):
            return True
    if key == "fonte_recurso" and item.get("fonte"):
        return True
    if key == "descricao" and (item.get("descricao") or item.get("resumo")):
        return True
    if key == "resumo" and (item.get("resumo") or item.get("descricao")):
        return True
    if key == "tipo_pesquisa" and item.get("tipo_pesquisa"):
        return True
    if key == "idioma_original" and (item.get("idioma_original") or ex.get("idioma_original")):
        return True
    return False


def _validate_arrays(item: Dict[str, Any]) -> List[str]:
    problems: List[str] = []
    for k in ("area_cientifica", "area_tecnologica", "setor_estrategico", "tags"):
        v = item.get(k)
        if v is None:
            continue
        if isinstance(v, str):
            problems.append(f"{k}_deveria_ser_lista_recebeu_str")
        elif isinstance(v, (list, tuple, set)):
            for el in v:
                if not isinstance(el, (str, int, float)) and el is not None:
                    problems.append(f"{k}_elemento_nao_escalar")
        else:
            problems.append(f"{k}_tipo_inesperado_{type(v).__name__}")
    return problems


def _missing_fields(item: Dict[str, Any], fields: Sequence[str]) -> List[str]:
    return [f for f in fields if not _field_present(item, f)]


def _load_standardized(std_dir: Path) -> List[Tuple[str, Dict[str, Any]]]:
    out: List[Tuple[str, Dict[str, Any]]] = []
    for p in sorted(std_dir.glob("*_standardized.json")):
        src = p.name.replace("_standardized.json", "")
        data = _load_json(p, [])
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            continue
        for it in data:
            if isinstance(it, dict):
                out.append((src, it))
    return out


def _dedupe_sort_key(order: int, source_id: str, item: Dict[str, Any]) -> Tuple[Any, ...]:
    has_date = 1 if _parse_date(item.get("data_publicacao")) else 0
    body = _summary_blob(item)
    text_len = min(len(body), 5000)
    tipo = str(item.get("tipo_conteudo") or "").lower()
    tipo_rank = 2 if tipo == "pesquisa" else (1 if tipo == "noticia" else 0)
    comp = sum(
        1
        for k in ("titulo", "fonte", "fonte_recurso", "data_publicacao", "tipo_conteudo", "validacao_status")
        if _field_present(item, k) or (k == "fonte_recurso" and item.get("fonte"))
    )
    if body:
        comp += 1
    q = int(item.get("qualidade_dado") or 0)
    return (has_date, text_len, comp, tipo_rank, q, -order)


def _dedupe_by_link(
    rows: List[Tuple[str, Dict[str, Any]]],
) -> Tuple[List[Tuple[str, Dict[str, Any]]], List[Dict[str, Any]]]:
    """Mantém um item por link: maior completude, data, texto, tipo mais específico."""
    by_link: Dict[str, List[Tuple[int, str, Dict[str, Any]]]] = defaultdict(list)
    for order, (sid, it) in enumerate(rows):
        lk = str(it.get("link") or "").strip() or f"__empty_{order}"
        by_link[lk].append((order, sid, it))

    kept: List[Tuple[str, Dict[str, Any]]] = []
    removed: List[Dict[str, Any]] = []
    for lk, group in sorted(by_link.items()):
        winner = max(group, key=lambda t: _dedupe_sort_key(t[0], t[1], t[2]))
        w_order, w_sid, w_it = winner
        w_key = _dedupe_sort_key(w_order, w_sid, w_it)
        for order, sid, it in group:
            if (order, sid, it) == winner:
                continue
            r_key = _dedupe_sort_key(order, sid, it)
            removed.append(
                {
                    "link": lk,
                    "mantido_source_id": w_sid,
                    "removido_source_id": sid,
                    "mantido_titulo": w_it.get("titulo"),
                    "removido_titulo": it.get("titulo"),
                    "mantido_scores": list(w_key),
                    "removido_scores": list(r_key),
                    "motivo": "dedupe_mesmo_link_menor_prioridade",
                }
            )
        kept.append((w_sid, w_it))
    return kept, removed


def _readiness_apply_future(
    sid: str,
    stats: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Critérios antes de apply futuro (nenhum item a public.edital neste módulo).
    Retorna (ok, motivo).
    """
    t = int(stats.get("total", 0))
    if t < 5:
        return False, "volume_baixo"
    if int(stats.get("rejected_noise", 0)) / t > 0.12:
        return False, "ruido_alto"
    if int(stats.get("review_for_edital", 0)) / t > 0.08:
        return False, "muitos_review_for_edital"
    if int(stats.get("sem_data", 0)) / t > 0.45:
        return False, "maioria_sem_data"
    if int(stats.get("missing_summary", 0)) / t > 0.45:
        return False, "maioria_sem_resumo"
    if int(stats.get("missing_fields_total", 0)) / t > 0.35:
        return False, "muitos_missing_fields"
    return True, "criterios_minimos_ok"


def _activation_waves(by_source: Dict[str, Any], summary_counts: Dict[str, Any]) -> Dict[str, Any]:
    waves = {
        "onda_1": ["nasa_news"],
        "onda_2": ["darpa_news"],
        "onda_3": ["darpa_opportunities_research"],
        "pendentes": [],
        "preparacao_iaea_wave1": ["iaea_news_publications"],
        "preparacao_eurekalert_wave1": ["eurekalert_science_filtered"],
    }
    notes: Dict[str, str] = {}
    nasa = by_source.get("nasa_news") or {}
    ok_nasa, why = _readiness_apply_future("nasa_news", nasa)
    if nasa.get("total", 0) == 0:
        notes["nasa_news"] = "sem_itens"
    elif ok_nasa:
        notes["nasa_news"] = "candidata_onda_1_criterios_apply_futuro_ok"
    else:
        notes["nasa_news"] = f"precisa_limpeza_{why}"

    notes["darpa_news"] = "onda_2_apos_reduzir_ruido_e_sem_data"
    notes["darpa_opportunities_research"] = "onda_3_apos_politica_pesquisa_vs_edital"
    notes["iaea_news_publications"] = "wave1: crawl + build_iaea_wave1_payloads + load --dry-run --wave iaea_wave1 (sem apply)"
    notes["eurekalert_science_filtered"] = (
        "wave1: crawl + build_eurekalert_wave1_payloads + generate_eurekalert_wave1_diagnostico "
        "+ load --dry-run --wave eurekalert_wave1 (sem apply; WAF pode bloquear bots)"
    )

    return {"waves": waves, "notas_por_fonte": notes, "totais_globais": summary_counts}


def main() -> int:
    ap = argparse.ArgumentParser(description="Dry-run roteamento news/research → noticia/pesquisa (sem DB).")
    ap.add_argument("--input-dir", default=str(DEFAULT_INPUT))
    ap.add_argument("--output-dir", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    std_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows_raw = _load_standardized(std_dir)
    total_before_dedupe = len(rows_raw)
    rows, removed_dupes = _dedupe_by_link(rows_raw)
    deduplicated_total = len(removed_dupes)

    cutoff = datetime.now(timezone.utc) - timedelta(days=365)

    processed: List[Dict[str, Any]] = []
    for source_id, item in rows:
        link = str(item.get("link") or "").strip()
        dt = _parse_date(item.get("data_publicacao"))

        routing, motivo = route_item(source_id, item)
        candidate_edital = routing == "review_for_edital"
        sem_data = dt is None
        missing_sum = _missing_summary_flag(item)
        review_missing_date = routing == "noticia" and sem_data
        pesquisa_sem_data = routing == "pesquisa" and sem_data

        array_issues = _validate_arrays(item)
        if routing == "noticia":
            missing = _missing_fields(item, NOTICIA_FIELDS)
        elif routing == "pesquisa":
            missing = _missing_fields(item, PESQUISA_FIELDS)
        elif routing == "review_for_edital":
            missing = _missing_fields(item, NOTICIA_FIELDS + ("descricao", "tipo_pesquisa", "documentos", "pdf_url"))
        else:
            missing = []

        processed.append(
            {
                "source_id": source_id,
                "link": link,
                "titulo": item.get("titulo"),
                "data_publicacao": item.get("data_publicacao"),
                "routing_decision": routing,
                "routing_motivo": motivo,
                "sem_data": sem_data,
                "fora_12_meses": dt is not None and dt < cutoff,
                "missing_summary": missing_sum,
                "review_missing_date": review_missing_date,
                "pesquisa_sem_data": pesquisa_sem_data,
                "candidate_for_edital": candidate_edital,
                "requires_manual_review": candidate_edital,
                "infer_content_type_legacy": _infer_legacy_table(item),
                "missing_fields": missing,
                "array_field_issues": array_issues,
            }
        )

    c = Counter(p["routing_decision"] for p in processed)
    total = len(processed)

    by_dest = {
        "public.noticia": int(c.get("noticia", 0)),
        "public.pesquisa": int(c.get("pesquisa", 0)),
        "review_for_edital": int(c.get("review_for_edital", 0)),
        "rejected_noise": int(c.get("rejected_noise", 0)),
    }

    missing_date_total = sum(1 for p in processed if p["sem_data"])
    review_missing_date_total = sum(1 for p in processed if p["review_missing_date"])
    missing_summary_total = sum(1 for p in processed if p["missing_summary"])

    by_source: Dict[str, Dict[str, Any]] = {}
    dup_pre_dedupe_by_source = Counter(sid for sid, _ in rows_raw)
    # duplicados removidos por fonte
    removed_by_source = Counter(r["removido_source_id"] for r in removed_dupes)

    for p in processed:
        sid = p["source_id"]
        if sid not in by_source:
            by_source[sid] = {
                "source_id": sid,
                "total": 0,
                "noticia": 0,
                "pesquisa": 0,
                "review_for_edital": 0,
                "rejected_noise": 0,
                "sem_data": 0,
                "fora_12_meses": 0,
                "missing_summary": 0,
                "review_missing_date": 0,
                "pesquisa_sem_data": 0,
                "missing_fields_total": 0,
                "array_issues_total": 0,
                "dedupe_removidos_destino_fonte": int(removed_by_source.get(sid, 0)),
            }
        b = by_source[sid]
        b["total"] += 1
        b[p["routing_decision"]] = b.get(p["routing_decision"], 0) + 1
        if p["sem_data"]:
            b["sem_data"] += 1
        if p["fora_12_meses"]:
            b["fora_12_meses"] += 1
        if p["missing_summary"]:
            b["missing_summary"] += 1
        if p["review_missing_date"]:
            b["review_missing_date"] += 1
        if p["pesquisa_sem_data"]:
            b["pesquisa_sem_data"] += 1
        if p["missing_fields"]:
            b["missing_fields_total"] += 1
        if p["array_field_issues"]:
            b["array_issues_total"] += 1

    for sid in list(by_source.keys()):
        raw_c = int(dup_pre_dedupe_by_source[sid])
        kept_c = int(by_source[sid]["total"])
        by_source[sid]["linhas_pre_dedupe"] = raw_c
        by_source[sid]["linhas_removidas_no_dedupe"] = max(0, raw_c - kept_c)

    by_source_list = list(by_source.values())
    readiness: Dict[str, Any] = {}
    for sid, b in sorted(by_source.items()):
        ok, why = _readiness_apply_future(sid, b)
        readiness[sid] = {"apply_futuro_ok": ok, "motivo": why}

    review_candidates = [
        {
            **{k: p[k] for k in ("source_id", "link", "titulo", "data_publicacao", "routing_motivo")},
            "routing_decision": "review_for_edital",
            "candidate_for_edital": True,
            "requires_manual_review": True,
            "infer_content_type_legacy": p["infer_content_type_legacy"],
            "missing_fields": p["missing_fields"],
        }
        for p in processed
        if p["routing_decision"] == "review_for_edital"
    ]

    examples: Dict[str, Any] = {"por_destino": defaultdict(list), "por_fonte": defaultdict(list)}
    for p in processed:
        if len(examples["por_destino"][p["routing_decision"]]) < 12:
            examples["por_destino"][p["routing_decision"]].append(
                {
                    k: p[k]
                    for k in (
                        "source_id",
                        "titulo",
                        "link",
                        "routing_motivo",
                        "missing_summary",
                        "review_missing_date",
                    )
                }
            )
        if len(examples["por_fonte"][p["source_id"]]) < 8:
            examples["por_fonte"][p["source_id"]].append(
                {k: p[k] for k in ("routing_decision", "titulo", "link", "routing_motivo", "sem_data")}
            )

    examples_out = {
        "por_destino": {k: v for k, v in examples["por_destino"].items()},
        "por_fonte": {k: v for k, v in examples["por_fonte"].items()},
    }

    dedup_report = {
        "data": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_antes_dedupe": total_before_dedupe,
        "total_depois_dedupe": total,
        "deduplicated_total": deduplicated_total,
        "regra": "mesmo_link_maior_completude_data_resumo_tipo",
        "removidos": removed_dupes,
    }
    (out_dir / "dedup_report.json").write_text(
        json.dumps(dedup_report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    dedup_md = [
        "# Deduplicação por link (news/research dry-run)",
        "",
        f"- Itens antes: **{total_before_dedupe}**",
        f"- Itens depois: **{total}**",
        f"- Removidos (duplicata): **{deduplicated_total}**",
        "",
        "## Amostra de removidos (até 30)",
        "",
        "```json",
        json.dumps(removed_dupes[:30], ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    (out_dir / "dedup_report.md").write_text("\n".join(dedup_md), encoding="utf-8")

    ajustes_pre_apply = [
        "Reexecutar crawler após melhorias de RSS/HTML para datas e resumos.",
        "Itens noticia com review_missing_date: corrigir data na fonte antes do apply.",
        "Itens com missing_summary: enriquecer só a partir de HTML/RSS real (sem invenção).",
        "Manter dedupe por link no job de carga dedicado.",
        "Auditoria manual apenas para review_for_edital; nunca public.edital automático neste módulo.",
    ]

    recomendacao_por_fonte: Dict[str, str] = {}
    for sid, b in sorted(by_source.items()):
        ok, why = _readiness_apply_future(sid, b)
        if b.get("total", 0) == 0:
            recomendacao_por_fonte[sid] = "sem_dados"
        elif ok and sid == "nasa_news":
            recomendacao_por_fonte[sid] = "OK_onda_1_apply_futuro_se_staging_validado"
        elif sid == "nasa_news":
            recomendacao_por_fonte[sid] = f"onda_1_mas_precisa_limpeza_{why}"
        elif sid == "darpa_news":
            recomendacao_por_fonte[sid] = "onda_2_apos_limpeza"
        elif sid == "darpa_opportunities_research":
            recomendacao_por_fonte[sid] = "onda_3_politica_edital"
        else:
            recomendacao_por_fonte[sid] = "pendente_crawler"

    summary = {
        "data_dry_run": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_dir": str(std_dir.resolve()),
        "output_dir": str(out_dir.resolve()),
        "modo": "dry_run_sem_supabase_sem_apply_com_dedupe",
        "total_itens_antes_dedupe": total_before_dedupe,
        "total_itens_depois_dedupe": total,
        "deduplicated_total": deduplicated_total,
        "por_destino_simulado": by_dest,
        "missing_date_total": missing_date_total,
        "review_missing_date_total": review_missing_date_total,
        "missing_summary_total": missing_summary_total,
        "review_for_edital_total": by_dest["review_for_edital"],
        "rejected_noise_total": by_dest["rejected_noise"],
        "fora_ultimos_12_meses": sum(1 for p in processed if p["fora_12_meses"]),
        "itens_com_missing_fields": sum(1 for p in processed if p["missing_fields"]),
        "itens_com_array_issues": sum(1 for p in processed if p["array_field_issues"]),
        "campos_noticia_validados": list(NOTICIA_FIELDS),
        "campos_pesquisa_validados": list(PESQUISA_FIELDS),
        "recomendacao_por_fonte": recomendacao_por_fonte,
        "readiness_apply_futuro": readiness,
        "ajustes_necessarios_pre_apply": ajustes_pre_apply,
        "plano_ativacao": _activation_waves(
            by_source,
            {
                "total_antes_dedupe": total_before_dedupe,
                "total_depois_dedupe": total,
                "deduplicated_total": deduplicated_total,
                **by_dest,
                "missing_date_total": missing_date_total,
                "review_missing_date_total": review_missing_date_total,
                "missing_summary_total": missing_summary_total,
            },
        ),
    }

    (out_dir / "dry_run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "by_destination.json").write_text(json.dumps(by_dest, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "by_source.json").write_text(json.dumps(by_source_list, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "examples.json").write_text(json.dumps(examples_out, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "review_candidates.json").write_text(
        json.dumps(review_candidates, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md_lines = [
        "# Dry-run news/research → noticia / pesquisa",
        "",
        f"- Gerado em: `{summary['data_dry_run']}`",
        f"- Entrada: `{summary['input_dir']}`",
        f"- **Sem Supabase**, sem apply. Deduplicação por link antes das métricas.",
        "",
        "## Totais",
        "",
        f"- Itens antes dedupe: **{total_before_dedupe}**",
        f"- Itens depois dedupe: **{total}**",
        f"- **deduplicated_total**: **{deduplicated_total}**",
        f"- Simulado `public.noticia`: **{by_dest['public.noticia']}**",
        f"- Simulado `public.pesquisa`: **{by_dest['public.pesquisa']}**",
        f"- **review_for_edital_total**: **{by_dest['review_for_edital']}** (só sinal forte em título/URL)",
        f"- **rejected_noise_total**: **{by_dest['rejected_noise']}**",
        f"- **missing_date_total**: **{missing_date_total}**",
        f"- **review_missing_date_total** (notícia sem data): **{review_missing_date_total}**",
        f"- **missing_summary_total**: **{missing_summary_total}**",
        f"- Fora dos últimos 12 meses: **{summary['fora_ultimos_12_meses']}**",
        "",
        "## Qualidade",
        "",
        f"- Itens com campos faltantes: **{summary['itens_com_missing_fields']}**",
        f"- Arrays mal tipados: **{summary['itens_com_array_issues']}**",
        "",
        "## Readiness apply futuro (por fonte)",
        "",
        "```json",
        json.dumps(readiness, ensure_ascii=False, indent=2),
        "```",
        "",
        "## NASA Onda 1",
        "",
        f"- **nasa_news**: `{readiness.get('nasa_news', {})}`",
        "",
        "## Por fonte",
        "",
        "```json",
        json.dumps(by_source_list, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Plano por ondas",
        "",
        "```json",
        json.dumps(summary["plano_ativacao"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Recomendação por fonte",
        "",
        "\n".join(f"- **{k}**: {v}" for k, v in sorted(recomendacao_por_fonte.items())),
        "",
        "## Ajustes antes de qualquer apply",
        "",
        "\n".join(f"- {x}" for x in ajustes_pre_apply),
        "",
        "## Dedupe",
        "",
        f"- Ver `dedup_report.json` / `dedup_report.md` ({deduplicated_total} removidos).",
        "",
    ]
    (out_dir / "dry_run_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "output_dir": str(out_dir),
                "total_antes_dedupe": total_before_dedupe,
                "total_depois_dedupe": total,
                "deduplicated_total": deduplicated_total,
                "por_destino": by_dest,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
