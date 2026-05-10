#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from uuid import uuid4
from urllib.parse import urlparse
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

import loader  # noqa: E402
from db import get_safe_connection_diagnostics, test_read_connection  # noqa: E402
from schema import normalizar  # noqa: E402

TRACK_FIELDS = [
    "area",
    "tipo_oportunidade",
    "tipo_recurso",
    "perfil_ideal",
    "publico_alvo",
    "setor_economico",
    "area_cientifica",
    "area_tecnologica",
    "setor_estrategico",
    "validacao_status",
    "qualidade_dado",
]

# Sobrescrita taxonómica explícita (--overwrite-fields): apenas chaves permitidas.
ALLOWED_TAXONOMY_OVERWRITE_FIELDS = frozenset({"setor_estrategico"})
# Nunca permitir substituição directa destes através de --overwrite-fields.
BLOCKED_LOADER_OVERWRITE_FIELDS = frozenset(
    {
        "link",
        "titulo",
        "id",
        "id_edital",
        "fonte_recurso",
        "fonte",
        "prazo_envio",
        "valor_maximo",
        "valor_minimo",
        "valor_total_texto",
        "valor",
        "descricao",
        "hash_deduplicacao",
        "extras",  # v1: demasiado amplo; usar só setor_estrategico.
    }
)


def _parse_overwrite_fields_arg(raw: str) -> Set[str]:
    if not (raw or "").strip():
        return set()
    return {p.strip() for p in raw.split(",") if p.strip()}


def _normalize_setor_key(val: Any) -> Tuple[str, ...]:
    """Normaliza lista/str de setor_estrategico para comparação estável (conjunto ordenado)."""
    if val is None:
        return tuple()
    if isinstance(val, str):
        s = val.strip()
        return (s,) if s else tuple()
    if isinstance(val, (list, tuple, set)):
        out: List[str] = []
        for x in val:
            if x is None:
                continue
            s = str(x).strip()
            if s:
                out.append(s)
        return tuple(sorted(set(out)))
    s = str(val).strip()
    return (s,) if s else tuple()


def _validate_overwrite_fields(parsed: Set[str]) -> Tuple[bool, str]:
    if not parsed:
        return True, ""
    for f in parsed:
        if f in BLOCKED_LOADER_OVERWRITE_FIELDS:
            return False, f"Campo bloqueado para --overwrite-fields: '{f}'."
        if f not in ALLOWED_TAXONOMY_OVERWRITE_FIELDS:
            return (
                False,
                f"Campo '{f}' não permitido. Permitidos: {sorted(ALLOWED_TAXONOMY_OVERWRITE_FIELDS)}",
            )
    return True, ""


def _build_source_readiness(readiness: Dict[str, Any]) -> Dict[str, List[str]]:
    ready = list(readiness.get("fontes_prontas_para_loader") or [])
    blocked = list(readiness.get("fontes_bloqueadas_temporariamente") or [])
    review = list(readiness.get("fontes_para_revisao") or [])
    status_dist = readiness.get("status_distribution") or {}
    ready_n = int(status_dist.get("pronto_para_loader", 0))
    ready_with_notes_n = int(status_dist.get("pronto_com_observacoes", 0))
    ready_main = ready[:ready_n]
    ready_with_notes = ready[ready_n : ready_n + ready_with_notes_n]
    return {
        "ready": sorted(ready_main),
        "ready_with_notes": sorted(ready_with_notes),
        "needs_manual_review": sorted(review),
        "blocked": sorted(blocked),
        "reprocess_after_fix": [],
    }


