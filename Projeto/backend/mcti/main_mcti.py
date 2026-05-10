import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_mcti import MCTIScraper
from utils_mcti import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "mcti_editais.json"
CSV_PATH = OUTPUT_DIR / "mcti_editais.csv"


def _enrich_item(item: dict) -> dict:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras.setdefault("regiao", "brasil")
    extras.setdefault("pais", "Brasil")
    extras.setdefault("idioma_original", "pt")
    extras.setdefault("setor_estrategico", "ciencia_tecnologia")
    extras.setdefault("subtema", [])
    extras.setdefault("area_cientifica", ["fisica", "quimica", "ciencia_dos_materiais"])
    extras.setdefault("area_tecnologica", ["inovacao", "pdi"])
    extras.setdefault("tipo_oportunidade", "chamada_publica")
    extras.setdefault("orgao_responsavel", "MCTI")
    extras.setdefault("instituicao", "Ministério da Ciência, Tecnologia e Inovação")
    extras.setdefault("orgao_contratante", "MCTI")
    extras.setdefault("documentos", extras.get("anexos", []))
    extras.setdefault("pdf_url", "")
    extras.setdefault("metodo_extracao", "crawler_detalhe")
    extras.setdefault("url_listagem", "")
    extras.setdefault("url_detalhe", item.get("link", ""))
    extras.setdefault("nivel_sensibilidade", "publico_institucional")
    item["extras"] = extras
    item.setdefault("valor", None)
    item.setdefault("programa", "mcti_fomento")
    item.setdefault("acao", "monitoramento_oportunidades_publicas")
    item.setdefault("tipo_recurso", "Oportunidade Publica")
    return item

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
    
    scraper = MCTIScraper()
    print("Coletando editais e programas do MCTI...")
    
    # Extrai a lista e processa detalhes
    editais = scraper.extract_editais()
    
    final_data = []
    for edital in editais:
        # Filtro de deadline final
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            print(f"Pulando edital vencido: {edital.titulo[:50]} ({edital.fim_inscricao})")
            continue
            
        print(f"Processando detalhes: {edital.titulo[:100]}")
        final_data.append(_enrich_item(edital.to_dict()))

    if final_data:
        save_json(final_data)
        save_csv(final_data)
        print(f"Sucesso! {len(final_data)} editais e programas MCTI salvos em {OUTPUT_DIR}")
    else:
        print("Nenhum edital do MCTI (com prazo válido) encontrado nas páginas oficiais.")

if __name__ == "__main__":
    main()
