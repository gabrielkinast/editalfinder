import json
import csv
import os
from pathlib import Path
from datetime import datetime
from extrair_informacoes_anp import ANPScraper
from utils_anp import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "anp_editais.json"
CSV_PATH = OUTPUT_DIR / "anp_editais.csv"


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").lower()
    link = str(item.get("link") or "").lower()
    desc = str(item.get("descricao") or "").lower()
    text = f"{title} {desc} {link}"
    if "gov.br/anp" not in link:
        return False
    if any(k in text for k in ["ações e programas", "acoes e programas", "forum de tecnologia", "noticia", "carta de servicos"]):
        return False
    if any(s in link for s in ("consulta-audiencia", "consultas-e-audiencias", "consulta_e_audiencia")):
        return True
    if "consulta" in text and ("audiência" in text or "audiencia" in text):
        return True
    return any(k in text for k in ["edital", "chamada", "consulta pública", "consulta publica", "inscri", "submiss"])


def _enrich_item(item: dict) -> dict:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras.update(
        {
            "pais": extras.get("pais") or "Brasil",
            "regiao": extras.get("regiao") or "brasil",
            "orgao_responsavel": extras.get("orgao_responsavel") or "ANP",
            "instituicao": extras.get("instituicao") or "Agência Nacional do Petróleo, Gás Natural e Biocombustíveis",
            "orgao_contratante": extras.get("orgao_contratante") or "ANP",
            "setor_estrategico": extras.get("setor_estrategico") or "energia_petroleo_gas",
            "tipo_oportunidade": extras.get("tipo_oportunidade") or "chamada_publica",
            "tipo_recurso": extras.get("tipo_recurso") or "fomento",
            "natureza_recurso": extras.get("natureza_recurso") or "nao_reembolsavel",
            "reembolsavel": extras.get("reembolsavel") if extras.get("reembolsavel") is not None else False,
            "area_cientifica": extras.get("area_cientifica") or ["energia", "quimica", "engenharia"],
            "area_tecnologica": extras.get("area_tecnologica") or ["petroleo_gas", "transicao_energetica", "biocombustiveis"],
            "url_listagem": extras.get("url_listagem") or "https://www.gov.br/anp/pt-br",
            "url_detalhe": extras.get("url_detalhe") or item.get("link") or "",
            "metodo_extracao": extras.get("metodo_extracao") or "html_listing_detail",
            "nivel_sensibilidade": extras.get("nivel_sensibilidade") or "publico_institucional",
        }
    )
    item["extras"] = extras
    item.setdefault("valor", None)
    item.setdefault("programa", "anp")
    item.setdefault("acao", "chamada_publica")
    item.setdefault("tipo_recurso", "fomento")
    return item


def _fallback_items() -> list:
    return [
        _enrich_item(
            {
                "titulo": "ANP - Página de Editais e Chamadas",
                "descricao": "Índice público de editais, chamadas e programas da ANP.",
                "link": "https://www.gov.br/anp/pt-br",
                "fonte": "ANP",
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
    # Use keys from first item to build header
    keys = data[0].keys()
    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    scraper = ANPScraper()
    print("Coletando editais, programas e fomento da ANP (Agência Nacional do Petróleo)...")
    
    # Extrai a lista e processa detalhes
    editais = scraper.extract_editais()
    
    final_data = []
    for edital in editais:
        print(f"Processando detalhes: {edital.titulo[:100]}")
        item = _enrich_item(edital.to_dict())
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            item["situacao"] = "Encerrado"
            extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
            extras.setdefault("prazo_inscricao_detectado", edital.fim_inscricao)
            item["extras"] = extras
            print(f"  (prazo de inscrição já encerrado: {edital.fim_inscricao}; mantido como Encerrado)")
        elif edital.fim_inscricao:
            item["situacao"] = item.get("situacao") or "Aberto"

        if _is_relevant_item(item):
            final_data.append(item)

    if not final_data:
        final_data = _fallback_items()
        print("[ANP] Fallback ativado por ausência de itens.")
    save_json(final_data)
    save_csv(final_data)
    print(f"Sucesso! {len(final_data)} editais e programas da ANP salvos em {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
