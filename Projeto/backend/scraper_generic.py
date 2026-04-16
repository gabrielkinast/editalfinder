import csv
import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

MONTHS_PT = {
    "janeiro": "01",
    "fevereiro": "02",
    "marco": "03",
    "março": "03",
    "abril": "04",
    "maio": "05",
    "junho": "06",
    "julho": "07",
    "agosto": "08",
    "setembro": "09",
    "outubro": "10",
    "novembro": "11",
    "dezembro": "12",
}


def normalize_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def parse_date(text):
    if not text:
        return None
    text = text.strip().lower()

    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        try:
            return datetime.strptime(m.group(0), "%Y-%m-%d").date().isoformat()
        except ValueError:
            pass

    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        try:
            d, mo, y = m.groups()
            return datetime.strptime(f"{int(d):02d}/{int(mo):02d}/{y}", "%d/%m/%Y").date().isoformat()
        except ValueError:
            pass

    m = re.search(r"(\d{1,2})\s+de\s+([a-zçãõéêôíóú]+)\s+de\s+(\d{4})", text)
    if m:
        d, month_name, y = m.groups()
        mo = MONTHS_PT.get(month_name)
        if mo:
            try:
                return datetime.strptime(f"{int(d):02d}/{mo}/{y}", "%d/%m/%Y").date().isoformat()
            except ValueError:
                pass

    return None


def extract_deadline(text):
    if not text:
        return None
    patterns = [
        r"(?:prazo|deadline|submiss[aã]o|inscri[cç][aã]o|encerramento|limite|até)\D{0,20}(\d{1,2}/\d{1,2}/\d{4})",
        r"(?:prazo|deadline|submiss[aã]o|inscri[cç][aã]o|encerramento|limite|até)\D{0,20}(\d{4}-\d{2}-\d{2})",
        r"(?:prazo|deadline|submiss[aã]o|inscri[cç][aã]o|encerramento|limite|até)\D{0,20}(\d{1,2}\s+de\s+[a-zçãõéêôíóú]+\s+de\s+\d{4})",
    ]
    for pattern in patterns:
        for hit in re.findall(pattern, text, re.IGNORECASE):
            parsed = parse_date(hit)
            if parsed:
                return parsed
    return None


def extract_value(text):
    if not text:
        return None
    m = re.search(
        r"(R\$\s?\d[\d\.\,]*(?:\s?(?:mil|milh[aã]o|milh[oõ]es|bilh[aã]o|bilh[oõ]es))?)",
        text,
        re.IGNORECASE,
    )
    if m:
        return normalize_text(m.group(1))
    return None


def classify_resource_type(text):
    if not text:
        return "Não Especificado"
    t = text.lower()
    if any(x in t for x in ["grant", "subven", "não reembols", "nao reembols", "fomento"]):
        return "Subvenção (Não Reembolsável)"
    if any(x in t for x in ["loan", "credit", "crédito", "credito", "reembols", "financiamento"]):
        return "Reembolsável (Financiamento)"
    if any(x in t for x in ["fellowship", "scholarship", "bolsa"]):
        return "Bolsa / Auxílio"
    return "Não Especificado"


def fetch_soup(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception:
        return None


def _host_matches_allowed(url: str, allowed_domains: Optional[List[str]]) -> bool:
    """Evita seguir links externos (reduz ruído e falhas de fetch)."""
    if not allowed_domains:
        return True
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return False
    if host.startswith("www."):
        host = host[4:]
    for domain in allowed_domains:
        d = domain.lower().lstrip(".")
        if host == d or host.endswith("." + d):
            return True
    return False


def scrape_source(config):
    all_items = []
    seen_links = set()
    max_items = config.get("max_items", 20)
    max_links_per_page = config.get("max_links_per_page", 120)

    keywords = [x.lower() for x in config["keywords"]]
    avoid = [x.lower() for x in config.get("avoid_keywords", [])]
    allowed_domains = config.get("allowed_domains")

    for listing_url in config["listing_urls"]:
        soup = fetch_soup(listing_url)
        if not soup:
            continue
        links = soup.select("a[href]")[:max_links_per_page]
        for a in links:
            if len(all_items) >= max_items:
                break
            href = a.get("href")
            title = normalize_text(a.get_text())
            if not href:
                continue
            full_url = urljoin(listing_url, href).split("#", 1)[0]
            if not full_url.startswith("http"):
                continue
            if not _host_matches_allowed(full_url, allowed_domains):
                continue
            if full_url in seen_links:
                continue

            hay = f"{title} {full_url}".lower()
            if not any(k in hay for k in keywords):
                continue
            if any(k in hay for k in avoid):
                continue

            seen_links.add(full_url)
            detail = fetch_soup(full_url) if not full_url.lower().endswith(".pdf") else None
            body_text = normalize_text(detail.get_text(" ")) if detail else title
            h1 = normalize_text((detail.select_one("h1").get_text() if detail and detail.select_one("h1") else title))
            pub_date = parse_date(body_text) or parse_date(title)
            deadline = extract_deadline(body_text)

            anexos = []
            if detail:
                for doc_a in detail.select("a[href]"):
                    doc_href = doc_a.get("href")
                    if not doc_href:
                        continue
                    doc_url = urljoin(full_url, doc_href)
                    low = doc_url.lower()
                    if any(low.endswith(ext) for ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip"]):
                        anexos.append({"nome": normalize_text(doc_a.get_text()) or "Documento", "url": doc_url})
            elif full_url.lower().endswith(".pdf"):
                anexos.append({"nome": "Edital PDF", "url": full_url})

            combined = f"{h1} {body_text}"
            if deadline:
                try:
                    if datetime.strptime(deadline, "%Y-%m-%d").date() < date.today():
                        continue
                except ValueError:
                    pass

            all_items.append(
                {
                    "titulo": h1 or title,
                    "descricao": combined[:3500],
                    "link": full_url,
                    "fonte": config["source_label"],
                    "data_publicacao": pub_date,
                    "fim_inscricao": deadline,
                    "situacao": "Aberto" if deadline else "Em andamento",
                    "valor": extract_value(combined),
                    "programa": config.get("program_hint"),
                    "acao": None,
                    "tipo_recurso": classify_resource_type(combined),
                    "extras": {
                        "anexos": anexos,
                        "url_pagina": listing_url,
                        "coletado_em": datetime.now().date().isoformat(),
                    },
                }
            )
        if len(all_items) >= max_items:
            break

    return all_items


def save_outputs(base_dir, output_prefix, items):
    output_dir = Path(base_dir) / "outputs"
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"{output_prefix}_editais.json"
    csv_path = output_dir / f"{output_prefix}_editais.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    if items:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(items[0].keys()))
            writer.writeheader()
            writer.writerows(items)
