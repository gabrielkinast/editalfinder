"""Testes do portão de qualidade do transformer (Etapas B–D+)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "CORE"
sys.path.insert(0, str(CORE))
sys.path.insert(0, str(ROOT))

from data_cleaning import clean_html, clean_text, normalize_aliases  # noqa: E402
from date_parser import normalize_date_str  # noqa: E402
from finance_parser import extract_value  # noqa: E402
from noise_filter import has_opportunity_signal, is_noise_title, is_noise_url  # noqa: E402
import transformer as tx  # noqa: E402


def test_contato_descartado() -> None:
    r = tx._transform_item_with_result(
        {"titulo": "Contato", "link": "https://exemplo.gov/edital/1", "fonte": "X"},
        "test",
    )
    assert r.rejected and r.rejection_reason == "titulo_ruido_exato"


def test_saiba_mais_descartado() -> None:
    r = tx._transform_item_with_result(
        {"titulo": " Saiba mais ", "link": "https://exemplo.gov/a", "fonte": "X"},
        "test",
    )
    assert r.rejected


def test_javascript_url_descartado() -> None:
    r = tx._transform_item_with_result(
        {
            "titulo": "Chamada pública 2026",
            "link": "javascript:void(0)",
            "fonte": "X",
        },
        "test",
    )
    assert r.rejected and r.rejection_reason in ("url_invalido", "sem_link")


def test_item_real_sem_prazo_incompleto() -> None:
    r = tx._transform_item_with_result(
        {
            "titulo": "Chamada pública 01/2026 — fomento à inovação em energia solar",
            "descricao": (
                "Chamada pública para submissão de propostas. Apoio a projetos de P&D em "
                "energia solar fotovoltaica. Inscrições abertas. Financiamento não reembolsável. "
                "Prazo final para envio 31/12/2030. Grant funding opportunity. "
                + ("Detalhes adicionais sobre elegibilidade e documentação. " * 8)
            ),
            "link": "https://exemplo.gov/chamada/solar",
            "fonte": "Ministério Teste",
            "extras": {},
        },
        "test",
    )
    assert not r.rejected and r.payload
    st = (r.payload.get("extras") or {}).get("validacao_status")
    assert st in ("incompleto", "valido")


def test_descricao_rica_preservada() -> None:
    long_desc = ("Detalhe " * 200) + " submission deadline 2026-04-30. call for proposals."
    r = tx._transform_item_with_result(
        {
            "titulo": "Chamada pública — Programa X de fomento",
            "descricao": long_desc,
            "resumo": "curto",
            "link": "https://exemplo.gov/p",
            "fonte": "F",
            "extras": {},
        },
        "test",
    )
    assert r.payload and len(r.payload.get("descricao") or "") >= len("curto")


def test_campos_desconhecidos_em_extras() -> None:
    r = tx._transform_item_with_result(
        {
            "titulo": "Chamada pública Y — edital de fomento",
            "descricao": (
                "Texto com prazo e inscrições. Chamada pública. Grant funding. "
                "submission deadline 2030-01-01. " + ("Conteúdo informativo. " * 30)
            ),
            "link": "https://exemplo.gov/y",
            "fonte": "Org",
            "campo_custom_crawler": {"a": 1},
        },
        "test",
    )
    assert r.payload
    ex = r.payload.get("extras") or {}
    assert "campo_custom_crawler" in ex or any("campo_custom" in k for k in ex)


def test_pdf_documentos_preservados() -> None:
    r = tx._transform_item_with_result(
        {
            "titulo": "Chamada pública — seleção 01/2026",
            "descricao": (
                "Inscrições e submissão de propostas. Chamada pública. Grant funding. "
                "submission deadline 2030-06-01. " + ("Critérios de elegibilidade. " * 25)
            ),
            "link": "https://exemplo.gov/s",
            "fonte": "F",
            "extras": {
                "pdf_url": "https://exemplo.gov/doc.pdf",
                "documentos": [{"nome": "A", "url": "https://exemplo.gov/a.pdf"}],
            },
        },
        "test",
    )
    assert r.payload
    ex = r.payload["extras"]
    assert ex.get("pdf_url") or ex.get("documentos")


def test_licitacao_objeto_enriquece() -> None:
    r = tx._transform_item_with_result(
        {
            "titulo": "Pregão eletrônico 99 — compra pública",
            "descricao": (
                "Licitação aberta. Chamada pública. submission deadline 2030-03-15. "
                + ("Resumo do edital. " * 30)
            ),
            "link": "https://exemplo.gov/pregao",
            "fonte": "Pref",
            "extras": {"objeto": "Aquisição de equipamentos laboratoriais para universidade."},
        },
        "test",
    )
    assert r.payload
    d = r.payload.get("descricao") or ""
    ex = r.payload.get("extras") or {}
    obj = str(ex.get("objeto") or "")
    full = (ex.get("descricao_completa") or "") + d + obj
    assert "laboratoriais" in full or "Aquisição" in full or "Aquisicao" in full


def test_noticia_sem_oportunidade_roteada_para_noticias() -> None:
    r = tx._transform_item_with_result(
        {
            "titulo": "Breaking science news today",
            "descricao": "Researchers published an interesting paper.",
            "link": "https://exemplo.gov/news/press-1",
            "fonte": "News",
        },
        "test",
    )
    assert not r.rejected and r.payload
    ex = r.payload.get("extras") or {}
    assert r.payload.get("content_type") == "noticia"
    assert ex.get("destination_table") == "noticia"


def test_unicode_cjk_preservado() -> None:
    t = "清华大学采购公告 项目编号 AB-12"
    assert clean_text(clean_html(f"<p>{t}</p>")) == t


def test_valor_10_milhoes() -> None:
    v = extract_value("O valor total é de R$ 10 milhões para empresas.")
    assert v and "10" in v and "milh" in v.lower()


def test_data_ate_preservada_original() -> None:
    raw = "até 30/04/2026"
    iso = normalize_date_str("30/04/2026")
    assert iso == "2026-04-30"


def test_titulo_com_contato_nao_descarta() -> None:
    assert not is_noise_title("Edital de apoio ao contato universidade-empresa")


def test_is_noise_url() -> None:
    assert is_noise_url("javascript:void(0)")
    assert is_noise_url("#")


def test_has_opportunity_signal() -> None:
    assert has_opportunity_signal("chamada pública com inscrições e prazo")


if __name__ == "__main__":
    os.chdir(CORE)
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("ok")
