from datetime import datetime

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
        "estado": None,
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

    for key in base:
        if key in item_transformado:
            base[key] = item_transformado[key]

    # normalização de datas
    base["data_publicacao"] = parse_date(base["data_publicacao"])
    base["fim_inscricao"] = parse_date(base["fim_inscricao"])

    return base