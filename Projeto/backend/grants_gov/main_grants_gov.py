from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_intel import build_defense_extras, detect_keywords
from defense_source_common import save_outputs

API_URL = "https://api.grants.gov/v1/api/search2"
HEADERS = {"Content-Type": "application/json", "User-Agent": "EditalFinderBot/1.0"}
PAGE_SIZE = 50
MAX_PAGES = 4


def _session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["POST"]),
    )
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s


def fetch_grants() -> List[Dict[str, object]]:
    items: List[Dict[str, object]] = []
    seen = set()
    session = _session()
    for page in range(MAX_PAGES):
        payload = {
            "startRecordNum": page * PAGE_SIZE,
            "rows": PAGE_SIZE,
            "oppStatuses": "forecasted|posted",
            "keyword": "defense military nuclear aerospace dual-use",
        }
        try:
            response = session.post(API_URL, headers=HEADERS, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as exc:
            print(f"[GRANTS_GOV] Falha na API (page={page + 1}): {exc}")
            continue

        rows = (
            data.get("data", {}).get("oppHits", [])
            or data.get("oppHits", [])
            or data.get("oppts", [])
            or []
        )
        if not rows:
            break
        for row in rows:
            title = str(row.get("opportunityTitle") or row.get("title") or "").strip()
            agency = str(row.get("agency") or row.get("agencyName") or "")
            desc = f"{title} {agency}".strip()
            if not detect_keywords(desc):
                continue
            opp_id = row.get("opportunityId") or row.get("id")
            link = (
                f"https://www.grants.gov/web/grants/view-opportunity.html?oppId={opp_id}"
                if opp_id else "https://www.grants.gov/"
            )
            dedupe_key = opp_id or link
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            extras = build_defense_extras(
                text=desc,
                source_name="Grants.gov",
                origem=link,
                pais="US",
                orgao_contratante=str(row.get("agency") or "US Federal Agencies"),
            )
            extras["agency_code"] = row.get("agencyCode") or row.get("agency")
            extras["opportunity_id"] = opp_id
            extras["codigo_oportunidade"] = str(opp_id or "")
            extras["numero_chamada"] = str(row.get("fundingOpportunityNumber") or "")
            extras["numero_processo"] = str(row.get("competitionId") or "")
            extras["modalidade"] = "grant"
            extras["publico_alvo"] = str(row.get("applicantTypes") or "")
            extras["objetivo"] = title[:600]
            extras["url_listagem"] = API_URL
            extras["url_detalhe"] = link
            extras["metodo_extracao"] = "api_rest"
            items.append(
                {
                    "titulo": title[:250] or "Funding Opportunity",
                    "descricao": desc[:3500],
                    "link": link,
                    "fonte": "Grants.gov",
                    "data_publicacao": str(row.get("postDate") or row.get("postedDate") or "")[:10] or datetime.now().date().isoformat(),
                    "fim_inscricao": str(row.get("closeDate") or row.get("closeDateFormatted") or "")[:10] or None,
                    "situacao": "Aberto",
                    "valor": row.get("awardCeiling") or row.get("awardFloor"),
                    "programa": "tecnologias_estrategicas",
                    "acao": "funding_opportunity",
                    "tipo_recurso": "grant",
                    "extras": extras,
                }
            )
    return items


def main() -> None:
    print("[GRANTS_GOV] Iniciando coleta por API...")
    items = fetch_grants()
    save_outputs(Path(__file__).parent, "grants_gov", items)
    print(f"[GRANTS_GOV] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
