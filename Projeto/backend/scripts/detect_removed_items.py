#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import urlparse

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "CORE"
DEFAULT_REPORT_DIR = ROOT / "audit_reports_main_pipeline"
STD_DIR = ROOT / "audit_reports_retransform" / "standardized"
NEWS_LOADER_DIR = ROOT / "audit_reports_news_research_loader"
KNOWN_REMOVED = ROOT / "audit_reports_credito" / "credito_brasil_onda_a_removed_links.json"
ENV_CANDIDATES = [ROOT / ".env.staging", ROOT / ".env.local", ROOT / ".env", CORE / ".env"]

NOISE_TITLES = (
    "entre em contato",
    "fale conosco",
    "ouvidoria",
    "internet banking",
    "conta pj",
    "conta digital",
    "acesse sua conta",
    "abra sua conta",
    "atendimento",
    "faq",
    "quem somos",
    "trabalhe conosco",
    "menu",
)
UNSTABLE_SOURCES = {
    "china_nsfc",
    "bae_systems_suppliers",
    "fapergs",
    "eurekalert_science_filtered",
    "china_avic",
    "china_norinco",
    "japan_kawasaki_heavy",
}


def _load_env_files() -> List[str]:
    loaded = []
    for p in ENV_CANDIDATES:
        if p.is_file():
            load_dotenv(dotenv_path=p, override=False)
            loaded.append(str(p.resolve()))
    return loaded


def _mask_host(url: str) -> str:
    try:
        host = urlparse(url).hostname or ""
        return host[:3] + "***" + host[-3:] if len(host) > 6 else "***"
    except Exception:
        return "***"


def _guard() -> Tuple[bool, Dict[str, Any]]:
    env = os.getenv("EDITALFINDER_ENV", "").strip().lower()
    url = os.getenv("SUPABASE_URL", "").strip()
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.getenv("SUPABASE_KEY", "").strip()
        or os.getenv("SUPABASE_ANON_KEY", "").strip()
    )
    reason = ""
    if env in ("production", "prod"):
        reason = "environment_marked_production"
    elif env not in ("staging", "local"):
        reason = "invalid_editalfinder_env"
    elif not url:
        reason = "missing_supabase_url"
    elif not key:
        reason = "missing_supabase_key"
    return reason == "", {"editalfinder_env": env, "has_supabase_url": bool(url), "has_key": bool(key), "url_host_masked": _mask_host(url), "block_reason": reason}


def _client() -> Any:
    from supabase import create_client

    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.getenv("SUPABASE_KEY", "").strip()
        or os.getenv("SUPABASE_ANON_KEY", "").strip()
    )
    return create_client(os.getenv("SUPABASE_URL", "").strip(), key)


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _links_from_rows(rows: Any) -> Set[str]:
    out: Set[str] = set()
    if not isinstance(rows, list):
        return out
    for r in rows:
        if isinstance(r, dict):
            link = str(r.get("link") or "").strip()
            if link:
                out.add(link)
    return out


def _source_from_std(path: Path) -> str:
    return path.name.replace("_standardized.json", "")


def _current_links_for_edital(source: str) -> Tuple[Set[str], List[str]]:
    path = STD_DIR / f"{source}_standardized.json"
    data = _load_json(path, [])
    return _links_from_rows(data), [str(path)]


def _payload_files_for(table: str, source: str = "", wave: str = "") -> List[Path]:
    suffix = "noticia" if table == "noticia" else "pesquisa"
    files = sorted(NEWS_LOADER_DIR.glob(f"*_payload_{suffix}.json"))
    if wave:
        files = [p for p in files if p.name.startswith(f"{wave}_") or p.name.startswith(wave.replace("_wave", "_wave"))]
    if source:
        files = [p for p in files if p.name.startswith(source) or source in p.name]
        if not files:
            # Known builders use wave prefix instead of source prefix for some sources.
            source_wave_hints = {
                "nasa_news": "nasa_wave",
                "darpa_news": "darpa_news_wave",
                "iaea_news_publications": "iaea_wave",
                "eurekalert_science_filtered": "eurekalert_wave",
            }
            hint = source_wave_hints.get(source, source)
            files = [p for p in sorted(NEWS_LOADER_DIR.glob(f"*_payload_{suffix}.json")) if p.name.startswith(hint)]
    return files


