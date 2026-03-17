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