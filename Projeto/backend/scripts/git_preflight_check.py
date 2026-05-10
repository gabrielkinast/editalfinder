#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pré-voo antes de git add: verifica .gitignore e procura padrões de segredos em ficheiros
candidatos a versionar. Não altera o repositório; não imprime valores de secrets.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "audit_reports_main_pipeline" / "git_preflight_check.json"
OUT_MD = ROOT / "audit_reports_main_pipeline" / "git_preflight_check.md"
GITIGNORE = ROOT / ".gitignore"

MAX_FILE_BYTES = 512_000
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip", ".7z", ".gz", ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3", ".bin", ".exe", ".dll", ".so", ".dylib"}

# Padrões (linha ou contexto); não capturar valores completos no relatório.
SECRET_PATTERNS: List[Tuple[str, re.Pattern]] = [
    ("SUPABASE_SERVICE_ROLE_KEY", re.compile(r"SUPABASE_SERVICE_ROLE_KEY", re.I)),
    ("SERVICE_ROLE", re.compile(r"(?<!#)\bSERVICE_ROLE\b", re.I)),
    ("SUPABASE_URL", re.compile(r"SUPABASE_URL\s*=", re.I)),
    ("SUPABASE_KEY", re.compile(r"SUPABASE_KEY\s*=", re.I)),
    ("API_KEY", re.compile(r"API_KEY\s*=", re.I)),
    ("TOKEN", re.compile(r"(?<!#)\bTOKEN\s*=", re.I)),
    ("SECRET", re.compile(r"(?<!#)\bSECRET\s*=", re.I)),
    ("PASSWORD", re.compile(r"PASSWORD\s*=", re.I)),
    ("JWT", re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_.-]{10,}", re.I)),
    ("Bearer", re.compile(r"Bearer\s+[a-zA-Z0-9._-]{12,}", re.I)),
    ("anon_key_hint", re.compile(r"SUPABASE_ANON_KEY\s*=", re.I)),
    ("BEGIN_PRIVATE", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
]


def _git_ok(cwd: Path) -> bool:
    try:
        subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except Exception:
        return False


def _read_gitignore_patterns() -> List[str]:
    if not GITIGNORE.is_file():
        return []
    lines: List[str] = []
    for raw in GITIGNORE.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        lines.append(s)
    return lines


def _path_matches_gitignore(rel_posix: str, patterns: List[str]) -> bool:
    """Aproximação de exclusão (fnmatch); suficiente para pré-voo."""
    rel = rel_posix.replace("\\", "/")
    for pat in patterns:
        if pat.endswith("/"):
            if fnmatch.fnmatch(rel + "/", pat + "*") or any(
                fnmatch.fnmatch(seg + "/", pat) for seg in _prefixes(rel)
            ):
                return True
            if fnmatch.fnmatch(rel.split("/")[0] + "/", pat) and rel.startswith(pat.rstrip("/")):
                return True
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel.split("/")[-1], pat):
            return True
        if "/" not in pat and pat in rel.split("/"):
            return True
    return False


def _prefixes(rel: str) -> List[str]:
    parts = rel.split("/")
    return ["/".join(parts[: i + 1]) for i in range(len(parts))]


def _list_candidate_files_git(root: Path) -> Set[Path]:
    out: Set[Path] = set()
    for cmd in (
        ["git", "-C", str(root), "ls-files", "-z"],
        ["git", "-C", str(root), "ls-files", "-o", "--exclude-standard", "-z"],
    ):
        try:
            p = subprocess.run(cmd, capture_output=True, check=False)
            if p.returncode != 0:
                continue
            for rel in p.stdout.decode("utf-8", errors="replace").split("\0"):
                if rel.strip():
                    out.add((root / rel).resolve())
        except Exception:
            continue
    return out


def _walk_fallback(root: Path, patterns: List[str]) -> Set[Path]:
    skip_dirs = {
        ".git",
        ".venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".idea",
        ".vscode",
        ".cursor",
    }
    found: Set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(root):
        dp = Path(dirpath)
        parts = set(dp.parts)
        if ".git" in parts:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        rel_dir = dp.relative_to(root).as_posix() if dp != root else ""
        for name in filenames:
            p = dp / name
            rel = f"{rel_dir}/{name}".lstrip("/") if rel_dir else name
            if _path_matches_gitignore(rel, patterns):
                continue
            if p.is_file():
                found.add(p.resolve())
    return found


def _mask_line(line: str, max_show: int = 72) -> str:
    s = line.strip()
    if len(s) > max_show:
        s = s[: max_show - 3] + "..."
    # Atribuições: manter chave, ocultar valor
    m = re.match(r"^(\s*[#]?\s*)([A-Za-z0-9_.-]+)(\s*=\s*)(.*)$", s)
    if m:
        prefix, key, eq, _val = m.groups()
        return f"{prefix}{key}{eq}<REDACTED>"
    if re.search(r"Bearer\s+", s, re.I):
        return re.sub(r"(Bearer\s+)(\S+)", r"\1<REDACTED>", s, flags=re.I)
    if re.search(r"eyJ", s):
        return "<REDACTED_JWT_LIKE>"
    return "<REDACTED_LINE>"


