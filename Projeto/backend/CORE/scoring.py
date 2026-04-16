import re
from datetime import datetime
from typing import Dict, List, Any

# Perfis de Oportunidade Expandidos
REFERENCE_PROFILES = {
    "Pesquisador": {
        "keywords": ["bolsa", "doutorado", "mestrado", "pesquisa científica", "produtividade", "artigo", "pós-graduação"],
        "eligibility": ["pessoa física", "pesquisador", "doutor", "mestre", "estudante"],
    },
    "Professor": {
        "keywords": ["docente", "ensino", "extensão", "sala de aula", "educação básica", "capacitação"],
        "eligibility": ["professor", "docente", "magistério", "educador"],
    },
    "Startup": {
        "keywords": ["startup", "microempresa", "inovação disruptiva", "aceleração", "mvp", "escalabilidade", "vcs"],
        "eligibility": ["me", "epp", "startup", "empresa de base tecnológica"],
    },
    "Empresa Industrial": {
        "keywords": ["indústria", "manufatura", "produtividade industrial", "máquinas", "equipamentos", "processos"],
        "eligibility": ["empresa", "indústria", "setor produtivo", "cnpj"],
    },
    "Universidade/ICT": {
        "keywords": ["infraestrutura", "laboratório", "pesquisa aplicada", "ict", "ciência e tecnologia", "academia"],
        "eligibility": ["instituição de ensino", "universidade", "ict", "fundação de apoio"],
    },
    "Prefeitura": {
        "keywords": ["município", "gestão pública", "cidade", "urbano", "serviços públicos", "desenvolvimento local"],
        "eligibility": ["prefeitura", "municipal", "administração pública direta"],
    },
    "Escola": {
        "keywords": ["ensino fundamental", "ensino médio", "escola pública", "pedagógico", "alunos", "merenda"],
        "eligibility": ["escola", "colégio", "instituição de ensino básico"],
    },
    "ONG": {
        "keywords": ["social", "sem fins lucrativos", "terceiro setor", "comunitário", "sociedade civil", "voluntariado"],
        "eligibility": ["ong", "oscip", "associação", "sem fins lucrativos"],
    },
    "Laboratório": {
        "keywords": ["análises", "ensaios", "certificação", "equipamento laboratorial", "metrologia", "pesquisa"],
        "eligibility": ["laboratório", "centro de pesquisa", "núcleo tecnológico"],
    },
    "Cooperativa": {
        "keywords": ["associativismo", "cooperativismo", "pequeno produtor", "agricultura familiar", "união"],
        "eligibility": ["cooperativa", "associação de produtores"],
    },
    "Consultoria/Assessor": {
        "keywords": ["gestão de projetos", "elaboração de propostas", "captação de recursos", "consultoria estratégica", "viabilidade"],
        "eligibility": ["prestador de serviços", "consultoria", "pessoa jurídica"],
    },
    "Investidor/VC": {
        "keywords": ["equity", "venture capital", "investimento anjo", "participação", "aporte", "rodada de investimento"],
        "eligibility": ["fundo de investimento", "investidor", "gestora"],
    },
    "Agronegócio": {
        "keywords": ["rural", "fazenda", "agronegócio", "safras", "pecuária", "biotecnologia agrária", "campo"],
        "eligibility": ["produtor rural", "empresa agrícola", "cooperativa agro"],
    },
    "HealthTech/Saúde": {
        "keywords": ["dispositivos médicos", "saúde digital", "clínica", "hospital", "fármacos", "biomedicina"],
        "eligibility": ["instituição de saúde", "hospital", "empresa de biotecnologia"],
    }
}

def calculate_compatibility(text: str, profile_name: str) -> int:
    """Calcula a compatibilidade percentual (0-100) de um texto com um perfil."""
    data = REFERENCE_PROFILES.get(profile_name)
    if not data: return 0
    
    score = 0
    for kw in data["keywords"]:
        if kw.lower() in text.lower():
            score += 20
            
    for el in data["eligibility"]:
        if el.lower() in text.lower():
            score += 40
            
    return min(score, 100)

