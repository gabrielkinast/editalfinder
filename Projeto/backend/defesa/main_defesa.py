import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_defesa import DefesaScraper
from utils_defesa import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_EDITAIS_PATH = OUTPUT_DIR / "defesa_editais.json"
JSON_NOTICIAS_PATH = OUTPUT_DIR / "defesa_noticias_militares.json"
CSV_PATH = OUTPUT_DIR / "defesa_editais.csv"

def save_json(data: list, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_csv(data: list, path: Path):
    if not data:
        return
    keys = data[0].keys()
    with open(path, "w", encoding="utf-8", newline="") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    scraper = DefesaScraper()
    print("Coletando editais e notícias do Ministério da Defesa...")
    
    # Extrai editais e notícias separadamente
    editais, noticias = scraper.extract_all()
    
    # Processa editais filtrando deadline
    final_editais = []
    for edital in editais:
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            print(f"Pulando edital vencido: {edital.titulo[:50]} ({edital.fim_inscricao})")
            continue
            
        print(f"Processando detalhes edital: {edital.titulo[:100]}")
        final_editais.append(edital.to_dict())

    # Processa notícias
    final_noticias = [n.to_dict() for n in noticias]

    # Salva editais (serão usados pelo transformer e loader)
    if final_editais:
        save_json(final_editais, JSON_EDITAIS_PATH)
        save_csv(final_editais, CSV_PATH)
        print(f"Sucesso! {len(final_editais)} editais salvos em {JSON_EDITAIS_PATH}")
    else:
        print("Nenhum edital da Defesa (com prazo válido) encontrado nas páginas oficiais.")

    # Salva notícias (apenas para informação local, não vai para o banco de dados)
    if final_noticias:
        save_json(final_noticias, JSON_NOTICIAS_PATH)
        print(f"Sucesso! {len(final_noticias)} notícias militares salvas em {JSON_NOTICIAS_PATH}")
    else:
        print("Nenhuma notícia militar relevante encontrada.")

if __name__ == "__main__":
    main()