def _scan_file(path: Path) -> List[Dict[str, Any]]:
    suf = path.suffix.lower()
    if suf in SKIP_EXTENSIONS:
        return []
    try:
        st = path.stat()
        if st.st_size > MAX_FILE_BYTES:
            return []
    except OSError:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    hits: List[Dict[str, Any]] = []
    for i, line in enumerate(text.splitlines(), 1):
        for label, rx in SECRET_PATTERNS:
            if rx.search(line):
                hits.append(
                    {
                        "pattern": label,
                        "line": i,
                        "masked": _mask_line(line),
                    }
                )
                break
    return hits


def _gitignore_covers(patterns: List[str], needles: Iterable[str]) -> Dict[str, bool]:
    out: Dict[str, bool] = {}
    for n in needles:
        out[n] = any(_path_matches_gitignore(n, patterns) for _ in [0]) or _path_matches_gitignore(n, patterns)
    return out


def main() -> int:
    patterns = _read_gitignore_patterns()
    git_present = _git_ok(ROOT)

    needles = {
        ".env": ".env",
        "CORE/.env": "CORE/.env",
        ".venv/": ".venv/x",
        "CORE/.venv/": "CORE/.venv/x",
    }
    ignore_checks = {k: _path_matches_gitignore(v, patterns) for k, v in needles.items()}

    if git_present:
        candidates = _list_candidate_files_git(ROOT)
    else:
        candidates = _walk_fallback(ROOT, patterns)

    suspicious: List[Dict[str, Any]] = []
    scanned = 0
    for p in sorted(candidates, key=lambda x: str(x).lower()):
        try:
            rel = p.relative_to(ROOT).as_posix()
        except ValueError:
            continue
        if p.is_dir():
            continue
        scanned += 1
        for h in _scan_file(p):
            suspicious.append({"file": rel, **h})

    risk = "low"
    if suspicious:
        risk = "high" if len(suspicious) > 5 else "medium"

    summary: Dict[str, Any] = {
        "git_repository_detected": git_present,
        "gitignore_path": str(GITIGNORE.relative_to(ROOT)).replace("\\", "/"),
        "gitignore_exists": GITIGNORE.is_file(),
        "ignore_rules_count": len(patterns),
        "ignore_coverage": ignore_checks,
        "files_scanned_estimate": scanned,
        "suspicious_hits_count": len(suspicious),
        "risk_before_git_add": risk,
        "suspicious": suspicious[:200],
        "truncated": len(suspicious) > 200,
        "safe_git_add_examples": [
            "git add .gitignore",
            "git add scripts/",
            "git add CORE/",
            "git add main.py",
            "git add docs/",
            "# Evitar: git add . ou git add -A sem rever o status depois de atualizar .gitignore",
            "# Preferir: git add -p   ou   git add caminhos explícitos",
        ],
        "nota": "Valores de segredos não são reproduzidos; apenas padrão e linha mascarada.",
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Git — pré-voo (preflight)",
        "",
        f"- Repositório Git detetado: **{git_present}**",
        f"- `.gitignore` presente: **{GITIGNORE.is_file()}** (regras: {len(patterns)})",
        "",
        "## Cobertura de exclusão (amostra)",
        "",
        "| Caminho | Coberto por `.gitignore` |",
        "|---------|---------------------------|",
    ]
    for k, v in ignore_checks.items():
        md_lines.append(f"| `{k}` | **{v}** |")
    md_lines.extend(
        [
            "",
            "## Risco antes de `git add`",
            "",
            f"- **{risk}** (`suspicious_hits_count={len(suspicious)}`, ficheiros analisados ≈ {scanned})",
            "",
            "## Ficheiros com padrões sensíveis (mascarados)",
            "",
        ]
    )
    if not suspicious:
        md_lines.append("- Nenhum acerto nos padrões procurados (ou nenhum ficheiro candidato).")
    else:
        for item in suspicious[:80]:
            md_lines.append(
                f"- `{item['file']}` — linha {item['line']} — `{item['pattern']}` — `{item['masked']}`"
            )
        if len(suspicious) > 80:
            md_lines.append(f"\n… mais {len(suspicious) - 80} entradas (ver JSON).")
    md_lines.extend(
        [
            "",
            "## Comandos seguros sugeridos",
            "",
            "```text",
            "git status",
            "git add .gitignore",
            "git add scripts/git_preflight_check.py",
            "git add -p",
            "```",
            "",
            "Evitar `git add .` imediato após mudar `.gitignore` sem rever `git status`.",
            "",
        ]
    )
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    print(str(OUT_JSON.resolve()))
    print(str(OUT_MD.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
