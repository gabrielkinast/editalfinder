"""
Caminho controlado «official_link_only» / acesso_limitado: link oficial útil sem inventar
conteúdo quando houve barreira técnica (403/Cloudflare/HTML insuficiente).

Não altera opportunity_gate global — só critérios locais para candidatos.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

# Fontes onde este modo está explicitamente permitido (expandir só após diagnóstico).
# SAM.gov: deliberadamente fora desta allowlist — ver config/sam_gov_scope_policy.json
# (official_link_only_default: false); só habilitar após caso real documentado com notice/detail.
OFFICIAL_LINK_ONLY_SOURCES: Dict[str, Dict[str, Any]] = {
    "nato_diana": {
        "domains": ("diana.nato.int",),
        "min_path_segments": 1,
    },
    "iarpa": {
        "domains": ("iarpa.gov", "www.iarpa.gov", "grants.gov", "www.grants.gov"),
        "min_path_segments": 1,
    },
    "bae_systems_suppliers": {
        "domains": ("baesystems.com", "hicx.net"),
        "min_path_segments": 2,
    },
}

_OPPORTUNITY_SLUG_RES: Tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(call|challenge|funding|opportunity|grant|accelerator|programme|program|"
        r"solicitation|baa|foa|rfp|tender|edital|chamada|licit|pregao|pregão|contratacao|contratação)\b",
        re.I,
    ),
)

_GENERIC_PATH_MARKERS = (
    "/contact",
    "/contato",
    "/about",
    "/sobre",
    "/home",
    "/menu",
    "/news",
    "/noticias",
    "/press",
    "/cookie",
    "/privacy",
)

_HOMEPAGE_PATHS = frozenset({"/", "", "/index.html", "/default.htm", "/home", "/en/", "/pt-br/"})


def _is_iarpa_research_programs_hub(link: str) -> bool:
    """Hub de listagem — não é oportunidade concreta; não usar official_link_only aqui."""
    try:
        u = urlparse(link)
        host = _strip_www((u.hostname or "").lower())
        path = (u.path or "/").rstrip("/").lower() or "/"
    except Exception:
        return False
    if host != "iarpa.gov":
        return False
    return path == "/research-programs"


def _strip_www(host: str) -> str:
    h = (host or "").lower().strip()
    return h[4:] if h.startswith("www.") else h


def _host_ok(link: str, domains: Tuple[str, ...]) -> bool:
    try:
        h = (urlparse(link).hostname or "").lower()
    except Exception:
        return False
    if not h:
        return False
    hn = _strip_www(h)
    for d in domains:
        dl = str(d).lower().strip()
        if not dl:
            continue
        dn = _strip_www(dl)
        if h == dl or hn == dn or h.endswith("." + dn):
            return True
    return False


def _path_segments(link: str) -> List[str]:
    try:
        path = urlparse(link).path or "/"
    except Exception:
        return []
    return [p for p in path.strip("/").split("/") if p]


def _is_probably_homepage(link: str) -> bool:
    try:
        p = (urlparse(link).path or "/").rstrip("/").lower() or "/"
    except Exception:
        return True
    if p in _HOMEPAGE_PATHS or p == "":
        return True
    segs = [s for s in p.strip("/").split("/") if s]
    if len(segs) == 0:
        return True
    if len(segs) == 1 and segs[0].lower() in ("index.html", "default.htm", "home"):
        return True
    return False


def _generic_institutional_path(link: str) -> bool:
    low = link.lower()
    if any(m in low for m in _GENERIC_PATH_MARKERS):
        if not any(rx.search(low) for rx in _OPPORTUNITY_SLUG_RES):
            return True
    return False


def _title_or_url_opportunity_signal(titulo: str, link: str) -> bool:
    blob = f"{titulo} {link}".lower()
    return any(rx.search(blob) for rx in _OPPORTUNITY_SLUG_RES)


def _technical_extraction_barrier(extras: Dict[str, Any], descricao: str) -> Tuple[bool, str]:
    """
    True se há indício de bloqueio / HTML insuficiente vs página de detalhe esperada.
    access_reason ∈ {cloudflare_or_403, html_insuficiente}
    """
    ex = extras or {}
    raw = str(ex.get("raw_detail_html_snippet") or "").lower()
    if any(x in raw for x in ("cloudflare", "cf-ray", "checking your browser", "attention required")):
        return True, "cloudflare_or_403"
    st = ex.get("http_status_detail")
    if st is None:
        st = ex.get("http_status_code")
    if str(st) in ("403", "401", "429", "503"):
        return True, "cloudflare_or_403"
    if ex.get("detail_fetch_failed") is True:
        return True, "cloudflare_or_403"
    meth = str(ex.get("metodo_extracao") or "")
    if meth in (
        "curated_official_public_brief",
        "curated_official_manifest",
        "curated_hub_summary",
        "bae_baesystems_waf_stub",
        "bae_hicx_fetch_failed",
        "bae_hicx_challenge_html",
    ):
        # Conteúdo não veio de HTML vivo do detalhe — tratamos como html insuficiente no sentido operacional.
        return True, "html_insuficiente"
    if len((descricao or "").strip()) < 100 and (
        ex.get("listing_fetch_failed")
        or ex.get("detail_html_too_short")
        or ex.get("access_limitation_candidate") is True
    ):
        return True, "html_insuficiente"
    return False, ""


def _has_supporting_metadata(item: Dict[str, Any], extras: Dict[str, Any]) -> Tuple[bool, List[str]]:
    signals: List[str] = []
    if (item.get("data_publicacao") or "").strip():
        signals.append("data_publicacao")
    if (item.get("fim_inscricao") or "").strip():
        signals.append("fim_inscricao")
    if (item.get("programa") or "").strip():
        signals.append("programa")
    if (extras.get("orgao_contratante") or "").strip() or (extras.get("instituicao") or "").strip():
        signals.append("orgao_ou_instituicao")
    if (extras.get("codigo_oportunidade") or "").strip() or (extras.get("numero_chamada") or "").strip():
        signals.append("codigo_ou_chamada")
    if isinstance(extras.get("documentos"), list) and len(extras.get("documentos") or []) > 0:
        signals.append("documentos")
    if str(extras.get("pdf_url") or "").strip().lower().startswith("http"):
        signals.append("pdf_url")
    if (extras.get("origem_portal") or "").strip() or (extras.get("url_detalhe") or "").strip():
        signals.append("portal_ou_url_detalhe")
    if isinstance(extras.get("subtema"), list) and len(extras.get("subtema") or []) > 0:
        signals.append("subtema")
    if (extras.get("tipo_oportunidade") or "").strip():
        signals.append("tipo_oportunidade")
    return len(signals) >= 1, signals


def is_official_link_only_candidate(item: Dict[str, Any], source_name: str) -> Dict[str, Any]:
    """
    Avalia se o item pode seguir como «official_link_only» (sem inventar dados).

    Devolve dict com accepted, reason, signals, missing, access_reason, suggested_confidence.
    """
    src = (source_name or "").strip().lower()
    cfg = OFFICIAL_LINK_ONLY_SOURCES.get(src)
    out: Dict[str, Any] = {
        "accepted": False,
        "reason": "",
        "signals": [],
        "missing": [],
        "access_reason": "",
        "suggested_confidence": "baixa",
    }
    if not cfg:
        out["reason"] = "fonte_fora_da_allowlist_official_link_only"
        out["missing"].append("allowlist")
        return out

    link = str(item.get("link") or item.get("url") or item.get("url_pagina") or "").strip()
    titulo = str(item.get("titulo") or "").strip()
    descricao = str(item.get("descricao") or item.get("resumo") or "").strip()
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}

    if not link.startswith("http"):
        out["reason"] = "sem_link_http"
        out["missing"].append("link")
        return out

    domains: Tuple[str, ...] = tuple(cfg.get("domains") or ())
    if not _host_ok(link, domains):
        out["reason"] = "dominio_nao_oficial_para_fonte"
        out["missing"].append("dominio_oficial")
        return out

    if src == "iarpa" and _is_iarpa_research_programs_hub(link):
        out["reason"] = "iarpa_research_programs_hub"
        return out

    if _is_probably_homepage(link):
        out["reason"] = "homepage_ou_raiz"
        out["missing"].append("profundidade_url")
        return out

    if _generic_institutional_path(link) and not _title_or_url_opportunity_signal(titulo, link):
        out["reason"] = "pagina_institucional_generica"
        return out

    segs = _path_segments(link)
    min_seg = int(cfg.get("min_path_segments") or 1)
    if len(segs) < min_seg:
        out["reason"] = "profundidade_url_insuficiente"
        out["missing"].append("path_depth")
        return out

    if not _title_or_url_opportunity_signal(titulo, link):
        if src == "bae_systems_suppliers":
            blob = f"{titulo} {link}".lower()
            if any(
                x in blob
                for x in (
                    "supplier",
                    "registration",
                    "vendor",
                    "procurement",
                    "portal",
                    "hicx",
                    "discovery-login",
                    "supply-chain",
                    "suppliers",
                    "responsible-supply",
                )
            ):
                pass
            else:
                out["reason"] = "sem_sinal_de_oportunidade_em_titulo_ou_url"
                out["missing"].append("opportunity_slug")
                return out
        else:
            out["reason"] = "sem_sinal_de_oportunidade_em_titulo_ou_url"
            out["missing"].append("opportunity_slug")
            return out

    tech_ok, access_reason = _technical_extraction_barrier(extras, descricao)
    if not tech_ok:
        out["reason"] = "sem_evidencia_de_bloqueio_ou_html_insuficiente"
        out["missing"].append("technical_barrier")
        return out

    meta_ok, meta_sigs = _has_supporting_metadata(item, extras)
    if not meta_ok:
        out["reason"] = "sem_metadado_extra_minimo"
        out["missing"].append("metadata")
        return out

    out["accepted"] = True
    out["reason"] = "ok"
    out["signals"] = meta_sigs + [f"tech:{access_reason}"]
    out["access_reason"] = access_reason
    # Confiança: mais metadados → média; caso mínimo → baixa
    out["suggested_confidence"] = "media" if len(meta_sigs) >= 3 else "baixa"
    return out


def official_link_only_extras_patch(
    item: Dict[str, Any],
    source_name: str,
    gate_keep: bool,
    gate_access: str,
    gate_reason: str,
) -> Optional[Dict[str, Any]]:
    """
    Se o gate rejeitou por relevância fraca mas o item cumpre critérios locais,
    devolve campos a fundir em extras; caso contrário None.
    """
    from CORE.opportunity_gate import (
        ACCESS_ERROR,
        ACCESS_INTERNAL,
        ACCESS_IP,
        ACCESS_LOGIN,
        ACCESS_UNAVAILABLE,
    )

    if gate_keep:
        return None
    if gate_access in (
        ACCESS_LOGIN,
        ACCESS_IP,
        ACCESS_INTERNAL,
        ACCESS_ERROR,
        ACCESS_UNAVAILABLE,
    ):
        return None
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return None

    cand = is_official_link_only_candidate(item, source_name)
    if not cand.get("accepted"):
        return None

    conf = cand.get("suggested_confidence") or "baixa"
    return {
        "extraction_mode": "official_link_only",
        "access_status": "access_limited",
        "access_reason": cand.get("access_reason") or "html_insuficiente",
        "requires_manual_review": True,
        "official_link_verified": True,
        "official_link_only_signals": list(cand.get("signals") or []),
        "classificacao_confianca": conf,
        "official_link_only_confidence_level": conf,
    }
