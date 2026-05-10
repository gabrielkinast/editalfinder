import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_fappr import FapprScraper
from utils_fappr import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "fappr_editais.json"
CSV_PATH = OUTPUT_DIR / "fappr_editais.csv"


def _enrich_item(item: dict) -> dict:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras.update(
        {
            "pais": extras.get("pais") or "Brasil",
            "regiao": extras.get("regiao") or "brasil",
            "orgao_responsavel": extras.get("orgao_responsavel") or "Fundação Araucária",
            "instituicao": extras.get("instituicao") or "Fundação Araucária (PR)",
            "orgao_contratante": extras.get("orgao_contratante") or "Fundação Araucária",
            "setor_estrategico": extras.get("setor_estrategico") or "ciencia_tecnologia_inovacao",
            "tipo_oportunidade": extras.get("tipo_oportunidade") or "chamada_publica",
            "tipo_recurso": extras.get("tipo_recurso") or "fomento",
            "natureza_recurso": extras.get("natureza_recurso") or "nao_reembolsavel",
            "reembolsavel": extras.get("reembolsavel") if extras.get("reembolsavel") is not None else False,
            "area_cientifica": extras.get("area_cientifica") or ["ciencia", "tecnologia", "inovacao"],
            "area_tecnologica": extras.get("area_tecnologica") or ["pesquisa_aplicada", "transformacao_digital"],
            "url_listagem": extras.get("url_listagem") or "https://www.fappr.pr.gov.br/",
            "url_detalhe": extras.get("url_detalhe") or item.get("link") or "",
            "metodo_extracao": extras.get("metodo_extracao") or "html_listing_detail",
            "nivel_sensibilidade": extras.get("nivel_sensibilidade") or "publico_institucional",
        }
    )
    item["extras"] = extras
    item.setdefault("valor", None)
    item.setdefault("programa", "fundacao_araucaria")
    item.setdefault("acao", "chamada_publica")
    item.setdefault("tipo_recurso", "fomento")
    return item


def _fallback_items() -> list:
    return [
        _enrich_item(
            {
                "titulo": "Fundação Araucária - Página de Editais e Programas",
                "descricao": "Índice público de editais, chamadas e programas da Fundação Araucária.",
                "link": "https://www.fappr.pr.gov.br/",
                "fonte": "Fundação Araucária",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "extras": {"metodo_extracao": "fallback_public_index"},
            }
        )
    ]

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
    
    scraper = FapprScraper()
    print("Coletando editais, programas e fomento da Fundação Araucária (Paraná)...")
    
    # Extrai a lista e processa detalhes
    editais = scraper.extract_editais()
    
    final_data = []
    for edital in editais:
        # Filtro de deadline final
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            print(f"Pulando edital vencido: {edital.titulo[:50]} ({edital.fim_inscricao})")
            continue
            
        print(f"Processando: {edital.titulo[:100]}")
        final_data.append(_enrich_item(edital.to_dict()))

    if not final_data:
        final_data = _fallback_items()
        print("[FAPPR] Fallback ativado por ausência de itens.")
    save_json(final_data)
    save_csv(final_data)
    print(f"Sucesso! {len(final_data)} editais e programas da Fundação Araucária salvos em {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
