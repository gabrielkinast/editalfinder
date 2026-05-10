#!/usr/bin/env python3
"""
Onda 1 — dry-run de integração apenas nasa_news (sem DB, sem apply).

Reutiliza roteamento e dedupe de dry_run_news_research_loader.py.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
STD_DEFAULT = ROOT / "audit_reports_news_research" / "standardized" / "nasa_news_standardized.json"
OUT_DIR = ROOT / "audit_reports_news_research_loader"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _norm_str_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        s = value.strip()
        return [s] if s else []
    if isinstance(value, (list, tuple, set)):
        out: List[str] = []
        for v in value:
            if v is None:
                continue
            s = str(v).strip()
            if s:
                out.append(s)
        return out
    s = str(value).strip()
    return [s] if s else []


def _norm_documentos(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return []


def _wave1_eligible_noticia(drnl: Any, item: Dict[str, Any]) -> Tuple[bool, str]:
    if drnl._is_generic(item):
        return False, "generico"
    if not drnl._parse_date(item.get("data_publicacao")):
        return False, "sem_data"
    if drnl._missing_summary_flag(item):
        return False, "sem_resumo_suficiente"
    if drnl._validate_arrays(item):
        return False, "array_invalido"
    return True, "ok"


def _wave1_eligible_pesquisa(drnl: Any, item: Dict[str, Any]) -> Tuple[bool, str]:
    if drnl._is_generic(item):
        return False, "generico"
    if not drnl._parse_date(item.get("data_publicacao")):
        return False, "sem_data"
    if drnl._missing_summary_flag(item):
        return False, "sem_descricao_suficiente"
    if drnl._validate_arrays(item):
        return False, "array_invalido"
    return True, "ok"


def _build_noticia_payload(drnl: Any, item: Dict[str, Any]) -> Dict[str, Any]:
    ex = dict(drnl._extras(item))
    ex["nasa_wave"] = 1
    ex["payload_simulado"] = "public.noticia"
    resumo = drnl._summary_blob(item)
    return {
        "titulo": item.get("titulo"),
        "resumo": resumo[:2800] if resumo else None,
        "link": str(item.get("link") or "").strip(),
        "fonte": item.get("fonte"),
        "fonte_recurso": item.get("fonte_recurso") or item.get("fonte"),
        "data_publicacao": item.get("data_publicacao"),
        "pais": item.get("pais"),
        "regiao": item.get("regiao"),
        "idioma_original": item.get("idioma_original") or ex.get("idioma_original"),
        "tipo_conteudo": item.get("tipo_conteudo") or "noticia",
        "area_cientifica": _norm_str_list(item.get("area_cientifica")),
        "area_tecnologica": _norm_str_list(item.get("area_tecnologica")),
        "setor_estrategico": _norm_str_list(item.get("setor_estrategico")),
        "tags": _norm_str_list(item.get("tags")),
        "extras": ex,
        "qualidade_dado": item.get("qualidade_dado"),
        "validacao_status": item.get("validacao_status"),
    }


def _build_pesquisa_payload(drnl: Any, item: Dict[str, Any]) -> Dict[str, Any]:
    ex = dict(drnl._extras(item))
    ex["nasa_wave"] = 1
    ex["payload_simulado"] = "public.pesquisa"
    desc = drnl._summary_blob(item)
    return {
        "titulo": item.get("titulo"),
        "descricao": desc[:2800] if desc else None,
        "link": str(item.get("link") or "").strip(),
        "fonte_recurso": item.get("fonte_recurso") or item.get("fonte"),
        "data_publicacao": item.get("data_publicacao"),
        "tipo_pesquisa": item.get("tipo_pesquisa"),
        "area_cientifica": _norm_str_list(item.get("area_cientifica")),
        "area_tecnologica": _norm_str_list(item.get("area_tecnologica")),
        "setor_estrategico": _norm_str_list(item.get("setor_estrategico")),
        "documentos": _norm_documentos(item.get("documentos")),
        "pdf_url": item.get("pdf_url"),
        "idioma_original": item.get("idioma_original") or ex.get("idioma_original"),
        "pais": item.get("pais"),
        "regiao": item.get("regiao"),
        "tags": _norm_str_list(item.get("tags")),
        "extras": ex,
        "qualidade_dado": item.get("qualidade_dado"),
        "validacao_status": item.get("validacao_status"),
    }


def _validate_payload_noticia(drnl: Any, row: Dict[str, Any]) -> List[str]:
    missing = []
    fake = {**{k: row.get(k) for k in row if k != "extras"}, "extras": row.get("extras") or {}}
    for f in drnl.NOTICIA_FIELDS:
        if f == "extras":
            if not row.get("extras"):
                missing.append(f)
            continue
        if not drnl._field_present(fake, f):
            missing.append(f)
    for k in ("area_cientifica", "area_tecnologica", "setor_estrategico", "tags"):
        v = row.get(k)
        if v is not None and not isinstance(v, list):
            missing.append(f"{k}_nao_e_lista")
    return missing


def _validate_payload_pesquisa(drnl: Any, row: Dict[str, Any]) -> List[str]:
    missing = []
    fake = {**{k: row.get(k) for k in row if k != "extras"}, "extras": row.get("extras") or {}}
    opcionais_vazios_ok = frozenset({"pdf_url"})
    for f in drnl.PESQUISA_FIELDS:
        if f == "extras":
            if not row.get("extras"):
                missing.append(f)
            continue
        if f in opcionais_vazios_ok and row.get(f) in (None, ""):
            continue
        if not drnl._field_present(fake, f):
            missing.append(f)
    for k in ("area_cientifica", "area_tecnologica", "setor_estrategico", "tags", "documentos"):
        v = row.get(k)
        if k == "documentos":
            if v is not None and not isinstance(v, list):
                missing.append("documentos_nao_e_lista")
            continue
        if v is not None and not isinstance(v, list):
            missing.append(f"{k}_nao_e_lista")
    return missing


def main() -> int:
    ap_path = ROOT / "scripts" / "dry_run_news_research_loader.py"
    drnl = _load_module("dry_run_news_research_loader", ap_path)

    import argparse

    p = argparse.ArgumentParser(description="Dry-run Onda 1 nasa_news (sem apply).")
    p.add_argument("--input", default=str(STD_DEFAULT))
    p.add_argument("--output-dir", default=str(OUT_DIR))
    args = p.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    data = drnl._load_json(in_path, [])
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        print(json.dumps({"ok": False, "erro": "json_invalido"}, ensure_ascii=False))
        return 1

    rows: List[Tuple[str, Dict[str, Any]]] = [("nasa_news", it) for it in data if isinstance(it, dict)]
    kept, dedup_removed = drnl._dedupe_by_link(rows)

    review_out: List[Dict[str, Any]] = []
    payload_noticia: List[Dict[str, Any]] = []
    payload_pesquisa: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []
    examples: List[Dict[str, Any]] = []
    campos_faltantes_noticia: List[Dict[str, Any]] = []
    campos_faltantes_pesquisa: List[Dict[str, Any]] = []

    for sid, item in kept:
        routing, motivo = drnl.route_item(sid, item)
        base = {
            "source_id": sid,
            "link": item.get("link"),
            "titulo": item.get("titulo"),
            "data_publicacao": item.get("data_publicacao"),
            "routing_decision": routing,
            "routing_motivo": motivo,
        }
        if routing == "review_for_edital":
            review_out.append(
                {
                    **base,
                    "candidate_for_edital": True,
                    "requires_manual_review": True,
                    "item_standardized": item,
                }
            )
            continue
        if routing == "rejected_noise":
            excluded.append({**base, "motivo_exclusao": "rejected_noise"})
            continue
        if routing == "noticia":
            ok, why = _wave1_eligible_noticia(drnl, item)
            if not ok:
                excluded.append({**base, "motivo_exclusao": f"nao_entra_payload_{why}"})
                continue
            pl = _build_noticia_payload(drnl, item)
            mf = _validate_payload_noticia(drnl, pl)
            if mf:
                campos_faltantes_noticia.append({"link": pl.get("link"), "missing_fields": mf})
                excluded.append({**base, "motivo_exclusao": "campos_faltantes_pos_mapeamento", "missing_fields": mf})
                continue
            payload_noticia.append(pl)
            if len(examples) < 10:
                examples.append({"tipo": "noticia", "titulo": pl.get("titulo"), "link": pl.get("link")})
            continue
        if routing == "pesquisa":
            ok, why = _wave1_eligible_pesquisa(drnl, item)
            if not ok:
                excluded.append({**base, "motivo_exclusao": f"nao_entra_payload_{why}"})
                continue
            pl = _build_pesquisa_payload(drnl, item)
            mf = _validate_payload_pesquisa(drnl, pl)
            if mf:
                campos_faltantes_pesquisa.append({"link": pl.get("link"), "missing_fields": mf})
                excluded.append({**base, "motivo_exclusao": "campos_faltantes_pos_mapeamento", "missing_fields": mf})
                continue
            payload_pesquisa.append(pl)
            if len(examples) < 10:
                examples.append({"tipo": "pesquisa", "titulo": pl.get("titulo"), "link": pl.get("link")})
            continue
        excluded.append({**base, "motivo_exclusao": f"routing_desconhecido_{routing}"})

    links_n = [x.get("link") for x in payload_noticia]
    links_p = [x.get("link") for x in payload_pesquisa]
    assert len(links_n) == len(set(links_n)), "links noticia duplicados"
    assert len(links_p) == len(set(links_p)), "links pesquisa duplicados"
    overlap = set(links_n) & set(links_p)
    assert not overlap, f"overlap noticia/pesquisa: {overlap}"

    apto = not overlap and (len(payload_noticia) + len(payload_pesquisa)) > 0
    for x in payload_noticia:
        if len((x.get("resumo") or "").strip()) < 40:
            apto = False
            break
    for x in payload_pesquisa:
        if len((x.get("descricao") or "").strip()) < 40:
            apto = False
            break
    if excluded:
        apto = False

    report = {
        "data": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fonte": "nasa_news",
        "input_file": str(in_path.resolve()),
        "total_standardized_lido": len(rows),
        "total_apos_dedupe": len(kept),
        "dedupe_removidos": len(dedup_removed),
        "payload_noticia_count": len(payload_noticia),
        "payload_pesquisa_count": len(payload_pesquisa),
        "review_for_edital_count": len(review_out),
        "excluded_count": len(excluded),
        "links_unicos_noticia": len(set(links_n)),
        "links_unicos_pesquisa": len(set(links_p)),
        "apto_staging_futuro": apto and len(excluded) == 0 and (len(payload_noticia) + len(payload_pesquisa)) > 0,
        "apto_staging_motivo": (
            "ok_todos_requisitos_wave1"
            if apto and len(excluded) == 0
            else "rever_exclusoes_ou_review_candidates"
        ),
        "review_for_edital_fora_do_payload": True,
        "nenhum_item_para_edital": True,
        "exemplos": examples,
        "campos_faltantes_noticia": campos_faltantes_noticia,
        "campos_faltantes_pesquisa": campos_faltantes_pesquisa,
        "exclusoes_resumo": excluded[:25],
    }

    (out_dir / "nasa_wave1_review_candidates.json").write_text(
        json.dumps(review_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "nasa_wave1_payload_noticia.json").write_text(
        json.dumps(payload_noticia, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "nasa_wave1_payload_pesquisa.json").write_text(
        json.dumps(payload_pesquisa, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "nasa_wave1_dry_run.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    cmd = (
        "# Comando futuro sugerido (NÃO executar neste ciclo — sem apply / sem Supabase):\n"
        "# Quando existir loader dedicado notícia/pesquisa em staging:\n"
        "#   CORE\\.venv\\Scripts\\python.exe scripts\\<loader_noticia_pesquisa>.py "
        "--input audit_reports_news_research_loader\\nasa_wave1_payload_noticia.json "
        "--table noticia --dry-run\n"
        "#   CORE\\.venv\\Scripts\\python.exe scripts\\<loader_noticia_pesquisa>.py "
        "--input audit_reports_news_research_loader\\nasa_wave1_payload_pesquisa.json "
        "--table pesquisa --dry-run\n"
    )

    md = [
        "# NASA news — Onda 1 (dry-run integração)",
        "",
        f"- Gerado em: `{report['data']}`",
        f"- Entrada: `{report['input_file']}`",
        "- **Sem apply**, sem Supabase, sem `public.edital`.",
        "",
        "## Totais",
        "",
        f"- Itens lidos (standardized): **{report['total_standardized_lido']}**",
        f"- Após dedupe interno: **{report['total_apos_dedupe']}**",
        f"- Removidos no dedupe: **{report['dedupe_removidos']}**",
        f"- Payload `public.noticia`: **{report['payload_noticia_count']}**",
        f"- Payload `public.pesquisa`: **{report['payload_pesquisa_count']}**",
        f"- `review_for_edital` (fora do payload): **{report['review_for_edital_count']}**",
        f"- Excluídos do payload (ruído / gates / campos): **{report['excluded_count']}**",
        "",
        "## Campos faltantes (validação payload)",
        "",
        f"- Notícia: **{len(report['campos_faltantes_noticia'])}** registos com falhas",
        f"- Pesquisa: **{len(report['campos_faltantes_pesquisa'])}** registos com falhas",
        "",
        "## Aptidão staging futuro",
        "",
        f"- **apto_staging_futuro**: `{report['apto_staging_futuro']}`",
        f"- Motivo: {report['apto_staging_motivo']}",
        "",
        "## Exclusões (amostra)",
        "",
        "```json",
        json.dumps(report["exclusoes_resumo"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Exemplos (payload)",
        "",
        "```json",
        json.dumps(examples, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Artefatos",
        "",
        "- `nasa_wave1_payload_noticia.json`",
        "- `nasa_wave1_payload_pesquisa.json`",
        "- `nasa_wave1_review_candidates.json`",
        "- `nasa_wave1_dry_run.json`",
        "",
        "## Comando futuro (não executado)",
        "",
        "```text",
        cmd.strip(),
        "```",
        "",
    ]
    (out_dir / "nasa_wave1_dry_run.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({"ok": True, "report": {k: report[k] for k in report if k != "exclusoes_resumo"}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
