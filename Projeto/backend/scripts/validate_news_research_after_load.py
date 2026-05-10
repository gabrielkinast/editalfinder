#!/usr/bin/env python3
"""
Validação pós-carga news/research contra Supabase (staging).

Compara contagens e integridade aos payloads em audit_reports_news_research_loader/.
Apenas SELECT (leituras via cliente Supabase). Não altera dados.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOADER_DIR = ROOT / "audit_reports_news_research_loader"

# (source, wave) suportados
ALLOWED_COMBOS = frozenset(
    {
        ("nasa_news", "nasa_wave2"),
        ("darpa_news", "darpa_news_wave1"),
        ("iaea_news_publications", "iaea_wave1"),
        ("eurekalert_science_filtered", "eurekalert_wave1"),
    }
)

# `rejected` é opcional (auditoria: links que não devem ter sido carregados).
WAVE_PRESETS: Dict[str, Dict[str, str]] = {
    "nasa_wave2": {
        "noticia": "nasa_wave2_payload_noticia.json",
        "pesquisa": "nasa_wave2_payload_pesquisa.json",
        "review": "nasa_wave2_review_candidates.json",
    },
    "darpa_news_wave1": {
        "noticia": "darpa_news_wave1_payload_noticia.json",
        "pesquisa": "darpa_news_wave1_payload_pesquisa.json",
        "review": "darpa_news_wave1_review_candidates.json",
    },
    "iaea_wave1": {
        "noticia": "iaea_wave1_payload_noticia.json",
        "pesquisa": "iaea_wave1_payload_pesquisa.json",
        "review": "iaea_wave1_review_candidates.json",
        "rejected": "iaea_wave1_rejected.json",
    },
    "eurekalert_wave1": {
        "noticia": "eurekalert_wave1_payload_noticia.json",
        "pesquisa": "eurekalert_wave1_payload_pesquisa.json",
        "review": "eurekalert_wave1_review_candidates.json",
        "rejected": "eurekalert_wave1_rejected.json",
    },
}


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _chunks(seq: Sequence[str], size: int) -> List[List[str]]:
    return [list(seq[i : i + size]) for i in range(0, len(seq), size)]


def _output_paths(in_dir: Path, wave: str) -> Tuple[Path, Path]:
    stem = f"{wave}_post_load_validation"
    return in_dir / f"{stem}.json", in_dir / f"{stem}.md"


def _report_title(source: str, wave: str) -> str:
    if wave == "nasa_wave2":
        return "NASA Wave 2 — validação pós-carga"
    if wave == "darpa_news_wave1":
        return "DARPA News Wave 1 — validação pós-carga"
    if wave == "iaea_wave1":
        return "IAEA Wave 1 — validação pós-carga"
    if wave == "eurekalert_wave1":
        return "EurekAlert Wave 1 — validação pós-carga"
    return f"{source} / {wave} — validação pós-carga"


def _links_from_payload_rows(rows: Any) -> List[str]:
    out: List[str] = []
    if not isinstance(rows, list):
        return out
    for x in rows:
        if isinstance(x, dict):
            lk = str(x.get("link") or "").strip()
            if lk:
                out.append(lk)
    return out


def _extras_tipo_pesquisa_incoerente(extras: Any) -> bool:
    """True se extras sugere tipo_pesquisa em registo que deve ser só notícia."""
    if not isinstance(extras, dict):
        return False
    v = extras.get("tipo_pesquisa")
    if v is None:
        return False
    if isinstance(v, str):
        return bool(v.strip())
    return True


def _is_str_array_bad(v: Any) -> bool:
    if v is None:
        return False
    return isinstance(v, str)


def _array_ok(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, list):
        return all(isinstance(x, (str, int, float)) or x is None for x in v)
    return False


CONFIG_NEWS_SOURCES = ROOT / "config" / "news_research_sources.json"


def _eurekalert_source_status_experimental() -> Tuple[bool, str]:
    """Fonte deve estar marcada como experimental_* em config."""
    cfg = _load_json(CONFIG_NEWS_SOURCES, {})
    for s in cfg.get("sources") or []:
        if isinstance(s, dict) and str(s.get("id") or "") == "eurekalert_science_filtered":
            st = str(s.get("status") or "").strip()
            ok = "experimental" in st.lower()
            return ok, st
    return False, ""


def _eurekalert_bio_agro_taxonomy_ok(row: Dict[str, Any]) -> bool:
    """
    Se extras.defense_semantica == biologica_agro, não deve haver marcadores de defesa militar
    em setor_estrategico / area_tecnologica.
    """
    ex = row.get("extras")
    if not isinstance(ex, dict):
        return True
    if ex.get("defense_semantica") != "biologica_agro":
        return True
    militar_terms = ("defesa", "militar", "dual-use", "dual use", "pentagon", "darpa", "warfighter")
    for fld in ("setor_estrategico", "area_tecnologica"):
        arr = row.get(fld)
        if not isinstance(arr, list):
            continue
        blob = " ".join(str(x).lower() for x in arr if x is not None)
        for t in militar_terms:
            if t in blob:
                return False
    return True


def _connect_supabase():
    from supabase import create_client

    url = os.getenv("SUPABASE_URL", "").strip()
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.getenv("SUPABASE_KEY", "").strip()
        or os.getenv("SUPABASE_ANON_KEY", "").strip()
    )
    if not url or not key:
        raise RuntimeError("SUPABASE_URL ou chave Supabase em falta após carregar env.")
    return create_client(url, key)


def _fetch_by_links(
    client: Any, table_or_view: str, links: List[str], columns: str, chunk: int = 80
) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for part in _chunks(links, chunk):
        if not part:
            continue
        r = client.table(table_or_view).select(columns).in_("link", part).execute()
        data = getattr(r, "data", None) or []
        if isinstance(data, list):
            out.extend([x for x in data if isinstance(x, dict)])
    return out


def _edital_overlap_count(client: Any, links: List[str], chunk: int = 60) -> int:
    n = 0
    for part in _chunks(links, chunk):
        if not part:
            continue
        r = client.table("edital").select("link", count="exact").in_("link", part).execute()
        data = getattr(r, "data", None) or []
        n += len(data) if isinstance(data, list) else 0
    return n


def _view_sample(client: Any, view: str, limit: int = 5) -> Tuple[bool, str, int]:
    try:
        r = client.table(view).select("link").limit(limit).execute()
        data = getattr(r, "data", None) or []
        if not isinstance(data, list):
            return False, "resposta_nao_lista", 0
        return True, "", len(data)
    except Exception as exc:
        return False, str(exc), 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Validação pós-carga news/research no Supabase (apenas SELECT).")
    ap.add_argument("--staging", action="store_true", help="Carrega .env.staging com prioridade.")
    ap.add_argument("--source", default="nasa_news", help="ex.: nasa_news, eurekalert_science_filtered")
    ap.add_argument("--wave", default="nasa_wave2", help="ex.: nasa_wave2, eurekalert_wave1")
    ap.add_argument("--input-dir", default=str(DEFAULT_LOADER_DIR))
    args = ap.parse_args()

    wave = str(args.wave or "").strip()
    source = str(args.source or "").strip()
    in_dir = Path(args.input_dir)

    if (source, wave) not in ALLOWED_COMBOS:
        print(
            f"Combinação não suportada: source={source!r} wave={wave!r}. "
            f"Opções: {sorted(ALLOWED_COMBOS)}",
            file=sys.stderr,
        )
        return 2

    preset = WAVE_PRESETS.get(wave)
    if not preset:
        print(f"Preset em falta para wave={wave!r}", file=sys.stderr)
        return 2

    out_json, out_md = _output_paths(in_dir, wave)

    path_n = in_dir / preset["noticia"]
    path_p = in_dir / preset["pesquisa"]
    path_rev = in_dir / preset.get("review", "")
    path_rej: Optional[Path] = (in_dir / preset["rejected"]) if preset.get("rejected") else None
    raw_n = _load_json(path_n, [])
    raw_p = _load_json(path_p, [])
    raw_rev = _load_json(path_rev, []) if path_rev and path_rev.is_file() else []
    raw_rej = _load_json(path_rej, []) if path_rej and path_rej.is_file() else []
    if not isinstance(raw_n, list) or not isinstance(raw_p, list):
        print(f"Payloads inválidos: {path_n} / {path_p}", file=sys.stderr)
        return 2
    if path_rev and path_rev.is_file() and not isinstance(raw_rev, list):
        raw_rev = []
    if path_rej and path_rej.is_file() and not isinstance(raw_rej, list):
        raw_rej = []

    expected_n = len(raw_n)
    expected_p = len(raw_p)
    expected_rev = len(raw_rev) if isinstance(raw_rev, list) else 0
    expected_rej = len(raw_rej) if isinstance(raw_rej, list) else 0
    links_n = [str(x.get("link") or "").strip() for x in raw_n if isinstance(x, dict) and str(x.get("link") or "").strip()]
    links_p = [str(x.get("link") or "").strip() for x in raw_p if isinstance(x, dict) and str(x.get("link") or "").strip()]
    set_n, set_p = set(links_n), set(links_p)
    overlap = sorted(set_n & set_p)

    last_summary_path = in_dir / "load_news_research_summary.json"
    last_summary = _load_json(last_summary_path, {})

    if args.staging:
        env_staging = ROOT / ".env.staging"
        if env_staging.is_file():
            load_dotenv(dotenv_path=env_staging, override=True)
        os.environ.setdefault("EDITALFINDER_ENV", "staging")

    checks: List[Dict[str, Any]] = []
    ok_all = True

    def add_check(name: str, ok: bool, detail: Any) -> None:
        nonlocal ok_all
        if not ok:
            ok_all = False
        checks.append({"name": name, "ok": ok, "detail": detail})

    add_check("payload_links_noticia_unicos", len(links_n) == len(set_n), {"count": len(links_n), "unique": len(set_n)})
    add_check("payload_links_pesquisa_unicos", len(links_p) == len(set_p), {"count": len(links_p), "unique": len(set_p)})
    add_check("payload_sem_overlap_noticia_pesquisa", len(overlap) == 0, {"overlap": overlap})
    add_check(
        "review_payload_legivel",
        (not path_rev) or (path_rev.is_file() and isinstance(raw_rev, list)),
        {"path": str(path_rev) if path_rev else "", "count": expected_rev},
    )
    add_check(
        "rejected_payload_legivel",
        (not preset.get("rejected")) or (path_rej is not None and path_rej.is_file() and isinstance(raw_rej, list)),
        {
            "path": str(path_rej.resolve()) if path_rej and path_rej.is_file() else "",
            "count": expected_rej,
        },
    )

    try:
        client = _connect_supabase()
    except Exception as exc:
        add_check("supabase_conexao", False, str(exc))
        report = {
            "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "staging_flag": bool(args.staging),
            "source": source,
            "wave": wave,
            "ok": False,
            "checks": checks,
            "erro_fatal": str(exc),
        }
        in_dir.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        title = _report_title(source, wave)
        out_md.write_text(
            f"# {title}\n\n**Falha:** sem ligação ao Supabase.\n\n```json\n"
            + json.dumps(report, ensure_ascii=False, indent=2)
            + "\n```\n",
            encoding="utf-8",
        )
        return 1

    add_check("supabase_conexao", True, "cliente criado (apenas leituras)")

    last_wave = (last_summary or {}).get("wave")
    last_src = (last_summary or {}).get("source")
    last_would_n = (last_summary or {}).get("would_upsert_noticia")
    last_would_p = (last_summary or {}).get("would_upsert_pesquisa")
    loader_summary_alignment = {
        "path": str(last_summary_path.resolve()) if last_summary_path.is_file() else str(last_summary_path),
        "alinhado": last_wave == wave and last_src == source and last_would_n == expected_n and last_would_p == expected_p,
        "wave_ficheiro": last_wave,
        "source_ficheiro": last_src,
        "would_upsert_noticia": last_would_n,
        "would_upsert_pesquisa": last_would_p,
        "expected_noticia": expected_n,
        "expected_pesquisa": expected_p,
        "nota": "Referência ao último load_news_research_summary.json; pode não coincidir se a última execução foi outra fonte/onda.",
    }

    cols_n = "link,resumo,data_publicacao,extras,area_cientifica,area_tecnologica,setor_estrategico,tags"
    cols_p = "link,descricao,data_publicacao,extras,area_cientifica,area_tecnologica,setor_estrategico,tags,fonte_recurso"
    cols_link_only = "link"

    rows_n = _fetch_by_links(client, "noticia", links_n, cols_n)
    rows_p = _fetch_by_links(client, "pesquisa", links_p, cols_p)

    fetched_n = {str(r.get("link") or "").strip(): r for r in rows_n}
    fetched_p = {str(r.get("link") or "").strip(): r for r in rows_p}

    missing_n = sorted(set_n - set(fetched_n.keys()))
    missing_p = sorted(set_p - set(fetched_p.keys()))

    add_check(
        "noticia_count_igual_esperado",
        len(fetched_n) == expected_n,
        {"esperado": expected_n, "encontrados": len(fetched_n), "missing": missing_n[:50], "missing_total": len(missing_n)},
    )
    add_check(
        "pesquisa_count_igual_esperado",
        len(fetched_p) == expected_p,
        {"esperado": expected_p, "encontrados": len(fetched_p), "missing": missing_p[:50], "missing_total": len(missing_p)},
    )

    bad_date_n: List[str] = []
    bad_resumo_n: List[str] = []
    bad_extras_n: List[str] = []
    bad_array_n: List[str] = []
    bad_noticia_extras_tipo_pesquisa: List[str] = []

    for lk, row in fetched_n.items():
        if not row.get("data_publicacao"):
            bad_date_n.append(lk)
        rs = str(row.get("resumo") or "").strip()
        if len(rs) < 1:
            bad_resumo_n.append(lk)
        ex = row.get("extras")
        if ex is None or not isinstance(ex, dict):
            bad_extras_n.append(lk)
        elif _extras_tipo_pesquisa_incoerente(ex):
            bad_noticia_extras_tipo_pesquisa.append(lk)
        for ak in ("area_cientifica", "area_tecnologica", "setor_estrategico", "tags"):
            if _is_str_array_bad(row.get(ak)):
                bad_array_n.append(f"{lk}:{ak}")
            elif row.get(ak) is not None and not _array_ok(row.get(ak)):
                bad_array_n.append(f"{lk}:{ak}:tipo")

    bad_date_p: List[str] = []
    bad_desc_p: List[str] = []
    bad_extras_p: List[str] = []
    bad_array_p: List[str] = []

    for lk, row in fetched_p.items():
        if not row.get("data_publicacao"):
            bad_date_p.append(lk)
        ds = str(row.get("descricao") or "").strip()
        if len(ds) < 1:
            bad_desc_p.append(lk)
        ex = row.get("extras")
        if ex is None or not isinstance(ex, dict):
            bad_extras_p.append(lk)
        for ak in ("area_cientifica", "area_tecnologica", "setor_estrategico", "tags"):
            if _is_str_array_bad(row.get(ak)):
                bad_array_p.append(f"{lk}:{ak}")
            elif row.get(ak) is not None and not _array_ok(row.get(ak)):
                bad_array_p.append(f"{lk}:{ak}:tipo")

    add_check("noticia_data_publicacao_preenchida", len(bad_date_n) == 0, {"bad": bad_date_n[:30], "count": len(bad_date_n)})
    add_check("noticia_resumo_preenchido", len(bad_resumo_n) == 0, {"bad": bad_resumo_n[:30], "count": len(bad_resumo_n)})
    add_check("noticia_extras_jsonb_objeto", len(bad_extras_n) == 0, {"bad": bad_extras_n[:30], "count": len(bad_extras_n)})
    add_check("noticia_arrays_nao_string", len(bad_array_n) == 0, {"bad": bad_array_n[:40], "count": len(bad_array_n)})
    add_check(
        "noticia_sem_tipo_pesquisa_incoerente_em_extras",
        len(bad_noticia_extras_tipo_pesquisa) == 0,
        {"bad": bad_noticia_extras_tipo_pesquisa[:30], "count": len(bad_noticia_extras_tipo_pesquisa)},
    )

    add_check("pesquisa_data_publicacao_preenchida", len(bad_date_p) == 0, {"bad": bad_date_p[:30], "count": len(bad_date_p)})
    add_check("pesquisa_descricao_preenchida", len(bad_desc_p) == 0, {"bad": bad_desc_p[:30], "count": len(bad_desc_p)})
    add_check("pesquisa_extras_jsonb_objeto", len(bad_extras_p) == 0, {"bad": bad_extras_p[:30], "count": len(bad_extras_p)})
    add_check("pesquisa_arrays_nao_string", len(bad_array_p) == 0, {"bad": bad_array_p[:40], "count": len(bad_array_p)})

    all_links = list(set_n | set_p)
    edital_hits = _edital_overlap_count(client, all_links)
    add_check("nenhum_link_payload_em_public_edital", edital_hits == 0, {"edital_rows_matching_links": edital_hits})

    links_review = _links_from_payload_rows(raw_rev)
    links_rej = _links_from_payload_rows(raw_rej)
    review_overlap_payload = sorted(set(links_review) & (set_n | set_p))
    rejected_overlap_payload = sorted(set(links_rej) & (set_n | set_p))
    add_check(
        "review_candidates_nao_sobrepoe_payload_de_carga",
        len(review_overlap_payload) == 0,
        {"overlap": review_overlap_payload},
    )
    add_check(
        "rejected_nao_sobrepoe_payload_de_carga",
        len(rejected_overlap_payload) == 0,
        {"overlap": rejected_overlap_payload},
    )

    review_loaded_db: List[str] = []
    for lk in links_review:
        if not lk.startswith("http"):
            continue
        n_hit = _fetch_by_links(client, "noticia", [lk], "link")
        p_hit = _fetch_by_links(client, "pesquisa", [lk], "link")
        if n_hit or p_hit:
            review_loaded_db.append(lk)

    rejected_loaded_db: List[str] = []
    for lk in links_rej:
        if not lk.startswith("http"):
            continue
        n_hit = _fetch_by_links(client, "noticia", [lk], "link")
        p_hit = _fetch_by_links(client, "pesquisa", [lk], "link")
        if n_hit or p_hit:
            rejected_loaded_db.append(lk)

    add_check(
        "review_candidates_ignorados_sem_linha_noticia_nem_pesquisa",
        len(review_loaded_db) == 0,
        {"presentes_na_bd_indevidamente": review_loaded_db[:40], "count": len(review_loaded_db)},
    )
    add_check(
        "rejected_ignorados_sem_linha_noticia_nem_pesquisa",
        len(rejected_loaded_db) == 0,
        {"presentes_na_bd_indevidamente": rejected_loaded_db[:40], "count": len(rejected_loaded_db)},
    )

    if wave == "iaea_wave1":
        add_check(
            "iaea_review_candidates_json_total_2",
            expected_rev == 2,
            {"esperado": 2, "no_ficheiro": expected_rev},
        )
        add_check(
            "iaea_rejected_json_total_24",
            expected_rej == 24,
            {"esperado": 24, "no_ficheiro": expected_rej},
        )

    if wave == "eurekalert_wave1":
        add_check(
            "eurekalert_esperado_0_noticia_3_pesquisa_0_review_0_rejected",
            expected_n == 0 and expected_p == 3 and expected_rev == 0 and expected_rej == 0,
            {
                "noticia_payload": expected_n,
                "pesquisa_payload": expected_p,
                "review_json": expected_rev,
                "rejected_json": expected_rej,
            },
        )
        exp_ok, exp_status = _eurekalert_source_status_experimental()
        add_check(
            "eurekalert_fonte_experimental_em_config",
            exp_ok,
            {"status": exp_status, "config": str(CONFIG_NEWS_SOURCES.resolve())},
        )

        bad_bio_tax: List[str] = []
        for lk, row in fetched_p.items():
            if not _eurekalert_bio_agro_taxonomy_ok(row):
                bad_bio_tax.append(lk)
        add_check(
            "eurekalert_bio_agro_sem_defesa_militar_indevida",
            len(bad_bio_tax) == 0,
            {
                "links": bad_bio_tax,
                "nota": "Quando extras.defense_semantica=biologica_agro, setor/area não devem conter defesa militar/dual-use/Pentagon/etc.",
            },
        )

        bad_fr: List[str] = []
        for lk, row in fetched_p.items():
            fr = str(row.get("fonte_recurso") or "").strip()
            if fr != "eurekalert_science_filtered":
                bad_fr.append(lk)
        add_check(
            "eurekalert_fonte_recurso_bd",
            len(bad_fr) == 0,
            {"esperado": "eurekalert_science_filtered", "links_errados": bad_fr},
        )

        bad_ef: List[str] = []
        for lk, row in fetched_p.items():
            ex = row.get("extras")
            if not isinstance(ex, dict) or not ex.get("eurekalert_filtered"):
                bad_ef.append(lk)
        add_check(
            "eurekalert_extras_eurekalert_filtered",
            len(bad_ef) == 0,
            {"sem_flag": bad_ef},
        )

    if links_n:
        vw_n_links = _fetch_by_links(client, "vw_noticias_front", links_n, cols_link_only)
        got_vw_n = {str(r.get("link") or "").strip() for r in vw_n_links}
        miss_vw_n = sorted(set_n - got_vw_n)
        add_check(
            "vw_noticias_front_contem_todos_links_noticia",
            len(miss_vw_n) == 0 and len(got_vw_n) == len(set_n),
            {"esperado_links": len(set_n), "vistos_na_view": len(got_vw_n), "missing": miss_vw_n[:30]},
        )
    else:
        add_check("vw_noticias_front_contem_todos_links_noticia", True, {"detail": "sem_links_noticia_no_payload"})

    if links_p:
        vw_p_links = _fetch_by_links(client, "vw_pesquisas_front", links_p, cols_link_only)
        got_vw_p = {str(r.get("link") or "").strip() for r in vw_p_links}
        miss_vw_p = sorted(set_p - got_vw_p)
        add_check(
            "vw_pesquisas_front_contem_todos_links_pesquisa",
            len(miss_vw_p) == 0 and len(got_vw_p) == len(set_p),
            {"esperado_links": len(set_p), "vistos_na_view": len(got_vw_p), "missing": miss_vw_p[:30]},
        )
    else:
        add_check("vw_pesquisas_front_contem_todos_links_pesquisa", True, {"detail": "sem_links_pesquisa_no_payload"})

    vw_n_ok, vw_n_err, vw_n_n = _view_sample(client, "vw_noticias_front", 5)
    vw_p_ok, vw_p_err, vw_p_n = _view_sample(client, "vw_pesquisas_front", 5)
    add_check("vw_noticias_front_consultavel", vw_n_ok, {"ok": vw_n_ok, "erro": vw_n_err, "amostra_rows": vw_n_n})
    add_check("vw_pesquisas_front_consultavel", vw_p_ok, {"ok": vw_p_ok, "erro": vw_p_err, "amostra_rows": vw_p_n})

    report: Dict[str, Any] = {
        "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "staging_flag": bool(args.staging),
        "source": source,
        "wave": wave,
        "payload_paths": {
            "noticia": str(path_n.resolve()),
            "pesquisa": str(path_p.resolve()),
            "review": str(path_rev.resolve()) if path_rev else "",
            "rejected": str(path_rej.resolve()) if path_rej and path_rej.is_file() else (str(path_rej) if path_rej else ""),
        },
        "expected_counts": {
            "noticia": expected_n,
            "pesquisa": expected_p,
            "review_candidates_json": expected_rev,
            "rejected_json": expected_rej,
        },
        "ok": ok_all,
        "checks": checks,
        "loader_summary_alignment": loader_summary_alignment,
        "output_paths": {"json": str(out_json.resolve()), "markdown": str(out_md.resolve())},
    }

    in_dir.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    title = _report_title(source, wave)
    lines = [
        f"# {title}",
        "",
        f"- Gerado: `{report['gerado_em']}`",
        f"- Staging: **{args.staging}**",
        f"- Fonte / onda: `{source}` / `{wave}`",
        f"- Resultado global: **{'OK' if ok_all else 'FALHOU'}**",
        "",
        "## Contagens esperadas (payload)",
        "",
        f"- Notícia: **{expected_n}**",
        f"- Pesquisa: **{expected_p}**",
        f"- Review (ficheiro JSON, não carregado pelo loader): **{expected_rev}**",
        f"- Rejected (ficheiro JSON, auditoria): **{expected_rej}**",
        "",
        "## Checks",
        "",
    ]
    for c in checks:
        st = "OK" if c["ok"] else "FALHOU"
        lines.append(f"- **{c['name']}**: {st}")
        if not c["ok"] and c.get("detail") is not None:
            lines.append(f"  - Detalhe: `{json.dumps(c['detail'], ensure_ascii=False)[:500]}`")
    la = report.get("loader_summary_alignment") or {}
    lines.extend(
        [
            "",
            "## Cruze com o último `load_news_research_summary.json`",
            "",
            f"- Alinhado (source + wave + would_upsert): **{la.get('alinhado')}**",
            f"- Ficheiro: `{la.get('path', '')}`",
            "",
            "## Ficheiro JSON",
            "",
            f"- `{out_json.name}`",
            "",
            "```json",
            json.dumps(report, ensure_ascii=False, indent=2)[:12000],
            "```",
            "",
        ]
    )
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({"ok": ok_all, "path": str(out_json)}, ensure_ascii=False))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
