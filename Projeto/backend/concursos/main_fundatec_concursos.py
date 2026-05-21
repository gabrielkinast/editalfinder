#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler piloto — Fundatec (notícias em www2.fundatec.org.br/category/concursos/).

- Respeita limites: User-Agent de browser, pausa entre GET, lista curta (--max-items).
- robots.txt da Fundatec costuma vir vazio; mesmo assim usa RobotFileParser quando legível.
- Saída standardized para `scripts/load_concursos_selecao.py` (fonte `fundatec`).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from concursos.common import (  # noqa: E402
    _iso_to_date,
    build_concurso_item,
    extract_inscricao_fim_explicit_br,
    extract_inscricao_fim_from_text,
    extract_prova_from_text,
    field_fill_stats,
    infer_nivel_escolaridade,
    infer_orgao_local_from_title,
    infer_status_concurso,
    infer_tipo_selecao_meta,
    normalize_text,
    parse_all_dates_br,
    parse_remuneracao_taxa_br,
    parse_vagas_certame,
    pci_adjust_confidence_for_ambiguity,
    pci_infer_extraction_confidence,
    pci_infer_qualidade_dado,
    pci_missing_core_fields,
    recency_should_discard,
    validate_concurso_item,
)

BASE = "https://www2.fundatec.org.br"
LISTING_PATH = "/category/concursos/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 EditalFinderConcursosBot/0.1"
)
FONT = "fundatec"

_MESES_PT: Dict[str, int] = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "marco": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

_RE_INSCR_ATE_DIA_PT = re.compile(
    r"(?i)(?:inscri[cç][aã]o|inscri[cç][oõ]es|prazo\s+(?:de\s+)?inscri[cç][aã]o|"
    r"prazo\s+(?:de\s+)?inscri[cç][oõ]es|"
    r"per[ií]odo\s+de\s+inscri[cç][aã]o|per[ií]odo\s+de\s+inscri[cç][oõ]es)[^\n]{0,140}?"
    r"(?:at[eé]|até)\s+(?:o\s+dia\s+)?(\d{1,2})\s+de\s+([a-zçãõáéíóúâêô]+)\s+de\s+(\d{4})",
)
_RE_PROVA_DIA_PT = re.compile(
    r"(?:provas?\s+(?:é|e|ser[aã]|serão|serao|marcad[ao]s?|realizad[ao]s?|realiza[cç][aã]o)|"
    r"realiza[cç][aã]o\s+das\s+provas)[^.]{0,90}?(\d{1,2})\s+de\s+([a-zçãõáéíóúâêô]+)\s+de\s+(\d{4})",
    re.IGNORECASE,
)


def _fetch(url: str) -> str:
    req = Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "pt-BR,pt;q=0.9",
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
        },
    )
    with urlopen(req, timeout=40) as resp:
        return resp.read().decode("utf-8", "replace")


