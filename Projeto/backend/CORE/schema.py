from datetime import datetime

from merge_utils import sanitize_for_postgres


def parse_date(date_str):
    if not date_str:
        return None

    try:
        return datetime.fromisoformat(date_str).date().isoformat()
    except Exception:
        return None


def modelo_base():
    return {
        "titulo": None,
        "descricao": None,
        "link": None,
        "fonte": None,
        "data_publicacao": None,
        "fim_inscricao": None,
        "situacao": None,
        "valor": None,
        "valor_minimo": None,
        "contrapartida": None,
        "elegibilidade": None,
        "contato": None,
        "link_inscricao": None,
        "ods": None,
        "programa": None,
        "acao": None,
        "tipo_recurso": None,
        "regiao": None,
        "publico_alvo": None,
        "temas": None,
        "score": 0,
        "score_detalhado": {}, # Novo campo: componentes do score
        "justificativa": None, # Novo campo: motivo do ranking
        "recomendacao": None,
        "compatibilidade": {}, 
        "extras": {}
    }


def normalizar(item_transformado):
    base = modelo_base()
    known = set(base.keys())
    # Campos fora do modelo base são preservados dentro de extras (não perdem no ETL).
    orphan = {}
    if isinstance(item_transformado, dict):
        for k, v in item_transformado.items():
            if k not in known:
                orphan[k] = v

    for key in base:
        if key in item_transformado:
            base[key] = item_transformado[key]

    if orphan:
        ex = base.get("extras")
        if not isinstance(ex, dict):
            ex = {}
        for k, v in orphan.items():
            if k == "extras" and isinstance(v, dict):
                ex = {**v, **ex}
            else:
                ex.setdefault(k, v)
        base["extras"] = ex

    # normalização de datas
    base["data_publicacao"] = parse_date(base["data_publicacao"])
    base["fim_inscricao"] = parse_date(base["fim_inscricao"])

    return sanitize_for_postgres(base)