#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stub Vunesp — tentativa de leitura educada de robots + página de concursos.

Motivo do stub: em vários ambientes o site devolve **403** a clientes HTTP simples
(WAF). O piloto ativo está em `main_pci_concursos.py`. Ver
`docs/CONCURSOS_WAVE1_PILOT_DECISION.md`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.vunesp.com.br"
UA = "EditalFinderConcursosBot/0.1 (stub; no aggressive crawl)"


def main() -> int:
    ap = argparse.ArgumentParser(description="Stub Vunesp — diagnóstico HTTP/robots")
    ap.add_argument("--output", type=str, default="")
    args = ap.parse_args()

    note = {
        "fonte": "vunesp",
        "status": "stub",
        "mensagem": "Use PCI piloto (concursos/main_pci_concursos.py). Vunesp requer browser/WAF bypass ou acordo institucional.",
    }
    try:
        req = Request(BASE + "/", headers={"User-Agent": UA})
        with urlopen(req, timeout=15) as r:
            note["home_http"] = getattr(r, "status", 200)
    except Exception as exc:
        note["home_http"] = "erro"
        note["erro"] = str(exc)

    if args.output:
        p = Path(args.output)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(note, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(note, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
