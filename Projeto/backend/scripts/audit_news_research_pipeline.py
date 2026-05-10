#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "audit_reports_news_research"


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_date(v: Any) -> datetime | None:
    if not v:
        return None
    s = str(v).strip()
    if not s:
        return None
    for p in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            dt = datetime.strptime(s[:19], p)
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def _looks_news(item: Dict[str, Any]) -> bool:
    blob = f"{item.get('titulo','')} {item.get('resumo','')} {item.get('descricao','')} {item.get('link','')}".lower()
    return any(k in blob for k in ("news", "announces", "announcement", "press", "update", "brief", "release"))


def _looks_research(item: Dict[str, Any]) -> bool:
    blob = f"{item.get('titulo','')} {item.get('resumo','')} {item.get('descricao','')} {item.get('link','')}".lower()
    return any(k in blob for k in ("research", "study", "report", "publication", "paper", "dataset", "technical"))


def _is_generic(item: Dict[str, Any]) -> bool:
    lk = str(item.get("link") or "").lower()
    title = str(item.get("titulo") or "").strip().lower()
    if any(x in lk for x in ("/about", "/contact", "/privacy", "/terms", "/login", "/careers", "/jobs")):
        return True
    if title in ("home", "news", "publications", "nasa", "darpa", "iaea", "eurekalert"):
        return True
    return False


def _load_standardized(std_dir: Path) -> List[Tuple[str, Dict[str, Any]]]:
    out: List[Tuple[str, Dict[str, Any]]] = []
    for p in sorted(std_dir.glob("*_standardized.json")):
        src = p.name.replace("_standardized.json", "")
        data = _load_json(p, [])
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            continue
        for it in data:
            if isinstance(it, dict):
                out.append((src, it))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Audita pipeline local de notícia/pesquisa (sem DB).")
    ap.add_argument("--input-dir", default=str(DEFAULT_DIR / "standardized"))
    ap.add_argument("--output-dir", default=str(DEFAULT_DIR))
    args = ap.parse_args()

    std_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = _load_standardized(std_dir)
    cutoff = datetime.now(timezone.utc) - timedelta(days=365)

    by_source = defaultdict(lambda: Counter())
    flags = Counter()
    seen = set()
    dup_links = []
    examples = []
    broken_like = 0
    for src, it in rows:
        by_source[src]["total"] += 1
        link = str(it.get("link") or "").strip()
        if link in seen:
            flags["duplicata_link"] += 1
            dup_links.append({"source_id": src, "link": link})
        else:
            seen.add(link)

        dt = _parse_date(it.get("data_publicacao"))
        if dt and dt >= cutoff:
            by_source[src]["within_12m"] += 1
        if not dt:
            by_source[src]["without_date"] += 1
            flags["sem_data_publicacao"] += 1

        if not link.startswith("http"):
            flags["link_quebrado_ou_invalido"] += 1
            broken_like += 1

        ctype = str(it.get("tipo_conteudo") or "").lower()
        if ctype == "noticia" and _looks_research(it):
            flags["noticia_com_sinal_pesquisa"] += 1
        if ctype == "pesquisa" and _looks_news(it):
            flags["pesquisa_com_sinal_noticia"] += 1
        if _is_generic(it):
            flags["conteudo_generico"] += 1
            by_source[src]["generic"] += 1

        if len(examples) < 120:
            examples.append(
                {
                    "source_id": src,
                    "titulo": it.get("titulo"),
                    "link": link,
                    "data_publicacao": it.get("data_publicacao"),
                    "tipo_conteudo": it.get("tipo_conteudo"),
                }
            )

    by_source_json = []
    noisy = []
    for src, c in sorted(by_source.items()):
        total = int(c.get("total", 0))
        generic = int(c.get("generic", 0))
        without_date = int(c.get("without_date", 0))
        noise_ratio = (generic + without_date) / total if total else 0.0
        row = {
            "source_id": src,
            "total": total,
            "within_12m": int(c.get("within_12m", 0)),
            "without_date": without_date,
            "generic": generic,
            "noise_ratio": round(noise_ratio, 3),
        }
        by_source_json.append(row)
        if noise_ratio >= 0.55 or total < 5:
            noisy.append({**row, "reason": "alto_ruido_ou_baixo_volume"})

    recommendations = {
        "ativar_primeiro": [
            r["source_id"]
            for r in by_source_json
            if r["total"] >= 8 and r["noise_ratio"] <= 0.45 and r["within_12m"] >= 3
        ][:3],
        "manter_em_teste": [r["source_id"] for r in noisy][:6],
    }

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input_dir": str(std_dir.resolve()),
        "rows_total": len(rows),
        "sources_total": len(by_source_json),
        "flags_totais": dict(flags),
        "links_quebrados_ou_invalidos": broken_like,
        "fontes_ruidosas": noisy,
        "recomendacao_fontes_ativar_primeiro": recommendations["ativar_primeiro"],
        "proximos_passos_integracao_loader": [
            "Adicionar job dedicado com --apply-content-routed para carregar apenas noticia/pesquisa em staging.",
            "Reforcar infer_content_type com features por fonte (NASA/DARPA/IAEA/EurekAlert).",
            "Criar whitelist de seeds por fonte e threshold minimo de data_publicacao para ativacao."
        ],
    }

    (out_dir / "audit_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "by_source.json").write_text(json.dumps(by_source_json, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "examples.json").write_text(json.dumps(examples, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Auditoria news/research pipeline",
        "",
        f"- Itens avaliados: **{len(rows)}**",
        f"- Fontes: **{len(by_source_json)}**",
        f"- Sem data_publicacao: **{flags.get('sem_data_publicacao', 0)}**",
        f"- Duplicatas por link: **{flags.get('duplicata_link', 0)}**",
        f"- Conteúdo genérico: **{flags.get('conteudo_generico', 0)}**",
        "",
        "## Fontes com maior ruído",
        "",
    ]
    if noisy:
        for r in noisy:
            md.append(
                f"- `{r['source_id']}` total={r['total']} sem_data={r['without_date']} "
                f"generic={r['generic']} noise_ratio={r['noise_ratio']}"
            )
    else:
        md.append("- Nenhuma fonte com ruído alto no critério atual.")

    md.extend(
        [
            "",
            "## Recomendação de ativação inicial",
            "",
            "- Ativar primeiro: " + (", ".join(recommendations["ativar_primeiro"]) if recommendations["ativar_primeiro"] else "nenhuma (revisar coleta)"),
            "- Manter em teste: " + (", ".join(recommendations["manter_em_teste"]) if recommendations["manter_em_teste"] else "nenhuma"),
            "",
            "## Próximos passos para integração com loader",
            "",
        ]
    )
    for p in summary["proximos_passos_integracao_loader"]:
        md.append(f"- {p}")
    (out_dir / "audit_summary.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

