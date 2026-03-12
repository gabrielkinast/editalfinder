from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

import importlib.util
import sys


def _carregar_modulo(nome: str, arquivo: str):
    caminho = Path(__file__).with_name(arquivo)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar {arquivo}")
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


_extrator = _carregar_modulo("extrair_informacoes_cnpq", "extrair_informações-cnpq.py")
CNPQScraper = _extrator.CNPQScraper


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)
CSV_PATH = OUTPUT_DIR / "cnpq_editais.csv"
JSON_PATH = OUTPUT_DIR / "cnpq_editais.json"


def passa_filtro(edital) -> bool:
    hoje = date.today()
    criado_2026_ou_mais = edital.publicado_em is not None and edital.publicado_em.year >= 2026
    deadline_aberto = edital.inscricoes_fim is not None and edital.inscricoes_fim >= hoje
    return criado_2026_ou_mais or deadline_aberto


def achatar_registro(edital) -> dict:
    data = edital.to_dict()
    data["anexos"] = json.dumps(data["anexos"], ensure_ascii=False)
    data["qtd_anexos"] = len(edital.anexos)
    return data


def salvar_csv(registros: list[dict]) -> None:
    if not registros:
        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "titulo",
                "url_pagina",
                "url_chamada",
                "publicado_em",
                "atualizado_em",
                "inscricoes_inicio",
                "inscricoes_fim",
                "situacao",
                "descricao",
                "anexos",
                "qtd_anexos",
            ])
        return

    with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(registros[0].keys()))
        writer.writeheader()
        writer.writerows(registros)


def salvar_json(registros: list[dict]) -> None:
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)


def main() -> None:
    scraper = CNPQScraper()
    editais = scraper.extrair_editais()
    print(f"Editais encontrados: {len(editais)}")

    filtrados: list[dict] = []
    for idx, edital in enumerate(editais, start=1):
        status = "OK" if passa_filtro(edital) else "SKIP"
        print(
            f"[{idx:02d}] {status} {edital.titulo} | "
            f"pub={edital.publicado_em} | fim={edital.inscricoes_fim} | anexos={len(edital.anexos)}"
        )
        if passa_filtro(edital):
            filtrados.append(achatar_registro(edital))

    salvar_csv(filtrados)
    salvar_json(filtrados)

    print()
    print(f"Total filtrado: {len(filtrados)}")
    print(f"CSV:  {CSV_PATH}")
    print(f"JSON: {JSON_PATH}")


if __name__ == "__main__":
    main()
