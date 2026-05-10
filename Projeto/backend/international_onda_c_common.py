"""Shared safe crawler helpers for international innovation Onda C sources."""
from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urljoin, urlparse

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import fetch_soup, normalize_text, save_outputs


ACTION_MARKERS = (
    "call",
    "open call",
    "apply",
    "application",
    "submission",
    "submit",
    "deadline",
    "closing date",
    "competition",
    "funding",
    "grant",
    "opportunity",
    "proposal",
    "tender",
    "procurement",
    "invitation to tender",
    "campaign",
    "fellowship",
    "award",
)

EXCLUDED_URL_PARTS = (
    "/about",
    "/contact",
    "/contacts",
    "/career",
    "/careers",
    "/news",
    "/blog",
    "/events",
    "/privacy",
    "/terms",
    "/cookies",
    "/faq",
    "/faqs",
    "/login",
)

MONTHS_EN = {
    "january": "01",
    "february": "02",
    "march": "03",
    "april": "04",
    "may": "05",
    "june": "06",
    "july": "07",
    "august": "08",
    "september": "09",
    "october": "10",
    "november": "11",
    "december": "12",
}


def _host_ok(url: str, domains: Iterable[str]) -> bool:
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    for domain in domains:
        d = domain.lower().lstrip(".")
        if host == d or host.endswith("." + d):
            return True
    return False


def _looks_excluded(url: str, text: str = "") -> bool:
    blob = f"{url} {text}".lower()
    if any(x in blob for x in EXCLUDED_URL_PARTS):
        return True
    title = normalize_text(text).lower()
    return title in {"home", "menu", "log in", "register", "view all", "explore", "quick guide"}


def _has_action_signal(text: str, extra_markers: Iterable[str] = ()) -> bool:
    low = (text or "").lower()
    return any(m in low for m in tuple(ACTION_MARKERS) + tuple(extra_markers))


def _extract_main_text(soup: Any, limit: int = 3200) -> str:
    if not soup:
        return ""
    container = soup.select_one("main") or soup.select_one("article") or soup.select_one("#content") or soup
    chunks: List[str] = []
    for node in container.select("h1, h2, h3, p, li, dt, dd"):
        txt = normalize_text(node.get_text(" "))
        if len(txt) < 20:
            continue
        low = txt.lower()
        if any(x in low for x in ("cookie", "privacy", "skip to", "sign in", "newsletter")):
            continue
        chunks.append(txt)
        if sum(len(x) for x in chunks) > limit:
            break
    return normalize_text(" ".join(chunks))[:limit]


def _parse_english_date(raw: str) -> Optional[str]:
    if not raw:
        return None
    text = normalize_text(raw).lower()
    patterns = (
        r"(\d{1,2})\s+([a-z]+)\s+(\d{4})",
        r"([a-z]+)\s+(\d{1,2}),?\s+(\d{4})",
        r"(\d{4})-(\d{2})-(\d{2})",
        r"(\d{1,2})/(\d{1,2})/(\d{4})",
    )
    for pat in patterns:
        m = re.search(pat, text)
        if not m:
            continue
        try:
            if pat.startswith("(\\d{4})"):
                return datetime.strptime(m.group(0), "%Y-%m-%d").date().isoformat()
            if "/" in pat:
                d, mo, y = m.groups()
                return datetime.strptime(f"{int(d):02d}/{int(mo):02d}/{y}", "%d/%m/%Y").date().isoformat()
            if m.group(1).isdigit():
                d, month, y = m.groups()
            else:
                month, d, y = m.groups()
            mo = MONTHS_EN.get(month)
            if mo:
                return datetime.strptime(f"{int(d):02d}/{mo}/{y}", "%d/%m/%Y").date().isoformat()
        except Exception:
            continue
    return None


