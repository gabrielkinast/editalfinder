#!/usr/bin/env python3
"""
Auditoria específica de preservação de documentos/PDFs no pipeline (dry-run).

Fluxo por item:
  bruto -> transformer._transform_item_with_result -> loader.map_to_db_schema/_strip_payload

Saídas:
  audit_reports_docs/audit_docs_summary.json
  audit_reports_docs/audit_docs_summary.md
  audit_reports_docs/audit_docs_by_source.json
  audit_reports_docs/audit_docs_losses.json
  audit_reports_docs/audit_docs_download_failures.json
  audit_reports_docs/audit_docs_examples.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT / "CORE"
OUT_DEFAULT = ROOT / "audit_reports_docs"

if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

import transformer as tr  # noqa: E402
import loader  # noqa: E402


TARGET_SOURCES = (
    "aneel",
    "bndes",
    "cnpq",
    "finep",
    "fapergs",
    "fapesp",
    "fapesc",
    "cnen",
    "pncp_defesa",
    "compras_defesa",
)


DOC_TYPE_PATTERNS: List[Tuple[str, Tuple[str, ...]]] = [
    ("edital_pdf", ("edital", "edital_", "edital-", "edital.", "chamada pública", "chamada publica")),
    ("anexo", ("anexo", "anex", "attachment")),
    ("regulamento", ("regulamento", "regulation", "normativo")),
    ("termo_referencia", ("termo de referência", "termo de referencia", "tr_", "termo_referencia")),
    ("chamada", ("chamada", "call for", "call_", "chamamento")),
    ("resultado", ("resultado", "resultado final", "homolog", "ata de julgamento")),
    ("formulario", ("formulário", "formulario", "form", "inscricao", "cadastro")),
    ("planilha", ("planilha", "sheet", ".xlsx", ".xls", ".csv")),
    ("cronograma", ("cronograma", "timeline", "schedule", "calendario")),
    ("modelo_documento", ("modelo", "template", "minuta", ".doc", ".docx")),
]


def _infer_source_name(json_path: Path) -> str:
    return json_path.parent.parent.name.lower()


def _discover_source_json(source: str) -> Optional[Path]:
    out = ROOT / source / "outputs"
    primary = out / f"{source}_editais.json"
    if primary.is_file():
        return primary
    if source == "plataforma_industria":
        alt = out / "plataforma_editais.json"
        if alt.is_file():
            return alt
    return None


def _is_http_url(u: str) -> bool:
    return u.lower().startswith(("http://", "https://"))


def _clean_url(raw: Any) -> str:
    if raw is None:
        return ""
    u = str(raw).strip()
    u = re.sub(r"\s+", " ", u).strip()
    return u


def _normalize_abs_url(url: str, base_url: str) -> str:
    u = _clean_url(url)
    if not u:
        return ""
    if u.lower().startswith(("javascript:", "#")):
        return ""
    if _is_http_url(u):
        return u
    if base_url and _is_http_url(base_url):
        try:
            return urljoin(base_url, u)
        except Exception:
            return u
    return u


def _classify_doc_type(title: str, url: str) -> str:
    blob = f"{title} {url}".lower()
    if any(x in blob for x in (".xlsx", ".xls", "planilha", "sheet", ".csv")):
        return "planilha"
    if any(x in blob for x in (".doc", ".docx", "modelo", "template", "minuta")):
        return "modelo_documento"
    for t, pats in DOC_TYPE_PATTERNS:
        if any(p in blob for p in pats):
            return t
    return "documento_desconhecido"


def _detect_format(url: str, title: str = "") -> str:
    blob = f"{url} {title}".lower()
    path = urlparse(url).path.lower()
    if path.endswith(".pdf") or ".pdf" in blob:
        return "pdf"
    if path.endswith(".docx") or ".docx" in blob:
        return "docx"
    if path.endswith(".doc") or ".doc" in blob:
        return "doc"
    if path.endswith(".xlsx") or ".xlsx" in blob:
        return "xlsx"
    if path.endswith(".xls") or ".xls" in blob:
        return "xls"
    if path.endswith(".csv") or ".csv" in blob:
        return "csv"
    if path.endswith(".zip") or ".zip" in blob:
        return "zip"
    if path.endswith(".rar") or ".rar" in blob:
        return "rar"
    if path.endswith(".html") or path.endswith(".htm"):
        return "html"
    return "outro"


def _extract_raw_doc_candidates(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    out: List[Dict[str, Any]] = []

    def _iter_docs_payload(v: Any) -> List[Any]:
        if isinstance(v, dict):
            return [v]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            try:
                j = json.loads(s)
                if isinstance(j, list):
                    return j
                if isinstance(j, dict):
                    return [j]
            except Exception:
                urls = re.findall(r"https?://[^\s\"'<>]+", s, flags=re.IGNORECASE)
                return [{"url": u, "nome": "Documento"} for u in urls]
        return []

    def _append_list(val: Any, origem: str) -> None:
        for d in _iter_docs_payload(val):
            if isinstance(d, dict):
                out.append(
                    {
                        "titulo": d.get("nome") or d.get("title") or d.get("titulo") or "Documento",
                        "url": d.get("url") or d.get("link") or "",
                        "origem": origem,
                    }
                )
            elif isinstance(d, str):
                out.append({"titulo": "Documento", "url": d, "origem": origem})

    _append_list(item.get("documentos"), "item.documentos")
    _append_list(item.get("anexos"), "item.anexos")
    _append_list(extras.get("documentos"), "extras.documentos")
    _append_list(extras.get("anexos"), "extras.anexos")

    for key in ("pdf_url", "url_chamada", "link_pdf", "anexo_pdf"):
        v = item.get(key)
        if isinstance(v, str) and ".pdf" in v.lower():
            out.append({"titulo": "PDF principal", "url": v, "origem": f"item.{key}"})
        ev = extras.get(key)
        if isinstance(ev, str) and ".pdf" in ev.lower():
            out.append({"titulo": "PDF principal", "url": ev, "origem": f"extras.{key}"})
    return out


def _normalize_docs(docs: List[Dict[str, Any]], base_url: str, default_status: str) -> List[Dict[str, Any]]:
    norm: List[Dict[str, Any]] = []
    seen = set()
    for d in docs:
        t = str(d.get("titulo") or "Documento").strip()[:240]
        url = _normalize_abs_url(str(d.get("url") or ""), base_url)
        if not url:
            continue
        if url in seen:
            continue
        seen.add(url)
        formato = _detect_format(url, t)
        norm.append(
            {
                "titulo": t,
                "url": url,
                "tipo": _classify_doc_type(t, url),
                "formato": formato,
                "origem": str(d.get("origem") or ""),
                "status_download": default_status,
                "erro_download": "",
                "texto_extraido": "",
                "resumo": "",
            }
        )
    return norm[:30]


def _best_primary_pdf(documents: List[Dict[str, Any]]) -> str:
    if not documents:
        return ""
    preferred = {"edital_pdf", "regulamento", "chamada", "termo_referencia"}
    for d in documents:
        if d.get("formato") == "pdf" and d.get("tipo") in preferred:
            return str(d.get("url") or "")
    for d in documents:
        if d.get("formato") == "pdf":
            return str(d.get("url") or "")
    return ""


def _count_docs_by_format(docs: List[Dict[str, Any]]) -> Tuple[int, int]:
    pdf_n = sum(1 for d in docs if str(d.get("formato") or "") == "pdf")
    non_pdf_n = sum(1 for d in docs if str(d.get("formato") or "") and str(d.get("formato") or "") != "pdf")
    return pdf_n, non_pdf_n


def _check_links(docs: List[Dict[str, Any]]) -> Dict[str, int]:
    broken = 0
    relative = 0
    invalid = 0
    dup_removed = 0
    seen = set()
    for d in docs:
        u = str(d.get("url") or "")
        if not u:
            broken += 1
            continue
        if u.lower().startswith(("javascript:", "#")):
            invalid += 1
        if not _is_http_url(u):
            relative += 1
        if u in seen:
            dup_removed += 1
        seen.add(u)
    return {
        "links_invalidos": invalid,
        "links_relativos_restantes": relative,
        "links_quebrados": broken,
        "duplicados": dup_removed,
    }


def _sample_download_status(payload: Dict[str, Any]) -> Tuple[str, str]:
    ex = payload.get("extras") if isinstance(payload.get("extras"), dict) else {}
    pdf_url = str(ex.get("pdf_url") or "")
    if not pdf_url:
        return "nao_baixado", "sem_pdf_url"
    if ex.get("pdf_lido_para_enriquecimento"):
        return "sucesso", ""
    if pdf_url and ".pdf" in pdf_url.lower():
        return "falhou", "pdf_nao_lido_no_transformer"
    return "nao_baixado", ""


def audit_one_source(json_path: Path, max_items: int, no_skip_pdf: bool) -> Dict[str, Any]:
    source = _infer_source_name(json_path)
    raw = json.loads(json_path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = [raw]
    items = [x for x in raw if isinstance(x, dict)][:max_items]

    transformed_ok = 0
    losses: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []
    examples: List[Dict[str, Any]] = []

    cnt = Counter()
    if not no_skip_pdf:
        tr.read_pdf_text = lambda pdf_url, page_referer=None: None  # type: ignore[method-assign]

    for it in items:
        base_link = str(it.get("link") or it.get("url") or "").strip()
        raw_docs = _normalize_docs(_extract_raw_doc_candidates(it), base_link, default_status="nao_baixado")
        raw_pdf = _best_primary_pdf(raw_docs)
        raw_has_docs = len(raw_docs) > 0
        raw_has_pdf = bool(raw_pdf)
        raw_pdf_docs_n, raw_non_pdf_docs_n = _count_docs_by_format(raw_docs)

        tr_res = tr._transform_item_with_result(it, source)
        if tr_res.rejected or not tr_res.payload:
            cnt["rejeitados"] += 1
            if raw_has_docs or raw_has_pdf:
                losses.append(
                    {
                        "fonte": source,
                        "etapa": "bruto->transformado",
                        "motivo": tr_res.rejection_reason,
                        "titulo": str(it.get("titulo") or "")[:200],
                        "link": base_link[:400],
                        "raw_pdf_url": raw_pdf,
                        "raw_docs_n": len(raw_docs),
                        "transformado_docs_n": 0,
                        "payload_docs_n": 0,
                    }
                )
            continue

        transformed_ok += 1
        pl = tr_res.payload
        ex = pl.get("extras") if isinstance(pl.get("extras"), dict) else {}
        tr_docs_in = ex.get("documentos") if isinstance(ex.get("documentos"), list) else []
        tr_docs_raw = []
        for d in tr_docs_in:
            if isinstance(d, dict):
                tr_docs_raw.append({"titulo": d.get("nome") or d.get("titulo") or "Documento", "url": d.get("url") or d.get("link") or "", "origem": "extras.documentos"})
        tr_docs = _normalize_docs(tr_docs_raw, str(pl.get("link") or base_link), default_status="nao_baixado")
        tr_pdf = str(ex.get("pdf_url") or "")
        tr_pdf_docs_n, tr_non_pdf_docs_n = _count_docs_by_format(tr_docs)

        loader.get_default_org_id = lambda: 11  # type: ignore[method-assign]
        mapped, extras_new = loader.map_to_db_schema(pl)
        merged = {**mapped, "extras": extras_new}
        stripped = loader._strip_payload(merged)
        payload_pdf = str(stripped.get("pdf_url") or "")
        payload_ex = extras_new if isinstance(extras_new, dict) else {}
        payload_docs_in = payload_ex.get("documentos") if isinstance(payload_ex.get("documentos"), list) else []
        payload_docs = _normalize_docs(
            [
                {"titulo": d.get("nome") or d.get("titulo") or "Documento", "url": d.get("url") or d.get("link") or "", "origem": "payload.extras.documentos"}
                for d in payload_docs_in
                if isinstance(d, dict)
            ],
            str(pl.get("link") or base_link),
            default_status="nao_baixado",
        )
        payload_pdf_docs_n, payload_non_pdf_docs_n = _count_docs_by_format(payload_docs)

        status_dl, err_dl = _sample_download_status(pl)
        if status_dl == "falhou":
            failures.append(
                {
                    "fonte": source,
                    "titulo": str(pl.get("titulo") or "")[:200],
                    "link": str(pl.get("link") or "")[:400],
                    "pdf_url": tr_pdf,
                    "status_download": status_dl,
                    "erro_download": err_dl,
                }
            )

        if raw_has_pdf and not tr_pdf:
            losses.append(
                {
                    "fonte": source,
                    "etapa": "bruto->transformado",
                    "motivo": "pdf_url_perdido",
                    "titulo": str(pl.get("titulo") or "")[:200],
                    "link": str(pl.get("link") or "")[:400],
                    "raw_pdf_url": raw_pdf,
                    "transformado_pdf_url": tr_pdf,
                    "payload_pdf_url": payload_pdf,
                    "raw_docs_n": len(raw_docs),
                    "transformado_docs_n": len(tr_docs),
                    "payload_docs_n": len(payload_docs),
                }
            )
        if tr_pdf and (not payload_pdf or payload_pdf != tr_pdf):
            losses.append(
                {
                    "fonte": source,
                    "etapa": "transformado->payload",
                    "motivo": "pdf_url_payload_inconsistente",
                    "titulo": str(pl.get("titulo") or "")[:200],
                    "link": str(pl.get("link") or "")[:400],
                    "raw_pdf_url": raw_pdf,
                    "transformado_pdf_url": tr_pdf,
                    "payload_pdf_url": payload_pdf,
                    "raw_docs_n": len(raw_docs),
                    "transformado_docs_n": len(tr_docs),
                    "payload_docs_n": len(payload_docs),
                }
            )
        if raw_has_docs and not tr_docs:
            losses.append(
                {
                    "fonte": source,
                    "etapa": "bruto->transformado",
                    "motivo": "documentos_perdidos",
                    "titulo": str(pl.get("titulo") or "")[:200],
                    "link": str(pl.get("link") or "")[:400],
                    "raw_pdf_url": raw_pdf,
                    "transformado_pdf_url": tr_pdf,
                    "payload_pdf_url": payload_pdf,
                    "raw_docs_n": len(raw_docs),
                    "transformado_docs_n": len(tr_docs),
                    "payload_docs_n": len(payload_docs),
                }
            )
        if raw_non_pdf_docs_n > 0 and tr_non_pdf_docs_n == 0:
            losses.append(
                {
                    "fonte": source,
                    "etapa": "bruto->transformado",
                    "motivo": "documentos_nao_pdf_perdidos",
                    "titulo": str(pl.get("titulo") or "")[:200],
                    "link": str(pl.get("link") or "")[:400],
                    "raw_pdf_url": raw_pdf,
                    "transformado_pdf_url": tr_pdf,
                    "payload_pdf_url": payload_pdf,
                    "raw_docs_n": len(raw_docs),
                    "transformado_docs_n": len(tr_docs),
                    "payload_docs_n": len(payload_docs),
                }
            )

        cnt["raw_pdf"] += 1 if raw_has_pdf else 0
        cnt["raw_docs"] += 1 if raw_has_docs else 0
        cnt["tr_pdf"] += 1 if bool(tr_pdf) else 0
        cnt["tr_docs"] += 1 if len(tr_docs) > 0 else 0
        cnt["payload_pdf"] += 1 if bool(payload_pdf) else 0
        cnt["payload_docs"] += 1 if len(payload_docs) > 0 else 0
        cnt["raw_docs_pdf"] += 1 if raw_pdf_docs_n > 0 else 0
        cnt["raw_docs_non_pdf"] += 1 if raw_non_pdf_docs_n > 0 else 0
        cnt["tr_docs_pdf"] += 1 if tr_pdf_docs_n > 0 else 0
        cnt["tr_docs_non_pdf"] += 1 if tr_non_pdf_docs_n > 0 else 0
        cnt["payload_docs_pdf"] += 1 if payload_pdf_docs_n > 0 else 0
        cnt["payload_docs_non_pdf"] += 1 if payload_non_pdf_docs_n > 0 else 0
        cnt["download_fail"] += 1 if status_dl == "falhou" else 0
        cnt["download_success"] += 1 if status_dl == "sucesso" else 0
        cnt["perdas_pdf"] += 1 if (raw_pdf_docs_n > 0 and tr_pdf_docs_n == 0) else 0
        cnt["perdas_nao_pdf"] += 1 if (raw_non_pdf_docs_n > 0 and tr_non_pdf_docs_n == 0) else 0
        for d in tr_docs:
            fmt = str(d.get("formato") or "outro").lower()
            cnt[f"fmt_{fmt}"] += 1

        links_info = _check_links(tr_docs)
        cnt["links_invalidos"] += links_info["links_invalidos"]
        cnt["links_relativos_restantes"] += links_info["links_relativos_restantes"]
        cnt["links_quebrados"] += links_info["links_quebrados"]
        cnt["duplicados_documentos"] += links_info["duplicados"]

        if len(examples) < 15:
            examples.append(
                {
                    "fonte": source,
                    "titulo": str(pl.get("titulo") or "")[:220],
                    "link": str(pl.get("link") or "")[:450],
                    "raw_pdf_url": raw_pdf,
                    "transformado_pdf_url": tr_pdf,
                    "payload_pdf_url": payload_pdf,
                    "raw_docs_n": len(raw_docs),
                    "transformado_docs_n": len(tr_docs),
                    "payload_docs_n": len(payload_docs),
                    "status_download": status_dl,
                    "erro_download": err_dl,
                    "docs_transformado_amostra": tr_docs[:3],
                }
            )

    return {
        "fonte": source,
        "arquivo": str(json_path.relative_to(ROOT)),
        "itens_amostra": len(items),
        "transformados": transformed_ok,
        "rejeitados": int(cnt["rejeitados"]),
        "raw_com_pdf_url": int(cnt["raw_pdf"]),
        "raw_com_documentos": int(cnt["raw_docs"]),
        "transformado_com_pdf_url": int(cnt["tr_pdf"]),
        "transformado_com_documentos": int(cnt["tr_docs"]),
        "payload_com_pdf_url": int(cnt["payload_pdf"]),
        "payload_com_documentos": int(cnt["payload_docs"]),
        "bruto_com_documentos_pdf": int(cnt["raw_docs_pdf"]),
        "bruto_com_documentos_nao_pdf": int(cnt["raw_docs_non_pdf"]),
        "transformado_com_documentos_pdf": int(cnt["tr_docs_pdf"]),
        "transformado_com_documentos_nao_pdf": int(cnt["tr_docs_non_pdf"]),
        "payload_com_documentos_pdf": int(cnt["payload_docs_pdf"]),
        "payload_com_documentos_nao_pdf": int(cnt["payload_docs_non_pdf"]),
        "perdas_pdf": int(cnt["perdas_pdf"]),
        "perdas_nao_pdf": int(cnt["perdas_nao_pdf"]),
        "downloads_falharam": int(cnt["download_fail"]),
        "downloads_sucesso": int(cnt["download_success"]),
        "links_invalidos": int(cnt["links_invalidos"]),
        "links_relativos_restantes": int(cnt["links_relativos_restantes"]),
        "links_quebrados": int(cnt["links_quebrados"]),
        "duplicados_documentos": int(cnt["duplicados_documentos"]),
        "formatos_detectados": {
            k.replace("fmt_", ""): int(v)
            for k, v in cnt.items()
            if k.startswith("fmt_")
        },
        "losses": losses[:80],
        "download_failures": failures[:80],
        "examples": examples,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def _write_md_summary(out_dir: Path, summary: Dict[str, Any], by_source: List[Dict[str, Any]]) -> None:
    lines = [
        "# Auditoria documentos/PDF (dry-run)",
        "",
        f"- Gerado: `{summary['data_auditoria']}`",
        f"- Fontes: `{','.join(summary['fontes'])}`",
        f"- Itens analisados: **{summary['itens_analisados']}**",
        "",
        "## Agregado",
        "",
        f"- Itens com PDF no bruto: **{summary['raw_com_pdf_url']}**",
        f"- Itens com docs no bruto: **{summary['raw_com_documentos']}**",
        f"- Preservados no transformado (pdf/docs): **{summary['transformado_com_pdf_url']} / {summary['transformado_com_documentos']}**",
        f"- Preservados no payload (pdf/docs): **{summary['payload_com_pdf_url']} / {summary['payload_com_documentos']}**",
        f"- Documentos não-PDF (bruto/transformado/payload): **{summary['bruto_com_documentos_nao_pdf']} / {summary['transformado_com_documentos_nao_pdf']} / {summary['payload_com_documentos_nao_pdf']}**",
        f"- Perdas PDF vs não-PDF: **{summary['perdas_pdf']} / {summary['perdas_nao_pdf']}**",
        f"- Falhas de download detectadas: **{summary['downloads_falharam']}**",
        f"- Duplicados removidos (estimado): **{summary['duplicados_documentos']}**",
        "",
        "## Por fonte",
        "",
        "| fonte | amostra | raw pdf | tr pdf | payload pdf | raw docs | tr docs | payload docs | falhas dl | perdas |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in by_source:
        if s.get("erro"):
            lines.append(f"| {s.get('fonte', '')} | — | — | — | — | — | — | — | — | — |")
            continue
        lines.append(
            f"| {s['fonte']} | {s.get('itens_amostra', 0)} | {s.get('raw_com_pdf_url', 0)} | {s.get('transformado_com_pdf_url', 0)} | "
            f"{s.get('payload_com_pdf_url', 0)} | {s.get('raw_com_documentos', 0)} | {s.get('transformado_com_documentos', 0)} | "
            f"{s.get('payload_com_documentos', 0)} | {s.get('downloads_falharam', 0)} | {len(s.get('losses') or [])} |"
        )
    fmt = summary.get("formatos_detectados") or {}
    if fmt:
        lines.extend(["", "## Formatos detectados", ""])
        for k, v in sorted(fmt.items(), key=lambda kv: kv[1], reverse=True):
            lines.append(f"- {k}: {v}")
    lines.extend(
        [
            "",
            "## Fontes com pior preservação",
            "",
        ]
    )
    for row in summary.get("fontes_pior_preservacao", [])[:6]:
        lines.append(f"- {row['fonte']}: score={row['score_perda']:.3f}")
    (out_dir / "audit_docs_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources", default=",".join(TARGET_SOURCES))
    ap.add_argument("--max-items", type=int, default=25)
    ap.add_argument("--output-dir", default=str(OUT_DEFAULT))
    ap.add_argument("--no-skip-pdf", action="store_true")
    args = ap.parse_args()

    out_dir = (Path(args.output_dir) if Path(args.output_dir).is_absolute() else (ROOT / args.output_dir)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    sources = [s.strip().lower() for s in args.sources.split(",") if s.strip()]
    by_source: List[Dict[str, Any]] = []
    all_losses: List[Dict[str, Any]] = []
    all_failures: List[Dict[str, Any]] = []
    all_examples: List[Dict[str, Any]] = []

    for src in sources:
        jp = _discover_source_json(src)
        if not jp:
            by_source.append({"fonte": src, "arquivo": "", "erro": "json_nao_encontrado"})
            continue
        try:
            block = audit_one_source(jp, args.max_items, no_skip_pdf=args.no_skip_pdf)
        except Exception as exc:
            block = {"fonte": src, "arquivo": str(jp.relative_to(ROOT)), "erro": str(exc)}
        by_source.append(block)
        all_losses.extend(block.get("losses") or [])
        all_failures.extend(block.get("download_failures") or [])
        all_examples.extend(block.get("examples") or [])

    def _sum(k: str) -> int:
        return sum(int(b.get(k) or 0) for b in by_source if isinstance(b, dict))

    formatos_counter: Counter[str] = Counter()
    for b in by_source:
        if not isinstance(b, dict):
            continue
        f_map = b.get("formatos_detectados") if isinstance(b.get("formatos_detectados"), dict) else {}
        for k, v in f_map.items():
            try:
                formatos_counter[str(k)] += int(v)
            except (TypeError, ValueError):
                continue

    worst: List[Dict[str, Any]] = []
    for b in by_source:
        if not isinstance(b, dict) or b.get("erro"):
            continue
        raw_docs = int(b.get("raw_com_documentos") or 0)
        raw_pdf = int(b.get("raw_com_pdf_url") or 0)
        denom = max(1, raw_docs + raw_pdf)
        kept = int(b.get("transformado_com_documentos") or 0) + int(b.get("transformado_com_pdf_url") or 0)
        score = max(0.0, 1.0 - (kept / denom))
        worst.append({"fonte": b.get("fonte"), "score_perda": score})
    worst.sort(key=lambda x: x["score_perda"], reverse=True)

    summary = {
        "data_auditoria": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fontes": sources,
        "max_items_por_fonte": args.max_items,
        "pdf_skip": not args.no_skip_pdf,
        "itens_analisados": _sum("itens_amostra"),
        "raw_com_pdf_url": _sum("raw_com_pdf_url"),
        "raw_com_documentos": _sum("raw_com_documentos"),
        "transformado_com_pdf_url": _sum("transformado_com_pdf_url"),
        "transformado_com_documentos": _sum("transformado_com_documentos"),
        "payload_com_pdf_url": _sum("payload_com_pdf_url"),
        "payload_com_documentos": _sum("payload_com_documentos"),
        "bruto_com_documentos_pdf": _sum("bruto_com_documentos_pdf"),
        "bruto_com_documentos_nao_pdf": _sum("bruto_com_documentos_nao_pdf"),
        "transformado_com_documentos_pdf": _sum("transformado_com_documentos_pdf"),
        "transformado_com_documentos_nao_pdf": _sum("transformado_com_documentos_nao_pdf"),
        "payload_com_documentos_pdf": _sum("payload_com_documentos_pdf"),
        "payload_com_documentos_nao_pdf": _sum("payload_com_documentos_nao_pdf"),
        "perdas_pdf": _sum("perdas_pdf"),
        "perdas_nao_pdf": _sum("perdas_nao_pdf"),
        "downloads_falharam": _sum("downloads_falharam"),
        "downloads_sucesso": _sum("downloads_sucesso"),
        "links_invalidos": _sum("links_invalidos"),
        "links_relativos_restantes": _sum("links_relativos_restantes"),
        "links_quebrados": _sum("links_quebrados"),
        "duplicados_documentos": _sum("duplicados_documentos"),
        "perdas_total": len(all_losses),
        "fontes_pior_preservacao": worst[:10],
        "formatos_detectados": dict(sorted(formatos_counter.items(), key=lambda kv: kv[1], reverse=True)),
    }

    (out_dir / "audit_docs_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "audit_docs_by_source.json").write_text(json.dumps(by_source, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "audit_docs_losses.json").write_text(json.dumps(all_losses[:500], ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "audit_docs_download_failures.json").write_text(
        json.dumps(all_failures[:500], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "audit_docs_examples.json").write_text(json.dumps(all_examples[:300], ensure_ascii=False, indent=2), encoding="utf-8")
    _write_md_summary(out_dir, summary, by_source)

    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
