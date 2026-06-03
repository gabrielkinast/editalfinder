"""Testes recoleta Backend 4 (sem rede, sem banco)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "CORE"))

from _recrawl_common import match_key, normalize_link, item_has_deadline  # noqa: E402
from compare_recrawl_with_db import compare_source  # noqa: E402
from source_deadline_parsers import parse_grants_api_deadlines  # noqa: E402


def test_match_by_link() -> None:
    a = {"link": "https://simpler.grants.gov/opportunity/123", "titulo": "A"}
    b = {"link": "https://simpler.grants.gov/opportunity/123/", "titulo": "A"}
    assert match_key(a) == match_key(b)


def test_compare_deadline_gained() -> None:
    db = [
        {
            "fonte_recurso": "Grants.gov",
            "link": "https://simpler.grants.gov/opportunity/99",
            "titulo": "Grant X",
            "prazo_envio": None,
        }
    ]
    new = [
        {
            "fonte": "Grants.gov",
            "link": "https://simpler.grants.gov/opportunity/99",
            "titulo": "Grant X",
            "prazo_data": "2027-01-15",
            "prazo_confidence": "alta",
        }
    ]
    r = compare_source(new, db, "grants")
    assert r["matched_count"] == 1
    assert r["deadlines_gained_on_matched"] == 1


def test_grants_posted_not_deadline_in_recrawl_logic() -> None:
    r = parse_grants_api_deadlines({"posted_date": "2026-05-09"})
    assert r.get("fim_inscricao") is None
    has, iso, _ = item_has_deadline({"fim_inscricao": None, "data_publicacao": "2026-05-09"})
    assert not has


def test_araucaria_no_invent_deadline() -> None:
    from source_deadline_parsers import parse_araucaria_deadlines

    r = parse_araucaria_deadlines("Cronograma sem datas fixas no edital")
    assert r.get("fim_inscricao") is None


def test_recrawl_declares_no_db_write_guard() -> None:
    path = ROOT / "scripts" / "recrawl_sources_dry_run.py"
    text = path.read_text(encoding="utf-8")
    assert "_assert_no_db_write" in text
    assert "from loader import" not in text
    assert "import loader" not in text


def test_china_offline_outputs_structure(tmp_path: Path) -> None:
    china_json = ROOT / "china_mofcom_tendering" / "outputs" / "china_mofcom_tendering_editais.json"
    if not china_json.is_file():
        return
    import recrawl_sources_dry_run as rr

    out = tmp_path / "b4"
    old_argv = sys.argv
    try:
        sys.argv = [
            "recrawl",
            "--source",
            "china",
            "--limit",
            "3",
            "--no-network",
            "--offline-fixtures",
            "--output",
            str(out),
        ]
        with patch.object(rr, "DEFAULT_OUT", out):
            assert rr.main() == 0
    finally:
        sys.argv = old_argv
    assert (out / "china" / "enriched_sample.json").is_file()
    data = json.loads((out / "china" / "enriched_sample.json").read_text(encoding="utf-8"))
    assert isinstance(data, list)
