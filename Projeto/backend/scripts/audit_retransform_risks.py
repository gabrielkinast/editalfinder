#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

import transformer as tr  # noqa: E402


OUT_DIR = ROOT / "audit_reports_retransform_risks"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _guess_item_kind(title: str, desc: str, reason: str) -> str:
    blob = f"{title} {desc}".lower()
    if any(x in reason.lower() for x in ("login", "restrito", "intranet", "erro", "indisponivel")):
        return "erro_login_restrito"
    if any(x in blob for x in ("pregão", "pregao", "licit", "tender", "procurement", "compra pública", "compra publica")):
        return "licitacao_compra_publica"
    if any(x in blob for x in ("chamada", "edital", "grant", "funding", "fomento", "bolsa")):
        return "oportunidade_real"
    if any(x in blob for x in ("notícia", "noticia", "news", "blog")):
        return "noticia"
    if any(x in blob for x in ("home", "contato", "about", "quem somos", "institucional")):
        return "pagina_generica"
    return "duvidoso"


def _classify_source_risk(raw: int, transformed: int, reasons: Counter[str], kinds: Counter[str]) -> str:
    if raw > 0 and transformed == 0:
        if sum(v for k, v in reasons.items() if "login" in k.lower() or "restrito" in k.lower() or "erro" in k.lower()) >= max(1, raw // 2):
            return "fonte_quebrada"
        if kinds.get("oportunidade_real", 0) + kinds.get("licitacao_compra_publica", 0) > 0:
            return "gate_agressivo"
        if kinds.get("pagina_generica", 0) + kinds.get("noticia", 0) >= max(1, raw // 2):
            return "fonte_ruidosa"
        return "crawler_fraco"
    if raw > 0 and transformed / max(1, raw) < 0.25:
        if kinds.get("oportunidade_real", 0) > kinds.get("pagina_generica", 0):
            return "precisa_revisao_manual"
        return "fonte_ruidosa"
    if raw <= 2 and transformed == 0:
        return "ok_sem_oportunidades_reais"
    return "pronta_para_ajuste_local"


def _recommendation(bucket: str) -> str:
    mapping = {
        "ok_sem_oportunidades_reais": "Sem ajuste imediato; monitorar frequência futura.",
        "crawler_fraco": "Rever extração do crawler (título/descrição/link detalhe) antes de mexer no gate.",
        "gate_agressivo": "Aplicar ajuste local por fonte com critérios objetivos e logs de relaxamento.",
        "fonte_ruidosa": "Aumentar filtro no crawler/listagem e reduzir URLs institucionais sem chamada.",
        "fonte_quebrada": "Validar acesso/fetch (login/restrição/erro) e robustez de coleta.",
        "precisa_revisao_manual": "Inspecionar amostra manualmente e decidir ajuste local controlado.",
        "pronta_para_excluir_temporariamente": "Suspender temporariamente até corrigir qualidade da fonte.",
        "pronta_para_ajuste_local": "Ajuste local pequeno no transformer sem mexer no gate global.",
    }
    return mapping.get(bucket, "Revisão manual.")


def main() -> int:
    summary = _load_json(ROOT / "audit_reports_retransform" / "retransform_summary.json")
    rows = _load_json(ROOT / "audit_reports_retransform" / "retransform_by_source.json")
    risk_sources = {x.split(":")[0].strip() for x in summary.get("fontes_risco_loader", [])}
    for r in rows:
        if not isinstance(r, dict):
            continue
        raw = int(r.get("itens_brutos_encontrados") or 0)
        trf = int(r.get("itens_transformados") or 0)
        rej = int(r.get("itens_rejeitados") or 0)
        if raw > 0 and (trf == 0 or rej / max(1, raw) >= 0.7):
            risk_sources.add(str(r.get("fonte")))

    by_source: List[Dict[str, Any]] = []
    all_examples: List[Dict[str, Any]] = []
    category_count: Counter[str] = Counter()

    for src in sorted(risk_sources):
        src_row = next((r for r in rows if isinstance(r, dict) and r.get("fonte") == src), None)
        if not src_row:
            continue
        raw_output = ROOT / str(src_row.get("raw_output_path") or "")
        raw_items = []
        if raw_output.is_file():
            rr = _load_json(raw_output)
            if isinstance(rr, dict):
                rr = [rr]
            if isinstance(rr, list):
                raw_items = [x for x in rr if isinstance(x, dict)]

        reasons: Counter[str] = Counter()
        kinds: Counter[str] = Counter()
        ex: List[Dict[str, Any]] = []
        for it in raw_items[:120]:
            trr = tr._transform_item_with_result(it, src)
            if trr.rejected:
                reason = trr.rejection_reason or "sem_motivo"
                reasons[reason] += 1
                kind = _guess_item_kind(str(it.get("titulo") or ""), str(it.get("descricao") or ""), reason)
                kinds[kind] += 1
                if len(ex) < 5:
                    ex.append(
                        {
                            "fonte": src,
                            "titulo": str(it.get("titulo") or "")[:240],
                            "link": str(it.get("link") or it.get("url") or "")[:500],
                            "motivo_rejeicao": reason,
                            "tipo_estimado": kind,
                            "descricao_curta": str(it.get("descricao") or "")[:300],
                        }
                    )

        bucket = _classify_source_risk(
            int(src_row.get("itens_brutos_encontrados") or 0),
            int(src_row.get("itens_transformados") or 0),
            reasons,
            kinds,
        )
        category_count[bucket] += 1
        diag = {
            "fonte": src,
            "bruto_total": int(src_row.get("itens_brutos_encontrados") or 0),
            "transformados": int(src_row.get("itens_transformados") or 0),
            "rejeitados": int(src_row.get("itens_rejeitados") or 0),
            "motivos_rejeicao": dict(reasons.most_common(10)),
            "tipos_rejeitados_estimados": dict(kinds),
            "exemplos_rejeitados": ex,
            "diagnostico": bucket,
            "recomendacao": _recommendation(bucket),
            "parece_problema_crawler": bucket in ("crawler_fraco", "fonte_quebrada"),
            "parece_problema_gate_transformer": bucket in ("gate_agressivo", "pronta_para_ajuste_local", "precisa_revisao_manual"),
            "parece_sem_oportunidade_real": bucket == "ok_sem_oportunidades_reais",
        }
        by_source.append(diag)
        all_examples.extend(ex)

    summary_out = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fontes_risco_total": len(by_source),
        "categorias": dict(category_count),
        "fontes": [x["fonte"] for x in by_source],
    }

    (OUT_DIR / "risk_summary.json").write_text(json.dumps(summary_out, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "risk_by_source.json").write_text(json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "risk_examples.json").write_text(json.dumps(all_examples[:400], ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Auditoria de risco pós-retransformação",
        "",
        f"- Fontes analisadas: **{summary_out['fontes_risco_total']}**",
        "",
        "## Categorias",
        "",
    ]
    for k, v in sorted(category_count.items(), key=lambda kv: kv[1], reverse=True):
        md.append(f"- {k}: {v}")
    md.extend(["", "## Fontes", ""])
    for row in by_source:
        md.append(
            f"- **{row['fonte']}**: bruto={row['bruto_total']}, transformados={row['transformados']}, "
            f"rejeitados={row['rejeitados']} -> `{row['diagnostico']}`"
        )
    (OUT_DIR / "risk_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(OUT_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
