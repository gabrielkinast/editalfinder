#!/usr/bin/env python3
"""
Gera payloads EurekAlert Wave 1 a partir de
audit_reports_news_research/standardized/eurekalert_science_filtered_standardized.json.

Regras: resumo notícia ≥40; descrição pesquisa ≥60; data obrigatória nos payloads;
termos fortes (config) em título/resumo/tags/URL; exclude medicina genérica;
pesquisa exige aparência técnica densa; taxonomia defesa biológica vs militar
(_apply_eurekalert_wave1_taxonomy). Sem Supabase / sem public.edital.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
STD_PATH = ROOT / "audit_reports_news_research" / "standardized" / "eurekalert_science_filtered_standardized.json"
CONFIG_PATH = ROOT / "config" / "news_research_sources.json"
OUT_DIR = ROOT / "audit_reports_news_research_loader"

SOURCE_ID = "eurekalert_science_filtered"
MIN_NOTICIA_RESUMO = 40
MIN_PESQUISA_DESC = 60


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


def _source_config() -> Dict[str, Any]:
    cfg = _load_json(CONFIG_PATH, {})
    for s in cfg.get("sources") or []:
        if isinstance(s, dict) and str(s.get("id") or "") == SOURCE_ID:
            return s
    return {}


def _filter_blob_item(item: Dict[str, Any]) -> str:
    ex = item.get("extras") or {}
    parts = [
        str(item.get("titulo") or ""),
        str(item.get("resumo") or "") or str(item.get("descricao") or ""),
        str(item.get("link") or ""),
    ]
    for k in ("matched_keywords", "feed_categories"):
        v = ex.get(k)
        if isinstance(v, list):
            parts.extend(str(x) for x in v if x)
    tags = item.get("tags")
    if isinstance(tags, list):
        parts.extend(str(x) for x in tags if x)
    return " ".join(parts).lower()


def _collect_interest_matches(item: Dict[str, Any], cfg: Dict[str, Any]) -> List[str]:
    blob = _filter_blob_item(item)
    matched: List[str] = []
    for kw in cfg.get("require_any_keyword") or []:
        if not isinstance(kw, str) or not kw.strip():
            continue
        ks = kw.strip().lower()
        if ks in blob:
            matched.append(kw.strip())
    return matched


def _exclude_hit(blob: str, cfg: Dict[str, Any]) -> Optional[str]:
    for kw in cfg.get("exclude_keywords") or []:
        if not isinstance(kw, str) or not kw.strip():
            continue
        if kw.strip().lower() in blob:
            return kw.strip()
    return None


def _blob_bio_defense_context(blob: str) -> bool:
    """Plant immunity / agro — não confundir com defesa militar."""
    b = blob.lower()
    markers = (
        "plant defense",
        "immune defense",
        "cellular defense",
        "pathogen defense",
        "biological defense",
        "defense mechanism",
        "crop defense",
        "disease resistance",
        "plant immunity",
        "growth and defense",
        "between growth and defense",
        "salicylic acid",
        "hormone in plants",
    )
    if any(m in b for m in markers):
        return True
    if re.search(r"\bplants?\s+", b) and ("defense" in b or "defence" in b):
        if any(x in b for x in ("immunity", "immune system", "pathogen")):
            return True
    return False


def _blob_military_strategic_context(blob: str) -> bool:
    b = blob.lower()
    keys = (
        "military",
        "defense technology",
        "defence technology",
        "national security",
        "warfighter",
        "aerospace defense",
        "defense industry",
        "defence industry",
        "security technology",
        "darpa",
        "dual-use",
        "dual use",
        "soldier",
        "navy ",
        "army ",
        "air force",
        "missile",
        "missiles",
        "pentagon",
    )
    return any(k in b for k in keys)


def _defense_solo_ambiguous_review(blob: str, interest: List[str]) -> bool:
    """Só 'defense' como keyword de interesse e sem contexto bio nem militar → revisão humana."""
    b = blob.lower()
    if "defense" not in b and "defence" not in b:
        return False
    if len(interest) != 1:
        return False
    if interest[0].strip().lower() not in ("defense", "defence"):
        return False
    if _blob_bio_defense_context(b):
        return False
    if _blob_military_strategic_context(b):
        return False
    return True


def _apply_eurekalert_wave1_taxonomy(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Corrige taxonomia: defesa biológica/agro ≠ setor_estrategico defesa militar.
    """
    blob = _filter_blob_item(item)
    b = blob.lower()
    out = dict(item)
    ex = dict(out.get("extras") or {})

    out["tipo_conteudo"] = "pesquisa"
    out["tipo_pesquisa"] = "pesquisa_cientifica"

    if _blob_bio_defense_context(blob):
        ac = ["biologia"]
        if any(k in b for k in ("crop", "agricultur", "farm", "plant ", "plants ", "salicylic")):
            ac = ["ciencias_agrarias"]
        at = ["biotecnologia"]
        if any(k in b for k in ("crop", "agricultur", "farm", "plant ", "plants ")):
            at = ["agrobiotecnologia", "biotecnologia"]
        se = ["bioeconomia"]
        if any(k in b for k in ("crop", "agricultur", "farm", "plant ", "plants ")):
            se = ["agricultura", "bioeconomia"]
        out["area_cientifica"] = ac
        out["area_tecnologica"] = at
        out["setor_estrategico"] = se
        out["tags"] = list(dict.fromkeys(ac + at + se))
        ex["defense_semantica"] = "biologica_agro"
        ex["taxonomia_wave"] = "eurekalert_wave1"

    elif _blob_military_strategic_context(blob):
        out["area_cientifica"] = ["engenharia"]
        out["area_tecnologica"] = ["aeroespacial", "engenharia", "defesa"]
        out["setor_estrategico"] = ["aeroespacial", "defesa"]
        out["tags"] = ["engenharia", "aeroespacial", "defesa", "seguranca"]
        ex["defense_semantica"] = "militar_dual_use"
        ex["taxonomia_wave"] = "eurekalert_wave1"

    elif ("artificial intelligence" in b or "machine learning" in b) and any(
        k in b for k in ("genetic", "genome", "dna", "gene", "mutation")
    ):
        out["area_cientifica"] = ["biologia"]
        out["area_tecnologica"] = ["ia", "computacao", "biotecnologia"]
        out["setor_estrategico"] = ["bioeconomia"]
        out["tags"] = ["ia", "biologia", "biotecnologia", "bioeconomia"]
        ex["defense_semantica"] = "nao_aplicavel"
        ex["taxonomia_wave"] = "eurekalert_wave1"

    elif any(k in b for k in ("aircraft", "journal of aircraft", "flight", "turbulence", "vortex")):
        out["area_cientifica"] = ["engenharia"]
        out["area_tecnologica"] = ["aeroespacial", "engenharia"]
        if _blob_military_strategic_context(blob):
            out["area_tecnologica"] = ["aeroespacial", "engenharia", "defesa"]
            out["setor_estrategico"] = ["aeroespacial", "defesa"]
            out["tags"] = ["engenharia", "aeroespacial", "defesa"]
            ex["defense_semantica"] = "militar_dual_use"
        else:
            out["setor_estrategico"] = ["aeroespacial"]
            out["tags"] = ["engenharia", "aeroespacial"]
            ex["defense_semantica"] = "nao_aplicavel"
        ex["taxonomia_wave"] = "eurekalert_wave1"

    else:
        out["area_cientifica"] = ["ciencia_tecnologia"]
        out["area_tecnologica"] = ["ciencia_tecnologia"]
        out["setor_estrategico"] = ["inovacao_industrial"]
        out["tags"] = ["ciencia_tecnologia"]
        ex["defense_semantica"] = "nao_classificado"
        ex["taxonomia_wave"] = "eurekalert_wave1"

    out["extras"] = ex
    return out


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
        out["tipo_pesquisa"] = "pesquisa_cientifica"
    return out


