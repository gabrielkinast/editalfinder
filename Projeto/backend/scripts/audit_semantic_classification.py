#!/usr/bin/env python3
from __future__ import annotations

import json
import argparse
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent


NUCLEAR_SOURCES = {"cnen", "ipen", "inb", "eletronuclear", "nuclep"}
DEFENSE_SOURCES = {"pncp_defesa", "compras_defesa", "marinha", "amazul", "defesa", "dcta_ita_iae", "nato_diana"}
CREDIT_SOURCES = {
    "bndes",
    "brde",
    "badesul",
    "caixa",
    "bnb",
    "banco_da_amazonia",
    "desenvolve_sp",
    "bdmg",
    "agerio",
}
FOMENTO_SOURCES = {"finep", "cnpq", "capes", "fapergs", "fapesp", "fapesc", "fappr", "fapemig", "confap"}


def _normalize(v: Any) -> str:
    return str(v or "").strip().lower()


def _arr(v: Any) -> List[str]:
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str) and v.strip():
        return [v.strip()]
    return []


def _txt(it: Dict[str, Any], ex: Dict[str, Any]) -> str:
    parts = [
        it.get("titulo") or "",
        it.get("descricao") or "",
        it.get("programa") or "",
        it.get("acao") or "",
        ex.get("objetivo") or "",
        ex.get("sam_gov_department") or "",
        ex.get("sam_gov_notice_type") or "",
        ex.get("sam_gov_subtier") or "",
        " ".join(_arr(ex.get("palavras_chave_detectadas"))),
    ]
    return " ".join(str(p) for p in parts).lower()


def _has(blob: str, kws: List[str]) -> bool:
    return any(k in blob for k in kws)


