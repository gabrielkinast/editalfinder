#!/usr/bin/env python3
"""
Auditoria dry-run do pipeline EditalFinder: JSON bruto → transformer → loader (simulado).

Sem upsert, sem migrações, sem deletes. PDFs não são baixados por defeito (--no-skip-pdf para testar rede).

Uso:
  python scripts/audit_pipeline.py
  python scripts/audit_pipeline.py --max-items 40 --sources finep,cnpq
  python scripts/audit_pipeline.py --output-dir audit_reports
  python scripts/audit_pipeline.py --only-loader --max-items 50 --output-dir audit_reports_loader
  python scripts/audit_pipeline.py --no-skip-pdf --sources aneel,bndes,finep --max-items 25
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
REPORTS_DIR_DEFAULT = ROOT / "audit_reports"

# Import CORE antes de carregar módulos que leem .env
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

# Credenciais fictícias só se .env não existir (map_to_db_schema chama get_default_org_id).
_ENV = CORE / ".env"
if _ENV.is_file():
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=_ENV)
if not os.getenv("SUPABASE_URL"):
    os.environ["SUPABASE_URL"] = "https://placeholder.local.supabase.co"
if not os.getenv("SUPABASE_KEY"):
    os.environ["SUPABASE_KEY"] = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9."
        "CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0"
    )

NOISE_TITLES = [
    # PT
    "contato",
    "fale conosco",
    "saiba mais",
    "leia mais",
    "clique aqui",
    "início",
    "inicio",
    "menu",
    "buscar",
    "detalhes",
    "informações",
    "informacoes",
    "downloads",
    "anexos",
    "formulário",
    "formulario",
    "resultado",
    "transparência",
    "transparencia",
    "ouvidoria",
    "perguntas frequentes",
    "faq",
    # EN
    "contact",
    "learn more",
    "read more",
    "click here",
    "more",
    "home",
    "search",
    "details",
    "information",
    "forms",
    "next",
    "previous",
    "about",
    # ES
    "contacto",
    "saber más",
    "leer más",
    "inicio",
    "detalles",
    # JA
    "ログイン",
    "お問い合わせ",
    "詳細",
    "もっと見る",
    # ZH
    "首页",
    "联系我们",
    "了解更多",
    "查看更多",
    "登录",
]
_NOISE_LOWER = frozenset(x.lower() for x in NOISE_TITLES if len(x) < 40)
_NOISE_JA_ZH = frozenset(x for x in NOISE_TITLES if any("\u3040" <= c <= "\u9fff" for c in x))

EMPTY_TRACK_FIELDS = [
    "titulo",
    "descricao",
    "link",
    "fonte",
    "data_publicacao",
    "fim_inscricao",
    "situacao",
    "valor",
    "programa",
    "acao",
    "tipo_recurso",
    "tipo_oportunidade",
    "area",
    "publico_alvo",
    "perfil_ideal",
    "setor_economico",
    "area_cientifica",
    "area_tecnologica",
    "setor_estrategico",
    "extras",
    "pdf_url",
    "documentos",
    "validacao_status",
    "qualidade_dado",
]

CRAWLER_CATEGORY: Dict[str, str] = {
    "finep": "fomento",
    "cnpq": "fomento",
    "capes": "fomento",
    "fapergs": "fomento",
    "fapesp": "fomento",
    "fapesc": "fomento",
    "fapemig": "fomento",
    "fappr": "fomento",
    "faperg": "fomento",
    "confap": "fomento",
    "bndes": "credito",
    "brde": "credito",
    "badesul": "credito",
    "caixa": "credito",
    "embrapii": "industria",
    "senai": "industria",
    "plataforma_industria": "industria",
    "abdi": "industria",
    "softex": "industria",
    "apex": "industria",
    "mcti": "ciencia",
    "cnen": "ciencia",
    "cbpf": "ciencia",
    "ipen": "ciencia",
    "impa": "ciencia",
    "science_scraper": "ciencia",
    "anp": "energia",
    "aneel": "energia",
    "petrobras": "energia",
    "mapa": "agro",
    "mma": "meio_ambiente",
    "saude": "saude",
    "fnde": "educacao",
    "pncp": "compras",
    "pncp_defesa": "defesa",
    "compras_defesa": "defesa",
    "defesa": "defesa",
    "marinha": "defesa",
    "amazul": "defesa",
    "nuclep": "defesa",
    "inb": "defesa",
    "eletronuclear": "defesa",
    "dcta_ita_iae": "defesa",
    "japan_jst": "internacional",
    "japan_e_rad": "internacional",
    "japan_kakenhi": "internacional",
    "japan_aist": "internacional",
    "japan_nedo": "internacional",
    "japan_jaxa": "internacional",
    "china_nsfc": "internacional",
    "china_mofcom_tendering": "internacional",
    "china_tendering_bidding": "internacional",
    "china_university_procurement": "internacional",
}


def _infer_source_name(json_path: Path) -> str:
    rel = json_path.relative_to(ROOT)
    return rel.parts[0].lower() if rel.parts else json_path.stem


def _raw_title(item: Dict[str, Any]) -> str:
    t = item.get("titulo") or item.get("title") or ""
    return str(t).strip()


def _raw_link(item: Dict[str, Any]) -> str:
    return str(
        item.get("link")
        or item.get("url")
        or item.get("url_pagina")
        or item.get("url_chamada")
        or ""
    ).strip()


def _is_noise_title(title: str) -> bool:
    if not title:
        return False
    t = title.strip()
    tl = t.lower()
    if tl in _NOISE_LOWER:
        return True
    for n in _NOISE_JA_ZH:
        if n in t:
            return True
    return False


def _is_empty_val(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    if isinstance(v, (list, dict)) and len(v) == 0:
        return True
    return False


def _extras_field(item: Dict[str, Any], key: str) -> Any:
    ex = item.get("extras")
    if isinstance(ex, dict):
        return ex.get(key)
    return None


def _field_value_for_audit(item: Dict[str, Any], field: str) -> Any:
    if field in (
        "tipo_oportunidade",
        "area",
        "publico_alvo",
        "setor_economico",
        "area_cientifica",
        "area_tecnologica",
        "setor_estrategico",
    ):
        return _extras_field(item, field) or item.get(field)
    if field in ("pdf_url", "documentos", "validacao_status", "qualidade_dado", "perfil_ideal"):
        v = _extras_field(item, field.replace("pdf_url", "pdf_url"))
        if field == "pdf_url":
            v = v or item.get("pdf_url")
        if field == "documentos":
            v = v or _extras_field(item, "documentos")
        if field == "validacao_status":
            v = v or _extras_field(item, "validacao_status")
        if field == "qualidade_dado":
            v = v or _extras_field(item, "qualidade_dado")
        if field == "perfil_ideal":
            v = v or _extras_field(item, "perfil_ideal")
        return v
    if field == "extras":
        return item.get("extras")
    return item.get(field)


def _pct(n: int, d: int) -> str:
    if d <= 0:
        return "0%"
    return f"{round(100 * n / d)}%"


def _maturity_label(
    raw_n: int,
    transformed: int,
    rejected: int,
    noise_raw: int,
    avg_quality: Optional[float],
) -> str:
    if raw_n <= 0:
        return "não testado"
    rej_rate = rejected / raw_n
    noise_rate = noise_raw / raw_n
    ok_rate = transformed / raw_n
    aq = avg_quality or 0.0
    if noise_rate > 0.18 or (rej_rate > 0.5 and noise_rate > 0.06):
        return "ruidoso"
    if rej_rate > 0.9 and ok_rate < 0.08:
        return "quebrado"
    if rej_rate > 0.75 and ok_rate < 0.15:
        return "fraco"
    if ok_rate > 0.65 and aq >= 62 and noise_rate < 0.04:
        return "maduro"
    if ok_rate > 0.45 and aq >= 52:
        return "bom"
    if ok_rate > 0.2:
        return "parcial"
    if rej_rate > 0.85:
        return "fraco"
    return "parcial"


def _discover_json_files() -> List[Path]:
    out: List[Path] = []
    for p in ROOT.glob("*/outputs/*.json"):
        if p.is_file():
            out.append(p.resolve())
    return sorted(out)


def _discover_standardized_files(dirs_raw: str) -> List[Path]:
    dirs: List[Path] = []
    if dirs_raw.strip():
        for part in dirs_raw.split(","):
            p = part.strip()
            if not p:
                continue
            pp = Path(p)
            dirs.append((pp if pp.is_absolute() else (ROOT / pp)).resolve())
    else:
        dirs = [(CORE / "transformer").resolve()]

    out: List[Path] = []
    seen: Set[Path] = set()
    for d in dirs:
        if not d.exists() or not d.is_dir():
            continue
        for p in d.glob("*_standardized.json"):
            rp = p.resolve()
            if rp.is_file() and rp not in seen:
                out.append(rp)
                seen.add(rp)
    return sorted(out)


def _infer_source_from_standardized(path: Path) -> str:
    stem = path.stem
    if stem.endswith("_standardized"):
        return stem[: -len("_standardized")].lower()
    return stem.lower()


def _grep_score_legacy() -> Dict[str, Any]:
    patterns = re.compile(
        r"\b(score|scores|relevance|relevancia|relevância|ranking|relevance_score|"
        r"relevancia_score|thematic_score)\b",
        re.IGNORECASE,
    )
    hits: Dict[str, int] = Counter()
    for py in list(CORE.rglob("*.py")) + list((ROOT / "scripts").glob("*.py")):
        if "audit_pipeline" in py.name:
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        c = len(patterns.findall(text))
        if c:
            hits[str(py.relative_to(ROOT))] = c
    return {"arquivos_com_ocorrencias": dict(hits), "total_arquivos": len(hits)}


def _collect_schema_gap_hints(
    standardized_item: Dict[str, Any], stripped_payload: Dict[str, Any]
) -> List[str]:
    wanted = [
        "area",
        "tipo_oportunidade",
        "perfil_ideal",
        "publico_alvo",
        "setor_economico",
        "area_cientifica",
        "area_tecnologica",
        "setor_estrategico",
        "validacao_status",
        "qualidade_dado",
        "documentos",
    ]
    hints: List[str] = []
    extras = standardized_item.get("extras") if isinstance(standardized_item.get("extras"), dict) else {}
    for key in wanted:
        src_has = (key in standardized_item and not _is_empty_val(standardized_item.get(key))) or (
            isinstance(extras, dict) and key in extras and not _is_empty_val(extras.get(key))
        )
        if not src_has:
            continue
        payload_has = (key in stripped_payload and not _is_empty_val(stripped_payload.get(key))) or (
            key == "publico_alvo" and not _is_empty_val(stripped_payload.get("publico_alvo"))
        )
        if not payload_has:
            hints.append(key)
    return hints


SEMANTIC_EQUIV: Dict[str, List[str]] = {
    "fonte": ["fonte_recurso"],
    "fim_inscricao": ["prazo_envio"],
    "valor": ["valor_maximo"],
    "tipo_recurso": ["objetivo"],
}


def _is_semantically_preserved(std_field: str, item: Dict[str, Any], payload: Dict[str, Any]) -> bool:
    if std_field in payload and not _is_empty_val(payload.get(std_field)):
        return True
    for alt in SEMANTIC_EQUIV.get(std_field, []):
        if alt in payload and not _is_empty_val(payload.get(alt)):
            return True
    if std_field == "pdf_url":
        ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
        src_pdf = item.get("pdf_url") or ex.get("pdf_url")
        return (not _is_empty_val(src_pdf)) and (not _is_empty_val(payload.get("pdf_url")))
    if std_field == "publico_alvo":
        return not _is_empty_val(payload.get("publico_alvo"))
    return False


def audit_loader_only_file(json_path: Path, max_items: int) -> Dict[str, Any]:
    from schema import normalizar
    import loader

    loader.get_default_org_id = lambda: 11  # type: ignore[method-assign]

    source_name = _infer_source_from_standardized(json_path)
    t0 = time.perf_counter()
    file_error: Optional[str] = None
    raw_items: List[Dict[str, Any]] = []
    try:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            raw = [raw]
        if not isinstance(raw, list):
            file_error = f"tipo_raiz_invalido:{type(raw).__name__}"
        else:
            raw_items = [x for x in raw if isinstance(x, dict)]
    except Exception as e:
        file_error = str(e)
        raw_items = []

    sample = raw_items[:max_items]
    comparisons: List[Dict[str, Any]] = []
    data_loss_examples: List[Dict[str, Any]] = []
    payload_examples: List[Dict[str, Any]] = []
    schema_gap_hints: Counter[str] = Counter()
    payload_empty_counter: Counter[str] = Counter()
    standardized_fields_counter: Counter[str] = Counter()
    payload_fields_counter: Counter[str] = Counter()
    lost_fields_counter: Counter[str] = Counter()
    lost_by_map_counter: Counter[str] = Counter()
    lost_by_strip_counter: Counter[str] = Counter()
    risk_overwrite_empty = 0
    processed = 0
    mapping_errors = 0

    for item in sample:
        processed += 1
        std_fields = sorted(item.keys())
        standardized_fields_counter.update(std_fields)
        extras_std = item.get("extras") if isinstance(item.get("extras"), dict) else {}
        titulo = str(item.get("titulo") or "")
        try:
            normalized = normalizar(item)
            normalized_fields = sorted(normalized.keys()) if isinstance(normalized, dict) else []
            row, ext = loader.map_to_db_schema(normalized)
            ext = ext if isinstance(ext, dict) else {}
            map_payload = {**row, **ext}
            stripped = loader._strip_payload(map_payload)
            payload_fields = sorted(stripped.keys())
            payload_fields_counter.update(payload_fields)
        except Exception as e:
            mapping_errors += 1
            comparisons.append(
                {
                    "fonte": source_name,
                    "arquivo": str(json_path.relative_to(ROOT)),
                    "titulo": titulo[:180],
                    "campos_no_standardized": std_fields,
                    "campos_no_payload": [],
                    "campos_perdidos": std_fields,
                    "extras_preservado": False,
                    "pdf_preservado": False,
                    "classificacao_preservada": False,
                    "perfil_preservado": False,
                    "observacoes": [f"erro_loader:{e}"],
                }
            )
            continue

        std_set = set(std_fields)
        norm_set = set(normalized_fields)
        map_set = set(map_payload.keys())
        payload_set = set(payload_fields)
        lost_normalize = sorted(std_set - norm_set)
        lost_map = sorted(norm_set - map_set)
        lost_strip = sorted(map_set - payload_set)
        semantic_lost: List[str] = []
        for sf in std_fields:
            if sf == "extras":
                continue
            src_val = item.get(sf)
            if _is_empty_val(src_val):
                continue
            if not _is_semantically_preserved(sf, item, stripped):
                semantic_lost.append(sf)
        lost_all = sorted(semantic_lost)
        for k in lost_all:
            lost_fields_counter[k] += 1
        for k in lost_map:
            lost_by_map_counter[k] += 1
        for k in lost_strip:
            lost_by_strip_counter[k] += 1

        for k in payload_fields:
            if _is_empty_val(stripped.get(k)):
                payload_empty_counter[k] += 1

        observacoes: List[str] = []
        extras_preservado = "extras" in payload_set and not _is_empty_val(stripped.get("extras"))
        if "extras" in std_set and not extras_preservado:
            observacoes.append("extras_existia_mas_nao_chegou_payload")
        pdf_src = item.get("pdf_url") or extras_std.get("pdf_url")
        pdf_preservado = bool(stripped.get("pdf_url"))
        if pdf_src and not pdf_preservado:
            observacoes.append("pdf_url_sumiu_no_payload")
        docs_src = item.get("documentos") or extras_std.get("documentos")
        if docs_src and not (stripped.get("documentos") or (stripped.get("extras") or {}).get("documentos")):
            observacoes.append("documentos_sumiram_no_payload")

        class_keys = [
            "area",
            "tipo_oportunidade",
            "publico_alvo",
            "setor_economico",
            "area_cientifica",
            "area_tecnologica",
            "setor_estrategico",
        ]
        class_src_has = any(
            (not _is_empty_val(item.get(k))) or (not _is_empty_val(extras_std.get(k))) for k in class_keys
        )
        class_payload_has = any((not _is_empty_val(stripped.get(k))) for k in class_keys)
        classificacao_preservada = (not class_src_has) or class_payload_has
        if class_src_has and not class_payload_has:
            observacoes.append("classificacao_sumiu_no_payload")

        perfil_src = item.get("perfil_ideal") or extras_std.get("perfil_ideal")
        perfil_preservado = bool(
            stripped.get("perfil_ideal")
            or stripped.get("publico_alvo")
            or (isinstance(stripped.get("extras"), dict) and stripped["extras"].get("perfil_ideal"))
        )
        if perfil_src and not perfil_preservado:
            observacoes.append("perfil_ideal_sumiu_no_payload")

        for critical in ("validacao_status", "qualidade_dado"):
            src_has = (critical in item and not _is_empty_val(item.get(critical))) or (
                critical in extras_std and not _is_empty_val(extras_std.get(critical))
            )
            pay_has = (critical in stripped and not _is_empty_val(stripped.get(critical))) or (
                isinstance(stripped.get("extras"), dict) and not _is_empty_val(stripped["extras"].get(critical))
            )
            if src_has and not pay_has:
                observacoes.append(f"{critical}_sumiu_no_payload")

        std_desc = str(item.get("descricao") or "")
        payload_desc = str(stripped.get("descricao") or "")
        if len(std_desc.strip()) > 200 and (len(payload_desc.strip()) < 30):
            observacoes.append("descricao_rica_virou_curta_ou_vazia")

        null_ratio = sum(1 for v in stripped.values() if _is_empty_val(v)) / max(1, len(stripped))
        if null_ratio > 0.6:
            observacoes.append("payload_com_muitos_campos_vazios")
            risk_overwrite_empty += 1

        for k in _collect_schema_gap_hints(item, stripped):
            schema_gap_hints[k] += 1

        cmp_obj = {
            "fonte": source_name,
            "arquivo": str(json_path.relative_to(ROOT)),
            "titulo": titulo[:180],
            "campos_no_standardized": std_fields,
            "campos_no_payload": payload_fields,
            "campos_perdidos": lost_all,
            "extras_preservado": extras_preservado,
            "pdf_preservado": pdf_preservado,
            "classificacao_preservada": classificacao_preservada,
            "perfil_preservado": perfil_preservado,
            "observacoes": observacoes,
            "campos_perdidos_no_normalizar": lost_normalize,
            "campos_perdidos_no_map_to_db_schema": lost_map,
            "campos_removidos_por_strip_payload": lost_strip,
        }
        comparisons.append(cmp_obj)

        if observacoes and len(data_loss_examples) < 25:
            data_loss_examples.append(cmp_obj)
        if len(payload_examples) < 8:
            payload_examples.append(
                {
                    "fonte": source_name,
                    "titulo": titulo[:160],
                    "payload_exemplo": {k: stripped.get(k) for k in list(payload_fields)[:25]},
                    "observacoes": observacoes,
                }
            )

    tempo_ms = int((time.perf_counter() - t0) * 1000)
    problems = sum(1 for c in comparisons if c.get("observacoes"))
    readiness = round(100 * (1 - (problems / max(1, len(comparisons)))), 2)
    return {
        "modo": "only_loader",
        "fonte_pipeline": source_name,
        "categoria": CRAWLER_CATEGORY.get(source_name, "outros"),
        "arquivo_standardized": str(json_path.relative_to(ROOT)),
        "file_error": file_error,
        "itens_standardized_total": len(raw_items),
        "itens_amostra": len(sample),
        "itens_processados_loader": len(comparisons),
        "itens_com_problema_payload": problems,
        "readiness_loader_score": readiness,
        "riscos_sobrescrita_por_vazio": risk_overwrite_empty,
        "mapping_errors": mapping_errors,
        "campos_no_standardized_contagem": dict(standardized_fields_counter),
        "campos_no_payload_contagem": dict(payload_fields_counter),
        "campos_perdidos_contagem": dict(lost_fields_counter),
        "campos_perdidos_no_map_contagem": dict(lost_by_map_counter),
        "campos_removidos_strip_contagem": dict(lost_by_strip_counter),
        "campos_vazios_no_payload_contagem": dict(payload_empty_counter),
        "schema_gap_hints": dict(schema_gap_hints),
        "comparacoes": comparisons,
        "payload_examples": payload_examples,
        "data_loss_examples": data_loss_examples,
        "tempo_ms": tempo_ms,
    }


def audit_one_file(
    json_path: Path,
    max_items: int,
    skip_pdf: bool,
) -> Dict[str, Any]:
    import transformer as tr

    if skip_pdf:
        tr.read_pdf_text = lambda pdf_url, page_referer=None: None  # type: ignore[method-assign]

    from schema import normalizar
    import loader

    loader.get_default_org_id = lambda: 11  # type: ignore[method-assign]

    source_name = _infer_source_name(json_path)
    t0 = time.perf_counter()
    file_error: Optional[str] = None
    raw_items: List[Any] = []
    try:
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            raw = [raw]
        if not isinstance(raw, list):
            file_error = f"tipo_raiz_invalido:{type(raw).__name__}"
        else:
            raw_items = [x for x in raw if isinstance(x, dict)]
    except Exception as e:
        file_error = str(e)
        raw_items = []

    sample = raw_items[:max_items]
    raw_n = len(sample)
    noise_raw = sum(1 for it in sample if _is_noise_title(_raw_title(it)))

    transformed_payloads: List[Dict[str, Any]] = []
    rejection_reasons: Counter[str] = Counter()
    incompletos = suspeitos = 0
    qualities: List[float] = []
    noise_passed: List[Dict[str, Any]] = []
    good_samples: List[Dict[str, Any]] = []
    bad_samples: List[Dict[str, Any]] = []
    loader_rows: List[Dict[str, Any]] = []
    dup_links_raw: Counter[str] = Counter()
    dup_links_ok: Counter[str] = Counter()
    data_loss_examples: List[Dict[str, Any]] = []
    class_issues: List[Dict[str, Any]] = []
    profile_issues: List[Dict[str, Any]] = []
    date_issues: List[Dict[str, Any]] = []
    value_issues: List[Dict[str, Any]] = []

    for it in sample:
        rl = _raw_link(it)
        if rl:
            dup_links_raw[rl] += 1

    for it in sample:
        tr_res = tr._transform_item_with_result(it, source_name)
        if tr_res.rejected or not tr_res.payload:
            rejection_reasons[tr_res.rejection_reason or "sem_motivo"] += 1
            if len(bad_samples) < 5:
                bad_samples.append(
                    {
                        "titulo": _raw_title(it),
                        "link": _raw_link(it),
                        "motivo": tr_res.rejection_reason,
                        "content_type": tr_res.content_type_detectado,
                    }
                )
            continue
        pl = tr_res.payload
        transformed_payloads.append(pl)
        ex = pl.get("extras") if isinstance(pl.get("extras"), dict) else {}
        st = ex.get("validacao_status")
        if st == "incompleto":
            incompletos += 1
        elif st == "suspeito":
            suspeitos += 1
        q = ex.get("qualidade_dado")
        if isinstance(q, (int, float)):
            qualities.append(float(q))
        tit = str(pl.get("titulo") or "")
        if _is_noise_title(tit):
            noise_passed.append(
                {
                    "fonte": source_name,
                    "titulo": tit,
                    "link": pl.get("link"),
                    "ficheiro": str(json_path.relative_to(ROOT)),
                }
            )
        lk = str(pl.get("link") or "")
        if lk:
            dup_links_ok[lk] += 1
        if len(good_samples) < 3 and tit and lk:
            good_samples.append({"titulo": tit[:120], "link": lk[:200]})

        # Perda bruto → transformado
        raw_pdf = None
        if isinstance(it.get("extras"), dict):
            raw_pdf = it["extras"].get("pdf_url")
        if not raw_pdf and it.get("pdf_url"):
            raw_pdf = it.get("pdf_url")
        out_pdf = ex.get("pdf_url") if isinstance(ex, dict) else None
        if raw_pdf and not out_pdf:
            if len(data_loss_examples) < 8:
                data_loss_examples.append(
                    {
                        "fonte": source_name,
                        "campo_perdido": "pdf_url/extras.pdf_url",
                        "bruto": str(raw_pdf)[:300],
                        "transformado": None,
                        "recomendacao": "preservar pdf_url em extras",
                    }
                )
        raw_desc = (it.get("descricao") or it.get("resumo") or "") or ""
        if isinstance(raw_desc, str) and len(raw_desc.strip()) > 400:
            out_desc = (pl.get("descricao") or "") or ""
            if isinstance(out_desc, str) and len(out_desc) < 50:
                if len(data_loss_examples) < 12:
                    data_loss_examples.append(
                        {
                            "fonte": source_name,
                            "campo_perdido": "descricao",
                            "bruto_len": len(raw_desc),
                            "transformado_len": len(out_desc),
                            "recomendacao": "rever truncagem ou gate",
                        }
                    )

        tipo_r = pl.get("tipo_recurso")
        if tipo_r in (None, "", "Não Especificado") and source_name in (
            "bndes",
            "brde",
            "caixa",
        ):
            if len(class_issues) < 30:
                class_issues.append(
                    {
                        "fonte": source_name,
                        "titulo": tit[:100],
                        "tipo_recurso": tipo_r,
                        "esperado_aproximado": "crédito/financiamento",
                    }
                )

        perfil = ex.get("perfil_ideal") if isinstance(ex, dict) else None
        if _is_empty_val(perfil) and source_name in ("finep", "cnpq", "pncp", "bndes"):
            if len(profile_issues) < 25:
                profile_issues.append(
                    {
                        "fonte": source_name,
                        "titulo": tit[:100],
                        "perfil_ideal": perfil,
                        "nota": "fonte estratégica sem perfil inferido",
                    }
                )

        fi = pl.get("fim_inscricao")
        if fi and isinstance(fi, str):
            try:
                from datetime import date

                y, m, d = int(fi[:4]), int(fi[5:7]), int(fi[8:10])
                if date(y, m, d) < date.today() and str(pl.get("situacao") or "").lower() in (
                    "aberto",
                    "",
                ):
                    if len(date_issues) < 15:
                        date_issues.append(
                            {
                                "fonte": source_name,
                                "fim_inscricao": fi,
                                "situacao": pl.get("situacao"),
                                "nota": "prazo passado com situacao aberta/genérica",
                            }
                        )
            except Exception:
                if len(date_issues) < 20:
                    date_issues.append(
                        {
                            "fonte": source_name,
                            "fim_inscricao": fi,
                            "nota": "data_iso_suspeita",
                        }
                    )

        val = pl.get("valor")
        raw_val = it.get("valor") or (it.get("extras") or {}).get("valor")
        if raw_val and _is_empty_val(val):
            if len(value_issues) < 12:
                value_issues.append(
                    {
                        "fonte": source_name,
                        "valor_bruto": str(raw_val)[:200],
                        "valor_transformado": val,
                    }
                )

        try:
            norm = normalizar(pl)
            row, ext = loader.map_to_db_schema(norm)
            merged = {**row, **(ext if isinstance(ext, dict) else {})}
            stripped = loader._strip_payload(merged)
            null_core = sum(1 for k, v in row.items() if _is_empty_val(v))
            stripped_null = sum(1 for k, v in stripped.items() if _is_empty_val(v))
            loader_rows.append(
                {
                    "chaves_core": len(row),
                    "chaves_apos_strip": len(stripped),
                    "nulos_core": null_core,
                    "nulos_strip": stripped_null,
                    "extras_preservado_fora_strip": isinstance(ext, dict) and len(ext) > 0,
                    "amostra_chaves_strip": sorted(stripped.keys())[:35],
                }
            )
        except Exception as e:
            loader_rows.append({"erro": str(e)})

    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    transformed = len(transformed_payloads)
    rejected = raw_n - transformed

    # Campos preenchidos (apenas transformados)
    field_counts = {f: 0 for f in EMPTY_TRACK_FIELDS}
    for pl in transformed_payloads:
        for f in EMPTY_TRACK_FIELDS:
            if not _is_empty_val(_field_value_for_audit(pl, f)):
                field_counts[f] += 1
    denom = max(1, transformed)
    campos_pct = {k: _pct(v, denom) for k, v in field_counts.items()}

    dup_exact_raw = sum(1 for v in dup_links_raw.values() if v > 1)
    dup_exact_ok = sum(1 for v in dup_links_ok.values() if v > 1)

    avg_q = sum(qualities) / len(qualities) if qualities else None
    maturidade = _maturity_label(raw_n, transformed, rejected, noise_raw, avg_q)

    return {
        "ficheiro": str(json_path.relative_to(ROOT)),
        "fonte_pipeline": source_name,
        "categoria": CRAWLER_CATEGORY.get(source_name, "outros"),
        "file_error": file_error,
        "itens_brutos_amostra": raw_n,
        "itens_brutos_ficheiro": len(raw_items) if not file_error else 0,
        "noise_titulos_bruto": noise_raw,
        "transformados": transformed,
        "rejeitados": rejected,
        "incompletos": incompletos,
        "suspeitos": suspeitos,
        "campos_preenchidos_pct": campos_pct,
        "motivos_rejeicao": dict(rejection_reasons),
        "qualidade_media": round(avg_q, 2) if avg_q is not None else None,
        "maturidade_detectada": maturidade,
        "amostras_boas": good_samples,
        "amostras_ruins": bad_samples[:8],
        "noise_passou_transformer": noise_passed,
        "duplicados_link_bruto": dup_exact_raw,
        "duplicados_link_transformados": dup_exact_ok,
        "data_loss_examples": data_loss_examples,
        "classification_flag_examples": class_issues,
        "profile_flag_examples": profile_issues,
        "date_flag_examples": date_issues,
        "value_flag_examples": value_issues,
        "loader_simulacao_n": len(loader_rows),
        "loader_primeiro": loader_rows[0] if loader_rows else None,
        "tempo_ms": elapsed_ms,
    }


def _aggregate_empty_ranking(by_source: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ranking só entre fontes com pelo menos 1 item transformado (evita indice 1.0 artificial)."""
    field_empty_global: Counter[str] = Counter()
    source_empty_score: Dict[str, float] = {}
    zero_transform_sources: List[str] = []
    for block in by_source:
        src = block.get("fonte_pipeline", "?")
        ficheiro = block.get("ficheiro", "")
        t = block.get("transformados") or 0
        if t <= 0:
            zero_transform_sources.append(f"{src} ({ficheiro})")
            continue
        empty_n = 0
        total = 0
        pct = block.get("campos_preenchidos_pct") or {}
        for f in EMPTY_TRACK_FIELDS:
            p = pct.get(f, "0%")
            try:
                filled = int(str(p).rstrip("%"))
            except ValueError:
                filled = 0
            empty_n += 100 - filled
            total += 100
        key = f"{src}|{Path(ficheiro).name}" if ficheiro else src
        source_empty_score[key] = empty_n / max(1, total)
        for f in EMPTY_TRACK_FIELDS:
            p = pct.get(f, "0%")
            try:
                filled = int(str(p).rstrip("%"))
            except ValueError:
                filled = 0
            field_empty_global[f] += 100 - filled
    ranking_sources = sorted(source_empty_score.items(), key=lambda x: x[1], reverse=True)
    ranking_fields = field_empty_global.most_common()
    return {
        "fontes_mais_campos_vazios": [
            {"fonte_ou_ficheiro": a, "indice_vazio_0_1": round(b, 4)} for a, b in ranking_sources[:25]
        ],
        "campos_mais_vazios_global": [{"campo": a, "score": b} for a, b in ranking_fields[:20]],
        "fontes_com_zero_aceites_na_amostra": zero_transform_sources[:60],
        "n_fontes_zero_aceites": len(zero_transform_sources),
    }


