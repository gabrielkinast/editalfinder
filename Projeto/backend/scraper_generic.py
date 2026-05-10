import csv
import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from CORE.http_fetch import fetch_pdf_bytes
from CORE.pdf_enrichment import extract_pdf_text_with_fallback
from crawler_output_safe import CONFIRMED_EMPTY_REASON, save_output_safely

try:
    import certifi

    _TLS_VERIFY = certifi.where()
except Exception:  # pragma: no cover - ambiente sem certifi
    _TLS_VERIFY = True


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

GENERIC_NOISE_TITLES = {
    "home",
    "menu",
    "buscar",
    "busca",
    "pesquisar",
    "entrar",
    "dados abertos",
    "acesso à informação",
    "acesso a informacao",
    "ações e programas",
    "acoes e programas",
    "quem é quem",
    "quem e quem",
    "temas de pesquisa",
    "painel de compras do governo federal",
    "empresas e negócios",
    "empresas e negocios",
    "ir para o conteúdo 1",
    "ir para o conteudo 1",
    "atvar o modo mais acessível",
    "ativar o modo mais acessível",
    "ativar o modo mais acessivel",
    "our priorities",
    "funding guidance",
    "articles",
    "managing your grant",
    "project reporting",
    "set up and develop your team",
    "manage your project",
}

NOISE_TEXT_HINTS = [
    "atenção! seu navegador não pode executar javascript",
    "atencao! seu navegador nao pode executar javascript",
    "ir para o conteúdo 1",
    "ir para o conteudo 1",
    "ir para a busca",
    "ir para o mapa do site",
    "quem somos",
    "perguntas frequentes",
    "transparência e prestação de contas",
    "transparencia e prestacao de contas",
    "notícias",
    "noticias",
]

DOCUMENT_NOISE_HINTS = [
    "carta de serviços",
    "carta de servicos",
    "política de privacidade",
    "politica de privacidade",
    "mapa do site",
    "termos de uso",
]

OPPORTUNITY_HINTS = [
    "edital",
    "chamada",
    "fomento",
    "financiamento",
    "crédito",
    "credito",
    "subven",
    "bolsa",
    "auxílio",
    "auxilio",
    "grant",
    "funding",
    "solicitation",
    "proposal",
    "investimento",
    "linha de crédito",
    "linha de credito",
]


def normalize_text(text):
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _extract_main_text(soup):
    container = (
        soup.select_one("main")
        or soup.select_one("article")
        or soup.select_one("#content")
        or soup.select_one(".content")
        or soup.select_one(".entry-content")
        or soup.select_one(".post-content")
        or soup
    )
    snippets = []
    for node in container.select("p, li"):
        chunk = normalize_text(node.get_text(" "))
        if len(chunk) < 30:
            continue
        low = chunk.lower()
        if any(k in low for k in ["cookie", "privacidade", "skip to", "fale conosco", "ouvidoria"]):
            continue
        snippets.append(chunk)
        if len(snippets) >= 12:
            break
    text = " ".join(snippets) if snippets else normalize_text(container.get_text(" "))
    for marker in ("Skip to main content", "Ir para o Conteúdo", "Atenção! Seu navegador não pode executar javascript"):
        text = text.replace(marker, " ")
    return normalize_text(text)


def _sanitize_description(text: str) -> str:
    if not text:
        return ""
    out = normalize_text(text)
    out = re.sub(r"https?://\S+", " ", out, flags=re.IGNORECASE)
    out = out.replace("Atenção! Seu navegador não pode executar javascript.", " ")
    out = out.replace("Ir para o Conteúdo", " ")
    out = re.sub(r"\s+=\s+[A-Za-zÀ-ÿ0-9_\- ]+", " ", out)
    return normalize_text(out)


def _title_is_noise(title: str) -> bool:
    low = normalize_text(title).lower()
    if not low or len(low) < 4:
        return True
    if re.fullmatch(r"\d{4}", low):
        return True
    return low in GENERIC_NOISE_TITLES