def get_all_compatibilities(edital: Dict[str, Any]) -> Dict[str, int]:
    """Gera um dicionário de compatibilidade para todos os perfis."""
    text = f"{edital.get('titulo', '')} {edital.get('temas', '')} {edital.get('objetivo', '')} {edital.get('publico_alvo', '')} {edital.get('descricao', '')}".lower()
    
    compatibilities = {}
    for profile in REFERENCE_PROFILES.keys():
        compat = calculate_compatibility(text, profile)
        if compat > 0:
            compatibilities[profile] = compat
            
    return compatibilities

def generate_justification(components: Dict[str, int]) -> str:
    """Gera um motivo resumido baseado nos componentes do score."""
    area = components.get("area", 0)
    deadline = components.get("deadline", 0)
    location = components.get("location", 0)
    eligibility = components.get("eligibility", 0)
    
    reasons = []
    
    if area >= 30 and eligibility >= 8:
        reasons.append("Alta aderência ao perfil técnico e elegibilidade.")
    elif area >= 30:
        reasons.append("Forte match com os temas de interesse.")
        
    if deadline >= 12:
        reasons.append("Prazo muito próximo, oportunidade exige atenção urgente.")
    elif deadline >= 8:
        reasons.append("Prazo em andamento, boa hora para preparar proposta.")
        
    if location >= 15:
        reasons.append("Excelente compatibilidade regional.")
    elif location == 0 and area >= 25:
        reasons.append("Boa aderência temática, mas baixa compatibilidade regional.")
        
    if not reasons:
        return "Oportunidade geral com critérios básicos atendidos."
        
    return " ".join(reasons[:2]) # Retorna os 2 motivos principais

def calculate_relevance_score(edital: Dict[str, Any], user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Calcula o score detalhado por componentes e gera justificativa.
    """
    text = f"{edital.get('titulo', '')} {edital.get('temas', '')} {edital.get('objetivo', '')} {edital.get('publico_alvo', '')}".lower()
    hoje = datetime.now().date()
    
    comp = {
        "area": 0,        # Max 40
        "deadline": 0,    # Max 15
        "location": 0,    # Max 20
        "eligibility": 0, # Max 15
        "value": 0,       # Max 10
    }
    
    # 1. Área/Temas
    if user_profile and "temas" in user_profile:
        for tema in user_profile["temas"]:
            if tema.lower() in text:
                comp["area"] += 20
        comp["area"] = min(comp["area"], 40)

    # 2. Prazo (Urgência)
    prazo = edital.get("prazo_envio")
    if prazo:
        try:
            dt_prazo = datetime.strptime(prazo, "%Y-%m-%d").date()
            dias = (dt_prazo - hoje).days
            if 0 <= dias <= 7: comp["deadline"] = 15
            elif 7 < dias <= 20: comp["deadline"] = 10
            elif 20 < dias <= 60: comp["deadline"] = 5
        except: pass

    # 3. Localidade
    if user_profile and "regiao" in user_profile:
        if edital.get("regiao") == user_profile["regiao"]:
            comp["location"] = 20
        elif edital.get("regiao") == "Nacional":
            comp["location"] = 10

    # 4. Elegibilidade
    if user_profile and "tipo_entidade" in user_profile:
        if user_profile["tipo_entidade"].lower() in text:
            comp["eligibility"] = 15
    else:
        # Se não houver perfil, tenta detectar palavras genéricas de elegibilidade
        if any(kw in text for kw in ["aberto para", "elegível", "pode participar"]):
            comp["eligibility"] = 8

    # 5. Valor
    valor_max = edital.get("valor_maximo") or 0
    if valor_max > 1000000: comp["value"] = 10
    elif valor_max > 100000: comp["value"] = 5

    total_score = sum(comp.values())
    justification = generate_justification(comp)
    compatibilities = get_all_compatibilities(edital)
    recommendations = [p for p, c in compatibilities.items() if c >= 60]

    return {
        "score_total": min(total_score, 100),
        "score_components": comp,
        "justification": justification,
        "compatibilities": compatibilities,
        "recommendations": recommendations
    }
