#!/usr/bin/env python3
"""
Dry-run global de `setor_estrategico` sobre o catálogo standardized local mais próximo
do pipeline atual (`audit_reports_retransform/standardized/`).

Sem Supabase, sem apply. Gera JSON + Markdown em `audit_reports_main_pipeline/`.
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

DEFAULT_INPUT_DIR = ROOT / "audit_reports_retransform" / "standardized"
OUT_JSON = ROOT / "audit_reports_main_pipeline" / "recovery_classificacao_global_dryrun.json"
OUT_MD = ROOT / "audit_reports_main_pipeline" / "recovery_classificacao_global_dryrun.md"

TRACK_LOSS = ("defesa_industrial", "aeroespacial", "cyber_defesa")
DEFENSE_LIKE = ("defesa_industrial", "defesa", "aeroespacial", "cyber_defesa", "dual_use")
NOISY_REMOVAL_GOOD = ("defesa_industrial", "aeroespacial", "cyber_defesa")

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


def _set_sig(s: Sequence[str]) -> Set[str]:
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
    if "esa_star" in fn or "esa star" in fl or "esa-star" in fl:
        return "esa_star"
    return None


def _has_defense_like(se: Sequence[str]) -> bool:
    return bool(_set_sig(se) & set(DEFENSE_LIKE))


def _item_corpus(row: Dict[str, Any]) -> str:
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


def _normalize_row_to_item(row: Dict[str, Any]) -> Dict[str, Any]:
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


def load_standardized_dir(input_dir: Path) -> List[Tuple[Dict[str, Any], str]]:
    out: List[Tuple[Dict[str, Any], str]] = []
    for fp in sorted(input_dir.glob("*_standardized.json")):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"Aviso: ignorar {fp}: {e}", file=sys.stderr)
            continue
        if not isinstance(data, list):
            continue
        for row in data:
            if isinstance(row, dict):
                out.append((row, fp.name))
    return out


def run_catalog(
    pairs: List[Tuple[Dict[str, Any], str]],
    *,
    input_dir: Path,
) -> Dict[str, Any]:
    total = len(pairs)
    mudam = 0
    loss_di = 0
    loss_aero = 0
    loss_cyber = 0
    ficam_vazios = 0
    vazios_tinham_setor_antes = 0
    vazios_ja_vazios_antes = 0
    mudancas_por_fonte: Counter[str] = Counter()
    mudancas_por_arquivo: Counter[str] = Counter()

    exemplos_mudanca: List[Dict[str, Any]] = []
    boas: List[Dict[str, Any]] = []
    duvidosos: List[Dict[str, Any]] = []
    lock_rec: List[Dict[str, Any]] = []

    military_by_family: Dict[str, Dict[str, int]] = defaultdict(
        lambda: {
            "linhas": 0,
            "com_defense_like_depois": 0,
            "regressao_militar": 0,
        }
    )

    for row, src_file in pairs:
        item = _normalize_row_to_item(row)
        fonte = item["fonte"] or "desconhecida"
        antes = _as_list((item["extras"] or {}).get("setor_estrategico"))
        corpus = _item_corpus(item)

        enrich_opportunity_classification(item)
        depois = _as_list(item["extras"].get("setor_estrategico"))
        hist = item["extras"].get("setor_estrategico_historico_merge")

        sa, sd = sorted(antes), sorted(depois)
        if sa != sd:
            mudam += 1
            mudancas_por_fonte[fonte] += 1
            mudancas_por_arquivo[src_file] += 1

        if "defesa_industrial" in antes and "defesa_industrial" not in depois:
            loss_di += 1
        if "aeroespacial" in antes and "aeroespacial" not in depois:
            loss_aero += 1
        if "cyber_defesa" in antes and "cyber_defesa" not in depois:
            loss_cyber += 1
        if not depois:
            ficam_vazios += 1
            if antes:
                vazios_tinham_setor_antes += 1
            else:
                vazios_ja_vazios_antes += 1

        fam = _military_family(fonte, src_file)
        if fam:
            bucket = military_by_family[fam]
            bucket["linhas"] += 1
            if _has_defense_like(depois):
                bucket["com_defense_like_depois"] += 1
            if _has_defense_like(antes) and not _has_defense_like(depois) and _military_evidence(corpus):
                bucket["regressao_militar"] += 1

        if sa == sd:
            continue

        ex_rec = {
            "fonte": fonte,
            "arquivo": src_file,
            "titulo": (item.get("titulo") or "")[:160],
            "link": (item.get("link") or "")[:300],
            "antes": antes,
            "depois": depois,
            "historico_merge": hist,
        }
        exemplos_mudanca.append(ex_rec)

        removed_noisy = bool(_set_sig(antes) & set(NOISY_REMOVAL_GOOD)) and not (
            _set_sig(antes) & set(NOISY_REMOVAL_GOOD) <= _set_sig(depois)
        )
        mil_reg = bool(fam) and _military_evidence(corpus) and _has_defense_like(antes) and not _has_defense_like(depois)

        if mil_reg or (fam and _has_defense_like(antes) and not _has_defense_like(depois) and len(antes) >= 2):
            lock_rec.append({**ex_rec, "motivo_lock": "military_family_evidence_loss" if mil_reg else "multi_sector_drop"})
        elif removed_noisy and not mil_reg:
            boas.append({**ex_rec, "motivo_boa": "remocao_slug_ruidoso"})
        else:
            duvidosos.append({**ex_rec, "motivo_duvidoso": "mudanca_sem_criterio_boa_ou_lock"})

    top_fontes = mudancas_por_fonte.most_common(40)
    top_arquivos = mudancas_por_arquivo.most_common(40)

    try:
        rel_data = str(input_dir.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        rel_data = str(input_dir.resolve()).replace("\\", "/")

    return {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "fonte_dados": rel_data,
        "total_editais_analisados": total,
        "total_mudariam_setor_estrategico": mudam,
        "total_perderiam_defesa_industrial": loss_di,
        "total_perderiam_aeroespacial": loss_aero,
        "total_perderiam_cyber_defesa": loss_cyber,
        "total_ficariam_sem_setor_estrategico": ficam_vazios,
        "total_ficariam_sem_setor_tinham_slugs_antes": vazios_tinham_setor_antes,
        "total_ficariam_sem_setor_ja_vazios_antes": vazios_ja_vazios_antes,
        "nota_cyber_defesa": (
            "Contagem só em extras.setor_estrategico. Neste corpus, cyber_defesa aparece sobretudo em "
            "area_tecnologica/subtema, não na lista de setor estratégico — por isso perda em setor pode ser 0."
        ),
        "top_fontes_mais_afetadas": top_fontes,
        "top_arquivos_mais_afetados": top_arquivos,
        "sanidade_fontes_militares": dict(military_by_family),
        "exemplos_correcoes_boas": boas[:40],
        "exemplos_casos_duvidosos": duvidosos[:40],
        "exemplos_lock_recomendado": lock_rec[:40],
        "exemplos_mudanca_todas_amostra": exemplos_mudanca[:80],
    }


def _md_table(rows: List[Tuple[str, str]]) -> str:
    lines = ["| chave | valor |", "| --- | ---: |"]
    for a, b in rows:
        lines.append(f"| {a} | {b} |")
    return "\n".join(lines)


def write_markdown(payload: Dict[str, Any], path: Path) -> None:
    t = payload["total_editais_analisados"]
    mud = payload["total_mudariam_setor_estrategico"]
    lines = [
        "# Dry-run — Recovery global de classificação de setores",
        "",
        f"- **Gerado (UTC):** {payload['gerado_em']}",
        f"- **Corpus:** `{payload['fonte_dados']}` (standardized local, sem Supabase)",
        "",
        "## Totais",
        "",
        _md_table(
            [
                ("Editais analisados", str(t)),
                ("Mudariam `setor_estrategico`", str(mud)),
                ("Perderiam `defesa_industrial`", str(payload["total_perderiam_defesa_industrial"])),
                ("Perderiam `aeroespacial`", str(payload["total_perderiam_aeroespacial"])),
                ("Perderiam `cyber_defesa` (só em `setor_estrategico`)", str(payload["total_perderiam_cyber_defesa"])),
                ("Ficariam sem `setor_estrategico`", str(payload["total_ficariam_sem_setor_estrategico"])),
                ("… desses, já vazios antes do enrich", str(payload.get("total_ficariam_sem_setor_ja_vazios_antes", "?"))),
                ("… desses, tinham slugs antes e esvaziam", str(payload.get("total_ficariam_sem_setor_tinham_slugs_antes", "?"))),
            ]
        ),
        "",
        f"**Nota `cyber_defesa`:** {payload.get('nota_cyber_defesa', '')}",
        "",
        "## Interpretação rápida (sanidade militar)",
        "",
        "- **DoD SBIR/STTR** e **NUCLEP**: no snapshot, todos os itens da família mantêm pelo menos um slug *defense-like* após o enrich — alinhado ao esperado.",
        "- **IARPA** / **DARPA** (e parte do **Grants.gov** agregado): muitos títulos/descrições estão em inglês com agências militares sem bater nas frases actuais de `THEMATIC_PATTERNS` (acento PT + listas focadas em PT). O enrich taxonómico pode **esvaziar** ou **reduzir** `setor_estrategico`; para cargas curadas, usar **`setor_estrategico_crawler_locked`** ou alargar padrões noutra PR.",
        "- **ESA OSIP / AMAZUL**: ver contagens na tabela abaixo; `aeroespacial` depende de evidência orbital/espacial no texto.",
        "",
        "## Top fontes mais afetadas (por nº de linhas com alteração)",
        "",
    ]
    for f, c in payload.get("top_fontes_mais_afetadas", [])[:20]:
        lines.append(f"- **{f}**: {c}")
    lines += ["", "## Sanidade — fontes militares / defesa (evidência textual heurística)", ""]
    for fam, stats in sorted((payload.get("sanidade_fontes_militares") or {}).items()):
        lines.append(f"### {fam}")
        lines.append(_md_table([(k, str(v)) for k, v in stats.items()]))
        lines.append("")
    lines += ["## Correções claramente boas (amostra)", ""]
    for i, ex in enumerate(payload.get("exemplos_correcoes_boas") or [], 1):
        lines.append(f"{i}. **{ex.get('fonte')}** — {ex.get('titulo', '')[:120]}")
        lines.append(f"   - antes: `{ex.get('antes')}` → depois: `{ex.get('depois')}`")
        lines.append("")
    lines += ["## Casos duvidosos (amostra)", ""]
    for i, ex in enumerate(payload.get("exemplos_casos_duvidosos") or [], 1):
        lines.append(f"{i}. **{ex.get('fonte')}** — {ex.get('titulo', '')[:120]}")
        lines.append(f"   - antes: `{ex.get('antes')}` → depois: `{ex.get('depois')}`")
        lines.append("")
    lines += ["## Lock de crawler recomendado (amostra)", ""]
    for i, ex in enumerate(payload.get("exemplos_lock_recomendado") or [], 1):
        lines.append(f"{i}. **{ex.get('fonte')}** ({ex.get('motivo_lock')}) — {ex.get('titulo', '')[:120]}")
        lines.append(f"   - antes: `{ex.get('antes')}` → depois: `{ex.get('depois')}`")
        lines.append("")
    lines += [
        "---",
        "Métricas derivadas de `enrich_opportunity_classification` + taxonomia corrente. **Não** constitui apply em base de dados.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Pasta com *_standardized.json",
    )
    ap.add_argument("--out-json", type=Path, default=OUT_JSON)
    ap.add_argument("--out-md", type=Path, default=OUT_MD)
    args = ap.parse_args()

    if not args.input_dir.is_dir():
        print(f"Pasta inexistente: {args.input_dir}", file=sys.stderr)
        return 2

    pairs = load_standardized_dir(args.input_dir)
    if not pairs:
        print("Nenhum item carregado.", file=sys.stderr)
        return 2

    payload = run_catalog(pairs, input_dir=args.input_dir.resolve())
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(payload, args.out_md)
    print(json.dumps({k: payload[k] for k in payload if k.startswith("total_")}, indent=2))
    print(f"JSON: {args.out_json}", file=sys.stderr)
    print(f"MD:   {args.out_md}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
