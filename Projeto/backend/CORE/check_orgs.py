from db import supabase
import json

def list_organizations():
    print("Listando organizações cadastradas...")
    try:
        response = supabase.table("organizacao").select("*").execute()
        print(f"Número de organizações: {len(response.data)}")
        for org in response.data:
            print(f"ID: {org.get('id') or org.get('id_organizacao')} | Nome: {org.get('nome')}")
    except Exception as e:
        print(f"Erro ao listar organizações: {e}")

if __name__ == "__main__":
    list_organizations()
