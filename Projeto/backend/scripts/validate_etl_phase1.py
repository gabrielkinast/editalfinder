#!/usr/bin/env python3
"""
Validação local da fase 1 (sem Supabase obrigatório):
- normalização + extras órfãos;
- merge de extras;
- classificação keyword em texto sintético.
Execute na raiz do repositório: python scripts/validate_etl_phase1.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "CORE"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(CORE))

from merge_utils import merge_descricao, merge_extras_dict  # noqa: E402
from schema import normalizar  # noqa: E402
from taxonomy_filtros import enrich_opportunity_classification, extras_to_filter_columns  # noqa: E402


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    print("=== validate_etl_phase1 ===")

    raw = {
        "titulo": "Chamada pública de fomento à inovação",
        "descricao": "Subvenção para empresas e ICTs. Energia renovável e agro. Prazo 2030.",
        "link": "https://exemplo.gov/chamada-1",
        "fonte": "TESTE",
        "tipo_recurso": "fomento",
        "campo_fora_do_modelo": "preservar",
        "extras": {"pais": "Brasil", "orgao_responsavel": "Finep"},
    }
    n = normalizar(raw)
    _assert("campo_fora_do_modelo" in n["extras"], "órfão deve ir para extras")
    _assert(n["extras"].get("pais") == "Brasil", "extras original preservado")

    item = dict(n)
    enrich_opportunity_classification(item)
    ex = item["extras"]
    _assert(len(ex.get("area", [])) >= 1, "deve classificar ao menos uma área")
    _assert(ex.get("tipo_oportunidade"), "deve sugerir tipo_oportunidade")
    _assert(ex.get("classificacao_confianca") in ("baixa", "media", "alta"), "confiança válida")
    _assert(ex.get("metodo_classificacao"), "metodo_classificacao")

    cols = extras_to_filter_columns(item, ex)
    _assert("tipo_oportunidade" in cols or "area" in cols, "colunas espelho derivadas")

    old_ex = {"pdf_url": "https://old/pdf", "area": ["Saúde"]}
    new_ex = {"area": ["Energia"], "tipo_oportunidade": "edital"}
    merged = merge_extras_dict(old_ex, new_ex)
    _assert("Energia" in merged["area"] and "Saúde" in merged["area"], "merge de listas")

    long_old = "x" * 2000
    short_new = "curto"
    _assert(
        merge_descricao(long_old, short_new) == long_old,
        "descrição rica não deve ser substituída por curta",
    )

    print("OK — exemplos JSON (trecho) após normalizar + classificar:")
    print(json.dumps({k: item[k] for k in ("titulo", "tipo_recurso", "link")}, ensure_ascii=False, indent=2))
    print("extras.area:", ex.get("area"))
    print("extras.tipo_oportunidade:", ex.get("tipo_oportunidade"))
    print("extras.classificacao_confianca:", ex.get("classificacao_confianca"))
    print("payload DB (filtros espelho, schema estendido):", json.dumps(cols, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
