"""Heurísticas leves para fontes públicas BR (BNDES, CNPq, Finep, Aneel).

Aplica-se após enrich_opportunity_classification: preenche lacunas sem sobrescrever listas já preenchidas.
"""
from __future__ import annotations

from typing import Any, Dict, List

_BR_SOURCES = frozenset({"aneel", "bndes", "cnpq", "finep", "capes", "mcti"})


def _norm_source(source_name: str, item: Dict[str, Any]) -> str:
    s = (source_name or "").lower()
    if s in _BR_SOURCES:
        return s
    f = str(item.get("fonte") or "").upper()
    for k in _BR_SOURCES:
        if k.upper() in f:
            return k
    return s


def _blob(item: Dict[str, Any]) -> str:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    parts = [
        str(item.get("titulo") or ""),
        str(item.get("descricao") or ""),
        str(item.get("programa") or ""),
        str(item.get("acao") or ""),
        str(item.get("link") or ""),
        str(ex.get("objetivo") or ""),
    ]
    return " ".join(parts).lower()


def _merge_extras_list(extras: Dict[str, Any], key: str, values: List[str]) -> None:
    cur = extras.get(key)
    if isinstance(cur, str) and cur.strip():
        cur = [cur.strip()]
    if isinstance(cur, list) and len(cur) > 0:
        return
    if values:
        extras[key] = values


def _has_any(blob: str, terms: List[str]) -> bool:
    return any(t in blob for t in terms)


def apply_br_public_source_hints(item: Dict[str, Any], source_name: str) -> None:
    """Preenche area/tipo_oportunidade/tipo_recurso/perfil_ideal quando vazios."""
    src = _norm_source(source_name, item)
    if src not in _BR_SOURCES:
        return
    extras = item.get("extras")
    if not isinstance(extras, dict):
        extras = {}
        item["extras"] = extras
    blob = _blob(item)
    link = str(item.get("link") or "").lower()

    if src == "aneel":
        _merge_extras_list(extras, "area", ["Energia"])
        _merge_extras_list(extras, "setor_economico", ["energia"])
        if _has_any(blob, ["p&d", "pesquisa", "inovacao", "inovação", "eficiencia", "eficiência", "rede eletrica"]):
            _merge_extras_list(extras, "area_tecnologica", ["regulação e mercado de energia", "P&D setor elétrico"])
        if not extras.get("tipo_oportunidade") and any(
            x in blob for x in ("licit", "pregão", "pregao", "compra", "contratação", "contratacao")
        ):
            extras["tipo_oportunidade"] = "licitação"
        elif not extras.get("tipo_oportunidade"):
            extras["tipo_oportunidade"] = "programa"
        if item.get("tipo_recurso") in (None, "", "Não Especificado"):
            if any(x in blob for x in ("p&d", "pdi", "pesquisa", "desenvolvimento", "inovação", "inovacao")):
                item["tipo_recurso"] = "fomento"
            elif any(x in blob for x in ("eficiência", "eficiencia", "energia", "tarifa")):
                item["tipo_recurso"] = "fomento"
        _merge_extras_list(extras, "setor_estrategico", ["energia"])
        if not extras.get("perfil_ideal") and _has_any(blob, ["empresa", "fornecedor", "concessionaria", "distribuidora"]):
            extras["perfil_ideal"] = "empresa"
        if _has_any(blob, ["empresa", "fornecedor", "concessionaria", "distribuidora"]):
            _merge_extras_list(extras, "publico_alvo", ["empresas"])

    elif src == "bndes":
        _merge_extras_list(extras, "area", ["Indústria"])
        _merge_extras_list(extras, "setor_economico", ["indústria", "crédito e financiamento"])
        if _has_any(blob, ["inovacao", "inovação", "industrial", "tecnologia"]):
            _merge_extras_list(extras, "area_tecnologica", ["financiamento produtivo", "inovação industrial"])
        if not extras.get("tipo_oportunidade"):
            extras["tipo_oportunidade"] = "chamada_publica"
        if item.get("tipo_recurso") in (None, "", "Não Especificado"):
            item["tipo_recurso"] = "financiamento"
        if _has_any(blob, ["tecnologia", "inovacao", "inovação", "p&d"]):
            _merge_extras_list(extras, "setor_estrategico", ["ciencia_tecnologia"])
        if not extras.get("perfil_ideal") and _has_any(blob, ["empresa", "cnpj", "industria", "indústria", "capital de giro"]):
            extras["perfil_ideal"] = "empresa"
        if _has_any(blob, ["empresa", "cnpj", "industria", "indústria"]):
            _merge_extras_list(extras, "publico_alvo", ["empresas", "industria"])

    elif src == "cnpq":
        _merge_extras_list(extras, "area", ["Educação e pesquisa"])
        _merge_extras_list(extras, "setor_economico", ["ciência e tecnologia"])
        if _has_any(blob, ["pesquisa", "cient", "laboratorio", "laboratório", "universidade", "ict"]):
            _merge_extras_list(extras, "area_cientifica", ["pesquisa científica"])
        if not extras.get("tipo_oportunidade"):
            extras["tipo_oportunidade"] = "chamada_publica" if "chamada" in blob else "edital"
        if item.get("tipo_recurso") in (None, "", "Não Especificado"):
            item["tipo_recurso"] = "fomento"
        if not extras.get("perfil_ideal") and _has_any(blob, ["pesquisador", "docente", "universidade", "ict", "bolsa"]):
            extras["perfil_ideal"] = "pesquisador"
        if _has_any(blob, ["pesquisador", "docente", "universidade", "ict", "bolsa"]):
            _merge_extras_list(extras, "publico_alvo", ["pesquisadores", "universidades", "ICTs"])

    elif src == "finep":
        _merge_extras_list(extras, "area", ["Tecnologia e inovação"])
        _merge_extras_list(extras, "setor_economico", ["inovação", "fomento à pesquisa"])
        if _has_any(blob, ["p&d", "pd&i", "inovacao", "inovação", "subvencao", "subvenção", "tecnologia"]):
            _merge_extras_list(extras, "area_tecnologica", ["PD&I", "subvenção econômica"])
        if not extras.get("tipo_oportunidade"):
            extras["tipo_oportunidade"] = "chamada_publica"
        if item.get("tipo_recurso") in (None, "", "Não Especificado"):
            item["tipo_recurso"] = "fomento"
        if not extras.get("perfil_ideal") and _has_any(blob, ["empresa", "startup", "ict", "subvencao", "subvenção"]):
            extras["perfil_ideal"] = "empresa"
        if _has_any(blob, ["empresa", "startup", "ict", "subvencao", "subvenção"]):
            _merge_extras_list(extras, "publico_alvo", ["empresas", "ICTs", "startups"])

    if link.endswith(".pdf") or "/chamadas" in link or "chamadas-publicas" in link:
        ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
        if not ex.get("pdf_url") and link.endswith(".pdf"):
            ex["pdf_url"] = item.get("link")
        docs = ex.get("documentos")
        if not docs and link.endswith(".pdf"):
            ex["documentos"] = [{"nome": "Documento PDF", "url": item.get("link")}]
        ex.setdefault("metodo_classificacao", "br_public_hints")
        item["extras"] = ex
