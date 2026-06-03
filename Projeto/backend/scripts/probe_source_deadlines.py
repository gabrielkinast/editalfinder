#!/usr/bin/env python3
"""
Probe de prazos por fonte (Backend 3) — não grava no banco.

Uso:
  python scripts/probe_source_deadlines.py --source china --limit 20
  python scripts/probe_source_deadlines.py --source araucaria --limit 20
  python scripts/probe_source_deadlines.py --source grants --limit 20
  python scripts/probe_source_deadlines.py --source china --offline
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "CORE"))

from source_deadline_parsers import (  # noqa: E402
    enrich_araucaria_crawler_item,
    enrich_china_crawler_item,
    enrich_grants_crawler_item,
    parse_araucaria_deadlines,
    parse_china_tender_deadlines,
    parse_grants_api_deadlines,
)

OUT_BASE = ROOT / "outputs" / "source_deadline_probes"

SAMPLES = {
    "china": {
        "json": ROOT / "china_mofcom_tendering" / "outputs" / "china_mofcom_tendering_editais.json",
        "html_fixture": (
            "<p>Bid closing date: 2026-08-15</p>"
            "<p>Published: 2026-01-10</p>"
        ),
    },
    "araucaria": {
        "json": ROOT / "fappr" / "outputs" / "fappr_editais.json",
        "text_fixture": "Inscrições até 25/05/2026. Chamada pública CP 10/2026.",
    },
    "grants": {
        "json": ROOT / "grants_gov" / "outputs" / "grants_gov_editais.json",
        "api_fixture": {
            "close_date": "2027-09-30",
            "posted_date": "2026-05-09",
            "opportunity_title": "Test Grant",
        },
    },
}


def _load_json_samples(path: Path, limit: int) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        data = [data]
    return data[:limit]


def probe_china(limit: int, offline: bool) -> Dict[str, Any]:
    raw = _load_json_samples(SAMPLES["china"]["json"], limit)
    parsed_list = []
    findings = []
    fixture = parse_china_tender_deadlines(
        "Tender notice",
        html=SAMPLES["china"]["html_fixture"],
    )
    findings.append(f"Fixture HTML: deadline={fixture.get('prazo_data')} field={fixture.get('deadline_source_field')}")
    for item in raw:
        html = ""
        if not offline:
            html = ""  # live fetch opcional — não implementado nesta fase
        enriched = enrich_china_crawler_item(item, detail_html=html, listing_text=item.get("descricao") or "")
        parsed_list.append(
            {
                "titulo": (item.get("titulo") or "")[:80],
                "link": item.get("link"),
                "fim_inscricao_antes": item.get("fim_inscricao"),
                "fim_inscricao_depois": enriched.get("fim_inscricao"),
                "extras_flags": {
                    k: enriched.get("extras", {}).get(k)
                    for k in ("deadline_missing_in_source", "deadline_normalizer")
                    if isinstance(enriched.get("extras"), dict)
                },
            }
        )
    with_deadline = sum(1 for p in parsed_list if p.get("fim_inscricao_depois"))
    findings.append(f"Amostra JSON ({len(raw)}): com prazo após parser: {with_deadline}/{len(raw) or 1}")
    return {"raw_sample": raw[:5], "parsed_sample": parsed_list, "findings": findings, "fixture": fixture}


def probe_araucaria(limit: int) -> Dict[str, Any]:
    raw = _load_json_samples(SAMPLES["araucaria"]["json"], limit)
    parsed_list = []
    findings = []
    fix = parse_araucaria_deadlines(SAMPLES["araucaria"]["text_fixture"])
    findings.append(f"Fixture PT: {fix.get('fim_inscricao')} ({fix.get('deadline_source_field')})")
    for item in raw:
        enriched = enrich_araucaria_crawler_item(item)
        ex = enriched.get("extras") if isinstance(enriched.get("extras"), dict) else {}
        parsed_list.append(
            {
                "titulo": (item.get("titulo") or "")[:80],
                "fim_antes": item.get("fim_inscricao"),
                "fim_depois": enriched.get("fim_inscricao"),
                "deadline_requires_pdf": ex.get("deadline_requires_pdf"),
            }
        )
    with_dl = sum(1 for p in parsed_list if p.get("fim_depois"))
    findings.append(f"Amostra: {with_dl}/{len(parsed_list)} com fim_inscricao após enrich")
    return {"raw_sample": raw[:5], "parsed_sample": parsed_list, "findings": findings, "fixture": fix}


def probe_grants(limit: int) -> Dict[str, Any]:
    raw = _load_json_samples(SAMPLES["grants"]["json"], limit)
    parsed_list = []
    findings = []
    fix_ok = parse_grants_api_deadlines(SAMPLES["grants"]["api_fixture"])
    fix_bad = parse_grants_api_deadlines(
        {"posted_date": "2026-05-09", "close_date": None},
    )
    findings.append(f"Fixture closeDate: {fix_ok.get('fim_inscricao')}")
    findings.append(f"Fixture só posted: missing={fix_bad.get('deadline_missing_in_source')}")
    for item in raw:
        ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
        api_row = {
            "close_date": ex.get("close_date") or item.get("fim_inscricao"),
            "posted_date": ex.get("posted_date") or item.get("data_publicacao"),
        }
        enriched = enrich_grants_crawler_item(item, api_row=api_row)
        parsed_list.append(
            {
                "titulo": (item.get("titulo") or "")[:60],
                "fim_antes": item.get("fim_inscricao"),
                "fim_depois": enriched.get("fim_inscricao"),
                "prazo_envio_raw": enriched.get("prazo_envio_raw"),
            }
        )
    with_dl = sum(1 for p in parsed_list if p.get("fim_depois"))
    findings.append(f"Amostra: {with_dl}/{len(parsed_list)} com prazo ISO")
    return {"raw_sample": raw[:5], "parsed_sample": parsed_list, "findings": findings, "fixtures": {"with_close": fix_ok, "posted_only": fix_bad}}


def write_probe(source: str, data: Dict[str, Any]) -> Path:
    out = OUT_BASE / source
    out.mkdir(parents=True, exist_ok=True)
    (out / "raw_sample.json").write_text(
        json.dumps(data.get("raw_sample", []), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out / "parsed_sample.json").write_text(
        json.dumps(data.get("parsed_sample", []), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md = ["# Deadline findings — " + source, ""]
    for line in data.get("findings", []):
        md.append(f"- {line}")
    md.append("")
    md.append("## Fixture")
    md.append("```json")
    md.append(json.dumps(data.get("fixture") or data.get("fixtures", {}), ensure_ascii=False, indent=2))
    md.append("```")
    (out / "deadline_findings.md").write_text("\n".join(md), encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, choices=["china", "araucaria", "grants"])
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--offline", action="store_true", help="Só JSON local + fixtures")
    args = ap.parse_args()

    if args.source == "china":
        data = probe_china(args.limit, args.offline)
    elif args.source == "araucaria":
        data = probe_araucaria(args.limit)
    else:
        data = probe_grants(args.limit)

    out = write_probe(args.source, data)
    print(f"[probe_source_deadlines] {args.source} -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
