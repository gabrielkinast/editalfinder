from __future__ import annotations

import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from defense_intel import build_defense_extras, detect_keywords
from defense_source_common import save_outputs
from keyword_taxonomy import classify_thematic_tags

logger = logging.getLogger("pncp_defesa")
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter("[%(name)s] %(levelname)s: %(message)s"))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

HEADERS = {
    "User-Agent": "EditalFinderBot/1.0 (+https://github.com; institutional public data)",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

TIMEOUT = 35
MAX_PAGES = 15
# O gateway PNCP pode variar o tamanho aceito; descobrimos na primeira chamada bem-sucedida.
_PAGE_SIZES_TRY = (20, 50, 80, 100)


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(HEADERS)
    return session


def _candidate_urls() -> Iterable[str]:
    return (
        "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao",
        "https://pncp.gov.br/api/pncp/v1/contratacoes/publicacao",
    )


def _extract_link(item: Dict[str, Any]) -> str:
    for key in ("linkSistemaOrigem", "link", "url", "urlPortal", "uri"):
        value = item.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value.split("?", 1)[0]
    numero = item.get("numeroControlePNCP")
    if numero:
        return f"https://pncp.gov.br/app/editais/{numero}"
    return "https://pncp.gov.br/app/editais"


def _extract_title(row: Dict[str, Any]) -> str:
    for key in ("objetoCompra", "objeto", "descricao", "titulo"):
        v = row.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return "Contratacao PNCP"


def _extract_date(row: Dict[str, Any], *keys: str) -> Optional[str]:
    for key in keys:
        value = row.get(key)
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


def _extract_value(row: Dict[str, Any]) -> Optional[str]:
    for key in ("valorTotalEstimado", "valorEstimado", "valorTotalHomologado", "valor"):
        value = row.get(key)
        if isinstance(value, (int, float)) and value > 0:
            return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return None


def _dedupe_docs(docs: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    out: List[Dict[str, str]] = []
    for d in docs:
        u = (d.get("url") or "").strip()
        if not u or u in seen:
            continue
        seen.add(u)
        out.append({"nome": (d.get("nome") or "Documento")[:200], "url": u[:2000]})
    return out


def _documents_from_row(row: Dict[str, Any]) -> List[Dict[str, str]]:
    """Coleta URLs de documentos/PDF quando a API as expõe no objeto."""
    docs: List[Dict[str, str]] = []

    def add(nome: str, url: Any) -> None:
        if isinstance(url, str) and url.startswith("http"):
            docs.append({"nome": nome[:200], "url": url.strip()})

    add("Sistema de origem", row.get("linkSistemaOrigem"))
    add("Link externo", row.get("linkExterno"))
    add("Edital PNCP", row.get("linkDocumento"))
    add("Compra", row.get("linkCompra"))

    for key, val in row.items():
        if isinstance(val, str) and val.startswith("http") and (".pdf" in val.lower() or "documento" in key.lower()):
            add(str(key), val)
        if isinstance(val, list):
            for it in val:
                if not isinstance(it, dict):
                    continue
                u = it.get("url") or it.get("uri") or it.get("link") or it.get("linkDocumento")
                n = it.get("nome") or it.get("titulo") or it.get("descricao") or "Anexo"
                add(str(n)[:120], u)

    return _dedupe_docs(docs)


def _request_page(
    session: requests.Session,
    url: str,
    page: int,
    page_size: int,
    extra_params: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    params: Dict[str, Any] = {"pagina": page, "tamanhoPagina": page_size}
    if extra_params:
        params.update(extra_params)
    r = session.get(url, params=params, timeout=TIMEOUT)
    if r.status_code >= 400:
        snippet = (r.text or "")[:400].replace("\n", " ")
        logger.debug("HTTP %s %s — %s", r.status_code, r.url, snippet)
    r.raise_for_status()
    payload = r.json()
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("data", "content", "items", "resultado", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    return []


def _date_window_params(days: int = 300) -> Dict[str, str]:
    end = date.today()
    start = end - timedelta(days=days)
    return {
        "dataInicial": start.strftime("%Y%m%d"),
        "dataFinal": end.strftime("%Y%m%d"),
    }


def _discover_query_params(
    session: requests.Session, url: str, page_size: int
) -> Optional[Dict[str, Any]]:
    """
    A API de consulta pode aceitar só pagina/tamanho ou exigir janela de datas (e às vezes modalidade).
    Retorna extra_params a fundir nas requisições (ou {} se o modo simples funcionar).
    """
    # 1) Sem filtros de data
    try:
        _request_page(session, url, 1, page_size, None)
        return {}
    except Exception:
        pass

    # 2) Com janela de datas (últimos ~10 meses)
    for days in (300, 450, 730):
        extra = _date_window_params(days)
        try:
            _request_page(session, url, 1, page_size, extra)
            logger.info("API exige intervalo de datas; usando últimos %s dias.", days)
            return extra
        except Exception:
            continue

    # 3) Data + modalidade comum (pregão eletrônico = 6 em muitos catálogos PNCP)
    extra = {**_date_window_params(365), "codigoModalidadeContratacao": 6}
    try:
        _request_page(session, url, 1, page_size, extra)
        logger.info("API exige data + codigoModalidadeContratacao=6.")
        return extra
    except Exception:
        pass

    for mod in (8, 1, 3, 4, 5):
        extra = {**_date_window_params(365), "codigoModalidadeContratacao": mod}
        try:
            _request_page(session, url, 1, page_size, extra)
            logger.info("API exige data + codigoModalidadeContratacao=%s.", mod)
            return extra
        except Exception:
            continue

    return None


def _row_to_item(
    row: Dict[str, Any],
    *,
    listagem_url: str,
) -> Optional[Dict[str, Any]]:
    title = _extract_title(row)
    orgao = str(row.get("orgaoEntidadeRazaoSocial") or "")
    info = str(row.get("informacaoComplementar") or "")
    modal = str(row.get("modalidadeNome") or "")
    text = f"{title} {orgao} {info} {modal}".strip()

    if not detect_keywords(text):
        return None

    pncp_id = str(row.get("numeroControlePNCP") or "")
    if not pncp_id:
        pncp_id = f"{row.get('anoCompra', '')}-{row.get('sequencialCompra', '')}".strip("-")

    link = _extract_link(row)
    valor_str = _extract_value(row)
    docs = _documents_from_row(row)
    pdf_url = ""
    for d in docs:
        if d["url"].lower().endswith(".pdf"):
            pdf_url = d["url"]
            break

    tags = classify_thematic_tags(text)
    extras = build_defense_extras(
        text=text,
        source_name="PNCP Defesa",
        origem=link,
        pais="Brasil",
        orgao_contratante=orgao,
    )

    publico_alvo = ["fornecedores", "empresas", "defesa"]
    numero_proc = str(row.get("processo") or row.get("numeroProcesso") or "")

    extras.update(
        {
            "area": [],
            "tipo_oportunidade": "compra_publica",
            "tipo_recurso": "contrato_publico",
            "natureza_recurso": "contratacao_publica",
            "publico_alvo": publico_alvo,
            "publico_alvo_texto": "fornecedores; empresas; defesa",
            "setor_economico": ["defesa", "compras_publicas"],
            "area_cientifica": [],
            "area_tecnologica": [],
            "setor_estrategico": ["defesa", "seguranca_nacional"],
            "subtema": list(tags)[:12],
            "pais": "Brasil",
            "regiao": "brasil",
            "estado": row.get("unidadeOrgaoUfSigla") or row.get("unidadeOrgaoUfNome") or "",
            "municipio": row.get("unidadeOrgaoMunicipioNome") or "",
            "regiao_atendida": [],
            "valor_total": valor_str or "",
            "valor_por_projeto": "",
            "valor_minimo": "",
            "valor_maximo": "",
            "faixa_valor": "",
            "reembolsavel": None,
            "modalidade": modal,
            "orgao_responsavel": orgao,
            "instituicao": orgao,
            "numero_edital": pncp_id,
            "numero_chamada": str(row.get("numeroCompra") or row.get("numeroControlePncp") or ""),
            "numero_programa": "",
            "numero_processo": numero_proc,
            "codigo_oportunidade": pncp_id,
            "objetivo": title[:700],
            "escopo": info[:2000] if info else "",
            "documentos": docs,
            "documentos_exigidos": [],
            "pdf_url": pdf_url,
            "url_listagem": listagem_url,
            "url_detalhe": link,
            "metodo_extracao": "api_pncp_defesa",
            "numero_controle_pncp": pncp_id,
            "thematic_tags": tags,
            "thematic_confidence": min(1.0, 0.35 + 0.1 * len(tags)) if tags else 0.0,
            "nivel_sensibilidade": "publico_institucional",
            "metodo_classificacao": "crawler_hints",
            "classificacao_confianca": "media" if tags else "baixa",
            "palavras_chave_detectadas": list(tags)[:20],
            "observacoes": "",
            "orgao_cnpj": row.get("orgaoEntidadeCnpj"),
            "unidade_nome": row.get("unidadeOrgaoNomeUnidade"),
            "amparo_legal": row.get("amparoLegalNome"),
            "coletado_em": date.today().isoformat(),
        }
    )

    descricao = " ".join(x for x in (title, info, modal, orgao) if x)[:4000]

    return {
        "titulo": title[:250],
        "descricao": descricao,
        "link": link,
        "fonte": "PNCP Defesa",
        "data_publicacao": _extract_date(row, "dataPublicacaoPncp", "dataPublicacao", "dataInclusao"),
        "fim_inscricao": _extract_date(row, "dataEncerramentoProposta", "dataAberturaProposta"),
        "situacao": str(row.get("situacaoCompraNome") or row.get("situacaoCompra") or "Em andamento"),
        "valor": valor_str or row.get("valorTotalEstimado") or row.get("valorEstimado"),
        "programa": "contratacoes_publicas_defesa",
        "acao": modal or "licitacao",
        "tipo_recurso": "contrato_publico",
        "extras": extras,
    }


def collect() -> List[Dict[str, object]]:
    session = _build_session()
    items: List[Dict[str, object]] = []
    seen: set[str] = set()
    working_url: Optional[str] = None
    page_size = 80
    query_extra: Dict[str, Any] = {}

    logger.info("Iniciando coleta PNCP Defesa (max_pages=%s)", MAX_PAGES)

    for url in _candidate_urls():
        for size in _PAGE_SIZES_TRY:
            extra = _discover_query_params(session, url, size)
            if extra is None:
                logger.debug("Sem combinação válida para %s tamanhoPagina=%s", url, size)
                continue
            try:
                probe = _request_page(session, url, 1, page_size=size, extra_params=extra)
                working_url = url
                page_size = size
                query_extra = extra
                logger.info(
                    "Endpoint ativo: %s tamanhoPagina=%s extra=%s (itens pág.1: %s)",
                    url,
                    size,
                    {k: query_extra.get(k) for k in list(query_extra)[:6]},
                    len(probe),
                )
                break
            except Exception as exc:
                logger.debug("Falha após discover %s: %s", url, exc)
        if working_url:
            break

    if not working_url:
        logger.error("Nenhum endpoint PNCP respondeu.")
        return []

    total_defesa = 0
    total_rows = 0

    for page in range(1, MAX_PAGES + 1):
        try:
            rows = _request_page(
                session, working_url, page, page_size=page_size, extra_params=query_extra or None
            )
        except Exception as exc:
            logger.warning("Falha na página %s: %s", page, exc)
            continue

        if not rows:
            logger.info("Página %s vazia — fim da paginação.", page)
            break

        total_rows += len(rows)
        page_kept = 0
        for row in rows:
            try:
                item = _row_to_item(row, listagem_url=working_url)
                if not item:
                    continue
                key = str(item.get("link") or item.get("extras", {}).get("numero_controle_pncp"))
                if key in seen:
                    continue
                seen.add(key)
                items.append(item)
                page_kept += 1
                total_defesa += 1
            except Exception as exc:
                logger.debug("Item ignorado: %s", exc)

        logger.info(
            "Página %s (tamanhoPagina=%s): %s linhas API, %s itens defesa aceitos (acumulado %s)",
            page,
            page_size,
            len(rows),
            page_kept,
            len(items),
        )

    logger.info(
        "Resumo: linhas_api=%s itens_defesa=%s endpoint=%s",
        total_rows,
        total_defesa,
        working_url,
    )
    return items


def _fallback_items() -> List[Dict[str, object]]:
    extras = build_defense_extras(
        text="pncp defesa contratacoes publicas",
        source_name="PNCP Defesa",
        origem="https://pncp.gov.br/app/editais",
        pais="Brasil",
        orgao_contratante="PNCP",
    )
    extras.update(
        {
            "regiao": "brasil",
            "tipo_oportunidade": "compra_publica",
            "tipo_recurso": "contrato_publico",
            "natureza_recurso": "contratacao_publica",
            "publico_alvo": ["fornecedores"],
            "url_listagem": "https://pncp.gov.br/app/editais",
            "url_detalhe": "https://pncp.gov.br/app/editais",
            "metodo_extracao": "fallback_public_index",
            "nivel_sensibilidade": "publico_institucional",
            "observacoes": "Consulta API indisponível (timeout/erro HTTP).",
        }
    )
    return [
        {
            "titulo": "PNCP Defesa - Índice de Contratações Públicas",
            "descricao": "Página pública de referência para contratações e editais de defesa no PNCP.",
            "link": "https://pncp.gov.br/app/editais",
            "fonte": "PNCP Defesa",
            "data_publicacao": None,
            "fim_inscricao": None,
            "situacao": "Em andamento",
            "valor": None,
            "programa": "contratacoes_publicas_defesa",
            "acao": "licitacao",
            "tipo_recurso": "contrato_publico",
            "extras": extras,
        }
    ]


def main() -> None:
    logger.info("main() — saída em outputs/pncp_defesa_editais.json")
    items = collect()
    if not items:
        items = _fallback_items()
        logger.warning("Fallback ativado: nenhum item defesa filtrado ou API vazia.")
    save_outputs(Path(__file__).parent, "pncp_defesa", items)
    logger.info("Registros salvos: %s", len(items))


if __name__ == "__main__":
    main()
