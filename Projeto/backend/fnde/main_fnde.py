import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path
from urllib.parse import urljoin

def get_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def main():
    url = "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas"
    print(f"Scraping FNDE: {url}")
    
    soup = get_soup(url)
    if not soup: return
    
    editais = []
    # FNDE costuma listar programas em listas ou tiles
    items = soup.select(".tileItem") or soup.select("ul li a")
    
    for item in items:
        link_tag = item if item.name == 'a' else item.find("a")
        if not link_tag: continue
        
        href = link_tag.get("href")
        if not href or not href.startswith("http"):
            href = urljoin(url, href)
            
        titulo = link_tag.get_text().strip()
        if len(titulo) > 10:
            editais.append({
                "titulo": titulo,
                "link": href,
                "fonte": "FNDE",
                "descricao": titulo,
                "situacao": "Aberto"
            })
            
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "fnde_editais.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(editais, f, indent=2, ensure_ascii=False)
        
    print(f"Sucesso! {len(editais)} editais salvos em {output_path}")

if __name__ == "__main__":
    main()
