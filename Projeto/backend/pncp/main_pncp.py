from __future__ import annotations

import csv
import json
import os
import time
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from keyword_taxonomy import classify_thematic_tags, has_interest_keyword

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
JSON_PATH = OUTPUT_DIR / "pncp_editais.json"
CSV_PATH = OUTPUT_DIR / "pncp_editais.csv"

HEADERS = {
    "User-Agent": "EditalFinderBot/1.0 (+https://github.com; institutional public data)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9",
}
# A API de consulta PNCP exige leitura tolerante a respostas grandes; (connect, read).
REQUEST_TIMEOUT = (12, 38)
DISCOVER_TIMEOUT = (8, 24)
# Parâmetros operacionais conservadores (sobrescrever por ambiente: PNCP_*).
PAGE_SIZE = max(10, int(os.environ.get("PNCP_PAGE_SIZE", "10")))
MAX_PAGES = max(1, int(os.environ.get("PNCP_MAX_PAGES", "2")))
PNCP_TOTAL_DAYS = max(3, int(os.environ.get("PNCP_TOTAL_DAYS", "9")))
PNCP_CHUNK_DAYS = max(1, int(os.environ.get("PNCP_CHUNK_DAYS", "3")))
CONSULTA_PUBLICACAO_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"


def _build_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=1,
        connect=2,
        read=1,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update(HEADERS)
    return s


def _candidate_urls() -> Iterable[str]:
    """Somente endpoint de consulta pública documentado; /api/pncp/v1 retorna 404."""
    return (CONSULTA_PUBLICACAO_URL,)


def _flatten_pncp_row(item: Dict[str, Any]) -> Dict[str, Any]:
    """Compat: respostas recentes trazem orgaoEntidade/unidadeOrgao aninhados."""
    out = dict(item)
    oe = item.get("orgaoEntidade")
    if isinstance(oe, dict):
        out.setdefault("orgaoEntidadeRazaoSocial", oe.get("razaoSocial"))
        out.setdefault("orgaoEntidadeCnpj", oe.get("cnpj"))
    uo = item.get("unidadeOrgao")
    if isinstance(uo, dict):
        out.setdefault("unidadeOrgaoNomeUnidade", uo.get("nomeUnidade"))
        out.setdefault("unidadeOrgaoUfSigla", uo.get("ufSigla"))
        out.setdefault("unidadeOrgaoUfNome", uo.get("ufNome"))
        out.setdefault("unidadeOrgaoMunicipioNome", uo.get("municipioNome"))
    al = item.get("amparoLegal")
    if isinstance(al, dict):
        out.setdefault("amparoLegalNome", al.get("nome"))
    return out


def _is_generic_pncp_portal_url(url: str) -> bool:
    u = url.split("?", 1)[0].rstrip("/").lower()
    return u in (
        "https://pncp.gov.br",
        "http://pncp.gov.br",
        "https://www.pncp.gov.br",
        "http://www.pncp.gov.br",
        "https://pncp.gov.br/app",
        "http://pncp.gov.br/app",
    )


def _extract_link(item: Dict[str, Any]) -> str:
    for key in ("linkSistemaOrigem", "link", "url", "urlPortal", "uri"):
        value = item.get(key)
        if isinstance(value, str) and value.startswith("http") and not _is_generic_pncp_portal_url(value):
            return value
    numero = item.get("numeroControlePNCP")
    if numero:
        return f"https://pncp.gov.br/app/editais/{numero}"
    return "https://pncp.gov.br/app/"


