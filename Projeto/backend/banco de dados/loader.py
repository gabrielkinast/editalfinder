import json
import importlib
from core.db import supabase
from core.schema import normalizar


def get_transformer(fonte):
    try:
        module = importlib.import_module(f"core.transformers.{fonte}")
        return module.transformar
    except ModuleNotFoundError:
        print(f"[ERRO] Transformer não encontrado para: {fonte}")
        return None


def ja_existe(link):
    response = supabase.table("editais") \
        .select("id") \
        .eq("link", link) \
        .execute()

    return len(response.data) > 0


def inserir_edital(edital):
    try:
        supabase.table("editais").insert(edital).execute()
    except Exception as e:
        print(f"[ERRO INSERT] {e}")


def load_json_to_db(file_path, fonte):
    transform = get_transformer(fonte)

    if not transform:
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    for item in data:
        try:
            transformado = transform(item)

            if not transformado.get("link"):
                print("[IGNORADO] Sem link")
                continue

            if ja_existe(transformado["link"]):
                print("[DUPLICADO]", transformado["link"])
                continue

            normalizado = normalizar(transformado)

            inserir_edital(normalizado)

            print("[OK]", normalizado["titulo"])

        except Exception as e:
            print(f"[ERRO PROCESSAMENTO] {e}")