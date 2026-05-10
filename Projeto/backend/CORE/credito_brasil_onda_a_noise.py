"""
Filtros de ruido — Onda A Credito/Desenvolvimento (Brasil).

Usado pelos crawlers e pelo transformer (rejeicao local, sem alterar opportunity_gate).
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Optional, Pattern, Set, Tuple

_ONDA_A_SOURCES: Set[str] = {
    "bnb",
    "banco_da_amazonia",
    "bdmg",
    "agerio",
    "desenvolve_sp",
}

# Padroes de URL (segmento ou host path) — evitar substring dentro de slug de produto.
_URL_NOISE_REGEX: Tuple[Tuple[str, Pattern[str]], ...] = (
    ("contato_path", re.compile(r"/contato(?:/|$|\?|#)", re.I)),
    ("fale_conosco", re.compile(r"fale[-_]conosco", re.I)),
    ("atendimento", re.compile(r"/atendimento(?:/|$|\?|#)|central[-_]de[-_]atendimento", re.I)),
    ("ouvidoria", re.compile(r"/ouvidoria(?:/|$|\?|#)", re.I)),
    ("faq", re.compile(r"/faq(?:/|$|\?|#)|perguntas[-_]frequentes|duvidas[-_]frequentes", re.I)),
    ("login", re.compile(r"/login(?:/|$|\?|#)|/log[-_]in", re.I)),
    ("internet_banking", re.compile(r"internet[-_]banking|internetbanking", re.I)),
    ("autoatendimento", re.compile(r"auto[-_]?atendimento", re.I)),
    ("abra_conta", re.compile(r"abra[-_]sua[-_]conta|/abrir[-_]conta", re.I)),
    ("conta_digital", re.compile(r"/conta[-_]digital|/conta[-_]corrente|/conta[-_]pj|/conta[-_]pf|/minha[-_]conta", re.I)),
    ("renegociacao", re.compile(r"renegociacao|renegocia[cç][aã]o[-_]de[-_]d[ií]vidas", re.I)),
    ("educacao_financeira", re.compile(r"educacao[-_]?financeira|educacaofinanceira", re.I)),
    ("quem_somos", re.compile(r"/quem[-_]somos(?:/|$|\?|#)", re.I)),
    ("institucional", re.compile(r"/institucional(?:/|$|\?|#)", re.I)),
    ("relacionamento", re.compile(r"/relacionamento(?:/|$|\?|#)", re.I)),
    ("privacidade", re.compile(r"politica[-_]de[-_]privacidade|/privacidade(?:/|$|\?|#)|/cookies", re.I)),
    ("carreiras", re.compile(r"/trabalhe[-_]conosco|/carreiras(?:/|$|\?|#)", re.I)),
    ("imprensa", re.compile(r"/imprensa/|sala[-_]de[-_]imprensa|sala[-_]imprensa", re.I)),
    ("noticias_blog", re.compile(r"/noticias/|/blog/", re.I)),
)

# BDMG / bancos: hubs institucionais frequentemente capturados pela home.
_URL_INSTITUTIONAL_REGEX: Tuple[Tuple[str, Pattern[str]], ...] = (
    ("sobre_bdmg", re.compile(r"/sobre[-_]bdmg|/sobre[-_]o[-_]banco", re.I)),
    ("documentacao_hub", re.compile(r"/documentos(?:/|$|\?|#)|/documentacao", re.I)),
    ("english_gate", re.compile(r"/en(?:/|$|\?|#)", re.I)),
    ("seja_parceiro", re.compile(r"sejaparceiro", re.I)),
    ("investimento_hub", re.compile(r"/investimento(?:/|$|\?|#)", re.I)),
    ("licitacoes_hub", re.compile(r"editais[-_]licitacoes|editais[-_]venda[-_]bens|licitacoes[-_]contratos[-_]administrativos", re.I)),
    ("transparencia", re.compile(r"transparencia|relacao[-_]investidores", re.I)),
    ("relatorio_sustentabilidade", re.compile(r"relatorio[-_]de[-_]sustentabilidade", re.I)),
    ("correspondente_finder", re.compile(r"correspondente(?:s)?(?:/|$|\?|#)|encontre[-_]correspondente", re.I)),
)


def _match_noise_patterns(lk: str, patterns: Tuple[Tuple[str, Pattern[str]], ...]) -> Optional[str]:
    for name, rx in patterns:
        if rx.search(lk):
            return name
    return None

# Presenca na URL indica pagina de produto de credito/fomento (nao aplicar exclusao institucional generica).
_CREDIT_PRODUCT_URL_HINTS: tuple[str, ...] = (
    "linhaspermanentes",
    "micro-empresa",
    "pequenas-empresas",
    "medio-porte",
    "credito",
    "crédito",
    "financ",
    "fomento",
    "pronampe",
    "pronaf",
    "fungetur",
    "labagro",
    "microcredito",
    "solicitacao-de-credito",
    "produtos-e-servicos",
    "atividades-financiadas",
    "empresas/credito",
    "financiamento-agro",
    "linhas-de-fomento",
    "linhas-de-credito",
    "opcoes-de-credito",
    "guia-do-financiamento",
    "negocios/online",
    "areas-de-atuacao",
    "bdmgorienta",
    "orienta",
    "fno",
    "finame",
    "fne",
    "fgi",
    "pronamp",
    "agronegocio",
    "inovacao",
    "empreendedor",
    "microempreendedor",
    "plano-safra",
    "agro",
)

_TITLE_NOISE_EXACT: frozenset[str] = frozenset(
    {
        "contato",
        "fale conosco",
        "entre em contato",
        "central de atendimento",
        "ouvidoria",
        "faq",
        "perguntas frequentes",
        "login",
        "internet banking",
        "abra sua conta",
        "abrir conta",
        "conta digital",
        "conta corrente",
        "menu",
        "quem somos",
        "english",
        "institucional",
        "correspondentes bancários",
        "correspondentes bancarios",
        "sobre o bdmg",
        "atuação",
        "atuacao",
        "nossa essência",
        "nossa essencia",
        "licitações e contratos",
        "licitacoes e contratos",
        "sala de imprensa",
        "notícias",
        "noticias",
        "eventos",
        "documentação bdmg",
        "documentacao bdmg",
        "segurança da informação e cibernética",
        "seguranca da informacao e cibernetica",
        "proteção de dados e privacidade",
        "protecao de dados e privacidade",
        "conhecimento",
        "saiba mais",
        "download",
        "encontre um correspondente",
        "titulos sustentáveis",
        "titulos sustentaveis",
    }
)

_TITLE_NOISE_SUBSTRINGS: Tuple[str, ...] = (
    "trabalhe no bdmg",
    "plano de cargos",
    "carreiras no bdmg",
)

_TITLE_NOISE_PREFIXES: Tuple[str, ...] = (
    "contato —",
    "contato -",
    "fale com",
    "acesse sua conta",
    "acesse seu ",
    "política de privacidade",
    "politica de privacidade",
)


def _norm_txt(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def credit_url_hint(lk: str) -> bool:
    low = (lk or "").lower()
    return any(h in low for h in _CREDIT_PRODUCT_URL_HINTS)


def credito_brasil_onda_a_ruido_motivo(
    source_name: str,
    titulo: str,
    descricao: str,
    link: str,
    extras: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """
    Retorna motivo corto se o item deve ser tratado como ruido institucional/bancario
    (nao oportunidade de credito/fomento neste lote). None se nao for ruido conhecido.
    """
    src = (source_name or "").strip().lower()
    if src and src not in _ONDA_A_SOURCES:
        return None

    lk = (link or "").lower()
    tit_n = _norm_txt(titulo or "")
    blob = _norm_txt(f"{titulo} {descricao} {link}")

    _strong_credit_path = (
        "pronampe",
        "linhaspermanentes",
        "micro-empresa",
        "pequenas-empresas",
        "solicitacao-de-credito",
        "microcredito",
        "produtos-e-servicos",
        "linhas-de-credito",
        "opcoes-de-credito",
        "credito-e-financiamento",
        "financiamento-agro",
        "linhas-de-fomento",
        "bdmgorienta",
        "atividades-financiadas",
        "guia-do-financiamento",
        "negocios/online",
        "areas-de-atuacao",
    )

    if credit_url_hint(lk):
        if tit_n in _TITLE_NOISE_EXACT or any(tit_n.startswith(p) for p in _TITLE_NOISE_PREFIXES):
            if any(x in lk for x in _strong_credit_path):
                return None
            return f"titulo_ruido_url_ambigua:{tit_n[:60]}"
        return None

    hit = _match_noise_patterns(lk, _URL_NOISE_REGEX)
    if hit:
        return f"url_institucional:{hit}"

    hit = _match_noise_patterns(lk, _URL_INSTITUTIONAL_REGEX)
    if hit:
        return f"url_institucional:{hit}"

    if tit_n in _TITLE_NOISE_EXACT:
        return f"titulo_institucional:{tit_n[:80]}"

    for sub in _TITLE_NOISE_SUBSTRINGS:
        if sub in tit_n:
            return f"titulo_institucional_contains:{sub}"

    for pref in _TITLE_NOISE_PREFIXES:
        if tit_n.startswith(pref):
            return f"titulo_institucional:{pref}"

    # Titulo curto + sem sinal de credito no titulo/URL
    if len(tit_n) <= 22 and tit_n:
        if not any(
            k in blob
            for k in (
                "credito",
                "crédito",
                "financ",
                "fomento",
                "linha",
                "micro",
                "rural",
                "agro",
                "pronaf",
                "pronampe",
                "emprestimo",
                "finame",
                "fno",
            )
        ):
            if any(k in tit_n for k in ("menu", "home", "busca", "login", "conta")):
                return "titulo_curto_navegacao"

    return None


def crawler_link_exclude_extra() -> list[str]:
    """
    Fragmentos conservadores para link_url_exclude_substrings (scraper usa 'in').
    Mantidos curtos para nao cortar slugs de produto; validacao fina e em regex no transformer.
    """
    return [
        "/fale-conosco",
        "/ouvidoria",
        "/internet-banking",
        "/educacao-financeira",
        "/quem-somos",
        "/sala-de-imprensa",
        "sala-imprensa",
        "/sobre-bdmg",
        "sejaparceiro",
        "/investimento",
        "editais-licitacoes",
        "relacao-investidores",
        "/en/",
        "/documentos",
        "/login",
        "/institucional/",
        "educacaofinanceira",
        "renegociacao",
        "conta-pj",
        "/concurso",
    ]


def crawler_should_drop_item(titulo: str, link: str, descricao: str = "") -> Optional[str]:
    """Usado pos-scrape nos crawlers; descricao opcional."""
    return credito_brasil_onda_a_ruido_motivo("", titulo, descricao, link, None)
