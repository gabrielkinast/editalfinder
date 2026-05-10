from __future__ import annotations

from pathlib import Path

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_source_common import save_outputs, scrape_html_portal


def _is_relevant_item(item):
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    title_link = f"{title} {link}"
    if any(k in title_link for k in ("about us", "contact", "news", "success stories", "privacy policy")):
        return False
    if "login" in link or "dashboard" in link:
        return False
    return any(
        k in text
        for k in (
            "open topic",
            "specific topic",
            "stratfi",
            "tacfi",
            "sbir",
            "sttr",
            "phase i",
            "phase ii",
            "solicitation",
            "funding",
            "award",
            "proposal",
        )
    )


def _fallback_items():
    return [
        {
            "titulo": "AFWERX Open Topics and Challenges",
            "descricao": "Hub de oportunidades de inovação da USAF/Space Force com foco em Open Topic, SBIR/STTR e transição para aquisição.",
            "link": "https://afwerx.com/divisions/afventures/",
            "fonte": "AFWERX",
            "data_publicacao": None,
            "fim_inscricao": None,
            "situacao": "Em andamento",
            "valor": None,
            "programa": "inovacao_defesa",
            "acao": "fomento_investimento",
            "tipo_recurso": "fomento_investimento",
            "extras": {
                "setor_estrategico": "defesa_industrial",
                "subtema": ["sbir", "sttr", "open_topic", "dual_use"],
                "tipo_oportunidade": "chamada_publica",
                "orgao_contratante": "USAF / AFWERX",
                "pais": "US",
                "nivel_sensibilidade": "publico_institucional",
                "origem": "https://afwerx.com/divisions/afventures/",
                "metodo_extracao": "fallback_public_index",
                "natureza_recurso": "nao_reembolsavel",
                "reembolsavel": False,
            },
        }
    ]


def main() -> None:
    print("[AFWERX] Iniciando coleta...")
    items = scrape_html_portal(
        source_label="AFWERX",
        country="US",
        listing_urls=[
            "https://afwerx.com/divisions/afventures/",
            "https://afwerx.com/",
            "https://afwerx.com/opportunities/",
        ],
        allowed_domains=["afwerx.com"],
        extra_keywords=["open topic", "sbir", "sttr", "funding", "challenge", "phase i", "phase ii"],
        max_items=40,
        max_listing_pages=4,
    )
    for it in items:
        it["programa"] = "inovacao_defesa"
        it["acao"] = "fomento_investimento"
        extras = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        extras["tipo_recurso"] = "fomento_investimento"
        extras["natureza_recurso"] = "nao_reembolsavel"
        extras["reembolsavel"] = False
        it["extras"] = extras
        it["tipo_recurso"] = "fomento_investimento"
    items = [x for x in items if _is_relevant_item(x)]
    if not items:
        items = _fallback_items()
        print("[AFWERX] Fallback ativado por indisponibilidade/bloqueio.")
    save_outputs(Path(__file__).parent, "afwerx", items)
    print(f"[AFWERX] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
