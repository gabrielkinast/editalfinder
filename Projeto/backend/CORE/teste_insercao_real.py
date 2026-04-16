from db import supabase
import json

def test_real_insert():
    print("\n--- TESTE DE INSERÇÃO REAL ---")
    test_item = {
        "titulo": "TESTE DE CONEXÃO AGENTE",
        "descricao": "Edital de teste inserido pelo agente via script de diagnóstico.",
        "link": "https://teste-agente.com.br",
        "fonte_recurso": "AGENTE_DIAGNOSTICO",
        "data_publicacao": "2026-03-24",
        "prazo_envio": "2026-12-31",
        "situacao": "Teste",
        "pdf_url": "https://teste-agente.com.br/edital.pdf",
        "status": "Ativo",
        "id_organizacao": 2
    }
    
    try:
        # Tenta inserir
        print(f"Inserindo: {test_item['titulo']}")
        response = supabase.table("edital").insert(test_item).execute()
        print(f"Sucesso! Data: {response.data}")
        
        # Confirma
        res = supabase.table("edital").select("*").eq("link", test_item["link"]).execute()
        if res.data:
            print(f"Confirmação: Encontrado registro com ID {res.data[0].get('id_edital', 'desconhecido')}")
            # Se encontrou, vamos ver todas as chaves
            print(f"Todas as colunas reais: {list(res.data[0].keys())}")
        else:
            print("AVISO: Registro não encontrado após inserção!")
            
    except Exception as e:
        print(f"ERRO NA INSERÇÃO: {e}")

if __name__ == "__main__":
    test_real_insert()
