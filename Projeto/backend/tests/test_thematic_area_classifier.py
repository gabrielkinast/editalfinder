"""Testes classify_thematic_area (Backend 5/6)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "CORE"))

from opportunity_classifier import classify_thematic_area  # noqa: E402


def _area(record: dict) -> dict:
    return classify_thematic_area(record)


def test_energia() -> None:
    r = _area({"titulo": "Chamada de hidrogênio verde e armazenamento de energia solar"})
    assert r["area_tematica_normalizada"] == "energia"


def test_saude() -> None:
    r = _area({"titulo": "Edital SUS — diagnóstico hospitalar e vacinas"})
    assert r["area_tematica_normalizada"] == "saude"


def test_defesa() -> None:
    r = _area({"titulo": "Programa NATO dual use defesa e segurança"})
    assert r["area_tematica_normalizada"] == "defesa_seguranca"


def test_aeroespacial() -> None:
    r = _area({"titulo": "Propulsão aeroespacial e motor de foguete hypersonic"})
    assert r["area_tematica_normalizada"] == "aeroespacial"
    assert r["area_tematica_confidence"] == "alta"


def test_satellite_orbital_espaco() -> None:
    r = _area({"titulo": "Satélite em órbita — programa espacial ESA spacecraft"})
    assert r["area_tematica_normalizada"] == "espaco"


def test_nuclear() -> None:
    r = _area({"titulo": "Pesquisa em reator nuclear e dosimetria CNEN"})
    assert r["area_tematica_normalizada"] == "nuclear"


def test_agro() -> None:
    r = _area({"titulo": "Embrapa — inovação na lavoura e pecuária rural"})
    assert r["area_tematica_normalizada"] == "agronegocio"


def test_generico_inovacao() -> None:
    r = _area({"titulo": "Programa de inovação aberta e transferência de tecnologia empresarial"})
    assert r["area_tematica_normalizada"] == "tecnologia_inovacao"


def test_amplo_sem_area() -> None:
    r = _area({"titulo": "Chamada pública institucional", "descricao": "Informações gerais"})
    assert r["area_tematica_normalizada"] in ("multissetorial", "sem_classificacao")


def test_inovacao_em_saude() -> None:
    r = _area(
        {
            "titulo": "Inovação em saúde — telemedicina e diagnóstico hospitalar",
            "descricao": "programa de inovação aberta em medicina",
        }
    )
    assert r["area_tematica_normalizada"] == "saude"
    assert "Tecnologia e Inovação" in r["area_tematica_secondary"] or "Computação e IA" in str(
        r["area_tematica_secondary"]
    )


def test_startups_energia() -> None:
    r = _area({"titulo": "Subvenção para startups de energia solar e baterias"})
    assert r["area_tematica_normalizada"] == "energia"
    assert "Startups" in r["area_tematica_secondary"]


def test_nato_counter_drone_defesa() -> None:
    r = _area({"titulo": "NATO counter-drone C-UAS programme for military security"})
    assert r["area_tematica_normalizada"] == "defesa_seguranca"
    assert r["area_tematica_normalizada"] != "aeroespacial"


def test_satellite_servicing_espaco() -> None:
    r = _area({"titulo": "Satellite servicing orbital mission and constellation deployment"})
    assert r["area_tematica_normalizada"] == "espaco"


def test_generic_aerospace_tag_only() -> None:
    r = _area(
        {
            "titulo": "Broad innovation funding call",
            "descricao": "Open research programme",
            "extras": {"thematic_tags": ["aeroespacial"], "setor_estrategico": ["veiculos"]},
        }
    )
    assert r["area_tematica_normalizada"] in ("multissetorial", "sem_classificacao")
    assert "Aeroespacial" in r["area_tematica_secondary"] or "aeroespacial" in str(
        r.get("area_tematica_secondary_keys", r["area_tematica_secondary"])
    )


def test_aerospace_propulsion_high_confidence() -> None:
    r = _area({"titulo": "Aerospace propulsion research — rocket engine and hypersonic UAV"})
    assert r["area_tematica_normalizada"] == "aeroespacial"
    assert r["area_tematica_confidence"] == "alta"


def test_darpa_broad_defesa_or_estrategicas() -> None:
    r = _area({"titulo": "DARPA broad research on strategic technology and supply chain"})
    assert r["area_tematica_normalizada"] in ("defesa_seguranca", "tecnologias_estrategicas")


def test_space_debris_orbital() -> None:
    r = _area({"titulo": "Space debris mitigation and orbital constellation monitoring"})
    assert r["area_tematica_normalizada"] == "espaco"
