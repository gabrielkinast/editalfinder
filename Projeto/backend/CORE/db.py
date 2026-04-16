from supabase import create_client, Client
import os
from dotenv import load_dotenv
from pathlib import Path

# Carrega o .env da mesma pasta que este arquivo (CORE/)
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(f"Variáveis de ambiente do Supabase não definidas em {env_path}")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)