import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0"
}

def get_soup(url: str) -> Optional[BeautifulSoup]:
    try:
        # Tenta com curl como fallback para contornar o 403 do requests
        import subprocess
        
        # Comando curl básico simulando browser
        cmd = [
            'curl', '-L', '-k',
            '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0 and result.stdout:
            return BeautifulSoup(result.stdout, "html.parser")
            
        # Fallback original
        session = requests.Session()
        response = session.get(url, headers=HEADERS, timeout=30, verify=False)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def normalize_text(text: str) -> str:
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def extract_date(text: str) -> Optional[str]:
    if not text:
        return None
    # Procura datas no formato DD/MM/YYYY
    match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if match:
        try:
            date_str = match.group(1)
            # Converte para YYYY-MM-DD
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None
    return None

def is_deadline_valid(deadline_str: str) -> bool:
    if not deadline_str:
        return True # Se não houver data, consideramos válida por precaução
    try:
        deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        return deadline_date >= today
    except ValueError:
        return True