def extract_deadline_en(text: str) -> Optional[str]:
    if not text:
        return None
    for pat in (
        r"(?:closing date|deadline|submit by|applications close|ends|submission deadline)\D{0,60}(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
        r"(?:closing date|deadline|submit by|applications close|ends|submission deadline)\D{0,60}([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"(?:closing date|deadline|submit by|applications close|ends|submission deadline)\D{0,60}(\d{4}-\d{2}-\d{2})",
        r"(?:closing date|deadline|submit by|applications close|ends|submission deadline)\D{0,60}(\d{1,2}/\d{1,2}/\d{4})",
    ):
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            parsed = _parse_english_date(m.group(1))
            if parsed:
                return parsed
    return None


def extract_deadline_from_soup(soup: Any, text: str) -> Optional[str]:
    parsed = extract_deadline_en(text)
    if parsed:
        return parsed
    if not soup:
        return None
    for node in soup.select("time[datetime]"):
        raw = node.get("datetime") or ""
        label = normalize_text((node.parent.get_text(" ") if node.parent else node.get_text(" ")))
        if any(x in label.lower() for x in ("closing", "deadline", "apply", "submission")):
            parsed = _parse_english_date(raw)
            if parsed:
                return parsed
    for node in soup.select("dt, strong, b, th"):
        label = normalize_text(node.get_text(" "))
        if not any(x in label.lower() for x in ("closing", "deadline", "apply by", "submission")):
            continue
        sib = node.find_next_sibling(["dd", "td", "p", "span"])
        raw = normalize_text(sib.get_text(" ")) if sib else ""
        parsed = _parse_english_date(raw)
        if parsed:
            return parsed
    return None


def classify_item(text: str, default_type: str, default_resource: str) -> Dict[str, str]:
    low = text.lower()
    if any(x in low for x in ("procurement", "tender", "invitation to tender", "itt")):
        return {"tipo_oportunidade": "procurement", "tipo_recurso": "oportunidade_fornecedor", "acao": "submit_tender"}
    if "fellowship" in low:
        return {"tipo_oportunidade": "fellowship", "tipo_recurso": "grant", "acao": "apply"}
    if any(x in low for x in ("research grant", "research council", "research organisation")):
        return {"tipo_oportunidade": "research_grant", "tipo_recurso": "grant", "acao": "apply"}
    if any(x in low for x in ("accelerator", "startup", "scale up", "scale-up")):
        return {"tipo_oportunidade": "startup_programme", "tipo_recurso": "apoio_inovacao", "acao": "apply"}
    if any(x in low for x in ("campaign", "open space innovation", "space", "esa")):
        return {"tipo_oportunidade": "space_opportunity", "tipo_recurso": "apoio_inovacao", "acao": "submit_idea"}
    if any(x in low for x in ("call for proposals", "call for proposal", "open call")):
        return {"tipo_oportunidade": "call_for_proposals", "tipo_recurso": "grant", "acao": "submit_proposal"}
    if any(x in low for x in ("competition", "funding opportunity", "grant", "funding")):
        return {"tipo_oportunidade": "funding_opportunity", "tipo_recurso": "grant", "acao": "apply"}
    return {"tipo_oportunidade": default_type, "tipo_recurso": default_resource, "acao": "review"}


def infer_profiles(text: str) -> List[str]:
    low = text.lower()
    profiles: List[str] = []
    if any(x in low for x in ("startup", "scale-up", "sme", "small business", "business", "companies", "organisations")):
        profiles.extend(["empresa", "pequena_empresa", "media_empresa"])
    if any(x in low for x in ("university", "research organisation", "researcher", "fellowship")):
        profiles.extend(["universidade", "ICT", "pesquisador"])
    if any(x in low for x in ("consortium", "collaborative", "partners")):
        profiles.append("consorcio")
    if any(x in low for x in ("supplier", "bidder", "tender", "procurement")):
        profiles.append("fornecedor")
    if not profiles:
        profiles.append("organizacao_internacional")
    seen = set()
    out = []
    for p in profiles:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out[:6]