def _build_matrix_row(block: Dict[str, Any]) -> Dict[str, Any]:
    m = block.get("maturidade_detectada", "não testado")
    t = block.get("transformados") or 0
    raw = block.get("itens_brutos_amostra") or 0
    rej = block.get("rejeitados") or 0
    noise_b = block.get("noise_titulos_bruto") or 0
    q = block.get("qualidade_media")
    qual = "alta" if q and q >= 68 else ("média" if q and q >= 55 else "baixa" if q else "n/d")
    ruido = "alto" if raw and noise_b / raw > 0.12 else ("médio" if raw and noise_b / raw > 0.04 else "baixo")
    pct = block.get("campos_preenchidos_pct") or {}
    empty_avg = 0.0
    n = 0
    for v in pct.values():
        try:
            empty_avg += 100 - int(str(v).rstrip("%"))
            n += 1
        except ValueError:
            pass
    empty_avg = empty_avg / max(1, n)
    campos_v = "alto" if empty_avg > 55 else ("médio" if empty_avg > 35 else "baixo")
    # simplified PDF column from campos_pct
    pdfp = block.get("campos_preenchidos_pct") or {}
    pdf_s = "bom" if int((pdfp.get("pdf_url") or "0%").rstrip("%") or 0) > 15 else "baixo"
    fn = Path(block.get("ficheiro") or "").name or ""
    return {
        "Crawler": f"{block.get('fonte_pipeline')}|{fn}" if fn else block.get("fonte_pipeline"),
        "fonte": block.get("fonte_pipeline"),
        "ficheiro": fn,
        "Categoria": block.get("categoria"),
        "Status": m,
        "Qualidade": qual,
        "Ruído": ruido,
        "Campos_vazios": campos_v,
        "PDFs": pdf_s,
        "Classificação": "ver relatório",
        "Perfil_ideal": "ver relatório",
        "Duplicatas": block.get("duplicados_link_bruto", 0) + block.get("duplicados_link_transformados", 0),
        "Performance_ms": block.get("tempo_ms"),
        "Recomendacao": "ver audit_by_source",
    }


