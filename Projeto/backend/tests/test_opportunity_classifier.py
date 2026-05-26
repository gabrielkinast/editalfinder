"""Testes CORE/opportunity_classifier.py (Backend 1)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from opportunity_classifier import (  # noqa: E402
    classify_geo_scope,
    classify_opportunity_modality,
    classify_record_kind,
    classify_source_normalized,
)


def test_fomento_edital() -> None:
    r = {
        "titulo": "Chamada pública de fomento à inovação 2026",
        "tipo_oportunidade": "chamada_publica",
        "fonte_recurso": "FAPESC",
        "pais": "Brasil",
    }
    assert classify_record_kind(r)["kind"] == "edital"
    mod = classify_opportunity_modality(r)
    assert mod["modalidade_normalizada"] == "fomento_chamada_publica"


def test_noticia() -> None:
    r = {
        "titulo": "Ministro anuncia investimentos — comunicado",
        "link": "https://exemplo.gov.br/noticias/123",
        "fonte_recurso": "MCTI",
    }
    assert classify_record_kind(r)["kind"] == "noticia"


def test_concurso() -> None:
    r = {"titulo": "Concurso público para analista", "tipo_oportunidade": "concurso"}
    assert classify_record_kind(r)["kind"] == "concurso"


def test_pesquisa() -> None:
    r = {
        "titulo": "New research article on quantum dots",
        "descricao": "Published in Nature, doi:10.1038/example",
    }
    assert classify_record_kind(r)["kind"] == "pesquisa"


def test_fonte_brasil() -> None:
    geo = classify_geo_scope({"fonte_recurso": "FAPERGS", "pais": "Brasil", "uf": "RS"})
    assert geo["scope"] == "brasil"


def test_fonte_internacional() -> None:
    geo = classify_geo_scope(
        {
            "fonte_recurso": "China International Technology Transfer",
            "link": "https://www.ittc.org.cn/opportunity",
        }
    )
    assert geo["scope"] == "internacional"


def test_fonte_multilateral() -> None:
    geo = classify_geo_scope({"fonte_recurso": "World Bank", "titulo": "Program"})
    assert geo["scope"] == "multilateral"


def test_source_normalized() -> None:
    src = classify_source_normalized({"fonte_recurso": "grants.gov"})
    assert "Grants.gov" in src["fonte_normalizada"]
    assert src["source_scope"] in ("internacional", "desconhecido")
