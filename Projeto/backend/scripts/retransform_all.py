#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

import transformer as tr  # noqa: E402

OUT_BASE_DEFAULT = ROOT / "audit_reports_retransform"
NEW_STD_DIR_DEFAULT = OUT_BASE_DEFAULT / "standardized"
OLD_STD_DIR = CORE / "transformer"

EMPTY_TRACK = (
    "area",
    "tipo_oportunidade",
    "tipo_recurso",
    "perfil_ideal",
    "documentos",
    "pdf_url",
)

NOISE_TITLES = {
    "contato",
    "fale conosco",
    "saiba mais",
    "menu",
    "buscar",
    "detalhes",
    "home",
    "about",
    "contact",
}


def _infer_source_from_output(path: Path) -> str:
    return path.parent.parent.name.lower()


def _discover_outputs() -> List[Path]:
    return sorted([p for p in ROOT.glob("*/outputs/*_editais.json") if p.is_file()])


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    if isinstance(v, (list, dict)) and len(v) == 0:
        return True
    return False


def _extras(item: Dict[str, Any]) -> Dict[str, Any]:
    ex = item.get("extras")
    return ex if isinstance(ex, dict) else {}


def _field_value(item: Dict[str, Any], field: str) -> Any:
    ex = _extras(item)
    if field in ("area", "tipo_oportunidade", "perfil_ideal", "documentos", "pdf_url"):
        return ex.get(field)
    if field == "tipo_recurso":
        return item.get("tipo_recurso") or ex.get("tipo_recurso")
    return item.get(field)


def _fill_pct(items: List[Dict[str, Any]], field: str) -> float:
    if not items:
        return 0.0
    ok = sum(1 for it in items if not _is_empty(_field_value(it, field)))
    return round(100.0 * ok / len(items), 2)


def _avg_quality(items: List[Dict[str, Any]]) -> Optional[float]:
    vals = []
    for it in items:
        q = _extras(it).get("qualidade_dado")
        if isinstance(q, (int, float)):
            vals.append(float(q))
    if not vals:
        return None
    return round(sum(vals) / len(vals), 2)


def _count_noise_pass(items: List[Dict[str, Any]]) -> int:
    n = 0
    for it in items:
        t = str(it.get("titulo") or "").strip().lower()
        if t in NOISE_TITLES:
            n += 1
    return n


