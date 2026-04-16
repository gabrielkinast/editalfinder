from db import supabase
import json

def create_minimal_org():
    print("Criando organização mínima padrão...")
    try:
        # Tenta com nome
        response = supabase.table("organizacao").insert({"nome": "ORGANIZACAO_TESTE"}).execute()
        print(f"Sucesso! Org criada: {response.data}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    create_minimal_org()
