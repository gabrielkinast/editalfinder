from db import supabase
import json

def list_columns():
    print("Tentando descobrir colunas da tabela edital...")
    try:
        # Tenta inserir um item vazio para forçar um erro que pode listar colunas faltando ou inválidas
        response = supabase.table("edital").insert({}).execute()
        print(f"Response: {response.data}")
    except Exception as e:
        print(f"Erro esperado ao inserir vazio: {e}")

def check_one_row():
    try:
        # Se houver qualquer dado, veremos as chaves
        response = supabase.table("edital").select("*").limit(1).execute()
        if response.data:
            print(f"Colunas encontradas (pelas chaves do primeiro item): {list(response.data[0].keys())}")
        else:
            print("Tabela está vazia. Não é possível inferir colunas via select.")
    except Exception as e:
        print(f"Erro ao selecionar: {e}")

if __name__ == "__main__":
    check_one_row()
    list_columns()
