"""Merge não destrutivo de registros e extras (ETL EditalFinder)."""
from __future__ import annotations

import json
import uuid
from collections.abc import Mapping, Sequence
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# PostgreSQL (text/jsonb via PostgREST) rejeita U+0000 em strings — comum em PDFs/HTML/PDFs.
_NUL = "\x00"


def sanitize_for_postgres(obj: Any) -> Any:
    """
    Remove caracteres NUL (\\x00) de strings e percorre Mapping/listas/tuplas aninhadas.
    Cobre dict “normal”, collections.ChainMap, bytes vindos de PDF, e escalares numpy.
    Evita erro 22P05 ('\\u0000 cannot be converted to text') no Supabase.
    """
    if obj is None:
        return None
    if isinstance(obj, (bool, int)):
        return obj
    if isinstance(obj, float):
        return obj
    if isinstance(obj, (datetime, date)):
        s = obj.isoformat()
        return s.replace(_NUL, "") if _NUL in s else s
    if isinstance(obj, Decimal):
        s = str(obj)
        return s.replace(_NUL, "") if _NUL in s else s
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, Enum):
        return sanitize_for_postgres(obj.value)
    if isinstance(obj, str):
        return obj.replace(_NUL, "") if _NUL in obj else obj
    if isinstance(obj, (bytes, bytearray)):
        try:
            decoded = bytes(obj).decode("utf-8", errors="surrogatepass")
        except Exception:
            decoded = bytes(obj).decode("latin-1", errors="replace")
        return decoded.replace(_NUL, "") if _NUL in decoded else decoded
    if isinstance(obj, memoryview):
        return sanitize_for_postgres(obj.tobytes())

    mod = type(obj).__module__
    if mod == "numpy" or mod.startswith("numpy."):
        try:
            shape = getattr(obj, "shape", None)
            if shape == ():
                return sanitize_for_postgres(obj.item())
        except Exception:
            pass

    if isinstance(obj, Mapping):
        out: Dict[str, Any] = {}
        for k, v in obj.items():
            sk = sanitize_for_postgres(k)
            if not isinstance(sk, str):
                sk = str(sk)
            out[sk.replace(_NUL, "")] = sanitize_for_postgres(v)
        return out
    if isinstance(obj, tuple):
        return tuple(sanitize_for_postgres(v) for v in obj)
    if isinstance(obj, list):
        return [sanitize_for_postgres(v) for v in obj]
    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        return [sanitize_for_postgres(v) for v in obj]

    return obj


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    if isinstance(v, (list, dict)) and len(v) == 0:
        return True
    return False


def merge_scalar_prefer_non_empty(old: Any, new: Any) -> Any:
    if _is_empty(new):
        return sanitize_for_postgres(old)
    return sanitize_for_postgres(new)


def merge_descricao(old: Optional[str], new: Optional[str]) -> Optional[str]:
    """Prefere o texto mais longo e informativo."""
    o = (old or "").strip()
    n = (new or "").strip()
    if not n:
        return sanitize_for_postgres(old)
    if not o:
        return sanitize_for_postgres(new)
    chosen = n if len(n) > len(o) else o
    return sanitize_for_postgres(chosen)


def _dedupe_list(seq: List[Any], *, key_fn=None) -> List[Any]:
    seen: Set[str] = set()
    out: List[Any] = []
    for x in seq:
        k = key_fn(x) if key_fn else json.dumps(x, sort_keys=True, ensure_ascii=False) if isinstance(x, dict) else str(x)
        if k in seen:
            continue
        seen.add(k)
        out.append(x)
    return out


def merge_extras_dict(old: Optional[Dict[str, Any]], new: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge profundo de extras: não sobrescreve valores bons com vazios;
    dicts recursivos; listas unidas sem duplicata (por serialização estável).
    """
    base = deepcopy(old) if isinstance(old, dict) else {}
    inc = new if isinstance(new, dict) else {}
    for k, v in inc.items():
        if k not in base or _is_empty(base.get(k)):
            if not _is_empty(v):
                base[k] = deepcopy(v) if isinstance(v, (dict, list)) else v
            continue
        cur = base[k]
        if isinstance(cur, dict) and isinstance(v, dict):
            base[k] = merge_extras_dict(cur, v)
        elif isinstance(cur, list) and isinstance(v, list):
            if v:
                base[k] = _dedupe_list(cur + v)
        elif isinstance(v, str) and isinstance(cur, str):
            base[k] = merge_descricao(cur, v)
        elif not _is_empty(v):
            base[k] = v
    return sanitize_for_postgres(base)


def anexos_dedupe_url(anexos: Any) -> List[Dict[str, Any]]:
    if not isinstance(anexos, list):
        return []
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for a in anexos:
        if not isinstance(a, dict):
            continue
        url = str(a.get("url") or "").strip()
        key = url or json.dumps(a, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out
