#!/usr/bin/env python3
"""
Copia instalador NSIS (e opcionalmente portable) para releases/ com nomes padronizados.
Gera README_RELEASE e SHA256SUMS para distribuição manual.

Uso (após npm run desktop:build):
  python scripts/create_desktop_release.py
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND = REPO_ROOT / "frontend" / "EditalFinder-React"
TAURI_CONF = FRONTEND / "src-tauri" / "tauri.conf.json"
PACKAGE_JSON = FRONTEND / "package.json"
NSIS_DIR = FRONTEND / "src-tauri" / "target" / "release" / "bundle" / "nsis"
PORTABLE_EXE = FRONTEND / "src-tauri" / "target" / "release" / "editalfinder.exe"
RELEASES_DIR = REPO_ROOT / "releases"


def read_version() -> str:
    """Versão canônica: tauri.conf.json, depois package.json."""
    if TAURI_CONF.is_file():
        try:
            data = json.loads(TAURI_CONF.read_text(encoding="utf-8"))
            v = (data.get("version") or "").strip()
            if v:
                return v
        except (json.JSONDecodeError, OSError) as e:
            print(f"Aviso: não foi possível ler {TAURI_CONF}: {e}", file=sys.stderr)

    if PACKAGE_JSON.is_file():
        try:
            data = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
            v = (data.get("version") or "").strip()
            if v and v != "0.0.0":
                return v
        except (json.JSONDecodeError, OSError) as e:
            print(f"Aviso: não foi possível ler {PACKAGE_JSON}: {e}", file=sys.stderr)

    return "0.1.0"


def find_nsis_setup() -> Path | None:
    if not NSIS_DIR.is_dir():
        return None
    candidates = sorted(
        NSIS_DIR.glob("EditalFinder_*_x64-setup.exe"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    # fallback: qualquer setup.exe no diretório
    for p in sorted(NSIS_DIR.glob("*setup*.exe"), key=lambda x: x.stat().st_mtime, reverse=True):
        return p
    return None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_version_tag(version: str) -> str:
    return re.sub(r"[^\w.\-]", "_", version)


def write_readme_release(version: str, files: list[tuple[str, Path]]) -> Path:
    out = RELEASES_DIR / f"README_RELEASE_v{safe_version_tag(version)}.txt"
    lines = [
        f"EditalFinder v{version}",
        "",
        "Como instalar:",
        f"1. Execute EditalFinder_v{version}_Windows_x64_Setup.exe.",
        "2. Siga as instruções do instalador.",
        "3. Abra o EditalFinder pelo atalho criado.",
        "4. Entre com usuário e senha.",
        "5. O aplicativo precisa de internet para funcionar.",
        "",
        "Observação:",
        "Se o Windows mostrar aviso de segurança, isso pode ocorrer porque o instalador ainda não possui assinatura digital.",
        "",
        "Arquivos nesta release:",
    ]
    for label, path in files:
        size_mb = path.stat().st_size / (1024 * 1024)
        lines.append(f"  - {path.name} ({label}, {size_mb:.2f} MB)")
    lines.extend(
        [
            "",
            f"Gerado em: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
            "Atualização: manual — instale novamente quando houver versão nova.",
        ]
    )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def write_sha256sums(version: str, entries: list[tuple[Path, str]]) -> Path:
    out = RELEASES_DIR / f"SHA256SUMS_v{safe_version_tag(version)}.txt"
    lines = [f"# EditalFinder v{version} — SHA-256", ""]
    for path, digest in entries:
        lines.append(f"{digest}  {path.name}")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    version = read_version()
    tag = safe_version_tag(version)
    RELEASES_DIR.mkdir(parents=True, exist_ok=True)

    setup_src = find_nsis_setup()
    if not setup_src:
        print(
            "Erro: instalador NSIS não encontrado.\n"
            f"  Esperado em: {NSIS_DIR}\n"
            "  Rode antes: cd frontend/EditalFinder-React && npm run desktop:build",
            file=sys.stderr,
        )
        return 1

    setup_dst = RELEASES_DIR / f"EditalFinder_v{version}_Windows_x64_Setup.exe"
    shutil.copy2(setup_src, setup_dst)
    print(f"Setup copiado: {setup_dst}")

    copied: list[tuple[str, Path]] = [("instalador NSIS", setup_dst)]
    checksums: list[tuple[Path, str]] = [(setup_dst, sha256_file(setup_dst))]

    if PORTABLE_EXE.is_file():
        portable_dst = RELEASES_DIR / f"EditalFinder_v{version}_Windows_x64_Portable.exe"
        shutil.copy2(PORTABLE_EXE, portable_dst)
        print(f"Portable copiado: {portable_dst}")
        copied.append(("executável portable", portable_dst))
        checksums.append((portable_dst, sha256_file(portable_dst)))
    else:
        print(f"Aviso: portable não encontrado ({PORTABLE_EXE}); apenas setup copiado.")

    readme = write_readme_release(version, copied)
    sums = write_sha256sums(version, checksums)
    print(f"README: {readme}")
    print(f"SHA256: {sums}")
    print("\nHashes SHA-256:")
    for path, digest in checksums:
        print(f"  {digest}  {path.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
