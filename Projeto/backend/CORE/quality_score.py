"""
Score de qualidade 0–100 (Backend 9) — não exclui registros automaticamente.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from noise_classifier import classify_noise
from validity_resolver import resolve_validity


def compute_quality_score(
    record: Dict[str, Any],
    enrichment: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    enrichment: dict já enriquecido (backend_9) ou None para calcular inline.
    """
    enr = enrichment or {}
    nz = {
        "is_noise": enr.get("is_noise"),
        "noise_type": enr.get("noise_type"),
        "is_actionable_opportunity": enr.get("is_actionable_opportunity"),
        "actionability_score": enr.get("actionability_score"),
        "quality_flags": enr.get("quality_flags") or [],
        "confidence": enr.get("confidence"),
    }
    if nz.get("noise_type") is None:
        full_nz = classify_noise(record)
        nz.update(full_nz)

    val_status = enr.get("validade_status")
    if not val_status:
        val = resolve_validity(record, noise=nz if nz.get("noise_type") else None)
        val_status = val.get("validade_status")

    score = 50.0
    reasons: List[str] = []
    flags: List[str] = list(nz.get("quality_flags") or [])

    titulo = (record.get("titulo") or "").strip()
    link = record.get("link") or record.get("url") or record.get("link_oficial")
    desc = (record.get("descricao") or record.get("resumo") or "").strip()
    fonte = enr.get("fonte_normalizada") or record.get("fonte_recurso") or record.get("fonte")

    # Positivos
    if len(titulo) >= 25:
        score += 8
        reasons.append("titulo_claro")
    elif len(titulo) >= 12:
        score += 4
    else:
        score -= 8
        flags.append("titulo_curto")
        reasons.append("titulo_fraco")

    if link and str(link).startswith("http"):
        score += 10
        reasons.append("link_oficial")
    else:
        score -= 12
        flags.append("sem_link")
        reasons.append("sem_link")

    if fonte:
        score += 6
        reasons.append("fonte_identificada")

    if val_status in ("aberto", "vencendo_7", "vencendo_30"):
        score += 15
        reasons.append("prazo_estruturado_futuro")
    elif val_status == "encerrado":
        score += 5
        reasons.append("prazo_encerrado_conhecido")
    elif val_status == "sem_prazo" and nz.get("is_actionable_opportunity"):
        score -= 10
        flags.append("sem_prazo_acionavel")
        reasons.append("sem_prazo")
    elif val_status == "nao_aplicavel":
        score -= 5
        reasons.append("validade_nao_aplicavel")

    prazo_conf = enr.get("prazo_confidence") or record.get("prazo_confidence")
    if prazo_conf == "alta":
        score += 5
    elif prazo_conf == "baixa":
        score -= 5
        flags.append("prazo_baixa_confianca")

    mod = enr.get("modalidade_normalizada") or record.get("modalidade_normalizada")
    if mod and mod not in ("sem_classificacao", "outro", "desconhecido"):
        score += 6
        reasons.append("modalidade_clara")

    area = enr.get("area_tematica_normalizada") or record.get("area_tematica_normalizada")
    if area and area not in ("desconhecida", "outro", ""):
        score += 5
        reasons.append("area_tematica")

    tipo = enr.get("tipo_registro") or record.get("tipo_registro")
    if tipo in ("edital", "concurso"):
        score += 8
        reasons.append("tipo_registro_claro")

    if len(desc) >= 120:
        score += 8
        reasons.append("descricao_util")
    elif len(desc) < 40:
        score -= 6
        flags.append("descricao_fraca")

    # Negativos ruído
    if nz.get("is_noise"):
        score -= 25
        flags.append("provavel_ruido")
        reasons.append(f"ruido:{nz.get('noise_type')}")
    elif nz.get("noise_type") in ("resultado", "homologacao", "retificacao", "noticia"):
        score -= 15
        flags.append("tipo_ruido_parcial")
    if "titulo_generico" in flags:
        score -= 10
    if "link_invalido" in flags:
        score -= 15

    for f in enr.get("qualidade_flags") or []:
        if f in ("revisao_humana", "possivel_noticia_em_edital", "kind_desconhecido"):
            score -= 5
            if f not in flags:
                flags.append(f)

    score = max(0.0, min(100.0, score))

    if score >= 70:
        level = "alto"
    elif score >= 45:
        level = "medio"
    elif score >= 25:
        level = "baixo"
    else:
        level = "revisao"

    if nz.get("is_noise") or "provavel_ruido" in flags:
        level = "revisao" if level != "alto" else "baixo"

    return {
        "quality_score": int(round(score)),
        "quality_level": level,
        "quality_flags": sorted(set(flags)),
        "quality_reasons": sorted(set(reasons)),
    }
