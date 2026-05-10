#!/usr/bin/env python3
"""Gera relatórios de política canónica Plataforma Inovação (SENAI vs plataforma_industria)."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "audit_reports_blocked_sources"
SENAI = ROOT / "audit_reports_retransform" / "standardized" / "senai_standardized.json"
PLAT = ROOT / "audit_reports_retransform" / "standardized" / "plataforma_industria_standardized.json"


def norm_link(u: Any) -> str:
    return str(u or "").strip().rstrip("/").lower()


def extras_of(it: Dict[str, Any]) -> Dict[str, Any]:
    ex = it.get("extras")
    return ex if isinstance(ex, dict) else {}


def extras_prune(ex: Dict[str, Any], max_str: int = 320) -> Dict[str, Any]:
    """Cópia legível de extras para o relatório (evita JSON gigante)."""
    out: Dict[str, Any] = {}
    for k, v in ex.items():
        if isinstance(v, str):
            out[k] = (v[:max_str] + "…") if len(v) > max_str else v
        elif isinstance(v, list) and k in ("documentos", "anexos"):
            slim = []
            for d in v[:25]:
                if isinstance(d, dict):
                    slim.append(
                        {
                            "nome": str(d.get("nome") or d.get("titulo") or "")[:120],
                            "url": str(d.get("url") or d.get("link") or "")[:400],
                            "formato": d.get("formato"),
                        }
                    )
            out[k] = slim
        elif isinstance(v, dict):
            try:
                s = json.dumps(v, ensure_ascii=False, default=str)
            except TypeError:
                s = str(v)
            out[k] = (s[:max_str] + "…") if len(s) > max_str else v
        elif isinstance(v, list):
            try:
                s = json.dumps(v, ensure_ascii=False, default=str)
            except TypeError:
                s = str(v)
            out[k] = (s[:max_str] + "…") if len(s) > max_str else v
        else:
            out[k] = v
    return out


def doc_list(it: Dict[str, Any]) -> List[Any]:
    ex = extras_of(it)
    for k in ("documentos", "anexos"):
        v = ex.get(k)
        if isinstance(v, list):
            return v
    return []


def extras_digest(ex: Dict[str, Any]) -> str:
    """Hash estável do extras (exclui blobs enormes repetidos) para comparação rápida."""
    keys = sorted(ex.keys())
    slim = {k: ex[k] for k in keys if k not in ("descricao_original", "descricao_traduzida", "objetivo")}
    try:
        raw = json.dumps(slim, ensure_ascii=False, sort_keys=True, default=str)
    except TypeError:
        raw = str(slim)
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]


def summarize_item(it: Dict[str, Any], label: str) -> Dict[str, Any]:
    ex = extras_of(it)
    desc = str(it.get("descricao") or "")
    docs = doc_list(it)
    extras_chars = 0
    for _k, v in ex.items():
        extras_chars += len(str(v))
    return {
        "fonte_rotulo": label,
        "fonte_campo": str(it.get("fonte") or ""),
        "titulo": str(it.get("titulo") or ""),
        "link": str(it.get("link") or ""),
        "descricao_len": len(desc),
        "descricao_sha256": hashlib.sha256(desc.encode("utf-8", errors="replace")).hexdigest(),
        "documentos_n": len(docs),
        "tipo_oportunidade": ex.get("tipo_oportunidade"),
        "tipo_recurso": str(it.get("tipo_recurso") or ex.get("tipo_recurso") or ""),
        "perfil_ideal": ex.get("perfil_ideal"),
        "validacao_status": ex.get("validacao_status"),
        "qualidade_dado": ex.get("qualidade_dado"),
        "data_publicacao": it.get("data_publicacao"),
        "coletado_em": ex.get("coletado_em"),
        "extras": extras_prune(ex),
        "extras_keys": sorted(ex.keys()),
        "extras_tamanho_total_chars": extras_chars,
        "content_hash": str(ex.get("content_hash") or ""),
        "extras_digest": extras_digest(ex),
    }


def pairwise(s: Dict[str, Any], p: Dict[str, Any]) -> Dict[str, Any]:
    keys = [
        "titulo",
        "descricao_sha256",
        "documentos_n",
        "tipo_oportunidade",
        "tipo_recurso",
        "perfil_ideal",
        "validacao_status",
        "qualidade_dado",
        "content_hash",
        "extras_digest",
        "coletado_em",
        "data_publicacao",
    ]
    diff = [k for k in keys if s.get(k) != p.get(k)]
    return {"campos_iguais": [k for k in keys if k not in diff], "campos_diferentes": diff}


def main() -> int:
    senai = json.loads(SENAI.read_text(encoding="utf-8"))
    plat = json.loads(PLAT.read_text(encoding="utf-8"))
    if not isinstance(senai, list):
        senai = [senai]
    if not isinstance(plat, list):
        plat = [plat]

    by_s = {norm_link(x.get("link")): x for x in senai if isinstance(x, dict)}
    by_p = {norm_link(x.get("link")): x for x in plat if isinstance(x, dict)}
    common = sorted(set(by_s) & set(by_p))
    only_plat = sorted(set(by_p) - set(by_s))

    comparisons: List[Dict[str, Any]] = []
    agg = {
        "pares": 0,
        "titulo_igual": 0,
        "descricao_igual": 0,
        "docs_senai_gt": 0,
        "docs_plat_gt": 0,
        "docs_igual": 0,
        "tipo_op_igual": 0,
        "qualidade_igual": 0,
    }
    for lk in common:
        a, b = by_s[lk], by_p[lk]
        sa, sb = summarize_item(a, "senai_standardized"), summarize_item(b, "plataforma_industria_standardized")
        pw = pairwise(sa, sb)
        comparisons.append({"link_normalizado": lk, "senai": sa, "plataforma_industria": sb, "diff": pw})
        agg["pares"] += 1
        if sa["titulo"] == sb["titulo"]:
            agg["titulo_igual"] += 1
        if sa["descricao_sha256"] == sb["descricao_sha256"]:
            agg["descricao_igual"] += 1
        if sa["documentos_n"] > sb["documentos_n"]:
            agg["docs_senai_gt"] += 1
        elif sb["documentos_n"] > sa["documentos_n"]:
            agg["docs_plat_gt"] += 1
        else:
            agg["docs_igual"] += 1
        if sa["tipo_oportunidade"] == sb["tipo_oportunidade"]:
            agg["tipo_op_igual"] += 1
        if sa["qualidade_dado"] == sb["qualidade_dado"]:
            agg["qualidade_igual"] += 1

    policy_json: Dict[str, Any] = {
        "titulo": "Política canónica — Plataforma Inovação (hubs /categoria/)",
        "data_geracao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "contexto": "SENAI e plataforma_industria partilham 22 URLs de hub; conteúdo e hash coincidem no standardized atual.",
        "fonte_canonica_proposta": "senai",
        "justificativa": [
            "Rótulo institucional: SENAI é o operador explícito da Plataforma Inovação no standardized (campo fonte/orgao).",
            "Descrição e content_hash iguais nos 22 pares — sem ganho material de qualidade ao duplicar a fonte no loader.",
            "documentos_n idêntico nos pares analisados; nenhuma vantagem documental da alias.",
            "tipo_oportunidade e qualidade_dado alinhados; risco de ambiguidade maior se dois crawlers escreverem o mesmo link com fonte_recurso distinto.",
            "URL é a mesma; estabilidade depende do portal, não da fonte de crawl.",
            "Manter plataforma_industria como alias opcional (metadados em extras no futuro) cobre o URL exclusivo inova-mes sem sobrescrever hubs.",
        ],
        "config_recomendada": "config/source_canonicalization.json",
        "politica_loader": "skip_alias_if_canonical_exists quando senai e plataforma_industria entram no mesmo dry-run/apply.",
        "agregados_comparacao_22_links": agg,
        "urls_so_plataforma_industria": only_plat,
        "pares_detalhe": comparisons,
        "recomendacao_final": "Carregar SENAI como canónico para hubs /categoria/; aplicar canonização para ignorar alias duplicado; permitir plataforma_industria apenas para URLs não cobertas pelo SENAI (ex.: inova-mes) ou fundir extras no futuro se preserve_alias_in_extras for implementado.",
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "plataforma_inovacao_canonical_policy.json").write_text(
        json.dumps(policy_json, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md_lines = [
        "# Política canónica — Plataforma Inovação",
        "",
        "## Decisão proposta",
        "",
        "- **Fonte canónica:** `senai`",
        "- **Alias:** `plataforma_industria`",
        "- **Regra de URL:** contém `plataforma-inovacao-para-industria/categoria`",
        "- **Política no loader:** `skip_alias_if_canonical_exists` (ver `config/source_canonicalization.json`)",
        "",
        "## Porquê SENAI como canónico",
        "",
        "1. Alinhamento institucional: o produto é a Plataforma Inovação operada no ecossistema SENAI/Sistema Indústria.",
        "2. Nos 22 pares com mesma URL, **título**, **content_hash** e **descrição** (hash) coincidem — não há ganho de riqueza textual ao preferir a alias.",
        "3. **Documentos** e campos semânticos principais coincidem nos pares; não há motivo para duplicar ingestão no mesmo `link`.",
        "4. O upsert por `link` faria a última fonte sobrescrever `fonte_recurso`; uma fonte canónica reduz ambiguidade.",
        "5. A alias continua útil para **URLs exclusivas** (ex.: categoria `inova-mes` ausente no crawl SENAI) e para rastreio futuro em `extras` se `preserve_alias_in_extras` for implementado.",
        "",
        "## Agregados (22 URLs comuns)",
        "",
        f"- Títulos iguais: **{agg['titulo_igual']}** / {agg['pares']}",
        f"- Descrição (sha256) igual: **{agg['descricao_igual']}** / {agg['pares']}",
        f"- Docs: SENAI > alias: **{agg['docs_senai_gt']}**, alias > SENAI: **{agg['docs_plat_gt']}**, igual: **{agg['docs_igual']}**",
        f"- tipo_oportunidade igual: **{agg['tipo_op_igual']}** / {agg['pares']}",
        f"- qualidade_dado igual: **{agg['qualidade_igual']}** / {agg['pares']}",
        "",
        "## URLs só na plataforma_industria",
        "",
    ]
    for u in only_plat:
        md_lines.append(f"- `{u}`")
    if not only_plat:
        md_lines.append("- (nenhum)")
    md_lines.extend(
        [
            "",
            "## Comparação detalhada",
            "",
            "Lista completa em `plataforma_inovacao_canonical_policy.json` (`pares_detalhe`: fonte, título, link, métricas de descrição, documentos, classificação, validacao_status, qualidade_dado, chaves de extras, content_hash, datas).",
            "",
            "## Recomendação final",
            "",
            policy_json["recomendacao_final"],
            "",
        ]
    )
    (OUT_DIR / "plataforma_inovacao_canonical_policy.md").write_text("\n".join(md_lines), encoding="utf-8")
    print("OK", OUT_DIR / "plataforma_inovacao_canonical_policy.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