def infer_sectors(text: str) -> List[str]:
    low = text.lower()
    candidates: List[str] = []
    checks = (
        ("aeroespacial", ("space", "satellite", "esa", "orbit", "navigation", "pnt", "earth observation")),
        ("energia", ("energy", "battery", "hydrogen", "solar", "wind")),
        ("sustentabilidade", ("sustainability", "sustainable", "circular", "green", "zero debris")),
        ("clima", ("climate", "carbon", "net zero", "emission")),
        ("digital", ("digital", "software", "cyber", "ai ", "artificial intelligence", "quantum", "data")),
        ("saude", ("health", "medical", "medicine", "biotech")),
        ("agricultura", ("agriculture", "food", "soil", "farming")),
        ("industria", ("industry", "industrial", "manufacturing", "manufactur")),
        ("materiais", ("materials", "raw materials", "advanced materials")),
        ("manufatura", ("manufacturing", "advanced manufacturing")),
        ("cidades", ("urban", "city", "cities", "mobility")),
        ("educacao", ("education", "skills", "training")),
        ("defesa", ("defence", "defense", "military", "dual-use", "dual use")),
        ("ciencia_tecnologia", ("research", "science", "technology", "innovation")),
    )
    for label, pats in checks:
        if any(p in low for p in pats):
            candidates.append(label)
    detected = []
    seen = set()
    for c in candidates:
        if c not in seen:
            seen.add(c)
            detected.append(c)
    return detected


