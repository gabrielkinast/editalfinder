import json
import csv
from pathlib import Path
from extrair_informacoes_softex import SoftexScraper
from utils_softex import is_deadline_valid

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
JSON_PATH = OUTPUT_DIR / "softex_editais.json"
CSV_PATH = OUTPUT_DIR / "softex_editais.csv"
POSITIVE_HINTS = [
    "edital",
    "chamada",
    "fomento",
    "programa",
    "inscri",
    "sele",
    "submiss",
    "geek",
    "acelera",
    "startup",
    "capacita",
    "transformação digital",
    "transformacao digital",
]
NOISE_HINTS = ["ouvidoria", "politica de privacidade", "cookies", "trabalhe conosco"]


def _enrich_item(item: dict) -> dict:
    extras = item.get("extras") if isinstance(item.get("extras"), dict) else {}
    extras.update(
        {
            "pais": extras.get("pais") or "Brasil",
            "regiao": extras.get("regiao") or "brasil",
            "orgao_responsavel": extras.get("orgao_responsavel") or "SOFTEX",
            "instituicao": extras.get("instituicao") or "Softex",
            "orgao_contratante": extras.get("orgao_contratante") or "SOFTEX",
            "setor_estrategico": extras.get("setor_estrategico") or "transformacao_digital",
            "tipo_oportunidade": extras.get("tipo_oportunidade") or "chamada_publica",
            "tipo_recurso": extras.get("tipo_recurso") or "fomento",
            "natureza_recurso": extras.get("natureza_recurso") or "nao_reembolsavel",
            "reembolsavel": extras.get("reembolsavel") if extras.get("reembolsavel") is not None else False,
            "area_cientifica": extras.get("area_cientifica") or ["computacao", "engenharia_software"],
            "area_tecnologica": extras.get("area_tecnologica") or ["ia", "software", "transformacao_digital"],
            "url_listagem": extras.get("url_listagem") or "https://softex.br/",
            "url_detalhe": extras.get("url_detalhe") or item.get("link") or "",
            "metodo_extracao": extras.get("metodo_extracao") or "html_listing_detail",
            "nivel_sensibilidade": extras.get("nivel_sensibilidade") or "publico_institucional",
        }
    )
    item["extras"] = extras
    item.setdefault("valor", None)
    item.setdefault("programa", "softex")
    item.setdefault("acao", "chamada_publica")
    item.setdefault("tipo_recurso", "fomento")
    return item


def _is_relevant_item(item: dict) -> bool:
    title = str(item.get("titulo") or "").strip().lower()
    link = str(item.get("link") or "").strip().lower()
    desc = str(item.get("descricao") or "").strip().lower()
    text = f"{title} {desc} {link}"
    if "softex.br" not in link:
        return False
    if link.rstrip("/") in {"https://softex.br", "http://softex.br", "https://www.softex.br", "http://www.softex.br"}:
        return False
    if any(k in text for k in NOISE_HINTS):
        return False
    if any(k in text for k in ["resultado final", "resultado da chamada", "evento em brasília", "evento em brasilia", "comunicado"]):
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
                "titulo": "SOFTEX - Página de Editais e Programas",
                "descricao": "Índice público de editais, chamadas e programas da Softex.",
                "link": "https://softex.br/",
                "fonte": "SOFTEX",
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
        scraper = SoftexScraper()
        print("[SOFTEX] Coletando editais e programas...")
        editais = scraper.extract_editais()
    except Exception as exc:
        print(f"[SOFTEX] Falha na coleta: {exc}")
        editais = []

    final_data = []
    for edital in editais:
        if edital.fim_inscricao and not is_deadline_valid(edital.fim_inscricao):
            print(f"[SOFTEX] Pulando edital vencido: {edital.titulo[:50]} ({edital.fim_inscricao})")
            continue
        item = _enrich_item(edital.to_dict())
        if _is_relevant_item(item):
            final_data.append(item)

    final_data = _dedupe(final_data)[:40]

    if not final_data:
        final_data = _fallback_items()
        print("[SOFTEX] Fallback ativado por ausência de itens.")
    save_json(final_data)
    save_csv(final_data)
    print(f"Sucesso! {len(final_data)} editais e programas da Softex salvos em {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
