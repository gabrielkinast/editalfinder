"""Gravação segura de outputs de crawlers (evita sobrescrever JSON útil com []).

Não altera Supabase nem loader. Uso típico: falha de rede/listagem → preservar
`*_editais.json` anterior e registrar relatório de falha.
"""

from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

CONFIRMED_EMPTY_REASON = "confirmed_no_items"

ROOT = Path(__file__).resolve().parent
FAILURES_DIR = ROOT / "audit_reports_crawler_failures"


@dataclass
class SaveOutputResult:
    """Resultado de save_output_safely."""

    status: str  # saved | preserved_failure | saved_empty_confirmed | no_op
    source_name: str
    output_path: Path
    message: str
    wrote_file: bool = False
    preserved_previous: bool = False
    backup_path: Optional[Path] = None
    suggested_exit_code: int = 0
    failure_kind: Optional[str] = None  # falha_de_coleta | coleta_vazia_sem_confirmacao | ...


def _load_json_array(path: Path) -> Optional[List[Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return raw
        if isinstance(raw, dict):
            return [raw]
    except Exception:
        pass
    return None


def _backup_existing_editais(output_path: Path, source_name: str) -> Optional[Path]:
    if not output_path.is_file():
        return None
    try:
        if output_path.stat().st_size == 0:
            return None
    except OSError:
        return None
    backups = output_path.parent / "backups"
    backups.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S", time.gmtime())
    dest = backups / f"{source_name}_editais_{stamp}.json"
    shutil.copy2(output_path, dest)
    return dest


def _append_failure_log(source_name: str, record: Dict[str, Any]) -> Path:
    FAILURES_DIR.mkdir(parents=True, exist_ok=True)
    log_path = FAILURES_DIR / "failures.jsonl"
    line = dict(record)
    line.setdefault("ts_utc", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    line.setdefault("source_name", source_name)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return log_path


def _write_latest_error(output_dir: Path, payload: Dict[str, Any]) -> Path:
    p = output_dir / "latest_error.json"
    p.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def save_output_safely(
    items: List[Dict[str, Any]],
    output_path: Path,
    source_name: str,
    *,
    allow_empty: bool = False,
    failure_reason: Optional[str] = None,
    empty_confirmed_reason: Optional[str] = None,
    collection_failed: bool = False,
    listing_events: Optional[List[Dict[str, Any]]] = None,
    extra_context: Optional[Dict[str, Any]] = None,
) -> SaveOutputResult:
    """
    - Itens > 0: grava (com backup do ficheiro anterior se existir).
    - Itens == [] + falha (failure_reason ou collection_failed): não apaga JSON anterior com dados;
      grava latest_error.json + entrada em audit_reports_crawler_failures/failures.jsonl.
    - Itens == [] confirmado: allow_empty=True e empty_confirmed_reason == 'confirmed_no_items'.
    - Itens == [] sem falha explícita nem confirmação: preserva se o anterior tinha len>0; caso contrário grava [].
    """
    output_path = Path(output_path)
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    listing_events = listing_events or []
    extra_context = extra_context or {}

    prev: Optional[List[Any]] = None
    if output_path.is_file():
        prev = _load_json_array(output_path)
    prev_n = len(prev) if isinstance(prev, list) else 0

    is_failure = bool(failure_reason) or bool(collection_failed)
    confirmed_empty = bool(allow_empty) and (empty_confirmed_reason == CONFIRMED_EMPTY_REASON)

    def _failure_record(msg: str, kind: str) -> Dict[str, Any]:
        return {
            "output_path": str(output_path),
            "message": msg,
            "failure_kind": kind,
            "failure_reason": failure_reason,
            "collection_failed": collection_failed,
            "listing_events": listing_events,
            "previous_item_count": prev_n,
            **extra_context,
        }

    # --- Caso 1: há itens ---
    if items:
        bk = _backup_existing_editais(output_path, source_name)
        output_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        if output_path.exists():
            try:
                (output_dir / "latest_error.json").unlink(missing_ok=True)
            except OSError:
                pass
        print(f"[{source_name}] coleta_ok: gravados {len(items)} itens em {output_path.name}")
        return SaveOutputResult(
            status="saved",
            source_name=source_name,
            output_path=output_path,
            message=f"Gravados {len(items)} itens.",
            wrote_file=True,
            preserved_previous=False,
            backup_path=bk,
            suggested_exit_code=0,
            failure_kind="coleta_com_itens",
        )

    # --- Caso 2: vazio confirmado ---
    if confirmed_empty:
        bk = _backup_existing_editais(output_path, source_name)
        output_path.write_text("[]", encoding="utf-8")
        print(f"[{source_name}] coleta_vazia_confirmada: gravado [] ({CONFIRMED_EMPTY_REASON})")
        return SaveOutputResult(
            status="saved_empty_confirmed",
            source_name=source_name,
            output_path=output_path,
            message="Lista vazia gravada por confirmação explícita.",
            wrote_file=True,
            preserved_previous=False,
            backup_path=bk,
            suggested_exit_code=0,
            failure_kind="coleta_vazia_confirmada",
        )

    # --- Caso 3: falha de coleta / rede / listagem ---
    if is_failure:
        msg = failure_reason or "collection_failed"
        rec = _failure_record(msg, "falha_de_coleta")
        _write_latest_error(output_dir, rec)
        _append_failure_log(source_name, rec)
        if prev_n > 0:
            print(
                f"[{source_name}] falha_de_coleta: não sobrescrever {output_path.name} "
                f"(preservando {prev_n} itens). Motivo: {msg}"
            )
            return SaveOutputResult(
                status="preserved_failure",
                source_name=source_name,
                output_path=output_path,
                message=msg,
                wrote_file=False,
                preserved_previous=True,
                suggested_exit_code=2,
                failure_kind="falha_de_coleta",
            )
        print(f"[{source_name}] falha_de_coleta: sem ficheiro anterior; não criado {output_path.name}. Motivo: {msg}")
        return SaveOutputResult(
            status="preserved_failure",
            source_name=source_name,
            output_path=output_path,
            message=msg,
            wrote_file=False,
            preserved_previous=False,
            suggested_exit_code=2,
            failure_kind="falha_de_coleta",
        )

    # --- Caso 4: vazio sem falha nem confirmação (ex.: filtros eliminaram tudo) ---
    if prev_n > 0:
        rec = _failure_record(
            "Itens vazios após coleta sem flag de falha nem confirmação de lista vazia; "
            "preservando dados anteriores.",
            "coleta_vazia_sem_confirmacao",
        )
        _write_latest_error(output_dir, rec)
        _append_failure_log(source_name, rec)
        print(
            f"[{source_name}] coleta_vazia_sem_confirmacao: não sobrescrever {output_path.name} "
            f"(preservando {prev_n} itens)."
        )
        return SaveOutputResult(
            status="preserved_failure",
            source_name=source_name,
            output_path=output_path,
            message=rec["message"],
            wrote_file=False,
            preserved_previous=True,
            suggested_exit_code=2,
            failure_kind="coleta_vazia_sem_confirmacao",
        )

    # Sem anterior útil: primeiro run ou ficheiro inexistente / vazio
    output_path.write_text("[]", encoding="utf-8")
    print(f"[{source_name}] coleta_ok: gravado [] (sem dados anteriores a preservar)")
    return SaveOutputResult(
        status="saved",
        source_name=source_name,
        output_path=output_path,
        message="Lista vazia gravada (sem ficheiro anterior com itens).",
        wrote_file=True,
        preserved_previous=False,
        suggested_exit_code=0,
        failure_kind="coleta_vazia_primeira_gravacao",
    )


__all__ = [
    "CONFIRMED_EMPTY_REASON",
    "SaveOutputResult",
    "save_output_safely",
]
