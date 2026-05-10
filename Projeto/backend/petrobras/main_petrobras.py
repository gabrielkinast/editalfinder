import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_petrobras import PetrobrasScraper
from utils_petrobras import is_deadline_valid, normalize_petrobras_url

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "petrobras_editais.json"
CSV_PATH = OUTPUT_DIR / "petrobras_editais.csv"

def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if any(k in text for k in ["resultado", "retificação", "retificacao", "socioambiental", "cookies", "copyright"]):
        return False
    return any(k in text for k in ["inscrições", "inscricoes", "edital", "chamada", "seleção pública", "selecao publica"])


def _console_text(text: str) -> str:
    try:
        return str(text).encode("cp1252", errors="replace").decode("cp1252")
    except Exception:
        return str(text)


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
            
        print(f"Processando detalhes: {_console_text(edital.titulo)[:100]}")
        item = edital.to_dict()
        if _is_relevant_item(item):
            final_data.append(item)

    # Dedupe por link canonizado (ex.: http vs https na Bússola).
    deduped: list = []
    seen: set[str] = set()
    for row in final_data:
        lk = normalize_petrobras_url(str(row.get("link") or ""))
        if not lk or lk in seen:
            continue
        seen.add(lk)
        row = dict(row)
        row["link"] = lk
        ex = row.get("extras")
        if isinstance(ex, dict) and ex.get("url_detalhe"):
            ex = dict(ex)
            ex["url_detalhe"] = normalize_petrobras_url(str(ex.get("url_detalhe") or ""))
            row["extras"] = ex
        deduped.append(row)
    final_data = deduped

    if final_data:
        save_json(final_data)
        save_csv(final_data)
        print(f"Sucesso! {len(final_data)} editais e programas da Petrobras salvos em {OUTPUT_DIR}")
    else:
        print("Nenhum edital da Petrobras (com prazo válido) encontrado nas páginas oficiais.")

if __name__ == "__main__":
    main()
