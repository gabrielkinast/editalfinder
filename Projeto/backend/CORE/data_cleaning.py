"""Normalização de aliases, limpeza de texto e HTML (Unicode preservado)."""
from __future__ import annotations

import html as html_module
import re
from typing import Any, Dict, List, Optional, Tuple

_SCRIPT_STYLE_RE = re.compile(
    r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL
)
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"[ \t\r\f\v]+")
_MULTILINE_WS = re.compile(r"\n{3,}")

# (campo_canonico, [aliases...])
_FIELD_ALIASES: List[Tuple[str, Tuple[str, ...]]] = [
    (
        "titulo",
        (
            "title",
            "name",
            "nome",
            "chamada",
            "edital",
            "oportunidade",
            "objeto",
        ),
    ),
    (
        "descricao",
        (
            "description",
            "resumo",
            "summary",
            "snippet",
            "texto",
            "conteudo",
            "content",
            "objetivo",
            "detalhes",
            "details",
        ),
    ),
    (
        "link",
        (
            "url",
            "href",
            "url_detalhe",
            "detail_url",
            "link_detalhe",
            "pagina",
            "page_url",
            "url_chamada",
            "url_pagina",
        ),
    ),
    (
        "fonte",
        (
            "source",
            "origem",
            "portal",
            "orgao",
            "instituicao",
            "institution",
        ),
    ),
    (
        "data_publicacao",
        (
            "published_at",
            "publication_date",
            "data",
            "data_inicio",
            "publicado_em",
        ),
    ),
    (
        "fim_inscricao",
        (
            "deadline",
            "closing_date",
            "prazo",
            "prazo_envio",
            "data_fim",
            "submission_deadline",
            "application_deadline",
            "inscricoes_fim",
        ),
    ),
    (
        "valor",
        (
            "amount",
            "funding",
            "budget",
            "valor_total",
            "valor_maximo",
            "recurso",
            "financiamento",
        ),
    ),
    (
        "programa",
        ("program", "linha", "linha_programa", "chamada_programa"),
    ),
    (
        "tipo_recurso",
        ("resource_type", "modalidade", "tipo", "categoria", "type"),
    ),
    (
        "acao",
        ("action", "acao_programa"),
    ),
    (
        "regiao",
        ("region", "abrangencia"),
    ),
]

_EXTRAS_ALIASES = ("extras", "metadata", "meta", "detalhes_extras")


def _first_str(item: Dict[str, Any], keys: Tuple[str, ...]) -> Optional[str]:
    for k in keys:
        v = item.get(k)
        if v is None:
            continue
        if isinstance(v, str) and v.strip():
            return v.strip()
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return str(v).strip()
    return None


def normalize_aliases(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Copia o item e preenche campos canónicos a partir de aliases.
    Chaves desconhecidas úteis permanecem no dict raiz para merge posterior em extras.
    """
    if not isinstance(item, dict):
        return {}
    out: Dict[str, Any] = dict(item)
    known_aliases = set()
    for canon, aliases in _FIELD_ALIASES:
        known_aliases.add(canon)
        known_aliases.update(aliases)
    for canon, aliases in _FIELD_ALIASES:
        if out.get(canon) is not None and str(out.get(canon)).strip():
            continue
        val = _first_str(out, (canon,) + aliases)
        if val is not None:
            out[canon] = val
    # extras: primeiro nome canónico
    ex = None
    for ek in _EXTRAS_ALIASES:
        v = out.get(ek)
        if isinstance(v, dict):
            ex = dict(v)
            break
    if ex is not None:
        out["extras"] = ex
        for ek in _EXTRAS_ALIASES:
            if ek != "extras" and ek in out:
                del out[ek]
    elif "extras" not in out or not isinstance(out.get("extras"), dict):
        out["extras"] = {}
    return out


def clean_html(value: Optional[str]) -> str:
    """Remove tags HTML/script/style; preserva texto; entidades decodificadas."""
    if not value or not isinstance(value, str):
        return ""
    t = _SCRIPT_STYLE_RE.sub(" ", value)
    t = _TAG_RE.sub(" ", t)
    t = html_module.unescape(t)
    return t


def clean_text(value: Optional[str], *, max_chars: Optional[int] = None) -> str:
    """
    Normaliza espaços, remove NUL e caracteres de controlo problemáticos.
    Unicode (CJK, acentos) preservado.
    """
    if not value:
        return ""
    if not isinstance(value, str):
        value = str(value)
    if "\x00" in value:
        value = value.replace("\x00", "")
    # remove C0 exceto \n e \t
    value = "".join(ch for ch in value if ord(ch) >= 32 or ch in "\n\t\r")
    value = _WS_RE.sub(" ", value)
    value = _MULTILINE_WS.sub("\n\n", value)
    value = value.strip()
    if max_chars is not None and len(value) > max_chars:
        return value[:max_chars].rstrip()
    return value


def clean_text_fields(item: Dict[str, Any], keys: Tuple[str, ...]) -> None:
    """In-place: limpa strings dos campos listados."""
    for k in keys:
        v = item.get(k)
        if isinstance(v, str):
            item[k] = clean_text(clean_html(v))


def _build_canonical_item_keys() -> frozenset:
    s: set = set()
    for canon, aliases in _FIELD_ALIASES:
        s.add(canon)
        s.update(aliases)
    s.update(
        {
            "extras",
            "metadata",
            "meta",
            "detalhes_extras",
            "situacao",
            "valor_minimo",
            "publico_alvo",
            "temas",
            "contrapartida",
            "elegibilidade",
            "contato",
            "link_inscricao",
            "ods",
            "anexos",
            "documentos",
            "score",
            "score_detalhado",
            "justificativa",
            "recomendacao",
            "compatibilidade",
        }
    )
    return frozenset(s)


CANONICAL_ITEM_KEYS = _build_canonical_item_keys()
