import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_mapa import MAPAScraper
from utils_mapa import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "mapa_editais.json"
CSV_PATH = OUTPUT_DIR / "mapa_editais.csv"


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if any(k in text for k in ["governo amplia acesso ao crédito", "receita pública", "notícia", "marca encerramento"]):
        return False
    return any(k in text for k in ["edital", "chamada", "inscri", "submiss", "consulta pública", "chamamento"])


def _enrich_item(item: dict) -> dict:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras.update(
        {
            "pais": extras.get("pais") or "Brasil",
            "regiao": extras.get("regiao") or "brasil",
            "orgao_responsavel": extras.get("orgao_responsavel") or "MAPA",
            "instituicao": extras.get("instituicao") or "Ministério da Agricultura e Pecuária",
            "orgao_contratante": extras.get("orgao_contratante") or "MAPA",
            "setor_estrategico": extras.get("setor_estrategico") or "agronegocio",
            "tipo_oportunidade": extras.get("tipo_oportunidade") or "chamada_publica",
            "tipo_recurso": extras.get("tipo_recurso") or "fomento",
            "natureza_recurso": extras.get("natureza_recurso") or "nao_reembolsavel",
            "reembolsavel": extras.get("reembolsavel") if extras.get("reembolsavel") is not None else False,
            "area_cientifica": extras.get("area_cientifica") or ["agronomia", "biotecnologia", "sustentabilidade"],
            "area_tecnologica": extras.get("area_tecnologica") or ["agritech", "cadeia_produtiva", "seguranca_alimentar"],
            "url_listagem": extras.get("url_listagem") or "https://www.gov.br/agricultura/pt-br",
            "url_detalhe": extras.get("url_detalhe") or item.get("link") or "",
            "metodo_extracao": extras.get("metodo_extracao") or "html_listing_detail",
            "nivel_sensibilidade": extras.get("nivel_sensibilidade") or "publico_institucional",
        }
    )
    item["extras"] = extras
    item.setdefault("valor", None)
    item.setdefault("programa", "mapa")
    item.setdefault("acao", "chamada_publica")
    item.setdefault("tipo_recurso", "fomento")
    return item


def _fallback_items() -> list:
    return [
        _enrich_item(
            {
                "titulo": "MAPA - Página de Editais e Programas",
                "descricao": "Índice público de editais, chamadas e programas do MAPA.",
                "link": "https://www.gov.br/agricultura/pt-br",
                "fonte": "MAPA",
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
    
    scraper = MAPAScraper()
    print("Coletando editais, fomento e crédito do MAPA...")
    
    # Extrai a lista e processa detalhes
    editais = scraper.extract_editais()
    
    final_data = []
    for edital in editais:
        # Filtro de deadline final
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            print(f"Pulando edital vencido: {edital.titulo[:50]} ({edital.fim_inscricao})")
            continue
            
        print(f"Processando detalhes: {edital.titulo[:100]}")
        item = _enrich_item(edital.to_dict())
        if _is_relevant_item(item):
            final_data.append(item)

    if not final_data:
        final_data = _fallback_items()
        print("[MAPA] Fallback ativado por ausência de itens.")
    save_json(final_data)
    save_csv(final_data)
    print(f"Sucesso! {len(final_data)} registros do MAPA salvos em {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
