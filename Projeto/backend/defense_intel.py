from __future__ import annotations

import re
from typing import Dict, List, Set

KEYWORDS_DEFESA: List[str] = [
    "defesa nacional",
    "base industrial de defesa",
    "industria de defesa",
    "defesa industrial",
    "seguranca publica",
    "seguranca nacional",
    "soberania",
    "tecnologias estrategicas",
    "dual-use",
    "dual use",
    "military",
    "defense",
    "defence",
    "aerospace",
    "naval",
    "army",
    "navy",
    "air force",
    "armed forces",
    "military vehicle",
    "armored vehicle",
    "land systems",
    "combat vehicle",
    "radar",
    "sensor",
    "missile defense",
    "air defense",
    "electronic warfare",
    "communication systems",
    "command and control",
    "c4isr",
    "autonomous systems",
    "unmanned systems",
    "uav",
    "uas",
    "drone",
    "cyber defense",
    "space defense",
    "critical infrastructure",
    "materiais avancados",
    "materiais de defesa",
    "blindagem",
    "veiculos militares",
    "sistemas navais",
    "aeronautica",
    "aeroespacial",
    "propulsao",
    "sistemas embarcados",
    "sensores",
    "radares",
    "comunicacoes militares",
    "defesa cibernetica",
    "energia",
    "nuclear",
    "energia nuclear",
    "nuclear defense",
    "fisica nuclear",
    "quimica nuclear",
    "engenharia nuclear",
    "radioprotecao",
    "radiofarmacos",
    "uranio",
    "combustivel nuclear",
    "reatores",
    "fusao nuclear",
    "fissao nuclear",
    "p&d",
    "pd&i",
    "pesquisa e desenvolvimento",
    "inovacao",
    "edital",
    "licitacao",
    "chamada publica",
    "pregao",
    "contrato publico",
    "financiamento",
    "subvencao",
    "grant",
    "funding",
    "procurement",
    "supplier",
    "supplier portal",
    "vendor",
    "small business",
    "sbir",
    "sttr",
]

SUBTHEME_PATTERNS: Dict[str, List[str]] = {
    "aeroespacial_militar": ["aeroespacial", "aerospace", "air force", "forca aerea"],
    "veiculos_militares": ["military vehicle", "veiculo militar", "armored vehicle", "blindado"],
    "naval_militar": ["naval", "navy", "marinha", "submarino", "sistemas navais"],
    "eletronica_defesa": ["electronic warfare", "eletronica de defesa", "avionics"],
    "sensores_radares": ["sensor", "sensores", "radar", "radares"],
    "comunicacoes_militares": ["communication systems", "comunicacoes militares", "c4isr"],
    "cyber_defesa": ["cyber defense", "defesa cibernetica", "ciberseguranca"],
    "materiais_defesa": ["materiais de defesa", "blindagem", "materiais avancados"],
    "energia_defesa": ["energia", "propulsao", "energia de defesa"],
    "nuclear_defesa": ["nuclear", "uranio", "reator", "radiofarmacos", "radioprotecao"],
    "dual_use": ["dual-use", "dual use", "duplo uso"],
    "fornecedores_defesa": ["supplier", "vendor", "fornecedor", "supplier portal"],
    "licitacoes_defesa": ["licitacao", "pregao", "procurement", "contrato publico", "tender"],
    "pdi_defesa": ["p&d", "pd&i", "research and development", "sbir", "sttr"],
    "seguranca_publica": ["seguranca publica", "policia", "law enforcement"],
    "sistemas_autonomos": ["autonomous systems", "unmanned systems", "uav", "uas", "drone"],
    "espaco_defesa": ["space defense", "espacial", "satellite", "launch"],
    "infraestrutura_critica": ["critical infrastructure", "infraestrutura critica"],
}

SENSITIVE_CONTEXT_MARKERS = [
    "fabricacao de armamentos",
    "como fabricar",
    "manual de armas",
    "explosivos",
    "municoes",
    "agente quimico",
]


def normalize_text(text: str) -> str:
    t = (text or "").lower()
    table = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
    t = t.translate(table)
    return re.sub(r"\s+", " ", t).strip()


def detect_keywords(text: str) -> List[str]:
    t = normalize_text(text)
    return sorted({k for k in KEYWORDS_DEFESA if k in t})


def classify_subthemes(text: str) -> List[str]:
    t = normalize_text(text)
    found: Set[str] = set()
    for subtheme, patterns in SUBTHEME_PATTERNS.items():
        if any(p in t for p in patterns):
            found.add(subtheme)
    return sorted(found)


def detect_sensitive_context(text: str) -> List[str]:
    t = normalize_text(text)
    return sorted({marker for marker in SENSITIVE_CONTEXT_MARKERS if marker in t})


def infer_opportunity_type(text: str, source_name: str = "") -> str:
    t = normalize_text(f"{source_name} {text}")
    if "supplier" in t or "fornecedor" in t or "vendor" in t:
        return "supplier_portal"
    if "licitacao" in t or "pregao" in t or "tender" in t or "procurement" in t:
        return "licitacao"
    if "chamada publica" in t or "call for proposals" in t:
        return "chamada_publica"
    if "sbir" in t or "sttr" in t or "research" in t or "p&d" in t or "pd&i" in t:
        return "programa_pdi"
    if "grant" in t or "funding opportunity" in t:
        return "grant"
    if "investment" in t or "investimento" in t:
        return "investimento"
    if "registro" in t and "fornecedor" in t:
        return "registro_fornecedor"
    return "noticia_institucional"


def build_defense_extras(
    text: str,
    source_name: str,
    origem: str,
    pais: str = "",
    empresa_prime: str = "",
    orgao_contratante: str = "",
) -> Dict[str, object]:
    keywords = detect_keywords(text)
    subtemas = classify_subthemes(text)
    sensitive_markers = detect_sensitive_context(text)
    area_cientifica = [
        s for s in subtemas
        if s in ("nuclear_defesa", "materiais_defesa", "sensores_radares", "espaco_defesa", "energia_defesa")
    ]
    area_tecnologica = [s for s in subtemas if s not in area_cientifica]
    return {
        "regiao": "",
        "setor_estrategico": "defesa_industrial",
        "subtema": subtemas,
        "area_cientifica": area_cientifica,
        "area_tecnologica": area_tecnologica,
        "tipo_oportunidade": infer_opportunity_type(text, source_name),
        "empresa_prime": empresa_prime,
        "orgao_contratante": orgao_contratante,
        "pais": pais,
        "idioma_original": "",
        "titulo_original": "",
        "descricao_original": "",
        "titulo_traduzido": "",
        "descricao_traduzida": "",
        "orgao_responsavel": "",
        "instituicao": "",
        "numero_edital": "",
        "numero_chamada": "",
        "numero_processo": "",
        "codigo_oportunidade": "",
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
        "metodo_extracao": "",
        "url_listagem": "",
        "url_detalhe": "",
        "nivel_sensibilidade": "publico_institucional",
        "contexto_sensivel_detectado": bool(sensitive_markers),
        "marcadores_contexto_sensivel": sensitive_markers,
        "origem": origem,
        "palavras_chave_detectadas": keywords,
        "necessita_traducao": False,
        "observacoes": "",
    }
