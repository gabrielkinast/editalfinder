"""
Desenvolve SP — coleta HTTP frequentemente bloqueada (403 WAF). Sem bypass:
exportamos seeds oficiais curados (URLs de crédito/solicitação) para pipeline e revisão humana.
"""
from pathlib import Path
import sys
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import save_outputs
from CORE.credito_brasil_onda_a_noise import crawler_should_drop_item

SOURCE_KEY = "desenvolve_sp"
LABEL = "DESENVOLVE_SP"

# URLs públicas citadas em materiais institucionais e no próprio domínio (entrada para empresas).
CURATED_SEEDS = [
    {
        "titulo": "Opções de crédito — empresas",
        "descricao": "Hub de linhas de crédito para empresas no site oficial da Desenvolve SP. "
        "Coleta automatizada retorna HTTP 403 neste ambiente; usar navegador para texto completo.",
        "link": "https://www.desenvolvesp.com.br/empresas/opcoes-de-credito/",
    },
    {
        "titulo": "Guia do financiamento — como solicitar",
        "descricao": "Passo a passo público para solicitação de financiamento no programa estadual.",
        "link": "https://www.desenvolvesp.com.br/empresas/guia-do-financiamento/como-solicitar/",
    },
    {
        "titulo": "Máquinas e equipamentos",
        "descricao": "Linhas para aquisição de máquinas e equipamentos (página de produto — ver condições no site).",
        "link": "https://www.desenvolvesp.com.br/empresas/opcoes-de-credito/maquinas-e-equipamentos/",
    },
    {
        "titulo": "Negócios online — canal de solicitação",
        "descricao": "Canal digital de solicitação/análise (portal oficial Desenvolve SP).",
        "link": "https://www.desenvolvesp.com.br/negocios/online",
    },
]


def _build_items():
    out = []
    now = datetime.now().date().isoformat()
    for row in CURATED_SEEDS:
        if crawler_should_drop_item(row["titulo"], row["link"], row.get("descricao") or ""):
            continue
        out.append(
            {
                "titulo": row["titulo"],
                "descricao": row["descricao"][:3500],
                "link": row["link"],
                "fonte": LABEL,
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "valor": None,
                "programa": "desenvolve_sp_credito",
                "acao": "credito",
                "tipo_recurso": "financiamento_reembolsavel",
                "extras": {
                    "pais": "Brasil",
                    "regiao": "sudeste",
                    "estado": "SP",
                    "tipo_oportunidade": "programa_credito",
                    "tipo_recurso": "credito",
                    "origem_portal": "Desenvolve SP (desenvolvesp.com.br)",
                    "natureza_recurso": "reembolsavel",
                    "reembolsavel": True,
                    "setor_estrategico": "desenvolvimento_regional",
                    "subtema": ["credito", "financiamento", "empresas"],
                    "area_cientifica": [],
                    "area_tecnologica": ["inovacao"],
                    "metodo_extracao": "curated_official_seed_http_blocked_waf",
                    "http_coleta_bloqueada": True,
                    "observacoes": "Site retornou 403 para requests automatizados; seeds são links oficiais para revisão manual ou fetch futuro com política explícita.",
                    "url_listagem": "https://www.desenvolvesp.com.br/empresas/opcoes-de-credito/",
                    "url_detalhe": row["link"],
                    "documentos": [],
                    "pdf_url": "",
                    "coletado_em": now,
                    "nivel_sensibilidade": "publico_institucional",
                },
            }
        )
    return out


def main():
    items = _build_items()
    save_outputs(Path(__file__).parent, SOURCE_KEY, items)
    print(f"[{LABEL}] Seeds curados salvos: {len(items)} (sem scraping HTML por bloqueio WAF).")


if __name__ == "__main__":
    main()
