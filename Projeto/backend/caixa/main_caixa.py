import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from urllib.parse import urljoin

def get_soup(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False) # CAIXA as vezes tem erro de SSL
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Erro ao acessar {url}: {e}")
        return None

def main():
    urls = [
        "https://www.caixa.gov.br/sustentabilidade/fundo-socioambiental-caixa/chamadas-abertas/Paginas/default.aspx",
        "https://www.caixa.gov.br/fundos-investimento/empresa/poupanca-e-investimentos/Paginas/default.aspx",
        "https://www.caixa.gov.br/empresa/credito-financiamento/Paginas/default.aspx"
    ]
    
    all_editais = []
    
    for url in urls:
        print(f"Scraping CAIXA: {url}")
        soup = get_soup(url)
        if not soup: continue
        
        # Seletores comuns na Caixa
        links = soup.select(".cx-link") or soup.select("a")
        for a in links:
            titulo = a.get_text().strip()
            href = a.get("href")
            if not href: continue
            
            # Filtro básico para evitar links de navegação
            if len(titulo) > 15 and any(kw in titulo.lower() or kw in href.lower() for kw in ["fundo", "chamada", "investimento", "credito", "financiamento", "edital"]):
                full_url = urljoin(url, href)
                if full_url not in [e["link"] for e in all_editais]:
                    all_editais.append({
                        "titulo": titulo,
                        "link": full_url,
                        "fonte": "CAIXA",
                        "descricao": titulo,
                        "situacao": "Aberto"
                    })
                    
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "caixa_editais.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_editais, f, indent=2, ensure_ascii=False)
        
    print(f"Sucesso! {len(all_editais)} itens da CAIXA salvos em {output_path}")

if __name__ == "__main__":
    # Suprime avisos de SSL inseguro se necessário
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
