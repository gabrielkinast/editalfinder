"""Testes do filtro CORE/opportunity_gate (Asia)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CORE.opportunity_gate import (  # noqa: E402
    ACCESS_LOGIN,
    ACCESS_IP,
    ACCESS_PUBLIC,
    INTENT_PROCUREMENT,
    INTENT_TENDER,
    evaluate_crawl_candidate,
)


def test_chinese_restricted_ip_message():
    html = "您当前访问的页面出错。当前访问的ip并非校内地址，该信息仅允许校内地址访问。"
    r = evaluate_crawl_candidate(
        titulo="Aviso",
        descricao=html,
        link="https://univ.example.edu.cn/notice/1",
        status_code=200,
        raw_html=html,
        fonte="Test",
    )
    assert not r.keep
    assert r.access_status == ACCESS_IP


def test_chinese_procurement_positive():
    html = "本招标公告适用于公开采购。投标截止日期：2026-06-01。采购金额约500万元。"
    r = evaluate_crawl_candidate(
        titulo="某项目招标公告",
        descricao=html,
        link="https://gov.example.cn/zbcg/2026/01",
        status_code=200,
        raw_html=html,
        fonte="Test",
        extras={"documentos": [{"nome": "规格书", "url": "https://x.pdf"}]},
    )
    assert r.keep
    assert r.access_status == ACCESS_PUBLIC
    assert r.opportunity_intent in (INTENT_PROCUREMENT, INTENT_TENDER)


def test_japanese_funding_positive():
    html = "公募について。研究助成金の申請受付を開始します。締切は2026年3月31日です。"
    r = evaluate_crawl_candidate(
        titulo="研究助成公募",
        descricao=html,
        link="https://agency.go.jp/call/2026",
        status_code=200,
        raw_html=html,
        fonte="Test",
    )
    assert r.keep


def test_login_chinese():
    html = "用户登录请输入密码和账号完成认证。"
    r = evaluate_crawl_candidate(
        titulo="Login",
        descricao=html,
        link="https://x.edu.cn/login",
        status_code=200,
        raw_html=html,
        fonte="Test",
    )
    assert not r.keep
    assert r.access_status == ACCESS_LOGIN


def test_generic_about():
    r = evaluate_crawl_candidate(
        titulo="About us",
        descricao="We are a leading university with many schools.",
        link="https://univ.edu/about",
        status_code=200,
        raw_html="",
        fonte="Test",
    )
    assert not r.keep


def test_news_without_call():
    r = evaluate_crawl_candidate(
        titulo="Campus news",
        descricao="The president visited the lab yesterday. No application.",
        link="https://univ.edu/news/2026/01/hello",
        status_code=200,
        raw_html="",
        fonte="Test",
    )
    assert not r.keep


def test_news_with_strong_procurement_signal():
    r = evaluate_crawl_candidate(
        titulo="News: open call",
        descricao="The agency published a 招标公告 today. 截止日期 2026-05-20.",
        link="https://univ.edu/news/tender",
        status_code=200,
        raw_html="",
        fonte="Test",
    )
    assert r.keep


def test_gov_br_program_weak_login_words_suppressed():
    """Rodape com 'login'/'account' nao deve bloquear pagina de programa em gov.br."""
    titulo = "Chamada pública de projetos PDI"
    descricao = (
        ("Programa de pesquisa, desenvolvimento e inovação. " * 40)
        + " Inscricoes e cronograma. Deadline 2026-06-01. grant funding."
    )
    html = ("Texto institucional. " * 30) + " Footer navigation login account password policy."
    r = evaluate_crawl_candidate(
        titulo=titulo,
        descricao=descricao,
        link="https://www.gov.br/aneel/pt-br/assuntos/programa-de-pesquisa/chamada-publica-exemplo",
        status_code=200,
        raw_html=html,
        fonte="Test",
    )
    assert r.access_status == ACCESS_PUBLIC


def test_real_login_page_still_blocked():
    r = evaluate_crawl_candidate(
        titulo="Acesso",
        descricao="Please log in to continue and view this content.",
        link="https://www.gov.br/exemplo/login",
        status_code=200,
        raw_html="<html>Please log in to continue.</html>",
        fonte="Test",
    )
    assert not r.keep
    assert r.access_status == ACCESS_LOGIN


def test_aneel_gov_br_chamadas_path_keeps_with_short_desc():
    """URL gov.br com 'chamadas' + fonte ANEEL não deve cair só em relevância limite."""
    r = evaluate_crawl_candidate(
        titulo="Sistemas de Armazenamento de Energia",
        descricao="Página com pouco texto sobre o subtema.",
        link="https://www.gov.br/aneel/pt-br/assuntos/programa-de-pesquisa-desenvolvimento-e-inovacao/chamadas-de-projetos-de-pdi-estrategicos/sistemas-de-armazenamento-de-energia",
        status_code=200,
        raw_html="",
        fonte="ANEEL",
    )
    assert r.keep
    assert r.trusted_fin_context is True
    assert r.gate_category


if __name__ == "__main__":
    test_chinese_restricted_ip_message()
    test_chinese_procurement_positive()
    test_japanese_funding_positive()
    test_login_chinese()
    test_generic_about()
    test_news_without_call()
    test_news_with_strong_procurement_signal()
    test_gov_br_program_weak_login_words_suppressed()
    test_real_login_page_still_blocked()
    test_aneel_gov_br_chamadas_path_keeps_with_short_desc()
    print("ok")