def _candidate_links(listing_url: str, soup: Any, config: Dict[str, Any]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    seen = set()
    for a in soup.select("a[href]"):
        title = normalize_text(a.get_text(" "))
        href = a.get("href") or ""
        url = urljoin(listing_url, href).split("#", 1)[0]
        if not url.startswith("http") or url in seen:
            continue
        if not _host_ok(url, config["allowed_domains"]):
            continue
        parent = a.find_parent(["article", "li", "section", "div"]) or a
        context = normalize_text(parent.get_text(" "))
        hay = f"{title} {context} {url}"
        if len(title) < 8 and len(context) < 80:
            continue
        if _looks_excluded(url, title):
            continue
        must_url = config.get("url_must_contain_any") or ()
        if must_url and not any(x in url.lower() for x in must_url):
            continue
        url_exclude = config.get("url_exclude_contains") or ()
        if url_exclude and any(x.lower() in url.lower() for x in url_exclude):
            continue
        exact_paths = config.get("url_exclude_exact_paths") or ()
        if exact_paths and urlparse(url).path.rstrip("/").lower() in {p.rstrip("/").lower() for p in exact_paths}:
            continue
        must_text = config.get("listing_text_must_contain_any") or ()
        if must_text and not any(x.lower() in hay.lower() for x in must_text):
            continue
        if not _has_action_signal(hay, config.get("extra_action_markers") or ()):
            continue
        seen.add(url)
        out.append({"title": title, "context": context, "url": url})
        if len(out) >= int(config.get("max_links", 30)):
            break
    return out


def build_item(source_key: str, label: str, config: Dict[str, Any], cand: Dict[str, str], listing_url: str) -> Dict[str, Any]:
    detail = fetch_soup(cand["url"], timeout=int(config.get("timeout", 12)))
    detail_text = _extract_main_text(detail) if detail else cand.get("context", "")
    h1 = ""
    if detail and detail.select_one("h1"):
        h1 = normalize_text(detail.select_one("h1").get_text(" "))
    title = h1 or cand.get("title") or label
    description = normalize_text(f"{title} {cand.get('context', '')} {detail_text}")[:4200]
    deadline = extract_deadline_from_soup(detail, description)
    classif = classify_item(description + " " + cand["url"], config["default_tipo_oportunidade"], config["default_tipo_recurso"])
    sectors_detected = infer_sectors(description)
    sectors = sectors_detected[:3]
    docs = []
    if detail:
        for a in detail.select("a[href]"):
            href = a.get("href") or ""
            url = urljoin(cand["url"], href)
            low = url.lower()
            if any(low.endswith(ext) for ext in (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip")):
                docs.append({"nome": normalize_text(a.get_text(" ")) or "Documento", "url": url})
            if len(docs) >= 8:
                break
    pdf_url = next((d["url"] for d in docs if str(d.get("url", "")).lower().endswith(".pdf")), "")
    return {
        "titulo": title[:240],
        "descricao": description,
        "link": cand["url"],
        "fonte": label,
        "fonte_recurso": label,
        "data_publicacao": _parse_english_date(description),
        "fim_inscricao": deadline,
        "situacao": "Aberto" if deadline else "Em andamento",
        "valor": "",
        "programa": config.get("programa", label),
        "acao": classif["acao"],
        "tipo_recurso": classif["tipo_recurso"],
        "perfil_ideal": infer_profiles(description),
        "publico_alvo": infer_profiles(description),
        "setor_estrategico": sectors,
        "area_tecnologica": sectors,
        "extras": {
            "origem_portal": config["origem_portal"],
            "url_listagem": listing_url,
            "url_detalhe": cand["url"],
            "url_pagina": listing_url,
            "idioma_original": "en",
            "pais": config.get("pais", "Internacional"),
            "regiao": config.get("regiao", "internacional"),
            "tipo_oportunidade": classif["tipo_oportunidade"],
            "tipo_recurso": classif["tipo_recurso"],
            "natureza_recurso": "nao_reembolsavel" if classif["tipo_recurso"] in ("grant", "apoio_inovacao") else "",
            "perfil_ideal": infer_profiles(description),
            "publico_alvo": infer_profiles(description),
            "setor_estrategico": sectors,
            "setores_detectados": sectors_detected,
            "tags_secundarias": sectors_detected[3:],
            "area_tecnologica": sectors,
            "documentos": docs,
            "pdf_url": pdf_url,
            "metodo_extracao": "international_onda_c_safe_html",
            "metodo_classificacao": f"{source_key}_local_calibration_seed",
            "coletado_em": date.today().isoformat(),
        },
    }


def crawl_source(source_key: str, label: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen = set()
    for listing_url in config["listing_urls"]:
        soup = fetch_soup(listing_url, timeout=int(config.get("timeout", 12)))
        if not soup:
            continue
        for cand in _candidate_links(listing_url, soup, config):
            if cand["url"] in seen:
                continue
            seen.add(cand["url"])
            item = build_item(source_key, label, config, cand, listing_url)
            detail_must = config.get("detail_text_must_contain_any") or ()
            if detail_must:
                detail_blob = f"{item.get('titulo')} {item.get('descricao')} {item.get('link')}".lower()
                if not any(x.lower() in detail_blob for x in detail_must):
                    continue
            if not _has_action_signal(f"{item['titulo']} {item['descricao']} {item['link']}", config.get("extra_action_markers") or ()):
                continue
            items.append(item)
            if len(items) >= int(config.get("max_items", 20)):
                return items
    for fallback in config.get("fallback_items") or []:
        if fallback["link"] in seen:
            continue
        seen.add(fallback["link"])
        base = {
            "title": fallback["titulo"],
            "context": fallback["descricao"],
            "url": fallback["link"],
        }
        items.append(build_item(source_key, label, config, base, fallback.get("url_listagem") or config["listing_urls"][0]))
    return items[: int(config.get("max_items", 20))]


def run_source(source_key: str, label: str, config: Dict[str, Any]) -> None:
    try:
        items = crawl_source(source_key, label, config)
        save_outputs(
            Path(source_key),
            source_key,
            items,
            allow_empty=bool(config.get("allow_empty")),
        )
        print(f"[{label}] Registros salvos: {len(items)}")
    except Exception as exc:
        save_outputs(Path(source_key), source_key, [], failure_reason=str(exc), collection_failed=True)
        print(f"[{label}] Falha na coleta: {exc}")
