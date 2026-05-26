"""Utilitários compartilhados — recoleta Backend 4 (sem escrita no banco)."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "outputs" / "backend_4_recrawl_comparison"

SOURCE_FONT_PATTERNS = {
    "china": ("china international", "mofcom", "chinabidding"),
    "araucaria": ("fundação araucária", "fundacao araucaria", "fappr"),
    "grants": ("grants.gov",),
}


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json_list(path: Path, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        data = [data]
    if limit:
        return data[:limit]
    return data


def normalize_link(link: Optional[str]) -> str:
    if not link:
        return ""
    u = str(link).strip().lower().split("#", 1)[0]
    if u.endswith("/"):
        u = u[:-1]
    return u


def normalize_title(t: Optional[str]) -> str:
    if not t:
        return ""
    s = unicodedata.normalize("NFKD", str(t))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s.lower()).strip()
    return s[:160]


def match_key(item: Dict[str, Any]) -> str:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    link = normalize_link(item.get("link"))
    if link:
        if "oppid=" in link or "oppid=" in link.lower():
            q = parse_qs(urlparse(link).query)
            oid = (q.get("oppId") or q.get("oppid") or [None])[0]
            if oid:
                return f"grants_opp:{oid}"
        if "/opportunity/" in link:
            tail = link.rstrip("/").split("/opportunity/")[-1].split("?")[0]
            if tail:
                return f"simpler:{tail}"
        return f"link:{link}"
    num = str(ex.get("opportunity_number") or ex.get("codigo_oportunidade") or ex.get("legacy_opp_id") or "").strip()
    if num:
        return f"num:{num.upper()}"
    tit = normalize_title(item.get("titulo"))
    fonte = normalize_title(item.get("fonte") or item.get("fonte_recurso"))
    return f"t:{tit}|{fonte}"


def db_structured_deadline(rec: Dict[str, Any]) -> bool:
    for k in ("prazo_envio", "fim_inscricao"):
        v = rec.get(k)
        if v and str(v).strip()[:4].isdigit() and "-" in str(v)[:10]:
            return True
    return False


def item_has_deadline(item: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[str]]:
    """(tem_prazo, iso, confidence)"""
    if item.get("prazo_data"):
        return True, str(item["prazo_data"])[:10], item.get("prazo_confidence")
    if item.get("fim_inscricao") and str(item["fim_inscricao"])[:4].isdigit():
        iso = str(item["fim_inscricao"])[:10]
        if "-" in iso:
            return True, iso, item.get("prazo_confidence") or "media"
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    be = ex.get("backend_enrichment") if isinstance(ex.get("backend_enrichment"), dict) else {}
    dn = ex.get("deadline_normalizer") if isinstance(ex.get("deadline_normalizer"), dict) else {}
    iso = be.get("prazo_data") or dn.get("prazo_data")
    if iso:
        return True, str(iso)[:10], be.get("prazo_confidence") or dn.get("prazo_confidence")
    return False, None, None


def fonte_matches(fonte: str, source: str) -> bool:
    f = fonte.lower()
    return any(p in f for p in SOURCE_FONT_PATTERNS.get(source, ()))
