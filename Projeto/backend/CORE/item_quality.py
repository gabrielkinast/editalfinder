"""Pontuação de qualidade e estados de validação para itens transformados."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple


def compute_item_quality(item: Dict[str, Any]) -> Tuple[int, str, List[str], List[str]]:
    """
    Retorna (score 0–100, nivel, flags, warnings).
    """
    warnings: List[str] = []
    flags: List[str] = []
    score = 0
    tit = (item.get("titulo") or "").strip()
    desc = (item.get("descricao") or "").strip()
    link = (item.get("link") or "").strip()
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    fonte = (item.get("fonte") or item.get("fonte_recurso") or ex.get("fonte_recurso") or "").strip()

    if len(tit) >= 12:
        score += 15
        flags.append("titulo_ok")
    elif len(tit) >= 6:
        score += 8
        warnings.append("titulo_curto")

    if len(desc) >= 400:
        score += 25
        flags.append("descricao_rica")
    elif len(desc) >= 120:
        score += 15
        flags.append("descricao_media")
    elif len(desc) >= 40:
        score += 8
        warnings.append("descricao_curta")
    else:
        warnings.append("descricao_muito_curta")

    if link.startswith("http"):
        score += 12
        flags.append("link_http")
    if ex.get("pdf_url") or ex.get("documentos"):
        score += 12
        flags.append("documentacao")

    if item.get("fim_inscricao"):
        score += 10
        flags.append("prazo")
    else:
        warnings.append("prazo_ausente")

    if item.get("valor"):
        score += 8
        flags.append("valor")
    else:
        warnings.append("valor_ausente")

    if fonte:
        score += 6
    else:
        warnings.append("fonte_ausente")

    tipo = item.get("tipo_recurso") or ex.get("tipo_recurso")
    if tipo and tipo != "Não Especificado":
        score += 7
        flags.append("tipo_recurso")
    else:
        warnings.append("tipo_recurso_ausente")

    if ex.get("area") or ex.get("tipo_oportunidade"):
        score += 5

    score = max(0, min(100, score))

    if score >= 72:
        nivel = "alto"
    elif score >= 45:
        nivel = "medio"
    else:
        nivel = "baixo"

    return score, nivel, flags, warnings


def _validation_status_from_payload(payload: Dict[str, Any], warnings: List[str]) -> str:
    """Mínimo salvar: título + link ou pdf + fonte. Ausência de prazo/valor não descarta."""
    ex0 = payload.get("extras") if isinstance(payload.get("extras"), dict) else {}
    if ex0.get("extraction_mode") == "official_link_only" or ex0.get("validacao_status") == "acesso_limitado":
        return "acesso_limitado"
    tit = (payload.get("titulo") or "").strip()
    link = (payload.get("link") or "").strip()
    fonte = (payload.get("fonte") or payload.get("fonte_recurso") or ex0.get("fonte_recurso") or "").strip()
    pdf_ok = bool((ex0.get("pdf_url") or "").strip().startswith("http"))
    if len(tit) < 4 or not fonte:
        return "suspeito"
    if not link.startswith("http") and not pdf_ok:
        return "suspeito"
    wset = set(warnings)
    if {"prazo_ausente", "valor_ausente", "descricao_muito_curta"} <= wset:
        return "incompleto"
    if "prazo_ausente" in wset or "valor_ausente" in wset or "descricao_muito_curta" in wset:
        return "incompleto"
    return "valido"


def apply_quality_to_payload(payload: Dict[str, Any]) -> None:
    """Escreve extras.qualidade_* e validacao_* no item já montado."""
    score, nivel, flags, warnings = compute_item_quality(payload)
    ex = payload.get("extras")
    if not isinstance(ex, dict):
        ex = {}
        payload["extras"] = ex
    if ex.get("extraction_mode") == "official_link_only":
        score = min(int(score), 58)
        nivel = "baixo" if score < 38 else "medio"
        warnings = list(dict.fromkeys(list(warnings) + ["official_link_only", "requires_manual_review"]))
    # Recovery D — hubs e documentação supplier: não inflar score como «edital forte»
    capped_recovery_d = False
    if ex.get("recovery_d_doc_supplier") or str(ex.get("tipo_oportunidade") or "").strip() == "documentacao_fornecedor":
        score = min(int(score), 62)
        warnings = list(dict.fromkeys(list(warnings) + ["recovery_d_doc_supplier_cap"]))
        capped_recovery_d = True
    elif ex.get("recovery_d1_hub_supplier"):
        score = min(int(score), 70)
        warnings = list(dict.fromkeys(list(warnings) + ["recovery_d_hub_supplier_cap"]))
        capped_recovery_d = True
    if capped_recovery_d:
        score = max(0, min(100, int(score)))
        if score >= 72:
            nivel = "alto"
        elif score >= 45:
            nivel = "medio"
        else:
            nivel = "baixo"
    ex["qualidade_dado"] = score
    ex["qualidade_nivel"] = nivel
    ex["qualidade_flags"] = flags
    ex["qualidade_problemas"] = list(warnings)
    ex["validacao_status"] = _validation_status_from_payload(payload, warnings)
    ex["validacao_warnings"] = list(warnings)
    if ex.get("extraction_mode") == "official_link_only":
        ex["validacao_status"] = "acesso_limitado"
        ex["classificacao_confianca"] = str(ex.get("official_link_only_confidence_level") or ex.get("classificacao_confianca") or "baixa")
        if "access_limited_pipeline" not in ex["validacao_warnings"]:
            ex["validacao_warnings"].append("access_limited_pipeline")
    if ex.get("opportunity_gate_relaxed"):
        sc = str(ex.get("opportunity_gate_relax_scope") or "")
        lk = str(payload.get("link") or "")
        lk_low = lk.lower()
        cred_br_linha = (
            sc == "credito_brasil_onda_a"
            and "bancoamazonia.com.br" in lk_low
            and (
                str(ex.get("tipo_oportunidade") or "").strip().casefold() == "programa_credito"
                or any(
                    p in lk_low
                    for p in (
                        "linhas-de-fomento",
                        "fno",
                        "pronaf",
                        "fungetur",
                        "finame",
                        "credito-e-financiamento",
                        "financiamento-agro",
                        "capital-de-giro",
                        "microcredito",
                        "fundo-constitucional",
                    )
                )
            )
        )
        he_topic = (
            str(payload.get("fonte") or "").strip().upper() == "HORIZON_EUROPE"
            and "topic-details/horizon-" in lk.lower()
            and sc == "horizon_europe_local"
        )
        erc_scheme = (
            str(payload.get("fonte") or "").strip().upper() == "ERC"
            and "/apply-grant/" in lk.lower()
            and "erc.europa.eu" in lk.lower()
            and sc == "erc_local"
        )
        dod_sbir_topic = (
            sc == "dod_sbir_sttr_recovery_a_local"
            and "sbir.gov" in lk_low
            and (
                re.search(r"/topics/\d+", lk_low) is not None
                or "/solicitations/" in lk_low
                or lk_low.startswith("https://www.sbir.gov/solicitation/")
            )
        )
        if cred_br_linha:
            ex["validacao_status"] = "incompleto"
            if "opportunity_gate_credito_br_onda_a_linha" not in ex["validacao_warnings"]:
                ex["validacao_warnings"].append("opportunity_gate_credito_br_onda_a_linha")
        elif he_topic or erc_scheme:
            tag = (
                "opportunity_gate_horizon_europe_relaxed"
                if he_topic
                else "opportunity_gate_erc_relaxed"
            )
            if tag not in ex["validacao_warnings"]:
                ex["validacao_warnings"].append(tag)
        elif dod_sbir_topic:
            ex["validacao_status"] = "incompleto"
            if "opportunity_gate_dod_sbir_sttr_topic" not in ex["validacao_warnings"]:
                ex["validacao_warnings"].append("opportunity_gate_dod_sbir_sttr_topic")
        elif sc == "amazul_local" and "amazul.mar.mil.br" in lk_low:
            ex["validacao_status"] = "incompleto"
            if "recovery_b_amazul_gate_relaxed" not in ex["validacao_warnings"]:
                ex["validacao_warnings"].append("recovery_b_amazul_gate_relaxed")
        elif sc == "ambev_local" and (
            ("100accelerator.com" in lk_low and "/challenges/" in lk_low) or "ambev.com.br" in lk_low
        ):
            ex["validacao_status"] = "incompleto"
            if "recovery_b_ambev_gate_relaxed" not in ex["validacao_warnings"]:
                ex["validacao_warnings"].append("recovery_b_ambev_gate_relaxed")
        elif sc == "badesul_local" and "badesul.com.br" in lk_low:
            ex["validacao_status"] = "incompleto"
            if "recovery_b_badesul_gate_relaxed" not in ex["validacao_warnings"]:
                ex["validacao_warnings"].append("recovery_b_badesul_gate_relaxed")
        elif ex.get("extraction_mode") != "official_link_only":
            ex["validacao_status"] = "suspeito"
            if "opportunity_gate_trusted_br_relaxed" not in ex["validacao_warnings"]:
                ex["validacao_warnings"].append("opportunity_gate_trusted_br_relaxed")

    # Recovery B.1 — AMAZUL: páginas de detalhe de compra/licitação calibradas não devem ficar suspeitas
    # quando o gate global não marcou relax (ex.: linhas já válidas em qualidade mas suspeito no staging legado).
    fonte_l = str(payload.get("fonte") or ex.get("fonte_recurso") or "").strip().lower()
    if fonte_l == "amazul" and ex.get("extraction_mode") != "official_link_only":
        lk_l = str(payload.get("link") or "").lower()
        slug_proc = "/acesso-a-informacao/licitacoes-e-contratos/" in lk_l and any(
            x in lk_l
            for x in (
                "dispensa-de-licitacao",
                "dispensa-de-licitação",
                "pregao",
                "pregão",
                "contrato",
                "edital",
            )
        )
        to = str(ex.get("tipo_oportunidade") or "").strip().lower()
        tc = str(ex.get("tipo_conteudo_amazul") or "")
        if (
            slug_proc
            and (to == "licitacao" or tc == "compra_licitacao")
            and str(ex.get("validacao_status") or "").strip().lower() == "suspeito"
        ):
            ex["validacao_status"] = "incompleto"
            if "recovery_b1_amazul_licitacao_detalhe" not in ex["validacao_warnings"]:
                ex["validacao_warnings"].append("recovery_b1_amazul_licitacao_detalhe")
    if ex["validacao_status"] == "incompleto" and not ex.get("validacao_erros"):
        ex["validacao_erros"] = []