def _has_opportunity_signal(text: str) -> bool:
    low = (text or "").lower()
    return any(k in low for k in OPPORTUNITY_HINTS)


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


def fetch_soup(url, timeout=10):
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, verify=_TLS_VERIFY)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("html"):
            return soup
    except Exception:
        pass
    # Fallback curl (-k): alguns *.rs.gov.br / TLS retornam 403 ou falham só com requests.
    try:
        curl_bin = "curl.exe" if sys.platform == "win32" else "curl"
        cmd = [
            curl_bin,
            "-skL",
            "--max-time",
            str(int(timeout) + 15),
            "-H",
            f"User-Agent: {HEADERS['User-Agent']}",
            "-H",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if result.returncode == 0 and result.stdout and "html" in result.stdout.lower()[:8000]:
            return BeautifulSoup(result.stdout, "html.parser")
    except Exception:
        pass
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
    http_timeout = int(config.get("http_timeout", 10))

    keywords = [x.lower() for x in config["keywords"]]
    avoid = [x.lower() for x in config.get("avoid_keywords", [])]
    allowed_domains = config.get("allowed_domains")

    for listing_url in config["listing_urls"]:
        soup = fetch_soup(listing_url, timeout=http_timeout)
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
            listing_base = listing_url.split("#", 1)[0].rstrip("/")
            if full_url.rstrip("/") == listing_base:
                continue
            if not _host_matches_allowed(full_url, allowed_domains):
                continue
            must_any = config.get("link_url_must_contain_any") or []
            if must_any and not any(str(s).lower() in full_url.lower() for s in must_any):
                continue
            must_all = config.get("link_url_must_contain_all") or []
            if must_all and not all(str(s).lower() in full_url.lower() for s in must_all):
                continue
            exc_sub = config.get("link_url_exclude_substrings") or []
            if exc_sub and any(str(s).lower() in full_url.lower() for s in exc_sub):
                continue
            min_depth = int(config.get("link_path_min_depth") or 0)
            if min_depth > 0:
                parts = [p for p in urlparse(full_url).path.strip("/").split("/") if p]
                if len(parts) < min_depth:
                    continue
            if full_url in seen_links:
                continue
            if _title_is_noise(title):
                continue

            hay = f"{title} {full_url}".lower()
            if not any(k in hay for k in keywords):
                continue
            if any(k in hay for k in avoid):
                continue

            seen_links.add(full_url)
            detail = fetch_soup(full_url, timeout=http_timeout) if not full_url.lower().endswith(".pdf") else None
            body_text = _extract_main_text(detail) if detail else title
            if detail and config.get("enrich_meta_tags"):
                meta_chunks = []
                for attrs in ({"name": "description"}, {"property": "og:description"}):
                    mtag = detail.find("meta", attrs=attrs)
                    if mtag and mtag.get("content"):
                        meta_chunks.append(normalize_text(mtag["content"]))
                og_title = detail.find("meta", attrs={"property": "og:title"})
                if og_title and og_title.get("content"):
                    meta_chunks.append(normalize_text(og_title["content"]))
                if meta_chunks:
                    body_text = normalize_text(f"{body_text} {' '.join(meta_chunks)}")
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
                    doc_name = normalize_text(doc_a.get_text()) or "Documento"
                    doc_hay = f"{doc_name} {doc_url}".lower()
                    if any(k in doc_hay for k in DOCUMENT_NOISE_HINTS):
                        continue
                    low = doc_url.lower()
                    if any(low.endswith(ext) for ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip"]):
                        anexos.append({"nome": doc_name, "url": doc_url})
            elif full_url.lower().endswith(".pdf"):
                anexos.append({"nome": "Edital PDF", "url": full_url})
            pdf_url = next((x.get("url") for x in anexos if isinstance(x, dict) and str(x.get("url", "")).lower().endswith(".pdf")), "")
            pdf_text = ""
            if pdf_url:
                try:
                    pdf_bytes = fetch_pdf_bytes(pdf_url, page_referer=full_url)
                    if pdf_bytes:
                        extracted = extract_pdf_text_with_fallback(pdf_bytes, max_pages=5) or ""
                        pdf_text = normalize_text(extracted)[:2200]
                except Exception:
                    pdf_text = ""

            combined = _sanitize_description(f"{h1} {body_text} {pdf_text}")
            combined_low = combined.lower()
            if _title_is_noise(h1 or title):
                continue
            if sum(1 for k in NOISE_TEXT_HINTS if k in combined_low) >= 2 and not _has_opportunity_signal(combined_low):
                continue
            if config.get("require_opportunity_signals", True):
                has_signal = _has_opportunity_signal(f"{h1} {combined} {full_url}")
                has_document = bool(pdf_url or anexos)
                if not has_signal and not has_document:
                    continue
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
                        "regiao": config.get("regiao", "brasil"),
                        "pais": config.get("pais", "Brasil"),
                        "idioma_original": config.get("idioma_original", "pt"),
                        "titulo_original": h1 or title,
                        "descricao_original": combined[:3500],
                        "titulo_traduzido": "",
                        "descricao_traduzida": "",
                        "setor_estrategico": config.get("setor_estrategico", ""),
                        "subtema": config.get("subtema_padrao", []),
                        "area_cientifica": config.get("area_cientifica", []),
                        "area_tecnologica": config.get("area_tecnologica", []),
                        "tipo_oportunidade": config.get("tipo_oportunidade", ""),
                        "orgao_responsavel": config.get("orgao_responsavel", config["source_label"]),
                        "instituicao": config.get("instituicao", config["source_label"]),
                        "empresa_prime": config.get("empresa_prime", ""),
                        "orgao_contratante": config.get("orgao_contratante", config["source_label"]),
                        "numero_edital": "",
                        "numero_chamada": "",
                        "numero_processo": "",
                        "codigo_oportunidade": "",
                        "modalidade": "",
                        "publico_alvo": "",
                        "elegibilidade": "",
                        "objetivo": "",
                        "escopo": "",
                        "itens_financiaveis": [],
                        "itens_nao_financiaveis": [],
                        "valor_total": "",
                        "valor_por_projeto": "",
                        "contrapartida": "",
                        "prazo_execucao": "",
                        "cronograma": [],
                        "documentos": anexos,
                        "pdf_url": pdf_url,
                        "pdf_texto_extraido": pdf_text,
                        "pdf_resumo": (pdf_text[:500] if pdf_text else ""),
                        "data_publicacao_original": "",
                        "fim_inscricao_original": "",
                        "prazo_submissao_original": "",
                        "metodo_extracao": "html_listing_detail",
                        "url_listagem": listing_url,
                        "url_detalhe": full_url,
                        "palavras_chave_detectadas": [k for k in keywords if k in combined.lower()][:20],
                        "nivel_sensibilidade": "publico_institucional",
                        "necessita_traducao": False,
                        "observacoes": "",
                        "anexos": anexos,
                        "url_pagina": listing_url,
                        "coletado_em": datetime.now().date().isoformat(),
                    },
                }
            )
        if len(all_items) >= max_items:
            break

    return all_items


def save_outputs(
    base_dir,
    output_prefix,
    items,
    *,
    failure_reason=None,
    collection_failed=False,
    allow_empty=False,
):
    output_dir = Path(base_dir) / "outputs"
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"{output_prefix}_editais.json"
    csv_path = output_dir / f"{output_prefix}_editais.csv"

    result = save_output_safely(
        [dict(x) for x in items] if items else [],
        json_path,
        output_prefix,
        allow_empty=allow_empty,
        empty_confirmed_reason=CONFIRMED_EMPTY_REASON if allow_empty else None,
        failure_reason=failure_reason,
        collection_failed=collection_failed,
    )
    if not result.wrote_file:
        return

    if items:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(items[0].keys()))
            writer.writeheader()
            writer.writerows(items)
