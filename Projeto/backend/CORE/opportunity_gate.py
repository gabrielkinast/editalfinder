"""Filtro central de qualidade para crawlers Asia (JP/CN).

Avalia login, restricao por IP/campus, erros, paginas genericas e relevancia
de oportunidade (funding, procurement, chamadas) antes do pipeline downstream.

Uso:
- ``evaluate_crawl_candidate`` no crawler (HTML + HTTP).
- ``evaluate_item_dict`` no transformer/loader (item JSON ja estruturado).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# --- access_status (contrato com extras / loader) ---
ACCESS_PUBLIC = "public_access"
ACCESS_LOGIN = "restricted_login"
ACCESS_IP = "restricted_ip"
ACCESS_INTERNAL = "internal_network"
ACCESS_ERROR = "error_page"
ACCESS_UNAVAILABLE = "unavailable"
ACCESS_UNKNOWN = "unknown"

# --- opportunity_intent ---
INTENT_FUNDING = "funding"
INTENT_GRANT = "grant"
INTENT_SCHOLARSHIP = "scholarship"
INTENT_RESEARCH_CALL = "research_call"
INTENT_PROCUREMENT = "procurement"
INTENT_TENDER = "tender"
INTENT_INVESTMENT = "investment"
INTENT_INNOVATION = "innovation_program"
INTENT_INSTITUTIONAL = "institutional_program"
INTENT_NEWS = "news"
INTENT_GENERIC = "generic_page"
INTENT_INVALID = "invalid"

# Frases fortes (substring) — bloqueiam mesmo em dominios publicos.
_STRONG_LOGIN_PATTERNS: Tuple[str, ...] = (
    "please log in",
    "please login",
    "user login",
    "session expired",
    "access denied",
    "please sign in",
    "authentication required",
    "faça login",
    "fazer login",
    "efetue login",
    "efetue o login",
    "ログイン",
    "サインイン",
    "認証",
    "パスワード",
    "アカウント",
    "権限がありません",
    "アクセスできません",
    "登录",
    "登陆",
    "用户登录",
    "密码",
    "账号",
    "认证",
    "未授权",
    "无权限",
    "访问被拒绝",
    "请先登录",
)

# Palavras curtas em ingles: usamos regex com limite de palavra para evitar
# "account" em textos institucionais / rodapes em gov.br sem pagina de login.
_WEAK_LOGIN_RES: Tuple[re.Pattern[str], ...] = (
    re.compile(r"\blogin\b", re.IGNORECASE),
    re.compile(r"\bsign\s*-?\s*in\b", re.IGNORECASE),
    re.compile(r"\blog\s+in\b", re.IGNORECASE),
    re.compile(r"\bpassword\b", re.IGNORECASE),
    re.compile(r"\baccounts?\b", re.IGNORECASE),
    re.compile(r"\bauthentication\b", re.IGNORECASE),
    re.compile(r"\bunauthorized\b", re.IGNORECASE),
    re.compile(r"\bforbidden\b", re.IGNORECASE),
    re.compile(r"\bsso\b", re.IGNORECASE),
)

_RESTRICTED_PATTERNS = [
    "internal network", "campus network", "intranet", "only accessible within",
    "ip address not allowed", "restricted to campus", "institutional access only",
    "学内限定", "学内ネットワーク", "学内専用", "学内", "アクセス制限",
    "関係者のみ", "内部限定",
    "校内", "校园网", "校内访问", "内网", "内部访问", "仅限校内",
    "仅供校内访问", "当前访问的ip并非校内", "该信息仅允许校内地址访问",
    "访问的ip并非校内地址", "非校内地址", "校园网访问", "您当前访问的ip",
    "并非校内地址", "仅允许校内",
]

_ERROR_PATTERNS = [
    "page not found", "not found", "service unavailable", "unavailable",
    "page error", "server error", "temporarily unavailable",
    "ページが見つかりません", "表示できません", "利用できません",
    "页面不存在", "页面出错", "访问出错", "找不到页面", "暂时无法访问",
    "服务器错误",
]

_GENERIC_URL_PARTS = [
    "/news/", "/about", "/contact", "/home", "/index.htm", "/default.",
    "/kygk", "about/news", "news_events", "/english/", "/info/",
]

_GENERIC_TITLES = {
    "home",
    "welcome",
    "contact",
    "about us",
    "about",
    "news",
    "首页",
    "主页",
    "联系我们",
    "关于我们",
    "科研概况",
}

_STRONG_POSITIVE = [
    "招标", "投标", "采购", "中标", "招标公告", "采购公告", "竞争性磋商",
    "公开招标", "询价", "入札", "調達", "公示", "公募", "募集",
    "助成", "補助金", "研究助成", "申請", "申請受付", "课题申请",
    "项目申报", "申报通知", "申报指南", "项目指南", "专项资金",
    "资助", "基金", "grant", "funding", "call for proposals",
    "call for applications", "fellowship", "tender", "procurement",
    "rfp", "bidding", "deadline", "截止日期", "締切", "募集要項",
    "deadline", "submission", "提出", "応募",
]

_DEADLINE_HINTS = [
    r"\b20\d{2}[-./]\d{1,2}[-./]\d{1,2}\b",
    r"\d{4}\s*年\s*\d{1,2}\s*月\s*\d{1,2}\s*日",
    "deadline", "締切", "截止", "期限", "due date",
]

_VALUE_HINTS = ["budget", "million", "billion", "万元", "百万", "予算", "funding amount", "総額"]

_FORM_HINTS = ["apply", "application", "申込", "申請", "在线申请", "submit", "提出先", "entry form"]

_STRONG_CALL_MARKERS: Tuple[str, ...] = (
    "招标公告",
    "采购公告",
    "公募",
    "募集要項",
    "课题申报",
    "项目申报",
    "call for proposals",
    "submission deadline",
    "入札公告",
    "chamada pública",
    "chamada publica",
    "consulta pública",
    "consulta publica",
    "edital",
    "licitação",
    "licitacao",
    "pregão eletrônico",
    "pregao eletronico",
    "financiamento",
    "linha de crédito",
    "linha de credito",
)


def _strong_call_signal(corpus: str) -> bool:
    return any(x in corpus for x in _STRONG_CALL_MARKERS)


@dataclass
class GateResult:
    keep: bool
    access_status: str
    opportunity_intent: str
    opportunity_score: int
    rejection_reason: str
    detected_terms: List[str] = field(default_factory=list)
    # Contexto BR (gov.br / agências): usado pelo transformer para relaxamento controlado.
    trusted_fin_context: bool = False
    # Categoria interpretável (não substitui intent interno; é rótulo para auditoria/UI).
    gate_category: str = ""


def trusted_br_relevance_soft_continue(gate: GateResult, titulo: str, link: str) -> bool:
    """
    Fonte/host BR confiável + rejeição só por fraca evidência textual: permite seguir o pipeline
    como suspeito/incompleto (transformer), sem reabrir login/erro/notícia.
    """
    if gate.keep:
        return False
    if not gate.trusted_fin_context:
        return False
    bad_access = (
        ACCESS_LOGIN,
        ACCESS_IP,
        ACCESS_INTERNAL,
        ACCESS_ERROR,
        ACCESS_UNAVAILABLE,
    )
    if gate.access_status in bad_access:
        return False
    if gate.opportunity_intent == INTENT_NEWS:
        return False
    rr = gate.rejection_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    tl = (titulo or "").strip()
    lk = (link or "").strip()
    if len(tl) < 8 or not lk.lower().startswith("http"):
        return False
    if _br_title_url_has_opportunity_marker(titulo, link):
        return True
    if _is_official_pdf_link(link):
        return True
    return False


def _derive_gate_category(
    *,
    access: str,
    intent: str,
    official_pdf: bool,
    trusted_fin: bool,
) -> str:
    if access == ACCESS_LOGIN:
        return "login"
    if access in (ACCESS_IP, ACCESS_INTERNAL):
        return "restrito"
    if access in (ACCESS_ERROR, ACCESS_UNAVAILABLE):
        return "erro"
    if official_pdf and trusted_fin:
        return "documento_oficial"
    if official_pdf:
        return "pdf_documento"
    if intent == INTENT_NEWS:
        return "noticia"
    if intent == INTENT_GENERIC:
        return "pagina_generica"
    if intent in (INTENT_PROCUREMENT, INTENT_TENDER):
        return "licitacao"
    if intent == INTENT_INSTITUTIONAL:
        return "programa"
    if intent == INTENT_RESEARCH_CALL:
        return "chamada_publica"
    if intent in (INTENT_GRANT,):
        return "edital"
    if intent == INTENT_SCHOLARSHIP:
        return "oportunidade"
    if intent == INTENT_INVESTMENT:
        return "linha_credito"
    if intent in (INTENT_FUNDING, INTENT_INNOVATION):
        return "oportunidade"
    return "pagina_generica"


def _matches_any(corpus: str, patterns: Tuple[str, ...], out: List[str]) -> bool:
    c_low = corpus.lower()
    for p in patterns:
        if p.lower() in c_low or p in corpus:
            out.append(p)
            return True
    return False


def _weak_login_hits(corpus: str, out: List[str]) -> bool:
    for rx in _WEAK_LOGIN_RES:
        m = rx.search(corpus)
        if m:
            out.append(m.group(0))
            return True
    return False


def _is_official_pdf_link(url: str) -> bool:
    u = (url or "").strip().lower().split("?", 1)[0]
    return u.endswith(".pdf")


def _is_br_trusted_finance_host(url: str) -> bool:
    u = (url or "").lower()
    return any(
        h in u
        for h in (
            "gov.br",
            "bndes.gov.br",
            "finep.gov.br",
            "cnpq.br",
            "aneel.gov.br",
        )
    )


def _is_br_trusted_finance_fonte(fonte: str) -> bool:
    f = (fonte or "").upper()
    return any(x in f for x in ("ANEEL", "BNDES", "CNPQ", "FINEP", "MCTI", "CAPES", "CAIXA"))


def _br_title_url_has_opportunity_marker(titulo: str, link: str) -> bool:
    blob = f"{titulo} {link}".lower()
    return any(
        k in blob
        for k in (
            "chamada",
            "edital",
            "programa",
            "consulta",
            "fundos",
            "linha",
            "licit",
            "pregão",
            "pregao",
            "financiamento",
            "credito",
            "crédito",
            "bolsa",
            "fomento",
            "subvenção",
            "subvencao",
            "chamadas-publicas",
            "chamadapublica",
            "resultado",
            "portaria",
            "normativo",
            "resolução",
            "resolucao",
            "extrato",
            "tomada",
            "credenciamento",
            "seleção",
            "selecao",
            "proposta",
            "publicação",
            "publicacao",
            "audiência",
            "audiencia",
            "atos",
            "deliberação",
            "deliberacao",
        )
    )


def _trusted_public_opportunity_context(url: str, titulo: str, descricao: str) -> bool:
    """Heuristica conservadora: gov.br (e afins) + sinais de chamada/edital ou texto longo."""
    u = (url or "").lower()
    td = f"{titulo or ''}\n{descricao or ''}".lower()
    hosts = (
        "gov.br",
        "jus.br",
        "bndes.gov.br",
        "bb.com.br",
        "caixa.gov.br",
        "banrisul.com.br",
        "brde.com.br",
        "badesul.com.br",
    )
    if not any(h in u for h in hosts):
        return False
    keys = (
        "edital",
        "chamada",
        "chamada pública",
        "chamada publica",
        "licita",
        "licitacao",
        "licitação",
        "concurso",
        "seleção",
        "selecao",
        "programa",
        "fomento",
        "financiamento",
        "credito",
        "crédito",
        "fundos",
        "oportunidade",
        "manifestação de interesse",
        "manifestacao de interesse",
        "pdi",
        "subvenção",
        "subvencao",
        "bolsa",
        "projeto",
    )
    if any(k in td or k in u for k in keys):
        return True
    if len((descricao or "").strip()) >= 260:
        return True
    return False


def detect_access_status(
    corpus: str,
    url: str,
    status_code: Optional[int],
    titulo: str = "",
    descricao: str = "",
) -> Tuple[str, List[str]]:
    terms: List[str] = []
    if status_code in (404, 502, 503, 500):
        terms.append(f"http_{status_code}")
        return ACCESS_ERROR, terms
    if status_code == 401:
        return ACCESS_LOGIN, ["http_401"]
    strong_terms: List[str] = []
    if _matches_any(corpus, _STRONG_LOGIN_PATTERNS, strong_terms):
        return ACCESS_LOGIN, strong_terms
    weak_terms: List[str] = []
    if _weak_login_hits(corpus, weak_terms):
        if _trusted_public_opportunity_context(url, titulo, descricao):
            return ACCESS_PUBLIC, ["login_fraco_suprimido_contexto_publico"] + weak_terms
        return ACCESS_LOGIN, weak_terms
    if _matches_any(corpus, tuple(_RESTRICTED_PATTERNS), terms):
        return ACCESS_IP, terms
    if status_code == 403:
        rest_terms: List[str] = []
        if _matches_any(corpus, tuple(_RESTRICTED_PATTERNS), rest_terms):
            return ACCESS_IP, rest_terms
        st2: List[str] = []
        if _matches_any(corpus, _STRONG_LOGIN_PATTERNS, st2):
            return ACCESS_LOGIN, st2
        wt2: List[str] = []
        if _weak_login_hits(corpus, wt2):
            if _trusted_public_opportunity_context(url, titulo, descricao):
                return ACCESS_PUBLIC, ["http_403", "login_fraco_suprimido_contexto_publico"] + wt2
            return ACCESS_LOGIN, wt2
        terms.append("http_403")
        return ACCESS_IP, terms
    if _matches_any(corpus, tuple(_ERROR_PATTERNS), terms):
        if re.search(r"\b404\b|\b403\b|\b500\b", corpus) and len(corpus) < 800:
            return ACCESS_ERROR, terms
        if any(x in corpus for x in ("页面不存在", "ページが見つかりません", "page not found")):
            return ACCESS_ERROR, terms
    return ACCESS_PUBLIC, terms


def classify_opportunity_intent(corpus: str, url: str) -> str:
    u = url.lower()
    c = corpus
    proc = ("招标", "投标", "采购", "入札", "調達", "tender", "procurement", "bidding", "rfp")
    fund = ("公募", "募集", "助成", "grant", "funding", "fellowship", "资助", "基金", "课题")
    if any(x in c or x in u for x in proc):
        return INTENT_PROCUREMENT if any(k in c for k in ("招标", "投标", "采购", "tender", "bid")) else INTENT_TENDER
    if any(x in c for x in fund):
        return INTENT_FUNDING
    if any(x in c for x in ("奖学金", "奨学金", "fellowship", "scholarship", "bolsa")):
        return INTENT_SCHOLARSHIP
    if any(x in c for x in ("投资", "投資", "venture", "startup", "初创", "スタートアップ")):
        return INTENT_INVESTMENT
    if any(x in c for x in ("创新", "イノベーション", "innovation program", "accelerator")):
        return INTENT_INNOVATION
    if any(x in c for x in ("程序", "プログラム", "program", "scheme", "initiative")):
        return INTENT_INSTITUTIONAL
    if any(x in u for x in ("/news/", "news", "お知らせ")) and not any(k in c for k in _STRONG_POSITIVE):
        return INTENT_NEWS
    return INTENT_GENERIC


def _score_opportunity(
    corpus: str,
    url: str,
    titulo: str,
    descricao: str,
    extras: Optional[Dict[str, Any]],
    *,
    detail_missing: bool = False,
    official_pdf_hint: bool = False,
    trusted_fin_hint: bool = False,
) -> Tuple[int, List[str]]:
    score = 0
    hits: List[str] = []
    low = corpus.lower()
    for kw in _STRONG_POSITIVE:
        if kw.lower() in low or kw in corpus:
            score += 3
            hits.append(kw)
            break
    for pat in _DEADLINE_HINTS:
        if re.search(pat, corpus, re.IGNORECASE) or pat in low:
            if pat not in ("deadline", "締切", "截止", "期限", "due date"):
                score += 3
                hits.append("deadline_date")
                break
            if pat in corpus:
                score += 2
                hits.append("deadline_word")
                break
    if extras:
        if extras.get("pdf_url") or (extras.get("documentos") and len(extras.get("documentos") or []) > 0):
            score += 2
            hits.append("pdf_or_docs")
        elif official_pdf_hint and trusted_fin_hint:
            score += 2
            hits.append("pdf_link_same_as_item")
        for k in ("numero_edital", "numero_chamada", "numero_processo", "codigo_oportunidade"):
            v = extras.get(k)
            if isinstance(v, str) and len(v.strip()) >= 4:
                score += 2
                hits.append(k)
                break
    if any(v in low for v in _VALUE_HINTS):
        score += 2
        hits.append("value_hint")
    if any(v in low for v in _FORM_HINTS):
        score += 2
        hits.append("form_hint")
    if len((titulo or "").strip()) >= 12:
        score += 1
        hits.append("title_ok")
    if len((descricao or "").strip()) >= 200:
        score += 1
        hits.append("desc_long")

    tl_raw = (titulo or "").strip()
    tl = tl_raw.lower()
    if tl_raw in _GENERIC_TITLES or tl in _GENERIC_TITLES or len(tl_raw) < 6:
        if not (trusted_fin_hint and official_pdf_hint):
            score -= 3
            hits.append("generic_title")
    if len((descricao or "").strip()) < 80 and not detail_missing:
        if not (trusted_fin_hint and official_pdf_hint):
            score -= 2
            hits.append("short_desc")
    for g in _GENERIC_URL_PARTS:
        if g in url.lower():
            score -= 2
            hits.append(f"url_noise:{g}")
    if "/news/" in url.lower() and not any(k in corpus for k in ("招标", "公募", "募集", "tender", "grant", "申报")):
        score -= 3
        hits.append("news_url_weak")
    # Paginas de visao geral de pesquisa (universidades CN) — nao sao procurement
    if "kygk" in url.lower() or "/kxyj/kygk" in url.lower() or "科研概况" in (titulo or ""):
        score -= 8
        hits.append("research_overview_page")

    if trusted_fin_hint:
        bl = f"{titulo} {descricao} {url}".lower()
        mk = (
            "chamada",
            "edital",
            "licit",
            "programa",
            "fundo",
            "crédito",
            "credito",
            "financi",
            "bolsa",
            "consulta",
            "pregão",
            "pregao",
            "chamadas-publicas",
            "chamadapublica",
            "mercado-de-capitais",
            "fundos-de-investimento",
            "resultado",
            "subsidio",
            "subvencao",
            "subvenção",
        )
        if any(k in bl for k in mk):
            score += 2
            hits.append("br_finance_keyword_bonus")
        if official_pdf_hint:
            score += 2
            hits.append("br_pdf_url_bonus")

    return score, hits


def evaluate_crawl_candidate(
    *,
    titulo: str,
    descricao: str,
    link: str,
    status_code: Optional[int],
    raw_html: str = "",
    fonte: str = "",
    extras: Optional[Dict[str, Any]] = None,
    detail_missing: bool = False,
) -> GateResult:
    """Avalia um candidato logo apos fetch do detalhe (crawler Asia)."""
    corpus = f"{titulo}\n{descricao}\n{link}\n{raw_html[:8000]}"
    access, access_terms = detect_access_status(corpus, link, status_code, titulo=titulo, descricao=descricao)
    detected = list(access_terms)
    official_pdf = _is_official_pdf_link(link)
    trusted_fin = _is_br_trusted_finance_host(link) or _is_br_trusted_finance_fonte(fonte)

    if access in (ACCESS_LOGIN, ACCESS_IP, ACCESS_INTERNAL, ACCESS_ERROR, ACCESS_UNAVAILABLE):
        reason = {
            ACCESS_LOGIN: "Pagina de login ou autenticacao",
            ACCESS_IP: "Acesso restrito (IP/campus/intranet)",
            ACCESS_INTERNAL: "Rede interna / intranet",
            ACCESS_ERROR: "Pagina de erro ou indisponivel",
            ACCESS_UNAVAILABLE: "Recurso indisponivel",
        }.get(access, "Acesso bloqueado")
        return GateResult(
            keep=False,
            access_status=access,
            opportunity_intent=INTENT_INVALID,
            opportunity_score=-50,
            rejection_reason=reason,
            detected_terms=detected,
            trusted_fin_context=trusted_fin,
            gate_category=_derive_gate_category(
                access=access,
                intent=INTENT_INVALID,
                official_pdf=official_pdf,
                trusted_fin=trusted_fin,
            ),
        )

    intent = classify_opportunity_intent(corpus, link)
    if official_pdf and trusted_fin and intent == INTENT_GENERIC:
        intent = INTENT_INSTITUTIONAL
    score, hits = _score_opportunity(
        corpus,
        link,
        titulo,
        descricao,
        extras,
        detail_missing=detail_missing,
        official_pdf_hint=official_pdf,
        trusted_fin_hint=trusted_fin,
    )
    detected.extend(h for h in hits if h not in detected)

    hard_news_only = intent in (INTENT_NEWS, INTENT_GENERIC) and score < 3
    if score >= 4:
        keep = True
        reason = ""
    elif trusted_fin:
        if score >= 2:
            keep, reason = True, ""
        elif official_pdf and score >= 0:
            keep, reason = True, ""
        elif score >= 1 and len((titulo or "").strip()) >= 10 and _br_title_url_has_opportunity_marker(
            titulo, link
        ):
            keep, reason = True, ""
        elif (
            _strong_call_signal(corpus)
            and len((titulo or "").strip()) >= 8
            and link.startswith("http")
        ):
            keep, reason = True, ""
        else:
            keep = False
            if score >= 1:
                reason = "Relevancia limite: poucos sinais de oportunidade"
            else:
                reason = "Pontuacao abaixo do minimo (oportunidade nao evidenciada)"
    elif score >= 2:
        keep = (
            _strong_call_signal(corpus)
            and len((titulo or "").strip()) >= 8
            and link.startswith("http")
        )
        reason = "" if keep else "Relevancia limite: poucos sinais de oportunidade"
    else:
        keep = False
        reason = "Pontuacao abaixo do minimo (oportunidade nao evidenciada)"

    if hard_news_only and score < 5 and not trusted_fin:
        keep = False
        reason = reason or "Noticia ou pagina generica sem chamada evidenciada"

    if not link or not link.startswith("http"):
        keep = False
        reason = "Link invalido"

    return GateResult(
        keep=keep,
        access_status=access,
        opportunity_intent=intent,
        opportunity_score=score,
        rejection_reason=reason if not keep else "",
        detected_terms=detected,
        trusted_fin_context=trusted_fin,
        gate_category=_derive_gate_category(
            access=access,
            intent=intent,
            official_pdf=official_pdf,
            trusted_fin=trusted_fin,
        ),
    )


def evaluate_item_dict(item: Dict[str, Any]) -> GateResult:
    """Mesma logica para item JSON (transformer / loader)."""
    titulo = str(item.get("titulo") or "")
    descricao = str(item.get("descricao") or item.get("resumo") or "")
    link = str(item.get("link") or item.get("url") or "")
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    status = extras.get("http_status_detail")
    try:
        status_i = int(status) if status is not None and str(status).isdigit() else None
    except Exception:
        status_i = None
    raw = str(extras.get("raw_detail_html_snippet") or "")
    return evaluate_crawl_candidate(
        titulo=titulo,
        descricao=descricao,
        link=link,
        status_code=status_i,
        raw_html=raw,
        fonte=str(item.get("fonte") or ""),
        extras=extras,
        detail_missing=bool(extras.get("detail_fetch_failed")),
    )


def rejection_record(
    *,
    titulo: str,
    link: str,
    fonte: str,
    gate: GateResult,
    status_code: Optional[int],
) -> Dict[str, Any]:
    return {
        "titulo": titulo[:300],
        "link": link,
        "fonte": fonte,
        "access_status": gate.access_status,
        "rejection_reason": gate.rejection_reason or gate.access_status,
        "opportunity_intent": gate.opportunity_intent,
        "opportunity_score": gate.opportunity_score,
        "detected_terms": gate.detected_terms[:40],
        "status_code": status_code,
    }


def annotate_kept_extras(extras: Dict[str, Any], gate: GateResult) -> None:
    extras["opportunity_score"] = gate.opportunity_score
    extras["opportunity_intent"] = gate.opportunity_intent
    extras["access_status"] = gate.access_status
    extras["rejection_reason"] = ""
    extras["pipeline_drop"] = False
