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


def _enrich_item(item: dict) -> dict:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    anexos = extras.get("anexos") if isinstance(extras.get("anexos"), list) else []
    pdf_url = ""
    for a in anexos:
        if isinstance(a, dict):
            url = str(a.get("url") or "")
            if url.lower().endswith(".pdf") or ".pdf?" in url.lower():
                pdf_url = url
                break
    extras.update(
        {
            "pais": "Brasil",
            "regiao": "brasil",
            "orgao_responsavel": "Ministério da Defesa",
            "instituicao": "Ministério da Defesa",
            "setor_estrategico": "defesa_industrial",
            "tipo_oportunidade": extras.get("tipo_oportunidade") or "chamada_publica",
            "tipo_recurso": extras.get("tipo_recurso") or "fomento",
            "natureza_recurso": extras.get("natureza_recurso") or "nao_reembolsavel",
            "reembolsavel": False,
            "area_cientifica": extras.get("area_cientifica") or ["defesa", "materiais", "energia_nuclear"],
            "area_tecnologica": extras.get("area_tecnologica") or ["defesa", "aeroespacial", "sensores", "radares"],
            "documentos": extras.get("documentos") or anexos,
            "pdf_url": extras.get("pdf_url") or pdf_url,
            "url_listagem": extras.get("url_listagem") or "https://www.gov.br/defesa/pt-br/assuntos/editais",
            "url_detalhe": extras.get("url_detalhe") or item.get("link") or "",
            "metodo_extracao": extras.get("metodo_extracao") or "html_listing_detail",
            "nivel_sensibilidade": extras.get("nivel_sensibilidade") or "publico_institucional",
        }
    )
    item["extras"] = extras
    item.setdefault("valor", None)
    item.setdefault("programa", "ministerio_da_defesa")
    item.setdefault("acao", "chamada_publica")
    item.setdefault("tipo_recurso", "fomento")
    return item


def _fallback_items() -> list:
    return [
        _enrich_item(
            {
                "titulo": "Ministério da Defesa - Página de Editais",
                "descricao": "Índice público para editais, chamadas e programas do Ministério da Defesa.",
                "link": "https://www.gov.br/defesa/pt-br/assuntos/editais",
                "fonte": "Ministério da Defesa",
                "data_publicacao": None,
                "fim_inscricao": None,
                "situacao": "Em andamento",
                "extras": {
                    "tipo_oportunidade": "chamada_publica",
                    "tipo_recurso": "fomento",
                    "natureza_recurso": "nao_reembolsavel",
                    "metodo_extracao": "fallback_public_index",
                    "observacoes": "Nenhum edital ativo encontrado na coleta atual.",
                },
            }
        )
    ]

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
        final_editais.append(_enrich_item(edital.to_dict()))

    # Processa notícias
    final_noticias = [n.to_dict() for n in noticias]

    # Salva editais (serão usados pelo transformer e loader)
    if not final_editais:
        final_editais = _fallback_items()
        print("[DEFESA] Fallback ativado por ausência de editais válidos.")
    save_json(final_editais, JSON_EDITAIS_PATH)
    save_csv(final_editais, CSV_PATH)
    print(f"Sucesso! {len(final_editais)} editais salvos em {JSON_EDITAIS_PATH}")

    # Salva notícias (apenas para informação local, não vai para o banco de dados)
    if final_noticias:
        save_json(final_noticias, JSON_NOTICIAS_PATH)
        print(f"Sucesso! {len(final_noticias)} notícias militares salvas em {JSON_NOTICIAS_PATH}")
    else:
        print("Nenhuma notícia militar relevante encontrada.")

if __name__ == "__main__":
    main()
