from db import supabase
import json

def create_default_org():
    print("Criando organização padrão...")
    default_org = {
        "id": 1,
        "nome": "ONG CADASTRADA (PADRÃO)",
        "descricao": "Organização padrão para novos editais."
    }
    
    try:
        # Tenta inserir
        response = supabase.table("organizacao").insert(default_org).execute()
        print(f"Sucesso ao criar organização! Data: {response.data}")
    except Exception as e:
        # Se falhar porque já existe ou id é serial
        print(f"Erro ao criar organização: {e}")
        try:
            # Tenta sem o ID se for serial
            default_org_no_id = {
                "nome": "ONG CADASTRADA (PADRÃO)",
                "descricao": "Organização padrão para novos editais."
            }
            response = supabase.table("organizacao").insert(default_org_no_id).execute()
            print(f"Sucesso ao criar organização (sem ID manual): {response.data}")
        except Exception as e2:
            print(f"Erro final: {e2}")

if __name__ == "__main__":
    create_default_org()
