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
    if any(k in title_link for k in ("resource guide", "help learning", "contact", "about us", "how to work")):
        return False
    if "onramp" in link or "guide" in link:
        return False
    if "/work-with-us/" not in link and "/latest/" not in link:
        return False
    return any(k in text for k in ("solicitation", "open", "cso", "challenge", "award", "proposal"))


def _fallback_items():
    return [
        {
            "titulo": "DIU Opportunities and CSOs",
            "descricao": "Portal oficial da Defense Innovation Unit para desafios, CSOs e oportunidades de transição tecnológica.",
            "link": "https://www.diu.mil/work-with-us",
            "fonte": "DIU",
            "data_publicacao": None,
            "fim_inscricao": None,
            "situacao": "Em andamento",
            "valor": None,
            "programa": "inovacao_defesa",
            "acao": "fomento_investimento",
            "tipo_recurso": "fomento_investimento",
            "extras": {
                "setor_estrategico": "defesa_industrial",
                "subtema": ["dual_use", "cso", "transition_funding"],
                "tipo_oportunidade": "chamada_publica",
                "orgao_contratante": "Defense Innovation Unit",
                "pais": "US",
                "nivel_sensibilidade": "publico_institucional",
                "origem": "https://www.diu.mil/work-with-us",
                "metodo_extracao": "fallback_public_index",
                "natureza_recurso": "nao_reembolsavel",
                "reembolsavel": False,
            },
        }
    ]


def main() -> None:
    print("[DIU] Iniciando coleta...")
    items = scrape_html_portal(
        source_label="DIU",
        country="US",
        listing_urls=[
            "https://www.diu.mil/work-with-us",
            "https://www.diu.mil/latest",
            "https://www.diu.mil/solutions",
        ],
        allowed_domains=["diu.mil"],
        extra_keywords=["commercial solutions opening", "cso", "funding", "award", "solicitation", "dual-use"],
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
        print("[DIU] Fallback ativado por indisponibilidade/bloqueio.")
    save_outputs(Path(__file__).parent, "diu", items)
    print(f"[DIU] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
