#!/usr/bin/env python3
"""
Dry-run local: compara `setor_estrategico` antes/depois de `enrich_opportunity_classification`
com a taxonomia corrente (sem Supabase, sem apply).

Uso:
  python scripts/dry_run_taxonomy_setor_recovery.py
  python scripts/dry_run_taxonomy_setor_recovery.py --json caminho/itens.json

O JSON deve ser uma lista de objetos com pelo menos: titulo, descricao, fonte (opcional), extras (opcional).
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from taxonomy_filtros import enrich_opportunity_classification  # noqa: E402

NOISY_SECTORS: Set[str] = {"aeroespacial", "defesa_industrial", "defesa", "dual_use"}


def _as_list(v: Any) -> List[str]:
    if isinstance(v, list):
        return [str(x).strip() for x in v if x is not None and str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def _count_noisy(se: Sequence[str]) -> int:
    return sum(1 for s in se if s in NOISY_SECTORS)


def _default_corpus() -> List[Dict[str, Any]]:
    return [
        {
            "fonte": "FAPESC",
            "titulo": "Transformacao digital na educacao basica",
            "descricao": (
                "Apoio a projetos de inovacao pedagogica e plataformas digitais. "
                "Chamada publica. Prazo 2030."
            ),
            "extras": {"setor_estrategico": ["aeroespacial", "defesa", "ciencia_tecnologia"]},
        },
        {
            "fonte": "CNPq",
            "titulo": "Universalidade e inclusao no ensino superior",
            "descricao": "Bolsas e auxilios. Ciencia e tecnologia. P&D em metodologias ativas.",
            "extras": {"setor_estrategico": ["aeroespacial"]},
        },
        {
            "fonte": "EXEMPLO",
            "titulo": "Cooperacao com o INPE em sensoriamento remoto",
            "descricao": "Projeto com satelite e orbital para monitoramento ambiental.",
            "extras": {},
        },
    ]


def _normalize_item(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "titulo": str(row.get("titulo") or ""),
        "descricao": str(row.get("descricao") or ""),
        "programa": str(row.get("programa") or ""),
        "acao": str(row.get("acao") or ""),
        "link": str(row.get("link") or ""),
        "fonte": str(row.get("fonte") or row.get("fonte_recurso") or "desconhecida"),
        "extras": deepcopy(row.get("extras") if isinstance(row.get("extras"), dict) else {}),
    }


def run_corpus(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    per_fonte_before = Counter()
    per_fonte_after = Counter()
    noisy_before = 0
    noisy_after = 0
    examples: List[Dict[str, Any]] = []

    for raw in rows:
        item = _normalize_item(raw)
        antes = _as_list((item["extras"] or {}).get("setor_estrategico"))
        f = item["fonte"]
        for s in antes:
            per_fonte_before[(f, s)] += 1
        noisy_before += _count_noisy(antes)

        enrich_opportunity_classification(item)
        depois = _as_list(item["extras"].get("setor_estrategico"))
        for s in depois:
            per_fonte_after[(f, s)] += 1
        noisy_after += _count_noisy(depois)

        if sorted(antes) != sorted(depois):
            examples.append(
                {
                    "fonte": f,
                    "titulo": item["titulo"][:120],
                    "antes": antes,
                    "depois": depois,
                    "historico": item["extras"].get("setor_estrategico_historico_merge"),
                }
            )

    summary = {
        "linhas": len(rows),
        "noisy_slugs_total_antes": noisy_before,
        "noisy_slugs_total_depois": noisy_after,
        "reducao_noisy_slugs": noisy_before - noisy_after,
        "por_fonte_top_antes": per_fonte_before.most_common(25),
        "por_fonte_top_depois": per_fonte_after.most_common(25),
        "exemplos_alterados": examples[:50],
    }
    return examples, summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--json",
        type=Path,
        help="Lista JSON de itens (titulo, descricao, fonte, extras opcional)",
    )
    ap.add_argument(
        "--out",
        type=Path,
        help="Escrever relatório JSON (opcional)",
    )
    args = ap.parse_args()

    if args.json:
        data = json.loads(args.json.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            print("O JSON raiz deve ser uma lista.", file=sys.stderr)
            return 2
        rows = data
    else:
        rows = _default_corpus()

    _, summary = run_corpus(rows)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Escrito: {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
