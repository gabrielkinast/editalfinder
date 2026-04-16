from db import supabase
import json

def diagnose_edital_table():
    print("--- DIAGNÓSTICO DA TABELA EDITAL ---")
    try:
        # Tenta selecionar tudo e ver se tem algo
        res = supabase.table("edital").select("*").execute()
        print(f"Número de registros: {len(res.data)}")
        if res.data:
            print(f"Colunas (keys do primeiro registro): {list(res.data[0].keys())}")
        else:
            print("Tabela vazia. Tentando obter nomes das colunas via inserção de erro.")
            try:
                # Inserindo com um campo inexistente para ver se o erro lista os campos válidos
                supabase.table("edital").insert({"campo_inexistente_teste": "valor"}).execute()
            except Exception as e:
                # A mensagem de erro costuma conter informações úteis
                print(f"Erro ao inserir campo inexistente: {e}")
                
    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    diagnose_edital_table()