def _current_links_for_content(table: str, source: str = "", wave: str = "") -> Tuple[Set[str], List[str]]:
    files = _payload_files_for(table, source, wave)
    links: Set[str] = set()
    for p in files:
        links |= _links_from_rows(_load_json(p, []))
    return links, [str(p) for p in files]


def _known_removed_links() -> Set[str]:
    data = _load_json(KNOWN_REMOVED, {})
    out: Set[str] = set()
    for block in (data.get("por_fonte") or {}).values():
        for item in block.get("removidos") or []:
            link = str(item.get("link") or "").strip()
            if link:
                out.add(link)
    return out


def _fetch_active_rows(sbx: Any, table: str, source: str = "") -> Tuple[bool, str, List[Dict[str, Any]]]:
    out: List[Dict[str, Any]] = []
    page = 0
    size = 1000
    try:
        while True:
            q = sbx.table(table).select("*").eq("ativo", True).range(page * size, page * size + size - 1)
            if source:
                q = q.eq("fonte_recurso", source) if table == "edital" else q.eq("fonte_recurso", source)
            r = q.execute()
            data = getattr(r, "data", None) or []
            if not isinstance(data, list) or not data:
                break
            out.extend([x for x in data if isinstance(x, dict)])
            if len(data) < size:
                break
            page += 1
        return True, "", out
    except Exception as exc:
        if source and table in ("noticia", "pesquisa") and "fonte_recurso" in str(exc).lower():
            return _fetch_active_rows_fonte_fallback(sbx, table, source)
        return False, str(exc), []


def _fetch_active_rows_fonte_fallback(sbx: Any, table: str, source: str) -> Tuple[bool, str, List[Dict[str, Any]]]:
    try:
        r = sbx.table(table).select("*").eq("ativo", True).eq("fonte", source).limit(5000).execute()
        return True, "", [x for x in (getattr(r, "data", None) or []) if isinstance(x, dict)]
    except Exception as exc:
        return False, str(exc), []


def _all_sources_from_files(table: str, source_filter: List[str], wave: str) -> List[str]:
    if source_filter:
        return sorted(set(source_filter))
    if table == "edital":
        return sorted(_source_from_std(p) for p in STD_DIR.glob("*_standardized.json"))
    # For content, source discovery from payload names is lossy; default to configured current active source ids.
    cfg = _load_json(ROOT / "config" / "pipeline_sources.json", {})
    waves = ((cfg.get("news_research") or {}).get("active_waves") or [])
    sources = [str(w.get("source") or "").strip() for w in waves if isinstance(w, dict)]
    if wave:
        sources = [str(w.get("source") or "").strip() for w in waves if isinstance(w, dict) and str(w.get("wave") or "") == wave]
    return sorted({s for s in sources if s})


def _source_of_row(row: Dict[str, Any]) -> str:
    return str(row.get("fonte_recurso") or row.get("fonte") or "").strip()


def _confidence(source: str, row: Dict[str, Any], known_removed: Set[str], current_path: List[str]) -> Tuple[str, str]:
    link = str(row.get("link") or "").strip()
    title = str(row.get("titulo") or "").strip().casefold()
    if link in known_removed:
        return "high", "link está em removed_links conhecido"
    if any(n in title for n in NOISE_TITLES):
        return "high", "título contém ruído claro"
    if source in UNSTABLE_SOURCES:
        return "low", "fonte com coleta instável/WAF/falha recente"
    recent = False
    for p in current_path:
        try:
            if time.time() - Path(p).stat().st_mtime < 3 * 24 * 3600:
                recent = True
                break
        except Exception:
            pass
    if recent:
        return "high", "fonte recrawleada/retransformada recentemente e link sumiu"
    return "medium", "link sumiu do payload atual, mas pode ser item expirado/histórico"


