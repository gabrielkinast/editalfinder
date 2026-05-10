from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_intel import build_defense_extras, detect_keywords
from defense_source_common import save_outputs

HEADERS = {"User-Agent": "EditalFinderBot/1.0", "Accept": "application/json"}


def _to_date(value: Any) -> str | None:
    if isinstance(value, str) and len(value) >= 10 and value[4] == "-" and value[7] == "-":
        return value[:10]
    return None


def collect() -> List[Dict[str, object]]:
    endpoints = [
        "https://dadosabertos.compras.gov.br/modulo-licitacoes/1_consultarLicitacao",
        "https://dadosabertos.compras.gov.br/modulo-licitacoes/1_consultarLicitacaoDia",
    ]
    items: List[Dict[str, object]] = []
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, headers=HEADERS, timeout=30)
            if response.status_code >= 400:
                continue
            data = response.json()
            rows = data if isinstance(data, list) else data.get("data", [])
            for row in rows[:250]:
                title = str(row.get("objeto") or row.get("descricao") or "Licitacao Compras.gov")
                orgao = str(row.get("orgao") or row.get("uasg") or "")
                merged = f"{title} {orgao}"
                if not detect_keywords(merged):
                    continue
                num = str(row.get("numeroLicitacao") or row.get("numero") or "")
                link = "https://www.gov.br/compras/pt-br"
                extras = build_defense_extras(
                    text=merged,
                    source_name="Compras.gov Defesa",
                    origem=link,
                    pais="BR",
                    orgao_contratante=orgao,
                )
                extras["numero_licitacao"] = num
                extras["uasg"] = row.get("uasg")
                extras["regiao"] = "brasil"
                extras["estado"] = row.get("uf") or ""
                extras["municipio"] = row.get("municipio") or ""
                extras["orgao_responsavel"] = orgao
                extras["instituicao"] = orgao
                extras["numero_processo"] = str(row.get("numeroProcesso") or row.get("processo") or "")
                extras["codigo_oportunidade"] = num
                extras["modalidade"] = str(row.get("modalidade") or "")
                extras["tipo_oportunidade"] = "licitacao"
                extras["tipo_recurso"] = "contrato_publico"
                extras["natureza_recurso"] = "contratacao_publica"
                extras["reembolsavel"] = None
                extras["publico_alvo"] = "fornecedores defesa"
                extras["valor_total"] = str(row.get("valorEstimado") or "")
                extras["documentos"] = []
                extras["documentos_exigidos"] = []
                extras["url_listagem"] = endpoint
                extras["url_detalhe"] = link if not num else f"{link}#licitacao-{num}"
                extras["metodo_extracao"] = "api_comprasgov_defesa"
                items.append(
                    {
                        "titulo": title[:250],
                        "descricao": merged[:3500],
                        "link": link if not num else f"{link}#licitacao-{num}",
                        "fonte": "Compras.gov Defesa",
                        "data_publicacao": _to_date(row.get("dataPublicacao")) or datetime.now().date().isoformat(),
                        "fim_inscricao": _to_date(row.get("dataAbertura")),
                        "situacao": str(row.get("situacao") or "Em andamento"),
                        "valor": row.get("valorEstimado"),
                        "programa": "contratacoes_publicas_defesa",
                        "acao": "licitacao",
                        "tipo_recurso": "contrato_publico",
                        "extras": extras,
                    }
                )
        except Exception:
            continue
    return items


def _fallback_items() -> List[Dict[str, object]]:
    link = "https://www.gov.br/compras/pt-br"
    extras = build_defense_extras(
        text="compras gov defesa licitacao contratacao publica",
        source_name="Compras.gov Defesa",
        origem=link,
        pais="Brasil",
        orgao_contratante="Governo Federal",
    )
    extras.update(
        {
            "regiao": "brasil",
            "tipo_oportunidade": "licitacao",
            "tipo_recurso": "contrato_publico",
            "natureza_recurso": "contratacao_publica",
            "url_listagem": link,
            "url_detalhe": link,
            "metodo_extracao": "fallback_public_index",
            "observacoes": "Dataset de dados abertos indisponível ou sem itens no momento.",
        }
    )
    return [
        {
            "titulo": "Compras.gov Defesa - Índice de Licitações",
            "descricao": "Página pública de referência para licitações e compras governamentais com possível escopo de defesa.",
            "link": link,
            "fonte": "Compras.gov Defesa",
            "data_publicacao": None,
            "fim_inscricao": None,
            "situacao": "Em andamento",
            "valor": None,
            "programa": "contratacoes_publicas_defesa",
            "acao": "licitacao",
            "tipo_recurso": "contrato_publico",
            "extras": extras,
        }
    ]


def main() -> None:
    items = collect()
    if not items:
        items = _fallback_items()
        print("[COMPRAS_DEFESA] Fallback ativado por indisponibilidade de endpoint.")
    save_outputs(Path(__file__).parent, "compras_defesa", items)
    print(f"[COMPRAS_DEFESA] Registros salvos: {len(items)}")


if __name__ == "__main__":
    main()
