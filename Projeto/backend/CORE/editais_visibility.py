"""
Classificação de visibilidade / ruído para public.edital (aba Editais).

Regra: editais_visibility_v1 — não altera banco; usado por scripts/audit_editais_visibility_noise.py
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

RULE_VERSION = "editais_visibility_v1"

VISIBLE_VALUES = frozenset(
    {
        "visible_current",
        "visible_continuous_flow",
        "visible_recent_strong_signal",
        "visible_manual_reviewed",
    }
)

REVIEW_VALUES = frozenset(
    {
        "review_missing_deadline",
        "review_possible_opportunity",
        "review_possible_continuous_flow",
        "review_link_suspicious",
    }
)

HIDDEN_VALUES = frozenset(
    {
        "hidden_historical",
        "hidden_institutional",
        "hidden_resultado",
        "hidden_invalid_link",
        "hidden_not_opportunity",
        "hidden_duplicate",
        "hidden_expired",
    }
)

BROKEN_LINK_STATUSES = frozenset(
    {"broken_404", "broken_spa_not_found", "invalid_url", "timeout"}
)

CONTINUOUS_FLOW_PHRASES = (
    "fluxo contínuo",
    "fluxo continuo",
    "continuous submission",
    "continuously open",
    "open continuously",
    "chamada permanente",
    "credenciamento contínuo",
    "rolling basis",
    "until funds are exhausted",
    "enquanto houver recursos",
    "open on a rolling",
    "always open",
)

STRONG_OPPORTUNITY_PHRASES = (
    "edital",
    "chamada pública",
    "chamada publica",
    "chamada",
    "seleção pública",
    "selecao publica",
    "submissão",
    "submissao",
    "inscrição",
    "inscricao",
    "proposta",
    "envio de proposta",
    "fomento",
    "subvenção",
    "subvencao",
    "bolsa",
    "financiamento",
    "apoio financeiro",
    "credenciamento",
    "programa",
    "oportunidade",
    "chamada vigente",
    "funding opportunity",
    "solicitation",
    "proposal",
    "request for proposals",
    "call for proposals",
    "grant",
    "award",
    "open date",
    "close date",
    "deadline",
    "sbir",
    "sttr",
    "baa",
    "nofo",
    "foa",
    "funding",
    "convocatoria",
    "subvención",
    "subvencion",
    "financiación",
    "financiacion",
    "beca",
    "licitação",
    "licitacao",
    "pregão",
    "pregao",
)

INSTITUTIONAL_PHRASES = (
    "página inicial",
    "pagina inicial",
    "page d'accueil",
    "home page",
    "homepage",
    " código de conduta",
    "codigo de conduta",
    "code of conduct",
    "integridade",
    "política de privacidade",
    "politica de privacidade",
    "privacy policy",
    "governança",
    "governanca",
    "relatório anual",
    "relatorio anual",
    "prestação de contas",
    "prestacao de contas",
    "regulamento interno",
    "transparência ativa",
    "transparencia ativa",
    "organograma",
    "diretoria",
    "institucional",
    "quem somos",
    "missão e visão",
    "missao e visao",
    "liderança",
    "leadership team",
    "about us",
    "about the agency",
    "contact us",
    "entre em contato",
    "fale conosco",
)

RESULTADO_PHRASES = (
    "resultado final",
    "resultado preliminar",
    "homologação",
    "homologacao",
    "classificação final",
    "classificacao final",
    "recursos",
    "julgamento",
    "ata de",
    "comunicado de resultado",
    "lista de aprovados",
    "retificação isolada",
    "retificacao isolada",
    "errata isolada",
    "final result",
    "preliminary result",
    "award notice",
    "selected projects",
    "winners announced",
)

NOT_OPPORTUNITY_TYPES = frozenset(
    {
        "noticia institucional",
        "pagina institucional",
        "página institucional",
        "portal",
        "noticia",
        "notícia",
        "relatorio",
        "relatório",
        "publicacao",
        "publicação",
    }
)

NOT_OPPORTUNITY_PHRASES = (
    "notícia",
    "noticia",
    "news release",
    "press release",
    "artigo científico",
    "artigo cientifico",
    "publicação científica",
    "relatório técnico",
    "relatorio tecnico",
    "blog post",
    "portal de",
    "página genérica",
    "pagina generica",
)

SOURCE_HINTS: Dict[str, Dict[str, Any]] = {
    "nuclep": {
        "hide_institutional_extra": True,
        "notes": "Ocultar código de conduta, home e institucional; manter licitação com objeto.",
    },
    "embrapii": {
        "hide_resultado": True,
        "prefer_years": (2025, 2026),
        "notes": "Resultados finais e chamadas antigas encerradas.",
    },
    "nedo": {
        "hide_institutional_pdf": True,
        "notes": "Regulamentos/PDFs sem chamada ativa.",
    },
    "grants": {
        "use_link_health": True,
        "prefer_simpler_canonical": True,
        "notes": (
            "Rota canônica Simpler.Grants.gov (/opportunity/…); "
            "view-opportunity.html?oppId legado → broken_spa_not_found / corrigir_url."
        ),
    },
    "grants.gov": {"use_link_health": True, "prefer_simpler_canonical": True},
    "afwerx": {
        "prefer_future_close": True,
        "notes": "Specific Topic com close date 2026; BAA/SBIR com prazo futuro.",
    },
    "senai": {"continuous_ok": True},
    "plataforma inovação": {"continuous_ok": True},
    "plataforma inovacao": {"continuous_ok": True},
    "amazul": {"licitacao_focus": True},
    "aneel": {"pdi_continuous": True},
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm(s: Any) -> str:
    if s is None:
        return ""
    t = str(s).strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def _extras(item: Dict[str, Any]) -> Dict[str, Any]:
    ex = item.get("extras")
    return ex if isinstance(ex, dict) else {}


def _parse_date(val: Any) -> Optional[date]:
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    s = str(val).strip()[:10]
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _deadline_dates(item: Dict[str, Any]) -> List[date]:
    ex = _extras(item)
    keys = (
        "prazo_envio",
        "fim_inscricao",
        "data_fim_inscricao",
        "data_encerramento",
        "close_date",
        "closeDate",
        "data_limite",
    )
    out: List[date] = []
    for k in keys:
        d = _parse_date(item.get(k) if k == "prazo_envio" else ex.get(k) or item.get(k))
        if d:
            out.append(d)
    d = _parse_date(item.get("prazo_envio"))
    if d:
        out.append(d)
    return out


def _max_deadline(item: Dict[str, Any]) -> Optional[date]:
    ds = _deadline_dates(item)
    return max(ds) if ds else None


def _publication_date(item: Dict[str, Any]) -> Optional[date]:
    ex = _extras(item)
    for k in ("data_publicacao", "posted_date", "postDate", "data_publicacao_original"):
        d = _parse_date(item.get(k) or ex.get(k))
        if d:
            return d
    return _parse_date(item.get("data_publicacao"))


def _combined_text(item: Dict[str, Any]) -> str:
    ex = _extras(item)
    parts = [
        item.get("titulo"),
        item.get("descricao"),
        item.get("objetivo"),
        item.get("link"),
        item.get("link_inscricao"),
        ex.get("objetivo"),
        ex.get("titulo_original"),
        ex.get("descricao_original"),
    ]
    return _norm(" ".join(str(p) for p in parts if p))


def _years_in_text(text: str) -> List[int]:
    return [int(y) for y in re.findall(r"\b(20\d{2})\b", text)]


def _has_phrase(text: str, phrases: Tuple[str, ...]) -> bool:
    return any(p in text for p in phrases)


def _strong_opportunity_signal(text: str) -> bool:
    return _has_phrase(text, STRONG_OPPORTUNITY_PHRASES)


def _continuous_flow(item: Dict[str, Any], text: str) -> bool:
    ex = _extras(item)
    st = _norm(ex.get("status_prazo") or item.get("status_prazo") or item.get("situacao"))
    if st in ("fluxo_continuo", "fluxo continuo", "continuous", "rolling"):
        return True
    if _has_phrase(text, CONTINUOUS_FLOW_PHRASES):
        return True
    if _norm(item.get("tipo_oportunidade")) in ("fluxo_continuo", "credenciamento", "rolling"):
        return True
    return False


def _is_institutional(text: str, link: str) -> bool:
    if _has_phrase(text, INSTITUTIONAL_PHRASES):
        return True
    low = link.lower()
    if any(x in low for x in ("/about", "/contact", "/privacy", "/governance", "/home", "/index")):
        if not _strong_opportunity_signal(text):
            return True
    if re.search(r"\bfaq\b", text) and "edital" not in text and "chamada" not in text:
        return True
    return False


def _is_resultado(text: str) -> bool:
    if not _has_phrase(text, RESULTADO_PHRASES):
        return False
    if _strong_opportunity_signal(text) and any(
        x in text for x in ("inscrição", "inscricao", "submissão", "submissao", "aberta", "open")
    ):
        return False
    return True


def _is_not_opportunity(item: Dict[str, Any], text: str) -> bool:
    tipo_o = _norm(item.get("tipo_oportunidade"))
    tipo_r = _norm(item.get("tipo_recurso"))
    ex = _extras(item)
    ct = _norm(ex.get("content_type") or ex.get("content_type_detectado") or "")
    if tipo_o in NOT_OPPORTUNITY_TYPES or tipo_r in NOT_OPPORTUNITY_TYPES:
        return True
    if ct in ("noticia", "pesquisa", "portal", "notícia"):
        return True
    if ex.get("destination_table") in ("noticia", "pesquisa"):
        return True
    if _has_phrase(text, NOT_OPPORTUNITY_PHRASES) and not _strong_opportunity_signal(text):
        return True
    return False


def _link_health_status(item: Dict[str, Any]) -> Tuple[Optional[str], bool]:
    """(aggregate_status, has_valid_essential_link)."""
    ex = _extras(item)
    lh = ex.get("link_health")
    if not isinstance(lh, dict):
        return None, bool(_norm(item.get("link")))
    st = _norm(lh.get("link_status"))
    if lh.get("has_accessible_link") is True:
        return st or "ok", True
    fields = lh.get("fields")
    if isinstance(fields, list):
        for f in fields:
            if not isinstance(f, dict):
                continue
            fst = _norm(f.get("link_status"))
            if fst in ("ok", "redirect_ok"):
                return st or fst, True
    if st in BROKEN_LINK_STATUSES:
        return st, False
    return st, st in ("ok", "redirect_ok", "")


def _normalize_link_key(link: str) -> str:
    u = (link or "").strip().lower().rstrip("/")
    if not u:
        return ""
    try:
        p = urlparse(u)
        return f"{p.netloc}{p.path}?{p.query}".rstrip("?")
    except Exception:
        return u


def _is_expired(item: Dict[str, Any], today: date, *, continuous: bool) -> bool:
    if continuous:
        return False
    ex = _extras(item)
    st = _norm(ex.get("status_prazo") or item.get("situacao") or item.get("status"))
    if st in ("encerrado", "encerrada", "closed", "expired", "finalizado", "inativo"):
        if not _strong_opportunity_signal(_combined_text(item)):
            return True
    max_d = _max_deadline(item)
    if max_d and max_d < today:
        return True
    return False


def _is_historical(item: Dict[str, Any], text: str, today: date, *, continuous: bool) -> bool:
    if continuous:
        return False
    years = _years_in_text(text)
    if not years:
        return False
    if max(years) > 2024:
        return False
    if _max_deadline(item) and _max_deadline(item) >= today:
        return False
    if _strong_opportunity_signal(text) and _publication_date(item):
        pub = _publication_date(item)
        if pub and pub >= today - timedelta(days=365):
            return False
    if max(years) <= 2024:
        return True
    return False


def _source_key(fonte: str) -> str:
    return _norm(fonte).replace(".gov", "").replace(" ", " ").strip()


def classify_edital_visibility(
    item: Dict[str, Any],
    *,
    today: Optional[date] = None,
    seen_links: Optional[Set[str]] = None,
    seen_hashes: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """
    Retorna dict com visibility, reason, confidence, rule_version, checked_at, signals, source_recommendation.
    """
    today = today or date.today()
    ex = _extras(item)
    text = _combined_text(item)
    link = str(item.get("link") or "").strip()
    fonte = str(item.get("fonte_recurso") or item.get("fonte") or "").strip()
    sk = _source_key(fonte)
    signals: List[str] = []

    # --- hidden: duplicate ---
    h = str(ex.get("hash_deduplicacao") or item.get("hash_deduplicacao") or "").strip()
    lk = _normalize_link_key(link)
    if seen_links is not None and lk and lk in seen_links:
        return _result(
            "hidden_duplicate",
            "Link normalizado já visto nesta auditoria.",
            "alta",
            signals + ["duplicate_link"],
            fonte,
            sk,
        )
    if seen_hashes is not None and h and h in seen_hashes:
        return _result(
            "hidden_duplicate",
            "hash_deduplicacao duplicado.",
            "alta",
            signals + ["duplicate_hash"],
            fonte,
            sk,
        )
    if seen_links is not None and lk:
        seen_links.add(lk)
    if seen_hashes is not None and h:
        seen_hashes.add(h)

    if item.get("ativo") is False or item.get("ativo") == 0:
        return _result(
            "hidden_expired",
            "Registro marcado ativo=false.",
            "alta",
            ["ativo_false"],
            fonte,
            sk,
        )

    continuous = _continuous_flow(item, text)
    if continuous:
        signals.append("continuous_flow")

    # --- hidden: not opportunity ---
    if _is_not_opportunity(item, text):
        return _result(
            "hidden_not_opportunity",
            "Conteúdo classificado como notícia/portal/página institucional, sem chamada ativa.",
            "alta" if not _strong_opportunity_signal(text) else "media",
            signals + ["not_opportunity"],
            fonte,
            sk,
        )

    # --- hidden: institutional ---
    if _is_institutional(text, link):
        return _result(
            "hidden_institutional",
            "Sinais de página institucional (home, conduta, governança, etc.).",
            "alta",
            signals + ["institutional"],
            fonte,
            sk,
        )

    # --- hidden: resultado ---
    if _is_resultado(text) or (
        SOURCE_HINTS.get(sk, {}).get("hide_resultado") and _is_resultado(text)
    ):
        return _result(
            "hidden_resultado",
            "Resultado/homologação/ata sem chamada ativa associada.",
            "alta",
            signals + ["resultado"],
            fonte,
            sk,
        )

    # --- hidden: invalid link ---
    lh_st, has_valid = _link_health_status(item)
    if lh_st in BROKEN_LINK_STATUSES and not has_valid:
        return _result(
            "hidden_invalid_link",
            f"link_health={lh_st}; sem outro link essencial válido.",
            "alta",
            signals + [f"link_health:{lh_st}"],
            fonte,
            sk,
        )
    if lh_st in ("forbidden_403", "suspicious"):
        signals.append(f"link_health:{lh_st}")

    # --- hidden: expired ---
    if _is_expired(item, today, continuous=continuous):
        return _result(
            "hidden_expired",
            "Prazo de envio/inscrição encerrado sem fluxo contínuo.",
            "alta",
            signals + ["expired_deadline"],
            fonte,
            sk,
        )

    # --- hidden: historical ---
    if _is_historical(item, text, today, continuous=continuous):
        return _result(
            "hidden_historical",
            "Referência temporal ≤2024 sem prazo futuro nem fluxo contínuo.",
            "media",
            signals + ["historical_year"],
            fonte,
            sk,
        )

    # --- visible paths ---
    max_d = _max_deadline(item)
    pub = _publication_date(item)
    qual = item.get("qualidade_dado")
    try:
        qual_n = float(qual) if qual is not None else 0.0
    except (TypeError, ValueError):
        qual_n = 0.0
    vs = _norm(item.get("validacao_status"))

    if ex.get("curadoria_front", {}).get("visibility") == "visible_manual_reviewed":
        return _result(
            "visible_manual_reviewed",
            "Curadoria manual positiva em extras.",
            "alta",
            signals + ["manual_reviewed"],
            fonte,
            sk,
        )

    if continuous:
        return _result(
            "visible_continuous_flow",
            "Fluxo contínuo ou chamada permanente.",
            "alta",
            signals,
            fonte,
            sk,
        )

    if max_d and max_d >= today:
        return _result(
            "visible_current",
            f"Prazo futuro ({max_d.isoformat()}).",
            "alta",
            signals + ["future_deadline"],
            fonte,
            sk,
        )

    if pub and pub >= today - timedelta(days=365) and _strong_opportunity_signal(text):
        if qual_n >= 70 or vs == "valido":
            return _result(
                "visible_recent_strong_signal",
                "Publicação recente (12m) com sinal forte de oportunidade.",
                "media",
                signals + ["recent_strong"],
                fonte,
                sk,
            )

    if vs == "valido" and qual_n >= 80 and not _is_institutional(text, link):
        return _result(
            "visible_recent_strong_signal",
            "validacao_status=valido e qualidade_dado≥80.",
            "media",
            signals + ["high_quality"],
            fonte,
            sk,
        )

    # --- review ---
    if lh_st in ("forbidden_403", "suspicious"):
        return _result(
            "review_link_suspicious",
            f"Link com status {lh_st}; revisar manualmente.",
            "media",
            signals,
            fonte,
            sk,
        )

    if continuous and not max_d:
        return _result(
            "review_possible_continuous_flow",
            "Possível fluxo contínuo sem prazo explícito.",
            "media",
            signals,
            fonte,
            sk,
        )

    if not max_d and _strong_opportunity_signal(text):
        return _result(
            "review_missing_deadline",
            "Oportunidade plausível sem prazo_envio/data_fim registrados.",
            "media",
            signals + ["missing_deadline"],
            fonte,
            sk,
        )

    if _strong_opportunity_signal(text):
        return _result(
            "review_possible_opportunity",
            "Sinal de oportunidade sem critério temporal claro.",
            "baixa",
            signals,
            fonte,
            sk,
        )

    return _result(
        "hidden_historical",
        "Sem prazo futuro, fluxo contínuo ou sinal forte recente.",
        "baixa",
        signals + ["fallback_hidden"],
        fonte,
        sk,
    )


def _result(
    visibility: str,
    reason: str,
    confidence: str,
    signals: List[str],
    fonte: str,
    sk: str,
) -> Dict[str, Any]:
    rec = _source_recommendation_for_item(visibility, sk)
    return {
        "visibility": visibility,
        "reason": reason,
        "confidence": confidence,
        "rule_version": RULE_VERSION,
        "checked_at": utc_now_iso(),
        "signals": list(dict.fromkeys(signals)),
        "source_recommendation": rec,
        "fonte_recurso": fonte,
    }


def _source_recommendation_for_item(visibility: str, sk: str) -> str:
    if visibility in VISIBLE_VALUES:
        return "manter_ativa"
    if visibility == "review_link_suspicious":
        return "revisar_manual"
    if visibility in REVIEW_VALUES:
        return "manter_com_curadoria"
    if visibility == "hidden_invalid_link":
        return "precisa_melhoria_crawler"
    if visibility in ("hidden_institutional", "hidden_not_opportunity"):
        return "precisa_melhoria_crawler"
    if visibility == "hidden_historical" or visibility == "hidden_expired":
        return "latente"
    return "manter_com_curadoria"


def build_curadoria_front(classification: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "visibility": classification["visibility"],
        "reason": classification["reason"],
        "confidence": classification["confidence"],
        "checked_at": classification["checked_at"],
        "rule_version": classification["rule_version"],
        "signals": classification.get("signals") or [],
        "source_recommendation": classification.get("source_recommendation") or "",
    }


def aggregate_source_report(
    rows: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Por fonte_recurso: totais, hidden reasons, exemplos."""
    by_fonte: Dict[str, Dict[str, Any]] = {}

    def bucket(fonte: str) -> Dict[str, Any]:
        if fonte not in by_fonte:
            by_fonte[fonte] = {
                "fonte_recurso": fonte,
                "total": 0,
                "visible_current": 0,
                "visible_other": 0,
                "review": 0,
                "hidden": 0,
                "hidden_by_reason": {},
                "noise_examples": [],
                "good_examples": [],
                "recommendation": "manter_com_curadoria",
            }
        return by_fonte[fonte]

    for row in rows:
        fonte = str(row.get("fonte_recurso") or "—").strip() or "—"
        b = bucket(fonte)
        b["total"] += 1
        vis = row.get("visibility") or ""
        if vis == "visible_current":
            b["visible_current"] += 1
        elif vis in VISIBLE_VALUES:
            b["visible_other"] += 1
        elif vis in REVIEW_VALUES:
            b["review"] += 1
        elif vis in HIDDEN_VALUES:
            b["hidden"] += 1
            b["hidden_by_reason"][vis] = b["hidden_by_reason"].get(vis, 0) + 1

        tit = str(row.get("titulo") or "")[:100]
        ex = {"id_edital": row.get("id_edital"), "titulo": tit, "visibility": vis, "reason": row.get("reason")}
        if vis in HIDDEN_VALUES and len(b["noise_examples"]) < 5:
            b["noise_examples"].append(ex)
        if vis in ("visible_current", "visible_continuous_flow") and len(b["good_examples"]) < 3:
            b["good_examples"].append(ex)

    for fonte, b in by_fonte.items():
        total = b["total"] or 1
        hidden_pct = b["hidden"] / total
        visible_pct = (b["visible_current"] + b["visible_other"]) / total
        if hidden_pct >= 0.65:
            b["recommendation"] = "precisa_melhoria_crawler"
        elif hidden_pct >= 0.45:
            b["recommendation"] = "latente"
        elif visible_pct >= 0.5:
            b["recommendation"] = "manter_ativa"
        elif b["review"] / total >= 0.35:
            b["recommendation"] = "manter_com_curadoria"
        elif hidden_pct >= 0.25:
            b["recommendation"] = "revisar_manual"
        sk = _source_key(fonte)
        if any(x in sk for x in ("grants", "nuclep", "embrapii")) and hidden_pct > 0.4:
            b["recommendation"] = "precisa_melhoria_crawler"

    return {"sources": sorted(by_fonte.values(), key=lambda x: (-x["hidden"], -x["total"], x["fonte_recurso"]))}