def _collect_post_urls(html: str, robots_parser, listing_url: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    out: List[str] = []
    seen: Set[str] = set()
    for a in soup.find_all("a", href=True):
        h = a["href"].strip().split("#")[0]
        full = urljoin(listing_url, h)
        if not full.startswith(BASE):
            continue
        if not re.search(r"/\d{4}/\d{2}/\d{2}/[^/]+/?$", urlparse(full).path or ""):
            continue
        if full.rstrip("/") in seen:
            continue
        if _robots_disallows(full, robots_parser):
            continue
        seen.add(full.rstrip("/"))
        out.append(full.rstrip("/"))
    return out


def _robots_disallows(url: str, robots_parser) -> bool:
    if robots_parser is None:
        return False
    try:
        return not robots_parser.can_fetch(USER_AGENT, url)
    except Exception:
        return True


def _title_for_geo_infer(titulo: str) -> str:
    """Normaliza títulos Fundatec (sufixo editorial, Município/UF) para infer_orgao_local_from_title."""
    t = normalize_text(titulo)
    t = re.sub(r"\s*-\s*Fundatec\s*$", "", t, flags=re.I)
    t = re.sub(r"/([A-Z]{2})\b", r" - \1", t)
    t = re.sub(r"\s+/([A-Z]{2})\b", r" - \1", t)
    return t


def _iso_from_pt_day_month(day: int, month_name: str, year: int) -> Optional[str]:
    mo = _MESES_PT.get(month_name.strip().lower())
    if not mo:
        return None
    try:
        return date(year, mo, day).isoformat()
    except ValueError:
        return None


def extract_data_fim_inscricao_fundatec(text: str) -> Optional[str]:
    """Só datas de fim de inscrições com contexto explícito (não usa primeira dd/mm/aaaa do texto)."""
    if not text:
        return None
    s = str(text)
    m = _RE_INSCR_ATE_DIA_PT.search(s)
    if m:
        d, mes, y = int(m.group(1)), m.group(2), int(m.group(3))
        hit = _iso_from_pt_day_month(d, mes, y)
        if hit:
            return hit
    ex = extract_inscricao_fim_explicit_br(s)
    if ex:
        return ex
    iso = extract_inscricao_fim_from_text(s)
    if iso:
        return iso
    return None


def extract_data_prova_fundatec(text: str) -> Optional[str]:
    if not text:
        return None
    s = str(text)
    m = _RE_PROVA_DIA_PT.search(s)
    if m:
        d, mes, y = int(m.group(1)), m.group(2), int(m.group(3))
        hit = _iso_from_pt_day_month(d, mes, y)
        if hit:
            return hit
    return extract_prova_from_text(s)


# --- Extração só do artigo principal (evita sidebar / relacionados / widgets) ---

_FUNDATEC_REMOVE_SELECTORS = (
    "aside",
    "nav",
    "footer",
    "header.site-header",
    "script",
    "style",
    "iframe",
    "form",
    ".sidebar",
    "#secondary",
    ".widget-area",
    ".widget",
    "#comments",
    ".comments-area",
    ".comment-respond",
    ".rp4wp-related-posts",
    ".rp4wp-related-post",
    ".related-posts",
    ".jetpack-related-posts",
    ".yarpp-related",
    ".post-navigation",
    ".nav-links",
    ".sharedaddy",
    ".sd-sharing",
)

_RE_FUNDATEC_BOILER_HEADING = re.compile(
    r"(?i)(relacionad|recentes|mais\s+lidas?|coment[aá]rios?|sidebar|newsletter|"
    r"últimas\s+not|ultimas\s+not)",
)


def _resolve_fundatec_main_content_node(soup: BeautifulSoup) -> Optional[Tag]:
    """Preferir conteúdo do post: article .entry-content > article > .entry-content > .post-content > main."""
    art = soup.find("article")
    if art:
        inner = art.select_one(".entry-content") or art.select_one(".post-content")
        if inner:
            return inner
        return art
    for sel in ("div.entry-content", "div.post-content", "main"):
        n = soup.select_one(sel)
        if n:
            return n
    return soup.find("body")


def _clone_main_node_strip_chaff(node: Tag) -> Tag:
    """Clone do nó principal com remoção de blocos típicos de WP fora do texto do post."""
    wrapper = BeautifulSoup(
        f'<div class="_fundatec_main_clone">{node.decode_contents()}</div>',
        "html.parser",
    )
    root = wrapper.find("div", class_="_fundatec_main_clone")
    if root is None:
        root = wrapper

    for sel in _FUNDATEC_REMOVE_SELECTORS:
        for el in root.select(sel):
            el.decompose()

    for bad in root.find_all(class_=re.compile(r"(?i)related|recent|sidebar|widget|comments", re.I)):
        bad.decompose()

    for hx in root.find_all(re.compile(r"^h[1-6]$")):
        if _RE_FUNDATEC_BOILER_HEADING.search(hx.get_text(" ", strip=True) or ""):
            hx.decompose()

    for fig in root.find_all("figure", class_=re.compile(r"(?i)gallery|wp-block", re.I)):
        cap = fig.get("class") or []
        if any("related" in str(c).lower() for c in cap):
            fig.decompose()

    return root


def _fundatec_title_text(soup: BeautifulSoup, main_clone: Tag) -> str:
    og = soup.find("meta", property="og:title")
    if og and og.get("content"):
        return normalize_text(og.get("content"))
    t = soup.find("title")
    if t and t.get_text(strip=True):
        return normalize_text(t.get_text())
    h1_art = main_clone.find("h1") if main_clone else None
    if h1_art and h1_art.get_text(strip=True):
        return normalize_text(h1_art.get_text())
    h1 = soup.find("h1")
    if h1:
        return normalize_text(h1.get_text())
    return ""


def extract_fundatec_article_text(soup: BeautifulSoup) -> Tuple[str, str, Tag, List[str]]:
    """
    Extrai título e texto só do corpo principal do artigo (sem sidebar/footer/widgets).
    Retorna (title_text, article_text_main_only, clone_tag_para_links, notas).
    """
    notes: List[str] = []
    main = _resolve_fundatec_main_content_node(soup)
    if main is None:
        notes.append("fundatec_sem_bloco_principal_html")
        empty_soup = BeautifulSoup("<div></div>", "html.parser")
        empty_root = empty_soup.find("div")
        if empty_root is None:
            empty_root = empty_soup.new_tag("div")
        return "", "", empty_root, notes

    clone = _clone_main_node_strip_chaff(main)
    body = normalize_text(clone.get_text(" ", strip=True))[:16000]
    tit = _fundatec_title_text(soup, clone)
    if not body.strip():
        notes.append("fundatec_corpo_principal_vazio_apos_limpeza")
    return tit, body, clone, notes


def _pick_portal_concurso_link_from_node(root: Tag, page_url: str) -> Optional[str]:
    """Primeiro link portal Fundatec dentro do fragmento do artigo."""
    for a in root.find_all("a", href=True):
        h = urljoin(page_url, a["href"].strip()).split("#")[0]
        low = h.lower()
        if "facebook.com" in low or "twitter.com" in low or "linkedin.com" in low:
            continue
        if "mailto:" in low:
            continue
        if "fundatec.org.br/portal/concursos" in low or "index_concursos.php" in low:
            return h
    return None


_RE_NOTICIA_PASSADA_OU_NAO_OPORTUNIDADE = (
    r"prova\s+(?:foi\s+)?realizada",
    r"provas?\s+foram\s+realizadas",
    r"foi\s+realizada\s+a\s+prova",
    r"candidatos?\s+particip",
    r"\bparticipam\b",
    r"\bmil\s+candidatos\b",
    r"\bresultado\b",
    r"\bgabarito\b",
    r"homologa[cç][aã]o",
    r"convoca[cç][aã]o",
)


def fundatec_should_discard_non_opportunity(
    *,
    titulo: str,
    body: str,
    link_edital: Optional[str],
    data_fim_inscricao: Optional[str],
    today: date,
) -> Tuple[bool, str]:
    """
    Descarta notícias de prova/resultado/passado que não são oportunidade ativa.
    Mantém se houver data_fim_inscricao futura (inscrições ainda relevantes).
    """
    blob = f"{titulo}\n{body}".lower()
    df = _iso_to_date(data_fim_inscricao)
    if df is not None and df >= today:
        return False, ""

    if re.search(r"(?i)retifica[cç][aã]o", blob) and not link_edital:
        return True, "noticia_nao_oportunidade_ativa"

    if re.search(r"(?i)\bdomingo\s*,\s*\d{1,2}\b", blob) and re.search(
        r"(?i)(foi\s+realizada|foram\s+realizadas?|prova\s+(?:foi\s+)?realizada|realiza[cç][aã]o\s+das?\s+provas)",
        blob,
    ):
        return True, "noticia_nao_oportunidade_ativa"

    if not link_edital:
        tit_l = (titulo or "").lower()
        if re.search(r"(?i)\b(resultado|gabarito|homologa[cç][aã]o|convoca[cç][aã]o)\b", tit_l):
            return True, "noticia_nao_oportunidade_ativa"

    for pat in _RE_NOTICIA_PASSADA_OU_NAO_OPORTUNIDADE:
        if re.search(pat, blob):
            return True, "noticia_nao_oportunidade_ativa"
    return False, ""


def fundatec_strip_vagas_salario_if_low_trust(
    *,
    link_edital: Optional[str],
    data_fim_inscricao: Optional[str],
    numero_vagas: Optional[int],
    salario_min: Optional[float],
    salario_max: Optional[float],
    taxa_inscricao: Optional[float],
) -> Tuple[Optional[int], Optional[float], Optional[float], Optional[float], List[str]]:
    """Sem portal oficial e sem data fim: não propagar vagas/salário/taxa (evita lixo de layout)."""
    notes: List[str] = []
    if link_edital is None and data_fim_inscricao is None:
        if (
            numero_vagas is not None
            or salario_min is not None
            or salario_max is not None
            or taxa_inscricao is not None
        ):
            notes.append("valores_suprimidos_sem_link_oficial_nem_data_fim")
        return None, None, None, None, notes
    return numero_vagas, salario_min, salario_max, taxa_inscricao, notes


def parse_post_page(url: str) -> Dict[str, Any]:
    html = _fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    tit, body, frag, article_notes = extract_fundatec_article_text(soup)
    if not tit:
        tit = url

    data_fim = extract_data_fim_inscricao_fundatec(body)
    data_prova = extract_data_prova_fundatec(body)
    dates_iso = parse_all_dates_br(body)
    data_pub = dates_iso[0].isoformat() if dates_iso else None

    vagas, vagas_notes = parse_vagas_certame(
        body,
        scan_limit=5000,
        paragraph_scope=True,
        title_for_crosscheck=tit,
    )
    sal_min, sal_max, taxa, money_meta = parse_remuneracao_taxa_br(body)
    portal = _pick_portal_concurso_link_from_node(frag, url)

    return {
        "titulo": tit,
        "body": body,
        "data_fim_inscricao": data_fim,
        "data_prova": data_prova,
        "data_publicacao": data_pub,
        "numero_vagas": vagas,
        "salario_min": sal_min,
        "salario_max": sal_max,
        "taxa_inscricao": taxa,
        "money_meta": money_meta,
        "vagas_extraction_notes": vagas_notes,
        "article_extraction_notes": article_notes,
        "link_edital": portal,
    }


def run_crawl(*, max_items: int, sleep_s: float, listing_url: str) -> Dict[str, Any]:
    from urllib.robotparser import RobotFileParser

    rp: Optional[Any] = None
    for robots_url in (urljoin(BASE, "/robots.txt"), "https://www.fundatec.org.br/robots.txt"):
        try:
            r2 = RobotFileParser()
            r2.set_url(robots_url)
            r2.read()
            rp = r2
            break
        except Exception:
            continue

    if _robots_disallows(listing_url, rp):
        raise RuntimeError(f"robots.txt bloqueia listagem: {listing_url}")

    listing_html = _fetch(listing_url)
    urls = _collect_post_urls(listing_html, rp, listing_url)[: max(max_items * 3, 20)]
    today = date.today()
    raw_rows: List[Dict[str, Any]] = []
    discarded: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []

    for url in urls:
        if len(raw_rows) >= max_items:
            break
        if _robots_disallows(url, rp):
            discarded.append({"url": url, "motivo": "robots_disallow"})
            continue
        try:
            time.sleep(sleep_s)
            parsed = parse_post_page(url)
            tit = parsed["titulo"]
            body = parsed["body"]
            data_fim = parsed["data_fim_inscricao"]
            data_prova = parsed["data_prova"]
            data_pub = parsed["data_publicacao"]
            vagas = parsed["numero_vagas"]
            sal_min = parsed["salario_min"]
            sal_max = parsed["salario_max"]
            taxa = parsed["taxa_inscricao"]
            money_meta = parsed.get("money_meta") or {}
            off = parsed["link_edital"]

            drop_no, why_no = fundatec_should_discard_non_opportunity(
                titulo=tit,
                body=body,
                link_edital=off,
                data_fim_inscricao=data_fim,
                today=today,
            )
            if drop_no:
                discarded.append({"url": url, "titulo": tit, "motivo": why_no})
                continue

            drop, why = recency_should_discard(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
                text_for_recent_heuristic=f"{tit} {body}",
            )
            if drop:
                discarded.append({"url": url, "titulo": tit, "motivo": why})
                continue

            vagas, sal_min, sal_max, taxa, strip_notes = fundatec_strip_vagas_salario_if_low_trust(
                link_edital=off,
                data_fim_inscricao=data_fim,
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
            )

            tipo, tipo_evid = infer_tipo_selecao_meta(tit, body)
            status = infer_status_concurso(
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                today=today,
            )
            if data_fim and off:
                validacao = "valido"
            elif off and not data_fim:
                validacao = "incompleto"
            else:
                validacao = "incompleto"

            geo = infer_orgao_local_from_title(_title_for_geo_infer(tit))
            orgao = geo["orgao"]
            instituicao = geo["instituicao"]
            municipio = geo["municipio"]
            estado = geo["estado"]
            nivel = infer_nivel_escolaridade(tit, body)

            extracted_fields: List[str] = []
            if orgao:
                extracted_fields.append("orgao_title")
            if instituicao:
                extracted_fields.append("instituicao_title")
            if municipio:
                extracted_fields.append("municipio_title")
            if estado:
                extracted_fields.append("estado_title")
            if nivel:
                extracted_fields.append("nivel_escolaridade_texto")
            if vagas is not None:
                extracted_fields.append("numero_vagas_texto")
            if sal_min is not None or sal_max is not None:
                extracted_fields.append("salario_texto")
            if taxa is not None:
                extracted_fields.append("taxa_inscricao_texto")
            if data_fim:
                extracted_fields.append("data_fim_inscricao_texto")
            if data_prova:
                extracted_fields.append("data_prova_texto")

            partial_core: Dict[str, Any] = {
                "data_fim_inscricao": data_fim,
                "data_prova": data_prova,
                "orgao": orgao,
                "estado": estado,
                "instituicao": instituicao,
                "link_edital": off,
                "numero_vagas": vagas,
            }
            missing_core = pci_missing_core_fields(partial_core)
            confidence = pci_infer_extraction_confidence(
                orgao=orgao,
                instituicao=instituicao,
                estado=estado,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                numero_vagas=vagas,
                salario_max=sal_max,
            )
            qualidade = pci_infer_qualidade_dado(
                titulo=tit,
                link=url,
                orgao=orgao,
                instituicao=instituicao,
                estado=estado,
                municipio=municipio,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                data_publicacao=data_pub,
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
            )
            if off is None and not data_fim:
                qualidade = "baixa"
            elif not data_fim and off:
                qualidade = "media"

            notes = list(money_meta.get("value_extraction_notes") or [])
            notes.extend(parsed.get("vagas_extraction_notes") or [])
            notes.extend(parsed.get("article_extraction_notes") or [])
            notes.extend(strip_notes)
            if not off:
                notes.append("portal_concurso_nao_encontrado_no_html")
            confidence = pci_adjust_confidence_for_ambiguity(confidence, value_extraction_notes=notes)

            extras: Dict[str, Any] = {
                "crawler": "main_fundatec_concursos",
                "wave": "concursos_wave1_fundatec",
                "fetched_at_utc": datetime.now(timezone.utc).isoformat(),
                "fundatec_noticia_url": url,
                "fundatec_listing_url": listing_url,
                "official_link_missing": off is None,
                "extracted_fields": sorted(set(extracted_fields)),
                "missing_core_fields": missing_core,
                "extraction_confidence": confidence,
                "source_is_aggregator": False,
                "value_extraction_notes": notes,
                "tipo_selecao_evidencia": tipo_evid,
                "possible_fee_detected": bool(money_meta.get("possible_fee_detected")),
                "possible_salary_detected": bool(money_meta.get("possible_salary_detected")),
            }

            row = build_concurso_item(
                titulo=tit[:500],
                link=url,
                fonte=FONT,
                fonte_tipo="banca",
                tipo_selecao=tipo,
                status=status,
                validacao_status=validacao,
                qualidade_dado=qualidade,
                extras=extras,
                categoria="banca_fundatec_noticia",
                orgao=orgao,
                instituicao=instituicao,
                banca="Fundatec",
                cargo=None,
                area=None,
                nivel_escolaridade=nivel,
                estado=estado,
                municipio=municipio,
                numero_vagas=vagas,
                salario_min=sal_min,
                salario_max=sal_max,
                taxa_inscricao=taxa,
                data_publicacao=data_pub,
                data_inicio_inscricao=None,
                data_fim_inscricao=data_fim,
                data_prova=data_prova,
                link_edital=off,
                tags=["fundatec", "wave1"],
            )
            verr = validate_concurso_item(row)
            if verr:
                errors.append({"url": url, "erros": verr})
                continue
            raw_rows.append(row)
        except Exception as exc:
            errors.append({"url": url, "erro": str(exc)})

    filled, missing = field_fill_stats(raw_rows)
    return {
        "fonte": FONT,
        "collected_at_utc": datetime.now(timezone.utc).isoformat(),
        "listing_url": listing_url,
        "total_bruto_urls": len(urls),
        "total_discarded_all": len(discarded),
        "discarded": discarded[:120],
        "total_standardized": len(raw_rows),
        "errors": errors,
        "field_fill": filled,
        "fields_always_missing": missing,
        "standardized": raw_rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Crawler piloto Fundatec → standardized JSON")
    ap.add_argument("--max-items", type=int, default=8, help="Máximo de notícias gravadas após filtros")
    ap.add_argument("--sleep", type=float, default=2.0, help="Pausa entre GET (segundos)")
    ap.add_argument(
        "--listing-url",
        default=BASE + LISTING_PATH,
        help="URL da listagem (categoria concursos)",
    )
    ap.add_argument(
        "--output-root",
        type=str,
        default=str(ROOT / "audit_reports_main_pipeline/concursos_wave1_fundatec"),
        help="Pasta wave1 Fundatec",
    )
    args = ap.parse_args()

    out_root = Path(args.output_root)
    std_dir = out_root / "standardized"
    std_dir.mkdir(parents=True, exist_ok=True)
    std_path = std_dir / f"{FONT}_standardized.json"

    try:
        report = run_crawl(max_items=args.max_items, sleep_s=args.sleep, listing_url=args.listing_url)
    except Exception as exc:
        err_payload = {"erro": str(exc), "listing_url": args.listing_url}
        out_root.mkdir(parents=True, exist_ok=True)
        (out_root / "crawler_summary.json").write_text(
            json.dumps(err_payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (out_root / "crawler_summary.md").write_text(
            f"# Crawler Fundatec — falha\n\n```json\n{json.dumps(err_payload, ensure_ascii=False, indent=2)}\n```\n"
        )
        print(f"[ERRO] {exc}", file=sys.stderr)
        return 1

    rows = report.pop("standardized")
    std_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    discarded = report.get("discarded", [])
    summary = {
        **report,
        "standardized_path": str(std_path.resolve()),
        "exemplos_payload": rows[:3],
    }
    (out_root / "crawler_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md = [
        "# Crawler piloto — Fundatec (notícias)",
        "",
        f"- **Fonte:** `{FONT}`",
        f"- **Listagem:** `{args.listing_url}`",
        f"- **Coleta (UTC):** `{summary['collected_at_utc']}`",
        f"- **URLs brutas (listagem):** {summary.get('total_bruto_urls', 0)}",
        f"- **Descartados:** {summary.get('total_discarded_all', 0)}",
        f"- **Standardized:** {summary.get('total_standardized', 0)}",
        f"- **Ficheiro:** `{std_path.as_posix()}`",
        "",
        "## Campos preenchidos",
        "",
        "```json",
        json.dumps(summary.get("field_fill", {}), ensure_ascii=False, indent=2),
        "```",
        "",
        "## Riscos",
        "",
        "- Conteúdo editorial; `link_edital` aponta para o portal de concursos Fundatec quando encontrado.",
        "- `parse_vagas` não lê números por extenso (ex.: “três vagas”).",
        "",
        "## Próximo passo",
        "",
        "`python scripts/load_concursos_selecao.py --dry-run --input-dir .../standardized --output-dir .../loader_dryrun_v4 --sources fundatec`",
        "",
    ]
    (out_root / "crawler_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(std_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
