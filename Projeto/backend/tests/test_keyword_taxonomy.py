"""Testes da taxonomia temática e do overwrite de setor_estrategico no enrich."""
from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "CORE"
sys.path.insert(0, str(CORE))
sys.path.insert(0, str(ROOT))

from keyword_taxonomy import classify_thematic_tags  # noqa: E402
from taxonomy_filtros import enrich_opportunity_classification  # noqa: E402


def test_digital_nao_dispara_aeroespacial_por_ita() -> None:
    text = (
        "Chamada para transformacao digital nas escolas publicas. "
        "Inovacao em gestao de dados e plataformas online."
    )
    tags = classify_thematic_tags(text)
    assert "aeroespacial" not in tags


def test_evidencia_aeroespacial_detecta() -> None:
    text = "Bolsas em engenharia aeroespacial e missao espacial com satelite de observacao."
    tags = classify_thematic_tags(text)
    assert "aeroespacial" in tags


def test_enrich_substitu_setor_estrategico_sem_uniao() -> None:
    item = {
        "titulo": "Fomento a pesquisa em energia solar",
        "descricao": (
            "Chamada publica de fomento. Financiamento a projetos de P&D. "
            "Eficiencia energetica e geracao distribuida. Prazo 2030."
        ),
        "programa": "",
        "acao": "",
        "link": "https://exemplo.gov/edital",
        "extras": {"setor_estrategico": ["aeroespacial", "defesa", "defesa_industrial"]},
    }
    enrich_opportunity_classification(item)
    se = item["extras"].get("setor_estrategico") or []
    assert "aeroespacial" not in se
    assert "defesa_industrial" not in se
    hist = item["extras"].get("setor_estrategico_historico_merge")
    assert isinstance(hist, list) and len(hist) >= 1
    assert hist[0] == ["aeroespacial", "defesa", "defesa_industrial"]


def test_enrich_respeita_setor_estrategico_crawler_locked() -> None:
    item = {
        "titulo": "Fomento a pesquisa em energia solar",
        "descricao": "Eficiencia energetica e geracao distribuida.",
        "programa": "",
        "acao": "",
        "link": "https://exemplo.gov/edital",
        "extras": {
            "setor_estrategico": ["aeroespacial", "defesa"],
            "setor_estrategico_crawler_locked": True,
        },
    }
    before = deepcopy(item["extras"]["setor_estrategico"])
    enrich_opportunity_classification(item)
    assert item["extras"]["setor_estrategico"] == before
