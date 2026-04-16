import json
import os
import sys
from pathlib import Path

# Adiciona o diretório atual ao path para importação direta
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from scrapers import ScienceScrapers
except ImportError:
    from .scrapers import ScienceScrapers

def main():
    output_dir = "science_scraper/outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    scrapers = ScienceScrapers()
    
    # Links Europa
    europa_links = [
        ("https://research-and-innovation.ec.europa.eu/research-area/industrial-research-and-innovation/chemicals-and-advanced-materials_en", "EC-Chemicals"),
        ("https://research-and-innovation.ec.europa.eu/research-area/industrial-research-and-innovation/artificial-intelligence-ai-science_en", "EC-AI"),
        ("https://research-and-innovation.ec.europa.eu/research-area/industrial-research-and-innovation/technology-infrastructures_en", "EC-Tech-Infra"),
        ("https://defence-industry-space.ec.europa.eu/eu-space/research-development-and-innovation_en", "EC-Space")
    ]
    for url, name in europa_links:
        scrapers.scrape_ec_europa(url, name)
        
    # Links OSTI (EUA)
    osti_links = [
        ("https://science.osti.gov/grants/FOAs/Open", "OSTI-Grants"),
        ("https://science.osti.gov/grants/Lab-Announcements/Open", "OSTI-Labs")
    ]
    for url, name in osti_links:
        scrapers.scrape_osti_gov(url, name)
        
    # Links Brasil
    scrapers.scrape_aeb()
    scrapers.scrape_aneel()
    scrapers.scrape_faperj()
    
    # Grants.gov
    scrapers.scrape_grants_gov()
    
    # Salvar resultados
    output_path = os.path.join(output_dir, "science_editais.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in scrapers.results], f, indent=2, ensure_ascii=False)
        
    print(f"\nFinalizado! {len(scrapers.results)} editais coletados em {output_path}")

if __name__ == "__main__":
    main()
