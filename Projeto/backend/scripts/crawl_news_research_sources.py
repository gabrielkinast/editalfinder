#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import time
import warnings
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DEFAULT = ROOT / "config" / "news_research_sources.json"
OUT_DEFAULT = ROOT / "audit_reports_news_research"

HEADERS = {
    "User-Agent": "EditalFinderBot/1.0 (+public scientific/news monitoring)",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_date(v: Any) -> Optional[datetime]:
    if not v:
        return None
    s = str(v).strip()
    if not s:
        return None
    patterns = [
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M %z",
        "%d %B %Y",
        "%d %b %Y",
        "%B %d, %Y",
        "%b %d, %Y",
    ]
    for p in patterns:
        try:
            dt = datetime.strptime(s[: max(len(p), 10)], p)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue
    try:
        dt2 = parsedate_to_datetime(s)
        if dt2:
            if dt2.tzinfo is None:
                dt2 = dt2.replace(tzinfo=timezone.utc)
            return dt2.astimezone(timezone.utc)
    except Exception:
        pass
    # IAEA / alguns feeds: ano de 2 dígitos "26-04-30  16:32"
    m_iaea = re.match(r"^\s*(\d{2})-(\d{2})-(\d{2})\s+", s)
    if m_iaea:
        try:
            yy, mo, d = int(m_iaea.group(1)), int(m_iaea.group(2)), int(m_iaea.group(3))
            year = 2000 + yy if yy < 70 else 1900 + yy
            return datetime(year, mo, d, tzinfo=timezone.utc)
        except Exception:
            pass
    m = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", s)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
        except Exception:
            return None
    m2 = re.search(r"\b(20\d{2})/(\d{2})/(\d{2})\b", s)
    if m2:
        try:
            return datetime(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)), tzinfo=timezone.utc)
        except Exception:
            return None
    m_br = re.search(r"\b(\d{2})/(\d{2})/(20\d{2})\b", s)
    if m_br:
        try:
            return datetime(int(m_br.group(3)), int(m_br.group(2)), int(m_br.group(1)), tzinfo=timezone.utc)
        except Exception:
            return None
    if "T" in s and re.match(r"20\d{2}-\d{2}-\d{2}T", s[:19]):
        try:
            dt3 = datetime.fromisoformat(s.replace("Z", "+00:00")[:32])
            if dt3.tzinfo is None:
                dt3 = dt3.replace(tzinfo=timezone.utc)
            return dt3.astimezone(timezone.utc)
        except Exception:
            pass
    return None


def _iso_date(dt: Optional[datetime]) -> Optional[str]:
    return dt.date().isoformat() if dt else None


def _strip_html(text: Any, max_len: int = 2400) -> str:
    """Remove tags e colapsa espaços; não inventa conteúdo."""
    if text is None:
        return ""
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", str(text))
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if max_len and len(t) > max_len:
        t = t[: max_len - 1].rsplit(" ", 1)[0] + "…"
    return t


def _local_tag(tag: str) -> str:
    if not tag:
        return ""
    return tag.split("}")[-1].lower()


def _child_text_join(it: ET.Element, *local_names: str) -> str:
    for child in list(it):
        if _local_tag(child.tag) in local_names:
            return "".join(child.itertext() or "").strip()
    return ""


def _parse_date_from_eureka_listing_title(titulo: str) -> Optional[datetime]:
    """Prefixo típico em listings EurekAlert: '4-May-2026 Título...' (inglês)."""
    if not titulo:
        return None
    m = re.match(r"^\s*(\d{1,2})-([A-Za-z]{3})-(\d{4})\b", titulo.strip())
    if not m:
        return None
    mon = m.group(2).lower()[:3]
    mmap = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }
    mo = mmap.get(mon)
    if not mo:
        return None
    try:
        return datetime(int(m.group(3)), mo, int(m.group(1)), tzinfo=timezone.utc)
    except Exception:
        return None


def _parse_date_from_url(url: str) -> Optional[datetime]:
    if not url:
        return None
    for pat in (
        r"(20\d{2})-(\d{2})-(\d{2})",
        r"(20\d{2})/(\d{2})/(\d{2})",
        r"/(20\d{2})/(\d{1,2})/(\d{1,2})/",
        r"/(20\d{2})/(\d{1,2})/(\d{1,2})[^/0-9]",
    ):
        m = re.search(pat, url)
        if not m:
            continue
        try:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if 1 <= mo <= 12 and 1 <= d <= 31:
                return datetime(y, mo, d, tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def _meta_and_jsonld_dates(html: str) -> List[str]:
    """Extrai strings de data candidatas de meta tags e JSON-LD (sem inventar)."""
    out: List[str] = []
    if not html or len(html) > 900_000:
        return out
    soup = BeautifulSoup(html, "html.parser")
    for attrs in (
        {"property": "article:published_time"},
        {"name": "article:published_time"},
        {"property": "og:updated_time"},
        {"name": "pubdate"},
        {"name": "date"},
    ):
        n = soup.find("meta", attrs=attrs)
        if n and n.get("content"):
            out.append(str(n.get("content")).strip())
    for script in soup.select('script[type="application/ld+json"]'):
        raw = script.string or script.get_text() or ""
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        stack = [data] if isinstance(data, dict) else list(data) if isinstance(data, list) else []
        while stack:
            cur = stack.pop()
            if isinstance(cur, dict):
                for k in ("datePublished", "dateModified", "uploadDate"):
                    v = cur.get(k)
                    if isinstance(v, str) and v.strip():
                        out.append(v.strip())
                for v in cur.values():
                    if isinstance(v, (dict, list)):
                        stack.append(v)
            elif isinstance(cur, list):
                stack.extend(cur)
    return out


def _og_image_from_html(html: str, page_url: str) -> Optional[str]:
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    for attrs in ({"property": "og:image"}, {"name": "twitter:image"}):
        n = soup.find("meta", attrs=attrs)
        if n and n.get("content"):
            u = urljoin(page_url, str(n.get("content")).strip())
            if u.startswith("http"):
                return u[:800]
    return None


def _defesanet_section_from_url(link: str) -> str:
    path = urlparse(link or "").path.strip("/")
    if not path:
        return "geral"
    return (path.split("/")[0] or "geral").lower()[:80]


def _defesanet_infer_eixo(section: str, feed_categories: List[str], blob: str) -> List[str]:
    """Eixos estratégicos para notícias DefesaNet (sem inventar domínios fora do editorial)."""
    eixo: List[str] = ["defesa"]
    sec = (section or "").lower()
    b = (blob or "").lower()
    cats = " ".join(feed_categories or []).lower()
    if sec in ("vant", "aeroespacial", "aeroco", "avibras-aeroco") or "aero" in b or "drone" in b:
        if "aeroespacial" not in eixo:
            eixo.append("aeroespacial")
    if sec == "naval" or "marinha" in b or "naval" in cats:
        eixo.append("seguranca")
    if any(k in b or k in cats for k in ("indústria", "industria", "avibras", "base industrial", "simde")):
        if "industria_estrategica" not in eixo:
            eixo.append("industria_estrategica")
    if any(
        k in b or k in cats
        for k in (
            "geopol",
            "ucrânia",
            "ucrania",
            "otan",
            "nato",
            "china",
            "rússia",
            "russia",
            "estratég",
            "estrateg",
        )
    ):
        if "geopolitica_tecnologica" not in eixo:
            eixo.append("geopolitica_tecnologica")
    if any(k in b or k in cats for k in ("cyber", "antidrone", "guerra eletr", "sensor", "doutrina")):
        if "tecnologia_militar" not in eixo:
            eixo.append("tecnologia_militar")
    if "seguranca" not in eixo and any(k in b for k in ("segurança", "seguranca", "antiterror")):
        eixo.append("seguranca")
    seen: set = set()
    out: List[str] = []
    for x in eixo:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _brisa_infer_eixo(feed_categories: List[str], blob: str) -> List[str]:
    """Eixos BRISA News: tecnologia/inovação base; defesa/aero só com evidência no texto."""
    b = (blob or "").lower()
    cats = " ".join(feed_categories or []).lower()
    eixo: List[str] = ["tecnologia", "inovacao"]
    if any(k in b or k in cats for k in ("engenharia", "residência", "residencia", "tic", "pesquisa aplicada")):
        if "engenharia" not in eixo:
            eixo.append("engenharia")
    if any(k in b or k in cats for k in ("indústria", "industria", "empresa", "softex", "soft landing", "exportação", "exportacao")):
        if "industria" not in eixo:
            eixo.append("industria")
    if any(k in b or k in cats for k in ("software", "tic", "programa", "digital", "tecnologia")):
        if "software" not in eixo:
            eixo.append("software")
    if any(
        k in b or k in cats
        for k in (
            "defesa",
            "aeroespacial",
            "militar",
            "exército",
            "exercito",
            "fab",
            "caça",
            "caca",
            "geopolítica",
            "geopolitica",
        )
    ):
        if "defesa_aeroespacial" not in eixo:
            eixo.append("defesa_aeroespacial")
    seen: set = set()
    out: List[str] = []
    for x in eixo:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


_BRISA_NON_ARTICLE_PATHS = (
    "/sobre-nos",
    "/casos-de-sucesso",
    "/fale-conosco",
    "/contato",
    "/servicos",
    "/solucoes",
)


def _brisa_artigos_infer_eixo(feed_categories: List[str], blob: str) -> List[str]:
    """Eixos BRISA Artigos: tecnologia/engenharia/software; IA só com evidência no texto."""
    eixo = _brisa_infer_eixo(feed_categories, blob)
    b = (blob or "").lower()
    cats = " ".join(feed_categories or []).lower()
    if any(
        k in b or k in cats
        for k in (
            "pesquisa aplicada",
            "pesquisa e desenvolvimento",
            "p&d",
            "laboratório",
            "laboratorio",
            "case study",
            "estudo de caso",
        )
    ):
        if "pesquisa_aplicada" not in eixo:
            eixo.append("pesquisa_aplicada")
    if any(
        k in b or k in cats
        for k in (
            "inteligência artificial",
            "inteligencia artificial",
            " machine learning",
            " ia ",
            "computação",
            "computacao",
            "dados",
            "analytics",
        )
    ):
        if "computacao_ia" not in eixo:
            eixo.append("computacao_ia")
    seen: set = set()
    out: List[str] = []
    for x in eixo:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _brisa_artigos_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower()
    if not lk.startswith("http") or "brisabr.com.br" not in lk:
        return False, "dominio_invalido"
    if "/news/" in lk:
        return False, "url_secao_news"
    path = urlparse(lk).path.rstrip("/").lower() or "/"
    if path in ("/artigos", "/news"):
        return False, "url_pagina_indice"
    if any(p in lk for p in _BRISA_NON_ARTICLE_PATHS):
        return False, "url_institucional"
    if any(x in lk for x in ("/tag/", "/author/", "/page/", "/wp-json", "/feed", "/category/")):
        return False, "url_nao_artigo"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=400)
    if len(body) < 20 and len(tit) < 25:
        return False, "sem_conteudo"
    return True, ""


def _brisa_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower()
    if not lk.startswith("http") or "brisabr.com.br" not in lk:
        return False, "dominio_invalido"
    if "/news/" not in lk:
        return False, "url_fora_secao_news"
    if "/artigos/" in lk or any(x in lk for x in ("/tag/", "/author/", "/page/", "/wp-json", "/feed", "/category/")):
        return False, "url_nao_artigo"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=400)
    if len(body) < 20 and len(tit) < 25:
        return False, "sem_conteudo_jornalistico"
    return True, ""


def _softex_infer_eixo(feed_categories: List[str], blob: str) -> List[str]:
    """Eixos SOFTEX: TI/exportação/indústria; IA/cyber só com evidência no texto."""
    eixo = _brisa_infer_eixo(feed_categories, blob)
    b = (blob or "").lower()
    cats = " ".join(feed_categories or []).lower()
    if any(
        k in b or k in cats
        for k in (
            "exportação",
            "exportacao",
            "softex",
            "startup",
            "brasil it",
            "software",
            "tic",
            "tecnologia",
        )
    ):
        if "industria" not in eixo:
            eixo.append("industria")
    if any(k in b or k in cats for k in ("inteligência artificial", "inteligencia artificial", " ia ", "machine learning")):
        if "computacao_ia" not in eixo:
            eixo.append("computacao_ia")
    if any(k in b or k in cats for k in ("energia", "energy summit", "sustentab")):
        if "engenharia" not in eixo:
            eixo.append("engenharia")
    seen: set = set()
    out: List[str] = []
    for x in eixo:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _softex_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower()
    if not lk.startswith("http") or "softex.br" not in lk:
        return False, "dominio_invalido"
    if any(
        x in lk
        for x in (
            "/tag/",
            "/author/",
            "/page/",
            "/wp-json",
            "/feed",
            "/category/",
            "/comments/",
            "/wp-content/",
        )
    ):
        return False, "url_nao_noticia"
    path = urlparse(lk).path.rstrip("/").lower()
    if path in ("", "/noticias", "/noticia"):
        return False, "url_pagina_indice"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=400)
    if len(body) < 20 and len(tit) < 25:
        return False, "sem_conteudo_jornalistico"
    return True, ""


def _defesanet_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip()
    if not lk.startswith("http") or "defesanet.com.br" not in lk.lower():
        return False, "dominio_invalido"
    if any(x in lk.lower() for x in ("/tag/", "/author/", "/page/", "/wp-json", "/feed", "/category/")):
        return False, "url_nao_artigo"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=400)
    if len(body) < 20 and len(tit) < 25:
        return False, "sem_conteudo_jornalistico"
    return True, ""


_EB_NOTICIA_PATH = "/web/noticias/w/"


def _normalize_eb_noticia_link(href: str, seed_url: str) -> Optional[str]:
    if not href:
        return None
    link = urljoin(seed_url, href).split("#", 1)[0]
    parsed = urlparse(link)
    host = (parsed.hostname or "").lower()
    if "eb.mil.br" not in host:
        return None
    path = (parsed.path or "").lower()
    if _EB_NOTICIA_PATH not in path:
        return None
    slug = path.split(_EB_NOTICIA_PATH, 1)[-1].strip("/")
    if not slug or slug in ("", "guest"):
        return None
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def _extract_eb_noticias_listing(seed_url: str, body: str, max_items: int) -> List[Dict[str, Any]]:
    """Listagem Liferay: links /web/noticias/w/{slug} em guest e noticiário."""
    soup = BeautifulSoup(body, "html.parser")
    out: List[Dict[str, Any]] = []
    seen: set = set()
    cap = max(max_items * 3, 24)
    skip_titles = {"", "veja mais", "compartilhar", "share"}
    for a in soup.find_all("a", href=True):
        link = _normalize_eb_noticia_link(a["href"], seed_url)
        if not link or link in seen:
            continue
        title = re.sub(r"\s+", " ", a.get_text() or "").strip()
        if len(title) < 12 or title.lower() in skip_titles:
            continue
        seen.add(link)
        out.append(
            {
                "titulo": title[:320],
                "descricao": "",
                "link": link[:800],
                "data_publicacao_raw": "",
                "source_method": "eb_liferay_listing",
                "feed_categories": [],
            }
        )
        if len(out) >= cap:
            break
    return out


def _exercito_brasileiro_infer_eixo(feed_categories: List[str], blob: str) -> List[str]:
    """Eixos para notícias oficiais eb.mil.br."""
    b = (blob or "").lower()
    cats = " ".join(feed_categories or []).lower()
    eixo: List[str] = ["defesa"]
    if any(k in b or k in cats for k in ("engenharia", "ctex", "blindad", "veículo de combate", "veiculo de combate", "tecnológ", "tecnolog")):
        if "engenharia" not in eixo:
            eixo.append("engenharia")
    if any(
        k in b or k in cats
        for k in (
            "infantaria",
            "cavalaria",
            "artilharia",
            "força terrestre",
            "forca terrestre",
            "operacional",
            "militar",
            "tropa",
            "batalhão",
            "batalhao",
        )
    ):
        if "tecnologia_militar" not in eixo:
            eixo.append("tecnologia_militar")
    if any(k in b or k in cats for k in ("colégio militar", "colegio militar", "academia militar", "formação", "formacao", "febrace", "educação", "educacao")):
        if "formacao_militar_cientifica" not in eixo:
            eixo.append("formacao_militar_cientifica")
    if any(k in b or k in cats for k in ("aeroespacial", "aviação", "aviacao", "helicóptero", "helicoptero", "fab ")):
        if "aeroespacial" not in eixo:
            eixo.append("aeroespacial")
    if any(k in b or k in cats for k in ("cyber", "cibernét", "cibernet", "guerra eletr", "defesa química", "defesa quimica", "cbrn", "nuclear")):
        if "computacao_cyber" not in eixo:
            eixo.append("computacao_cyber")
    if any(k in b or k in cats for k in ("segurança", "seguranca", "fronteira", "crime", "operação", "operacao")):
        if "seguranca" not in eixo:
            eixo.append("seguranca")
    seen: set = set()
    out: List[str] = []
    for x in eixo:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _exercito_brasileiro_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower()
    if not lk.startswith("http") or "eb.mil.br" not in lk:
        return False, "dominio_invalido"
    if _EB_NOTICIA_PATH not in lk:
        return False, "url_fora_noticiario"
    if any(x in lk for x in ("/tag/", "/author/", "/page/", "/wp-json", "/feed", "/category/")):
        return False, "url_nao_noticia"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=400)
    if len(body) < 15 and len(tit) < 25:
        return False, "sem_conteudo"
    return True, ""


_ITA_PROJETOS_HUB = "/projetos"
_ITA_PROJETOS_SKIP = (
    "status-de-um-projeto",
    "departamento-do-projeto",
    "tipo-de-projeto",
    "area-de-conhecimento",
)


def _normalize_ita_projetos_link(href: str, seed_url: str) -> Optional[str]:
    if not href:
        return None
    link = urljoin(seed_url, href).split("#", 1)[0].rstrip("/")
    parsed = urlparse(link)
    host = (parsed.hostname or "").lower()
    if "ita.br" not in host:
        return None
    path = (parsed.path or "").lower().rstrip("/")
    if not path.startswith("/projetos/") or path == _ITA_PROJETOS_HUB:
        return None
    slug = path.split("/projetos/", 1)[-1].strip("/")
    if not slug or "/" in slug or len(slug) < 4:
        return None
    if any(seg in path for seg in _ITA_PROJETOS_SKIP):
        return None
    return link


def _extract_ita_projetos_listing(seed_url: str, body: str, max_items: int) -> List[Dict[str, Any]]:
    """Hub Drupal /projetos: cards com links /projetos/{slug} (sem feed RSS útil)."""
    soup = BeautifulSoup(body, "html.parser")
    out: List[Dict[str, Any]] = []
    seen: set = set()
    skip_titles = {"", "projetos", "veja mais", "laboratórios", "laboratorios", "concluído", "concluido"}
    cap = max(max_items * 2, 12)
    for a in soup.find_all("a", href=True):
        link = _normalize_ita_projetos_link(a["href"], seed_url)
        if not link or link in seen:
            continue
        title = re.sub(r"\s+", " ", a.get_text() or "").strip()
        if len(title) < 12 or title.lower() in skip_titles:
            continue
        seen.add(link)
        out.append(
            {
                "titulo": title[:320],
                "descricao": "",
                "link": link[:800],
                "data_publicacao_raw": "",
                "source_method": "ita_projetos_listing",
                "feed_categories": ["projeto"],
                "ita_page_kind": "projeto_pesquisa",
            }
        )
        if len(out) >= cap:
            break
    return out


def _extract_ita_institutional_portal(seed_url: str, body: str) -> List[Dict[str, Any]]:
    """Página institucional estática (laboratório): um registro portal/pesquisa, sem série temporal."""
    soup = BeautifulSoup(body, "html.parser")
    h1 = soup.find("h1")
    title = re.sub(r"\s+", " ", (h1.get_text() if h1 else (soup.title.string if soup.title else ""))).strip()
    desc = _snippet_from_article_html(body, max_len=900)
    canonical = seed_url.split("#", 1)[0].rstrip("/")
    return [
        {
            "titulo": (title or "ITA")[:320],
            "descricao": desc,
            "link": canonical[:800],
            "data_publicacao_raw": "",
            "source_method": "ita_institutional_portal",
            "feed_categories": ["laboratorio", "portal_institucional"],
            "ita_page_kind": "portal_institucional",
        }
    ]


def _ita_infer_eixo(feed_categories: List[str], blob: str, src_id: str = "") -> List[str]:
    b = (blob or "").lower()
    cats = " ".join(feed_categories or []).lower()
    eixo: List[str] = ["engenharia", "ciencia_tecnologia"]
    if src_id == "ita_lab_guerra_eletronica" or any(
        k in b or k in cats for k in ("guerra eletr", "guerra eletrônica", "guerra eletronica", "lab-ge", "defesa")
    ):
        if "defesa" not in eixo:
            eixo.append("defesa")
        if "tecnologia_militar" not in eixo:
            eixo.append("tecnologia_militar")
        if "computacao_cyber" not in eixo:
            eixo.append("computacao_cyber")
    if any(k in b or k in cats for k in ("aeronáut", "aeronaut", "aviação", "aviacao", "aeroespacial", "cpemaf")):
        if "aeroespacial" not in eixo:
            eixo.append("aeroespacial")
    if any(k in b or k in cats for k in ("eletrônic", "eletronic", "sistemas embarcados", "rf ", "radar", "antena")):
        if "computacao_cyber" not in eixo:
            eixo.append("computacao_cyber")
    if any(k in b or k in cats for k in ("inteligência artificial", "inteligencia artificial", " ia ", "machine learning")):
        if "computacao_ia" not in eixo:
            eixo.append("computacao_ia")
    if any(k in b or k in cats for k in ("mobilidade", "energia", "sustentab", "poluente", "queimador")):
        if "energia" not in eixo:
            eixo.append("energia")
    seen: set = set()
    out: List[str] = []
    for x in eixo:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _ita_projetos_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower()
    if not lk.startswith("http") or "ita.br" not in lk:
        return False, "dominio_invalido"
    if not _normalize_ita_projetos_link(lk, lk):
        return False, "url_fora_catalogo_projetos"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    body = _strip_html(r.get("descricao") or "", max_len=400)
    if len(body) < 25 and len(tit) < 20:
        return False, "sem_resumo_minimo"
    return True, ""


_MCTI_NOTICIAS_BASE = "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/noticias"
_MCTI_ARTICLE_RE = re.compile(
    r"/mcti/pt-br/acompanhe-o-mcti/noticias/(\d{4})/(\d{2})/[^/?#]+",
    re.I,
)

_MCTI_POSITIVE_SIGNALS: Tuple[Tuple[str, str], ...] = (
    ("pesquisa", "pesquisa"),
    ("pesquisador", "pesquisa"),
    ("ciência", "ciencia"),
    ("ciencia", "ciencia"),
    ("científic", "ciencia"),
    ("cientific", "ciencia"),
    ("tecnologia", "tecnologia"),
    ("inovação", "inovacao"),
    ("inovacao", "inovacao"),
    ("inteligência artificial", "ia"),
    ("inteligencia artificial", "ia"),
    (" ia ", "ia"),
    ("semicondutor", "semicondutores"),
    ("chips", "semicondutores"),
    ("transformação digital", "transformacao_digital"),
    ("transformacao digital", "transformacao_digital"),
    ("conectividade", "transformacao_digital"),
    ("5g", "transformacao_digital"),
    ("6g", "transformacao_digital"),
    ("espaço", "espaco"),
    ("espaco", "espaco"),
    ("satélite", "espaco"),
    ("satelite", "espaco"),
    ("clima", "clima_cientifico"),
    ("energia", "energia"),
    ("laboratório", "pesquisa"),
    ("laboratorio", "pesquisa"),
    ("instituto", "pesquisa"),
    ("fomento", "fomento"),
    ("finep", "fomento"),
    ("cnpq", "fomento"),
    ("capes", "fomento"),
    ("fndct", "fomento"),
    ("chamada", "fomento"),
    ("edital", "fomento"),
    ("bolsa", "fomento"),
    ("programa científico", "pesquisa"),
    ("programa cientifico", "pesquisa"),
    ("projeto de pesquisa", "pesquisa"),
    ("biotecnologia", "biotecnologia"),
    ("nanotecnologia", "materiais_avancados"),
    ("materiais avançados", "materiais_avancados"),
    ("materiais avancados", "materiais_avancados"),
    ("computação", "computacao"),
    ("computacao", "computacao"),
    ("cibersegurança", "cyber"),
    ("ciberseguranca", "cyber"),
    ("nuclear", "nuclear"),
    ("aeroespacial", "aeroespacial"),
    ("síncrotron", "pesquisa"),
    ("sincrotron", "pesquisa"),
    ("sirius", "pesquisa"),
    ("defesa", "defesa"),
)

_MCTI_NEGATIVE_SIGNALS: Tuple[str, ...] = (
    "agenda",
    "reunião",
    "reuniao",
    "visita",
    "cerimônia",
    "cerimonia",
    "solenidade",
    "posse",
    "nomeação",
    "nomeacao",
    "homenagem",
    "participação em evento",
    "participacao em evento",
    "ministro participa",
    "ministra participa",
    "comitiva",
    "audiência",
    "audiencia",
    "encontro institucional",
    "assinatura de acordo",
    "campanha institucional",
    "balanço institucional",
    "balanco institucional",
    "nota oficial",
    "transparência",
    "transparencia",
    "governança interna",
    "governanca interna",
    "ouvidoria",
    "corregedoria",
    "capacitação interna",
    "capacitacao interna",
    "comunicação administrativa",
    "comunicacao administrativa",
    "conferência nacional",
    "conferencia nacional",
    "semana nacional",
)

_MCTI_EDITAL_MARKERS: Tuple[str, ...] = (
    "edital",
    "chamada pública",
    "chamada publica",
    "fomento",
    "finep",
    "cnpq",
    "fndct",
    "bolsa",
    "linha de fomento",
    "recursos para pesquisa",
)


