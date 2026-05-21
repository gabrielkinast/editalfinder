#!/usr/bin/env python3
"""
Diagnóstico — MCTI Transformação Digital / Fomento (sem apply).

Classifica links e gera relatório em audit_reports_news_research/mcti_fomento_diagnostic/
"""
from __future__ import annotations

import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "audit_reports_news_research" / "mcti_fomento_diagnostic"
URL = "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/transformacaodigital/fomento-1"
URL_ARQUIVOS = "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/transformacaodigital/Fomento"
HEADERS = {
    "User-Agent": "EditalFinderBot/1.0 (+public scientific/news monitoring)",
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def _http_get(url: str, timeout: int = 120, retries: int = 5) -> Optional[requests.Response]:
    session = requests.Session()
    session.headers.update(HEADERS)
    for i in range(retries):
        try:
            r = session.get(url, timeout=timeout)
            if r.status_code < 400 and len(r.text or "") > 500:
                return r
        except Exception:
            pass
        if i < retries - 1:
            time.sleep(3.0 * (i + 1))
    return None


def _classify_item(titulo: str, link: str, contexto: str = "", in_content_core: bool = True) -> Tuple[str, str]:
    """Retorna (classificacao, motivo)."""
    b = f"{titulo} {link} {contexto}".lower()
    path = urlparse(link).path.lower()

    if link.lower().endswith(".pdf"):
        if any(k in b for k in ("edital", "chamamento", "chamada", "retific", "resultado", "anexo")):
            return "edital_chamada", "pdf_edital_ou_chamamento"
        return "radar_oportunidade", "pdf_programa_ou_anexo"

    if any(k in b for k in ("edital de chamamento", "edital n", "edital no", "chamamento público", "chamamento publico")):
        return "edital_chamada", "titulo_ou_url_edital_chamamento"
    if "/acesso-a-informacao/editais/" in path or "/editais/edital" in path:
        return "edital_chamada", "url_repositorio_editais_mcti"
    if "in.gov.br" in link.lower() and "edital" in b:
        return "edital_chamada", "publicacao_dou_edital"

    if re.search(r"/noticias/\d{4}$", path) or path.endswith("/noticias"):
        return "institucional_latente", "indice_noticias_ano"
    if "/acompanhe-o-mcti/noticias/" in path and re.search(r"/noticias/[^/]+$", path):
        return "noticia", "artigo_noticias_mcti"
    if "comunicado" in b and any(k in b for k in ("chamamento", "sessão", "sessao", "habilitação", "habilitacao")):
        return "radar_oportunidade", "comunicado_processo_seletivo"
    if "comunicado" in path or "/comunicado" in path:
        return "radar_oportunidade", "comunicado_chamamento"

    if any(
        k in b
        for k in (
            "inscrições abertas",
            "inscricoes abertas",
            "prazo até",
            "prazo ate",
            "submissão de propostas",
            "submissao de propostas",
        )
    ):
        return "radar_oportunidade", "indicio_prazo_ou_inscricao"

    if any(
        k in b
        for k in (
            "bolsa científica",
            "bolsa cientifica",
            "fomento",
            "programa",
            "linha de crédito",
            "financiamento",
            "chamamento",
            "transformação digital",
            "transformacao digital",
        )
    ):
        if path.rstrip("/").endswith(("fomento-1", "fomento")) and in_content_core:
            return "institucional_latente", "hub_fomento_self"
        return "radar_oportunidade", "programa_ou_linha_fomento"

    if any(k in b for k in ("licitações", "licitacoes", "pregão", "pregao", "contratos")):
        return "edital_chamada", "licitacao_contratacao_publica"

    if any(k in b for k in ("acesso à informação", "acesso a informacao", "mapa do site", "ouvidoria", "lgpd")):
        return "institucional_latente", "menu_govbr_institucional"

    if "gov.br/mcti" in link.lower():
        return "institucional_latente", "pagina_institucional_mcti"

    return "institucional_latente", "sem_sinal_oportunidade"


def _extract_links(soup: BeautifulSoup, base_url: str, scope: str) -> List[Dict[str, Any]]:
    root = soup.select_one("#content-core") if scope == "content_core" else soup
    if root is None:
        root = soup
    out: List[Dict[str, Any]] = []
    seen: set = set()
    for a in root.find_all("a", href=True):
        href = (a.get("href") or "").strip()
        if href.startswith(("#", "mailto:", "javascript:")):
            continue
        full = urljoin(base_url, href).split("#", 1)[0]
        if full in seen:
            continue
        seen.add(full)
        titulo = re.sub(r"\s+", " ", a.get_text() or "").strip()
        if len(titulo) < 2 and not full.lower().endswith(".pdf"):
            continue
        ctx_el = a.find_parent(["li", "p", "td", "div"])
        contexto = ""
        if ctx_el:
            contexto = re.sub(r"\s+", " ", ctx_el.get_text() or "").strip()[:400]
        cls, motivo = _classify_item(
            titulo or full.rsplit("/", 1)[-1],
            full,
            contexto,
            in_content_core=(scope == "content_core"),
        )
        out.append(
            {
                "titulo": (titulo or full.rsplit("/", 1)[-1])[:220],
                "link": full[:500],
                "classificacao": cls,
                "motivo": motivo,
                "contexto_amostra": contexto[:200] if contexto else None,
                "is_pdf": full.lower().endswith(".pdf"),
            }
        )
    return out


def _extract_dates_prazos(text: str) -> Dict[str, List[str]]:
    dates = sorted(set(re.findall(r"\b\d{1,2}/\d{1,2}/20\d{2}\b", text[:25000])))
    prazos = []
    for m in re.finditer(
        r"(?i)(prazo[s]?\s*(?:de|para|até|ate)?[^.;]{5,90}|inscrições?\s+abertas[^.;]{0,80}|até\s+\d{1,2}/\d{1,2}/20\d{2})",
        text[:25000],
    ):
        prazos.append(re.sub(r"\s+", " ", m.group(0)).strip()[:120])
    return {"datas_dd_mm_yyyy": dates[:30], "prazos_texto": prazos[:20]}


def _robots_summary() -> Dict[str, str]:
    out: Dict[str, str] = {}
    for u in ("https://www.gov.br/robots.txt", "https://www.gov.br/mcti/robots.txt"):
        r = _http_get(u, timeout=25, retries=2)
        if not r:
            out[u] = "fetch_failed"
            continue
        body = r.text or ""
        disallow_mcti = [ln for ln in body.splitlines() if "mcti" in ln.lower() and "disallow" in ln.lower()]
        out[u] = (
            "Disallow vazio para User-agent * (mcti)"
            if u.endswith("/mcti/robots.txt") and "Disallow:\n" in body.replace(" ", "")
            else ("; ".join(disallow_mcti[:3]) if disallow_mcti else "permitido (sem Disallow específico mcti)")
        )
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    errors: List[Dict[str, str]] = []

    cache_path = OUT / "_cache_page.html"
    html_body = ""
    fetch_meta: Dict[str, Any] = {"url": URL, "from_cache": False}
    resp = _http_get(URL)
    if resp:
        html_body = resp.text or ""
        cache_path.write_text(html_body, encoding="utf-8")
        fetch_meta["status"] = resp.status_code
        fetch_meta["bytes"] = len(html_body)
    elif cache_path.is_file():
        html_body = cache_path.read_text(encoding="utf-8")
        fetch_meta["from_cache"] = True
        fetch_meta["bytes"] = len(html_body)
        fetch_meta["status"] = 200
    if not html_body:
        print("[ERRO] Falha ao obter página principal (sem cache)", file=__import__("sys").stderr)
        return 1

    soup = BeautifulSoup(html_body, "html.parser")
    h1 = [re.sub(r"\s+", " ", x.get_text()).strip() for x in soup.find_all("h1")]
    title = (soup.title.string or "").strip() if soup.title else ""

    core = soup.select_one("#content-core")
    core_text = core.get_text("\n", strip=True) if core else ""
    dates_prazos = _extract_dates_prazos(core_text)

    links_page = _extract_links(soup, URL, "content_core")
    links_full = _extract_links(soup, URL, "full_page")

    # Arquivos Fomento (opcional)
    arch_links: List[Dict[str, Any]] = []
    arch_meta: Dict[str, Any] = {"url": URL_ARQUIVOS, "fetched": False}
    time.sleep(1.2)
    r_arch = _http_get(URL_ARQUIVOS, timeout=60, retries=2)
    if r_arch:
        arch_meta["fetched"] = True
        arch_meta["status"] = r_arch.status_code
        arch_meta["bytes"] = len(r_arch.text or "")
        arch_all = _extract_links(BeautifulSoup(r_arch.text, "html.parser"), URL_ARQUIVOS, "content_core")
        arch_links = [
            x
            for x in arch_all
            if x["classificacao"] in ("edital_chamada", "radar_oportunidade") or x.get("is_pdf")
        ][:30]
        arch_meta["links_total_content_core"] = len(arch_all)
    else:
        errors.append({"url": URL_ARQUIVOS, "error": "fetch_failed"})

    # RSS probes
    rss_probes = []
    for rss_u in (
        f"{URL.rstrip('/')}/RSS",
        "https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/transformacaodigital/RSS",
    ):
        time.sleep(0.8)
        rr = _http_get(rss_u, timeout=25, retries=2)
        rss_probes.append(
            {
                "url": rss_u,
                "ok": bool(rr and rr.status_code == 200),
                "is_feed_xml": bool(
                    rr and ("<rss" in (rr.text or "").lower()[:800] or "<feed" in (rr.text or "").lower()[:800])
                ),
                "status": rr.status_code if rr else None,
            }
        )

    counts_core = Counter(x["classificacao"] for x in links_page)
    counts_full = Counter(x["classificacao"] for x in links_full)

    oportunidades_core = [
        x
        for x in links_page
        if x["classificacao"] in ("edital_chamada", "radar_oportunidade")
    ]
    noticias_core = [x for x in links_page if x["classificacao"] == "noticia"]
    editais_site = [x for x in links_full if x["classificacao"] == "edital_chamada"][:25]
    radar_site = [
        x
        for x in links_full
        if x["classificacao"] == "radar_oportunidade"
        and "gov.br/mcti" in x["link"].lower()
        and "/noticias/" not in x["link"].lower()
    ][:25]
    core_paras = [
        re.sub(r"\s+", " ", p).strip()[:300]
        for p in (core_text or "").split("\n")
        if len(p.strip()) > 40
    ][:8]

    # Recomendação produto
    recomendacao = {
        "rota_principal": "Radar / Editais",
        "nao_noticias": True,
        "nao_news_research_apply": True,
        "motivo": (
            "Hub gov.br de programas e chamamentos (Transformação Digital); conteúdo é "
            "oportunidades/editais e comunicados de processo, não feed de notícias editoriais."
        ),
        "pipeline_sugerido": "Crawler dedicado editais/radar (review_for_edital) — fora de crawl_news_research_sources notícia",
        "source_id_sugerido": "mcti_fomento_transformacao_digital",
    }

    if not oportunidades_core and arch_links:
        oportunidades_arch = [
            x for x in arch_links if x["classificacao"] in ("edital_chamada", "radar_oportunidade")
        ]
        if oportunidades_arch:
            oportunidades_core = oportunidades_arch[:25]
            recomendacao["nota"] = "Oportunidades concentradas em Arquivos Fomento, não no corpo curto de fomento-1."

    summary: Dict[str, Any] = {
        "fonte": "mcti_fomento_transformacao_digital",
        "url": URL,
        "data_execucao": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "modo": "diagnostico",
        "apply": False,
        "fetch": fetch_meta,
        "diagnostico_pagina": {
            "cms": "gov.br / Plone (Zope) — padrão CAPES/MCTI",
            "titulo_html": title,
            "h1": h1,
            "estrutura": "Página hub institucional (#content-core) com links para programas, arquivos e editais",
            "rss_util": any(p.get("is_feed_xml") for p in rss_probes),
            "rss_notas": "Feeds por pasta podem existir mas conexão instável no ambiente de auditoria",
            "robots": _robots_summary(),
            "listagem_oportunidades_ativas": len(oportunidades_core) > 0,
            "noticias_no_escopo": len(noticias_core),
            "pdfs_content_core": sum(1 for x in links_page if x.get("is_pdf")),
        },
        "datas_prazos_no_texto": dates_prazos,
        "contagens": {
            "links_content_core": len(links_page),
            "links_pagina_completa": len(links_full),
            "por_classificacao_content_core": dict(counts_core),
            "por_classificacao_pagina_completa": dict(counts_full),
        },
        "texto_hub_amostra": core_paras,
        "itens_content_core": links_page,
        "itens_oportunidade_destaque": oportunidades_core[:30],
        "itens_noticia_destaque": noticias_core[:15],
        "itens_edital_site_nav": editais_site,
        "itens_radar_programas_site_nav": radar_site,
        "arquivos_fomento": {"meta": arch_meta, "links_filtrados": arch_links},
        "rss_probes": rss_probes,
        "recomendacao_produto": recomendacao,
        "errors": errors,
    }

    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "itens_classificados.json").write_text(
        json.dumps(
            {
                "content_core": links_page,
                "pagina_completa_amostra": links_full[:80],
                "arquivos_fomento": arch_links,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    md = [
        "# MCTI — Transformação Digital / Fomento (diagnóstico)",
        "",
        f"- **URL:** {URL}",
        f"- **Execução:** {summary['data_execucao']}",
        f"- **Apply:** não",
        "",
        "## Conclusão de roteamento",
        "",
        f"- **Rota recomendada:** **{recomendacao['rota_principal']}**",
        f"- **Notícias (news/research):** não — {recomendacao['motivo']}",
        f"- **`source_id` sugerido:** `{recomendacao['source_id_sugerido']}`",
        "",
        "## Estrutura gov.br",
        "",
        f"- **CMS:** {summary['diagnostico_pagina']['cms']}",
        f"- **Título:** {title}",
        f"- **H1:** {', '.join(h1) or '—'}",
        f"- **RSS útil:** {'sim' if summary['diagnostico_pagina']['rss_util'] else 'não confirmado'}",
        f"- **robots MCTI:** {summary['diagnostico_pagina']['robots'].get('https://www.gov.br/mcti/robots.txt', '—')}",
        "",
        "## Contagens (content-core)",
        "",
    ]
    for k, v in sorted(counts_core.items()):
        md.append(f"- **{k}:** {v}")
    md.extend(
        [
            "",
            f"- **Links na página inteira (nav):** {len(links_full)}",
            f"- **Editais/chamadas (nav, amostra):** {len(editais_site)}",
            f"- **Programas fomento (nav, amostra):** {len(radar_site)}",
            f"- **Oportunidades no content-core:** {len(oportunidades_core)}",
            f"- **Notícias no content-core:** {len(noticias_core)}",
            f"- **PDFs no content-core:** {summary['diagnostico_pagina']['pdfs_content_core']}",
            "",
            "## Conteúdo do hub (content-core)",
            "",
            "Página **institucional explicativa** sobre instrumentos de fomento (emendas, chamadas FINEP/CNPq/EMBRAPII, Lei das TICs). "
            "**Não** é feed de editais abertos com prazo na própria URL.",
            "",
        ]
    )
    for p in core_paras[:5]:
        md.append(f"- {p}")
    md.extend(
        [
            "",
            "## Datas e prazos no texto",
            "",
            f"- **Datas (DD/MM/AAAA):** {', '.join(dates_prazos['datas_dd_mm_yyyy']) or '—'}",
            "",
        ]
    )
    if dates_prazos["prazos_texto"]:
        md.append("### Indícios de prazo")
        for p in dates_prazos["prazos_texto"][:8]:
            md.append(f"- {p}")
        md.append("")

    md.extend(["## Oportunidades / editais (content-core + arquivos)", ""])
    for i, row in enumerate(oportunidades_core[:20], 1):
        md.append(f"### {i}. [{row['classificacao']}] {row['titulo'][:90]}")
        md.append("")
        md.append(f"- **Motivo:** {row['motivo']}")
        md.append(f"- **Link:** {row['link']}")
        md.append("")

    if editais_site:
        md.extend(["## Editais/chamadas (navegação gov.br MCTI)", ""])
        for row in editais_site[:12]:
            md.append(f"- `[{row['classificacao']}]` {row['titulo'][:75]} — {row['link'][:95]}")
        md.append("")

    if arch_meta.get("fetched") and arch_links:
        md.extend(["## Arquivos Fomento (links filtrados)", "", f"- **URL:** {URL_ARQUIVOS}", ""])
        for row in arch_links[:12]:
            md.append(f"- `[{row['classificacao']}]` {row['titulo'][:70]} — {row['link'][:90]}")
        md.append("")

    md.extend(
        [
            "## Próximo passo (fora deste diagnóstico)",
            "",
            "1. Crawler **editais/radar** com seeds explícitos (programas + `/acesso-a-informacao/editais/`).",
            "2. `review_for_edital` para chamamentos; não usar `load_news_research_sources` notícia.",
            "3. Não misturar com Concursos militares/aero já cobertos em `concursos/`.",
            "",
        ]
    )
    (OUT / "summary.md").write_text("\n".join(md), encoding="utf-8")

    print(
        json.dumps(
            {
                "rota": recomendacao["rota_principal"],
                "oportunidades_core": len(oportunidades_core),
                "contagens_core": dict(counts_core),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    print(str(OUT / "summary.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
