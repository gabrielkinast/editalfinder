#!/usr/bin/env python3
"""
Gera payloads IAEA Wave 1 a partir de
audit_reports_news_research/standardized/iaea_news_publications_standardized.json.

- Dedupe; roteamento via dry_run (review oportunidades IAEA).
- Notícia: data + resumo ≥40 + tipo noticia (sem data → fora do payload).
- Pesquisa Wave 1: exige data no payload; sem data → review (não payload).
- Notícia no payload: sem campo `tipo_pesquisa` (incoerente com `public.noticia`).
- Rejeitados e dry-run documentados. Sem Supabase.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
STD_PATH = ROOT / "audit_reports_news_research" / "standardized" / "iaea_news_publications_standardized.json"
OUT_DIR = ROOT / "audit_reports_news_research_loader"

SOURCE_ID = "iaea_news_publications"
MIN_TEXTO = 40


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_list_arrays(item: Dict[str, Any], log: List[str], link: str) -> Dict[str, Any]:
    out = dict(item)
    for k in ("area_cientifica", "area_tecnologica", "setor_estrategico", "tags"):
        v = out.get(k)
        if v is None:
            continue
        if isinstance(v, str):
            s = v.strip()
            out[k] = [s] if s else None
            log.append(f"{link}:{k}:str_to_list")
        elif isinstance(v, (list, tuple)):
            out[k] = [str(x).strip() for x in v if x is not None and str(x).strip()] or None
        else:
            out[k] = None
            log.append(f"{link}:{k}:tipo_reset")
    return out


def _ensure_pesquisa_descricao_tipo(item: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(item)
    if not (out.get("descricao") or "").strip():
        r = (out.get("resumo") or "").strip()
        if r:
            out["descricao"] = r
    if not (out.get("tipo_pesquisa") or "").strip():
        out["tipo_pesquisa"] = "relatorio_tecnico"
    return out


def _finalize_noticia_payload_row(item: Dict[str, Any]) -> Dict[str, Any]:
    """public.noticia: não carregar tipo_pesquisa herdado do standardized quando tipo_conteudo é notícia."""
    out = dict(item)
    if str(out.get("tipo_conteudo") or "").strip().lower() == "noticia":
        out.pop("tipo_pesquisa", None)
    return out


def _has_date(dr: Any, item: Dict[str, Any]) -> bool:
    return dr._parse_date(item.get("data_publicacao")) is not None


def _resumo_len(item: Dict[str, Any]) -> int:
    return len(str(item.get("resumo") or "").strip())


def _desc_len(item: Dict[str, Any]) -> int:
    return len(str(item.get("descricao") or "").strip())


def _technical_blob(item: Dict[str, Any]) -> str:
    return f"{item.get('titulo','')} {item.get('link','')} {item.get('resumo','')} {item.get('descricao','')}".lower()


def _technical_appearance(item: Dict[str, Any]) -> bool:
    b = _technical_blob(item)
    keys = (
        "tecdoc",
        "safety standard",
        "technical report",
        "guidance document",
        "nuclear security series",
        "iaea series",
        "/publications/",
        "/resources/",
        "treated water",
        "infrastructure development",
        "research project",
    )
    return any(k in b for k in keys)


def _ambiguous_news_vs_pub(item: Dict[str, Any]) -> bool:
    lk = str(item.get("link") or "").lower()
    tc = str(item.get("tipo_conteudo") or "").lower()
    if tc == "noticia" and "/publications/" in lk and "/newscenter/" not in lk:
        return True
    if tc == "pesquisa" and "/newscenter/pressreleases/" in lk and "report" not in _technical_blob(item):
        return True
    return False


def _append_rejected(
    bucket: List[Dict[str, Any]],
    *,
    link: Any,
    titulo: Any,
    stage: str,
    motivo: str,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    row: Dict[str, Any] = {
        "source_id": SOURCE_ID,
        "link": link,
        "titulo": titulo,
        "stage": stage,
        "motivo": motivo,
    }
    if extra:
        row["extra"] = extra
    bucket.append(row)


def main() -> int:
    dr = _load_module("dry_run_loader", SCRIPTS / "dry_run_news_research_loader.py")
    lnr = _load_module("load_news_research", SCRIPTS / "load_news_research_sources.py")

    raw_list = _load_json(STD_PATH, [])
    if not isinstance(raw_list, list) or not raw_list:
        print(f"Entrada vazia ou inválida: {STD_PATH}", file=sys.stderr)
        return 2

    rows: List[Tuple[str, Dict[str, Any]]] = [
        (SOURCE_ID, it) for it in raw_list if isinstance(it, dict)
    ]
    kept, removed_dupes = dr._dedupe_by_link(rows)

    array_fix_log: List[str] = []
    noticia_out: List[Dict[str, Any]] = []
    pesquisa_out: List[Dict[str, Any]] = []
    review_out: List[Dict[str, Any]] = []
    rejected_out: List[Dict[str, Any]] = []
    excluded_validation: List[Dict[str, Any]] = []
    excluded_quality: List[Dict[str, Any]] = []

    missing_summary_in = sum(1 for _, it in kept if dr._missing_summary_flag(it))
    missing_date_in = sum(1 for _, it in kept if not it.get("data_publicacao"))

    for sid, item in kept:
        item = _ensure_list_arrays(item, array_fix_log, str(item.get("link") or ""))
        item = _ensure_pesquisa_descricao_tipo(item)
        routing, motivo = dr.route_item(sid, item)

        if routing == "review_for_edital":
            review_out.append(
                {
                    "source_id": sid,
                    "link": item.get("link"),
                    "titulo": item.get("titulo"),
                    "data_publicacao": item.get("data_publicacao"),
                    "routing_motivo": motivo,
                    "routing_decision": "review_for_edital",
                    "candidate_for_edital": True,
                    "requires_manual_review": True,
                    "infer_content_type_legacy": dr._infer_legacy_table(item),
                    "extras": item.get("extras"),
                }
            )
            continue
        if routing == "rejected_noise":
            _append_rejected(rejected_out, link=item.get("link"), titulo=item.get("titulo"), stage="rejected_noise", motivo=motivo)
            continue

        if routing == "pesquisa" and not _has_date(dr, item):
            review_out.append(
                {
                    "source_id": sid,
                    "link": item.get("link"),
                    "titulo": item.get("titulo"),
                    "data_publicacao": item.get("data_publicacao"),
                    "routing_motivo": "pesquisa_sem_data_wave1_revisao",
                    "routing_decision": "review_manual",
                    "candidate_for_edital": False,
                    "requires_manual_review": True,
                    "technical_guess": _technical_appearance(item),
                    "extras": item.get("extras"),
                }
            )
            continue

        if routing == "noticia" and not _has_date(dr, item):
            if _technical_appearance(item):
                review_out.append(
                    {
                        "source_id": sid,
                        "link": item.get("link"),
                        "titulo": item.get("titulo"),
                        "routing_motivo": "noticia_sem_data_aparente_conteudo_tecnico",
                        "routing_decision": "review_manual",
                        "candidate_for_edital": False,
                        "requires_manual_review": True,
                        "extras": item.get("extras"),
                    }
                )
            else:
                _append_rejected(
                    rejected_out,
                    link=item.get("link"),
                    titulo=item.get("titulo"),
                    stage="excluded_noticia_sem_data",
                    motivo="noticia_exige_data_publicacao",
                )
            continue

        if _ambiguous_news_vs_pub(item):
            review_out.append(
                {
                    "source_id": sid,
                    "link": item.get("link"),
                    "titulo": item.get("titulo"),
                    "routing_motivo": "ambigo_noticia_vs_publicacao",
                    "routing_decision": "review_manual",
                    "candidate_for_edital": False,
                    "requires_manual_review": True,
                    "tipo_conteudo": item.get("tipo_conteudo"),
                    "extras": item.get("extras"),
                }
            )
            continue

        if routing == "noticia":
            rl = _resumo_len(item)
            if _has_date(dr, item) and 20 <= rl < MIN_TEXTO:
                review_out.append(
                    {
                        "source_id": sid,
                        "link": item.get("link"),
                        "titulo": item.get("titulo"),
                        "routing_motivo": "resumo_fraco_mas_com_data",
                        "routing_decision": "review_manual",
                        "resumo_len": rl,
                        "extras": item.get("extras"),
                    }
                )
                continue
            if rl < MIN_TEXTO:
                excluded_quality.append({"routing": "noticia", "link": item.get("link"), "razao": "resumo_curto_payload"})
                _append_rejected(
                    rejected_out,
                    link=item.get("link"),
                    titulo=item.get("titulo"),
                    stage="excluded_quality",
                    motivo="resumo_curto",
                    extra={"len": rl},
                )
                continue
            tc = str(item.get("tipo_conteudo") or "").strip().lower()
            if tc != "noticia":
                excluded_quality.append({"routing": "noticia", "link": item.get("link"), "razao": "tipo_conteudo_nao_noticia"})
                _append_rejected(rejected_out, link=item.get("link"), titulo=item.get("titulo"), stage="excluded_quality", motivo=tc or "tipo")
                continue
            miss = lnr._validate_noticia_payload(item)
            if miss or dr._is_generic(item):
                excluded_validation.append(
                    {
                        "routing": "noticia",
                        "link": item.get("link"),
                        "titulo": item.get("titulo"),
                        "missing": miss,
                        "generic": dr._is_generic(item),
                    }
                )
                _append_rejected(
                    rejected_out,
                    link=item.get("link"),
                    titulo=item.get("titulo"),
                    stage="excluded_validation",
                    motivo="loader_validacao_ou_generico",
                    extra={"missing": miss},
                )
                continue
            noticia_out.append(_finalize_noticia_payload_row(item))
            continue

        if routing == "pesquisa":
            dl = _desc_len(item)
            if dl < MIN_TEXTO:
                if _technical_appearance(item) and dl >= 20:
                    review_out.append(
                        {
                            "source_id": sid,
                            "link": item.get("link"),
                            "titulo": item.get("titulo"),
                            "routing_motivo": "descricao_fraca_publicacao_tecnica",
                            "routing_decision": "review_manual",
                            "descricao_len": dl,
                            "extras": item.get("extras"),
                        }
                    )
                else:
                    excluded_quality.append({"routing": "pesquisa", "link": item.get("link"), "razao": "descricao_curta"})
                    _append_rejected(
                        rejected_out,
                        link=item.get("link"),
                        titulo=item.get("titulo"),
                        stage="excluded_quality",
                        motivo="descricao_curta",
                        extra={"len": dl},
                    )
                continue
            tc = str(item.get("tipo_conteudo") or "").strip().lower()
            if tc != "pesquisa":
                excluded_quality.append({"routing": "pesquisa", "link": item.get("link"), "razao": "tipo_conteudo_incoerente"})
                _append_rejected(rejected_out, link=item.get("link"), titulo=item.get("titulo"), stage="excluded_quality", motivo=tc or "tipo")
                continue
            if not (item.get("tipo_pesquisa") or "").strip():
                item["tipo_pesquisa"] = "relatorio_tecnico"
            miss = lnr._validate_pesquisa_payload(item)
            if miss or dr._is_generic(item):
                excluded_validation.append(
                    {
                        "routing": "pesquisa",
                        "link": item.get("link"),
                        "titulo": item.get("titulo"),
                        "missing": miss,
                        "generic": dr._is_generic(item),
                    }
                )
                _append_rejected(
                    rejected_out,
                    link=item.get("link"),
                    titulo=item.get("titulo"),
                    stage="excluded_validation",
                    motivo="loader_validacao_ou_generico",
                    extra={"missing": miss},
                )
                continue
            pesquisa_out.append(item)

    links_n = [str(x.get("link") or "").strip() for x in noticia_out]
    links_p = [str(x.get("link") or "").strip() for x in pesquisa_out]
    overlap = sorted(set(links_n) & set(links_p))

    validation_report = {
        "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fonte": SOURCE_ID,
        "wave": "iaea_wave1",
        "entrada": str(STD_PATH.resolve()),
        "total_entrada": len(raw_list),
        "apos_dedupe": len(kept),
        "dedupe_removidos": len(removed_dupes),
        "payload_noticia_count": len(noticia_out),
        "payload_pesquisa_count": len(pesquisa_out),
        "review_candidates_count": len(review_out),
        "rejected_count": len(rejected_out),
        "excluded_quality_count": len(excluded_quality),
        "excluded_validation_count": len(excluded_validation),
        "entrada_missing_summary": missing_summary_in,
        "entrada_missing_date": missing_date_in,
        "links_unicos_noticia": len(links_n) == len(set(links_n)),
        "links_unicos_pesquisa": len(links_p) == len(set(links_p)),
        "overlap_noticia_pesquisa_links": overlap,
        "nenhum_item_public_edital": True,
        "array_normalizations_logged": len(array_fix_log),
        "readiness_apply_staging": {
            "ok": len(noticia_out) + len(pesquisa_out) >= 1,
            "nota": "Wave 1: só avançar apply após revisão humana dos review_manual e confirmação de zero erros no dry-run do loader; não executar apply automaticamente.",
        },
    }

    if overlap:
        print(f"AVISO: overlap noticia/pesquisa: {overlap}", file=sys.stderr)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "iaea_wave1_payload_noticia.json").write_text(
        json.dumps(noticia_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "iaea_wave1_payload_pesquisa.json").write_text(
        json.dumps(pesquisa_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "iaea_wave1_review_candidates.json").write_text(
        json.dumps(review_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "iaea_wave1_rejected.json").write_text(
        json.dumps(rejected_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    dry_json = {
        **validation_report,
        "dedupe_amostra": removed_dupes[:40],
        "rejected": rejected_out[:200],
        "excluded_quality": excluded_quality[:120],
        "excluded_validation": excluded_validation[:80],
        "review_candidates": review_out,
        "governance": {
            "public_edital": 0,
            "review_for_edital_carregado_loader": 0,
            "apply": False,
        },
    }
    (OUT_DIR / "iaea_wave1_dry_run.json").write_text(json.dumps(dry_json, ensure_ascii=False, indent=2), encoding="utf-8")

    apto = validation_report["readiness_apply_staging"]["ok"]
    md = [
        "# IAEA Wave 1 — build de payloads (sem Supabase)",
        "",
        f"- Gerado: `{validation_report['gerado_em']}`",
        f"- Entrada: `{validation_report['entrada']}`",
        f"- Linhas entrada: **{validation_report['total_entrada']}**",
        f"- Após dedupe: **{validation_report['apos_dedupe']}** (removidos **{validation_report['dedupe_removidos']}**)",
        "",
        "## Resumo (entrada)",
        "",
        f"- `missing_summary` (entrada): **{missing_summary_in}**",
        f"- Sem data (entrada): **{missing_date_in}**",
        "",
        "## Payloads",
        "",
        f"- `iaea_wave1_payload_noticia.json`: **{len(noticia_out)}**",
        f"- `iaea_wave1_payload_pesquisa.json`: **{len(pesquisa_out)}**",
        f"- `iaea_wave1_review_candidates.json`: **{len(review_out)}** (não carregados como notícia/pesquisa)",
        f"- `iaea_wave1_rejected.json`: **{len(rejected_out)}**",
        f"- Excluídos qualidade: **{len(excluded_quality)}**",
        f"- Excluídos validação loader: **{len(excluded_validation)}**",
        "",
        "## Apto para staging (heurístico)",
        "",
        f"- Volume útil (notícia+pesquisa) ≥ 1: **{len(noticia_out) + len(pesquisa_out) >= 1}**",
        f"- `readiness_apply_staging.ok`: **{apto}** — ainda **sem apply** neste fluxo.",
        "",
        "## Dry-run loader (sem apply)",
        "",
        "```",
        "python scripts/load_news_research_sources.py --dry-run --staging --source iaea_news_publications --input-dir audit_reports_news_research_loader --wave iaea_wave1",
        "```",
        "",
        "Após correr o comando acima, ver `audit_reports_news_research_loader/load_news_research_summary.json` → campo `errors_count` (objetivo **0** antes de qualquer apply).",
        "",
    ]
    (OUT_DIR / "iaea_wave1_dry_run.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(validation_report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
