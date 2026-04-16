from pathlib import Path

from db import supabase
from log_utils import get_logger


logger = get_logger("setup_database")
SQL_FILE = Path(__file__).parent / "schema_json_tables.sql"


def run_sql_via_rpc(sql_text: str) -> bool:
    """Try to execute SQL through a Postgres RPC function."""
    rpc_candidates = ("exec_sql", "sql", "run_sql")
    for rpc_name in rpc_candidates:
        try:
            supabase.rpc(rpc_name, {"sql": sql_text}).execute()
            logger.info("SQL executado via RPC '%s'.", rpc_name)
            return True
        except Exception as exc:
            logger.warning("RPC '%s' indisponível: %s", rpc_name, exc)
    return False


def main():
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"Arquivo SQL não encontrado: {SQL_FILE}")

    sql_text = SQL_FILE.read_text(encoding="utf-8")
    if run_sql_via_rpc(sql_text):
        print("Tabelas auxiliares criadas/validadas com sucesso.")
    else:
        print("Não foi possível executar SQL automaticamente via RPC.")
        print(f"Execute manualmente o conteúdo de: {SQL_FILE}")


if __name__ == "__main__":
    main()
