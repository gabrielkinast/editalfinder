"""Contrato único de saída do pipeline de transformação (EditalFinder)."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TransformResult:
    """Resultado por item: payload aceito, rejeição documentada ou avisos."""

    payload: Optional[Dict[str, Any]]
    rejected: bool
    rejection_reason: str
    warnings: List[str] = field(default_factory=list)
    report_delta: Dict[str, Any] = field(default_factory=dict)
    original_item: Optional[Dict[str, Any]] = None
    content_type_detectado: str = "desconhecido"
    sinais_detectados: List[str] = field(default_factory=list)

    def to_rejected_record(self) -> Dict[str, Any]:
        """Formato para outputs/rejected/transformer_rejected_<fonte>.json."""
        oi = self.original_item if isinstance(self.original_item, dict) else {}
        pl = self.payload if isinstance(self.payload, dict) else {}
        return {
            "titulo": pl.get("titulo") or oi.get("titulo") or "",
            "link": pl.get("link") or oi.get("link") or oi.get("url") or "",
            "fonte": pl.get("fonte") or oi.get("fonte") or "",
            "motivo_descarte": self.rejection_reason or ("rejected" if self.rejected else ""),
            "content_type_detectado": self.content_type_detectado,
            "sinais_detectados": list(self.sinais_detectados),
            "validacao_warnings": list(self.warnings),
            "item_original": deepcopy(oi) if oi else {},
        }


@dataclass
class TransformBatchResult:
    """Lote por fonte: itens aceitos, rejeitados e relatório agregado."""

    items: List[Dict[str, Any]]
    rejected: List[Dict[str, Any]]
    report: Dict[str, Any]


def new_batch_report(fonte: str) -> Dict[str, Any]:
    return {
        "fonte": fonte,
        "recebidos": 0,
        "transformados": 0,
        "descartados": 0,
        "incompletos": 0,
        "suspeitos": 0,
        "official_link_only": 0,
        "acesso_limitados": 0,
        "content_type_counts": {},
        "motivos_descarte": {},
        "campos_vazios_mais_comuns": {},
        "qualidade_media": None,
        "_qualidade_soma": 0,
        "_qualidade_n": 0,
    }


def merge_report_delta(report: Dict[str, Any], tr: TransformResult) -> None:
    report["recebidos"] = report.get("recebidos", 0) + 1
    if tr.rejected or not tr.payload:
        report["descartados"] = report.get("descartados", 0) + 1
        key = tr.rejection_reason or "sem_motivo"
        md = report.setdefault("motivos_descarte", {})
        md[key] = md.get(key, 0) + 1
        return
    report["transformados"] = report.get("transformados", 0) + 1
    ex = tr.payload.get("extras") if isinstance(tr.payload.get("extras"), dict) else {}
    ct = str(tr.payload.get("content_type") or ex.get("content_type") or tr.content_type_detectado or "desconhecido")
    ctc = report.setdefault("content_type_counts", {})
    ctc[ct] = ctc.get(ct, 0) + 1
    if ex.get("extraction_mode") == "official_link_only":
        report["official_link_only"] = report.get("official_link_only", 0) + 1
    st = ex.get("validacao_status")
    if st == "incompleto":
        report["incompletos"] = report.get("incompletos", 0) + 1
    elif st == "suspeito":
        report["suspeitos"] = report.get("suspeitos", 0) + 1
    elif st == "acesso_limitado":
        report["acesso_limitados"] = report.get("acesso_limitados", 0) + 1
    q = ex.get("qualidade_dado")
    if isinstance(q, (int, float)):
        report["_qualidade_soma"] = report.get("_qualidade_soma", 0) + float(q)
        report["_qualidade_n"] = report.get("_qualidade_n", 0) + 1
    for k in ("fim_inscricao", "valor", "descricao", "tipo_recurso", "publico_alvo", "data_publicacao"):
        v = tr.payload.get(k) if k != "publico_alvo" else tr.payload.get(k) or ex.get("publico_alvo")
        if k == "tipo_recurso" and v in (None, "", "Não Especificado"):
            cv = report.setdefault("campos_vazios_mais_comuns", {})
            cv[k] = cv.get(k, 0) + 1
        elif k != "tipo_recurso" and (v is None or (isinstance(v, str) and not v.strip())):
            cv = report.setdefault("campos_vazios_mais_comuns", {})
            cv[k] = cv.get(k, 0) + 1


def finalize_batch_report(report: Dict[str, Any]) -> Dict[str, Any]:
    n = report.pop("_qualidade_n", 0) or 0
    s = report.pop("_qualidade_soma", 0) or 0
    if n:
        report["qualidade_media"] = round(s / n, 2)
    else:
        report["qualidade_media"] = None
    return report