def _official_link_quick_audit(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    olo = 0
    acc = 0
    reasons: Counter[str] = Counter()
    examples: List[Dict[str, Any]] = []
    for it in items:
        ex = _extras(it)
        if ex.get("extraction_mode") == "official_link_only":
            olo += 1
            reasons[str(ex.get("access_reason") or "unknown")] += 1
    for it in items:
        ex = _extras(it)
        if str(ex.get("validacao_status") or "") == "acesso_limitado":
            acc += 1
            if len(examples) < 10:
                examples.append(
                    {
                        "titulo": str(it.get("titulo") or "")[:160],
                        "link": it.get("link"),
                        "access_reason": ex.get("access_reason"),
                        "extraction_mode": ex.get("extraction_mode"),
                    }
                )
    return {
        "official_link_only_total": olo,
        "access_limited_total": acc,
        "access_reason_counts": dict(reasons),
        "access_limited_examples": examples[:8],
    }


def _dup_links(items: List[Dict[str, Any]]) -> int:
    c: Counter[str] = Counter()
    for it in items:
        lk = str(it.get("link") or "").strip()
        if lk:
            c[lk] += 1
    return sum(1 for _, v in c.items() if v > 1)


def _core_counts(items: List[Dict[str, Any]]) -> Dict[str, int]:
    out = {f: 0 for f in EMPTY_TRACK}
    for it in items:
        for f in EMPTY_TRACK:
            if not _is_empty(_field_value(it, f)):
                out[f] += 1
    return out


def _compare_old_new(old_items: List[Dict[str, Any]], new_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    old_links = {str(i.get("link") or "").strip() for i in old_items if str(i.get("link") or "").strip()}
    new_links = {str(i.get("link") or "").strip() for i in new_items if str(i.get("link") or "").strip()}
    old_counts = _core_counts(old_items)
    new_counts = _core_counts(new_items)
    improved = {}
    worsened = {}
    for f in EMPTY_TRACK:
        if new_counts[f] > old_counts[f]:
            improved[f] = {"old": old_counts[f], "new": new_counts[f], "delta": new_counts[f] - old_counts[f]}
        elif new_counts[f] < old_counts[f]:
            worsened[f] = {"old": old_counts[f], "new": new_counts[f], "delta": new_counts[f] - old_counts[f]}
    return {
        "old_count": len(old_items),
        "new_count": len(new_items),
        "delta_count": len(new_items) - len(old_items),
        "old_links_now_missing": sorted(list(old_links - new_links))[:80],
        "new_links_before_missing": sorted(list(new_links - old_links))[:80],
        "core_fields_improved": improved,
        "core_fields_worsened": worsened,
        "old_documents_count": old_counts["documentos"],
        "new_documents_count": new_counts["documentos"],
        "old_pdf_count": old_counts["pdf_url"],
        "new_pdf_count": new_counts["pdf_url"],
    }


def _load_json_list(path: Path) -> List[Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = [raw]
    return [x for x in raw if isinstance(x, dict)] if isinstance(raw, list) else []


def process_source(path: Path, max_items: int, std_out_dir: Path) -> Dict[str, Any]:
    source = _infer_source_from_output(path)
    raw_items = _load_json_list(path)
    if max_items > 0:
        raw_items = raw_items[:max_items]

    kept: List[Dict[str, Any]] = []
    rejected = 0
    incompletos = 0
    suspeitos = 0
    acesso_limitado = 0
    reasons: Counter[str] = Counter()

    for it in raw_items:
        tr_res = tr._transform_item_with_result(it, source)
        if tr_res.rejected or not tr_res.payload:
            rejected += 1
            reasons[tr_res.rejection_reason or "sem_motivo"] += 1
            continue
        kept.append(tr_res.payload)
        st = _extras(tr_res.payload).get("validacao_status")
        if st == "incompleto":
            incompletos += 1
        elif st == "suspeito":
            suspeitos += 1
        elif st == "acesso_limitado":
            acesso_limitado += 1

    std_out_dir.mkdir(parents=True, exist_ok=True)
    new_std_path = std_out_dir / f"{source}_standardized.json"
    new_std_path.write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")

    old_std_path = OLD_STD_DIR / f"{source}_standardized.json"
    old_items: List[Dict[str, Any]] = []
    if old_std_path.is_file():
        try:
            old_items = _load_json_list(old_std_path)
        except Exception:
            old_items = []

    cmp = _compare_old_new(old_items, kept)

    return {
        "fonte": source,
        "raw_output_path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "old_standardized_path": str(old_std_path.relative_to(ROOT)).replace("\\", "/") if old_std_path.is_file() else "",
        "new_standardized_path": str(new_std_path.relative_to(ROOT)).replace("\\", "/"),
        "itens_brutos_encontrados": len(raw_items),
        "itens_transformados": len(kept),
        "itens_rejeitados": rejected,
        "itens_incompletos": incompletos,
        "itens_suspeitos": suspeitos,
        "itens_acesso_limitado": acesso_limitado,
        "documentos_preservados": _core_counts(kept)["documentos"],
        "pdf_url_preservado": _core_counts(kept)["pdf_url"],
        "area_preenchida": _core_counts(kept)["area"],
        "tipo_oportunidade_preenchido": _core_counts(kept)["tipo_oportunidade"],
        "tipo_recurso_preenchido": _core_counts(kept)["tipo_recurso"],
        "perfil_ideal_preenchido": _core_counts(kept)["perfil_ideal"],
        "qualidade_dado_media": _avg_quality(kept),
        "motivos_rejeicao_principais": dict(reasons.most_common(10)),
        "quick_audit": {
            "ruido_passou": _count_noise_pass(kept),
            "duplicatas_link": _dup_links(kept),
            "campos_preenchidos_pct": {f: _fill_pct(kept, f) for f in EMPTY_TRACK},
            **_official_link_quick_audit(kept),
        },
        "old_vs_new": cmp,
        "risk_notes": [],
    }


def _build_md_summary(summary: Dict[str, Any], rows: List[Dict[str, Any]]) -> str:
    lines = [
        "# Retranformação dry-run",
        "",
        f"- Gerado: `{summary['data_auditoria']}`",
        f"- Fontes processadas: **{summary['fontes_processadas']}**",
        f"- Itens brutos: **{summary['itens_brutos_total']}**",
        f"- Itens transformados: **{summary['itens_transformados_total']}**",
        f"- Itens rejeitados: **{summary['itens_rejeitados_total']}**",
        "",
        "## Por fonte",
        "",
        "| fonte | bruto | transformados | rejeitados | incompletos | suspeitos | docs | pdf | qualidade média |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        q = r.get("qualidade_dado_media")
        qv = f"{q:.2f}" if isinstance(q, (int, float)) else "-"
        lines.append(
            f"| {r['fonte']} | {r['itens_brutos_encontrados']} | {r['itens_transformados']} | {r['itens_rejeitados']} | "
            f"{r['itens_incompletos']} | {r['itens_suspeitos']} | {r['documentos_preservados']} | {r['pdf_url_preservado']} | {qv} |"
        )
    lines.extend(
        [
            "",
            "## Riscos antes do loader real",
            "",
        ]
    )
    for rr in summary.get("fontes_risco_loader", [])[:20]:
        lines.append(f"- {rr}")
    return "\n".join(lines)


def _merge_retransform_by_source(
    out_dir: Path, new_rows: List[Dict[str, Any]], partial: bool
) -> List[Dict[str, Any]]:
    """Com --sources, funde com retransform_by_source.json existente para não apagar outras fontes."""
    if not partial:
        return new_rows
    path = out_dir / "retransform_by_source.json"
    prev: List[Dict[str, Any]] = []
    if path.is_file():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                prev = [x for x in raw if isinstance(x, dict)]
        except Exception:
            prev = []
    by_fonte: Dict[str, Dict[str, Any]] = {}
    for r in prev:
        k = str(r.get("fonte") or "").strip().lower()
        if k:
            by_fonte[k] = r
    for r in new_rows:
        k = str(r.get("fonte") or "").strip().lower()
        if k:
            by_fonte[k] = r
    return [by_fonte[k] for k in sorted(by_fonte.keys())]


def _merge_standardized_old_vs_new(
    out_dir: Path,
    new_fontes: List[Dict[str, Any]],
    partial: bool,
    data_auditoria: str,
) -> Dict[str, Any]:
    if not partial:
        return {"data_auditoria": data_auditoria, "fontes": new_fontes}
    path = out_dir / "standardized_old_vs_new.json"
    if not path.is_file():
        return {"data_auditoria": data_auditoria, "fontes": new_fontes}
    try:
        prev = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        prev = {}
    by_f: Dict[str, Dict[str, Any]] = {}
    for x in prev.get("fontes") or []:
        if isinstance(x, dict) and x.get("fonte"):
            by_f[str(x["fonte"])] = x
    for x in new_fontes:
        if isinstance(x, dict) and x.get("fonte"):
            by_f[str(x["fonte"])] = x
    return {"data_auditoria": data_auditoria, "fontes": [by_f[k] for k in sorted(by_f.keys())]}


def _build_old_new_md(rows: List[Dict[str, Any]]) -> str:
    lines = [
        "# Standardized antigo vs novo",
        "",
        "| fonte | old | new | delta | docs old->new | pdf old->new | old pass agora rejeitados | old rejeitados agora passados |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        c = r["old_vs_new"]
        lines.append(
            f"| {r['fonte']} | {c['old_count']} | {c['new_count']} | {c['delta_count']} | "
            f"{c['old_documents_count']}->{c['new_documents_count']} | {c['old_pdf_count']}->{c['new_pdf_count']} | "
            f"{len(c['old_links_now_missing'])} | {len(c['new_links_before_missing'])} |"
        )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default="", help="Lista CSV de fontes")
    ap.add_argument("--max-items", type=int, default=0, help="Limite por fonte (0=todos)")
    ap.add_argument("--dry-run", action="store_true", help="Sem loader/supabase (apenas transformação)")
    ap.add_argument("--output-dir", default=str(OUT_BASE_DEFAULT))
    ap.add_argument("--standardized-dir", default="", help="Pasta para standardized rebuilt")
    args = ap.parse_args()

    out_dir = Path(args.output_dir)
    if not out_dir.is_absolute():
        out_dir = (ROOT / out_dir).resolve()
    std_dir = Path(args.standardized_dir).resolve() if args.standardized_dir else (out_dir / "standardized")
    out_dir.mkdir(parents=True, exist_ok=True)
    std_dir.mkdir(parents=True, exist_ok=True)

    allowed = {s.strip().lower() for s in args.sources.split(",") if s.strip()} if args.sources.strip() else None
    outputs = _discover_outputs()
    if allowed:
        outputs = [p for p in outputs if _infer_source_from_output(p) in allowed]

    rows: List[Dict[str, Any]] = []
    for p in outputs:
        try:
            rows.append(process_source(p, args.max_items, std_dir))
        except Exception as exc:
            rows.append(
                {
                    "fonte": _infer_source_from_output(p),
                    "raw_output_path": str(p.relative_to(ROOT)).replace("\\", "/"),
                    "erro": str(exc),
                }
            )

    ok_rows = [r for r in rows if "erro" not in r]
    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dry_run": True,
        "fontes_processadas": len(ok_rows),
        "fontes_com_erro": len(rows) - len(ok_rows),
        "itens_brutos_total": sum(r["itens_brutos_encontrados"] for r in ok_rows),
        "itens_transformados_total": sum(r["itens_transformados"] for r in ok_rows),
        "itens_rejeitados_total": sum(r["itens_rejeitados"] for r in ok_rows),
        "fontes_risco_loader": [],
    }
    for r in ok_rows:
        qa = r["quick_audit"]
        if qa["ruido_passou"] > 0 or qa["duplicatas_link"] > 0:
            summary["fontes_risco_loader"].append(
                f"{r['fonte']}: ruido_passou={qa['ruido_passou']}, duplicatas={qa['duplicatas_link']}"
            )
        if r["itens_transformados"] == 0 and r["itens_brutos_encontrados"] > 0:
            summary["fontes_risco_loader"].append(f"{r['fonte']}: 0 transformados com bruto disponível")

    partial = allowed is not None
    merged_rows = _merge_retransform_by_source(out_dir, rows, partial)
    if partial:
        summary["partial_merge_retransform"] = True
        summary["fontes_total_apos_merge"] = len(merged_rows)
    (out_dir / "retransform_by_source.json").write_text(
        json.dumps(merged_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "retransform_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "retransform_summary.md").write_text(_build_md_summary(summary, ok_rows), encoding="utf-8")

    old_new_entries = [
        {
            "fonte": r["fonte"],
            "old_vs_new": r["old_vs_new"],
        }
        for r in ok_rows
    ]
    old_new_json = _merge_standardized_old_vs_new(out_dir, old_new_entries, partial, summary["data_auditoria"])
    (out_dir / "standardized_old_vs_new.json").write_text(json.dumps(old_new_json, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "standardized_old_vs_new.md").write_text(_build_old_new_md(ok_rows), encoding="utf-8")
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
