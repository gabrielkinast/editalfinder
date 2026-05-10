#!/usr/bin/env python3
"""
Auditoria de rejeições do opportunity_gate (falsos positivos prováveis).

Lê JSON bruto das fontes BR críticas, aplica evaluate_item_dict e filtra por:
  - Relevancia limite: poucos sinais de oportunidade
  - Pontuacao abaixo do minimo (oportunidade nao evidenciada)

Gera:
  audit_reports_gate/audit_gate_false_positives.json
  audit_reports_gate/audit_gate_false_positives.md

Uso:
  python scripts/audit_gate_false_positives.py
  python scripts/audit_gate_false_positives.py --max-items 200
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
OUT_DIR = ROOT / "audit_reports_gate"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from opportunity_gate import evaluate_item_dict  # noqa: E402

SOURCES = ("aneel", "bndes", "cnpq", "finep")

_BR_MARKERS = (
    "chamada",
    "edital",
    "programa",
    "consulta",
    "licit",
    "pregão",
    "pregao",
    "financiamento",
    "credito",
    "crédito",
    "bolsa",
    "fomento",
    "linha de crédito",
    "linha de credito",
    "resultado",
    "portaria",
    "normativo",
    "resolução",
    "resolucao",
    "extrato",
    "seleção",
    "selecao",
    "proposta",
    "publicação",
    "publicacao",
)


def _raw_path(source: str) -> Path:
    return ROOT / source / "outputs" / f"{source}_editais.json"


def _is_target_rejection(reason: str) -> bool:
    r = (reason or "").strip()
    return "Relevancia limite" in r or "Pontuacao abaixo" in r


def _short_desc(item: Dict[str, Any], max_len: int = 220) -> str:
    t = str(item.get("descricao") or item.get("resumo") or "").strip().replace("\n", " ")
    if len(t) <= max_len:
        return t
    return t[: max_len - 3] + "..."


def _absent_markers(corpus: str) -> List[str]:
    low = corpus.lower()
    return [m for m in _BR_MARKERS if m not in low][:15]


def _heuristic_class(item: Dict[str, Any]) -> str:
    tit = (item.get("titulo") or "").strip().lower()
    link = (item.get("link") or item.get("url") or "").strip().lower()
    desc = (item.get("descricao") or item.get("resumo") or "").strip().lower()
    blob = f"{tit} {desc} {link}"

    if len(tit) < 2 and len(link) < 8:
        return "lixo"
    if tit in ("contato", "menu", "saiba mais", "início", "inicio", "buscar", "detalhes"):
        return "lixo"
    if link.endswith(".pdf") or ".pdf?" in link:
        return "documento_pdf_provavel"
    if "/noticia" in link or "/news/" in link or "/noticias/" in link:
        if any(k in blob for k in ("chamada", "edital", "financiamento", "seleção", "selecao")):
            return "duvidoso"
        return "noticia"
    if any(
        k in blob
        for k in (
            "chamada pública",
            "chamada publica",
            "edital",
            "pregão",
            "pregao",
            "linha de crédito",
            "linha de credito",
            "consulta pública",
            "consulta publica",
            "financiamento",
            "fomento",
            "bolsa",
            "licitação",
            "licitacao",
        )
    ):
        return "oportunidade_real_provavel"
    if any(k in blob for k in ("institucional", "quem somos", "apresentação", "apresentacao", "sobre o ")):
        return "pagina_institucional"
    if len(desc) < 60 and not any(k in blob for k in ("programa", "projeto", "chamada", "edital", "financi", "bolsa")):
        return "pagina_generica"
    return "duvidoso"


def _recommendation(bucket: str) -> str:
    if bucket in ("lixo", "noticia", "pagina_institucional", "pagina_generica"):
        return "rejeitar"
    if bucket in ("oportunidade_real_provavel", "documento_pdf_provavel", "duvidoso"):
        return "revisar_manual"
    return "revisar_manual"


def _possible_tipo(blob: str) -> str:
    low = blob.lower()
    if any(x in low for x in ("licit", "pregão", "pregao", "compra pública", "compra publica")):
        return "licitacao"
    if "consulta pública" in low or "consulta publica" in low:
        return "chamada_publica"
    if "bolsa" in low:
        return "bolsa"
    if any(x in low for x in ("financiamento", "crédito", "credito", "linha de crédito", "linha de credito")):
        return "financiamento_linha"
    if "chamada" in low or "edital" in low:
        return "chamada_publica_ou_edital"
    if low.endswith(".pdf") or ".pdf" in low:
        return "documento_oficial"
    return "programa_ou_institucional"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-items", type=int, default=500, help="Máximo de itens por ficheiro JSON")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []

    for src in SOURCES:
        path = _raw_path(src)
        if not path.is_file():
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            rows.append(
                {
                    "fonte": src,
                    "arquivo": str(path.relative_to(ROOT)),
                    "erro_leitura": str(e),
                }
            )
            continue
        if isinstance(raw, dict):
            raw = [raw]
        if not isinstance(raw, list):
            continue
        items = [x for x in raw[: args.max_items] if isinstance(x, dict)]
        for it in items:
            gate = evaluate_item_dict(it)
            reason = gate.rejection_reason or ""
            if gate.keep or not _is_target_rejection(reason):
                continue
            tit = str(it.get("titulo") or "")
            link = str(it.get("link") or it.get("url") or "")
            corpus = f"{tit}\n{link}\n{_short_desc(it, 800)}".lower()
            bucket = _heuristic_class(it)
            rows.append(
                {
                    "fonte": src,
                    "arquivo": str(path.relative_to(ROOT)),
                    "titulo": tit[:400],
                    "link": link[:800],
                    "descricao_curta": _short_desc(it),
                    "motivo_rejeicao": reason,
                    "opportunity_score": gate.opportunity_score,
                    "opportunity_intent": gate.opportunity_intent,
                    "gate_category": gate.gate_category,
                    "sinais_detectados": list(gate.detected_terms or [])[:40],
                    "sinais_ausentes": _absent_markers(corpus),
                    "classificacao_heuristica": bucket,
                    "possivel_tipo_real": _possible_tipo(corpus),
                    "recomendacao": _recommendation(bucket),
                    "item_snapshot": {
                        "titulo": it.get("titulo"),
                        "descricao": (str(it.get("descricao") or it.get("resumo") or "")[:1200]),
                        "link": it.get("link") or it.get("url"),
                        "fonte": it.get("fonte"),
                        "extras": it.get("extras") if isinstance(it.get("extras"), dict) else {},
                    },
                }
            )

    summary = {
        "fontes": list(SOURCES),
        "total_rejeicoes_gate_alvo": len(rows),
        "por_fonte": {s: sum(1 for r in rows if r.get("fonte") == s) for s in SOURCES},
        "por_classificacao_heuristica": {},
    }
    for r in rows:
        k = r.get("classificacao_heuristica") or "?"
        summary["por_classificacao_heuristica"][k] = summary["por_classificacao_heuristica"].get(k, 0) + 1

    out_json = OUT_DIR / "audit_gate_false_positives.json"
    payload = {"summary": summary, "itens": rows}
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Auditoria: falsos positivos do `opportunity_gate`",
        "",
        "Rejeições filtradas: **Relevancia limite** ou **Pontuacao abaixo do minimo**.",
        "",
        f"- Total na amostra: **{summary['total_rejeicoes_gate_alvo']}**",
        f"- Por fonte: `{json.dumps(summary['por_fonte'], ensure_ascii=False)}`",
        f"- Por heurística: `{json.dumps(summary['por_classificacao_heuristica'], ensure_ascii=False)}`",
        "",
        "Detalhe completo: `audit_gate_false_positives.json`.",
        "",
        "## Amostra (até 40 linhas)",
        "",
        "| fonte | classificacao | recomendacao | motivo | titulo (resumo) |",
        "|---|---|---|---|---|",
    ]
    for r in rows[:40]:
        tit = str(r.get("titulo") or "")[:70].replace("|", "/")
        md_lines.append(
            f"| {r.get('fonte')} | {r.get('classificacao_heuristica')} | {r.get('recomendacao')} | "
            f"{str(r.get('motivo_rejeicao') or '')[:40]} | {tit} |"
        )
    (OUT_DIR / "audit_gate_false_positives.md").write_text("\n".join(md_lines), encoding="utf-8")
    print(out_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
