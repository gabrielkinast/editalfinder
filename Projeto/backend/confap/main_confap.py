import requests
from bs4 import BeautifulSoup
import json
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
    url = "https://confap.org.br/pt/editais"
    print(f"Scraping CONFAP: {url}")
    
    soup = get_soup(url)
    if not soup: return
    
    editais = []
    # CONFAP costuma listar editais em blocos ou tabelas
    items = soup.select(".edital-item") or soup.select("article") or soup.select("a")
    for a in items:
        titulo = a.get_text().strip()
        href = a.get("href")
        if not href: continue
        
        if len(titulo) > 10 and any(kw in titulo.lower() or kw in href.lower() for kw in ["edital", "chamada", "fomento", "oportunidade"]):
            full_url = urljoin(url, href)
            if full_url not in [e["link"] for e in editais]:
                editais.append({
                    "titulo": titulo,
                    "link": full_url,
                    "fonte": "CONFAP",
                    "descricao": titulo,
                    "situacao": "Aberto"
                })
                
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "confap_editais.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(editais, f, indent=2, ensure_ascii=False)
        
    print(f"Sucesso! {len(editais)} editais salvos em {output_path}")

if __name__ == "__main__":
    main()
