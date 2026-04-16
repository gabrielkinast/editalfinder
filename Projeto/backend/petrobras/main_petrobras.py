import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_petrobras import PetrobrasScraper
from utils_petrobras import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "petrobras_editais.json"
CSV_PATH = OUTPUT_DIR / "petrobras_editais.csv"

def save_json(data: list):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_csv(data: list):
    if not data:
        return
    keys = data[0].keys()
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    scraper = PetrobrasScraper()
    print("Coletando editais, programas e fomento da Petrobras...")
    
    # Extrai a lista e processa detalhes
    editais = scraper.extract_editais()
    
    final_data = []
    for edital in editais:
        # Filtro de deadline final
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            print(f"Pulando edital vencido: {edital.titulo[:50]} ({edital.fim_inscricao})")
            continue
            
        print(f"Processando detalhes: {edital.titulo[:100]}")
        final_data.append(edital.to_dict())

    if final_data:
        save_json(final_data)
        save_csv(final_data)
        print(f"Sucesso! {len(final_data)} editais e programas da Petrobras salvos em {OUTPUT_DIR}")
    else:
        print("Nenhum edital da Petrobras (com prazo válido) encontrado nas páginas oficiais.")

if __name__ == "__main__":
    main()