def _detect(table: str, sources: List[str], wave: str, sbx: Any) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    candidates: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    known_removed = _known_removed_links()
    for source in sources:
        if table == "edital":
            current_links, refs = _current_links_for_edital(source)
        else:
            current_links, refs = _current_links_for_content(table, source, wave)
        ok, err, rows = _fetch_active_rows(sbx, table, source)
        if not ok:
            errors.append({"table": table, "source": source, "error": err})
            continue
        for row in rows:
            link = str(row.get("link") or "").strip()
            if not link or link in current_links:
                continue
            conf, reason = _confidence(source, row, known_removed, refs)
            candidates.append(
                {
                    "table": table,
                    "source": source or _source_of_row(row),
                    "link": link,
                    "titulo": str(row.get("titulo") or "")[:500],
                    "motivo": reason,
                    "existe_no_banco": True,
                    "existe_no_payload_atual": False,
                    "recomendacao": "deactivate",
                    "confidence": conf,
                    "reference_files": refs,
                }
            )
    return candidates, errors


def _write(report_dir: Path, report: Dict[str, Any]) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "removed_items_candidates.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Candidatos a resíduos antigos",
        "",
        f"- Gerado: `{report['timestamp']}`",
        f"- Ambiente: `{report['environment']}`",
        f"- Tabela: `{report['table']}`",
        f"- Candidatos: **{len(report['removed_candidates'])}**",
        f"- Erros: **{len(report['errors'])}**",
        "",
        "## Candidatos por confiança",
        "",
    ]
    counts = {}
    for c in report["removed_candidates"]:
        counts[c["confidence"]] = counts.get(c["confidence"], 0) + 1
    for k in ("high", "medium", "low"):
        lines.append(f"- {k}: **{counts.get(k, 0)}**")
    lines += ["", "## Exemplos", ""]
    for c in report["removed_candidates"][:80]:
        lines.append(f"- `{c['confidence']}` `{c['table']}` `{c['source']}`: {c['titulo']} - {c['link']}")
    lines += ["", "Nunca recomendar ou executar DELETE. A recomendação operacional é apenas `ativo=false`."]
    (report_dir / "removed_items_candidates.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Detecta resíduos comparando banco ativo com payloads locais atuais (somente SELECT).")
    ap.add_argument("--table", choices=("edital", "noticia", "pesquisa"), required=True)
    ap.add_argument("--source", default="")
    ap.add_argument("--sources", default="")
    ap.add_argument("--wave", default="")
    ap.add_argument("--staging", action="store_true")
    ap.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    args = ap.parse_args()

    env_files = _load_env_files()
    if args.staging:
        os.environ.setdefault("EDITALFINDER_ENV", "staging")
    ok, guard = _guard()
    report_dir = args.report_dir if args.report_dir.is_absolute() else ROOT / args.report_dir
    if not ok:
        report = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "environment": os.getenv("EDITALFINDER_ENV", ""),
            "env_files_loaded": env_files,
            "table": args.table,
            "sources": [],
            "wave": args.wave,
            "removed_candidates": [],
            "errors": [{"reason": guard.get("block_reason")}],
            "environment_guard": guard,
            "mode": "select_only",
        }
        _write(report_dir, report)
        print(json.dumps({"ok": False, "errors": 1, "path": str((report_dir / "removed_items_candidates.json").resolve())}, ensure_ascii=False))
        return 1

    source_filter = [x.strip().lower() for x in (args.sources or args.source).split(",") if x.strip()]
    sources = _all_sources_from_files(args.table, source_filter, args.wave)
    sbx = _client()
    candidates, errors = _detect(args.table, sources, args.wave, sbx)
    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "environment": os.getenv("EDITALFINDER_ENV", ""),
        "env_files_loaded": env_files,
        "table": args.table,
        "sources": sources,
        "wave": args.wave,
        "removed_candidates": candidates,
        "errors": errors,
        "environment_guard": guard,
        "mode": "select_only",
        "recommendations": ["Revisar candidatos high antes de apply.", "Nunca usar DELETE; usar deactivate_removed_items.py para ativo=false."],
    }
    _write(report_dir, report)
    print(json.dumps({"ok": len(errors) == 0, "candidates": len(candidates), "errors": len(errors), "path": str((report_dir / "removed_items_candidates.json").resolve())}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