def _finalize_noticia_payload_row(item: Dict[str, Any]) -> Dict[str, Any]:
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


def _technical_dense_eureka(item: Dict[str, Any]) -> bool:
    d = _desc_len(item)
    b = _technical_blob(item)
    if d >= 420:
        return True
    if any(x in b for x in ("doi:", "arxiv", "peer-reviewed", "methods", "spectroscopy", "nanoscale", "simulation")):
        return d >= 180
    hits = sum(
        1
        for t in (
            "reactor",
            "quantum",
            "semiconductor",
            "photovoltaic",
            "battery",
            "satellite",
            "propulsion",
            "radiation",
            "algorithm",
            "superconduct",
        )
        if t in b
    )
    return d >= 220 and hits >= 2


def _ambiguous_noticia_pesquisa(item: Dict[str, Any]) -> bool:
    tc = str(item.get("tipo_conteudo") or "").lower()
    b = _technical_blob(item)
    if tc == "noticia" and ("doi:" in b or "published in the journal" in b) and _desc_len(item) > 300:
        return True
    if tc == "pesquisa" and "news-releases" in str(item.get("link") or "").lower() and _desc_len(item) < 200:
        return True
    return False


def _medical_noise_but_relevant_tech(item: Dict[str, Any]) -> bool:
    b = _technical_blob(item)
    med = ("cancer", "patient", "clinical trial", "hospital", "disease", "psychology")
    tech = ("nuclear", "quantum", "satellite", "battery", "semiconductor", "reactor", "fusion", "rocket")
    return any(m in b for m in med) and any(t in b for t in tech)


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

    src_cfg = _source_config()
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
        blob = _filter_blob_item(item)
        interest = _collect_interest_matches(item, src_cfg)
        if not interest:
            _append_rejected(
                rejected_out,
                link=item.get("link"),
                titulo=item.get("titulo"),
                stage="pre_payload",
                motivo="sem_termo_forte_interesse",
            )
            continue
        excl = _exclude_hit(blob, src_cfg)
        if excl:
            _append_rejected(
                rejected_out,
                link=item.get("link"),
                titulo=item.get("titulo"),
                stage="pre_payload",
                motivo=f"exclude_keyword:{excl}",
            )
            continue

        if _defense_solo_ambiguous_review(blob, interest):
            review_out.append(
                {
                    "source_id": sid,
                    "link": item.get("link"),
                    "titulo": item.get("titulo"),
                    "data_publicacao": item.get("data_publicacao"),
                    "routing_motivo": "defense_contexto_insuficiente_review_manual",
                    "routing_decision": "review_manual",
                    "candidate_for_edital": False,
                    "requires_manual_review": True,
                    "matched_keywords_interesse": interest,
                    "extras": item.get("extras"),
                }
            )
            continue

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

        if _ambiguous_noticia_pesquisa(item):
            review_out.append(
                {
                    "source_id": sid,
                    "link": item.get("link"),
                    "titulo": item.get("titulo"),
                    "data_publicacao": item.get("data_publicacao"),
                    "routing_motivo": "ambiguo_noticia_vs_pesquisa",
                    "routing_decision": "review_manual",
                    "candidate_for_edital": False,
                    "requires_manual_review": True,
                    "tipo_conteudo": item.get("tipo_conteudo"),
                    "extras": item.get("extras"),
                }
            )
            continue

        if _medical_noise_but_relevant_tech(item):
            review_out.append(
                {
                    "source_id": sid,
                    "link": item.get("link"),
                    "titulo": item.get("titulo"),
                    "data_publicacao": item.get("data_publicacao"),
                    "routing_motivo": "possivel_ruido_medico_com_sinal_tecnico",
                    "routing_decision": "review_manual",
                    "requires_manual_review": True,
                    "extras": item.get("extras"),
                }
            )
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
                    "extras": item.get("extras"),
                }
            )
            continue

        if routing == "noticia" and not _has_date(dr, item):
            review_out.append(
                {
                    "source_id": sid,
                    "link": item.get("link"),
                    "titulo": item.get("titulo"),
                    "data_publicacao": item.get("data_publicacao"),
                    "routing_motivo": "noticia_sem_data",
                    "routing_decision": "review_manual",
                    "requires_manual_review": True,
                    "extras": item.get("extras"),
                }
            )
            continue

        if routing == "noticia":
            rl = _resumo_len(item)
            if _has_date(dr, item) and 20 <= rl < MIN_NOTICIA_RESUMO:
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
            if rl < MIN_NOTICIA_RESUMO:
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
                _append_rejected(
                    rejected_out, link=item.get("link"), titulo=item.get("titulo"), stage="excluded_quality", motivo=tc or "tipo"
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
            if dl < MIN_PESQUISA_DESC:
                if dl >= 40 and _technical_dense_eureka(item):
                    review_out.append(
                        {
                            "source_id": sid,
                            "link": item.get("link"),
                            "titulo": item.get("titulo"),
                            "routing_motivo": "descricao_entre_40_e_59_texto_denso",
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
                        motivo="descricao_curta_pesquisa",
                        extra={"len": dl},
                    )
                continue
            if not _technical_dense_eureka(item):
                review_out.append(
                    {
                        "source_id": sid,
                        "link": item.get("link"),
                        "titulo": item.get("titulo"),
                        "data_publicacao": item.get("data_publicacao"),
                        "routing_motivo": "pesquisa_texto_nao_denso_suficiente",
                        "routing_decision": "review_manual",
                        "descricao_len": dl,
                        "extras": item.get("extras"),
                    }
                )
                continue
            tc = str(item.get("tipo_conteudo") or "").strip().lower()
            if tc != "pesquisa":
                excluded_quality.append({"routing": "pesquisa", "link": item.get("link"), "razao": "tipo_conteudo_incoerente"})
                _append_rejected(
                    rejected_out, link=item.get("link"), titulo=item.get("titulo"), stage="excluded_quality", motivo=tc or "tipo"
                )
                continue
            item = _apply_eurekalert_wave1_taxonomy(item)
            if not (item.get("tipo_pesquisa") or "").strip():
                item["tipo_pesquisa"] = "pesquisa_cientifica"
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
        "wave": "eurekalert_wave1",
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
            "nota": "Wave 1 EurekAlert: revisar WAF/crawl local; sem apply automático.",
        },
    }

    if overlap:
        print(f"AVISO: overlap noticia/pesquisa: {overlap}", file=sys.stderr)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "eurekalert_wave1_payload_noticia.json").write_text(
        json.dumps(noticia_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "eurekalert_wave1_payload_pesquisa.json").write_text(
        json.dumps(pesquisa_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "eurekalert_wave1_review_candidates.json").write_text(
        json.dumps(review_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT_DIR / "eurekalert_wave1_rejected.json").write_text(
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
    (OUT_DIR / "eurekalert_wave1_dry_run.json").write_text(json.dumps(dry_json, ensure_ascii=False, indent=2), encoding="utf-8")

    apto = validation_report["readiness_apply_staging"]["ok"]
    md = [
        "# EurekAlert Wave 1 — build de payloads (sem Supabase)",
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
        f"- `eurekalert_wave1_payload_noticia.json`: **{len(noticia_out)}**",
        f"- `eurekalert_wave1_payload_pesquisa.json`: **{len(pesquisa_out)}**",
        f"- `eurekalert_wave1_review_candidates.json`: **{len(review_out)}**",
        f"- `eurekalert_wave1_rejected.json`: **{len(rejected_out)}**",
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
        "python scripts/load_news_research_sources.py --dry-run --staging --source eurekalert_science_filtered --input-dir audit_reports_news_research_loader --wave eurekalert_wave1",
        "```",
        "",
        "Após correr o comando acima, ver `audit_reports_news_research_loader/load_news_research_summary.json` → campo `errors_count` (objetivo **0** antes de qualquer apply).",
        "",
    ]
    (OUT_DIR / "eurekalert_wave1_dry_run.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(validation_report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
