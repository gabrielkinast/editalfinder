import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_bndes import BNDESScraper
from utils_bndes import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "bndes_editais.json"
CSV_PATH = OUTPUT_DIR / "bndes_editais.csv"

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
    
    scraper = BNDESScraper()
    print("Coletando editais do BNDES (Fundos de Investimento)...")
    
    # Extrai a lista de editais
    editais = scraper.extract_editais()
    
    # Processa cada um para pegar detalhes e salva
    final_data = []
    hoje = datetime.now().date()
    
    for edital in editais:
        # O filtro de deadline já foi aplicado dentro de extract_editais
        # Mas vamos garantir aqui também
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            print(f"Pulo edital vencido: {edital.titulo} ({edital.fim_inscricao})")
            continue
            
        print(f"Processando detalhes: {edital.titulo}")
        # Detalhes já vêm da process_detail_page
        final_data.append(edital.to_dict())

    if final_data:
        save_json(final_data)
        save_csv(final_data)
        print(f"Sucesso! {len(final_data)} editais salvos em {OUTPUT_DIR}")
    else:
        print("Nenhum edital do BNDES (com prazo válido) encontrado.")

if __name__ == "__main__":
    main()