def _write_technical_report(
    out_dir: Path,
    summary: Dict[str, Any],
    by_source: List[Dict[str, Any]],
    all_noise: List[Dict[str, Any]],
    all_data_loss: List[Dict[str, Any]],
    all_class: List[Dict[str, Any]],
    all_profile: List[Dict[str, Any]],
    all_dates: List[Dict[str, Any]],
    all_values: List[Dict[str, Any]],
    score_rep: Dict[str, Any],
    empty_rank: Dict[str, Any],
) -> None:
    """Relatório técnico longo (22 secções) a partir de evidências já agregadas."""
    maturidade_c = Counter(b.get("maturidade_detectada", "?") for b in by_source)
    motivos: Counter[str] = Counter()
    for b in by_source:
        for k, v in (b.get("motivos_rejeicao") or {}).items():
            motivos[k] += int(v)

    top_bugs = motivos.most_common(12)
    maduros = [b.get("fonte_pipeline") for b in by_source if b.get("maturidade_detectada") == "maduro"]
    ruidosos = [b.get("fonte_pipeline") for b in by_source if b.get("maturidade_detectada") == "ruidoso"]
    quebrados = [b.get("fonte_pipeline") for b in by_source if b.get("maturidade_detectada") == "quebrado"]

    lines = [
        "# Relatório técnico de auditoria (dry-run)",
        "",
        f"Gerado: `{summary.get('data_auditoria')}` · Amostra: até **{summary.get('max_items_por_ficheiro')}** itens por ficheiro · PDF: **{'off' if summary.get('pdf_skip') else 'on'}**.",
        "",
        "## 0. Como ler estes números (sem alarme falso)",
        "- **«Quebrado»** na matriz reflete sobretudo *amostra + PDF off + gate*; valide com `--no-skip-pdf` em poucas fontes antes de mexer em crawlers.",
        "- **«Ruído que passou = 0»** é bom sinal, mas não substitui revisão de *oportunidades boas rejeitadas* (veja motivos agregados na secção 4).",
        "- **Login (242)** pode misturar lixo real e falsos positivos; o projeto agora **suprime padrões de login fracos** em contexto `gov.br`/bancos públicos com sinais de chamada/edital.",
        "- **Loader-only:** `python scripts/audit_pipeline.py --only-loader` para separar perdas do loader.",
        "- **Score:** `EDITALFINDER_SKIP_SCORING=true` remove cálculo de relevância no transformer (caminho mais leve).",
        "",
        "## 1. Resumo executivo",
        f"- **{summary.get('ficheiros_processados')}** ficheiros JSON processados; **{summary.get('itens_analisados_total')}** itens na amostra.",
        f"- **{summary.get('fontes_com_amostra_positiva')}** ficheiros tinham itens brutos na amostra.",
        f"- Distribuição heurística de maturidade: {dict(maturidade_c)}.",
        "- O `opportunity_gate` e regras de relevância excluem muitas URLs institucionais/PDFs sem texto — várias fontes ficam com **0 aceites** na amostra (ver secção 8 e `audit_by_source.json`).",
        "",
        "## 2. Quantidade de fontes testadas",
        str(summary.get("ficheiros_processados")),
        "",
        "## 3. Quantidade de itens analisados",
        str(summary.get("itens_analisados_total")),
        "",
        "## 4. Principais bugs / causas de rejeição (agregado)",
        "",
        "| Motivo (rejection_reason) | Contagem na amostra |",
        "|---------------------------|---------------------|",
    ]
    for m, c in top_bugs:
        lines.append(f"| {m} | {c} |")
    lines.extend(
        [
            "",
            "## 5. Principais ruídos",
            f"- Títulos de lista negra **no bruto** contam-se por ficheiro; exemplos que **passaram** o transformer: **{len(all_noise)}** (ficheiro `audit_noise_examples.json`).",
            "",
            "## 6. Campos mais vazios (só itens transformados)",
            "",
        ]
    )
    for row in (empty_rank.get("campos_mais_vazios_global") or [])[:12]:
        lines.append(f"- **{row.get('campo')}**: score acumulado {row.get('score')}")
    lines.extend(
        [
            "",
            "## 7. Dados perdidos no transformer",
            f"- Exemplos: **{len(all_data_loss)}** em `audit_data_loss_examples.json`.",
            "",
            "## 8. Dados perdidos no loader",
            "- Simulação: `map_to_db_schema` + `_strip_payload`; ver `audit_loader_payload.json` (chaves após strip vs extras fora do strip em modo legado).",
            "",
            "## 9. Duplicidade",
            "- Por ficheiro: contagem de links repetidos no bruto e nos aceites — `audit_duplicates.json`.",
            "",
            "## 10. Classificação",
            f"- Flags heurísticas (ex.: crédito sem tipo): **{len(all_class)}** exemplos em `audit_classification_issues.json`.",
            "",
            "## 11. perfil_ideal",
            f"- **{len(all_profile)}** exemplos em `audit_profile_issues.json`.",
            "",
            "## 12. Datas",
            f"- **{len(all_dates)}** flags em `audit_by_source.json` (por fonte) + agregado nos exemplos.",
            "",
            "## 13. Valores",
            f"- **{len(all_values)}** exemplos de valor bruto sem valor transformado.",
            "",
            "## 14. PDF / documentos",
            "- Nesta corrida os PDFs **não foram baixados** (`pdf_skip`); percentagens de `pdf_url` nos aceites reflectem só metadados do crawler + extras.",
            "",
            "## 15. Performance",
            "- Tempos por ficheiro: `audit_performance.json`.",
            "",
            "## 16. Score / relevância legado",
            f"- Ficheiros Python com ocorrências: **{score_rep.get('total_arquivos')}** — detalhe em `audit_score_legacy.json`.",
            "",
            "## 17. Status por crawler (amostra)",
            f"- **Maduro** (exemplos): {', '.join(maduros[:15]) or '—'}",
            f"- **Ruidoso**: {', '.join(ruidosos[:15]) or '—'}",
            f"- **Quebrado** (0 aceites ou erro): {len(quebrados)} fontes — primeiras: {', '.join(quebrados[:20]) or '—'}",
            "",
            "## 18. Top 10 correções mais importantes",
            "1. Rever falsos positivos do **opportunity_gate** (login em páginas gov.br reais de editais).",
            "2. Separar **PDF só como documento** vs página de oportunidade no gate.",
            "3. Afinar **relevância mínima** para BNDES/BRDE/Caixa/Badesul (muitas exclusões na amostra).",
            "4. Melhorar **tipo_recurso** para linhas de crédito.",
            "5. Preencher **perfil_ideal** nas fontes estratégicas.",
            "6. Reduzir **campos vazios** nas fontes no topo de `audit_empty_fields.json`.",
            "7. **Deduplicação** por link dentro do mesmo JSON de crawler.",
            "8. Preservar **pdf_url** quando presente no bruto.",
            "9. Auditoria com **PDF on** apenas num subconjunto controlado.",
            "10. Documentar **fontes com_zero_aceites** como risco de gate vs risco de crawler.",
            "",
            "## 19. Correções rápidas",
            "- Ajustar listas de ruído / títulos genéricos no crawler ou em `noise_filter` com base em `audit_noise_examples.json`.",
            "",
            "## 20. Correções médias",
            "- Refinar `opportunity_gate` por domínio (gov.br, bndes.gov.br, etc.).",
            "",
            "## 21. Correções grandes",
            "- Separar pipeline **crawl → normalização mínima → gate pesado opcional**.",
            "",
            "## 22. Próximas etapas",
            "- Correr amostra maior (`--max-items 100`) em subset de fontes críticas.",
            "- Correr subconjunto com `--no-skip-pdf` em staging.",
            "- Validar matriz completa em `audit_matrix_crawlers.json`.",
            "",
            "---",
            "*Maturidade é heurística sobre a amostra; não substitui revisão humana dos JSONs.*",
        ]
    )
    (out_dir / "audit_relatorio_tecnico.md").write_text("\n".join(lines), encoding="utf-8")


