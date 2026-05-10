"""Classificacao operacional de destino: edital, noticia ou pesquisa."""
from __future__ import annotations

import re
from typing import Any, Dict


NEWS_HINTS = (
    "/news/",
    "/noticias/",
    "/noticia/",
    "/press/",
    "/releases/",
    "press release",
    "comunicado",
    "noticia",
    "notícia",
    "publicado em",
    "redacao",
    "redação",
    "ministro",
    "secretario",
    "secretário",
    "reuniao",
    "reunião",
)

RESEARCH_HINTS = (
    "artigo cientifico",
    "artigo científico",
    "paper",
    "journal",
    "publication",
    "published in",
    "research article",
    "pesquisa publicada",
    "resultado de pesquisa",
    "scientific result",
    "dataset",
    "preprint",
    "doi:",
    "doi.org/",
    "laboratorio",
    "laboratório",
    "linha de pesquisa",
    "research program",
)

OPPORTUNITY_HINTS = (
    "edital",
    "chamada",
    "call for proposals",
    "call for applications",
    "grant",
    "funding opportunity",
    "licitação",
    "licitacao",
    "pregão",
    "pregao",
    "tender",
    "procurement",
    "rfp",
    "submissão",
    "submissao",
    "inscrições",
    "inscricoes",
    "deadline",
    "prazo",
    "bolsa",
    "fomento",
    "financiamento",
    "supplier portal",
)

TYPE_OPPORTUNITY_HINTS = (
    "edital",
    "chamada",
    "chamada_publica",
    "call for proposals",
    "call for applications",
    "grant",
    "funding_opportunity",
    "funding opportunity",
    "licitação",
    "licitacao",
    "pregão",
    "pregao",
    "tender",
    "procurement",
    "rfp",
    "bolsa",
    "fomento",
    "financiamento",
    "subvencao",
    "subvenção",
)

TYPE_RESEARCH_HINTS = (
    "paper",
    "artigo cientifico",
    "artigo científico",
    "research article",
    "publicacao",
    "publicação",
    "dataset",
    "preprint",
)


def _norm(v: Any) -> str:
    return re.sub(r"\s+", " ", str(v or "")).strip()


def _extras(item: Dict[str, Any]) -> Dict[str, Any]:
    ex = item.get("extras")
    return ex if isinstance(ex, dict) else {}


def has_opportunity_marker(text: str) -> bool:
    low = (text or "").casefold()
    return any(h.casefold() in low for h in OPPORTUNITY_HINTS)


def infer_content_type(item: Dict[str, Any]) -> str:
    """Retorna o tipo de conteudo mais provavel para roteamento de banco."""
    if not isinstance(item, dict):
        return "desconhecido"
    ex = _extras(item)
    tipo_blob = " ".join(
        _norm(x)
        for x in (
            item.get("tipo_oportunidade"),
            item.get("tipo_recurso"),
            ex.get("tipo_oportunidade"),
            ex.get("tipo_recurso"),
        )
        if _norm(x)
    ).casefold()
    type_is_news = "noticia" in tipo_blob or "notícia" in tipo_blob or "comunicado" in tipo_blob or "press" in tipo_blob
    if any(h.casefold() in tipo_blob for h in TYPE_OPPORTUNITY_HINTS):
        return "edital"
    if any(h.casefold() in tipo_blob for h in TYPE_RESEARCH_HINTS):
        return "pesquisa"
    explicit = _norm(
        item.get("content_type")
        or item.get("content_type_detectado")
        or ex.get("content_type")
        or ex.get("content_type_detectado")
        or ex.get("tipo_conteudo")
    ).casefold()
    if explicit in {"edital", "oportunidade", "chamada_publica", "licitacao", "compra_publica", "supplier_portal", "grant", "funding_opportunity"}:
        return "edital"
    if explicit in {"noticia", "news", "press_release", "comunicado"}:
        return "noticia"
    if explicit in {"pesquisa", "research", "paper", "publicacao", "publicação", "dataset"}:
        return "pesquisa"

    text = "\n".join(
        _norm(x)
        for x in (
            item.get("titulo"),
            item.get("descricao"),
            item.get("link"),
            item.get("tipo_recurso"),
            item.get("tipo_oportunidade"),
            ex.get("tipo_oportunidade"),
            ex.get("origem_portal"),
            ex.get("descricao_original"),
            ex.get("titulo_original"),
        )
    )
    low = text.casefold()
    has_opp = has_opportunity_marker(low)
    if has_opp:
        return "edital"
    if type_is_news:
        return "noticia"
    link_low = _norm(item.get("link")).casefold()
    if any(h.casefold() in link_low for h in NEWS_HINTS):
        return "noticia"
    if any(h.casefold() in low for h in RESEARCH_HINTS):
        return "pesquisa"
    if any(h.casefold() in low for h in NEWS_HINTS):
        return "noticia"
    return "edital"


def destination_table_for_item(item: Dict[str, Any]) -> str:
    ct = infer_content_type(item)
    if ct == "noticia":
        return "noticia"
    if ct == "pesquisa":
        return "pesquisa"
    return "edital"


def apply_content_type(item: Dict[str, Any], content_type: str) -> None:
    if not isinstance(item, dict):
        return
    ct = content_type or infer_content_type(item)
    item["content_type"] = ct
    ex = item.get("extras")
    if not isinstance(ex, dict):
        ex = {}
        item["extras"] = ex
    ex["content_type"] = ct
    ex["destination_table"] = destination_table_for_item(item)
