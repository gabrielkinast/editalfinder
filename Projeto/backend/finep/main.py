from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

from extrair_informações import FinepScraper
from models import EditalFinep
from utils import normalize_ascii

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
CSV_PATH = OUTPUT_DIR / "finep_editais.csv"
JSON_PATH = OUTPUT_DIR / "finep_editais.json"



def passa_filtro(edital: EditalFinep, hoje: date | None = None) -> bool:
    hoje = hoje or date.today()
    situacao_ok = normalize_ascii(edital.situacao) == "aberta"
    publicado_2026_ou_mais = edital.data_publicacao is not None and edital.data_publicacao.year >= 2026
    prazo_valido = edital.prazo_envio is not None and edital.prazo_envio >= hoje
    return situacao_ok and (publicado_2026_ou_mais or prazo_valido)



def salvar_csv(registros: list[dict]) -> None:
    if not registros:
        CSV_PATH.write_text("", encoding="utf-8")
        return

    with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(registros[0].keys()))
        writer.writeheader()
        writer.writerows(registros)



def salvar_json(registros: list[dict]) -> None:
    with JSON_PATH.open("w", encoding="utf-8") as fp:
        json.dump(registros, fp, ensure_ascii=False, indent=2)



def main() -> None:
    scraper = FinepScraper()
    links = scraper.extrair_links_chamadas_abertas()
    print(f"Links encontrados: {len(links)}")

    filtrados: list[dict] = []
    hoje = date.today()

    for index, link in enumerate(links, start=1):
        try:
            edital = scraper.extrair_detalhes_chamada(link)
            status = "OK " if passa_filtro(edital, hoje=hoje) else "SKIP"
            print(
                f"[{index:02d}] {status} {edital.titulo} | "
                f"pub={edital.data_publicacao} | prazo={edital.prazo_envio} | situacao={edital.situacao}"
            )
            if status == "OK ":
                filtrados.append(edital.to_dict())
        except Exception as exc:
            print(f"[{index:02d}] ERRO {link} -> {exc}")

    salvar_csv(filtrados)
    salvar_json(filtrados)

    print()
    print(f"Total filtrado: {len(filtrados)}")
    print(f"CSV:  {CSV_PATH}")
    print(f"JSON: {JSON_PATH}")


if __name__ == "__main__":
    main()
