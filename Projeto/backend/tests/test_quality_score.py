"""Testes CORE/quality_score.py (Backend 9)."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from opportunity_enricher import enrich_opportunity_record  # noqa: E402
from quality_score import compute_quality_score  # noqa: E402


def test_high_quality_edital() -> None:
    future = (date.today() + timedelta(days=45)).isoformat()
    rec = {
        "titulo": "Chamada pública de fomento à inovação — edital 05/2026",
        "descricao": "A " * 40 + "Submissão de propostas.",
        "fim_inscricao": future,
        "fonte_recurso": "FAPESC",
        "link": "https://fapesc.sc.gov.br/edital/5",
    }
    enr = enrich_opportunity_record(rec)
    assert enr.get("quality_score", 0) >= 55
    assert enr.get("quality_level") in ("alto", "medio")


def test_low_quality_noticia() -> None:
    rec = {
        "titulo": "Comunicado institucional",
        "link": "https://gov.br/noticias/x",
        "descricao": "Texto curto.",
    }
    out = compute_quality_score(rec)
    assert out["quality_level"] in ("baixo", "revisao")
    assert out["quality_score"] < 50


def test_enricher_backend_9_fields() -> None:
    rec = {"titulo": "Chamada pública teste", "link": "https://example.org/c", "fim_inscricao": "2030-01-15"}
    enr = enrich_opportunity_record(rec)
    be = enr["extras"]["backend_enrichment"]
    assert be.get("enrichment_version") == "backend_10.1"
    assert be.get("actionability_type")
    assert "validade_status" in be
    assert "noise_score" in be
    assert "quality_score" in be
