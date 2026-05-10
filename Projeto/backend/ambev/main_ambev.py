import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_ambev import AmbevScraper
from utils_ambev import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "ambev_editais.json"
CSV_PATH = OUTPUT_DIR / "ambev_editais.csv"

def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if "subchallenge" in title or "challengeschallenges" in title:
        return False
    if any(k in text for k in ["resultado final", "closed", "newsroom"]):
        return False
    if item.get("fim_inscricao"):
        return True
    # Páginas curadas do 100+ (já filtradas no extrator): manter desafio ativo
    if "100accelerator.com/challenges/" in link:
        tail = link.rstrip("/").split("/")[-1]
        if tail and tail != "challenges":
            return True
    return any(k in text for k in ("edital", "chamada", "inscri", "programa", "startup", "desafio"))


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
    
    scraper = AmbevScraper()
    print("Coletando editais, programas e fomento da AMBEV...")
    
    # Extrai a lista e processa detalhes
    editais = scraper.extract_editais()
    
    final_data = []
    for edital in editais:
        link_l = (edital.link or "").lower()
        is_100_challenge = "100accelerator.com/challenges/" in link_l and link_l.rstrip("/").split("/")[-1] not in ("", "challenges")

        # Filtro de deadline: no 100+ o HTML costuma trazer várias datas antigas;
        # se o extrator escolher uma data passada, tratamos como prazo desconhecido.
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            if is_100_challenge:
                edital.fim_inscricao = None
            else:
                print(f"Pulando edital vencido: {edital.titulo[:50]} ({edital.fim_inscricao})")
                continue

        print(f"Processando detalhes: {edital.titulo[:100]}")
        item = edital.to_dict()
        if _is_relevant_item(item):
            final_data.append(item)

    if final_data:
        save_json(final_data)
        save_csv(final_data)
        print(f"Sucesso! {len(final_data)} editais e programas da AMBEV salvos em {OUTPUT_DIR}")
    else:
        print("Nenhuma chamada aberta da AMBEV encontrada nas páginas oficiais.")

if __name__ == "__main__":
    main()