def _run_loader_only_mode(
    out_dir: Path,
    max_items: int,
    allowed: Optional[Set[str]],
    standardized_dirs: str,
) -> int:
    files = _discover_standardized_files(standardized_dirs)
    if allowed:
        files = [p for p in files if _infer_source_from_standardized(p) in allowed]

    by_source: List[Dict[str, Any]] = []
    all_comparisons: List[Dict[str, Any]] = []
    all_data_loss: List[Dict[str, Any]] = []
    all_payload_examples: List[Dict[str, Any]] = []
    schema_gaps_global: Counter[str] = Counter()
    field_loss_global: Counter[str] = Counter()
    payload_empty_global: Counter[str] = Counter()
    errors = 0

    for fp in files:
        try:
            block = audit_loader_only_file(fp, max_items=max_items)
        except Exception as e:
            errors += 1
            block = {
                "modo": "only_loader",
                "fonte_pipeline": _infer_source_from_standardized(fp),
                "arquivo_standardized": str(fp.relative_to(ROOT)),
                "file_error": f"audit_loader_only_exception:{e}",
                "itens_amostra": 0,
                "itens_processados_loader": 0,
                "itens_com_problema_payload": 0,
                "readiness_loader_score": 0.0,
                "schema_gap_hints": {},
                "campos_perdidos_contagem": {},
                "campos_vazios_no_payload_contagem": {},
                "comparacoes": [],
                "data_loss_examples": [],
                "payload_examples": [],
                "tempo_ms": 0,
            }
        by_source.append(block)
        all_comparisons.extend(block.get("comparacoes") or [])
        all_data_loss.extend(block.get("data_loss_examples") or [])
        all_payload_examples.extend(block.get("payload_examples") or [])
        schema_gaps_global.update(block.get("schema_gap_hints") or {})
        field_loss_global.update(block.get("campos_perdidos_contagem") or {})
        payload_empty_global.update(block.get("campos_vazios_no_payload_contagem") or {})

    total_items = sum(int(b.get("itens_amostra") or 0) for b in by_source)
    total_problem_items = sum(int(b.get("itens_com_problema_payload") or 0) for b in by_source)
    summary = {
        "modo": "only_loader",
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "max_items_por_ficheiro": max_items,
        "standardized_dirs": standardized_dirs,
        "ficheiros_standardized_encontrados": len(_discover_standardized_files(standardized_dirs)),
        "ficheiros_processados": len(by_source),
        "itens_analisados_total": total_items,
        "itens_com_alerta_payload": total_problem_items,
        "erros_audit_exception": errors,
    }

    ranking_fontes_perda = sorted(
        [
            {
                "fonte": b.get("fonte_pipeline"),
                "arquivo": b.get("arquivo_standardized"),
                "problemas_payload": b.get("itens_com_problema_payload", 0),
                "itens_amostra": b.get("itens_amostra", 0),
                "readiness_loader_score": b.get("readiness_loader_score"),
                "riscos_sobrescrita_por_vazio": b.get("riscos_sobrescrita_por_vazio", 0),
            }
            for b in by_source
        ],
        key=lambda x: (
            -int(x.get("problemas_payload") or 0),
            float(x.get("readiness_loader_score") or 0),
        ),
    )
    fontes_prontas_loader = sorted(
        ranking_fontes_perda, key=lambda x: float(x.get("readiness_loader_score") or 0), reverse=True
    )

    payload_comparacao = {
        "comparacoes": all_comparisons[:2500],
        "totais": {
            "n_comparacoes": len(all_comparisons),
            "n_com_observacoes": sum(1 for c in all_comparisons if c.get("observacoes")),
        },
    }
    empty_fields = {
        "campos_mais_vazios_no_payload": [
            {"campo": k, "contagem_vazio": int(v)} for k, v in payload_empty_global.most_common(40)
        ],
        "fontes_com_maior_perda": ranking_fontes_perda[:40],
        "fontes_mais_prontas_loader": fontes_prontas_loader[:40],
    }
    data_loss = {
        "top_campos_perdidos": [{"campo": k, "contagem": int(v)} for k, v in field_loss_global.most_common(60)],
        "exemplos": all_data_loss[:300],
    }
    schema_gaps = {
        "campos_em_extras_que_deveriam_virar_coluna": [
            {"campo": k, "ocorrencias": int(v)} for k, v in schema_gaps_global.most_common(40)
        ],
        "top_10_campos_prioritarios": [
            {"campo": k, "ocorrencias": int(v)} for k, v in schema_gaps_global.most_common(10)
        ],
    }

    (out_dir / "audit_loader_only_summary.json").write_text(
        json.dumps({**summary, "ranking_fontes_perda": ranking_fontes_perda[:30]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_loader_only_by_source.json").write_text(
        json.dumps(by_source, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_loader_only_empty_fields.json").write_text(
        json.dumps(empty_fields, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_loader_only_data_loss.json").write_text(
        json.dumps(data_loss, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_loader_only_payload_examples.json").write_text(
        json.dumps(
            {
                "payload_examples": all_payload_examples[:300],
                "comparacao_obrigatoria_por_item": payload_comparacao,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "audit_loader_only_schema_gaps.json").write_text(
        json.dumps(schema_gaps, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md_lines = [
        "# Auditoria loader-only",
        "",
        "## Interpretação",
        "- Isto **não** executa crawler nem transformer: só mede **standardized → normalizar → map_to_db_schema → _strip_payload**.",
        "- Compare com a auditoria completa (JSON bruto) para separar perdas do **transformer** vs **loader/schema**.",
        "",
        f"- Ficheiros standardized processados: **{summary['ficheiros_processados']}**",
        f"- Itens analisados (amostra): **{summary['itens_analisados_total']}**",
        f"- Itens com alerta de payload: **{summary['itens_com_alerta_payload']}**",
        "",
        "## Top 10 perdas de dados (campos)",
    ]
    for row in data_loss["top_campos_perdidos"][:10]:
        md_lines.append(f"- `{row['campo']}`: {row['contagem']}")
    md_lines.extend(["", "## Top 10 fontes com maior problema no payload"])
    for row in ranking_fontes_perda[:10]:
        md_lines.append(
            f"- `{row['fonte']}` ({Path(str(row['arquivo'])).name}): problemas={row['problemas_payload']}, "
            f"amostra={row['itens_amostra']}, readiness={row['readiness_loader_score']}"
        )
    md_lines.extend(["", "## Top 10 campos para schema/map_to_db_schema"])
    for row in schema_gaps["top_10_campos_prioritarios"]:
        md_lines.append(f"- `{row['campo']}`: {row['ocorrencias']}")
    md_lines.extend(
        [
            "",
            "## Recomendações prioritárias",
            "1. Reduzir perdas em `_strip_payload` para campos críticos vindos de `extras`.",
            "2. Garantir preservação de `pdf_url` e `documentos` no payload final.",
            "3. Revisar rota de `perfil_ideal`/classificação para não sumir no payload.",
            "4. Identificar colunas candidatas no schema pelos tops de `audit_loader_only_schema_gaps.json`.",
            "5. Mitigar risco de sobrescrita por vazios nos loaders com mais alertas.",
        ]
    )
    (out_dir / "audit_loader_only_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(
        f"[audit-loader-only] Relatórios em {out_dir} "
        f"({summary['ficheiros_processados']} ficheiros, {summary['itens_analisados_total']} itens)."
    )
    return 0 if errors == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria dry-run EditalFinder")
    ap.add_argument("--max-items", type=int, default=50, help="Máximo de itens por ficheiro JSON")
    ap.add_argument("--sources", type=str, default="", help="Filtrar por pasta raiz (ex.: finep,cnpq)")
    ap.add_argument("--output-dir", type=Path, default=REPORTS_DIR_DEFAULT)
    ap.add_argument(
        "--only-loader",
        action="store_true",
        help="Lê *_standardized.json e simula apenas normalizar/map_to_db_schema/_strip_payload.",
    )
    ap.add_argument(
        "--standardized-dirs",
        type=str,
        default="CORE/transformer",
        help="Diretórios de *_standardized.json (separados por vírgula).",
    )
    ap.add_argument(
        "--no-skip-pdf",
        action="store_true",
        help="Permitir download/leitura de PDF (lento; não recomendado em auditoria larga)",
    )
    args = ap.parse_args()
    out_dir: Path = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    allowed: Optional[Set[str]] = None
    if args.sources.strip():
        allowed = {x.strip().lower() for x in args.sources.split(",") if x.strip()}

    if args.only_loader:
        return _run_loader_only_mode(
            out_dir=out_dir,
            max_items=args.max_items,
            allowed=allowed,
            standardized_dirs=args.standardized_dirs,
        )

    files = _discover_json_files()
    if allowed:
        files = [p for p in files if _infer_source_name(p) in allowed]

    by_source: List[Dict[str, Any]] = []
    all_noise: List[Dict[str, Any]] = []
    all_data_loss: List[Dict[str, Any]] = []
    all_class: List[Dict[str, Any]] = []
    all_profile: List[Dict[str, Any]] = []
    all_dates: List[Dict[str, Any]] = []
    all_values: List[Dict[str, Any]] = []
    perf: List[Dict[str, Any]] = []
    errors = 0

    for jp in files:
        try:
            block = audit_one_file(jp, args.max_items, skip_pdf=not args.no_skip_pdf)
        except Exception as e:
            errors += 1
            block = {
                "ficheiro": str(jp.relative_to(ROOT)),
                "fonte_pipeline": _infer_source_name(jp),
                "file_error": f"audit_exception:{e}",
                "maturidade_detectada": "quebrado",
            }
        by_source.append(block)
        all_noise.extend(block.get("noise_passou_transformer") or [])
        all_data_loss.extend(block.get("data_loss_examples") or [])
        all_class.extend(block.get("classification_flag_examples") or [])
        all_profile.extend(block.get("profile_flag_examples") or [])
        all_dates.extend(block.get("date_flag_examples") or [])
        all_values.extend(block.get("value_flag_examples") or [])
        perf.append(
            {
                "fonte": block.get("fonte_pipeline"),
                "tempo_ms": block.get("tempo_ms"),
                "amostra": block.get("itens_brutos_amostra"),
            }
        )

    empty_rank = _aggregate_empty_ranking(by_source)
    score_rep = _grep_score_legacy()

    total_items = sum(b.get("itens_brutos_amostra") or 0 for b in by_source)
    tested_sources = sum(1 for b in by_source if (b.get("itens_brutos_amostra") or 0) > 0)

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "max_items_por_ficheiro": args.max_items,
        "ficheiros_json_encontrados": len(_discover_json_files()),
        "ficheiros_processados": len(by_source),
        "fontes_com_amostra_positiva": tested_sources,
        "itens_analisados_total": total_items,
        "erros_audit_exception": errors,
        "pdf_skip": not args.no_skip_pdf,
    }

    (out_dir / "audit_summary.json").write_text(
        json.dumps({**summary, "ranking_campos_vazios": empty_rank}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _write_technical_report(
        out_dir,
        summary,
        by_source,
        all_noise,
        all_data_loss,
        all_class,
        all_profile,
        all_dates,
        all_values,
        score_rep,
        empty_rank,
    )
    (out_dir / "audit_by_source.json").write_text(
        json.dumps(by_source, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_noise_examples.json").write_text(
        json.dumps(all_noise[:200], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_empty_fields.json").write_text(
        json.dumps(empty_rank, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_data_loss_examples.json").write_text(
        json.dumps(all_data_loss[:150], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    dup_report = {
        "por_fonte": [
            {
                "fonte": b.get("fonte_pipeline"),
                "dup_links_bruto": b.get("duplicados_link_bruto"),
                "dup_links_transformado": b.get("duplicados_link_transformados"),
            }
            for b in by_source
        ]
    }
    (out_dir / "audit_duplicates.json").write_text(
        json.dumps(dup_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_classification_issues.json").write_text(
        json.dumps(all_class[:120], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_profile_issues.json").write_text(
        json.dumps(all_profile[:120], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    loader_payload = [b.get("loader_primeiro") for b in by_source if b.get("loader_primeiro")]
    (out_dir / "audit_loader_payload.json").write_text(
        json.dumps(loader_payload[:120], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_performance.json").write_text(
        json.dumps(sorted(perf, key=lambda x: x.get("tempo_ms") or 0, reverse=True)[:40], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "audit_score_legacy.json").write_text(
        json.dumps(score_rep, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    matrix = [_build_matrix_row(b) for b in by_source]
    (out_dir / "audit_matrix_crawlers.json").write_text(
        json.dumps(matrix, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md_lines = [
        "# Resumo da auditoria (dry-run)",
        "",
        "## Interpretação (importante)",
        "- **Ruído que passou = 0** não prova ausência de ruído no mundo real: só significa que, na amostra, nenhum título da lista negra entrou como aceite.",
        "- Com **`--no-skip-pdf` desligado** (default), muitos itens perdem sinais de PDF e o **`opportunity_gate`** pode rejeitar mais — o contador **«quebrado»** mistura *crawler vazio*, *gate agressivo* e *amostra pequena*; **não** implica «consertar N crawlers».",
        "- Rejeições **«login/autenticação»** podem ser páginas inúteis **ou** falsos positivos; o gate foi afinado para **suprimir login fraco** em `gov.br`/bancos públicos quando há contexto de chamada/edital ou descrição longa (ver `CORE/opportunity_gate.py`).",
        "- Para isolar **loader vs transformer**, use **`--only-loader`** sobre `*_standardized.json`.",
        "- Para PDF real só em poucas fontes: **`--no-skip-pdf --sources fonte1,fonte2`**.",
        "- Para tirar score/relevância do caminho crítico no transformer: **`EDITALFINDER_SKIP_SCORING=true`**.",
        "",
        f"- Ficheiros processados: **{len(by_source)}**",
        f"- Itens analisados (amostra): **{total_items}** (máx. {args.max_items} por ficheiro)",
        f"- Fontes com dados na amostra: **{tested_sources}**",
        f"- PDFs na auditoria: **{'desativados (skip)' if not args.no_skip_pdf else 'ativos'}**",
        "",
        "## Matriz (resumo)",
        "",
        "| Crawler | Categoria | Status | Qualidade | Ruído |",
        "|---------|-----------|--------|-----------|-------|",
    ]
    for row in matrix[:40]:
        md_lines.append(
            f"| {row.get('Crawler')} | {row.get('Categoria')} | {row.get('Status')} | "
            f"{row.get('Qualidade')} | {row.get('Ruído')} |"
        )
    if len(matrix) > 40:
        md_lines.append(f"| … | … | *+{len(matrix) - 40} linhas em audit_matrix_crawlers.json* | … | … |")
    md_lines.extend(
        [
            "",
            "## Ruído que passou o transformer",
            f"Total registos: **{len(all_noise)}** (ver `audit_noise_examples.json`).",
            "",
            "## Top correções sugeridas (automático)",
            "1. Rever fontes classificadas como **ruidoso** ou **quebrado** em `audit_by_source.json`.",
            "2. Reduzir campos vazios nas fontes no topo de `audit_empty_fields.json`.",
            "3. Tratar perdas PDF/descrição em `audit_data_loss_examples.json`.",
            "4. Afinar `tipo_recurso` para crédito (BNDES/BRDE/Caixa) com base nos exemplos de classificação.",
            "5. Inferir `perfil_ideal` para fontes estratégicas listadas em `audit_profile_issues.json`.",
            "6. Corrigir datas/prazo vs `situacao` nos casos de `audit_classification_issues.json` / datas.",
            "7. Rever duplicados de link no mesmo JSON (`audit_duplicates.json`).",
            "8. Planejar deprecação de score/relevância com base em `audit_score_legacy.json`.",
            "",
            "Detalhe completo das 22 secções pedidas: consolidar a partir dos JSON em `audit_reports/` + este ficheiro.",
        ]
    )
    (out_dir / "audit_summary.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"[audit] Relatórios em {out_dir} ({len(by_source)} ficheiros, {total_items} itens).")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
