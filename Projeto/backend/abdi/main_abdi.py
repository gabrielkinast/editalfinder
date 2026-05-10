import json
import csv
from pathlib import Path
from extrair_informacoes_abdi import ABDIScraper

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "abdi_editais.json"
CSV_PATH = OUTPUT_DIR / "abdi_editais.csv"
POSITIVE_HINTS = ["edital", "chamada", "fomento", "consulta pública", "processo seletivo", "inovacao", "industria"]
NOISE_HINTS = ["ouvidoria", "cookies", "trabalhe conosco", "politica de privacidade", "perfil-das-propostas-inscritas"]


def _enrich_item(item: dict) -> dict:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras.update(
        {
            "pais": extras.get("pais") or "Brasil",
            "regiao": extras.get("regiao") or "brasil",
            "orgao_responsavel": extras.get("orgao_responsavel") or "ABDI",
            "instituicao": extras.get("instituicao") or "Agência Brasileira de Desenvolvimento Industrial",
            "orgao_contratante": extras.get("orgao_contratante") or "ABDI",
            "setor_estrategico": extras.get("setor_estrategico") or "industria_inovacao",
            "tipo_oportunidade": extras.get("tipo_oportunidade") or "chamada_publica",
            "tipo_recurso": extras.get("tipo_recurso") or "fomento",
            "natureza_recurso": extras.get("natureza_recurso") or "nao_reembolsavel",
            "reembolsavel": extras.get("reembolsavel") if extras.get("reembolsavel") is not None else False,
            "area_cientifica": extras.get("area_cientifica") or ["engenharia", "economia_industrial"],
            "area_tecnologica": extras.get("area_tecnologica") or ["industria_4_0", "transformacao_digital"],
            "url_listagem": extras.get("url_listagem") or "https://www.abdi.com.br/",
            "url_detalhe": extras.get("url_detalhe") or item.get("link") or "",
            "metodo_extracao": extras.get("metodo_extracao") or "html_listing_detail",
            "nivel_sensibilidade": extras.get("nivel_sensibilidade") or "publico_institucional",
        }
    )
    item["extras"] = extras
    item.setdefault("valor", None)
    item.setdefault("programa", "abdi")
    item.setdefault("acao", "chamada_publica")
    item.setdefault("tipo_recurso", "fomento")
    return item


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").strip().lower()
    link = str(item.get("link") or "").strip().lower()
    desc = str(item.get("descricao") or "").strip().lower()
    text = f"{title} {desc} {link}"
    if title in {"baixar", "documento", "home"} or title.startswith("documento:"):
        return False
    if "termo de referência" in text or "termo de referencia" in text:
        return False
    if "abdi.com.br" not in link:
        return False
    if any(k in text for k in NOISE_HINTS):
        return False
    return any(k in text for k in POSITIVE_HINTS)


def _dedupe(items: list[dict]) -> list[dict]:
    out = []
    seen = set()
    for it in items:
        key = f"{it.get('link','')}|{it.get('titulo','')}".strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def _fallback_items() -> list:
    return [
        _enrich_item(
            {
                "titulo": "ABDI - Página de Editais e Programas",
                "descricao": "Índice público de editais, chamadas e programas da ABDI.",
                "link": "https://www.abdi.com.br/",
                "fonte": "ABDI",
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
    try:
        scraper = ABDIScraper()
        print("[ABDI] Coletando editais...")
        editais = scraper.extract_editais()
    except Exception as exc:
        print(f"[ABDI] Falha na coleta: {exc}")
        editais = []

    final_data = []
    for edital in editais:
        item = _enrich_item(edital.to_dict())
        if _is_relevant_item(item):
            final_data.append(item)

    final_data = _dedupe(final_data)[:40]

    if not final_data:
        final_data = _fallback_items()
        print("[ABDI] Fallback ativado por ausência de itens.")
    save_json(final_data)
    save_csv(final_data)
    print(f"Sucesso! {len(final_data)} editais salvos em {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
