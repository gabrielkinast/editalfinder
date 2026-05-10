#!/usr/bin/env python3
"""
Diagnóstico IAEA Wave 1 a partir do standardized + config (sem Supabase).
Gera audit_reports_news_research/iaea_wave1_diagnostico.{json,md}.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "news_research_sources.json"
STD_DEFAULT = ROOT / "audit_reports_news_research" / "standardized" / "iaea_news_publications_standardized.json"
RAW_DEFAULT = ROOT / "audit_reports_news_research" / "raw" / "iaea_news_publications_raw.json"
OUT_DIR = ROOT / "audit_reports_news_research"


def _load_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _summary_len(it: Dict[str, Any]) -> int:
    r = it.get("resumo") or it.get("descricao") or ""
    return len(str(r).strip())


def main() -> int:
    ap = argparse.ArgumentParser(description="Diagnóstico IAEA Wave 1 (ficheiros locais).")
    ap.add_argument("--standardized", default=str(STD_DEFAULT))
    ap.add_argument("--raw", default=str(RAW_DEFAULT))
    ap.add_argument("--config", default=str(CONFIG_PATH))
    ap.add_argument("--output-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    std_path = Path(args.standardized)
    raw_path = Path(args.raw)
    cfg_path = Path(args.config)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    dr = _load_module("dry_run_loader", ROOT / "scripts" / "dry_run_news_research_loader.py")

    cfg = _load_json(cfg_path, {})
    iaea_cfg: Dict[str, Any] = {}
    for s in cfg.get("sources") or []:
        if isinstance(s, dict) and s.get("id") == "iaea_news_publications":
            iaea_cfg = s
            break

    items = _load_json(std_path, [])
    if not isinstance(items, list):
        print(f"Entrada inválida: {std_path}", file=sys.stderr)
        return 2

    raw_items = _load_json(raw_path, [])

    by_seed = Counter()
    by_tipo = Counter()
    by_seed_kind_extras = Counter()
    missing_summary = 0
    missing_date = 0
    generic_n = 0
    generico_samples: List[Dict[str, str]] = []
    candidatos_noticia: List[Dict[str, Any]] = []
    candidatos_pesquisa: List[Dict[str, Any]] = []

    for it in items:
        if not isinstance(it, dict):
            continue
        ex = it.get("extras") if isinstance(it.get("extras"), dict) else {}
        su = str(ex.get("seed_url") or "")
        by_seed[su] += 1
        sk = str(ex.get("seed_kind") or "mixed")
        by_seed_kind_extras[sk] += 1
        tc = str(it.get("tipo_conteudo") or "")
        by_tipo[tc] += 1
        if ex.get("missing_summary") or _summary_len(it) < 40:
            missing_summary += 1
        if not it.get("data_publicacao"):
            missing_date += 1
        if dr._is_generic(it):
            generic_n += 1
            if len(generico_samples) < 12:
                generico_samples.append({"titulo": str(it.get("titulo") or "")[:120], "link": str(it.get("link") or "")[:200]})
        lk = str(it.get("link") or "")
        if it.get("data_publicacao") and _summary_len(it) >= 40 and not dr._is_generic(it):
            if tc == "noticia":
                if len(candidatos_noticia) < 15:
                    candidatos_noticia.append({"titulo": it.get("titulo"), "link": it.get("link"), "data_publicacao": it.get("data_publicacao")})
            elif tc == "pesquisa":
                if len(candidatos_pesquisa) < 15:
                    candidatos_pesquisa.append({"titulo": it.get("titulo"), "link": it.get("link"), "data_publicacao": it.get("data_publicacao")})

    rss_fields_doc = (
        "Os feeds RSS/Atom da IAEA expõem tipicamente: `title`, `link`, `description` (ou `summary`/`content` em Atom), "
        "`pubDate` ou `published`/`updated`. Muitos itens chegam com `description` vazio ou HTML mínimo — daí "
        "`missing_summary` até enriquecimento por página (`meta description`, `og:description`, primeiro `<p>` útil em `<main>`/`<article>`, "
        "datas em `article:published_time` / JSON-LD `datePublished`/`dateModified`, ou data inferível apenas do URL quando presente)."
    )

    diagnostico: Dict[str, Any] = {
        "gerado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fonte_id": "iaea_news_publications",
        "ficheiros": {
            "standardized": str(std_path.resolve()) if std_path.is_file() else str(std_path),
            "raw": str(raw_path.resolve()) if raw_path.is_file() else str(raw_path),
            "config": str(cfg_path.resolve()),
        },
        "seeds_config": {
            "seed_urls_news": iaea_cfg.get("seed_urls_news") or [],
            "seed_urls_publications": iaea_cfg.get("seed_urls_publications") or [],
            "seed_urls_legacy": iaea_cfg.get("seed_urls") or [],
            "page_enrich_max": iaea_cfg.get("page_enrich_max"),
            "max_items": iaea_cfg.get("max_items"),
        },
        "contagens": {
            "total_standardized": len(items),
            "itens_por_seed_url": dict(by_seed),
            "itens_por_seed_kind_extras": dict(by_seed_kind_extras),
            "por_tipo_conteudo": dict(by_tipo),
            "estimativa_from_news_seeds": sum(by_seed.get(u, 0) for u in (iaea_cfg.get("seed_urls_news") or [])),
            "estimativa_from_publications_seeds": sum(by_seed.get(u, 0) for u in (iaea_cfg.get("seed_urls_publications") or [])),
            "missing_summary": missing_summary,
            "missing_date": missing_date,
            "genericos_heuristica": generic_n,
        },
        "porque_missing_summary": (
            "Resumo curto ou ausente quando: (1) o item RSS não traz `description` útil; (2) o HTML da página não foi obtido (429/403/timeout); "
            "(3) a página não tem `meta description`/`og:description` nem parágrafo `<p>` suficientemente longo após strip HTML."
        ),
        "porque_sem_data": (
            "Sem `data_publicacao` quando: (1) `pubDate` ausente ou num formato não parseado; (2) meta/JSON-LD sem datas válidas na página; "
            "(3) URL sem segmento de data reconhecível; (4) item é hub/listagem sem data editorial."
        ),
        "rss_e_atom_campos": ["title", "link", "description|encoded|summary|content", "pubDate|published|updated"],
        "enriquecimento_pagina": rss_fields_doc,
        "amostras": {
            "genericos": generico_samples,
            "bons_candidatos_noticia": candidatos_noticia,
            "bons_candidatos_pesquisa": candidatos_pesquisa,
        },
        "raw_amostra_campos": _sample_raw_fields(raw_items[:3]) if raw_items else [],
        "notas_tecnicas": [
            "Feeds com XML inválido (ex.: `<br>` em `<title>`) são lidos via extrator `rss_loose` no crawler.",
            "Publicações RSS muitas vezes vêm sem `description`: o standardized pode usar o título oficial (≥40 caracteres) como texto descritivo mínimo para `pesquisa`, após strip.",
        ],
        "recomendacao_wave1_staging": (
            "Avaliar `build_iaea_wave1_payloads` + `load_news_research_sources.py --dry-run --wave iaea_wave1`; "
            "só considerar apply manual após rever `iaea_wave1_review_candidates.json` e confirmar `errors_count==0` no resumo do loader."
        ),
    }

    out_json = out_dir / "iaea_wave1_diagnostico.json"
    out_md = out_dir / "iaea_wave1_diagnostico.md"
    out_json.write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# IAEA Wave 1 — diagnóstico",
        "",
        f"- Gerado: `{diagnostico['gerado_em']}`",
        f"- Standardized: `{diagnostico['ficheiros']['standardized']}`",
        "",
        "## Seeds (config)",
        "",
        "```json",
        json.dumps(diagnostico["seeds_config"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Contagens",
        "",
        f"- Total itens (standardized): **{diagnostico['contagens']['total_standardized']}**",
        f"- Por `tipo_conteudo`: `{diagnostico['contagens']['por_tipo_conteudo']}`",
        f"- Por `extras.seed_kind`: `{diagnostico['contagens']['itens_por_seed_kind_extras']}`",
        f"- `missing_summary` (heurística): **{missing_summary}**",
        f"- Sem `data_publicacao`: **{missing_date}**",
        f"- Genéricos (heurística `_is_generic`): **{generic_n}**",
        "",
        "### Por seed URL (agregado no standardized)",
        "",
        "```json",
        json.dumps(diagnostico["contagens"]["itens_por_seed_url"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Por que `missing_summary`?",
        "",
        diagnostico["porque_missing_summary"],
        "",
        "## Por que itens sem data?",
        "",
        diagnostico["porque_sem_data"],
        "",
        "## Campos típicos RSS/Atom",
        "",
        "- " + ", ".join(f"`{x}`" for x in diagnostico["rss_e_atom_campos"]),
        "",
        "## Enriquecimento (meta / JSON-LD / parágrafo / URL)",
        "",
        diagnostico["enriquecimento_pagina"],
        "",
        "## Amostras: bons candidatos",
        "",
        "### Notícia (data + resumo ≥40, não genérico)",
        "",
        "```json",
        json.dumps(candidatos_noticia, ensure_ascii=False, indent=2),
        "```",
        "",
        "### Pesquisa / publicação técnica",
        "",
        "```json",
        json.dumps(candidatos_pesquisa, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Notas técnicas",
        "",
        "- " + "\n- ".join(diagnostico.get("notas_tecnicas") or []),
        "",
        "## Recomendação (staging)",
        "",
        diagnostico.get("recomendacao_wave1_staging", ""),
        "",
        "## Próximo passo",
        "",
        "```",
        "python scripts/build_iaea_wave1_payloads.py",
        "```",
        "",
    ]
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(json.dumps({"ok": True, "json": str(out_json), "md": str(out_md)}, ensure_ascii=False))
    return 0


def _sample_raw_fields(samples: List[Any]) -> List[Dict[str, Any]]:
    out = []
    for r in samples:
        if not isinstance(r, dict):
            continue
        out.append(
            {
                "titulo": (str(r.get("titulo") or "")[:80]),
                "link": (str(r.get("link") or "")[:120]),
                "keys": sorted(r.keys()),
                "data_publicacao_raw": str(r.get("data_publicacao_raw") or "")[:80],
                "descricao_len": len(str(r.get("descricao") or "")),
                "seed_kind": r.get("seed_kind"),
            }
        )
    return out


if __name__ == "__main__":
    raise SystemExit(main())
