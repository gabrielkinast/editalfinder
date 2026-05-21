"""Testes do crawler Cebraspe (PAS / API)."""

from datetime import date

from concursos.main_cebraspe_concursos import (
    _etapa_encerrada,
    _etapa_parece_resultado_ou_gabarito,
    _pick_primary_etapa,
    run_crawl,
)


def test_pick_primary_prefers_vigente():
    today = date(2025, 9, 1)
    etapas = [
        {
            "etapaId": 1,
            "etapaDescricao": "PAS 1",
            "isEtapaVigente": False,
            "eventoDaEtapa": {"dataIniInscricao": None, "dataFimInscricao": None},
            "dataProva": "2024-12-01T08:00:00",
        },
        {
            "etapaId": 2,
            "etapaDescricao": "PAS 2",
            "isEtapaVigente": True,
            "eventoDaEtapa": {
                "dataIniInscricao": "2025-08-26T10:00:00",
                "dataFimInscricao": "2025-09-24T18:00:00",
            },
            "dataProva": "2025-12-14T08:00:00",
        },
    ]
    e = _pick_primary_etapa(etapas, today)
    assert e is not None
    assert e["etapaId"] == 2


def test_resultado_gabarito_heuristica():
    e = {"etapaDescricao": "Publicação do gabarito definitivo", "arquivosGabarito": [{"x": 1}]}
    assert _etapa_parece_resultado_ou_gabarito(e) is True


def test_etapa_encerrada_por_prova_passada():
    today = date(2026, 5, 1)
    etapa = {
        "etapaDescricao": "PAS 1",
        "provaRealizada": 0,
        "eventoDaEtapa": {"dataIniInscricao": None, "dataFimInscricao": "2025-01-10T18:00:00"},
        "dataProva": "2025-02-01T08:00:00",
    }
    assert _etapa_encerrada(etapa, today) is True


def test_run_crawl_smoke_com_as_of_historico():
    """Com data histórica, a API atual deve produzir ≥1 linha ou lista vazia sem erro (rede)."""
    rep = run_crawl(max_items=5, sleep_s=0.2, as_of=date(2025, 9, 1))
    assert "total_bruto_api" in rep
    assert rep["total_bruto_api"] >= 0
    assert isinstance(rep.get("standardized"), list)
    assert rep.get("errors") == []
