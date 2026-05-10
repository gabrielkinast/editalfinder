#!/usr/bin/env python3
from __future__ import annotations

import os
import traceback
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
import sys

if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from db import get_safe_connection_diagnostics, test_read_connection  # noqa: E402


def _load_env() -> None:
    # Prioriza .env.staging quando existir; fallback para CORE/.env
    env_staging = ROOT / ".env.staging"
    env_core = ROOT / "CORE" / ".env"
    if env_staging.is_file():
        load_dotenv(dotenv_path=env_staging, override=False)
    if env_core.is_file():
        load_dotenv(dotenv_path=env_core, override=False)


def main() -> int:
    _load_env()
    diag = get_safe_connection_diagnostics()
    print(f"URL mascarada: {diag.get('url_masked')}")
    print(f"Chave presente: {diag.get('key_exists')}")
    print(f"Variável de chave escolhida: {diag.get('key_name_selected')}")
    print(f"Tamanho da chave: {diag.get('key_len')}")
    print(f"Prefixo mascarado da chave: {diag.get('key_prefix_masked')}")

    try:
        ok, err = test_read_connection()
        print(f"Conectou com sucesso: {ok}")
        if ok:
            print("Leitura retornou pelo menos 1 registro (ou tabela acessível).")
        else:
            print(f"Erro completo: {err}")
        return 0 if ok else 1
    except Exception:
        print("Conectou com sucesso: False")
        print("Erro completo:")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
