#!/usr/bin/env python3
"""
Compara dois relatórios de scripts/audit_pipeline.py (antes vs depois do gate).

Lê audit_summary.json + audit_by_source.json em dois diretórios e, se existir,
audit_gate_false_positives.json para contar recuperações pelo gate (mesmo snapshot).

Uso:
  python scripts/compare_gate_audit_reports.py \\
    --before audit_reports_pdf_subset_skipscore \\
    --after audit_reports_gate_after \\
    --false-positives audit_reports_gate/audit_gate_false_positives.json \\
    --output audit_reports_gate_after/COMPARACAO_gate_before_after.md
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))


def _load_summary(d: Path) -> Dict[str, Any]:
    p = d / "audit_summary.json"
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _aggregate_motivos(by_source: List[Dict[str, Any]]) -> Counter[str]:
    c: Counter[str] = Counter()
    for b in by_source:
        for k, v in (b.get("motivos_rejeicao") or {}).items():
            try:
                c[k] += int(v)
            except (TypeError, ValueError):
                continue
    return c


def _load_by_source(d: Path) -> List[Dict[str, Any]]:
    p = d / "audit_by_source.json"
    if not p.is_file():
        return []
    raw = json.loads(p.read_text(encoding="utf-8"))
    return raw if isinstance(raw, list) else []


def _totals(by_source: List[Dict[str, Any]]) -> Tuple[int, int, int]:
    raw = sum(int(b.get("itens_brutos_amostra") or 0) for b in by_source)
    ok = sum(int(b.get("transformados") or 0) for b in by_source)
    rej = sum(int(b.get("rejeitados") or 0) for b in by_source)
    return raw, ok, rej


def _count_false_positives_recovered(fp_path: Path) -> Tuple[int, List[str]]:
    from opportunity_gate import evaluate_item_dict

    if not fp_path.is_file():
        return 0, []
    data = json.loads(fp_path.read_text(encoding="utf-8"))
    items = data.get("itens") if isinstance(data, dict) else []
    recovered: List[str] = []
    n = 0
    for row in items:
        snap = row.get("item_snapshot")
        if not isinstance(snap, dict):
            continue
        it = {
            "titulo": snap.get("titulo"),
            "descricao": snap.get("descricao"),
            "link": snap.get("link"),
            "fonte": snap.get("fonte"),
            "extras": snap.get("extras") if isinstance(snap.get("extras"), dict) else {},
        }
        g = evaluate_item_dict(it)
        if g.keep:
            n += 1
            link = str(snap.get("link") or "")[:200]
            recovered.append(f"{row.get('fonte')}: {link}")
    return n, recovered[:80]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", type=Path, required=True)
    ap.add_argument("--after", type=Path, required=True)
    ap.add_argument("--false-positives", type=Path, default=ROOT / "audit_reports_gate" / "audit_gate_false_positives.json")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    before_dir = (ROOT / args.before).resolve() if not args.before.is_absolute() else args.before
    after_dir = (ROOT / args.after).resolve() if not args.after.is_absolute() else args.after
    fp_path = args.false_positives
    out_path = (ROOT / args.output).resolve() if not args.output.is_absolute() else args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sb = _load_summary(before_dir)
    sa = _load_summary(after_dir)
    bsrc = _load_by_source(before_dir)
    asrc = _load_by_source(after_dir)
    mb = _aggregate_motivos(bsrc)
    ma = _aggregate_motivos(asrc)
    raw_b, ok_b, rej_b = _totals(bsrc)
    raw_a, ok_a, rej_a = _totals(asrc)

    def _m(c: Counter[str], sub: str) -> int:
        return sum(v for k, v in c.items() if sub in k)

    rel_b = _m(mb, "Relevancia limite")
    rel_a = _m(ma, "Relevancia limite")
    pts_b = _m(mb, "Pontuacao abaixo")
    pts_a = _m(ma, "Pontuacao abaixo")
    noise_b = sum(len(b.get("noise_passou_transformer") or []) for b in bsrc)
    noise_a = sum(len(b.get("noise_passou_transformer") or []) for b in asrc)

    n_rec, rec_list = _count_false_positives_recovered(fp_path)

    still_fp: List[str] = []
    if fp_path.is_file():
        from opportunity_gate import evaluate_item_dict

        data = json.loads(fp_path.read_text(encoding="utf-8"))
        for row in data.get("itens") or []:
            snap = row.get("item_snapshot")
            if not isinstance(snap, dict):
                continue
            it = {
                "titulo": snap.get("titulo"),
                "descricao": snap.get("descricao"),
                "link": snap.get("link"),
                "fonte": snap.get("fonte"),
                "extras": snap.get("extras") if isinstance(snap.get("extras"), dict) else {},
            }
            g = evaluate_item_dict(it)
            if not g.keep and (("Relevancia limite" in (g.rejection_reason or "")) or ("Pontuacao abaixo" in (g.rejection_reason or ""))):
                still_fp.append(f"{row.get('fonte')}: {(snap.get('link') or '')[:120]}")

    lines = [
        "# Comparação gate: antes vs depois",
        "",
        "## Diretórios",
        "",
        f"- **Antes:** `{before_dir}`",
        f"- **Depois:** `{after_dir}`",
        f"- **Falsos positivos (snapshot):** `{fp_path}`",
        "",
        "## Agregados (audit_by_source)",
        "",
        "| Métrica | Antes | Depois | Delta |",
        "|---|---:|---:|---:|",
        f"| Itens brutos (amostra) | {raw_b} | {raw_a} | {raw_a - raw_b} |",
        f"| Transformados (aceitos) | {ok_b} | {ok_a} | {ok_a - ok_b} |",
        f"| Rejeitados | {rej_b} | {rej_a} | {rej_a - rej_b} |",
        f"| Rejeições «Relevancia limite» | {rel_b} | {rel_a} | {rel_a - rel_b} |",
        f"| Rejeições «Pontuacao abaixo» | {pts_b} | {pts_a} | {pts_a - pts_b} |",
        f"| Ruído que passou (lista noise) | {noise_b} | {noise_a} | {noise_a - noise_b} |",
        "",
        "## Recuperação no snapshot de falsos positivos",
        "",
        f"- Itens do relatório FP que o gate **aceitaria agora** (`keep=True`): **{n_rec}**",
        "",
        "_Se o JSON de FP tiver 0 itens, o gate atual já não emite essas duas rejeições na amostra bruta das quatro fontes — não há linhas para «recuperar» nesse ficheiro; use um baseline antigo ou histórico git para listar casos._",
        "",
    ]
    if rec_list:
        lines.append("### Links recuperados (amostra)")
        lines.extend(f"- {x}" for x in rec_list[:40])
        lines.append("")

    lines.extend(
        [
            "## Possíveis falsos positivos restantes (gate ainda rejeita com motivo alvo)",
            "",
        ]
    )
    if still_fp:
        lines.extend(f"- {x}" for x in still_fp[:35])
    else:
        lines.append("_Nenhum ou relatório FP ausente._")
    lines.extend(["", "## Campos vazios (score global no audit_summary)", ""])

    def _field_rank(summary: Dict[str, Any], field: str) -> Optional[int]:
        rk = summary.get("ranking_campos_vazios") or {}
        for row in rk.get("campos_mais_vazios_global") or []:
            if row.get("campo") == field:
                v = row.get("score")
                return int(v) if isinstance(v, (int, float)) else None
        return None

    def _rank_line(label: str, key: str) -> str:
        rb = _field_rank(sb, key) if sb else None
        ra = _field_rank(sa, key) if sa else None
        return f"- **{label}:** antes={rb} · depois={ra}"

    for key, label in [
        ("area", "area"),
        ("tipo_oportunidade", "tipo_oportunidade"),
        ("perfil_ideal", "perfil_ideal"),
        ("setor_economico", "setor_economico"),
        ("documentos", "documentos"),
    ]:
        lines.append(_rank_line(label, key))

    lines.extend(
        [
            "",
            "_Nota: o «score» global de campos vazios no `audit_summary` soma vazios em **todos** os itens transformados; com muito mais aceites, alguns campos (ex.: `documentos`, `fim_inscricao`) podem subir no ranking mesmo com melhoria por item — comparar também `campos_preenchidos_pct` em `audit_by_source.json`._",
            "",
            "## Respostas objetivas",
            "",
            f"1. **Oportunidades antes rejeitadas e agora aceitas (agregado):** delta de transformados = **{ok_a - ok_b}** (na mesma amostra/max-items; depende de ter corrido o pipeline com os mesmos parâmetros).",
            f"2. **Lixo passou?** entradas em `noise_passou_transformer`: antes **{noise_b}**, depois **{noise_a}**.",
            f"3. **Campos ricos:** `br_public_hints` + relax do gate; o auditor agora lê `tipo_oportunidade`/`area`/setores em `extras` (ver `campos_preenchidos_pct` por fonte).",
            f"4. **BNDES/CNPq/Finep/Aneel:** ver delta por fonte em `audit_by_source.json` de cada pasta.",
            "5. **Regras a ajustar:** se «Relevancia limite»/«Pontuacao abaixo» ainda dominam, rever `trusted_fin` + lista de marcadores ou expandir `trusted_br_relevance_soft_continue` com critérios mais rígidos contra notícias.",
            "",
            "## Próxima etapa (recomendações)",
            "",
            "- Rever manualmente uma amostra dos **25 aceites por fonte** (guias vs chamadas reais) para calibrar `noticia_sem_oportunidade` e `content_type_detectado`.",
            "- Melhorar **extração de `documentos`/`pdf_url`** quando o HTML não traz PDF mas o crawler já tem `extras.pdf_url`.",
            "- Opcional: persistir `opportunity_gate_category` no loader/schema quando for ligar o Supabase.",
            "- Expandir taxonomia só com evidência (novos padrões PT) para `area_cientifica` quando o texto tiver disciplinas explícitas.",
        ]
    )

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