def _save_source_readiness_config(cfg: Dict[str, List[str]]) -> Path:
    cfg_dir = ROOT / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    path = cfg_dir / "source_readiness.json"
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _merge_readiness_conservative(
    existing: Dict[str, Any], derived: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    União não destrutiva: incorpora listas derivadas do readiness_for_loader.json
    sem remover fontes já presentes no config em disco. Resolve conflitos por prioridade:
    blocked > needs_manual_review > reprocess_after_fix > ready > ready_with_notes.
    """
    keys = ("ready", "ready_with_notes", "blocked", "needs_manual_review", "reprocess_after_fix")

    def _norm_list(v: Any) -> List[str]:
        if not isinstance(v, list):
            return []
        return sorted({str(x).strip().lower() for x in v if str(x).strip()})

    merged: Dict[str, List[str]] = {}
    for k in keys:
        ex = _norm_list(existing.get(k))
        dv = derived.get(k) if isinstance(derived.get(k), list) else []
        dv_l = [str(x).strip().lower() for x in dv if str(x).strip()]
        merged[k] = sorted(set(ex) | set(dv_l))

    blk = set(merged["blocked"])
    rev = set(merged["needs_manual_review"])
    rer = set(merged["reprocess_after_fix"])
    ready = set(merged["ready"]) - blk - rev - rer
    notes = set(merged["ready_with_notes"]) - blk - rev - rer - ready
    return {
        "ready": sorted(ready),
        "ready_with_notes": sorted(notes),
        "blocked": sorted(blk),
        "needs_manual_review": sorted(rev),
        "reprocess_after_fix": sorted(rer),
    }


def _overlay_curated_source_readiness(
    derived: Dict[str, List[str]], curated: Dict[str, Any]
) -> Tuple[Dict[str, List[str]], Dict[str, Any]]:
    """
    Aplica `config/source_readiness.json` como camada operacional curada.

    O readiness derivado vem de auditorias/retransformacoes e pode ficar defasado
    quando uma fonte ja foi corrigida em lote posterior. O config em disco guarda
    a decisao operacional atual; cada fonte presente nele troca de categoria aqui.
    """
    keys = ("ready", "ready_with_notes", "blocked", "needs_manual_review", "reprocess_after_fix")

    def _norm(values: Any) -> List[str]:
        if not isinstance(values, list):
            return []
        return sorted({str(v).strip().lower() for v in values if str(v).strip()})

    out = {k: _norm(derived.get(k)) for k in keys}
    curated_norm = {k: _norm(curated.get(k)) for k in keys}
    curated_sources = {src for values in curated_norm.values() for src in values}

    changes: List[Dict[str, str]] = []
    for src in sorted(curated_sources):
        before = next((k for k in keys if src in out[k]), "")
        after = next((k for k in keys if src in curated_norm[k]), "")
        if not after:
            continue
        for k in keys:
            out[k] = [v for v in out[k] if v != src]
        out[after].append(src)
        if before != after:
            changes.append({"fonte": src, "from": before or "unclassified", "to": after})

    out = {k: sorted(set(v)) for k, v in out.items()}
    report = {
        "applied": bool(curated_sources),
        "curated_sources_total": len(curated_sources),
        "changes_total": len(changes),
        "changes": changes[:200],
        "policy": "config/source_readiness.json overrides derived readiness for sources explicitly listed there.",
    }
    return out, report


def _write_readiness_guard_reports(
    *,
    summary: Dict[str, Any],
    derived_slice: Dict[str, List[str]],
    derived_path: Path,
    guard_dir: Path,
) -> None:
    guard_dir.mkdir(parents=True, exist_ok=True)
    rw = summary.get("readiness_config_write") or {}
    payload = {
        "data_auditoria": summary.get("data_auditoria"),
        "readiness_config_write": rw,
        "readiness_derived_slice_path": str(derived_path.resolve()),
        "derived_slice_counts": {k: len(v) for k, v in derived_slice.items()},
        "policy": (
            "Por defeito load_ready_sources.py não grava config/source_readiness.json. "
            "Use --write-readiness-config para merge conservativo com o ficheiro em disco."
        ),
    }
    (guard_dir / "readiness_config_write_guard.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [
        "# Readiness config — proteção contra escrita destrutiva",
        "",
        "## Política",
        "",
        "- O loader **lê** `readiness_for_loader.json` para calcular `allowed` / `blocked`, mas **não** sobrescreve `config/source_readiness.json` por defeito (dry-run e apply).",
        "- O slice `pronto_para_loader` + `pronto_com_observacoes` é exportado apenas para **relatório derivado** (ver caminho em JSON).",
        "- Com **`--write-readiness-config`**: merge **conservativo** (união + prioridade) e gravação explícita em `config/source_readiness.json`.",
        "",
        "## Última execução (resumo)",
        "",
        f"- `readiness_config_write.written`: **{rw.get('written')}**",
        f"- `readiness_config_write.merge_mode`: `{rw.get('merge_mode', '')}`",
        f"- `readiness_config_write.path`: `{rw.get('path', '')}`",
        f"- Relatório slice derivado: `{derived_path}`",
        "",
    ]
    (guard_dir / "readiness_config_write_guard.md").write_text("\n".join(lines), encoding="utf-8")


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _append_jsonl(path: Path, record: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _save_execution_db(record: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        loader.supabase.table("carga_execucao").insert(record).execute()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    if isinstance(v, (list, dict)) and len(v) == 0:
        return True
    return False


def _source_from_std_file(path: Path) -> str:
    return path.name.replace("_standardized.json", "")


def _norm_canonical_link(u: Any) -> str:
    return str(u or "").strip().rstrip("/").lower()


def _load_source_canonicalization_config(root: Path) -> Dict[str, Any]:
    p = root / "config" / "source_canonicalization.json"
    if not p.is_file():
        return {}
    data = _load_json(p, {})
    return data if isinstance(data, dict) else {}


def _canonical_rank_for_sort(source: str, canon: Dict[str, Any]) -> Tuple[int, str]:
    rank = 10_000
    groups = canon.get("canonical_groups") or {}
    for _gid, g in groups.items():
        if not isinstance(g, dict):
            continue
        can = str(g.get("canonical_source") or "")
        if source == can:
            rank = min(rank, 0)
            continue
        als = g.get("aliases") or []
        if isinstance(als, list) and source in als:
            try:
                idx = int(als.index(source)) + 1
            except ValueError:
                continue
            rank = min(rank, idx)
    return (rank, source)


def _sort_selected_for_canonical(selected: List[Path], canon: Dict[str, Any]) -> List[Path]:
    if not canon.get("canonical_groups"):
        return sorted(selected, key=lambda p: p.name)
    return sorted(selected, key=lambda p: (_canonical_rank_for_sort(_source_from_std_file(p), canon), p.name))


def _collect_claimed_links_by_group(
    input_dir: Path, selected_paths: List[Path], canon: Dict[str, Any]
) -> Dict[str, Set[str]]:
    selected_sources = {_source_from_std_file(p) for p in selected_paths}
    out: Dict[str, Set[str]] = {}
    groups = canon.get("canonical_groups") or {}
    for gid, g in groups.items():
        if not isinstance(g, dict):
            continue
        can = str(g.get("canonical_source") or "")
        if can not in selected_sources:
            continue
        url_contains = str((g.get("match_rules") or {}).get("url_contains") or "")
        std_path = input_dir / f"{can}_standardized.json"
        if not std_path.is_file():
            continue
        raw = _load_json(std_path, [])
        if isinstance(raw, dict):
            raw = [raw]
        claimed: Set[str] = set()
        for it in raw:
            if not isinstance(it, dict):
                continue
            link = str(it.get("link") or "")
            if url_contains and url_contains not in link:
                continue
            claimed.add(_norm_canonical_link(link))
        out[str(gid)] = claimed
    return out


def _canonical_skip_item(
    source: str,
    link_raw: str,
    canon: Dict[str, Any],
    claimed_by_group: Dict[str, Set[str]],
    selected_sources: Set[str],
) -> Tuple[bool, str]:
    if not link_raw.strip():
        return False, ""
    groups = canon.get("canonical_groups") or {}
    for gid, g in groups.items():
        if not isinstance(g, dict):
            continue
        if str(g.get("policy") or "") != "skip_alias_if_canonical_exists":
            continue
        als = g.get("aliases") or []
        if not isinstance(als, list) or source not in als:
            continue
        can = str(g.get("canonical_source") or "")
        if can not in selected_sources:
            continue
        url_contains = str((g.get("match_rules") or {}).get("url_contains") or "")
        if url_contains and url_contains not in link_raw:
            continue
        nl = _norm_canonical_link(link_raw)
        if nl in claimed_by_group.get(str(gid), set()):
            return True, f"group={gid} canonical={can} alias={source}"
    return False, ""


def _doc_format(doc: Dict[str, Any]) -> str:
    fmt = str(doc.get("formato") or "").strip().lower()
    if fmt:
        return fmt
    url = str(doc.get("url") or doc.get("link") or "").strip().lower().split("?", 1)[0]
    if "." in url:
        ext = url.rsplit(".", 1)[-1]
        if ext:
            return ext
    return "outro"


def _docs_from_any(item: Any) -> List[Dict[str, Any]]:
    if isinstance(item, list):
        return [d for d in item if isinstance(d, dict)]
    if isinstance(item, str):
        try:
            parsed = json.loads(item)
            if isinstance(parsed, list):
                return [d for d in parsed if isinstance(d, dict)]
        except Exception:
            return []
    return []


def _docs_metrics(docs: List[Dict[str, Any]]) -> Dict[str, int]:
    total = len(docs)
    if total == 0:
        return {"total": 0, "pdf": 0, "nao_pdf": 0}
    pdf = 0
    for d in docs:
        fmt = _doc_format(d)
        if fmt == "pdf":
            pdf += 1
    return {"total": total, "pdf": pdf, "nao_pdf": max(total - pdf, 0)}


def _aggregate_official_link_metrics(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Agrega métricas official_link_only / access_limited a partir das linhas por fonte."""
    tot_payload = sum(int(r.get("official_link_only_payload") or 0) for r in rows)
    acc_lim = sum(int(r.get("access_limited_items") or 0) for r in rows)
    by_source_raw: Dict[str, int] = {}
    for r in rows:
        fn = str(r.get("fonte") or "").strip()
        if not fn:
            continue
        by_source_raw[fn] = int(r.get("official_link_only_payload") or 0)
    by_source = {
        k: v
        for k, v in sorted(by_source_raw.items(), key=lambda kv: (-kv[1], kv[0]))
        if v > 0
    }
    examples: List[Dict[str, Any]] = []
    for r in rows:
        for ex in r.get("official_link_only_examples") or []:
            if len(examples) >= 40:
                break
            if isinstance(ex, dict):
                examples.append(ex)
        if len(examples) >= 40:
            break
    acr: Counter[str] = Counter()
    for r in rows:
        part = r.get("official_link_only_access_reasons") or {}
        if isinstance(part, dict):
            for k, v in part.items():
                try:
                    acr[str(k)] += int(v or 0)
                except Exception:
                    continue
    access_reason_counts = dict(sorted(acr.items(), key=lambda kv: (-kv[1], kv[0])))
    return {
        "official_link_only_total": tot_payload,
        "access_limited_total": acc_lim,
        "official_link_only_by_source": by_source,
        "official_link_only_examples": examples,
        "access_reason_counts": access_reason_counts,
    }


def _critical_empty_fields(
    mapped: Dict[str, Any],
    extras_out: Dict[str, Any],
    extras_in: Dict[str, Any],
) -> List[str]:
    missing = []
    if _is_empty(mapped.get("titulo")):
        missing.append("titulo")
    if _is_empty(mapped.get("link")):
        missing.append("link")
    if _is_empty(mapped.get("fonte_recurso")):
        missing.append("fonte_recurso")
    if extras_in.get("validacao_status") is not None and _is_empty(extras_out.get("validacao_status")):
        missing.append("validacao_status")
    return missing


def _simulate_source(
    std_path: Path,
    limit: int,
    *,
    canon: Optional[Dict[str, Any]] = None,
    claimed_by_group: Optional[Dict[str, Set[str]]] = None,
    selected_sources: Optional[Set[str]] = None,
    taxonomy_overwrite_keys: Optional[Set[str]] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    source = _source_from_std_file(std_path)
    canon = canon or {}
    claimed_by_group = claimed_by_group or {}
    selected_sources = selected_sources or set()
    raw = _load_json(std_path, [])
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raw = []
    items = [x for x in raw if isinstance(x, dict)]
    if limit > 0:
        items = items[:limit]

    would_upsert = 0
    would_ignore = 0
    canonical_skipped = 0
    mapping_errors = 0
    critical_missing_count = 0
    critical_counter: Counter[str] = Counter()
    payload_examples: List[Dict[str, Any]] = []
    docs_preserved = pdf_preserved = 0
    docs_input_count = pdf_input_count = 0
    docs_lost = 0
    std_docs_non_pdf_items = 0
    payload_docs_non_pdf_items = 0
    non_pdf_lost = 0
    val_status_preserved = qualidade_preserved = 0
    sem_fields_ok = 0
    docs_loss_examples: List[Dict[str, Any]] = []
    field_input: Counter[str] = Counter()
    field_payload: Counter[str] = Counter()
    field_preserved: Counter[str] = Counter()
    canonical_skip_examples: List[Dict[str, Any]] = []
    official_link_only_standardized = 0
    official_link_only_payload = 0
    access_limited_items = 0
    official_link_only_access_reasons: Counter[str] = Counter()
    official_link_only_examples: List[Dict[str, Any]] = []
    destination_counts: Counter[str] = Counter()
    content_route_examples: List[Dict[str, Any]] = []
    taxonomy_diff_count = 0
    taxonomy_overwrite_examples: List[Dict[str, Any]] = []
    taxonomy_preview_errors = 0

    for it in items:
        link_raw = str(it.get("link") or "")
        skip_canon, skip_reason = _canonical_skip_item(
            source, link_raw, canon, claimed_by_group, selected_sources
        )
        if skip_canon:
            canonical_skipped += 1
            if len(canonical_skip_examples) < 30:
                canonical_skip_examples.append(
                    {
                        "fonte": source,
                        "motivo": "canonicalization_skip",
                        "detalhe": skip_reason,
                        "titulo": str(it.get("titulo") or "")[:220],
                        "link": link_raw[:500],
                    }
                )
            continue
        try:
            norm = normalizar(it)
            destination = loader.get_destination_table(norm)
            destination_counts[destination] += 1
            if destination in ("noticia", "pesquisa"):
                payload_content = loader.map_to_content_schema(norm, destination)
                if not payload_content.get("link"):
                    mapping_errors += 1
                    would_ignore += 1
                else:
                    would_upsert += 1
                    if len(content_route_examples) < 20:
                        content_route_examples.append(
                            {
                                "fonte": source,
                                "destination_table": destination,
                                "titulo": str(payload_content.get("titulo") or "")[:220],
                                "link": str(payload_content.get("link") or "")[:420],
                                "content_type": payload_content.get("content_type"),
                            }
                        )
                continue
            mapped, extras = loader.map_to_db_schema(norm)
            payload_full = loader.sanitize_for_postgres({**mapped, "extras": extras})
            payload_db = loader.sanitize_for_postgres(loader._strip_payload({**mapped, "extras": extras}))
        except Exception as exc:
            mapping_errors += 1
            would_ignore += 1
            if len(payload_examples) < 8:
                payload_examples.append(
                    {
                        "fonte": source,
                        "tipo": "erro_mapeamento",
                        "erro": str(exc),
                        "titulo": str(it.get("titulo") or "")[:220],
                        "link": str(it.get("link") or "")[:420],
                    }
                )
            continue

        would_upsert += 1
        ex = payload_full.get("extras") if isinstance(payload_full.get("extras"), dict) else {}
        in_ex = norm.get("extras") if isinstance(norm.get("extras"), dict) else {}

        if taxonomy_overwrite_keys and "setor_estrategico" in taxonomy_overwrite_keys:
            lk = str(mapped.get("link") or "").strip()
            if lk:
                try:
                    existing_row = loader.fetch_edital_by_link(lk)
                    if existing_row:
                        m_def = loader._rebuild_merged_extras(existing_row, ex)
                        m_ow = loader._rebuild_merged_extras(
                            existing_row, ex, taxonomy_replace_keys=taxonomy_overwrite_keys
                        )
                        sd = _normalize_setor_key(m_def.get("setor_estrategico"))
                        so = _normalize_setor_key(m_ow.get("setor_estrategico"))
                        if sd != so:
                            taxonomy_diff_count += 1
                            if len(taxonomy_overwrite_examples) < 25:
                                taxonomy_overwrite_examples.append(
                                    {
                                        "fonte": source,
                                        "titulo": str(payload_full.get("titulo") or "")[:220],
                                        "link": lk[:500],
                                        "setor_pos_merge_default": m_def.get("setor_estrategico"),
                                        "setor_pos_merge_com_overwrite": m_ow.get("setor_estrategico"),
                                        "setor_payload": ex.get("setor_estrategico"),
                                    }
                                )
                except Exception:
                    taxonomy_preview_errors += 1

        raw_std_ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        if str(raw_std_ex.get("extraction_mode") or "") == "official_link_only":
            official_link_only_standardized += 1
        if str(ex.get("extraction_mode") or "") == "official_link_only":
            official_link_only_payload += 1
        vs_item = str(it.get("validacao_status") or "").strip().lower()
        vs_payload = str(payload_full.get("validacao_status") or "").strip().lower()
        vs_ex = str(ex.get("validacao_status") or "").strip().lower()
        lim_ex = str(ex.get("access_status") or "").strip().lower() == "access_limited"
        lim_val = vs_item == "acesso_limitado" or vs_payload == "acesso_limitado" or vs_ex == "acesso_limitado"
        if lim_ex or lim_val:
            access_limited_items += 1
        ar = str(ex.get("access_reason") or "").strip()
        if str(ex.get("extraction_mode") or "") == "official_link_only" or lim_ex or lim_val:
            official_link_only_access_reasons[ar if ar else "(sem access_reason)"] += 1
        if str(ex.get("extraction_mode") or "") == "official_link_only" and len(official_link_only_examples) < 20:
            official_link_only_examples.append(
                {
                    "fonte": source,
                    "titulo": str(payload_full.get("titulo") or "")[:220],
                    "link": str(payload_full.get("link") or "")[:420],
                    "extraction_mode": ex.get("extraction_mode"),
                    "access_status": ex.get("access_status"),
                    "access_reason": ex.get("access_reason"),
                }
            )
        docs_in = _docs_from_any(in_ex.get("documentos")) or _docs_from_any(in_ex.get("anexos")) or _docs_from_any(norm.get("documentos")) or _docs_from_any(norm.get("anexos"))
        docs_out = _docs_from_any(ex.get("documentos")) or _docs_from_any(ex.get("anexos"))
        pdf_in = in_ex.get("pdf_url") or norm.get("pdf_url")
        if docs_in:
            docs_input_count += 1
            in_m = _docs_metrics(docs_in)
            if in_m["nao_pdf"] > 0:
                std_docs_non_pdf_items += 1
        if pdf_in:
            pdf_input_count += 1
        miss = _critical_empty_fields(payload_db, ex, in_ex)
        if miss:
            critical_missing_count += 1
            for m in miss:
                critical_counter[m] += 1

        if docs_in and docs_out:
            docs_preserved += 1
            out_m = _docs_metrics(docs_out)
            if out_m["nao_pdf"] > 0:
                payload_docs_non_pdf_items += 1
        if docs_in and not docs_out:
            docs_lost += 1
            in_m = _docs_metrics(docs_in)
            if in_m["nao_pdf"] > 0:
                non_pdf_lost += 1
            if len(docs_loss_examples) < 12:
                docs_loss_examples.append(
                    {
                        "fonte": source,
                        "titulo": str(payload_full.get("titulo") or "")[:220],
                        "link": str(payload_full.get("link") or "")[:420],
                        "docs_standardized_n": in_m["total"],
                        "docs_payload_n": 0,
                        "docs_standardized_nao_pdf_n": in_m["nao_pdf"],
                        "pdf_url_payload": payload_full.get("pdf_url"),
                    }
                )
        if pdf_in and (ex.get("pdf_url") or payload_full.get("pdf_url")):
            pdf_preserved += 1
        if in_ex.get("validacao_status") and ex.get("validacao_status"):
            val_status_preserved += 1
        if in_ex.get("qualidade_dado") is not None and ex.get("qualidade_dado") is not None:
            qualidade_preserved += 1
        for f in TRACK_FIELDS:
            if f == "tipo_recurso":
                vin = norm.get("tipo_recurso") or in_ex.get("tipo_recurso")
                vout = payload_full.get("tipo_recurso") or ex.get("tipo_recurso")
            else:
                vin = in_ex.get(f)
                vout = ex.get(f)
            if not _is_empty(vin):
                field_input[f] += 1
            if not _is_empty(vout):
                field_payload[f] += 1
            if not _is_empty(vin) and not _is_empty(vout):
                field_preserved[f] += 1
        if ex.get("area") or ex.get("tipo_oportunidade") or ex.get("perfil_ideal"):
            sem_fields_ok += 1

        if len(payload_examples) < 10:
            payload_examples.append(
                {
                    "fonte": source,
                    "titulo": str(payload_full.get("titulo") or "")[:220],
                    "link": str(payload_full.get("link") or "")[:420],
                    "pdf_url": payload_full.get("pdf_url"),
                    "validacao_status": ex.get("validacao_status"),
                    "qualidade_dado": ex.get("qualidade_dado"),
                    "area": ex.get("area"),
                    "tipo_oportunidade": ex.get("tipo_oportunidade"),
                    "tipo_recurso": payload_full.get("tipo_recurso") or ex.get("tipo_recurso"),
                    "perfil_ideal": ex.get("perfil_ideal"),
                    "documentos_n": (
                        len(ex.get("documentos") or [])
                        if isinstance(ex.get("documentos"), list)
                        else len(ex.get("anexos") or [])
                        if isinstance(ex.get("anexos"), list)
                        else 0
                    ),
                    "db_payload_has_extras": isinstance(payload_db.get("extras"), dict),
                    "critical_missing": miss,
                }
            )

    row = {
        "fonte": source,
        "standardized_path": str(std_path.relative_to(ROOT)).replace("\\", "/"),
        "itens_standardized": len(items),
        "would_upsert": would_upsert,
        "would_ignore": would_ignore,
        "mapping_errors": mapping_errors,
        "critical_empty_items": critical_missing_count,
        "critical_empty_fields": dict(critical_counter),
        "docs_input_items": docs_input_count,
        "docs_preserved_items": docs_preserved,
        "documentos_perdidos_no_payload": docs_lost,
        "standardized_com_documentos_nao_pdf": std_docs_non_pdf_items,
        "payload_com_documentos_nao_pdf": payload_docs_non_pdf_items,
        "perda_documentos_nao_pdf": non_pdf_lost,
        "pdf_input_items": pdf_input_count,
        "pdf_preserved_items": pdf_preserved,
        "validacao_status_preserved_items": val_status_preserved,
        "qualidade_dado_preserved_items": qualidade_preserved,
        "semantic_fields_present_items": sem_fields_ok,
        "docs_loss_examples": docs_loss_examples,
        "field_input_non_empty": dict(field_input),
        "field_payload_non_empty": dict(field_payload),
        "field_preserved_non_empty": dict(field_preserved),
        "canonical_skipped": canonical_skipped,
        "canonical_skip_examples": canonical_skip_examples,
        "official_link_only_standardized": official_link_only_standardized,
        "official_link_only_payload": official_link_only_payload,
        "access_limited_items": access_limited_items,
        "official_link_only_access_reasons": dict(official_link_only_access_reasons),
        "official_link_only_examples": official_link_only_examples,
        "destination_counts": dict(destination_counts),
        "content_route_examples": content_route_examples,
        "taxonomy_overwrite_diff_count": taxonomy_diff_count,
        "taxonomy_overwrite_preview_errors": taxonomy_preview_errors,
        "taxonomy_overwrite_examples": taxonomy_overwrite_examples,
    }
    return row, payload_examples


def _mask_host(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    try:
        host = (urlparse(u).hostname or "").strip()
    except Exception:
        host = ""
    if not host:
        return ""
    if len(host) <= 6:
        return host[0] + "***" + host[-1]
    return host[:3] + "***" + host[-3:]


def _truthy_env(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def _confirm_staging_allowed(has_staging_flag: bool) -> Tuple[bool, Dict[str, Any]]:
    url = os.getenv("SUPABASE_URL", "").strip()
    env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
    has_url = bool(url)
    has_service_key = bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip() or os.getenv("SUPABASE_KEY", "").strip())
    has_anon_key = bool(os.getenv("SUPABASE_ANON_KEY", "").strip())
    has_allow_staging_apply = _truthy_env("EDITALFINDER_ALLOW_STAGING_APPLY")
    env_ok = env in ("staging", "local")
    env_prod = env in ("production", "prod")

    block_reason = ""
    if not has_staging_flag:
        block_reason = "missing_staging_flag"
    elif env_prod:
        block_reason = "environment_marked_production"
    elif not env_ok:
        block_reason = "invalid_editalfinder_env"
    elif not has_url:
        block_reason = "missing_supabase_url"
    elif not has_service_key:
        block_reason = "missing_service_key"
    elif not has_allow_staging_apply:
        block_reason = "missing_allow_staging_apply"

    safe = block_reason == ""
    guard = {
        "editalfinder_env": env,
        "has_supabase_url": has_url,
        "has_service_key": has_service_key,
        "has_anon_key": has_anon_key,
        "has_allow_staging_apply": has_allow_staging_apply,
        "url_host_masked": _mask_host(url),
        "block_reason": block_reason,
    }
    return safe, guard


def _apply_source(
    std_path: Path,
    limit: int,
    *,
    canon: Optional[Dict[str, Any]] = None,
    claimed_by_group: Optional[Dict[str, Set[str]]] = None,
    selected_sources: Optional[Set[str]] = None,
    taxonomy_replace_keys: Optional[Set[str]] = None,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
    source = _source_from_std_file(std_path)
    canon = canon or {}
    claimed_by_group = claimed_by_group or {}
    selected_sources = selected_sources or set()
    raw = _load_json(std_path, [])
    if isinstance(raw, dict):
        raw = [raw]
    if not isinstance(raw, list):
        raw = []
    items = [x for x in raw if isinstance(x, dict)]
    if limit > 0:
        items = items[:limit]

    processed = inserted = updated = ignored = errors = canonical_skipped = 0
    routed_noticia = routed_pesquisa = 0
    payload_examples: List[Dict[str, Any]] = []
    err_rows: List[Dict[str, Any]] = []

    for it in items:
        link_raw = str(it.get("link") or "")
        skip_canon, _skip_reason = _canonical_skip_item(
            source, link_raw, canon, claimed_by_group, selected_sources
        )
        if skip_canon:
            canonical_skipped += 1
            continue
        processed += 1
        try:
            item_n = normalizar(it)
            destination = loader.get_destination_table(item_n)
            if destination in ("noticia", "pesquisa"):
                status, row_id = loader.inserir_ou_atualizar_conteudo(
                    destination,
                    loader.map_to_content_schema(item_n, destination),
                )
                if status != "ok":
                    errors += 1
                    err_rows.append(
                        {
                            "fonte": source,
                            "destination_table": destination,
                            "titulo": str(it.get("titulo") or "")[:220],
                            "link": str(it.get("link") or "")[:420],
                            "erro": f"content_upsert_status={status}",
                        }
                    )
                    continue
                if destination == "noticia":
                    routed_noticia += 1
                else:
                    routed_pesquisa += 1
                inserted += 1
                if len(payload_examples) < 10:
                    payload_examples.append(
                        {
                            "fonte": source,
                            "destination_table": destination,
                            "titulo": str(it.get("titulo") or "")[:220],
                            "link": str(it.get("link") or "")[:420],
                            "content_row_id": row_id,
                        }
                    )
                continue
            mapped, extras_new = loader.map_to_db_schema(item_n)
            if not mapped.get("link"):
                ignored += 1
                continue
            existing = loader.fetch_edital_by_link(str(mapped["link"]))
            merged_extras = loader._rebuild_merged_extras(
                existing, extras_new, taxonomy_replace_keys=taxonomy_replace_keys
            )
            payload = loader._merge_db_row(existing, mapped, merged_extras, item_n)
            status, id_edital = loader.inserir_ou_atualizar_edital(payload)
            if not id_edital:
                errors += 1
                err_rows.append(
                    {
                        "fonte": source,
                        "titulo": str(it.get("titulo") or "")[:220],
                        "link": str(it.get("link") or "")[:420],
                        "erro": f"upsert_status={status}",
                    }
                )
                continue
            if existing:
                updated += 1
            else:
                inserted += 1
            loader.save_detail_tables(id_edital, merged_extras)
            if len(payload_examples) < 10:
                payload_examples.append(
                    {
                        "fonte": source,
                        "titulo": str(payload.get("titulo") or "")[:220],
                        "link": str(payload.get("link") or "")[:420],
                        "pdf_url": payload.get("pdf_url"),
                        "extras_has_documentos": isinstance((payload.get("extras") or {}).get("documentos"), list),
                        "extras_has_validacao_status": (payload.get("extras") or {}).get("validacao_status") is not None,
                    }
                )
        except Exception as exc:
            errors += 1
            err_rows.append(
                {
                    "fonte": source,
                    "titulo": str(it.get("titulo") or "")[:220],
                    "link": str(it.get("link") or "")[:420],
                    "erro": str(exc),
                }
            )

    return (
        {
            "fonte": source,
            "processed": processed,
            "inserted": inserted,
            "updated": updated,
            "ignored": ignored,
            "errors": errors,
            "canonical_skipped": canonical_skipped,
            "routed_noticia": routed_noticia,
            "routed_pesquisa": routed_pesquisa,
        },
        payload_examples,
        err_rows,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--check-env-only", action="store_true")
    ap.add_argument("--test-db-before-apply", action="store_true")
    ap.add_argument("--sources", default="")
    ap.add_argument("--exclude-blocked", action="store_true")
    ap.add_argument("--input-dir", default="audit_reports_retransform/standardized")
    ap.add_argument("--readiness", default="audit_reports_retransform/readiness_for_loader.json")
    ap.add_argument(
        "--output-dir",
        default="",
        help="Diretório para load_ready_summary*.json/md (relativo à raiz do repo se não for absoluto). Vazio = audit_reports_loader_ready.",
    )
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument(
        "--write-readiness-config",
        action="store_true",
        help="Grava config/source_readiness.json com merge conservativo sobre o ficheiro em disco (por defeito NÃO grava).",
    )
    ap.add_argument(
        "--overwrite-fields",
        default="",
        metavar="CAMPOS",
        help=(
            "Substitui chaves taxonómicas no merge de extras em vez de união de listas. "
            "Lista separada por vírgulas; v1 apenas: setor_estrategico. "
            "Obrigatório combinar com --sources. Apply real: usar também --apply --staging."
        ),
    )
    args = ap.parse_args()

    overwrite_fields_set = _parse_overwrite_fields_arg(str(getattr(args, "overwrite_fields", "") or ""))
    ok_ow, err_ow = _validate_overwrite_fields(overwrite_fields_set)
    if not ok_ow:
        print(f"[ERRO] {err_ow}", file=sys.stderr)
        return 2
    if overwrite_fields_set and not (args.sources or "").strip():
        print(
            "[ERRO] --overwrite-fields exige --sources (lista explícita de fontes).",
            file=sys.stderr,
        )
        return 2
    taxonomy_overwrite_keys: Optional[Set[str]] = (
        set(overwrite_fields_set) if overwrite_fields_set else None
    )

    input_dir = (ROOT / args.input_dir).resolve() if not Path(args.input_dir).is_absolute() else Path(args.input_dir)
    readiness_path = (ROOT / args.readiness).resolve() if not Path(args.readiness).is_absolute() else Path(args.readiness)
    if str(getattr(args, "output_dir", "") or "").strip():
        od = Path(args.output_dir)
        out_dir = od.resolve() if od.is_absolute() else (ROOT / args.output_dir).resolve()
    else:
        out_dir = (ROOT / "audit_reports_loader_ready").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    history_jsonl = out_dir / "load_execution_history.jsonl"
    exec_id = str(uuid4())
    t0 = time.time()
    env_safe, env_diag = _confirm_staging_allowed(args.staging)
    loader.detect_optional_tables()

    if args.check_env_only:
        db_diag = get_safe_connection_diagnostics()
        guard_report = {
            "editalfinder_env": env_diag.get("editalfinder_env"),
            "has_supabase_url": env_diag.get("has_supabase_url"),
            "has_service_key": env_diag.get("has_service_key"),
            "has_anon_key": env_diag.get("has_anon_key"),
            "has_allow_staging_apply": env_diag.get("has_allow_staging_apply"),
            "url_host_masked": env_diag.get("url_host_masked"),
            "key_name_selected": db_diag.get("key_name_selected"),
            "key_len": db_diag.get("key_len"),
            "key_prefix_masked": db_diag.get("key_prefix_masked"),
            "environment_safe": env_safe,
            "block_reason": env_diag.get("block_reason", ""),
        }
        (out_dir / "environment_guard_check.json").write_text(
            json.dumps(guard_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        md = [
            "# Environment guard check",
            "",
            f"- editalfinder_env: `{guard_report['editalfinder_env']}`",
            f"- has_supabase_url: **{guard_report['has_supabase_url']}**",
            f"- has_service_key: **{guard_report['has_service_key']}**",
            f"- has_anon_key: **{guard_report['has_anon_key']}**",
            f"- has_allow_staging_apply: **{guard_report['has_allow_staging_apply']}**",
            f"- url_host_masked: `{guard_report['url_host_masked']}`",
            f"- key_name_selected: `{guard_report['key_name_selected']}`",
            f"- key_len: **{guard_report['key_len']}**",
            f"- key_prefix_masked: `{guard_report['key_prefix_masked']}`",
            f"- environment_safe: **{guard_report['environment_safe']}**",
            f"- block_reason: `{guard_report['block_reason']}`",
        ]
        (out_dir / "environment_guard_check.md").write_text("\n".join(md), encoding="utf-8")
        _append_jsonl(
            history_jsonl,
            {
                "id_execucao": exec_id,
                "modo": "check_env_only",
                "status": "ok" if env_safe else "blocked",
                "data_inicio": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
                "data_fim": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "duracao_segundos": round(time.time() - t0, 3),
                "environment_guard": guard_report,
            },
        )
        print(out_dir)
        return 0 if env_safe else 1

    readiness = _load_json(readiness_path, {})
    src_cfg = _build_source_readiness(readiness)
    cfg_disk = ROOT / "config" / "source_readiness.json"
    curated_cfg = _load_json(cfg_disk, {})
    if not isinstance(curated_cfg, dict):
        curated_cfg = {}
    src_cfg, readiness_curated_overlay = _overlay_curated_source_readiness(src_cfg, curated_cfg)
    derived_slice_path = out_dir / "readiness_derived_slice.json"
    derived_slice_path.write_text(
        json.dumps(
            {
                "readiness_path": str(readiness_path),
                "source_readiness_config_disk_path": str(cfg_disk.resolve()),
                "curated_overlay": readiness_curated_overlay,
                "slice": src_cfg,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    readiness_config_write: Dict[str, Any] = {
        "written": False,
        "path": "",
        "merge_mode": "none",
    }
    if args.write_readiness_config:
        merged_cfg = _merge_readiness_conservative(curated_cfg, src_cfg)
        wp = _save_source_readiness_config(merged_cfg)
        readiness_config_write = {
            "written": True,
            "path": str(wp.resolve()),
            "merge_mode": "conservative_union_priority",
        }

    allowed_from_readiness = set(src_cfg["ready"]) | set(src_cfg["ready_with_notes"])
    blocked = set(src_cfg["blocked"]) | set(src_cfg["needs_manual_review"]) | set(src_cfg["reprocess_after_fix"])
    requested = {s.strip().lower() for s in args.sources.split(",") if s.strip()} if args.sources.strip() else set()

    std_files = sorted([p for p in input_dir.glob("*_standardized.json") if p.is_file()])
    selected = []
    excluded: List[Dict[str, Any]] = []
    for p in std_files:
        src = _source_from_std_file(p)
        if requested and src not in requested:
            excluded.append({"fonte": src, "reason": "not_in_sources_filter"})
            continue
        if args.exclude_blocked and src in blocked:
            excluded.append({"fonte": src, "reason": "blocked_by_readiness"})
            continue
        if args.exclude_blocked and src not in allowed_from_readiness:
            excluded.append({"fonte": src, "reason": "not_ready_in_readiness"})
            continue
        selected.append(p)

    canon_cfg = _load_source_canonicalization_config(ROOT)
    selected = _sort_selected_for_canonical(selected, canon_cfg)
    claimed_by_group = _collect_claimed_links_by_group(input_dir, selected, canon_cfg)
    selected_sources_set = {_source_from_std_file(p) for p in selected}

    by_source: List[Dict[str, Any]] = []
    payload_examples: List[Dict[str, Any]] = []
    for p in selected:
        row, ex = _simulate_source(
            p,
            args.limit,
            canon=canon_cfg,
            claimed_by_group=claimed_by_group,
            selected_sources=selected_sources_set,
            taxonomy_overwrite_keys=taxonomy_overwrite_keys,
        )
        by_source.append(row)
        payload_examples.extend(ex)

    field_input_tot: Counter[str] = Counter()
    field_payload_tot: Counter[str] = Counter()
    field_preserved_tot: Counter[str] = Counter()
    destination_counts_tot: Counter[str] = Counter()
    for r in by_source:
        for k, v in (r.get("field_input_non_empty") or {}).items():
            field_input_tot[k] += int(v or 0)
        for k, v in (r.get("field_payload_non_empty") or {}).items():
            field_payload_tot[k] += int(v or 0)
        for k, v in (r.get("field_preserved_non_empty") or {}).items():
            field_preserved_tot[k] += int(v or 0)
        for k, v in (r.get("destination_counts") or {}).items():
            destination_counts_tot[str(k)] += int(v or 0)

    overwrite_sources_list = sorted(
        {s.strip().lower() for s in (args.sources or "").split(",") if s.strip()}
    )
    overwritten_fields_total = sum(int(r.get("taxonomy_overwrite_diff_count") or 0) for r in by_source)

    summary = {
        "id_execucao": exec_id,
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": "apply" if args.apply else "dry-run",
        "staging_flag": args.staging,
        "apply_requested": args.apply,
        "taxonomy_overwrite_enabled": bool(taxonomy_overwrite_keys),
        "overwrite_fields": sorted(overwrite_fields_set) if overwrite_fields_set else [],
        "overwrite_sources": overwrite_sources_list,
        "overwritten_fields_count": overwritten_fields_total,
        "input_dir": str(input_dir),
        "readiness_path": str(readiness_path),
        "source_readiness_config_disk_path": str(cfg_disk.resolve()),
        "readiness_derived_slice_path": str(derived_slice_path.resolve()),
        "readiness_curated_overlay": readiness_curated_overlay,
        "readiness_config_write": readiness_config_write,
        "sources_selected": len(by_source),
        "sources_excluded": len(excluded),
        "itens_standardized_total": sum(r["itens_standardized"] for r in by_source),
        "would_upsert_total": sum(r["would_upsert"] for r in by_source),
        "would_ignore_total": sum(r["would_ignore"] for r in by_source),
        "mapping_errors_total": sum(r["mapping_errors"] for r in by_source),
        "critical_empty_items_total": sum(r["critical_empty_items"] for r in by_source),
        "docs_input_items_total": sum(r["docs_input_items"] for r in by_source),
        "docs_preserved_items_total": sum(r["docs_preserved_items"] for r in by_source),
        "documentos_perdidos_no_payload_total": sum(r["documentos_perdidos_no_payload"] for r in by_source),
        "standardized_com_documentos_nao_pdf_total": sum(r["standardized_com_documentos_nao_pdf"] for r in by_source),
        "payload_com_documentos_nao_pdf_total": sum(r["payload_com_documentos_nao_pdf"] for r in by_source),
        "perda_documentos_nao_pdf_total": sum(r["perda_documentos_nao_pdf"] for r in by_source),
        "pdf_input_items_total": sum(r["pdf_input_items"] for r in by_source),
        "pdf_preserved_items_total": sum(r["pdf_preserved_items"] for r in by_source),
        "validacao_status_preserved_items_total": sum(r["validacao_status_preserved_items"] for r in by_source),
        "qualidade_dado_preserved_items_total": sum(r["qualidade_dado_preserved_items"] for r in by_source),
        "fields_input_non_empty_total": dict(field_input_tot),
        "fields_payload_non_empty_total": dict(field_payload_tot),
        "fields_preserved_non_empty_total": dict(field_preserved_tot),
        "destination_counts_total": dict(destination_counts_tot),
        "canonical_skipped_total": sum(int(r.get("canonical_skipped") or 0) for r in by_source),
        "canonicalization_config_path": str((ROOT / "config" / "source_canonicalization.json").resolve())
        if (ROOT / "config" / "source_canonicalization.json").is_file()
        else "",
        "canonical_skip_examples": [
            x for r in by_source for x in (r.get("canonical_skip_examples") or [])
        ][:40],
        "canonical_claimed_links_by_group": {k: len(v) for k, v in claimed_by_group.items()},
    }
    tw_ex_all: List[Dict[str, Any]] = []
    tw_prev_err_tot = 0
    for r in by_source:
        tw_prev_err_tot += int(r.get("taxonomy_overwrite_preview_errors") or 0)
        for x in r.get("taxonomy_overwrite_examples") or []:
            if len(tw_ex_all) < 40:
                tw_ex_all.append(x)
    summary["taxonomy_overwrite_preview_examples"] = tw_ex_all
    summary["taxonomy_overwrite_preview_errors_total"] = tw_prev_err_tot
    summary.update(_aggregate_official_link_metrics(by_source))

    # Segurança: apply só em staging explícito; sem salvar por padrão.
    summary["environment_guard"] = env_diag
    summary["db_connection_diag"] = get_safe_connection_diagnostics()
    apply_status = "not_requested"
    if args.apply:
        if not args.staging:
            apply_status = "blocked_missing_staging_flag"
        elif not env_safe:
            apply_status = "blocked_staging_env_not_confirmed"
        else:
            apply_status = "apply_not_executed_in_this_script_yet"
    summary["apply_status"] = apply_status

    staging_rows: List[Dict[str, Any]] = []
    staging_errors: List[Dict[str, Any]] = []
    staging_payload_examples: List[Dict[str, Any]] = []
    if args.apply and apply_status == "apply_not_executed_in_this_script_yet":
        if args.test_db_before_apply:
            db_ok, db_err = test_read_connection()
            summary["db_precheck"] = {"ok": db_ok, "error": db_err}
            if not db_ok:
                summary["apply_status"] = "blocked_db_precheck_failed"
                (out_dir / "load_ready_summary.json").write_text(
                    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                (out_dir / "load_ready_by_source.json").write_text(json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8")
                (out_dir / "load_ready_payload_examples.json").write_text(
                    json.dumps(payload_examples[:300], ensure_ascii=False, indent=2), encoding="utf-8"
                )
                (out_dir / "load_ready_excluded_sources.json").write_text(json.dumps(excluded, ensure_ascii=False, indent=2), encoding="utf-8")
                _append_jsonl(
                    history_jsonl,
                    {
                        "id_execucao": exec_id,
                        "modo": "apply",
                        "status": "blocked_db_precheck_failed",
                        "data_inicio": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
                        "data_fim": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "duracao_segundos": round(time.time() - t0, 3),
                        "summary": summary,
                    },
                )
                _write_readiness_guard_reports(
                    summary=summary,
                    derived_slice=src_cfg,
                    derived_path=derived_slice_path,
                    guard_dir=out_dir,
                )
                print(out_dir)
                return 1
        for p in selected:
            row, exs, errs = _apply_source(
                p,
                args.limit,
                canon=canon_cfg,
                claimed_by_group=claimed_by_group,
                selected_sources=selected_sources_set,
                taxonomy_replace_keys=taxonomy_overwrite_keys,
            )
            staging_rows.append(row)
            staging_payload_examples.extend(exs)
            staging_errors.extend(errs)
        summary["apply_status"] = "applied_to_staging"
        summary["apply_processed_total"] = sum(r["processed"] for r in staging_rows)
        summary["apply_inserted_total"] = sum(r["inserted"] for r in staging_rows)
        summary["apply_updated_total"] = sum(r["updated"] for r in staging_rows)
        summary["apply_ignored_total"] = sum(r["ignored"] for r in staging_rows)
        summary["apply_errors_total"] = sum(r["errors"] for r in staging_rows)

    (out_dir / "load_ready_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "load_ready_by_source.json").write_text(json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "load_ready_payload_examples.json").write_text(json.dumps(payload_examples[:300], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "load_ready_excluded_sources.json").write_text(json.dumps(excluded, ensure_ascii=False, indent=2), encoding="utf-8")

    docs_loss_examples_all: List[Dict[str, Any]] = []
    for r in by_source:
        docs_loss_examples_all.extend(r.get("docs_loss_examples") or [])
    docs_report = {
        "data_auditoria": summary["data_auditoria"],
        "standardized_com_documentos": summary["docs_input_items_total"],
        "payload_com_documentos": summary["docs_preserved_items_total"],
        "documentos_perdidos_no_payload": summary["documentos_perdidos_no_payload_total"],
        "standardized_com_documentos_nao_pdf": summary["standardized_com_documentos_nao_pdf_total"],
        "payload_com_documentos_nao_pdf": summary["payload_com_documentos_nao_pdf_total"],
        "perda_documentos_nao_pdf": summary["perda_documentos_nao_pdf_total"],
        "pdf_url_input": summary["pdf_input_items_total"],
        "pdf_url_preservado": summary["pdf_preserved_items_total"],
        "exemplos_perda": docs_loss_examples_all[:50],
    }
    (out_dir / "docs_payload_preservation.json").write_text(
        json.dumps(docs_report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    rw = summary.get("readiness_config_write") or {}
    md = [
        "# Loader controlado (dry-run)",
        "",
        f"- Modo: **{summary['mode']}**",
        f"- Apply status: `{summary['apply_status']}`",
        f"- `config/source_readiness.json` escrito: **{rw.get('written')}** (`{rw.get('merge_mode', '')}`)",
        f"- Slice derivado (relatório): `{summary.get('readiness_derived_slice_path', '')}`",
        f"- Fontes selecionadas: **{summary['sources_selected']}**",
        f"- Fontes excluídas: **{summary['sources_excluded']}**",
        f"- Itens standardized: **{summary['itens_standardized_total']}**",
        f"- Destinos: `{summary.get('destination_counts_total', {})}`",
        f"- Upsert simulado: **{summary['would_upsert_total']}**",
        f"- Ignorados simulados: **{summary['would_ignore_total']}**",
        f"- Ignorados por canonização (alias duplicado): **{summary.get('canonical_skipped_total', 0)}**",
        f"- Erros de mapeamento: **{summary['mapping_errors_total']}**",
        "",
        "## Preservação",
        "",
        f"- Itens com documentos na entrada: **{summary['docs_input_items_total']}**",
        f"- Itens com documentos preservados: **{summary['docs_preserved_items_total']}**",
        f"- Itens com documentos perdidos no payload: **{summary['documentos_perdidos_no_payload_total']}**",
        f"- Itens com docs não-PDF no standardized: **{summary['standardized_com_documentos_nao_pdf_total']}**",
        f"- Itens com docs não-PDF no payload: **{summary['payload_com_documentos_nao_pdf_total']}**",
        f"- Perda de docs não-PDF: **{summary['perda_documentos_nao_pdf_total']}**",
        f"- Itens com pdf_url na entrada: **{summary['pdf_input_items_total']}**",
        f"- Itens com pdf_url preservado: **{summary['pdf_preserved_items_total']}**",
        f"- Itens com validacao_status preservado: **{summary['validacao_status_preserved_items_total']}**",
        f"- Itens com qualidade_dado preservada: **{summary['qualidade_dado_preserved_items_total']}**",
        f"- Itens com campos críticos vazios: **{summary['critical_empty_items_total']}**",
        "",
        "## Taxonomia — sobrescrita (`--overwrite-fields`)",
        "",
        f"- taxonomy_overwrite_enabled: **{summary.get('taxonomy_overwrite_enabled')}**",
        f"- overwrite_fields: `{summary.get('overwrite_fields', [])}`",
        f"- overwrite_sources: `{summary.get('overwrite_sources', [])}`",
        f"- overwritten_fields_count (diff merge default vs merge com replace): **{summary.get('overwritten_fields_count', 0)}**",
        f"- taxonomy_overwrite_preview_errors_total: **{summary.get('taxonomy_overwrite_preview_errors_total', 0)}**",
        "",
    ]
    if summary.get("taxonomy_overwrite_enabled"):
        md.append("### Pré-visualização (dry-run com leitura DB para diff)")
        md.append("")
        for ex in (summary.get("taxonomy_overwrite_preview_examples") or [])[:15]:
            if not isinstance(ex, dict):
                continue
            md.append(
                f"- **{ex.get('fonte')}** — {str(ex.get('titulo') or '')[:80]} — "
                f"default=`{ex.get('setor_pos_merge_default')}` → overwrite=`{ex.get('setor_pos_merge_com_overwrite')}`"
            )
        md.append("")
    md.extend(
        [
        "## Official link only (auditoria)",
        "",
        f"- official_link_only_total (`extras.extraction_mode` no payload pós-mapeamento): **{summary.get('official_link_only_total', 0)}**",
        f"- Itens standardized com `extras.extraction_mode == official_link_only` (pré-simulação): **{sum(int(r.get('official_link_only_standardized') or 0) for r in by_source)}**",
        f"- access_limited_total (`access_status == access_limited` ou `validacao_status` acesso_limitado): **{summary.get('access_limited_total', 0)}**",
        "",
        "### official_link_only_by_source",
        "",
        ]
    )
    olo_by = summary.get("official_link_only_by_source") or {}
    if olo_by:
        for fn, cnt in olo_by.items():
            md.append(f"- `{fn}`: **{cnt}**")
    else:
        md.append("- *(nenhum item com extraction_mode official_link_only no payload)*")
    md.extend(
        [
            "",
            "### access_reason_counts",
            "",
        ]
    )
    arc = summary.get("access_reason_counts") or {}
    if arc:
        for k, v in arc.items():
            md.append(f"- `{k}`: **{v}**")
    else:
        md.append("- *(vazio)*")
    md.extend(
        [
            "",
            "### official_link_only_examples",
            "",
        ]
    )
    for ex in (summary.get("official_link_only_examples") or [])[:20]:
        if not isinstance(ex, dict):
            continue
        md.append(
            f"- **{ex.get('fonte')}** — {str(ex.get('titulo') or '')[:120]} — "
            f"`access_reason={ex.get('access_reason')}` — link=`{str(ex.get('link') or '')[:90]}`"
        )
    if not (summary.get("official_link_only_examples") or []):
        md.append("- *(nenhum)*")
    md.extend(
        [
            "",
            "## Fontes excluídas",
            "",
        ]
    )
    for e in excluded[:80]:
        md.append(f"- {e['fonte']}: {e['reason']}")
    (out_dir / "load_ready_summary.md").write_text("\n".join(md), encoding="utf-8")

    docs_md = [
        "# Preservação de documentos no payload",
        "",
        f"- standardized_com_documentos: **{docs_report['standardized_com_documentos']}**",
        f"- payload_com_documentos: **{docs_report['payload_com_documentos']}**",
        f"- documentos_perdidos_no_payload: **{docs_report['documentos_perdidos_no_payload']}**",
        f"- standardized_com_documentos_nao_pdf: **{docs_report['standardized_com_documentos_nao_pdf']}**",
        f"- payload_com_documentos_nao_pdf: **{docs_report['payload_com_documentos_nao_pdf']}**",
        f"- perda_documentos_nao_pdf: **{docs_report['perda_documentos_nao_pdf']}**",
        f"- pdf_url_input: **{docs_report['pdf_url_input']}**",
        f"- pdf_url_preservado: **{docs_report['pdf_url_preservado']}**",
        "",
        "## Exemplos de perda",
        "",
    ]
    for ex in docs_report["exemplos_perda"][:20]:
        docs_md.append(
            f"- {ex.get('fonte')}: docs_std={ex.get('docs_standardized_n')} "
            f"docs_payload={ex.get('docs_payload_n')} nao_pdf_std={ex.get('docs_standardized_nao_pdf_n')} "
            f"link={ex.get('link')}"
        )
    if not docs_report["exemplos_perda"]:
        docs_md.append("- Nenhuma perda detectada.")
    (out_dir / "docs_payload_preservation.md").write_text("\n".join(docs_md), encoding="utf-8")

    # Relatórios finais específicos solicitados.
    if not args.apply:
        (out_dir / "final_dry_run_before_staging.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_dir / "final_dry_run_before_staging.md").write_text(
            (out_dir / "load_ready_summary.md").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    else:
        staging_summary = {
            "data_auditoria": summary.get("data_auditoria"),
            "apply_status": summary.get("apply_status"),
            "staging_flag": args.staging,
            "environment_safe": env_safe,
            "environment_guard": env_diag,
            "official_link_only_total": summary.get("official_link_only_total", 0),
            "access_limited_total": summary.get("access_limited_total", 0),
            "official_link_only_by_source": summary.get("official_link_only_by_source", {}),
            "official_link_only_examples": (summary.get("official_link_only_examples") or [])[:40],
            "access_reason_counts": summary.get("access_reason_counts", {}),
            "sources_selected": summary.get("sources_selected", 0),
            "sources_excluded": summary.get("sources_excluded", 0),
            "total_fontes_carregadas": len([r for r in staging_rows if (r.get("inserted", 0) + r.get("updated", 0)) > 0]),
            "total_itens_processados": sum(r.get("processed", 0) for r in staging_rows),
            "inseridos": sum(r.get("inserted", 0) for r in staging_rows),
            "atualizados": sum(r.get("updated", 0) for r in staging_rows),
            "ignorados": sum(r.get("ignored", 0) for r in staging_rows),
            "erros": sum(r.get("errors", 0) for r in staging_rows),
            "fontes_excluidas": excluded,
            "fields_preserved_non_empty_total": summary.get("fields_preserved_non_empty_total", {}),
            "blocked_sources_loaded": [
                r.get("fonte")
                for r in staging_rows
                if r.get("fonte") in blocked and (r.get("inserted", 0) + r.get("updated", 0)) > 0
            ],
        }
        (out_dir / "staging_load_summary.json").write_text(
            json.dumps(staging_summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_dir / "staging_load_by_source.json").write_text(
            json.dumps(staging_rows, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_dir / "staging_load_errors.json").write_text(
            json.dumps(staging_errors[:500], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_dir / "staging_load_payload_examples.json").write_text(
            json.dumps(staging_payload_examples[:300], ensure_ascii=False, indent=2), encoding="utf-8"
        )
        top_fontes = sorted(staging_rows, key=lambda x: x.get("processed", 0), reverse=True)[:10]
        md_stage = [
            "# Staging load summary",
            "",
            f"- apply_status: `{staging_summary['apply_status']}`",
            f"- environment_safe: **{staging_summary['environment_safe']}**",
            f"- total_fontes_carregadas: **{staging_summary['total_fontes_carregadas']}**",
            f"- total_itens_processados: **{staging_summary['total_itens_processados']}**",
            f"- inseridos: **{staging_summary['inseridos']}**",
            f"- atualizados: **{staging_summary['atualizados']}**",
            f"- ignorados: **{staging_summary['ignorados']}**",
            f"- erros: **{staging_summary['erros']}**",
            "",
            "## Top fontes por itens",
            "",
        ]
        for r in top_fontes:
            md_stage.append(
                f"- {r.get('fonte')}: processed={r.get('processed')} inserted={r.get('inserted')} updated={r.get('updated')} errors={r.get('errors')}"
            )
        md_stage.extend(
            [
                "",
                "## Official link only (auditoria)",
                "",
                f"- official_link_only_total: **{staging_summary.get('official_link_only_total', 0)}**",
                f"- access_limited_total: **{staging_summary.get('access_limited_total', 0)}**",
                "",
            ]
        )
        if staging_summary["blocked_sources_loaded"]:
            md_stage.append("")
            md_stage.append("## ALERTA")
            md_stage.append(f"- Fontes bloqueadas carregadas: {staging_summary['blocked_sources_loaded']}")
        (out_dir / "staging_load_summary.md").write_text("\n".join(md_stage), encoding="utf-8")

        post_validation = {
            "executed": summary.get("apply_status") == "applied_to_staging",
            "apply_status": summary.get("apply_status"),
            "environment_safe": env_safe,
            "records_processed": sum(r.get("processed", 0) for r in staging_rows),
            "records_inserted_or_updated": sum((r.get("inserted", 0) + r.get("updated", 0)) for r in staging_rows),
            "blocked_sources_loaded": staging_summary["blocked_sources_loaded"],
            "duplicates_check": "not_executed" if summary.get("apply_status") != "applied_to_staging" else "pending_manual_sql_validation",
            "critical_empty_check": summary.get("critical_empty_items_total", 0),
            "docs_preservation_check": {
                "docs_input_items_total": summary.get("docs_input_items_total", 0),
                "docs_preserved_items_total": summary.get("docs_preserved_items_total", 0),
                "pdf_preserved_items_total": summary.get("pdf_preserved_items_total", 0),
            },
        }
        (out_dir / "post_staging_validation.json").write_text(
            json.dumps(post_validation, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        md_post = [
            "# Post staging validation",
            "",
            f"- executed: **{post_validation['executed']}**",
            f"- apply_status: `{post_validation['apply_status']}`",
            f"- environment_safe: **{post_validation['environment_safe']}**",
            f"- records_processed: **{post_validation['records_processed']}**",
            f"- records_inserted_or_updated: **{post_validation['records_inserted_or_updated']}**",
            f"- blocked_sources_loaded: **{len(post_validation['blocked_sources_loaded'])}**",
            f"- duplicates_check: `{post_validation['duplicates_check']}`",
            "",
            "## Preservação",
            f"- docs_input_items_total: **{post_validation['docs_preservation_check']['docs_input_items_total']}**",
            f"- docs_preserved_items_total: **{post_validation['docs_preservation_check']['docs_preserved_items_total']}**",
            f"- pdf_preserved_items_total: **{post_validation['docs_preservation_check']['pdf_preserved_items_total']}**",
        ]
        (out_dir / "post_staging_validation.md").write_text("\n".join(md_post), encoding="utf-8")

    # Histórico local sempre.
    end_ts = time.time()
    exec_record_local = {
        "id_execucao": exec_id,
        "ambiente": env_diag.get("editalfinder_env") or ("staging" if args.staging else "unknown"),
        "status": summary.get("apply_status"),
        "data_inicio": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t0)),
        "data_fim": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(end_ts)),
        "duracao_segundos": round(end_ts - t0, 3),
        "fontes_carregadas": len([r for r in staging_rows if (r.get("inserted", 0) + r.get("updated", 0)) > 0]) if args.apply else 0,
        "fontes_excluidas": len(excluded),
        "itens_processados": summary.get("apply_processed_total", summary.get("would_upsert_total", 0)),
        "itens_inseridos": summary.get("apply_inserted_total", 0),
        "itens_atualizados": summary.get("apply_updated_total", 0),
        "itens_ignorados": summary.get("apply_ignored_total", summary.get("would_ignore_total", 0)),
        "erros": summary.get("apply_errors_total", summary.get("mapping_errors_total", 0)),
        "fontes": [r.get("fonte") for r in by_source],
        "fontes_excluidas_detalhe": excluded,
        "blocked_sources_loaded": (
            [r.get("fonte") for r in staging_rows if r.get("fonte") in blocked and (r.get("inserted", 0) + r.get("updated", 0)) > 0]
            if args.apply
            else []
        ),
        "environment_guard": env_diag,
        "relatorio_json": {"summary_path": str((out_dir / "load_ready_summary.json"))},
    }
    _append_jsonl(history_jsonl, exec_record_local)

    # Persistência opcional em tabela carga_execucao (se existir).
    db_record = {
        "id_execucao": exec_id,
        "ambiente": exec_record_local["ambiente"],
        "status": exec_record_local["status"] or "",
        "data_inicio": exec_record_local["data_inicio"],
        "data_fim": exec_record_local["data_fim"],
        "duracao_segundos": exec_record_local["duracao_segundos"],
        "fontes_carregadas": exec_record_local["fontes_carregadas"],
        "fontes_excluidas": exec_record_local["fontes_excluidas"],
        "itens_processados": exec_record_local["itens_processados"],
        "itens_inseridos": exec_record_local["itens_inseridos"],
        "itens_atualizados": exec_record_local["itens_atualizados"],
        "itens_ignorados": exec_record_local["itens_ignorados"],
        "erros": exec_record_local["erros"],
        "fontes": exec_record_local["fontes"],
        "fontes_excluidas_detalhe": exec_record_local["fontes_excluidas_detalhe"],
        "blocked_sources_loaded": exec_record_local["blocked_sources_loaded"],
        "environment_guard": exec_record_local["environment_guard"],
        "relatorio_json": {
            "summary": summary,
            "db_connection_diag": summary.get("db_connection_diag"),
        },
    }
    ok_db, err_db = _save_execution_db(db_record)
    summary["carga_execucao_db"] = {"saved": ok_db, "error": err_db}
    (out_dir / "load_ready_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    _write_readiness_guard_reports(
        summary=summary,
        derived_slice=src_cfg,
        derived_path=derived_slice_path,
        guard_dir=out_dir,
    )

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
