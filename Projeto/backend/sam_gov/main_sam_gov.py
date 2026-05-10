from __future__ import annotations

import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Set
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT_DIR / ".env.staging")
    load_dotenv(ROOT_DIR / ".env")
except ImportError:
    pass

_SAM_DIR = Path(__file__).resolve().parent
if str(_SAM_DIR) not in sys.path:
    sys.path.insert(0, str(_SAM_DIR))
from scope_policy import load_policy, opportunity_dict_to_item  # noqa: E402


def _session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
    )
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": "EditalFinderBot/1.0 (local; sam_gov scoped crawl)"})
    return s


def _posted_range(policy: Dict[str, Any]) -> tuple[str, str]:
    days = int((policy.get("collection") or {}).get("posted_days_back") or 300)
    days = max(1, min(days, 365))
    end = datetime.utcnow().date()
    start = end - timedelta(days=days)
    return start.strftime("%m/%d/%Y"), end.strftime("%m/%d/%Y")


def _fetch_opportunities_page(
    sess: requests.Session,
    base_url: str,
    api_key: str,
    params: Dict[str, Any],
    timeout: float,
) -> List[Dict[str, Any]]:
    q = dict(params)
    q["api_key"] = api_key
    url = f"{base_url}?{urlencode(q)}"
    r = sess.get(url, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, dict):
        return []
    rows = data.get("opportunitiesData")
    if isinstance(rows, list):
        return [x for x in rows if isinstance(x, dict)]
    return []


def _collect_via_api(policy: Dict[str, Any], api_key: str) -> List[Dict[str, Any]]:
    coll = policy.get("collection") or {}
    bases = list(coll.get("api_base_urls") or [])
    if not bases:
        bases = [
            "https://api.sam.gov/prod/opportunities/v2/search",
            "https://api.sam.gov/opportunities/v2/search",
        ]
    posted_from, posted_to = _posted_range(policy)
    per_limit = int(coll.get("per_request_limit") or 8)
    per_limit = max(1, min(per_limit, 25))
    max_calls = int(coll.get("max_distinct_api_calls") or 8)
    delay = float(coll.get("request_delay_seconds") or 1.25)
    timeout = float(coll.get("http_timeout_seconds") or 45)
    queries = list(coll.get("title_search_queries") or ["research", "SBIR"])
    ptypes = list(coll.get("optional_ptypes") or [])

    sess = _session()
    merged: Dict[str, Dict[str, Any]] = {}
    calls = 0

    def _run(base: str, extra: Dict[str, Any]) -> None:
        nonlocal calls
        if calls >= max_calls:
            return
        params: Dict[str, Any] = {
            "postedFrom": posted_from,
            "postedTo": posted_to,
            "limit": str(per_limit),
            "offset": "0",
        }
        params.update(extra)
        try:
            rows = _fetch_opportunities_page(sess, base, api_key, params, timeout)
            calls += 1
            for row in rows:
                nid = str(row.get("noticeId") or "").strip()
                if nid:
                    merged[nid] = row
        except Exception as exc:
            print(f"[SAM.gov] API erro ({base} {extra}): {exc}")
        time.sleep(delay)

    working_base: str | None = None
    for base in bases:
        try:
            _fetch_opportunities_page(
                sess,
                base,
                api_key,
                {
                    "postedFrom": posted_from,
                    "postedTo": posted_to,
                    "limit": "1",
                    "offset": "0",
                    "title": "research",
                },
                timeout,
            )
            working_base = base
            print(f"[SAM.gov] API base OK: {base}")
            break
        except Exception:
            continue

    if not working_base:
        print("[SAM.gov] Nenhum endpoint API respondeu com sucesso (rede/chave/URL).")
        return []

    for title_q in queries:
        if calls >= max_calls:
            break
        _run(working_base, {"title": title_q[:80]})
    for pt in ptypes[:4]:
        if calls >= max_calls:
            break
        _run(working_base, {"ptype": pt, "title": "technology"})

    out: List[Dict[str, Any]] = []
    for row in merged.values():
        it = opportunity_dict_to_item(row, policy)
        if it:
            out.append(it)
    max_out = int(coll.get("max_items_output") or 25)
    return out[: max(0, min(max_out, 25))]


def main() -> None:
    print("[SAM.gov] Coleta com política de escopo (config/sam_gov_scope_policy.json)…")
    policy = load_policy()
    if not policy:
        print("[SAM.gov] Política ausente — nada a fazer.")
        save_outputs(Path(__file__).parent, "sam_gov", [])
        return

    api_key = (
        os.environ.get("SAM_GOV_API_KEY")
        or os.environ.get("SAM_API_KEY")
        or os.environ.get("DATA_GOV_API_KEY")
        or ""
    ).strip()

    items: List[Dict[str, Any]] = []
    failure_reason = ""
    if not api_key:
        failure_reason = "SAM.gov exige api_key publica; SAM_GOV_API_KEY/SAM_API_KEY/DATA_GOV_API_KEY ausente."
        print(
            "[SAM.gov] Sem SAM_GOV_API_KEY (ou SAM_API_KEY) no ambiente — "
            "a API pública GSA exige chave pública da conta SAM.gov. "
            "Não se usa fallback de listagem/hub. Output vazio."
        )
    else:
        items = _collect_via_api(policy, api_key)
        print(f"[SAM.gov] Itens após política local: {len(items)}")
        if not items:
            failure_reason = "API SAM.gov respondeu sem itens dentro da politica local ou falhou em todos os endpoints."

    save_outputs(
        Path(__file__).parent,
        "sam_gov",
        items,
        failure_reason=failure_reason or None,
        collection_failed=not items,
    )
    print(f"[SAM.gov] Registros gravados: {len(items)}")


if __name__ == "__main__":
    main()
