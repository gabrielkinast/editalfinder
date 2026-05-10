#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
RETRANS_DIR = ROOT / "audit_reports_retransform"
RISK_DIR = ROOT / "audit_reports_retransform_risks"
SEM_DIR = ROOT / "audit_reports_semantic"
ACCESS_DIR = ROOT / "audit_reports_access"


def _load(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _load_access_by_fonte() -> Dict[str, Dict[str, Any]]:
    path = ACCESS_DIR / "source_access_by_source.json"
    data = _load(path, [])
    if not isinstance(data, list):
        return {}
    return {str(r["fonte"]): r for r in data if isinstance(r, dict) and r.get("fonte")}


def _access_limited(acc: Dict[str, Any]) -> bool:
    if not acc:
        return False
    if acc.get("readiness_access_tag") == "blocked_access_limited":
        return True
    cls = acc.get("primary_classification") or ""
    return cls in (
        "cloudflare_403",
        "access_http_403",
        "rate_limit_429",
        "robots_disallow",
        "captcha",
        "login_required",
    )


def _status(
    row: Dict[str, Any],
    risk_map: Dict[str, str],
    sem_map: Dict[str, Dict[str, Any]],
    access_map: Dict[str, Dict[str, Any]],
) -> str:
    src = row["fonte"]
    raw = int(row.get("itens_brutos_encontrados") or 0)
    trf = int(row.get("itens_transformados") or 0)
    rej = int(row.get("itens_rejeitados") or 0)
    rr = risk_map.get(src, "")
    sem = sem_map.get(src, {})
    flag_rate = float(sem.get("flag_rate_pct") or 0.0)
    docs = int(row.get("documentos_preservados") or 0)
    noise = int((row.get("quick_audit") or {}).get("ruido_passou") or 0)
    acc = access_map.get(src) or {}

    if raw > 0 and trf == 0:
        return "bloquear_temporariamente"
    # SAM.gov: sem itens transformados não deve ir para o loader (pendente API / escopo).
    if str(src).lower() == "sam_gov" and trf == 0:
        return "bloquear_temporariamente"
    # Risco de acesso/crawler não deve bloquear se já há itens transformados (evidência real).
    if trf == 0 and rr in ("fonte_quebrada", "crawler_fraco"):
        if _access_limited(acc):
            return "bloquear_temporariamente"
        return "reprocessar_depois_de_ajuste"
    if rej / max(1, raw) > 0.8 and trf < 5:
        return "reprocessar_depois_de_ajuste"
    if flag_rate > 140 or noise > 0:
        return "pronto_com_observacoes"
    if trf > 0 and docs >= 0:
        qa = row.get("quick_audit") or {}
        olo = int(qa.get("official_link_only_total") or 0)
        if olo / max(1, trf) >= 0.35:
            return "pronto_com_observacoes"
        inc = int(row.get("itens_incompletos") or 0)
        if inc > 0 and (inc / trf) >= 0.85:
            return "pronto_com_observacoes"
        if trf > 0 and rr == "gate_agressivo":
            return "pronto_com_observacoes"
        if _access_limited(acc):
            return "pronto_com_observacoes"
        return "pronto_para_loader"
    return "precisa_revisao_manual"


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Gera readiness_for_loader.json a partir de retransform_by_source.json e relatórios auxiliares."
    )
    ap.add_argument(
        "--retransform-by-source",
        default="",
        help="Caminho para retransform_by_source.json (por defeito: audit_reports_retransform/retransform_by_source.json).",
    )
    ap.add_argument(
        "--old-vs-new",
        default="",
        help="Caminho para standardized_old_vs_new.json (por defeito: junto ao retransform).",
    )
    ap.add_argument(
        "--risk-dir",
        default="",
        help="Pasta com risk_by_source.json (por defeito: audit_reports_retransform_risks).",
    )
    ap.add_argument(
        "--semantic-dir",
        default="",
        help="Pasta com audit_semantic_by_source.json (por defeito: audit_reports_semantic).",
    )
    ap.add_argument(
        "--output-dir",
        default="",
        help="Pasta de saída para readiness_for_loader.json e readiness_rows.json (por defeito: audit_reports_retransform).",
    )
    args = ap.parse_args()

    retrans_path = (
        Path(args.retransform_by_source).resolve()
        if args.retransform_by_source.strip()
        else (RETRANS_DIR / "retransform_by_source.json")
    )
    out_dir = Path(args.output_dir).resolve() if args.output_dir.strip() else RETRANS_DIR
    old_vs_path = (
        Path(args.old_vs_new).resolve()
        if args.old_vs_new.strip()
        else (retrans_path.parent / "standardized_old_vs_new.json")
    )
    risk_dir = Path(args.risk_dir).resolve() if args.risk_dir.strip() else RISK_DIR
    sem_dir = Path(args.semantic_dir).resolve() if args.semantic_dir.strip() else SEM_DIR

    by_source = _load(retrans_path, [])
    risk_by_source = _load(risk_dir / "risk_by_source.json", [])
    sem_by_source = _load(sem_dir / "audit_semantic_by_source.json", [])
    sem_summary = _load(sem_dir / "audit_semantic_summary.json", {})
    old_new = _load(old_vs_path, {})

    risk_map = {r["fonte"]: r.get("diagnostico", "") for r in risk_by_source if isinstance(r, dict)}
    sem_map = {r["fonte"]: r for r in sem_by_source if isinstance(r, dict)}
    old_map = {r["fonte"]: r.get("old_vs_new", {}) for r in old_new.get("fontes", []) if isinstance(r, dict)}
    access_map = _load_access_by_fonte()

    rows: List[Dict[str, Any]] = []
    for r in by_source:
        if not isinstance(r, dict):
            continue
        src = r["fonte"]
        st = _status(r, risk_map, sem_map, access_map)
        sem = sem_map.get(src, {})
        cmp = old_map.get(src, {})
        acc = access_map.get(src) or {}
        ac_limited = _access_limited(acc)
        rr = risk_map.get(src, "nao_mapeado")
        access_diag: Dict[str, Any] = {
            "primary_classification": acc.get("primary_classification"),
            "recommended_method": acc.get("recommended_method"),
            "readiness_access_tag": acc.get("readiness_access_tag"),
        }
        if ac_limited and rr in ("fonte_quebrada", "crawler_fraco"):
            access_diag["nota"] = (
                "Probe de acesso indica limite (WAF/robots/login/captcha). "
                "Não assumir apenas que o crawler está logicamente incorreto — ver audit_reports_access/."
            )
        elif ac_limited and int(r.get("itens_brutos_encontrados") or 0) > 0 and int(r.get("itens_transformados") or 0) == 0:
            access_diag["nota"] = (
                "Brutos sem transformados com sinais de acesso limitado no último audit_source_access_methods."
            )
        qa_row = r.get("quick_audit") or {}
        olo_n = int(qa_row.get("official_link_only_total") or 0)
        trf_n = max(1, int(r.get("itens_transformados") or 0))
        ol_ratio = round(olo_n / trf_n, 4)
        rows.append(
            {
                "fonte": src,
                "transformados": r.get("itens_transformados"),
                "rejeitados": r.get("itens_rejeitados"),
                "risco": rr,
                "qualidade_semantica": {
                    "flag_rate_pct": sem.get("flag_rate_pct"),
                    "flags_top": sorted((sem.get("flags") or {}).items(), key=lambda kv: kv[1], reverse=True)[:5],
                },
                "documentos": r.get("documentos_preservados"),
                "campos_vazios": (r.get("quick_audit") or {}).get("campos_preenchidos_pct"),
                "old_vs_new": {
                    "delta_count": cmp.get("delta_count"),
                    "old_pass_agora_rejeitados": len(cmp.get("old_links_now_missing", [])),
                    "old_rej_agora_passados": len(cmp.get("new_links_before_missing", [])),
                },
                "recomendacao_loader": st,
                "diagnostico_acesso": access_diag,
                "official_link_only_ratio": ol_ratio,
                "readiness_official_link_dependency": "alta" if ol_ratio >= 0.35 else "baixa",
            }
        )

    status_count: Dict[str, int] = {}
    for r in rows:
        status_count[r["recomendacao_loader"]] = status_count.get(r["recomendacao_loader"], 0) + 1

    ready = [r["fonte"] for r in rows if r["recomendacao_loader"] in ("pronto_para_loader", "pronto_com_observacoes")]
    blocked = [r["fonte"] for r in rows if r["recomendacao_loader"] == "bloquear_temporariamente"]
    review = [r["fonte"] for r in rows if r["recomendacao_loader"] in ("reprocessar_depois_de_ajuste", "precisa_revisao_manual")]

    readiness = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fontes_total": len(rows),
        "status_distribution": status_count,
        "fontes_prontas_para_loader": ready,
        "fontes_bloqueadas_temporariamente": blocked,
        "fontes_para_revisao": review,
        "top20_problemas_semanticos": sem_summary.get("top20_problemas_semanticos", [])[:20],
        "top20_ajustes_recomendados": sem_summary.get("top20_ajustes_recomendados", [])[:20],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "readiness_for_loader.json").write_text(json.dumps(readiness, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "readiness_rows.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Readiness para loader",
        "",
        f"- Fontes totais: **{readiness['fontes_total']}**",
        f"- Origem `retransform_by_source.json`: `{retrans_path}`",
        f"- Saída: `{out_dir}`",
        "",
        "## Distribuição",
        "",
    ]
    for k, v in sorted(status_count.items(), key=lambda kv: kv[1], reverse=True):
        md.append(f"- {k}: {v}")
    md.extend(
        [
            "",
            "## Fontes bloqueadas temporariamente",
            "",
        ]
    )
    for s in blocked:
        md.append(f"- {s}")
    md.extend(["", "## Fontes prontas para loader", ""])
    for s in ready:
        md.append(f"- {s}")
    (out_dir / "readiness_for_loader.md").write_text("\n".join(md), encoding="utf-8")

    human = [
        "# Old vs New — revisão humana",
        "",
        "## Fontes que melhoraram claramente",
        "",
    ]
    improved = sorted(
        rows,
        key=lambda r: int(((old_map.get(r["fonte"], {})).get("core_fields_improved") or {}).get("documentos", {}).get("delta", 0)),
        reverse=True,
    )
    for r in improved[:20]:
        d = int(((old_map.get(r["fonte"], {})).get("core_fields_improved") or {}).get("documentos", {}).get("delta", 0))
        if d > 0:
            human.append(f"- {r['fonte']}: +{d} em documentos preservados")
    human.extend(["", "## Fontes que pioraram", ""])
    worsened = sorted(rows, key=lambda r: int((old_map.get(r["fonte"], {}) or {}).get("delta_count") or 0))
    for r in worsened[:20]:
        dc = int((old_map.get(r["fonte"], {}) or {}).get("delta_count") or 0)
        if dc < 0:
            human.append(f"- {r['fonte']}: delta itens {dc}")
    human.extend(["", "## Fontes para revisão manual antes do loader", ""])
    for s in review[:30]:
        human.append(f"- {s}")
    human.extend(["", "## Acesso (WAF / robots) — interpretação", ""])
    human.append(
        "Se existir `audit_reports_access/source_access_by_source.json` (gerado por "
        "`scripts/audit_source_access_methods.py`), cada fonte pode trazer "
        "`diagnostico_acesso` em `readiness_rows.json` com `readiness_access_tag` "
        "e `primary_classification` — evita confundir bloqueio de rede com crawler logicamente errado."
    )
    human.extend(
        [
            "",
            "## Official link only / acesso limitado",
            "",
            "Campos `official_link_only_ratio` e `readiness_official_link_dependency` em `readiness_rows.json`: "
            "se a proporção de itens `extraction_mode=official_link_only` for ≥ 0.35, "
            "a recomendação deixa de ser `pronto_para_loader` e passa a `pronto_com_observacoes`. "
            "Relatório agregado: `audit_reports_access/official_link_only_summary.*` "
            "(`scripts/audit_official_link_only.py`).",
        ]
    )
    human.extend(["", "## Top 20 problemas semânticos", ""])
    for k, v in readiness["top20_problemas_semanticos"]:
        human.append(f"- {k}: {v}")
    human.extend(["", "## Top 20 ajustes recomendados", ""])
    for x in readiness["top20_ajustes_recomendados"]:
        human.append(f"- {x}")
    (out_dir / "old_vs_new_human_review.md").write_text("\n".join(human), encoding="utf-8")
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
