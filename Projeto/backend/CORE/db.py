import os
from typing import Any, Dict, Tuple
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega env nesta ordem (sem sobrescrever variáveis já exportadas no shell):
# 1) <repo>/.env.staging
# 2) <repo>/.env.local
# 3) <repo>/.env
# 4) <repo>/CORE/.env
ROOT = Path(__file__).resolve().parents[1]
ENV_CANDIDATES = [
    ROOT / ".env.staging",
    ROOT / ".env.local",
    ROOT / ".env",
    ROOT / "CORE" / ".env",
]
for p in ENV_CANDIDATES:
    if p.is_file():
        load_dotenv(dotenv_path=p, override=False)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY_NAME = ""
SUPABASE_KEY = None


def _non_empty(name: str) -> str:
    return os.getenv(name, "").strip()


def _choose_supabase_key() -> Tuple[str, str]:
    # Regra: SUPABASE_KEY -> SUPABASE_SERVICE_ROLE_KEY -> SUPABASE_ANON_KEY
    for name in ("SUPABASE_KEY", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_ANON_KEY"):
        val = _non_empty(name)
        if val:
            return name, val
    return "", ""


SUPABASE_KEY_NAME, SUPABASE_KEY = _choose_supabase_key()

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Variáveis de ambiente do Supabase não definidas.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def _mask_url(url: str) -> str:
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if len(host) <= 6:
            host_m = host[:1] + "***" + host[-1:]
        else:
            host_m = host[:3] + "***" + host[-3:]
        return f"{parsed.scheme}://{host_m}"
    except Exception:
        return "***"


def _mask_key_prefix(key: str) -> str:
    if not key:
        return ""
    if len(key) <= 6:
        return key[:2] + "***"
    return key[:3] + "***" + key[-2:]


def get_safe_connection_diagnostics() -> Dict[str, Any]:
    return {
        "url_masked": _mask_url(SUPABASE_URL or ""),
        "key_name_selected": SUPABASE_KEY_NAME,
        "key_exists": bool(SUPABASE_KEY),
        "key_len": len(SUPABASE_KEY or ""),
        "key_prefix_masked": _mask_key_prefix(SUPABASE_KEY or ""),
        "env_sources_found": [str(p) for p in ENV_CANDIDATES if p.is_file()],
    }


def test_read_connection() -> Tuple[bool, str]:
    try:
        _ = supabase.table("organizacao").select("*").limit(1).execute()
        return True, ""
    except Exception as exc:
        return False, str(exc)