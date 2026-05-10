#!/usr/bin/env python3
"""
Gera payloads DARPA News (Onda 3 conservadora) a partir de
audit_reports_news_research/standardized/darpa_news_standardized.json.

- Dedupe por link; route_item (review_for_edital por sinais fortes em título/URL).
- Filtros de qualidade adicionais (data, corpo mínimo, tipo coerente, arrays).
- Não toca Supabase nem public.edital.
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
STD_PATH = ROOT / "audit_reports_news_research" / "standardized" / "darpa_news_standardized.json"
OUT_DIR = ROOT / "audit_reports_news_research_loader"

SOURCE_ID = "darpa_news"
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


def _body_len(item: Dict[str, Any], key: str) -> int:
    return len(str(item.get(key) or "").strip())


def _has_publicacao_date(dr: Any, item: Dict[str, Any]) -> bool:
    return dr._parse_date(item.get("data_publicacao")) is not None


def _pesquisa_data_ok(dr: Any, item: Dict[str, Any]) -> Tuple[bool, str]:
    if _has_publicacao_date(dr, item):
        return True, ""
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    j = str(ex.get("data_publicacao_justificativa") or "").strip()
    if len(j) >= 20:
        return True, "extras.data_publicacao_justificativa"
    return False, "sem_data_sem_justificativa_extras"


def _darpa_quality_noticia(dr: Any, item: Dict[str, Any]) -> Optional[str]:
    tit = str(item.get("titulo") or "").strip()
    if len(tit) < 3:
        return "titulo_curto"
    if not str(item.get("link") or "").strip().startswith("http"):
        return "link_invalido"
    if not _has_publicacao_date(dr, item):
        return "sem_data_publicacao"
    if _body_len(item, "resumo") < MIN_TEXTO:
        return "resumo_curto"
    tc = str(item.get("tipo_conteudo") or "").strip().lower()
    if tc and tc != "noticia":
        return "tipo_conteudo_nao_noticia"
    for k in ("area_cientifica", "area_tecnologica", "setor_estrategico", "tags"):
        v = item.get(k)
        if v is not None and isinstance(v, str):
            return f"{k}_deveria_ser_lista"
    return None


def _darpa_quality_pesquisa(dr: Any, item: Dict[str, Any]) -> Optional[str]:
    tit = str(item.get("titulo") or "").strip()
    if len(tit) < 3:
        return "titulo_curto"
    if not str(item.get("link") or "").strip().startswith("http"):
        return "link_invalido"
    ok_d, _why = _pesquisa_data_ok(dr, item)
    if not ok_d:
        return "sem_data_ou_justificativa"
    if _body_len(item, "descricao") < MIN_TEXTO:
        return "descricao_curta"
    tc = str(item.get("tipo_conteudo") or "").strip().lower()
    if tc and tc != "pesquisa":
        return "tipo_conteudo_incoerente_pesquisa"
    for k in ("area_cientifica", "area_tecnologica", "setor_estrategico", "tags"):
        v = item.get(k)
        if v is not None and isinstance(v, str):
            return f"{k}_deveria_ser_lista"
    return None


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
    excluded_quality: List[Dict[str, Any]] = []
    excluded_validation: List[Dict[str, Any]] = []

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
            rejected_out.append({"source_id": sid, "link": item.get("link"), "titulo": item.get("titulo"), "motivo": motivo})
            continue

        if routing == "noticia":
            q = _darpa_quality_noticia(dr, item)
            if q:
                excluded_quality.append(
                    {"routing": "noticia", "link": item.get("link"), "titulo": item.get("titulo"), "razao": q}
                )
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
                continue
            noticia_out.append(item)
            continue

        if routing == "pesquisa":
            q = _darpa_quality_pesquisa(dr, item)
            if q:
                excluded_quality.append(
                    {"routing": "pesquisa", "link": item.get("link"), "titulo": item.get("titulo"), "razao": q}
                )
                continue
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
                continue
            pesquisa_out.append(item)

    links_n = [str(x.get("link") or "").strip() for x in noticia_out]
    links_p = [str(x.get("link") or "").strip() for x in pesquisa_out]
    overlap = sorted(set(links_n) & set(links_p))

    validation_report = {
        "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fonte": SOURCE_ID,
        "entrada": str(STD_PATH.resolve()),
        "total_entrada": len(raw_list),
        "apos_dedupe": len(kept),
        "dedupe_removidos": len(removed_dupes),
        "payload_noticia_count": len(noticia_out),
        "payload_pesquisa_count": len(pesquisa_out),
        "review_candidates_count": len(review_out),
        "rejected_routing_count": len(rejected_out),
        "excluded_quality_count": len(excluded_quality),
        "excluded_validation_count": len(excluded_validation),
        "links_unicos_noticia": len(links_n) == len(set(links_n)),
        "links_unicos_pesquisa": len(links_p) == len(set(links_p)),
        "overlap_noticia_pesquisa_links": overlap,
        "nenhum_item_public_edital": True,
        "array_normalizations_logged": len(array_fix_log),
        "readiness_apply_staging": {
            "ok": len(noticia_out) + len(pesquisa_out) >= 1 and len(excluded_validation) == 0,
            "nota": "Apto se houver volume útil e zero erros de validação do loader nos payloads; revisar review_for_edital manualmente antes de apply.",
        },
    }

    if overlap:
        print(f"AVISO: overlap noticia/pesquisa: {overlap}", file=sys.stderr)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "darpa_news_wave1_payload_noticia.json").write_text(
        json.dumps(noticia_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "darpa_news_wave1_payload_pesquisa.json").write_text(
        json.dumps(pesquisa_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "darpa_news_wave1_review_candidates.json").write_text(
        json.dumps(review_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    dry_json = {
        **validation_report,
        "dedupe_amostra": removed_dupes[:40],
        "rejected_noise": rejected_out,
        "excluded_quality": excluded_quality[:120],
        "excluded_validation": excluded_validation[:80],
        "review_candidates": review_out,
        "governance": {
            "public_edital": 0,
            "review_for_edital_carregado_loader": 0,
            "apply": False,
        },
    }
    (OUT_DIR / "darpa_news_wave1_dry_run.json").write_text(
        json.dumps(dry_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    apto = validation_report["readiness_apply_staging"]["ok"]
    md = [
        "# DARPA News — build de payloads (Onda 3, conservador)",
        "",
        f"- Gerado: `{validation_report['gerado_em']}`",
        f"- Entrada: `{validation_report['entrada']}`",
        f"- Linhas entrada: **{validation_report['total_entrada']}**",
        f"- Após dedupe: **{validation_report['apos_dedupe']}** (removidos **{validation_report['dedupe_removidos']}**)",
        "",
        "## Payloads",
        "",
        f"- `darpa_news_wave1_payload_noticia.json`: **{validation_report['payload_noticia_count']}**",
        f"- `darpa_news_wave1_payload_pesquisa.json`: **{validation_report['payload_pesquisa_count']}**",
        f"- `darpa_news_wave1_review_candidates.json`: **{validation_report['review_candidates_count']}** (não carregados pelo loader)",
        f"- `rejected_noise`: **{validation_report['rejected_routing_count']}**",
        f"- Excluídos qualidade DARPA: **{validation_report['excluded_quality_count']}**",
        f"- Excluídos validação loader: **{validation_report['excluded_validation_count']}**",
        "",
        "## Apto apply staging (heurístico)",
        "",
        f"- **{apto}** — ver `readiness_apply_staging` em `darpa_news_wave1_dry_run.json`.",
        "",
        "## Dry-run loader (sem apply)",
        "",
        "```",
        "python scripts/load_news_research_sources.py --dry-run --staging --source darpa_news --input-dir audit_reports_news_research_loader --wave darpa_news_wave1",
        "```",
        "",
    ]
    (OUT_DIR / "darpa_news_wave1_dry_run.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(validation_report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
