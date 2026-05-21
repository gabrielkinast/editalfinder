#!/usr/bin/env python3
"""
Validação amostral pós-dry-run: classifica alterações em A/B/C/D, recomenda fontes
e estratégia de apply em staging (sem DB, sem apply).

Lê o dry-run JSON só como referência opcional; reprocessa o standardized para contagens.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from keyword_taxonomy import _normalize  # noqa: E402
from taxonomy_filtros import enrich_opportunity_classification  # noqa: E402

DEFAULT_INPUT = ROOT / "audit_reports_retransform" / "standardized"
DRYRUN_JSON = ROOT / "audit_reports_main_pipeline" / "recovery_classificacao_global_dryrun.json"
OUT_JSON = ROOT / "audit_reports_main_pipeline" / "recovery_classificacao_global_review.json"
OUT_MD = ROOT / "audit_reports_main_pipeline" / "recovery_classificacao_global_review.md"

DEFENSE_LIKE = frozenset({"defesa_industrial", "defesa", "aeroespacial", "cyber_defesa", "dual_use"})
NOISY = frozenset({"defesa_industrial", "aeroespacial", "cyber_defesa"})

LOCK_SOURCE_FILES = frozenset(
    {
        "iarpa_standardized.json",
        "darpa_opportunities_standardized.json",
        "darpa_news_standardized.json",
    }
)

EN_CALIBRATION_MIN_ROWS = 12
EN_CALIBRATION_MIN_PCT_HAD_TO_EMPTY = 0.38

VERIFIED_OK_FILES = frozenset(
    {
        "dod_sbir_sttr_standardized.json",
        "nuclep_standardized.json",
    }
)

MILITARY_MARKERS = (
    " sbir ",
    " sttr ",
    " darpa ",
    " iarpa ",
    " warfighter ",
    " defense ",
    " defence ",
    " military ",
    " department of defense ",
    " dod ",
    " usaf ",
    " air force ",
    " navy ",
    " space force ",
    " classified ",
    " missile ",
    " weapon ",
    " warfare ",
    " dept of the army ",
    " materiel command ",
    "army --",
    " grants.gov ",
)


def _as_list(v: Any) -> List[str]:
    if isinstance(v, list):
        return [str(x).strip() for x in v if x is not None and str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def _sig(s: Sequence[str]) -> Set[str]:
    return set(s)


def _military_evidence(corpus: str) -> bool:
    n = f" {_normalize(corpus)} "
    return any(m in n for m in MILITARY_MARKERS)


def _military_family(fonte: str, source_file: str) -> Optional[str]:
    fl = (fonte or "").lower()
    fn = (source_file or "").lower()
    if "dod_sbir" in fn or ("sbir" in fl and "dod" in fl):
        return "dod_sbir_sttr"
    if "darpa" in fn or "darpa" in fl:
        return "darpa"
    if "iarpa" in fn or "iarpa" in fl:
        return "iarpa"
    if "amazul" in fn or "amazul" in fl:
        return "amazul"
    if "nuclep" in fn or "nuclep" in fl:
        return "nuclep"
    if "esa_osip" in fn:
        return "esa_osip"
    return None


def _has_defense_like(se: Sequence[str]) -> bool:
    return bool(_sig(se) & DEFENSE_LIKE)


def _corpus(row: Dict[str, Any]) -> str:
    ex = row.get("extras") if isinstance(row.get("extras"), dict) else {}
    parts = [
        str(row.get("titulo") or ""),
        str(row.get("descricao") or ""),
        str(row.get("programa") or ""),
        str(row.get("acao") or ""),
        str(row.get("link") or ""),
        str(ex.get("objetivo") or ""),
        str(ex.get("elegibilidade") or ""),
        str(row.get("tipo_recurso") or ""),
    ]
    return " ".join(parts)


def _to_item(row: Dict[str, Any]) -> Dict[str, Any]:
    ex = row.get("extras") if isinstance(row.get("extras"), dict) else {}
    return {
        "titulo": str(row.get("titulo") or ""),
        "descricao": str(row.get("descricao") or ""),
        "programa": str(row.get("programa") or ""),
        "acao": str(row.get("acao") or ""),
        "link": str(row.get("link") or ""),
        "fonte": str(row.get("fonte") or row.get("fonte_recurso") or ""),
        "tipo_recurso": row.get("tipo_recurso"),
        "extras": deepcopy(ex),
    }


def load_pairs(input_dir: Path) -> List[Tuple[Dict[str, Any], str]]:
    out: List[Tuple[Dict[str, Any], str]] = []
    for fp in sorted(input_dir.glob("*_standardized.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, list):
            continue
        for row in data:
            if isinstance(row, dict):
                out.append((row, fp.name))
    return out


def classify_row(
    *,
    source_file: str,
    antes: List[str],
    depois: List[str],
    corpus: str,
    changed: bool,
) -> str:
    """D (política por ficheiro) > unchanged > C > B > A."""
    if source_file in LOCK_SOURCE_FILES:
        return "D"
    if not changed:
        return "unchanged"

    had_b = bool(antes)
    empty_after = not depois
    lost_defense = _has_defense_like(antes) and not _has_defense_like(depois)
    mil_txt = _military_evidence(corpus)
    fam = _military_family("", source_file)

    if (
        lost_defense
        and mil_txt
        and source_file not in VERIFIED_OK_FILES
        and fam not in ("dod_sbir_sttr", "nuclep")
    ):
        return "C"

    if had_b and empty_after:
        return "B"

    removed_noisy = bool(_sig(antes) & NOISY) and not (_sig(antes) & NOISY <= _sig(depois))
    if removed_noisy and not mil_txt:
        return "A"
    if removed_noisy and mil_txt and _has_defense_like(depois):
        return "A"
    if not empty_after and not mil_txt:
        return "A"
    if not empty_after:
        return "B"

    return "B"


def build_source_recommendations(by_file: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    apply_normal: List[str] = []
    apply_locked: List[str] = []
    apply_after_en: List[str] = []
    exclude_global: List[str] = []

    for sf in sorted(by_file):
        st = by_file[sf]
        n = st["linhas"]
        pct_empty = st["pct_had_to_empty"]

        if sf in LOCK_SOURCE_FILES:
            apply_locked.append(sf)
            continue
        if sf in VERIFIED_OK_FILES:
            apply_normal.append(sf)
            continue
        if (
            n >= EN_CALIBRATION_MIN_ROWS
            and pct_empty >= EN_CALIBRATION_MIN_PCT_HAD_TO_EMPTY
            and "defesa" not in sf
            and "pncp_defesa" not in sf
        ):
            apply_after_en.append(sf)
            continue
        if "suppliers" in sf or "european_defence_fund" in sf or "nato_diana" in sf:
            exclude_global.append(sf)
            continue
        apply_normal.append(sf)

    return {
        "aplicar_recovery_normalmente": apply_normal,
        "aplicar_com_setor_estrategico_crawler_locked": apply_locked,
        "aplicar_so_depois_calibracao_en": sorted(set(apply_after_en)),
        "excluir_apply_global_por_enquanto": sorted(set(exclude_global)),
    }


def _single_pass_review(pairs: List[Tuple[Dict[str, Any], str]], dryref: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    cat_counts: Counter[str] = Counter()
    samples: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    n_empty_after = 0
    n_had_to_empty = 0
    n_D_changed = 0
    by_file: Dict[str, Dict[str, int]] = defaultdict(
        lambda: {"linhas": 0, "mudam": 0, "had_to_empty": 0, "tinham_setor": 0, "vazio_depois": 0}
    )

    for row, source_file in pairs:
        item = _to_item(row)
        antes = _as_list((item["extras"] or {}).get("setor_estrategico"))
        corpus = _corpus(row)
        enrich_opportunity_classification(item)
        depois = _as_list(item["extras"].get("setor_estrategico"))
        changed = sorted(antes) != sorted(depois)

        by_file[source_file]["linhas"] += 1
        if changed:
            by_file[source_file]["mudam"] += 1
        if antes:
            by_file[source_file]["tinham_setor"] += 1
        if not depois:
            by_file[source_file]["vazio_depois"] += 1
            n_empty_after += 1
        if antes and not depois:
            by_file[source_file]["had_to_empty"] += 1
            n_had_to_empty += 1

        cat = classify_row(
            source_file=source_file,
            antes=antes,
            depois=depois,
            corpus=corpus,
            changed=changed,
        )
        cat_counts[cat] += 1
        if source_file in LOCK_SOURCE_FILES and changed:
            n_D_changed += 1

        rec = {
            "categoria": cat,
            "arquivo": source_file,
            "fonte": item.get("fonte") or "",
            "titulo": (item.get("titulo") or "")[:140],
            "link": (item.get("link") or "")[:240],
            "antes": antes,
            "depois": depois,
        }
        if len(samples[cat]) < 22:
            samples[cat].append(rec)

    by_file_stats: Dict[str, Dict[str, Any]] = {}
    for sf, b in by_file.items():
        n = b["linhas"]
        by_file_stats[sf] = {
            **b,
            "pct_had_to_empty": round(b["had_to_empty"] / n, 4) if n else 0.0,
            "pct_mudam": round(b["mudam"] / n, 4) if n else 0.0,
        }

    rec_src = build_source_recommendations(by_file_stats)
    n_A = cat_counts["A"]
    n_B = cat_counts["B"]
    n_C = cat_counts["C"]
    n_D = cat_counts["D"]
    blocked_lock_all_rows = sum(1 for _, sf in pairs if sf in LOCK_SOURCE_FILES)

    return {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "referencia_dryrun_json": str(DRYRUN_JSON.relative_to(ROOT)).replace("\\", "/"),
        "dryrun_resumo_citado": (
            {
                "total_editais": dryref.get("total_editais_analisados"),
                "mudariam_setor": dryref.get("total_mudariam_setor_estrategico"),
                "tinham_slugs_e_vazio": dryref.get("total_ficariam_sem_setor_tinham_slugs_antes"),
            }
            if dryref
            else None
        ),
        "categorias_legenda": {
            "A": "Correção segura — perda de DI/aero/cyber em setor sem evidência militar (heurística) ou mudança coerente sem esvaziamento.",
            "B": "Correção provável — precisa review manual (tipicamente tinha setor(s) e ficou vazio).",
            "C": "Regressão provável — evidência militar no texto e perda de slugs defense-like (ex.: Grants.gov misto, EDF).",
            "D": "Política de lock por ficheiro — todas as linhas de IARPA / DARPA Opportunities (e darpa_news se existir); não aplicar overwrite global sem `setor_estrategico_crawler_locked`.",
        },
        "contagens_por_categoria": dict(cat_counts),
        "metricas_apply_staging": {
            "itens_aplicacao_segura_estimados_categoria_A": n_A,
            "itens_revisao_manual_prioritaria_categoria_B": n_B,
            "itens_regressao_provavel_categoria_C": n_C,
            "itens_fonte_lock_categoria_D": n_D,
            "linhas_tot_em_ficheiros_lock_D": blocked_lock_all_rows,
            "itens_mudam_em_ficheiros_lock": n_D_changed,
            "itens_inalterados": cat_counts["unchanged"],
            "total_ficariam_sem_setor_estrategico": n_empty_after,
            "total_tinham_slugs_e_ficam_vazios": n_had_to_empty,
            "nota": (
                "D = todas as linhas dos ficheiros IARPA/DARPA listados (política de lock). "
                "Outras linhas: unchanged > C > B > A. Apply global seguro ~ categoria A fora de ficheiros lock; "
                "B+C exigem wave com QA ou calibração antes do apply."
            ),
        },
        "amostras_por_categoria": {k: v for k, v in samples.items()},
        "recomendacao_fontes_por_estrategia": rec_src,
        "estrategia_apply_staging": {
            "opcao_A_global_exceto_lock": (
                "Aplicar overwrite taxonómico globalmente excepto ficheiros em "
                "`aplicar_com_setor_estrategico_crawler_locked` e `excluir_apply_global_por_enquanto`; "
                "adiar linhas categoria B para wave com QA ou manter merge antigo só nessas PKs."
            ),
            "opcao_B_lotes": [
                "1) Lote 'genérico seguro': ficheiros em apply_normal com pct_had_to_empty < 0.25.",
                "2) Lote 'Brasil': demais apply_normal BR (FAP*, CNPq, ANEEL, BNDES, …).",
                "3) Lote 'internacional CTI': apply_normal restante com EN leve ou já calibrado.",
                "4) Lote 'defesa': DoD/NUCLEP apply normal com spot-check; IARPA/DARPA só com lock ou pós-calibração EN.",
            ],
            "opcao_C_so_limpeza_nao_militar": (
                "UPDATE/loader só remove defesa_industrial/aeroespacial de setor_estrategico quando "
                "arquivo fonte ∉ conjunto militar e texto normalizado não contém MILITARY_MARKERS; "
                "não altera linhas que ficariam totalmente vazias (deixa para wave B)."
            ),
        },
        "recomendacao_final": (
            "Adoptar **Opção B** com primeiro wave limitado a ficheiros de baixo `pct_had_to_empty`. "
            "Manter **IARPA** e **DARPA Opportunities** (e `darpa_news` se existir) com "
            "`setor_estrategico_crawler_locked` até extensão EN da taxonomia ou `calibrate_*` dedicado. "
            "Rever **categoria B** (tinha setor → vazio) antes de apply em massa. **Opção A** só após "
            "fecho de B em fontes críticas. **Opção C** como complemento cirúrgico a Opção B."
        ),
        "ficheiros_lock": sorted(LOCK_SOURCE_FILES),
        "ficheiros_verificados_ok_dryrun": sorted(VERIFIED_OK_FILES),
    }


def _write_md(payload: Dict[str, Any], path: Path) -> None:
    m = payload["metricas_apply_staging"]
    lines = [
        "# Review — Recovery global de classificação de setores (pré-apply staging)",
        "",
        f"- **Gerado (UTC):** {payload['gerado_em']}",
        f"- **Referência dry-run:** `{payload['referencia_dryrun_json']}`",
        "",
        "## Legenda A/B/C/D",
        "",
    ]
    for k, v in payload["categorias_legenda"].items():
        lines.append(f"- **{k}:** {v}")
    lines += ["", "## Métricas (staging, estimativa)", ""]
    for key, val in m.items():
        lines.append(f"- **{key}:** {val}")
    lines += ["", "## Recomendação final (resumo executivo)", "", payload["recomendacao_final"], ""]
    lines += ["## Estratégias de apply", ""]
    for k, v in payload["estrategia_apply_staging"].items():
        lines.append(f"### {k}")
        if isinstance(v, list):
            for x in v:
                lines.append(f"- {x}")
        else:
            lines.append(v)
        lines.append("")
    lines += ["## Fontes por política", ""]
    for bucket, files in payload["recomendacao_fontes_por_estrategia"].items():
        lines.append(f"### {bucket} ({len(files)})")
        for f in files[:60]:
            lines.append(f"- `{f}`")
        if len(files) > 60:
            lines.append(f"- … +{len(files) - 60} ficheiros (ver JSON completo)")
        lines.append("")
    lines += ["## Amostras por categoria", ""]
    for cat in ("A", "B", "C", "D"):
        lines.append(f"### Categoria {cat}")
        for ex in payload["amostras_por_categoria"].get(cat, [])[:12]:
            lines.append(
                f"- **{ex.get('fonte')}** (`{ex.get('arquivo')}`) — {ex.get('titulo', '')[:100]}\n"
                f"  - antes: `{ex.get('antes')}` → depois: `{ex.get('depois')}`"
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--dryrun-json", type=Path, default=DRYRUN_JSON)
    args = ap.parse_args()

    dryref: Optional[Dict[str, Any]] = None
    if args.dryrun_json.is_file():
        dryref = json.loads(args.dryrun_json.read_text(encoding="utf-8"))

    pairs = load_pairs(args.input_dir)
    if not pairs:
        print("Sem dados.", file=sys.stderr)
        return 2

    payload = _single_pass_review(pairs, dryref)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_md(payload, OUT_MD)
    print(f"Escrito {OUT_JSON}", file=sys.stderr)
    print(f"Escrito {OUT_MD}", file=sys.stderr)
    print(json.dumps(payload["metricas_apply_staging"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
