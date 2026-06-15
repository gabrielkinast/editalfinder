from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import argparse
import hashlib
import json
import logging as std_logging
import os
import re
import warnings
from datetime import datetime
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlparse

# Tentativa de importação opcional de pypdf
try:
    import pypdf
except ImportError:
    pypdf = None # type: ignore

from http_fetch import fetch_pdf_bytes
from log_utils import get_logger
from pdf_enrichment import extract_pdf_text_with_fallback

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - optional dependency
    PdfReader = None

# Configuração de diretórios
BASE_DIR = Path(__file__).parent.parent
CORE_DIR = BASE_DIR / "CORE"
TRANSFORMER_OUTPUT_DIR = CORE_DIR / "transformer"
logger = get_logger("transformer")

# PDFs malformados geram muito ruído no console; não são erro fatal.
for _log_name in ("pypdf", "pypdf._reader", "pypdf.pdf", "pypdf.generic", "pypdf.constants"):
    std_logging.getLogger(_log_name).setLevel(std_logging.ERROR)
warnings.filterwarnings(
    "ignore",
    message=r".*wrong pointing object.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*incorrect startxref pointer.*",
    category=UserWarning,
)

# Garante que a pasta de saída existe
TRANSFORMER_OUTPUT_DIR.mkdir(exist_ok=True)

# Descrição quase completa para classificação e front (evita truncar em 1k).
MAX_DESCRICAO_CHARS = 50000

PDF_MAX_PAGES = 10  # Aumentado de 3 para 10 para capturar elegibilidade e anexos no final


def _transform_item_workers() -> int:
    """Threads por lista de editais em transform_generic (baixar/ler PDFs em paralelo)."""
    try:
        v = int(os.getenv("EDITALFINDER_TRANSFORM_ITEM_WORKERS", "6") or "6")
    except ValueError:
        v = 6
    return max(1, min(v, 16))


def _transformer_skip_scoring() -> bool:
    """Quando true, nao calcula score/relevancia (caminho mais leve). Env: EDITALFINDER_SKIP_SCORING."""
    return os.getenv("EDITALFINDER_SKIP_SCORING", "").strip().lower() in ("1", "true", "yes", "on")


def _extras_value_nonempty(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, bool):
        return True
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return bool(str(v).strip())
    if isinstance(v, str):
        return bool(v.strip())
    if isinstance(v, (list, tuple, dict, set)):
        return len(v) > 0
    return True


def _extras_apply_patch_preserve_nonempty(target: Dict[str, Any], patch: Dict[str, Any]) -> None:
    """Aplica patch sem substituir valores já úteis por defaults vazios (ex.: build_defense_extras)."""
    for k, v in patch.items():
        if k == "documentos" and target.get("documentos") and isinstance(v, list) and len(v) == 0:
            continue
        if v is None:
            continue
        if isinstance(v, str) and not v.strip():
            if _extras_value_nonempty(target.get(k)):
                continue
        if isinstance(v, (list, dict)) and len(v) == 0:
            if _extras_value_nonempty(target.get(k)):
                continue
        target[k] = v


def _build_field_confidence(item: Dict[str, Any], *, pdf_text: Optional[str] = None) -> Dict[str, float]:
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}

    def present(v: Any) -> bool:
        if v is None:
            return False
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return False
            return s.casefold() not in {"não especificado", "nao especificado", "n/a", "none"}
        if isinstance(v, (list, dict)):
            return len(v) > 0
        return True

    docs = ex.get("documentos") if isinstance(ex.get("documentos"), list) else []
    return {
        "titulo": 0.95 if present(item.get("titulo")) else 0.0,
        "descricao": 0.9 if len(str(item.get("descricao") or "")) >= 160 else 0.55 if present(item.get("descricao")) else 0.0,
        "prazo": 0.9 if present(item.get("fim_inscricao")) else 0.0,
        "valor": 0.85 if present(item.get("valor")) or present(ex.get("valor_total_texto")) else 0.0,
        "documentos": 0.9 if docs else 0.55 if present(ex.get("pdf_url")) else 0.0,
        "orgao": 0.85 if present(ex.get("orgao_responsavel") or ex.get("orgao_contratante") or ex.get("instituicao")) else 0.35,
        "tipo_recurso": 0.8 if present(item.get("tipo_recurso") or ex.get("tipo_recurso")) else 0.0,
        "pdf_enrichment": 0.85 if present(pdf_text) else 0.0,
    }


def _enrich_grants_gov_catalog_extras(item: Dict[str, Any]) -> None:
    """Preserva oppId e metadados Grants.gov a partir da URL e do texto (sem inventar códigos)."""
    link = str(item.get("link") or "").strip()
    if "grants.gov" not in link.lower():
        return
    ex = item.get("extras")
    if not isinstance(ex, dict):
        return
    try:
        q = parse_qs(urlparse(link).query)
        raw_ids = q.get("oppId") or q.get("oppid") or []
        opp_id = str(raw_ids[0]).strip() if raw_ids else ""
    except Exception:
        opp_id = ""
    if opp_id.isdigit():
        ex.setdefault("grants_gov_opp_id", opp_id)
        if not str(ex.get("codigo_oportunidade") or "").strip():
            ex["codigo_oportunidade"] = opp_id
    desc = str(item.get("descricao") or "")
    if not str(ex.get("numero_chamada") or "").strip():
        m = re.search(r"Opportunity number:\s*([A-Z0-9./_-]+)", desc, re.IGNORECASE)
        if m:
            ex["numero_chamada"] = m.group(1).strip()
    opp_st = str(ex.get("grants_opp_status") or "").strip()
    if opp_st and not str(ex.get("grants_gov_status") or "").strip():
        ex["grants_gov_status"] = opp_st
    agency = str(ex.get("agency") or ex.get("orgao_contratante") or "").strip()
    if agency:
        ex.setdefault("agency", agency)
    if "view-opportunity" in link.lower():
        ex.setdefault("origem_portal", ex.get("origem_portal") or "Grants.gov")
    close = ex.get("closeDate") or ex.get("close_date") or ex.get("grants_close_date")
    if close and not item.get("fim_inscricao"):
        iso = normalize_date_str(str(close), locale="en_US")
        if iso:
            item["fim_inscricao"] = iso
            ex.setdefault("grants_close_date", iso)
            ex.setdefault("deadline_source_field", "closeDate")


import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(Path(__file__).resolve().parent.parent))

from date_parser import DATE_CANDIDATE_REGEX, extract_deadline_from_text, normalize_date_str
from finance_parser import extract_value, extract_value_min
from data_cleaning import (
    CANONICAL_ITEM_KEYS,
    clean_text_fields,
    normalize_aliases,
)
from noise_filter import (
    detect_content_type,
    has_opportunity_signal,
    should_discard_item,
)
from content_routing import apply_content_type, infer_content_type
from transform_enrichment import build_full_text, enrich_description, merge_item_extras
from transform_types import (
    TransformBatchResult,
    TransformResult,
    finalize_batch_report,
    merge_report_delta,
    new_batch_report,
)
from item_quality import apply_quality_to_payload
from scoring import calculate_relevance_score
from keyword_taxonomy import classify_thematic_tags
from taxonomy_filtros import (
    calibrate_amazul_extras,
    calibrate_dcta_ita_iae_extras,
    calibrate_doe_arpae_extras,
    calibrate_nato_diana_extras,
    calibrate_iarpa_extras,
    calibrate_sam_gov_extras,
    calibrate_erc_extras,
    calibrate_horizon_europe_extras,
    calibrate_marinha_extras,
    calibrate_petrobras_extras,
    calibrate_pncp_extras,
    calibrate_portal_plataforma_inovacao_extras,
    calibrate_softex_extras,
    calibrate_japan_jst_extras,
    calibrate_japan_jaea_extras,
    calibrate_japan_jaxa_extras,
    calibrate_japan_e_rad_extras,
    calibrate_china_nsfc_extras,
    calibrate_china_cnnc_extras,
    calibrate_china_avic_extras,
    calibrate_china_norinco_extras,
    calibrate_china_university_procurement_extras,
    calibrate_apex_extras,
    calibrate_ambev_extras,
    calibrate_corporate_supplier_sources_extras,
    calibrate_faperg_extras,
    calibrate_bnb_extras,
    calibrate_badesul_extras,
    calibrate_banco_da_amazonia_extras,
    calibrate_desenvolve_sp_extras,
    calibrate_bdmg_extras,
    calibrate_agerio_extras,
    calibrate_bndes_extras,
    calibrate_embrapii_extras,
    calibrate_nuclep_extras,
    calibrate_bid_lab_extras,
    calibrate_caf_extras,
    calibrate_fonplata_extras,
    calibrate_eureka_network_extras,
    calibrate_eic_extras,
    calibrate_innovate_uk_extras,
    calibrate_ukri_funding_extras,
    calibrate_eurostars_extras,
    calibrate_eit_extras,
    calibrate_dod_sbir_sttr_extras,
    calibrate_esa_star_extras,
    calibrate_esa_osip_extras,
    enrich_opportunity_classification,
)
from merge_utils import sanitize_for_postgres
from defense_intel import build_defense_extras
try:
    from asia_intel import build_asia_extras
except Exception:
    build_asia_extras = None  # type: ignore

try:
    from asia_translate import enrich_asia_translation
except Exception:
    enrich_asia_translation = None  # type: ignore


ASIA_SOURCE_PREFIXES = ("japan_", "china_")


def _is_asia_source(source_name: str, extras: dict) -> bool:
    """True se a fonte e asiatica (por prefixo do nome ou por extras.regiao)."""
    if extras and extras.get("regiao") == "asia":
        return True
    if not source_name:
        return False
    name = str(source_name).lower()
    return name.startswith(ASIA_SOURCE_PREFIXES)

def normalize_text_encoding(text):
    """Corrige encoding comum de PDFs brasileiros (caracteres corrompidos pelo pypdf)."""
    if not text:
        return text
    if "\x00" in text:
        text = text.replace("\x00", "")
    replacements = {
        "þ": "ç", "Þ": "Ç",
        "ã": "ã", "õ": "õ", "Ã": "Ã", "Õ": "Õ",
        "á": "á", "é": "é", "í": "í", "ó": "ó", "ú": "ú",
        "à": "à", "è": "è", "ì": "ì", "ò": "ò", "ù": "ù",
        "â": "â", "ê": "ê", "î": "î", "ô": "ô", "û": "û",
        "Á": "Á", "É": "É", "Í": "Í", "Ó": "Ó", "Ú": "Ú",
        "Â": "Â", "Ê": "Ê", "Î": "Î", "Ô": "Ô", "Û": "Û",
        "Ã": "Ã", "Ç": "Ç",
    }
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    return text

def extract_situacao(text):
    """Extrai a situação do programa ou ação (ex: em elaboração, aberto, encerrado)."""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Mapeamento consolidado para 'situacao'
    situacao_map = {
        r"(?:em\s+elabora[çc][ãa]o|pr[eé]-publica[çc][ãa]o)": "Em Elaboração",
        r"(?:em\s+andamento|em\s+execu[çc][ãa]o|ativ[oa]|vigente|abert[oa]|publicad[oa]|dispon[ií]vel)": "Aberto",
        r"(?:homologad[oa]|resultad[oa]|finalizad[oa]|conclu[ií]d[oa]|encerrad[oa]|esgotad[oa])": "Encerrado",
        r"(?:suspens[oa]|cancelad[oa])": "Suspenso",
    }
    
    for pattern, situacao in situacao_map.items():
        if re.search(pattern, text_lower):
            return situacao
    
    if re.search(r"(?:edital|chamada)\s+(?:n[º°]\s*)?\d+[/.-]\d+", text_lower):
        return "Aberto"

    return None

def extract_regiao(text):
    """Extrai a abrangência regional com suporte a internacional e estados."""
    if not text:
        return None

    text_lower = text.lower()
    
    if any(x in text_lower for x in ["internacional", "global", "exterior", "world", "europe", "estados unidos"]):
        return "Internacional"

    regioes = {
        "Nacional": [
            r"brasil(?:\s+todo)?", r"todo\s+o\s+brasil", r"nacional",
            r"a\s+nível\s+nacional", r"em\s+todo\s+o\s+território",
            r"país\s+inteiro", r"abrangência\s+nacional"
        ],
        "Sul": [r"\bsul\b", r"região\s+sul", r"paraná", r"santa\s+catarina", r"rio\s+grande\s+do\s+sul", r"\bpr\b", r"\bsc\b", r"\brs\b"],
        "Sudeste": [r"\bsudeste\b", r"região\s+sudeste", r"são\s+paulo", r"rio\s+de\s+janeiro", r"espírito\s+santo", r"minas\s+gerais", r"mg\b", r"sp\b", r"rj\b", r"es\b"],
        "Nordeste": [r"\bnordeste\b", r"região\s+nordeste", r"bahia", r"sergipe", r"pernambuco", r"ceará", r"alagoas", r"paraíba", r"rio\s+grande\s+do\s+norte", r"maranhão", r"piauí"],
        "Centro-Oeste": [r"centro-oeste", r"região\s+centro-oeste", r"goiás", r"mato\s+grosso", r"mato\s+grosso\s+do\s+sul", r"distrito\s+federal", r"df\b"],
        "Norte": [r"\bnorte\b", r"região\s+norte", r"amazonas", r"pará", r"amapá", r"roraima", r"tocantins", r"acre", r"rondônia"],
    }

    for regiao, patterns in regioes.items():
        if regiao == "Nacional": continue
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return regiao

    for pattern in regioes["Nacional"]:
        if re.search(pattern, text_lower):
            return "Nacional"

    if re.search(r"(?:estadual|estado|específico\s+para)", text_lower):
        return "Estadual"

    return "Nacional"

