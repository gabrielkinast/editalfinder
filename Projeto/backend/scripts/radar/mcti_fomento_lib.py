"""
MCTI Fomento — crawl e standardização para Radar/Editais (sem public.noticia).
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "EditalFinderBot/1.0 (+public scientific/news monitoring)",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Connection": "close",
}

SOURCE_ID = "mcti_fomento_transformacao_digital"
ORGAO = "Ministério da Ciência, Tecnologia e Inovação"
FONTE = "MCTI"
AREA_DEFAULT = ["Transformação Digital", "Fomento", "Ciência e Tecnologia"]

SEEDS: Tuple[str, ...] = (
    "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/transformacaodigital/fomento-1",
    "https://www.gov.br/mcti/pt-br/acesso-a-informacao/editais/",
    "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/chamamento-oceano",
    "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/bolsa-cientifica",
    "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/chamamento-vacina",
)

EXCLUDE_LINK_SUBSTRINGS = (
    "governodigital.pt-br",
    "/search?",
    "searchabletext=",
    "facebook.com",
    "twitter.com",
    "instagram.com",
    "youtube.com",
    "whatsapp.com",
    "linkedin.com",
    "sharer.php",
    "compartilhe por",
    "copiar para área de transferência",
)

SOCIAL_TITLE_MARKERS = (
    "compartilhe por",
    "compartilhe:",
    "link para copiar",
)

EXCLUDE_FROM_STANDARDIZED = (
    "consultar minhas solicitações",
    "consultar as minhas",
)

# --- Curadoria v2: menu/navegação gov.br (não são oportunidades) ---
INSTITUCIONAL_TITLE_BLOCKLIST: Tuple[str, ...] = (
    "assuntos",
    "acesso à informação",
    "acesso a informacao",
    "institucional",
    "o ministério",
    "o ministerio",
    "a ministra",
    "agenda de autoridades",
    "base jurídica",
    "base juridica",
    "competências",
    "competencias",
    "ouvidoria",
    "corregedoria",
    "desenvolvimento de pessoas",
    "estrutura organizacional",
    "ações e programas",
    "acoes e programas",
    "carta de serviços",
    "carta de servicos",
    "renúncia de receitas",
    "renuncia de receitas",
    "servidores",
    "pgd",
    "ppa",
    "cct",
    "fndct",
    "sirene",
    "indicadores",
    "clima",
    "bens sensíveis",
    "bens sensiveis",
    "legislação",
    "legislacao",
    "semicondutores",
    "padis",
    "lei do bem",
    "propriedade intelectual",
    "popularização da ciência",
    "popularizacao da ciencia",
    "fale com",
    "imagens",
    "sobre",
    "teste",
    "transformação digital",
    "transformacao digital",
    "oceano e antártica",
    "oceano e antartica",
    "editais",
    "licitações e contratos",
    "licitacoes e contratos",
    "participação social",
    "participacao social",
    "contratos de gestão",
    "contratos de gestao",
    "composição",
    "composicao",
    "comissão de ética",
    "comissao de etica",
    "agenda de autoridades",
    "fundo de amparo ao trabalhador",
)

INSTITUCIONAL_URL_SEGMENTS: Tuple[str, ...] = (
    "/assuntos/",
    "/institucional",
    "/ouvidoria",
    "/corregedoria",
    "/servidores",
    "/ppa/",
    "/cct/",
    "/fndct",
    "/sirene",
    "/padis/",
    "/pgd/",
    "/clima/",
    "/semicondutor",
    "/lei-do-bem",
    "/propriedade-intelectual",
    "/popularizacao",
    "/popularização",
    "/indicadores/",
    "/bens-sensiveis",
    "/legislacao/",
    "/legislação/",
    "/acoes-e-programas",
    "/carta-de-servicos",
    "/renuncia-de-receitas",
    "/desenvolvimento-de-pessoas",
    "/estrutura-organizacional",
    "/agenda-de-autoridades",
    "/base-juridica",
    "/competencias",
    "/composicao",
    "/comissao-de-etica",
    "/a-ministra",
    "/o-ministerio",
    "/fale-com",
    "/imagens/",
    "/sobre/",
    "/teste/",
    "/noticias/",
    "/licitacoes-e-contratos",
    "/contratos-de-gestao-organizacoes-sociais/",
    "/participacao-social",
)

# Allowlist forte — sinal de oportunidade real
OPPORTUNITY_ALLOWLIST_KEYWORDS: Tuple[str, ...] = (
    "chamamento",
    "chamada pública",
    "chamada publica",
    "edital",
    "bolsa científica",
    "bolsa cientifica",
    "bolsa cient",
    "chamamento oceano",
    "chamamento vacina",
    "bolsa cientifica",
    "lei das tics",
    "lei de tics",
    "lei-de-tics",
    "ppi",
    "subvenção",
    "subvencao",
    "seleção pública",
    "selecao publica",
    "processo seletivo",
    "inscrições abertas",
    "inscricoes abertas",
    "habilitação de propostas",
    "habilitacao de propostas",
    "convocação",
    "convocacao",
    "resultado",
    "retificação",
    "retificacao",
    "portaria",
    "comunicado",
    "documentos relacionados",
    "documento relacionado",
    "emendas",
    "câmara 4.0",
    "camara 4.0",
    "transformação digital",
    "transformacao digital",
)

OPPORTUNITY_PATH_ALLOWLIST: Tuple[str, ...] = (
    "/acompanhe-o-mcti/chamamento-oceano",
    "/acompanhe-o-mcti/chamamento-vacina",
    "/acompanhe-o-mcti/bolsa-cientifica",
    "/acompanhe-o-mcti/lei-de-tics",
    "/acesso-a-informacao/editais/edital",
    "/acesso-a-informacao/editais/edital-",
)

# Subpastas temáticas de Transformação Digital (menu, não chamada ativa)
TRANSFORMACAO_DIGITAL_DENY_SLUGS: Tuple[str, ...] = (
    "capacitacao-tecnologica",
    "comunicacoes-avancadas",
    "cooperacao-internacional",
    "e-digital",
    "estrategia-brasileira-de-inteligencia-artificial",
    "estrategia-brasileira",
    "internet-das-coisas",
    "observatorio-de-tecnologias-digitais",
    "plano-brasileiro-de-inteligencia-artificial",
    "seguranca-cibernetica",
    "arquivos-internet-das-coisas",
    "oceano-e-antartica",
)

PDF_CONTEXT_KEYWORDS: Tuple[str, ...] = (
    "edital",
    "chamamento",
    "chamada",
    "programa",
    "anexo",
    "fomento",
    "bolsa",
    "vacina",
    "oceano",
    "portaria",
    "resultado",
    "retific",
    "comunicado",
    "emenda",
    "subvenc",
    "selecao",
    "seleção",
)

REVIEW_TITLE_MARKERS: Tuple[str, ...] = (
    "documentos relacionados",
    "documento relacionado",
    "comunicado",
    "perguntas e repostas",
    "perguntas e respostas",
    "fique por dentro",
    "saiba mais",
)

# --- Curadoria v3 (conservadora): pronto_para_apply | review | institucional_latente | descartado_ruido ---
NIVEL_PRONTO = "pronto_para_apply"
NIVEL_REVIEW = "review"
NIVEL_INSTITUCIONAL = "institucional_latente"
NIVEL_DESCARTADO = "descartado_ruido"

STRONG_SIGNAL_KEYWORDS: Tuple[str, ...] = (
    "edital",
    "chamamento",
    "chamada-publica",
    "chamada publica",
    "selecao publica",
    "selecao publica",
    "resultado",
    "portaria",
    "bolsa cientifica",
    "bolsa-cientifica",
    "chamamento-vacina",
    "chamamento-oceano",
    "vacinas",
)

PDF_V3_ALLOW_KEYWORDS: Tuple[str, ...] = (
    "edital",
    "chamamento",
    "chamada",
    "selecao",
    "resultado",
    "portaria",
    "termo de referencia",
    "termo-de-referencia",
    "comunicado",
)

PDF_V3_SOFT_DENY: Tuple[str, ...] = (
    "estudo",
    "cartilha",
    "relatorio",
    "apresentacao",
    "parecer",
    "publicizacao",
    "duvidas",
    "salvamento",
)

HUB_PAGE_TITLES: Tuple[str, ...] = (
    "chamamento oceano",
    "chamamento vacinas nacionais",
    "bolsa cientifica",
    "bolsa científica",
    "bolsa cientifica",
)

GENERIC_PROGRAM_PATH_MARKERS: Tuple[str, ...] = (
    "/transformacaodigital",
    "/oceano-e-antartica",
    "/acoes-e-programas",
    "/contratos-de-gestao",
    "/lei-do-bem",
    "/padis",
    "/fndct",
    "/cct/",
    "/sirene",
)


def _http_get(url: str, timeout: int = 90, retries: int = 4) -> Optional[requests.Response]:
    session = requests.Session()
    session.headers.update(HEADERS)
    for i in range(retries):
        try:
            r = session.get(url, timeout=timeout)
            if r.status_code < 400 and len(r.text or "") > 200:
                return r
        except Exception:
            pass
        if i < retries - 1:
            time.sleep(2.0 * (i + 1))
    return None


def _norm_title(titulo: str) -> str:
    t = re.sub(r"\s+", " ", (titulo or "").strip().lower())
    t = t.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    t = t.replace("ã", "a").replace("õ", "o").replace("ç", "c").replace("â", "a").replace("ê", "e")
    return t


def _title_blocklist_hit(titulo: str) -> Optional[str]:
    nt = _norm_title(titulo)
    if not nt:
        return None
    for blocked in INSTITUCIONAL_TITLE_BLOCKLIST:
        bn = _norm_title(blocked)
        if nt == bn or nt.startswith(bn + " ") or nt.endswith(" " + bn):
            return blocked
        if len(bn) >= 8 and bn in nt and len(nt) <= len(bn) + 25:
            return blocked
    return None


def _url_blocklist_hit(link: str) -> Optional[str]:
    path = urlparse(link).path.lower()
    if path.endswith("/acesso-a-informacao") or path.rstrip("/").endswith("/editais"):
        return "indice_acesso_informacao_ou_editais"
    if "/acesso-a-informacao/" in path and "/editais/" not in path:
        return "secao_transparencia_sem_edital"
    for seg in INSTITUCIONAL_URL_SEGMENTS:
        if seg in path:
            return seg.strip("/")
    return None


def _path_allowlist_hit(link: str) -> bool:
    path = urlparse(link).path.lower()
    if path.rstrip("/").endswith("/fomento-1"):
        return False
    if path.rstrip("/").endswith("/transformacaodigital"):
        return False
    if "/oceano-e-antartica" in path and "chamamento-oceano" not in path:
        return False
    for deny in TRANSFORMACAO_DIGITAL_DENY_SLUGS:
        if f"/{deny}" in path or path.rstrip("/").endswith(f"/{deny}"):
            return False
    if "/transformacaodigital/" in path:
        if any(
            k in path
            for k in (
                "fomento",
                "arquivos",
                "emendas",
                "iniciativas",
                "chamamento",
                "edital",
                "bolsa",
            )
        ):
            return True
        return False
    for seg in OPPORTUNITY_PATH_ALLOWLIST:
        if seg in path:
            return True
    return False


def _text_allowlist_hit(titulo: str, link: str, contexto: str = "") -> bool:
    blob = _norm_title(f"{titulo} {link} {contexto}")
    if not any(_norm_title(kw) in blob for kw in OPPORTUNITY_ALLOWLIST_KEYWORDS):
        return False
    weak_only = ("oceano", "vacina", "fomento", "transformacao digital", "oceano e antartica")
    if any(w in blob for w in weak_only) and not _path_allowlist_hit(link):
        strong = (
            "chamamento",
            "edital",
            "chamada publica",
            "bolsa",
            "selecao publica",
            "processo seletivo",
            "comunicado",
            "resultado",
            "portaria",
            "subvencao",
            "ppi",
            "lei das tics",
            "emenda",
        )
        return any(s in blob for s in strong)
    return True


def _pdf_allowed(titulo: str, link: str, contexto: str = "") -> bool:
    if not link.lower().endswith(".pdf") and ".pdf" not in link.lower():
        return True
    blob = _norm_title(f"{titulo} {link} {contexto}")
    return any(k in blob for k in PDF_CONTEXT_KEYWORDS)


def evaluate_curation(
    titulo: str,
    link: str,
    contexto: str = "",
    classificacao: str = "",
) -> Tuple[str, str, Optional[str]]:
    """
    decision: queue | institucional_latente | descartado_ruido
    Retorna (decision, motivo, classificacao_ajustada).
    """
    titulo = re.sub(r"\s+", " ", (titulo or "")).strip()
    link = _normalize_link(link)
    ctx = contexto or ""

    if not link.startswith("http"):
        return "descartado_ruido", "link_invalido", None
    if not _is_mcti_opportunity_link(link):
        return "descartado_ruido", "fora_dominio_mcti", None

    tb = _title_blocklist_hit(titulo)
    if tb:
        return "institucional_latente", f"blocklist_titulo:{tb}", None

    ub = _url_blocklist_hit(link)
    if ub:
        return "institucional_latente", f"blocklist_url:{ub}", None

    if any(x in titulo.lower() for x in SOCIAL_TITLE_MARKERS):
        return "descartado_ruido", "link_social_ou_compartilhamento", None

    if any(x in titulo.lower() for x in EXCLUDE_FROM_STANDARDIZED):
        return "descartado_ruido", "titulo_excluido_operacional", None

    is_pdf = link.lower().endswith(".pdf") or ".pdf" in link.lower()
    if is_pdf and not _pdf_allowed(titulo, link, ctx):
        return "descartado_ruido", "pdf_sem_sinal_edital_chamamento_fomento", None

    path_ok = _path_allowlist_hit(link)
    text_ok = _text_allowlist_hit(titulo, link, ctx)

    if not path_ok and not text_ok:
        if _is_institutional_index(link, titulo):
            return "institucional_latente", "indice_institucional", None
        return "descartado_ruido", "fora_allowlist_oportunidade", None

    cls = classificacao or ""
    if not cls or cls in ("institucional_latente", "excluded", "noticia"):
        cls, _ = classify_link(titulo, link, ctx)

    if cls not in ("radar_oportunidade", "edital_chamada"):
        if cls == "institucional_latente":
            return "institucional_latente", "classificacao_institucional", None
        return "descartado_ruido", f"classificacao_{cls}", None

    if is_pdf:
        if any(k in _norm_title(titulo + link + ctx) for k in ("edital", "chamamento", "chamada", "portaria", "resultado")):
            cls = "edital_chamada"
        else:
            cls = "radar_oportunidade"

    return "queue", "allowlist_ok", cls


def _is_institutional_index(link: str, titulo: str = "") -> bool:
    if _title_blocklist_hit(titulo):
        return True
    if _url_blocklist_hit(link):
        return True
    path = urlparse(link).path.lower().rstrip("/")
    if path.endswith("/acesso-a-informacao") or path.endswith("/editais"):
        return True
    if "/acesso-a-informacao/" in path and "/editais/" not in path:
        return True
    return False


def _is_mcti_opportunity_link(link: str) -> bool:
    low = (link or "").lower()
    if not low.startswith("http"):
        return False
    for ex in EXCLUDE_LINK_SUBSTRINGS:
        if ex in low:
            return False
    if "gov.br/mcti" in low:
        return True
    if low.endswith(".pdf") and "/mcti/" in low:
        return True
    return False


def _pdf_belongs_to_page(page_link: str, pdf_href: str) -> bool:
    page_path = urlparse(page_link).path.lower()
    pdf_path = urlparse(pdf_href).path.lower()
    for pat in (r"/acompanhe-o-mcti/([^/]+)", r"/acesso-a-informacao/editais/([^/]+)"):
        m = re.search(pat, page_path)
        if m:
            slug = m.group(1)
            if f"/{slug}/" in pdf_path or pdf_path.rstrip("/").endswith(f"/{slug}"):
                return True
    base = page_path.rstrip("/")
    if base and (pdf_path.startswith(base) or base in pdf_path):
        return True
    return False


def _normalize_link(link: str) -> str:
    u = (link or "").strip().split("#", 1)[0].rstrip("/")
    if u.startswith("http://"):
        u = "https://" + u[7:]
    return u


def _parse_date(v: Any) -> Optional[datetime]:
    if not v:
        return None
    s = str(v).strip()
    if not s:
        return None
    for pat in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            if pat == "%Y-%m-%d":
                return datetime.strptime(s[:10], pat).replace(tzinfo=timezone.utc)
            return datetime.strptime(s[:10], "%d/%m/%Y" if "/" in s[:10] else pat).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    try:
        dt = parsedate_to_datetime(s)
        if dt:
            return dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    m = re.search(r"\b(\d{2})/(\d{2})/(20\d{2})\b", s)
    if m:
        try:
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)), tzinfo=timezone.utc)
        except ValueError:
            return None
    m2 = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", s)
    if m2:
        try:
            return datetime(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)), tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _iso_date(dt: Optional[datetime]) -> Optional[str]:
    return dt.date().isoformat() if dt else None


def _strip_html(text: Any, max_len: int = 2400) -> str:
    if text is None:
        return ""
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", str(text))
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if max_len and len(t) > max_len:
        t = t[: max_len - 1].rsplit(" ", 1)[0] + "…"
    return t


def classify_link(titulo: str, link: str, contexto: str = "") -> Tuple[str, str]:
    """radar_oportunidade | edital_chamada | institucional_latente | noticia | excluded"""
    b = f"{titulo} {link} {contexto}".lower()
    path = urlparse(link).path.lower()
    low = link.lower()

    for ex in EXCLUDE_LINK_SUBSTRINGS:
        if ex in low:
            return "excluded", "url_bloqueada"

    if not low.startswith("http"):
        return "excluded", "link_invalido"
    if "gov.br/mcti" not in low and not (low.endswith(".pdf") and "ita.br" not in low):
        if "in.gov.br" in low and "edital" in b:
            pass
        elif "gov.br/mcti" not in low:
            return "excluded", "fora_dominio_mcti"

    if link.lower().endswith(".pdf") or ".pdf" in link.lower():
        if not _pdf_allowed(titulo, link, contexto):
            return "institucional_latente", "pdf_sem_contexto"
        if any(k in b for k in ("edital", "chamamento", "chamada", "retific", "resultado", "portaria")):
            return "edital_chamada", "pdf_edital"
        if any(k in b for k in ("programa", "fomento", "bolsa", "vacina", "oceano", "emenda")):
            return "radar_oportunidade", "pdf_programa"
        return "institucional_latente", "pdf_sem_sinal"

    if any(k in b for k in ("edital de chamamento", "edital nº", "edital no", "edital de chamada")):
        return "edital_chamada", "titulo_edital"
    if "/acesso-a-informacao/editais/edital" in path:
        return "edital_chamada", "repositorio_edital"
    if path.endswith("/editais") or path.endswith("/editais/"):
        return "institucional_latente", "indice_editais"

    if "/noticias/" in path and re.search(r"/noticias/[^/]+", path):
        return "noticia", "secao_noticias"

    if "chamamento" in path or "chamamento" in b:
        if "comunicado" in path or "comunicado" in b:
            return "radar_oportunidade", "comunicado_processo"
        return "radar_oportunidade", "programa_chamamento"

    if any(k in path for k in ("bolsa-cientifica", "chamamento-vacina", "lei-de-tics")):
        return "radar_oportunidade", "programa_mcti"
    if "transformacaodigital" in path and not path.rstrip("/").endswith("fomento-1"):
        return "radar_oportunidade", "transformacao_digital"

    if any(k in b for k in ("licitação", "licitacao", "pregão", "pregao")):
        if "/licitacoes" in path:
            return "edital_chamada", "licitacao"
        return "institucional_latente", "licitacao_generica"

    if "/contratos-de-gestao" in path:
        return "institucional_latente", "contrato_gestao_os"

    if path.rstrip("/").endswith(("fomento-1", "/fomento")):
        return "institucional_latente", "hub_fomento"

    if "gov.br/mcti" in low:
        return "institucional_latente", "pagina_mcti_generica"

    return "excluded", "sem_classificacao"


def _should_queue(
    cls: str,
    titulo: str,
    link: str,
    contexto: str = "",
    *,
    strict: bool = True,
) -> bool:
    if strict:
        decision, _, _ = evaluate_curation(titulo, link, contexto, cls)
        return decision == "queue"
    if cls not in ("radar_oportunidade", "edital_chamada"):
        return False
    if not _is_mcti_opportunity_link(link):
        return False
    tl = titulo.lower()
    if any(x in tl for x in EXCLUDE_FROM_STANDARDIZED):
        return False
    if any(x in tl for x in SOCIAL_TITLE_MARKERS):
        return False
    return True


def _record_discard(
    descartados: List[Dict[str, Any]],
    titulo: str,
    link: str,
    decision: str,
    motivo: str,
    origem: str,
    classificacao: str = "",
) -> None:
    descartados.append(
        {
            "titulo": titulo[:320],
            "link": _normalize_link(link),
            "classificacao_original": classificacao or None,
            "decisao": decision,
            "motivo": motivo,
            "origem": origem,
        }
    )


def load_diagnostic_candidates(root: Path, *, strict: bool = True) -> List[Dict[str, Any]]:
    diag_dir = root / "audit_reports_news_research" / "mcti_fomento_diagnostic"
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    def add(row: Dict[str, Any], origin: str, strict: bool = True) -> None:
        link = _normalize_link(str(row.get("link") or ""))
        if not link or link in seen:
            return
        tit = re.sub(r"\s+", " ", str(row.get("titulo") or "")).strip() or link.rsplit("/", 1)[-1]
        cls = str(row.get("classificacao") or "")
        ctx = str(row.get("contexto_amostra") or "")
        if strict:
            decision, motivo, cls_adj = evaluate_curation(tit, link, ctx, cls)
            if decision != "queue":
                return
            cls = cls_adj or cls
        elif cls not in ("radar_oportunidade", "edital_chamada"):
            return
        seen.add(link)
        out.append(
            {
                "titulo": tit[:320],
                "link": link,
                "classificacao": cls_adj or cls,
                "origem": origin,
                "contexto_amostra": row.get("contexto_amostra"),
                "is_pdf": bool(row.get("is_pdf")),
            }
        )

    summary_path = diag_dir / "summary.json"
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        for key in ("itens_edital_site_nav", "itens_radar_programas_site_nav", "itens_oportunidade_destaque"):
            for row in summary.get(key) or []:
                if isinstance(row, dict):
                    add(row, f"summary.{key}", strict=strict)

    items_path = diag_dir / "itens_classificados.json"
    if items_path.is_file():
        blob = json.loads(items_path.read_text(encoding="utf-8"))
        for key in ("content_core", "arquivos_fomento", "pagina_completa_amostra"):
            for row in blob.get(key) or []:
                if isinstance(row, dict):
                    add(row, f"itens.{key}", strict=strict)

    return out


def _extract_listing_links(
    seed_url: str,
    html: str,
    max_links: int = 40,
    *,
    strict: bool = True,
    descartados: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(html, "html.parser")
    root = soup.select_one("#content-core") or soup
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for a in root.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if not href or href.startswith("#"):
            continue
        full = _normalize_link(urljoin(seed_url, href))
        if full in seen:
            continue
        tit = re.sub(r"\s+", " ", a.get_text() or "").strip()
        if len(tit) < 4 and not full.lower().endswith(".pdf"):
            continue
        cls, motivo_cls = classify_link(tit or full, full)
        decision, motivo_cur, cls_adj = evaluate_curation(tit or full, full, "", cls)
        if strict:
            if decision != "queue":
                if descartados is not None and decision in ("institucional_latente", "descartado_ruido"):
                    _record_discard(
                        descartados,
                        tit or full,
                        full,
                        decision,
                        motivo_cur,
                        f"crawl_listing:{seed_url}",
                        cls,
                    )
                continue
            cls = cls_adj or cls
        elif not _should_queue(cls, tit, full, strict=False):
            continue
        seen.add(full)
        out.append(
            {
                "titulo": (tit or full.rsplit("/", 1)[-1])[:320],
                "link": full,
                "classificacao": cls,
                "origem": f"crawl_listing:{seed_url}",
                "is_pdf": full.lower().endswith(".pdf"),
            }
        )
        if len(out) >= max_links:
            break
    return out


def _snippet_from_html(html: str, max_len: int = 900) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for attrs in ({"property": "og:description"}, {"name": "description"}):
        n = soup.find("meta", attrs=attrs)
        if n and n.get("content"):
            s = _strip_html(n.get("content"), max_len=max_len)
            if len(s) >= 30:
                return s
    main = soup.select_one("#content-core") or soup.find("article") or soup.find("main")
    if main:
        for p in main.find_all("p", limit=8):
            t = _strip_html(p.get_text(), max_len=max_len)
            if len(t) >= 40:
                return t
    return ""


def _dates_from_html(html: str) -> Tuple[Optional[str], Optional[str], List[str]]:
    """data_publicacao iso, prazo iso, raw hints."""
    pub: Optional[str] = None
    prazo: Optional[str] = None
    hints: List[str] = []
    soup = BeautifulSoup(html, "html.parser")
    for attrs in ({"property": "article:published_time"}, {"name": "pubdate"}):
        n = soup.find("meta", attrs=attrs)
        if n and n.get("content"):
            pub = _iso_date(_parse_date(n.get("content"))) or pub
    el = soup.select_one(".documentPublished, .published")
    if el:
        m = re.search(r"\b(\d{2}/\d{2}/20\d{2})\b", el.get_text(" ", strip=True))
        if m:
            pub = _iso_date(_parse_date(m.group(1))) or pub
    text = soup.get_text(" ", strip=True)[:20000]
    for m in re.finditer(
        r"(?i)(prazo[s]?\s*(?:final|para|de)?\s*(?:inscrição|inscricao|envio|submissão|submissao)?[^.]{0,40}?\b\d{1,2}/\d{1,2}/20\d{2})",
        text,
    ):
        hints.append(re.sub(r"\s+", " ", m.group(0))[:120])
        dt = _parse_date(m.group(0))
        if dt and not prazo:
            prazo = _iso_date(dt)
    for m in re.finditer(r"\b(\d{2}/\d{2}/20\d{2})\b", text[:8000]):
        d = _iso_date(_parse_date(m.group(1)))
        if d and not pub:
            pub = d
    if any(k in text.lower() for k in ("inscrições abertas", "inscricoes abertas", "inscrições até")):
        hints.append("inscricoes_abertas_mencionadas")
    return pub, prazo, hints


def _infer_tags(titulo: str, resumo: str, tipo: str) -> List[str]:
    b = f"{titulo} {resumo}".lower()
    tags = ["mcti", "fomento", "ciencia_tecnologia"]
    if tipo == "edital_chamada":
        tags.append("edital_chamada")
    else:
        tags.append("radar_oportunidade")
    if "transformação digital" in b or "transformacao digital" in b:
        tags.append("transformacao_digital")
    if "chamamento" in b or "chamada" in b:
        tags.append("chamamento")
    if "bolsa" in b:
        tags.append("bolsas")
    if "oceano" in b or "vacina" in b:
        tags.append("programa_setorial")
    if "lei" in b and "tic" in b:
        tags.append("lei_tics")
    return list(dict.fromkeys(tags))


def enrich_candidate(row: Dict[str, Any], budget: Dict[str, int]) -> Dict[str, Any]:
    out = dict(row)
    link = str(out.get("link") or "")
    if not link.startswith("http"):
        return out
    if int(budget.get("n", 0)) >= int(budget.get("max", 30)):
        return out
    is_pdf = link.lower().endswith(".pdf") or ".pdf" in link.lower()
    if is_pdf:
        if not _pdf_allowed(
            str(out.get("titulo") or ""),
            link,
            str(out.get("contexto_amostra") or ""),
        ):
            out["_enriched"] = False
            return out
        budget["n"] = int(budget.get("n", 0)) + 1
        if not out.get("resumo"):
            out["resumo"] = (
                f"Documento PDF associado ao programa MCTI ({out.get('classificacao', 'oportunidade')}). "
                "Consultar link para detalhes; sem extração OCR neste dry-run."
            )[:900]
        out["link_documento"] = link
        out["_enriched"] = True
        return out

    resp = _http_get(link, timeout=75)
    if not resp:
        return out
    budget["n"] = int(budget.get("n", 0)) + 1
    time.sleep(0.5)
    html = resp.text or ""
    if not out.get("titulo") or len(str(out.get("titulo"))) < 8:
        soup = BeautifulSoup(html, "html.parser")
        h1 = soup.find("h1")
        if h1:
            out["titulo"] = re.sub(r"\s+", " ", h1.get_text()).strip()[:320]
    sn = _snippet_from_html(html)
    if sn:
        out["resumo"] = sn
    pub, prazo, hints = _dates_from_html(html)
    if pub:
        out["data_publicacao"] = pub
    if prazo:
        out["prazo"] = prazo
    out["prazo_hints"] = hints
    soup = BeautifulSoup(html, "html.parser")
    og = soup.find("meta", attrs={"property": "og:image"})
    if og and og.get("content"):
        out["imagem_url"] = str(og.get("content"))[:500]
    for a in soup.select('a[href*=".pdf"]'):
        href = urljoin(link, a.get("href") or "").split("#")[0]
        if "gov.br/mcti" not in href.lower():
            continue
        if not _pdf_belongs_to_page(link, href):
            continue
        out["link_edital"] = out.get("link_edital") or href
        if href.lower().endswith(".pdf") or "/@@download/" in href.lower():
            out["link_documento"] = href
        break
    out["_enriched"] = True
    return out


def _is_pronto_para_apply(std: Dict[str, Any]) -> bool:
    return bool(std.get("nivel_curacao") == NIVEL_PRONTO or (
        std.get("validacao_status") == "valido"
        and std.get("status") in ("ativo", "latente")
        and std.get("tipo") in ("edital_chamada", "radar_oportunidade")
        and std.get("pronto_para_apply")
    ))


def _is_lei_tics_ppi(link: str, titulo: str, contexto: str = "") -> bool:
    blob = _norm_title(f"{link} {titulo} {contexto}")
    path = urlparse(link).path.lower()
    return "lei-de-tics" in path or "lei das tics" in blob or "lei de tics" in blob or "/ppi" in path


def _is_hub_page(titulo: str, link: str) -> bool:
    nt = _norm_title(titulo)
    path = urlparse(link).path.lower().rstrip("/")
    if nt in {_norm_title(h) for h in HUB_PAGE_TITLES}:
        if path.endswith(("chamamento-oceano", "chamamento-vacina", "bolsa-cientifica")):
            return True
    for end in ("/chamamento-oceano", "/chamamento-vacina", "/bolsa-cientifica"):
        if path.endswith(end):
            return True
    return False


def _strong_text_signal(titulo: str, link: str, contexto: str = "") -> bool:
    blob = _norm_title(f"{titulo} {link} {contexto}")
    if not any(k in blob for k in STRONG_SIGNAL_KEYWORDS):
        return False
    if "oceano" in blob and "chamamento" not in blob and "edital" not in blob:
        return False
    if "vacina" in blob and "chamamento" not in blob and "edital" not in blob:
        return False
    return True


def _specific_call_page(link: str, titulo: str) -> bool:
    path = urlparse(link).path.lower()
    low = link.lower()
    if low.endswith(".pdf") or ".pdf" in low:
        return _pdf_allowed_v3(titulo, link)
    if "/acesso-a-informacao/editais/edital" in path:
        return True
    if any(p in path for p in ("/chamamento-oceano/", "/chamamento-vacina/", "/bolsa-cientifica/")):
        if path.rstrip("/").endswith(("chamamento-oceano", "chamamento-vacina", "bolsa-cientifica")):
            return False
        return True
    if "/arquivos/" in path and any(k in path for k in ("edital", "chamamento", "portaria", "resultado")):
        return True
    return False


def _prazo_ou_documento_oficial(row: Dict[str, Any]) -> bool:
    if row.get("prazo"):
        return True
    if row.get("link_edital") or row.get("link_documento"):
        u = _norm_title(f"{row.get('link_edital')} {row.get('link_documento')}")
        return any(k in u for k in ("edital", "chamamento", "portaria", "resultado"))
    link = str(row.get("link") or "").lower()
    if link.endswith(".pdf") and _pdf_allowed_v3(str(row.get("titulo") or ""), link):
        return True
    return False


def _pdf_allowed_v3(titulo: str, link: str, contexto: str = "") -> bool:
    if not link.lower().endswith(".pdf") and ".pdf" not in link.lower():
        return True
    blob = _norm_title(f"{titulo} {link} {contexto}")
    if not any(k in blob for k in PDF_V3_ALLOW_KEYWORDS):
        return False
    if any(d in blob for d in PDF_V3_SOFT_DENY):
        if not any(k in blob for k in ("edital", "chamamento", "chamada", "portaria", "resultado")):
            return False
    return True


def _generic_program_without_call(titulo: str, link: str, contexto: str = "") -> bool:
    path = urlparse(link).path.lower()
    blob = _norm_title(f"{titulo} {link} {contexto}")
    if any(m in path for m in GENERIC_PROGRAM_PATH_MARKERS):
        if any(k in blob for k in ("edital", "chamamento", "selecao publica", "chamada publica")):
            return False
        return True
    return False


def _collect_v3_signals(row: Dict[str, Any]) -> List[str]:
    titulo = str(row.get("titulo") or "")
    link = str(row.get("link") or "")
    ctx = str(row.get("contexto_amostra") or row.get("resumo") or "")
    out: List[str] = []
    if _strong_text_signal(titulo, link, ctx):
        out.append("texto_ou_url_forte")
    if _specific_call_page(link, titulo):
        out.append("pagina_ou_pdf_chamada")
    if _prazo_ou_documento_oficial(row):
        out.append("prazo_ou_documento_oficial")
    return out


def evaluate_curation_v3(
    titulo: str,
    link: str,
    contexto: str = "",
    classificacao: str = "",
) -> Tuple[str, str, Optional[str]]:
    """Fila v3: só entra o que pode virar review ou pronto (não menu institucional)."""
    decision, motivo, cls = evaluate_curation(titulo, link, contexto, classificacao)
    if decision != "queue":
        return decision, motivo, cls

    if _is_lei_tics_ppi(link, titulo, contexto):
        return NIVEL_INSTITUCIONAL, "lei_tics_ppi_programa_permanente", "radar_institucional_latente"

    if _generic_program_without_call(titulo, link, contexto):
        return NIVEL_INSTITUCIONAL, "programa_generico_sem_chamada", None

    is_pdf = ".pdf" in link.lower()
    if is_pdf and not _pdf_allowed_v3(titulo, link, contexto):
        return NIVEL_INSTITUCIONAL, "pdf_institucional_ou_estudo", None

    path = urlparse(link).path.lower()
    if "/acesso-a-informacao/editais/edital" in path:
        return "queue", "edital_repositorio", cls or "edital_chamada"

    if any(p in path for p in ("/chamamento-oceano", "/chamamento-vacina", "/bolsa-cientifica")):
        if _is_hub_page(titulo, link) and not _strong_text_signal(titulo, link, contexto):
            return NIVEL_INSTITUCIONAL, "hub_programa_sem_chamada", None
        if _is_hub_page(titulo, link):
            return "queue", "hub_com_titulo_forte", cls
        return "queue", "programa_chamamento", cls

    blob = _norm_title(f"{titulo} {link} {contexto}")
    if _strong_text_signal(titulo, link, contexto) and (_specific_call_page(link, titulo) or is_pdf):
        return "queue", "sinal_forte_v3", cls

    if any(k in blob for k in ("comunicado", "documentos relacionados", "resultado", "portaria")):
        if "/chamamento" in path or "/editais/" in path:
            return "queue", "processo_chamamento", cls

    return NIVEL_INSTITUCIONAL, "v3_sem_sinais_suficientes_fila", None


def _is_processo_ato_not_pronto(titulo: str, link: str) -> bool:
    """Comunicados, resultados, pareceres etc. — review, não apply direto."""
    path = urlparse(link).path.lower()
    if "/acesso-a-informacao/editais/edital" in path:
        return False
    blob = _norm_title(f"{titulo} {link}")
    if "edital de chamamento" in blob or re.search(r"edital\s+n[oº°]?\s*\d", blob):
        return False
    markers = (
        "comunicado",
        "resultado",
        "parecer",
        "relatorio",
        "relatório",
        "despacho",
        "recurso",
        "extrato",
        "reconsideracao",
        "contrarraz",
        "intimacao",
        "intimação",
        "republicacao",
        "habilitacao de propostas",
        "entidades habilitadas",
        "estudo de publicizacao",
    )
    return any(m in blob for m in markers)


def assign_nivel_v3(row: Dict[str, Any]) -> Tuple[str, str, List[str]]:
    """Retorna (nivel, motivo, sinais_v3)."""
    titulo = str(row.get("titulo") or "")
    link = str(row.get("link") or "")
    ctx = str(row.get("contexto_amostra") or row.get("resumo") or "")

    if _is_lei_tics_ppi(link, titulo, ctx):
        return NIVEL_REVIEW, "lei_tics_ppi_nao_apply", ["programa_permanente"]

    if _generic_program_without_call(titulo, link, ctx):
        return NIVEL_INSTITUCIONAL, "programa_institucional_generico", []

    is_pdf = ".pdf" in link.lower()
    if is_pdf and not _pdf_allowed_v3(titulo, link, ctx):
        if any(d in _norm_title(f"{titulo} {link}") for d in PDF_V3_SOFT_DENY):
            return NIVEL_INSTITUCIONAL, "pdf_estudo_cartilha_relatorio", []
        return NIVEL_REVIEW, "pdf_ambiguo", []

    if _is_hub_page(titulo, link):
        return NIVEL_INSTITUCIONAL, "hub_programa_sem_chamada_especifica", []

    sinais = _collect_v3_signals(row)
    blob = _norm_title(f"{titulo} {link} {ctx}")
    path_l = link.lower()

    if len(sinais) >= 2 and not _is_hub_page(titulo, link):
        if _is_processo_ato_not_pronto(titulo, link):
            return NIVEL_REVIEW, "ato_ou_comunicado_processo", sinais

        if "/acesso-a-informacao/editais/edital" in path_l:
            pub = _parse_date(row.get("data_publicacao"))
            if pub and pub.year < 2023 and not row.get("prazo"):
                return NIVEL_REVIEW, "edital_antigo_sem_prazo", sinais
            return NIVEL_PRONTO, "edital_repositorio_sei", sinais

        if is_pdf and ("portaria" in blob or "comissao" in blob):
            if "edital-de-chamamento" not in blob and "edital de chamamento" not in blob:
                return NIVEL_REVIEW, "portaria_ou_comissao", sinais

        if is_pdf and "edital" in blob and "resultado" not in blob and "parecer" not in blob:
            return NIVEL_PRONTO, "pdf_edital_oficial", sinais

        if "edital" in blob and ("retificad" in blob or "chamamento sepef" in blob):
            if row.get("link_documento") or row.get("link_edital"):
                return NIVEL_PRONTO, "edital_programa_com_documento", sinais
            return NIVEL_REVIEW, "edital_programa_sem_anexo_extraido", sinais

        return NIVEL_REVIEW, "dois_sinais_sem_edital_principal", sinais

    if len(sinais) >= 1:
        if any(k in blob for k in ("comunicado", "documentos relacionados", "perguntas", "saiba mais", "fique por dentro")):
            return NIVEL_REVIEW, "comunicado_ou_faq", sinais
        if "resultado" in blob or "portaria" in blob or "retific" in blob:
            return NIVEL_REVIEW, "ato_processo_seletivo", sinais
        if _is_hub_page(titulo, link):
            return NIVEL_INSTITUCIONAL, "hub_com_sinal_parcial", sinais
        return NIVEL_REVIEW, "sinal_unico_revisar", sinais

    return NIVEL_INSTITUCIONAL, "sem_sinais_v3", []


def standardize_row(
    row: Dict[str, Any],
    *,
    strict: bool = True,
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Retorna (standardized_row, review_candidate, discard_record).
    """
    link = _normalize_link(str(row.get("link") or ""))
    titulo = re.sub(r"\s+", " ", str(row.get("titulo") or "")).strip()
    tipo = str(row.get("classificacao") or "")
    ctx = str(row.get("contexto_amostra") or "")

    if strict:
        decision, motivo, tipo_adj = evaluate_curation(titulo, link, ctx, tipo)
        if decision != "queue":
            discard = {
                "titulo": titulo[:320],
                "link": link,
                "classificacao_original": tipo,
                "decisao": decision,
                "motivo": motivo,
                "origem": row.get("origem"),
            }
            return None, None, discard
        if tipo_adj:
            tipo = tipo_adj

    if tipo not in ("radar_oportunidade", "edital_chamada"):
        return None, None, None
    if not _is_mcti_opportunity_link(link):
        return None, None, {
            "titulo": titulo,
            "link": link,
            "decisao": "descartado_ruido",
            "motivo": "fora_dominio_mcti",
            "origem": row.get("origem"),
        }
    if not link.startswith("http") or len(titulo) < 8:
        return None, {
            "link": link,
            "titulo": titulo,
            "motivo_review": "titulo_ou_link_invalido",
            "origem": row.get("origem"),
        }, None

    resumo = _strip_html(row.get("resumo") or row.get("contexto_amostra") or "", max_len=900)
    if len(resumo) < 25:
        ctx = str(row.get("contexto_amostra") or "")
        if len(ctx) >= 40:
            resumo = _strip_html(ctx, max_len=900)

    data_pub = row.get("data_publicacao")
    prazo = row.get("prazo")
    prazo_dt = _parse_date(prazo)
    pub_dt = _parse_date(data_pub)
    now = datetime.now(timezone.utc)

    ambiguo = False
    motivos_review: List[str] = []
    nt = _norm_title(titulo)
    if any(_norm_title(m) in nt for m in REVIEW_TITLE_MARKERS):
        ambiguo = True
        motivos_review.append("titulo_requer_revisao_manual")

    if "/contratos-de-gestao" in link.lower():
        ambiguo = True
        motivos_review.append("contrato_gestao_pode_ser_institucional")

    if tipo == "edital_chamada" and not prazo:
        y = pub_dt.year if pub_dt else 0
        if y and y < now.year - 1:
            status = "latente"
            motivos_review.append("edital_antigo_sem_prazo")
        else:
            status = "incompleto"
            motivos_review.append("edital_sem_prazo_extraido")
    elif prazo_dt and prazo_dt.date() >= now.date():
        status = "ativo"
    elif prazo_dt and prazo_dt.date() < now.date():
        status = "latente"
        motivos_review.append("prazo_expirado")
    elif any(k in (resumo + titulo).lower() for k in ("inscrições abertas", "inscricoes abertas")):
        status = "ativo"
    elif tipo == "radar_oportunidade":
        has_chamada = _text_allowlist_hit(titulo, link, resumo)
        if _path_allowlist_hit(link) and (len(resumo) >= 40 or has_chamada):
            status = "ativo"
        else:
            status = "incompleto"
            motivos_review.append("programa_sem_resumo_ou_chamada_explicita")
    else:
        status = "incompleto"
        motivos_review.append("sem_prazo_nem_sinal_abertura")

    if len(resumo) < 40:
        ambiguo = True
        motivos_review.append("resumo_curto")

    q = 45
    if len(resumo) >= 40:
        q += min(35, len(resumo) // 20)
    if data_pub:
        q += 5
    if prazo:
        q += 10
    q = min(100, q)

    val = "valido" if len(resumo) >= 40 and len(titulo) >= 12 and status in ("ativo", "latente") else "incompleto"
    if ambiguo or val == "incompleto":
        val = "incompleto"

    link_edital = row.get("link_edital")
    link_doc = row.get("link_documento")
    if link.lower().endswith(".pdf"):
        link_doc = link_doc or link

    std: Dict[str, Any] = {
        "titulo": titulo[:320],
        "resumo": resumo[:900] if resumo else None,
        "link": link[:800],
        "fonte": FONTE,
        "fonte_recurso": SOURCE_ID,
        "tipo": tipo,
        "area": list(AREA_DEFAULT),
        "orgao": ORGAO,
        "data_publicacao": data_pub if isinstance(data_pub, str) else _iso_date(pub_dt),
        "prazo": prazo if isinstance(prazo, str) else _iso_date(prazo_dt),
        "link_edital": link_edital,
        "link_documento": link_doc,
        "status": status,
        "validacao_status": val,
        "qualidade_dado": q,
        "tags": _infer_tags(titulo, resumo or "", tipo),
        "destino_simulado": "review_for_edital" if tipo == "edital_chamada" else "public.edital_radar",
        "extras": {
            "source_id": SOURCE_ID,
            "origem": row.get("origem"),
            "classificacao_diagnostico": tipo,
            "curacao_v2": strict,
            "prazo_hints": row.get("prazo_hints") or [],
            "page_enriched": bool(row.get("_enriched")),
            "is_pdf": link.lower().endswith(".pdf"),
            "nao_noticia": True,
            "copyright_note": "resumo_meta_ou_paragrafo_sem_corpo_integral",
        },
    }
    std["pronto_para_apply"] = _is_pronto_para_apply(std)

    review = None
    if ambiguo or (val == "incompleto" and motivos_review):
        review = {
            "titulo": titulo,
            "link": link,
            "tipo": tipo,
            "status": status,
            "validacao_status": val,
            "motivos": motivos_review,
            "resumo_amostra": (resumo or "")[:200],
            "origem": row.get("origem"),
        }

    if status == "latente" and tipo == "edital_chamada" and not prazo:
        return std, review, None

    if val == "incompleto" and not ambiguo:
        return std, review, None

    if ambiguo:
        return std, review, None

    return std, None, None


def crawl_mcti_fomento(
    root: Path,
    *,
    max_enrich: int = 28,
    max_per_seed: int = 35,
    strict_curation: bool = True,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """Retorna (standardized, review_candidates, descartados_ruido, meta)."""
    errors: List[Dict[str, str]] = []
    queue: Dict[str, Dict[str, Any]] = {}
    descartados: List[Dict[str, Any]] = []

    for row in load_diagnostic_candidates(root, strict=strict_curation):
        link = _normalize_link(row["link"])
        tit = row.get("titulo", "")
        ctx = str(row.get("contexto_amostra") or "")
        cls = str(row.get("classificacao") or "")
        if strict_curation:
            decision, motivo, _ = evaluate_curation(tit, link, ctx, cls)
            if decision != "queue":
                _record_discard(descartados, tit, link, decision, motivo, row.get("origem", "diagnostic"), cls)
                continue
        queue[link] = row

    for seed in SEEDS:
        time.sleep(1.0)
        resp = _http_get(seed)
        if not resp:
            errors.append({"seed": seed, "error": "fetch_failed"})
            continue
        for item in _extract_listing_links(
            seed,
            resp.text or "",
            max_links=max_per_seed,
            strict=strict_curation,
            descartados=descartados if strict_curation else None,
        ):
            link = item["link"]
            if link not in queue:
                queue[link] = item

    budget = {"n": 0, "max": max_enrich}
    enriched: List[Dict[str, Any]] = []
    for link in sorted(queue.keys()):
        row = enrich_candidate(queue[link], budget)
        enriched.append(row)

    standardized: List[Dict[str, Any]] = []
    review: List[Dict[str, Any]] = []
    seen_review_links: Set[str] = set()
    seen_std_links: Set[str] = set()

    for row in enriched:
        std, rev, discard = standardize_row(row, strict=strict_curation)
        if discard:
            descartados.append(discard)
        if std:
            sk = std.get("link")
            if sk and sk in seen_std_links:
                continue
            if sk:
                seen_std_links.add(sk)
            standardized.append(std)
        if rev:
            rk = rev.get("link")
            if rk and rk not in seen_review_links:
                seen_review_links.add(rk)
                review.append(rev)

    meta = {
        "source_id": SOURCE_ID,
        "seeds": list(SEEDS),
        "candidatos_fila": len(queue),
        "candidatos_brutos_diagnostic": None,
        "page_enrich_fetches": budget.get("n", 0),
        "errors": errors,
        "strict_curation": strict_curation,
        "total_descartados": len(descartados),
        "pronto_para_apply": sum(1 for r in standardized if r.get("pronto_para_apply")),
    }
    return standardized, review, descartados, meta


def _v3_record_base(row: Dict[str, Any], nivel: str, motivo: str, sinais: List[str]) -> Dict[str, Any]:
    return {
        "titulo": str(row.get("titulo") or "")[:320],
        "link": _normalize_link(str(row.get("link") or "")),
        "nivel_curacao": nivel,
        "motivo_nivel": motivo,
        "sinais_v3": sinais,
        "origem": row.get("origem"),
        "classificacao": row.get("classificacao"),
    }


def process_enriched_row_v3(
    row: Dict[str, Any],
) -> Tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]:
    """
    Retorna (bucket, record, discard_optional).
    bucket: pronto | review | institucional | descartado
    """
    titulo = str(row.get("titulo") or "")
    link = str(row.get("link") or "")
    ctx = str(row.get("contexto_amostra") or "")

    decision, motivo_pre, cls_adj = evaluate_curation_v3(
        titulo, link, ctx, str(row.get("classificacao") or "")
    )
    if decision not in ("queue",):
        discard = _v3_record_base(row, decision, motivo_pre, [])
        discard["decisao"] = decision
        return "descartado" if decision == NIVEL_DESCARTADO else "institucional", discard, discard

    if cls_adj:
        row = dict(row)
        row["classificacao"] = cls_adj

    nivel, motivo, sinais = assign_nivel_v3(row)

    if nivel == NIVEL_INSTITUCIONAL:
        rec = _v3_record_base(row, nivel, motivo, sinais)
        rec["decisao"] = NIVEL_INSTITUCIONAL
        return "institucional", rec, None

    std, rev, _ = standardize_row(row, strict=False)
    if not std:
        rec = _v3_record_base(row, NIVEL_REVIEW, motivo or "sem_standardized", sinais)
        return "review", rec, None

    std["nivel_curacao"] = nivel
    std["motivo_nivel"] = motivo
    std["sinais_v3"] = sinais
    std["extras"]["curacao_v3"] = True
    std["pronto_para_apply"] = False

    if nivel == NIVEL_PRONTO:
        std["pronto_para_apply"] = True
        std["validacao_status"] = "valido"
        if not std.get("status") or std.get("status") == "incompleto":
            std["status"] = "ativo" if row.get("prazo") else "latente"
        return "pronto", std, None

    if nivel == NIVEL_REVIEW:
        std["pronto_para_apply"] = False
        review_rec = rev or {
            "titulo": std.get("titulo"),
            "link": std.get("link"),
            "tipo": std.get("tipo"),
            "status": std.get("status"),
            "validacao_status": std.get("validacao_status"),
            "motivos": [motivo],
            "resumo_amostra": (std.get("resumo") or "")[:200],
            "origem": row.get("origem"),
        }
        review_rec["nivel_curacao"] = NIVEL_REVIEW
        review_rec["motivo_nivel"] = motivo
        review_rec["sinais_v3"] = sinais
        return "review", review_rec, None

    rec = _v3_record_base(row, nivel, motivo, sinais)
    return "institucional", rec, None


def crawl_mcti_fomento_v3(
    root: Path,
    *,
    max_enrich: int = 28,
    max_per_seed: int = 35,
) -> Tuple[
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    Dict[str, Any],
]:
    """Retorna (pronto_standardized, review, institucional_latente, descartados, meta)."""
    errors: List[Dict[str, str]] = []
    queue: Dict[str, Dict[str, Any]] = {}
    descartados: List[Dict[str, Any]] = []
    institucional: List[Dict[str, Any]] = []

    def _eval_v3(tit: str, lnk: str, ctx: str, cls: str) -> Tuple[str, str, Optional[str]]:
        return evaluate_curation_v3(tit, lnk, ctx, cls)

    diag_dir = root / "audit_reports_news_research" / "mcti_fomento_diagnostic"
    seen: Set[str] = set()

    def _add_diag(row: Dict[str, Any], origin: str) -> None:
        link = _normalize_link(str(row.get("link") or ""))
        if not link or link in seen:
            return
        tit = re.sub(r"\s+", " ", str(row.get("titulo") or "")).strip() or link.rsplit("/", 1)[-1]
        cls = str(row.get("classificacao") or "")
        ctx = str(row.get("contexto_amostra") or "")
        decision, motivo, cls_adj = _eval_v3(tit, link, ctx, cls)
        if decision != "queue":
            _record_discard(
                descartados if decision == NIVEL_DESCARTADO else institucional,
                tit,
                link,
                decision,
                motivo,
                origin,
                cls,
            )
            return
        seen.add(link)
        queue[link] = {
            "titulo": tit[:320],
            "link": link,
            "classificacao": cls_adj or cls,
            "origem": origin,
            "contexto_amostra": row.get("contexto_amostra"),
            "is_pdf": bool(row.get("is_pdf")),
        }

    summary_path = diag_dir / "summary.json"
    if summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        for key in ("itens_edital_site_nav", "itens_radar_programas_site_nav", "itens_oportunidade_destaque"):
            for row in summary.get(key) or []:
                if isinstance(row, dict):
                    _add_diag(row, f"summary.{key}")

    items_path = diag_dir / "itens_classificados.json"
    if items_path.is_file():
        blob = json.loads(items_path.read_text(encoding="utf-8"))
        for key in ("content_core", "arquivos_fomento", "pagina_completa_amostra"):
            for row in blob.get(key) or []:
                if isinstance(row, dict):
                    _add_diag(row, f"itens.{key}")

    for seed in SEEDS:
        time.sleep(1.0)
        resp = _http_get(seed)
        if not resp:
            errors.append({"seed": seed, "error": "fetch_failed"})
            continue
        soup = BeautifulSoup(resp.text or "", "html.parser")
        root_el = soup.select_one("#content-core") or soup
        seen_seed: Set[str] = set()
        for a in root_el.find_all("a", href=True):
            href = (a.get("href") or "").strip()
            if not href or href.startswith("#"):
                continue
            full = _normalize_link(urljoin(seed, href))
            if full in seen_seed:
                continue
            tit = re.sub(r"\s+", " ", a.get_text() or "").strip()
            if len(tit) < 4 and not full.lower().endswith(".pdf"):
                continue
            cls, _ = classify_link(tit or full, full)
            decision, motivo, cls_adj = _eval_v3(tit or full, full, "", cls)
            if decision != "queue":
                bucket = descartados if decision == NIVEL_DESCARTADO else institucional
                _record_discard(bucket, tit or full, full, decision, motivo, f"crawl:{seed}", cls)
                continue
            seen_seed.add(full)
            if full not in queue:
                queue[full] = {
                    "titulo": (tit or full.rsplit("/", 1)[-1])[:320],
                    "link": full,
                    "classificacao": cls_adj or cls,
                    "origem": f"crawl_listing:{seed}",
                    "is_pdf": full.lower().endswith(".pdf"),
                }
            if len(seen_seed) >= max_per_seed:
                break

    budget = {"n": 0, "max": max_enrich}
    pronto: List[Dict[str, Any]] = []
    review: List[Dict[str, Any]] = []
    seen_pronto: Set[str] = set()
    seen_review: Set[str] = set()

    for link in sorted(queue.keys()):
        row = enrich_candidate(queue[link], budget)
        if ".pdf" in link.lower() and not _pdf_allowed_v3(
            str(row.get("titulo") or ""), link, str(row.get("contexto_amostra") or "")
        ):
            rec = _v3_record_base(row, NIVEL_INSTITUCIONAL, "pdf_nao_aplicavel_v3", [])
            institucional.append(rec)
            continue

        bucket, record, discard = process_enriched_row_v3(row)
        if discard and bucket in ("descartado", "institucional"):
            if bucket == "descartado":
                descartados.append(discard)
            else:
                institucional.append(record)
            continue

        lk = record.get("link")
        if bucket == "pronto" and lk and lk not in seen_pronto:
            seen_pronto.add(lk)
            pronto.append(record)
        elif bucket == "review" and lk and lk not in seen_review:
            seen_review.add(lk)
            review.append(record)
        elif bucket == "institucional":
            institucional.append(record)

    meta = {
        "source_id": SOURCE_ID,
        "seeds": list(SEEDS),
        "candidatos_fila": len(queue),
        "page_enrich_fetches": budget.get("n", 0),
        "errors": errors,
        "curacao": "v3_conservadora",
        "total_pronto_para_apply": len(pronto),
        "total_review": len(review),
        "total_institucional_latente": len(institucional),
        "total_descartados": len(descartados),
    }
    return pronto, review, institucional, descartados, meta
