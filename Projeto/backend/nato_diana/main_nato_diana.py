from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs, scrape_html_portal


def _curated_official_public_briefs() -> List[Dict[str, object]]:
    """
    Quando diana.nato.int bloqueia scraping (ex.: Cloudflare), mantemos oportunidades
    reais com texto alinhado a comunicações públicas da FAQ DIANA (sem inventar PDFs
    nem contornar login). Atualizar este bloco quando novos desafios forem anunciados.
    """
    brief_common = (
        "NATO’s Defence Innovation Accelerator for the North Atlantic (DIANA) runs competitive "
        "challenges for start-ups and SMEs from Allied nations. Submissions are made through the "
        "official DIANA Challenge Portal when a call is open. Source synthesis from publicly "
        "published DIANA FAQ material (May 2026 context)."
    )
    return [
        {
            "titulo": "Decision Superiority for NATO Warfighters — DIANA challenge call",
            "descricao": (
                "DIANA challenge seeking mature technology solutions (TRL 7+) from start-ups and "
                "small and medium-sized enterprises in NATO member nations, with principal place of "
                "business and control requirements as set out in the public Terms and Conditions of "
                "Bidding. The programme uses contractual funding (publicly cited up to approximately "
                "EUR/USD 100k scale for this track) and concludes with demonstrations to NATO Allied "
                "Command Operations and other stakeholders; there is no separate ‘Phase 2’ for this "
                "challenge in the published model. Innovators selected may be eligible for follow-on "
                "contracts through DIANA’s Rapid Adoption Service, subject to NATO and national rules. "
                "Applications are submitted through the DIANA Challenge Portal (Challenges menu). "
                "Published submission window reference: 5 May 2026, 09:00 BST (verify on portal for "
                "any amendment). "
                + brief_common
            ),
            "link": "https://www.diana.nato.int/challenges.html",
            "fonte": "NATO DIANA",
            "data_publicacao": None,
            "fim_inscricao": "2026-05-05",
            "situacao": "Aberto",
            "valor": None,
            "programa": "NATO DIANA challenges",
            "acao": "challenge_call",
            "tipo_recurso": "fomento_pdi",
            "extras": {
                "pais": "NATO (Aliança)",
                "regiao": "Internacional",
                "idioma_original": "en",
                "tipo_oportunidade": "challenge",
                "orgao_contratante": "NATO DIANA",
                "instituicao": "NATO",
                "nivel_sensibilidade": "publico_institucional",
                "url_listagem": "https://www.diana.nato.int/faq.html",
                "url_detalhe": "https://www.diana.nato.int/challenges.html",
                "metodo_extracao": "curated_official_public_brief",
                "documentos": [],
                "pdf_url": "",
                "subtema": ["dual_use", "defence_innovation"],
                "codigo_oportunidade": "DIANA-WARFIGHTERS-2026",
                "numero_chamada": "DIANA-WARFIGHTERS-2026",
            },
        },
        {
            "titulo": "NATO DIANA — Programme FAQ (challenges, eligibility, portal)",
            "descricao": (
                "Official programme information covering how DIANA challenges work, eligibility for "
                "start-ups and SMEs with limited prior defence and security experience, use of the "
                "Challenge Portal for proposals, and timelines for further challenge waves announced "
                "by DIANA. This entry summarises the public FAQ narrative; it is not a substitute for "
                "the portal terms. Use for orientation alongside specific challenge pages. "
                + brief_common
            ),
            "link": "https://www.diana.nato.int/faq.html",
            "fonte": "NATO DIANA",
            "data_publicacao": None,
            "fim_inscricao": None,
            "situacao": "Em andamento",
            "valor": None,
            "programa": "NATO DIANA",
            "acao": "programme_information",
            "tipo_recurso": "fomento_pdi",
            "extras": {
                "pais": "NATO (Aliança)",
                "regiao": "Internacional",
                "idioma_original": "en",
                "tipo_oportunidade": "programa",
                "orgao_contratante": "NATO DIANA",
                "instituicao": "NATO",
                "nivel_sensibilidade": "publico_institucional",
                "url_listagem": "https://www.diana.nato.int/faq.html",
                "url_detalhe": "https://www.diana.nato.int/faq.html",
                "metodo_extracao": "curated_official_public_brief",
                "documentos": [],
                "pdf_url": "",
                "subtema": ["defence_innovation", "accelerator"],
            },
        },
    ]


def _filter_scraped(items: List[Dict[str, object]]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for it in items:
        link = str(it.get("link") or "")
        low = link.lower()
        if "diana.nato.int" not in low:
            continue
        # Evitar gravar só a página-índice de desafios como “detalhe” (curated pode usar o mesmo URL).
        path = urlparse(link).path.lower()
        if path.endswith("/challenges.html") or path == "/challenges.html":
            continue
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        if ex.get("metodo_extracao") == "fallback_public_index":
            continue
        body = str(it.get("descricao") or "")
        if len(body.strip()) < 120:
            continue
        out.append(it)
    return out


def main() -> None:
    print("[NATO_DIANA] Iniciando coleta...")
    items = scrape_html_portal(
        source_label="NATO DIANA",
        country="NATO (Aliança)",
        listing_urls=[
            "https://www.diana.nato.int/challenges.html",
            "https://www.diana.nato.int/faq.html",
        ],
        allowed_domains=["diana.nato.int"],
        extra_keywords=[
            "diana",
            "challenge",
            "innovator",
            "accelerator",
            "nato",
            "dual-use",
            "dual use",
            "call",
            "portal",
            "submission",
            "trl",
            "sme",
            "startup",
        ],
        max_items=24,
        max_listing_pages=3,
    )
    items = _filter_scraped(items)
    if not items:
        items = _curated_official_public_briefs()
        print(
            "[NATO_DIANA] Listagem em tempo real indisponível ou filtrada; "
            "a usar briefs curados públicos (sem fallback_public_index)."
        )
    save_outputs(Path(__file__).parent, "nato_diana", items)
    print(f"[NATO_DIANA] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
