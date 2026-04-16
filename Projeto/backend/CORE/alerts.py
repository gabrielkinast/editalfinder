import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Adiciona o CORE ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def calculate_score(edital, perfil):
    """
    Calcula o score de aderência baseado no perfil do usuário.
    Perfil exemplo: {"temas": ["química", "inovação"], "regiao": "Nacional"}
    """
    score = 0
    text = f"{edital.get('titulo', '')} {edital.get('temas', '')} {edital.get('objetivo', '')}".lower()
    
    for tema in perfil.get("temas", []):
        if tema.lower() in text:
            score += 20
            
    if edital.get("regiao") == perfil.get("regiao"):
        score += 30
        
    return min(score, 100)

def generate_smart_alert(edital, old_edital=None):
    """Gera a mensagem do alerta baseada no estado do edital."""
    hoje = datetime.now().date()
    
    # 1. Edital Novo
    if not old_edital:
        perfil_quimica = {"temas": ["química", "engenharia"], "regiao": "Nacional"}
        score = calculate_score(edital, perfil_quimica)
        
        prazo = edital.get("prazo_envio")
        prazo_str = ""
        if prazo:
            try:
                dt_prazo = datetime.strptime(prazo, "%Y-%m-%d").date()
                dias = (dt_prazo - hoje).days
                prazo_str = f", prazo em {dias} dias"
            except: pass
            
        return {
            "tipo": "NOVO_EDITAL",
            "score": score,
            "mensagem": f"Nova chamada da {edital.get('fonte_recurso')} para {edital.get('titulo')[:50]}...{prazo_str}. Alta aderência detectada ({score}%)."
        }
    
    # 2. Prorrogação ou Mudança de Prazo
    if edital.get("prazo_envio") != old_edital.get("prazo_envio"):
        return {
            "tipo": "PRORROGADO",
            "mensagem": f"O edital {edital.get('titulo')} teve o prazo alterado de {old_edital.get('prazo_envio')} para {edital.get('prazo_envio')}."
        }
        
    # 3. Retificação (Mudança no objetivo ou descrição)
    if edital.get("objetivo") != old_edital.get("objetivo"):
        return {
            "tipo": "RETIFICADO",
            "mensagem": f"O edital {edital.get('titulo')} foi retificado. Verifique as mudanças no objetivo."
        }

    return None

def process_alerts(new_editais, old_editais_map):
    """Processa todos os editais para gerar alertas."""
    alerts = []
    for edital in new_editais:
        link = edital.get("link")
        old_edital = old_editais_map.get(link)
        
        alert = generate_smart_alert(edital, old_edital)
        if alert:
            alerts.append(alert)
            print(f"ALERTA: {alert['mensagem']}")
            
    return alerts