def extract_contrapartida(text):
    """Extrai informações sobre contrapartida financeira ou econômica."""
    if not text:
        return None
    text_lower = text.lower()
    patterns = [
        r"(?:contrapartida(?:\s+financeira|\s+m[ií]nima)?(?:[\s:])((?:[^\n\.]{10,200}(?:\n|$)){1,3}))",
        r"(?:aporte\s+de\s+recursos?\s+pr[oó]prios(?:[\s:])((?:[^\n\.]{10,200}(?:\n|$)){1,3}))",
        r"(?:recursos?\s+de\s+outras\s+fontes(?:[\s:])((?:[^\n\.]{10,200}(?:\n|$)){1,3}))",
        r"(?:participa[çc][ãa]o\s+da\s+proponente(?:[\s:])((?:[^\n\.]{10,200}(?:\n|$)){1,3}))",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            val = re.sub(r'\s+', ' ', match.group(1).strip())
            return val[:250]
    
    if "sem contrapartida" in text_lower or "não exige contrapartida" in text_lower:
        return "Não exige contrapartida"
        
    return None

def extract_elegibilidade(text):
    """Extrai critérios de elegibilidade (quem pode participar)."""
    if not text:
        return None
    text_lower = text.lower()
    patterns = [
        r"(?:elegibilidade|crit[eé]rios\s+de\s+elegibilidade|quem\s+pode\s+participar)(?:[\s:])((?:[^\n\.]{10,250}(?:\n|$)){1,4})",
        r"(?:requisitos\s+m[ií]nimos)(?:[\s:])((?:[^\n\.]{10,250}(?:\n|$)){1,4})",
        r"(?:proponentes\s+eleg[ií]veis(?:[\s:])((?:[^\n\.]{10,250}(?:\n|$)){1,4}))",
        r"(?:poderão\s+se\s+inscrever(?:[\s:])((?:[^\n\.]{10,250}(?:\n|$)){1,4}))",
    ]
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            val = re.sub(r'\s+', ' ', match.group(1).strip())
            return val[:400]
    
    # Heurística para capturar o parágrafo após a palavra-chave
    if "elegibilidade" in text_lower:
        idx = text_lower.find("elegibilidade")
        excerpt = text[idx:idx+500]
        # Tenta pegar o primeiro parágrafo relevante
        lines = [l.strip() for l in excerpt.split('\n') if len(l.strip()) > 20]
        if lines:
            return " ".join(lines[:2])[:400]
            
    return None

def extract_contato(text):
    """Extrai email ou telefone de contato/suporte."""
    if not text:
        return None
    
    # Emails
    emails = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if emails:
        # Filtra emails que não parecem ser suporte
        suporte = [e for e in emails if any(kw in e.lower() for kw in ["suporte", "duvida", "edital", "contato", "chamada"])]
        if suporte:
            return suporte[0]
        return emails[0]
    
    # Telefones
    phones = re.findall(r"(?:\(?\d{2}\)?\s?)?\d{4,5}[-\s]?\d{4}", text)
    if phones:
        return phones[0]
    
    return None

def extract_ods(text):
    """Extrai Objetivos de Desenvolvimento Sustentável (ODS)."""
    if not text:
        return None
    text_lower = text.lower()
    # Busca por ODS 1, ODS 2... ODS 17 ou menção a Objetivos de Desenvolvimento Sustentável
    ods_matches = re.findall(r"(?:ods\s*(\d{1,2}))", text_lower)
    if ods_matches:
        unique_ods = sorted(list(set([int(m) for m in ods_matches if int(m) <= 17])))
        if unique_ods:
            return ", ".join([f"ODS {n}" for n in unique_ods])
    
    if "objetivos de desenvolvimento sustentável" in text_lower or "agenda 2030" in text_lower:
        return "Menciona ODS/Agenda 2030"
        
    return None

def extract_link_inscricao(text):
    """Tenta encontrar um link específico para inscrição."""
    if not text:
        return None
    
    # Busca por links que contenham palavras-chave de inscrição
    urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*(?:\?\S*)?', text)
    inscricao_urls = [u for u in urls if any(kw in u.lower() for kw in ["inscricao", "cadastro", "proposta", "submit", "apply"])]
    
    if inscricao_urls:
        return inscricao_urls[0]
    return None

def extract_program_action(title):
    """Tenta extrair o nome do programa ou ação do título."""
    if not title:
        return None, None
    
    # Heurística: programas costumam vir após um traço ou hífen longo
    if " – " in title:
        partes = title.split(" – ", 1)
        return partes[1].strip(), None
    if " - " in title:
        partes = title.split(" - ", 1)
        return partes[1].strip(), None
    
    return None, None

def extract_target_audience(text):
    """Extrai o público-alvo do texto com filtros para evitar capturar menus."""
    if not text:
        return None
    
    text_lower = text.lower()
    
    patterns = [
        r"(?:p[uú]blico(?:\s+-?\s*alvo|[\s:])((?:[^\n\.]{15,150}(?:\n|$)){1,5}))",
        r"(?:eleg[ií]vel(?:is)?(?:[\s:])((?:[^\n\.]{15,150}(?:\n|$)){1,5}))",
        r"(?:destinado(?:a|o|s)?(?:[\s:])((?:[^\n\.]{15,150}(?:\n|$)){1,5}))",
        r"(?:podem\s+participar(?:[\s:])((?:[^\n\.]{15,150}(?:\n|$)){1,5}))",
        r"(?:quem\s+pode\s+se\s+inscrever(?:[\s:])((?:[^\n\.]{15,150}(?:\n|$)){1,5}))",
        r"(?:institui[uçõ]es?(?:[\s:])((?:[^\n\.]{15,150}(?:\n|$)){1,5}))",
        r"(?:empresas?(?:[\s:])((?:[^\n\.]{15,150}(?:\n|$)){1,5}))",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            audience = match.group(1).strip()
            audience = re.sub(r'\s+', ' ', audience)
            # Filtro para evitar capturar rodapés de contato ou manuais
            if len(audience) > 20 and not any(x in audience for x in ["manual", "duvidas", "orientações", "suporte"]):
                return audience[:250]
    
    # Fallback refinado
    keywords = {
        "startups": "Startups",
        "microempresas": "Micro e Pequenas Empresas",
        "pesquisadores": "Pesquisadores e Acadêmicos",
        "instituições de ciência e tecnologia": "ICTs",
        "organizações da sociedade civil": "ONGs/OSCs",
        "prefeituras": "Gestão Pública/Municípios"
    }
    found = [v for k, v in keywords.items() if k in text_lower]
    if found:
        return "Destinado a: " + ", ".join(found)
        
    return None

def extract_themes(text):
    """Extrai os temas/áreas do texto do PDF com filtros de ruído."""
    if not text:
        return None
    
    text_lower = text.lower()
    
    patterns = [
        r"(?:temas?|eixos?\s+temáticos?|prioridades?|áreas?\s+de\s+atuação)(?:[\s:])((?:[^\n\.]{10,150}(?:\n|$)){1,3})",
        r"(?:áreas?(?:[\s:])((?:[^\n\.]{10,150}(?:\n|$)){1,3}))",
        r"(?:linhas?\s+de\s+pesquisa(?:[\s:])((?:[^\n\.]{10,150}(?:\n|$)){1,3}))",
        r"(?:setores?\s+prioritários?(?:[\s:])((?:[^\n\.]{10,150}(?:\n|$)){1,3}))",
        r"(?:tecnologias?(?:[\s:])((?:[^\n\.]{10,150}(?:\n|$)){1,3}))",
        r"(?:foco\s+em(?:[\s:])((?:[^\n\.]{10,150}(?:\n|$)){1,3}))",
        r"(?:objetivos?\s+de\s+desenvolvimento\s+sustentável(?:[\s:])((?:[^\n\.]{10,150}(?:\n|$)){1,3}))",
    ]
    
    extracted_themes = []
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            for theme in matches:
                theme = re.sub(r'\s+', ' ', theme.strip())
                # Filtro de ruído específico para temas
                if len(theme) > 10 and not any(x in theme for x in ["manual", "duvida", "clique", "acesse"]):
                    if theme not in extracted_themes:
                        extracted_themes.append(theme[:150])
    
    if extracted_themes:
        return "; ".join(extracted_themes[:5])
    
    # Fallback: busca por palavras-chave de áreas comuns se nada for extraído
    areas = ["saúde", "energia", "educação", "tecnologia", "meio ambiente", "agricultura", "indústria", "biotecnologia"]
    text_clean = f" {re.sub(r'[^\w\s]', ' ', text_lower)} "
    found = [a.capitalize() for a in areas if f" {a.lower()} " in text_clean]
    if found:
        return "; ".join(found[:3])
    
    return None

def extract_resource_type(text):
    """Identifica o tipo de recurso (subvenção, reembolsável, etc) no texto."""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Ordem de prioridade para detecção
    if any(
        kw in text_lower
        for kw in [
            "não reembolsável",
            "nao reembolsavel",
            "subvenção econômica",
            "subvencao economica",
            "fndct",
            "seleção pública",
            "selecao publica",
            "grant funding",
            "funding opportunity",
            "foa ",
            "solicitation",
            "non-repayable",
            "sem ônus",
            "fomento direto",
        ]
    ):
        return "Subvenção (Não Reembolsável)"
    if any(kw in text_lower for kw in ["financiamento reembolsável", "credito", "empréstimo", "financiamento", "reembolsável", "reembolsavel", "loan", "crédito", "linha de crédito"]):
        return "Reembolsável (Financiamento)"
    if any(kw in text_lower for kw in ["bolsa de pesquisa", "bolsa de estudo", "auxílio à pesquisa", "chamada cnpq", "bolsa", "fellowship", "scholarship", "auxílio individual"]):
        return "Bolsa / Auxílio"
    if any(kw in text_lower for kw in ["prêmio de inovação", "premiacao", "concurso", "prêmio", "award", "prize", "desafio"]):
        return "Prêmio / Concurso"
    if any(kw in text_lower for kw in ["investimento anjo", "equity", "venture capital", "participação acionária", "aporte de capital"]):
        return "Investimento (Equity)"
    if "subvenção" in text_lower or "subvencao" in text_lower or "apoio financeiro" in text_lower:
        return "Subvenção (Não Reembolsável)"
    
    # Se ainda não detectou, mas há valores altos e palavras de 'crédito'
    if "crédito" in text_lower or "credito" in text_lower:
        return "Reembolsável (Financiamento)"

    return "Não Especificado"


def extract_program_action_from_text(text):
    if not text:
        return None, None
    prog_match = re.search(r"(programa[^:.\n]{3,120})", text, re.IGNORECASE)
    acao_match = re.search(r"(?:ação|acao)[^:.\n]{3,120}", text, re.IGNORECASE)
    programa = prog_match.group(1).strip(" -:") if prog_match else None
    acao = acao_match.group(0).strip(" -:") if acao_match else None
    return programa, acao


def extract_numero_edital(text: str):
    if not text:
        return None
    patterns = [
        r"(?:edital|chamada)\s*(?:n[º°o]\s*)?([A-Z0-9./_-]{3,})",
        r"(?:招标编号|公告编号|项目编号)\s*[:：]?\s*([A-Z0-9\-_/]{4,})",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def extract_numero_processo(text: str):
    if not text:
        return None
    m = re.search(r"(?:processo|proc\.)\s*(?:n[º°o]\s*)?([A-Z0-9./_-]{5,})", text, re.IGNORECASE)
    return m.group(1).strip() if m else None


def extract_codigo_oportunidade(text: str):
    if not text:
        return None
    m = re.search(
        r"(?:oppid|opportunity id|topic code|call id|baa)\s*[:#=-]?\s*([A-Z0-9./_-]{3,})",
        text,
        re.IGNORECASE,
    )
    return m.group(1).strip() if m else None


def _normalize_doc_url(url: str, base_url: str) -> str:
    u = str(url or "").strip()
    if not u:
        return ""
    if u.lower().startswith(("javascript:", "#")):
        return ""
    if u.startswith(("http://", "https://")):
        return u
    if base_url and base_url.startswith(("http://", "https://")):
        try:
            return urljoin(base_url, u)
        except Exception:
            return u
    return u


def _classify_document_type(nome: str, url: str) -> str:
    blob = f"{nome} {url}".lower()
    if any(x in blob for x in (".xlsx", ".xls", "planilha", "sheet", "csv")):
        return "planilha"
    if any(x in blob for x in (".doc", ".docx", "modelo", "template", "minuta")):
        return "modelo_documento"
    rules = (
        ("edital_pdf", ("edital", "chamada publica", "chamada pública")),
        ("anexo", ("anexo", "attachment")),
        ("regulamento", ("regulamento", "normativo")),
        ("termo_referencia", ("termo de referência", "termo de referencia", "termo_referencia")),
        ("chamada", ("chamada", "call for")),
        ("resultado", ("resultado", "homolog")),
        ("formulario", ("formulário", "formulario", "form")),
        ("manual", ("manual", "guia")),
        ("cronograma", ("cronograma", "calendario", "timeline")),
    )
    for t, pats in rules:
        if any(p in blob for p in pats):
            return t
    return "documento_desconhecido"


def _detect_document_format(url: str, nome: str = "") -> str:
    blob = f"{url} {nome}".lower()
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


def _normalize_documents_payload(docs: List[Dict[str, Any]], base_url: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    for d in docs:
        nome = str(d.get("nome") or d.get("title") or d.get("titulo") or "Documento").strip()[:220]
        raw_url = str(d.get("url") or d.get("link") or "").strip()
        origem = str(d.get("origem") or d.get("source") or "").strip()[:80]
        url = _normalize_doc_url(raw_url, base_url)
        if not url or url in seen:
            continue
        seen.add(url)
        formato = _detect_document_format(url, nome)
        tipo_explicit = str(d.get("tipo") or "").strip()
        if tipo_explicit in (
            "sistema_origem",
            "processo_eletronico",
            "edital_pncp",
            "detalhe_pncp",
        ):
            tipo_final = tipo_explicit
        else:
            tipo_final = _classify_document_type(nome, url)
        out.append(
            {
                "nome": nome,
                "titulo": nome,
                "url": url,
                "tipo": tipo_final,
                "formato": formato,
                "origem": origem or "crawler",
                "status_download": "nao_baixado",
                "erro_download": "",
                "texto_extraido": "",
                "resumo": "",
            }
        )
    return out[:20]


def extract_documentos(item: dict) -> List[Dict[str, Any]]:
    docs_raw: List[Dict[str, Any]] = []
    candidates = []
    if isinstance(item.get("extras"), dict):
        candidates.append(("extras.anexos", item["extras"].get("anexos")))
        candidates.append(("extras.documentos", item["extras"].get("documentos")))
    candidates.append(("item.anexos", item.get("anexos")))
    candidates.append(("item.documentos", item.get("documentos")))
    base_url = str(item.get("link") or item.get("url") or "")

    def _iter_docs_payload(v: Any) -> List[Dict[str, Any]]:
        if isinstance(v, dict):
            return [v]
        if isinstance(v, list):
            return [x for x in v if isinstance(x, (dict, str))]
        if isinstance(v, str):
            s = v.strip()
            if not s:
                return []
            try:
                j = json.loads(s)
                if isinstance(j, dict):
                    return [j]
                if isinstance(j, list):
                    return [x for x in j if isinstance(x, (dict, str))]
            except Exception:
                # fallback: extrai links no texto bruto
                urls = re.findall(r"https?://[^\s\"'<>]+", s, flags=re.IGNORECASE)
                return [{"url": u, "nome": "Documento"} for u in urls]
        return []

    for origem, c in candidates:
        for d in _iter_docs_payload(c):
            if isinstance(d, dict):
                docs_raw.append(
                    {
                        "nome": d.get("nome") or d.get("title") or d.get("titulo") or "Documento",
                        "url": d.get("url") or d.get("link") or "",
                        "origem": origem,
                    }
                )
            elif isinstance(d, str):
                docs_raw.append({"nome": "Documento", "url": d, "origem": origem})
    if not docs_raw:
        pdf_url = extract_pdf_url(item)
        if pdf_url:
            docs_raw.append({"nome": "Documento PDF", "url": pdf_url, "origem": "extract_pdf_url"})
    return _normalize_documents_payload(docs_raw, base_url)


def _pick_primary_pdf(docs: List[Dict[str, Any]]) -> str:
    if not docs:
        return ""
    preferred = {"edital_pdf", "regulamento", "chamada", "termo_referencia"}
    for d in docs:
        if str(d.get("formato") or "").lower() == "pdf" and d.get("tipo") in preferred:
            return str(d.get("url") or "")
    for d in docs:
        if str(d.get("formato") or "").lower() == "pdf":
            return str(d.get("url") or "")
    return ""


def extract_cronograma(text: str) -> List[Dict[str, str]]:
    if not text:
        return []
    events = []
    labels = ("inscrição", "submissão", "resultado", "contratação", "homologação", "proposal", "deadline")
    for label in labels:
        m = re.search(rf"{label}.{{0,30}}{DATE_CANDIDATE_REGEX}", text, re.IGNORECASE)
        if m:
            date_norm = normalize_date_str(m.group(0))
            if date_norm:
                events.append({"evento": label, "data": date_norm})
    return events[:8]


def extract_pdf_url(item):
    """Busca recursivamente por uma URL de PDF dentro de qualquer campo do item."""
    if not isinstance(item, (dict, list)):
        return None

    # Chaves que costumam conter o PDF diretamente
    direct_keys = ["pdf_url", "url_chamada", "link_pdf", "anexo_pdf", "url", "link"]
    
    if isinstance(item, dict):
        # 1. Tenta chaves diretas primeiro
        for key in direct_keys:
            val = item.get(key)
            if isinstance(val, str) and val.lower().endswith(".pdf"):
                return val
        
        # 2. Busca recursiva em todos os campos
        for key, val in item.items():
            if isinstance(val, str) and ".pdf" in val.lower():
                # Verifica se é uma URL válida de PDF
                match = re.search(r'(https?://[^\s"\'<>]+?\.pdf(?:\?[^\s"\'<>]*)?)', val, re.IGNORECASE)
                if match:
                    return match.group(1)
            elif isinstance(val, (dict, list)):
                res = extract_pdf_url(val)
                if res:
                    return res
    
    elif isinstance(item, list):
        for sub_item in item:
            res = extract_pdf_url(sub_item)
            if res:
                return res
                
    return None


def read_pdf_text(pdf_url, page_referer=None):
    """Lê primeiras páginas de um PDF via URL (headers de navegador + fallback curl)."""
    if not pdf_url or PdfReader is None:
        return None
    ref = page_referer
    if ref and isinstance(ref, str) and ref.lower().endswith(".pdf"):
        ref = None
    pdf_bytes = fetch_pdf_bytes(pdf_url, page_referer=ref)
    if not pdf_bytes or len(pdf_bytes) < 5:
        logger.warning("PDF não baixado ou vazio: %s", pdf_url)
        return None
    try:
        text = extract_pdf_text_with_fallback(pdf_bytes, max_pages=PDF_MAX_PAGES)
        if not text:
            return None
        text = normalize_text_encoding(text)
        return text.strip() or None
    except Exception as exc:
        logger.warning("Falha ao extrair texto do PDF %s: %s", pdf_url, exc)
    return None

def transform_generic(data, source_name) -> TransformBatchResult:
    """Transformador genérico: retorna itens aceites, rejeitados e relatório por fonte."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    iw = _transform_item_workers()
    indexed: List[Tuple[int, Dict[str, Any]]] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            logger.warning("Item ignorado (não é dict) em %s: %r", source_name, type(item))
            continue
        indexed.append((i, item))

    results: List[TransformResult] = []
    if len(indexed) <= 2 or iw <= 1:
        for _, item in indexed:
            try:
                results.append(_transform_item_with_result(item, source_name))
            except Exception:
                logger.exception(
                    "Erro ao transformar item em %s (titulo=%s)",
                    source_name,
                    (item or {}).get("titulo"),
                )
                results.append(
                    TransformResult(
                        payload=None,
                        rejected=True,
                        rejection_reason="transform_exception",
                        warnings=[],
                        report_delta={"erro": "exception"},
                        original_item=dict(item) if isinstance(item, dict) else None,
                        content_type_detectado="erro",
                    )
                )
    else:
        tmp: List[Optional[TransformResult]] = [None] * len(indexed)
        with ThreadPoolExecutor(max_workers=min(iw, len(indexed))) as ex:
            fut_to_pos: Dict[Any, int] = {}
            for pos, (_, item) in enumerate(indexed):
                fut = ex.submit(_transform_item_with_result, item, source_name)
                fut_to_pos[fut] = pos
            for fut in as_completed(fut_to_pos):
                pos = fut_to_pos[fut]
                try:
                    tmp[pos] = fut.result()
                except Exception:
                    logger.exception(
                        "Erro ao transformar item em %s (pos=%s titulo=%s)",
                        source_name,
                        pos,
                        (indexed[pos][1] or {}).get("titulo"),
                    )
                    tmp[pos] = TransformResult(
                        payload=None,
                        rejected=True,
                        rejection_reason="transform_exception",
                        warnings=[],
                        report_delta={"erro": "exception"},
                        original_item=dict(indexed[pos][1]) if indexed[pos][1] else None,
                        content_type_detectado="erro",
                    )
        results = [t for t in tmp if t is not None]

    report = new_batch_report(source_name)
    payloads: List[Dict[str, Any]] = []
    for tr in results:
        merge_report_delta(report, tr)
        if tr.payload and isinstance(tr.payload, dict):
            payloads.append(tr.payload)

    deduped_data: List[Dict[str, Any]] = []
    seen = set()
    for row in payloads:
        dedupe_key = "|".join(
            [
                str(row.get("link") or ""),
                str(row.get("titulo") or ""),
                str(row.get("fonte") or ""),
                str(row.get("data_publicacao") or ""),
                str(row.get("fim_inscricao") or ""),
            ]
        )
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        deduped_data.append(row)

    rejected_records = [tr.to_rejected_record() for tr in results if tr.rejected]
    finalize_batch_report(report)

    rejected_dir = BASE_DIR / "outputs" / "rejected"
    rejected_dir.mkdir(parents=True, exist_ok=True)
    if rejected_records:
        rej_path = rejected_dir / f"transformer_rejected_{source_name}.json"
        with open(rej_path, "w", encoding="utf-8") as rf:
            json.dump(rejected_records, rf, ensure_ascii=False, indent=2)
        logger.info("Rejeitados transformer: %s (%s itens)", rej_path.name, len(rejected_records))
    rep_path = rejected_dir / f"transformer_report_{source_name}.json"
    with open(rep_path, "w", encoding="utf-8") as pf:
        json.dump(report, pf, ensure_ascii=False, indent=2)

    return TransformBatchResult(items=deduped_data, rejected=rejected_records, report=report)


def clean_extracted_text(text):
    """Limpa textos extraídos de PDFs ou Scrapers, removendo ruído de navegação e formatação."""
    if not text:
        return ""
    if "\x00" in text:
        text = text.replace("\x00", "")

    # Remove excesso de espaços e quebras de linha
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Blacklist de ruído comum em cabeçalhos/rodapés/menus de sites governamentais
    noise_patterns = [
        r"manuais manual do cliente", r"cadastro de proponente", r"em caso de dúvidas",
        r"perguntas frequentes", r"mapa do site", r"política de privacidade",
        r"todos os direitos reservados", r"desenvolvido por", r"acesso à informação",
        r"ir para o conteúdo", r"ir para o menu", r"ir para a busca",
    ]
    
    for pattern in noise_patterns:
        text = re.compile(pattern, re.IGNORECASE).sub("", text)
        
    return text.strip()

import hashlib

def generate_content_hash(text_list: List[Any]) -> str:
    """Gera um hash SHA-256 a partir de uma lista de textos relevantes, normalizando-os."""
    normalized_parts = []
    for t in text_list:
        if isinstance(t, str) and t:
            # Normaliza: minúsculas, remove espaços extras e pontuação básica para o hash
            clean = re.sub(r'\s+', '', t.lower())
            clean = re.sub(r'[^\w]', '', clean)
            normalized_parts.append(clean)
            
    combined = "".join(normalized_parts)
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def _content_type_final(link: str, ct_ml: str) -> str:
    """PDF em domínio público BR → documento_oficial; demais PDFs → pdf_documento."""
    low_path = (link or "").strip().lower().split("?", 1)[0]
    if low_path.endswith(".pdf"):
        lk = (link or "").lower()
        if any(
            h in lk
            for h in (
                "gov.br",
                "bndes.gov.br",
                "finep.gov.br",
                "cnpq.br",
                "aneel.gov.br",
            )
        ):
            return "documento_oficial"
        return "pdf_documento"
    return ct_ml


def _pncp_defesa_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local (não-global) para PNCP Defesa/Compras Defesa:
    evita falso negativo de compra pública quando há metadados oficiais.
    """
    src = (source_name or "").strip().lower()
    if src not in ("pncp_defesa", "compras_defesa"):
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    lk = (link or "").lower()
    if "/editais/" not in lk and "pncp" not in lk:
        return False
    blob = f"{titulo} {descricao} {item.get('acao') or ''} {item.get('tipo_recurso') or ''}".lower()
    procurement_markers = (
        "pregão",
        "pregao",
        "licit",
        "concorr",
        "dispensa",
        "aquisição",
        "aquisicao",
        "contrata",
        "compra pública",
        "compra publica",
    )
    if not any(m in blob for m in procurement_markers):
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    has_official_meta = any(
        str(ex.get(k) or "").strip()
        for k in ("numero_edital", "numero_processo", "codigo_oportunidade", "numero_controle_pncp")
    )
    has_core_data = bool(str(item.get("fim_inscricao") or "").strip()) or bool(str(item.get("valor") or "").strip())
    return has_official_meta or has_core_data


def _badesul_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local para BADESUL: permite seguir quando há sinais claros de
    linha/programa de crédito ou subvenção com documento oficial.
    """
    src = (source_name or "").strip().lower()
    if src != "badesul":
        return False
    rr = gate_reason or ""
    if (
        "Relevancia limite" not in rr
        and "Pontuacao abaixo" not in rr
        and "Noticia ou pagina generica" not in rr
    ):
        return False
    lk = (link or "").lower()
    if "badesul.com.br" not in lk or "idpublicacao=" not in lk:
        return False
    blob = f"{titulo} {descricao} {item.get('acao') or ''} {item.get('tipo_recurso') or ''}".lower()
    credit_markers = (
        "credito",
        "crédito",
        "financiamento",
        "subven",
        "programa",
        "linha",
        "capital de giro",
        "investimento",
        "carencia",
        "carência",
        "taxa",
        "empresa",
        "municip",
        "prefeitura",
        "produtor rural",
        "cooperativa",
    )
    if not any(m in blob for m in credit_markers):
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    has_docs = isinstance(ex.get("documentos"), list) and len(ex.get("documentos") or []) > 0
    has_pdf = bool(str(ex.get("pdf_url") or "").strip())
    return has_docs or has_pdf


_LOTE_CREDITO_BR_SOURCES = frozenset(
    {"bnb", "banco_da_amazonia", "desenvolve_sp", "bdmg", "agerio"}
)
_LOTE_CREDITO_BR_HOSTS: Dict[str, Tuple[str, ...]] = {
    "bnb": ("bnb.gov.br",),
    "banco_da_amazonia": ("bancoamazonia.com.br",),
    "desenvolve_sp": ("desenvolvesp.com.br",),
    "bdmg": ("bdmg.mg.gov.br", "bdmgorienta.bdmg.mg.gov.br"),
    "agerio": ("agerio.com.br", "portal.agerio.com.br"),
}

_LOTE_MULTILATERAL_ONDA_B_SOURCES = frozenset(
    {"bid_lab", "caf", "fonplata", "eureka_network", "eic"}
)
_LOTE_MULTILATERAL_ONDA_B_HOSTS: Dict[str, Tuple[str, ...]] = {
    "bid_lab": ("bidlab.org", "iadb.org", "idbinvest.org"),
    "caf": ("caf.com",),
    "fonplata": ("fonplata.org",),
    "eureka_network": ("eurekanetwork.org",),
    "eic": ("eic.ec.europa.eu", "ec.europa.eu"),
}

_LOTE_INOVACAO_INTERNACIONAL_ONDA_C_SOURCES = frozenset(
    {"innovate_uk", "ukri_funding", "eurostars", "eit", "esa_star", "esa_osip"}
)
_LOTE_INOVACAO_INTERNACIONAL_ONDA_C_HOSTS: Dict[str, Tuple[str, ...]] = {
    "innovate_uk": ("ukri.org", "gov.uk", "apply-for-innovation-funding.service.gov.uk"),
    "ukri_funding": ("ukri.org",),
    "eurostars": ("eurekanetwork.org",),
    "eit": ("eit.europa.eu",),
    "esa_star": ("esa.int", "procurement.esa.int", "esamultimedia.esa.int"),
    "esa_osip": ("ideas.esa.int", "esa.int"),
}


def _credito_brasil_onda_a_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local (só transformer): agências de crédito BR — gate global pode cortar
    páginas curtas de produto; aqui exige host oficial da fonte + marcadores de financiamento no texto/URL.
    Não altera opportunity_gate.py.
    """
    src = (source_name or "").strip().lower()
    if src not in _LOTE_CREDITO_BR_SOURCES:
        return False
    from CORE.credito_brasil_onda_a_noise import credit_url_hint as _onda_a_credit_url
    from CORE.credito_brasil_onda_a_noise import credito_brasil_onda_a_ruido_motivo as _onda_a_noise

    if _onda_a_noise(src, titulo, descricao, link, item.get("extras") if isinstance(item.get("extras"), dict) else {}):
        return False
    rr = gate_reason or ""
    if (
        "Relevancia limite" not in rr
        and "Pontuacao abaixo" not in rr
        and "Noticia ou pagina generica" not in rr
    ):
        return False
    lk = (link or "").lower()
    hosts = _LOTE_CREDITO_BR_HOSTS.get(src, ())
    if not hosts or not any(h in lk for h in hosts):
        return False
    blob = f"{titulo} {descricao} {link}".lower()
    strong_markers = (
        "credito",
        "crédito",
        "financiamento",
        "fomento",
        "linha",
        "emprestimo",
        "empréstimo",
        "microcredito",
        "microcrédito",
        "pronampe",
        "pronaf",
        "solicit",
        "opcoes-de-credito",
        "credito-e-financiamento",
        "linhas-de-fomento",
        "linhas-de-credito",
        "capital de giro",
        "maquinas",
        "máquinas",
        "negocios/online",
        "microempreendedor",
        "areas-de-atuacao",
        "produtos-e-servicos",
        "solicitacao-de-credito",
        "atividades-financiadas",
        "guia-do-financiamento",
        "financiamento-agro",
        "bdmgorienta",
        "giro",
        "fungetur",
        "fgi",
        "finame",
        "fno",
        "labagro",
    )
    if any(m in blob for m in strong_markers):
        return True
    if _onda_a_credit_url(lk) and any(m in blob for m in ("rural", "agro", "micro", "pequena", "empreendedor", "empresa")):
        return True
    return False


def _multilateral_onda_b_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """Relaxamento local Onda B: calls/funding oficiais multilaterais com ação concreta."""
    src = (source_name or "").strip().lower()
    if src not in _LOTE_MULTILATERAL_ONDA_B_SOURCES:
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    lk = (link or "").lower()
    hosts = _LOTE_MULTILATERAL_ONDA_B_HOSTS.get(src, ())
    if not hosts or not any(h in lk for h in hosts):
        return False
    blob = f"{titulo} {descricao} {link}".lower()
    if any(k in blob for k in ("about", "contact", "news", "blog", "event", "press release", "careers")):
        return False
    markers = (
        "call",
        "open call",
        "deadline",
        "apply",
        "application",
        "submission",
        "challenge",
        "proposal",
        "grant",
        "funding",
        "venture",
        "startup",
        "procurement",
        "tender",
        "convocatoria",
        "propuesta",
        "financiamiento",
        "cooperacion tecnica",
        "cooperacao tecnica",
        "pathfinder",
        "accelerator",
        "transition",
        "eurostars",
        "globalstars",
    )
    return any(m in blob for m in markers)


def _inovacao_internacional_onda_c_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """Relaxamento local Onda C: fontes oficiais com call/apply/deadline/tender/campaign concreto."""
    src = (source_name or "").strip().lower()
    if src not in _LOTE_INOVACAO_INTERNACIONAL_ONDA_C_SOURCES:
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr and "Noticia ou pagina generica" not in rr:
        return False
    lk = (link or "").lower()
    hosts = _LOTE_INOVACAO_INTERNACIONAL_ONDA_C_HOSTS.get(src, ())
    if not hosts or not any(h in lk for h in hosts):
        return False
    path = urlparse(lk).path.strip("/").lower()
    if not path and src not in {"esa_star"}:
        return False
    blob = f"{titulo} {descricao} {link}".lower()
    if any(k in blob for k in ("about", "contact", "careers", "privacy", "cookie", "press release", "blog")):
        return False
    markers = (
        "call",
        "open call",
        "deadline",
        "closing date",
        "apply",
        "application",
        "submission",
        "submit",
        "competition",
        "funding",
        "grant",
        "opportunity",
        "proposal",
        "fellowship",
        "procurement",
        "tender",
        "invitation to tender",
        "itt",
        "campaign",
        "channel",
        "submit ideas",
        "esa-star",
        "eurostars",
    )
    return any(m in blob for m in markers)


def _dod_sbir_sttr_topic_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local (Recovery A): tópico/solicitação oficial em sbir.gov quando o gate
    corta HTML magro (ex.: API 429). Não altera opportunity_gate.py — exige URL de detalhe.
    """
    if (source_name or "").strip().lower() != "dod_sbir_sttr":
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr and "Noticia ou pagina generica" not in rr:
        return False
    lk = (link or "").lower()
    if "sbir.gov" not in lk:
        return False
    try:
        path = (urlparse(lk).path or "").rstrip("/").lower()
    except Exception:
        return False
    if re.match(r"^/topics/\d+", path):
        detail_ok = True
    elif path.startswith("/solicitation/") and len(path) > len("/solicitation"):
        detail_ok = True
    else:
        parts = [p for p in path.split("/") if p]
        detail_ok = len(parts) >= 2 and parts[0] == "solicitations" and bool(parts[1])
    if not detail_ok:
        return False
    blob = f"{titulo} {descricao} {link}".lower()
    return any(
        m in blob
        for m in (
            "sbir",
            "sttr",
            "solicitation",
            "topic",
            "phase i",
            "phase ii",
            "agency",
            "proposal",
        )
    )


def _petrobras_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local Petrobras: seleções na Bússola Social e regulamentos PDF oficiais
    passam baixa pontuação do opportunity_gate global sem alterar o gate.
    """
    src = (source_name or "").strip().lower()
    if src != "petrobras":
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    lk = (link or "").lower()
    bussola = "bussolasocial.com.br/petrobras/editais" in lk
    doc_pdf = "petrobras.com.br" in lk and "/documents/" in lk and ".pdf" in lk
    if not bussola and not doc_pdf:
        return False
    blob = f"{titulo} {descricao} {lk}".lower()
    markers = (
        "incentiv",
        "nao incentiv",
        "não incentiv",
        "regulamento",
        "selecao",
        "seleção",
        "edital",
        "projeto",
        "cultural",
        "patrocinio",
        "patrocínio",
        "projetos",
        "inscric",
        "inscriç",
    )
    return any(m in blob for m in markers)


def _marinha_hub_only(link: str) -> bool:
    """Hub institucional sem detalhe (não relaxar opportunity_gate)."""
    lk = (link or "").lower().rstrip("/")
    if "marinha.mil.br" not in lk:
        return False
    return bool(re.search(r"/editais$", lk) or re.search(r"/licitacoes$", lk) or re.search(r"/licitações$", lk))


def _marinha_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """Relaxamento local Marinha: páginas de detalhe com sinais de licitação/compra pública."""
    src = (source_name or "").strip().lower()
    if src != "marinha":
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    lk = (link or "").lower()
    if "marinha.mil.br" not in lk:
        return False
    if _marinha_hub_only(str(link or "")):
        return False
    blob = f"{titulo} {descricao} {lk}".lower()
    markers = (
        "preg",
        "licit",
        "edital",
        "uasg",
        "modalidade",
        "contrata",
        "aquisi",
        "dispensa",
        "compra public",
        "compra públ",
        ".pdf",
        "processo",
        "ata de",
        "julgamento",
    )
    return any(m in blob for m in markers)


def _amazul_hub_only(link: str) -> bool:
    lk = (link or "").lower().rstrip("/")
    if "amazul.mar.mil.br" not in lk:
        return False
    return bool(
        re.search(r"/licitacoes$", lk)
        or re.search(r"/licitações$", lk)
        or re.search(r"/chamadas-publicas$", lk)
        or re.search(r"/chamadas-públicas$", lk)
    )


def _amazul_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """Relaxamento local AMAZUL: detalhe com licitação/chamada/edital (não hub vazio)."""
    src = (source_name or "").strip().lower()
    if src != "amazul":
        return False
    rr = gate_reason or ""
    if (
        "Relevancia limite" not in rr
        and "Pontuacao abaixo" not in rr
        and "Noticia ou pagina generica" not in rr
    ):
        return False
    lk = (link or "").lower()
    if "amazul.mar.mil.br" not in lk:
        return False
    if _amazul_hub_only(str(link or "")):
        return False
    blob = f"{titulo} {descricao} {lk}".lower()
    markers = (
        "preg",
        "licit",
        "edital",
        "chamada",
        "uasg",
        "modalidade",
        "contrata",
        "aquisi",
        "dispensa",
        "compra public",
        "compra públ",
        ".pdf",
        "subven",
        "fomento",
        "nuclear",
    )
    return any(m in blob for m in markers)


def _dcta_ita_iae_hub_only(link: str) -> bool:
    """Raiz gov.br/dcta|ita|iae/pt-br ou secções índice (sem objeto concreto)."""
    lk = (link or "").lower().rstrip("/")
    if "gov.br" not in lk:
        return False
    if not any(x in lk for x in ("/dcta/", "/ita/", "/iae/")):
        return False
    try:
        path = urlparse(lk).path.strip("/")
        parts = [p for p in path.split("/") if p]
    except Exception:
        return False
    if len(parts) <= 2:
        return True
    if len(parts) == 3:
        hub_slugs = (
            "chamamentos-e-licitacoes",
            "chamamentos-e-licitações",
            "editais",
            "licitacoes",
            "licitações",
            "compras",
            "noticias",
            "notícias",
            "concursos",
            "acesso-a-informacao",
            "acesso-a-informação",
            "servicos",
            "serviços",
        )
        return parts[2] in hub_slugs
    return False


def _dcta_ita_iae_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """Relaxamento local DCTA/ITA/IAE: detalhe gov.br com sinais de edital/chamada/licitação/académico."""
    src = (source_name or "").strip().lower()
    if src != "dcta_ita_iae":
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    lk = (link or "").lower()
    if "gov.br" not in lk or not any(x in lk for x in ("/dcta/", "/ita/", "/iae/")):
        return False
    if _dcta_ita_iae_hub_only(str(link or "")):
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if ex.get("metodo_extracao") == "fallback_public_index":
        return False
    blob = f"{titulo} {descricao} {lk} {item.get('acao') or ''} {item.get('tipo_recurso') or ''}".lower()
    markers = (
        "edital",
        "chamada",
        "licit",
        "preg",
        "compra public",
        "compra públ",
        "contrata",
        "dispensa",
        "uasg",
        "modalidade",
        "fomento",
        "pesquisa",
        "bolsa",
        "mestrado",
        "doutorado",
        "stricto sensu",
        "processo seletivo",
        "seleção",
        "selecao",
        "credenciamento",
        ".pdf",
        "programa de",
        "linha de pesquisa",
    )
    return any(m in blob for m in markers)


def _horizon_europe_hub_only(link: str) -> bool:
    lk = (link or "").lower().rstrip("/")
    if "europa.eu" not in lk and "ec.europa" not in lk:
        return False
    if "topic-search" in lk and "topic-details" not in lk:
        return True
    if re.search(r"horizon-europe_?en?$", lk) or re.search(r"horizon-europe/?$", lk):
        return True
    return False


def _horizon_europe_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """Relaxamento local Horizon Europe: detalhe EC com sinais de call/topic/grant (não hub de busca)."""
    if (source_name or "").strip().lower() != "horizon_europe":
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    lk = (link or "").lower()
    if "europa.eu" not in lk and "ec.europa" not in lk:
        return False
    if _horizon_europe_hub_only(str(link or "")):
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if ex.get("metodo_extracao") == "fallback_public_index":
        return False
    blob = f"{titulo} {descricao} {lk} {item.get('acao') or ''}".lower()
    markers = (
        "horizon",
        "topic",
        "call",
        "grant",
        "funding",
        "tender",
        "work programme",
        "submission",
        "deadline",
        "innovation action",
        "ria",
        "csa",
        "msca",
        "cascade",
        "coordinator",
        "consortium",
        ".pdf",
    )
    return any(m in blob for m in markers)


def _erc_hub_only(link: str) -> bool:
    lk = (link or "").lower().rstrip("/")
    if "erc.europa.eu" not in lk:
        return False
    if lk.endswith("/funding") or lk.endswith("/funding/advanced-grants"):
        return True
    if lk.endswith("/apply-grant") or lk.endswith("/apply-grants"):
        return True
    return False


def _erc_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    if (source_name or "").strip().lower() != "erc":
        return False
    lk = (link or "").lower()
    rr = gate_reason or ""
    rr_l = rr.lower()
    if "erc.europa.eu" not in lk:
        return False
    if _erc_hub_only(str(link or "")):
        return False
    login_fp = "login" in rr_l or "autenticacao" in rr_l
    if (
        "relevancia limite" not in rr_l
        and "pontuacao abaixo" not in rr_l
        and not (login_fp and "/apply-grant/" in lk)
    ):
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if ex.get("metodo_extracao") == "fallback_public_index":
        return False
    blob = f"{titulo} {descricao} {lk}".lower()
    markers = (
        "starting grant",
        "consolidator",
        "advanced grant",
        "synergy",
        "proof of concept",
        "erc",
        "call",
        "deadline",
        "proposal",
        "applicant",
        "researcher",
        "grant",
        ".pdf",
    )
    return any(m in blob for m in markers)


def _doe_arpae_hub_only(link: str) -> bool:
    lk = (link or "").lower().rstrip("/")
    if "arpa-e-foa.energy.gov" in lk:
        return "#foaid" not in lk
    if "arpa-e.energy.gov" not in lk and "energy.gov" not in lk:
        return False
    return bool(re.search(r"funding-opportunities/?$", lk))


def _doe_arpae_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    if (source_name or "").strip().lower() != "doe_arpae":
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    lk = (link or "").lower()
    if "arpa-e-foa.energy.gov" not in lk and "arpa-e.energy.gov" not in lk and "energy.gov" not in lk:
        return False
    if _doe_arpae_hub_only(str(link or "")):
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if ex.get("metodo_extracao") == "fallback_public_index":
        return False
    if "arpa-e-foa.energy.gov" in lk and "#foaid" in lk:
        return True
    blob = f"{titulo} {descricao} {lk}".lower()
    markers = (
        "foa",
        "funding opportunity",
        "solicitation",
        "arpa-e",
        "arpa e",
        "open funding",
        "apply",
        "concept paper",
        "teaming",
        "award",
        "program",
        "energy",
        ".pdf",
    )
    return any(m in blob for m in markers)


def _nato_diana_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    if (source_name or "").strip().lower() != "nato_diana":
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    lk = (link or "").lower()
    if "diana.nato.int" not in lk:
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if ex.get("metodo_extracao") == "fallback_public_index":
        return False
    blob = f"{titulo} {descricao} {lk}".lower()
    markers = (
        "diana",
        "nato",
        "challenge",
        "innovation",
        "accelerator",
        "dual-use",
        "dual use",
        "startup",
        "sme",
        "trl",
        "portal",
        "warfighter",
        "faq",
        "curated_official_public_brief",
    )
    return any(m in blob for m in markers)


def _senai_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local SENAI / plataforma_industria (Portal da Indústria): não é gov.br confiável no gate global;
    permite seguir só com URL de detalhe + sinais de chamada/programa/fomento.
    """
    src = (source_name or "").strip().lower()
    if src not in ("senai", "plataforma_industria"):
        return False
    rr = gate_reason or ""
    if (
        "Relevancia limite" not in rr
        and "Pontuacao abaixo" not in rr
        and "Noticia ou pagina generica" not in rr
    ):
        return False
    lk = (link or "").lower()
    if "portaldaindustria.com.br" not in lk:
        return False
    strip = lk.rstrip("/")
    if strip.endswith("/senai") or strip.endswith("/senai/canais/chamadas-publicas") or strip.endswith(
        "/senai/canais/editais"
    ):
        return False
    # Hub da plataforma sem /categoria/ — índice genérico
    if "/categoria/" not in lk and strip.endswith("/canais/plataforma-inovacao-para-industria"):
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if ex.get("metodo_extracao") == "fallback_public_index":
        return False
    blob = f"{titulo} {descricao} {item.get('acao') or ''} {item.get('tipo_recurso') or ''} {lk}".lower()
    markers = (
        "chamada",
        "edital",
        "programa",
        "inovação",
        "inovacao",
        "fomento",
        "projeto",
        "financi",
        "credito",
        "crédito",
        "senai",
        "smart factory",
        "plataforma",
        "rota 2030",
        "finep",
        "bndes",
        "seleção",
        "selecao",
        "inscri",
        "submiss",
        "parceria",
        "coopera",
    )
    return any(m in blob for m in markers)


def _softex_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local Softex: páginas de programa/inscrição sem score alto no gate global.
    """
    src = (source_name or "").strip().lower()
    if src != "softex":
        return False
    rr = gate_reason or ""
    if (
        "Relevancia limite" not in rr
        and "Pontuacao abaixo" not in rr
        and "Noticia ou pagina generica" not in rr
    ):
        return False
    lk = (link or "").lower()
    if "softex.br" not in lk:
        return False
    if lk.rstrip("/") in (
        "https://softex.br",
        "http://softex.br",
        "https://www.softex.br",
        "http://www.softex.br",
    ):
        return False
    path = (urlparse(link).path or "").strip("/")
    if len(path) < 6:
        return False
    blob = f"{titulo} {descricao} {item.get('acao') or ''} {lk}".lower()
    markers = (
        "edital",
        "chamada",
        "programa",
        "inscri",
        "fomento",
        "seleção",
        "selecao",
        "submiss",
        "geek",
        "capacita",
        "acelera",
        "startup",
        "bolsa",
        "transformação digital",
        "transformacao digital",
    )
    if not any(m in blob for m in markers):
        return False
    # Notícia institucional sem oportunidade (exportação / evento) — manter bloqueio
    noise = ("exportação", "exportacao", "hannover", "brasil-it supera", "reforça presença", "reforca presenca")
    if "/noticias/" in lk or "brasil-it" in lk:
        if not any(m in blob for m in ("inscri", "edital", "chamada", "programa", "fomento", "seleção", "selecao")):
            return False
        if any(n in blob for n in noise) and "inscri" not in blob and "edital" not in blob:
            return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    anexos = ex.get("anexos") if isinstance(ex.get("anexos"), list) else []
    docs = ex.get("documentos") if isinstance(ex.get("documentos"), list) else []
    if anexos or docs or str(ex.get("pdf_url") or "").strip():
        return True
    # Texto de detalhe suficiente (crawler já abriu a página)
    return len((descricao or "").strip()) >= 120 or len((titulo or "").strip()) >= 24


def _ambev_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local Ambev / 100+ Accelerator: desafios temáticos (open innovation) com score
    baixo no gate global por texto em inglês sem marcadores PT/\"grant\" explícitos.
    Não altera opportunity_gate.py — só continua o pipeline quando o URL e o texto são coerentes.
    """
    src = (source_name or "").strip().lower()
    if src != "ambev":
        return False
    rr = gate_reason or ""
    if (
        "Relevancia limite" not in rr
        and "Pontuacao abaixo" not in rr
        and "Noticia ou pagina generica" not in rr
    ):
        return False
    lk = (link or "").lower()
    blob = f"{titulo} {descricao} {lk}".lower()
    if any(x in blob for x in ("resultado final", "page not found", "closed", "newsroom")):
        return False
    marketing_only = (
        "/news/" in lk
        or "/press/" in lk
        or "/marcas" in lk
        or "/produtos" in lk
        or "/sustentabilidade" in lk
    )
    if marketing_only and "100accelerator.com/challenges/" not in lk:
        return False
    if "100accelerator.com/challenges/" in lk:
        parts = [p for p in lk.split("/") if p]
        try:
            ix = parts.index("challenges")
        except ValueError:
            return False
        if ix + 1 >= len(parts):
            return False
        slug = parts[ix + 1]
        if slug in ("challenges", "challenge", ""):
            return False
        return len((descricao or "").strip()) >= 40 or len((titulo or "").strip()) >= 6
    if "ambev.com.br" in lk:
        path = (urlparse(link).path or "").strip("/")
        if len(path.split("/")) < 1:
            return False
        markers = ("startup", "programa", "inova", "edital", "chamada", "desafio", "oportunidade", "negocio")
        if not any(m in blob for m in markers):
            return False
        return len((descricao or "").strip()) >= 40
    return False


def _corporate_supplier_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local para fontes *_suppliers / japan_kawasaki_heavy: o gate marca \"login\"
    por menções a registo/login em textos legítimos de onboarding de fornecedor (não altera opportunity_gate.py).
    """
    src = (source_name or "").strip().lower()
    if src not in (
        "bae_systems_suppliers",
        "rheinmetall_suppliers",
        "thales_suppliers",
        "general_dynamics_suppliers",
        "lockheed_martin_suppliers",
        "japan_kawasaki_heavy",
    ) and not src.endswith("_suppliers"):
        return False
    rr = gate_reason or ""
    low_rr = rr.lower()
    if "login" not in low_rr and "autentic" not in low_rr and "relevancia limite" not in low_rr:
        return False
    lk = (link or "").lower()
    if any(x in lk for x in ("/careers", "/jobs", "/investor", "/investors", "/ir/")):
        return False
    if "page=" in lk and not any(x in lk for x in ("become-a-supplier", "lieferantenportal")):
        return False
    supplier_hit = any(
        p in lk
        for p in (
            "become-a-supplier",
            "supplier",
            "suppliers",
            "procurement",
            "lieferantenportal",
            "ivalua.app",
            "hicx.net",
            "procurementportal",
            "supplier-relations",
            "/supplier",
            "purchasing",
        )
    )
    if not supplier_hit:
        return False
    blob = f"{titulo} {descricao} {lk}".lower()
    markers = (
        "supplier",
        "procurement",
        "purchasing",
        "vendor",
        "registration",
        "onboarding",
        "fornecedor",
        "portal",
        "lieferant",
        "sourcing",
    )
    if not any(m in blob for m in markers):
        return False
    if "ivalua.app" in lk or "hicx.net" in lk:
        return len((titulo or "").strip()) >= 8
    return len((descricao or "").strip()) >= 60 or len((titulo or "").strip()) >= 14


def _apex_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """Relaxamento local ApexBrasil: páginas de programa/chamada/licitação com gate conservador."""
    src = (source_name or "").strip().lower()
    if src != "apex":
        return False
    rr = gate_reason or ""
    if (
        "Relevancia limite" not in rr
        and "Pontuacao abaixo" not in rr
        and "Noticia ou pagina generica" not in rr
    ):
        return False
    lk = (link or "").lower()
    if "apexbrasil.com.br" not in lk:
        return False
    if "/eventos" in lk and "inscri" not in f"{titulo} {descricao}".lower():
        return False
    blob = f"{titulo} {descricao} {item.get('acao') or ''} {lk}".lower()
    markers = (
        "edital",
        "chamada",
        "licit",
        "pregao",
        "pregão",
        "programa",
        "inscri",
        "seleção",
        "selecao",
        "proposta",
        "exportação",
        "exportacao",
        "internacionaliz",
        "contrato",
        "fomento",
    )
    if not any(m in blob for m in markers):
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if str(ex.get("pdf_url") or "").strip().startswith("http"):
        return True
    anexos = ex.get("anexos") if isinstance(ex.get("anexos"), list) else []
    docs = ex.get("documentos") if isinstance(ex.get("documentos"), list) else []
    if anexos or docs:
        return True
    return len((descricao or "").strip()) >= 100 or len((titulo or "").strip()) >= 18


def _faperg_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """Relaxamento local FAPERGS (id de fonte `faperg`): editais/chamadas estaduais."""
    src = (source_name or "").strip().lower()
    if src != "faperg":
        return False
    rr = gate_reason or ""
    if (
        "Relevancia limite" not in rr
        and "Pontuacao abaixo" not in rr
        and "Noticia ou pagina generica" not in rr
    ):
        return False
    lk = (link or "").lower()
    if "fapergs.rs.gov.br" not in lk:
        return False
    blob = f"{titulo} {descricao} {lk}".lower()
    markers = (
        "edital",
        "chamada",
        "fomento",
        "bolsa",
        "programa",
        "pesquisa",
        "inscri",
        "processo seletivo",
        "auxilio",
        "auxílio",
        "centelha",
    )
    if not any(m in blob for m in markers):
        return False
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    if str(ex.get("pdf_url") or "").strip().startswith("http"):
        return True
    docs = ex.get("documentos") if isinstance(ex.get("documentos"), list) else []
    anexos = ex.get("anexos") if isinstance(ex.get("anexos"), list) else []
    if docs or anexos:
        return True
    return len((descricao or "").strip()) >= 80


def _pncp_soft_continue(
    source_name: str,
    gate_reason: str,
    item: Dict[str, Any],
    titulo: str,
    descricao: str,
    link: str,
) -> bool:
    """
    Relaxamento local e cauteloso para PNCP (não-defesa):
    somente quando há metadados oficiais e sinais de contratação pública.
    """
    src = (source_name or "").strip().lower()
    if src != "pncp":
        return False
    rr = gate_reason or ""
    if "Relevancia limite" not in rr and "Pontuacao abaixo" not in rr:
        return False
    lk = (link or "").lower()
    ex = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    has_ctrl = bool(
        str(
            ex.get("codigo_oportunidade")
            or ex.get("numero_edital")
            or ex.get("pncp_id")
            or ex.get("numero_controle_pncp")
            or ""
        ).strip()
    )
    if "pncp.gov.br" not in lk:
        # Sistema de origem externo (ex.: portal estadual) com controle PNCP nos extras.
        if not has_ctrl or not lk.startswith("http"):
            return False
    # Não permitir índice genérico puro do portal.
    if lk.rstrip("/") in ("https://pncp.gov.br/app/editais", "http://pncp.gov.br/app/editais"):
        return False
    blob = f"{titulo} {descricao} {item.get('acao') or ''} {item.get('tipo_recurso') or ''}".lower()
    procurement_markers = (
        "pncp",
        "contrata",
        "licit",
        "pregão",
        "pregao",
        "processo",
        "compra",
        "contrato",
        "edital",
        "orgao",
        "órgão",
        "objeto",
        "valor",
        "prazo",
    )
    if not any(m in blob for m in procurement_markers):
        return False
    has_official_meta = any(
        str(ex.get(k) or "").strip()
        for k in ("numero_edital", "numero_processo", "codigo_oportunidade", "numero_controle_pncp")
    )
    has_core_data = bool(str(item.get("fim_inscricao") or "").strip()) or bool(str(item.get("valor") or "").strip())
    return has_official_meta or has_core_data


def _transform_item_with_result(item: Any, source_name: str) -> TransformResult:
    """Portão de qualidade: devolve TransformResult (payload ou rejeição documentada)."""
    warnings: List[str] = []
    if not isinstance(item, dict):
        return TransformResult(
            payload=None,
            rejected=True,
            rejection_reason="item_nao_dict",
            warnings=warnings,
            report_delta={},
            original_item=None,
            content_type_detectado="invalido",
        )

    orig = dict(item)
    work = normalize_aliases(dict(item))
    clean_text_fields(work, ("titulo", "descricao"))

    listing_desc = clean_extracted_text(work.get("descricao") or work.get("resumo") or "")
    desc = listing_desc
    titulo = clean_extracted_text(work.get("titulo") or "")
    is_generic_title = titulo.lower() in [
        "edital",
        "chamada",
        "chamada pública",
        "oportunidade",
        "imposto de renda",
    ]

    extras_raw: Dict[str, Any] = dict(work.get("extras") or {})
    extras_text = " ".join(str(v) for v in extras_raw.values() if isinstance(v, (str, int, float)))
    full_text = f"{titulo} {desc} {extras_text}"

    link = work.get("link") or work.get("url") or work.get("url_pagina") or work.get("url_chamada")
    if link and isinstance(link, str) and link.count("http") > 1:
        parts = link.split("http")
        link = "http" + parts[-1]
        logger.debug("Link corrigido (duplicidade http): %s", link)

    if isinstance(link, str) and (source_name or "").strip().lower() == "pncp":
        lk_root = link.split("?", 1)[0].rstrip("/").lower()
        if lk_root in ("https://pncp.gov.br", "http://pncp.gov.br"):
            ctrl = str(
                extras_raw.get("codigo_oportunidade")
                or extras_raw.get("pncp_id")
                or extras_raw.get("numero_edital")
                or ""
            ).strip()
            if ctrl and "app/editais" not in link.lower():
                link = f"https://pncp.gov.br/app/editais/{ctrl}"
                work["link"] = link

    if link and any(x in link.lower() for x in ["/search?", "SearchableText=", "termos="]):
        logger.warning("Link de busca ignorado em %s: %s", source_name, link)
        return TransformResult(
            payload=None,
            rejected=True,
            rejection_reason="link_busca",
            warnings=warnings,
            report_delta={},
            original_item=orig,
            content_type_detectado="pagina_generica",
        )

    src_l_noise = (source_name or "").strip().lower()
    if src_l_noise in _LOTE_CREDITO_BR_SOURCES:
        from CORE.credito_brasil_onda_a_noise import credito_brasil_onda_a_ruido_motivo as _onda_a_noise

        rmot = _onda_a_noise(src_l_noise, titulo, desc, str(link or ""), extras_raw)
        if rmot:
            warnings.append("credito_brasil_onda_a_noise_filter")
            return TransformResult(
                payload=None,
                rejected=True,
                rejection_reason=f"onda_a_ruido_institucional:{rmot}",
                warnings=warnings,
                report_delta={},
                original_item=orig,
                content_type_detectado="pagina_institucional",
            )

    pdf_url = extract_pdf_url(work)
    full_text_pre = build_full_text(work, titulo=titulo, descricao=desc, pdf_text=None)
    disc, disc_reason, ct_pre, sinais_pre = should_discard_item(
        titulo=titulo,
        descricao=desc,
        link=str(link or ""),
        pdf_url=pdf_url,
        full_text=full_text_pre,
        extras=extras_raw,
    )
    route_ct_pre = infer_content_type(
        {**work, "titulo": titulo, "descricao": desc, "link": link, "extras": {**extras_raw, "content_type_detectado": ct_pre}}
    )
    if disc and route_ct_pre in ("noticia", "pesquisa"):
        warnings.append(f"routed_discard_candidate_{route_ct_pre}")
        extras_raw["discard_reason_for_edital"] = disc_reason
        extras_raw["content_type"] = route_ct_pre
        extras_raw["destination_table"] = route_ct_pre
        disc = False
    if disc:
        return TransformResult(
            payload=None,
            rejected=True,
            rejection_reason=disc_reason,
            warnings=warnings,
            report_delta={"sinais": sinais_pre},
            original_item=orig,
            content_type_detectado=ct_pre,
            sinais_detectados=list(sinais_pre),
        )

    gate_item = {**work, "titulo": titulo, "descricao": desc, "link": link, "extras": extras_raw}
    _gate = None
    try:
        try:
            from opportunity_gate import evaluate_item_dict as _eval_gate
        except ImportError:
            from CORE.opportunity_gate import evaluate_item_dict as _eval_gate

        _gate = _eval_gate(gate_item)
    except Exception:
        logger.exception(
            "Transformer: falha ao executar opportunity_gate (fonte=%s, link=%s)",
            source_name,
            link,
        )
        warnings.append("opportunity_gate_eval_exception")

    if _gate is not None and _gate.gate_category:
        extras_raw["opportunity_gate_category"] = _gate.gate_category

    content_type_pre = route_ct_pre
    if _gate is not None and not _gate.keep:
        try:
            from opportunity_gate import trusted_br_relevance_soft_continue as _gate_soft
        except ImportError:
            from CORE.opportunity_gate import trusted_br_relevance_soft_continue as _gate_soft

        if content_type_pre in ("noticia", "pesquisa"):
            warnings.append(f"routed_non_edital_{content_type_pre}")
            extras_raw["opportunity_gate_rejected_for_edital"] = True
            extras_raw["opportunity_gate_rejection_reason"] = _gate.rejection_reason or ""
            extras_raw["content_type"] = content_type_pre
            extras_raw["destination_table"] = content_type_pre
        elif _gate_soft(_gate, titulo, str(link or "")):
            warnings.append("opportunity_gate_trusted_br_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw.setdefault("opportunity_gate_category", _gate.gate_category or "")
        elif _pncp_defesa_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_pncp_defesa_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "pncp_defesa_local"
            extras_raw.setdefault("opportunity_gate_category", "compra_publica")
        elif _pncp_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_pncp_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "pncp_local"
            extras_raw.setdefault("opportunity_gate_category", "licitacao")
        elif _badesul_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_badesul_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "badesul_local"
            extras_raw.setdefault("opportunity_gate_category", "linha_credito")
        elif _credito_brasil_onda_a_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_credito_br_onda_a_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "credito_brasil_onda_a"
            extras_raw.setdefault("opportunity_gate_category", "linha_credito")
        elif _multilateral_onda_b_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_multilateral_onda_b_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "credito_multilateral_onda_b"
            extras_raw.setdefault("opportunity_gate_category", "funding_opportunity")
        elif _inovacao_internacional_onda_c_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_inovacao_internacional_onda_c_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "inovacao_internacional_onda_c"
            extras_raw.setdefault("opportunity_gate_category", "funding_opportunity")
        elif _dod_sbir_sttr_topic_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_dod_sbir_sttr_recovery_a_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "dod_sbir_sttr_recovery_a_local"
            extras_raw.setdefault("opportunity_gate_category", "funding_opportunity")
        elif _petrobras_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_petrobras_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "petrobras_local"
            extras_raw.setdefault("opportunity_gate_category", "chamada_publica")
        elif _marinha_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_marinha_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "marinha_local"
            extras_raw.setdefault("opportunity_gate_category", "licitacao")
        elif _amazul_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_amazul_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "amazul_local"
            extras_raw.setdefault("opportunity_gate_category", "compra_publica")
        elif _dcta_ita_iae_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_dcta_ita_iae_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "dcta_ita_iae_local"
            extras_raw.setdefault("opportunity_gate_category", "chamada_publica")
        elif _horizon_europe_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_horizon_europe_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "horizon_europe_local"
            extras_raw["opportunity_gate_category"] = "grant"
        elif _erc_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_erc_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "erc_local"
            extras_raw["opportunity_gate_category"] = "grant"
        elif _doe_arpae_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_doe_arpae_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "doe_arpae_local"
            extras_raw["opportunity_gate_category"] = "funding_opportunity"
        elif _nato_diana_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_nato_diana_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "nato_diana_local"
            extras_raw["opportunity_gate_category"] = "chamada_publica"
        elif _senai_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            _srcn = (source_name or "").strip().lower()
            if _srcn == "plataforma_industria":
                warnings.append("opportunity_gate_plataforma_industria_soft")
                extras_raw["opportunity_gate_relax_scope"] = "plataforma_industria_local"
            else:
                warnings.append("opportunity_gate_senai_soft")
                extras_raw["opportunity_gate_relax_scope"] = "senai_local"
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw.setdefault("opportunity_gate_category", "chamada_publica")
        elif _softex_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_softex_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "softex_local"
            extras_raw.setdefault("opportunity_gate_category", "programa")
        elif _apex_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_apex_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "apex_local"
            extras_raw.setdefault("opportunity_gate_category", "chamada_publica")
        elif _faperg_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_faperg_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "faperg_local"
            extras_raw.setdefault("opportunity_gate_category", "edital")
        elif _ambev_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_ambev_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "ambev_local"
            extras_raw.setdefault("opportunity_gate_category", "innovation_program")
        elif _corporate_supplier_soft_continue(
            source_name=source_name,
            gate_reason=_gate.rejection_reason or "",
            item=work,
            titulo=titulo,
            descricao=desc,
            link=str(link or ""),
        ):
            warnings.append("opportunity_gate_corporate_supplier_soft")
            extras_raw["opportunity_gate_relaxed"] = True
            extras_raw["opportunity_gate_relax_reason"] = _gate.rejection_reason or ""
            extras_raw["opportunity_gate_relax_scope"] = "corporate_supplier_local"
            extras_raw.setdefault("opportunity_gate_category", "supplier_portal")
        else:
            _olo_patch: Optional[Dict[str, Any]] = None
            try:
                from CORE.official_link_only import official_link_only_extras_patch as _olo_fn
            except ImportError:
                from official_link_only import official_link_only_extras_patch as _olo_fn

            _olo_patch = _olo_fn(
                {**work, "titulo": titulo, "descricao": desc, "link": link, "extras": extras_raw},
                str(source_name or ""),
                _gate.keep,
                _gate.access_status,
                _gate.rejection_reason or "",
            )
            if _olo_patch:
                warnings.append("opportunity_gate_official_link_only")
                for _k, _v in _olo_patch.items():
                    extras_raw[_k] = _v
            else:
                logger.info(
                    "Transformer: excluido pelo opportunity_gate (%s): %s",
                    (_gate.rejection_reason or _gate.access_status or ""),
                    link,
                )
                return TransformResult(
                    payload=None,
                    rejected=True,
                    rejection_reason=_gate.rejection_reason or str(_gate.access_status) or "opportunity_gate",
                    warnings=warnings,
                    report_delta={"detected_terms": list(_gate.detected_terms or [])},
                    original_item=orig,
                    content_type_detectado=str(_gate.opportunity_intent or ct_pre),
                    sinais_detectados=list(_gate.detected_terms or []),
                )

    pdf_text = None
    if pdf_url:
        pdf_text = read_pdf_text(pdf_url, page_referer=link)
        if pdf_text:
            pdf_text = clean_extracted_text(pdf_text)
            if is_generic_title:
                lines = [l.strip() for l in pdf_text.split(".") if len(l.strip()) > 20]
                if lines:
                    titulo = lines[0][:200]

    full_text = build_full_text(work, titulo=titulo, descricao=desc, pdf_text=pdf_text)
    ct_post = detect_content_type(
        titulo=titulo, descricao=desc, link=str(link or ""), full_text=full_text
    )
    content_type_post = infer_content_type(
        {
            **work,
            "titulo": titulo,
            "descricao": desc,
            "link": link,
            "tipo_recurso": item.get("tipo_recurso") if isinstance(item, dict) else "",
            "extras": {**extras_raw, "content_type_detectado": ct_post},
        }
    )
    if ct_post == "noticia" and not has_opportunity_signal(full_text):
        content_type_post = "noticia"

    hash_parts: List[Any] = [titulo, desc, pdf_text]
    if (source_name or "").strip().lower() == "pncp":
        hash_parts.extend(
            [
                str(link or ""),
                str(extras_raw.get("codigo_oportunidade") or extras_raw.get("pncp_id") or extras_raw.get("numero_edital") or ""),
                str(extras_raw.get("numero_processo") or ""),
            ]
        )
    content_hash = generate_content_hash(hash_parts)
    prog, acao = extract_program_action(titulo)

    data_publicacao = (
        work.get("data_publicacao")
        or work.get("publicado_em")
        or normalize_date_str(str(work.get("data") or ""))
        or normalize_date_str(str(work.get("published_at") or ""))
    )
    fim_raw = (
        work.get("fim_inscricao")
        or work.get("prazo_envio")
        or work.get("deadline")
        or work.get("inscricoes_fim")
        or extract_deadline_from_text(full_text)
    )
    fim_inscricao = normalize_date_str(str(fim_raw)) if fim_raw else None
    data_publicacao = normalize_date_str(str(data_publicacao)) if data_publicacao else None
    if not data_publicacao:
        for maybe_date in re.findall(DATE_CANDIDATE_REGEX, full_text):
            normalized = normalize_date_str(maybe_date)
            if normalized:
                data_publicacao = normalized
                break

    item_programa = work.get("programa")
    item_acao = work.get("acao")
    if not item_programa or not item_acao:
        extra_prog, extra_acao = extract_program_action_from_text(full_text)
        item_programa = item_programa or prog or extra_prog
        item_acao = item_acao or acao or extra_acao

    item_valor = work.get("valor") or extras_raw.get("valor")
    if not item_valor:
        item_valor = extract_value(full_text)

    item_tipo = work.get("tipo_recurso") or extras_raw.get("tipo_recurso")
    if not item_tipo or item_tipo == "Não Especificado":
        item_tipo = extract_resource_type(full_text)

    docs = extract_documentos(work)
    numero_edital = extract_numero_edital(full_text)
    numero_processo = extract_numero_processo(full_text)
    codigo_op = extract_codigo_oportunidade(full_text)
    cronograma = extract_cronograma(full_text)

    enrich_patch: Dict[str, Any] = {}
    if fim_raw and str(fim_raw).strip():
        raw_s = str(fim_raw).strip()
        if re.search(r"[a-zA-Zà-úÀ-Ú]", raw_s) or "até" in raw_s.lower():
            enrich_patch["fim_inscricao_original"] = raw_s
        elif normalize_date_str(raw_s) != fim_inscricao:
            enrich_patch["fim_inscricao_original"] = raw_s
    for _rk in ("prazo_envio_raw", "fim_inscricao_raw"):
        _rv = work.get(_rk) or extras_raw.get(_rk)
        if _rv:
            enrich_patch[_rk] = str(_rv).strip()[:200]
    for _dk in ("deadline", "deadline_source", "deadline_source_field", "grants_close_date"):
        _dv = extras_raw.get(_dk)
        if _dv is not None and _dv != "":
            enrich_patch[_dk] = _dv

    desc_enriched, desc_extras = enrich_description(
        work,
        listing_desc=listing_desc,
        pdf_text=pdf_text,
        programa=str(item_programa or ""),
        valor=str(item_valor or ""),
        publico_alvo=str(work.get("publico_alvo") or extras_raw.get("publico_alvo") or ""),
        fonte=str(work.get("fonte") or source_name.upper()),
        titulo=titulo,
    )
    enrich_patch.update(desc_extras)
    desc_final = desc_enriched
    if desc_final and len(desc_final) > MAX_DESCRICAO_CHARS:
        enrich_patch.setdefault("descricao_completa", desc_final[:50000])
        desc_final = desc_final[:MAX_DESCRICAO_CHARS]

    orphans = {
        k: v
        for k, v in work.items()
        if k not in CANONICAL_ITEM_KEYS and k != "extras"
    }
    merged_extras = merge_item_extras(
        crawler_extras=extras_raw,
        orphan_fields=orphans,
        enrichment_patch=enrich_patch,
        core_keys=CANONICAL_ITEM_KEYS,
    )
    merged_extras["numero_edital"] = merged_extras.get("numero_edital") or numero_edital or ""
    merged_extras["numero_processo"] = merged_extras.get("numero_processo") or numero_processo or ""
    merged_extras["codigo_oportunidade"] = merged_extras.get("codigo_oportunidade") or codigo_op or ""
    existing_docs = merged_extras.get("documentos") if isinstance(merged_extras.get("documentos"), list) else []
    docs_merged = _normalize_documents_payload(
        list(existing_docs) + list(docs),
        str(link or ""),
    )
    merged_extras["documentos"] = docs_merged
    primary_from_docs = _pick_primary_pdf(docs_merged)
    if primary_from_docs and not merged_extras.get("pdf_url"):
        merged_extras["pdf_url"] = primary_from_docs
    merged_extras["cronograma"] = merged_extras.get("cronograma") or cronograma
    merged_extras["url_detalhe"] = merged_extras.get("url_detalhe") or link or ""
    merged_extras["metodo_extracao"] = merged_extras.get("metodo_extracao") or "html_detail_enrichment"

    out = {
        "titulo": titulo,
        "descricao": desc_final,
        "link": link,
        "fonte": work.get("fonte") or source_name.upper(),
        "data_publicacao": data_publicacao,
        "fim_inscricao": fim_inscricao,
        "situacao": work.get("situacao") or extract_situacao(full_text) or "Aberto",
        "valor": item_valor,
        "programa": item_programa,
        "acao": item_acao,
        "tipo_recurso": item_tipo,
        "regiao": work.get("regiao") or extract_regiao(full_text),
        "extras": merged_extras,
    }
    apply_content_type(out, content_type_post)
    thematic_context = " ".join(
        [
            out.get("titulo") or "",
            out.get("descricao") or "",
            out.get("programa") or "",
            out.get("acao") or "",
            str(out.get("extras") or ""),
        ]
    )
    tags = classify_thematic_tags(thematic_context)
    out["extras"]["thematic_tags"] = tags
    out["extras"]["thematic_confidence"] = min(1.0, 0.35 + 0.1 * len(tags)) if tags else 0.0
    out["extras"]["public_investment_scope"] = True
    if _is_asia_source(source_name, out["extras"]) and build_asia_extras is not None:
        # Rota Asia: defaults multilingue + valores ja preenchidos pelo crawler ganham precedencia.
        existing_extras = out["extras"]
        asia_defaults = build_asia_extras(
            titulo_original=existing_extras.get("titulo_original") or out.get("titulo") or "",
            descricao_original=existing_extras.get("descricao_original") or out.get("descricao") or "",
            text_for_classification=thematic_context,
            source_name=out.get("fonte") or source_name,
            origem=out.get("link") or "",
            pais=existing_extras.get("pais", ""),
            instituicao=existing_extras.get("instituicao", ""),
            orgao_responsavel=existing_extras.get("orgao_responsavel", ""),
            orgao_contratante=existing_extras.get("orgao_contratante", out.get("fonte") or source_name),
            empresa_prime=existing_extras.get("empresa_prime", ""),
            idioma_original=existing_extras.get("idioma_original") or None,
            titulo_traduzido=existing_extras.get("titulo_traduzido", ""),
            descricao_traduzida=existing_extras.get("descricao_traduzida", ""),
        )
        merged = {**asia_defaults, **existing_extras}
        # Para listas/strings vazias preenchidas pelo crawler, prefere defaults nao vazios.
        for key in ("subtema", "palavras_chave_detectadas"):
            crawler_val = existing_extras.get(key)
            default_val = asia_defaults.get(key)
            if (not crawler_val) and default_val:
                merged[key] = default_val
        for key in ("setor_estrategico", "tipo_oportunidade", "idioma_original"):
            if not merged.get(key):
                merged[key] = asia_defaults.get(key, "")
        out["extras"] = merged
        # Tradutor opcional: por padrao no-op, controlado via env var.
        if enrich_asia_translation is not None:
            try:
                enrich_asia_translation(out["extras"])
            except Exception:
                logger.exception("Falha ao executar enrich_asia_translation em %s", source_name)
    else:
        # PNCP / SENAI / Softex / plataforma_industria: não aplicar heurísticas de defesa (infer_opportunity_type mistura licitação/fornecedor/notícia).
        if (source_name or "").strip().lower() not in (
            "pncp",
            "senai",
            "softex",
            "plataforma_industria",
            "petrobras",
            "marinha",
            "amazul",
            "dcta_ita_iae",
            "horizon_europe",
            "erc",
            "doe_arpae",
            "sam_gov",
            "apex",
            "faperg",
        ):
            defense_patch = build_defense_extras(
                text=thematic_context,
                source_name=out.get("fonte") or source_name,
                origem=out.get("link") or "",
                pais=out["extras"].get("pais", ""),
                empresa_prime=out["extras"].get("empresa_prime", ""),
                orgao_contratante=out["extras"].get("orgao_contratante", out.get("fonte") or source_name),
            )
            # Não sobrescreve anexos/documentos já extraídos com listas vazias de defaults.
            if out["extras"].get("documentos") and not defense_patch.get("documentos"):
                defense_patch.pop("documentos", None)
            _extras_apply_patch_preserve_nonempty(out["extras"], defense_patch)
    _enrich_grants_gov_catalog_extras(out)
    try:
        from grants_link_resolver import apply_link_resolution_to_item, is_grants_gov_record

        if is_grants_gov_record(out):
            apply_link_resolution_to_item(out, rewrite_link="if_broken")
    except ImportError:
        pass
    try:
        from link_health import stamp_structural_link_health

        stamp_structural_link_health(out, source_key="grants_gov")
    except ImportError:
        pass
    out["extras"]["content_hash"] = content_hash # Salva hash nos extras para auditoria
    
    primary_pdf = str(out["extras"].get("pdf_url") or "") or pdf_url or _pick_primary_pdf(
        out["extras"].get("documentos") if isinstance(out["extras"].get("documentos"), list) else []
    )
    if primary_pdf:
        out["extras"]["pdf_url"] = primary_pdf
        docs_now = out["extras"].get("documentos") if isinstance(out["extras"].get("documentos"), list) else []
        if not any(str(d.get("url") or "") == primary_pdf for d in docs_now if isinstance(d, dict)):
            docs_now.append(
                {
                    "nome": "Documento PDF",
                    "titulo": "Documento PDF",
                    "url": primary_pdf,
                    "tipo": "edital_pdf",
                    "formato": "pdf",
                    "origem": "pdf_url",
                    "status_download": "nao_baixado",
                    "erro_download": "",
                    "texto_extraido": "",
                    "resumo": "",
                }
            )
            out["extras"]["documentos"] = _normalize_documents_payload(docs_now, str(out.get("link") or ""))
    if pdf_text:
        out["extras"]["pdf_lido_para_enriquecimento"] = True
        out["extras"]["pdf_texto_extraido"] = (pdf_text[:4000] if len(pdf_text) > 4000 else pdf_text)
        out["extras"]["pdf_resumo"] = (pdf_text[:700] + "...") if len(pdf_text) > 700 else pdf_text
        if not out.get("publico_alvo"):
            out["publico_alvo"] = extract_target_audience(pdf_text)
        if not out.get("temas"):
            out["temas"] = extract_themes(pdf_text)
        if not out.get("valor_minimo"):
            out["valor_minimo"] = extract_value_min(pdf_text)
        if out.get("situacao") == "Aberto": # Tenta refinar a situação se estiver genérico
            out["situacao"] = extract_situacao(pdf_text) or "Aberto"
        if not out.get("regiao") or out.get("regiao") == "Nacional":
            out["regiao"] = extract_regiao(pdf_text)
        if not out.get("contrapartida"):
            out["contrapartida"] = extract_contrapartida(pdf_text)
        if not out.get("elegibilidade"):
            out["elegibilidade"] = extract_elegibilidade(pdf_text)
        if not out.get("contato"):
            out["contato"] = extract_contato(pdf_text)
        if not out.get("link_inscricao"):
            out["link_inscricao"] = extract_link_inscricao(pdf_text)
        if not out.get("ods"):
            out["ods"] = extract_ods(pdf_text)
        if not out["extras"].get("objetivo"):
            out["extras"]["objetivo"] = (pdf_text[:600] if pdf_text else "")
        if not out["extras"].get("elegibilidade"):
            out["extras"]["elegibilidade"] = extract_elegibilidade(pdf_text) or ""
        
        # 6. Score e recomendacoes (opcional; desligar com EDITALFINDER_SKIP_SCORING)
        if _transformer_skip_scoring():
            out.setdefault("score", 0)
            out.setdefault("score_detalhado", {})
            out.setdefault("justificativa", "")
            out.setdefault("recomendacao", "")
            out.setdefault("compatibilidade", "")
        else:
            profile = {
                "temas": ["inovação", "investimento", "captação", "fomento", "crédito", "tecnologia", "consultoria"],
                "regiao": "Nacional",
                "tipo_entidade": "Consultoria",
            }
            scoring = calculate_relevance_score(out, profile)

            out["score"] = scoring["score_total"]
            out["score_detalhado"] = scoring["score_components"]
            out["justificativa"] = scoring["justification"]
            out["recomendacao"] = ", ".join(scoring["recommendations"]) if scoring["recommendations"] else "Geral"
            out["compatibilidade"] = scoring["compatibilities"]

    enrich_opportunity_classification(out)
    try:
        from br_public_hints import apply_br_public_source_hints
    except ImportError:
        from CORE.br_public_hints import apply_br_public_source_hints

    apply_br_public_source_hints(out, source_name)
    src_l = (source_name or "").strip().lower()
    if src_l == "pncp":
        calibrate_pncp_extras(out)
    elif src_l in ("senai", "plataforma_industria"):
        calibrate_portal_plataforma_inovacao_extras(out, src_l)
    elif src_l == "softex":
        calibrate_softex_extras(out)
    elif src_l == "apex":
        calibrate_apex_extras(out)
    elif src_l == "ambev":
        calibrate_ambev_extras(out)
    elif src_l.endswith("_suppliers") or src_l == "japan_kawasaki_heavy":
        calibrate_corporate_supplier_sources_extras(out, source_name)
    elif src_l == "faperg":
        calibrate_faperg_extras(out)
    elif src_l == "petrobras":
        calibrate_petrobras_extras(out)
    elif src_l == "marinha":
        calibrate_marinha_extras(out)
    elif src_l == "amazul":
        calibrate_amazul_extras(out)
    elif src_l == "dcta_ita_iae":
        calibrate_dcta_ita_iae_extras(out)
    elif src_l == "horizon_europe":
        calibrate_horizon_europe_extras(out)
    elif src_l == "erc":
        calibrate_erc_extras(out)
    elif src_l == "doe_arpae":
        calibrate_doe_arpae_extras(out)
    elif src_l == "nato_diana":
        calibrate_nato_diana_extras(out)
    elif src_l == "iarpa":
        calibrate_iarpa_extras(out)
    elif src_l == "sam_gov":
        calibrate_sam_gov_extras(out)
    elif src_l == "japan_jst":
        calibrate_japan_jst_extras(out)
    elif src_l == "japan_jaea":
        calibrate_japan_jaea_extras(out)
    elif src_l == "japan_jaxa":
        calibrate_japan_jaxa_extras(out)
    elif src_l == "japan_e_rad":
        calibrate_japan_e_rad_extras(out)
    elif src_l == "china_nsfc":
        calibrate_china_nsfc_extras(out)
    elif src_l == "china_cnnc":
        calibrate_china_cnnc_extras(out)
    elif src_l == "china_avic":
        calibrate_china_avic_extras(out)
    elif src_l == "china_norinco":
        calibrate_china_norinco_extras(out)
    elif src_l == "china_university_procurement":
        calibrate_china_university_procurement_extras(out)
    elif src_l == "bnb":
        calibrate_bnb_extras(out)
    elif src_l == "banco_da_amazonia":
        calibrate_banco_da_amazonia_extras(out)
    elif src_l == "badesul":
        calibrate_badesul_extras(out)
    elif src_l == "desenvolve_sp":
        calibrate_desenvolve_sp_extras(out)
    elif src_l == "bdmg":
        calibrate_bdmg_extras(out)
    elif src_l == "agerio":
        calibrate_agerio_extras(out)
    elif src_l == "bndes":
        calibrate_bndes_extras(out)
    elif src_l == "embrapii":
        calibrate_embrapii_extras(out)
    elif src_l == "nuclep":
        calibrate_nuclep_extras(out)
    elif src_l == "bid_lab":
        calibrate_bid_lab_extras(out)
    elif src_l == "caf":
        calibrate_caf_extras(out)
    elif src_l == "fonplata":
        calibrate_fonplata_extras(out)
    elif src_l == "eureka_network":
        calibrate_eureka_network_extras(out)
    elif src_l == "eic":
        calibrate_eic_extras(out)
    elif src_l == "innovate_uk":
        calibrate_innovate_uk_extras(out)
    elif src_l == "ukri_funding":
        calibrate_ukri_funding_extras(out)
    elif src_l == "eurostars":
        calibrate_eurostars_extras(out)
    elif src_l == "dod_sbir_sttr":
        calibrate_dod_sbir_sttr_extras(out)
    elif src_l == "eit":
        calibrate_eit_extras(out)
    elif src_l == "esa_star":
        calibrate_esa_star_extras(out)
    elif src_l == "esa_osip":
        calibrate_esa_osip_extras(out)
    apply_quality_to_payload(out)
    out["extras"]["field_confidence"] = _build_field_confidence(out, pdf_text=pdf_text)
    out["extras"]["extraction_richness"] = round(
        sum(float(v or 0.0) for v in out["extras"]["field_confidence"].values())
        / max(1, len(out["extras"]["field_confidence"])),
        3,
    )
    ct_final = detect_content_type(
        titulo=str(out.get("titulo") or ""),
        descricao=str(out.get("descricao") or ""),
        link=str(out.get("link") or ""),
        full_text=build_full_text(
            out,
            titulo=str(out.get("titulo") or ""),
            descricao=str(out.get("descricao") or ""),
            pdf_text=None,
        ),
    )
    ct_operacional = infer_content_type(
        {**out, "extras": {**(out.get("extras") or {}), "content_type_detectado": ct_final}}
    )
    apply_content_type(out, ct_operacional)
    out["extras"]["content_type_detectado"] = _content_type_final(str(out.get("link") or ""), ct_final)
    if item_valor:
        out["extras"]["valor_total_texto"] = out["extras"].get("valor_total_texto") or str(item_valor)

    try:
        from opportunity_enricher import apply_backend_enrichment_if_enabled

        # Feature flag: EDITALFINDER_ENABLE_BACKEND_ENRICHMENT — ver opportunity_enricher.py
        apply_backend_enrichment_if_enabled(out)
    except ImportError:
        pass

    sanitized = sanitize_for_postgres(out)
    return TransformResult(
        payload=sanitized,
        rejected=False,
        rejection_reason="",
        warnings=warnings,
        report_delta={"qualidade_dado": (sanitized.get("extras") or {}).get("qualidade_dado")},
        original_item=orig,
        content_type_detectado=(sanitized.get("extras") or {}).get("content_type") or ct_final,
    )


def _transform_single_item(item: Any, source_name: str) -> Optional[Dict[str, Any]]:
    """Compatibilidade: retorna só o dict padronizado (ou None)."""
    return _transform_item_with_result(item, source_name).payload


def transform_cnpq(data, source_label: str = "cnpq"):
    return transform_generic(data, source_label)


def transform_finep(data, source_label: str = "finep"):
    batch = transform_generic(data, source_label)
    for item in batch.items:
        if "fonte_recurso" in (item.get("extras") or {}):
            item["tipo_recurso"] = extract_resource_type(
                f"{item.get('titulo', '')} {item.get('descricao', '')} "
                f"{item['extras'].get('fonte_recurso', '')}"
            )
    return batch


def transform_fapergs(data, source_label: str = "fapergs"):
    return transform_generic(data, source_label)


def transform_embrapii(data, source_label: str = "embrapii"):
    return transform_generic(data, source_label)


def transform_bndes(data, source_label: str = "bndes"):
    """Usa sempre o nome da pasta/fonte (ex.: apex, japan_aist) para relatório e *_rejected.json."""
    return transform_generic(data, source_label)

def process_source(source_name, input_file, transform_func) -> int:
    """Processa uma fonte. Retorna 0 = ok ou ignorado; 1 = erro."""
    if not input_file.exists():
        logger.error("Arquivo não encontrado para %s: %s", source_name, input_file)
        print(f"Arquivo não encontrado para {source_name}: {input_file}")
        return 0

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = [data]
        if not isinstance(data, list):
            logger.error(
                "JSON inválido para %s: esperado lista, recebido %s",
                source_name,
                type(data).__name__,
            )
            print(f"Erro: formato JSON inválido em {input_file.name}")
            return 1

        batch_or_list = transform_func(data, source_name)
        if isinstance(batch_or_list, TransformBatchResult):
            deduped_data = list(batch_or_list.items)
            logger.info(
                "Relatório transformer %s: recebidos=%s transformados=%s descartados=%s "
                "incompletos=%s suspeitos=%s qualidade_media=%s",
                source_name,
                (batch_or_list.report or {}).get("recebidos"),
                (batch_or_list.report or {}).get("transformados"),
                (batch_or_list.report or {}).get("descartados"),
                (batch_or_list.report or {}).get("incompletos"),
                (batch_or_list.report or {}).get("suspeitos"),
                (batch_or_list.report or {}).get("qualidade_media"),
            )
        else:
            deduped_data = []
            seen = set()
            for row in batch_or_list or []:
                if not isinstance(row, dict):
                    continue
                dedupe_key = "|".join(
                    [
                        str(row.get("link") or ""),
                        str(row.get("titulo") or ""),
                        str(row.get("fonte") or ""),
                        str(row.get("data_publicacao") or ""),
                        str(row.get("fim_inscricao") or ""),
                    ]
                )
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                deduped_data.append(row)

        output_file = TRANSFORMER_OUTPUT_DIR / f"{source_name}_standardized.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(deduped_data, f, ensure_ascii=False, indent=2)
        
        missing_value = sum(1 for x in deduped_data if not x.get("valor"))
        missing_type = sum(1 for x in deduped_data if x.get("tipo_recurso") in (None, "Não Especificado"))
        missing_pdf = sum(1 for x in deduped_data if not (x.get("extras") or {}).get("pdf_url"))
        logger.info(
            "Fonte %s: total=%s, sem_valor=%s, sem_tipo_recurso=%s, sem_pdf_url=%s",
            source_name,
            len(deduped_data),
            missing_value,
            missing_type,
            missing_pdf,
        )
        print(f"Processado {source_name}: {len(deduped_data)} editais.")
        return 0
    except Exception as e:
        logger.exception("Erro ao processar %s", source_name)
        print(f"Erro ao processar {source_name}: {e}")
        return 1


def _parse_transform_sources_arg(raw: Optional[str]) -> Optional[Set[str]]:
    if not raw or not str(raw).strip():
        return None
    parts = {p.strip().lower() for p in str(raw).split(",") if p.strip()}
    return parts or None


def _filter_transform_sources(
    sources_list: List[Tuple[str, Path, Callable[..., Any]]],
    allowed: Optional[Set[str]],
) -> List[Tuple[str, Path, Callable[..., Any]]]:
    if not allowed:
        return sources_list
    known = {t[0].lower() for t in sources_list}
    unknown = allowed - known
    if unknown:
        logger.warning(
            "Fontes desconhecidas em --sources / EDITALFINDER_TRANSFORM_SOURCES: %s",
            ", ".join(sorted(unknown)),
        )
    return [t for t in sources_list if t[0].lower() in allowed]


def _run_sources_with_workers(
    sources_list: List[Tuple[str, Path, Callable[..., Any]]], workers: int
) -> int:
    """Executa process_source em paralelo (I/O). Retorna número de falhas."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    n = len(sources_list)
    if n == 0:
        return 0
    w = max(1, min(workers, n, 20))
    if w <= 1:
        failures = 0
        for spec in sources_list:
            failures += process_source(spec[0], spec[1], spec[2])
        return failures

    failures = 0
    logger.info("Transformer paralelo: workers=%s fontes=%s", w, n)
    print(f"[transformer] Paralelo: {w} workers, {n} fontes.")
    with ThreadPoolExecutor(max_workers=w) as ex:
        futures = {
            ex.submit(process_source, sn, inf, fn): sn for sn, inf, fn in sources_list
        }
        for fut in as_completed(futures):
            sn = futures[fut]
            try:
                failures += int(fut.result() or 0)
            except Exception as exc:
                logger.exception("Falha inesperada na fonte %s", sn)
                print(f"Erro inesperado na fonte {sn}: {exc}")
                failures += 1
    return failures


def _parse_transformer_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Padroniza JSONs brutos dos crawlers para *_standardized.json."
    )
    p.add_argument(
        "--sources",
        type=str,
        default=os.getenv("EDITALFINDER_TRANSFORM_SOURCES", "") or "",
        help="Fontes (nomes de pasta), separadas por virgula. Ex.: cnpq,finep,pncp_defesa",
    )
    p.add_argument(
        "--workers",
        type=int,
        default=int(os.getenv("EDITALFINDER_TRANSFORM_WORKERS", "8") or "8"),
        help="Fontes JSON em paralelo (default: 8 ou EDITALFINDER_TRANSFORM_WORKERS). Max 20 no executor.",
    )
    p.add_argument(
        "--item-workers",
        type=int,
        default=int(os.getenv("EDITALFINDER_TRANSFORM_ITEM_WORKERS", "6") or "6"),
        help="Itens por ficheiro em paralelo no transform_generic (PDF/rede; default 6). Use 1 para sequencial.",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_transformer_cli()
    workers = max(1, min(int(args.workers or 1), 32))
    item_w = max(1, min(int(args.item_workers or 1), 16))
    os.environ["EDITALFINDER_TRANSFORM_ITEM_WORKERS"] = str(item_w)
    allowed = _parse_transform_sources_arg(args.sources)

    if PdfReader is None:
        logger.warning("Dependência 'pypdf' não encontrada. Fallback de leitura de PDF desativado.")
    sources = [
        ("cnpq", BASE_DIR / "cnpq" / "outputs" / "cnpq_editais.json", transform_cnpq),
        ("finep", BASE_DIR / "finep" / "outputs" / "finep_editais.json", transform_finep),
        ("fapergs", BASE_DIR / "fapergs" / "outputs" / "fapergs_editais.json", transform_fapergs),
        ("embrapii", BASE_DIR / "embrapii" / "outputs" / "embrapii_editais.json", transform_embrapii),
        ("bndes", BASE_DIR / "bndes" / "outputs" / "bndes_editais.json", transform_bndes),
        ("abdi", BASE_DIR / "abdi" / "outputs" / "abdi_editais.json", transform_bndes),
        ("mcti", BASE_DIR / "mcti" / "outputs" / "mcti_editais.json", transform_bndes),
        ("saude", BASE_DIR / "saude" / "outputs" / "saude_editais.json", transform_bndes),
        ("mapa", BASE_DIR / "mapa" / "outputs" / "mapa_editais.json", transform_bndes),
        ("defesa", BASE_DIR / "defesa" / "outputs" / "defesa_editais.json", transform_bndes),
        ("mma", BASE_DIR / "mma" / "outputs" / "mma_editais.json", transform_bndes),
        ("softex", BASE_DIR / "softex" / "outputs" / "softex_editais.json", transform_bndes),
        ("apex", BASE_DIR / "apex" / "outputs" / "apex_editais.json", transform_bndes),
        ("anp", BASE_DIR / "anp" / "outputs" / "anp_editais.json", transform_bndes),
        ("petrobras", BASE_DIR / "petrobras" / "outputs" / "petrobras_editais.json", transform_bndes),
        ("ambev", BASE_DIR / "ambev" / "outputs" / "ambev_editais.json", transform_bndes),
        ("fapesc", BASE_DIR / "fapesc" / "outputs" / "fapesc_editais.json", transform_bndes),
        ("fappr", BASE_DIR / "fappr" / "outputs" / "fappr_editais.json", transform_bndes),
        ("aneel", BASE_DIR / "aneel" / "outputs" / "aneel_editais.json", transform_bndes),
        ("capes", BASE_DIR / "capes" / "outputs" / "capes_editais.json", transform_bndes),
        ("fapesp", BASE_DIR / "fapesp" / "outputs" / "fapesp_editais.json", transform_bndes),
        ("faperg", BASE_DIR / "faperg" / "outputs" / "faperg_editais.json", transform_bndes),
        ("senai", BASE_DIR / "senai" / "outputs" / "senai_editais.json", transform_bndes),
        ("horizon_europe", BASE_DIR / "horizon_europe" / "outputs" / "horizon_europe_editais.json", transform_bndes),
        ("nsf", BASE_DIR / "nsf" / "outputs" / "nsf_editais.json", transform_bndes),
        ("doe_arpae", BASE_DIR / "doe_arpae" / "outputs" / "doe_arpae_editais.json", transform_bndes),
        ("erc", BASE_DIR / "erc" / "outputs" / "erc_editais.json", transform_bndes),
        ("wellcome", BASE_DIR / "wellcome" / "outputs" / "wellcome_editais.json", transform_bndes),
        ("cnen", BASE_DIR / "cnen" / "outputs" / "cnen_editais.json", transform_bndes),
        ("ipen", BASE_DIR / "ipen" / "outputs" / "ipen_editais.json", transform_bndes),
        ("eletronuclear", BASE_DIR / "eletronuclear" / "outputs" / "eletronuclear_editais.json", transform_bndes),
        ("impa", BASE_DIR / "impa" / "outputs" / "impa_editais.json", transform_bndes),
        ("cbpf", BASE_DIR / "cbpf" / "outputs" / "cbpf_editais.json", transform_bndes),
        ("science_scraper", BASE_DIR / "science_scraper" / "outputs" / "science_editais.json", transform_bndes),
        ("fnde", BASE_DIR / "fnde" / "outputs" / "fnde_editais.json", transform_bndes),
        ("caixa", BASE_DIR / "caixa" / "outputs" / "caixa_editais.json", transform_bndes),
        ("badesul", BASE_DIR / "badesul" / "outputs" / "badesul_editais.json", transform_bndes),
        ("brde", BASE_DIR / "brde" / "outputs" / "brde_editais.json", transform_bndes),
        ("plataforma_industria", BASE_DIR / "plataforma_industria" / "outputs" / "plataforma_editais.json", transform_bndes),
        ("confap", BASE_DIR / "confap" / "outputs" / "confap_editais.json", transform_bndes),
        ("pncp", BASE_DIR / "pncp" / "outputs" / "pncp_editais.json", transform_bndes),
        ("marinha", BASE_DIR / "marinha" / "outputs" / "marinha_editais.json", transform_bndes),
        ("dcta_ita_iae", BASE_DIR / "dcta_ita_iae" / "outputs" / "dcta_ita_iae_editais.json", transform_bndes),
        ("inb", BASE_DIR / "inb" / "outputs" / "inb_editais.json", transform_bndes),
        ("nuclep", BASE_DIR / "nuclep" / "outputs" / "nuclep_editais.json", transform_bndes),
        ("amazul", BASE_DIR / "amazul" / "outputs" / "amazul_editais.json", transform_bndes),
        ("fapemig", BASE_DIR / "fapemig" / "outputs" / "fapemig_editais.json", transform_bndes),
        ("sam_gov", BASE_DIR / "sam_gov" / "outputs" / "sam_gov_editais.json", transform_bndes),
        ("dod_sbir_sttr", BASE_DIR / "dod_sbir_sttr" / "outputs" / "dod_sbir_sttr_editais.json", transform_bndes),
        ("grants_gov", BASE_DIR / "grants_gov" / "outputs" / "grants_gov_editais.json", transform_bndes),
        ("darpa_opportunities", BASE_DIR / "darpa_opportunities" / "outputs" / "darpa_opportunities_editais.json", transform_bndes),
        ("european_defence_fund", BASE_DIR / "european_defence_fund" / "outputs" / "european_defence_fund_editais.json", transform_bndes),
        ("nato_diana", BASE_DIR / "nato_diana" / "outputs" / "nato_diana_editais.json", transform_bndes),
        ("diu", BASE_DIR / "diu" / "outputs" / "diu_editais.json", transform_bndes),
        ("afwerx", BASE_DIR / "afwerx" / "outputs" / "afwerx_editais.json", transform_bndes),
        ("iarpa", BASE_DIR / "iarpa" / "outputs" / "iarpa_editais.json", transform_bndes),
        ("pncp_defesa", BASE_DIR / "pncp_defesa" / "outputs" / "pncp_defesa_editais.json", transform_bndes),
        ("compras_defesa", BASE_DIR / "compras_defesa" / "outputs" / "compras_defesa_editais.json", transform_bndes),
        ("lockheed_martin_suppliers", BASE_DIR / "lockheed_martin_suppliers" / "outputs" / "lockheed_martin_suppliers_editais.json", transform_bndes),
        ("bae_systems_suppliers", BASE_DIR / "bae_systems_suppliers" / "outputs" / "bae_systems_suppliers_editais.json", transform_bndes),
        ("general_dynamics_suppliers", BASE_DIR / "general_dynamics_suppliers" / "outputs" / "general_dynamics_suppliers_editais.json", transform_bndes),
        ("rheinmetall_suppliers", BASE_DIR / "rheinmetall_suppliers" / "outputs" / "rheinmetall_suppliers_editais.json", transform_bndes),
        ("thales_suppliers", BASE_DIR / "thales_suppliers" / "outputs" / "thales_suppliers_editais.json", transform_bndes),
        # ------------------------------------------------------------------
        # Expansao Asia
        # ------------------------------------------------------------------
        ("japan_jst", BASE_DIR / "japan_jst" / "outputs" / "japan_jst_editais.json", transform_bndes),
        ("japan_jsps", BASE_DIR / "japan_jsps" / "outputs" / "japan_jsps_editais.json", transform_bndes),
        ("japan_kakenhi", BASE_DIR / "japan_kakenhi" / "outputs" / "japan_kakenhi_editais.json", transform_bndes),
        ("japan_e_rad", BASE_DIR / "japan_e_rad" / "outputs" / "japan_e_rad_editais.json", transform_bndes),
        ("japan_mext", BASE_DIR / "japan_mext" / "outputs" / "japan_mext_editais.json", transform_bndes),
        ("japan_qst", BASE_DIR / "japan_qst" / "outputs" / "japan_qst_editais.json", transform_bndes),
        ("japan_jaea", BASE_DIR / "japan_jaea" / "outputs" / "japan_jaea_editais.json", transform_bndes),
        ("japan_nims", BASE_DIR / "japan_nims" / "outputs" / "japan_nims_editais.json", transform_bndes),
        ("japan_riken", BASE_DIR / "japan_riken" / "outputs" / "japan_riken_editais.json", transform_bndes),
        ("japan_kek", BASE_DIR / "japan_kek" / "outputs" / "japan_kek_editais.json", transform_bndes),
        ("japan_jetro_procurement", BASE_DIR / "japan_jetro_procurement" / "outputs" / "japan_jetro_procurement_editais.json", transform_bndes),
        ("japan_atla", BASE_DIR / "japan_atla" / "outputs" / "japan_atla_editais.json", transform_bndes),
        ("japan_mod", BASE_DIR / "japan_mod" / "outputs" / "japan_mod_editais.json", transform_bndes),
        ("japan_jaxa", BASE_DIR / "japan_jaxa" / "outputs" / "japan_jaxa_editais.json", transform_bndes),
        ("japan_nedo", BASE_DIR / "japan_nedo" / "outputs" / "japan_nedo_editais.json", transform_bndes),
        ("japan_aist", BASE_DIR / "japan_aist" / "outputs" / "japan_aist_editais.json", transform_bndes),
        ("china_nsfc", BASE_DIR / "china_nsfc" / "outputs" / "china_nsfc_editais.json", transform_bndes),
        ("china_most", BASE_DIR / "china_most" / "outputs" / "china_most_editais.json", transform_bndes),
        ("china_cas", BASE_DIR / "china_cas" / "outputs" / "china_cas_editais.json", transform_bndes),
        ("china_caea", BASE_DIR / "china_caea" / "outputs" / "china_caea_editais.json", transform_bndes),
        ("china_cnnc", BASE_DIR / "china_cnnc" / "outputs" / "china_cnnc_editais.json", transform_bndes),
        ("china_cgn", BASE_DIR / "china_cgn" / "outputs" / "china_cgn_editais.json", transform_bndes),
        ("china_mofcom_tendering", BASE_DIR / "china_mofcom_tendering" / "outputs" / "china_mofcom_tendering_editais.json", transform_bndes),
        ("china_tendering_bidding", BASE_DIR / "china_tendering_bidding" / "outputs" / "china_tendering_bidding_editais.json", transform_bndes),
        ("china_university_procurement", BASE_DIR / "china_university_procurement" / "outputs" / "china_university_procurement_editais.json", transform_bndes),
        ("china_mod_public", BASE_DIR / "china_mod_public" / "outputs" / "china_mod_public_editais.json", transform_bndes),
        # Fase 2 Asia - suppliers privados publicos
        ("japan_mitsubishi_heavy", BASE_DIR / "japan_mitsubishi_heavy" / "outputs" / "japan_mitsubishi_heavy_editais.json", transform_bndes),
        ("japan_kawasaki_heavy", BASE_DIR / "japan_kawasaki_heavy" / "outputs" / "japan_kawasaki_heavy_editais.json", transform_bndes),
        ("japan_ihi", BASE_DIR / "japan_ihi" / "outputs" / "japan_ihi_editais.json", transform_bndes),
        ("china_norinco", BASE_DIR / "china_norinco" / "outputs" / "china_norinco_editais.json", transform_bndes),
        ("china_avic", BASE_DIR / "china_avic" / "outputs" / "china_avic_editais.json", transform_bndes),
    ]

    sources = _filter_transform_sources(sources, allowed)
    if allowed:
        print(
            f"[transformer] Filtro ativo: {len(sources)} fonte(s) de {len(allowed)} pedida(s)."
        )

    failures = _run_sources_with_workers(sources, workers)
    if failures:
        print(f"[transformer] Concluido com {failures} fonte(s) com erro.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
