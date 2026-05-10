from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List, Set
from urllib.parse import urljoin
from datetime import datetime

import requests
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scraper_generic import (  # noqa: E402
    extract_deadline,
    normalize_text,
    parse_date,
    save_outputs,
)

EXCHANGE_LISTINGS = [
    "https://arpa-e-foa.energy.gov/Default.aspx",
    "https://arpa-e-foa.energy.gov/Default.aspx?Archive=1",
]

_SKIP_TITLES_LOWER = frozenset(
    {
        "skip to main content",
        "skip to content",
        "here",
        "login",
        "register",
        "funding opportunities",
        "funding archive",
    }
)

_FOA_CODE = re.compile(r"\b(DE-FOA-\d+|RFI-\d+)\b", re.IGNORECASE)


def _skip_collect_title(title: str) -> bool:
    t = (title or "").strip().lower()
    if len(t) < 6:
        return True
    if t in _SKIP_TITLES_LOWER:
        return True
    return False


def collect_arpa_e_exchange_foas(*, max_items: int, http_timeout: int) -> List[Dict[str, object]]:
    """
    Lista pública ARPA-E eXCHANGE: âncoras #FoaId... (o scraper genérico remove o fragmento e colapsa tudo num único URL).
    Mantém o fragmento no `link` para unicidade e rastreio.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; EditalResearch/1.1; academic/edital-ingest)",
        "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    }
    seen: Set[str] = set()
    out: List[Dict[str, object]] = []
    for listing_url in EXCHANGE_LISTINGS:
        if len(out) >= max_items:
            break
        try:
            r = requests.get(listing_url, timeout=http_timeout, headers=headers)
            r.raise_for_status()
        except Exception as exc:
            print(f"[DOE_ARPAE] Falha ao ler {listing_url}: {exc}")
            continue
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a[href]"):
            if len(out) >= max_items:
                break
            href = (a.get("href") or "").strip()
            if not href.startswith("#FoaId"):
                continue
            title = normalize_text(a.get_text())
            if _skip_collect_title(title):
                continue
            if not _FOA_CODE.search(title):
                continue
            full_url = urljoin(listing_url, href)
            if full_url in seen:
                continue
            seen.add(full_url)
            tr = a.find_parent("tr")
            row_text = normalize_text(tr.get_text()) if tr else ""
            desc = (row_text if len(row_text) > len(title) else title)[:3500]
            footer = (
                "Official U.S. Department of Energy ARPA-E funding record on the public ARPA-E eXCHANGE portal "
                "(arpa-e-foa.energy.gov). Submission deadlines, budgets, eligibility, and required forms are defined "
                "in the Notice of Funding Opportunity (NOFO) and associated documents on the portal."
            )
            if len(desc) < 400:
                desc = f"{desc}\n\n{footer}" if desc.strip() else footer
            if len(title) < 12:
                title = f"{title} — ARPA-E eXCHANGE"
            combined = f"{title} {desc}"
            pub_date = parse_date(combined) or None
            deadline = extract_deadline(combined)
            m_foa = _FOA_CODE.search(title)
            codigo = m_foa.group(1).upper() if m_foa else ""
            out.append(
                {
                    "titulo": title,
                    "descricao": desc,
                    "link": full_url,
                    "fonte": "DOE_ARPAE",
                    "data_publicacao": pub_date,
                    "fim_inscricao": deadline,
                    "situacao": "Aberto" if deadline else "Em andamento",
                    "valor": None,
                    "programa": "DOE / ARPA-E (eXCHANGE)",
                    "acao": None,
                    "tipo_recurso": "fomento",
                    "extras": {
                        "regiao": "América do Norte",
                        "pais": "Estados Unidos",
                        "idioma_original": "en",
                        "titulo_original": title,
                        "descricao_original": desc,
                        "titulo_traduzido": "",
                        "descricao_traduzida": "",
                        "setor_estrategico": "",
                        "subtema": [],
                        "area_cientifica": [],
                        "area_tecnologica": [],
                        "tipo_oportunidade": "",
                        "orgao_responsavel": "ARPA-E",
                        "instituicao": "U.S. Department of Energy",
                        "empresa_prime": "",
                        "orgao_contratante": "ARPA-E",
                        "numero_edital": "",
                        "numero_chamada": codigo,
                        "numero_processo": "",
                        "codigo_oportunidade": codigo,
                        "modalidade": "",
                        "publico_alvo": "",
                        "elegibilidade": "",
                        "objetivo": "",
                        "escopo": "",
                        "itens_financiaveis": [],
                        "itens_nao_financiaveis": [],
                        "valor_total": "",
                        "valor_por_projeto": "",
                        "contrapartida": "",
                        "prazo_execucao": "",
                        "cronograma": [],
                        "documentos": [],
                        "pdf_url": "",
                        "pdf_texto_extraido": "",
                        "pdf_resumo": "",
                        "data_publicacao_original": "",
                        "fim_inscricao_original": "",
                        "prazo_submissao_original": "",
                        "metodo_extracao": "arpa_e_exchange_listing",
                        "url_listagem": listing_url,
                        "url_detalhe": full_url,
                        "palavras_chave_detectadas": [],
                        "nivel_sensibilidade": "publico_institucional",
                        "necessita_traducao": False,
                        "observacoes": "",
                        "anexos": [],
                        "url_pagina": listing_url,
                        "coletado_em": datetime.now().date().isoformat(),
                    },
                }
            )
    return out


def main():
    max_items = 18
    http_timeout = 28
    try:
        items = collect_arpa_e_exchange_foas(max_items=max_items, http_timeout=http_timeout)
    except Exception as exc:
        print(f"[DOE_ARPAE] Falha na coleta eXCHANGE: {exc}")
        items = []
    if not items:
        print("[DOE_ARPAE] Nenhum FOA/RFI na listagem pública (sem fallback de índice).")
    save_outputs(Path(__file__).parent, "doe_arpae", items)
    print(f"DOE/ARPA-E: {len(items)} registros salvos.")


if __name__ == "__main__":
    main()
