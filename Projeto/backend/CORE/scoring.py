import re
from datetime import datetime
from typing import Dict, List, Any

from functools import lru_cache

# Perfis de Oportunidade Expandidos (Fallback caso o banco falhe)
DEFAULT_REFERENCE_PROFILES = {
    "Pesquisador": {
        "keywords": ["bolsa", "doutorado", "mestrado", "pesquisa científica", "produtividade", "artigo", "pós-graduação"],
        "eligibility": ["pessoa física", "pesquisador", "doutor", "mestre", "estudante"],
    },
    "Consultoria em Captação de Recursos": {
        "keywords": ["fomento", "subvenção", "financiamento", "captação", "elaboração de projetos", "propostas", "edital"],
        "eligibility": ["assessoria", "consultoria", "empresa", "ict", "ong"],
    }
}

@lru_cache(maxsize=32)
def get_profiles_for_org(id_organizacao: int = 11) -> Dict[str, Any]:
    """Busca os perfis de interesse da organização no banco de dados com cache."""
    from db import supabase
    try:
        response = supabase.table("organizacao").select("perfis_interesse").eq("id_organizacao", id_organizacao).execute()
        if response.data and response.data[0].get("perfis_interesse"):
            # Converte lista de objetos para o dicionário esperado pela lógica de scoring
            db_profiles = response.data[0]["perfis_interesse"]
            if isinstance(db_profiles, list):
                return {p["nome"]: {"keywords": p["keywords"], "eligibility": p["eligibility"]} for p in db_profiles}
    except Exception as e:
        print(f"Erro ao carregar perfis do banco: {e}")
    
    return DEFAULT_REFERENCE_PROFILES

def calculate_compatibility(text: str, profile_name: str, profiles_dict: Dict[str, Any]) -> int:
    """Calcula a compatibilidade percentual (0-100) de um texto com um perfil."""
    data = profiles_dict.get(profile_name)
    if not data: return 0
    
    score = 0
    for kw in data["keywords"]:
        if kw.lower() in text.lower():
            score += 20
            
    for el in data["eligibility"]:
        if el.lower() in text.lower():
            score += 40
            
    return min(score, 100)

def get_all_compatibilities(edital: Dict[str, Any], profiles_dict: Dict[str, Any]) -> Dict[str, int]:
    """Gera um dicionário de compatibilidade para todos os perfis."""
    text = f"{edital.get('titulo', '')} {edital.get('temas', '')} {edital.get('objetivo', '')} {edital.get('publico_alvo', '')} {edital.get('descricao', '')}".lower()
    
    compatibilities = {}
    for profile in profiles_dict.keys():
        compat = calculate_compatibility(text, profile, profiles_dict)
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
    
    # Carrega os perfis da organização (ID 11 por padrão ou do perfil do usuário se existir)
    id_org = user_profile.get("id_organizacao", 11) if user_profile else 11
    profiles_dict = get_profiles_for_org(id_org)
    
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
    compatibilities = get_all_compatibilities(edital, profiles_dict)
    recommendations = [p for p, c in compatibilities.items() if c >= 60]

    return {
        "score_total": min(total_score, 100),
        "score_components": comp,
        "justification": justification,
        "compatibilities": compatibilities,
        "recommendations": recommendations
    }
