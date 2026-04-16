import requests
from bs4 import BeautifulSoup
import re
from typing import Optional
from datetime import datetime
import subprocess

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
}

def get_soup(url: str) -> Optional[BeautifulSoup]:
    try:
        # Tenta com curl.exe como fallback para contornar bloqueios em sites corporativos/gov
        cmd = [
            'curl.exe', '-L', '-k',
            '-H', f'User-Agent: {HEADERS["User-Agent"]}',
            '-H', f'Accept: {HEADERS["Accept"]}',
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        
        if result.returncode == 0 and result.stdout:
            if "<html" in result.stdout.lower():
                return BeautifulSoup(result.stdout, "html.parser")
            
        # Fallback para requests
        response = requests.get(url, headers=HEADERS, timeout=30, verify=False)
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
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None
    return None

def is_deadline_valid(deadline_str: str) -> bool:
    if not deadline_str:
        return True
    try:
        deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        return deadline_date >= today
    except ValueError:
        return True
