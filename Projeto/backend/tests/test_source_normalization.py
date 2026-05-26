"""Testes normalização de fonte — Backend 8 FINEP/FNDCT."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from opportunity_classifier import classify_source_normalized  # noqa: E402
from opportunity_enricher import enrich_opportunity_record  # noqa: E402


def test_finep_link_fndct_fonte() -> None:
    rec = {
        "fonte_recurso": "FNDCT",
        "link": "https://www.finep.gov.br/chamadas/publica/123",
    }
    src = classify_source_normalized(rec)
    assert src["fonte_normalizada"] == "FINEP"
    assert src["fundo_origem"] == "FNDCT"
    assert src["source_scope"] == "brasil"
    assert src["pais_origem"] == "Brasil"


def test_titulo_finep_fndct() -> None:
    rec = {
        "fonte_recurso": "FNDCT",
        "titulo": "Chamada Pública FINEP/FNDCT — inovação industrial",
    }
    src = classify_source_normalized(rec)
    assert src["fonte_normalizada"] == "FINEP"
    assert src["fundo_origem"] == "FNDCT"
    assert any("FNDCT tratado" in n for n in src.get("source_notes") or [])


def test_fndct_only_no_finep_force() -> None:
    rec = {
        "fonte_recurso": "FNDCT",
        "titulo": "Programa de apoio à inovação",
        "descricao": "Recursos do fundo nacional para P&D.",
    }
    src = classify_source_normalized(rec)
    assert src["fonte_normalizada"] == "FNDCT"
    assert src.get("fundo_origem") == "FNDCT"
    assert src["fonte_normalizada"] != "FINEP"


def test_fonte_finep() -> None:
    src = classify_source_normalized({"fonte_recurso": "Finep"})
    assert src["fonte_normalizada"] == "FINEP"


def test_cnpq_not_finep() -> None:
    src = classify_source_normalized({"fonte_recurso": "CNPq"})
    assert src["fonte_normalizada"] == "CNPq"
    assert src["fonte_normalizada"] != "FINEP"


def test_descricao_finep_only_with_fndct_fonte() -> None:
    rec = {
        "fonte_recurso": "FNDCT",
        "descricao": "Chamada operada pela FINEP com recursos do FNDCT.",
    }
    src = classify_source_normalized(rec)
    assert src["fonte_normalizada"] == "FINEP"
    assert src["fundo_origem"] == "FNDCT"


def test_descricao_mention_alone_not_finep() -> None:
    rec = {
        "fonte_recurso": "BDMG",
        "descricao": "Programa similar ao apoio da FINEP para inovação.",
    }
    src = classify_source_normalized(rec)
    assert src["fonte_normalizada"] != "FINEP"


def test_enricher_exposes_fundo_origem() -> None:
    rec = {
        "fonte_recurso": "FNDCT",
        "link": "https://www.finep.gov.br/edital/1",
        "titulo": "Edital FINEP",
    }
    out = enrich_opportunity_record(rec)
    assert out["fonte_normalizada"] == "FINEP"
    assert out["fundo_origem"] == "FNDCT"
    assert out["extras"]["backend_enrichment"]["fundo_origem"] == "FNDCT"
    assert isinstance(out.get("source_notes"), list)
