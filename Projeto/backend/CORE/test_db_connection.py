from db import supabase
import json

def test_connection():
    print("Testando conexão com Supabase...")
    try:
        # Tenta selecionar o primeiro item da tabela edital
        response = supabase.table("edital").select("*").limit(1).execute()
        print(f"Conexão OK! {len(response.data)} itens encontrados.")
        if response.data:
            print(f"Primeiro item: {response.data[0].get('titulo', 'Sem título')}")
    except Exception as e:
        print(f"Erro na conexão: {e}")

def test_manual_insert():
    print("\nTestando inserção manual...")
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
        # Verifica se já existe antes de inserir
        check = supabase.table("edital").select("id").eq("link", test_item["link"]).execute()
        if check.data:
            print("Item de teste já existe. Deletando para re-inserir...")
            supabase.table("edital").delete().eq("link", test_item["link"]).execute()

        response = supabase.table("edital").insert(test_item).execute()
        print(f"Inserção OK! Response data: {response.data}")
        
        # Confirma se o item foi realmente inserido
        confirm = supabase.table("edital").select("*").eq("link", test_item["link"]).execute()
        if confirm.data:
            print(f"Confirmação: Item encontrado no banco com ID {confirm.data[0]['id']}")
        else:
            print("AVISO: Item NÃO encontrado após inserção!")
            
    except Exception as e:
        print(f"Erro na inserção: {e}")

if __name__ == "__main__":
    test_connection()
    test_manual_insert()
