"""Detecção de ruído, URLs inválidas, tipo de conteúdo e regras de descarte."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

# Título exato (após strip); comparação case-insensitive para Latin
_EXACT_DISCARD_TITLES_LOWER = frozenset(
    {
        "contato",
        "contact",
        "saiba mais",
        "learn more",
        "menu",
        "home",
        "início",
        "inicio",
        "login",
        "entrar",
        "sign in",
        "lorem ipsum",
    }
)

# Títulos curtos só de navegação (exact)
_EXACT_CJK_NAV = frozenset(
    {
        "首页",
        "联系我们",
        "登录",
        "詳細",
        "お問い合わせ",
    }
)

_OPPORTUNITY_SUBSTRINGS = (
    "招标",
    "投标",
    "采购",
    "公示",
    "公募",
    "募集",
    "助成",
    "课题",
    "项目申报",
    "edital",
    "chamada",
    "chamada pública",
    "chamada publica",
    "fomento",
    "subvenção",
    "subvencao",
    "financiamento",
    "licitação",
    "licitacao",
    "pregão",
    "pregao",
    "compra pública",
    "compra publica",
    "contrato",
    "seleção",
    "selecao",
    "bolsa",
    "grant",
    "funding",
    "tender",
    "procurement",
    "call for proposals",
    "call for applications",
    "deadline",
    "inscrições",
    "inscricoes",
    "submissão",
    "submissao",
    "programa",
    "oportunidade",
    "crédito",
    "credito",
    "rfp",
    "bidding",
)

_NEWS_WEAK_HINTS = (
    "/news/",
    "/noticias/",
    "/press/",
    "press release",
    "comunicado",
    "breaking news",
    "お知らせ",
)

_RESEARCH_WEAK_HINTS = (
    "paper",
    "publication",
    "published in",
    "journal",
    "research article",
    "resultado de pesquisa",
    "pesquisa publicada",
    "scientific result",
    "dataset",
    "doi.org/",
    "doi:",
    "linha de pesquisa",
)


def _norm_title(t: str) -> str:
    return (t or "").strip()


def is_noise_title(title: str) -> bool:
    """True só para título de navegação exato (não substring em frase longa)."""
    t = _norm_title(title)
    if not t:
        return True
    if t in _EXACT_CJK_NAV:
        return True
    if t.casefold() in _EXACT_DISCARD_TITLES_LOWER:
        return True
    return False


def is_noise_url(url: Optional[str]) -> bool:
    if not url or not isinstance(url, str):
        return True
    u = url.strip()
    if not u:
        return True
    low = u.lower().strip()
    if low.startswith("javascript:"):
        return True
    if low in ("#", "about:blank"):
        return True
    if low.endswith("#") and low.count("/") <= 1:
        return True
    return False


def has_opportunity_signal(text: str) -> bool:
    low = (text or "").casefold()
    for s in _OPPORTUNITY_SUBSTRINGS:
        if s.casefold() in low or s in (text or ""):
            return True
    return False


def detect_content_type(
    *,
    titulo: str,
    descricao: str,
    link: str,
    full_text: str,
) -> str:
    corpus = f"{titulo}\n{descricao}\n{link}\n{full_text}".casefold()
    raw = f"{titulo}\n{descricao}\n{link}\n{full_text}"
    lk_cf = (link or "").strip().casefold()
    if "topic-details/horizon-" in lk_cf and "europa.eu" in lk_cf:
        return "chamada_publica"
    if "erc.europa.eu/apply-grant/" in lk_cf:
        return "chamada_publica"
    if "arpa-e-foa.energy.gov" in lk_cf and "#foaid" in lk_cf:
        return "chamada_publica"
    if "diana.nato.int" in lk_cf:
        return "chamada_publica"
    # 100+ Accelerator (AB InBev): páginas de desafio temático — open innovation, não notícia genérica.
    if "100accelerator.com" in lk_cf and "/challenges/" in lk_cf:
        segs = [s for s in lk_cf.split("/") if s]
        try:
            ix = segs.index("challenges")
        except ValueError:
            ix = -1
        if ix >= 0 and ix + 1 < len(segs) and segs[ix + 1] not in ("challenges", "challenge", ""):
            return "chamada_publica"
    if has_opportunity_signal(raw):
        if any(x in corpus for x in ("licitação", "licitacao", "pregão", "pregao", "compra pública", "compra publica")):
            return "licitacao"
        if any(x in corpus for x in ("招标", "投标", "采购", "tender", "procurement", "bidding", "rfp")):
            return "compra_publica"
        if any(x in corpus for x in ("chamada pública", "chamada publica", "edital", "grant", "funding", "fomento", "公募", "募集")):
            return "chamada_publica"
        return "oportunidade"

    low_path = (link or "").strip().casefold().split("?", 1)[0]
    if low_path.endswith(".pdf"):
        lk = (link or "").casefold()
        if any(
            h in lk
            for h in (
                "gov.br",
                "bndes.gov.br",
                "finep.gov.br",
                "cnpq.br",
                "aneel.gov.br",
            )
        ):
            return "documento_oficial"
        return "pdf_documento"

    low_link = link.casefold()
    for h in _NEWS_WEAK_HINTS:
        if h.casefold() in low_link or h in link:
            return "noticia"

    if any(h.casefold() in corpus for h in _RESEARCH_WEAK_HINTS):
        return "pesquisa"

    if len(_norm_title(titulo)) >= 20 and not has_opportunity_signal(raw):
        # Texto longo sem sinal pode ser notícia ou página institucional
        if any(k in corpus for k in ("published", "publicado em", "reporter", "redação", "redacao")):
            return "noticia"

    if len(_norm_title(titulo)) < 8 and len((descricao or "").strip()) < 80:
        return "pagina_generica"

    return "desconhecido"


def is_navigation_page(item: Dict[str, Any], link: str, titulo: str) -> bool:
    if is_noise_title(titulo):
        return True
    low = link.casefold()
    for frag in ("/contact", "/contato", "/login", "/signin", "/home", "/default.aspx", "search?", "query="):
        if frag in low:
            if not has_opportunity_signal(f"{titulo} {item.get('descricao', '')}"):
                return True
    return False


def should_discard_item(
    *,
    titulo: str,
    descricao: str,
    link: str,
    pdf_url: Optional[str],
    full_text: str,
    extras: Dict[str, Any],
) -> Tuple[bool, str, str, List[str]]:
    """Heurísticas locais (pré-gate). O opportunity_gate é aplicado no transformer."""
    sinais: List[str] = []
    ct = detect_content_type(titulo=titulo, descricao=descricao, link=link, full_text=full_text)

    if is_noise_title(titulo):
        return True, "titulo_ruido_exato", ct, ["exact_nav_title"]

    pdf_ok = bool((pdf_url or "").strip()) and str(pdf_url).strip().lower().startswith("http")
    link_st = (link or "").strip()
    if "javascript:void" in link_st.lower() or link_st.lower().startswith("javascript:") or link_st in ("#",):
        if not pdf_ok:
            return True, "url_invalido", ct, ["javascript_or_hash_url"]

    if not link_st.startswith("http") and not pdf_ok:
        return True, "sem_link", ct, ["no_http_link_no_pdf"]

    if is_noise_url(link_st) and not pdf_ok:
        return True, "url_invalido", ct, ["invalid_or_empty_url"]

    if ct == "noticia" and not has_opportunity_signal(full_text):
        return True, "noticia_sem_oportunidade", "noticia", ["news_pattern_no_opportunity_signal"]

    t_ok = len(_norm_title(titulo)) >= 4 and not is_noise_title(titulo)
    d_ok = len((descricao or "").strip()) >= 40
    docs = extras.get("documentos") if isinstance(extras.get("documentos"), list) else []
    has_doc = bool(docs) or pdf_ok
    if not t_ok and not d_ok and not has_doc:
        return True, "sem_conteudo_util", ct, ["no_title_no_desc_no_doc"]

    if len(_norm_title(titulo)) < 4 and not d_ok and not has_doc:
        return True, "titulo_curto_sem_contexto", ct, ["short_title_no_context"]

    return False, "", ct, sinais
