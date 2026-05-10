import os
from pathlib import Path
from db import supabase
from log_utils import get_logger

logger = get_logger("migration_runner")
MIGRATION_FILE = Path(__file__).parent / "migration_consolidar_status.sql"

def run_sql_via_rpc(sql_text: str) -> bool:
    """Tenta executar o SQL através de uma função RPC no Postgres (exec_sql)."""
    # Nota: No Supabase, você precisa criar uma função SQL para executar SQL arbitrário
    # create or replace function exec_sql(sql text) returns void as $$
    # begin execute sql; end;
    # $$ language plpgsql security definer;
    
    rpc_candidates = ("exec_sql", "sql", "run_sql")
    for rpc_name in rpc_candidates:
        try:
            supabase.rpc(rpc_name, {"sql": sql_text}).execute()
            logger.info(f"SQL executado com sucesso via RPC '{rpc_name}'.")
            return True
        except Exception as exc:
            logger.debug(f"RPC '{rpc_name}' falhou ou indisponível: {exc}")
    return False

def main():
    migration_files = [
        "migration_consolidar_status.sql",
        "migration_org_profiles.sql"
    ]
    
    for filename in migration_files:
        migration_path = Path(__file__).parent / filename
        if not migration_path.exists():
            print(f"Erro: Arquivo de migração não encontrado em {migration_path}")
            continue

        print(f"\nLendo migração: {filename}")
        sql_text = migration_path.read_text(encoding="utf-8")
        
        print(f"Tentando executar '{filename}' no Supabase...")
        if run_sql_via_rpc(sql_text):
            print(f"Migração '{filename}' executada com sucesso!")
        else:
            print("\n" + "="*50)
            print(f"AVISO: Não foi possível executar '{filename}' via RPC.")
            print("EXECUTE MANUALMENTE NO SQL EDITOR DO SUPABASE:")
            print(f"Arquivo: {migration_path.absolute()}")
            print("="*50 + "\n")

if __name__ == "__main__":
    main()
