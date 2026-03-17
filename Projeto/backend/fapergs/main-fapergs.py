from __future__ import annotations

import csv
import json
import importlib.util
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def _load_module(filename: str, module_name: str):
    path = BASE_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {filename}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_load_module("models_fapergs.py", "models_fapergs")
_load_module("utils_fapergs.py", "utils_fapergs")
extrair_mod = _load_module("extrair_informações-fapergs.py", "extrair_informações_fapergs")

FapergsScraper = extrair_mod.FapergsScraper

CSV_PATH = OUTPUT_DIR / "fapergs_editais.csv"
JSON_PATH = OUTPUT_DIR / "fapergs_editais.json"



def passa_filtro(edital) -> bool:
    hoje = date.today()

    # Se achou na página de "abertos", mantém por padrão.
    # Só descarta quando houver prazo explicitamente vencido.
    if edital.prazo_envio is not None and edital.prazo_envio < hoje:
        return False

    return True



def save_csv(rows: list[dict]) -> None:
    fields = [
        "titulo", "numero_edital", "url_pagina", "pdf_url", "situacao",
        "data_publicacao", "prazo_envio", "objetivo", "descricao", "anexos",
    ]
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            out = row.copy()
            out["anexos"] = json.dumps(out.get("anexos", []), ensure_ascii=False)
            writer.writerow(out)



def save_json(rows: list[dict]) -> None:
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)



def main() -> None:
    scraper = FapergsScraper()
    items = scraper.collect()
    print(f"Entradas coletadas: {len(items)}")

    filtered: list[dict] = []
    for idx, item in enumerate(items, start=1):
        keep = passa_filtro(item)
        status = "OK" if keep else "SKIP"
        print(
            f"[{idx:02d}] {status} {item.titulo} | "
            f"pub={item.data_publicacao} | prazo={item.prazo_envio} | pdf={item.pdf_url}"
        )
        if keep:
            filtered.append(item.to_dict())

    save_csv(filtered)
    save_json(filtered)
    print()
    print(f"Total filtrado: {len(filtered)}")
    print(f"CSV:  {CSV_PATH}")
    print(f"JSON: {JSON_PATH}")


if __name__ == "__main__":
    main()
