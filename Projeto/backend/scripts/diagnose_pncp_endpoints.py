#!/usr/bin/env python3
"""
Diagnóstico isolado de endpoints públicos PNCP (somente GET).

Não grava no banco, não chama loader. Saídas em audit_reports_blocked_sources/.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "audit_reports_blocked_sources"
OUT_JSON = OUT_DIR / "pncp_endpoint_diagnosis.json"
OUT_MD = OUT_DIR / "pncp_endpoint_diagnosis.md"
OUT_SAMPLES = OUT_DIR / "pncp_endpoint_samples.json"

CONSULTA_PUBLICACAO = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
LEGACY_PNCP_PREFIX = "https://pncp.gov.br/api/pncp/v1/contratacoes/publicacao"

HEADERS = {
    "User-Agent": "EditalFinderBot/1.0 (+https://github.com; institutional public data)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(HEADERS)
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.35,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    return s


def _mask_cnpj(s: str) -> str:
    return re.sub(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b", "[CNPJ]", s)


def _mask(obj: Any, depth: int = 0) -> Any:
    if depth > 5:
        return "[trunc]"
    if isinstance(obj, str):
        t = _mask_cnpj(obj)
        return t[:600] + ("…" if len(t) > 600 else "")
    if isinstance(obj, dict):
        return {str(k): _mask(v, depth + 1) for k, v in list(obj.items())[:60]}
    if isinstance(obj, list):
        return [_mask(x, depth + 1) for x in obj[:15]]
    return obj


def _rows(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for k in ("data", "content", "items", "resultado", "result"):
            v = payload.get(k)
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
    return []


def _get(
    session: requests.Session,
    url: str,
    params: Dict[str, Any],
    timeout: Tuple[int, int],
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    t0 = time.time()
    rec: Dict[str, Any] = {"url": url, "params": params}
    rows_out: List[Dict[str, Any]] = []
    try:
        r = session.get(url, params=params, timeout=timeout)
        rec["status"] = r.status_code
        rec["elapsed_ms"] = int((time.time() - t0) * 1000)
        ct = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        rec["content_type"] = ct
        if "json" in ct or (r.text or "").strip().startswith("{"):
            try:
                body = r.json()
                rec["json_keys"] = list(body.keys())[:30] if isinstance(body, dict) else "list"
                if isinstance(body, dict) and "message" in body:
                    rec["api_message"] = body.get("message")
                rows_out = _rows(body)
                rec["row_count"] = len(rows_out)
                if rows_out:
                    rec["first_row_keys"] = sorted(rows_out[0].keys())[:45]
            except Exception as exc:
                rec["json_error"] = str(exc)
                rec["text_preview"] = (r.text or "")[:400]
        else:
            rec["text_preview"] = (r.text or "")[:400]
    except Exception as exc:
        rec["status"] = -1
        rec["elapsed_ms"] = int((time.time() - t0) * 1000)
        rec["error"] = str(exc)
    return rec, rows_out


def _date_win(days: int) -> Tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=days - 1)
    return start.strftime("%Y%m%d"), end.strftime("%Y%m%d")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--connect-timeout", type=int, default=12)
    ap.add_argument("--read-timeout", type=int, default=75)
    ap.add_argument("--quick", action="store_true", help="Menos requisições (sem varrer todas as UFs).")
    args = ap.parse_args()
    timeout = (args.connect_timeout, args.read_timeout)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = _session()

    tentativas: List[Dict[str, Any]] = []
    samples: List[Dict[str, Any]] = []

    def run(name: str, url: str, params: Dict[str, Any]) -> None:
        rec, rows_out = _get(session, url, params, timeout)
        rec["name"] = name
        tentativas.append(rec)
        if rows_out:
            samples.append({"name": name, "params": params, "first_row_masked": _mask(rows_out[0])})

    # --- Erro esperado: parâmetros obrigatórios (documentação PNCP Consulta) ---
    run("sem_data_sem_modalidade", CONSULTA_PUBLICACAO, {"pagina": 1, "tamanhoPagina": 10})
    di, df = _date_win(3)
    run("com_data_sem_modalidade", CONSULTA_PUBLICACAO, {"pagina": 1, "tamanhoPagina": 10, "dataInicial": di, "dataFinal": df})
    run("tamanhoPagina_menor_10", CONSULTA_PUBLICACAO, {"pagina": 1, "tamanhoPagina": 5, "dataInicial": di, "dataFinal": df, "codigoModalidadeContratacao": 8})

    # --- Combinações válidas típicas ---
    for days in (3, 7) if args.quick else (3, 7, 14, 30):
        di, df = _date_win(days)
        for mod in (8, 6) if args.quick else (8, 6, 1, 3, 4, 5):
            run(
                f"ok_nacional_{days}d_mod{mod}",
                CONSULTA_PUBLICACAO,
                {
                    "pagina": 1,
                    "tamanhoPagina": 10,
                    "dataInicial": di,
                    "dataFinal": df,
                    "codigoModalidadeContratacao": mod,
                },
            )

    run("legado_pncp_v1_prefixo", LEGACY_PNCP_PREFIX, {"pagina": 1, "tamanhoPagina": 10, "dataInicial": di, "dataFinal": df, "codigoModalidadeContratacao": 8})

    if not args.quick:
        for uf in ("DF", "RJ"):
            run(
                f"com_uf_{uf}_3d_mod8",
                CONSULTA_PUBLICACAO,
                {
                    "pagina": 1,
                    "tamanhoPagina": 10,
                    "dataInicial": di,
                    "dataFinal": df,
                    "codigoModalidadeContratacao": 8,
                    "uf": uf,
                },
            )

    melhor = None
    best_n = -1
    for t in tentativas:
        n = int(t.get("row_count") or 0)
        if n > best_n:
            best_n = n
            melhor = {k: t[k] for k in ("name", "url", "params", "status", "row_count", "elapsed_ms") if k in t}

    diagnosis = {
        "endpoint_principal": CONSULTA_PUBLICACAO,
        "observacao_api": (
            "GET /v1/contratacoes/publicacao exige dataInicial, dataFinal, codigoModalidadeContratacao e pagina; "
            "tamanhoPagina minimo 10. Janelas muito amplas sem filtro podem demorar ou estourar timeout."
        ),
        "melhor_amostra_pagina1": melhor,
        "tentativas": tentativas,
    }

    OUT_JSON.write_text(json.dumps(diagnosis, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_SAMPLES.write_text(json.dumps(samples[:25], ensure_ascii=False, indent=2), encoding="utf-8")

    linhas = [
        "# Diagnóstico PNCP — API pública de consulta",
        "",
        "## Endpoint funcional",
        "",
        f"- **URL:** `{CONSULTA_PUBLICACAO}`",
        "- **Método:** GET público (sem autenticação no diagnóstico).",
        "",
        "## Parâmetros obrigatórios (comportamento observado + manual/Swagger)",
        "",
        "| Parâmetro | Observação |",
        "|-----------|------------|",
        "| `dataInicial` | AAAAMMDD; sem isso a API responde 400. |",
        "| `dataFinal` | AAAAMMDD. |",
        "| `codigoModalidadeContratacao` | Inteiro (tabela de modalidades); sem isso 400. |",
        "| `pagina` | Paginação (1-based nas amostras). |",
        "| `tamanhoPagina` | Mínimo **10** (`must be greater than or equal to 10`). |",
        "",
        "## Parâmetros opcionais úteis",
        "",
        "- `uf`: reduz volume e estabiliza tempo de resposta em alguns casos.",
        "- `codigoMunicipioIbge`, `cnpj`, `codigoUnidadeAdministrativa`, `codigoModoDisputa`, `idUsuario` (refino).",
        "",
        "## Resposta e campos úteis",
        "",
        "- Corpo JSON paginado: lista em **`data`** (schema atual).",
        "- Identificação: `numeroControlePNCP`, `processo`, `anoCompra` + `sequencialCompra`.",
        "- Objeto e prazos: `objetoCompra`, `dataPublicacaoPncp` / `dataInclusao`, `dataEncerramentoProposta`, `dataAberturaProposta`.",
        "- Órgão/unidade: objetos aninhados `orgaoEntidade` e `unidadeOrgao` (razão social, UF, município) — o crawler deve achatar para compatibilidade.",
        "- Modalidade: `modalidadeId`, `modalidadeNome`.",
        "- Links/anexos: `linkSistemaOrigem`, `linkProcessoEletronico`, etc. (varia por registro).",
        "",
        "## Prefixo legado",
        "",
        f"- `{LEGACY_PNCP_PREFIX}` tende a **404** (não usar).",
        "",
        "## Melhor tentativa (mais linhas na página 1)",
        "",
        "```json",
        json.dumps(melhor, ensure_ascii=False, indent=2) if melhor else "{}",
        "```",
        "",
        f"- Relatório JSON: `{OUT_JSON}`",
        f"- Amostras mascaradas: `{OUT_SAMPLES}`",
    ]
    OUT_MD.write_text("\n".join(linhas), encoding="utf-8")
    print(str(OUT_DIR))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
