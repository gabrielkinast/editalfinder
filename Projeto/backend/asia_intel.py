"""asia_intel.py

Camada de classificacao tematica multilingue (PT/EN/JA/ZH) para fontes
japonesas e chinesas do EditalFinder. Espelha defense_intel.py mas e
voltada a oportunidades publicas e institucionais de C&T, P&D, materiais,
nuclear (uso pacifico), aceleradores, semicondutores, tecnologias quanticas,
aeroespacial, dual-use e procurement publico.

Saida principal: build_asia_extras(...) -> dict compativel com o esquema
"extras" definido para a expansao Asia.

NAO contem nem coleta instrucoes tecnicas sensiveis. Termos relacionados a
fabricacao de armamentos, municao, agentes quimicos/radiologicos sao
marcados em metadados para auditoria, sem censurar ou descartar oportunidades.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Listas de palavras-chave por idioma (curadas a partir do briefing do projeto)
# ---------------------------------------------------------------------------

KEYWORDS_PT: List[str] = [
    "fisica", "matematica", "quimica",
    "fisica nuclear", "quimica nuclear", "engenharia nuclear",
    "energia nuclear", "ciencia dos materiais", "materiais avancados",
    "aceleradores", "radiacao", "radioprotecao",
    "fusao nuclear", "fissao nuclear", "semicondutores",
    "tecnologias quanticas", "aeroespacial", "defesa", "defesa industrial",
    "tecnologias estrategicas", "dual-use", "dual use", "duplo uso",
    "procurement", "licitacao", "edital", "chamada publica",
    "financiamento", "bolsa", "grant", "p&d", "pd&i", "inovacao",
]

KEYWORDS_EN: List[str] = [
    "physics", "mathematics", "chemistry",
    "nuclear physics", "nuclear chemistry", "nuclear engineering",
    "nuclear energy", "materials science", "advanced materials",
    "accelerators", "accelerator", "radiation", "radiological protection",
    "nuclear fusion", "nuclear fission",
    "semiconductors", "semiconductor",
    "quantum technology", "quantum computing", "quantum sensors",
    "quantum information",
    "aerospace", "defense", "defence", "industrial defense", "industrial defence",
    "dual-use", "dual use",
    "procurement", "tender", "contract", "grant", "funding",
    "research and development", "r&d", "innovation",
    "call for proposals", "funding opportunity", "supplier",
]

# Japones - hiragana, katakana e kanji aceitos como esta.
KEYWORDS_JA: List[str] = [
    "物理", "数学", "化学",
    "原子力", "核物理", "核化学", "原子力工学", "原子力エネルギー",
    "放射線", "放射線防護", "加速器", "核融合", "核分裂",
    "材料科学", "先端材料", "半導体",
    "量子技術", "量子情報", "量子コンピュータ", "量子センサー",
    "航空宇宙", "宇宙",
    "防衛", "安全保障", "デュアルユース",
    "調達", "入札", "公募", "公示",
    "研究開発", "共同研究", "助成", "補助金", "委託研究",
]

# Chines simplificado.
KEYWORDS_ZH: List[str] = [
    "物理", "数学", "化学",
    "核物理", "核化学", "核工程", "核能",
    "辐射", "辐射防护", "加速器",
    "核聚变", "核裂变",
    "材料科学", "先进材料",
    "半导体",
    "量子技术", "量子计算", "量子信息", "量子传感",
    "航空航天", "空天",
    "国防", "安全", "军民两用",
    "采购", "招标", "投标", "中标", "公告",
    "资助", "基金", "科研", "研究开发", "创新", "课题", "项目申报",
]

ALL_KEYWORDS: List[str] = KEYWORDS_PT + KEYWORDS_EN + KEYWORDS_JA + KEYWORDS_ZH


# ---------------------------------------------------------------------------
# Setores estrategicos -> regras de mapeamento
# ---------------------------------------------------------------------------

STRATEGIC_SECTORS: List[str] = [
    "ciencia_tecnologia",
    "pesquisa_basica",
    "pesquisa_aplicada",
    "defesa_industrial",
    "nuclear",
    "materiais_avancados",
    "aeroespacial",
    "semicondutores",
    "tecnologias_quanticas",
    "energia",
    "dual_use",
    "procurement_publico",
]

# Regras heuristicas: a primeira regra cujo padrao bater define o setor.
# A ordem importa: setores mais "estreitos" vem antes dos mais "amplos".
SECTOR_RULES: List[Tuple[str, List[str]]] = [
    ("nuclear", [
        "原子力", "核物理", "核化学", "原子力工学", "原子力エネルギー",
        "核融合", "核分裂", "核能", "核物理", "核化学", "核工程",
        "核聚变", "核裂变", "辐射", "辐射防护", "放射線", "放射線防護",
        "加速器",
        "nuclear", "radiological", "radiation",
        "nuclear physics", "nuclear chemistry", "nuclear engineering",
        "nuclear energy", "nuclear fusion", "nuclear fission",
        "accelerator", "accelerators",
    ]),
    ("semicondutores", [
        "半導体", "半导体", "semiconductor", "semiconductors",
    ]),
    ("tecnologias_quanticas", [
        "量子技術", "量子情報", "量子コンピュータ", "量子センサー",
        "量子技术", "量子计算", "量子信息", "量子传感",
        "quantum technology", "quantum computing", "quantum information",
        "quantum sensors", "quantum sensing",
    ]),
    ("aeroespacial", [
        "航空宇宙", "航空航天", "宇宙", "空天",
        "aerospace", "space agency", "satellite", "satelite",
        "launch vehicle", "rocket",
    ]),
    ("materiais_avancados", [
        "材料科学", "先端材料", "材料科学", "先进材料",
        "advanced materials", "materials science",
    ]),
    ("defesa_industrial", [
        "防衛", "安全保障",
        "国防", "军民两用", "军工",
        "defense", "defence", "military",
    ]),
    ("dual_use", [
        "デュアルユース", "军民两用",
        "dual-use", "dual use",
    ]),
    ("procurement_publico", [
        "調達", "入札", "公示",
        "采购", "招标", "投标", "中标",
        "procurement", "tender", "tendering", "bidding", "rfp", "rfq",
    ]),
    ("energia", [
        "energy", "エネルギー", "能源",
    ]),
    ("ciencia_tecnologia", [
        "公募", "公告",
        "助成", "補助金", "委託研究", "研究開発", "共同研究",
        "基金", "资助", "科研", "研究开发", "创新", "课题", "项目申报",
        "grant", "funding", "research and development", "r&d",
        "call for proposals", "funding opportunity",
    ]),
]


# ---------------------------------------------------------------------------
# Subtemas
# ---------------------------------------------------------------------------

SUBTHEME_PATTERNS: Dict[str, List[str]] = {
    "fisica": ["fisica", "physics", "物理"],
    "matematica": ["matematica", "mathematics", "数学"],
    "quimica": ["quimica", "chemistry", "化学"],
    "fisica_nuclear": ["fisica nuclear", "nuclear physics", "核物理"],
    "quimica_nuclear": ["quimica nuclear", "nuclear chemistry", "核化学"],
    "engenharia_nuclear": [
        "engenharia nuclear", "nuclear engineering",
        "原子力工学", "核工程",
    ],
    "energia_nuclear": [
        "energia nuclear", "nuclear energy",
        "原子力エネルギー", "核能",
    ],
    "radiacao": ["radiacao", "radiation", "放射線", "辐射"],
    "radioprotecao": [
        "radioprotecao", "radiological protection",
        "放射線防護", "辐射防护",
    ],
    "aceleradores": ["acelerador", "accelerator", "加速器"],
    "fusao_nuclear": ["fusao nuclear", "nuclear fusion", "核融合", "核聚变"],
    "fissao_nuclear": ["fissao nuclear", "nuclear fission", "核分裂", "核裂变"],
    "materiais_nucleares": [
        "materiais nucleares", "nuclear materials", "核材料",
    ],
    "ciencia_dos_materiais": [
        "ciencia dos materiais", "materials science",
        "材料科学",
    ],
    "materiais_avancados": [
        "materiais avancados", "advanced materials",
        "先端材料", "先进材料",
    ],
    "ligas_metalicas": ["ligas metalicas", "metallic alloy", "alloy", "合金"],
    "ceramicas": ["ceramica", "ceramics", "セラミックス", "陶瓷"],
    "polimeros": ["polimero", "polymer", "ポリマー", "聚合物"],
    "semicondutores": ["semicondutores", "semiconductor", "半導体", "半导体"],
    "baterias": ["bateria", "battery", "電池", "电池"],
    "energia": ["energia", "energy", "エネルギー", "能源"],
    "tecnologias_quanticas": [
        "tecnologias quanticas", "quantum technology",
        "量子技術", "量子技术",
    ],
    "computacao_quantica": [
        "computacao quantica", "quantum computing",
        "量子コンピュータ", "量子计算",
    ],
    "sensores_quanticos": [
        "sensores quanticos", "quantum sensors", "quantum sensing",
        "量子センサー", "量子传感",
    ],
    "aeroespacial": [
        "aeroespacial", "aerospace",
        "航空宇宙", "航空航天", "宇宙", "空天",
    ],
    "defesa_industrial": [
        "defesa industrial", "industrial defense", "industrial defence",
        "防衛産業", "国防工业", "军工",
    ],
    "dual_use": [
        "dual-use", "dual use", "duplo uso",
        "デュアルユース", "军民两用",
    ],
    "sensores": ["sensor", "sensores", "センサー", "传感器"],
    "radares": ["radar", "radares", "レーダー", "雷达"],
    "eletronica_defesa": [
        "eletronica de defesa", "defense electronics",
        "防衛エレクトロニクス", "国防电子",
    ],
    "sistemas_autonomos": [
        "sistemas autonomos", "autonomous systems", "unmanned",
        "uav", "drone", "ドローン", "无人机",
    ],
    "veiculos_militares": [
        "veiculos militares", "military vehicle", "armored vehicle",
        "軍用車両", "军用车辆",
    ],
    "naval_militar": [
        "naval", "navy", "海軍", "海军", "submarino", "submarine",
    ],
    "espaco": ["espaco", "space", "宇宙", "空间"],
    "infraestrutura_critica": [
        "infraestrutura critica", "critical infrastructure",
        "重要インフラ", "关键基础设施",
    ],
    "procurement": [
        "procurement", "licitacao", "tender", "tendering",
        "調達", "入札", "采购", "招标", "投标",
    ],
    "pdi": [
        "p&d", "pd&i", "research and development", "r&d",
        "研究開発", "研究开发",
    ],
}


# ---------------------------------------------------------------------------
# Tipos de oportunidade
# ---------------------------------------------------------------------------

OPPORTUNITY_TYPES: List[str] = [
    "funding_opportunity", "grant", "chamada_publica", "edital", "bolsa",
    "pesquisa_colaborativa", "programa_pdi", "procurement", "licitacao",
    "contrato_publico", "supplier_portal", "registro_fornecedor",
    "noticia_institucional", "investimento", "roadmap",
]

OPPORTUNITY_RULES: List[Tuple[str, List[str]]] = [
    ("supplier_portal", ["supplier", "vendor", "fornecedor", "サプライヤー", "供应商"]),
    ("registro_fornecedor", ["vendor registration", "registro de fornecedor",
                              "業者登録", "供应商注册"]),
    ("licitacao", ["licitacao", "tender", "tendering", "招标", "投标", "入札"]),
    ("procurement", ["procurement", "調達", "采购", "rfp", "rfq"]),
    ("contrato_publico", ["contract notice", "公共合同", "契約公告"]),
    ("bolsa", ["bolsa", "fellowship", "scholarship", "奨学金", "奖学金"]),
    ("grant", ["grant", "助成", "資助", "资助", "補助金", "基金"]),
    ("funding_opportunity", ["funding opportunity", "公募", "call for proposals",
                              "募集", "招募"]),
    ("chamada_publica", ["chamada publica", "公開募集", "公开招募"]),
    ("edital", ["edital"]),
    ("pesquisa_colaborativa", ["共同研究", "joint research", "collaborative research",
                                "合作研究"]),
    ("programa_pdi", ["pd&i", "p&d", "研究開発", "研究开发", "r&d program"]),
    ("investimento", ["investment", "investimento", "投資", "投资"]),
]


# ---------------------------------------------------------------------------
# Marcadores de contexto sensivel
# ---------------------------------------------------------------------------

# Lista de termos sensiveis em PT/EN/JA/ZH usada apenas para sinalizar
# contexto nos extras. Nao bloqueia subtemas, tipo de oportunidade, carga
# ou persistencia no banco.
SENSITIVE_CONTEXT_MARKERS: List[str] = [
    # PT
    "fabricacao de armamentos", "como fabricar arma", "manual de arma",
    "instrucoes de fabricacao",
    "municoes", "municao", "explosivos",
    "agente quimico", "agente radiologico",
    # EN
    "weapon manufacturing", "how to build a weapon", "weapons manual",
    "weapons fabrication", "munitions manufacturing",
    "explosive precursor", "chemical agent", "radiological agent",
    "weaponization",
    # JA
    "兵器製造", "武器の製造", "弾薬製造",
    "化学剤製造", "放射性物質兵器",
    # ZH
    "武器制造", "弹药制造",
    "化学战剂", "放射性战剂", "武器化",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_HIRAGANA_RE = re.compile(r"[\u3040-\u309F]")
_KATAKANA_RE = re.compile(r"[\u30A0-\u30FF]")
_CJK_HAN_RE = re.compile(r"[\u4E00-\u9FFF]")


def _normalize_latin(text: str) -> str:
    """Normaliza apenas a porcao latina do texto (lower + remove acentos)."""
    if not text:
        return ""
    t = text.lower()
    table = str.maketrans("áàâãéêíóôõúç", "aaaaeeiooouc")
    t = t.translate(table)
    return re.sub(r"\s+", " ", t).strip()


def detect_language(text: str) -> str:
    """Heuristica simples por proporcao de caracteres.

    - Se houver hiragana ou katakana -> 'ja'
    - Se nao houver kana mas houver Han (CJK Unified Ideographs) -> 'zh'
    - Caso contrario -> 'en'

    Observacao: textos japoneses tipicamente misturam kana com kanji; textos
    chineses usam apenas Han. Nao distinguimos zh-CN vs zh-TW.
    """
    if not text:
        return "en"
    if _HIRAGANA_RE.search(text) or _KATAKANA_RE.search(text):
        return "ja"
    if _CJK_HAN_RE.search(text):
        return "zh"
    return "en"


def _contains_any(haystack: str, needles: Iterable[str]) -> bool:
    for n in needles:
        if not n:
            continue
        # Para latim, normalizamos; para CJK, comparamos direto.
        if _CJK_HAN_RE.search(n) or _HIRAGANA_RE.search(n) or _KATAKANA_RE.search(n):
            if n in haystack:
                return True
        else:
            if n.lower() in haystack.lower():
                return True
    return False


def detect_keywords(text: str, *, max_terms: int = 60) -> List[str]:
    """Retorna a lista (ordenada e unica) de palavras-chave detectadas."""
    if not text:
        return []
    found: Set[str] = set()
    norm_latin = _normalize_latin(text)
    for kw in ALL_KEYWORDS:
        if _CJK_HAN_RE.search(kw) or _HIRAGANA_RE.search(kw) or _KATAKANA_RE.search(kw):
            if kw in text:
                found.add(kw)
        else:
            if kw in norm_latin:
                found.add(kw)
        if len(found) >= max_terms:
            break
    return sorted(found)


def has_sensitive_content(text: str) -> bool:
    """True se o texto contem marcadores sensiveis para auditoria."""
    if not text:
        return False
    norm_latin = _normalize_latin(text)
    for term in SENSITIVE_CONTEXT_MARKERS:
        if _CJK_HAN_RE.search(term) or _HIRAGANA_RE.search(term) or _KATAKANA_RE.search(term):
            if term in text:
                return True
        else:
            if term in norm_latin:
                return True
    return False


def detect_sensitive_context(text: str) -> List[str]:
    """Retorna marcadores sensiveis detectados, sem filtrar o registro."""
    if not text:
        return []
    norm_latin = _normalize_latin(text)
    found: Set[str] = set()
    for term in SENSITIVE_CONTEXT_MARKERS:
        if _CJK_HAN_RE.search(term) or _HIRAGANA_RE.search(term) or _KATAKANA_RE.search(term):
            if term in text:
                found.add(term)
        elif term in norm_latin:
            found.add(term)
    return sorted(found)


def classify_strategic_sector(text: str) -> str:
    """Aplica as regras de SECTOR_RULES e retorna o setor mais especifico."""
    if not text:
        return "ciencia_tecnologia"
    for sector, patterns in SECTOR_RULES:
        if _contains_any(text, patterns):
            return sector
    return "ciencia_tecnologia"


def classify_subthemes(text: str) -> List[str]:
    """Lista de subtemas detectados; conteudo sensivel nao e censurado."""
    if not text:
        return []
    found: Set[str] = set()
    for subtheme, patterns in SUBTHEME_PATTERNS.items():
        if _contains_any(text, patterns):
            found.add(subtheme)
    return sorted(found)


def infer_opportunity_type(text: str, *, source_name: str = "", hint: str = "") -> str:
    """Inferencia heuristica de tipo de oportunidade."""
    if hint and hint in OPPORTUNITY_TYPES:
        return hint
    composite = f"{source_name} {text}"
    for op_type, patterns in OPPORTUNITY_RULES:
        if _contains_any(composite, patterns):
            return op_type
    return "noticia_institucional"


# ---------------------------------------------------------------------------
# Builder principal
# ---------------------------------------------------------------------------

def build_asia_extras(
    *,
    titulo_original: str = "",
    descricao_original: str = "",
    text_for_classification: str = "",
    source_name: str = "",
    origem: str = "",
    pais: str = "",
    instituicao: str = "",
    orgao_responsavel: str = "",
    orgao_contratante: str = "",
    empresa_prime: str = "",
    tipo_oportunidade_hint: str = "",
    idioma_original: Optional[str] = None,
    titulo_traduzido: str = "",
    descricao_traduzida: str = "",
) -> Dict[str, object]:
    """Monta o dict de extras para fontes asiaticas.

    Os valores ja existentes no item original devem ter precedencia sobre
    estes defaults. O transformer fara: extras = {**asia_defaults, **extras}.
    """
    text = text_for_classification or f"{titulo_original} {descricao_original}"
    if idioma_original is None:
        idioma_original = detect_language(text or titulo_original or descricao_original)

    keywords = detect_keywords(text)
    sector = classify_strategic_sector(text)
    subtemas = classify_subthemes(text)
    sensitive_markers = detect_sensitive_context(text)
    area_cientifica = [
        s for s in subtemas
        if s in (
            "fisica", "matematica", "quimica", "fisica_nuclear", "quimica_nuclear",
            "engenharia_nuclear", "energia_nuclear", "radioprotecao", "aceleradores",
            "ciencia_dos_materiais", "materiais_avancados", "semicondutores",
            "tecnologias_quanticas", "aeroespacial",
        )
    ]
    area_tecnologica = [s for s in subtemas if s not in area_cientifica]
    op_type = infer_opportunity_type(
        text, source_name=source_name, hint=tipo_oportunidade_hint,
    )
    necessita_traducao = idioma_original in ("ja", "zh") and not (
        titulo_traduzido or descricao_traduzida
    )

    return {
        "regiao": "asia",
        "pais": pais or "",
        "idioma_original": idioma_original or "",
        "titulo_original": titulo_original or "",
        "descricao_original": descricao_original or "",
        "titulo_traduzido": titulo_traduzido or "",
        "descricao_traduzida": descricao_traduzida or "",
        "setor_estrategico": sector,
        "subtema": subtemas,
        "area_cientifica": area_cientifica,
        "area_tecnologica": area_tecnologica,
        "tipo_oportunidade": op_type,
        "orgao_responsavel": orgao_responsavel or "",
        "instituicao": instituicao or "",
        "empresa_prime": empresa_prime or "",
        "orgao_contratante": orgao_contratante or "",
        "nivel_sensibilidade": "publico_institucional",
        "contexto_sensivel_detectado": bool(sensitive_markers),
        "marcadores_contexto_sensivel": sensitive_markers,
        "origem": origem or "",
        "palavras_chave_detectadas": keywords,
        "necessita_traducao": bool(necessita_traducao),
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
        "observacoes": "",
    }


__all__ = [
    "KEYWORDS_PT", "KEYWORDS_EN", "KEYWORDS_JA", "KEYWORDS_ZH", "ALL_KEYWORDS",
    "STRATEGIC_SECTORS", "SUBTHEME_PATTERNS", "OPPORTUNITY_TYPES",
    "SENSITIVE_CONTEXT_MARKERS",
    "detect_language", "detect_keywords", "has_sensitive_content", "detect_sensitive_context",
    "classify_strategic_sector", "classify_subthemes", "infer_opportunity_type",
    "build_asia_extras",
]
