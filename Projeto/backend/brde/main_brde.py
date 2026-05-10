from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import scrape_source, save_outputs

POSITIVE_HINTS = [
    "linha",
    "financiamento",
    "credito",
    "inovacao",
    "chamada",
    "edital",
    "programa",
    "pronampe",
]
STRONG_POSITIVE_HINTS = [
    "linha de financiamento",
    "linhas de financiamento",
    "linha de credito",
    "credito simples",
    "pronampe",
    "brde labs",
]
NOISE_HINTS = [
    "ouvidoria",
    "faq",
    "codigo de conduta",
    "politica de privacidade",
    "transparencia",
    "acessibilidade",
    "fale conosco",
    "internet banking",
    "termos de uso",
    "home",
    "pagina inicial",
    "documentos pessoa fisica",
    "documentos pessoa juridica",
    "documentos cooperativas",
    "area-do-cliente",
    "tarifas",
    "equipe de atendimento",
    "tutorial do sistema",
]


def _is_relevant_item(item: dict) -> bool:
    text = f"{item.get('titulo','')} {item.get('descricao','')}".lower()
    link = str(item.get("link") or "").lower()
    title = str(item.get("titulo") or "").strip().lower()
    if not title or len(title) < 8:
        return False
    path_ok = any(p in link for p in ["/linhas-de-financiamento/", "/inovacao/", "/programas/"])
    if not path_ok:
        return False
    if "noticias" in link:
        return False
    has_positive = any(k in text or k in link for k in POSITIVE_HINTS)
    has_noise = any(k in text or k in link for k in NOISE_HINTS)
    has_strong_positive = any(k in text or k in link for k in STRONG_POSITIVE_HINTS)
    return has_positive and (not has_noise or has_strong_positive)


def main():
    config = {
        "source_label": "BRDE",
        "listing_urls": [
            "https://www.brde.com.br/",
            "https://www.brde.com.br/linhas-de-financiamento/",
            "https://www.brde.com.br/inovacao/",
        ],
        "keywords": [
            "credito",
            "financiamento",
            "linha de credito",
            "taxa",
            "carencia",
            "prazo",
            "inovacao",
            "fomento",
            "edital",
            "chamada",
        ],
        "avoid_keywords": ["concurso", "estagio", "ouvidoria", "licitacao"],
        "program_hint": "Linhas BRDE",
        "allowed_domains": ["brde.com.br"],
        "max_items": 30,
        "max_links_per_page": 180,
        "setor_estrategico": "desenvolvimento_regional",
        "orgao_responsavel": "BRDE",
        "instituicao": "Banco Regional de Desenvolvimento do Extremo Sul",
        "orgao_contratante": "BRDE",
        "tipo_oportunidade": "linha_credito",
        "area_cientifica": [],
        "area_tecnologica": ["inovacao", "transformacao_digital"],
        "subtema_padrao": ["credito", "financiamento", "desenvolvimento_regional"],
    }
    try:
        items = scrape_source(config)
    except Exception as exc:
        print(f"[BRDE] Falha na coleta: {exc}")
        items = []
    seen = set()
    filtered = []
    for x in items:
        if not _is_relevant_item(x):
            continue
        key = f"{x.get('link','')}|{x.get('titulo','')}".strip().lower()
        if key in seen:
            continue
        seen.add(key)
        filtered.append(x)
    items = filtered[:20]
    for item in items:
        extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
        extras["natureza_recurso"] = "reembolsavel"
        extras["reembolsavel"] = True
        extras["tipo_recurso"] = "financiamento_reembolsavel"
        extras["publico_alvo"] = extras.get("publico_alvo") or "empresas e produtores"
        item["extras"] = extras
        item["tipo_recurso"] = "financiamento_reembolsavel"
    if not items:
        items = [
            {
                "titulo": "BRDE - Linhas de Financiamento",
                "descricao": "Índice público de linhas de crédito e financiamento do BRDE.",
                "link": "https://www.brde.com.br/linhas-de-financiamento/",
                "fonte": "BRDE",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "linhas_brde",
                "acao": "credito",
                "tipo_recurso": "financiamento_reembolsavel",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "brasil",
                    "tipo_oportunidade": "linha_credito",
                    "tipo_recurso": "financiamento_reembolsavel",
                    "natureza_recurso": "reembolsavel",
                    "reembolsavel": True,
                    "url_listagem": "https://www.brde.com.br/linhas-de-financiamento/",
                    "url_detalhe": "https://www.brde.com.br/linhas-de-financiamento/",
                    "metodo_extracao": "fallback_public_index",
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        ]
        print("[BRDE] Fallback ativado por ausência de itens.")
    save_outputs(Path(__file__).parent, "brde", items)
    print(f"[BRDE] Registros salvos: {len(items)}")

if __name__ == "__main__":
    main()
