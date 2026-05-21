#!/usr/bin/env python3
"""
Subsets válidos da rodada military_research_expansion para apply staging (sem apply).

Origem: audit_reports_news_research/military_research_expansion_dryrun/standardized/
Gera 4 pastas subset + loader dry-run + consolidado por fonte.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DRYRUN_DIR = ROOT / "audit_reports_news_research" / "military_research_expansion_dryrun"
ORIGIN_STD = DRYRUN_DIR / "standardized"
WINDOW_MONTHS = 12


def _parse_pub_date(s: Any) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _eixo_distribution(items: List[Dict[str, Any]]) -> Dict[str, int]:
    c: Counter = Counter()
    for it in items:
        for e in it.get("eixo_estrategico") or (it.get("extras") or {}).get("eixo_estrategico") or []:
            if e:
                c[str(e)] += 1
    return dict(c.most_common(20))


def _load_origin(source_id: str) -> List[Dict[str, Any]]:
    path = ORIGIN_STD / f"{source_id}_standardized.json"
    if not path.is_file():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def _is_baa_or_review(it: Dict[str, Any]) -> bool:
    ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
    if ex.get("possivel_edital"):
        return True
    if str(ex.get("destino_sugerido") or "").strip() == "Radar/Editais":
        return True
    if ex.get("review_for_edital"):
        return True
    link = str(it.get("link") or "").lower()
    titulo = str(it.get("titulo") or "").lower()
    if "baa" in link or "broad agency announcement" in titulo:
        if "baa" in link or "baa-forms" in link or "/baa" in link:
            return True
    return False


def _filter_noticia_12m(it: Dict[str, Any], min_dt: datetime, fonte: str) -> Tuple[bool, str]:
    fr = str(it.get("fonte_recurso") or "").strip()
    if fr != fonte:
        return False, f"fonte_recurso!={fonte}"
    if str(it.get("validacao_status") or "") != "valido":
        return False, "validacao_status!=valido"
    if str(it.get("tipo_conteudo") or "").strip().lower() != "noticia":
        return False, "tipo_conteudo!=noticia"
    dt = _parse_pub_date(it.get("data_publicacao"))
    if not dt or dt < min_dt:
        return False, "fora_janela_12m_ou_sem_data"
    return True, ""


def _filter_pesquisa_area(it: Dict[str, Any], fonte: str) -> Tuple[bool, str]:
    fr = str(it.get("fonte_recurso") or "").strip()
    if fr != fonte:
        return False, f"fonte_recurso!={fonte}"
    if str(it.get("validacao_status") or "") != "valido":
        return False, "validacao_status!=valido"
    tp = str(it.get("tipo_pesquisa") or "").strip()
    if tp != "area_tecnologica":
        return False, "tipo_pesquisa!=area_tecnologica"
    tr = str(it.get("tipo_recurso") or (it.get("extras") or {}).get("tipo_recurso") or "").strip()
    if tr and tr != "area_tecnologica":
        return False, "tipo_recurso!=area_tecnologica"
    return True, ""


def _filter_pesquisa_arl_resources(it: Dict[str, Any]) -> Tuple[bool, str]:
    fr = str(it.get("fonte_recurso") or "").strip()
    if fr != "arl_resources":
        return False, "fonte_recurso!=arl_resources"
    if str(it.get("validacao_status") or "") != "valido":
        return False, "validacao_status!=valido"
    if str(it.get("tipo_conteudo") or "").strip().lower() != "pesquisa":
        return False, "tipo_conteudo!=pesquisa"
    if _is_baa_or_review(it):
        return False, "baa_ou_review_for_edital"
    if not str(it.get("tipo_pesquisa") or "").strip():
        return False, "tipo_pesquisa_vazio"
    return True, ""


def _prepare_noticia(row: Dict[str, Any], subset_tag: str, display_fonte: str) -> Dict[str, Any]:
    out = dict(row)
    ex = dict(out.get("extras") or {})
    ex["subset"] = subset_tag
    ex["subset_policy"] = "military_research_expansion_apply_controlado"
    out["extras"] = ex
    out["fonte"] = display_fonte
    if not out.get("descricao") and out.get("resumo"):
        out["descricao"] = out["resumo"]
    out.pop("tipo_pesquisa", None)
    return out


def _prepare_pesquisa(row: Dict[str, Any], subset_tag: str, display_fonte: str) -> Dict[str, Any]:
    out = dict(row)
    ex = dict(out.get("extras") or {})
    ex["subset"] = subset_tag
    ex["subset_policy"] = "military_research_expansion_apply_controlado"
    out["extras"] = ex
    out["fonte"] = display_fonte
    if not out.get("descricao") and out.get("resumo"):
        out["descricao"] = out["resumo"]
    if not out.get("tipo_oportunidade"):
        out["tipo_oportunidade"] = "pesquisa_estrategica"
    return out


def _run_subset(
    *,
    source_id: str,
    out_dir_name: str,
    display_fonte: str,
    destino: str,
    filter_fn: Callable[[Dict[str, Any]], Tuple[bool, str]],
    prepare_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    sort_key: Callable[[Dict[str, Any]], Any],
    filtros_doc: Dict[str, Any],
    observacoes: List[str],
    empty_noticia: bool,
    empty_pesquisa: bool,
    min_dt: Optional[datetime] = None,
) -> int:
    out_base = ROOT / "audit_reports_news_research" / out_dir_name
    std_name = f"{source_id}_standardized.json"
    if destino == "public.pesquisa":
        std_out = out_base / "standardized" / std_name
        empty_noticia = True
    else:
        std_out = out_base / "standardized" / std_name
        empty_pesquisa = True

    all_in = _load_origin(source_id)
    validos_origem = sum(1 for it in all_in if str(it.get("validacao_status") or "") == "valido")

    chosen: List[Dict[str, Any]] = []
    rejeitados: List[Dict[str, Any]] = []

    for it in all_in:
        ok, why = filter_fn(it)
        lk = str(it.get("link") or "").strip()
        if not ok:
            rejeitados.append(
                {
                    "link": lk,
                    "titulo": (it.get("titulo") or "")[:120],
                    "fonte_recurso": it.get("fonte_recurso"),
                    "validacao_status": it.get("validacao_status"),
                    "motivo": why,
                }
            )
            continue
        chosen.append(prepare_fn(it))

    chosen.sort(key=sort_key, reverse=True)

    std_out.parent.mkdir(parents=True, exist_ok=True)
    std_out.write_text(json.dumps(chosen, ensure_ascii=False, indent=2), encoding="utf-8")

    if empty_noticia:
        (out_base / f"{source_id}_payload_noticia.json").write_text("[]", encoding="utf-8")
    if empty_pesquisa:
        (out_base / f"{source_id}_payload_pesquisa.json").write_text("[]", encoding="utf-8")
    (out_base / f"{source_id}_review_candidates.json").write_text("[]", encoding="utf-8")

    input_dir_rel = f"audit_reports_news_research/{out_dir_name}"
    load_cmd = [
        sys.executable,
        str(ROOT / "scripts" / "load_news_research_sources.py"),
        "--dry-run",
        "--source",
        source_id,
        "--input-dir",
        input_dir_rel,
    ]
    proc = subprocess.run(load_cmd, cwd=str(ROOT), capture_output=True, text=True)
    if proc.stdout:
        print(proc.stdout)
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        return proc.returncode

    load_summary: Dict[str, Any] = {}
    load_path = out_base / "load_news_research_summary.json"
    if load_path.is_file():
        load_summary = json.loads(load_path.read_text(encoding="utf-8"))

    eixos = _eixo_distribution(chosen)
    consolidado: Dict[str, Any] = {
        "fonte": source_id,
        "nome_exibicao": display_fonte,
        "loader_source_id": source_id,
        "destino": destino,
        "data_execucao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "origem_dryrun": str(DRYRUN_DIR.relative_to(ROOT)).replace("\\", "/"),
        "origem_standardized": str((ORIGIN_STD / std_name).relative_to(ROOT)).replace("\\", "/"),
        "subset_standardized": str(std_out.relative_to(ROOT)).replace("\\", "/"),
        "totais_origem": len(all_in),
        "validos_no_dryrun": validos_origem,
        "filtros": filtros_doc,
        "subset": {
            "escolhidos": len(chosen),
            "rejeitados_na_filtragem": len(rejeitados),
        },
        "loader_dryrun": {
            "comando": " ".join(load_cmd),
            "would_upsert_noticia": load_summary.get("would_upsert_noticia"),
            "would_upsert_pesquisa": load_summary.get("would_upsert_pesquisa"),
            "errors_count": load_summary.get("errors_count"),
            "apply_status": load_summary.get("apply_status"),
            "routing_skipped_count": load_summary.get("routing_skipped_count"),
        },
        "eixos_estrategicos": eixos,
        "itens_excluidos": rejeitados,
        "itens": [
            {
                "titulo": it.get("titulo"),
                "data_publicacao": it.get("data_publicacao"),
                "link": it.get("link"),
                "fonte_recurso": it.get("fonte_recurso"),
                "tipo_pesquisa": it.get("tipo_pesquisa"),
                "tipo_recurso": it.get("tipo_recurso"),
            }
            for it in chosen
        ],
        "observacoes": observacoes + ["Apply não executado nesta tarefa."],
        "apply_staging": {"executado": False},
    }
    if min_dt is not None:
        consolidado["janela_meses"] = WINDOW_MONTHS

    (out_base / "consolidado_subset.json").write_text(
        json.dumps(consolidado, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        f"# {display_fonte} — subset válido (staging)",
        "",
        f"- **Execução:** {consolidado['data_execucao']}",
        f"- **Destino:** `{destino}`",
        f"- **Loader `--source`:** `{source_id}`",
        "",
        "## Loader dry-run",
        "",
        f"- **would_upsert_noticia:** {consolidado['loader_dryrun']['would_upsert_noticia']}",
        f"- **would_upsert_pesquisa:** {consolidado['loader_dryrun']['would_upsert_pesquisa']}",
        f"- **errors_count:** {consolidado['loader_dryrun']['errors_count']}",
        f"- **apply_status:** {consolidado['loader_dryrun']['apply_status']}",
        "",
        "## Contagem",
        "",
        f"| Métrica | Valor |",
        f"|---------|------:|",
        f"| Válidos no dry-run | {validos_origem} |",
        f"| Itens no subset | {len(chosen)} |",
        f"| Excluídos na filtragem | {len(rejeitados)} |",
        "",
        "## Eixos estratégicos",
        "",
    ]
    for k, v in sorted(eixos.items(), key=lambda x: (-x[1], x[0])):
        md.append(f"- `{k}`: {v}")
    if rejeitados:
        md.extend(["", "## Itens excluídos (amostra)", ""])
        for row in rejeitados[:25]:
            md.append(f"- `{row.get('motivo')}` — {(row.get('titulo') or row.get('link') or '')[:90]}")
        if len(rejeitados) > 25:
            md.append(f"- … +{len(rejeitados) - 25} outros (ver consolidado_subset.json)")
    md.extend(["", "## Itens no subset", ""])
    for i, row in enumerate(consolidado["itens"], 1):
        md.append(
            f"{i}. **{row.get('data_publicacao') or '—'}** — "
            f"{(row.get('titulo') or '')[:85]}"
        )
        md.append(f"   - {row.get('link')}")
    md.append("")
    (out_base / "consolidado_subset.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "source": source_id,
                "subset": len(chosen),
                "excluidos": len(rejeitados),
                "would_upsert_noticia": consolidado["loader_dryrun"]["would_upsert_noticia"],
                "would_upsert_pesquisa": consolidado["loader_dryrun"]["would_upsert_pesquisa"],
                "errors_count": consolidado["loader_dryrun"]["errors_count"],
            },
            indent=2,
        )
    )
    return 0


def main() -> int:
    min_dt = datetime.now(timezone.utc) - timedelta(days=30 * WINDOW_MONTHS)
    rc = 0

    rc |= _run_subset(
        source_id="afrl_technology_areas",
        out_dir_name="afrl_technology_areas_subset_valido",
        display_fonte="AFRL",
        destino="public.pesquisa",
        filter_fn=lambda it: _filter_pesquisa_area(it, "afrl_technology_areas"),
        prepare_fn=lambda it: _prepare_pesquisa(
            it, "afrl_technology_areas_valido", "AFRL"
        ),
        sort_key=lambda x: str(x.get("titulo") or ""),
        filtros_doc={
            "fonte_recurso": "afrl_technology_areas",
            "validacao_status": "valido",
            "tipo_pesquisa": "area_tecnologica",
            "tipo_recurso": "area_tecnologica",
            "tipo_oportunidade": "pesquisa_estrategica",
            "excluido": ["review_candidates", "fontes_latentes"],
        },
        observacoes=[
            "Catálogo AFRL Technology Areas (sem data de publicação; catalogo_institucional).",
            "Fonte oficial afrl_technology_areas → public.pesquisa.",
        ],
        empty_noticia=True,
        empty_pesquisa=False,
    )

    rc |= _run_subset(
        source_id="arl_news",
        out_dir_name="arl_news_subset_valido",
        display_fonte="ARL",
        destino="public.noticia",
        filter_fn=lambda it: _filter_noticia_12m(it, min_dt, "arl_news"),
        prepare_fn=lambda it: _prepare_noticia(it, "arl_news_valido_12m", "ARL"),
        sort_key=lambda x: _parse_pub_date(x.get("data_publicacao"))
        or datetime(1970, 1, 1, tzinfo=timezone.utc),
        filtros_doc={
            "fonte_recurso": "arl_news",
            "validacao_status": "valido",
            "tipo_conteudo": "noticia",
            "janela_meses": WINDOW_MONTHS,
            "excluido": ["review_candidates", "fontes_latentes"],
        },
        observacoes=[
            "ARL DEVCOM media center (arl_news) — notícias válidas 12 meses.",
            "Distinto de afrl_news (.af.mil) já aplicado em rodada anterior.",
        ],
        empty_noticia=False,
        empty_pesquisa=True,
        min_dt=min_dt,
    )

    rc |= _run_subset(
        source_id="arl_resources",
        out_dir_name="arl_resources_subset_valido",
        display_fonte="ARL",
        destino="public.pesquisa",
        filter_fn=_filter_pesquisa_arl_resources,
        prepare_fn=lambda it: _prepare_pesquisa(it, "arl_resources_valido", "ARL"),
        sort_key=lambda x: str(x.get("data_publicacao") or ""),
        filtros_doc={
            "fonte_recurso": "arl_resources",
            "validacao_status": "valido",
            "excluido": [
                "baa",
                "review_for_edital",
                "possivel_edital",
                "destino Radar/Editais",
                "review_candidates",
                "fontes_latentes",
            ],
        },
        observacoes=[
            "Recursos ARL (PDF/CRA/portais); tipo_pesquisa/tipo_recurso conforme classificação no dry-run.",
            "BAA e itens review_for_edital excluídos do subset de staging.",
        ],
        empty_noticia=True,
        empty_pesquisa=False,
    )

    rc |= _run_subset(
        source_id="space_force_news",
        out_dir_name="space_force_news_subset_valido",
        display_fonte="U.S. Space Force",
        destino="public.noticia",
        filter_fn=lambda it: _filter_noticia_12m(it, min_dt, "space_force_news"),
        prepare_fn=lambda it: _prepare_noticia(
            it, "space_force_news_valido_12m", "U.S. Space Force"
        ),
        sort_key=lambda x: _parse_pub_date(x.get("data_publicacao"))
        or datetime(1970, 1, 1, tzinfo=timezone.utc),
        filtros_doc={
            "fonte_recurso": "space_force_news",
            "validacao_status": "valido",
            "tipo_conteudo": "noticia",
            "janela_meses": WINDOW_MONTHS,
            "excluido": ["review_candidates", "fontes_latentes"],
        },
        observacoes=[
            "Notícias USSF (spaceforce.mil) via listagem Wayback-first quando live 403.",
        ],
        empty_noticia=False,
        empty_pesquisa=True,
        min_dt=min_dt,
    )

    return min(rc, 1)


if __name__ == "__main__":
    raise SystemExit(main())
