#!/usr/bin/env python3
"""
Auditoria de métodos de acesso públicos por fonte (sem contornar WAF/captcha/login).

Saídas:
  audit_reports_access/source_access_summary.{md,json}
  audit_reports_access/source_access_by_source.json

Uso:
  python scripts/audit_source_access_methods.py
  python scripts/audit_source_access_methods.py --sources iarpa,sam_gov
  python scripts/audit_source_access_methods.py --readiness config/source_readiness.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import requests

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from source_access_utils import (  # noqa: E402
    cache_http_response,
    classify_html_response,
    detect_cloudflare_response,
    discover_feeds,
    discover_official_documents,
    extract_json_ld,
    extract_meta_tags,
    extract_open_graph,
    fetch_robots_txt,
    fetch_sitemap_urls,
    polite_get,
    recommend_safe_method,
    robots_can_fetch,
)

OUT_DIR = ROOT / "audit_reports_access"
POLICY_PATH = ROOT / "config" / "source_access_policy.json"
READINESS_PATH = ROOT / "config" / "source_readiness.json"


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _discover_seed_urls_from_repo(fonte: str, limit: int = 5) -> List[str]:
    folder = ROOT / fonte
    if not folder.is_dir():
        return []
    found: List[str] = []
    for path in sorted(folder.glob("main*.py")):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in re.finditer(r"https?://[^\s\"\'\)\]\>]+", text):
            u = m.group(0).rstrip(".,);")
            if any(x in u.lower() for x in ("example.com", "localhost", "{", "}")):
                continue
            if u not in found:
                found.append(u)
            if len(found) >= limit:
                return found
    return found


def _target_sources(args: argparse.Namespace) -> List[str]:
    if args.sources:
        return sorted({s.strip().lower() for s in args.sources.split(",") if s.strip()})
    readiness = _load_json(Path(args.readiness), {})
    pol = _load_json(Path(args.policy), {})
    policy_fontes = {str(k).strip().lower() for k in (pol.get("fontes") or {}).keys()}
    out: Set[str] = set()
    out |= policy_fontes
    for bucket in ("blocked", "needs_manual_review", "reprocess_after_fix"):
        for s in readiness.get(bucket) or []:
            out.add(str(s).strip().lower())
    if args.include_ready:
        for bucket in ("ready", "ready_with_notes"):
            for s in readiness.get(bucket) or []:
                out.add(str(s).strip().lower())
    return sorted(out)


def _audit_seed(
    fonte: str,
    seed_url: str,
    sess,
    cache_dir: Path,
    timeout: float,
    sleep_between: float,
) -> Dict[str, Any]:
    robots = fetch_robots_txt(seed_url, timeout=timeout, sleep_between=sleep_between, session=sess)
    raw_lines = robots.get("raw_lines") or []
    disallow: Optional[bool] = None
    if raw_lines:
        disallow = robots_can_fetch(raw_lines, seed_url) is False
    r_main = None
    err_main: Optional[str] = None
    if disallow is True:
        cls = "robots_disallow"
        body = ""
    else:
        r_main, err_main = polite_get(
            seed_url,
            timeout=timeout,
            max_retries=1,
            sleep_between=sleep_between,
            session=sess,
        )
        cls = classify_html_response(seed_url, r_main, err_main, robots_disallows=disallow)

    body = (r_main.text if r_main and r_main.text else "") or ""
    body_snip = body[:4000]
    signals: Dict[str, Any] = {
        "rss_found": False,
        "sitemap_ok": False,
        "json_ld_types": [],
        "meta_keys": [],
        "open_graph_keys": [],
        "document_links_n": 0,
    }
    feeds: List[Dict[str, str]] = []
    sm: Dict[str, Any] = {}
    jld: List[Dict[str, Any]] = []
    meta: Dict[str, str] = {}
    og: Dict[str, str] = {}
    docs: List[str] = []
    if r_main is not None and r_main.status_code == 200 and body and cls in (
        "ok_html_publico",
        "spa_pouco_html",
        "captcha",
        "login_required",
    ):
        feeds = discover_feeds(body, seed_url)
        signals["rss_found"] = len(feeds) > 0
        sm = fetch_sitemap_urls(seed_url, robots.get("sitemap_hints") or [], timeout=timeout, session=sess)
        for block in sm.get("checked") or []:
            if block.get("ok") and int(block.get("loc_count_sample") or 0) > 0:
                signals["sitemap_ok"] = True
                break
        jld = extract_json_ld(body)
        signals["json_ld_types"] = [x.get("@type") for x in jld if x.get("@type")]
        meta = extract_meta_tags(body)
        signals["meta_keys"] = sorted(meta.keys())[:40]
        og = extract_open_graph(body)
        signals["open_graph_keys"] = sorted(og.keys())[:25]
        docs = discover_official_documents(body, seed_url)
        signals["document_links_n"] = len(docs)

    probe_alt: List[Dict[str, Any]] = []
    rec = {
        "seed_url": seed_url,
        "robots": {k: v for k, v in robots.items() if k != "raw_lines"},
        "robots_disallows_url": bool(disallow) if disallow is not None else None,
        "primary_probe": {
            "status_code": getattr(r_main, "status_code", None),
            "final_url": getattr(r_main, "url", None),
            "bytes": len(body.encode("utf-8")) if body else 0,
            "cloudflare_headers": bool(r_main and detect_cloudflare_response(r_main)),
            "fetch_error": err_main,
        },
        "primary_classification": cls,
        "feeds": feeds[:12],
        "sitemap": sm,
        "json_ld_sample": jld[:8],
        "meta_sample": dict(list(meta.items())[:20]),
        "open_graph_sample": dict(list(og.items())[:12]),
        "document_links_sample": docs[:15],
        "signals": signals,
        "probe_alternatives": probe_alt,
    }
    cache_http_response(
        seed_url,
        {
            "fonte": fonte,
            "classification": cls,
            "status": rec["primary_probe"]["status_code"],
        },
        cache_dir=cache_dir,
    )
    return rec


def _optional_probes(
    urls: List[str],
    sess,
    timeout: float,
    sleep_between: float,
) -> tuple[List[Dict[str, Any]], bool]:
    """GET opcionais declarados na política (páginas públicas alternativas)."""
    rows: List[Dict[str, Any]] = []
    json_ok = False
    for u in urls:
        r, err = polite_get(u, timeout=timeout, max_retries=1, sleep_between=sleep_between, session=sess)
        ct = (r.headers.get("Content-Type") or "").lower() if r is not None else ""
        is_json = "json" in ct and r is not None and r.status_code == 200
        if is_json:
            json_ok = True
        rows.append(
            {
                "url": u,
                "status_code": getattr(r, "status_code", None),
                "error": err,
                "content_type": ct[:80] if ct else None,
                "bytes": len((r.text or "").encode("utf-8")) if r and r.text else 0,
            }
        )
    return rows, json_ok


def audit_fonte(
    fonte: str,
    policy: Dict[str, Any],
    sess,
    cache_dir: Path,
    timeout: float,
    sleep_between: float,
) -> Dict[str, Any]:
    pol_fontes = policy.get("fontes") or {}
    entry = pol_fontes.get(fonte) or {}
    seeds = list(entry.get("seed_urls") or [])
    if not seeds:
        seeds = _discover_seed_urls_from_repo(fonte, limit=3)
    if not seeds:
        return {
            "fonte": fonte,
            "policy_entry": entry,
            "seed_urls": [],
            "primary_classification": "fonte_sem_dados",
            "recommended_method": "revisar_manualmente",
            "readiness_access_tag": "blocked_access_limited",
            "interpretacao_crawler": "sem_url_seed_configurada",
            "probes": [],
            "optional_probes": [],
        }

    probes = [_audit_seed(fonte, seeds[0], sess, cache_dir, timeout, sleep_between)]
    cls = probes[0]["primary_classification"]
    opt_urls = list(entry.get("optional_safe_get_urls") or [])
    optional_rows: List[Dict[str, Any]] = []
    json_ok = False
    if opt_urls:
        optional_rows, json_ok = _optional_probes(opt_urls, sess, timeout, sleep_between)

    if json_ok and entry.get("allowed_methods") and "usar_api_publica" in entry["allowed_methods"]:
        cls = "api_publica_disponivel"

    sig = dict(probes[0].get("signals") or {})
    if cls in ("cloudflare_403", "endpoint_quebrado", "spa_pouco_html") and optional_rows:
        if any((x.get("status_code") == 200 and int(x.get("bytes") or 0) > 500) for x in optional_rows):
            sig["alternate_public_page_ok"] = True

    rec_method = recommend_safe_method(cls, sig)
    if entry.get("allowed_methods") and rec_method == "blocked_access_limited":
        if "official_curated_links" in entry["allowed_methods"]:
            rec_method = "usar_curadoria_oficial_minima"

    readiness_tag = (
        "blocked_access_limited"
        if cls in ("cloudflare_403", "access_http_403", "rate_limit_429", "robots_disallow")
        else "ok"
    )
    interp = "acesso_limitado_waf_ou_robots" if readiness_tag == "blocked_access_limited" else "crawler_nao_evidenciado_como_quebrado_por_acesso"
    if cls in ("captcha", "login_required"):
        readiness_tag = "blocked_access_limited"
        interp = "destino_exige_login_ou_captcha_publico"

    return {
        "fonte": fonte,
        "policy_entry": {k: v for k, v in entry.items() if k != "notes"},
        "policy_notes": entry.get("notes"),
        "seed_urls": seeds,
        "primary_classification": cls,
        "recommended_method": rec_method,
        "readiness_access_tag": readiness_tag,
        "interpretacao_crawler": interp,
        "probes": probes,
        "optional_probes": optional_rows,
        "allowed_methods_policy": entry.get("allowed_methods") or [],
        "disallowed_methods_policy": entry.get("disallowed_methods") or [],
    }


def _write_summary_md(rows: List[Dict[str, Any]], path: Path) -> None:
    lines = [
        "# Auditoria de métodos de acesso por fonte",
        "",
        f"- Fontes analisadas: **{len(rows)}**",
        "- Critério: pedidos HTTP modestos; respeito a `robots.txt` (não GET se `Disallow` explícito para o path).",
        "",
        "## Resumo por classificação",
        "",
    ]
    c = Counter(r.get("primary_classification") or "?" for r in rows)
    for k, v in c.most_common():
        lines.append(f"- `{k}`: {v}")
    lines.extend(["", "## Por fonte", ""])
    for r in rows:
        lines.append(f"### `{r['fonte']}`")
        lines.append(f"- **Classificação:** `{r.get('primary_classification')}`")
        lines.append(f"- **Método seguro recomendado:** `{r.get('recommended_method')}`")
        lines.append(f"- **Tag readiness (acesso):** `{r.get('readiness_access_tag')}`")
        lines.append(f"- **Interpretação:** {r.get('interpretacao_crawler')}")
        if r.get("policy_notes"):
            lines.append(f"- **Notas política:** {r['policy_notes']}")
        seeds = r.get("seed_urls") or []
        if seeds:
            lines.append(f"- **Seed:** `{seeds[0]}`")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria de acesso público por fonte.")
    ap.add_argument("--policy", type=str, default=str(POLICY_PATH))
    ap.add_argument("--readiness", type=str, default=str(READINESS_PATH))
    ap.add_argument("--sources", type=str, default="", help="Lista separada por vírgulas (sobrepõe o default).")
    ap.add_argument("--output-dir", type=str, default=str(OUT_DIR))
    ap.add_argument("--include-ready", action="store_true", help="Inclui também fontes ready / ready_with_notes.")
    ap.add_argument("--timeout", type=float, default=18.0)
    ap.add_argument("--sleep", type=float, default=1.0)
    args = ap.parse_args()

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cache_dir = out / ".http_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    policy = _load_json(Path(args.policy), {})
    timeout = float((policy.get("defaults") or {}).get("timeout_sec") or args.timeout)
    sleep_between = float((policy.get("defaults") or {}).get("polite_sleep_sec") or args.sleep)

    targets = _target_sources(args)
    sess = requests.Session()
    rows_new: List[Dict[str, Any]] = []
    for fonte in targets:
        print(f"[audit_access] {fonte} …", flush=True)
        rows_new.append(audit_fonte(fonte, policy, sess, cache_dir, timeout, sleep_between))

    by_path = out / "source_access_by_source.json"
    merged: Dict[str, Dict[str, Any]] = {}
    if by_path.is_file():
        prev = _load_json(by_path, [])
        if isinstance(prev, list):
            for item in prev:
                if isinstance(item, dict) and item.get("fonte"):
                    merged[str(item["fonte"]).lower()] = item
    for item in rows_new:
        merged[str(item["fonte"]).lower()] = item
    rows = [merged[k] for k in sorted(merged.keys())]

    by_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    dist = Counter(r.get("primary_classification") or "?" for r in rows)
    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fontes_total": len(rows),
        "classificacao_distribuicao": dict(dist),
        "metodos_recomendados_top": Counter(r.get("recommended_method") or "?" for r in rows).most_common(20),
        "readiness_access_limited_count": sum(1 for r in rows if r.get("readiness_access_tag") == "blocked_access_limited"),
        "policy_path": str(Path(args.policy).resolve()),
        "readiness_path": str(Path(args.readiness).resolve()),
    }
    (out / "source_access_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_summary_md(rows, out / "source_access_summary.md")
    print(out.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