def _normalize_mcti_noticia_link(href: str, seed_url: str = "") -> Optional[str]:
    if not href:
        return None
    link = urljoin(seed_url or _MCTI_NOTICIAS_BASE, href).split("#", 1)[0].rstrip("/")
    low = link.lower()
    if "gov.br/mcti" not in low:
        return None
    if not _MCTI_ARTICLE_RE.search(low):
        return None
    slug = low.split("/noticias/", 1)[-1]
    if re.fullmatch(r"\d{4}", slug) or re.fullmatch(r"\d{4}/\d{2}", slug):
        return None
    if any(x in slug for x in ("@@", "login", "search", "rss", "atom")):
        return None
    return link


def _mcti_date_from_url(link: str) -> Optional[datetime]:
    m = _MCTI_ARTICLE_RE.search(link or "")
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), 1, tzinfo=timezone.utc)
    except Exception:
        return None


def _extract_mcti_noticias_listing(seed_url: str, body: str, max_items: int) -> List[Dict[str, Any]]:
    """Listagem gov.br/Plone — URLs /noticias/YYYY/MM/slug."""
    soup = BeautifulSoup(body, "html.parser")
    out: List[Dict[str, Any]] = []
    seen: set = set()
    cap = max(max_items * 25, max_items)
    for a in soup.find_all("a", href=True):
        link = _normalize_mcti_noticia_link(a["href"], seed_url)
        if not link or link in seen:
            continue
        title = re.sub(r"\s+", " ", a.get_text() or "").strip()
        if len(title) < 12:
            continue
        seen.add(link)
        dt = _mcti_date_from_url(link)
        pub = ""
        if dt:
            pub = dt.strftime("%Y-%m-%d")
        out.append(
            {
                "titulo": title[:320],
                "descricao": "",
                "link": link[:800],
                "data_publicacao_raw": pub,
                "source_method": "mcti_govbr_listing",
                "feed_categories": [],
            }
        )
        if len(out) >= cap:
            break
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def _sort_key(r: Dict[str, Any]) -> datetime:
        return (
            _parse_date(r.get("data_publicacao_raw"))
            or _mcti_date_from_url(str(r.get("link") or ""))
            or epoch
        )

    out.sort(key=_sort_key, reverse=True)
    return out[:cap]


