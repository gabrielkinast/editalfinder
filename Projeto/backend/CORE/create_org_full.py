from db import supabase
import json

def create_org_full():
    print("Criando organização completa...")
    try:
        response = supabase.table("organizacao").insert({
            "nome": "ORG_PADRAO", 
            "tipo": "OUTRO", 
            "país": "Brasil"
        }).execute()
        print(f"Sucesso! Org: {response.data}")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    create_org_full()