def audit_item(source: str, it: Dict[str, Any]) -> List[str]:
    ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
    blob = _txt(it, ex)
    flags: List[str] = []
    area = _arr(ex.get("area"))
    perfil = _arr(ex.get("perfil_ideal"))
    setor_est = _arr(ex.get("setor_estrategico"))
    area_c = _arr(ex.get("area_cientifica"))
    area_t = _arr(ex.get("area_tecnologica"))
    publico = _arr(ex.get("publico_alvo"))
    tipo_op = _normalize(ex.get("tipo_oportunidade"))
    tipo_rec = _normalize(it.get("tipo_recurso") or ex.get("tipo_recurso"))
    conf = _normalize(ex.get("classificacao_confianca"))

    if not area and not tipo_op and not tipo_rec:
        flags.append("classificacao_ausente")
    if tipo_rec in ("", "não especificado", "nao especificado", "outro", "geral"):
        flags.append("tipo_recurso_generico")
    if tipo_op in ("", "programa", "oportunidade", "generico", "generic_page"):
        flags.append("tipo_oportunidade_generico")
    if len(perfil) > 5:
        flags.append("perfil_ideal_excessivo")
    if len(area) > 6:
        flags.append("area_excessiva")
    if len(setor_est) > 5:
        flags.append("setor_estrategico_excessivo")
    if area_c and not _has(blob, ["pesquisa", "cient", "science", "univers", "laborat"]):
        flags.append("area_cientifica_sem_evidencia")
    if area_t and not _has(blob, ["tecn", "inova", "engenh", "sistema", "software", "ia"]):
        flags.append("area_tecnologica_sem_evidencia")
    if publico and not _has(blob, ["empresa", "fornecedor", "pesquisador", "univers", "ict", "startup", "estudante"]):
        flags.append("publico_alvo_sem_evidencia")
    if len(area) + len(perfil) + len(setor_est) > 12:
        flags.append("classificacao_muito_ampla")
    if "credit" in tipo_rec or "financi" in tipo_rec or "linha" in tipo_op:
        if not _has(blob, ["crédito", "credito", "financi", "juros", "amortização", "carência"]):
            flags.append("oportunidade_credito_sem_credito")
    if "fomento" in tipo_rec or "chamada" in tipo_op or "bolsa" in tipo_rec:
        lk = (it.get("link") or "").lower()
        he_topic = (
            _normalize(source) == "horizon_europe"
            and "topic-details/horizon-" in lk
            and tipo_op in ("funding_opportunity", "chamada_internacional", "chamada_publica", "grant")
            and (
                "fomento" in tipo_rec
                or "grant" in tipo_rec
                or "subven" in tipo_rec
                or "nao reembols" in tipo_rec
                or "não reembols" in tipo_rec
            )
        )
        erc_grant = (
            _normalize(source) == "erc"
            and "erc.europa.eu/apply-grant/" in lk
            and tipo_op in ("grant", "chamada_publica")
            and ("fomento" in tipo_rec or "grant" in tipo_rec)
        )
        if he_topic or erc_grant:
            pass
        elif _normalize(source) == "sam_gov" and tipo_op in ("chamada_publica", "funding_opportunity") and _has(
            blob,
            [
                "sbir",
                "sttr",
                "research",
                "solicitation",
                "baa",
                "federal",
                "department",
                "technology",
                "science",
                "nasa",
                "doe",
                "dod",
            ],
        ):
            pass
        elif not _has(
            blob,
            [
                "fomento",
                "pesquisa",
                "bolsa",
                "chamada",
                "subven",
                "edital",
                "grant",
                "funding",
                "horizon",
                "research",
                "topic",
            ],
        ):
            flags.append("oportunidade_fomento_sem_fomento")
    if "licit" in tipo_op or "compra" in tipo_op:
        if not _has(blob, ["licit", "pregão", "pregao", "tender", "procurement", "compra"]):
            if source == "pncp" and _has(
                blob,
                [
                    "contrat",
                    "dispensa",
                    "aquisi",
                    "compra publica",
                    "compra pública",
                    "processo",
                    "edital",
                    "licit",
                ],
            ):
                pass
            elif source == "sam_gov" and _has(
                blob,
                [
                    "sam.gov",
                    "solicitation",
                    "presolicitation",
                    "department",
                    "federal",
                    "notice",
                    "rfp",
                    "rfq",
                    "naics",
                    "psc",
                    "procurement",
                    "contract opportunity",
                    "sub-tier",
                    "office:",
                ],
            ):
                pass
            else:
                flags.append("licitacao_sem_licitacao")
    if source in NUCLEAR_SOURCES and not _has(blob, ["nuclear", "radi", "reator", "radioisot", "urânio", "uranio"]):
        flags.append("fonte_nuclear_sem_nuclear")
    if source in DEFENSE_SOURCES and not (
        _has(blob, ["defesa", "militar", "forças armadas", "forcas armadas", "exército", "marinha", "aeronáutica", "aeronautica"])
        or (
            source == "nato_diana"
            and _has(
                blob,
                [
                    "defence",
                    "defense",
                    "nato",
                    "diana",
                    "military",
                    "allied",
                    "warfighter",
                    "inovacao_defesa",
                    "dual_use",
                ],
            )
        )
        or (
            source == "iarpa"
            and _has(
                blob,
                [
                    "iarpa",
                    "intelligence advanced",
                    "grants.gov",
                    "baa",
                    "broad agency",
                    "solicitation",
                    "funding opportunity",
                    "research program",
                    "odni",
                    "national intelligence",
                ],
            )
        )
    ):
        flags.append("fonte_defesa_sem_defesa")
    if source in FOMENTO_SOURCES and tipo_op in ("chamada_publica", "edital", "bolsa"):
        if not _has(blob, ["pesquisa", "cient", "univers", "ict", "laborat", "bolsa"]):
            flags.append("chamada_cientifica_sem_pesquisa")
    if conf == "baixa" and (area or tipo_op or tipo_rec):
        flags.append("classificacao_incoerente_com_fonte")
    return flags


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", default=str(ROOT / "audit_reports_retransform" / "standardized"))
    ap.add_argument("--output-dir", default=str(ROOT / "audit_reports_semantic"))
    args = ap.parse_args()

    in_dir = Path(args.input_dir).resolve() if not Path(args.input_dir).is_absolute() else Path(args.input_dir)
    out_dir = Path(args.output_dir).resolve() if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted([p for p in in_dir.glob("*_standardized.json") if p.is_file()])
    by_source: List[Dict[str, Any]] = []
    all_flags: List[Dict[str, Any]] = []
    profile_excess: List[Dict[str, Any]] = []
    area_excess: List[Dict[str, Any]] = []
    expected_vs_detected: Dict[str, Dict[str, Any]] = {}
    examples: List[Dict[str, Any]] = []
    flag_counter: Counter[str] = Counter()

    for p in files:
        source = p.name.replace("_standardized.json", "")
        data = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            data = [data]
        items = [x for x in data if isinstance(x, dict)]
        src_flags: Counter[str] = Counter()
        q_vals = []
        for it in items:
            ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
            flags = audit_item(source, it)
            for f in flags:
                src_flags[f] += 1
                flag_counter[f] += 1
            if flags and len(examples) < 400:
                examples.append(
                    {
                        "fonte": source,
                        "titulo": str(it.get("titulo") or "")[:220],
                        "link": str(it.get("link") or "")[:420],
                        "flags": flags,
                        "tipo_recurso": it.get("tipo_recurso") or ex.get("tipo_recurso"),
                        "tipo_oportunidade": ex.get("tipo_oportunidade"),
                        "area": ex.get("area"),
                        "perfil_ideal": ex.get("perfil_ideal"),
                    }
                )
            if isinstance(ex.get("qualidade_dado"), (int, float)):
                q_vals.append(float(ex.get("qualidade_dado")))

            area = _arr(ex.get("area"))
            perfil = _arr(ex.get("perfil_ideal"))
            setor = _arr(ex.get("setor_estrategico"))
            if len(perfil) > 5 and len(profile_excess) < 300:
                profile_excess.append({"fonte": source, "titulo": it.get("titulo"), "perfil_ideal": perfil})
            if len(area) > 6 and len(area_excess) < 300:
                area_excess.append({"fonte": source, "titulo": it.get("titulo"), "area": area, "setor_estrategico": setor})

            all_flags.append(
                {
                    "fonte": source,
                    "titulo": str(it.get("titulo") or "")[:220],
                    "link": str(it.get("link") or "")[:420],
                    "flags": flags,
                }
            )

        n = len(items)
        expected_vs_detected[source] = {
            "fonte": source,
            "grupo_credito": source in CREDIT_SOURCES,
            "grupo_fomento": source in FOMENTO_SOURCES,
            "grupo_nuclear": source in NUCLEAR_SOURCES,
            "grupo_defesa": source in DEFENSE_SOURCES,
            "itens": n,
            "flags_criticas": sum(src_flags[f] for f in ("classificacao_ausente", "classificacao_incoerente_com_fonte", "licitacao_sem_licitacao")),
        }
        by_source.append(
            {
                "fonte": source,
                "itens": n,
                "qualidade_media": round(sum(q_vals) / len(q_vals), 2) if q_vals else None,
                "flags": dict(src_flags),
                "flag_rate_pct": round(100.0 * sum(src_flags.values()) / max(1, n), 2),
            }
        )

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fontes": len(by_source),
        "itens_total": sum(x["itens"] for x in by_source),
        "flags_totais": dict(flag_counter),
        "top20_problemas_semanticos": flag_counter.most_common(20),
    }

    adjustments = [
        "Restringir perfil_ideal genérico por evidência textual mínima.",
        "Separar regras de crédito vs fomento por fonte + palavras-chave obrigatórias.",
        "Exigir marcador de licitação para tipo_oportunidade=licitacao/compra_publica.",
        "Reduzir classificação ampla quando classficacao_confianca=baixa.",
        "Para fontes nucleares/defesa: usar peso institucional + objeto para evitar over/under tag.",
        "Fortalecer extração de publico_alvo por entidades explícitas.",
        "Adicionar fallback de área para itens com tipo_recurso definido e área vazia.",
        "Revisar taxonomia em fontes com flag_rate > 100%.",
    ]
    summary["top20_ajustes_recomendados"] = adjustments[:20]

    (out_dir / "audit_semantic_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "audit_semantic_by_source.json").write_text(json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "audit_semantic_flags.json").write_text(json.dumps(all_flags[:3000], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "audit_profile_excess.json").write_text(json.dumps(profile_excess, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "audit_area_excess.json").write_text(json.dumps(area_excess, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "audit_expected_vs_detected.json").write_text(json.dumps(expected_vs_detected, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "audit_examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Auditoria semântica",
        "",
        f"- Fontes: **{summary['fontes']}**",
        f"- Itens: **{summary['itens_total']}**",
        "",
        "## Top 20 problemas",
        "",
    ]
    for k, v in summary["top20_problemas_semanticos"]:
        md.append(f"- {k}: {v}")
    md.extend(["", "## Top ajustes recomendados", ""])
    for a in adjustments[:20]:
        md.append(f"- {a}")
    (out_dir / "audit_semantic_summary.md").write_text("\n".join(md), encoding="utf-8")
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
