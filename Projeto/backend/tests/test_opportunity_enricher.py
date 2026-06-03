"""Testes CORE/opportunity_enricher.py (Backend 2)."""
from __future__ import annotations

import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from opportunity_enricher import (  # noqa: E402
    apply_backend_enrichment_if_enabled,
    backend_enrichment_enabled,
    enrich_opportunity_record,
)


def test_preserves_original_record() -> None:
    rec = {"titulo": "Edital X", "prazo_envio": "2026-12-01", "extras": {"a": 1}}
    original = copy.deepcopy(rec)
    enriched = enrich_opportunity_record(rec)
    assert rec == original
    assert enriched is not rec


def test_keeps_legacy_fields() -> None:
    rec = {
        "titulo": "Chamada pública de fomento",
        "fim_inscricao": "2026-08-15",
        "fonte": "FAPESC",
        "extras": {"programa": "P1"},
    }
    out = enrich_opportunity_record(rec)
    assert out["fim_inscricao"] == "2026-08-15"
    assert out["extras"]["programa"] == "P1"
    assert out.get("prazo_data") == "2026-08-15"


def test_adds_classification() -> None:
    rec = {
        "titulo": "Chamada pública de inovação 2026",
        "fonte_recurso": "BNDES",
        "pais": "Brasil",
    }
    out = enrich_opportunity_record(rec)
    assert out.get("tipo_registro") == "edital"
    assert out.get("modalidade_normalizada")
    assert out.get("escopo_geografico") == "brasil"
    assert isinstance(out.get("qualidade_flags"), list)
    assert "backend_enrichment" in out["extras"]


def test_noticia_classification() -> None:
    rec = {
        "titulo": "Comunicado: ministro anuncia programa",
        "link": "https://gov.br/noticias/1",
        "descricao": "Texto institucional sem chamada.",
    }
    out = enrich_opportunity_record(rec)
    assert out.get("tipo_registro") == "noticia"
    assert out["titulo"] == rec["titulo"]
    assert out["descricao"] == rec["descricao"]


def test_empty_record() -> None:
    out = enrich_opportunity_record({})
    assert out.get("prazo_status") == "sem_prazo"
    assert out.get("tipo_registro") in ("desconhecido", "portal", "edital")


def test_invalid_deadline_flag() -> None:
    rec = {"titulo": "X", "prazo": "data inválida xyz"}
    out = enrich_opportunity_record(rec)
    assert out.get("prazo_status") in ("prazo_invalido", "sem_prazo")
    assert "prazo_invalido" in (out.get("qualidade_flags") or []) or out.get("prazo_status") == "sem_prazo"


def test_flag_off_by_default() -> None:
    import os

    os.environ.pop("EDITALFINDER_ENABLE_BACKEND_ENRICHMENT", None)
    assert backend_enrichment_enabled() is False
    item = {"titulo": "T", "extras": {}}
    before = copy.deepcopy(item)
    apply_backend_enrichment_if_enabled(item)
    assert item == before


def test_flag_on_attaches_extras_only() -> None:
    import os

    os.environ["EDITALFINDER_ENABLE_BACKEND_ENRICHMENT"] = "true"
    try:
        item = {
            "titulo": "Chamada pública fomento",
            "fonte_recurso": "CNPq",
            "extras": {},
        }
        apply_backend_enrichment_if_enabled(item)
        assert "backend_enrichment" in item["extras"]
        assert item["extras"]["backend_enrichment"].get("tipo_registro")
        assert "prazo_data" not in item or item.get("prazo_data") is None
    finally:
        os.environ.pop("EDITALFINDER_ENABLE_BACKEND_ENRICHMENT", None)
