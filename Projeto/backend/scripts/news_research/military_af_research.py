#!/usr/bin/env python3
"""
Crawlers e relevância — expansão militar/técnico-científica (AFMC, AFNWC, Space Force, ARL, AFRL tech areas).
Import tardio de crawl_news_research_sources para evitar ciclo.
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

_DOD_ARTICLE_RE = re.compile(
    r"/News/Article-Display/Article/(\d+)/([^/?#]+)",
    re.I,
)
_DOD_WAYBACK_WEB = "https://web.archive.org/web/2025/"

_DOD_AFMIL_SITES: Dict[str, Dict[str, Any]] = {
    "afmc_news": {
        "base": "https://www.afmc.af.mil",
        "news_hub": "https://www.afmc.af.mil/News/",
        "domain": "afmc.af.mil",
        "inst": "AFMC",
        "display": "AFMC",
        "extra_positive": (
            ("logistics", "logistica_militar"),
            ("acquisition", "industria_estrategica"),
            ("sustainment", "logistica_militar"),
            ("maintenance", "engenharia_avancada"),
            ("modernization", "engenharia_avancada"),
            ("test ", "engenharia_avancada"),
            ("test course", "engenharia_avancada"),
            ("engineering", "engenharia_avancada"),
            ("readiness", "defesa"),
            ("industry", "industria_estrategica"),
            ("collaboration", "industria_estrategica"),
            ("digital", "computacao"),
            ("software", "computacao"),
        ),
    },
    "afnwc_news": {
        "base": "https://www.afnwc.af.mil",
        "news_hub": "https://www.afnwc.af.mil/News/",
        "domain": "afnwc.af.mil",
        "inst": "AFNWC",
        "display": "AFNWC",
        "extra_positive": (
            ("nuclear", "nuclear"),
            ("weapon system", "sistemas_de_armas"),
            ("icbm", "nuclear"),
            ("minuteman", "nuclear"),
            ("sustainment", "sistemas_de_armas"),
            ("warhead", "nuclear"),
            ("strategic", "defesa"),
            ("modernization", "engenharia_avancada"),
        ),
    },
    "space_force_news": {
        "base": "https://www.spaceforce.mil",
        "news_hub": "https://www.spaceforce.mil/News/",
        "domain": "spaceforce.mil",
        "inst": "U.S. Space Force",
        "display": "U.S. Space Force",
        "extra_positive": (
            ("satellite", "satelites"),
            ("launch", "espaco"),
            ("orbital", "espaco"),
            ("cislunar", "espaco"),
            ("space domain", "espaco"),
            ("domain awareness", "espaco"),
            (" sda ", "espaco"),
            ("guardian", "espaco"),
            ("spacelift", "espaco"),
            ("gps", "satelites"),
            ("missile warning", "sensores"),
            ("space system", "espaco"),
            ("communications", "comunicacoes"),
            ("communication", "comunicacoes"),
            ("cyber", "cyber"),
            ("innovation", "inovacao"),
            ("industry partner", "industria_estrategica"),
            ("partnership", "industria_estrategica"),
        ),
    },
}

# Prioridade operacional (probe 2026-05): live 200 primeiro; Wayback para hubs /News/
MILITARY_SOURCE_PRIORITY: Tuple[str, ...] = (
    "afrl_technology_areas",
    "arl_news",
    "arl_resources",
    "afnwc_innovation",
    "afnwc_weapon_systems",
    "space_force_news",
    "afnwc_news",
    "afmc_news",
)

_ARL_NEWS_POSITIVE: Tuple[Tuple[str, str], ...] = (
    ("material", "materiais_avancados"),
    ("composite", "materiais_avancados"),
    ("robot", "robotica"),
    ("autonom", "autonomia"),
    ("artificial intelligence", "inteligencia_artificial"),
    ("machine learning", "inteligencia_artificial"),
    (" ai ", "inteligencia_artificial"),
    ("sensor", "sensores"),
    ("lidar", "sensores"),
    ("energy", "energia"),
    ("battery", "energia"),
    ("cyber", "cyber"),
    ("comput", "computacao"),
    ("soldier", "defesa"),
    ("lethality", "defesa"),
    ("weapon", "sistemas_de_armas"),
    ("munition", "sistemas_de_armas"),
    ("engineering", "engenharia_avancada"),
    ("research", "pesquisa"),
    ("laboratory", "pesquisa"),
    ("defense research", "defesa"),
    ("devcom", "defesa"),
    ("additive manufactur", "materiais_avancados"),
    ("drone", "autonomia"),
    ("electronic warfare", "guerra_eletronica"),
)

_TECH_AREA_EIXOS: Dict[str, List[str]] = {
    "aerospace": ["aeroespacial", "defesa", "propulsao"],
    "artificial-intelligence": ["inteligencia_artificial", "computacao", "defesa"],
    "basic-research": ["pesquisa", "defesa"],
    "cross-domain": ["defesa", "aeroespacial", "espaco"],
    "directed-energy": ["energia_dirigida", "defesa"],
    "human-performance": ["pesquisa", "defesa"],
    "information": ["computacao", "comunicacoes", "cyber"],
    "integrated-capabilities": ["defesa", "engenharia_avancada"],
    "materials-manufacturing": ["materiais_avancados", "engenharia_avancada"],
    "munitions": ["sistemas_de_armas", "defesa"],
    "quantum": ["computacao", "defesa"],
    "sensors": ["sensores", "radar", "defesa"],
    "space": ["espaco", "satelites", "aeroespacial"],
    "vanguards": ["inovacao", "defesa", "aeroespacial"],
    "science-technology-strategy": ["defesa", "pesquisa", "engenharia_avancada"],
}

_AFNWC_PORTAL_CONFIG: Dict[str, Dict[str, Any]] = {
    "afnwc_innovation": {
        "hub": "https://www.afnwc.af.mil/Innovation/",
        "titulo_portal": "AFNWC Innovation",
        "descricao": (
            "Nuclear enterprise innovation programs, modernization and technical integration "
            "at Air Force Nuclear Weapons Center."
        ),
        "tipo_pesquisa": "portal_institucional",
        "tipo_recurso": "portal_estrategico",
        "areas": ["nuclear", "defesa", "inovacao", "engenharia_avancada", "aeroespacial"],
        "path_allow": ("/innovation", "/fact-sheet", "/modernization", "/integration"),
    },
    "afnwc_weapon_systems": {
        "hub": "https://www.afnwc.af.mil/Weapon-Systems/",
        "titulo_portal": "AFNWC Weapon Systems",
        "descricao": (
            "Strategic weapon systems portfolio — ICBM, nuclear sustainment and "
            "modernization programs."
        ),
        "tipo_pesquisa": "portal_institucional",
        "tipo_recurso": "sistema_estrategico",
        "areas": ["nuclear", "sistemas_de_armas", "defesa", "engenharia_avancada"],
        "path_allow": ("/weapon-systems", "/fact-sheet", "/minuteman", "/icbm", "/lgm"),
    },
}

_ARL_RESOURCES_DENY = frozenset(
    {
        "careers",
        "privacy",
        "foia",
        "eeo",
        "visitor",
        "benefits",
        "student-in-processing",
        "civilian-in-processing",
        "veterans",
        "rotc",
        "business-professionals",
        "pay-for-performance",
        "no_fear",
    }
)

STRATEGIC_MILITARY_NEWS_IDS = frozenset(_DOD_AFMIL_SITES.keys()) | frozenset({"arl_news"})
STRATEGIC_MILITARY_PESQUISA_IDS = frozenset(
    {
        "afrl_technology_areas",
        "afnwc_innovation",
        "afnwc_weapon_systems",
        "arl_resources",
    }
)
STRATEGIC_MILITARY_ALL_IDS = STRATEGIC_MILITARY_NEWS_IDS | STRATEGIC_MILITARY_PESQUISA_IDS


def _c() -> Any:
    from scripts import crawl_news_research_sources as mod

    return mod


def _dod_wayback_enabled() -> bool:
    v = os.environ.get("DOD_AFMIL_WAYBACK_FALLBACK", "").strip().lower()
    if v in ("1", "true", "yes"):
        return True
    return os.environ.get("AFRL_WAYBACK_FALLBACK", "").strip().lower() in ("1", "true", "yes")


def _dod_unwrap_wayback(url: str) -> str:
    return _c()._afrl_unwrap_wayback_url(url)


def _dod_parse_listing_date(text: str) -> Optional[str]:
    return _c()._afrl_parse_listing_date(text)


def _dod_http_get(url: str, timeout: int = 60) -> Tuple[Optional[requests.Response], str]:
    """GET com fallback Wayback para domínios .af.mil / spaceforce.mil bloqueados."""
    mod = _c()
    low = (url or "").lower()
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    wb_first = _dod_wayback_enabled() and any(
        d in low for d in (".af.mil", "spaceforce.mil")
    ) and bool(re.search(r"/news/?(\?|$)", low, re.I))

    def _try_wayback() -> Tuple[Optional[requests.Response], str]:
        wb_url = _DOD_WAYBACK_WEB + _dod_unwrap_wayback(url)
        try:
            wr = requests.get(wb_url, headers=headers, timeout=timeout + 25)
            if wr.status_code < 400 and len((wr.text or "").strip()) > 500:
                return wr, "wayback"
        except Exception:
            pass
        return None, "failed"

    if wb_first:
        wr, mode = _try_wayback()
        if wr:
            return wr, mode

    r = mod._http_get(url, timeout=timeout)
    if r and r.status_code == 200 and len((r.text or "").strip()) > 500:
        return r, "live"
    if not _dod_wayback_enabled():
        return (r if r and r.status_code == 200 else None), "failed" if not r else "live"
    if not any(d in low for d in (".af.mil", "spaceforce.mil", "afresearchlab.com")):
        return (r if r and r.status_code == 200 else None), "failed"
    wr, mode = _try_wayback()
    if wr:
        return wr, mode
    return (r if r and r.status_code == 200 else None), "failed"


def _normalize_dod_article_link(href: str, seed_url: str, domain: str) -> Optional[str]:
    if not href:
        return None
    href = _dod_unwrap_wayback(href)
    link = urljoin(seed_url, href).split("#", 1)[0].rstrip("/")
    if domain not in link.lower():
        return None
    if not _DOD_ARTICLE_RE.search(link):
        return None
    if any(x in link.lower() for x in ("/photos/", "/video/", "/biographies/")):
        return None
    return link


def extract_dod_afmil_news_from_html(
    seed_url: str, body: str, max_items: int, domain: str, inst: str
) -> List[Dict[str, Any]]:
    mod = _c()
    if not body:
        return []
    soup = BeautifulSoup(body, "html.parser")
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for art in soup.select("article.article-listing-item"):
        if len(out) >= max_items:
            break
        a = art.select_one('a[href*="/News/Article-Display/Article/"]')
        if not a:
            continue
        link = _normalize_dod_article_link(a.get("href") or "", seed_url, domain)
        if not link or link in seen:
            continue
        seen.add(link)
        tit = re.sub(r"\s+", " ", (a.get_text() or "").strip())[:320]
        if len(tit) < 12:
            continue
        block_txt = art.get_text(" ", strip=True)
        pub = _dod_parse_listing_date(block_txt) or ""
        desc = ""
        sum_el = art.select_one(".summary, [class*='summary']")
        if sum_el:
            desc = mod._strip_html(sum_el.get_text(), max_len=1200)
        if len(desc) < 25:
            desc = mod._strip_html(block_txt, max_len=800)
        out.append(
            {
                "titulo": tit,
                "descricao": desc[:3000],
                "link": link[:800],
                "data_publicacao_raw": pub,
                "source_method": "dod_afmil_news_listing_html",
                "feed_categories": ["news"],
                "fonte_instituicao_raw": inst,
                "autor": inst,
            }
        )
    if len(out) < max(5, max_items // 3):
        for a in soup.select('a[href*="/News/Article-Display/Article/"]'):
            if len(out) >= max_items:
                break
            link = _normalize_dod_article_link(a.get("href") or "", seed_url, domain)
            if not link or link in seen:
                continue
            seen.add(link)
            tit = re.sub(r"\s+", " ", (a.get_text() or "").strip())[:320]
            if len(tit) < 12:
                continue
            out.append(
                {
                    "titulo": tit,
                    "descricao": "",
                    "link": link[:800],
                    "data_publicacao_raw": "",
                    "source_method": "dod_afmil_news_listing_fallback",
                    "feed_categories": ["news"],
                    "fonte_instituicao_raw": inst,
                    "autor": inst,
                }
            )
    return out


def crawl_dod_afmil_news_listing(
    source_id: str, max_items: int, min_dt: Optional[datetime]
) -> List[Dict[str, Any]]:
    cfg = _DOD_AFMIL_SITES.get(source_id)
    if not cfg:
        return []
    mod = _c()
    hub = str(cfg["news_hub"])
    domain = str(cfg["domain"])
    inst = str(cfg["inst"])
    cap = max(max_items * 3, max_items)
    out: List[Dict[str, Any]] = []
    seen: set = set()
    max_pages = max(4, (cap // 8) + 2)
    for page in range(1, max_pages + 1):
        if len(out) >= cap:
            break
        url = hub if page == 1 else f"{hub}?Page={page}"
        resp, fetch_mode = _dod_http_get(url, timeout=60)
        if not resp:
            break
        batch = extract_dod_afmil_news_from_html(url, resp.text or "", cap, domain, inst)
        if fetch_mode == "wayback":
            for row in batch:
                row["source_method"] = str(row.get("source_method") or "") + "_wayback"
        if not batch and page > 1:
            break
        for r in batch:
            lk = str(r.get("link") or "")
            if lk in seen:
                continue
            dt = mod._parse_date(r.get("data_publicacao_raw"))
            if min_dt and dt and dt < min_dt:
                continue
            seen.add(lk)
            out.append(r)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def _sort_key(row: Dict[str, Any]) -> datetime:
        return mod._parse_date(row.get("data_publicacao_raw")) or epoch

    out.sort(key=_sort_key, reverse=True)
    return out[:cap]


def military_infer_eixo(source_id: str, blob: str, base_eixos: Optional[List[str]] = None) -> List[str]:
    mod = _c()
    out = mod._afrl_infer_eixo(blob, base_eixos or [])
    cfg = _DOD_AFMIL_SITES.get(source_id) or {}
    seen = set(out)
    b = (blob or "").lower()
    for needle, eixo in cfg.get("extra_positive") or ():
        if needle in b and eixo not in seen:
            seen.add(eixo)
            out.append(eixo)
    return out[:12]


def evaluate_arl_news_relevance(r: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """Filtro ARL: pesquisa aplicada militar (probe: media-center HTTP 200)."""
    mod = _c()
    tit = str(r.get("titulo") or "")
    desc = str(r.get("descricao") or "")
    link = str(r.get("link") or "")
    blob = f"{tit} {desc} {link}".lower()
    motivos_neg = [n for n in mod._AFRL_NEGATIVE_SIGNALS if n in blob]
    motivos_pos: List[str] = []
    eixos: List[str] = []
    seen_e: set = set()
    for needle, eixo in _ARL_NEWS_POSITIVE:
        if needle in blob:
            motivos_pos.append(needle.strip())
            if eixo not in seen_e:
                seen_e.add(eixo)
                eixos.append(eixo)
    if not eixos and any(k in blob for k in ("arl", "army research", "devcom")):
        eixos = ["defesa", "pesquisa"]
    meta: Dict[str, Any] = {
        "motivos_relevancia": list(dict.fromkeys(motivos_pos))[:20],
        "motivos_descarte": list(dict.fromkeys(motivos_neg))[:15],
        "eixos_detectados": eixos[:12],
        "relevancia_arl": "media",
        "military_source_id": "arl_news",
    }
    n_pos, n_neg = len(set(motivos_pos)), len(set(motivos_neg))
    possivel_edital = any(m in blob for m in mod._AFRL_OPPORTUNITY_MARKERS)
    meta["possivel_edital"] = possivel_edital
    if possivel_edital:
        return "review", {**meta, "motivo": "sinal_opportunity_arl", "destino_sugerido": "Radar/Editais"}
    if n_pos == 0 and n_neg > 0:
        return "discard", {**meta, "motivo": "sem_sinal_pesquisa_aplicada"}
    if n_pos == 0:
        return "discard", {**meta, "motivo": "sem_sinal_tecnico_arl"}
    if n_neg > 0 and n_pos < 2:
        return "review", {**meta, "motivo": "institucional_com_pesquisa_fraca"}
    meta["relevancia_arl"] = "alta" if n_pos >= 3 else "media"
    return "keep", meta


def military_evaluate_relevance(
    source_id: str, r: Dict[str, Any], *, route: str = "news"
) -> Tuple[str, Dict[str, Any]]:
    if source_id == "arl_news":
        return evaluate_arl_news_relevance(r)
    mod = _c()
    tit = str(r.get("titulo") or "")
    desc = str(r.get("descricao") or "")
    link = str(r.get("link") or "")
    blob = f"{tit} {desc} {link}".lower()
    action, meta = mod._afrl_evaluate_relevance(r, route=route)
    eixos = military_infer_eixo(source_id, blob, meta.get("eixos_detectados") or [])
    meta["eixos_detectados"] = eixos
    meta["military_source_id"] = source_id
    possivel_edital = bool(meta.get("possivel_edital")) or any(
        m in blob for m in mod._AFRL_OPPORTUNITY_MARKERS
    )
    meta["possivel_edital"] = possivel_edital
    if possivel_edital:
        meta["destino_sugerido"] = "Radar/Editais"
        return "review", {**meta, "motivo": "sinal_opportunity"}
    return action, meta


def dod_afmil_news_should_keep_raw(source_id: str, r: Dict[str, Any]) -> Tuple[bool, str]:
    mod = _c()
    cfg = _DOD_AFMIL_SITES.get(source_id) or {}
    domain = str(cfg.get("domain") or "")
    lk = str(r.get("link") or "").strip()
    if domain and domain not in lk.lower():
        return False, "url_fora_dominio"
    if not _normalize_dod_article_link(lk, lk, domain):
        return False, "url_fora_artigo_news"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    body = mod._strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 20 and len(tit) < 40:
        return False, "sem_resumo_minimo"
    return True, ""


def arl_news_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    mod = _c()
    lk = str(r.get("link") or "").strip().lower()
    if "arl.devcom.army.mil" not in lk or "/news/" not in lk:
        return False, "url_fora_noticia_arl"
    if lk.rstrip("/").endswith("/news"):
        return False, "url_indice_news"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    body = mod._strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 15 and len(tit) < 35:
        return False, "sem_resumo_minimo"
    return True, ""


def pesquisa_portal_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 8:
        return False, "titulo_curto"
    lk = str(r.get("link") or "").strip()
    if not lk.startswith("http"):
        return False, "sem_link"
    return True, ""


def crawl_arl_media_center_news(max_items: int, min_dt: Optional[datetime]) -> List[Dict[str, Any]]:
    mod = _c()
    base = "https://arl.devcom.army.mil"
    hubs = [f"{base}/media-center/", f"{base}/news/"]
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for hub in hubs:
        resp, mode = _dod_http_get(hub, timeout=60)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text or "", "html.parser")
        for a in soup.select("a[href]"):
            if len(out) >= max_items * 2:
                break
            href = (a.get("href") or "").strip()
            if not href or href.startswith("#"):
                continue
            link = urljoin(base, href).split("#", 1)[0].rstrip("/")
            low = link.lower()
            if "arl.devcom.army.mil" not in low or "/news/" not in low:
                continue
            if low.endswith("/news"):
                continue
            if link in seen:
                continue
            tit = re.sub(r"\s+", " ", (a.get_text() or "")).strip()[:320]
            if len(tit) < 12:
                continue
            seen.add(link)
            desc = ""
            card = a.find_parent(["article", "motion-element", "div", "li"])
            if card:
                desc = mod._strip_html(card.get_text(" ", strip=True), max_len=800)
            dt_raw = mod._parse_date_from_url(link)
            pub = mod._iso_date(dt_raw) if dt_raw else ""
            out.append(
                {
                    "titulo": tit,
                    "descricao": desc[:3000],
                    "link": link[:800],
                    "data_publicacao_raw": pub,
                    "source_method": f"arl_news_listing_{mode}",
                    "feed_categories": ["news"],
                    "fonte_instituicao_raw": "ARL",
                    "autor": "ARL",
                }
            )
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def _sort_key(row: Dict[str, Any]) -> datetime:
        return mod._parse_date(row.get("data_publicacao_raw")) or epoch

    out.sort(key=_sort_key, reverse=True)
    filtered: List[Dict[str, Any]] = []
    for r in out:
        dt = mod._parse_date(r.get("data_publicacao_raw"))
        if min_dt and dt and dt < min_dt:
            continue
        filtered.append(r)
        if len(filtered) >= max_items:
            break
    return filtered[:max_items]


def _enrich_technology_area_row(row: Dict[str, Any], max_snippet: int = 8) -> None:
    mod = _c()
    link = str(row.get("link") or "")
    if not link.startswith("http"):
        return
    resp, mode = _dod_http_get(link, timeout=35)
    if not resp or not (resp.text or "").strip():
        return
    sn = mod._snippet_from_article_html(resp.text or "")
    if len(sn) >= 40:
        row["descricao"] = sn[:3000]
    row["_page_enriched"] = True
    row["source_method"] = f"{row.get('source_method') or 'afrl_technology_areas'}_detail_{mode}"


def crawl_afrl_technology_areas(max_items: int, *, enrich_detail: bool = True) -> List[Dict[str, Any]]:
    mod = _c()
    hub = "https://afresearchlab.com/technology/"
    resp, mode = _dod_http_get(hub, timeout=60)
    if not resp:
        return []
    soup = BeautifulSoup(resp.text or "", "html.parser")
    out: List[Dict[str, Any]] = []
    seen: set = set()
    enrich_n = 0
    for a in soup.select("a[href]"):
        if len(out) >= max_items:
            break
        href = a.get("href") or ""
        if "/technology/" not in href:
            continue
        link = urljoin(hub, href).split("#", 1)[0].rstrip("/")
        if link in seen or link.rstrip("/").endswith("/technology"):
            continue
        tit = re.sub(r"\s+", " ", (a.get_text() or "")).strip()
        if len(tit) < 4:
            slug = link.rstrip("/").split("/")[-1].replace("-", " ").title()
            tit = slug
        if len(tit) < 4:
            continue
        seen.add(link)
        slug = link.rstrip("/").split("/")[-1]
        areas = list(_TECH_AREA_EIXOS.get(slug, ["defesa", "engenharia_avancada", "pesquisa"]))
        row = {
            "titulo": tit[:320],
            "descricao": f"AFRL technology area — {tit}. Strategic research portfolio.",
            "link": link[:800],
            "data_publicacao_raw": "",
            "source_method": f"afrl_technology_areas_{mode}",
            "feed_categories": ["technology_area", slug],
            "afrl_tech_slug": slug,
            "tipo_pesquisa": "area_tecnologica",
            "tipo_recurso": "area_tecnologica",
            "tipo_oportunidade": "pesquisa_estrategica",
            "area_tecnologica": areas,
            "setor_estrategico": ["defesa", "aeroespacial"],
            "fonte_instituicao_raw": "AFRL",
        }
        if enrich_detail and enrich_n < min(max_items, 15):
            _enrich_technology_area_row(row)
            enrich_n += 1
        out.append(row)
    return out


def classify_arl_resource(link: str, titulo: str, descricao: str = "") -> Dict[str, Any]:
    """Classifica recurso ARL: pesquisa, documento, institucional_latente ou review."""
    blob = f"{titulo} {descricao} {link}".lower()
    mod = _c()
    possivel_edital = any(
        k in blob
        for k in (
            "baa",
            "broad agency",
            "solicitation",
            "opportunity",
            "questions-answers",
            "rfp",
            "sbir",
            "sttr",
            "funding",
            "proposal",
        )
    )
    is_pdf = link.lower().endswith(".pdf")
    static_inst = any(
        k in blob
        for k in (
            "privacy",
            "foia",
            "eeo",
            "visitor",
            "hrpp faq",
            "forms.gov",
        )
    )
    technical_doc = is_pdf or any(
        k in blob
        for k in (
            "database",
            "libs",
            "mil-std",
            "peer review",
            "executive summary",
            "presentation",
            "technical",
            "algorithm",
        )
    )
    cra = "/cras/" in link.lower() or "collaborative research" in blob
    out: Dict[str, Any] = {
        "possivel_edital": possivel_edital,
        "institucional_latente": False,
        "tipo_pesquisa": "portal_institucional",
        "tipo_recurso": "portal_estrategico",
    }
    if possivel_edital:
        out["tipo_pesquisa"] = "portal_institucional"
        out["tipo_recurso"] = "portal_estrategico"
        out["destino_sugerido"] = "Radar/Editais"
        return out
    if cra:
        out["tipo_pesquisa"] = "programa_pesquisa"
        out["tipo_recurso"] = "programa_estrategico"
        return out
    if technical_doc:
        out["tipo_pesquisa"] = "relatorio_tecnico" if is_pdf else "portal_institucional"
        out["tipo_recurso"] = "documento_estrategico" if is_pdf else "portal_estrategico"
        return out
    if static_inst:
        out["institucional_latente"] = True
        out["tipo_pesquisa"] = "portal_institucional"
        out["tipo_recurso"] = "portal_estrategico"
        return out
    return out


def _extract_afnwc_portal_cards_from_html(
    hub: str, body: str, max_items: int, path_allow: Tuple[str, ...]
) -> List[Dict[str, Any]]:
    mod = _c()
    if not body:
        return []
    soup = BeautifulSoup(body, "html.parser")
    base = "https://www.afnwc.af.mil"
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for a in soup.select("a[href]"):
        if len(out) >= max_items:
            break
        href = _dod_unwrap_wayback((a.get("href") or "").strip())
        link = urljoin(base, href).split("#", 1)[0].rstrip("/")
        if "afnwc.af.mil" not in link.lower():
            continue
        low = link.lower()
        if any(x in low for x in ("/news/", "article-display", "biographies", "/about-us/faq")):
            continue
        if path_allow and not any(p in low for p in path_allow):
            if hub.rstrip("/").lower() not in low:
                continue
        tit = re.sub(r"\s+", " ", (a.get_text() or "")).strip()
        if len(tit) < 10:
            continue
        if tit.lower() in ("home", "about us", "news", "contact"):
            continue
        if link in seen:
            continue
        seen.add(link)
        out.append(
            {
                "titulo": tit[:320],
                "descricao": "",
                "link": link[:800],
                "data_publicacao_raw": "",
                "source_method": "afnwc_portal_cards_html",
                "feed_categories": ["portal"],
                "fonte_instituicao_raw": "AFNWC",
            }
        )
    if not out:
        main = soup.find("main") or soup.body
        if main:
            for h in main.find_all(["h2", "h3"]):
                tit = re.sub(r"\s+", " ", (h.get_text() or "")).strip()
                if len(tit) < 10:
                    continue
                out.append(
                    {
                        "titulo": tit[:320],
                        "descricao": mod._strip_html(
                            (h.find_next(["p", "div"]) or h).get_text(" ", strip=True),
                            max_len=600,
                        ),
                        "link": hub[:800],
                        "data_publicacao_raw": "",
                        "source_method": "afnwc_portal_section_html",
                        "feed_categories": ["portal_section"],
                        "fonte_instituicao_raw": "AFNWC",
                    }
                )
                if len(out) >= max_items:
                    break
    return out


def crawl_afnwc_portal(source_id: str, max_items: int) -> List[Dict[str, Any]]:
    cfg = _AFNWC_PORTAL_CONFIG.get(source_id)
    if not cfg:
        return []
    hub = str(cfg["hub"])
    path_allow = tuple(cfg.get("path_allow") or ())
    resp, mode = _dod_http_get(hub, timeout=60)
    cards: List[Dict[str, Any]] = []
    if resp:
        cards = _extract_afnwc_portal_cards_from_html(hub, resp.text or "", max_items, path_allow)
        for c in cards:
            c["source_method"] = f"{c.get('source_method')}_{mode}"
    portal = {
        "titulo": cfg["titulo_portal"],
        "descricao": str(cfg.get("descricao") or "")[:3000],
        "link": hub[:800],
        "data_publicacao_raw": "",
        "source_method": f"afnwc_portal_hub_{mode if resp else 'failed'}",
        "feed_categories": ["portal_hub"],
        "tipo_pesquisa": cfg.get("tipo_pesquisa"),
        "tipo_recurso": cfg.get("tipo_recurso"),
        "area_tecnologica": list(cfg.get("areas") or []),
        "setor_estrategico": ["defesa", "nuclear"],
        "fonte_instituicao_raw": "AFNWC",
        "_portal_cards": cards[: max_items - 1],
    }
    out = [portal]
    out.extend(cards[: max(0, max_items - 1)])
    return out[:max_items]


def crawl_arl_resources(max_items: int) -> List[Dict[str, Any]]:
    mod = _c()
    base = "https://arl.devcom.army.mil"
    hub = f"{base}/resources/"
    resp, mode = _dod_http_get(hub, timeout=60)
    if not resp:
        return []
    soup = BeautifulSoup(resp.text or "", "html.parser")
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for a in soup.select("a[href]"):
        if len(out) >= max_items * 3:
            break
        href = (a.get("href") or "").strip()
        link = urljoin(base, href).split("#", 1)[0].rstrip("/")
        low = link.lower()
        if not low.startswith(base):
            continue
        if any(d in low for d in _ARL_RESOURCES_DENY):
            continue
        path = urlparse(low).path.lower()
        if path in ("/resources", "/resources/"):
            continue
        if not (
            path.startswith("/resources/")
            or path.startswith("/baa-forms")
            or "/cras/" in path
            or path.startswith("/htmdec")
            or path.startswith("/r2c2")
        ):
            continue
        if link in seen or link.rstrip("/") == hub.rstrip("/"):
            continue
        tit = re.sub(r"\s+", " ", (a.get_text() or "")).strip()
        if len(tit) < 8:
            continue
        seen.add(link)
        cls = classify_arl_resource(link, tit)
        out.append(
            {
                "titulo": tit[:320],
                "descricao": "",
                "link": link[:800],
                "data_publicacao_raw": "",
                "source_method": f"arl_resources_{mode}",
                "feed_categories": ["resource"],
                "fonte_instituicao_raw": "ARL",
                "tipo_pesquisa": cls.get("tipo_pesquisa"),
                "tipo_recurso": cls.get("tipo_recurso"),
                "tipo_oportunidade": "pesquisa_estrategica",
                "_possivel_edital": cls.get("possivel_edital"),
                "_institucional_latente": cls.get("institucional_latente"),
                "_destino_sugerido": cls.get("destino_sugerido"),
            }
        )
    return out[:max_items]


# Aliases for crawl imports / probes
_dod_afmil_http_get = _dod_http_get
_extract_dod_afmil_news_from_html = extract_dod_afmil_news_from_html
_crawl_dod_afmil_news_listing = crawl_dod_afmil_news_listing
_crawl_afrl_technology_areas = crawl_afrl_technology_areas
_crawl_afnwc_portal_cards = crawl_afnwc_portal
_crawl_arl_resources = crawl_arl_resources
_crawl_arl_media_center_news = crawl_arl_media_center_news