def _extract_title(item: Dict[str, Any]) -> str:
    for key in ("objetoCompra", "objeto", "descricao", "titulo"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "Contratacao publica PNCP"


def _extract_date(item: Dict[str, Any], *keys: str) -> Optional[str]:
    for key in keys:
        value = item.get(key)
        if not isinstance(value, str):
            continue
        raw = value.strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
            try:
                return datetime.strptime(raw[:26], fmt).date().isoformat()
            except ValueError:
                continue
        if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
            return raw[:10]
    return None


def _extract_value(item: Dict[str, Any]) -> Optional[str]:
    for key in ("valorTotalEstimado", "valorEstimado", "valorTotalHomologado", "valor"):
        value = item.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return None


def _documents_from_item(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []

    def add(nome: str, url: Any, tipo: Optional[str] = None) -> None:
        if isinstance(url, str) and url.startswith("http"):
            row: Dict[str, Any] = {"nome": nome[:200], "url": url[:2000]}
            if tipo:
                row["tipo"] = tipo
            docs.append(row)

    lo = item.get("linkSistemaOrigem")
    if isinstance(lo, str) and lo.startswith("http"):
        add("Sistema de origem (compras)", lo, "sistema_origem")
    lp = item.get("linkProcessoEletronico")
    if isinstance(lp, str) and lp.startswith("http"):
        add("Processo eletrônico", lp, "processo_eletronico")
    ld = item.get("linkDocumento")
    if isinstance(ld, str) and ld.startswith("http"):
        tdoc = "edital_pncp" if ld.lower().split("?", 1)[0].endswith(".pdf") else "edital_pncp"
        add("Documento / edital (PNCP)", ld, tdoc)

    for key in ("link", "url", "urlPortal", "uri", "linkExterno"):
        add(key, item.get(key))

    for k, v in item.items():
        if isinstance(v, str) and v.startswith("http") and (".pdf" in v.lower() or "document" in k.lower()):
            add(k, v)
        if isinstance(v, list):
            for it in v:
                if not isinstance(it, dict):
                    continue
                add(str(it.get("nome") or it.get("titulo") or "anexo"), it.get("url") or it.get("uri") or it.get("link"))

    seen = set()
    out: List[Dict[str, Any]] = []
    for d in docs:
        u = d.get("url", "").strip()
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(d)
    return out


def _has_procurement_signal(text: str) -> bool:
    low = text.lower()
    markers = (
        "pncp",
        "contrata",
        "licit",
        "pregão",
        "pregao",
        "processo",
        "compra",
        "contrato",
        "edital",
        "objeto",
        "órgão",
        "orgao",
    )
    return any(m in low for m in markers)


def _normalize_item(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    title = _extract_title(item)
    desc = " ".join(
        x for x in [title, str(item.get("informacaoComplementar") or ""), str(item.get("modalidadeNome") or "")]
        if x
    ).strip()
    if not (_has_procurement_signal(desc) or has_interest_keyword(desc)):
        return None

    tags = classify_thematic_tags(desc)
    item_id = str(item.get("numeroControlePNCP") or "")
    if not item_id:
        item_id = f"{item.get('anoCompra', '')}-{item.get('sequencialCompra', '')}"
    numero_processo = str(item.get("processo") or item.get("numeroProcesso") or "").strip()
    if not item_id.strip() and not numero_processo:
        return None
    docs = _documents_from_item(item)
    pdf_url = ""
    for d in docs:
        if d["url"].lower().split("?", 1)[0].endswith(".pdf"):
            pdf_url = d["url"]
            break

    return {
        "titulo": title[:250],
        "descricao": desc[:3500],
        "link": _extract_link(item),
        "fonte": "PNCP",
        "data_publicacao": _extract_date(item, "dataPublicacaoPncp", "dataPublicacao", "dataInclusao"),
        "fim_inscricao": _extract_date(item, "dataEncerramentoProposta", "dataAberturaProposta"),
        "situacao": str(item.get("situacaoCompraNome") or item.get("situacaoCompra") or "Em andamento"),
        "valor": _extract_value(item),
        "programa": str(item.get("orgaoEntidadeRazaoSocial") or "Contratacoes Publicas"),
        "acao": str(item.get("modalidadeNome") or "Licitacao"),
        "tipo_recurso": "Contratacao Publica",
        "extras": {
            "pais": "brasil",
            "regiao": "brasil",
            "estado": (item.get("unidadeOrgaoUfSigla") or item.get("unidadeOrgaoUfNome") or ""),
            "municipio": item.get("unidadeOrgaoMunicipioNome") or "",
            "orgao_responsavel": item.get("orgaoEntidadeRazaoSocial") or "",
            "instituicao": item.get("orgaoEntidadeRazaoSocial") or "",
            "numero_edital": str(item.get("numeroControlePNCP") or ""),
            "numero_programa": "",
            "numero_processo": numero_processo,
            "codigo_oportunidade": str(item.get("numeroControlePNCP") or ""),
            "modalidade": item.get("modalidadeNome") or "",
            "tipo_oportunidade": "compra_publica",
            "tipo_recurso": "contrato_publico",
            "natureza_recurso": "contratacao_publica",
            "reembolsavel": None,
            "publico_alvo": "fornecedores",
            "porte_empresa": [],
            "setor_economico": [],
            "area_tematica": tags,
            "area_cientifica": [],
            "area_tecnologica": [],
            "regiao_atendida": [],
            "elegibilidade": "",
            "objetivo": _extract_title(item)[:700],
            "escopo": str(item.get("informacaoComplementar") or "")[:1500],
            "itens_financiaveis": [],
            "itens_nao_financiaveis": [],
            "valor_total": _extract_value(item) or "",
            "valor_por_projeto": "",
            "valor_minimo": "",
            "valor_maximo": "",
            "taxa_juros": "",
            "carencia": "",
            "prazo_pagamento": "",
            "contrapartida": "",
            "prazo_execucao": "",
            "cronograma": [],
            "documentos_exigidos": [],
            "documentos": docs,
            "pdf_url": pdf_url,
            "pdf_resumo": "",
            "contato": "",
            "url_listagem": CONSULTA_PUBLICACAO_URL,
            "url_detalhe": _extract_link(item),
            "metodo_extracao": "api_pncp",
            "pncp_id": item_id,
            "numero_controle_pncp": item_id,
            "orgao_cnpj": item.get("orgaoEntidadeCnpj"),
            "orgao_nome": item.get("orgaoEntidadeRazaoSocial"),
            "unidade_nome": item.get("unidadeOrgaoNomeUnidade"),
            "modalidade_id": item.get("modalidadeId"),
            "modalidade_nome": item.get("modalidadeNome"),
            "modo_disputa_id": item.get("modoDisputaId"),
            "modo_disputa_nome": item.get("modoDisputaNome"),
            "amparo_legal": item.get("amparoLegalNome"),
            "uf_nome": item.get("unidadeOrgaoUfNome"),
            "municipio_nome": item.get("unidadeOrgaoMunicipioNome"),
            "coletado_em": datetime.now().date().isoformat(),
            "thematic_tags": tags,
            "thematic_confidence": min(1.0, 0.35 + 0.1 * len(tags)) if tags else 0.0,
            "public_investment_scope": True,
            "observacoes": "",
        },
    }


def _request_page_with_params(
    session: requests.Session,
    url: str,
    page: int,
    page_size: int,
    extra_params: Optional[Dict[str, Any]] = None,
    *,
    timeout: Optional[tuple[int, int]] = None,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {"pagina": page, "tamanhoPagina": page_size}
    if extra_params:
        params.update(extra_params)
    response = session.get(url, timeout=timeout or REQUEST_TIMEOUT, params=params)
    response.raise_for_status()
    payload = response.json()
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("data", "content", "items", "resultado", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    return []


def _publicacao_extra(data_inicial: date, data_final: date, codigo_modalidade: int) -> Dict[str, Any]:
    return {
        "dataInicial": data_inicial.strftime("%Y%m%d"),
        "dataFinal": data_final.strftime("%Y%m%d"),
        "codigoModalidadeContratacao": codigo_modalidade,
    }


def _iter_date_chunks(*, total_days: int = 28, chunk_days: int = 7) -> List[tuple[date, date]]:
    """Janelas contíguas cobrindo os últimos total_days (incluindo hoje)."""
    end = date.today()
    start = end - timedelta(days=total_days - 1)
    chunks: List[tuple[date, date]] = []
    cur = start
    while cur <= end:
        chunk_end = min(cur + timedelta(days=chunk_days - 1), end)
        chunks.append((cur, chunk_end))
        cur = chunk_end + timedelta(days=1)
    # Semanas mais recentes primeiro: consultas nacionais amplas costumam estourar timeout em períodos antigos.
    return list(reversed(chunks))


def _discover_modalidade(session: requests.Session, url: str) -> Optional[int]:
    """
    API pública exige dataInicial, dataFinal e codigoModalidadeContratacao (Swagger PNCP Consulta).
    Testa janelas curtas e modalidades comuns até obter HTTP 200.
    """
    end = date.today()
    for span in (3, 7, 14):
        d0 = end - timedelta(days=span - 1)
        d1 = end
        for mod in (8, 6, 1, 3, 4, 5):
            extra = _publicacao_extra(d0, d1, mod)
            try:
                _request_page_with_params(session, url, 1, PAGE_SIZE, extra, timeout=DISCOVER_TIMEOUT)
                return mod
            except Exception:
                continue
    return None


def collect_pncp() -> List[Dict[str, Any]]:
    collected: List[Dict[str, Any]] = []
    seen_keys = set()
    session = _build_session()
    working_url = CONSULTA_PUBLICACAO_URL
    modality = _discover_modalidade(session, working_url)
    if modality is None:
        print("[PNCP] Nao foi possivel negociar parametros obrigatorios com a API de publicacao.")
        return []

    print(
        f"[PNCP] Usando codigoModalidadeContratacao={modality} com janelas de {PNCP_CHUNK_DAYS} dias "
        f"(ultimos {PNCP_TOTAL_DAYS} dias, blocos mais recentes primeiro)."
    )

    for chunk_start, chunk_end in _iter_date_chunks(total_days=PNCP_TOTAL_DAYS, chunk_days=PNCP_CHUNK_DAYS):
        extra = _publicacao_extra(chunk_start, chunk_end, modality)
        for page in range(1, MAX_PAGES + 1):
            try:
                rows = _request_page_with_params(session, working_url, page, PAGE_SIZE, extra)
            except Exception as exc:
                print(f"[PNCP] Falha chunk {chunk_start}->{chunk_end} pagina {page}: {exc}")
                break

            if not rows:
                break

            for row in rows:
                flat = _flatten_pncp_row(row)
                normalized = _normalize_item(flat)
                if not normalized:
                    continue
                dedupe_key = "|".join(
                    [
                        normalized.get("link") or "",
                        normalized.get("titulo") or "",
                        normalized.get("fonte") or "",
                        normalized.get("data_publicacao") or "",
                        normalized.get("fim_inscricao") or "",
                    ]
                )
                if dedupe_key in seen_keys:
                    continue
                seen_keys.add(dedupe_key)
                collected.append(normalized)

            if len(rows) < PAGE_SIZE:
                break

            time.sleep(0.35)

    return collected


def _fallback_items() -> List[Dict[str, Any]]:
    return [
        {
            "titulo": "PNCP - Portal Nacional de Contratações Públicas",
            "descricao": "Índice público de contratações e editais governamentais no PNCP.",
            "link": "https://pncp.gov.br/app/editais",
            "fonte": "PNCP",
            "data_publicacao": None,
            "fim_inscricao": None,
            "situacao": "Em andamento",
            "valor": None,
            "programa": "contratacoes_publicas",
            "acao": "licitacao",
            "tipo_recurso": "Contratacao Publica",
            "extras": {
                "pais": "brasil",
                "regiao": "brasil",
                "tipo_oportunidade": "compra_publica",
                "tipo_recurso": "contrato_publico",
                "natureza_recurso": "contratacao_publica",
                "orgao_responsavel": "PNCP",
                "instituicao": "Portal Nacional de Contratações Públicas",
                "url_listagem": "https://pncp.gov.br/app/editais",
                "url_detalhe": "https://pncp.gov.br/app/editais",
                "metodo_extracao": "fallback_public_index",
                "nivel_sensibilidade": "publico_institucional",
                "observacoes": "Endpoint oficial indisponível ou bloqueando parâmetros.",
            },
        }
    ]


def save_outputs(items: List[Dict[str, Any]]) -> None:
    with JSON_PATH.open("w", encoding="utf-8") as fp:
        json.dump(items, fp, ensure_ascii=False, indent=2)

    if not items:
        CSV_PATH.write_text("", encoding="utf-8")
        return
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(items[0].keys()))
        writer.writeheader()
        writer.writerows(items)


def main() -> None:
    print("[PNCP] Iniciando coleta de contratacoes publicas")
    items = collect_pncp()
    if not items:
        items = []
        print("[PNCP] Sem itens válidos de contratação nesta execução; fallback genérico desativado.")
    save_outputs(items)
    print(f"[PNCP] Registros salvos: {len(items)}")
    print(f"[PNCP] JSON: {JSON_PATH}")


if __name__ == "__main__":
    main()