def _mcti_evaluate_relevance(r: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    keep | review | discard + metadados de curadoria.
    """
    tit = str(r.get("titulo") or "")
    desc = str(r.get("descricao") or "")
    link = str(r.get("link") or "")
    blob = f"{tit} {desc} {link}".lower()

    motivos_pos: List[str] = []
    eixos: List[str] = []
    seen_e: set = set()
    for needle, eixo in _MCTI_POSITIVE_SIGNALS:
        if needle in blob:
            motivos_pos.append(needle.strip())
            if eixo not in seen_e:
                seen_e.add(eixo)
                eixos.append(eixo)

    motivos_neg = [n for n in _MCTI_NEGATIVE_SIGNALS if n in blob]
    possivel_edital = any(m in blob for m in _MCTI_EDITAL_MARKERS)

    n_pos = len(set(motivos_pos))
    n_neg = len(set(motivos_neg))

    meta: Dict[str, Any] = {
        "motivos_relevancia": list(dict.fromkeys(motivos_pos))[:20],
        "motivos_descarte": list(dict.fromkeys(motivos_neg))[:15],
        "eixos_detectados": eixos[:12],
        "possivel_edital": bool(possivel_edital),
    }

    if n_pos == 0 and n_neg > 0:
        meta["relevancia_mcti"] = "baixa"
        return "discard", {**meta, "motivo": "apenas_sinais_administrativos"}
    if n_pos == 0:
        meta["relevancia_mcti"] = "baixa"
        return "discard", {**meta, "motivo": "sem_sinal_tecnico"}

    if n_neg > 0 and n_pos < 2:
        meta["relevancia_mcti"] = "media"
        return "review", {**meta, "motivo": "sinais_administrativos_com_tecnico_fraco"}

    if n_neg >= 2 and n_pos < 3:
        meta["relevancia_mcti"] = "media"
        return "review", {**meta, "motivo": "muitos_sinais_administrativos"}

    if n_pos >= 3:
        meta["relevancia_mcti"] = "alta"
    else:
        meta["relevancia_mcti"] = "media"
    return "keep", meta


def _mcti_infer_eixo(feed_categories: List[str], blob: str, eixos_detectados: List[str]) -> List[str]:
    eixo = list(eixos_detectados or [])
    b = (blob or "").lower()
    for e in eixo:
        if e not in eixo:
            pass
    mapping = {
        "ciencia": "ciencia",
        "tecnologia": "tecnologia",
        "inovacao": "inovacao",
        "ia": "ia",
        "transformacao_digital": "transformacao_digital",
        "semicondutores": "semicondutores",
        "espaco": "espaco",
        "clima_cientifico": "clima_cientifico",
        "energia": "energia",
        "pesquisa": "pesquisa",
        "fomento": "fomento",
        "computacao": "computacao",
        "cyber": "cyber",
        "materiais_avancados": "materiais_avancados",
        "biotecnologia": "biotecnologia",
        "nuclear": "nuclear",
        "aeroespacial": "aeroespacial",
        "defesa": "defesa",
    }
    out: List[str] = []
    seen: set = set()
    for x in eixo:
        if x in mapping and mapping[x] not in seen:
            seen.add(mapping[x])
            out.append(mapping[x])
    if not out:
        if any(k in b for k in ("pesquisa", "ciência", "ciencia", "científ")):
            out.append("ciencia")
        if any(k in b for k in ("tecnologia", "inovação", "inovacao")):
            out.append("tecnologia")
    if not out:
        out = ["ciencia", "tecnologia"]
    return out


def _mcti_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip()
    if not _normalize_mcti_noticia_link(lk, lk):
        return False, "url_fora_noticias_mcti"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _mcti_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 25 and len(tit) < 40:
        return False, "sem_resumo_minimo"
    return True, ""


# --- War.gov / U.S. Department of Defense News (RSS ArticleCS; hub HTML 403 em alguns clientes) ---
_WAR_GOV_RSS_NEWS_STORIES = (
    "https://www.defense.gov/DesktopModules/ArticleCS/RSS.ashx?ContentType=1&Site=945&max=100"
)
_WAR_GOV_NEWS_STORY_PATH = "/news/news-stories/article/"
_WAR_GOV_FEATURES_PATH = "/news/features/"
_WAR_GOV_POSITIVE_SIGNALS: Tuple[Tuple[str, str], ...] = (
    ("defense technology", "defesa"),
    ("military technology", "defesa"),
    ("artificial intelligence", "ia"),
    (" ai ", "ia"),
    ("machine learning", "ia"),
    ("cybersecurity", "cyber"),
    ("cyber ", "cyber"),
    ("space ", "espaco"),
    ("satellite", "espaco"),
    ("missile defense", "defesa"),
    ("missile", "defesa"),
    ("hypersonic", "hipersonicos"),
    ("drone", "autonomia"),
    ("unmanned", "autonomia"),
    ("autonomous", "autonomia"),
    ("sensor", "sensores"),
    ("radar", "sensores"),
    ("electronic warfare", "guerra_eletronica"),
    ("shipbuilding", "engenharia_avancada"),
    ("aircraft", "aeroespacial"),
    ("aerospace", "aeroespacial"),
    ("logistics", "engenharia_avancada"),
    ("industrial base", "industria_estrategica"),
    ("research", "pesquisa"),
    ("innovation", "inovacao"),
    ("science", "ciencia"),
    ("engineering", "engenharia_avancada"),
    ("stem", "ciencia"),
    ("gps", "espaco"),
    ("directed-energy", "defesa"),
    ("counter-drone", "defesa"),
    ("c-uas", "defesa"),
    ("indo-pacific", "geopolitica_tecnologica"),
    ("nato", "geopolitica_tecnologica"),
    ("deterrence", "geopolitica_tecnologica"),
    ("nuclear", "nuclear"),
)
_WAR_GOV_NEGATIVE_SIGNALS: Tuple[str, ...] = (
    "ceremony",
    "ceremonial",
    "speech",
    "remarks by",
    "transcript",
    "secretary travels",
    "travels to ",
    "meeting with",
    "visit to ",
    "honors ",
    "honour ",
    "award ceremony",
    "memorial",
    "observance",
    "live event",
    "media invitation",
    "media advisory",
    "press briefing",
    "routine personnel",
    "personnel update",
    "change of command",
    "retirement ceremony",
    "memorial day",
    "veterans day",
    "wreath-laying",
    "photo opportunity",
    "statement attributable",
    "readout of",
    "administrative announcement",
    "military commission",
    "pretrial hearing",
    "biography",
    "biographies",
)
_WAR_GOV_PROCUREMENT_MARKERS: Tuple[str, ...] = (
    "solicitation",
    "contract award",
    "procurement",
    "request for proposals",
    "request for information",
    "rfp ",
    "rfi:",
    "baa ",
)


def _war_gov_section_from_url(link: str) -> str:
    lk = (link or "").lower()
    if _WAR_GOV_NEWS_STORY_PATH in lk:
        return "news_stories"
    if _WAR_GOV_FEATURES_PATH in lk and "/article/" in lk:
        return "features"
    if "/news/advisories/" in lk or "/news/releases/" in lk:
        return "press_products"
    if "/news/speeches/" in lk:
        return "speeches"
    if "/about/biographies/" in lk:
        return "biographies"
    if "media.defense.gov" in lk:
        return "publications"
    if "/live-events" in lk or "live-event" in lk:
        return "live_events"
    return "other"


def _war_gov_url_allowed(link: str) -> Tuple[bool, str]:
    lk = (link or "").strip()
    low = lk.lower()
    if not lk.startswith("http"):
        return False, "url_invalida"
    if "war.gov" not in low and "defense.gov" not in low:
        return False, "dominio_fora"
    if "media.defense.gov" in low:
        return False, "publicacao_pdf_media"
    sec = _war_gov_section_from_url(lk)
    if sec == "news_stories":
        return True, sec
    if sec == "features":
        return True, sec
    if sec in ("press_products", "speeches", "biographies", "publications", "live_events", "other"):
        return False, f"secao_{sec}"
    return False, "path_nao_noticia"


def _war_gov_infer_eixo(blob: str, eixos_detectados: List[str]) -> List[str]:
    out: List[str] = list(eixos_detectados or [])
    seen = set(out)
    b = (blob or "").lower()
    for needle, eixo in _WAR_GOV_POSITIVE_SIGNALS:
        if needle in b and eixo not in seen:
            seen.add(eixo)
            out.append(eixo)
    if not out and any(k in b for k in ("department of war", "defense", "military")):
        out.append("defesa")
    return out[:10]


def _war_gov_evaluate_relevance(r: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """keep | review | discard — curadoria técnica/estratégica."""
    tit = str(r.get("titulo") or "")
    desc = str(r.get("descricao") or "")
    link = str(r.get("link") or "")
    sec = str(r.get("war_gov_section") or _war_gov_section_from_url(link))
    blob = f"{tit} {desc} {link} {sec}".lower()

    motivos_pos = []
    seen_p: set = set()
    for needle, _eixo in _WAR_GOV_POSITIVE_SIGNALS:
        if needle in blob and needle not in seen_p:
            seen_p.add(needle)
            motivos_pos.append(needle.strip())

    motivos_neg = [n for n in _WAR_GOV_NEGATIVE_SIGNALS if n in blob]
    possivel_procurement = any(m in blob for m in _WAR_GOV_PROCUREMENT_MARKERS)

    eixos = _war_gov_infer_eixo(blob, [])
    meta: Dict[str, Any] = {
        "motivos_relevancia": list(dict.fromkeys(motivos_pos))[:20],
        "motivos_descarte": list(dict.fromkeys(motivos_neg))[:15],
        "eixos_detectados": eixos,
        "war_gov_section": sec,
        "possivel_procurement": bool(possivel_procurement),
    }

    n_pos = len(set(motivos_pos))
    n_neg = len(set(motivos_neg))

    if sec not in ("news_stories", "features"):
        meta["relevancia_war_gov"] = "baixa"
        return "discard", {**meta, "motivo": "secao_nao_prioritaria"}

    if possivel_procurement and n_pos < 2:
        meta["relevancia_war_gov"] = "media"
        return "review", {**meta, "motivo": "sinal_procurement_sem_tecnico_forte"}

    if n_pos == 0 and n_neg > 0:
        meta["relevancia_war_gov"] = "baixa"
        return "discard", {**meta, "motivo": "apenas_sinais_institucionais"}

    if n_pos == 0:
        meta["relevancia_war_gov"] = "baixa"
        return "discard", {**meta, "motivo": "sem_sinal_tecnico"}

    if n_neg > 0 and n_pos < 2:
        meta["relevancia_war_gov"] = "media"
        return "review", {**meta, "motivo": "institucional_com_tecnico_fraco"}

    if n_neg >= 2 and n_pos < 3:
        meta["relevancia_war_gov"] = "media"
        return "review", {**meta, "motivo": "muitos_sinais_institucionais"}

    if n_pos >= 3:
        meta["relevancia_war_gov"] = "alta"
    else:
        meta["relevancia_war_gov"] = "media"
    return "keep", meta


def _war_gov_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip()
    ok_path, why = _war_gov_url_allowed(lk)
    if not ok_path:
        return False, why
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 20 and len(tit) < 35:
        return False, "sem_resumo_minimo"
    r["war_gov_section"] = why
    return True, ""


# --- NATO News (AEM hub SPA; listagem via sitemap; detalhe .model.json / og:*) ---
_NATO_SITEMAP_URL = "https://www.nato.int/sitemap.xml"
_NATO_NEWS_HUB = "https://www.nato.int/en/news-and-events/articles/news"
_NATO_NEWS_ARTICLE_RE = re.compile(
    r"/en/news-and-events/articles/news/(\d{4})/(\d{2})/(\d{2})/([^/?#]+)",
    re.I,
)
_NATO_POSITIVE_SIGNALS: Tuple[Tuple[str, str], ...] = (
    ("defence", "defesa"),
    ("defense", "defesa"),
    ("deterrence", "geopolitica_tecnologica"),
    ("nato", "geopolitica_tecnologica"),
    ("cyber", "cyber"),
    ("cybersecurity", "cyber"),
    ("space", "espaco"),
    ("satellite", "espaco"),
    ("innovation", "inovacao"),
    ("emerging technolog", "inovacao"),
    ("artificial intelligence", "ia"),
    (" ai ", "ia"),
    ("machine learning", "ia"),
    ("drone", "autonomia"),
    ("unmanned", "autonomia"),
    ("missile defense", "defesa"),
    ("missile", "defesa"),
    ("electronic warfare", "guerra_eletronica"),
    ("interoperability", "industria_estrategica"),
    ("industry", "industria_estrategica"),
    ("defence industry", "industria_estrategica"),
    ("defense industry", "industria_estrategica"),
    ("military technology", "tecnologia_militar"),
    ("resilience", "defesa"),
    ("exercise", "defesa"),
    ("ukraine", "geopolitica_tecnologica"),
    ("quantum", "computacao"),
    ("hypersonic", "hipersonicos"),
    ("air defence", "aeroespacial"),
    ("air defense", "aeroespacial"),
    ("fighter", "aeroespacial"),
    ("aircraft", "aeroespacial"),
    ("maritime", "defesa"),
    ("naval", "defesa"),
    ("procurement", "industria_estrategica"),
    ("armament", "defesa"),
    ("nuclear", "nuclear"),
)
_NATO_NEGATIVE_SIGNALS: Tuple[str, ...] = (
    "ceremony",
    "ceremonial",
    "speech",
    "remarks by",
    "statement by the secretary general",
    "press conference transcript",
    "transcript of",
    "protocol visit",
    "official visit",
    "visit to ",
    "travels to ",
    "meeting with",
    "commemoration",
    "commemorative",
    "wreath-laying",
    "wreath laying",
    "agenda",
    "calendar of",
    "photo opportunity",
    "media advisory",
    "invitation to media",
    "appoints ",
    "appointment of",
    "takes office",
    "handover ceremony",
    "national day",
    "condolences",
    "congratulates",
    "congratulate",
    "deep dive recap",
    "gender perspectives in military education",
    "communications officials",
    "senior communications",
)


def _nato_slug_to_title(slug: str) -> str:
    s = re.sub(r"[-_]+", " ", (slug or "").strip())
    return re.sub(r"\s+", " ", s).title()[:320]


def _nato_date_from_url(link: str) -> Optional[datetime]:
    m = _NATO_NEWS_ARTICLE_RE.search(link or "")
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
    except Exception:
        return None


def _nato_section_from_url(link: str) -> str:
    lk = (link or "").lower()
    if "/articles/news/" in lk:
        return "news"
    if "/articles/nato-stories/" in lk:
        return "nato_stories"
    if "/speeches/" in lk or "/speech/" in lk:
        return "speeches"
    if "/statements/" in lk:
        return "statements"
    if "/publications/" in lk:
        return "publications"
    return "other"


def _nato_url_allowed(link: str) -> Tuple[bool, str]:
    lk = (link or "").strip()
    low = lk.lower()
    if not lk.startswith("http") or "nato.int" not in low:
        return False, "dominio_fora"
    if not _NATO_NEWS_ARTICLE_RE.search(low):
        return False, "path_nao_artigo_news"
    sec = _nato_section_from_url(lk)
    if sec != "news":
        return False, f"secao_{sec}"
    return True, sec


def _nato_model_json_url(public_link: str) -> str:
    m = _NATO_NEWS_ARTICLE_RE.search(public_link or "")
    if not m:
        return ""
    y, mo, d, slug = m.group(1), m.group(2), m.group(3), m.group(4)
    return (
        f"https://www.nato.int/content/nato/en/news-and-events/articles/news/"
        f"{y}/{mo}/{d}/{slug}.model.json"
    )


def _nato_fields_from_model(body: str, page_url: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    try:
        data = json.loads(body)
    except Exception:
        return out
    if isinstance(data.get("title"), str) and data["title"].strip():
        out["titulo"] = re.sub(r"\s+", " ", data["title"]).strip()[:320]
    if isinstance(data.get("description"), str) and data["description"].strip():
        out["descricao"] = _strip_html(data["description"], max_len=3000)
    dl = data.get("dataLayer")
    if isinstance(dl, dict):
        for v in dl.values():
            if not isinstance(v, dict):
                continue
            if not out.get("titulo") and isinstance(v.get("dc:title"), str):
                out["titulo"] = v["dc:title"].strip()[:320]
            mod = v.get("repo:modifyDate")
            if mod and not out.get("data_publicacao_raw"):
                out["data_publicacao_raw"] = str(mod)[:32]
            tags = v.get("xdm:tags")
            if isinstance(tags, list) and tags:
                out["feed_categories"] = [str(t) for t in tags if t][:40]

    def _walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if not out.get("descricao"):
                t = obj.get("text") or obj.get("richText")
                if isinstance(t, str) and len(_strip_html(t, max_len=600)) >= 40:
                    if obj.get("richText") or "<p" in t.lower():
                        out["descricao"] = _strip_html(t, max_len=3000)
            src = obj.get("src")
            if (
                not out.get("imagem_url")
                and isinstance(src, str)
                and ("coreimg" in src or "scene7" in src or "/dam/" in src)
            ):
                out["imagem_url"] = urljoin(page_url, src)[:800]
            for v in obj.values():
                _walk(v)
        elif isinstance(obj, list):
            for x in obj[:80]:
                _walk(x)

    _walk(data.get(":items"))
    return out


def _extract_nato_news_sitemap(max_items: int, min_dt: Optional[datetime]) -> List[Dict[str, Any]]:
    """Artigos /articles/news/YYYY/MM/DD/slug via sitemap oficial (hub HTML é SPA + general_search)."""
    resp = _http_get(_NATO_SITEMAP_URL, timeout=180)
    if not resp:
        return []
    body = resp.text or ""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    mapped: List[Tuple[datetime, Dict[str, Any]]] = []
    seen: set = set()
    cap = max(max_items * 8, max_items)
    for block in re.finditer(r"<url>([\s\S]*?)</url>", body, re.I):
        inner = block.group(1)
        loc_m = re.search(r"<loc>([^<]+)</loc>", inner, re.I)
        if not loc_m:
            continue
        loc = loc_m.group(1).strip().split("#", 1)[0].rstrip("/")
        m = _NATO_NEWS_ARTICLE_RE.search(loc)
        if not m:
            continue
        if loc in seen:
            continue
        seen.add(loc)
        slug = m.group(4)
        dt = _nato_date_from_url(loc)
        lm_m = re.search(r"<lastmod>([^<]+)</lastmod>", inner, re.I)
        lastmod = lm_m.group(1).strip()[:32] if lm_m else ""
        if min_dt and dt and dt < min_dt:
            continue
        pub_raw = _iso_date(dt) or (lastmod[:10] if lastmod else "")
        mapped.append(
            (
                dt or _parse_date(lastmod) or epoch,
                {
                    "titulo": _nato_slug_to_title(slug),
                    "descricao": "",
                    "link": loc[:800],
                    "data_publicacao_raw": pub_raw,
                    "source_method": "nato_sitemap",
                    "feed_categories": ["news"],
                    "nato_section": "news",
                    "fonte_instituicao_raw": "NATO",
                    "autor": "NATO",
                },
            )
        )
    mapped.sort(key=lambda x: x[0], reverse=True)
    out: List[Dict[str, Any]] = []
    for _, row in mapped:
        out.append(row)
        if len(out) >= cap:
            break
    return out


def _nato_infer_eixo(blob: str, eixos_detectados: List[str]) -> List[str]:
    out: List[str] = list(eixos_detectados or [])
    seen = set(out)
    b = (blob or "").lower()
    for needle, eixo in _NATO_POSITIVE_SIGNALS:
        if needle in b and eixo not in seen:
            seen.add(eixo)
            out.append(eixo)
    if not out and any(k in b for k in ("nato", "alliance", "defence", "defense")):
        out.append("defesa")
    return out[:10]


def _nato_evaluate_relevance(r: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """keep | review | discard — curadoria defesa/tecnologia/estratégia."""
    tit = str(r.get("titulo") or "")
    desc = str(r.get("descricao") or "")
    link = str(r.get("link") or "")
    sec = str(r.get("nato_section") or _nato_section_from_url(link))
    blob = f"{tit} {desc} {link} {sec}".lower()

    motivos_pos = []
    seen_p: set = set()
    for needle, _eixo in _NATO_POSITIVE_SIGNALS:
        if needle in blob and needle not in seen_p:
            seen_p.add(needle)
            motivos_pos.append(needle.strip())

    motivos_neg = [n for n in _NATO_NEGATIVE_SIGNALS if n in blob]
    eixos = _nato_infer_eixo(blob, [])
    meta: Dict[str, Any] = {
        "motivos_relevancia": list(dict.fromkeys(motivos_pos))[:20],
        "motivos_descarte": list(dict.fromkeys(motivos_neg))[:15],
        "eixos_detectados": eixos,
        "nato_section": sec,
    }

    n_pos = len(set(motivos_pos))
    n_neg = len(set(motivos_neg))

    if sec != "news":
        meta["relevancia_nato"] = "baixa"
        return "discard", {**meta, "motivo": "secao_nao_news"}

    if n_pos == 0 and n_neg > 0:
        meta["relevancia_nato"] = "baixa"
        return "discard", {**meta, "motivo": "apenas_sinais_institucionais"}

    if n_pos == 0:
        meta["relevancia_nato"] = "baixa"
        return "discard", {**meta, "motivo": "sem_sinal_tecnico"}

    if any(n in blob for n in ("speech", "remarks by", "transcript")) and n_pos < 2:
        meta["relevancia_nato"] = "media"
        return "review", {**meta, "motivo": "possivel_discurso_com_sinal_fraco"}

    if n_neg > 0 and n_pos < 2:
        meta["relevancia_nato"] = "media"
        return "review", {**meta, "motivo": "institucional_com_tecnico_fraco"}

    if n_neg >= 2 and n_pos < 3:
        meta["relevancia_nato"] = "media"
        return "review", {**meta, "motivo": "muitos_sinais_institucionais"}

    if n_pos >= 3:
        meta["relevancia_nato"] = "alta"
    else:
        meta["relevancia_nato"] = "media"
    return "keep", meta


def _nato_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip()
    ok_path, why = _nato_url_allowed(lk)
    if not ok_path:
        return False, why
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _nato_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 20 and len(tit) < 40:
        return False, "sem_resumo_minimo"
    r["nato_section"] = why
    return True, ""


# --- AFRL (Air Force Research Laboratory) — hub HTML 403 com bot padrão; ArticleCS sem RSS útil ---
_AFRL_BASE = "https://www.afrl.af.mil"
_AFRL_NEWS_HUB = f"{_AFRL_BASE}/News/"
_AFRL_MISSION_HUB = f"{_AFRL_BASE}/Mission-Organizations/"
_AFRL_WAYBACK_WEB = "https://web.archive.org/web/2025/"
# Catálogo público de diretorias (fallback quando hub Mission-Organizations inacessível).
_AFRL_MISSION_STATIC: Tuple[Tuple[str, str], ...] = (
    ("RE", "Materials and Manufacturing Directorate"),
    ("RQ", "Aerospace Systems Directorate"),
    ("RY", "Sensors Directorate"),
    ("RW", "Warfare Directorate"),
    ("711HPW", "711th Human Performance Wing"),
    ("AFOSR", "Air Force Office of Scientific Research"),
    ("RG", "AFWERX"),
)
_AFRL_ARTICLE_RE = re.compile(
    r"/News/Article-Display/Article/(\d+)/([^/?#]+)",
    re.I,
)
_AFRL_DATE_RE = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
    r"(\d{1,2}),\s+(20\d{2})\b",
    re.I,
)
_AFRL_MISSION_PATH_DENY = frozenset(
    {
        "news",
        "questions",
        "about-us",
        "site_map",
        "mission-organizations",
        "organizations",
        "win-the-future",
        "",
    }
)
_AFRL_POSITIVE_SIGNALS: Tuple[Tuple[str, str], ...] = (
    ("air force research laboratory", "defesa"),
    ("afrl", "defesa"),
    ("aerospace", "aeroespacial"),
    ("aero", "aeroespacial"),
    ("propulsion", "propulsao"),
    ("rocket engine", "propulsao"),
    ("hypersonic", "hipersonicos"),
    ("material", "materiais_avancados"),
    ("additive manufactur", "materiais_avancados"),
    ("sensor", "sensores"),
    ("radar", "sensores"),
    ("electronic warfare", "guerra_eletronica"),
    ("spectrum warfare", "guerra_eletronica"),
    ("directed energy", "energia_dirigida"),
    ("artificial intelligence", "ia"),
    (" ai ", "ia"),
    ("machine learning", "ia"),
    ("autonomous", "autonomia"),
    ("unmanned", "autonomia"),
    ("drone", "autonomia"),
    ("cyber", "cyber"),
    ("space", "espaco"),
    ("satellite", "espaco"),
    ("artemis", "espaco"),
    ("quantum", "quantum"),
    ("microelectron", "microeletronica"),
    ("biotechnolog", "biotecnologia"),
    ("simulation", "simulacao_modelagem"),
    ("modeling", "simulacao_modelagem"),
    ("engineering", "engenharia_avancada"),
    ("research", "pesquisa"),
    ("innovation", "inovacao"),
    ("directorate", "defesa"),
    ("laboratory", "pesquisa"),
    ("flight test", "aeroespacial"),
    ("human performance", "pesquisa"),
    ("cislunar", "espaco"),
    ("additive manufactur", "materiais_avancados"),
    ("manufacturing", "materiais_avancados"),
    ("munition", "defesa"),
    ("warfare", "defesa"),
    ("transition", "inovacao"),
    ("sbir", "inovacao"),
    ("sttr", "inovacao"),
)
_AFRL_NEGATIVE_SIGNALS: Tuple[str, ...] = (
    "ceremony",
    "ceremonial",
    "ribbon cutting",
    "ribbon-cutting",
    "change of command",
    "welcomes new commander",
    "hosts usecaf",
    "immersion tour",
    "official visit",
    "protocol visit",
    "travels to ",
    "meeting with",
    "honors ",
    "honour ",
    "award winners",
    "fellows, early career",
    "speech",
    "remarks by",
    "press conference transcript",
    "agenda",
    "commemoration",
    "wreath-laying",
    "careers",
    "now hiring",
    "job opening",
    "photo opportunity",
)
_AFRL_OPPORTUNITY_MARKERS: Tuple[str, ...] = (
    "sbir",
    "sttr",
    "solicitation",
    "broad agency",
    "request for proposals",
    "request for information",
    "rfp ",
    "rfi:",
    "funding opportunity",
    "small business",
    "afwerx",
    "spacewerx",
    "proposal",
    "funding",
)
_AFRL_DIRECTORATE_CONFIG: Dict[str, Dict[str, Any]] = {
    "afrl_air_warfare_research": {
        "code": "RA",
        "titulo": "Air Warfare Directorate",
        "highlights_heading": "Air Warfare Directorate Highlights",
        "tipo_pesquisa": "centro_pesquisa",
        "tipo_recurso": "organizacao_pesquisa",
        "descricao_institucional": (
            "The Air Warfare Directorate unifies expertise from AFRL's former Munitions "
            "and Aerospace Systems Directorates to develop advanced air combat technologies."
        ),
        "area_tecnologica": [
            "aeroespacial",
            "defesa",
            "propulsao",
            "autonomia",
            "hipersonicos",
            "sensores",
            "engenharia_avancada",
        ],
        "setor_estrategico": ["defesa", "aeroespacial"],
    },
    "afrl_space_warfare_research": {
        "code": "RJ",
        "titulo": "Space Warfare Directorate",
        "highlights_heading": "Space Warfare Directorate Highlights",
        "tipo_pesquisa": "centro_pesquisa",
        "tipo_recurso": "organizacao_pesquisa",
        "descricao_institucional": (
            "The Space Warfare Directorate develops and transitions space technologies "
            "for national security and warfighter advantage."
        ),
        "area_tecnologica": [
            "espaco",
            "satelites",
            "propulsao",
            "cislunar",
            "defesa",
            "sensores",
            "comunicacoes",
            "aeroespacial",
        ],
        "setor_estrategico": ["defesa", "aeroespacial", "espaco"],
    },
    "afrl_technology_transition": {
        "code": "RR",
        "titulo": "Technology Transition Office",
        "highlights_heading": "Technology Transition Office Highlights",
        "tipo_pesquisa": "portal_institucional",
        "tipo_recurso": "portal_estrategico",
        "descricao_institucional": (
            "The Technology Transition Office accelerates AFRL innovations into "
            "operational capability, industry partnerships, and small-business programs."
        ),
        "area_tecnologica": [
            "transferencia_tecnologica",
            "inovacao",
            "defesa",
            "aeroespacial",
            "small_business",
            "sbir_sttr",
        ],
        "setor_estrategico": ["defesa", "aeroespacial", "industria_estrategica"],
    },
}
_AFRL_DIRECTORATE_IDS = frozenset(_AFRL_DIRECTORATE_CONFIG.keys())
_AFRL_DIRECTORATE_CODES = frozenset(c["code"] for c in _AFRL_DIRECTORATE_CONFIG.values())
_AFRL_FIXTURES_DIR = ROOT / "fixtures" / "news_research"


def _afrl_unwrap_wayback_url(url: str) -> str:
    u = (url or "").strip()
    if "web.archive.org/web/" not in u.lower():
        return u
    m = re.search(r"web\.archive\.org/web/\d+[a-z_]*/((?:https?://).+)", u, re.I)
    if m:
        return m.group(1).split("#", 1)[0].rstrip("/")
    return u


def _afrl_normalize_article_link(href: str, seed_url: str = "") -> Optional[str]:
    if not href:
        return None
    href = _afrl_unwrap_wayback_url(href)
    link = urljoin(seed_url or _AFRL_NEWS_HUB, href).split("#", 1)[0].rstrip("/")
    low = link.lower()
    if "afrl.af.mil" not in low:
        return None
    if not _AFRL_ARTICLE_RE.search(low):
        return None
    if any(x in low for x in ("/photos/", "/video/", "/biographies/")):
        return None
    return link


def _afrl_parse_listing_date(text: str) -> Optional[str]:
    m = _AFRL_DATE_RE.search(text or "")
    if not m:
        return None
    try:
        mo_map = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }
        mo = mo_map.get(m.group(1).lower())
        if not mo:
            return None
        dt = datetime(int(m.group(3)), mo, int(m.group(2)), tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


def _extract_afrl_news_from_html(seed_url: str, body: str, max_items: int) -> List[Dict[str, Any]]:
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
        link = _afrl_normalize_article_link(a.get("href") or "", seed_url)
        if not link or link in seen:
            continue
        seen.add(link)
        tit = re.sub(r"\s+", " ", (a.get_text() or "").strip())[:320]
        if len(tit) < 12:
            continue
        block_txt = art.get_text(" ", strip=True)
        pub = _afrl_parse_listing_date(block_txt) or ""
        desc = ""
        sum_el = art.select_one(".summary, [class*='summary']")
        if sum_el:
            desc = _strip_html(sum_el.get_text(), max_len=1200)
        if len(desc) < 25:
            desc = _strip_html(block_txt, max_len=800)
            if tit and desc.startswith(tit[:40]):
                desc = desc[len(tit) :].strip()
        out.append(
            {
                "titulo": tit,
                "descricao": desc[:3000],
                "link": link[:800],
                "data_publicacao_raw": pub,
                "source_method": "afrl_news_listing_html",
                "feed_categories": ["news"],
                "fonte_instituicao_raw": "AFRL",
                "autor": "AFRL",
            }
        )
    if len(out) < max(5, max_items // 3):
        for a in soup.select('a[href*="/News/Article-Display/Article/"]'):
            if len(out) >= max_items:
                break
            link = _afrl_normalize_article_link(a.get("href") or "", seed_url)
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
                    "source_method": "afrl_news_listing_fallback",
                    "feed_categories": ["news"],
                    "fonte_instituicao_raw": "AFRL",
                    "autor": "AFRL",
                }
            )
    return out


def _crawl_afrl_news_listing(max_items: int, min_dt: Optional[datetime]) -> List[Dict[str, Any]]:
    """Paginação ?Page=N no hub News (10 artigos/página típico)."""
    cap = max(max_items * 3, max_items)
    out: List[Dict[str, Any]] = []
    seen: set = set()
    max_pages = max(4, (cap // 8) + 2)
    for page in range(1, max_pages + 1):
        if len(out) >= cap:
            break
        url = _AFRL_NEWS_HUB if page == 1 else f"{_AFRL_NEWS_HUB}?Page={page}"
        resp, fetch_mode = _afrl_http_get(url, timeout=60)
        if not resp:
            break
        batch = _extract_afrl_news_from_html(url, resp.text or "", max_items=cap)
        if fetch_mode == "wayback":
            for row in batch:
                row["source_method"] = "afrl_news_listing_wayback"
        if not batch and page > 1:
            break
        for r in batch:
            lk = str(r.get("link") or "")
            if lk in seen:
                continue
            dt = _parse_date(r.get("data_publicacao_raw"))
            if min_dt and dt and dt < min_dt:
                continue
            seen.add(lk)
            out.append(r)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def _sort_key(row: Dict[str, Any]) -> datetime:
        return _parse_date(row.get("data_publicacao_raw")) or epoch

    out.sort(key=_sort_key, reverse=True)
    return out[:cap]


def _afrl_title_from_article_slug(link: str) -> str:
    m = _AFRL_ARTICLE_RE.search(link or "")
    if not m:
        return ""
    slug = (m.group(2) or "").replace("-", " ").strip()
    return slug[:320].title() if slug else ""


def _afrl_directorate_fixture_path(code: str) -> Path:
    return _AFRL_FIXTURES_DIR / f"afrl_{code.upper()}_directorate.html"


def _afrl_fetch_directorate_html(code: str) -> Tuple[str, str]:
    """HTML da página de diretoria (live → fixture local se 403)."""
    url = f"{_AFRL_BASE}/{code}/"
    resp, mode = _afrl_http_get(url, timeout=60)
    if resp and (resp.text or "").strip():
        return resp.text or "", mode
    fix = _afrl_directorate_fixture_path(code)
    if fix.is_file():
        return fix.read_text(encoding="utf-8", errors="replace"), "fixture"
    return "", "failed"


def _afrl_highlight_card_from_anchor(
    a: Any, directorate_code: str, page_url: str, seen: set
) -> Optional[Dict[str, Any]]:
    href = _afrl_unwrap_wayback_url((a.get("href") or "").strip())
    link = _afrl_normalize_article_link(href, page_url)
    if not link or link in seen:
        return None
    link_text = re.sub(r"\s+", " ", (a.get_text() or "")).strip()
    read_more = bool(re.search(r"read\s*more", link_text, re.I))
    card = a.find_parent(["article", "motion-element", "motion-list-item", "motion-slide", "motion-group", "div", "li"])
    block_text = link_text
    if card:
        block_text = re.sub(r"\s+", " ", (card.get_text(" ", strip=True) or "")).strip()
    titulo = ""
    for tag in ("h1", "h2", "h3"):
        prev = a.find_previous(tag)
        if prev:
            tit = re.sub(r"\s+", " ", (prev.get_text() or "")).strip()
            if len(tit) >= 12:
                titulo = tit[:320]
                break
    resumo = re.sub(r"\s*read\s*more\s*$", "", block_text, flags=re.I).strip()
    if not titulo:
        titulo = re.sub(r"\s*read\s*more\s*$", "", block_text, flags=re.I).strip()[:320]
    if not titulo:
        titulo = _afrl_title_from_article_slug(link)
    if len(titulo) < 12:
        return None
    if titulo and resumo.lower().startswith(titulo.lower()[: min(40, len(titulo))]):
        resumo = resumo[len(titulo) :].strip(" .,-")
    if len(resumo) < 25 and len(block_text) > len(resumo):
        resumo = re.sub(r"\s*read\s*more\s*$", "", block_text, flags=re.I).strip()[:3000]
    imagem_url = ""
    if card:
        im = card.find("img")
        if im and im.get("src"):
            imagem_url = urljoin(page_url, str(im.get("src")))[:800]
    pub = _afrl_parse_listing_date(resumo) or _afrl_parse_listing_date(block_text) or ""
    seen.add(link)
    return {
        "titulo": titulo[:320],
        "descricao": resumo[:3000],
        "link": link[:800],
        "data_publicacao_raw": pub,
        "imagem_url": imagem_url,
        "diretoria_origem": directorate_code,
        "read_more_label": "Read More" if read_more else "",
        "source_method": "afrl_directorate_highlights_html",
        "fonte_instituicao_raw": "AFRL",
        "autor": "AFRL",
    }


def _extract_afrl_highlights_from_html(
    body: str, directorate_code: str, page_url: str, max_items: int = 120
) -> List[Dict[str, Any]]:
    if not body:
        return []
    out: List[Dict[str, Any]] = []
    seen: set = set()
    soup = BeautifulSoup(body, "html.parser")
    for a in soup.select('a[href*="/News/Article-Display/Article/"]'):
        if len(out) >= max_items:
            break
        card = _afrl_highlight_card_from_anchor(a, directorate_code, page_url, seen)
        if card:
            out.append(card)
    if len(out) < max(3, max_items // 4):
        for m in re.finditer(
            r"\[([^\]]+?)\]\((https?://[^)]+/News/Article-Display/Article/\d+/[^)]+)\)",
            body,
            re.I,
        ):
            if len(out) >= max_items:
                break
            text, href = m.group(1), m.group(2)
            fake = soup.new_tag("a", href=href)
            fake.string = text
            card = _afrl_highlight_card_from_anchor(fake, directorate_code, page_url, seen)
            if card:
                out.append(card)
    return out


def _afrl_fetch_article_date(link: str) -> Optional[str]:
    resp, _ = _afrl_http_get(link, timeout=28)
    if not resp or not (resp.text or "").strip():
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    for sel in (".date", ".published", "time[datetime]", "[class*='date']"):
        el = soup.select_one(sel)
        if el:
            dt_txt = el.get("datetime") or el.get_text(" ", strip=True)
            if dt_txt and _parse_date(dt_txt[:80]):
                return _parse_date(dt_txt[:80]).strftime("%Y-%m-%d")
    sn = _snippet_from_article_html(resp.text)
    pub = _afrl_parse_listing_date(sn)
    return pub


def _afrl_highlight_cards_for_extras(highlights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []
    for h in highlights:
        cards.append(
            {
                "titulo": h.get("titulo"),
                "link": h.get("link"),
                "resumo": (str(h.get("descricao") or ""))[:600],
                "imagem_url": h.get("imagem_url") or None,
                "diretoria_origem": h.get("diretoria_origem"),
                "read_more_label": h.get("read_more_label") or "Read More",
                "data_publicacao_raw": h.get("data_publicacao_raw") or None,
            }
        )
    return cards


def _afrl_detect_opportunity(blob: str) -> bool:
    b = (blob or "").lower()
    return any(m in b for m in _AFRL_OPPORTUNITY_MARKERS)


def _build_afrl_directorate_institutional(
    source_id: str, highlights: List[Dict[str, Any]], fetch_mode: str
) -> Dict[str, Any]:
    cfg = _AFRL_DIRECTORATE_CONFIG[source_id]
    code = str(cfg["code"])
    url = f"{_AFRL_BASE}/{code}/"
    hl_cards = _afrl_highlight_cards_for_extras(highlights)
    blob = f"{cfg.get('titulo', '')} {' '.join(str(h.get('titulo') or '') for h in highlights)}"
    possivel_edital = source_id == "afrl_technology_transition" and _afrl_detect_opportunity(blob)
    return {
        "titulo": cfg["titulo"],
        "descricao": str(cfg.get("descricao_institucional") or "")[:3000],
        "link": url[:800],
        "data_publicacao_raw": "",
        "source_method": f"afrl_directorate_{fetch_mode}",
        "feed_categories": ["directorate", code],
        "afrl_org_slug": code.lower(),
        "afrl_page_kind": cfg.get("tipo_pesquisa"),
        "afrl_directorate_code": code,
        "fonte_instituicao_raw": "AFRL",
        "_afrl_highlights_raw": highlights,
        "_afrl_highlights_extras": hl_cards,
        "_afrl_fetch_mode": fetch_mode,
        "_afrl_possivel_edital_institutional": possivel_edital,
        "area_tecnologica": list(cfg.get("area_tecnologica") or []),
        "setor_estrategico": list(cfg.get("setor_estrategico") or []),
    }


def _crawl_afrl_directorate_institutional(source_id: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """1 registro pesquisa + highlights brutos (para estatísticas)."""
    cfg = _AFRL_DIRECTORATE_CONFIG[source_id]
    code = str(cfg["code"])
    page_url = f"{_AFRL_BASE}/{code}/"
    body, fetch_mode = _afrl_fetch_directorate_html(code)
    highlights = _extract_afrl_highlights_from_html(body, code, page_url) if body else []
    institutional = _build_afrl_directorate_institutional(source_id, highlights, fetch_mode)
    return [institutional], highlights


def _crawl_afrl_mission_highlights(max_items: int, min_dt: Optional[datetime]) -> List[Dict[str, Any]]:
    """Highlights RA/RJ/RR com data → candidatos a notícia (afrl_mission_highlights)."""
    cap = max(max_items * 4, max_items)
    out: List[Dict[str, Any]] = []
    seen: set = set()
    date_fetches = 0
    max_date_fetches = max(12, min(max_items, 25))
    for source_id in sorted(_AFRL_DIRECTORATE_IDS):
        if len(out) >= cap:
            break
        _, highlights = _crawl_afrl_directorate_institutional(source_id)
        for h in highlights:
            if len(out) >= cap:
                break
            lk = str(h.get("link") or "")
            if not lk or lk in seen:
                continue
            dt = _parse_date(h.get("data_publicacao_raw"))
            if not dt and date_fetches < max_date_fetches:
                pub = _afrl_fetch_article_date(lk)
                date_fetches += 1
                if pub:
                    h["data_publicacao_raw"] = pub
                    dt = _parse_date(pub)
            if not dt:
                continue
            if min_dt and dt < min_dt:
                continue
            seen.add(lk)
            h["source_method"] = "afrl_mission_highlights"
            h["feed_categories"] = ["mission_highlight", str(h.get("diretoria_origem") or "")]
            out.append(h)
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def _sort_key(row: Dict[str, Any]) -> datetime:
        return _parse_date(row.get("data_publicacao_raw")) or epoch

    out.sort(key=_sort_key, reverse=True)
    return out[:max_items]


def _afrl_mission_static_fallback(max_items: int) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for slug, tit in _AFRL_MISSION_STATIC:
        if len(out) >= max_items:
            break
        link = f"{_AFRL_BASE}/{slug}/"
        out.append(
            {
                "titulo": tit,
                "descricao": f"Diretoria/organização AFRL — {tit}.",
                "link": link[:800],
                "data_publicacao_raw": "",
                "source_method": "afrl_mission_static_catalog",
                "feed_categories": ["mission_organization", slug],
                "afrl_org_slug": slug.lower(),
                "afrl_page_kind": "centro_pesquisa",
                "fonte_instituicao_raw": "AFRL",
            }
        )
    return out


def _afrl_mission_link_allowed(link: str) -> Tuple[bool, str]:
    low = (link or "").lower().rstrip("/")
    if "afrl.af.mil" not in low:
        return False, "dominio_fora"
    path = urlparse(low).path.strip("/")
    parts = [p for p in path.split("/") if p]
    if len(parts) != 1:
        return False, "path_nao_organizacao_raiz"
    slug = parts[0].lower()
    if slug in _AFRL_MISSION_PATH_DENY:
        return False, f"path_negado_{slug}"
    if slug in ("news", "photos", "video"):
        return False, "secao_news"
    return True, slug


def _extract_afrl_mission_organizations(seed_url: str, body: str, max_items: int) -> List[Dict[str, Any]]:
    if not body:
        return []
    soup = BeautifulSoup(body, "html.parser")
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for a in soup.select("a[href]"):
        if len(out) >= max_items:
            break
        href = _afrl_unwrap_wayback_url((a.get("href") or "").strip())
        link = urljoin(seed_url or _AFRL_MISSION_HUB, href).split("#", 1)[0].rstrip("/")
        ok, slug = _afrl_mission_link_allowed(link)
        if not ok or link in seen:
            continue
        tit = re.sub(r"\s+", " ", (a.get_text() or "").strip())[:320]
        if len(tit) < 8:
            continue
        low_t = tit.lower()
        if low_t in ("home", "news", "mission organizations", "organizations", "contact us"):
            continue
        seen.add(link)
        blob = f"{tit} {slug}"
        tipo_org = "centro_pesquisa"
        if any(k in blob.lower() for k in ("directorate", "wing", "office", "afwerx", "afosr")):
            tipo_org = "centro_pesquisa"
        elif "library" in blob.lower():
            tipo_org = "portal_institucional"
        out.append(
            {
                "titulo": tit,
                "descricao": "",
                "link": link[:800],
                "data_publicacao_raw": "",
                "source_method": "afrl_mission_organizations_html",
                "feed_categories": ["mission_organization", slug[:40]],
                "afrl_org_slug": slug,
                "afrl_page_kind": tipo_org,
                "fonte_instituicao_raw": "AFRL",
            }
        )
    return out


def _afrl_infer_eixo(blob: str, eixos_detectados: List[str]) -> List[str]:
    out: List[str] = list(eixos_detectados or [])
    seen = set(out)
    b = (blob or "").lower()
    for needle, eixo in _AFRL_POSITIVE_SIGNALS:
        if needle in b and eixo not in seen:
            seen.add(eixo)
            out.append(eixo)
    if not out:
        if "afrl" in b or "research laboratory" in b:
            out.append("defesa")
    return out[:12]


def _afrl_evaluate_relevance(r: Dict[str, Any], *, route: str = "news") -> Tuple[str, Dict[str, Any]]:
    tit = str(r.get("titulo") or "")
    desc = str(r.get("descricao") or "")
    link = str(r.get("link") or "")
    blob = f"{tit} {desc} {link}".lower()
    motivos_pos = []
    seen_p: set = set()
    for needle, _eixo in _AFRL_POSITIVE_SIGNALS:
        if needle in blob and needle not in seen_p:
            seen_p.add(needle)
            motivos_pos.append(needle.strip())
    motivos_neg = [n for n in _AFRL_NEGATIVE_SIGNALS if n in blob]
    eixos = _afrl_infer_eixo(blob, [])
    possivel_edital = any(m in blob for m in _AFRL_OPPORTUNITY_MARKERS)
    meta: Dict[str, Any] = {
        "motivos_relevancia": list(dict.fromkeys(motivos_pos))[:20],
        "motivos_descarte": list(dict.fromkeys(motivos_neg))[:15],
        "eixos_detectados": eixos,
        "possivel_edital": bool(possivel_edital),
        "afrl_route": route,
    }
    n_pos = len(set(motivos_pos))
    n_neg = len(set(motivos_neg))

    if route == "mission":
        if any(n in blob for n in ("news", "article-display")):
            return "discard", {**meta, "motivo": "nao_organizacao"}
        if n_pos == 0 and not any(
            k in blob for k in ("directorate", "wing", "laboratory", "afwerx", "afosr", "afrl")
        ):
            return "discard", {**meta, "motivo": "sem_sinal_organizacao_tecnica"}
        meta["relevancia_afrl"] = "media"
        return "keep", meta

    if n_pos == 0 and n_neg > 0:
        meta["relevancia_afrl"] = "baixa"
        return "discard", {**meta, "motivo": "apenas_sinais_institucionais"}
    if n_pos == 0:
        meta["relevancia_afrl"] = "baixa"
        return "discard", {**meta, "motivo": "sem_sinal_tecnico"}
    if n_neg > 0 and n_pos < 2:
        meta["relevancia_afrl"] = "media"
        return "review", {**meta, "motivo": "institucional_com_tecnico_fraco"}
    if n_neg >= 2 and n_pos < 3:
        meta["relevancia_afrl"] = "media"
        return "review", {**meta, "motivo": "muitos_sinais_institucionais"}
    meta["relevancia_afrl"] = "alta" if n_pos >= 3 else "media"
    return "keep", meta


def _afrl_news_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip()
    if not _afrl_normalize_article_link(lk, lk):
        return False, "url_fora_artigo_news"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw"))
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 20 and len(tit) < 40:
        return False, "sem_resumo_minimo"
    return True, ""


def _afrl_directorate_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 8:
        return False, "titulo_curto"
    return True, ""


def _afrl_mission_highlights_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip()
    if not _afrl_normalize_article_link(lk, lk):
        return False, "url_fora_artigo"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    if not str(r.get("diretoria_origem") or "").strip():
        return False, "sem_diretoria_origem"
    return True, ""


def _afrl_mission_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip()
    ok, why = _afrl_mission_link_allowed(lk)
    if not ok:
        return False, why
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 8:
        return False, "titulo_curto"
    return True, ""


_CAPES_NOTICIAS_PREFIX = "/capes/pt-br/assuntos/noticias/"


def _normalize_capes_noticia_link(href: str, seed_url: str = "") -> Optional[str]:
    if not href:
        return None
    link = urljoin(seed_url or "https://www.gov.br/capes/pt-br/assuntos/noticias", href).split("#", 1)[0].rstrip("/")
    low = link.lower()
    if "gov.br/capes" not in low or _CAPES_NOTICIAS_PREFIX not in low:
        return None
    slug = low.split(_CAPES_NOTICIAS_PREFIX, 1)[-1].strip("/")
    if not slug or "/" in slug:
        return None
    if slug.endswith((".rss", ".xml")) or slug in ("rss", "atom", "feed"):
        return None
    if any(x in slug for x in ("@@", "login", "search")):
        return None
    return link


def _capes_strategic_categoria(blob: str) -> str:
    """Categoria editorial CAPES (uma primária)."""
    b = (blob or "").lower()
    rules: List[Tuple[str, Tuple[str, ...]]] = [
        ("Bolsas", ("bolsa", "bolsas", "bolseir", "aurora", "prêmio carolina", "premio carolina")),
        ("Pós-graduação", ("pós-graduação", "pos-graduacao", "pós graduação", "doutorado", "mestrado", "snpg", "sucupira")),
        ("Internacionalização", ("internacional", "intercâmbio", "intercambio", "cooperação", "cooperacao", "embaixador", "mocambique", "estados unidos")),
        ("Formação", ("formação", "formacao", "professor", "docente", "magistério", "magisterio", "capacitação", "capacitacao")),
        ("Educação", ("educação", "educacao", "ensino", "educação básica", "educacao basica", "educação superior", "pne", "plano nacional de educação")),
        ("Inovação", ("inovação", "inovacao", "empreendedor", "sebrae", "tecnologia", "digital")),
        ("Pesquisa", ("pesquisa", "pesquisador", "científic", "cientific", "laboratório", "laboratorio", "acelerador", "física", "fisica")),
    ]
    for label, keys in rules:
        if any(k in b for k in keys):
            return label
    return "Ciência"


def _capes_infer_eixo(feed_categories: List[str], blob: str) -> List[str]:
    b = (blob or "").lower()
    cats = " ".join(feed_categories or []).lower()
    cat_label = _capes_strategic_categoria(f"{b} {cats}")
    eixo: List[str] = ["ciencia_tecnologia"]
    mapping = {
        "Educação": "formacao_cientifica",
        "Formação": "formacao_cientifica",
        "Ciência": "ciencia_tecnologia",
        "Pesquisa": "pesquisa_aplicada",
        "Pós-graduação": "pos_graduacao",
        "Bolsas": "bolsas_fomento",
        "Internacionalização": "internacionalizacao",
        "Inovação": "inovacao",
    }
    tag = mapping.get(cat_label)
    if tag and tag not in eixo:
        eixo.append(tag)
    if any(k in b or k in cats for k in ("engenharia", "física", "fisica", "matemática", "matematica")):
        if "engenharia" not in eixo:
            eixo.append("engenharia")
    if any(k in b or k in cats for k in ("defesa", "militar", "exército", "exercito")):
        if "defesa" not in eixo:
            eixo.append("defesa")
    seen: set = set()
    out: List[str] = []
    for x in eixo:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _capes_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip()
    if not lk.startswith("http") or not _normalize_capes_noticia_link(lk, lk):
        return False, "url_fora_noticias_capes"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=400)
    if len(body) < 20 and len(tit) < 25:
        return False, "sem_resumo_minimo"
    return True, ""


def _rss_items_newest_first(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def _key(r: Dict[str, Any]) -> datetime:
        return _parse_date(r.get("data_publicacao_raw")) or epoch

    return sorted(items, key=_key, reverse=True)


_F35_NEWS_BASE = "https://www.f35.com"
_F35_FEED_PATH = "/content/lockheed-martin/data/feeds/f35feed.json"
_F35_HUB_FRAG = "/news-and-features/"
_F35_SKIP_CONTENT_TYPES = frozenset({"video", "gallery", "podcast"})


def _f35_flatten_tags(tag_obj: Any) -> List[str]:
    out: List[str] = []
    if isinstance(tag_obj, dict):
        for k, v in tag_obj.items():
            if isinstance(v, str) and v.strip():
                out.append(v.strip()[:120])
            elif isinstance(k, str) and k.strip():
                out.append(k.strip()[:120])
    elif isinstance(tag_obj, list):
        for x in tag_obj:
            if isinstance(x, str) and x.strip():
                out.append(x.strip()[:120])
    return out


def _f35_public_link(href: str) -> str:
    if not href:
        return ""
    link = urljoin(_F35_NEWS_BASE, href).split("#", 1)[0]
    m = re.search(
        r"/content/lockheed-martin/f35/news-and-features/([^/?#]+\.html?)",
        link,
        re.I,
    )
    if m:
        return f"{_F35_NEWS_BASE}/f35/news-and-features/{m.group(1)}"
    if _F35_HUB_FRAG in link.lower():
        return link
    return link


def _f35_infer_eixo(feed_categories: List[str], blob: str) -> List[str]:
    b = (blob or "").lower()
    cats = " ".join(feed_categories or []).lower()
    eixo: List[str] = ["aeroespacial", "defesa"]
    if any(k in b or k in cats for k in ("f-35", "f35", "fighter", "lightning", "stealth", "aircraft")):
        if "aviacao_militar" not in eixo:
            eixo.append("aviacao_militar")
    if any(
        k in b or k in cats
        for k in (
            "sustainment",
            "production",
            "assembly",
            "contract",
            "industry",
            "pratt",
            "lockheed",
            "skunk",
        )
    ):
        if "industria_estrategica" not in eixo:
            eixo.append("industria_estrategica")
    if any(k in b or k in cats for k in ("training", "deployment", "squadron", "wing", "pilot", "air force", "airbase")):
        if "tecnologia_militar" not in eixo:
            eixo.append("tecnologia_militar")
    if any(k in b or k in cats for k in ("international", "alliance", "nato", "uk ", "germany", "japan", "netherlands")):
        if "geopolitica_tecnologica" not in eixo:
            eixo.append("geopolitica_tecnologica")
    seen: set = set()
    out: List[str] = []
    for x in eixo:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _f35_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower()
    if not lk.startswith("http") or "f35.com" not in lk:
        return False, "dominio_invalido"
    if _F35_HUB_FRAG not in lk:
        return False, "url_fora_news_features"
    if lk.rstrip("/").endswith("news-and-features.html"):
        return False, "url_pagina_indice"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 15:
        return False, "sem_resumo_minimo"
    cts = " ".join(str(x).lower() for x in (r.get("feed_categories") or []))
    if any(sk in cts for sk in _F35_SKIP_CONTENT_TYPES):
        return False, "tipo_conteudo_nao_noticia"
    return True, ""


def _extract_f35_news_json(
    feed_url: str,
    body: str,
    max_items: int,
    min_dt: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Feed JSON estático AEM (data-path no hub News & Features)."""
    try:
        data = json.loads(body)
    except Exception:
        return []
    items = data if isinstance(data, list) else []
    if not items and isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list) and v:
                items = v
                break
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    mapped: List[Tuple[datetime, Dict[str, Any]]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        title = re.sub(r"\s+", " ", str(it.get("Title") or "")).strip()[:320]
        desc = _strip_html(it.get("Description") or "", max_len=1200)
        pub = str(it.get("Date") or "").strip()
        dt = _parse_date(pub)
        if min_dt and dt and dt < min_dt:
            continue
        href = str(it.get("URL") or "").strip()
        link = _f35_public_link(href)
        if not title or not link:
            continue
        cats: List[str] = []
        for key in ("Category Tags", "Content Type Tags", "General Tags"):
            cats.extend(_f35_flatten_tags(it.get(key)))
        thumb = str(it.get("Thumbnail Image") or "").strip()
        imagem = urljoin(_F35_NEWS_BASE, thumb) if thumb else None
        mapped.append(
            (
                dt or epoch,
                {
                    "titulo": title,
                    "descricao": desc,
                    "link": link[:800],
                    "data_publicacao_raw": pub,
                    "source_method": "f35_json_feed",
                    "feed_categories": cats[:40],
                    "imagem_url": imagem,
                    "fonte_instituicao_raw": "Lockheed Martin / F-35 Program",
                    "autor": "F-35",
                },
            )
        )
    mapped.sort(key=lambda x: x[0], reverse=True)
    out: List[Dict[str, Any]] = []
    for _, row in mapped:
        out.append(row)
        if len(out) >= max_items:
            break
    return out


_LM_NEWS_BASE = "https://www.lockheedmartin.com"
_LM_FEED_PATH = "/content/lockheed-martin/data/feeds/newsfeed.json"
_LM_NEWS_HUB = "/en-us/news.html"
_LM_REVIEW_STORY_TYPES = frozenset({"Supplier", "3rd Party Article", "Statement & Speech"})
_LM_REJECT_URL_FRAGMENTS = (
    "/capabilities/",
    "/suppliers/",
    "/who-we-are/",
    "/careers",
    "/employees/",
    "/investor",
    "/investors/",
    "/esg/",
    "/sustainability-report",
)


def _lm_flatten_tags(tag_obj: Any) -> List[str]:
    out: List[str] = []
    if isinstance(tag_obj, dict):
        for k, v in tag_obj.items():
            if isinstance(v, str) and v.strip():
                out.append(v.strip()[:120])
            elif isinstance(k, str) and k.strip():
                out.append(k.strip()[:120])
    elif isinstance(tag_obj, list):
        for x in tag_obj:
            if isinstance(x, str) and x.strip():
                out.append(x.strip()[:120])
    return out


def _lm_public_link(href: str, source_url: str = "") -> str:
    raw = (href or source_url or "").strip()
    if not raw:
        return ""
    link = urljoin(_LM_NEWS_BASE, raw).split("#", 1)[0]
    m = re.search(
        r"/content/lockheed-martin/en-us(/news/[^?#]+\.html?)",
        link,
        re.I,
    )
    if m:
        return f"{_LM_NEWS_BASE}/en-us{m.group(1)}"
    return link


def _lm_is_news_article_url(link: str) -> bool:
    ul = (link or "").lower()
    if not ul.startswith("http"):
        return False
    if "news.lockheedmartin.com" in ul:
        return True
    if re.search(
        r"lockheedmartin\.com/en-us/news/(features|press|media|stories|news-releases)/",
        ul,
    ):
        return True
    if "/content/lockheed-martin/en-us/news/" in ul:
        return True
    return False


def _lm_is_institutional_url(link: str) -> bool:
    ul = (link or "").lower()
    return any(frag in ul for frag in _LM_REJECT_URL_FRAGMENTS)


def _lm_blob(row: Dict[str, Any]) -> str:
    cats = " ".join(str(c) for c in (row.get("feed_categories") or []))
    return (
        f"{row.get('titulo','')} {row.get('descricao','')} {cats} "
        f"{row.get('story_type','')} {row.get('lm_product','')}"
    ).lower()


def _lm_classify_for_pipeline(r: Dict[str, Any]) -> Tuple[str, str]:
    """
    keep → notícia | review → review_candidates | reject → descartar.
    """
    link = str(r.get("link") or "")
    if not _lm_is_news_article_url(link):
        return "reject", "url_nao_newsroom"
    if _lm_is_institutional_url(link):
        return "reject", "url_institucional_capability_supplier"
    if link.rstrip("/").endswith("/news.html") or link.rstrip("/").endswith("/en-us/news"):
        return "reject", "url_pagina_indice"
    st = str(r.get("story_type") or "").strip()
    if st in _LM_REVIEW_STORY_TYPES:
        return "review", f"story_type_{st.replace(' ', '_').lower()}"
    b = _lm_blob(r)
    weak_csr = (
        "social impact" in b
        and not any(
            k in b
            for k in (
                "aircraft",
                "missile",
                "space",
                "defense",
                "aerospace",
                "radar",
                "sensor",
                "cyber",
                "autonom",
            )
        )
    )
    if weak_csr:
        return "review", "social_impact_sem_sinal_tecnico"
    if any(k in b for k in ("investor relations", "earnings call", "quarterly results", "stock price")):
        return "review", "sinal_investor_relations"
    if any(
        k in b
        for k in (
            "named a top employer",
            "best place to work",
            "careers at lockheed",
            "now hiring",
            "job opening",
        )
    ):
        return "reject", "hiring_careers"
    if any(k in b for k in ("philanthrop", "charitable foundation", "scholarship program")):
        return "review", "philanthropy_csr"
    if "award" in b and "contract" not in b and "program" not in b:
        if any(k in b for k in ("diversity award", "top employer", "workplace award", "innovation award ceremony")):
            return "review", "corporate_award"
    return "keep", ""


def _lm_infer_eixo(feed_categories: List[str], blob: str) -> List[str]:
    b = (blob or "").lower()
    cats = " ".join(feed_categories or []).lower()
    eixo: List[str] = []
    if any(k in b or k in cats for k in ("defense", "defence", "military", "weapon", "missile defense")):
        eixo.append("defesa")
    if any(
        k in b or k in cats
        for k in ("aerospace", "aero", "aircraft", "aviation", "fighter", "helicopter", "sikorsky", "f-35", "f35")
    ):
        eixo.append("aeroespacial")
    if any(k in b or k in cats for k in ("space", "satellite", "orion", "nasa", "launch", "orbit")):
        eixo.append("espaco")
    if any(k in b or k in cats for k in ("radar", "sensor", "lidar")):
        eixo.append("sensores_radar")
    if any(k in b or k in cats for k in ("electronic warfare", "ew ", "invisible battlespace", "spectrum")):
        eixo.append("guerra_eletronica")
    if any(k in b or k in cats for k in ("artificial intelligence", " ai", "autonom", "machine learning")):
        eixo.append("ia_cyber")
    if any(k in b or k in cats for k in ("cyber", "5g.mil", "c4isr")):
        if "ia_cyber" not in eixo:
            eixo.append("ia_cyber")
    if any(k in b or k in cats for k in ("hypersonic", "supersonic")):
        eixo.append("hipersonicos")
    if any(k in b or k in cats for k in ("material", "composite", "additive")):
        eixo.append("materiais_avancados")
    if any(k in b or k in cats for k in ("engineering", "propulsion", "manufacturing", "production")):
        eixo.append("engenharia")
    if any(
        k in b or k in cats
        for k in ("multi-domain", "joint all-domain", "21st century security", "mission integration")
    ):
        eixo.append("industria_estrategica")
    if not eixo:
        eixo = ["defesa", "aeroespacial"]
    seen: set = set()
    out: List[str] = []
    for x in eixo:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


_DARPA_SITEMAP_URL = "https://www.darpa.mil/sitemap.xml"
_DARPA_PROGRAM_PATH_RE = re.compile(r"/research/programs/([a-z0-9][a-z0-9-]*)", re.I)

_DARPA_POSITIVE_SIGNALS: Tuple[Tuple[str, str], ...] = (
    ("artificial intelligence", "ia"),
    ("autonomous", "autonomia"),
    ("robotics", "robotica"),
    ("sensor", "sensores"),
    ("radar", "sensores"),
    ("electronic warfare", "guerra_eletronica"),
    ("cyber", "cyber"),
    ("hypersonic", "hipersonicos"),
    ("space", "espaco"),
    ("aerospace", "aeroespacial"),
    ("material", "materiais_avancados"),
    ("quantum", "quantum"),
    ("biotechnology", "biotecnologia"),
    ("microelectronics", "microeletronica"),
    ("semiconductor", "semicondutores"),
    ("propulsion", "propulsao"),
    ("defense", "defesa"),
    ("military", "defesa"),
    ("national security", "defesa"),
    ("communications", "comunicacoes"),
    ("electromagnetic", "guerra_eletronica"),
    ("advanced manufacturing", "engenharia_avancada"),
    ("command and control", "c4isr"),
)

_DARPA_NEGATIVE_SIGNALS: Tuple[str, ...] = (
    "careers",
    "job opening",
    "privacy policy",
    "visitor information",
    "speaker request",
    "public affairs only",
    "podcast episode",
    "media contact",
)


def _darpa_slug_to_title(slug: str) -> str:
    s = (slug or "").replace("-", " ").strip()
    return re.sub(r"\s+", " ", s).title()[:320]


def _darpa_infer_eixo(blob: str) -> List[str]:
    b = (blob or "").lower()
    out: List[str] = []
    seen: set = set()
    for needle, eixo in _DARPA_POSITIVE_SIGNALS:
        if needle in b and eixo not in seen:
            seen.add(eixo)
            out.append(eixo)
    if not out:
        if any(k in b for k in ("research", "program", "technology", "science")):
            out.append("engenharia_avancada")
    return out[:8]


def _darpa_evaluate_strategic(r: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """keep | review | discard — notícias/programas (não opportunities)."""
    blob = f"{r.get('titulo','')} {r.get('descricao','')} {r.get('link','')}".lower()
    pos = [n for n, _ in _DARPA_POSITIVE_SIGNALS if n in blob]
    neg = [n for n in _DARPA_NEGATIVE_SIGNALS if n in blob]
    meta: Dict[str, Any] = {
        "motivos_relevancia": list(dict.fromkeys(pos))[:15],
        "motivos_descarte": list(dict.fromkeys(neg))[:10],
        "eixos_detectados": _darpa_infer_eixo(blob),
    }
    if any(x in blob for x in ("rfi:", "baa", "broad agency", "solicitation", "request for proposals")):
        meta["possivel_opportunity"] = True
        return "review", {**meta, "motivo": "sinal_opportunity_em_news"}
    if neg and len(pos) < 1:
        return "discard", {**meta, "motivo": "institucional_sem_sinal_tecnico"}
    if not pos:
        return "review", {**meta, "motivo": "sinal_tecnico_fraco"}
    return "keep", meta


def _normalize_darpa_opportunity_link(r: Dict[str, Any]) -> str:
    tit = str(r.get("titulo") or "").strip()
    pub = str(r.get("data_publicacao_raw") or r.get("data_publicacao") or "").strip()
    slug = re.sub(r"[^a-z0-9]+", "-", tit.lower()).strip("-")[:90] or "item"
    base = "https://www.darpa.mil/work-with-us/opportunities"
    return f"{base}#{slug}"


def _infer_darpa_opportunity_type(titulo: str) -> str:
    t = (titulo or "").lower()
    if t.startswith("rfi:") or " request for information" in t:
        return "RFI"
    if "baa" in t or "broad agency" in t:
        return "BAA"
    if "rfp" in t or "request for proposals" in t:
        return "RFP"
    if "solicitation" in t:
        return "solicitation"
    if "proposers day" in t:
        return "proposers_day"
    return "opportunity"


def _extract_darpa_programs_sitemap(max_items: int, min_dt: Optional[datetime]) -> List[Dict[str, Any]]:
    """Programas ativos via sitemap (hub HTML é SPA/filtros JS)."""
    resp = _http_get(_DARPA_SITEMAP_URL, timeout=120)
    if not resp:
        return []
    body = resp.text or ""
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for block in re.finditer(r"<url>([\s\S]*?)</url>", body, re.I):
        inner = block.group(1)
        loc_m = re.search(r"<loc>([^<]+)</loc>", inner, re.I)
        if not loc_m:
            continue
        loc = loc_m.group(1).strip().split("#", 1)[0].rstrip("/")
        m = _DARPA_PROGRAM_PATH_RE.search(loc)
        if not m:
            continue
        slug = m.group(1).lower()
        if slug in ("programs",):
            continue
        if loc in seen:
            continue
        lastmod = ""
        lm_m = re.search(r"<lastmod>([^<]+)</lastmod>", inner, re.I)
        if lm_m:
            lastmod = lm_m.group(1).strip()[:10]
        dt = _parse_date(lastmod) if lastmod else None
        if min_dt and dt and dt < min_dt:
            continue
        seen.add(loc)
        out.append(
            {
                "titulo": _darpa_slug_to_title(slug),
                "descricao": "",
                "link": loc[:800],
                "data_publicacao_raw": lastmod or "",
                "source_method": "darpa_sitemap_programs",
                "feed_categories": ["research_program"],
                "darpa_program_slug": slug,
            }
        )
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)

    def _sort_key(r: Dict[str, Any]) -> datetime:
        return _parse_date(r.get("data_publicacao_raw")) or epoch

    out.sort(key=_sort_key, reverse=True)
    return out[: max(max_items * 3, max_items)]


def _darpa_news_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower()
    if "darpa.mil/news/" not in lk:
        return False, "url_fora_news_darpa"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 10:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 25:
        return False, "sem_resumo_minimo"
    return True, ""


def _darpa_programs_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower()
    if not _DARPA_PROGRAM_PATH_RE.search(lk):
        return False, "url_fora_programa"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 4:
        return False, "titulo_curto"
    return True, ""


def _darpa_opportunities_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 6:
        return False, "titulo_curto"
    body = _strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 20:
        return False, "sem_resumo_minimo"
    return True, ""


def _lockheed_martin_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower()
    if not lk.startswith("http") or "lockheedmartin.com" not in lk:
        return False, "dominio_invalido"
    if not _lm_is_news_article_url(lk):
        return False, "url_fora_newsroom"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 12:
        return False, "titulo_curto"
    dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(lk)
    if not dt:
        return False, "sem_data_publicacao"
    body = _strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 15:
        return False, "sem_resumo_minimo"
    return True, ""


def _extract_lockheed_martin_news_json(
    feed_url: str,
    body: str,
    max_items: int,
    min_dt: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Feed JSON AEM newsroom (hub SPA Algolia; data-path newsfeed.json)."""
    try:
        data = json.loads(body)
    except Exception:
        return []
    items = data if isinstance(data, list) else []
    if not items and isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list) and v:
                items = v
                break
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    cap = max(max_items * 12, max_items)
    mapped: List[Tuple[datetime, Dict[str, Any]]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        title = re.sub(r"\s+", " ", str(it.get("Title") or "")).strip()[:320]
        desc = _strip_html(it.get("Description") or "", max_len=1200)
        pub = str(it.get("Date") or "").strip()
        dt = _parse_date(pub)
        if min_dt and dt and dt < min_dt:
            continue
        href = str(it.get("URL") or "").strip()
        src_u = str(it.get("SourceURL") or "").strip()
        link = _lm_public_link(href, src_u)
        if not title or not link or not _lm_is_news_article_url(link):
            continue
        cats = _lm_flatten_tags(it.get("Tags"))
        st = str(it.get("Story Type") or "").strip()
        if st:
            cats.append(st[:120])
        prod = str(it.get("Product") or "").strip()
        if prod:
            cats.append(prod[:120])
        thumb = str(it.get("Thumbnail Image") or "").strip()
        imagem = urljoin(_LM_NEWS_BASE, thumb) if thumb else None
        mapped.append(
            (
                dt or epoch,
                {
                    "titulo": title,
                    "descricao": desc,
                    "link": link[:800],
                    "data_publicacao_raw": pub,
                    "source_method": "lm_json_feed",
                    "feed_categories": cats[:40],
                    "imagem_url": imagem,
                    "fonte_instituicao_raw": "Lockheed Martin",
                    "autor": "Lockheed Martin",
                    "story_type": st,
                    "lm_product": prod,
                },
            )
        )
    mapped.sort(key=lambda x: x[0], reverse=True)
    out: List[Dict[str, Any]] = []
    for _, row in mapped:
        out.append(row)
        if len(out) >= cap:
            break
    return out


def _ita_lab_guerra_eletronica_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    lk = str(r.get("link") or "").strip().lower().rstrip("/")
    if not lk.startswith("http") or "ita.br" not in lk:
        return False, "dominio_invalido"
    if "/laboratorios/guerraeletronica" not in lk:
        return False, "url_fora_lab_ge"
    tit = re.sub(r"\s+", " ", str(r.get("titulo") or "")).strip()
    if len(tit) < 10:
        return False, "titulo_curto"
    body = _strip_html(r.get("descricao") or "", max_len=500)
    if len(body) < 40:
        return False, "sem_resumo_institucional"
    return True, ""


_STRATEGIC_NEWS_RAW_FILTERS = {
    "defesanet": _defesanet_should_keep_raw,
    "brisa_news": _brisa_should_keep_raw,
    "brisa_artigos": _brisa_artigos_should_keep_raw,
    "exercito_brasileiro": _exercito_brasileiro_should_keep_raw,
    "softex_noticias": _softex_should_keep_raw,
    "ita_projetos": _ita_projetos_should_keep_raw,
    "ita_lab_guerra_eletronica": _ita_lab_guerra_eletronica_should_keep_raw,
    "capes_noticias": _capes_should_keep_raw,
    "f35_news": _f35_should_keep_raw,
    "lockheed_martin_news": _lockheed_martin_should_keep_raw,
    "mcti_noticias": _mcti_should_keep_raw,
    "war_gov_news": _war_gov_should_keep_raw,
    "nato_news": _nato_should_keep_raw,
    "afrl_news": _afrl_news_should_keep_raw,
    "afrl_mission_organizations": _afrl_mission_should_keep_raw,
    "afrl_air_warfare_research": _afrl_directorate_should_keep_raw,
    "afrl_space_warfare_research": _afrl_directorate_should_keep_raw,
    "afrl_technology_transition": _afrl_directorate_should_keep_raw,
    "afrl_mission_highlights": _afrl_mission_highlights_should_keep_raw,
    "darpa_news": _darpa_news_should_keep_raw,
    "darpa_programs_research": _darpa_programs_should_keep_raw,
    "darpa_opportunities_research": _darpa_opportunities_should_keep_raw,
}

def _mil_news_should_keep_raw(source_id: str):
    from scripts.news_research import military_af_research as mil

    return lambda r: mil.dod_afmil_news_should_keep_raw(source_id, r)


def _mil_arl_news_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    from scripts.news_research import military_af_research as mil

    return mil.arl_news_should_keep_raw(r)


def _mil_pesquisa_should_keep_raw(r: Dict[str, Any]) -> Tuple[bool, str]:
    from scripts.news_research import military_af_research as mil

    return mil.pesquisa_portal_should_keep_raw(r)


_STRATEGIC_BRISA_IDS = frozenset({"brisa_news", "brisa_artigos"})
_STRATEGIC_CAPES_IDS = frozenset({"capes_noticias"})
_STRATEGIC_MCTI_IDS = frozenset({"mcti_noticias"})
_STRATEGIC_WAR_GOV_IDS = frozenset({"war_gov_news"})
_STRATEGIC_NATO_IDS = frozenset({"nato_news"})
_STRATEGIC_AFRL_IDS = frozenset(
    {
        "afrl_news",
        "afrl_mission_organizations",
        "afrl_air_warfare_research",
        "afrl_space_warfare_research",
        "afrl_technology_transition",
        "afrl_mission_highlights",
    }
)
_STRATEGIC_MILITARY_NEWS_IDS = frozenset(
    {"afmc_news", "afnwc_news", "space_force_news", "arl_news"}
)
_STRATEGIC_MILITARY_PESQUISA_IDS = frozenset(
    {
        "afrl_technology_areas",
        "afnwc_innovation",
        "afnwc_weapon_systems",
        "arl_resources",
    }
)
_STRATEGIC_MILITARY_IDS = _STRATEGIC_MILITARY_NEWS_IDS | _STRATEGIC_MILITARY_PESQUISA_IDS
_STRATEGIC_ITA_IDS = frozenset({"ita_projetos", "ita_lab_guerra_eletronica"})
_STRATEGIC_ENRICH_SLOW_IDS = (
    frozenset(
        {
            "defesanet",
            "exercito_brasileiro",
            "softex_noticias",
            "capes_noticias",
            "f35_news",
            "lockheed_martin_news",
            "mcti_noticias",
            "war_gov_news",
            "nato_news",
            "afrl_news",
            "afrl_mission_organizations",
            "afrl_air_warfare_research",
            "afrl_space_warfare_research",
            "afrl_technology_transition",
            "afrl_mission_highlights",
            "darpa_news",
            "darpa_programs_research",
            "afmc_news",
            "afnwc_news",
            "space_force_news",
            "arl_news",
            "afrl_technology_areas",
            "afnwc_innovation",
            "afnwc_weapon_systems",
            "arl_resources",
        }
    )
    | _STRATEGIC_BRISA_IDS
    | _STRATEGIC_ITA_IDS
    | _STRATEGIC_MCTI_IDS
    | _STRATEGIC_WAR_GOV_IDS
    | _STRATEGIC_NATO_IDS
    | _STRATEGIC_AFRL_IDS
    | _STRATEGIC_MILITARY_IDS
)
_STRATEGIC_DARPA_IDS = frozenset({"darpa_news", "darpa_programs_research", "darpa_opportunities_research"})
_STRATEGIC_DISPLAY_FONTES = {
    "exercito_brasileiro": "Exército Brasileiro",
    "softex_noticias": "SOFTEX",
    "ita_projetos": "ITA",
    "ita_lab_guerra_eletronica": "ITA",
    "capes_noticias": "CAPES",
    "f35_news": "F-35",
    "lockheed_martin_news": "Lockheed Martin",
    "mcti_noticias": "MCTI",
    "war_gov_news": "U.S. Department of Defense / War.gov",
    "nato_news": "NATO",
    "afrl_news": "AFRL",
    "afrl_mission_organizations": "AFRL",
    "afrl_air_warfare_research": "AFRL",
    "afrl_space_warfare_research": "AFRL",
    "afrl_technology_transition": "AFRL",
    "afrl_mission_highlights": "AFRL",
    "darpa_news": "DARPA",
    "darpa_programs_research": "DARPA",
    "darpa_opportunities_research": "DARPA",
    "afmc_news": "AFMC",
    "afnwc_news": "AFNWC",
    "space_force_news": "U.S. Space Force",
    "arl_news": "ARL",
    "afrl_technology_areas": "AFRL",
    "afnwc_innovation": "AFNWC",
    "afnwc_weapon_systems": "AFNWC",
    "arl_resources": "ARL",
}

for _mid in _STRATEGIC_MILITARY_NEWS_IDS:
    if _mid != "arl_news":
        _STRATEGIC_NEWS_RAW_FILTERS[_mid] = _mil_news_should_keep_raw(_mid)
_STRATEGIC_NEWS_RAW_FILTERS["arl_news"] = _mil_arl_news_should_keep_raw
for _pid in _STRATEGIC_MILITARY_PESQUISA_IDS:
    _STRATEGIC_NEWS_RAW_FILTERS[_pid] = _mil_pesquisa_should_keep_raw


def _snippet_from_article_html(html: str, max_len: int = 1200) -> str:
    """Meta description / og:description / primeiro parágrafo principal."""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for attrs in ({"property": "og:description"}, {"name": "description"}):
        n = soup.find("meta", attrs=attrs)
        if n and n.get("content"):
            s = _strip_html(n.get("content"), max_len=max_len)
            if len(s) >= 20:
                return s
    main = soup.find("article") or soup.find("main") or soup.body
    if main:
        for p in main.find_all("p", limit=6):
            t = _strip_html(p.get_text(), max_len=max_len)
            if len(t) >= 40:
                return t
    return ""


def _filter_search_blob(r: Dict[str, Any]) -> str:
    """Texto agregado para require/exclude: título, descrição, link, categorias do feed."""
    parts = [
        str(r.get("titulo") or ""),
        str(r.get("descricao") or ""),
        str(r.get("link") or ""),
    ]
    cats = r.get("feed_categories")
    if isinstance(cats, list):
        parts.extend(str(c) for c in cats if c)
    return " ".join(parts).lower()


def _apply_source_filters(
    src: Dict[str, Any], r: Dict[str, Any]
) -> Tuple[bool, List[str], Optional[str]]:
    """
    exclude_keywords / require_any_keyword sobre blob expandido (incl. categorias RSS).
    Devolve (passou, keywords que deram match require_any, motivo de exclusão ou None).

    Nota: contexto biológico de \"defense\" (plant immunity, etc.) não é rejeitado aqui;
    a taxonomia (militar vs biológico) é aplicada em build_eurekalert_wave1_payloads.py.
    """
    blob = _filter_search_blob(r)
    matched: List[str] = []
    for kw in src.get("exclude_keywords") or []:
        if not isinstance(kw, str) or not kw.strip():
            continue
        ks = kw.strip().lower()
        if ks in blob:
            return False, [], f"exclude_keyword:{kw.strip()}"
    req = src.get("require_any_keyword") or []
    if isinstance(req, list) and req:
        for kw in req:
            if not isinstance(kw, str) or not kw.strip():
                continue
            ks = kw.strip().lower()
            if ks in blob:
                matched.append(kw.strip())
        if not matched:
            return False, [], "require_any_keyword_no_match"
    return True, matched, None


def _passes_source_filters(src: Dict[str, Any], r: Dict[str, Any]) -> bool:
    ok, _, _ = _apply_source_filters(src, r)
    return ok


def _exclude_reason_is_medical_generic(reason: Optional[str]) -> bool:
    """Heurística para diagnóstico: exclusão alinhada a temas de saúde/medicina genéricos."""
    if not reason or not str(reason).startswith("exclude_keyword:"):
        return False
    frag = str(reason).split(":", 1)[-1].lower()
    needles = (
        "cancer",
        "clinical",
        "patient",
        "hospital",
        "disease",
        "medicine",
        "health",
        "psychology",
        "oncology",
        "covid",
        "diabetes",
        "alzheimer",
        "pediatric",
        "trial",
        "therapy",
        "biology",
    )
    return any(n in frag for n in needles)


def _loose_item_categories(inner: str) -> List[str]:
    out: List[str] = []
    for m in re.finditer(r"<category\b([^>]*)>([\s\S]*?)</category>", inner, re.I):
        attrs, inner_txt = m.group(1), m.group(2)
        term_m = re.search(r'term\s*=\s*["\']([^"\']+)["\']', attrs)
        if term_m:
            t = term_m.group(1).strip()
            if t:
                out.append(t)
                continue
        t = re.sub(r"\s+", " ", _strip_html(inner_txt, max_len=400)).strip()
        if t:
            out.append(t)
    for m in re.finditer(r"<category\b([^/>]+)/>", inner, re.I):
        attrs = m.group(1)
        term_m = re.search(r'term\s*=\s*["\']([^"\']+)["\']', attrs)
        if term_m:
            t = term_m.group(1).strip()
            if t:
                out.append(t)
    return out


def _first_pdf_from_iaea_page(html: str, base_url: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """Primeiro PDF IAEA visível na página (anchor), sem rastrear site inteiro."""
    if not html:
        return None, []
    soup = BeautifulSoup(html, "html.parser")
    for a in soup.select('a[href*=".pdf"]'):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        full = urljoin(base_url, href).split("#", 1)[0]
        low = full.lower()
        if not low.endswith(".pdf"):
            continue
        host = (urlparse(full).hostname or "").lower()
        if "iaea.org" not in host:
            continue
        doc = {"url": full[:800], "tipo": "pdf"}
        return full[:800], [doc]
    return None, []


def _maybe_enrich_from_page(r: Dict[str, Any], budget: Dict[str, int], src_id: str = "") -> None:
    """
    Até `max` GETs por fonte: meta/JSON-LD/resumo quando RSS/listing veio vazio.
    Não inventa texto: só extrai do HTML público.
    """
    max_f = int(budget.get("max", 25))
    if int(budget.get("n", 0)) >= max_f:
        return
    lk = str(r.get("link") or "").strip()
    if not lk.startswith("http"):
        return
    body = _strip_html(r.get("descricao") or "", max_len=600)
    min_body = 40 if src_id == "iaea_news_publications" else 35
    need_text = len(body) < min_body
    raw_pub = str(r.get("data_publicacao_raw") or "").strip()
    need_date = not raw_pub or not _parse_date(raw_pub)
    need_image = src_id in _STRATEGIC_ENRICH_SLOW_IDS and not (r.get("imagem_url") or "").strip()
    if not need_text and not need_date and not need_image:
        return
    if src_id in ("afrl_news", "afrl_mission_highlights"):
        resp, _fm = _afrl_http_get(lk, timeout=28)
    elif src_id in _STRATEGIC_MILITARY_NEWS_IDS:
        from scripts.news_research import military_af_research as mil

        resp, _fm = mil._dod_http_get(lk, timeout=28)
    else:
        resp = _http_get(lk, timeout=22)
        _fm = "live"
    if not resp or not (resp.text or "").strip():
        return
    budget["n"] = int(budget.get("n", 0)) + 1
    r["_page_enriched"] = True
    if _fm == "wayback":
        r["_afrl_fetch_mode"] = "wayback"
    html = resp.text
    if need_text:
        sn = _snippet_from_article_html(html)
        if sn:
            r["descricao"] = sn[:3000]
    if need_date:
        found = False
        for cand in _meta_and_jsonld_dates(html):
            if _parse_date(cand):
                r["data_publicacao_raw"] = cand[:120]
                found = True
                break
        if not found:
            for m in re.finditer(r"\b(20\d{2}-\d{2}-\d{2})\b", html[:14000]):
                if _parse_date(m.group(1)):
                    r["data_publicacao_raw"] = m.group(1)
                    found = True
                    break
        if not found:
            udt = _parse_date_from_url(lk)
            if udt:
                r["data_publicacao_raw"] = udt.strftime("%Y-%m-%d")
    if src_id == "iaea_news_publications" and not (r.get("pdf_url") or "").strip():
        pdf_u, docs = _first_pdf_from_iaea_page(html, lk)
        if pdf_u:
            r["pdf_url"] = pdf_u
            if docs:
                cur = r.get("documentos")
                if isinstance(cur, list):
                    r["documentos"] = cur + docs
                else:
                    r["documentos"] = docs
    if src_id in _STRATEGIC_ENRICH_SLOW_IDS:
        if not (r.get("imagem_url") or "").strip():
            img = _og_image_from_html(html, lk)
            if img:
                r["imagem_url"] = img
        if not (r.get("autor") or "").strip() and (r.get("fonte_instituicao_raw") or "").strip():
            r["autor"] = str(r.get("fonte_instituicao_raw")).strip()[:200]
    if src_id == "exercito_brasileiro" and need_date:
        soup_eb = BeautifulSoup(html, "html.parser")
        dates_el = soup_eb.select_one(".dates, [class*='dates']")
        if dates_el:
            txt_dates = dates_el.get_text(" ", strip=True)
            m_pub = re.search(r"Publicado em\s+(\d{2}/\d{2}/\d{4})", txt_dates, re.I)
            if m_pub:
                r["data_publicacao_raw"] = m_pub.group(1)
        body_after_og = _strip_html(r.get("descricao") or "", max_len=600)
        if need_text or len(body_after_og) < 40:
            ogd = soup_eb.find("meta", attrs={"property": "og:description"})
            if ogd and ogd.get("content"):
                od = _strip_html(ogd.get("content"), max_len=600)
                if len(od) >= 20:
                    r["descricao"] = od[:3000]
            sn = _snippet_from_article_html(html)
            if len(sn) >= 40:
                r["descricao"] = sn[:3000]
    if src_id == "capes_noticias":
        soup_cap = BeautifulSoup(html, "html.parser")
        if need_date:
            pub_el = soup_cap.select_one(".documentPublished, .published, [class*='documentPublished']")
            if pub_el:
                m_pub = re.search(r"\b(\d{2}/\d{2}/(20\d{2}))\b", pub_el.get_text(" ", strip=True))
                if m_pub:
                    r["data_publicacao_raw"] = m_pub.group(1)
        if need_text or len(_strip_html(r.get("descricao") or "", max_len=600)) < 40:
            lead = soup_cap.select_one("#content-core p, .documentDescription, [property='rnews:articleBody'] p")
            if lead:
                ld = _strip_html(lead.get_text(), max_len=900)
                if len(ld) >= 40:
                    r["descricao"] = ld[:3000]
        byline = soup_cap.select_one(".documentByLine, .author")
        if byline and not (r.get("autor") or "").strip():
            tx = re.sub(r"\s+", " ", byline.get_text()).strip()
            if tx and "publicado" not in tx.lower()[:12]:
                r["autor"] = tx[:200]
    if src_id == "mcti_noticias":
        soup_mcti = BeautifulSoup(html, "html.parser")
        if need_date:
            pub_el = soup_mcti.select_one(".documentPublished, .published, [class*='documentPublished']")
            if pub_el:
                m_pub = re.search(r"\b(\d{2}/\d{2}/(20\d{2}))\b", pub_el.get_text(" ", strip=True))
                if m_pub:
                    r["data_publicacao_raw"] = m_pub.group(1)
        if need_text or len(_strip_html(r.get("descricao") or "", max_len=600)) < 40:
            lead = soup_mcti.select_one("#content-core p, .documentDescription, [property='rnews:articleBody'] p")
            if lead:
                ld = _strip_html(lead.get_text(), max_len=900)
                if len(ld) >= 30:
                    r["descricao"] = ld[:3000]
            if len(_strip_html(r.get("descricao") or "", max_len=600)) < 30:
                sn = _snippet_from_article_html(html)
                if len(sn) >= 30:
                    r["descricao"] = sn[:3000]
        byline = soup_mcti.select_one(".documentByLine, .author")
        if byline and not (r.get("autor") or "").strip():
            tx = re.sub(r"\s+", " ", byline.get_text()).strip()
            if tx and "publicado" not in tx.lower()[:12]:
                r["autor"] = tx[:200]
    if src_id == "nato_news":
        model_u = _nato_model_json_url(lk)
        if model_u and (need_text or need_date or need_image):
            mresp = _http_get(model_u, timeout=28)
            if mresp and (mresp.text or "").strip().startswith("{"):
                parsed = _nato_fields_from_model(mresp.text, lk)
                if need_text and parsed.get("descricao"):
                    r["descricao"] = parsed["descricao"][:3000]
                if parsed.get("titulo"):
                    r["titulo"] = parsed["titulo"][:320]
                if need_date and parsed.get("data_publicacao_raw"):
                    r["data_publicacao_raw"] = parsed["data_publicacao_raw"][:120]
                if need_image and parsed.get("imagem_url"):
                    r["imagem_url"] = parsed["imagem_url"]
                if parsed.get("feed_categories"):
                    r["feed_categories"] = parsed["feed_categories"]
    if src_id in ("afrl_news", "afrl_mission_highlights"):
        soup_afrl = BeautifulSoup(html, "html.parser")
        if need_date:
            for sel in (".date", ".published", "time[datetime]", "[class*='date']"):
                el = soup_afrl.select_one(sel)
                if el:
                    dt_txt = el.get("datetime") or el.get_text(" ", strip=True)
                    if dt_txt and _parse_date(dt_txt[:80]):
                        r["data_publicacao_raw"] = dt_txt[:120]
                        break
        if need_text or len(_strip_html(r.get("descricao") or "", max_len=600)) < 40:
            ogd = soup_afrl.find("meta", attrs={"property": "og:description"})
            if ogd and ogd.get("content"):
                od = _strip_html(ogd.get("content"), max_len=600)
                if len(od) >= 25:
                    r["descricao"] = od[:3000]
            if len(_strip_html(r.get("descricao") or "", max_len=600)) < 40:
                lead = soup_afrl.select_one(".summary, .article-summary, #main p, article p")
                if lead:
                    ld = _strip_html(lead.get_text(), max_len=900)
                    if len(ld) >= 30:
                        r["descricao"] = ld[:3000]
                if len(_strip_html(r.get("descricao") or "", max_len=600)) < 40:
                    sn = _snippet_from_article_html(html)
                    if len(sn) >= 30:
                        r["descricao"] = sn[:3000]
    if src_id == "afrl_mission_organizations":
        soup_mo = BeautifulSoup(html, "html.parser")
        if need_text or len(_strip_html(r.get("descricao") or "", max_len=600)) < 30:
            ogd = soup_mo.find("meta", attrs={"property": "og:description"})
            if ogd and ogd.get("content"):
                od = _strip_html(ogd.get("content"), max_len=600)
                if len(od) >= 25:
                    r["descricao"] = od[:3000]
            if len(_strip_html(r.get("descricao") or "", max_len=600)) < 30:
                sn = _snippet_from_article_html(html)
                if len(sn) >= 25:
                    r["descricao"] = sn[:3000]
    if src_id in _STRATEGIC_ENRICH_SLOW_IDS:
        time.sleep(0.45)


def _http_get(url: str, timeout: int = 30) -> Optional[requests.Response]:
    headers = dict(HEADERS)
    if "afrl.af.mil" in (url or "").lower():
        headers["User-Agent"] = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code >= 400:
            return None
        return r
    except Exception:
        return None


def _afrl_wayback_fallback_enabled() -> bool:
    return os.environ.get("AFRL_WAYBACK_FALLBACK", "").strip().lower() in ("1", "true", "yes")


def _afrl_http_get(url: str, timeout: int = 60) -> Tuple[Optional[requests.Response], str]:
    """
    GET para páginas afrl.af.mil. Se Akamai retornar 403, opcionalmente usa Wayback
    (somente com AFRL_WAYBACK_FALLBACK=1 — típico em dry-run fora de rede autorizada).
    """
    r = _http_get(url, timeout=timeout)
    if r:
        return r, "live"
    if not _afrl_wayback_fallback_enabled() or "afrl.af.mil" not in (url or "").lower():
        return None, "failed"
    wb_url = _AFRL_WAYBACK_WEB + url
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        wr = requests.get(wb_url, headers=headers, timeout=timeout + 20)
        if wr.status_code < 400 and len((wr.text or "").strip()) > 500:
            return wr, "wayback"
    except Exception:
        pass
    return None, "failed"


def _looks_like_feed_xml(text: str) -> bool:
    low = (text or "").lower()
    return "<rss" in low or "<feed" in low or "<rdf:rdf" in low


def _xml_text_local(el: ET.Element, *local_names: str) -> str:
    want = {n.lower() for n in local_names}
    for ch in list(el):
        tag = _local_tag(ch.tag)
        if tag in want:
            return "".join(ch.itertext() or "").strip()
    return ""


def _extract_feed_items_loose(feed_url: str, body: str) -> List[Dict[str, Any]]:
    """
    Fallback quando o XML do feed é inválido (ex.: `<br>` em `<title>` na IAEA publications).
    Extrai blocos `<item>...</item>` e saneia tags vazias comuns antes do ElementTree.
    """
    out: List[Dict[str, Any]] = []
    for m in re.finditer(r"<item\b[^>]*>([\s\S]*?)</item>", body, re.I):
        inner = m.group(1)
        inner = re.sub(r"(?is)<\s*br\s*/?>", " ", inner)
        inner = re.sub(r"(?is)<\s*img[^>]*/?>", " ", inner)
        frag = f"<?xml version='1.0' encoding='utf-8'?><item>{inner}</item>"
        try:
            it = ET.fromstring(frag.encode("utf-8", errors="ignore"))
        except Exception:
            continue
        title = _xml_text_local(it, "title")[:320]
        link = _xml_text_local(it, "link")
        if not link:
            guid = _xml_text_local(it, "guid", "id")
            if guid.startswith("http"):
                link = guid
        desc = (
            _xml_text_local(it, "description")
            or _xml_text_local(it, "summary")
            or _child_text_join(it, "encoded")
        )
        desc = _strip_html(desc, max_len=3000)
        pub = _xml_text_local(it, "pubDate", "published", "updated")
        if link:
            link = urljoin(feed_url, link)
        if not title and not link:
            continue
        cats_loose = _loose_item_categories(inner)
        out.append(
            {
                "titulo": title[:320],
                "descricao": re.sub(r"\s+", " ", desc).strip()[:3000],
                "link": link[:800],
                "data_publicacao_raw": pub,
                "source_method": "rss_loose",
                "feed_categories": cats_loose,
            }
        )
    return out


def _extract_feed_items(feed_url: str, body: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(body.encode("utf-8", errors="ignore"))
    except Exception:
        return _extract_feed_items_loose(feed_url, body)

    # RSS 2.0 / Atom fallback
    items = root.findall(".//item")
    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

    if not items and "<item" in (body or "").lower():
        return _extract_feed_items_loose(feed_url, body)

    for it in items:
        def _text(path: str) -> str:
            n = it.find(path)
            return (n.text or "").strip() if n is not None and n.text else ""

        title = _text("title") or _text("{http://www.w3.org/2005/Atom}title")
        link = _text("link")
        if not link:
            guid = _text("guid") or _text("{http://www.w3.org/2005/Atom}id")
            if guid.startswith("http"):
                link = guid
        if not link:
            atom_link = it.find("{http://www.w3.org/2005/Atom}link")
            if atom_link is not None:
                link = atom_link.attrib.get("href", "").strip()
        desc = (
            _text("description")
            or _child_text_join(it, "encoded")
            or _text("summary")
            or _text("{http://www.w3.org/2005/Atom}summary")
            or _child_text_join(it, "content")
        )
        desc = _strip_html(desc, max_len=3000)
        pub = (
            _text("pubDate")
            or _child_text_join(it, "date")
            or _text("published")
            or _text("updated")
            or _text("{http://www.w3.org/2005/Atom}updated")
            or _text("{http://www.w3.org/2005/Atom}published")
        )
        if link:
            link = urljoin(feed_url, link)
        if not title and not link:
            continue
        cats: List[str] = []
        for cat in it.findall("category"):
            t = (cat.text or "").strip()
            if not t:
                t = (cat.get("term") or cat.get("text") or "").strip()
            if t:
                cats.append(t)
        for cat in it.findall("{http://www.w3.org/2005/Atom}category"):
            t = (cat.get("term") or cat.text or "").strip()
            if t:
                cats.append(t)
        inst_src = ""
        for ch in list(it):
            lt = _local_tag(ch.tag)
            if lt in ("creator", "author", "source", "publisher", "contributor"):
                tx = "".join(ch.itertext() or "").strip()
                if tx and not inst_src:
                    inst_src = tx[:500]
        out.append(
            {
                "titulo": title[:320],
                "descricao": re.sub(r"\s+", " ", desc).strip()[:3000],
                "link": link[:800],
                "data_publicacao_raw": pub,
                "source_method": "rss",
                "feed_categories": cats,
                "fonte_instituicao_raw": inst_src or None,
            }
        )
    return out


def _extract_listing_items(seed_url: str, body: str, max_items: int) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(body, "html.parser")
    out: List[Dict[str, Any]] = []
    seen = set()
    seed_host = (urlparse(seed_url).hostname or "").lower()
    banned_hosts = ("x.com", "facebook.com", "linkedin.com", "youtube.com", "instagram.com")
    generic_titles = {
        "home",
        "news",
        "events",
        "search",
        "about",
        "contact",
        "publications",
        "work with us",
        "skip to main content",
    }
    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        link = urljoin(seed_url, href).split("#", 1)[0]
        host = (urlparse(link).hostname or "").lower()
        if host and seed_host and host != seed_host:
            if not host.endswith("." + seed_host):
                continue
        if any(bh in host for bh in banned_hosts):
            continue
        if link in seen:
            continue
        if "eurekalert.org" in seed_host:
            if not re.search(r"/news-releases/\d{4,}\b", link, re.I):
                continue
        seen.add(link)
        title = " ".join((a.get_text() or "").split()).strip()
        ctx = f"{title} {link}".lower()
        # filtros conservadores de ruído
        if any(x in link.lower() for x in ("/login", "/signin", "/contact", "/about", "/privacy", "/terms", "/cookie", "/careers", "/jobs")):
            continue
        if title.lower() in generic_titles:
            continue
        if len(title) < 10 and not any(k in ctx for k in ("news", "research", "publication", "report", "study", "nasa", "darpa", "iaea", "eurekalert")):
            continue
        path = urlparse(link).path or "/"
        segs = [s for s in path.split("/") if s]
        if len(segs) < 2 and not any(k in ctx for k in ("rss", "xml", "news", "article", "publication")):
            continue
        out.append(
            {
                "titulo": title[:320] or link.rsplit("/", 1)[-1][:120],
                "descricao": "",
                "link": link[:800],
                "data_publicacao_raw": "",
                "source_method": "html_listing",
                "feed_categories": [],
            }
        )
        if len(out) >= max_items:
            break
    return out


def _discover_rss_links(seed_url: str, body: str) -> List[str]:
    soup = BeautifulSoup(body, "html.parser")
    out = []
    for n in soup.select("link[type='application/rss+xml'][href], link[type='application/atom+xml'][href]"):
        h = (n.get("href") or "").strip()
        if h:
            out.append(urljoin(seed_url, h))
    for a in soup.select("a[href]"):
        h = (a.get("href") or "").strip()
        txt = " ".join((a.get_text() or "").split()).lower()
        if not h:
            continue
        hl = h.lower()
        if hl.endswith(".rss") or hl.endswith(".xml") or "rss" in hl or "atom" in hl or "rss" in txt:
            out.append(urljoin(seed_url, h))
    ded = []
    seen = set()
    for u in out:
        if u in seen:
            continue
        seen.add(u)
        ded.append(u)
    return ded[:8]


def _seed_plan(src: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Lista (seed_url, seed_kind) com kind news|publications|mixed para roteamento IAEA."""
    sid = str(src.get("id") or "")
    if sid == "iaea_news_publications":
        news = [str(u).strip() for u in (src.get("seed_urls_news") or []) if str(u).strip()]
        pubs = [str(u).strip() for u in (src.get("seed_urls_publications") or []) if str(u).strip()]
        if news or pubs:
            # Publicações primeiro para garantir itens `pesquisa` antes do teto max_items.
            return [(u, "publications") for u in pubs] + [(u, "news") for u in news]
    out: List[Tuple[str, str]] = []
    for u in src.get("seed_urls") or []:
        u = str(u).strip()
        if u:
            out.append((u, "mixed"))
    return out


def _detect_content_type(item: Dict[str, Any], src_id: str) -> str:
    lk = str(item.get("link") or "").lower()
    tit = str(item.get("titulo") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    blob = f"{tit} {desc} {lk}"

    if src_id == "iaea_news_publications":
        sk = str(item.get("seed_kind") or "mixed")
        if sk == "publications":
            return "pesquisa"
        if sk == "news":
            return "noticia"
        if "/publications/" in lk or "/resources/" in lk or "/sites/default/files/" in lk:
            return "pesquisa"
        if any(
            x in lk
            for x in (
                "/newscenter/",
                "/pressreleases/",
                "/press/",
                "/multimedia/",
                "/newscenter/news/",
            )
        ):
            return "noticia"
        if any(
            x in blob
            for x in (
                "technical report",
                "safety standard",
                "iaea series",
                "nuclear security series",
                "guidance document",
                "publication ",
                "tecdoc",
            )
        ):
            return "pesquisa"

    if src_id == "brisa_artigos":
        return "pesquisa"
    if src_id in _STRATEGIC_ITA_IDS:
        return "pesquisa"
    if src_id in (
        "defesanet",
        "brisa_news",
        "exercito_brasileiro",
        "capes_noticias",
        "f35_news",
        "lockheed_martin_news",
        "mcti_noticias",
        "war_gov_news",
        "nato_news",
        "afrl_news",
        "afrl_mission_highlights",
        "darpa_news",
    ) or src_id in _STRATEGIC_MILITARY_NEWS_IDS:
        return "noticia"
    if src_id in _AFRL_DIRECTORATE_IDS or src_id == "afrl_mission_organizations":
        return "pesquisa"
    if src_id in _STRATEGIC_MILITARY_PESQUISA_IDS:
        return "pesquisa"
    if src_id == "darpa_programs_research":
        return "pesquisa"

    if src_id == "eurekalert_science_filtered":
        if any(
            x in blob
            for x in (
                "published in",
                "peer-reviewed",
                "peer reviewed",
                "in the journal",
                "proceedings",
                "technical report",
                "preprint",
                "doi:",
                "arxiv:",
                "10.1038/",
                "10.1126/",
                "systematic review",
            )
        ):
            return "pesquisa"
        if len(desc) > 1200 and any(x in blob for x in ("study", "researchers", "findings", "experiments", "method")):
            return "pesquisa"
        return "noticia"

    t = blob
    if any(x in t for x in ("report", "study", "publication", "paper", "research", "white paper", "technical")):
        return "pesquisa"
    if "darpa_opportunities_research" in src_id:
        return "pesquisa"
    return "noticia"


def _iaea_infer_tags(blob: str, base_tags: List[str]) -> List[str]:
    """Refina tags nucleares quando o texto/URL traz evidência (sem inventar domínios fora do nuclear)."""
    b = blob.lower()
    extra: List[str] = []
    if any(k in b for k in ("safeguard", "safeguards", "verification", "inspector")):
        extra.append("seguranca_nuclear")
    if any(k in b for k in ("reactor", "nuclear energy", "nuclear power", "npp", "electricity")):
        extra.append("energia")
    if any(k in b for k in ("radiotherapy", "cancer", "health", "nutrition", "sterile")):
        extra.append("aplicacoes_nucleares")
    seen = set()
    out: List[str] = []
    for t in list(base_tags) + extra:
        if not isinstance(t, str) or not t.strip():
            continue
        k = t.strip()
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def _std_item(src: Dict[str, Any], raw: Dict[str, Any]) -> Dict[str, Any]:
    sid = str(src.get("id") or "")
    dt = _parse_date(raw.get("data_publicacao_raw")) or _parse_date_from_url(str(raw.get("link") or ""))
    if not dt and sid == "eurekalert_science_filtered":
        dt = _parse_date_from_eureka_listing_title(str(raw.get("titulo") or ""))
    content_type = _detect_content_type(raw, sid)
    tags = []
    for a in src.get("areas") or []:
        if isinstance(a, str) and a.strip():
            tags.append(a.strip())
    if sid == "iaea_news_publications":
        tags = _iaea_infer_tags(
            f"{raw.get('titulo','')} {raw.get('descricao','')} {raw.get('link','')}",
            tags,
        )
    if sid == "eurekalert_science_filtered":
        fc = raw.get("feed_categories")
        if isinstance(fc, list):
            for c in fc:
                if isinstance(c, str) and c.strip():
                    c2 = c.strip()[:120]
                    if c2 not in tags:
                        tags.append(c2)
    body = _strip_html(raw.get("descricao") or "", max_len=2500)
    desc_fallback_titulo = False
    if sid == "iaea_news_publications" and content_type == "pesquisa" and len(body) < 40:
        tt = re.sub(r"\s+", " ", str(raw.get("titulo") or "").strip())
        if len(tt) >= 40:
            body = tt[:2500]
            desc_fallback_titulo = True
    ita_desc_fallback_titulo = False
    if sid == "ita_projetos" and content_type == "pesquisa" and len(body) < 40:
        tt = re.sub(r"\s+", " ", str(raw.get("titulo") or "").strip())
        if len(tt) >= 40:
            body = tt[:2500]
            ita_desc_fallback_titulo = True
    missing_summary = len(body) < 40
    has_date = bool(_iso_date(dt))
    catalog_pesquisa = (
        sid in _STRATEGIC_MILITARY_PESQUISA_IDS
        or sid in _AFRL_DIRECTORATE_IDS
        or sid in ("afrl_mission_organizations", "ita_lab_guerra_eletronica", "ita_projetos")
    )
    if catalog_pesquisa and content_type == "pesquisa" and missing_summary:
        tt_cat = re.sub(r"\s+", " ", str(raw.get("titulo") or "").strip())
        if len(tt_cat) >= 12:
            body = (body + " " + tt_cat).strip()[:2500]
            missing_summary = len(body) < 40
    if content_type == "pesquisa" and not has_date:
        if catalog_pesquisa and not missing_summary:
            val = "valido"
        elif catalog_pesquisa and len(re.sub(r"\s+", " ", str(raw.get("titulo") or "")).strip()) >= 10:
            val = "valido"
        else:
            val = "incompleto"
    elif missing_summary and not has_date:
        val = "acesso_limitado"
    elif missing_summary:
        val = "incompleto"
    else:
        val = "valido" if has_date else "incompleto"
    q = 40
    if body:
        q = min(95, 55 + min(40, len(body) // 25))
    if has_date:
        q = min(100, q + 5)
    fonte_nome = src.get("name")
    if sid == "iaea_news_publications":
        fonte_rec = "iaea_news_publications"
    elif sid == "eurekalert_science_filtered":
        fonte_rec = "eurekalert_science_filtered"
    elif sid == "defesanet":
        fonte_rec = "defesanet"
    elif sid == "brisa_news":
        fonte_rec = "brisa_news"
    elif sid == "brisa_artigos":
        fonte_rec = "brisa_artigos"
    elif sid == "exercito_brasileiro":
        fonte_rec = "exercito_brasileiro"
    elif sid == "softex_noticias":
        fonte_rec = "softex_noticias"
    elif sid == "ita_projetos":
        fonte_rec = "ita_projetos"
    elif sid == "ita_lab_guerra_eletronica":
        fonte_rec = "ita_lab_guerra_eletronica"
    elif sid == "capes_noticias":
        fonte_rec = "capes_noticias"
    elif sid == "f35_news":
        fonte_rec = "f35_news"
    elif sid == "lockheed_martin_news":
        fonte_rec = "lockheed_martin_news"
    elif sid == "mcti_noticias":
        fonte_rec = "mcti_noticias"
    elif sid == "war_gov_news":
        fonte_rec = "war_gov_news"
    elif sid == "nato_news":
        fonte_rec = "nato_news"
    elif sid in _STRATEGIC_AFRL_IDS:
        fonte_rec = sid
    elif sid in _STRATEGIC_DARPA_IDS:
        fonte_rec = sid
    elif sid in _STRATEGIC_MILITARY_IDS:
        fonte_rec = sid
    else:
        fonte_rec = fonte_nome
    docs: List[Any] = []
    if isinstance(raw.get("documentos"), list):
        docs = [d for d in raw.get("documentos") if isinstance(d, dict)]
    pdf_u = raw.get("pdf_url") if isinstance(raw.get("pdf_url"), str) else None
    io_lang = raw.get("idioma_original") or raw.get("lang")
    idioma = str(io_lang).strip()[:12] if io_lang else "en"
    if (
        sid in ("defesanet", "exercito_brasileiro", "softex_noticias", "capes_noticias")
        or sid in _STRATEGIC_BRISA_IDS
        or sid in _STRATEGIC_ITA_IDS
        or sid in _STRATEGIC_MCTI_IDS
    ):
        idioma = "pt-BR"
    extras: Dict[str, Any] = {
        "source_id": src.get("id"),
        "source_method": raw.get("source_method"),
        "seed_url": raw.get("seed_url"),
        "seed_kind": raw.get("seed_kind"),
        "kind_declared": src.get("kind"),
        "time_window_months": src.get("time_window_months"),
        "content_type": content_type,
        "titulo_original": raw.get("titulo"),
        "descricao_original": raw.get("descricao"),
        "origem_portal": src.get("name"),
        "url_detalhe": raw.get("link"),
        "idioma_original": idioma if idioma else "en",
        "missing_summary": missing_summary,
        "pesquisa_sem_data": bool(content_type == "pesquisa" and not has_date),
        "page_enriched": bool(raw.get("_page_enriched")),
        "iaea_descricao_fallback_titulo": desc_fallback_titulo,
    }
    if sid == "eurekalert_science_filtered":
        extras["eurekalert_filtered"] = True
        extras["matched_keywords"] = list(raw.get("_matched_keywords") or [])
        extras["feed_categories"] = [
            x for x in (raw.get("feed_categories") or []) if isinstance(x, str) and x.strip()
        ][:40]
        if raw.get("fonte_instituicao_raw"):
            extras["instituicao_fonte_original"] = str(raw.get("fonte_instituicao_raw"))[:500]

    imagem_url = raw.get("imagem_url") if isinstance(raw.get("imagem_url"), str) else None
    autor: Optional[str] = None
    categoria: Optional[str] = None
    eixo_estrategico: List[str] = []
    relevancia: Optional[int] = None
    if sid == "defesanet":
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        for c in feed_cats:
            if c not in tags:
                tags.append(c[:120])
        section = _defesanet_section_from_url(str(raw.get("link") or ""))
        blob_def = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _defesanet_infer_eixo(section, feed_cats, blob_def)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = feed_cats[0][:120] if feed_cats else section
        autor = (str(raw.get("autor") or raw.get("fonte_instituicao_raw") or "").strip()[:200] or None)
        relevancia = q
        extras["defesanet_section"] = section
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_rss_sem_artigo_integral"

    if sid == "brisa_news":
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        for c in feed_cats:
            if c not in tags:
                tags.append(c[:120])
        blob_brisa = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _brisa_infer_eixo(feed_cats, blob_brisa)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = feed_cats[0][:120] if feed_cats else "News"
        autor = (str(raw.get("autor") or raw.get("fonte_instituicao_raw") or "").strip()[:200] or None)
        relevancia = q
        extras["brisa_section"] = "news"
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_rss_sem_artigo_integral"

    if sid == "brisa_artigos":
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        for c in feed_cats:
            if c not in tags:
                tags.append(c[:120])
        blob_art = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _brisa_artigos_infer_eixo(feed_cats, blob_art)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        cat0 = feed_cats[0][:120] if feed_cats else "Artigos"
        categoria = "Artigos" if cat0.lower() == "news" else cat0
        autor = (str(raw.get("autor") or raw.get("fonte_instituicao_raw") or "").strip()[:200] or None)
        relevancia = q
        extras["brisa_section"] = "artigos"
        extras["editorial_tipo"] = "artigo"
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_rss_sem_artigo_integral"
        extras["permalink_note"] = "wordpress_slug_raiz_feed_artigos"

    if sid == "exercito_brasileiro":
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        for c in feed_cats:
            if c not in tags:
                tags.append(c[:120])
        blob_eb = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _exercito_brasileiro_infer_eixo(feed_cats, blob_eb)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = feed_cats[0][:120] if feed_cats else "Noticiário do Exército"
        autor = (str(raw.get("autor") or "Exército Brasileiro").strip()[:200] or None)
        relevancia = q
        extras["eb_portal"] = "liferay"
        extras["eb_section"] = "noticiario"
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_meta_sem_artigo_integral"
        if "concurso" in str(raw.get("link") or "").lower():
            extras["sinal_concurso_no_slug"] = True

    if sid == "softex_noticias":
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        for c in feed_cats:
            if c not in tags:
                tags.append(c[:120])
        blob_sx = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _softex_infer_eixo(feed_cats, blob_sx)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = next(
            (c[:120] for c in feed_cats if "notícia" in c.lower() or "noticia" in c.lower()),
            feed_cats[0][:120] if feed_cats else "Notícias",
        )
        autor = (str(raw.get("autor") or raw.get("fonte_instituicao_raw") or "").strip()[:200] or None)
        relevancia = q
        extras["softex_section"] = "noticias"
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_rss_sem_artigo_integral"
        extras["permalink_note"] = "wordpress_slug_raiz_feed_global"

    if sid in _STRATEGIC_ITA_IDS:
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_ita = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _ita_infer_eixo(feed_cats, blob_ita, src_id=sid)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        page_kind = str(raw.get("ita_page_kind") or extras.get("ita_page_kind") or "").strip()
        categoria = feed_cats[0][:120] if feed_cats else ("portal_institucional" if sid == "ita_lab_guerra_eletronica" else "projeto")
        relevancia = q
        extras["ita_cms"] = "drupal"
        extras["ita_page_kind"] = page_kind or (
            "portal_institucional" if sid == "ita_lab_guerra_eletronica" else "projeto_pesquisa"
        )
        extras["ita_http_only"] = True
        extras["feed_categories"] = feed_cats[:25]
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_meta_paragrafo_sem_corpo_integral"
        extras["pesquisa_sem_data_catalogo"] = bool(not has_date)
        if ita_desc_fallback_titulo:
            extras["ita_descricao_fallback_titulo"] = True

    if sid == "capes_noticias":
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_cap = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        categoria = _capes_strategic_categoria(blob_cap)
        eixo_estrategico = _capes_infer_eixo(feed_cats, blob_cap)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        autor = (str(raw.get("autor") or raw.get("fonte_instituicao_raw") or "").strip()[:200] or None)
        relevancia = q
        extras["capes_section"] = "noticias"
        extras["capes_cms"] = "govbr_plone"
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_rss_ou_lead_sem_corpo_integral"

    if sid == "f35_news":
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        for c in feed_cats:
            if c not in tags:
                tags.append(c[:120])
        blob_f35 = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _f35_infer_eixo(feed_cats, blob_f35)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = next(
            (c[:120] for c in feed_cats if c.lower() in ("news", "feature", "news article")),
            feed_cats[0][:120] if feed_cats else "News",
        )
        autor = (str(raw.get("autor") or "F-35").strip()[:200] or None)
        relevancia = q
        extras["f35_feed_json"] = _F35_FEED_PATH
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_feed_json_sem_artigo_integral"

    if sid == "lockheed_martin_news":
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        for c in feed_cats:
            if c not in tags:
                tags.append(c[:120])
        blob_lm = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _lm_infer_eixo(feed_cats, blob_lm)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = str(raw.get("story_type") or feed_cats[0] if feed_cats else "Newsroom")[:120]
        autor = (str(raw.get("autor") or "Lockheed Martin").strip()[:200] or None)
        relevancia = q
        extras["lm_feed_json"] = _LM_FEED_PATH
        extras["lm_story_type"] = raw.get("story_type")
        extras["lm_product"] = raw.get("lm_product")
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_feed_json_sem_artigo_integral"
        extras["filtro_relevancia_tecnica"] = True

    if sid == "mcti_noticias":
        rel = raw.get("_mcti_relevance") if isinstance(raw.get("_mcti_relevance"), dict) else {}
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_mcti = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _mcti_infer_eixo(feed_cats, blob_mcti, list(rel.get("eixos_detectados") or []))
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = eixo_estrategico[0] if eixo_estrategico else "ciencia_tecnologia"
        autor = (str(raw.get("autor") or "MCTI").strip()[:200] or None)
        relevancia = q
        extras["mcti_cms"] = "govbr_plone"
        extras["relevancia_mcti"] = rel.get("relevancia_mcti") or "media"
        extras["motivos_relevancia"] = list(rel.get("motivos_relevancia") or [])[:20]
        extras["motivos_descarte"] = list(rel.get("motivos_descarte") or [])[:15]
        extras["possivel_edital"] = bool(rel.get("possivel_edital"))
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_lead_og_sem_corpo_integral"
        extras["filtro_relevancia_mcti"] = True

    if sid == "war_gov_news":
        rel_w = raw.get("_war_gov_relevance") if isinstance(raw.get("_war_gov_relevance"), dict) else {}
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_w = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _war_gov_infer_eixo(blob_w, list(rel_w.get("eixos_detectados") or []))
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        sec = str(rel_w.get("war_gov_section") or raw.get("war_gov_section") or "news_stories")
        categoria = "News Stories" if sec == "news_stories" else ("Features" if sec == "features" else sec)
        autor = (str(raw.get("autor") or "U.S. Department of Defense").strip()[:200] or None)
        relevancia = q
        extras["war_gov_section"] = sec
        extras["relevancia_war_gov"] = rel_w.get("relevancia_war_gov") or "media"
        extras["motivos_relevancia"] = list(rel_w.get("motivos_relevancia") or [])[:20]
        extras["motivos_descarte"] = list(rel_w.get("motivos_descarte") or [])[:15]
        extras["possivel_procurement"] = bool(rel_w.get("possivel_procurement"))
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_rss_oficial_sem_corpo_integral"
        extras["filtro_relevancia_war_gov"] = True
        extras["fonte_oficial_governamental"] = True

    if sid == "nato_news":
        rel_n = raw.get("_nato_relevance") if isinstance(raw.get("_nato_relevance"), dict) else {}
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_n = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _nato_infer_eixo(blob_n, list(rel_n.get("eixos_detectados") or []))
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        sec_n = str(rel_n.get("nato_section") or raw.get("nato_section") or "news")
        categoria = "News" if sec_n == "news" else sec_n
        autor = (str(raw.get("autor") or "NATO").strip()[:200] or None)
        relevancia = q
        extras["nato_section"] = sec_n
        extras["relevancia_nato"] = rel_n.get("relevancia_nato") or "media"
        extras["motivos_relevancia"] = list(rel_n.get("motivos_relevancia") or [])[:20]
        extras["motivos_descarte"] = list(rel_n.get("motivos_descarte") or [])[:15]
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_model_json_ou_og_sem_corpo_integral"
        extras["filtro_relevancia_nato"] = True
        extras["fonte_oficial_internacional"] = True
        extras["listing_method"] = "nato_sitemap_aem"

    if sid == "afrl_news":
        rel_a = raw.get("_afrl_relevance") if isinstance(raw.get("_afrl_relevance"), dict) else {}
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_a = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _afrl_infer_eixo(blob_a, list(rel_a.get("eixos_detectados") or []))
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = feed_cats[0][:120] if feed_cats else "News"
        autor = (str(raw.get("autor") or "AFRL").strip()[:200] or None)
        relevancia = q
        extras["afrl_route"] = "news"
        extras["relevancia_afrl"] = rel_a.get("relevancia_afrl") or "media"
        extras["motivos_relevancia"] = list(rel_a.get("motivos_relevancia") or [])[:20]
        extras["motivos_descarte"] = list(rel_a.get("motivos_descarte") or [])[:15]
        extras["possivel_edital"] = bool(rel_a.get("possivel_edital"))
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_listing_ou_og_sem_corpo_integral"
        extras["filtro_relevancia_afrl"] = True
        extras["fonte_oficial_governamental"] = True
        extras["listing_method"] = "afrl_news_listing_html"

    if sid == "afrl_mission_organizations":
        rel_m = raw.get("_afrl_relevance") if isinstance(raw.get("_afrl_relevance"), dict) else {}
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_m = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _afrl_infer_eixo(blob_m, list(rel_m.get("eixos_detectados") or []))
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = str(raw.get("afrl_org_slug") or "mission_organization")[:120]
        relevancia = q
        extras["afrl_route"] = "mission"
        extras["afrl_org_slug"] = raw.get("afrl_org_slug")
        extras["afrl_page_kind"] = raw.get("afrl_page_kind") or "centro_pesquisa"
        extras["relevancia_afrl"] = rel_m.get("relevancia_afrl") or "media"
        extras["motivos_relevancia"] = list(rel_m.get("motivos_relevancia") or [])[:20]
        extras["feed_categories"] = feed_cats[:25]
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_meta_organizacao_sem_corpo_integral"
        extras["catalogo_institucional"] = True
        extras["pesquisa_sem_data_catalogo"] = True
        extras["listing_method"] = "afrl_mission_organizations_html"

    if sid in _AFRL_DIRECTORATE_IDS:
        hl_ex = raw.get("_afrl_highlights_extras") if isinstance(raw.get("_afrl_highlights_extras"), list) else []
        cfg_d = _AFRL_DIRECTORATE_CONFIG.get(sid) or {}
        blob_d = f"{raw.get('titulo','')} {' '.join(str(c.get('titulo') or '') for c in hl_ex)}"
        eixo_estrategico = _afrl_infer_eixo(blob_d, list(cfg_d.get("area_tecnologica") or []))
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        extras["afrl_route"] = "directorate"
        extras["afrl_directorate_code"] = raw.get("afrl_directorate_code") or cfg_d.get("code")
        extras["highlights"] = hl_ex[:80]
        extras["highlights_total"] = len(hl_ex)
        extras["catalogo_institucional"] = True
        extras["pesquisa_sem_data_catalogo"] = True
        extras["listing_method"] = raw.get("source_method") or "afrl_directorate_html"
        extras["afrl_fetch_mode"] = raw.get("_afrl_fetch_mode")
        extras["area_tecnologica"] = list(cfg_d.get("area_tecnologica") or [])
        extras["setor_estrategico"] = list(cfg_d.get("setor_estrategico") or [])
        if raw.get("_afrl_possivel_edital_institutional"):
            extras["possivel_edital"] = True
            extras["destino_sugerido"] = "Radar/Editais"

    if sid == "afrl_mission_highlights":
        rel_h = raw.get("_afrl_relevance") if isinstance(raw.get("_afrl_relevance"), dict) else {}
        blob_h = f"{raw.get('titulo','')} {body}"
        eixo_estrategico = _afrl_infer_eixo(blob_h, list(rel_h.get("eixos_detectados") or []))
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        extras["afrl_route"] = "mission_highlight"
        extras["diretoria_origem"] = raw.get("diretoria_origem")
        extras["read_more_label"] = raw.get("read_more_label") or "Read More"
        extras["relevancia_afrl"] = rel_h.get("relevancia_afrl") or "media"
        extras["motivos_relevancia"] = list(rel_h.get("motivos_relevancia") or [])[:20]
        extras["motivos_descarte"] = list(rel_h.get("motivos_descarte") or [])[:15]
        extras["possivel_edital"] = bool(rel_h.get("possivel_edital"))
        extras["eixo_estrategico"] = eixo_estrategico
        extras["filtro_relevancia_afrl"] = True
        extras["fonte_oficial_governamental"] = True
        extras["listing_method"] = "afrl_mission_highlights"
        if rel_h.get("possivel_edital"):
            extras["destino_sugerido"] = "Radar/Editais"

    if sid in _STRATEGIC_MILITARY_NEWS_IDS:
        rel_mil = raw.get("_military_relevance") if isinstance(raw.get("_military_relevance"), dict) else {}
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_mil = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        from scripts.news_research import military_af_research as mil

        eixo_estrategico = mil.military_infer_eixo(
            sid, blob_mil, list(rel_mil.get("eixos_detectados") or [])
        )
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        display = _STRATEGIC_DISPLAY_FONTES.get(sid) or "U.S. DoD"
        categoria = feed_cats[0][:120] if feed_cats else "News"
        autor = (str(raw.get("autor") or display).strip()[:200] or None)
        relevancia = q
        extras["military_route"] = "news"
        extras["relevancia_military"] = rel_mil.get("relevancia_afrl") or "media"
        extras["motivos_relevancia"] = list(rel_mil.get("motivos_relevancia") or [])[:20]
        extras["motivos_descarte"] = list(rel_mil.get("motivos_descarte") or [])[:15]
        extras["possivel_edital"] = bool(rel_mil.get("possivel_edital"))
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_listing_ou_og_sem_corpo_integral"
        extras["filtro_relevancia_military"] = True
        extras["fonte_oficial_governamental"] = True
        extras["listing_method"] = raw.get("source_method") or "dod_afmil_news_listing_html"
        if rel_mil.get("possivel_edital"):
            extras["destino_sugerido"] = "Radar/Editais"
        if sid == "arl_news":
            extras["relevancia_arl"] = rel_mil.get("relevancia_arl") or "media"
            extras["filtro_relevancia_arl"] = True

    if sid in _STRATEGIC_MILITARY_PESQUISA_IDS:
        from scripts.news_research import military_af_research as mil

        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_p = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = mil.military_infer_eixo(sid, blob_p, list(raw.get("area_tecnologica") or []))
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        extras["feed_categories"] = feed_cats[:25]
        extras["eixo_estrategico"] = eixo_estrategico
        extras["tipo_pesquisa"] = raw.get("tipo_pesquisa") or (
            "area_tecnologica" if sid == "afrl_technology_areas" else "portal_institucional"
        )
        extras["tipo_recurso"] = raw.get("tipo_recurso") or (
            "area_tecnologica" if sid == "afrl_technology_areas" else "portal_estrategico"
        )
        extras["tipo_oportunidade"] = "pesquisa_estrategica"
        extras["catalogo_institucional"] = not bool(raw.get("data_publicacao_raw"))
        extras["pesquisa_sem_data_catalogo"] = not bool(raw.get("data_publicacao_raw"))
        extras["listing_method"] = raw.get("source_method")
        if raw.get("_possivel_edital") or raw.get("_portal_cards"):
            extras["possivel_edital"] = bool(raw.get("_possivel_edital"))
            if raw.get("_portal_cards"):
                extras["portal_cards"] = raw.get("_portal_cards")
            if raw.get("_possivel_edital"):
                extras["destino_sugerido"] = "Radar/Editais"
        if sid == "afrl_technology_areas":
            extras["afrl_tech_slug"] = raw.get("afrl_tech_slug")
            extras["area_tecnologica"] = list(raw.get("area_tecnologica") or extras.get("eixo_estrategico") or [])
        if sid == "arl_resources":
            extras["arl_resource_class"] = raw.get("arl_resource_class") or (
                "institucional_latente" if raw.get("_institucional_latente") else "recurso_pesquisa"
            )
            if raw.get("_destino_sugerido"):
                extras["destino_sugerido"] = raw.get("_destino_sugerido")
        if sid in ("afnwc_innovation", "afnwc_weapon_systems"):
            extras["setor_estrategico"] = list(raw.get("setor_estrategico") or ["defesa", "nuclear"])[:8]
            if sid == "afnwc_weapon_systems":
                extras["tipo_recurso"] = "sistema_estrategico"

    if sid in _STRATEGIC_DARPA_IDS:
        fc = raw.get("feed_categories") if isinstance(raw.get("feed_categories"), list) else []
        feed_cats = [str(c).strip() for c in fc if isinstance(c, str) and str(c).strip()]
        blob_d = f"{raw.get('titulo','')} {body} {' '.join(feed_cats)}"
        eixo_estrategico = _darpa_infer_eixo(blob_d)
        for e in eixo_estrategico:
            if e not in tags:
                tags.append(e)
        categoria = (
            "research_program"
            if sid == "darpa_programs_research"
            else ("opportunity" if sid == "darpa_opportunities_research" else "news")
        )
        autor = (str(raw.get("autor") or "DARPA").strip()[:200] or None)
        relevancia = q
        rel_d = raw.get("_darpa_relevance") if isinstance(raw.get("_darpa_relevance"), dict) else {}
        extras["darpa_route"] = sid
        extras["feed_categories"] = feed_cats[:25]
        extras["autor"] = autor
        extras["categoria"] = categoria
        extras["eixo_estrategico"] = eixo_estrategico
        extras["relevancia"] = relevancia
        extras["copyright_note"] = "resumo_rss_ou_lead_sem_corpo_integral"
        if rel_d:
            extras["motivos_relevancia"] = rel_d.get("motivos_relevancia")
            extras["motivos_descarte"] = rel_d.get("motivos_descarte")
        if sid == "darpa_programs_research":
            extras["darpa_program_slug"] = raw.get("darpa_program_slug")
            extras["listing_method"] = "sitemap_programs"
            extras["tipo_pesquisa"] = "programa_pesquisa"
            extras["tipo_recurso"] = "programa_estrategico"
            extras["tipo_oportunidade"] = "pesquisa_estrategica"
        if sid == "darpa_opportunities_research":
            extras["tipo_oportunidade"] = _infer_darpa_opportunity_type(str(raw.get("titulo") or ""))
            extras["review_for_edital"] = True
            extras["darpa_opp_canonical"] = True

    display_fonte = _STRATEGIC_DISPLAY_FONTES.get(sid) or (
        "BRISA" if sid in _STRATEGIC_BRISA_IDS else fonte_nome
    )

    row: Dict[str, Any] = {
        "titulo": raw.get("titulo"),
        "resumo": body or None,
        "descricao": body or None,
        "link": raw.get("link"),
        "fonte": display_fonte,
        "fonte_recurso": fonte_rec,
        "data_publicacao": _iso_date(dt),
        "pais": src.get("country"),
        "regiao": src.get("region"),
        "idioma_original": idioma if idioma else "en",
        "tipo_conteudo": content_type,
        "tipo_pesquisa": (
            "programa_pesquisa"
            if sid == "darpa_programs_research"
            else (
                "artigo"
                if sid == "brisa_artigos"
                else (
                    "portal_institucional"
                    if sid == "ita_lab_guerra_eletronica"
                    else (
                        "projeto_pesquisa"
                        if sid == "ita_projetos"
                        else (
                            "centro_pesquisa"
                            if sid == "afrl_mission_organizations"
                            else (
                                _AFRL_DIRECTORATE_CONFIG.get(sid, {}).get("tipo_pesquisa")
                                if sid in _AFRL_DIRECTORATE_IDS
                                else (
                                    raw.get("tipo_pesquisa")
                                    if sid in _STRATEGIC_MILITARY_PESQUISA_IDS
                                    else ("relatorio_tecnico" if content_type == "pesquisa" else None)
                                )
                            )
                        )
                    )
                )
            )
        ),
        "area_cientifica": [a for a in tags if a in ("ciencia_tecnologia", "fisica", "nuclear", "medicina")],
        "area_tecnologica": [a for a in tags if a not in ("fisica",)],
        "setor_estrategico": [a for a in tags if a in ("defesa", "nuclear", "aeroespacial", "industria_estrategica")],
        "tags": tags,
        "imagem_url": imagem_url,
        "documentos": docs,
        "pdf_url": pdf_u,
        "qualidade_dado": q,
        "validacao_status": val,
        "extras": extras,
    }
    if sid == "darpa_programs_research":
        row["tipo_recurso"] = "programa_estrategico"
        row["tipo_oportunidade"] = "pesquisa_estrategica"
    if sid == "afrl_mission_organizations":
        row["tipo_recurso"] = "organizacao_pesquisa"
        row["tipo_oportunidade"] = "pesquisa_estrategica"
    if sid in _AFRL_DIRECTORATE_IDS:
        cfg_dr = _AFRL_DIRECTORATE_CONFIG.get(sid) or {}
        row["tipo_recurso"] = cfg_dr.get("tipo_recurso") or "organizacao_pesquisa"
        row["tipo_oportunidade"] = "pesquisa_estrategica"
    if sid in _STRATEGIC_MILITARY_PESQUISA_IDS:
        row["tipo_recurso"] = (
            raw.get("tipo_recurso")
            or ("area_tecnologica" if sid == "afrl_technology_areas" else "portal_estrategico")
        )
        row["tipo_oportunidade"] = "pesquisa_estrategica"
        areas = raw.get("area_tecnologica")
        if isinstance(areas, list) and areas:
            row["area_tecnologica"] = [str(a) for a in areas if a][:12]
        row["setor_estrategico"] = list(raw.get("setor_estrategico") or ["defesa", "aeroespacial"])[:8]
    if (
        sid in ("defesanet", "exercito_brasileiro", "softex_noticias", "f35_news", "lockheed_martin_news")
        or sid in _STRATEGIC_BRISA_IDS
        or sid in _STRATEGIC_ITA_IDS
        or sid in _STRATEGIC_CAPES_IDS
        or sid in _STRATEGIC_MCTI_IDS
        or sid in _STRATEGIC_WAR_GOV_IDS
        or sid in _STRATEGIC_NATO_IDS
        or sid in _STRATEGIC_AFRL_IDS
        or sid in _STRATEGIC_DARPA_IDS
        or sid in _STRATEGIC_MILITARY_IDS
    ):
        row["autor"] = autor
        row["categoria"] = categoria
        row["eixo_estrategico"] = eixo_estrategico
        row["relevancia"] = relevancia
    return row


def crawl_source(src: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    max_items = int(src.get("max_items") or 30)
    tw = int(src.get("time_window_months") or 12)
    min_dt = _now_utc() - timedelta(days=30 * tw)
    raw_items: List[Dict[str, Any]] = []
    standardized: List[Dict[str, Any]] = []
    seen = set()
    errors = []
    lm_review: List[Dict[str, Any]] = []
    mcti_review: List[Dict[str, Any]] = []
    mcti_discard: List[Dict[str, Any]] = []
    mcti_pre_relevance: List[Dict[str, Any]] = []
    war_gov_review: List[Dict[str, Any]] = []
    war_gov_discard: List[Dict[str, Any]] = []
    war_gov_pre_relevance: List[Dict[str, Any]] = []
    nato_review: List[Dict[str, Any]] = []
    nato_discard: List[Dict[str, Any]] = []
    nato_pre_relevance: List[Dict[str, Any]] = []
    afrl_review: List[Dict[str, Any]] = []
    afrl_discard: List[Dict[str, Any]] = []
    afrl_pre_relevance: List[Dict[str, Any]] = []
    afrl_opp_review: List[Dict[str, Any]] = []
    military_review: List[Dict[str, Any]] = []
    military_discard: List[Dict[str, Any]] = []
    military_pre_relevance: List[Dict[str, Any]] = []
    military_opp_review: List[Dict[str, Any]] = []

    filter_stats: Dict[str, Any] = {
        "rejected_lm_routing": 0,
        "lm_sent_review": 0,
        "rejected_mcti_non_path": 0,
        "mcti_sent_review": 0,
        "mcti_sent_discard": 0,
        "extracted_total": 0,
        "skipped_duplicate_link": 0,
        "rejected_exclude_keyword": 0,
        "rejected_exclude_medical_generic": 0,
        "rejected_require_any_keyword": 0,
        "rejected_feed_kind_cap": 0,
        "passed_theme_filters": 0,
        "matched_keyword_counts": {},
        "reject_samples": [],
    }

    plan = _seed_plan(src)
    if not plan:
        plan = [(str(s).strip(), "mixed") for s in (src.get("seed_urls") or []) if str(s).strip()]

    sid0 = str(src.get("id") or "")
    kind_counts: Dict[str, int] = {}
    feed_caps: Dict[str, Any] = src.get("feed_kind_caps") if isinstance(src.get("feed_kind_caps"), dict) else {}

    for seed, seed_kind in plan:
        if len(raw_items) >= max_items:
            break
        extracted: List[Dict[str, Any]]
        if sid0 == "darpa_programs_research":
            extracted = _extract_darpa_programs_sitemap(max_items=max_items, min_dt=min_dt)
        elif sid0 == "nato_news":
            extracted = _extract_nato_news_sitemap(max_items=max_items, min_dt=min_dt)
        elif sid0 == "afrl_news":
            extracted = _crawl_afrl_news_listing(max_items=max_items, min_dt=min_dt)
        elif sid0 in _AFRL_DIRECTORATE_IDS:
            extracted, hl_meta = _crawl_afrl_directorate_institutional(sid0)
            filter_stats["afrl_highlights_captured"] = len(hl_meta)
            filter_stats["afrl_highlights_with_date"] = sum(
                1 for h in hl_meta if _parse_date(h.get("data_publicacao_raw"))
            )
        elif sid0 == "afrl_mission_highlights":
            extracted = _crawl_afrl_mission_highlights(max_items=max_items, min_dt=min_dt)
        elif sid0 in _STRATEGIC_MILITARY_NEWS_IDS and sid0 != "arl_news":
            from scripts.news_research import military_af_research as mil

            extracted = mil.crawl_dod_afmil_news_listing(sid0, max_items=max_items, min_dt=min_dt)
        elif sid0 == "arl_news":
            from scripts.news_research import military_af_research as mil

            extracted = mil.crawl_arl_media_center_news(max_items=max_items, min_dt=min_dt)
        elif sid0 == "afrl_technology_areas":
            from scripts.news_research import military_af_research as mil

            extracted = mil.crawl_afrl_technology_areas(max_items=max_items)
        elif sid0 in ("afnwc_innovation", "afnwc_weapon_systems"):
            from scripts.news_research import military_af_research as mil

            extracted = mil.crawl_afnwc_portal(sid0, max_items=max_items)
        elif sid0 == "arl_resources":
            from scripts.news_research import military_af_research as mil

            extracted = mil.crawl_arl_resources(max_items=max_items)
        elif sid0 == "afrl_mission_organizations":
            hub = str(seed or _AFRL_MISSION_HUB)
            resp_m, mo_mode = _afrl_http_get(hub, timeout=60)
            extracted = []
            if resp_m:
                extracted = _extract_afrl_mission_organizations(
                    hub, resp_m.text or "", max_items=max_items
                )
            if not extracted:
                extracted = _afrl_mission_static_fallback(max_items)
                if extracted:
                    filter_stats["afrl_mission_static_fallback"] = len(extracted)
            if not extracted and not resp_m:
                errors.append({"seed": seed, "error": "fetch_failed"})
            elif mo_mode == "wayback" and extracted:
                filter_stats["afrl_mission_wayback"] = True
        else:
            resp = _http_get(str(seed))
            if not resp:
                errors.append({"seed": seed, "error": "fetch_failed"})
                continue
            body = resp.text or ""
            if _looks_like_feed_xml(body):
                extracted = _extract_feed_items(str(seed), body)
                if sid0 == "capes_noticias":
                    extracted = _rss_items_newest_first(extracted)
            elif sid0 == "exercito_brasileiro":
                extracted = _extract_eb_noticias_listing(str(seed), body, max_items=max_items)
            elif sid0 == "ita_projetos":
                extracted = _extract_ita_projetos_listing(str(seed), body, max_items=max_items)
            elif sid0 == "ita_lab_guerra_eletronica":
                extracted = _extract_ita_institutional_portal(str(seed), body)
            elif sid0 == "f35_news":
                extracted = _extract_f35_news_json(
                    str(seed), body, max_items=max_items, min_dt=min_dt
                )
            elif sid0 == "lockheed_martin_news":
                extracted = _extract_lockheed_martin_news_json(
                    str(seed), body, max_items=max_items, min_dt=min_dt
                )
            elif sid0 == "mcti_noticias":
                extracted = _extract_mcti_noticias_listing(str(seed), body, max_items=max_items)
            else:
                extracted = _extract_listing_items(str(seed), body, max_items=max_items)
                if len(extracted) < max(5, max_items // 6):
                    for rss in _discover_rss_links(str(seed), body):
                        rr = _http_get(rss)
                        if not rr:
                            continue
                        if not _looks_like_feed_xml(rr.text or ""):
                            continue
                        extracted.extend(_extract_feed_items(rss, rr.text or ""))
                        if len(extracted) >= max_items:
                            break
        for r in extracted:
            filter_stats["extracted_total"] += 1
            lk = str(r.get("link") or "").strip()
            if not lk:
                continue
            if sid0 == "brisa_news" and "/news/" not in lk.lower():
                filter_stats["rejected_brisa_non_news_path"] = (
                    int(filter_stats.get("rejected_brisa_non_news_path") or 0) + 1
                )
                continue
            if sid0 == "brisa_artigos" and "/news/" in lk.lower():
                filter_stats["rejected_brisa_artigos_news_path"] = (
                    int(filter_stats.get("rejected_brisa_artigos_news_path") or 0) + 1
                )
                continue
            if sid0 == "exercito_brasileiro" and _EB_NOTICIA_PATH not in lk.lower():
                filter_stats["rejected_eb_non_noticia_path"] = (
                    int(filter_stats.get("rejected_eb_non_noticia_path") or 0) + 1
                )
                continue
            if sid0 == "softex_noticias" and "softex.br" not in lk.lower():
                filter_stats["rejected_softex_non_domain"] = (
                    int(filter_stats.get("rejected_softex_non_domain") or 0) + 1
                )
                continue
            if sid0 == "ita_projetos" and not _normalize_ita_projetos_link(lk, lk):
                filter_stats["rejected_ita_non_projeto_path"] = (
                    int(filter_stats.get("rejected_ita_non_projeto_path") or 0) + 1
                )
                continue
            if sid0 == "ita_lab_guerra_eletronica" and "/laboratorios/guerraeletronica" not in lk.lower():
                filter_stats["rejected_ita_non_lab_ge_path"] = (
                    int(filter_stats.get("rejected_ita_non_lab_ge_path") or 0) + 1
                )
                continue
            if sid0 == "lockheed_martin_news":
                lm_action, lm_why = _lm_classify_for_pipeline(r)
                if lm_action == "reject":
                    filter_stats["rejected_lm_routing"] = (
                        int(filter_stats.get("rejected_lm_routing") or 0) + 1
                    )
                    if len(filter_stats["reject_samples"]) < 24:
                        filter_stats["reject_samples"].append(
                            {
                                "link": lk[:800],
                                "titulo": (str(r.get("titulo") or ""))[:220],
                                "excluded_reason": lm_why,
                            }
                        )
                    continue
                if lm_action == "review":
                    filter_stats["lm_sent_review"] = int(filter_stats.get("lm_sent_review") or 0) + 1
                    lm_review.append(
                        {
                            "titulo": r.get("titulo"),
                            "link": lk,
                            "data_publicacao_raw": r.get("data_publicacao_raw"),
                            "story_type": r.get("story_type"),
                            "descricao": (str(r.get("descricao") or ""))[:500],
                            "review_reason": lm_why,
                            "routing": "review_ambiguous_noticia",
                        }
                    )
                    continue
            if sid0 == "mcti_noticias" and not _normalize_mcti_noticia_link(lk, lk):
                filter_stats["rejected_mcti_non_path"] = (
                    int(filter_stats.get("rejected_mcti_non_path") or 0) + 1
                )
                continue
            if sid0 == "war_gov_news":
                ok_wg, wg_why = _war_gov_url_allowed(lk)
                if not ok_wg:
                    filter_stats["rejected_war_gov_path"] = (
                        int(filter_stats.get("rejected_war_gov_path") or 0) + 1
                    )
                    if len(filter_stats["reject_samples"]) < 24:
                        filter_stats["reject_samples"].append(
                            {
                                "link": lk[:800],
                                "titulo": (str(r.get("titulo") or ""))[:220],
                                "excluded_reason": wg_why,
                            }
                        )
                    continue
                r["war_gov_section"] = wg_why
            if sid0 == "nato_news":
                ok_nato, nato_why = _nato_url_allowed(lk)
                if not ok_nato:
                    filter_stats["rejected_nato_path"] = (
                        int(filter_stats.get("rejected_nato_path") or 0) + 1
                    )
                    if len(filter_stats["reject_samples"]) < 24:
                        filter_stats["reject_samples"].append(
                            {
                                "link": lk[:800],
                                "titulo": (str(r.get("titulo") or ""))[:220],
                                "excluded_reason": nato_why,
                            }
                        )
                    continue
                r["nato_section"] = nato_why
            if sid0 == "afrl_news" and not _afrl_normalize_article_link(lk, lk):
                filter_stats["rejected_afrl_non_news_path"] = (
                    int(filter_stats.get("rejected_afrl_non_news_path") or 0) + 1
                )
                continue
            if sid0 in _STRATEGIC_MILITARY_NEWS_IDS and sid0 != "arl_news":
                from scripts.news_research import military_af_research as mil

                dom = str((mil._DOD_AFMIL_SITES.get(sid0) or {}).get("domain") or "")
                if dom and dom not in lk.lower():
                    filter_stats["rejected_military_non_domain"] = (
                        int(filter_stats.get("rejected_military_non_domain") or 0) + 1
                    )
                    continue
                if not mil._normalize_dod_article_link(lk, lk, dom):
                    filter_stats["rejected_military_non_news_path"] = (
                        int(filter_stats.get("rejected_military_non_news_path") or 0) + 1
                    )
                    continue
            if sid0 == "arl_news" and "arl.devcom.army.mil" not in lk.lower():
                filter_stats["rejected_arl_non_domain"] = (
                    int(filter_stats.get("rejected_arl_non_domain") or 0) + 1
                )
                continue
            if sid0 == "afrl_mission_organizations":
                ok_mo, mo_why = _afrl_mission_link_allowed(lk)
                if not ok_mo:
                    filter_stats["rejected_afrl_mission_path"] = (
                        int(filter_stats.get("rejected_afrl_mission_path") or 0) + 1
                    )
                    continue
                r["afrl_org_slug"] = mo_why
            if sid0 == "darpa_opportunities_research":
                r["link"] = _normalize_darpa_opportunity_link(r)[:800]
                lk = str(r.get("link") or "").strip()
            if sid0 == "darpa_news" and "darpa.mil/news/" not in lk.lower():
                filter_stats["rejected_darpa_non_news_path"] = (
                    int(filter_stats.get("rejected_darpa_non_news_path") or 0) + 1
                )
                continue
            if lk in seen:
                filter_stats["skipped_duplicate_link"] += 1
                continue
            ok, matched_kws, excl = _apply_source_filters(src, r)
            if not ok:
                if excl == "require_any_keyword_no_match":
                    filter_stats["rejected_require_any_keyword"] += 1
                elif excl and str(excl).startswith("exclude_keyword"):
                    filter_stats["rejected_exclude_keyword"] += 1
                    if _exclude_reason_is_medical_generic(excl):
                        filter_stats["rejected_exclude_medical_generic"] += 1
                if len(filter_stats["reject_samples"]) < 24:
                    filter_stats["reject_samples"].append(
                        {
                            "link": lk[:800],
                            "titulo": (str(r.get("titulo") or ""))[:220],
                            "excluded_reason": excl,
                        }
                    )
                continue
            if sid0 == "iaea_news_publications" and feed_caps.get(seed_kind) is not None:
                lim = int(feed_caps[seed_kind])
                if kind_counts.get(seed_kind, 0) >= lim:
                    filter_stats["rejected_feed_kind_cap"] += 1
                    continue
            seen.add(lk)
            r["seed_url"] = seed
            r["seed_kind"] = seed_kind
            r["_matched_keywords"] = matched_kws
            for mk in matched_kws:
                kc = filter_stats["matched_keyword_counts"]
                kc[mk] = kc.get(mk, 0) + 1
            filter_stats["passed_theme_filters"] += 1
            kind_counts[seed_kind] = kind_counts.get(seed_kind, 0) + 1
            raw_items.append(r)
            if len(raw_items) >= max_items:
                break
        time.sleep(
            0.35
            if sid0 in ("exercito_brasileiro", "ita_projetos", "ita_lab_guerra_eletronica", "mcti_noticias")
            else 0.2
        )

    enrich_max = int(src.get("page_enrich_max") or 25)
    enrich_budget = {"n": 0, "max": enrich_max}
    for r in raw_items:
        _maybe_enrich_from_page(r, enrich_budget, src_id=sid0)

    discarded_post_filter: List[Dict[str, Any]] = []
    raw_filter_fn = _STRATEGIC_NEWS_RAW_FILTERS.get(sid0)
    if raw_filter_fn:
        kept: List[Dict[str, Any]] = []
        for r in raw_items:
            ok, why = raw_filter_fn(r)
            if ok:
                kept.append(r)
            else:
                discarded_post_filter.append(
                    {
                        "link": str(r.get("link") or "")[:800],
                        "titulo": str(r.get("titulo") or "")[:200],
                        "motivo": why,
                    }
                )
        raw_items = kept

    if sid0 == "mcti_noticias" and raw_items:
        mcti_pre_relevance = [dict(r) for r in raw_items]
        kept_mcti: List[Dict[str, Any]] = []
        for r in raw_items:
            action, rel_meta = _mcti_evaluate_relevance(r)
            r["_mcti_relevance"] = rel_meta
            r["_mcti_action"] = action
            entry = {
                "titulo": r.get("titulo"),
                "link": str(r.get("link") or "")[:800],
                "data_publicacao_raw": r.get("data_publicacao_raw"),
                "descricao": (str(r.get("descricao") or ""))[:600],
                "relevancia_mcti": rel_meta.get("relevancia_mcti"),
                "motivos_relevancia": rel_meta.get("motivos_relevancia"),
                "motivos_descarte": rel_meta.get("motivos_descarte"),
                "possivel_edital": rel_meta.get("possivel_edital"),
                "eixos_detectados": rel_meta.get("eixos_detectados"),
                "motivo": rel_meta.get("motivo"),
            }
            if action == "discard":
                filter_stats["mcti_sent_discard"] = int(filter_stats.get("mcti_sent_discard") or 0) + 1
                mcti_discard.append({**entry, "routing": "descartado_ruido"})
            elif action == "review":
                filter_stats["mcti_sent_review"] = int(filter_stats.get("mcti_sent_review") or 0) + 1
                mcti_review.append({**entry, "routing": "review_relevancia"})
            else:
                kept_mcti.append(r)
        raw_items = kept_mcti

    if sid0 == "war_gov_news" and raw_items:
        war_gov_pre_relevance = [dict(r) for r in raw_items]
        kept_wg: List[Dict[str, Any]] = []
        for r in raw_items:
            action, rel_meta = _war_gov_evaluate_relevance(r)
            r["_war_gov_relevance"] = rel_meta
            r["_war_gov_action"] = action
            entry = {
                "titulo": r.get("titulo"),
                "link": str(r.get("link") or "")[:800],
                "data_publicacao_raw": r.get("data_publicacao_raw"),
                "descricao": (str(r.get("descricao") or ""))[:600],
                "war_gov_section": rel_meta.get("war_gov_section"),
                "relevancia_war_gov": rel_meta.get("relevancia_war_gov"),
                "motivos_relevancia": rel_meta.get("motivos_relevancia"),
                "motivos_descarte": rel_meta.get("motivos_descarte"),
                "possivel_procurement": rel_meta.get("possivel_procurement"),
                "eixos_detectados": rel_meta.get("eixos_detectados"),
                "motivo": rel_meta.get("motivo"),
            }
            if action == "discard":
                filter_stats["war_gov_sent_discard"] = int(filter_stats.get("war_gov_sent_discard") or 0) + 1
                war_gov_discard.append({**entry, "routing": "descartados_ruido"})
            elif action == "review":
                filter_stats["war_gov_sent_review"] = int(filter_stats.get("war_gov_sent_review") or 0) + 1
                war_gov_review.append({**entry, "routing": "review_relevancia"})
            else:
                kept_wg.append(r)
        raw_items = kept_wg

    if sid0 == "nato_news" and raw_items:
        nato_pre_relevance = [dict(r) for r in raw_items]
        kept_nato: List[Dict[str, Any]] = []
        for r in raw_items:
            action, rel_meta = _nato_evaluate_relevance(r)
            r["_nato_relevance"] = rel_meta
            r["_nato_action"] = action
            entry = {
                "titulo": r.get("titulo"),
                "link": str(r.get("link") or "")[:800],
                "data_publicacao_raw": r.get("data_publicacao_raw"),
                "descricao": (str(r.get("descricao") or ""))[:600],
                "nato_section": rel_meta.get("nato_section"),
                "relevancia_nato": rel_meta.get("relevancia_nato"),
                "motivos_relevancia": rel_meta.get("motivos_relevancia"),
                "motivos_descarte": rel_meta.get("motivos_descarte"),
                "eixos_detectados": rel_meta.get("eixos_detectados"),
                "motivo": rel_meta.get("motivo"),
            }
            if action == "discard":
                filter_stats["nato_sent_discard"] = int(filter_stats.get("nato_sent_discard") or 0) + 1
                nato_discard.append({**entry, "routing": "descartados_ruido"})
            elif action == "review":
                filter_stats["nato_sent_review"] = int(filter_stats.get("nato_sent_review") or 0) + 1
                nato_review.append({**entry, "routing": "review_relevancia"})
            else:
                kept_nato.append(r)
        raw_items = kept_nato

    if sid0 in ("afrl_news", "afrl_mission_highlights") and raw_items:
        afrl_pre_relevance = [dict(r) for r in raw_items]
        kept_afrl: List[Dict[str, Any]] = []
        for r in raw_items:
            route = "highlight" if sid0 == "afrl_mission_highlights" else "news"
            action, rel_meta = _afrl_evaluate_relevance(r, route=route)
            r["_afrl_relevance"] = rel_meta
            r["_afrl_action"] = action
            entry = {
                "titulo": r.get("titulo"),
                "link": str(r.get("link") or "")[:800],
                "data_publicacao_raw": r.get("data_publicacao_raw"),
                "descricao": (str(r.get("descricao") or ""))[:600],
                "relevancia_afrl": rel_meta.get("relevancia_afrl"),
                "motivos_relevancia": rel_meta.get("motivos_relevancia"),
                "motivos_descarte": rel_meta.get("motivos_descarte"),
                "possivel_edital": rel_meta.get("possivel_edital"),
                "motivo": rel_meta.get("motivo"),
            }
            if action == "discard":
                filter_stats["afrl_sent_discard"] = int(filter_stats.get("afrl_sent_discard") or 0) + 1
                afrl_discard.append({**entry, "routing": "descartados_ruido"})
            elif action == "review":
                filter_stats["afrl_sent_review"] = int(filter_stats.get("afrl_sent_review") or 0) + 1
                afrl_review.append({**entry, "routing": "review_relevancia"})
            else:
                kept_afrl.append(r)
                if rel_meta.get("possivel_edital"):
                    afrl_opp_review.append(
                        {
                            **entry,
                            "routing": "review_for_edital",
                            "review_reason": "sinal_opportunity_em_noticia",
                            "review_for_edital": True,
                        }
                    )
        raw_items = kept_afrl

    if sid0 == "afrl_mission_organizations" and raw_items:
        kept_mo: List[Dict[str, Any]] = []
        for r in raw_items:
            action, rel_meta = _afrl_evaluate_relevance(r, route="mission")
            r["_afrl_relevance"] = rel_meta
            entry = {
                "titulo": r.get("titulo"),
                "link": str(r.get("link") or "")[:800],
                "afrl_org_slug": r.get("afrl_org_slug"),
                "motivos_relevancia": rel_meta.get("motivos_relevancia"),
                "motivo": rel_meta.get("motivo"),
            }
            if action == "discard":
                filter_stats["afrl_mission_discard"] = int(filter_stats.get("afrl_mission_discard") or 0) + 1
                afrl_discard.append({**entry, "routing": "descartados_ruido"})
            elif action == "review":
                filter_stats["afrl_mission_review"] = int(filter_stats.get("afrl_mission_review") or 0) + 1
                afrl_review.append({**entry, "routing": "review_relevancia"})
            else:
                kept_mo.append(r)
        raw_items = kept_mo

    if sid0 in _STRATEGIC_MILITARY_NEWS_IDS and raw_items:
        from scripts.news_research import military_af_research as mil

        military_pre_relevance = [dict(r) for r in raw_items]
        kept_mil: List[Dict[str, Any]] = []
        for r in raw_items:
            action, rel_meta = mil.military_evaluate_relevance(sid0, r, route="news")
            r["_military_relevance"] = rel_meta
            r["_military_action"] = action
            entry = {
                "titulo": r.get("titulo"),
                "link": str(r.get("link") or "")[:800],
                "data_publicacao_raw": r.get("data_publicacao_raw"),
                "descricao": (str(r.get("descricao") or ""))[:600],
                "relevancia_military": rel_meta.get("relevancia_afrl"),
                "motivos_relevancia": rel_meta.get("motivos_relevancia"),
                "motivos_descarte": rel_meta.get("motivos_descarte"),
                "possivel_edital": rel_meta.get("possivel_edital"),
                "eixos_detectados": rel_meta.get("eixos_detectados"),
                "motivo": rel_meta.get("motivo"),
                "destino_sugerido": "Radar/Editais" if rel_meta.get("possivel_edital") else None,
            }
            if action == "discard":
                filter_stats["military_sent_discard"] = int(filter_stats.get("military_sent_discard") or 0) + 1
                military_discard.append({**entry, "routing": "descartados_ruido"})
            elif action == "review":
                filter_stats["military_sent_review"] = int(filter_stats.get("military_sent_review") or 0) + 1
                military_review.append({**entry, "routing": "review_relevancia"})
            else:
                kept_mil.append(r)
                if rel_meta.get("possivel_edital"):
                    military_opp_review.append(
                        {
                            **entry,
                            "routing": "review_for_edital",
                            "review_reason": "sinal_opportunity_em_noticia",
                            "review_for_edital": True,
                        }
                    )
        raw_items = kept_mil

    if sid0 in _STRATEGIC_MILITARY_PESQUISA_IDS and raw_items:
        kept_pes: List[Dict[str, Any]] = []
        for r in raw_items:
            if r.get("_possivel_edital"):
                military_opp_review.append(
                    {
                        "titulo": r.get("titulo"),
                        "link": str(r.get("link") or "")[:800],
                        "descricao": (str(r.get("descricao") or ""))[:600],
                        "routing": "review_for_edital",
                        "review_reason": "recurso_baa_opportunity_arl",
                        "destino_sugerido": "Radar/Editais",
                        "review_for_edital": True,
                        "source_id": sid0,
                    }
                )
            if r.get("_institucional_latente"):
                r["arl_resource_class"] = "institucional_latente"
            kept_pes.append(r)
        raw_items = kept_pes

    for r in raw_items:
        dt = _parse_date(r.get("data_publicacao_raw")) or _parse_date_from_url(str(r.get("link") or ""))
        if sid0 == "nato_news" and not dt:
            dt = _nato_date_from_url(str(r.get("link") or ""))
        if sid0 == "mcti_noticias" and not dt:
            dt = _mcti_date_from_url(str(r.get("link") or ""))
        if not dt and sid0 == "eurekalert_science_filtered":
            dt = _parse_date_from_eureka_listing_title(str(r.get("titulo") or ""))
        r["data_publicacao"] = _iso_date(dt)
        r["within_window"] = bool(dt and dt >= min_dt)

    # Para first cycle: manter itens sem data, mas sinalizar.
    for r in raw_items:
        std = _std_item(src, r)
        standardized.append(std)

    by_kind: Dict[str, int] = {}
    for r in raw_items:
        k = str(r.get("seed_kind") or "mixed")
        by_kind[k] = by_kind.get(k, 0) + 1
    meta = {
        "source_id": src.get("id"),
        "source_name": src.get("name"),
        "method": src.get("method"),
        "seed_urls_used": [s for s, _ in plan],
        "max_items": max_items,
        "time_window_months": tw,
        "raw_total": len(raw_items),
        "within_window_total": sum(1 for r in raw_items if r.get("within_window")),
        "without_date_total": sum(1 for r in raw_items if not r.get("data_publicacao")),
        "raw_by_seed_kind": by_kind,
        "feed_kind_caps_applied": feed_caps if sid0 == "iaea_news_publications" else {},
        "page_enrich_fetch_total": int(enrich_budget.get("n", 0)),
        "errors": errors,
        "theme_filter_stats": filter_stats,
    }
    if raw_filter_fn:
        meta["discarded_post_enrich"] = discarded_post_filter
        meta["discarded_post_enrich_total"] = len(discarded_post_filter)
    if sid0 == "defesanet":
        sections: Dict[str, int] = {}
        for r in raw_items:
            sec = _defesanet_section_from_url(str(r.get("link") or ""))
            sections[sec] = sections.get(sec, 0) + 1
        meta["sections_count"] = sections
    if sid0 == "brisa_news":
        meta["feed_items_available"] = meta.get("raw_total")
        meta["note_low_volume"] = (
            "O feed /news/feed/ publica poucos itens (típico 4); não usar feed global sem filtro /news/."
        )
    if sid0 == "brisa_artigos":
        meta["feed_items_available"] = filter_stats.get("extracted_total")
        meta["note_permalink"] = (
            "Feed /artigos/feed/ usa permalinks slug na raiz (sem /artigos/ no path); "
            "filtrar /news/ e páginas institucionais."
        )
        meta["time_window_label"] = f"{tw}_months_pesquisa"
    if sid0 == "exercito_brasileiro":
        meta["listing_method"] = "eb_liferay_html"
        meta["note_no_rss"] = "Sem RSS útil; seeds guest + noticiario-do-exercito."
    if sid0 == "softex_noticias":
        meta["feed_url"] = "https://softex.br/feed/"
        meta["note_permalink"] = (
            "RSS global WordPress (não /noticias/feed/ — 403); permalinks slug na raiz; "
            "hub HTML https://softex.br/noticias/."
        )
    if sid0 == "ita_projetos":
        meta["listing_method"] = "ita_drupal_projetos_hub"
        meta["note_no_rss"] = "Hub /projetos sem RSS; HTTPS www.ita.br costuma timeout — usar HTTP."
        meta["note_no_publication_date"] = "Catálogo institucional; datas de projeto ausentes no HTML."
    if sid0 == "ita_lab_guerra_eletronica":
        meta["page_kind"] = "portal_institucional"
        meta["note_static_lab"] = (
            "Página única de laboratório (missão/visão); não é feed de notícias; "
            "tipo_pesquisa=portal_institucional."
        )
    if sid0 == "capes_noticias":
        meta["feed_url"] = "https://www.gov.br/capes/pt-br/assuntos/noticias/rss.xml"
        meta["listing_url"] = "https://www.gov.br/capes/pt-br/assuntos/noticias"
        meta["note_rss_guid"] = "Feed Plone usa <guid> como URL canônica (link RSS vazio)."
        meta["note_sort"] = "Itens ordenados por pubDate desc antes do cap max_items."
    if sid0 == "f35_news":
        meta["feed_json_url"] = f"{_F35_NEWS_BASE}{_F35_FEED_PATH}"
        meta["listing_url"] = f"{_F35_NEWS_BASE}/f35/news-and-features.html"
        meta["listing_method"] = "aem_json_feed"
        meta["note_spa"] = (
            "Hub HTML é SPA (Algolia InstantSearch); listagem estável via JSON "
            f"{_F35_FEED_PATH} referenciado em data-path."
        )
        meta["note_no_rss"] = "Sem RSS dedicado; feed JSON oficial no DOM."
    if sid0 == "lockheed_martin_news":
        meta["feed_json_url"] = f"{_LM_NEWS_BASE}{_LM_FEED_PATH}"
        meta["listing_url"] = f"{_LM_NEWS_BASE}{_LM_NEWS_HUB}"
        meta["listing_method"] = "aem_json_feed"
        meta["review_candidates"] = lm_review
        meta["review_candidates_total"] = len(lm_review)
        meta["note_spa"] = (
            "Hub /en-us/news.html é SPA (Algolia); feed JSON newsfeed.json. "
            "robots Disallow em /en-us/news/news-releases e in-the-news — usar URLs "
            "news.lockheedmartin.com e /en-us/news/features|press."
        )
        meta["note_routing"] = (
            "capabilities/suppliers/who-we-are → rejeitado; Supplier/3rd Party/Statement → review."
        )
    if sid0 == "mcti_noticias":
        meta["listing_url"] = _MCTI_NOTICIAS_BASE
        meta["listing_method"] = "mcti_govbr_plone_listing"
        meta["note_no_rss"] = (
            "RSS/Atom em /noticias/rss.xml e /atom.xml retornam 404; listagem HTML hub + /noticias/YYYY."
        )
        meta["feeds_tested_404"] = [
            f"{_MCTI_NOTICIAS_BASE}/rss.xml",
            f"{_MCTI_NOTICIAS_BASE}/atom.xml",
        ]
        meta["review_candidates"] = mcti_review
        meta["review_candidates_total"] = len(mcti_review)
        meta["descartados_ruido"] = mcti_discard
        meta["descartados_ruido_total"] = len(mcti_discard)
        meta["mcti_pre_relevance_raw"] = mcti_pre_relevance
        meta["mcti_pre_relevance_total"] = len(mcti_pre_relevance)
        meta["note_relevance"] = (
            "Filtro forte CT&I: descarte se só sinais administrativos; review se admin+ técnico fraco; "
            "possivel_edital não roteia para Radar."
        )
        meta["note_fomento_separado"] = "MCTI Fomento permanece em Radar/Editais (mcti_fomento), não neste pipeline."
    if sid0 == "war_gov_news":
        meta["listing_url"] = "https://www.war.gov/news/"
        meta["feed_rss_url"] = _WAR_GOV_RSS_NEWS_STORIES
        meta["listing_method"] = "dod_articlecs_rss"
        meta["note_hub_403"] = (
            "Hub https://www.war.gov/news/ pode retornar 403 a bots; listagem estável via "
            "DesktopModules/ArticleCS/RSS ContentType=1 (News Stories)."
        )
        meta["note_sections"] = {
            "news_stories": "RSS ContentType=1 → public.noticia",
            "features": "path permitido se aparecer no feed",
            "press_products": "filtrado (Advisories/Releases)",
            "speeches": "descartado",
            "biographies": "descartado",
            "publications": "descartado (media.defense.gov)",
            "live_events": "descartado",
        }
        meta["robots_txt"] = "https://www.war.gov/robots.txt — testar em staging"
        meta["review_candidates"] = war_gov_review
        meta["review_candidates_total"] = len(war_gov_review)
        meta["descartados_ruido"] = war_gov_discard
        meta["descartados_ruido_total"] = len(war_gov_discard)
        meta["war_gov_pre_relevance_raw"] = war_gov_pre_relevance
        meta["war_gov_pre_relevance_total"] = len(war_gov_pre_relevance)
        meta["note_relevance"] = (
            "Filtro forte defesa/tecnologia: descarte institucional puro; review se admin+ técnico fraco "
            "ou procurement; possivel_procurement não vira edital automaticamente."
        )
        meta["note_fonte"] = (
            "fonte_recurso=war_gov_news; exibição neutra U.S. Department of Defense / War.gov "
            "(fonte oficial governamental, não jornalismo independente)."
        )
    if sid0 == "nato_news":
        meta["listing_url"] = _NATO_NEWS_HUB
        meta["sitemap_url"] = _NATO_SITEMAP_URL
        meta["listing_method"] = "nato_sitemap_aem"
        meta["note_hub_spa"] = (
            "Hub /en/news-and-events/articles/news é SPA (general_search + tag nato:content-type/news); "
            "search.json não responde a bots; listagem estável via sitemap.xml."
        )
        meta["note_detail"] = (
            "Detalhe: .model.json (title/description) + og:image; sem corpo integral."
        )
        meta["feeds_tested_missing"] = [
            "https://www.nato.int/rss/en/natohq/news.xml",
            "https://www.nato.int/cps/en/natohq/news_rss.htm",
        ]
        meta["robots_txt"] = "https://www.nato.int/robots.txt"
        meta["review_candidates"] = nato_review
        meta["review_candidates_total"] = len(nato_review)
        meta["descartados_ruido"] = nato_discard
        meta["descartados_ruido_total"] = len(nato_discard)
        meta["nato_pre_relevance_raw"] = nato_pre_relevance
        meta["nato_pre_relevance_total"] = len(nato_pre_relevance)
        meta["note_routing"] = (
            "news → public.noticia; speeches/statements/publications/nato-stories fora do path /articles/news/; "
            "institucional puro → descarte; discurso com sinal técnico → review."
        )
    if sid0 == "afrl_news":
        meta["listing_url"] = _AFRL_NEWS_HUB
        meta["listing_method"] = "afrl_news_listing_html"
        meta["note_hub_403"] = (
            "Hub /News/ retorna 403 com User-Agent do bot; listagem via browser UA + paginação ?Page=N."
        )
        meta["note_rss"] = (
            "RSS ArticleCS testado (Site 1–900): sem feed com links afrl.af.mil; não usar af.mil Site=1."
        )
        meta["robots_txt"] = "https://www.afrl.af.mil/robots.txt (403 com bot padrão)"
        meta["review_candidates"] = afrl_review + afrl_opp_review
        meta["review_candidates_total"] = len(afrl_review) + len(afrl_opp_review)
        meta["descartados_ruido"] = afrl_discard
        meta["descartados_ruido_total"] = len(afrl_discard)
        meta["afrl_pre_relevance_raw"] = afrl_pre_relevance
        meta["afrl_pre_relevance_total"] = len(afrl_pre_relevance)
        meta["review_for_edital_candidates"] = afrl_opp_review
        meta["note_opportunity"] = (
            "Notícias com SBIR/STTR/solicitation mantidas em noticia com possivel_edital; "
            "cópia em review_for_edital sem auto public.edital."
        )
    if sid0 == "afrl_mission_organizations":
        meta["listing_url"] = _AFRL_MISSION_HUB
        meta["listing_method"] = "afrl_mission_organizations_html"
        meta["note_catalog"] = (
            "Diretorias/laboratórios AFRL (paths /RE/, /711HPW/, etc.); tipo_pesquisa=centro_pesquisa; "
            "sem data_publicacao (catalogo institucional)."
        )
        meta["review_candidates"] = afrl_review
        meta["review_candidates_total"] = len(afrl_review)
        meta["descartados_ruido"] = afrl_discard
        meta["descartados_ruido_total"] = len(afrl_discard)
    if sid0 in _AFRL_DIRECTORATE_IDS:
        cfg_m = _AFRL_DIRECTORATE_CONFIG.get(sid0) or {}
        meta["listing_url"] = f"{_AFRL_BASE}/{cfg_m.get('code', '')}/"
        meta["listing_method"] = "afrl_directorate_highlights_html"
        meta["highlights_captured"] = filter_stats.get("afrl_highlights_captured")
        meta["highlights_with_date"] = filter_stats.get("afrl_highlights_with_date")
        meta["note_institutional"] = (
            "1 registro pesquisa por diretoria; extras.highlights = cards sem data ou todos os cards; "
            "highlights com data → afrl_mission_highlights."
        )
    if sid0 == "afrl_mission_highlights":
        meta["listing_method"] = "afrl_mission_highlights_ra_rj_rr"
        meta["note_routing"] = (
            "Highlights com data_publicacao → noticia (fonte_recurso=afrl_mission_highlights); "
            "sem data permanecem só em extras.highlights da diretoria."
        )
        meta["review_candidates"] = afrl_review + afrl_opp_review
        meta["review_candidates_total"] = len(afrl_review) + len(afrl_opp_review)
        meta["descartados_ruido"] = afrl_discard
        meta["descartados_ruido_total"] = len(afrl_discard)
        meta["review_for_edital_candidates"] = afrl_opp_review
    if sid0 in _STRATEGIC_MILITARY_IDS:
        from scripts.news_research import military_af_research as mil

        cfg_m = mil._DOD_AFMIL_SITES.get(sid0) or mil._AFNWC_PORTAL_CONFIG.get(sid0) or {}
        hub = cfg_m.get("news_hub") or cfg_m.get("hub") or (src.get("listing_url") or "")
        meta["listing_url"] = hub
        meta["listing_method"] = src.get("method") or "military_expansion"
        meta["note_hub_403"] = (
            "Domínios .af.mil / spaceforce.mil costumam 403 com bot UA; "
            "dry-run: DOD_AFMIL_WAYBACK_FALLBACK=1 ou AFRL_WAYBACK_FALLBACK=1."
        )
        meta["review_candidates"] = military_review + military_opp_review
        meta["review_candidates_total"] = len(military_review) + len(military_opp_review)
        meta["descartados_ruido"] = military_discard
        meta["descartados_ruido_total"] = len(military_discard)
        meta["military_pre_relevance_raw"] = military_pre_relevance
        meta["military_pre_relevance_total"] = len(military_pre_relevance)
        meta["review_for_edital_candidates"] = military_opp_review
        meta["note_opportunity"] = (
            "BAA/solicitation/opportunity → review_for_edital com destino_sugerido=Radar/Editais; "
            "sem roteamento automático para public.edital."
        )
        if sid0 == "afrl_technology_areas":
            meta["note_live"] = "afresearchlab.com/technology/ acessível (HTTP 200); áreas como pesquisa_estrategica."
        if sid0 == "arl_news":
            meta["note_arl"] = "Listagem via media-center + /news/ (Drupal); sem ArticleCS .af.mil."
        if sid0 == "arl_resources":
            meta["note_arl_resources"] = "Recursos /resources/, BAA, CRAs; BAA → review."
    return raw_items, standardized, meta


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawl seguro de fontes notícia/pesquisa (sem apply).")
    ap.add_argument("--config", default=str(CONFIG_DEFAULT))
    ap.add_argument("--output-dir", default=str(OUT_DEFAULT))
    ap.add_argument("--sources", default="", help="CSV de source ids")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    out_dir = Path(args.output_dir)
    raw_dir = out_dir / "raw"
    std_dir = out_dir / "standardized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    std_dir.mkdir(parents=True, exist_ok=True)

    cfg = _load_json(cfg_path, {})
    sources = cfg.get("sources") if isinstance(cfg, dict) else []
    if not isinstance(sources, list):
        sources = []
    filt = {s.strip() for s in args.sources.split(",") if s.strip()}
    if filt:
        sources = [s for s in sources if str(s.get("id") or "") in filt]

    all_meta = []
    by_source = []
    examples = []
    total_raw = total_std = 0
    for s in sources:
        raw_items, std_items, meta = crawl_source(s)
        sid = str(s.get("id") or "source")
        (raw_dir / f"{sid}_raw.json").write_text(json.dumps(raw_items, ensure_ascii=False, indent=2), encoding="utf-8")
        (std_dir / f"{sid}_standardized.json").write_text(json.dumps(std_items, ensure_ascii=False, indent=2), encoding="utf-8")
        (out_dir / f"{sid}_crawl_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        total_raw += len(raw_items)
        total_std += len(std_items)
        by_source.append(
            {
                "source_id": sid,
                "raw_total": len(raw_items),
                "standardized_total": len(std_items),
                "within_window_total": meta["within_window_total"],
                "without_date_total": meta["without_date_total"],
                "error_total": len(meta["errors"]),
            }
        )
        examples.extend(
            {
                "source_id": sid,
                "titulo": i.get("titulo"),
                "link": i.get("link"),
                "data_publicacao": i.get("data_publicacao"),
                "tipo_conteudo": i.get("tipo_conteudo"),
            }
            for i in std_items[:8]
        )
        all_meta.append(meta)

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "config_path": str(cfg_path.resolve()),
        "sources_total": len(sources),
        "raw_total": total_raw,
        "standardized_total": total_std,
        "by_source_path": str((out_dir / "by_source.json")),
        "examples_path": str((out_dir / "examples.json")),
        "notes": [
            "Sem apply em banco; apenas geração local de artefatos.",
            "Janela alvo: últimos 12 meses quando data disponível.",
            "Itens sem data são mantidos neste ciclo e sinalizados em auditoria."
        ],
    }

    (out_dir / "by_source.json").write_text(json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "examples.json").write_text(json.dumps(examples[:80], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "news_research_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# News/Research crawl summary",
        "",
        f"- Fontes avaliadas: **{summary['sources_total']}**",
        f"- Itens brutos: **{summary['raw_total']}**",
        f"- Itens standardized: **{summary['standardized_total']}**",
        "- Sem apply em Supabase (first cycle).",
        "",
        "## Por fonte",
        "",
    ]
    for r in by_source:
        md.append(
            f"- `{r['source_id']}`: raw={r['raw_total']} std={r['standardized_total']} "
            f"janela12m={r['within_window_total']} sem_data={r['without_date_total']} erros={r['error_total']}"
        )
    (out_dir / "news_research_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

