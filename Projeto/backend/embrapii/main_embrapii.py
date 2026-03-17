import json
import csv
from pathlib import Path
from extrair_informacoes_embrapii import coletar_chamadas

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def salvar_json(chamadas):
    with open(OUTPUT_DIR / "embrapii_editais.json", "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in chamadas], f, ensure_ascii=False, indent=2)

def salvar_csv(chamadas):
    with open(OUTPUT_DIR / "embrapii_editais.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "link", "ano", "data_publicacao", "deadline"])
        writer.writeheader()
        for c in chamadas:
            writer.writerow(c.to_dict())

def main():
    chamadas = coletar_chamadas()
    if not chamadas:
        print("Nenhum edital no momento.")
        # Opcional: Limpar arquivos antigos se preferir, ou apenas avisar
        return

    salvar_json(chamadas)
    salvar_csv(chamadas)
    print(f"{len(chamadas)} chamadas de 2026 salvas.")

if __name__ == "__main__":
    main()
